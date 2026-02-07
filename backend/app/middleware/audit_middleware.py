"""Audit logging middleware."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from starlette.responses import Response
from app.utils.audit_logger import audit_logger
import logging

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests for audit trail."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip audit for health checks and metrics
        if request.url.path in ["/health", "/health/detailed", "/metrics", "/docs", "/openapi.json", "/"]:
            return await call_next(request)
        
        # Get user info if authenticated (from request state set by UserContextMiddleware)
        user = getattr(request.state, "user", None)
        user_id = int(user.get("sub")) if user and user.get("sub") else None
        username = user.get("username") if user else None
        
        # Determine action from request
        action = f"{request.method.lower()}_{request.url.path.replace('/', '_').replace('-', '_')}"
        resource = request.url.path.split("/")[-1] if request.url.path else None
        
        # Process request
        response = await call_next(request)
        
        # Log audit event
        audit_logger.log_action(
            action=action,
            request=request,
            user_id=user_id,
            username=username,
            resource=resource,
            status_code=response.status_code
        )
        
        return response
