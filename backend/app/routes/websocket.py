"""WebSocket routes for real-time updates with pub/sub pattern."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
import asyncio
import logging
import json
from typing import List, Set, Optional
from threading import Lock
from app.services.ship_service import ship_service
from app.config.settings import settings
from app.utils.message_queue import message_queue

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["websocket"])

# WebSocket connection limits
MAX_WEBSOCKET_CONNECTIONS = 1000


class ConnectionManager:
    """Thread-safe WebSocket connection manager with pub/sub."""
    
    def __init__(self, max_connections: int = MAX_WEBSOCKET_CONNECTIONS):
        self._active_connections: Set[WebSocket] = set()
        self._lock = Lock()  # Thread-safe access
        self._max_connections = max_connections
        self._broadcast_task: Optional[asyncio.Task] = None
        self._running = False
    
    async def connect(self, websocket: WebSocket) -> bool:
        """
        Accept a new WebSocket connection.
        
        Returns:
            True if connected, False if limit reached
        """
        with self._lock:
            if len(self._active_connections) >= self._max_connections:
                logger.warning(f"WebSocket connection limit reached ({self._max_connections})")
                return False
        
        await websocket.accept()
        
        with self._lock:
            self._active_connections.add(websocket)
            count = len(self._active_connections)
        
        logger.info(f"WebSocket connected. Total connections: {count}")
        
        # Start broadcast task if not running
        if not self._running:
            self._start_broadcast_task()
            # Subscribe to message queue for updates
            message_queue.subscribe(self._handle_message)
        
        return True
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection (thread-safe)."""
        with self._lock:
            if websocket in self._active_connections:
                self._active_connections.remove(websocket)
            count = len(self._active_connections)
        
        logger.info(f"WebSocket disconnected. Total connections: {count}")
    
    def _start_broadcast_task(self):
        """Start the broadcast task for pub/sub updates."""
        if self._running:
            return
        
        self._running = True
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())
        logger.info("Started WebSocket broadcast task")
    
    async def _handle_message(self, message: dict):
        """Handle message from message queue."""
        if message.get("type") == "ship_update" and "update" in message:
            await self._broadcast_message(message["update"])
    
    async def _broadcast_loop(self):
        """Main broadcast loop - polls ship service and publishes to queue."""
        last_positions = {}
        
        while self._running:
            try:
                # Get current ship positions
                current_ships = ship_service.get_all_ships(limit=settings.MAX_SHIPS_DISPLAY)
                current_positions = {ship.MMSI: ship for ship in current_ships}
                
                # Find changed positions
                updates = []
                for mmsi, ship in current_positions.items():
                    if mmsi not in last_positions or \
                       last_positions[mmsi].latitude != ship.latitude or \
                       last_positions[mmsi].longitude != ship.longitude:
                        updates.append(ship.model_dump())  # Pydantic v2
                
                # Publish updates to message queue
                if updates:
                    message = {
                        "type": "ship_update",
                        "update": {
                            "type": "update",
                            "ships": updates
                        }
                    }
                    await message_queue.publish(message)
                
                # Send initial positions to new connections
                if last_positions != current_positions:
                    initial_message = {
                        "type": "ship_update",
                        "update": {
                            "type": "initial",
                            "ships": [ship.model_dump() for ship in current_ships]
                        }
                    }
                    await message_queue.publish(initial_message)
                
                last_positions = current_positions
                
                # Heartbeat ping
                await self._send_heartbeat()
                
                await asyncio.sleep(settings.SHIP_UPDATE_INTERVAL)
                
            except asyncio.CancelledError:
                logger.info("Broadcast task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}", exc_info=True)
                await asyncio.sleep(settings.SHIP_UPDATE_INTERVAL)
    
    async def _broadcast_message(self, message: dict, initial_only: bool = False):
        """Broadcast message to all active connections."""
        disconnected = []
        
        # Get snapshot of connections (thread-safe)
        with self._lock:
            connections = list(self._active_connections)
        
        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.debug(f"Error sending to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def _send_heartbeat(self):
        """Send ping to all connections to detect dead ones."""
        disconnected = []
        
        with self._lock:
            connections = list(self._active_connections)
        
        for connection in connections:
            try:
                # Send ping frame
                await connection.send_text(json.dumps({"type": "ping"}))
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)
    
    async def close_all(self):
        """Close all connections gracefully."""
        logger.info("Closing all WebSocket connections")
        self._running = False
        
        # Unsubscribe from message queue
        message_queue.unsubscribe(self._handle_message)
        
        if self._broadcast_task:
            self._broadcast_task.cancel()
            try:
                await self._broadcast_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        with self._lock:
            connections = list(self._active_connections)
        
        for connection in connections:
            try:
                await connection.close()
            except Exception:
                pass
        
        with self._lock:
            self._active_connections.clear()
        
        logger.info("All WebSocket connections closed")


manager = ConnectionManager(max_connections=MAX_WEBSOCKET_CONNECTIONS)


@router.websocket("/ship-updates")
async def websocket_ship_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time ship position updates."""
    # Try to connect
    if not await manager.connect(websocket):
        await websocket.close(code=1008, reason="Connection limit reached")
        return
    
    try:
        # Send initial positions
        ships = ship_service.get_all_ships(limit=settings.MAX_SHIPS_DISPLAY)
        await websocket.send_json({
            "type": "initial",
            "ships": [ship.model_dump() for ship in ships]  # Pydantic v2
        })
        
        # Keep connection alive - wait for messages (ping/pong)
        while True:
            try:
                # Wait for client messages (ping/pong)
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                message = json.loads(data)
                
                # Handle pong
                if message.get("type") == "pong":
                    continue
                    
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({"type": "ping"})
                except Exception:
                    break
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
    finally:
        manager.disconnect(websocket)
