"""Tests for Mini-Agent-BPS configuration lookup."""

from pathlib import Path

from mini_agent.config import Config


def test_find_config_file_checks_bps_user_directory(monkeypatch, tmp_path):
    """The BPS-specific user config directory should take precedence."""
    monkeypatch.setenv("HOME", str(tmp_path))
    config_dir = tmp_path / ".mini-agent-bps" / "config"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    config_file.write_text("api_key: test\n", encoding="utf-8")

    found = Config.find_config_file("config.yaml")

    assert found == config_file
