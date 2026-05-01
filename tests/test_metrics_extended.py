"""Extended tests for mini_agent/metrics.py — Prometheus metrics."""

import time
from unittest.mock import patch

import pytest

from mini_agent.metrics import (
    _NoOpMetric,
    _NoOpTimer,
    _noop,
    get_metrics_text,
    init_app_info,
    track_duration,
)


class TestNoOpMetric:
    """Test _NoOpMetric fallback."""

    def test_inc(self):
        m = _NoOpMetric()
        m.inc()  # Should not raise

    def test_dec(self):
        m = _NoOpMetric()
        m.dec()

    def test_set(self):
        m = _NoOpMetric()
        m.set(42)

    def test_observe(self):
        m = _NoOpMetric()
        m.observe(1.5)

    def test_labels(self):
        m = _NoOpMetric()
        result = m.labels("a", "b")
        assert isinstance(result, _NoOpMetric)

    def test_info(self):
        m = _NoOpMetric()
        m.info({"key": "value"})

    def test_time(self):
        m = _NoOpMetric()
        timer = m.time()
        assert isinstance(timer, _NoOpTimer)


class TestNoOpTimer:
    def test_context_manager(self):
        timer = _NoOpTimer()
        with timer:
            pass  # Should not raise


class TestNoop:
    def test_returns_noop_metric(self):
        result = _noop()
        assert isinstance(result, _NoOpMetric)


class TestTrackDuration:
    def test_track_duration_observes(self):
        mock_histogram = _NoOpMetric()
        observed = []
        mock_histogram.observe = lambda v: observed.append(v)

        with track_duration(mock_histogram):
            time.sleep(0.01)

        assert len(observed) == 1
        assert observed[0] >= 0.01

    def test_track_duration_on_exception(self):
        mock_histogram = _NoOpMetric()
        observed = []
        mock_histogram.observe = lambda v: observed.append(v)

        with pytest.raises(ValueError):
            with track_duration(mock_histogram):
                raise ValueError("test")

        # Duration should still be recorded
        assert len(observed) == 1


class TestInitAppInfo:
    def test_init_app_info(self):
        # Should not raise regardless of prometheus availability
        init_app_info("1.0.0")


class TestGetMetricsText:
    def test_returns_bytes_and_content_type(self):
        body, content_type = get_metrics_text()
        assert isinstance(body, bytes)
        assert isinstance(content_type, str)
