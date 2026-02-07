"""Distributed state management using Redis (optional)."""
import logging
from typing import Optional, Dict, Any
import json
from app.config.settings import settings

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not available - distributed state disabled")


class StateManager:
    """Manages distributed state using Redis (optional fallback to local)."""
    
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
        self._local_state: Dict[str, Any] = {}
        self._use_redis = False
        
        if REDIS_AVAILABLE and settings.REDIS_URL:
            try:
                self._redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                self._redis_client.ping()
                self._use_redis = True
                logger.info("Redis connected - using distributed state")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Using local state.")
                self._redis_client = None
                self._use_redis = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from state."""
        if self._use_redis and self._redis_client:
            try:
                value = self._redis_client.get(key)
                return json.loads(value) if value else None
            except Exception as e:
                logger.error(f"Error getting from Redis: {e}")
                return self._local_state.get(key)
        else:
            return self._local_state.get(key)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in state."""
        if self._use_redis and self._redis_client:
            try:
                json_value = json.dumps(value)
                if ttl:
                    self._redis_client.setex(key, ttl, json_value)
                else:
                    self._redis_client.set(key, json_value)
            except Exception as e:
                logger.error(f"Error setting in Redis: {e}")
                self._local_state[key] = value
        else:
            self._local_state[key] = value
    
    def delete(self, key: str):
        """Delete key from state."""
        if self._use_redis and self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception as e:
                logger.error(f"Error deleting from Redis: {e}")
        
        if key in self._local_state:
            del self._local_state[key]
    
    def close(self):
        """Close Redis connection."""
        if self._redis_client:
            try:
                self._redis_client.close()
            except Exception:
                pass


# Global state manager instance
state_manager = StateManager()
