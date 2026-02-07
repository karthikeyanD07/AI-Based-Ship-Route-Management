"""Database service for persisting ship data with retry logic."""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.database import Ship, Route, get_db_session, init_db
from app.models.schemas import ShipPosition
from app.config.settings import settings
from app.utils.db_retry import retry_db_operation

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations with retry logic."""
    
    def __init__(self):
        self._initialized = False
        try:
            # Only initialize if database URL is configured
            if settings.DATABASE_URL and "postgresql" in settings.DATABASE_URL.lower():
                init_db()
                self._initialized = True
                logger.info("Database initialized successfully")
            else:
                logger.info("Database not configured, using in-memory storage only")
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}. Using in-memory storage.")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Check if database is available."""
        return self._initialized
    
    def _save_ship_position_impl(self, db: Session, ship: ShipPosition) -> Optional[Ship]:
        """Internal implementation of save_ship_position."""
        # Check if ship exists
        db_ship = db.query(Ship).filter(Ship.mmsi == ship.MMSI).first()
        
        if db_ship:
            # Update existing
            db_ship.latitude = ship.latitude
            db_ship.longitude = ship.longitude
            db_ship.sog = ship.sog
            db_ship.cog = ship.cog
            db_ship.status = ship.status
            if ship.name:
                db_ship.name = ship.name
        else:
            # Create new
            db_ship = Ship(
                mmsi=ship.MMSI,
                latitude=ship.latitude,
                longitude=ship.longitude,
                sog=ship.sog,
                cog=ship.cog,
                status=ship.status,
                name=ship.name
            )
            db.add(db_ship)
        
        db.commit()
        db.refresh(db_ship)
        return db_ship
    
    def save_ship_position(self, ship: ShipPosition) -> Optional[Ship]:
        """
        Save or update ship position in database with retry logic.
        Uses proper session management.
        """
        if not self._initialized:
            return None
        
        try:
            with get_db_session() as db:
                return self._save_ship_position_impl(db, ship)
        except Exception as e:
            logger.error(f"Error saving ship position: {e}", exc_info=True)
            return None
    
    async def save_ship_position_async(self, ship: ShipPosition) -> Optional[Ship]:
        """
        Async version with retry logic for background tasks.
        """
        if not self._initialized:
            return None
        
        try:
            def _save():
                with get_db_session() as db:
                    return self._save_ship_position_impl(db, ship)
            
            return await retry_db_operation(_save)
        except Exception as e:
            logger.error(f"Error saving ship position (async): {e}", exc_info=True)
            return None
    
    def get_ship_from_db(self, mmsi: int) -> Optional[Ship]:
        """Get ship from database."""
        if not self._initialized:
            return None
        
        try:
            with get_db_session() as db:
                return db.query(Ship).filter(Ship.mmsi == mmsi).first()
        except Exception as e:
            logger.error(f"Error getting ship from database: {e}", exc_info=True)
            return None
    
    def _save_route_impl(self, db: Session, ship_id: str, start_port: str, end_port: str,
                        route_points: List[List[float]], distance_km: float, 
                        estimated_hours: float) -> Optional[Route]:
        """Internal implementation of save_route."""
        import json
        route = Route(
            ship_id=ship_id,
            start_port=start_port,
            end_port=end_port,
            route_points=json.dumps(route_points),
            distance_km=distance_km,
            estimated_time_hours=estimated_hours
        )
        db.add(route)
        db.commit()
        db.refresh(route)
        return route
    
    def save_route(self, ship_id: str, start_port: str, end_port: str,
                   route_points: List[List[float]], distance_km: float, 
                   estimated_hours: float) -> Optional[Route]:
        """Save route to database with proper session management."""
        if not self._initialized:
            return None
        
        try:
            with get_db_session() as db:
                return self._save_route_impl(
                    db, ship_id, start_port, end_port,
                    route_points, distance_km, estimated_hours
                )
        except Exception as e:
            logger.error(f"Error saving route: {e}", exc_info=True)
            return None


# Global instance
db_service = DatabaseService()
