"""Request size limiting middleware."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette import status

MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """Limit request body size."""
    
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        
        if content_length:
            try:
                size = int(content_length)
                if size > MAX_REQUEST_SIZE:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"error": f"Request too large. Maximum size: {MAX_REQUEST_SIZE / 1024 / 1024}MB"}
                    )
            except ValueError:
                pass  # Invalid content-length, let it through
        
        response = await call_next(request)
        return response
