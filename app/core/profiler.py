import asyncio
import functools
import time
import tracemalloc

from app.config import settings
from app.core.logger import logger


def profiler(func):
    if settings.APP_ENV not in ["local", "development"]:
        return func
    if asyncio.iscoroutinefunction(func):
        # If the function is async, we wrap it differently
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Start the timer and memory tracking
            start_time = time.time()
            tracemalloc.start()

            try:
                # Execute the async function
                result = await func(*args, **kwargs)
            finally:
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                end_time = time.time()
                # Calculate duration and memory usage
                duration = end_time - start_time
                memory_used = current / 10 ** 6  # Convert to MB
                peak_memory_used = peak / 10 ** 6  # Convert to MB

                # duration_timedelta = timedelta(milliseconds=duration)
                # Log the stats
                seconds = int(duration)
                milliseconds = (duration - seconds) * 1000

                l = f"async def {func.__name__}(...) | Executed in {seconds}s {milliseconds:.2f}ms"
                if memory_used:
                    l += f" | Used {memory_used:.6f}MB"
                if peak_memory_used:
                    l += f" | Peaked at {peak_memory_used:.6f}MB"

                logger.debug(l)

            return result

        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            tracemalloc.start()

            try:
                result = func(*args, **kwargs)
            finally:
                current, peak = tracemalloc.get_traced_memory()
                tracemalloc.stop()
                end_time = time.time()

                # Calculate duration and memory usage
                duration = end_time - start_time
                memory_used = current / 10 ** 6  # Convert to MB
                peak_memory_used = peak / 10 ** 6  # Convert to MB

                # duration_timedelta = timedelta(minutes=duration)
                # print(duration)
                seconds = int(duration)
                milliseconds = (duration - seconds) * 1000

                # Log the stats
                l = f"def {func.__name__}(...) | Executed in {seconds}s {milliseconds:.2f}ms"
                if memory_used:
                    l += f" | Used {memory_used:.6f}MB"
                if peak_memory_used:
                    l += f" | Peaked at {peak_memory_used:.6f}MB"
                logger.debug(l)
            return result
        return sync_wrapper