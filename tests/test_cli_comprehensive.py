"""Comprehensive tests for mini_agent/cli.py — CLI functions.

Tests parse_args, print_banner, print_help, print_session_info, print_stats,
initialize_base_tools, add_workspace_tools.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest


class TestParseArgs:
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
        with patch("sys.argv", ["bpsagent", "--task", "Cari data inflasi"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.task == "Cari data inflasi"

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


class TestPrintBanner:
    def test_print_banner(self, capsys):
        from mini_agent.cli import print_banner
        print_banner()
        captured = capsys.readouterr()
        assert "BPS Stat Agent" in captured.out
        assert "╔" in captured.out
        assert "╚" in captured.out


class TestPrintHelp:
    def test_print_help(self, capsys):
        from mini_agent.cli import print_help
        print_help()
        captured = capsys.readouterr()
        assert "/help" in captured.out
        assert "/exit" in captured.out
        assert "/clear" in captured.out
        assert "/stats" in captured.out


class TestPrintSessionInfo:
    def test_print_session_info(self, capsys):
        from mini_agent.cli import print_session_info

        mock_agent = MagicMock()
        mock_agent.messages = [MagicMock(), MagicMock()]
        mock_agent.tools = [MagicMock(), MagicMock(), MagicMock()]

        print_session_info(mock_agent, Path("/tmp/workspace"), "MiniMax-M2.5")
        captured = capsys.readouterr()
        assert "Session Info" in captured.out
        assert "MiniMax-M2.5" in captured.out
        assert "2 messages" in captured.out
        assert "3 tools" in captured.out


class TestPrintStats:
    def test_print_stats(self, capsys):
        from mini_agent.cli import print_stats

        mock_agent = MagicMock()
        mock_msg_user = MagicMock()
        mock_msg_user.role = "user"
        mock_msg_assistant = MagicMock()
        mock_msg_assistant.role = "assistant"
        mock_msg_tool = MagicMock()
        mock_msg_tool.role = "tool"
        mock_agent.messages = [mock_msg_user, mock_msg_assistant, mock_msg_tool]
        mock_agent.tools = [MagicMock()]
        mock_agent.api_total_tokens = 1500

        session_start = datetime(2024, 1, 1, 10, 0, 0)
        print_stats(mock_agent, session_start)
        captured = capsys.readouterr()
        assert "Session Statistics" in captured.out
        assert "User Messages" in captured.out
        assert "1,500" in captured.out


class TestInitializeBaseTools:
    @pytest.mark.asyncio
    async def test_initialize_with_all_disabled(self, capsys):
        from mini_agent.cli import initialize_base_tools

        mock_config = MagicMock()
        mock_config.tools.enable_bash = False
        mock_config.tools.enable_skills = False
        mock_config.tools.enable_mcp = False

        tools, skill_loader = await initialize_base_tools(mock_config)
        assert isinstance(tools, list)
        assert skill_loader is None

    @pytest.mark.asyncio
    async def test_initialize_with_bash_enabled(self, capsys):
        from mini_agent.cli import initialize_base_tools

        mock_config = MagicMock()
        mock_config.tools.enable_bash = True
        mock_config.tools.enable_skills = False
        mock_config.tools.enable_mcp = False

        tools, skill_loader = await initialize_base_tools(mock_config)
        assert len(tools) >= 2  # BashOutputTool + BashKillTool
        tool_names = [t.name for t in tools]
        assert "bash_output" in tool_names or "get_bash_output" in tool_names

    @pytest.mark.asyncio
    async def test_initialize_with_skills_enabled(self, capsys):
        from mini_agent.cli import initialize_base_tools

        mock_config = MagicMock()
        mock_config.tools.enable_bash = False
        mock_config.tools.enable_skills = True
        mock_config.tools.enable_mcp = False
        mock_config.tools.skills_dir = "skills"

        with patch("mini_agent.cli.Config.get_package_dir", return_value=Path("/nonexistent")):
            tools, skill_loader = await initialize_base_tools(mock_config)
            assert isinstance(tools, list)

    @pytest.mark.asyncio
    async def test_initialize_with_mcp_enabled(self, capsys):
        from mini_agent.cli import initialize_base_tools

        mock_config = MagicMock()
        mock_config.tools.enable_bash = False
        mock_config.tools.enable_skills = False
        mock_config.tools.enable_mcp = True
        mock_config.tools.mcp.connect_timeout = 10
        mock_config.tools.mcp.execute_timeout = 30
        mock_config.tools.mcp.sse_read_timeout = 60
        mock_config.tools.mcp_config_path = "mcp.json"

        with patch("mini_agent.cli.Config.find_config_file", return_value=None):
            tools, skill_loader = await initialize_base_tools(mock_config)
            assert isinstance(tools, list)


class TestAddWorkspaceTools:
    def test_add_workspace_tools_with_bash(self, tmp_path, capsys):
        from mini_agent.cli import add_workspace_tools

        mock_config = MagicMock()
        mock_config.tools.enable_bash = True
        mock_config.tools.enable_file_tools = True
        mock_config.tools.enable_note = True
        mock_config.tools.bash_timeout = 120

        tools = []
        add_workspace_tools(tools, mock_config, tmp_path)
        assert len(tools) > 0
        # Should have bash, file tools, note tools, and all research tools
        tool_names = [t.name for t in tools]
        assert "bash" in tool_names

    def test_add_workspace_tools_no_bash(self, tmp_path, capsys):
        from mini_agent.cli import add_workspace_tools

        mock_config = MagicMock()
        mock_config.tools.enable_bash = False
        mock_config.tools.enable_file_tools = False
        mock_config.tools.enable_note = False

        tools = []
        add_workspace_tools(tools, mock_config, tmp_path)
        # Should still load research/statistics/analysis/quality/writing/document/knowledge tools
        assert len(tools) > 0

    def test_add_workspace_tools_creates_workspace(self, tmp_path, capsys):
        from mini_agent.cli import add_workspace_tools

        mock_config = MagicMock()
        mock_config.tools.enable_bash = False
        mock_config.tools.enable_file_tools = False
        mock_config.tools.enable_note = False

        new_dir = tmp_path / "new_workspace"
        tools = []
        add_workspace_tools(tools, mock_config, new_dir)
        assert new_dir.exists()
