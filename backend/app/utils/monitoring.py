"""Monitoring and alerting utilities."""
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from app.config.settings import settings

logger = logging.getLogger(__name__)


class AlertManager:
    """Manages alerts and thresholds."""
    
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.error_windows = defaultdict(deque)
        self.alert_thresholds = {
            "error_rate": 10,  # errors per minute
            "latency_p95": 1000,  # milliseconds
            "db_connection_failures": 5,
            "weather_api_failures": 5
        }
        self.alerts_sent = set()
    
    def record_error(self, error_type: str, endpoint: str = None):
        """Record an error."""
        key = f"{error_type}:{endpoint or 'global'}"
        now = datetime.utcnow()
        
        # Add to window
        self.error_windows[key].append(now)
        
        # Remove old entries (older than 1 minute)
        cutoff = now - timedelta(minutes=1)
        while self.error_windows[key] and self.error_windows[key][0] < cutoff:
            self.error_windows[key].popleft()
        
        # Check threshold
        count = len(self.error_windows[key])
        if count >= self.alert_thresholds.get(error_type, 10):
            self._trigger_alert(error_type, count, endpoint)
    
    def _trigger_alert(self, error_type: str, count: int, endpoint: str = None):
        """Trigger an alert if not already sent."""
        alert_key = f"{error_type}:{endpoint or 'global'}"
        if alert_key not in self.alerts_sent:
            self.alerts_sent.add(alert_key)
            logger.error(
                f"ALERT: {error_type} threshold exceeded. "
                f"Count: {count}, Endpoint: {endpoint or 'global'}"
            )
            # In production, send to alerting system (PagerDuty, etc.)
    
    def reset_alert(self, error_type: str, endpoint: str = None):
        """Reset alert state."""
        alert_key = f"{error_type}:{endpoint or 'global'}"
        self.alerts_sent.discard(alert_key)


# Global alert manager
alert_manager = AlertManager()


def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics."""
    try:
        from app.services.ship_service import ship_service
        from app.routes.websocket import manager as ws_manager
        from app.services.db_service import db_service
        from app.services.weather_service import weather_service
        
        # Get WebSocket connection count (thread-safe)
        ws_count = 0
        if hasattr(ws_manager, '_active_connections') and hasattr(ws_manager, '_lock'):
            with ws_manager._lock:
                ws_count = len(ws_manager._active_connections)
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "ships_tracked": len(ship_service.ship_positions) if ship_service.ship_positions else 0,
            "websocket_connections": ws_count,
            "database_available": db_service.is_available(),
            "weather_available": bool(weather_service.api_key),
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}", exc_info=True)
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": "Failed to collect metrics"
        }
    
    return metrics
