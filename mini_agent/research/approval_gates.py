"""Human-in-the-loop approval gates for critical research decisions.

Provides phase-aware quality gates that evaluate project state against
configurable criteria.  Each gate can operate in auto-approve mode
(for CI/testing) or require explicit human confirmation before the
research workflow proceeds to the next phase.
"""

from __future__ import annotations

from datetime import UTC
from typing import Any

from pydantic import BaseModel, Field

from .project_state import ProjectState

# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------


class GateResult(BaseModel):
    """Result of evaluating an approval gate.

    Attributes:
        passed: Whether all criteria were satisfied.
        feedback: Human-readable summary of the evaluation.
        criteria_results: Per-criterion pass/fail mapping.
    """

    passed: bool = False
    feedback: str = ""
    criteria_results: dict[str, bool] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Single approval gate
# ---------------------------------------------------------------------------


class ApprovalGate:
    """A single approval gate with named criteria.

    Each gate represents a checkpoint in the research workflow where
    the project state is evaluated against a set of criteria.  Gates
    can be configured to auto-approve (useful for testing or fully
    autonomous runs).

    Args:
        gate_name: Unique identifier for this gate.
        criteria: List of human-readable criteria descriptions.
        auto_approve: If ``True``, the gate always passes.
    """

    def __init__(
        self,
        gate_name: str,
        criteria: list[str],
        auto_approve: bool = False,
    ) -> None:
        self.gate_name = gate_name
        self.criteria = list(criteria)
        self.auto_approve = auto_approve

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate(self, project_state: ProjectState) -> GateResult:
        """Evaluate the gate against the current project state.

        When ``auto_approve`` is ``True`` every criterion is marked as
        passed.  Otherwise, each criterion is checked against the
        project state using heuristic rules.

        Args:
            project_state: The current project state to evaluate.

        Returns:
            A ``GateResult`` with per-criterion outcomes.
        """
        if self.auto_approve:
            return GateResult(
                passed=True,
                feedback=f"Gate '{self.gate_name}' auto-approved.",
                criteria_results={c: True for c in self.criteria},
            )

        criteria_results = self._check_criteria(project_state)
        passed = all(criteria_results.values())

        failed = [c for c, ok in criteria_results.items() if not ok]
        if passed:
            feedback = f"Gate '{self.gate_name}' passed all {len(self.criteria)} criteria."
        else:
            feedback = f"Gate '{self.gate_name}' failed {len(failed)}/{len(self.criteria)} criteria: " + "; ".join(
                failed
            )

        return GateResult(
            passed=passed,
            feedback=feedback,
            criteria_results=criteria_results,
        )

    def get_criteria(self) -> list[str]:
        """Return the list of criteria for this gate.

        Returns:
            Copy of the criteria list.
        """
        return list(self.criteria)

    # ------------------------------------------------------------------
    # Internal criterion checks
    # ------------------------------------------------------------------

    def _check_criteria(self, state: ProjectState) -> dict[str, bool]:
        """Run heuristic checks for each criterion.

        The checks are intentionally simple — they verify that the
        project state contains the expected artefacts rather than
        performing deep content analysis.
        """
        results: dict[str, bool] = {}

        for criterion in self.criteria:
            results[criterion] = self._check_single(criterion, state)

        return results

    def _check_single(self, criterion: str, state: ProjectState) -> bool:  # noqa: PLR0911
        """Evaluate a single criterion string against project state."""
        cl = criterion.lower()

        # Research questions defined
        if "research question" in cl and "defined" in cl:
            return len(state.research_questions) > 0

        # Methodology selected
        if "methodology" in cl and ("selected" in cl or "defined" in cl):
            return state.phase.value not in ("plan",)

        # Data sources identified / collected
        if "data source" in cl and ("identified" in cl or "collected" in cl):
            return len(state.data_inventory) > 0

        # Literature collected
        if "literature" in cl and ("collected" in cl or "reviewed" in cl):
            return state.literature.total_papers > 0

        # Bibliography exists
        if "bibliography" in cl or "bib file" in cl:
            return state.literature.total_papers > 0

        # Citations verified
        if "citation" in cl and "verified" in cl:
            return state.literature.verified

        # Analysis complete / results available
        if "analysis" in cl and ("complete" in cl or "results" in cl):
            results_section = state.paper.sections.get("results")
            return results_section is not None and results_section.status not in ("pending",)

        # Sections drafted
        if "section" in cl and ("drafted" in cl or "written" in cl or "complete" in cl):
            drafted = sum(1 for s in state.paper.sections.values() if s.status not in ("pending", "in_progress"))
            return drafted >= len(state.paper.sections) // 2

        # All sections final
        if "all sections" in cl and "final" in cl:
            return all(s.status == "final" for s in state.paper.sections.values())

        # Quality gates passed
        if "quality" in cl and ("passed" in cl or "run" in cl):
            return state.quality.statistical_validity not in ("not_run", "failed")

        # Statistical validity
        if "statistical" in cl and "validity" in cl:
            return state.quality.statistical_validity == "passed"

        # Style compliance
        if "style" in cl and "compliance" in cl:
            return state.quality.style_compliance == "passed"

        # Peer review
        if "peer review" in cl:
            return state.quality.peer_review not in ("not_run", "failed")

        # Default: cannot verify → mark as not passed
        return False


