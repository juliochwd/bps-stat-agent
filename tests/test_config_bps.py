"""Tests for BPS Stat Agent configuration lookup."""

import os
from pathlib import Path
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
