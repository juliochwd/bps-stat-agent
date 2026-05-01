"""Tests for mini_agent.research.models.decision_log."""

from __future__ import annotations

import pytest

from mini_agent.research.models.decision_log import DECISION_TYPES, DecisionEntry, DecisionLog


@pytest.fixture
def log(tmp_path):
    return DecisionLog(workspace_path=tmp_path)


class TestEntry:
    def test_auto_timestamp(self):
        assert DecisionEntry(phase="plan", decision_type="methodology").timestamp != ""

    def test_fields(self):
        e = DecisionEntry(
            phase="analyze", decision_type="statistical_test", description="SW", alternatives_considered=["KS", "AD"]
        )
        assert len(e.alternatives_considered) == 2


class TestLogDecision:
    def test_creates(self, log):
        assert log.log_decision(phase="plan", decision_type="methodology", description="Panel").description == "Panel"

    def test_count(self, log):
        log.log_decision(phase="plan", decision_type="methodology", description="A")
        log.log_decision(phase="plan", decision_type="scope_change", description="B")
        assert log.count == 2


class TestGetDecisions:
    def test_by_phase(self, log):
        log.log_decision(phase="plan", decision_type="methodology", description="A")
        log.log_decision(phase="analyze", decision_type="methodology", description="B")
        assert len(log.get_decisions(phase="plan")) == 1

    def test_by_type(self, log):
        log.log_decision(phase="plan", decision_type="methodology", description="A")
        log.log_decision(phase="plan", decision_type="scope_change", description="B")
        assert len(log.get_decisions(decision_type="scope_change")) == 1

    def test_by_both(self, log):
        log.log_decision(phase="plan", decision_type="methodology", description="A")
        log.log_decision(phase="analyze", decision_type="methodology", description="C")
        assert len(log.get_decisions(phase="plan", decision_type="methodology")) == 1

    def test_no_filter(self, log):
        log.log_decision(phase="plan", decision_type="methodology", description="A")
        log.log_decision(phase="analyze", decision_type="scope_change", description="B")
        assert len(log.get_decisions()) == 2


class TestPersistence:
    def test_save_load(self, tmp_path):
        l1 = DecisionLog(workspace_path=tmp_path)
        l1.log_decision(phase="plan", decision_type="methodology", description="OLS")
        l1.save()
        assert DecisionLog(workspace_path=tmp_path).count == 1

    def test_empty(self, tmp_path):
        assert DecisionLog(workspace_path=tmp_path).count == 0


class TestSummary:
    def test_empty(self, log):
        assert "No decisions" in log.get_summary()

    def test_has_entries(self, log):
        log.log_decision(phase="plan", decision_type="methodology", description="FE", rationale="Het")
        assert "methodology" in log.get_summary() and "FE" in log.get_summary()

    def test_count(self, log):
        log.log_decision(phase="plan", decision_type="methodology", description="A")
        log.log_decision(phase="plan", decision_type="scope_change", description="B")
        assert "2 entries" in log.get_summary()


class TestTypes:
    def test_methodology(self):
        assert "methodology" in DECISION_TYPES

    def test_variable(self):
        assert "variable_selection" in DECISION_TYPES

    def test_strings(self):
        assert all(isinstance(t, str) for t in DECISION_TYPES)
