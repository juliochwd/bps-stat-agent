"""Tests for mini_agent.research.session_resume."""

from __future__ import annotations

import pytest

from mini_agent.research.session_resume import SessionCheckpoint, SessionResumeManager


@pytest.fixture
def manager(tmp_path):
    return SessionResumeManager(workspace_path=tmp_path)


class TestCreateCheckpoint:
    def test_creates_yaml(self, manager, tmp_path):
        manager.create_checkpoint(phase="plan", messages_summary="Started")
        assert len(list((tmp_path / ".sessions").glob("checkpoint_*.yaml"))) == 1

    def test_creates_latest(self, manager, tmp_path):
        manager.create_checkpoint(phase="plan", messages_summary="x")
        assert (tmp_path / ".sessions" / "latest.yaml").exists()

    def test_returns_dict(self, manager):
        r = manager.create_checkpoint(
            phase="collect", messages_summary="Data", key_decisions=["BPS"], pending_tasks=["GDP"]
        )
        assert isinstance(r, dict) and r["phase"] == "collect"

    def test_timestamp(self, manager):
        assert manager.create_checkpoint(phase="plan", messages_summary="x")["timestamp"] != ""


class TestGetLatest:
    def test_none_when_empty(self, manager):
        assert manager.get_latest_checkpoint() is None

    def test_returns_most_recent(self, manager):
        manager.create_checkpoint(phase="plan", messages_summary="first")
        manager.create_checkpoint(phase="collect", messages_summary="second")
        assert manager.get_latest_checkpoint()["phase"] == "collect"


class TestListCheckpoints:
    def test_empty(self, manager):
        assert manager.list_checkpoints() == []

    def test_returns_all(self, manager):
        for p in ["plan", "collect", "analyze"]:
            manager.create_checkpoint(phase=p, messages_summary=p)
        assert len(manager.list_checkpoints()) == 3


class TestResumeContext:
    def test_empty_when_no_cp(self, manager):
        assert manager.get_resume_context() == ""

    def test_contains_phase(self, manager):
        manager.create_checkpoint(phase="write", messages_summary="Writing")
        assert "WRITE" in manager.get_resume_context()

    def test_contains_summary(self, manager):
        manager.create_checkpoint(phase="plan", messages_summary="Defined RQs")
        assert "Defined RQs" in manager.get_resume_context()

    def test_contains_decisions(self, manager):
        manager.create_checkpoint(phase="plan", messages_summary="x", key_decisions=["Panel"])
        assert "Panel" in manager.get_resume_context()

    def test_contains_tasks(self, manager):
        manager.create_checkpoint(phase="plan", messages_summary="x", pending_tasks=["Download"])
        assert "Download" in manager.get_resume_context()


class TestCleanup:
    def test_keeps_last_n(self, manager):
        for i in range(7):
            manager.create_checkpoint(phase="plan", messages_summary=f"cp-{i}")
        assert manager.cleanup_old_checkpoints(keep_last=3) == 4

    def test_no_removal(self, manager):
        manager.create_checkpoint(phase="plan", messages_summary="one")
        assert manager.cleanup_old_checkpoints(keep_last=5) == 0


class TestModel:
    def test_auto_timestamp(self):
        assert SessionCheckpoint(phase="plan", messages_summary="t").timestamp != ""
