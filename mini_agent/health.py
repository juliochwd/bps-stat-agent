"""Lightweight HTTP health check server for production deployments.

Provides /health and /ready endpoints for container orchestrators (Docker, K8s).
Runs as a background thread alongside the main STDIO-based agent.

Usage:
    from mini_agent.health import start_health_server, stop_health_server

    # Start health server on port 8080
    start_health_server(port=8080)

    # Later, stop it
    stop_health_server()
"""

import json
import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

# Global state
_server: HTTPServer | None = None
_thread: threading.Thread | None = None
_start_time: float = 0.0
_ready_check: Callable[[], bool] | None = None


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check endpoints."""

    def do_GET(self):
        if self.path == "/health":
            self._respond_health()
        elif self.path == "/ready":
            self._respond_ready()
        elif self.path == "/metrics":
            self._respond_metrics()
        else:
            self._respond(404, {"error": "not_found"})

    def _respond_health(self):
        """Liveness check - is the process alive?"""
        uptime = time.time() - _start_time if _start_time else 0
        self._respond(200, {
            "status": "healthy",
            "uptime_seconds": round(uptime, 2),
            "timestamp": datetime.now(UTC).isoformat(),
            "version": _get_version(),
        })

    def _respond_ready(self):
        """Readiness check - is the service ready to accept work?"""
        if _ready_check and not _ready_check():
            self._respond(503, {"status": "not_ready"})
        else:
            self._respond(200, {
                "status": "ready",
                "timestamp": datetime.now(UTC).isoformat(),
            })

    def _respond_metrics(self):
        """Serve Prometheus metrics if available, otherwise 404."""
        try:
            from .metrics import PROMETHEUS_AVAILABLE, get_metrics_text
            if PROMETHEUS_AVAILABLE:
                body_bytes, content_type = get_metrics_text()
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.end_headers()
                self.wfile.write(body_bytes)
                return
        except ImportError:
            pass
        self._respond(404, {"error": "metrics_not_available"})

    def _respond(self, status_code: int, body: dict):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

    def log_message(self, format, *args):
        """Suppress default HTTP server logging."""
        pass


def _get_version() -> str:
    try:
        from mini_agent import __version__
        return __version__
    except ImportError:
        return "unknown"


def start_health_server(
    port: int = 8080,
    host: str = "0.0.0.0",
    ready_check: Callable[[], bool] | None = None,
) -> None:
    """Start the health check HTTP server in a background thread.

    Args:
        port: Port to listen on (default: 8080)
        host: Host to bind to (default: 0.0.0.0)
        ready_check: Optional callable that returns True if service is ready
    """
    global _server, _thread, _start_time, _ready_check

    if _server is not None:
        return  # Already running

    _start_time = time.time()
    _ready_check = ready_check
    _server = HTTPServer((host, port), HealthHandler)
    _thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _thread.start()


def stop_health_server() -> None:
    """Stop the health check HTTP server."""
    global _server, _thread

    if _server:
        _server.shutdown()
        _server = None
    if _thread:
        _thread.join(timeout=5)
        _thread = None
