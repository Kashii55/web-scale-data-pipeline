import time
import asyncio
from functools import wraps
from utils.logger import get_logger

logger = get_logger("Retry")

def retry_sync(max_retries: int = 3, base_delay: float = 2.0, exceptions=(Exception,)):
    """Decorator for sync functions with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"All {max_retries} retries exhausted for {func.__name__}: {e}")
                        raise
                    delay = base_delay ** attempt
                    logger.warning(f"Attempt {attempt}/{max_retries} failed for {func.__name__}: {e}. Retrying in {delay:.1f}s...")
                    time.sleep(delay)
        return wrapper
    return decorator


def retry_async(max_retries: int = 3, base_delay: float = 2.0, exceptions=(Exception,)):
    """Decorator for async functions with exponential backoff"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"All {max_retries} retries exhausted for {func.__name__}: {e}")
                        raise
                    delay = base_delay ** attempt
                    logger.warning(f"Attempt {attempt}/{max_retries} failed for {func.__name__}: {e}. Retrying in {delay:.1f}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
