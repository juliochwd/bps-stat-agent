"""Phase-gated tool loading for research workflow.

Manages which tools are visible to the LLM at each research phase.
Maximum 15 tools per phase to prevent LLM confusion.
Core tools (read_file, write_file, project_status) are always available.
"""

from __future__ import annotations

from .project_state import ResearchPhase

# Tool names available in each phase
# Core tools are ALWAYS loaded regardless of phase
CORE_TOOLS = frozenset(
    {
        "read_file",
        "write_file",
        "edit_file",
        "bash",
        "project_status",
        "switch_phase",
        "record_note",
        "recall_notes",
    }
)

PHASE_TOOLS: dict[ResearchPhase, list[str]] = {
    ResearchPhase.PLAN: [
        "project_init",
        "literature_search",
        "convert_document",
        "get_skill",
    ],
    ResearchPhase.COLLECT: [
        "literature_search",
        "citation_manager",
        "verify_citations",
        "convert_document",
        "parse_academic_pdf",
        "extract_references",
        "chunk_document",
        "embed_papers",
        "build_knowledge_graph",
        "get_skill",
        # BPS tools loaded via MCP (separate)
    ],
    ResearchPhase.ANALYZE: [
        "python_repl",
        "descriptive_stats",
        "regression_analysis",
        "time_series_analysis",
        "hypothesis_test",
        "bayesian_analysis",
        "causal_inference",
        "survival_analysis",
        "nonparametric_test",
        "create_visualization",
        "auto_visualize",
        "automated_eda",
        "validate_data",
        "conversational_analysis",
        "get_skill",
    ],
    ResearchPhase.WRITE: [
        "write_section",
        "compile_paper",
        "generate_table",
        "generate_diagram",
        "convert_figure_tikz",
        "check_grammar",
        "check_style",
        "check_readability",
        "citation_manager",
        "create_visualization",
        "get_skill",
    ],
    ResearchPhase.REVIEW: [
        "check_statistical_validity",
        "verify_citations",
        "simulate_peer_review",
        "detect_plagiarism",
        "audit_reproducibility",
        "quality_gate_runner",
        "check_grammar",
        "check_style",
        "get_skill",
    ],
}


class PhaseManager:
    """Manages tool loading per research phase.

    Ensures the LLM sees only relevant tools for the current phase,
    preventing confusion from too many options.
    """

    def __init__(self) -> None:
        self._current_phase: ResearchPhase = ResearchPhase.PLAN

    @property
    def current_phase(self) -> ResearchPhase:
        """Get the current research phase."""
        return self._current_phase

    @current_phase.setter
    def current_phase(self, phase: ResearchPhase) -> None:
        """Set the current research phase."""
        self._current_phase = phase

    def get_tool_names_for_phase(self, phase: ResearchPhase | None = None) -> list[str]:
        """Get the list of tool names that should be active for a phase.

        Args:
            phase: The phase to get tools for (defaults to current phase)

        Returns:
            List of tool names (core + phase-specific)
        """
        target_phase = phase or self._current_phase
        phase_specific = PHASE_TOOLS.get(target_phase, [])
        # Combine core + phase-specific, deduplicate while preserving order
        all_tools = list(CORE_TOOLS) + [t for t in phase_specific if t not in CORE_TOOLS]
        return all_tools

    def filter_tools(self, all_tools: list, phase: ResearchPhase | None = None) -> list:
        """Filter a list of Tool objects to only those active in the current phase.

        Args:
            all_tools: Complete list of available Tool objects
            phase: The phase to filter for (defaults to current phase)

        Returns:
            Filtered list of Tool objects for the phase
        """
        allowed_names = set(self.get_tool_names_for_phase(phase))
        return [tool for tool in all_tools if tool.name in allowed_names]

    def get_phase_description(self, phase: ResearchPhase | None = None) -> str:
        """Get a human-readable description of a phase.

        Args:
            phase: The phase to describe (defaults to current phase)

        Returns:
            Phase description string
        """
        target_phase = phase or self._current_phase
        descriptions = {
            ResearchPhase.PLAN: "PLAN — Define research scope, questions, methodology, and paper structure",
            ResearchPhase.COLLECT: "COLLECT — Gather data from BPS/APIs and literature from academic databases",
            ResearchPhase.ANALYZE: "ANALYZE — Run statistical analysis, generate visualizations and results",
            ResearchPhase.WRITE: "WRITE — Generate paper sections (LaTeX/DOCX) with citations and figures",
            ResearchPhase.REVIEW: "REVIEW — Quality gate: verify citations, check statistics, simulate peer review",
        }
        return descriptions.get(target_phase, f"Unknown phase: {target_phase}")

    def get_next_phase(self, phase: ResearchPhase | None = None) -> ResearchPhase | None:
        """Get the next phase in the workflow.

        Args:
            phase: Current phase (defaults to current phase)

        Returns:
            Next phase, or None if at the last phase
        """
        target_phase = phase or self._current_phase
        phase_order = list(ResearchPhase)
        current_idx = phase_order.index(target_phase)
        if current_idx < len(phase_order) - 1:
            return phase_order[current_idx + 1]
        return None

    def can_transition_to(self, target_phase: ResearchPhase) -> bool:
        """Check if transition to target phase is allowed.

        Transitions are allowed forward or backward (for revisions).

        Args:
            target_phase: The phase to transition to

        Returns:
            True if transition is allowed
        """
        # All transitions are allowed (forward for progress, backward for revisions)
        return target_phase != self._current_phase
