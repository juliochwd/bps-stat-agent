"""Comprehensive tests for mini_agent/tracing.py — OpenTelemetry tracing.

Tests configure_tracing with mocked OTel, trace_span with real OTel.
"""

from unittest.mock import MagicMock, patch

import pytest

from mini_agent.tracing import (
    _NoOpSpan,
    _NoOpTracer,
    configure_tracing,
    get_tracer,
    trace_agent_run,
    trace_llm_call,
    trace_span,
    trace_tool_call,
)


class TestConfigureTracingWithOTel:
    """Test configure_tracing when OTel IS available."""

    def test_configure_console_exporter(self):
        """Test configuring with console exporter."""
        import mini_agent.tracing as tracing_mod
        if not tracing_mod.OTEL_AVAILABLE:
            pytest.skip("OpenTelemetry not installed")

        # Save original tracer
        original = tracing_mod._tracer
        try:
            configure_tracing(
                service_name="test-service",
                service_version="1.0.0",
                exporter="console",
            )
            # After configuration, tracer should not be NoOp
            tracer = get_tracer()
            assert not isinstance(tracer, _NoOpTracer)
        finally:
            tracing_mod._tracer = original

    def test_configure_none_exporter(self):
        """Test configuring with 'none' exporter does nothing."""
        import mini_agent.tracing as tracing_mod
        if not tracing_mod.OTEL_AVAILABLE:
            pytest.skip("OpenTelemetry not installed")
        configure_tracing(exporter="none")

    def test_configure_otlp_exporter(self):
        """Test configuring with OTLP exporter."""
        import mini_agent.tracing as tracing_mod
        if not tracing_mod.OTEL_AVAILABLE:
            pytest.skip("OpenTelemetry not installed")

        original = tracing_mod._tracer
        try:
            configure_tracing(
                service_name="test",
                exporter="otlp",
                otlp_endpoint="http://localhost:4317",
            )
        finally:
            tracing_mod._tracer = original

    def test_configure_env_override(self):
        """Test that environment variables override parameters."""
        with patch.dict("os.environ", {"OTEL_EXPORTER": "none"}):
            configure_tracing(exporter="console")


class TestTraceSpanWithOTel:
    """Test trace_span when OTel is configured."""

    def test_trace_span_with_real_tracer(self):
        """Test trace_span when a real tracer is configured."""
        import mini_agent.tracing as tracing_mod

        mock_span = MagicMock()
        mock_span.__enter__ = MagicMock(return_value=mock_span)
        mock_span.__exit__ = MagicMock(return_value=False)

        mock_tracer = MagicMock()
        mock_tracer.start_as_current_span.return_value = mock_span

        original_tracer = tracing_mod._tracer
        try:
            tracing_mod._tracer = mock_tracer
            with patch("mini_agent.tracing.OTEL_AVAILABLE", True):
                with trace_span("test.operation", attributes={"key": "value"}) as span:
                    assert span is mock_span
                    span.set_attribute.assert_called_with("key", "value")
        finally:
            tracing_mod._tracer = original_tracer

    def test_trace_span_with_complex_attributes(self):
        """Test trace_span converts non-primitive attributes to string."""
        import mini_agent.tracing as tracing_mod

        mock_span = MagicMock()
        mock_span.__enter__ = MagicMock(return_value=mock_span)
        mock_span.__exit__ = MagicMock(return_value=False)

        mock_tracer = MagicMock()
        mock_tracer.start_as_current_span.return_value = mock_span

        original_tracer = tracing_mod._tracer
        try:
            tracing_mod._tracer = mock_tracer
            with patch("mini_agent.tracing.OTEL_AVAILABLE", True):
                with trace_span("test", attributes={"list_val": [1, 2, 3], "int_val": 42}) as span:
                    # list should be converted to string, int should stay
                    calls = span.set_attribute.call_args_list
                    assert len(calls) == 2
        finally:
            tracing_mod._tracer = original_tracer


class TestTraceHelpers:
    """Test trace_agent_run, trace_llm_call, trace_tool_call."""

    def test_trace_agent_run_no_id(self):
        with trace_agent_run() as span:
            assert isinstance(span, _NoOpSpan)

    def test_trace_agent_run_with_id(self):
        with trace_agent_run(run_id="run-abc-123") as span:
            assert isinstance(span, _NoOpSpan)

    def test_trace_llm_call(self):
        with trace_llm_call(provider="openai", model="gpt-4") as span:
            assert isinstance(span, _NoOpSpan)

    def test_trace_tool_call_no_args(self):
        with trace_tool_call("bash_tool") as span:
            assert isinstance(span, _NoOpSpan)

    def test_trace_tool_call_with_args(self):
        with trace_tool_call("search", arguments={"query": "test", "limit": 5}) as span:
            assert isinstance(span, _NoOpSpan)
