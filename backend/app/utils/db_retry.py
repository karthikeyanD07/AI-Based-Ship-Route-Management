"""Database retry utilities with exponential backoff."""
import asyncio
import logging
from typing import Callable, Any, TypeVar, Optional
from functools import wraps
from sqlalchemy.exc import OperationalError, DisconnectionError

logger = logging.getLogger(__name__)

T = TypeVar('T')


async def retry_db_operation(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    *args,
    **kwargs
) -> Any:
    """
    Retry database operation with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Multiplier for delay
        *args, **kwargs: Arguments to pass to function
        
    Returns:
        Function result
        
    Raises:
        Exception: If all retries fail
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except (OperationalError, DisconnectionError) as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(
                    f"Database operation failed (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                    f"Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
            else:
                logger.error(f"Database operation failed after {max_retries + 1} attempts: {e}")
                raise
        except Exception as e:
            # Don't retry on non-database errors
            logger.error(f"Non-retryable error in database operation: {e}")
            raise
    
    if last_exception:
        raise last_exception


def db_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0
):
    """Decorator for retrying database operations."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_db_operation(
                func,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor,
                *args,
                **kwargs
            )
        return wrapper
    return decorator