# ---------------------------------------------------------------------------
# Phase-level evaluator
# ---------------------------------------------------------------------------


# Pre-defined gate criteria per phase
_PHASE_GATE_CRITERIA: dict[str, list[str]] = {
    "plan": [
        "Research questions defined",
        "Methodology selected",
        "Data sources identified",
        "Literature search strategy defined",
    ],
    "collect": [
        "Data sources collected",
        "Literature collected and reviewed",
        "Bibliography file created",
        "Data quality checks passed",
    ],
    "analyze": [
        "Analysis complete with results",
        "Statistical validity verified",
        "Figures and tables generated",
        "Results section drafted",
    ],
    "write": [
        "All sections drafted",
        "Citations verified",
        "Style compliance checked",
        "Abstract written",
    ],
    "review": [
        "Peer review completed",
        "Statistical validity verified",
        "All sections final",
        "Quality gates passed",
    ],
}


class QualityGateEvaluator:
    """Evaluates quality gates for each research phase.

    Wraps a collection of ``ApprovalGate`` instances — one per phase —
    and provides a unified interface for phase-level evaluation.

    Args:
        gates: Optional mapping of phase name to ``ApprovalGate``.
               If not provided, default gates are created from
               ``_PHASE_GATE_CRITERIA``.
    """

    def __init__(self, gates: dict[str, ApprovalGate] | None = None) -> None:
        if gates is not None:
            self._gates = dict(gates)
        else:
            self._gates = self._build_default_gates()

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------

    def evaluate_phase(
        self,
        phase: str,
        project_state: ProjectState,
    ) -> GateResult:
        """Evaluate the quality gate for a specific phase.

        Args:
            phase: Phase name (e.g. ``"plan"``, ``"collect"``).
            project_state: Current project state.

        Returns:
            ``GateResult`` for the phase.  If no gate is configured
            for the phase, a passing result is returned.
        """
        gate = self._gates.get(phase.lower())
        if gate is None:
            return GateResult(
                passed=True,
                feedback=f"No gate configured for phase '{phase}'.",
                criteria_results={},
            )

        return gate.evaluate(project_state)

    def get_phase_criteria(self, phase: str) -> list[str]:
        """Get the criteria list for a specific phase.

        Args:
            phase: Phase name.

        Returns:
            List of criteria strings, or empty list if no gate exists.
        """
        gate = self._gates.get(phase.lower())
        if gate is None:
            return []
        return gate.get_criteria()

    # ------------------------------------------------------------------
    # Gate management
    # ------------------------------------------------------------------

    def set_auto_approve(self, phase: str, auto_approve: bool = True) -> None:
        """Toggle auto-approve for a specific phase gate.

        Args:
            phase: Phase name.
            auto_approve: Whether to auto-approve.
        """
        gate = self._gates.get(phase.lower())
        if gate is not None:
            gate.auto_approve = auto_approve

    def set_all_auto_approve(self, auto_approve: bool = True) -> None:
        """Toggle auto-approve for all phase gates.

        Args:
            auto_approve: Whether to auto-approve.
        """
        for gate in self._gates.values():
            gate.auto_approve = auto_approve

    def add_gate(self, phase: str, gate: ApprovalGate) -> None:
        """Add or replace a gate for a phase.

        Args:
            phase: Phase name.
            gate: The ``ApprovalGate`` to register.
        """
        self._gates[phase.lower()] = gate

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_phases(self) -> list[str]:
        """List all phases that have configured gates.

        Returns:
            Sorted list of phase names.
        """
        return sorted(self._gates.keys())

    def get_summary(self, project_state: ProjectState) -> str:
        """Generate a human-readable summary of all gate evaluations.

        Args:
            project_state: Current project state.

        Returns:
            Formatted markdown summary.
        """
        lines = ["## Quality Gate Summary\n"]

        for phase in ("plan", "collect", "analyze", "write", "review"):
            gate = self._gates.get(phase)
            if gate is None:
                continue

            result = gate.evaluate(project_state)
            icon = "✅" if result.passed else "❌"
            lines.append(f"### {icon} {phase.upper()}")

            for criterion, passed in result.criteria_results.items():
                c_icon = "✅" if passed else "❌"
                lines.append(f"  {c_icon} {criterion}")

            lines.append("")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _build_default_gates() -> dict[str, ApprovalGate]:
        """Build default gates from ``_PHASE_GATE_CRITERIA``."""
        gates: dict[str, ApprovalGate] = {}
        for phase, criteria in _PHASE_GATE_CRITERIA.items():
            gates[phase] = ApprovalGate(
                gate_name=f"{phase}_gate",
                criteria=criteria,
                auto_approve=False,
            )
        return gates


