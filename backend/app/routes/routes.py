"""API routes for route optimization."""
from fastapi import APIRouter, HTTPException, Request
from backend.app.services.route_service import route_service
from backend.app.services.db_service import db_service
from backend.app.models.schemas import OptimizeRouteRequest, OptimizedRouteResponse
from backend.app.middleware.rate_limit import limiter
# Removed get_db import - using db_service methods directly
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["routes"])


@router.post("/get_optimized_route/", response_model=OptimizedRouteResponse)
@limiter.limit("30/minute")
async def get_optimized_route(request: Request, route_request: OptimizeRouteRequest):
    """
    Get optimized route between two ports.
    
    Args:
        request: OptimizeRouteRequest with ship_id, start, and end ports
        
    Returns:
        OptimizedRouteResponse with route points and metadata
    """
    try:
        result = route_service.optimize_route(
            ship_id=route_request.ship_id,
            start_port=route_request.start,
            end_port=route_request.end
        )
        
        # Save route to database if available (with proper session management)
        if db_service.is_available() and result.optimized_route:
            try:
                db_service.save_route(
                    ship_id=route_request.ship_id,
                    start_port=route_request.start,
                    end_port=route_request.end,
                    route_points=result.optimized_route,
                    distance_km=result.distance_km or 0.0,
                    estimated_hours=result.estimated_time_hours or 0.0
                )
            except Exception as e:
                logger.debug(f"Failed to save route to database: {e}")
        
        return result
    except ValueError as e:
        logger.warning(f"Route optimization validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error optimizing route: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error optimizing route")
