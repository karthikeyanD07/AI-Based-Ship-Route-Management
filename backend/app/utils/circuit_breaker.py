"""Circuit breaker pattern for external API calls."""
import asyncio
import logging
from enum import Enum
from typing import Callable, Any, Optional
from datetime import datetime, timedelta
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker for resilient external API calls."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type that counts as failure
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to call
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Function result
            
        Raises:
            Exception: If circuit is open or function fails
        """
        async with self._lock:
            # Check if we should attempt recovery
            if self.state == CircuitState.OPEN:
                if self.last_failure_time and \
                   (datetime.now() - self.last_failure_time).total_seconds() >= self.recovery_timeout:
                    logger.info("Circuit breaker: Attempting recovery (half-open)")
                    self.state = CircuitState.HALF_OPEN
                    self.failure_count = 0
                else:
                    raise Exception(f"Circuit breaker is OPEN. Service unavailable.")
            
            # Attempt call
            try:
                result = await func(*args, **kwargs)
                
                # Success - reset failure count
                if self.state == CircuitState.HALF_OPEN:
                    logger.info("Circuit breaker: Recovery successful, closing circuit")
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                elif self.state == CircuitState.CLOSED:
                    self.failure_count = 0
                
                return result
                
            except self.expected_exception as e:
                self.failure_count += 1
                self.last_failure_time = datetime.now()
                
                if self.failure_count >= self.failure_threshold:
                    logger.warning(
                        f"Circuit breaker: Opening circuit after {self.failure_count} failures"
                    )
                    self.state = CircuitState.OPEN
                
                raise


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    expected_exception: type = Exception
):
    """Decorator for circuit breaker pattern."""
    breaker = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator
