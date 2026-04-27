"""Tests for the tracing module."""

from unittest.mock import patch

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


class TestNoOpSpan:
    def test_noop_span_operations(self):
        span = _NoOpSpan()
        span.set_attribute("key", "value")
        span.set_status("OK")
        span.set_status("ERROR", description="something failed")
        span.record_exception(ValueError("test"))
        span.add_event("event_name")
        span.add_event("event_name", attributes={"k": "v"})
        span.end()

    def test_noop_span_context_manager(self):
        span = _NoOpSpan()
        with span as s:
            assert s is span


class TestNoOpTracer:
    def test_start_as_current_span(self):
        tracer = _NoOpTracer()
        span = tracer.start_as_current_span("test")
        assert isinstance(span, _NoOpSpan)

    def test_start_span(self):
        tracer = _NoOpTracer()
        span = tracer.start_span("test")
        assert isinstance(span, _NoOpSpan)


class TestGetTracer:
    def test_get_tracer_returns_noop_by_default(self):
        tracer = get_tracer()
        assert isinstance(tracer, _NoOpTracer)


class TestConfigureTracing:
    def test_configure_tracing_without_otel(self):
        with patch("mini_agent.tracing.OTEL_AVAILABLE", False):
            configure_tracing()

    def test_configure_tracing_noop_when_not_installed(self):
        with patch("mini_agent.tracing.OTEL_AVAILABLE", False):
            configure_tracing(exporter="console")
            tracer = get_tracer()
            assert isinstance(tracer, _NoOpTracer)


class TestTraceSpan:
    def test_trace_span_context_manager(self):
        with trace_span("test.span") as span:
            assert isinstance(span, _NoOpSpan)

    def test_trace_span_with_attributes(self):
        with trace_span("test.span", attributes={"key": "value"}) as span:
            assert isinstance(span, _NoOpSpan)


class TestTraceAgentRun:
    def test_trace_agent_run(self):
        with trace_agent_run() as span:
            assert isinstance(span, _NoOpSpan)

    def test_trace_agent_run_with_id(self):
        with trace_agent_run(run_id="test-123") as span:
            assert isinstance(span, _NoOpSpan)


class TestTraceLLMCall:
    def test_trace_llm_call(self):
        with trace_llm_call(provider="anthropic", model="claude-3") as span:
            assert isinstance(span, _NoOpSpan)


class TestTraceToolCall:
    def test_trace_tool_call(self):
        with trace_tool_call("search_tool") as span:
            assert isinstance(span, _NoOpSpan)

    def test_trace_tool_call_with_arguments(self):
        with trace_tool_call("search_tool", arguments={"query": "test", "limit": 10}) as span:
            assert isinstance(span, _NoOpSpan)
