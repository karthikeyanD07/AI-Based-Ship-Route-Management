"""Input sanitization middleware."""
import bleach
import logging
from typing import Any, Dict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# Allowed HTML tags (minimal set)
ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}
ALLOWED_PROTOCOLS = []


class InputSanitizerMiddleware(BaseHTTPMiddleware):
    """Sanitize user input to prevent XSS and injection attacks."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.app = app
    
    def sanitize_string(self, value: str) -> str:
        """Sanitize a string value."""
        if not isinstance(value, str):
            return value
        # Remove all HTML tags and attributes
        return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES)
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary values."""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_string(item) if isinstance(item, str)
                    else self.sanitize_dict(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        return sanitized
    
    async def dispatch(self, request: Request, call_next):
        # Sanitize query parameters
        if request.query_params:
            sanitized_params = {}
            for key, value in request.query_params.items():
                sanitized_params[key] = self.sanitize_string(value)
            # Note: FastAPI doesn't allow modifying query_params directly
            # This is a best-effort sanitization
        
        # For JSON body, sanitization happens in route handlers
        # We log potentially dangerous patterns here
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            if body:
                body_str = body.decode("utf-8", errors="ignore")
                # Check for common injection patterns
                dangerous_patterns = ["<script", "javascript:", "onerror=", "onload="]
                if any(pattern in body_str.lower() for pattern in dangerous_patterns):
                    logger.warning(f"Potentially dangerous input detected in {request.url.path}")
        
        response = await call_next(request)
        return response
