import logging
import time
from functools import wraps


logger = logging.getLogger(__name__)


def profile_execution(func):
    """
    Decorator to profile and log the execution time of strategy methods.
    Useful for identifying performance bottlenecks on edge devices.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time

        # Determine pair/metadata if passed
        pair = "unknown"
        if len(args) > 2 and isinstance(args[2], dict) and "pair" in args[2]:
            pair = args[2]["pair"]
        elif "metadata" in kwargs and "pair" in kwargs["metadata"]:
            pair = kwargs["metadata"]["pair"]

        logger.info(
            f"[PROFILER] {func.__name__} executed for {pair} in {execution_time:.4f} seconds"
        )
        return result

    return wrapper
