"""Tests for mini_agent/cli.py — CLI entry point."""

import platform
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestGetLogDirectory:
    def test_returns_path(self):
        from mini_agent.cli import get_log_directory

        result = get_log_directory()
        assert isinstance(result, Path)
        assert ".bps-stat-agent" in str(result)
        assert "log" in str(result)


class TestShowLogDirectory:
    @patch("mini_agent.cli._open_directory_in_file_manager")
    def test_nonexistent_directory(self, mock_open, capsys):
        from mini_agent.cli import show_log_directory

        with patch("mini_agent.cli.get_log_directory", return_value=Path("/nonexistent")):
            show_log_directory(open_file_manager=False)
            captured = capsys.readouterr()
            assert "does not exist" in captured.out

    @patch("mini_agent.cli._open_directory_in_file_manager")
    def test_empty_directory(self, mock_open, tmp_path, capsys):
        from mini_agent.cli import show_log_directory

        with patch("mini_agent.cli.get_log_directory", return_value=tmp_path):
            show_log_directory(open_file_manager=False)
            captured = capsys.readouterr()
            assert "No log files" in captured.out

    @patch("mini_agent.cli._open_directory_in_file_manager")
    def test_with_log_files(self, mock_open, tmp_path, capsys):
        from mini_agent.cli import show_log_directory

        # Create some log files
        (tmp_path / "agent_2024.log").write_text("log content")
        (tmp_path / "agent_2023.log").write_text("old log")

        with patch("mini_agent.cli.get_log_directory", return_value=tmp_path):
            show_log_directory(open_file_manager=False)
            captured = capsys.readouterr()
            assert "agent_2024.log" in captured.out


class TestReadLogFile:
    def test_nonexistent_file(self, capsys):
        from mini_agent.cli import read_log_file

        with patch("mini_agent.cli.get_log_directory", return_value=Path("/nonexistent")):
            read_log_file("missing.log")
            captured = capsys.readouterr()
            assert "not found" in captured.out

    def test_existing_file(self, tmp_path, capsys):
        from mini_agent.cli import read_log_file

        log_file = tmp_path / "test.log"
        log_file.write_text("Log line 1\nLog line 2\n")

        with patch("mini_agent.cli.get_log_directory", return_value=tmp_path):
            read_log_file("test.log")
            captured = capsys.readouterr()
            assert "Log line 1" in captured.out
            assert "End of file" in captured.out


class TestOpenDirectoryInFileManager:
    @patch("subprocess.run")
    def test_linux(self, mock_run):
        from mini_agent.cli import _open_directory_in_file_manager

        with patch("platform.system", return_value="Linux"):
            _open_directory_in_file_manager(Path("/tmp"))
            mock_run.assert_called_once_with(["xdg-open", "/tmp"], check=False)

    @patch("subprocess.run")
    def test_darwin(self, mock_run):
        from mini_agent.cli import _open_directory_in_file_manager

        with patch("platform.system", return_value="Darwin"):
            _open_directory_in_file_manager(Path("/tmp"))
            mock_run.assert_called_once_with(["open", "/tmp"], check=False)

    @patch("subprocess.run")
    def test_windows(self, mock_run):
        from mini_agent.cli import _open_directory_in_file_manager

        with patch("platform.system", return_value="Windows"):
            _open_directory_in_file_manager(Path("/tmp"))
            mock_run.assert_called_once_with(["explorer", "/tmp"], check=False)

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_file_not_found(self, mock_run, capsys):
        from mini_agent.cli import _open_directory_in_file_manager

        with patch("platform.system", return_value="Linux"):
            _open_directory_in_file_manager(Path("/tmp"))
            captured = capsys.readouterr()
            assert "Could not open" in captured.out


class TestPrintBanner:
    def test_prints_banner(self, capsys):
        from mini_agent.cli import print_banner

        print_banner()
        captured = capsys.readouterr()
        assert "BPS Stat Agent" in captured.out
        assert "╔" in captured.out
        assert "╚" in captured.out


class TestPrintHelp:
    def test_prints_help(self, capsys):
        from mini_agent.cli import print_help

        print_help()
        captured = capsys.readouterr()
        assert "/help" in captured.out
        assert "/clear" in captured.out
        assert "/exit" in captured.out
        assert "Keyboard Shortcuts" in captured.out
