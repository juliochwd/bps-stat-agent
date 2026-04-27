import importlib
import sys
import time
from unittest.mock import patch

import pytest


class TestNoopMetricsWhenNotInstalled:
    def test_noop_metrics_when_not_installed(self):
        saved = sys.modules.pop("mini_agent.metrics", None)
        try:
            with patch.dict(sys.modules, {"prometheus_client": None}):
                import mini_agent.metrics as m
                importlib.reload(m)

                assert m.PROMETHEUS_AVAILABLE is False

                m.AGENT_RUNS_TOTAL.labels(status="completed").inc()
                m.AGENT_STEPS_TOTAL.inc()
                m.AGENT_RUN_DURATION.observe(1.5)
                m.AGENT_ACTIVE_RUNS.inc()
                m.AGENT_ACTIVE_RUNS.dec()
                m.LLM_REQUESTS_TOTAL.labels(provider="anthropic", model="test", status="success").inc()
                m.LLM_REQUEST_DURATION.labels(provider="anthropic", model="test").observe(2.0)
                m.LLM_TOKENS_TOTAL.labels(provider="anthropic", model="test", type="prompt").inc()
                m.LLM_RETRIES_TOTAL.labels(provider="anthropic", model="test").inc()
                m.TOOL_CALLS_TOTAL.labels(tool_name="bash", status="success").inc()
                m.TOOL_CALL_DURATION.labels(tool_name="bash").observe(0.5)
                m.APP_INFO.info({"version": "0.1.0"})

                body, content_type = m.get_metrics_text()
                assert body == b"# prometheus_client not installed\n"
                assert content_type == "text/plain"

                m.init_app_info("1.0.0")
        finally:
            sys.modules.pop("mini_agent.metrics", None)
            if saved is not None:
                sys.modules["mini_agent.metrics"] = saved


class TestMetricsWithPrometheus:
    @pytest.mark.skipif(
        not importlib.util.find_spec("prometheus_client"),
        reason="prometheus_client not installed",
    )
    def test_counter_increment(self):
        from mini_agent.metrics import AGENT_STEPS_TOTAL, PROMETHEUS_AVAILABLE
        assert PROMETHEUS_AVAILABLE is True

        before = AGENT_STEPS_TOTAL._value.get()
        AGENT_STEPS_TOTAL.inc()
        after = AGENT_STEPS_TOTAL._value.get()
        assert after == before + 1

    @pytest.mark.skipif(
        not importlib.util.find_spec("prometheus_client"),
        reason="prometheus_client not installed",
    )
    def test_histogram_observe(self):
        from mini_agent.metrics import AGENT_RUN_DURATION, get_metrics_text
        AGENT_RUN_DURATION.observe(5.0)
        AGENT_RUN_DURATION.observe(10.0)

        body, content_type = get_metrics_text()
        assert b"agent_run_duration_seconds" in body

    @pytest.mark.skipif(
        not importlib.util.find_spec("prometheus_client"),
        reason="prometheus_client not installed",
    )
    def test_track_duration_context_manager(self):
        from mini_agent.metrics import AGENT_RUN_DURATION, get_metrics_text, track_duration
        with track_duration(AGENT_RUN_DURATION):
            time.sleep(0.05)

        body, _ = get_metrics_text()
        assert b"agent_run_duration_seconds" in body

    @pytest.mark.skipif(
        not importlib.util.find_spec("prometheus_client"),
        reason="prometheus_client not installed",
    )
    def test_get_metrics_text(self):
        from mini_agent.metrics import get_metrics_text
        body, content_type = get_metrics_text()
        assert isinstance(body, bytes)
        assert "text/plain" in content_type

    @pytest.mark.skipif(
        not importlib.util.find_spec("prometheus_client"),
        reason="prometheus_client not installed",
    )
    def test_init_app_info(self):
        from mini_agent.metrics import init_app_info, get_metrics_text
        init_app_info("0.1.3")
        body, _ = get_metrics_text()
        assert b"bps_stat_agent_info" in body

    @pytest.mark.skipif(
        not importlib.util.find_spec("prometheus_client"),
        reason="prometheus_client not installed",
    )
    def test_labels(self):
        from mini_agent.metrics import AGENT_RUNS_TOTAL, LLM_REQUESTS_TOTAL, get_metrics_text
        labeled = AGENT_RUNS_TOTAL.labels(status="completed")
        labeled.inc()
        chained = LLM_REQUESTS_TOTAL.labels(provider="openai", model="gpt-4", status="success")
        chained.inc()

        body, _ = get_metrics_text()
        assert b"agent_runs_total" in body
        assert b"llm_requests_total" in body


class TestNoopFallbackBehavior:
    def test_noop_labels_chaining(self):
        from mini_agent.metrics import _NoOpMetric
        m = _NoOpMetric()
        result = m.labels(foo="bar").labels(baz="qux")
        assert isinstance(result, _NoOpMetric)
        result.inc()
        result.dec()
        result.set(42)
        result.observe(1.0)

    def test_noop_timer(self):
        from mini_agent.metrics import _NoOpMetric
        m = _NoOpMetric()
        with m.time():
            pass
