"""Prometheus metrics for BPS Stat Agent.

Provides application metrics for monitoring agent performance, LLM usage,
and tool execution. Metrics are exposed via the health check server's /metrics endpoint.

If prometheus_client is not installed, all metric operations become no-ops.
"""

import time
from contextlib import contextmanager

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Gauge,
        Histogram,
        Info,
        generate_latest,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


# ---- No-op fallbacks when prometheus_client is not installed ----

class _NoOpMetric:
    """No-op metric that silently ignores all operations."""
    def inc(self, *a, **kw): pass
    def dec(self, *a, **kw): pass
    def set(self, *a, **kw): pass
    def observe(self, *a, **kw): pass
    def labels(self, *a, **kw): return self
    def info(self, *a, **kw): pass
    def time(self): return _NoOpTimer()

class _NoOpTimer:
    def __enter__(self): return self
    def __exit__(self, *a): pass


def _noop(*a, **kw):
    return _NoOpMetric()


if PROMETHEUS_AVAILABLE:
    # ---- Agent Metrics ----
    AGENT_RUNS_TOTAL = Counter(
        "agent_runs_total",
        "Total number of agent runs",
        ["status"],  # completed, cancelled, error, max_steps
    )
    AGENT_STEPS_TOTAL = Counter(
        "agent_steps_total",
        "Total number of agent steps executed",
    )
    AGENT_RUN_DURATION = Histogram(
        "agent_run_duration_seconds",
        "Duration of agent runs",
        buckets=[1, 5, 10, 30, 60, 120, 300, 600],
    )
    AGENT_ACTIVE_RUNS = Gauge(
        "agent_active_runs",
        "Number of currently active agent runs",
    )

    # ---- LLM Metrics ----
    LLM_REQUESTS_TOTAL = Counter(
        "llm_requests_total",
        "Total LLM API requests",
        ["provider", "model", "status"],  # status: success, error, retry_exhausted
    )
    LLM_REQUEST_DURATION = Histogram(
        "llm_request_duration_seconds",
        "Duration of LLM API requests",
        ["provider", "model"],
        buckets=[0.5, 1, 2, 5, 10, 30, 60, 120],
    )
    LLM_TOKENS_TOTAL = Counter(
        "llm_tokens_total",
        "Total tokens consumed",
        ["provider", "model", "type"],  # type: prompt, completion, total
    )
    LLM_RETRIES_TOTAL = Counter(
        "llm_retries_total",
        "Total LLM retry attempts",
        ["provider", "model"],
    )

    # ---- Tool Metrics ----
    TOOL_CALLS_TOTAL = Counter(
        "tool_calls_total",
        "Total tool executions",
        ["tool_name", "status"],  # status: success, error
    )
    TOOL_CALL_DURATION = Histogram(
        "tool_call_duration_seconds",
        "Duration of tool executions",
        ["tool_name"],
        buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60],
    )

    # ---- App Info ----
    APP_INFO = Info("bps_stat_agent", "BPS Stat Agent application info")

    def init_app_info(version: str = "unknown"):
        APP_INFO.info({"version": version})

    def get_metrics_text() -> tuple[bytes, str]:
        """Generate Prometheus metrics text for /metrics endpoint."""
        return generate_latest(), CONTENT_TYPE_LATEST

else:
    # All metrics are no-ops
    AGENT_RUNS_TOTAL = _NoOpMetric()
    AGENT_STEPS_TOTAL = _NoOpMetric()
    AGENT_RUN_DURATION = _NoOpMetric()
    AGENT_ACTIVE_RUNS = _NoOpMetric()
    LLM_REQUESTS_TOTAL = _NoOpMetric()
    LLM_REQUEST_DURATION = _NoOpMetric()
    LLM_TOKENS_TOTAL = _NoOpMetric()
    LLM_RETRIES_TOTAL = _NoOpMetric()
    TOOL_CALLS_TOTAL = _NoOpMetric()
    TOOL_CALL_DURATION = _NoOpMetric()
    APP_INFO = _NoOpMetric()

    def init_app_info(version: str = "unknown"):
        pass

    def get_metrics_text() -> tuple[bytes, str]:
        return b"# prometheus_client not installed\n", "text/plain"


@contextmanager
def track_duration(histogram):
    """Context manager to track duration with a Histogram."""
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        histogram.observe(duration)
