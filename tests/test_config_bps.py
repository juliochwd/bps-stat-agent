"""Tests for BPS Stat Agent configuration lookup."""

from unittest.mock import patch

from mini_agent.config import Config


def test_find_config_file_checks_bps_user_directory(tmp_path):
    """The BPS-specific user config directory should take precedence."""
    # Create a fake home directory with bps-stat-agent config
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    config_dir = fake_home / ".bps-stat-agent" / "config"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("api_key: test\n", encoding="utf-8")

    # Mock Path.home() to return our fake home
    # Also mock cwd to be somewhere without a dev config
    fake_cwd = tmp_path / "cwd"
    fake_cwd.mkdir()
    dev_config_dir = fake_cwd / "mini_agent" / "config"
    dev_config_dir.mkdir(parents=True)
    # Don't create config.yaml in dev_config_dir so it doesn't exist

    with patch("pathlib.Path.home", return_value=fake_home):
        with patch("pathlib.Path.cwd", return_value=fake_cwd):
            found = Config.find_config_file("config.yaml")
            assert found == config_file, f"Expected {config_file}, got {found}"


def test_from_yaml_parses_logging_config(tmp_path):
    """Config.from_yaml should parse logging section."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "api_key: sk-test-real-key-12345\nlogging:\n  level: DEBUG\n  json_output: true\n  log_file: /tmp/test.log\n",
        encoding="utf-8",
    )
    config = Config.from_yaml(config_file)
    assert config.logging.level == "DEBUG"
    assert config.logging.json_output is True
    assert config.logging.log_file == "/tmp/test.log"


def test_from_yaml_logging_defaults(tmp_path):
    """Config.from_yaml should use logging defaults when section is missing."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("api_key: sk-test-real-key-12345\n", encoding="utf-8")
    config = Config.from_yaml(config_file)
    assert config.logging.level == "INFO"
    assert config.logging.json_output is False
    assert config.logging.log_file is None


def test_from_yaml_parses_tracing_config(tmp_path):
    """Config.from_yaml should parse tracing section."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        "api_key: sk-test-real-key-12345\n"
        "tracing:\n"
        "  enabled: true\n"
        "  exporter: otlp\n"
        "  otlp_endpoint: http://localhost:4317\n",
        encoding="utf-8",
    )
    config = Config.from_yaml(config_file)
    assert config.tracing.enabled is True
    assert config.tracing.exporter == "otlp"
    assert config.tracing.otlp_endpoint == "http://localhost:4317"


def test_from_yaml_tracing_defaults(tmp_path):
    """Config.from_yaml should use tracing defaults when section is missing."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("api_key: sk-test-real-key-12345\n", encoding="utf-8")
    config = Config.from_yaml(config_file)
    assert config.tracing.enabled is False
    assert config.tracing.exporter == "none"
    assert config.tracing.otlp_endpoint is None


def test_from_yaml_bash_disabled_by_default(tmp_path):
    """Config.from_yaml should have enable_bash=False by default."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("api_key: sk-test-real-key-12345\n", encoding="utf-8")
    config = Config.from_yaml(config_file)
    assert config.tools.enable_bash is False


def test_from_yaml_dotenv_loads(tmp_path, monkeypatch):
    """Config.from_yaml should call load_dotenv to load .env file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("api_key: sk-test-real-key-12345\n", encoding="utf-8")

    with patch("mini_agent.config.load_dotenv") as mock_load:
        Config.from_yaml(config_file)
        mock_load.assert_called_once()
