"""Service for weather data integration with circuit breaker."""
import httpx
import logging
from typing import Dict, Optional
from app.config.settings import settings
from app.utils.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

# Circuit breaker for weather API
weather_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    expected_exception=httpx.HTTPError
)


class WeatherService:
    """Service for fetching weather data with connection pooling and circuit breaker."""
    
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        # Reusable HTTP client with connection pooling
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
    
    async def close(self):
        """Close HTTP client."""
        await self._client.aclose()
    
    async def _fetch_weather(self, lat: float, lon: float) -> Optional[Dict]:
        """Internal method to fetch weather (protected by circuit breaker)."""
        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"
        }
        
        response = await self._client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_weather_at_location(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Get weather data for a specific location with circuit breaker protection.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Weather data dictionary or None if error
        """
        if not self.api_key:
            logger.warning("OpenWeather API key not configured")
            return None
        
        try:
            return await weather_circuit_breaker.call(self._fetch_weather, lat, lon)
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return None


# Global service instance
weather_service = WeatherService()
