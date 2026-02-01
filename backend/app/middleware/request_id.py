"""Request ID tracking middleware using contextvars for thread-safety."""
import uuid
import logging
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)

# Context variable for request ID (thread-safe)
_request_id: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class RequestIDFilter(logging.Filter):
    """Logging filter that adds request ID from context."""
    
    def filter(self, record):
        request_id = _request_id.get()
        record.request_id = request_id or "N/A"
        return True


# Add filter to root logger
logging.getLogger().addFilter(RequestIDFilter())


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add request ID to all requests for tracing (thread-safe)."""
    
    async def dispatch(self, request: Request, call_next):
        # Generate or get request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Set in context (thread-safe)
        _request_id.set(request_id)
        
        # Add to request state
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Clear context
            _request_id.set(None)
