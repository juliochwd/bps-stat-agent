"""Extended tests for mini_agent/research/approval_gates.py."""

from unittest.mock import MagicMock

import pytest

from mini_agent.research.approval_gates import (
    ApprovalGate,
    ApprovalGateManager,
    ApprovalRequest,
    ApprovalResponse,
    GateResult,
    QualityGateEvaluator,
    _BLOCKING_GATES,
    _PHASE_GATE_CRITERIA,
)


@pytest.fixture
def mock_project_state():
    """Create a mock project state."""
    state = MagicMock()
    state.research_questions = ["Q1", "Q2"]
    state.phase.value = "collect"
    state.data_inventory = [{"source": "BPS"}]
    state.literature.total_papers = 5
    state.literature.verified = True
    state.paper.sections = {
        "introduction": MagicMock(status="final"),
        "methodology": MagicMock(status="final"),
        "results": MagicMock(status="final"),
        "discussion": MagicMock(status="final"),
    }
    state.quality.statistical_validity = "passed"
    state.quality.style_compliance = "passed"
    state.quality.peer_review = "passed"
    return state


class TestGateResult:
    def test_defaults(self):
        gr = GateResult()
        assert gr.passed is False
        assert gr.feedback == ""
        assert gr.criteria_results == {}

    def test_custom(self):
        gr = GateResult(
            passed=True,
            feedback="All good",
            criteria_results={"c1": True, "c2": True},
        )
        assert gr.passed is True
        assert len(gr.criteria_results) == 2


class TestApprovalGate:
    def test_auto_approve(self, mock_project_state):
        gate = ApprovalGate("test_gate", ["criterion 1"], auto_approve=True)
        result = gate.evaluate(mock_project_state)
        assert result.passed is True
        assert "auto-approved" in result.feedback

    def test_get_criteria(self):
        gate = ApprovalGate("test", ["c1", "c2", "c3"])
        assert gate.get_criteria() == ["c1", "c2", "c3"]

    def test_research_questions_defined(self, mock_project_state):
        gate = ApprovalGate("test", ["Research questions defined"])
        result = gate.evaluate(mock_project_state)
        assert result.criteria_results["Research questions defined"] is True

    def test_research_questions_not_defined(self, mock_project_state):
        mock_project_state.research_questions = []
        gate = ApprovalGate("test", ["Research questions defined"])
        result = gate.evaluate(mock_project_state)
        assert result.criteria_results["Research questions defined"] is False

    def test_data_sources_identified(self, mock_project_state):
        gate = ApprovalGate("test", ["Data sources identified"])
        result = gate.evaluate(mock_project_state)
        assert result.criteria_results["Data sources identified"] is True

    def test_literature_collected(self, mock_project_state):
        gate = ApprovalGate("test", ["Literature collected and reviewed"])
        result = gate.evaluate(mock_project_state)
        assert result.criteria_results["Literature collected and reviewed"] is True

    def test_citations_verified(self, mock_project_state):
        gate = ApprovalGate("test", ["Citations verified"])
        result = gate.evaluate(mock_project_state)
        assert result.criteria_results["Citations verified"] is True

    def test_analysis_complete(self, mock_project_state):
        gate = ApprovalGate("test", ["Analysis complete with results"])
        result = gate.evaluate(mock_project_state)
        assert result.criteria_results["Analysis complete with results"] is True

    def test_statistical_validity(self, mock_project_state):
        gate = ApprovalGate("test", ["Statistical validity verified"])
        result = gate.evaluate(mock_project_state)
        assert result.criteria_results["Statistical validity verified"] is True

    def test_style_compliance(self, mock_project_state):
        gate = ApprovalGate("test", ["Style compliance checked"])
        result = gate.evaluate(mock_project_state)
        assert result.criteria_results["Style compliance checked"] is True

    def test_peer_review(self, mock_project_state):
        gate = ApprovalGate("test", ["Peer review completed"])
        result = gate.evaluate(mock_project_state)
        assert result.criteria_results["Peer review completed"] is True

    def test_all_sections_final(self, mock_project_state):
        gate = ApprovalGate("test", ["All sections final"])
        result = gate.evaluate(mock_project_state)
        assert result.criteria_results["All sections final"] is True

    def test_unknown_criterion_fails(self, mock_project_state):
        gate = ApprovalGate("test", ["Unknown criterion xyz"])
        result = gate.evaluate(mock_project_state)
        assert result.criteria_results["Unknown criterion xyz"] is False

    def test_failed_gate_feedback(self, mock_project_state):
        mock_project_state.research_questions = []
        gate = ApprovalGate("test", ["Research questions defined", "Data sources identified"])
        result = gate.evaluate(mock_project_state)
        assert result.passed is False
        assert "failed" in result.feedback


