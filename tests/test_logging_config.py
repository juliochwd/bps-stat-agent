import json
import logging
import sys

import pytest

from mini_agent.config import LoggingConfig
from mini_agent.logging_config import JSONFormatter, configure_logging


class TestJSONFormatter:
    def test_produces_valid_json(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="hello world",
            args=(),
            exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_includes_required_fields(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="mini_agent.llm",
            level=logging.WARNING,
            pathname="llm.py",
            lineno=10,
            msg="rate limited",
            args=(),
            exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        assert parsed["level"] == "WARNING"
        assert parsed["logger"] == "mini_agent.llm"
        assert parsed["message"] == "rate limited"
        assert "timestamp" in parsed
        assert "module" in parsed
        assert "function" in parsed
        assert "line" in parsed

    def test_captures_exception_info(self):
        formatter = JSONFormatter()
        try:
            raise ValueError("bad value")
        except ValueError:
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=1,
                msg="something failed",
                args=(),
                exc_info=sys.exc_info(),
            )
        parsed = json.loads(formatter.format(record))
        assert "exception" in parsed
        assert parsed["exception"]["type"] == "ValueError"
        assert "bad value" in parsed["exception"]["message"]
        assert "traceback" in parsed["exception"]

    def test_includes_extra_data(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="with extras",
            args=(),
            exc_info=None,
        )
        record.extra_data = {"request_id": "abc-123"}
        parsed = json.loads(formatter.format(record))
        assert parsed["data"] == {"request_id": "abc-123"}

    def test_no_exception_key_when_no_error(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="ok",
            args=(),
            exc_info=None,
        )
        parsed = json.loads(formatter.format(record))
        assert "exception" not in parsed


class TestConfigureLogging:
    def setup_method(self):
        root = logging.getLogger()
        self._original_handlers = root.handlers[:]
        self._original_level = root.level

    def teardown_method(self):
        root = logging.getLogger()
        root.handlers = self._original_handlers
        root.level = self._original_level
        for name in ["httpx", "httpcore", "urllib3", "asyncio"]:
            logging.getLogger(name).setLevel(logging.NOTSET)

    def test_sets_root_level(self):
        configure_logging(level="DEBUG", json_output=False)
        assert logging.getLogger().level == logging.DEBUG

    def test_json_handler_uses_json_formatter(self):
        configure_logging(level="INFO", json_output=True)
        root = logging.getLogger()
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0].formatter, JSONFormatter)

    def test_human_readable_handler(self):
        configure_logging(level="INFO", json_output=False)
        root = logging.getLogger()
        assert len(root.handlers) == 1
        assert not isinstance(root.handlers[0].formatter, JSONFormatter)

    def test_file_handler_added(self, tmp_path):
        log_file = str(tmp_path / "test.log")
        configure_logging(level="INFO", json_output=False, log_file=log_file)
        root = logging.getLogger()
        assert len(root.handlers) == 2
        file_handlers = [h for h in root.handlers if isinstance(h, logging.FileHandler)]
        assert len(file_handlers) == 1
        assert isinstance(file_handlers[0].formatter, JSONFormatter)

    def test_clears_existing_handlers(self):
        root = logging.getLogger()
        root.addHandler(logging.StreamHandler())
        root.addHandler(logging.StreamHandler())
        assert len(root.handlers) >= 2
        configure_logging(level="INFO", json_output=False)
        assert len(root.handlers) == 1

    def test_suppresses_noisy_loggers(self):
        configure_logging(level="DEBUG", json_output=False)
        for name in ["httpx", "httpcore", "urllib3", "asyncio"]:
            assert logging.getLogger(name).level == logging.WARNING

    def test_stdout_handler_writes_to_stdout(self):
        configure_logging(level="INFO", json_output=False)
        root = logging.getLogger()
        stream_handlers = [h for h in root.handlers if isinstance(h, logging.StreamHandler)]
        assert any(h.stream is sys.stdout for h in stream_handlers)

    def test_invalid_level_defaults_to_info(self):
        configure_logging(level="NONEXISTENT", json_output=False)
        assert logging.getLogger().level == logging.INFO


class TestLoggingConfig:
    def test_defaults(self):
        cfg = LoggingConfig()
        assert cfg.level == "INFO"
        assert cfg.json_output is False
        assert cfg.log_file is None

    def test_custom_values(self):
        cfg = LoggingConfig(level="DEBUG", json_output=True, log_file="/tmp/app.log")
        assert cfg.level == "DEBUG"
        assert cfg.json_output is True
        assert cfg.log_file == "/tmp/app.log"
