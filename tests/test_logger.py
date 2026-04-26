"""Tests for AgentLogger module."""

import json
from pathlib import Path
from unittest.mock import MagicMock

from mini_agent.logger import AgentLogger
from mini_agent.schema import Message, ToolCall, FunctionCall


class TestAgentLogger:
    def test_init_creates_log_dir(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        logger = AgentLogger()
        assert logger.log_dir.exists()
        assert logger.log_file is None
        assert logger.log_index == 0

    def test_start_new_run_creates_log_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        logger = AgentLogger()
        logger.start_new_run()
        assert logger.log_file is not None
        assert logger.log_file.exists()
        assert "agent_run_" in logger.log_file.name

    def test_get_log_file_path_before_run(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        logger = AgentLogger()
        path = logger.get_log_file_path()
        assert "(no active log)" in str(path)

    def test_get_log_file_path_after_run(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        logger = AgentLogger()
        logger.start_new_run()
        path = logger.get_log_file_path()
        assert path == logger.log_file
        assert path.exists()

    def test_log_request(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        logger = AgentLogger()
        logger.start_new_run()
        messages = [Message(role="user", content="Hello")]
        logger.log_request(messages=messages)
        content = logger.log_file.read_text()
        assert "REQUEST" in content
        assert "Hello" in content

    def test_log_response(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        logger = AgentLogger()
        logger.start_new_run()
        logger.log_response(content="Test response", thinking="I think...")
        content = logger.log_file.read_text()
        assert "RESPONSE" in content
        assert "Test response" in content
        assert "I think..." in content

    def test_log_tool_result(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        logger = AgentLogger()
        logger.start_new_run()
        logger.log_tool_result(
            tool_name="read_file",
            arguments={"path": "/test.txt"},
            result_success=True,
            result_content="file content",
        )
        content = logger.log_file.read_text()
        assert "TOOL_RESULT" in content
        assert "read_file" in content
        assert "file content" in content

    def test_log_tool_result_failure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        logger = AgentLogger()
        logger.start_new_run()
        logger.log_tool_result(
            tool_name="bash",
            arguments={"command": "ls"},
            result_success=False,
            result_error="Permission denied",
        )
        content = logger.log_file.read_text()
        assert "Permission denied" in content

    def test_no_write_before_start(self, tmp_path, monkeypatch):
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        logger = AgentLogger()
        # Should not crash when log_file is None
        logger.log_request(messages=[Message(role="user", content="test")])
        logger.log_response(content="test")
        logger.log_tool_result(tool_name="test", arguments={}, result_success=True)
