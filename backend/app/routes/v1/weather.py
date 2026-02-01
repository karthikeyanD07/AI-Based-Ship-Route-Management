"""API v1 routes for weather data (versioned)."""
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from typing import Optional
import logging
from backend.app.services.weather_service import weather_service
from backend.app.middleware.per_user_rate_limit import per_user_limit
from backend.app.auth.security import get_current_user
from backend.app.utils.audit_logger import audit_logger

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["weather-v1"])


@router.get("/weather")
@per_user_limit("60/minute")  # Per-user rate limiting
async def get_weather_v1(
    request: Request,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    user: Optional[dict] = Depends(get_current_user)  # Optional auth
):
    """
    Get weather data for a specific location (v1).
    Authentication is optional but recommended.
    """
    try:
        weather_data = await weather_service.get_weather_at_location(lat, lon)
        if weather_data is None:
            raise HTTPException(
                status_code=503,
                detail="Weather service unavailable. Check API key configuration."
            )
        
        # Audit log
        if user:
            audit_logger.log_action(
                action="weather_query",
                request=request,
                user_id=int(user.get("sub")) if user.get("sub") else None,
                username=user.get("username"),
                resource="weather",
                details={"lat": lat, "lon": lon},
                status_code=200
            )
        
        return weather_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching weather: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching weather data")
