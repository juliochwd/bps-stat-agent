"""Tests for mini_agent/setup_wizard.py — interactive setup wizard."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from mini_agent.setup_wizard import (
    CONFIG_TEMPLATE,
    _copy_system_prompt,
    _install_playwright_chromium,
    _prompt,
    _read_existing_config,
    _write_config_yaml,
    _write_mcp_json,
    get_user_config_dir,
    needs_setup,
    run_setup_wizard,
)


class TestGetUserConfigDir:
    def test_returns_path(self):
        result = get_user_config_dir()
        assert isinstance(result, Path)
        assert str(result).endswith(".bps-stat-agent/config")


class TestNeedsSetup:
    def test_needs_setup_no_config(self):
        """Returns True when no config file exists."""
        with patch("mini_agent.setup_wizard.Config.find_config_file", return_value=None):
            assert needs_setup() is True

    def test_needs_setup_empty_config(self, tmp_path):
        """Returns True when config is empty."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")
        with patch("mini_agent.setup_wizard.Config.find_config_file", return_value=config_file):
            assert needs_setup() is True

    def test_needs_setup_invalid_api_key(self, tmp_path):
        """Returns True when API key is a placeholder."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"api_key": "YOUR_API_KEY_HERE"}))
        with patch("mini_agent.setup_wizard.Config.find_config_file", return_value=config_file):
            assert needs_setup() is True

    def test_needs_setup_no_mcp_json(self, tmp_path):
        """Returns True when mcp.json is missing."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"api_key": "sk-real-key-123"}))
        with patch(
            "mini_agent.setup_wizard.Config.find_config_file",
            side_effect=lambda f: config_file if f == "config.yaml" else None,
        ):
            assert needs_setup() is True

    def test_needs_setup_empty_bps_key(self, tmp_path):
        """Returns True when BPS_API_KEY is empty in mcp.json."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"api_key": "sk-real-key-123"}))

        mcp_file = tmp_path / "mcp.json"
        mcp_file.write_text(json.dumps({"mcpServers": {"bps": {"env": {"BPS_API_KEY": ""}}}}))

        with patch(
            "mini_agent.setup_wizard.Config.find_config_file",
            side_effect=lambda f: config_file if f == "config.yaml" else mcp_file,
        ):
            assert needs_setup() is True

    def test_needs_setup_valid_config(self, tmp_path):
        """Returns False when config is valid."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"api_key": "sk-real-key-123"}))

        mcp_file = tmp_path / "mcp.json"
        mcp_file.write_text(
            json.dumps({"mcpServers": {"bps": {"env": {"BPS_API_KEY": "abc123"}}}})
        )

        with patch(
            "mini_agent.setup_wizard.Config.find_config_file",
            side_effect=lambda f: config_file if f == "config.yaml" else mcp_file,
        ):
            assert needs_setup() is False

    def test_needs_setup_exception_returns_true(self):
        """Returns True on any exception."""
        with patch(
            "mini_agent.setup_wizard.Config.find_config_file",
            side_effect=Exception("boom"),
        ):
            assert needs_setup() is True


class TestReadExistingConfig:
    def test_reads_existing_config(self, tmp_path):
        """Reads existing config values."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        config_file = config_dir / "config.yaml"
        config_file.write_text(
            yaml.dump(
                {
                    "api_key": "sk-real-key",
                    "api_base": "https://api.example.com",
                    "model": "gpt-4",
                    "provider": "openai",
                }
            )
        )

        mcp_file = config_dir / "mcp.json"
        mcp_file.write_text(
            json.dumps({"mcpServers": {"bps": {"env": {"BPS_API_KEY": "bps-key-123"}}}})
        )

        result = _read_existing_config(config_dir)
        assert result["ai_api_key"] == "sk-real-key"
        assert result["ai_api_base"] == "https://api.example.com"
        assert result["ai_model"] == "gpt-4"
        assert result["ai_provider"] == "openai"
        assert result["bps_api_key"] == "bps-key-123"

    def test_reads_empty_dir(self, tmp_path):
        """Returns empty dict for empty directory."""
        result = _read_existing_config(tmp_path)
        assert result == {}

    def test_skips_invalid_api_key(self, tmp_path):
        """Skips placeholder API keys."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        config_file.write_text(yaml.dump({"api_key": "YOUR_API_KEY_HERE"}))

        result = _read_existing_config(config_dir)
        assert "ai_api_key" not in result


class TestWriteConfigYaml:
    def test_writes_config(self, tmp_path):
        """Writes config.yaml with correct content."""
        config_dir = tmp_path / "config"
        path = _write_config_yaml(
            config_dir,
            ai_api_key="sk-test",
            ai_api_base="https://api.test.com",
            ai_model="gpt-4",
            ai_provider="openai",
        )

        assert path.exists()
        content = path.read_text()
        assert "sk-test" in content
        assert "https://api.test.com" in content
        assert "gpt-4" in content
        assert "openai" in content

    def test_creates_directory(self, tmp_path):
        """Creates config directory if it doesn't exist."""
        config_dir = tmp_path / "deep" / "nested" / "config"
        path = _write_config_yaml(
            config_dir,
            ai_api_key="key",
            ai_api_base="base",
            ai_model="model",
            ai_provider="openai",
        )
        assert path.exists()
        assert config_dir.exists()


