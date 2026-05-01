"""Comprehensive coverage tests for mini_agent/cli.py.

Tests parse_args, print functions, initialize_base_tools, add_workspace_tools,
run_agent (non-interactive), show_log_directory, read_log_file, main.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ===========================================================================
# parse_args tests
# ===========================================================================


class TestParseArgs:
    """Test parse_args with various argument combinations."""

    def test_no_args(self):
        with patch("sys.argv", ["bpsagent"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.workspace is None
            assert args.task is None
            assert args.command is None

    def test_workspace_arg(self):
        with patch("sys.argv", ["bpsagent", "--workspace", "/tmp/test"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.workspace == "/tmp/test"

    def test_workspace_short(self):
        with patch("sys.argv", ["bpsagent", "-w", "/tmp/test"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.workspace == "/tmp/test"

    def test_task_arg(self):
        with patch("sys.argv", ["bpsagent", "--task", "find inflation data"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.task == "find inflation data"

    def test_task_short(self):
        with patch("sys.argv", ["bpsagent", "-t", "test task"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.task == "test task"

    def test_setup_command(self):
        with patch("sys.argv", ["bpsagent", "setup"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.command == "setup"

    def test_setup_force(self):
        with patch("sys.argv", ["bpsagent", "setup", "--force"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.command == "setup"
            assert args.force is True

    def test_log_command(self):
        with patch("sys.argv", ["bpsagent", "log"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.command == "log"
            assert args.filename is None

    def test_log_with_filename(self):
        with patch("sys.argv", ["bpsagent", "log", "agent_run.log"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.command == "log"
            assert args.filename == "agent_run.log"

    def test_research_command(self):
        with patch("sys.argv", ["bpsagent", "research"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.command == "research"

    def test_research_with_title(self):
        with patch("sys.argv", ["bpsagent", "research", "--title", "My Paper"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.command == "research"
            assert args.title == "My Paper"

    def test_research_with_template(self):
        with patch("sys.argv", ["bpsagent", "research", "--template", "ieee"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.template == "ieee"

    def test_combined_args(self):
        with patch("sys.argv", ["bpsagent", "-w", "/tmp", "-t", "do something"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.workspace == "/tmp"
            assert args.task == "do something"


# ===========================================================================
# Print function tests
# ===========================================================================


class TestPrintFunctions:
    """Test print_banner, print_help, print_session_info, print_stats."""

    def test_print_banner(self, capsys):
        from mini_agent.cli import print_banner
        print_banner()
        captured = capsys.readouterr()
        assert "Agent" in captured.out or "BPS" in captured.out
        assert "╔" in captured.out  # Box drawing

    def test_print_help(self, capsys):
        from mini_agent.cli import print_help
        print_help()
        captured = capsys.readouterr()
        assert "/help" in captured.out
        assert "/exit" in captured.out
        assert "/clear" in captured.out
        assert "/stats" in captured.out

    def test_print_session_info(self, capsys):
        from mini_agent.cli import print_session_info
        from mini_agent.schema import Message

        agent = MagicMock()
        agent.messages = [
            MagicMock(role="system"),
            MagicMock(role="user"),
        ]
        agent.tools = {"tool1": MagicMock(), "tool2": MagicMock()}

        print_session_info(agent, Path("/tmp/workspace"), "gpt-4")
        captured = capsys.readouterr()
        assert "Model" in captured.out
        assert "Workspace" in captured.out
        assert "2 messages" in captured.out
        assert "2 tools" in captured.out

    def test_print_stats(self, capsys):
        from mini_agent.cli import print_stats

        agent = MagicMock()
        agent.messages = [
            MagicMock(role="system"),
            MagicMock(role="user"),
            MagicMock(role="assistant"),
            MagicMock(role="tool"),
            MagicMock(role="user"),
        ]
        agent.api_total_tokens = 1500

        session_start = datetime.now()
        print_stats(agent, session_start)
        captured = capsys.readouterr()
        assert "Statistics" in captured.out
        assert "User Messages" in captured.out


# ===========================================================================
# Log functions tests
# ===========================================================================


class TestLogFunctions:
    """Test show_log_directory and read_log_file."""

    def test_get_log_directory(self):
        from mini_agent.cli import get_log_directory
        result = get_log_directory()
        assert isinstance(result, Path)
        assert "log" in str(result)

    def test_show_log_directory_nonexistent(self, capsys):
        from mini_agent.cli import show_log_directory
        with patch("mini_agent.cli.get_log_directory", return_value=Path("/nonexistent/path")):
            show_log_directory(open_file_manager=False)
            captured = capsys.readouterr()
            assert "does not exist" in captured.out

    def test_show_log_directory_empty(self, capsys, tmp_path):
        from mini_agent.cli import show_log_directory
        log_dir = tmp_path / "log"
        log_dir.mkdir()
        with patch("mini_agent.cli.get_log_directory", return_value=log_dir):
            show_log_directory(open_file_manager=False)
            captured = capsys.readouterr()
            assert "No log files" in captured.out

    def test_show_log_directory_with_files(self, capsys, tmp_path):
        from mini_agent.cli import show_log_directory
        log_dir = tmp_path / "log"
        log_dir.mkdir()
        (log_dir / "test1.log").write_text("log content 1")
        (log_dir / "test2.log").write_text("log content 2")
        with patch("mini_agent.cli.get_log_directory", return_value=log_dir):
            show_log_directory(open_file_manager=False)
            captured = capsys.readouterr()
            assert "test1.log" in captured.out or "test2.log" in captured.out

    def test_read_log_file_nonexistent(self, capsys):
        from mini_agent.cli import read_log_file
        with patch("mini_agent.cli.get_log_directory", return_value=Path("/nonexistent")):
            read_log_file("missing.log")
            captured = capsys.readouterr()
            assert "not found" in captured.out

    def test_read_log_file_exists(self, capsys, tmp_path):
        from mini_agent.cli import read_log_file
        log_dir = tmp_path / "log"
        log_dir.mkdir()
        (log_dir / "test.log").write_text("Hello log content")
        with patch("mini_agent.cli.get_log_directory", return_value=log_dir):
            read_log_file("test.log")
            captured = capsys.readouterr()
            assert "Hello log content" in captured.out


# ===========================================================================
# initialize_base_tools tests
# ===========================================================================


class TestInitializeBaseTools:
    """Test initialize_base_tools."""

    @pytest.mark.asyncio
    async def test_basic_tools_loaded(self, capsys):
        from mini_agent.cli import initialize_base_tools

        config = MagicMock()
        config.tools.enable_bash = True
        config.tools.enable_skills = False
        config.tools.enable_mcp = False

        tools, skill_loader = await initialize_base_tools(config)
        assert len(tools) >= 2  # BashOutputTool + BashKillTool
        assert skill_loader is None

    @pytest.mark.asyncio
    async def test_no_tools_disabled(self, capsys):
        from mini_agent.cli import initialize_base_tools

        config = MagicMock()
        config.tools.enable_bash = False
        config.tools.enable_skills = False
        config.tools.enable_mcp = False

        tools, skill_loader = await initialize_base_tools(config)
        assert len(tools) == 0


# ===========================================================================
# add_workspace_tools tests
# ===========================================================================


class TestAddWorkspaceTools:
    """Test add_workspace_tools."""

    def test_adds_bash_and_file_tools(self, tmp_path, capsys):
        from mini_agent.cli import add_workspace_tools

        config = MagicMock()
        config.tools.enable_bash = True
        config.tools.enable_file_tools = True
        config.tools.enable_note = False

        tools = []
        add_workspace_tools(tools, config, tmp_path)
        tool_names = [t.name for t in tools]
        assert "bash" in tool_names
        assert "read_file" in tool_names
        assert "write_file" in tool_names
        assert "edit_file" in tool_names

    def test_adds_note_tools(self, tmp_path, capsys):
        from mini_agent.cli import add_workspace_tools

        config = MagicMock()
        config.tools.enable_bash = False
        config.tools.enable_file_tools = False
        config.tools.enable_note = True

        tools = []
        add_workspace_tools(tools, config, tmp_path)
        tool_names = [t.name for t in tools]
        assert "record_note" in tool_names
        assert "recall_notes" in tool_names

    def test_creates_workspace_dir(self, tmp_path, capsys):
        from mini_agent.cli import add_workspace_tools

        config = MagicMock()
        config.tools.enable_bash = False
        config.tools.enable_file_tools = False
        config.tools.enable_note = False

        new_dir = tmp_path / "new_workspace"
        tools = []
        add_workspace_tools(tools, config, new_dir)
        assert new_dir.exists()


# ===========================================================================
# main() tests
# ===========================================================================


class TestMain:
    """Test main entry point."""

    def test_main_setup_command(self):
        from mini_agent.cli import main

        with patch("sys.argv", ["bpsagent", "setup"]), \
             patch("mini_agent.setup_wizard.run_setup_wizard", return_value=True) as mock_setup:
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_main_log_command(self, capsys):
        from mini_agent.cli import main

        with patch("sys.argv", ["bpsagent", "log"]), \
             patch("mini_agent.cli.show_log_directory") as mock_show:
            main()
            mock_show.assert_called_once()

    def test_main_log_with_file(self, capsys):
        from mini_agent.cli import main

        with patch("sys.argv", ["bpsagent", "log", "test.log"]), \
             patch("mini_agent.cli.read_log_file") as mock_read:
            main()
            mock_read.assert_called_once_with("test.log")


# ===========================================================================
# _open_directory_in_file_manager tests
# ===========================================================================


class TestOpenDirectoryInFileManager:
    """Test _open_directory_in_file_manager."""

    def test_linux(self, tmp_path):
        from mini_agent.cli import _open_directory_in_file_manager
        with patch("platform.system", return_value="Linux"), \
             patch("subprocess.run") as mock_run:
            _open_directory_in_file_manager(tmp_path)
            mock_run.assert_called_once()

    def test_darwin(self, tmp_path):
        from mini_agent.cli import _open_directory_in_file_manager
        with patch("platform.system", return_value="Darwin"), \
             patch("subprocess.run") as mock_run:
            _open_directory_in_file_manager(tmp_path)
            mock_run.assert_called_once()

    def test_windows(self, tmp_path):
        from mini_agent.cli import _open_directory_in_file_manager
        with patch("platform.system", return_value="Windows"), \
             patch("subprocess.run") as mock_run:
            _open_directory_in_file_manager(tmp_path)
            mock_run.assert_called_once()

    def test_file_not_found(self, tmp_path, capsys):
        from mini_agent.cli import _open_directory_in_file_manager
        with patch("platform.system", return_value="Linux"), \
             patch("subprocess.run", side_effect=FileNotFoundError):
            _open_directory_in_file_manager(tmp_path)
            captured = capsys.readouterr()
            assert "Could not open" in captured.out
