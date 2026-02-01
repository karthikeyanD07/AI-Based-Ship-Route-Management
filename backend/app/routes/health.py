"""Health check and status endpoints."""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
from backend.app.services.db_service import db_service
from backend.app.services.weather_service import weather_service
from backend.app.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Ship Route Management API"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with dependency verification."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AI Ship Route Management API",
        "dependencies": {}
    }
    
    # Check database - ACTUAL CONNECTIVITY TEST
    try:
        db_available = db_service.is_available()
        if db_available:
            # Actually test the connection
            from backend.app.models.database import get_db_session
            from sqlalchemy import text
            try:
                with get_db_session() as db:
                    result = db.execute(text("SELECT 1")).scalar()
                    if result == 1:
                        health_status["dependencies"]["database"] = {
                            "status": "healthy",
                            "configured": True,
                            "connected": True
                        }
                    else:
                        raise Exception("Database query returned unexpected result")
            except Exception as conn_error:
                health_status["dependencies"]["database"] = {
                    "status": "unhealthy",
                    "configured": True,
                    "connected": False,
                    "error": str(conn_error) if settings.DEBUG else "Connection failed"
                }
                health_status["status"] = "degraded"
        else:
            health_status["dependencies"]["database"] = {
                "status": "not_configured",
                "configured": False
            }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["dependencies"]["database"] = {
            "status": "error",
            "error": str(e) if settings.DEBUG else "Database check failed"
        }
        health_status["status"] = "degraded"
    
    # Check weather service - ACTUAL CONNECTIVITY TEST
    try:
        weather_available = bool(weather_service.api_key)
        if weather_available:
            # Test actual API call (with timeout)
            import asyncio
            try:
                test_result = await asyncio.wait_for(
                    weather_service.get_weather_at_location(0.0, 0.0),
                    timeout=5.0
                )
                health_status["dependencies"]["weather_api"] = {
                    "status": "healthy" if test_result else "unhealthy",
                    "configured": True,
                    "connected": test_result is not None
                }
                if not test_result:
                    health_status["status"] = "degraded"
            except asyncio.TimeoutError:
                health_status["dependencies"]["weather_api"] = {
                    "status": "timeout",
                    "configured": True,
                    "connected": False
                }
                health_status["status"] = "degraded"
            except Exception as api_error:
                health_status["dependencies"]["weather_api"] = {
                    "status": "error",
                    "configured": True,
                    "connected": False,
                    "error": str(api_error) if settings.DEBUG else "API call failed"
                }
                health_status["status"] = "degraded"
        else:
            health_status["dependencies"]["weather_api"] = {
                "status": "not_configured",
                "configured": False
            }
    except Exception as e:
        logger.error(f"Weather service health check failed: {e}")
        health_status["dependencies"]["weather_api"] = {
            "status": "error",
            "error": str(e) if settings.DEBUG else "Weather service check failed"
        }
    
    return health_status


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Ship Route Management API",
        "version": "1.0.0",
        "docs": "/docs"
    }
