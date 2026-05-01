"""Extended tests for mini_agent/retry.py — retry mechanism."""

import asyncio
from unittest.mock import MagicMock

import pytest

from mini_agent.retry import RetryConfig, RetryExhaustedError, async_retry


class TestRetryConfig:
    def test_defaults(self):
        config = RetryConfig()
        assert config.enabled is True
        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0

    def test_custom(self):
        config = RetryConfig(
            enabled=False,
            max_retries=5,
            initial_delay=0.5,
            max_delay=30.0,
            exponential_base=3.0,
        )
        assert config.enabled is False
        assert config.max_retries == 5

    def test_calculate_delay_first_attempt(self):
        config = RetryConfig(initial_delay=1.0, exponential_base=2.0)
        assert config.calculate_delay(0) == 1.0

    def test_calculate_delay_second_attempt(self):
        config = RetryConfig(initial_delay=1.0, exponential_base=2.0)
        assert config.calculate_delay(1) == 2.0

    def test_calculate_delay_third_attempt(self):
        config = RetryConfig(initial_delay=1.0, exponential_base=2.0)
        assert config.calculate_delay(2) == 4.0

    def test_calculate_delay_capped_at_max(self):
        config = RetryConfig(initial_delay=1.0, exponential_base=2.0, max_delay=5.0)
        assert config.calculate_delay(10) == 5.0

    def test_calculate_delay_custom_base(self):
        config = RetryConfig(initial_delay=0.5, exponential_base=3.0)
        assert config.calculate_delay(2) == 0.5 * 9  # 0.5 * 3^2


class TestRetryExhaustedError:
    def test_creation(self):
        original = ValueError("original error")
        err = RetryExhaustedError(original, attempts=3)
        assert err.last_exception is original
        assert err.attempts == 3
        assert "3 attempts" in str(err)
        assert "original error" in str(err)

    def test_long_error_truncated(self):
        original = ValueError("x" * 1000)
        err = RetryExhaustedError(original, attempts=1)
        assert len(str(err)) < 1000


class TestAsyncRetry:
    @pytest.mark.asyncio
    async def test_success_first_try(self):
        """Function succeeds on first try."""
        config = RetryConfig(max_retries=3, initial_delay=0.01)

        @async_retry(config)
        async def success():
            return "ok"

        result = await success()
        assert result == "ok"

    @pytest.mark.asyncio
    async def test_success_after_retries(self):
        """Function succeeds after some retries."""
        config = RetryConfig(max_retries=3, initial_delay=0.01)
        call_count = [0]

        @async_retry(config)
        async def flaky():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("not yet")
            return "ok"

        result = await flaky()
        assert result == "ok"
        assert call_count[0] == 3

    @pytest.mark.asyncio
    async def test_exhausted_retries(self):
        """Function fails all retries."""
        config = RetryConfig(max_retries=2, initial_delay=0.01)

        @async_retry(config)
        async def always_fail():
            raise ValueError("always fails")

        with pytest.raises(RetryExhaustedError) as exc_info:
            await always_fail()

        assert exc_info.value.attempts == 3  # initial + 2 retries
        assert isinstance(exc_info.value.last_exception, ValueError)

    @pytest.mark.asyncio
    async def test_on_retry_callback(self):
        """on_retry callback is called on each retry."""
        config = RetryConfig(max_retries=3, initial_delay=0.01)
        callbacks = []

        def on_retry(exc, attempt):
            callbacks.append((str(exc), attempt))

        @async_retry(config, on_retry=on_retry)
        async def flaky():
            if len(callbacks) < 2:
                raise ValueError("fail")
            return "ok"

        result = await flaky()
        assert result == "ok"
        assert len(callbacks) == 2

    @pytest.mark.asyncio
    async def test_non_retryable_exception(self):
        """Non-retryable exceptions are not retried."""
        config = RetryConfig(
            max_retries=3,
            initial_delay=0.01,
            retryable_exceptions=(ValueError,),
        )
        call_count = [0]

        @async_retry(config)
        async def raises_type_error():
            call_count[0] += 1
            raise TypeError("not retryable")

        with pytest.raises(TypeError):
            await raises_type_error()

        assert call_count[0] == 1  # No retries

    @pytest.mark.asyncio
    async def test_default_config(self):
        """Test with default config (None)."""

        @async_retry()
        async def success():
            return "default"

        result = await success()
        assert result == "default"
