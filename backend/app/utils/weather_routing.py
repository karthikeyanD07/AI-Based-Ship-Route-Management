"""
Weather Routing Integration Module
Provides weather-aware route optimization using simple weather models.
Future: Can integrate with 52North WeatherRoutingTool for advanced features.
"""
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import math
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WeatherCondition:
    """Weather condition at a specific point."""
    wind_speed: float  # knots
    wind_direction: float  # degrees
    wave_height: float  # meters
    timestamp: datetime


class WeatherRouter:
    """
    Weather-aware routing engine.
    
    Provides simple weather routing with future extensibility
    for advanced algorithms (52North WRT, genetic algorithms, etc.)
    """
    
    def __init__(self):
        self.weather_data_cache = {}
        
    def get_weather_forecast(
        self,
        lat: float,
        lon: float,
        timestamp: datetime
    ) -> WeatherCondition:
        """
        Get weather forecast for a location and time.
        
        Args:
            lat: Latitude
            lon: Longitude
            timestamp: Forecast time
            
        Returns:
            WeatherCondition with forecast data
            
        Note:
            Currently uses simplified weather model.
            Future: Integrate with NOAA, OpenWeather, or ECMWF APIs
        """
        # Simplified weather model based on location and season
        # In production, replace with real weather API calls
        
        # Approximate seasonal wind patterns
        month = timestamp.month
        
        # Northern hemisphere trade winds (simplified)
        if -30 <= lat <= 30:
            # Trade winds - easterly
            base_wind_dir = 90.0
            base_wind_speed = 12.0
        elif 30 < lat <= 60:
            # Westerlies
            base_wind_dir = 270.0
            base_wind_speed = 15.0
        else:
            # Polar easterlies
            base_wind_dir = 90.0
            base_wind_speed = 20.0
            
        # Add some variation based on longitude
        wind_variation = math.sin(math.radians(lon)) * 5.0
        
        # Seasonal variation
        if month in [12, 1, 2]:  # Winter
            wind_speed = base_wind_speed * 1.3
            wave_height = 3.0
        elif month in [6, 7, 8]:  # Summer
            wind_speed = base_wind_speed * 0.8
            wave_height = 1.5
        else:  # Spring/Fall
            wind_speed = base_wind_speed
            wave_height = 2.0
            
        return WeatherCondition(
            wind_speed=wind_speed + wind_variation,
            wind_direction=base_wind_dir,
            wave_height=wave_height,
            timestamp=timestamp
        )
    
    def calculate_speed_adjustment(
        self,
        base_speed: float,
        weather: WeatherCondition,
        course: float
    ) -> float:
        """
        Calculate speed adjustment based on weather conditions.
        
        Args:
            base_speed: Vessel's base speed (knots)
            weather: Weather conditions
            course: Vessel's course (degrees)
            
        Returns:
            Adjusted speed (knots)
        """
        # Calculate relative wind direction
        relative_wind = abs(weather.wind_direction - course)
        if relative_wind > 180:
            relative_wind = 360 - relative_wind
            
        # Head wind penalty, tail wind bonus
        if relative_wind < 45:  # Tail wind
            wind_factor = 1.0 + (weather.wind_speed / base_speed) * 0.05
        elif relative_wind > 135:  # Head wind
            wind_factor = 1.0 - (weather.wind_speed / base_speed) * 0.15
        else:  # Beam wind
            wind_factor = 1.0 - (weather.wind_speed / base_speed) * 0.08
            
        # Wave height penalty
        if weather.wave_height > 4.0:
            wave_factor = 0.85
        elif weather.wave_height > 2.5:
            wave_factor = 0.95
        else:
            wave_factor = 1.0
            
        adjusted_speed = base_speed * wind_factor * wave_factor
        return max(adjusted_speed, base_speed * 0.5)  # Never below 50% of base speed
    
    def optimize_route_with_weather(
        self,
        route_points: List[Tuple[float, float]],
        base_speed: float,
        departure_time: Optional[datetime] = None
    ) -> Dict:
        """
        Optimize route considering weather conditions.
        
        Args:
            route_points: List of (lat, lon) waypoints
            base_speed: Vessel's base speed in knots
            departure_time: Departure time (defaults to now)
            
        Returns:
            Dictionary with weather-adjusted route data
        """
        if departure_time is None:
            departure_time = datetime.now()
            
        adjusted_segments = []
        current_time = departure_time
        total_time_hours = 0.0
        total_distance_km = 0.0
        
        for i in range(len(route_points) - 1):
            start = route_points[i]
            end = route_points[i + 1]
            
            # Calculate distance
            distance_km = self._haversine_distance(start, end)
            
            # Calculate course
            course = self._calculate_course(start, end)
            
            # Get weather forecast for segment midpoint
            mid_lat = (start[0] + end[0]) / 2
            mid_lon = (start[1] + end[1]) / 2
            weather = self.get_weather_forecast(mid_lat, mid_lon, current_time)
            
            # Adjust speed for weather
            adjusted_speed = self.calculate_speed_adjustment(
                base_speed, weather, course
            )
            
            # Calculate time for this segment
            distance_nm = distance_km / 1.852
            segment_time_hours = distance_nm / adjusted_speed
            
            adjusted_segments.append({
                "start": start,
                "end": end,
                "distance_km": distance_km,
                "distance_nm": distance_nm,
                "base_speed": base_speed,
                "adjusted_speed": adjusted_speed,
                "course": course,
                "time_hours": segment_time_hours,
                "weather": {
                    "wind_speed": weather.wind_speed,
                    "wind_direction": weather.wind_direction,
                    "wave_height": weather.wave_height,
                    "forecast_time": weather.timestamp.isoformat()
                }
            })
            
            total_distance_km += distance_km
            total_time_hours += segment_time_hours
            current_time += timedelta(hours=segment_time_hours)
            
        return {
            "route_points": route_points,
            "segments": adjusted_segments,
            "total_distance_km": round(total_distance_km, 2),
            "total_distance_nm": round(total_distance_km / 1.852, 2),
            "total_time_hours": round(total_time_hours, 2),
            "total_time_days": round(total_time_hours / 24, 2),
            "departure_time": departure_time.isoformat(),
            "arrival_time": current_time.isoformat(),
            "average_speed": round(total_distance_km / 1.852 / total_time_hours, 2) if total_time_hours > 0 else 0,
            "optimization_type": "weather_aware"
        }
    
    def _haversine_distance(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """Calculate great circle distance in kilometers."""
        lat1, lon1 = math.radians(point1[0]), math.radians(point1[1])
        lat2, lon2 = math.radians(point2[0]), math.radians(point2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return 6371 * c  # Earth radius in km
    
    def _calculate_course(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float]
    ) -> float:
        """Calculate initial course between two points in degrees."""
        lat1, lon1 = math.radians(start[0]), math.radians(start[1])
        lat2, lon2 = math.radians(end[0]), math.radians(end[1])
        
        dlon = lon2 - lon1
        
        y = math.sin(dlon) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
        
        course = math.degrees(math.atan2(y, x))
        return (course + 360) % 360


# Singleton instance
weather_router = WeatherRouter()