class TestWriteMcpJson:
    def test_writes_mcp_json(self, tmp_path):
        """Writes mcp.json with BPS API key."""
        config_dir = tmp_path / "config"
        path = _write_mcp_json(config_dir, bps_api_key="test-bps-key")

        assert path.exists()
        data = json.loads(path.read_text())
        assert "mcpServers" in data
        assert data["mcpServers"]["bps"]["env"]["BPS_API_KEY"] == "test-bps-key"

    def test_includes_research_servers(self, tmp_path):
        """Includes research ecosystem MCP servers."""
        config_dir = tmp_path / "config"
        path = _write_mcp_json(config_dir, bps_api_key="key")

        data = json.loads(path.read_text())
        servers = data["mcpServers"]
        assert "papers" in servers
        assert "pdf" in servers
        assert "jupyter" in servers


class TestCopySystemPrompt:
    def test_copies_system_prompt(self, tmp_path):
        """Copies system_prompt.md from package config."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        # Create a fake source
        with patch("mini_agent.setup_wizard.Config.get_package_dir") as mock_pkg:
            pkg_dir = tmp_path / "package"
            pkg_config = pkg_dir / "config"
            pkg_config.mkdir(parents=True)
            (pkg_config / "system_prompt.md").write_text("# System Prompt")
            mock_pkg.return_value = pkg_dir

            result = _copy_system_prompt(config_dir)
            assert result is not None
            assert result.read_text() == "# System Prompt"

    def test_does_not_overwrite_existing(self, tmp_path):
        """Does not overwrite existing system_prompt.md."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        existing = config_dir / "system_prompt.md"
        existing.write_text("Custom prompt")

        result = _copy_system_prompt(config_dir)
        assert result == existing
        assert result.read_text() == "Custom prompt"


class TestInstallPlaywrightChromium:
    @patch("mini_agent.setup_wizard.subprocess.run")
    def test_successful_install(self, mock_run):
        """Returns True on successful install."""
        mock_run.return_value = MagicMock(returncode=0)
        assert _install_playwright_chromium() is True

    @patch("mini_agent.setup_wizard.subprocess.run")
    def test_failed_install(self, mock_run):
        """Returns False on non-zero return code."""
        mock_run.return_value = MagicMock(returncode=1)
        assert _install_playwright_chromium() is False

    @patch("mini_agent.setup_wizard.subprocess.run", side_effect=FileNotFoundError)
    def test_playwright_not_found(self, mock_run):
        """Returns False when playwright not found."""
        assert _install_playwright_chromium() is False

    @patch("mini_agent.setup_wizard.subprocess.run")
    def test_timeout(self, mock_run):
        """Returns False on timeout."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=300)
        assert _install_playwright_chromium() is False


class TestPrompt:
    @patch("builtins.input", return_value="user_value")
    def test_returns_user_input(self, mock_input):
        result = _prompt("Label")
        assert result == "user_value"

    @patch("builtins.input", return_value="")
    def test_returns_default_when_empty(self, mock_input):
        result = _prompt("Label", default="default_val")
        assert result == "default_val"

    @patch("builtins.input", side_effect=EOFError)
    def test_eof_returns_default(self, mock_input):
        result = _prompt("Label", default="fallback")
        assert result == "fallback"

    @patch("builtins.input", side_effect=KeyboardInterrupt)
    def test_keyboard_interrupt_returns_default(self, mock_input):
        result = _prompt("Label", default="fallback")
        assert result == "fallback"

    @patch("builtins.input", side_effect=["", "value"])
    def test_required_field_reprompts(self, mock_input):
        result = _prompt("Label", required=True)
        assert result == "value"


class TestRunSetupWizard:
    @patch("mini_agent.setup_wizard._install_playwright_chromium", return_value=True)
    @patch("mini_agent.setup_wizard._copy_system_prompt", return_value=None)
    @patch("mini_agent.setup_wizard._prompt")
    @patch("mini_agent.setup_wizard.get_user_config_dir")
    def test_full_wizard_run(self, mock_dir, mock_prompt, mock_copy, mock_pw, tmp_path):
        """Test full wizard run with mocked inputs."""
        config_dir = tmp_path / "config"
        mock_dir.return_value = config_dir
        mock_prompt.side_effect = [
            "sk-test-key",  # AI API Key
            "https://api.test.com",  # AI API Base
            "gpt-4",  # AI Model
            "openai",  # AI Provider
            "bps-key-123",  # BPS API Key
        ]

        result = run_setup_wizard(force=True)
        assert result is True
        assert (config_dir / "config.yaml").exists()
        assert (config_dir / "mcp.json").exists()