class TestQualityGateEvaluator:
    def test_default_gates(self):
        evaluator = QualityGateEvaluator()
        phases = evaluator.list_phases()
        assert "plan" in phases
        assert "collect" in phases
        assert "analyze" in phases
        assert "write" in phases
        assert "review" in phases

    def test_evaluate_phase(self, mock_project_state):
        evaluator = QualityGateEvaluator()
        result = evaluator.evaluate_phase("plan", mock_project_state)
        assert isinstance(result, GateResult)

    def test_evaluate_unknown_phase(self, mock_project_state):
        evaluator = QualityGateEvaluator()
        result = evaluator.evaluate_phase("unknown", mock_project_state)
        assert result.passed is True
        assert "No gate configured" in result.feedback

    def test_get_phase_criteria(self):
        evaluator = QualityGateEvaluator()
        criteria = evaluator.get_phase_criteria("plan")
        assert len(criteria) > 0
        assert "Research questions defined" in criteria

    def test_get_phase_criteria_unknown(self):
        evaluator = QualityGateEvaluator()
        criteria = evaluator.get_phase_criteria("unknown")
        assert criteria == []

    def test_set_auto_approve(self, mock_project_state):
        evaluator = QualityGateEvaluator()
        evaluator.set_auto_approve("plan", True)
        result = evaluator.evaluate_phase("plan", mock_project_state)
        assert result.passed is True

    def test_set_all_auto_approve(self, mock_project_state):
        evaluator = QualityGateEvaluator()
        evaluator.set_all_auto_approve(True)
        for phase in ["plan", "collect", "analyze", "write", "review"]:
            result = evaluator.evaluate_phase(phase, mock_project_state)
            assert result.passed is True

    def test_add_gate(self, mock_project_state):
        evaluator = QualityGateEvaluator()
        custom_gate = ApprovalGate("custom", ["Custom criterion"], auto_approve=True)
        evaluator.add_gate("custom_phase", custom_gate)
        result = evaluator.evaluate_phase("custom_phase", mock_project_state)
        assert result.passed is True

    def test_get_summary(self, mock_project_state):
        evaluator = QualityGateEvaluator()
        summary = evaluator.get_summary(mock_project_state)
        assert "Quality Gate Summary" in summary
        assert "PLAN" in summary


class TestApprovalGateManager:
    def test_init_defaults(self):
        mgr = ApprovalGateManager()
        assert len(mgr._config) == len(ApprovalGateManager.GATE_TYPES)
        assert all(v is True for v in mgr._config.values())

    def test_init_custom(self):
        mgr = ApprovalGateManager({"methodology_selection": False})
        assert mgr.is_gate_enabled("methodology_selection") is False

    def test_is_gate_enabled(self):
        mgr = ApprovalGateManager()
        assert mgr.is_gate_enabled("methodology_selection") is True
        assert mgr.is_gate_enabled("nonexistent") is False

    def test_request_approval_enabled(self):
        mgr = ApprovalGateManager()
        resp = mgr.request_approval("methodology_selection", "Choose method")
        assert resp.approved is False
        assert "Awaiting" in resp.feedback
        assert len(mgr.log) == 1

    def test_request_approval_disabled(self):
        mgr = ApprovalGateManager({"methodology_selection": False})
        resp = mgr.request_approval("methodology_selection", "Choose method")
        assert resp.approved is True
        assert "Auto-approved" in resp.feedback

    def test_record_response(self):
        mgr = ApprovalGateManager()
        mgr.request_approval("methodology_selection", "Choose method")
        resp = mgr.record_response(0, approved=True, feedback="Looks good")
        assert resp.approved is True
        assert resp.feedback == "Looks good"

    def test_record_response_invalid_index(self):
        mgr = ApprovalGateManager()
        with pytest.raises(IndexError):
            mgr.record_response(99, approved=True)

    def test_format_request_blocking(self):
        mgr = ApprovalGateManager()
        req = ApprovalRequest(
            gate_type="methodology_selection",
            description="Select regression method",
            options=["OLS", "GLS", "GMM"],
        )
        formatted = mgr.format_request(req)
        assert "BLOCKING" in formatted
        assert "Methodology Selection" in formatted
        assert "OLS" in formatted

    def test_format_request_advisory(self):
        mgr = ApprovalGateManager()
        req = ApprovalRequest(
            gate_type="outlier_removal",
            description="Remove 3 outliers",
        )
        formatted = mgr.format_request(req)
        assert "ADVISORY" in formatted

    def test_get_pending_count(self):
        mgr = ApprovalGateManager()
        mgr.request_approval("methodology_selection", "test1")
        mgr.request_approval("variable_selection", "test2")
        assert mgr.get_pending_count() == 2

        mgr.record_response(0, approved=True)
        assert mgr.get_pending_count() == 1
