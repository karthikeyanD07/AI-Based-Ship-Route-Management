"""Advanced route optimization algorithms for maritime navigation using searoute."""
import math
import logging
from typing import List, Tuple
from geopy.distance import geodesic

logger = logging.getLogger(__name__)


class RouteOptimizer:
    """Maritime route optimization powered by the searoute library.

    searoute traces actual ship lanes and avoids landmasses and canals
    automatically (Panama, Suez, etc.), giving realistic sea distances
    and waypoints instead of a simple great-circle arc.
    """

    def __init__(self):
        self.earth_radius_km = 6371.0
        try:
            import searoute as sr
            self._sr = sr
            logger.info("searoute library loaded – using real maritime routing")
        except ImportError:
            self._sr = None
            logger.warning("searoute not available – falling back to great-circle routing")

    # ------------------------------------------------------------------
    # Public API (unchanged signature so nothing else needs editing)
    # ------------------------------------------------------------------

    def optimize_route(
        self,
        start_lat: float,
        start_lon: float,
        end_lat: float,
        end_lon: float,
        avoid_land: bool = True,
    ) -> Tuple[List[List[float]], float]:
        """Return (route_points [[lat, lon], …], total_distance_km)."""

        if not (-90 <= start_lat <= 90) or not (-180 <= start_lon <= 180):
            raise ValueError(f"Invalid start coordinates: lat={start_lat}, lon={start_lon}")
        if not (-90 <= end_lat <= 90) or not (-180 <= end_lon <= 180):
            raise ValueError(f"Invalid end coordinates: lat={end_lat}, lon={end_lon}")

        if self._sr is not None:
            return self._searoute_route(start_lat, start_lon, end_lat, end_lon)
        else:
            return self._great_circle_route(start_lat, start_lon, end_lat, end_lon)

    # ------------------------------------------------------------------
    # Primary: searoute
    # ------------------------------------------------------------------

    def _searoute_route(
        self,
        start_lat: float, start_lon: float,
        end_lat: float,   end_lon: float,
    ) -> Tuple[List[List[float]], float]:
        """
        Use the searoute library to compute a realistic sea route.

        searoute expects (lon, lat) order – the opposite of our internal
        (lat, lon) convention – so we swap on the way in and on the way out.
        """
        try:
            # searoute input: [lon, lat]
            origin      = [start_lon, start_lat]
            destination = [end_lon,   end_lat]

            result = self._sr.searoute(origin, destination, units="km")

            # GeoJSON coords are [lon, lat] – flip to [lat, lon] for frontend
            coords = result["geometry"]["coordinates"]
            route_points = [[lat, lon] for lon, lat in coords]

            # Use the library's calculated distance if available,
            # otherwise sum up haversine distances ourselves
            dist_km = result["properties"].get("length")
            if dist_km is None:
                dist_km = self._sum_distance(route_points)

            logger.info(
                f"searoute: {len(route_points)} waypoints, {dist_km:.1f} km "
                f"({start_lat},{start_lon}) → ({end_lat},{end_lon})"
            )
            return route_points, float(dist_km)

        except Exception as exc:
            logger.error(f"searoute failed ({exc}), falling back to great-circle")
            return self._great_circle_route(start_lat, start_lon, end_lat, end_lon)

    # ------------------------------------------------------------------
    # Fallback: great-circle
    # ------------------------------------------------------------------

    def _great_circle_route(
        self,
        start_lat: float, start_lon: float,
        end_lat: float,   end_lon: float,
        steps: int = 120,
    ) -> Tuple[List[List[float]], float]:
        """Simple great-circle fallback when searoute is unavailable."""
        route = self.great_circle_route(start_lat, start_lon, end_lat, end_lon, steps)
        dist  = self._sum_distance(route)
        return route, dist

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def great_circle_route(
        self,
        start_lat: float, start_lon: float,
        end_lat: float,   end_lon: float,
        steps: int = 120,
    ) -> List[List[float]]:
        """Generate interpolated great-circle points (used as fallback)."""
        φ1 = math.radians(start_lat);  λ1 = math.radians(start_lon)
        φ2 = math.radians(end_lat);    λ2 = math.radians(end_lon)

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
            B = math.sin(f * Δ)        / math.sin(Δ)
            x = A * math.cos(φ1) * math.cos(λ1) + B * math.cos(φ2) * math.cos(λ2)
            y = A * math.cos(φ1) * math.sin(λ1) + B * math.cos(φ2) * math.sin(λ2)
            z = A * math.sin(φ1)                  + B * math.sin(φ2)
            φ = math.atan2(z, math.sqrt(x * x + y * y))
            λ = math.atan2(y, x)
            route.append([math.degrees(φ), math.degrees(λ)])
        return route

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers

    def _sum_distance(self, route: List[List[float]]) -> float:
        total = 0.0
        for i in range(1, len(route)):
            total += self.haversine_distance(
                route[i-1][0], route[i-1][1],
                route[i][0],   route[i][1],
            )
        return total


# Global singleton
route_optimizer = RouteOptimizer()
