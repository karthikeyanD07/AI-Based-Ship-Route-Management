"""API routes for ship tracking."""
from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional
import logging
from app.services.ship_service import ship_service
from app.models.schemas import ShipTrafficResponse, ShipPosition
from app.middleware.rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["ships"])


@router.get("/ship-traffic", response_model=ShipTrafficResponse)
@limiter.limit("60/minute")
async def get_ship_traffic(
    request: Request,
    limit: Optional[int] = Query(None, ge=1, le=1000),
    offset: int = Query(0, ge=0, description="Number of ships to skip for pagination")
):
    """
    Get real-time positions of all tracked ships.
    
    Args:
        limit: Maximum number of ships to return (optional)
        
    Returns:
        ShipTrafficResponse with list of ship positions
    """
    try:
        ships = ship_service.get_all_ships(limit=limit, offset=offset)
        total_count = len(ship_service.ship_positions)
        return {
            "ships": ships,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + (limit or total_count)) < total_count
        }
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching ship data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching ship data")


@router.get("/ship/{mmsi}", response_model=ShipPosition)
@limiter.limit("60/minute")
async def get_ship_by_mmsi(request: Request, mmsi: int):
    """
    Get real-time position of a specific ship by MMSI.
    
    Args:
        mmsi: Maritime Mobile Service Identity number
        
    Returns:
        ShipPosition with current ship data
    """
    try:
        ship = ship_service.get_ship_by_mmsi(mmsi)
        if ship is None:
            raise HTTPException(status_code=404, detail=f"Ship with MMSI {mmsi} not found")
        return ship
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ship data: {str(e)}")
