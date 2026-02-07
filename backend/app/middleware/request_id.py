from contextvars import ContextVar 
from typing import Optional 
from starlette.middleware.base import BaseHTTPMiddleware 
from starlette.requests import Request 
from starlette.responses import Response 
import uuid 
 
_request_id = ContextVar("request_id", default=None) 
 
class RequestIDMiddleware(BaseHTTPMiddleware): 
    async def dispatch(self, request: Request, call_next): 
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())) 
        _request_id.set(request_id) 
        response = await call_next(request) 
        response.headers["X-Request-ID"] = request_id 
        return response 
