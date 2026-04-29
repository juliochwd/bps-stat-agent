"""Tests for the health check HTTP server."""

import json
import urllib.request

import pytest

from mini_agent.health import start_health_server, stop_health_server

_BASE_PORT = 18_080


@pytest.fixture()
def _port_counter():
    """Yield a unique port per test to avoid bind conflicts."""
    _port_counter._n = getattr(_port_counter, "_n", 0) + 1
    return _BASE_PORT + _port_counter._n


@pytest.fixture()
def health_server(_port_counter):
    port = _port_counter
    start_health_server(port=port, host="127.0.0.1")
    yield port
    stop_health_server()


@pytest.fixture()
def health_server_not_ready(_port_counter):
    port = _port_counter
    start_health_server(port=port, host="127.0.0.1", ready_check=lambda: False)
    yield port
    stop_health_server()


def _get(port: int, path: str) -> tuple[int, dict]:
    url = f"http://127.0.0.1:{port}{path}"
    try:
        with urllib.request.urlopen(url) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


class TestHealthEndpoint:
    def test_health_endpoint_returns_200(self, health_server):
        status, body = _get(health_server, "/health")

        assert status == 200
        assert body["status"] == "healthy"
        assert "uptime_seconds" in body
        assert body["uptime_seconds"] >= 0
        assert "timestamp" in body
        assert "version" in body

    def test_health_version_matches_package(self, health_server):
        from mini_agent import __version__

        _, body = _get(health_server, "/health")
        assert body["version"] == __version__


class TestReadyEndpoint:
    def test_ready_endpoint_returns_200(self, health_server):
        status, body = _get(health_server, "/ready")

        assert status == 200
        assert body["status"] == "ready"
        assert "timestamp" in body

    def test_ready_endpoint_with_failing_check(self, health_server_not_ready):
        status, body = _get(health_server_not_ready, "/ready")

        assert status == 503
        assert body["status"] == "not_ready"


class TestRouting:
    def test_404_for_unknown_path(self, health_server):
        status, body = _get(health_server, "/unknown")

        assert status == 404
        assert body["error"] == "not_found"

    def test_metrics_endpoint(self, health_server):
        url = f"http://127.0.0.1:{health_server}/metrics"
        try:
            with urllib.request.urlopen(url) as resp:
                status = resp.status
                content_type = resp.headers.get("Content-Type", "")
                body = resp.read()
        except urllib.error.HTTPError as exc:
            status = exc.code
            body = exc.read()
            content_type = ""

        assert status in (200, 404)
        if status == 200:
            # Prometheus metrics are returned as text, not JSON
            assert len(body) > 0
            assert "text/" in content_type


class TestLifecycle:
    def test_start_stop_server(self, _port_counter):
        port = _port_counter
        start_health_server(port=port, host="127.0.0.1")
        status, _ = _get(port, "/health")
        assert status == 200
        stop_health_server()

    def test_double_start_is_safe(self, _port_counter):
        port = _port_counter
        try:
            start_health_server(port=port, host="127.0.0.1")
            start_health_server(port=port, host="127.0.0.1")
            status, _ = _get(port, "/health")
            assert status == 200
        finally:
            stop_health_server()

    def test_stop_without_start_is_safe(self):
        stop_health_server()
