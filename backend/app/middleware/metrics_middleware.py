"""Metrics collection middleware."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
from backend.app.utils.metrics import metrics


class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect request metrics."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Increment request counter
        metrics.increment("http_requests_total")
        metrics.increment(f"http_requests_{request.method.lower()}")
        
        try:
            response = await call_next(request)
            
            # Record status code
            metrics.increment(f"http_responses_{response.status_code}")
            
            return response
        except Exception as e:
            metrics.increment("http_errors_total")
            raise
        finally:
            # Record request duration
            duration_ms = (time.time() - start_time) * 1000
            metrics.record_timing("http_request_duration_ms", duration_ms)
