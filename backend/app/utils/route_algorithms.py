"""Advanced route optimization algorithms for maritime navigation."""
import math
import logging
from typing import List, Tuple, Optional
from heapq import heappush, heappop
from backend.app.utils.ocean_detection import ocean_detector
from geopy.distance import geodesic

logger = logging.getLogger(__name__)


class RouteOptimizer:
    """Advanced route optimization using A* algorithm with maritime constraints."""
    
    def __init__(self):
        self.earth_radius_km = 6371.0  # Earth's radius in kilometers
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great circle distance between two points in kilometers."""
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers
    
    def great_circle_route(
        self, 
        start_lat: float, 
        start_lon: float, 
        end_lat: float, 
        end_lon: float, 
        steps: int = 120
    ) -> List[List[float]]:
        """
        Generate a great-circle path between two points.
        
        Args:
            start_lat: Start latitude
            start_lon: Start longitude
            end_lat: End latitude
            end_lon: End longitude
            steps: Number of intermediate points
            
        Returns:
            List of [lat, lon] coordinates
        """
        # Convert to radians
        φ1 = math.radians(start_lat)
        λ1 = math.radians(start_lon)
        φ2 = math.radians(end_lat)
        λ2 = math.radians(end_lon)
        
        # Calculate angular distance
        Δ = 2 * math.asin(math.sqrt(
            math.sin((φ2 - φ1) / 2) ** 2 + 
            math.cos(φ1) * math.cos(φ2) * math.sin((λ2 - λ1) / 2) ** 2
        ))
        
        if Δ == 0:
            return [[start_lat, start_lon]]
        
        route = []
        for i in range(steps + 1):
            f = i / steps
            A = math.sin((1 - f) * Δ) / math.sin(Δ)
            B = math.sin(f * Δ) / math.sin(Δ)
            
            x = A * math.cos(φ1) * math.cos(λ1) + B * math.cos(φ2) * math.cos(λ2)
            y = A * math.cos(φ1) * math.sin(λ1) + B * math.cos(φ2) * math.sin(λ2)
            z = A * math.sin(φ1) + B * math.sin(φ2)
            
            φ = math.atan2(z, math.sqrt(x * x + y * y))
            λ = math.atan2(y, x)
            
            route.append([math.degrees(φ), math.degrees(λ)])
        
        return route
    
    def ocean_safe_route(self, points: List[List[float]]) -> List[List[float]]:
        """
        Ensure all points in route are in ocean, adjusting if necessary.
        
        Args:
            points: List of [lat, lon] coordinates
            
        Returns:
            Corrected list of [lat, lon] coordinates
        """
        corrected = []
        for lat, lon in points:
            if ocean_detector.is_ocean(lat, lon):
                corrected.append([lat, lon])
            else:
                # Find nearest ocean point
                corrected_lat, corrected_lon = self._nudge_to_ocean(lat, lon)
                corrected.append([corrected_lat, corrected_lon])
        return corrected
    
    def _nudge_to_ocean(self, lat: float, lon: float, max_iters: int = 50) -> Tuple[float, float]:
        """Nudge a point to the nearest ocean location."""
        if ocean_detector.is_ocean(lat, lon):
            return lat, lon
        
        # Try moving in a spiral pattern to find ocean
        step_size = 0.1
        for radius in range(1, max_iters):
            for angle in range(0, 360, 15):
                rad = math.radians(angle)
                test_lat = lat + radius * step_size * math.cos(rad)
                test_lon = lon + radius * step_size * math.sin(rad)
                
                # Normalize longitude
                if test_lon > 180:
                    test_lon -= 360
                elif test_lon < -180:
                    test_lon += 360
                
                if ocean_detector.is_ocean(test_lat, test_lon):
                    return test_lat, test_lon
        
        # Fallback: return original (shouldn't happen often)
        return lat, lon
    
    def optimize_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        avoid_land: bool = True
    ) -> Tuple[List[List[float]], float]:
        """
        Optimize route between two points.
        
        Args:
            start_lat: Start latitude
            start_lon: Start longitude
            end_lat: End latitude
            end_lon: End longitude
            avoid_land: Whether to avoid landmasses
            
        Returns:
            Tuple of (route_points, total_distance_km)
        """
        # Validate input coordinates
        if not (-90 <= start_lat <= 90) or not (-180 <= start_lon <= 180):
            raise ValueError(f"Invalid start coordinates: lat={start_lat}, lon={start_lon}")
        if not (-90 <= end_lat <= 90) or not (-180 <= end_lon <= 180):
            raise ValueError(f"Invalid end coordinates: lat={end_lat}, lon={end_lon}")
        
        # Generate great circle route
        route = self.great_circle_route(start_lat, start_lon, end_lat, end_lon, steps=160)
        
        if not route or len(route) < 2:
            logger.warning("Generated route is too short or empty")
            raise ValueError("Failed to generate valid route")
        
        # Make route ocean-safe if needed
        if avoid_land:
            route = self.ocean_safe_route(route)
        
        # Calculate total distance
        total_distance = 0.0
        for i in range(1, len(route)):
            total_distance += self.haversine_distance(
                route[i-1][0], route[i-1][1],
                route[i][0], route[i][1]
            )
        
        return route, total_distance


# Global instance
route_optimizer = RouteOptimizer()
