"""Graceful degradation utilities."""
import logging
from typing import Callable, Any, Optional
from functools import wraps
from backend.app.services.db_service import db_service
from backend.app.services.weather_service import weather_service

logger = logging.getLogger(__name__)


class DegradedMode:
    """Manages degraded mode state."""
    
    def __init__(self):
        self.db_degraded = False
        self.weather_degraded = False
    
    def is_db_available(self) -> bool:
        """Check if database is available."""
        return db_service.is_available() and not self.db_degraded
    
    def is_weather_available(self) -> bool:
        """Check if weather service is available."""
        return bool(weather_service.api_key) and not self.weather_degraded
    
    def set_db_degraded(self, degraded: bool = True):
        """Set database degraded mode."""
        self.db_degraded = degraded
        logger.warning(f"Database degraded mode: {degraded}")
    
    def set_weather_degraded(self, degraded: bool = True):
        """Set weather service degraded mode."""
        self.weather_degraded = degraded
        logger.warning(f"Weather service degraded mode: {degraded}")


# Global degraded mode manager
degraded_mode = DegradedMode()


def with_fallback(fallback_value: Any = None, fallback_func: Optional[Callable] = None):
    """
    Decorator for graceful degradation with fallback.
    
    Usage:
        @with_fallback(fallback_value={"status": "degraded"})
        async def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Function {func.__name__} failed, using fallback: {e}")
                if fallback_func:
                    return await fallback_func(*args, **kwargs)
                return fallback_value
        return wrapper
    return decorator


def read_only_mode(func: Callable) -> Callable:
    """
    Decorator to make function read-only when database is degraded.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if degraded_mode.db_degraded:
            # Check if this is a write operation
            if func.__name__.startswith(("create", "update", "delete", "save", "post", "put", "patch")):
                raise Exception("Service is in read-only mode. Database is unavailable.")
        return await func(*args, **kwargs)
    return wrapper
