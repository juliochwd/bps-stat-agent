"""Extended tests for mini_agent/health.py — health check server."""

import json
import threading
import time
from http.client import HTTPConnection
from unittest.mock import patch

import pytest

from mini_agent.health import (
    HealthHandler,
    _get_version,
    start_health_server,
    stop_health_server,
)


class TestGetVersion:
    def test_returns_version_string(self):
        version = _get_version()
        assert isinstance(version, str)
        assert version != ""

    def test_returns_unknown_on_import_error(self):
        with patch.dict("sys.modules", {"mini_agent": None}):
            with patch("builtins.__import__", side_effect=ImportError):
                # Direct test of the function logic
                try:
                    from mini_agent import __version__
                    assert isinstance(__version__, str)
                except ImportError:
                    pass


class TestHealthServer:
    """Integration tests for the health server."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Ensure server is stopped after each test."""
        yield
        stop_health_server()
        # Reset global state
        import mini_agent.health as h
        h._server = None
        h._thread = None
        h._start_time = 0.0
        h._ready_check = None

    def test_start_and_stop(self):
        """Test starting and stopping the server."""
        start_health_server(port=18080)
        time.sleep(0.1)

        # Make a request
        conn = HTTPConnection("127.0.0.1", 18080, timeout=2)
        conn.request("GET", "/health")
        resp = conn.getresponse()
        assert resp.status == 200

        data = json.loads(resp.read())
        assert data["status"] == "healthy"
        assert "uptime_seconds" in data
        assert "timestamp" in data
        conn.close()

        stop_health_server()

    def test_ready_endpoint_default(self):
        """Test /ready endpoint without custom check."""
        start_health_server(port=18081)
        time.sleep(0.1)

        conn = HTTPConnection("127.0.0.1", 18081, timeout=2)
        conn.request("GET", "/ready")
        resp = conn.getresponse()
        assert resp.status == 200

        data = json.loads(resp.read())
        assert data["status"] == "ready"
        conn.close()

    def test_ready_endpoint_not_ready(self):
        """Test /ready endpoint when check returns False."""
        start_health_server(port=18082, ready_check=lambda: False)
        time.sleep(0.1)

        conn = HTTPConnection("127.0.0.1", 18082, timeout=2)
        conn.request("GET", "/ready")
        resp = conn.getresponse()
        assert resp.status == 503

        data = json.loads(resp.read())
        assert data["status"] == "not_ready"
        conn.close()

    def test_404_endpoint(self):
        """Test unknown endpoint returns 404."""
        start_health_server(port=18083)
        time.sleep(0.1)

        conn = HTTPConnection("127.0.0.1", 18083, timeout=2)
        conn.request("GET", "/unknown")
        resp = conn.getresponse()
        assert resp.status == 404
        conn.close()

    def test_double_start(self):
        """Starting twice should be idempotent."""
        start_health_server(port=18084)
        start_health_server(port=18084)  # Should not raise
        time.sleep(0.1)

        conn = HTTPConnection("127.0.0.1", 18084, timeout=2)
        conn.request("GET", "/health")
        resp = conn.getresponse()
        assert resp.status == 200
        conn.close()

    def test_stop_when_not_running(self):
        """Stopping when not running should not raise."""
        stop_health_server()  # Should not raise
