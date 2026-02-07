"""API routes for weather data."""
from fastapi import APIRouter, HTTPException, Query, Request
from app.services.weather_service import weather_service
from app.middleware.rate_limit import limiter
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["weather"])


@router.get("/weather")
@limiter.limit("60/minute")
async def get_weather(
    request: Request,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude")
):
    """
    Get weather data for a specific location.
    
    Args:
        lat: Latitude in degrees
        lon: Longitude in degrees
        
    Returns:
        Weather data dictionary
    """
    try:
        weather_data = await weather_service.get_weather_at_location(lat, lon)
        if weather_data is None:
            raise HTTPException(
                status_code=503,
                detail="Weather service unavailable. Check API key configuration."
            )
        return weather_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching weather: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching weather data")
