"""Service layer for route optimization."""
import logging
from typing import Dict, Tuple, List
from ..utils.route_algorithms import route_optimizer
from ..models.schemas import OptimizedRouteResponse
from ..utils.cache import route_cache
from ..data.ports_database import port_db
from ..utils.emissions import emissions_calc

logger = logging.getLogger(__name__)


class RouteService:
    """Service for route optimization."""
    
    def get_port_coordinates(self, port_name: str) -> Tuple[float, float]:
        """Get coordinates for a port by name from database."""
        return port_db.get_port_coords(port_name)
    
    def search_ports(self, query: str) -> List[str]:
        """Search available ports."""
        return port_db.search_ports(query)
    
    def get_all_ports(self) -> List[str]:
        """Get list of all available ports."""
        return port_db.get_all_ports()
    
    def optimize_route(
        self,
        ship_id: str,
        start_port: str,
        end_port: str
    ) -> OptimizedRouteResponse:
        """
        Optimize route between two ports with caching.
        
        Args:
            ship_id: Ship identifier
            start_port: Start port name
            end_port: End port name
            
        Returns:
            Optimized route with distance and time estimates
        """
        # Check cache first
        cache_key = f"{ship_id}:{start_port}:{end_port}"
        cached = route_cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for route {start_port} -> {end_port}")
            return OptimizedRouteResponse(
                ship_id=ship_id,
                optimized_route=cached["route_points"],
                distance_km=cached["distance_km"],
                estimated_time_hours=cached["estimated_hours"]
            )
        
        logger.info(f"Optimizing route: {start_port} -> {end_port}")
        
        # Get port coordinates from database
        start_lat, start_lon = port_db.get_port_coords(start_port)
        end_lat, end_lon = port_db.get_port_coords(end_port)
        
        # Optimize route
        route_points, distance_km = route_optimizer.optimize_route(
            start_lat, start_lon, end_lat, end_lon, avoid_land=True
        )
        
        # Estimate time (assuming average speed of 12 knots)
        # 12 knots = standard merchant vessel speed for route planning
        # This is a typical speed for cargo ships and container vessels
        avg_speed_knots = 12.0
        distance_nautical_miles = distance_km / 1.852
        estimated_hours = distance_nautical_miles / avg_speed_knots
        
        result = OptimizedRouteResponse(
            ship_id=ship_id,
            optimized_route=route_points,
            distance_km=round(distance_km, 2),
            estimated_time_hours=round(estimated_hours, 2)
        )
        
        # Cache the result (route points, distance, time)
        route_cache.set(cache_key, {
            "route_points": route_points,
            "distance_km": result.distance_km,
            "estimated_hours": result.estimated_time_hours
        }, ttl=3600)  # Cache for 1 hour
        
        return result
    
    def compare_routes(
        self,
        ship_id: str,
        start_port: str,
        end_port: str,
        vessel_type: str = "container",
        vessel_size: str = "medium"
    ) -> Dict:
        """
        Compare three route optimization strategies.
        
        Args:
            ship_id: Ship identifier
            start_port: Start port name
            end_port: End port name
            vessel_type: Vessel type for emissions calculation
            vessel_size: Vessel size classification
            
        Returns:
            Comparison of fastest, balanced, and greenest routes
        """
        logger.info(f"Comparing routes: {start_port} -> {end_port}")
        
        # Get basic route
        basic_route = self.optimize_route(ship_id, start_port, end_port)
        
        # Define three strategies with different speeds
        strategies = [
            {"name": "fastest", "speed_knots": 15.0, "color": "#FF6B6B"},
            {"name": "balanced", "speed_knots": 12.0, "color": "#4ECDC4"},
            {"name": "greenest", "speed_knots": 10.0, "color": "#95E38B"}
        ]
        
        results = []
        
        for strategy in strategies:
            speed = strategy["speed_knots"]
            distance_km = basic_route.distance_km
            distance_nm = distance_km / 1.852
            
            # Calculate time
            time_hours = distance_nm / speed
            time_days = time_hours / 24
            
            # Calculate emissions
            emissions = emissions_calc.calculate_co2_emissions(
                distance_km=distance_km,
                speed_knots=speed,
                vessel_type=vessel_type,
                vessel_size=vessel_size
            )
            
            results.append({
                "route_name": strategy["name"],
                "color": strategy["color"],
                "route_points": basic_route.optimized_route,
                "distance_km": distance_km,
                "distance_nm": round(distance_nm, 2),
                "speed_knots": speed,
                "estimated_time_hours": round(time_hours, 2),
                "estimated_time_days": round(time_days, 2),
                "total_co2_tonnes": emissions["total_co2_tonnes"],
                "fuel_tonnes": emissions["fuel_consumed_tonnes"],
                "fuel_type": emissions["fuel_type"]
            })
        
        # Calculate savings vs fastest route
        fastest = results[0]
        for route in results[1:]:
            route["time_difference_hours"] = round(route["estimated_time_hours"] - fastest["estimated_time_hours"], 2)
            route["co2_savings_tonnes"] = round(fastest["total_co2_tonnes"] - route["total_co2_tonnes"], 2)
            route["co2_savings_percent"] = round(
                (fastest["total_co2_tonnes"] - route["total_co2_tonnes"]) / fastest["total_co2_tonnes"] * 100,
                1
            )
        
        return {
            "ship_id": ship_id,
            "start_port": start_port,
            "end_port": end_port,
            "vessel_type": vessel_type,
            "vessel_size": vessel_size,
            "routes": results,
            "recommendation": self._get_recommendation(results)
        }
    
    def optimize_route_with_weather(
        self,
        ship_id: str,
        start_port: str,
        end_port: str,
        vessel_speed: float = 12.0
    ) -> Dict:
        """
        Optimize route with weather considerations.
        
        Args:
            ship_id: Ship identifier
            start_port: Start port name
            end_port: End port name
            vessel_speed: Vessel's base speed in knots
            
        Returns:
            Weather-aware route optimization data
        """
        from app.utils.weather_routing import weather_router
        from datetime import datetime
        
        logger.info(f"Weather routing: {start_port} -> {end_port} @ {vessel_speed}kn")
        
        # Get basic optimized route first
        basic_route = self.optimize_route(ship_id, start_port, end_port)
        
        # Apply weather optimization
        weather_result = weather_router.optimize_route_with_weather(
            route_points=basic_route.optimized_route,
            base_speed=vessel_speed,
            departure_time=datetime.now()
        )
        
        # Enhance with ship and port info
        weather_result["ship_id"] = ship_id
        weather_result["start_port"] = start_port
        weather_result["end_port"] = end_port
        weather_result["weather_impact"] = {
            "time_difference_vs_simple": round(
                weather_result["total_time_hours"] - basic_route.estimated_time_hours, 2
            ),
            "speed_efficiency": round(
                (weather_result["average_speed"] / vessel_speed) * 100, 1
            )
        }
        
        return weather_result
    
    def _get_recommendation(self, routes: List[Dict]) -> str:
        """Generate recommendation based on route comparison."""
        greenest = routes[2]  # Greenest route
        balanced = routes[1]  # Balanced route
        
        if greenest["co2_savings_percent"] > 20 and greenest["time_difference_hours"] < 48:
            return f"The greenest route saves {greenest['co2_savings_tonnes']} tonnes CO2 ({greenest['co2_savings_percent']}%) with only {greenest['time_difference_hours']} extra hours. Highly recommended for sustainability goals."
        elif balanced["co2_savings_percent"] > 10:
            return f"The balanced route offers {balanced['co2_savings_tonnes']} tonnes CO2 savings ({balanced['co2_savings_percent']}%) with reasonable time impact. Best overall choice."
        else:
            return "The fastest route is recommended for time-critical shipments."


# Global singleton instance
route_service = RouteService()
