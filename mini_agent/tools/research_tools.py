"""Research-specific tools for the Academic Research Agent.

Provides tools for:
- project_init: Initialize a new research project
- project_status: Show current project status
- switch_phase: Transition between research phases
"""

from __future__ import annotations

from typing import Any

from .base import Tool, ToolResult


class ProjectInitTool(Tool):
    """Initialize a new research project with workspace structure."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "project_init"

    @property
    def description(self) -> str:
        return (
            "Initialize a new academic research project. Creates workspace structure "
            "(data/, literature/, analysis/, writing/, review/) and project.yaml state file. "
            "Use this at the start of a new research project."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Research paper title",
                },
                "template": {
                    "type": "string",
                    "enum": ["ieee", "elsevier", "springer", "springer_lncs", "mdpi", "apa7"],
                    "description": "Journal template to use (default: elsevier)",
                },
                "target_journal": {
                    "type": "string",
                    "description": "Target journal name (e.g., 'Bulletin of Indonesian Economic Studies')",
                },
                "research_questions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Initial research questions",
                },
            },
            "required": ["title"],
        }

    async def execute(
        self,
        title: str,
        template: str = "elsevier",
        target_journal: str = "",
        research_questions: list[str] | None = None,
    ) -> ToolResult:
        try:
            from ..research.project_state import ProjectState
            from ..research.workspace import WorkspaceScaffolder

            # Create project state
            state = ProjectState.create_new(
                title=title,
                template=template,
                target_journal=target_journal,
                research_questions=research_questions,
            )

            # Scaffold workspace
            scaffolder = WorkspaceScaffolder(self._workspace_dir)
            workspace_path = scaffolder.scaffold(state)

            # Verify
            verification = scaffolder.verify()
            all_ok = all(verification.values())

            summary = (
                f"Research project initialized successfully!\n\n"
                f"**Title:** {title}\n"
                f"**Template:** {template}\n"
                f"**Journal:** {target_journal or '(not specified)'}\n"
                f"**Workspace:** {workspace_path.absolute()}\n"
                f"**Phase:** PLAN\n"
            )

            if research_questions:
                summary += f"**Research Questions:** {len(research_questions)}\n"
                for i, q in enumerate(research_questions, 1):
                    summary += f"  RQ{i}: {q}\n"

            summary += f"\n**Workspace verified:** {'✅ All OK' if all_ok else '⚠️ Some issues'}"

            return ToolResult(success=True, content=summary)

        except Exception as e:
            return ToolResult(success=False, error=f"Failed to initialize project: {e}")


class ProjectStatusTool(Tool):
    """Show current research project status."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "project_status"

    @property
    def description(self) -> str:
        return (
            "Show the current research project status including: current phase, "
            "research questions, data inventory, literature count, paper progress, "
            "and quality gate results."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "verbose": {
                    "type": "boolean",
                    "description": "Include detailed breakdown (default: false)",
                },
            },
            "required": [],
        }

    async def execute(self, verbose: bool = False) -> ToolResult:
        try:
            from ..research.project_state import ProjectState
            from ..research.workspace import WorkspaceScaffolder

            state = ProjectState.load(self._workspace_dir)
            summary = state.get_progress_summary()

            if verbose:
                scaffolder = WorkspaceScaffolder(self._workspace_dir)
                summary += "\n\n" + scaffolder.get_workspace_summary()

            return ToolResult(success=True, content=summary)

        except FileNotFoundError:
            return ToolResult(
                success=False,
                error="No active research project. Use `project_init` to create one.",
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to get project status: {e}")


class SwitchPhaseTool(Tool):
    """Switch to a different research phase."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "switch_phase"

    @property
    def description(self) -> str:
        return (
            "Switch to a different research phase. Saves current state and loads "
            "phase-appropriate tools. Phases: plan, collect, analyze, write, review."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_phase": {
                    "type": "string",
                    "enum": ["plan", "collect", "analyze", "write", "review"],
                    "description": "Phase to switch to",
                },
                "reason": {
                    "type": "string",
                    "description": "Reason for phase transition",
                },
            },
            "required": ["target_phase"],
        }

    async def execute(self, target_phase: str, reason: str = "") -> ToolResult:
        try:
            from ..research.project_state import ProjectState, ResearchPhase

            state = ProjectState.load(self._workspace_dir)
            old_phase = state.phase

            new_phase = ResearchPhase(target_phase)
            if new_phase == old_phase:
                return ToolResult(
                    success=True,
                    content=f"Already in phase {target_phase.upper()}",
                )

            state.transition_phase(new_phase)
            state.save(self._workspace_dir)

            msg = f"Phase transition: {old_phase.value.upper()} → {new_phase.value.upper()}\n"
            if reason:
                msg += f"Reason: {reason}\n"

            msg += (
                f"\nNote: Tool availability has changed for the {new_phase.value.upper()} phase. "
                f"Use `project_status` to see current state."
            )

            return ToolResult(success=True, content=msg)

        except FileNotFoundError:
            return ToolResult(
                success=False,
                error="No active research project. Use `project_init` first.",
            )
        except ValueError as e:
            return ToolResult(success=False, error=f"Invalid phase: {e}")
        except Exception as e:
            return ToolResult(success=False, error=f"Phase transition failed: {e}")
