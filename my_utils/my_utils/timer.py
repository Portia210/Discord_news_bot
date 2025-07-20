import time
import functools
import asyncio
from .setup_logger import get_app_logger


def measure_time(func):
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        logger = get_app_logger()
        start_time = time.time()
        logger.debug(f"Starting {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            logger.debug(f"Finished {func.__name__} in {duration:.2f} seconds")
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            logger.error(f"{func.__name__} failed after {duration:.2f} seconds: {str(e)}")
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        logger = get_app_logger()
        start_time = time.time()
        logger.debug(f"Starting {func.__name__}")
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            logger.debug(f"Finished {func.__name__} in {duration:.2f} seconds")
            return result
        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            logger.error(f"{func.__name__} failed after {duration:.2f} seconds: {str(e)}")
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper