"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List


class ShipPosition(BaseModel):
    """Ship position data model."""
    MMSI: int
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    sog: float = Field(..., ge=0, description="Speed over ground in knots")
    cog: float = Field(..., ge=0, le=360, description="Course over ground in degrees")
    status: str = "Unknown"
    name: Optional[str] = None


class ShipTrafficResponse(BaseModel):
    """Response model for ship traffic endpoint with pagination."""
    ships: List[ShipPosition]
    total: int
    limit: Optional[int] = None
    offset: int = 0
    has_more: bool = False


class OptimizeRouteRequest(BaseModel):
    """Request model for route optimization."""
    ship_id: str = Field(..., description="Ship identifier (MMSI)")
    start: str = Field(..., description="Start port name")
    end: str = Field(..., description="End port name")


class RoutePoint(BaseModel):
    """Single point in a route."""
    latitude: float
    longitude: float


class OptimizedRouteResponse(BaseModel):
    """Response model for optimized route."""
    ship_id: str
    optimized_route: List[List[float]]  # List of [lat, lon] pairs
    distance_km: Optional[float] = None
    estimated_time_hours: Optional[float] = None
