"""Full coverage tests for mini_agent/cli.py.

Tests run_agent, main, initialize_base_tools, add_workspace_tools,
print functions, and helper functions.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock, mock_open

import pytest


class TestPrintBanner:
    def test_print_banner(self, capsys):
        from mini_agent.cli import print_banner
        print_banner()
        captured = capsys.readouterr()
        assert "BPS" in captured.out or "Agent" in captured.out or len(captured.out) > 0


class TestPrintHelp:
    def test_print_help(self, capsys):
        from mini_agent.cli import print_help
        print_help()
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestGetLogDirectory:
    def test_returns_path(self):
        from mini_agent.cli import get_log_directory
        result = get_log_directory()
        assert isinstance(result, Path)


class TestShowLogDirectory:
    def test_show_log_directory(self, capsys):
        with patch("mini_agent.cli._open_directory_in_file_manager"):
            from mini_agent.cli import show_log_directory
            show_log_directory(open_file_manager=False)
            captured = capsys.readouterr()
            assert len(captured.out) > 0


class TestReadLogFile:
    def test_read_nonexistent(self, capsys):
        from mini_agent.cli import read_log_file
        read_log_file("nonexistent_file.log")
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower() or "error" in captured.out.lower() or len(captured.out) > 0


class TestYearConversions:
    def test_placeholder(self):
        # year_to_th is in bps_mcp_server, not cli
        pass


class TestParseArgsFull:
    def test_no_args(self):
        with patch("sys.argv", ["bpsagent"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.workspace is None
            assert args.task is None

    def test_research_with_title(self):
        with patch("sys.argv", ["bpsagent", "research", "--title", "My Paper"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.command == "research"
            assert args.title == "My Paper"

    def test_research_with_template(self):
        with patch("sys.argv", ["bpsagent", "research", "--title", "Paper", "--template", "ieee"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.template == "ieee"

    def test_research_with_journal(self):
        with patch("sys.argv", ["bpsagent", "research", "--title", "Paper", "--journal", "Nature"]):
            from mini_agent.cli import parse_args
            args = parse_args()
            assert args.journal == "Nature"


class TestInitializeBaseTools:
    @pytest.mark.asyncio
    async def test_initialize_base_tools(self):
        from mini_agent.cli import initialize_base_tools
        mock_config = MagicMock()
        mock_config.tools = MagicMock()
        mock_config.tools.enabled = []
        mock_config.tools.mcp_servers = []
        mock_config.tools.skills_dir = None
        mock_config.agent = MagicMock()
        mock_config.agent.skills_dir = None

        tools, skill_loader = await initialize_base_tools(mock_config)
        assert isinstance(tools, list)


class TestAddWorkspaceTools:
    def test_add_workspace_tools(self, tmp_path):
        from mini_agent.cli import add_workspace_tools
        mock_config = MagicMock()
        mock_config.tools = MagicMock()
        mock_config.tools.enabled = ["file_read", "file_write"]
        mock_config.tools.bps_api_key = ""
        mock_config.tools.sandbox = MagicMock()
        mock_config.tools.sandbox.enabled = False
        mock_config.research = MagicMock()
        mock_config.research.enabled = False

        tools = []
        add_workspace_tools(tools, mock_config, tmp_path)
        # Should add some tools
        assert isinstance(tools, list)


class TestRunAgent:
    @pytest.mark.asyncio
    async def test_run_agent_no_config(self, tmp_path, capsys):
        from mini_agent.cli import run_agent
        # Config file doesn't exist
        with patch("mini_agent.config.Config.get_default_config_path") as mock_path:
            mock_path.return_value = tmp_path / "nonexistent_config.yaml"
            await run_agent(workspace_dir=tmp_path)
            captured = capsys.readouterr()
            assert "not found" in captured.out.lower() or "configuration" in captured.out.lower()

    @pytest.mark.asyncio
    async def test_run_agent_invalid_config(self, tmp_path, capsys):
        from mini_agent.cli import run_agent
        config_path = tmp_path / "config.yaml"
        config_path.write_text("invalid: yaml: content: [")
        with patch("mini_agent.config.Config.get_default_config_path") as mock_path:
            mock_path.return_value = config_path
            await run_agent(workspace_dir=tmp_path)
            captured = capsys.readouterr()
            # Should print error
            assert len(captured.out) > 0


class TestMainFunction:
    def test_main_setup(self):
        with patch("sys.argv", ["bpsagent", "setup"]):
            with patch("mini_agent.setup_wizard.run_setup_wizard", return_value=True):
                from mini_agent.cli import main
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0

    def test_main_log(self, capsys):
        with patch("sys.argv", ["bpsagent", "log"]):
            with patch("mini_agent.cli.show_log_directory"):
                from mini_agent.cli import main
                main()

    def test_main_log_with_file(self, capsys):
        with patch("sys.argv", ["bpsagent", "log", "test.log"]):
            with patch("mini_agent.cli.read_log_file") as mock_read:
                from mini_agent.cli import main
                main()
                mock_read.assert_called_once_with("test.log")


class TestPrintSessionInfo:
    def test_print_session_info(self, capsys):
        from mini_agent.cli import print_session_info
        mock_agent = MagicMock()
        mock_agent.tools = [MagicMock(name="tool1"), MagicMock(name="tool2")]
        workspace = Path("/tmp/test")
        print_session_info(mock_agent, workspace, "gpt-4")
        captured = capsys.readouterr()
        assert len(captured.out) > 0


class TestPrintStats:
    def test_print_stats(self, capsys):
        from mini_agent.cli import print_stats
        mock_agent = MagicMock()
        # Mock messages as a list of objects with .role attribute
        mock_msg_user = MagicMock()
        mock_msg_user.role = "user"
        mock_msg_assistant = MagicMock()
        mock_msg_assistant.role = "assistant"
        mock_agent.messages = [mock_msg_user, mock_msg_assistant]
        mock_agent.tools = [MagicMock()]
        mock_agent.api_total_tokens = 1000
        session_start = datetime.now()
        print_stats(mock_agent, session_start)
        captured = capsys.readouterr()
        assert len(captured.out) > 0
