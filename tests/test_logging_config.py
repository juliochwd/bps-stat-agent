"""Tests for mini_agent/logging_config.py — structured logging setup."""

import json
import logging
import sys
from unittest.mock import patch

import pytest

from mini_agent.logging_config import JSONFormatter, configure_logging


class TestJSONFormatter:
    """Tests for the JSONFormatter class."""

    def setup_method(self):
        self.formatter = JSONFormatter()

    def test_basic_format(self):
        """Test basic log record formatting."""
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Hello %s",
            args=("world",),
            exc_info=None,
        )
        output = self.formatter.format(record)
        data = json.loads(output)

        assert data["level"] == "INFO"
        assert data["logger"] == "test.logger"
        assert data["message"] == "Hello world"
        assert data["line"] == 42
        assert "timestamp" in data
        assert "module" in data
        assert "function" in data

    def test_format_with_exception(self):
        """Test formatting with exception info."""
        try:
            raise ValueError("test error")
        except ValueError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Something failed",
            args=(),
            exc_info=exc_info,
        )
        output = self.formatter.format(record)
        data = json.loads(output)

        assert "exception" in data
        assert data["exception"]["type"] == "ValueError"
        assert data["exception"]["message"] == "test error"
        assert "traceback" in data["exception"]

    def test_format_with_extra_data(self):
        """Test formatting with extra_data attribute."""
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="With data",
            args=(),
            exc_info=None,
        )
        record.extra_data = {"key": "value", "count": 42}
        output = self.formatter.format(record)
        data = json.loads(output)

        assert "data" in data
        assert data["data"]["key"] == "value"
        assert data["data"]["count"] == 42

    def test_format_without_exception(self):
        """Test that exception key is absent when no exception."""
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=1,
            msg="No error",
            args=(),
            exc_info=None,
        )
        output = self.formatter.format(record)
        data = json.loads(output)
        assert "exception" not in data


class TestConfigureLogging:
    """Tests for the configure_logging function."""

    def teardown_method(self):
        """Reset root logger after each test."""
        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(logging.WARNING)

    def test_configure_json_output(self):
        """Test JSON output configuration."""
        configure_logging(level="DEBUG", json_output=True)
        root = logging.getLogger()

        assert root.level == logging.DEBUG
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0], logging.StreamHandler)
        assert isinstance(root.handlers[0].formatter, JSONFormatter)

    def test_configure_human_readable_output(self):
        """Test human-readable output configuration."""
        configure_logging(level="WARNING", json_output=False)
        root = logging.getLogger()

        assert root.level == logging.WARNING
        assert len(root.handlers) == 1
        assert not isinstance(root.handlers[0].formatter, JSONFormatter)

    def test_configure_with_log_file(self, tmp_path):
        """Test configuration with file logging."""
        log_file = str(tmp_path / "test.log")
        configure_logging(level="INFO", json_output=True, log_file=log_file)
        root = logging.getLogger()

        assert len(root.handlers) == 2
        # One StreamHandler, one FileHandler
        handler_types = {type(h) for h in root.handlers}
        assert logging.StreamHandler in handler_types
        assert logging.FileHandler in handler_types

    def test_configure_suppresses_noisy_loggers(self):
        """Test that noisy loggers are suppressed."""
        configure_logging(level="DEBUG", json_output=True)

        for name in ["httpx", "httpcore", "urllib3", "asyncio"]:
            assert logging.getLogger(name).level == logging.WARNING

    def test_configure_invalid_level_defaults_to_info(self):
        """Test that invalid level defaults to INFO."""
        configure_logging(level="INVALID_LEVEL", json_output=True)
        root = logging.getLogger()
        assert root.level == logging.INFO

    def test_configure_clears_existing_handlers(self):
        """Test that existing handlers are cleared after configure_logging."""
        root = logging.getLogger()
        # After configure_logging, only the configured handlers should remain
        configure_logging(level="INFO", json_output=True)
        # Should have exactly 1 handler (stdout)
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0], logging.StreamHandler)
