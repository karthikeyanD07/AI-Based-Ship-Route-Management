from starlette.middleware.base import BaseHTTPMiddleware 
from starlette.requests import Request 
 
class UserContextMiddleware(BaseHTTPMiddleware): 
    async def dispatch(self, request: Request, call_next): 
        # Auth is handled at route level, not middleware 
        request.state.user = None 
        response = await call_next(request) 
        return response 
