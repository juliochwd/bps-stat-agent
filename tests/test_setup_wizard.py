"""Tests for the setup wizard module."""

import json
from pathlib import Path
from unittest.mock import MagicMock

import yaml

from mini_agent.config import Config
from mini_agent.setup_wizard import (
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
    def test_returns_correct_path(self):
        result = get_user_config_dir()
        assert result == Path.home() / ".bps-stat-agent" / "config"

    def test_returns_path_object(self):
        assert isinstance(get_user_config_dir(), Path)


class TestNeedsSetup:
    def test_returns_true_when_no_config(self, monkeypatch):
        monkeypatch.setattr(Config, "find_config_file", lambda filename: None)
        assert needs_setup() is True

    def test_returns_true_when_api_key_is_placeholder(self, tmp_path, monkeypatch):
        config_file = tmp_path / "config.yaml"
        config_file.write_text('api_key: "YOUR_API_KEY_HERE"\n', encoding="utf-8")
        monkeypatch.setattr(
            Config, "find_config_file", lambda filename: config_file if filename == "config.yaml" else None
        )
        assert needs_setup() is True

    def test_returns_true_when_bps_key_empty(self, tmp_path, monkeypatch):
        config_file = tmp_path / "config.yaml"
        config_file.write_text('api_key: "sk-real-key-12345"\n', encoding="utf-8")
        mcp_file = tmp_path / "mcp.json"
        mcp_file.write_text(json.dumps({"mcpServers": {"bps": {"env": {"BPS_API_KEY": ""}}}}), encoding="utf-8")
        monkeypatch.setattr(
            Config,
            "find_config_file",
            lambda filename: config_file if filename == "config.yaml" else mcp_file if filename == "mcp.json" else None,
        )
        assert needs_setup() is True

    def test_returns_false_when_fully_configured(self, tmp_path, monkeypatch):
        config_file = tmp_path / "config.yaml"
        config_file.write_text('api_key: "sk-real-key-12345"\n', encoding="utf-8")
        mcp_file = tmp_path / "mcp.json"
        mcp_file.write_text(
            json.dumps({"mcpServers": {"bps": {"env": {"BPS_API_KEY": "real-bps-key"}}}}), encoding="utf-8"
        )
        monkeypatch.setattr(
            Config,
            "find_config_file",
            lambda filename: config_file if filename == "config.yaml" else mcp_file if filename == "mcp.json" else None,
        )
        assert needs_setup() is False

    def test_returns_true_on_corrupted_yaml(self, tmp_path, monkeypatch):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("{{{{invalid yaml", encoding="utf-8")
        monkeypatch.setattr(
            Config, "find_config_file", lambda filename: config_file if filename == "config.yaml" else None
        )
        assert needs_setup() is True

    def test_returns_true_when_no_mcp_json(self, tmp_path, monkeypatch):
        config_file = tmp_path / "config.yaml"
        config_file.write_text('api_key: "sk-real-key-12345"\n', encoding="utf-8")
        monkeypatch.setattr(
            Config, "find_config_file", lambda filename: config_file if filename == "config.yaml" else None
        )
        assert needs_setup() is True


class TestReadExistingConfig:
    def test_returns_values_from_existing_config(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            'api_key: "sk-real"\napi_base: "https://example.com"\nmodel: "gpt-4"\nprovider: "openai"\n',
            encoding="utf-8",
        )
        mcp_file = tmp_path / "mcp.json"
        mcp_file.write_text(json.dumps({"mcpServers": {"bps": {"env": {"BPS_API_KEY": "bps-123"}}}}), encoding="utf-8")

        result = _read_existing_config(tmp_path)
        assert result["ai_api_key"] == "sk-real"
        assert result["ai_api_base"] == "https://example.com"
        assert result["ai_model"] == "gpt-4"
        assert result["ai_provider"] == "openai"
        assert result["bps_api_key"] == "bps-123"

    def test_returns_empty_when_no_files(self, tmp_path):
        result = _read_existing_config(tmp_path)
        assert result == {}

    def test_excludes_placeholder_api_key(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text('api_key: "YOUR_API_KEY_HERE"\n', encoding="utf-8")
        result = _read_existing_config(tmp_path)
        assert "ai_api_key" not in result


class TestWriteConfigYaml:
    def test_creates_valid_yaml(self, tmp_path):
        config_dir = tmp_path / "config"
        path = _write_config_yaml(
            config_dir,
            ai_api_key="sk-test",
            ai_api_base="https://api.test.com",
            ai_model="test-model",
            ai_provider="openai",
        )
        assert path.exists()
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["api_key"] == "sk-test"
        assert data["api_base"] == "https://api.test.com"
        assert data["model"] == "test-model"
        assert data["provider"] == "openai"

    def test_creates_directory(self, tmp_path):
        config_dir = tmp_path / "deep" / "nested" / "config"
        _write_config_yaml(
            config_dir, ai_api_key="sk-test", ai_api_base="https://api.test.com", ai_model="m", ai_provider="openai"
        )
        assert config_dir.exists()

    def test_includes_tools_config(self, tmp_path):
        config_dir = tmp_path / "config"
        path = _write_config_yaml(
            config_dir, ai_api_key="sk-test", ai_api_base="https://api.test.com", ai_model="m", ai_provider="openai"
        )
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["tools"]["enable_mcp"] is True
        assert data["tools"]["enable_skills"] is True
        assert data["tools"]["enable_bash"] is True


class TestWriteMcpJson:
    def test_creates_valid_json(self, tmp_path):
        path = _write_mcp_json(tmp_path, bps_api_key="bps-key-123")
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["mcpServers"]["bps"]["env"]["BPS_API_KEY"] == "bps-key-123"

    def test_uses_direct_command(self, tmp_path):
        path = _write_mcp_json(tmp_path, bps_api_key="bps-key-123")
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["mcpServers"]["bps"]["command"] == "bps-mcp-server"
        assert data["mcpServers"]["bps"]["args"] == []


class TestCopySystemPrompt:
    def test_copies_file(self, tmp_path, monkeypatch):
        fake_pkg = tmp_path / "fake_pkg"
        fake_pkg.mkdir()
        (fake_pkg / "config").mkdir()
        (fake_pkg / "config" / "system_prompt.md").write_text("# Prompt", encoding="utf-8")
        monkeypatch.setattr(Config, "get_package_dir", lambda: fake_pkg)

        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()
        result = _copy_system_prompt(dest_dir)
        assert result is not None
        assert (dest_dir / "system_prompt.md").exists()

    def test_skips_existing(self, tmp_path, monkeypatch):
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()
        existing = dest_dir / "system_prompt.md"
        existing.write_text("custom prompt", encoding="utf-8")

        result = _copy_system_prompt(dest_dir)
        assert result == existing
        assert existing.read_text() == "custom prompt"


class TestPrompt:
    def test_returns_default_on_empty_input(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "")
        result = _prompt("Test", default="default_val")
        assert result == "default_val"

    def test_returns_user_input(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "user_value")
        result = _prompt("Test", default="default_val")
        assert result == "user_value"

    def test_masked_uses_getpass(self, monkeypatch):
        monkeypatch.setattr("getpass.getpass", lambda _: "secret123")
        result = _prompt("Password", masked=True)
        assert result == "secret123"

    def test_required_rejects_empty_then_accepts(self, monkeypatch):
        call_count = [0]

        def fake_input(_):
            call_count[0] += 1
            if call_count[0] == 1:
                return ""
            return "finally_provided"

        monkeypatch.setattr("builtins.input", fake_input)
        result = _prompt("Required field", required=True)
        assert result == "finally_provided"
        assert call_count[0] == 2


class TestInstallPlaywright:
    def test_failure_is_nonfatal(self, monkeypatch):
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(returncode=1))
        result = _install_playwright_chromium()
        assert result is False

    def test_file_not_found_is_nonfatal(self, monkeypatch):
        def raise_fnf(*a, **kw):
            raise FileNotFoundError("not found")

        monkeypatch.setattr("subprocess.run", raise_fnf)
        result = _install_playwright_chromium()
        assert result is False


class TestRunSetupWizard:
    def test_writes_all_files(self, tmp_path, monkeypatch):
        config_dir = tmp_path / "config"
        monkeypatch.setattr("mini_agent.setup_wizard.get_user_config_dir", lambda: config_dir)

        inputs = iter(["sk-test-key", "https://api.test.com", "test-model", "openai", "bps-key-123"])
        monkeypatch.setattr("getpass.getpass", lambda _: next(inputs))
        monkeypatch.setattr("builtins.input", lambda _: next(inputs))
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(returncode=0))

        fake_pkg = tmp_path / "fake_pkg"
        fake_pkg.mkdir()
        (fake_pkg / "config").mkdir()
        (fake_pkg / "config" / "system_prompt.md").write_text("# Prompt", encoding="utf-8")
        monkeypatch.setattr(Config, "get_package_dir", lambda: fake_pkg)

        result = run_setup_wizard()
        assert result is True
        assert (config_dir / "config.yaml").exists()
        assert (config_dir / "mcp.json").exists()

    def test_idempotent(self, tmp_path, monkeypatch):
        config_dir = tmp_path / "config"
        monkeypatch.setattr("mini_agent.setup_wizard.get_user_config_dir", lambda: config_dir)
        monkeypatch.setattr("subprocess.run", lambda *a, **kw: MagicMock(returncode=0))

        fake_pkg = tmp_path / "fake_pkg"
        fake_pkg.mkdir()
        (fake_pkg / "config").mkdir()
        (fake_pkg / "config" / "system_prompt.md").write_text("# Prompt", encoding="utf-8")
        monkeypatch.setattr(Config, "get_package_dir", lambda: fake_pkg)

        # First run
        inputs1 = iter(["sk-key-1", "https://api.test.com", "model-1", "openai", "bps-1"])
        monkeypatch.setattr("getpass.getpass", lambda _: next(inputs1))
        monkeypatch.setattr("builtins.input", lambda _: next(inputs1))
        run_setup_wizard()

        # Second run - press Enter for all (use defaults from first run)
        monkeypatch.setattr("getpass.getpass", lambda _: "")
        monkeypatch.setattr("builtins.input", lambda _: "")
        result = run_setup_wizard()
        assert result is True
