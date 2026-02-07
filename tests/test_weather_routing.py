"""
Unit tests for weather routing functionality.
"""
import pytest
import sys
from datetime import datetime
sys.path.insert(0, r'c:\Users\KARTHIKEYAN D\Desktop\AI-SHIP-ROUTE-RECOVERY')

from backend.app.utils.weather_routing import weather_router, WeatherCondition


class TestWeatherRouter:
    """Tests for weather routing functionality."""
    
    def test_get_weather_forecast(self):
        """Test weather forecast generation."""
        weather = weather_router.get_weather_forecast(
            lat=1.29,  # Singapore
            lon=103.85,
            timestamp=datetime.now()
        )
        assert isinstance(weather, WeatherCondition)
        assert weather.wind_speed > 0
        assert 0 <= weather.wind_direction <= 360
        assert weather.wave_height >= 0
    
    def test_speed_adjustment_headwind(self):
        """Test speed reduction in headwind."""
        weather = WeatherCondition(
            wind_speed=20.0,
            wind_direction=0.0,  # North wind
            wave_height=2.0,
            timestamp=datetime.now()
        )
        base_speed = 12.0
        course = 0.0  # Sailing north (into wind)
        
        adjusted = weather_router.calculate_speed_adjustment(
            base_speed, weather, course
        )
        # Should be slower in headwind
        assert adjusted < base_speed
    
    def test_speed_adjustment_tailwind(self):
        """Test speed increase in tailwind."""
        weather = WeatherCondition(
            wind_speed=15.0,
            wind_direction=0.0,  # North wind
            wave_height=1.5,
            timestamp=datetime.now()
        )
        base_speed = 12.0
        course = 180.0  # Sailing south (with wind)
        
        adjusted = weather_router.calculate_speed_adjustment(
            base_speed, weather, course
        )
        # Should be faster in tailwind
        assert adjusted >= base_speed
    
    def test_optimize_route_with_weather(self):
        """Test full weather routing optimization."""
        route_points = [
            (1.29, 103.85),  # Singapore
            (22.28, 114.16),  # Hong Kong
            (31.23, 121.47)  # Shanghai
        ]
        
        result = weather_router.optimize_route_with_weather(
            route_points=route_points,
            base_speed=12.0,
            departure_time=datetime.now()
        )
        
        assert "route_points" in result
        assert "segments" in result
        assert "total_distance_km" in result
        assert "total_time_hours" in result
        assert result["total_distance_km"] > 0
        assert result["total_time_hours"] > 0
        assert len(result["segments"]) == len(route_points) - 1
    
    def test_weather_impact_on_segments(self):
        """Test that weather affects different segments differently."""
        route_points = [
            (0, 0),
            (10, 0),
            (10, 10),
            (0, 10)
        ]
        
        result = weather_router.optimize_route_with_weather(
            route_points=route_points,
            base_speed=12.0
        )
        
        segments = result["segments"]
        # Check that segments have different adjusted speeds
        speeds = [seg["adjusted_speed"] for seg in segments]
        assert len(set(speeds)) > 1  # Not all speeds are identical


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
