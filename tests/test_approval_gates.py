"""Tests for mini_agent.research.approval_gates."""

from __future__ import annotations

import pytest

from mini_agent.research.approval_gates import ApprovalGateManager, ApprovalRequest, ApprovalResponse


@pytest.fixture
def enabled():
    return ApprovalGateManager()


@pytest.fixture
def disabled():
    return ApprovalGateManager(gates_config={g: False for g in ApprovalGateManager.GATE_TYPES})


@pytest.fixture
def partial():
    c = {g: False for g in ApprovalGateManager.GATE_TYPES}
    c["methodology_selection"] = True
    return ApprovalGateManager(gates_config=c)


class TestModels:
    def test_request_timestamp(self):
        assert ApprovalRequest(gate_type="methodology_selection", description="t").timestamp != ""

    def test_request_fields(self):
        r = ApprovalRequest(gate_type="scope_changes", description="E", options=["A", "B"], context={"r": "d"})
        assert r.options == ["A", "B"]

    def test_response_default(self):
        assert ApprovalResponse().approved is False

    def test_response_approved(self):
        assert ApprovalResponse(approved=True).approved is True


class TestGateEnabled:
    def test_all_enabled(self, enabled):
        for g in ApprovalGateManager.GATE_TYPES:
            assert enabled.is_gate_enabled(g) is True

    def test_all_disabled(self, disabled):
        for g in ApprovalGateManager.GATE_TYPES:
            assert disabled.is_gate_enabled(g) is False

    def test_unknown(self, enabled):
        assert enabled.is_gate_enabled("nonexistent") is False


class TestAutoApprove:
    def test_disabled_auto(self, disabled):
        r = disabled.request_approval(gate_type="methodology_selection", description="OLS")
        assert r.approved is True and "Auto" in r.feedback

    def test_logs(self, disabled):
        disabled.request_approval(gate_type="methodology_selection", description="OLS")
        assert len(disabled.log) == 1


class TestEnabledGate:
    def test_pending(self, enabled):
        r = enabled.request_approval(gate_type="methodology_selection", description="Panel", options=["OLS", "FE"])
        assert r.approved is False and "Awaiting" in r.feedback

    def test_pending_count(self, enabled):
        enabled.request_approval(gate_type="methodology_selection", description="A")
        enabled.request_approval(gate_type="variable_selection", description="B")
        assert enabled.get_pending_count() == 2


class TestRecord:
    def test_approval(self, enabled):
        enabled.request_approval(gate_type="methodology_selection", description="OLS")
        r = enabled.record_response(0, approved=True, selected_option="OLS", feedback="OK")
        assert r.approved is True and r.selected_option == "OLS"

    def test_denial(self, enabled):
        enabled.request_approval(gate_type="final_submission", description="Submit")
        assert enabled.record_response(0, approved=False, feedback="No").approved is False

    def test_count_decreases(self, enabled):
        enabled.request_approval(gate_type="methodology_selection", description="A")
        enabled.record_response(0, approved=True)
        assert enabled.get_pending_count() == 0


class TestFormat:
    def test_blocking(self, enabled):
        assert "BLOCKING" in enabled.format_request(ApprovalRequest(gate_type="methodology_selection", description="X"))

    def test_advisory(self, enabled):
        assert "ADVISORY" in enabled.format_request(ApprovalRequest(gate_type="outlier_removal", description="X"))

    def test_options(self, enabled):
        f = enabled.format_request(
            ApprovalRequest(gate_type="variable_selection", description="X", options=["GDP", "CPI"])
        )
        assert "GDP" in f and "CPI" in f


class TestPartial:
    def test_enabled_blocks(self, partial):
        assert partial.request_approval(gate_type="methodology_selection", description="t").approved is False

    def test_disabled_auto(self, partial):
        assert partial.request_approval(gate_type="outlier_removal", description="t").approved is True
