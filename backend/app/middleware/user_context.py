"""Middleware to add user context to request state."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from backend.app.auth.security import get_current_user

class UserContextMiddleware(BaseHTTPMiddleware):
    """Add authenticated user to request state."""
    
    async def dispatch(self, request: Request, call_next):
        # Get current user if authenticated
        user = await get_current_user()
        if user:
            request.state.user = user
        else:
            request.state.user = None
        
        response = await call_next(request)
        return response
