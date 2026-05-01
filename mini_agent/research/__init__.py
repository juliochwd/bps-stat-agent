"""BPS Academic Research Agent — Research Engine Package.

This package extends the BPS Stat Agent with academic research capabilities:
- Project state management (multi-session persistence)
- Phase-gated tool loading (PLAN → COLLECT → ANALYZE → WRITE → REVIEW)
- Research orchestration with sub-agent delegation
- Workspace scaffolding for research projects
- LLM gateway with multi-model routing
- DSPy pipeline for optimizable research workflows
- Sub-agent system for specialized tasks
- Session resume for cross-session continuity
- Approval gates for human-in-the-loop decisions
- Quality gates for automated verification
"""

from .constants import RESEARCH_VERSION
from .exceptions import ResearchError
from .phase_manager import PhaseManager, ResearchPhase
from .project_state import ProjectState
from .workspace import WorkspaceScaffolder

__all__ = [
    "PhaseManager",
    "ProjectState",
    "ResearchError",
    "ResearchPhase",
    "RESEARCH_VERSION",
    "WorkspaceScaffolder",
]
