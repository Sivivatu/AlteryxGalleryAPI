"""
Retry logic with exponential backoff for API requests.
"""

import random
import time
from functools import wraps
from typing import Any, Callable, Type

from ..exceptions import RateLimitError


def retry_with_backoff(
    max_retries: int = 3,
    backoff_factor: float = 0.5,
    jitter: bool = True,
    retry_on: tuple[Type[Exception], ...] = (RateLimitError, Exception),
):
    """Decorator to retry function calls with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts. Defaults to 3.
        backoff_factor: Multiplier for exponential backoff. Defaults to 0.5.
        jitter: Add random jitter to backoff to avoid thundering herd. Defaults to True.
        retry_on: Tuple of exception types to retry on. Defaults to (RateLimitError, Exception).

    Returns:
        Decorated function with retry logic

    Example:
        @retry_with_backoff(max_retries=3, backoff_factor=0.5)
        def my_function():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e

                    if attempt < max_retries:
                        sleep_time = backoff_factor * (2**attempt)

                        if jitter:
                            sleep_time = sleep_time * random.uniform(0.8, 1.2)

                        # Check if RateLimitError provides retry_after
                        if isinstance(e, RateLimitError) and e.retry_after:
                            sleep_time = min(sleep_time, e.retry_after)

                        time.sleep(sleep_time)
                    else:
                        raise

            if last_exception is not None:
                raise last_exception

        return wrapper

    return decorator
