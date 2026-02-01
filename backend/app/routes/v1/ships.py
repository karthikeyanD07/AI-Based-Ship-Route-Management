"""API v1 routes for ship tracking (versioned)."""
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from typing import Optional as Opt, Optional
import logging
from backend.app.services.ship_service import ship_service
from backend.app.models.schemas import ShipTrafficResponse, ShipPosition
from backend.app.middleware.per_user_rate_limit import per_user_limit
from backend.app.auth.security import get_current_user
from backend.app.utils.audit_logger import audit_logger

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["ships-v1"])


@router.get("/ships", response_model=ShipTrafficResponse)
@per_user_limit("100/minute")  # Per-user rate limiting
async def get_ship_traffic_v1(
    request: Request,
    limit: Opt[int] = Query(None, ge=1, le=1000),
    offset: int = Query(0, ge=0, description="Number of ships to skip for pagination"),
    user: Opt[dict] = Depends(get_current_user)  # Optional auth
):
    """
    Get real-time positions of all tracked ships (v1).
    Authentication is optional but recommended.
    """
    try:
        ships = ship_service.get_all_ships(limit=limit, offset=offset)
        total_count = len(ship_service.ship_positions)
        
        # Audit log
        if user:
            audit_logger.log_action(
                action="ships_list",
                request=request,
                user_id=int(user.get("sub")) if user.get("sub") else None,
                username=user.get("username"),
                resource="ships",
                status_code=200
            )
        
        return {
            "ships": ships,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + (limit or total_count)) < total_count
        }
    except Exception as e:
        logger.error(f"Error fetching ship data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching ship data")


@router.get("/ships/{mmsi}", response_model=ShipPosition)
@per_user_limit("100/minute")
async def get_ship_by_mmsi_v1(
    request: Request,
    mmsi: int,
    user: Opt[dict] = Depends(get_current_user)  # Optional auth
):
    """
    Get real-time position of a specific ship by MMSI (v1).
    Authentication is optional but recommended.
    """
    try:
        ship = ship_service.get_ship_by_mmsi(mmsi)
        if ship is None:
            raise HTTPException(status_code=404, detail=f"Ship with MMSI {mmsi} not found")
        
        # Audit log
        if user:
            audit_logger.log_action(
                action="ship_view",
                request=request,
                user_id=int(user.get("sub")) if user.get("sub") else None,
                username=user.get("username"),
                resource="ship",
                resource_id=str(mmsi),
                status_code=200
            )
        
        return ship
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching ship data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error fetching ship data: {str(e)}")
