"""Main FastAPI application entry point."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import asyncio
import logging

from backend.app.config.settings import settings
from backend.app.routes import ships, routes, health, weather, websocket, auth
from backend.app.routes.v1 import ships as ships_v1, routes as routes_v1, weather as weather_v1
from backend.app.routes.websocket import manager as websocket_manager
from backend.app.middleware.rate_limit import limiter
from backend.app.middleware.error_handler import error_handler, validation_error_handler
from backend.app.middleware.request_id import RequestIDMiddleware
from backend.app.middleware.security_headers import SecurityHeadersMiddleware
from backend.app.middleware.input_sanitizer import InputSanitizerMiddleware
from backend.app.middleware.audit_middleware import AuditMiddleware
from backend.app.middleware.user_context import UserContextMiddleware
from backend.app.services.weather_service import weather_service
from backend.app.utils.structured_logging import setup_structured_logging

# Setup structured logging
setup_structured_logging()
logger = logging.getLogger(__name__)

# Import ship_service after logging is configured
from backend.app.services.ship_service import ship_service

# Initialize FastAPI app
app = FastAPI(
    title="AI Ship Route Management API",
    description="Real-time ship tracking and route optimization system",
    version="1.0.0"
)

# Add security middleware (order matters!)
app.add_middleware(SecurityHeadersMiddleware)  # First - add security headers
app.add_middleware(RequestIDMiddleware)  # Second - add request IDs
app.add_middleware(UserContextMiddleware)  # Third - add user context
app.add_middleware(InputSanitizerMiddleware)  # Fourth - sanitize input
app.add_middleware(AuditMiddleware)  # Fifth - audit logging

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add rate limiting state
app.state.limiter = limiter

# Add error handlers
app.add_exception_handler(StarletteHTTPException, error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(Exception, error_handler)

# Include routers
app.include_router(health.router)  # Health checks (no version)
app.include_router(auth.router)  # Authentication routes (v1)

# Legacy routes (backward compatibility - no version prefix)
app.include_router(ships.router)
app.include_router(routes.router)
app.include_router(weather.router)

# Versioned routes (v1)
app.include_router(ships_v1.router)
app.include_router(routes_v1.router)
app.include_router(weather_v1.router)

# WebSocket (no version)
app.include_router(websocket.router)


@app.on_event("startup")
async def startup_event():
    """Startup tasks."""
    logger.info("Starting AI Ship Route Management API")
    
    # Start message queue
    from backend.app.utils.message_queue import message_queue
    message_queue.start()
    
    # Start background task for ship position updates
    if ship_service.ship_positions:
        task = asyncio.create_task(ship_service.update_all_ships())
        ship_service._update_task = task
        logger.info(f"Started ship update task for {len(ship_service.ship_positions)} ships")
    else:
        logger.warning("No ships loaded - ship tracking disabled")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown tasks."""
    logger.info("Shutting down API")
    ship_service.stop_updates()
    await weather_service.close()  # Close HTTP client
    await websocket_manager.close_all()  # Close all WebSocket connections gracefully
    
    # Stop message queue
    from backend.app.utils.message_queue import message_queue
    await message_queue.stop()