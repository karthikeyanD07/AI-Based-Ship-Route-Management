"""Per-user rate limiting middleware."""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import Callable, Optional
from fastapi import Request
from backend.app.auth.security import get_current_user
from backend.app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


def get_user_identifier(request: Request) -> str:
    """
    Get user identifier for rate limiting.
    Uses user ID if authenticated, otherwise IP address.
    """
    try:
        # Try to get authenticated user
        user = request.state.get("user")
        if user and user.get("sub"):
            return f"user:{user['sub']}"
    except Exception:
        pass
    
    # Fallback to IP address
    return f"ip:{get_remote_address(request)}"


# Per-user rate limiter
per_user_limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"] if settings.RATE_LIMIT_ENABLED else []
)


def per_user_limit(limit: str):
    """
    Decorator for per-user rate limiting.
    
    Usage:
        @per_user_limit("100/minute")
        async def my_endpoint(request: Request):
            ...
    """
    def decorator(func: Callable) -> Callable:
        return per_user_limiter.limit(limit)(func)
    return decorator
