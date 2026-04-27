"""OpenTelemetry distributed tracing for BPS Stat Agent.

Provides request tracing across agent runs, LLM calls, and tool executions.
Traces can be exported to any OTLP-compatible backend (Jaeger, Zipkin, etc.).

If opentelemetry packages are not installed, all tracing operations become no-ops.
"""

import os
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import (
        BatchSpanProcessor,
        ConsoleSpanExporter,
    )
    from opentelemetry.semconv.resource import ResourceAttributes
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False


# ---- No-op fallbacks ----

class _NoOpSpan:
    """No-op span that silently ignores all operations."""
    def set_attribute(self, key: str, value: Any) -> None: pass
    def set_status(self, status: Any, description: str | None = None) -> None: pass
    def record_exception(self, exception: Exception) -> None: pass
    def add_event(self, name: str, attributes: dict | None = None) -> None: pass
    def end(self) -> None: pass
    def __enter__(self): return self
    def __exit__(self, *args): pass


class _NoOpTracer:
    """No-op tracer that returns no-op spans."""
    def start_as_current_span(self, name: str, **kwargs) -> Any:
        return _NoOpSpan()

    def start_span(self, name: str, **kwargs) -> Any:
        return _NoOpSpan()


_tracer: Any = _NoOpTracer()


def configure_tracing(
    service_name: str = "bps-stat-agent",
    service_version: str = "unknown",
    exporter: str = "console",
    otlp_endpoint: str | None = None,
) -> None:
    """Configure OpenTelemetry tracing.

    Args:
        service_name: Name of the service for traces
        service_version: Version of the service
        exporter: Exporter type - "console", "otlp", or "none"
        otlp_endpoint: OTLP endpoint URL (required if exporter="otlp")
    """
    global _tracer

    if not OTEL_AVAILABLE:
        return

    # Allow env var override
    exporter = os.environ.get("OTEL_EXPORTER", exporter)
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", otlp_endpoint)

    if exporter == "none":
        return

    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: service_version,
    })

    provider = TracerProvider(resource=resource)

    if exporter == "console":
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    elif exporter == "otlp" and otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            provider.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
            )
        except ImportError:
            # Fall back to console if OTLP exporter not installed
            provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(service_name, service_version)


def get_tracer() -> Any:
    """Get the configured tracer (or no-op tracer if not configured)."""
    return _tracer


@contextmanager
def trace_span(
    name: str,
    attributes: dict[str, Any] | None = None,
) -> Generator[Any, None, None]:
    """Create a traced span as context manager.

    Works as no-op if OpenTelemetry is not installed.

    Args:
        name: Span name
        attributes: Optional span attributes

    Yields:
        The span (or no-op span)
    """
    if OTEL_AVAILABLE and not isinstance(_tracer, _NoOpTracer):
        with _tracer.start_as_current_span(name) as span:
            if attributes:
                for key, value in attributes.items():
                    span.set_attribute(key, str(value) if not isinstance(value, (str, int, float, bool)) else value)
            yield span
    else:
        yield _NoOpSpan()


def trace_agent_run(run_id: str | None = None):
    """Create a span for an agent run."""
    attrs = {}
    if run_id:
        attrs["agent.run_id"] = run_id
    return trace_span("agent.run", attributes=attrs)


def trace_llm_call(provider: str, model: str):
    """Create a span for an LLM API call."""
    return trace_span("llm.generate", attributes={
        "llm.provider": provider,
        "llm.model": model,
    })


def trace_tool_call(tool_name: str, arguments: dict | None = None):
    """Create a span for a tool execution."""
    attrs = {"tool.name": tool_name}
    if arguments:
        # Only include argument keys, not values (may contain sensitive data)
        attrs["tool.argument_keys"] = ",".join(arguments.keys())
    return trace_span("tool.execute", attributes=attrs)
