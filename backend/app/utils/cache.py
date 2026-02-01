"""Caching utilities with LRU eviction."""
import hashlib
import json
from functools import wraps
from typing import Callable, Any, Optional, OrderedDict
from datetime import datetime, timedelta
import logging
from collections import OrderedDict as LRUDict

logger = logging.getLogger(__name__)


class LRUCache:
    """LRU cache with TTL and size limits."""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize LRU cache.
        
        Args:
            max_size: Maximum number of entries
            default_ttl: Default TTL in seconds
        """
        self._cache: LRUDict[str, tuple] = LRUDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache (moves to end for LRU)."""
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        
        # Check TTL
        if datetime.now() > expiry:
            del self._cache[key]
            return None
        
        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache with TTL."""
        ttl = ttl or self.default_ttl
        expiry = datetime.now() + timedelta(seconds=ttl)
        
        # Remove if exists (will be re-added at end)
        if key in self._cache:
            del self._cache[key]
        
        # Add new entry
        self._cache[key] = (value, expiry)
        
        # Evict oldest if over limit
        if len(self._cache) > self.max_size:
            self._cache.popitem(last=False)  # Remove oldest (first item)
    
    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()


# Global cache instance with size limit
route_cache = LRUCache(max_size=1000, default_ttl=3600)  # 1 hour for routes


def cached(ttl: int = 300):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{route_cache._generate_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = route_cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Compute result
            result = await func(*args, **kwargs) if hasattr(func, '__call__') else func(*args, **kwargs)
            
            # Store in cache
            route_cache.set(cache_key, result, ttl=ttl)
            logger.debug(f"Cached result for {func.__name__}")
            
            return result
        return wrapper
    return decorator
