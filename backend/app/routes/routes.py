"""API routes for route optimization and comparison."""
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from typing import Optional
from ..services.route_service import route_service
from ..data.ports_database import port_db
from ..models.schemas import OptimizedRouteResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api", tags=["routes"])


class CompareRoutesRequest(BaseModel):
    ship_id: str
    start_port: str
    end_port: str
    vessel_type: str = "container"
    vessel_size: str = "medium"
    fuel_type: str = "HFO"


class WeatherRouteRequest(BaseModel):
    ship_id: str
    start: str  # matches what the frontend sends
    end: str    # matches what the frontend sends
    vessel_speed: float = 12.0


class EmissionsRequest(BaseModel):
    distance_km: float
    speed_knots: float = 12.0
    vessel_type: str = "container"
    vessel_size: str = "medium"
    fuel_type: str = "HFO"


@router.post("/get_optimized_route/", response_model=OptimizedRouteResponse)
@limiter.limit("30/minute")
async def get_optimized_route(
    request: Request,
    ship_id: str,
    start: str,
    end: str,
    optimization_level: str = Query("simple", regex="^(simple|advanced)$")
):
    """
    Optimize route between two ports (original endpoint - backward compatible).
    
    Args:
        ship_id: Ship MMSI or identifier
        start: Starting port name
        end: Destination port name
        optimization_level: 'simple' (default, fast) or 'advanced' (future: weather-optimized)
        
    Returns:
        OptimizedRouteResponse with route points and metadata
        
    Note:
        - 'simple': Uses great-circle optimization (current implementation)
        - 'advanced': Reserved for future weather routing integration
    """
    try:
        result = route_service.optimize_route(ship_id, start, end)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route optimization failed: {str(e)}")


@router.get("/ports/search")
@limiter.limit("60/minute")
async def search_ports(
    request: Request,
    q: str = Query(..., min_length=2, description="Search query")
):
    """
    Search available ports by name.
    
    Args:
        q: Search query (minimum 2 characters)
        
    Returns:
        List of matching port names
    """
    try:
        results = route_service.search_ports(q)
        return {
            "query": q,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ports/all")
@limiter.limit("60/minute")
async def get_all_ports(request: Request):
    """Get list of all available ports."""
    try:
        ports = route_service.get_all_ports()
        return {
            "ports": ports,
            "count": len(ports)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/route/compare")
@limiter.limit("20/minute")
async def compare_routes(
    request: Request,
    body: CompareRoutesRequest
):
    """
    Compare multiple route optimization strategies.
    
    Returns three route options:
    - **Fastest**: Shortest time, higher fuel consumption (15 knots)
    - **Balanced**: Good balance of time and efficiency (12 knots)
    - **Greenest**: Lowest emissions, slower speed (10 knots)
    """
    try:
        result = route_service.compare_routes(
            body.ship_id, body.start_port, body.end_port,
            body.vessel_type, body.vessel_size
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Route comparison failed: {str(e)}")


@router.post("/route/emissions")
@limiter.limit("60/minute")
async def calculate_emissions(
    request: Request,
    body: EmissionsRequest
):
    """
    Calculate CO2 emissions for a voyage.
    Uses IMO Fourth GHG Study 2020 emission factors.
    """
    try:
        from app.utils.emissions import emissions_calc
        
        result = emissions_calc.calculate_co2_emissions(
            body.distance_km, body.speed_knots, body.vessel_type,
            body.vessel_size, body.fuel_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emissions calculation failed: {str(e)}")


@router.post("/route/weather-optimized")
@limiter.limit("20/minute")
async def get_weather_optimized_route(
    request: Request,
    body: WeatherRouteRequest
):
    """
    Get weather-optimized route with real-time weather considerations.
    Accepts 'start' and 'end' port names (matching the frontend field names).
    """
    try:
        result = route_service.optimize_route_with_weather(
            body.ship_id, body.start, body.end, body.vessel_speed
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather routing failed: {str(e)}")
