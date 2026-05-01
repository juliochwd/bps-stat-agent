"""Extended tests for mini_agent/config.py — configuration management."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from mini_agent.config import (
    AgentConfig,
    Config,
    LLMConfig,
    LoggingConfig,
    MCPConfig,
    ResearchConfig,
    RetryConfig,
    ToolsConfig,
    TracingConfig,
)


class TestRetryConfig:
    def test_defaults(self):
        rc = RetryConfig()
        assert rc.enabled is True
        assert rc.max_retries == 3
        assert rc.initial_delay == 1.0
        assert rc.max_delay == 60.0
        assert rc.exponential_base == 2.0


class TestLLMConfig:
    def test_defaults(self):
        lc = LLMConfig(api_key="test-key")
        assert lc.api_key == "test-key"
        assert lc.api_base == "https://api.minimax.io"
        assert lc.model == "MiniMax-M2.5"
        assert lc.provider == "anthropic"


class TestAgentConfig:
    def test_defaults(self):
        ac = AgentConfig()
        assert ac.max_steps == 50
        assert ac.workspace_dir == "./workspace"


class TestMCPConfig:
    def test_defaults(self):
        mc = MCPConfig()
        assert mc.connect_timeout == 10.0
        assert mc.execute_timeout == 60.0
        assert mc.sse_read_timeout == 120.0


class TestLoggingConfig:
    def test_defaults(self):
        lc = LoggingConfig()
        assert lc.level == "INFO"
        assert lc.json_output is False
        assert lc.log_file is None


class TestTracingConfig:
    def test_defaults(self):
        tc = TracingConfig()
        assert tc.enabled is False
        assert tc.exporter == "none"


class TestToolsConfig:
    def test_defaults(self):
        tc = ToolsConfig()
        assert tc.enable_file_tools is True
        assert tc.enable_bash is False
        assert tc.enable_mcp is True


class TestResearchConfig:
    def test_defaults(self):
        rc = ResearchConfig()
        assert rc.primary_model == "claude-sonnet-4-20250514"
        assert rc.max_cost_per_project == 50.0
        assert rc.sandbox_backend == "docker"


class TestConfigFromYaml:
    def test_load_valid_config(self, tmp_path):
        """Test loading a valid config file."""
        config_data = {
            "api_key": "sk-valid-key-123",
            "api_base": "https://api.test.com",
            "model": "gpt-4",
            "provider": "openai",
            "max_steps": 100,
            "workspace_dir": "./ws",
            "retry": {
                "enabled": True,
                "max_retries": 5,
            },
            "tools": {
                "enable_file_tools": True,
                "enable_bash": True,
                "mcp": {
                    "connect_timeout": 15.0,
                },
            },
            "logging": {
                "level": "DEBUG",
                "json_output": True,
            },
            "tracing": {
                "enabled": True,
                "exporter": "console",
            },
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = Config.from_yaml(config_file)
        assert config.llm.api_key == "sk-valid-key-123"
        assert config.llm.provider == "openai"
        assert config.agent.max_steps == 100
        assert config.tools.enable_bash is True
        assert config.logging.level == "DEBUG"
        assert config.tracing.enabled is True

    def test_load_missing_file(self, tmp_path):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            Config.from_yaml(tmp_path / "nonexistent.yaml")

    def test_load_empty_file(self, tmp_path):
        """Test loading empty config file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("")

        with pytest.raises(ValueError, match="empty"):
            Config.from_yaml(config_file)

    def test_load_missing_api_key(self, tmp_path):
        """Test loading config without api_key."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"model": "gpt-4"}))

        with pytest.raises(ValueError, match="api_key"):
            Config.from_yaml(config_file)

    def test_load_invalid_api_key(self, tmp_path):
        """Test loading config with placeholder api_key when no env vars set."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"api_key": "YOUR_API_KEY_HERE"}))

        # Clear all env vars that could provide a key
        env_overrides = {
            "MINIMAX_API_KEY": "",
            "ANTHROPIC_AUTH_TOKEN": "",
            "OPENAI_API_KEY": "",
        }
        with patch.dict(os.environ, env_overrides, clear=False):
            # Remove the keys entirely
            for k in env_overrides:
                os.environ.pop(k, None)
            with pytest.raises(ValueError, match="valid API Key"):
                Config.from_yaml(config_file)

    def test_load_env_override(self, tmp_path):
        """Test that env var overrides placeholder api_key."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump({"api_key": "YOUR_API_KEY_HERE"}))

        # Clear other env vars and set only OPENAI_API_KEY
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "sk-from-env",
            "MINIMAX_API_KEY": "",
            "ANTHROPIC_AUTH_TOKEN": "",
        }, clear=False):
            os.environ.pop("MINIMAX_API_KEY", None)
            os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)
            config = Config.from_yaml(config_file)
            assert config.llm.api_key == "sk-from-env"

    def test_load_with_research_config(self, tmp_path):
        """Test loading config with research section."""
        config_data = {
            "api_key": "sk-valid-key",
            "research": {
                "primary_model": "gpt-4o",
                "max_cost_per_project": 25.0,
            },
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_data))

        config = Config.from_yaml(config_file)
        assert config.research is not None
        assert config.research.primary_model == "gpt-4o"
        assert config.research.max_cost_per_project == 25.0


class TestConfigFindConfigFile:
    def test_find_in_user_dir(self, tmp_path):
        """Test finding config in user directory."""
        user_config = tmp_path / ".bps-stat-agent" / "config" / "config.yaml"
        user_config.parent.mkdir(parents=True)
        user_config.write_text("api_key: test")

        with patch("pathlib.Path.home", return_value=tmp_path):
            with patch("pathlib.Path.cwd", return_value=tmp_path / "other"):
                result = Config.find_config_file("config.yaml")
                assert result == user_config

    def test_find_returns_none(self, tmp_path):
        """Test returns None when not found."""
        with patch("pathlib.Path.home", return_value=tmp_path):
            with patch("pathlib.Path.cwd", return_value=tmp_path):
                result = Config.find_config_file("nonexistent.yaml")
                # May return package config or None
                if result is not None:
                    assert result.name == "nonexistent.yaml"


class TestConfigGetPackageDir:
    def test_returns_path(self):
        result = Config.get_package_dir()
        assert isinstance(result, Path)
        assert result.exists()


class TestConfigGetDefaultConfigPath:
    def test_returns_path(self):
        result = Config.get_default_config_path()
        assert isinstance(result, Path)
        assert "config.yaml" in str(result)
