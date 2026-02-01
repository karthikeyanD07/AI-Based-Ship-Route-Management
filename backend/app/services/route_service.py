"""Service layer for route optimization."""
import logging
from typing import Dict, Tuple, List
from backend.app.utils.route_algorithms import route_optimizer
from backend.app.models.schemas import OptimizedRouteResponse
from backend.app.utils.cache import route_cache

logger = logging.getLogger(__name__)


# Port coordinates (should be moved to database in production)
PORT_COORDS = {
    "Port A": (33.7405, -118.2519),  # Los Angeles
    "Port B": (40.6728, -74.1536),   # New York
    "Port C": (29.7305, -95.0892),   # Houston
    "Port D": (25.7785, -80.1826),   # Miami
    "Port E": (32.0835, -81.0998),   # Savannah
    "Port F": (47.6019, -122.3381),  # Seattle
}


class RouteService:
    """Service for route optimization."""
    
    def get_port_coordinates(self, port_name: str) -> Tuple[float, float]:
        """Get coordinates for a port by name."""
        if port_name not in PORT_COORDS:
            raise ValueError(f"Unknown port: {port_name}")
        return PORT_COORDS[port_name]
    
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
            OptimizedRouteResponse with route and metadata
        """
        # Check cache first
        cache_key = f"route:{start_port}:{end_port}"
        cached_result = route_cache.get(cache_key)
        if cached_result:
            logger.info(f"Route cache hit for {start_port} -> {end_port}")
            return OptimizedRouteResponse(
                ship_id=ship_id,
                optimized_route=cached_result["route_points"],
                distance_km=cached_result["distance_km"],
                estimated_time_hours=cached_result["estimated_hours"]
            )
        
        # Get port coordinates
        start_lat, start_lon = self.get_port_coordinates(start_port)
        end_lat, end_lon = self.get_port_coordinates(end_port)
        
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


# Global service instance
route_service = RouteService()
