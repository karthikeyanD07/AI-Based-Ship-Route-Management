"""Service layer for ship tracking and management."""
import pandas as pd
import numpy as np
import math
import random
import asyncio
import logging
from typing import Dict, List, Optional
from pathlib import Path
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from backend.app.config.settings import settings
from backend.app.models.schemas import ShipPosition
from backend.app.utils.ocean_detection import ocean_detector
from backend.app.services.db_service import db_service
# Removed get_db import - using db_service methods directly

logger = logging.getLogger(__name__)


class ShipService:
    """Service for managing ship positions and movements."""
    
    def __init__(self):
        self.ship_positions: Dict[int, Dict] = {}
        self.ais_data: Optional[pd.DataFrame] = None
        self._update_task: Optional[asyncio.Task] = None
        self._running = False
        self._lock = Lock()  # Thread safety lock
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ship_update")
        try:
            self._load_ais_data()
            self._initialize_ships()
            logger.info(f"ShipService initialized with {len(self.ship_positions)} ships")
        except Exception as e:
            logger.error(f"Failed to initialize ShipService: {e}", exc_info=True)
            # Don't crash - allow app to start with empty ship list
            self.ship_positions = {}
            self.ais_data = None
    
    def _load_ais_data(self):
        """Load AIS data from CSV file with size limits."""
        csv_file = settings.CSV_DATA_FILE
        
        if not Path(csv_file).exists():
            # Try alternative file
            csv_file = "trip9.csv"
            if not Path(csv_file).exists():
                logger.warning(f"CSV file not found: {settings.CSV_DATA_FILE} or trip9.csv")
                raise FileNotFoundError(f"CSV file not found: {settings.CSV_DATA_FILE} or trip9.csv")
        
        # Check file size
        file_size = Path(csv_file).stat().st_size
        max_size = 500 * 1024 * 1024  # 500MB
        
        # For large files, use streaming approach
        if file_size > max_size:
            logger.warning(f"CSV file is large ({file_size / 1024 / 1024:.2f}MB), using streaming")
            # Stream and sample data instead of loading all
            chunks = []
            chunk_size = 10000
            max_rows = settings.MAX_SHIPS_DISPLAY * 10  # Limit rows loaded
            
            for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
                chunks.append(chunk)
                total_rows = sum(len(c) for c in chunks)
                if total_rows >= max_rows:
                    logger.info(f"Loaded {total_rows} rows, limiting further loading")
                    break
            
            self.ais_data = pd.concat(chunks, ignore_index=True)
        else:
            logger.info(f"Loading AIS data from {csv_file} ({file_size / 1024 / 1024:.2f}MB)")
            # For smaller files, load normally but still limit
            self.ais_data = pd.read_csv(csv_file, nrows=settings.MAX_SHIPS_DISPLAY * 10)
        
        # Standardize column names
        column_mapping = {
            "ID": "MMSI",
            "MMSI": "MMSI",
            "Latitude": "lat",
            "LAT": "lat",
            "Longitude": "lon",
            "LON": "lon",
            "Speed": "sog",
            "SOG": "sog",
            "Course": "cog",
            "COG": "cog",
            "ShipStatus": "status",
            "Status": "status"
        }
        
        self.ais_data.rename(
            columns={k: v for k, v in column_mapping.items() if k in self.ais_data.columns},
            inplace=True
        )
        
        # Ensure required columns exist
        required_columns = {"MMSI", "lat", "lon", "sog", "cog", "status"}
        missing_columns = required_columns - set(self.ais_data.columns)
        
        if missing_columns:
            # Add missing columns with defaults
            if "cog" in missing_columns:
                self.ais_data["cog"] = np.random.uniform(0, 360, len(self.ais_data))
            if "status" in missing_columns:
                self.ais_data["status"] = "Unknown"
        
        # Fix NaN values
        self.ais_data.replace([np.nan, np.inf, -np.inf], 0, inplace=True)
        self.ais_data.fillna({
            "sog": 0.0,
            "cog": 0.0,
            "status": "Unknown",
            "lat": 0.0,
            "lon": 0.0
        }, inplace=True)
        
        # Convert numeric columns
        for col in ["sog", "cog", "lat", "lon", "MMSI"]:
            self.ais_data[col] = pd.to_numeric(self.ais_data[col], errors="coerce").fillna(0.0)
    
    def _initialize_ships(self):
        """Initialize ship positions from AIS data."""
        if self.ais_data is None or self.ais_data.empty:
            return
        
        # Select unique ships
        unique_ships = self.ais_data["MMSI"].drop_duplicates()
        num_ships = min(settings.MAX_SHIPS_DISPLAY, len(unique_ships))
        selected_ships = unique_ships.sample(n=num_ships, random_state=42).tolist()
        
        # Initialize positions
        for _, row in self.ais_data[self.ais_data["MMSI"].isin(selected_ships)].iterrows():
            lat, lon = float(row["lat"]), float(row["lon"])
            
            # Ensure ship starts in water
            if not ocean_detector.is_ocean(lat, lon):
                lat, lon = self._adjust_to_ocean(lat, lon)
            
            # Assign speed if missing
            sog = float(row["sog"])
            if sog == 0:
                sog = random.uniform(5, 15)
            
            mmsi = int(row["MMSI"])
            # Validate coordinates
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                logger.warning(f"Invalid coordinates for ship {mmsi}: lat={lat}, lon={lon}")
                continue
            
            ship_data = {
                "latitude": lat,
                "longitude": lon,
                "sog": sog,
                "cog": float(row["cog"]) % 360,  # Normalize COG to 0-360
                "status": str(row["status"])
            }
            self.ship_positions[mmsi] = ship_data
    
    def _adjust_to_ocean(self, lat: float, lon: float) -> tuple:
        """Adjust coordinates to nearest ocean point."""
        if ocean_detector.is_ocean(lat, lon):
            return lat, lon
        
        # Try small adjustments
        for offset in [0.1, 0.2, 0.5, 1.0]:
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                test_lat = lat + offset * math.cos(rad)
                test_lon = lon + offset * math.sin(rad)
                
                if ocean_detector.is_ocean(test_lat, test_lon):
                    return test_lat, test_lon
        
        return lat, lon  # Fallback
    
    def move_ship(self, mmsi: int):
        """
        Move a ship based on its speed and course.
        Thread-safe operation.
        
        Constants:
        - 0.0002: Conversion factor from knots to degrees per update cycle
          (approximate: 1 knot ≈ 0.000278 degrees/sec, scaled for 3s updates)
        """
        with self._lock:
            if mmsi not in self.ship_positions:
                return
            
            ship = self.ship_positions[mmsi].copy()  # Copy to avoid holding lock during computation
        
        # Don't move if moored
        if ship["sog"] == 0:
            return
        
        # Convert speed to movement (knots to degrees approximation)
        # 0.0002 = conversion factor: knots * time_interval * conversion_rate
        distance = ship["sog"] * 0.0002
        angle = math.radians(ship["cog"])
        
        # Calculate new position
        lat_change = distance * math.cos(angle)
        lon_change = distance * math.sin(angle)
        
        new_lat = ship["latitude"] + lat_change
        new_lon = ship["longitude"] + lon_change
        
        # Normalize longitude
        if new_lon > 180:
            new_lon -= 360
        elif new_lon < -180:
            new_lon += 360
        
        # Ensure ship stays in ocean
        if ocean_detector.is_ocean(new_lat, new_lon):
            with self._lock:
                if mmsi in self.ship_positions:  # Check again after lock
                    self.ship_positions[mmsi]["latitude"] = new_lat
                    self.ship_positions[mmsi]["longitude"] = new_lon
        else:
            # Adjust course if hitting land
            with self._lock:
                if mmsi in self.ship_positions:
                    self.ship_positions[mmsi]["cog"] = (ship["cog"] + random.uniform(-10, 10)) % 360
    
    async def update_all_ships(self):
        """Update positions of all ships using thread pool for CPU-bound work."""
        self._running = True
        logger.info("Starting ship position update task")
        loop = asyncio.get_event_loop()
        max_queue_size = 1000  # Backpressure: limit queue size
        
        while self._running:
            try:
                # Get ship list atomically
                with self._lock:
                    ship_mmsis = list(self.ship_positions.keys())
                
                # Backpressure: if too many ships, skip this cycle
                if len(ship_mmsis) > max_queue_size:
                    logger.warning(f"Too many ships ({len(ship_mmsis)}), skipping update cycle")
                    await asyncio.sleep(settings.SHIP_UPDATE_INTERVAL)
                    continue
                
                # Process ships in parallel using thread pool
                if ship_mmsis:
                    # Run CPU-bound move_ship operations in thread pool
                    futures = [
                        loop.run_in_executor(self._executor, self.move_ship, mmsi)
                        for mmsi in ship_mmsis[:max_queue_size]  # Limit to queue size
                    ]
                    # Wait for all updates to complete
                    await asyncio.gather(*futures, return_exceptions=True)
                
                # Periodically save to database (every 10 cycles = 30 seconds)
                if db_service.is_available() and len(ship_mmsis) > 0:
                    try:
                        # Save a batch of ships to database (async with proper session management)
                        ships_to_save = self.get_all_ships(limit=100)
                        save_tasks = [
                            db_service.save_ship_position_async(ship_pos)
                            for ship_pos in ships_to_save[:10]  # Save 10 at a time
                        ]
                        # Run saves in parallel
                        await asyncio.gather(*save_tasks, return_exceptions=True)
                    except Exception as e:
                        logger.debug(f"Database save error: {e}")
                
                await asyncio.sleep(settings.SHIP_UPDATE_INTERVAL)
            except asyncio.CancelledError:
                logger.info("Ship update task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in ship update loop: {e}", exc_info=True)
                await asyncio.sleep(settings.SHIP_UPDATE_INTERVAL)  # Continue despite errors
    
    def stop_updates(self):
        """Stop the background update task."""
        self._running = False
        if self._update_task:
            self._update_task.cancel()
        self._executor.shutdown(wait=True, timeout=5)
    
    def get_all_ships(self, limit: Optional[int] = None, offset: int = 0) -> List[ShipPosition]:
        """
        Get all ship positions with pagination support.
        
        Args:
            limit: Maximum number of ships to return
            offset: Number of ships to skip (for pagination)
        """
        ships = []
        count = 0
        skipped = 0
        
        # Thread-safe read
        with self._lock:
            ship_items = list(self.ship_positions.items())
        
        for mmsi, ship in ship_items:
            # Pagination: skip until we reach offset
            if skipped < offset:
                skipped += 1
                continue
            
            if limit and count >= limit:
                break
            
            # Get ship metadata from AIS data
            ship_data = None
            if self.ais_data is not None:
                ship_rows = self.ais_data[self.ais_data["MMSI"] == mmsi]
                if not ship_rows.empty:
                    ship_data = ship_rows.iloc[0].to_dict()
            
            ship_position = ShipPosition(
                MMSI=mmsi,
                latitude=float(ship["latitude"]),
                longitude=float(ship["longitude"]),
                sog=float(ship["sog"]),
                cog=float(ship["cog"]),
                status=ship["status"],
                name=ship_data.get("name") if ship_data else None
            )
            ships.append(ship_position)
            count += 1
        
        return ships
    
    def get_ship_by_mmsi(self, mmsi: int) -> Optional[ShipPosition]:
        """Get a specific ship by MMSI (thread-safe)."""
        with self._lock:
            if mmsi not in self.ship_positions:
                return None
            
            ship = self.ship_positions[mmsi].copy()  # Copy to avoid holding lock
        
        return ShipPosition(
            MMSI=mmsi,
            latitude=float(ship["latitude"]),
            longitude=float(ship["longitude"]),
            sog=float(ship["sog"]),
            cog=float(ship["cog"]),
            status=ship["status"]
        )


# Global service instance - initialized on module load
# If initialization fails, service will have empty ship list but app can still start
try:
    ship_service = ShipService()
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to initialize ShipService: {e}", exc_info=True)
    # Create empty service instance so app can start
    ship_service = ShipService.__new__(ShipService)
    ship_service.ship_positions = {}
    ship_service.ais_data = None
    ship_service._update_task = None
    ship_service._running = False
    ship_service._lock = Lock()
    ship_service._executor = ThreadPoolExecutor(max_workers=4)