# ---------------------------------------------------------------------------
# Human-in-the-loop approval workflow
# ---------------------------------------------------------------------------


class ApprovalRequest(BaseModel):
    """A request for human approval at a decision point."""

    gate_type: str = ""
    description: str = ""
    options: list[str] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: _now_iso())


class ApprovalResponse(BaseModel):
    """Human response to an approval request."""

    approved: bool = False
    selected_option: str | None = None
    feedback: str = ""
    timestamp: str = Field(default_factory=lambda: _now_iso())


def _now_iso() -> str:
    from datetime import datetime

    return datetime.now(UTC).isoformat()


# Gates that block progression vs advisory-only
_BLOCKING_GATES = {
    "methodology_selection",
    "variable_selection",
    "result_interpretation",
    "final_submission",
}
_ADVISORY_GATES = {
    "outlier_removal",
    "scope_changes",
}


class ApprovalGateManager:
    """Manages human-in-the-loop approval gates across the research workflow."""

    GATE_TYPES: set[str] = {
        "methodology_selection",
        "variable_selection",
        "outlier_removal",
        "result_interpretation",
        "scope_changes",
        "final_submission",
    }

    def __init__(self, gates_config: dict[str, bool] | None = None) -> None:
        self._config: dict[str, bool] = {}
        if gates_config is not None:
            self._config = dict(gates_config)
        else:
            self._config = {g: True for g in self.GATE_TYPES}
        self.log: list[tuple[ApprovalRequest, ApprovalResponse]] = []

    def is_gate_enabled(self, gate_type: str) -> bool:
        return self._config.get(gate_type, False)

    def request_approval(
        self,
        gate_type: str,
        description: str,
        options: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> ApprovalResponse:
        req = ApprovalRequest(
            gate_type=gate_type,
            description=description,
            options=options or [],
            context=context or {},
        )

        if not self.is_gate_enabled(gate_type):
            resp = ApprovalResponse(
                approved=True,
                feedback=f"Auto-approved (gate '{gate_type}' is disabled).",
            )
        else:
            resp = ApprovalResponse(
                approved=False,
                feedback=f"Awaiting human approval for: {description}",
            )

        self.log.append((req, resp))
        return resp

    def record_response(
        self,
        request_index: int,
        approved: bool,
        selected_option: str | None = None,
        feedback: str = "",
    ) -> ApprovalResponse:
        if request_index >= len(self.log):
            raise IndexError(f"No request at index {request_index}")

        req, _ = self.log[request_index]
        resp = ApprovalResponse(
            approved=approved,
            selected_option=selected_option,
            feedback=feedback,
        )
        self.log[request_index] = (req, resp)
        return resp

    def format_request(self, req: ApprovalRequest) -> str:
        gate_label = req.gate_type.replace("_", " ").title()
        blocking = req.gate_type in _BLOCKING_GATES
        level = "BLOCKING" if blocking else "ADVISORY"
        lines = [f"[{level}] {gate_label}", f"  {req.description}"]
        if req.options:
            lines.append("  Options: " + ", ".join(req.options))
        return "\n".join(lines)

    def get_pending_count(self) -> int:
        return sum(1 for _, resp in self.log if not resp.approved)
