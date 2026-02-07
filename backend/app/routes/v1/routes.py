"""API v1 routes for route optimization (versioned)."""
from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Optional
import logging
from app.services.route_service import route_service
from app.services.db_service import db_service
from app.models.schemas import OptimizeRouteRequest, OptimizedRouteResponse
from app.middleware.per_user_rate_limit import per_user_limit
from app.auth.security import get_current_user
from app.utils.audit_logger import audit_logger

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["routes-v1"])


@router.post("/routes/optimize", response_model=OptimizedRouteResponse)
@per_user_limit("30/minute")  # Per-user rate limiting
async def get_optimized_route_v1(
    request: Request,
    route_request: OptimizeRouteRequest,
    user: Optional[dict] = Depends(get_current_user)  # Optional auth
):
    """
    Get optimized route between two ports (v1).
    Authentication is optional but recommended.
    """
    try:
        result = route_service.optimize_route(
            ship_id=route_request.ship_id,
            start_port=route_request.start,
            end_port=route_request.end
        )
        
        # Save route to database if available
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
        
        # Audit log
        if user:
            audit_logger.log_action(
                action="route_optimize",
                request=request,
                user_id=int(user.get("sub")) if user.get("sub") else None,
                username=user.get("username"),
                resource="route",
                resource_id=route_request.ship_id,
                status_code=200
            )
        
        return result
    except ValueError as e:
        logger.warning(f"Route optimization validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error optimizing route: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error optimizing route")
