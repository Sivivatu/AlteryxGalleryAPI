"""
Pytest unit tests for retry_with_backoff decorator.
"""

import pytest

from alteryx_server_py.utils.retry import retry_with_backoff
from alteryx_server_py.exceptions import RateLimitError


class TestRetryWithBackoff:
    """Tests for the retry_with_backoff decorator."""

    def test_success_on_first_attempt(self):
        """Expected use: function succeeds immediately without retrying."""
        call_count = 0

        @retry_with_backoff(max_retries=3, backoff_factor=0)
        def succeed():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = succeed()
        assert result == "ok"
        assert call_count == 1

    def test_retries_and_eventually_succeeds(self):
        """Expected use: function fails twice then succeeds on third attempt."""
        call_count = 0

        @retry_with_backoff(max_retries=3, backoff_factor=0, jitter=False)
        def fail_twice_then_succeed():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("temporary failure")
            return "success"

        result = fail_twice_then_succeed()
        assert result == "success"
        assert call_count == 3

    def test_raises_after_all_retries_exhausted(self):
        """Failure case: function always fails, exception re-raised after max_retries."""

        @retry_with_backoff(max_retries=2, backoff_factor=0, jitter=False)
        def always_fail():
            raise ValueError("always fails")

        with pytest.raises(ValueError, match="always fails"):
            always_fail()

    def test_negative_max_retries_does_not_raise_type_error(self):
        """Edge case: negative max_retries means loop never runs; last_exception stays None.

        Previously ``raise last_exception`` caused a ``TypeError`` because
        ``last_exception`` was ``None``.  The guard ``if last_exception is not None``
        prevents that error.

        NOTE: With ``max_retries=-1`` the decorated function body is never invoked
        (``range(0)`` is empty), so the wrapper silently returns ``None``.
        """

        @retry_with_backoff(max_retries=-1)
        def never_executed():
            raise ValueError("should not be called")

        # range(0) is empty — the body never runs, so no exception should propagate
        result = never_executed()
        assert result is None

    def test_zero_max_retries_runs_once_and_reraises(self):
        """Edge case: max_retries=0 executes the function exactly once and re-raises on failure."""
        call_count = 0

        @retry_with_backoff(max_retries=0, backoff_factor=0, jitter=False)
        def fail_once():
            nonlocal call_count
            call_count += 1
            raise ValueError("immediate failure")

        with pytest.raises(ValueError, match="immediate failure"):
            fail_once()

        assert call_count == 1

    def test_respects_retry_on_filter(self):
        """Edge case: only retries on specified exception types."""
        call_count = 0

        @retry_with_backoff(max_retries=3, backoff_factor=0, jitter=False, retry_on=(ValueError,))
        def raise_type_error():
            nonlocal call_count
            call_count += 1
            raise TypeError("not retried")

        with pytest.raises(TypeError):
            raise_type_error()

        # TypeError is not in retry_on, so no retries should have happened
        assert call_count == 1

    def test_rate_limit_error_with_retry_after(self):
        """Expected use: RateLimitError with retry_after is handled."""
        call_count = 0

        @retry_with_backoff(max_retries=2, backoff_factor=0, jitter=False)
        def hit_rate_limit():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise RateLimitError(retry_after=1)
            return "done"

        result = hit_rate_limit()
        assert result == "done"
        assert call_count == 2
