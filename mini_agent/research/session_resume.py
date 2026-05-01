"""Cross-session continuity for research projects.

Provides checkpoint creation, persistence, and context generation so the
LLM can seamlessly resume work from any prior session state.  Checkpoints
are stored as YAML files in the ``.sessions/`` directory within the
project workspace.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from .project_state import ProjectState


class SessionCheckpoint(BaseModel):
    """Snapshot of project state at a point in time.

    Attributes:
        timestamp: ISO 8601 timestamp of checkpoint creation.
        phase: Research phase at checkpoint time.
        messages_summary: Human-readable summary of session progress.
        key_decisions: Important decisions made during the session.
        pending_tasks: Tasks remaining to be completed.
        artifacts: Mapping of artifact names to workspace-relative paths.
    """

    timestamp: str = ""
    phase: str = ""
    messages_summary: str = ""
    key_decisions: list[str] = Field(default_factory=list)
    pending_tasks: list[str] = Field(default_factory=list)
    artifacts: dict[str, str] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


class SessionResumeManager:
    """Manages cross-session continuity for research projects.

    Creates, saves, and loads checkpoints so the LLM can pick up
    exactly where a previous session left off.  Checkpoints are stored
    as YAML files in ``<workspace>/.sessions/``.
    """

    SESSIONS_DIR: str = ".sessions"

    def __init__(self, workspace_path: Path) -> None:
        """Initialise the session resume manager.

        Args:
            workspace_path: Root path of the research workspace.
        """
        self.workspace_path = Path(workspace_path)
        self._sessions_dir = self.workspace_path / self.SESSIONS_DIR
        self._sessions_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Checkpoint creation
    # ------------------------------------------------------------------

    def create_checkpoint(
        self,
        phase: str,
        messages_summary: str,
        key_decisions: list[str] | None = None,
        pending_tasks: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create and persist a checkpoint for the current session.

        Args:
            phase: Current research phase name (e.g. ``"plan"``).
            messages_summary: Human-readable summary of what happened.
            key_decisions: Important decisions made during the session.
            pending_tasks: Tasks remaining to be completed.

        Returns:
            The checkpoint data as a plain dict.
        """
        checkpoint = SessionCheckpoint(
            phase=phase,
            messages_summary=messages_summary,
            key_decisions=key_decisions or [],
            pending_tasks=pending_tasks or [],
        )

        # Persist to YAML
        self._save_checkpoint(checkpoint)

        return checkpoint.model_dump(mode="json")

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_latest_checkpoint(self) -> dict[str, Any] | None:
        """Load the most recent checkpoint from the workspace.

        Returns:
            The latest checkpoint as a dict, or ``None`` if no
            checkpoint exists.
        """
        latest_file = self._sessions_dir / "latest.yaml"
        if not latest_file.exists():
            return None

        with open(latest_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return data if data else None

    def list_checkpoints(self) -> list[dict[str, Any]]:
        """List all checkpoints ordered by timestamp (oldest first).

        Returns:
            List of checkpoint dicts.
        """
        checkpoints: list[dict[str, Any]] = []

        if not self._sessions_dir.exists():
            return checkpoints

        for path in sorted(self._sessions_dir.glob("checkpoint_*.yaml")):
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data:
                checkpoints.append(data)

        return checkpoints

    # ------------------------------------------------------------------
    # Context generation
    # ------------------------------------------------------------------

    def get_resume_context(self) -> str:
        """Generate a formatted resume context for system-prompt injection.

        Reads the latest checkpoint and produces a structured summary
        that the LLM can use to understand where the previous session
        left off.

        Returns:
            Formatted context string, or an empty string if no
            checkpoint exists.
        """
        checkpoint = self.get_latest_checkpoint()
        if checkpoint is None:
            return ""

        lines = [
            "## Session Resume — Research Project Context\n",
            f"**Phase:** {str(checkpoint.get('phase', 'unknown')).upper()}",
            f"**Checkpoint:** {checkpoint.get('timestamp', 'N/A')}",
            "",
        ]

        summary = checkpoint.get("messages_summary", "")
        if summary:
            lines.append("### Progress Summary")
            lines.append(summary)
            lines.append("")

        decisions = checkpoint.get("key_decisions", [])
        if decisions:
            lines.append("### Key Decisions")
            for decision in decisions:
                lines.append(f"  - {decision}")
            lines.append("")

        pending = checkpoint.get("pending_tasks", [])
        if pending:
            lines.append("### Pending Tasks")
            for task in pending:
                lines.append(f"  - {task}")
            lines.append("")

        artifacts = checkpoint.get("artifacts", {})
        if artifacts:
            lines.append("### Available Artifacts")
            for name, path in sorted(artifacts.items()):
                lines.append(f"  - **{name}**: `{path}`")
            lines.append("")

        lines.append(
            "Resume work from the current phase. Review pending tasks and continue where the previous session stopped."
        )

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def cleanup_old_checkpoints(self, keep_last: int = 5) -> int:
        """Remove old checkpoint files, keeping the most recent ones.

        Args:
            keep_last: Number of most-recent checkpoints to retain.

        Returns:
            Number of checkpoint files removed.
        """
        checkpoint_files = sorted(self._sessions_dir.glob("checkpoint_*.yaml"))

        if len(checkpoint_files) <= keep_last:
            return 0

        to_remove = checkpoint_files[:-keep_last]
        for path in to_remove:
            path.unlink(missing_ok=True)

        return len(to_remove)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def create_from_project_state(
        self,
        project_state: ProjectState,
        context: str = "",
    ) -> dict[str, Any]:
        """Create a checkpoint directly from a ProjectState instance.

        Automatically derives pending tasks from the project state
        (unanswered research questions, incomplete sections, etc.).

        Args:
            project_state: Current project state to snapshot.
            context: Optional additional context string.

        Returns:
            The checkpoint data as a plain dict.
        """
        pending_tasks: list[str] = []

        # Unanswered research questions
        for rq in project_state.research_questions:
            if rq.status != "answered":
                pending_tasks.append(f"Answer {rq.id}: {rq.question}")

        # Incomplete paper sections
        for name, section in project_state.paper.sections.items():
            if section.status in ("pending", "in_progress"):
                pending_tasks.append(f"Write section: {name}")

        # Quality gates not yet run
        if project_state.quality.statistical_validity == "not_run":
            pending_tasks.append("Run statistical validity check")
        if project_state.quality.citation_verification == "not_run":
            pending_tasks.append("Verify citations")

        summary = context or project_state.get_progress_summary()

        return self.create_checkpoint(
            phase=project_state.phase.value,
            messages_summary=summary,
            key_decisions=[],
            pending_tasks=pending_tasks,
        )

    def has_active_project(self) -> bool:
        """Check if there's an active project in the workspace.

        Returns:
            ``True`` if a ``project.yaml`` exists in the workspace.
        """
        return (self.workspace_path / "project.yaml").exists()

    # ------------------------------------------------------------------
    # Internal persistence
    # ------------------------------------------------------------------

    def _save_checkpoint(self, checkpoint: SessionCheckpoint) -> Path:
        """Persist a checkpoint to the .sessions/ directory.

        Args:
            checkpoint: The checkpoint to save.

        Returns:
            Path to the saved checkpoint file.
        """
        self._sessions_dir.mkdir(parents=True, exist_ok=True)

        data = checkpoint.model_dump(mode="json")

        # Timestamp-based filename for ordering
        ts = checkpoint.timestamp.replace(":", "-").replace("+", "_")
        checkpoint_file = self._sessions_dir / f"checkpoint_{ts}.yaml"

        with open(checkpoint_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Also write a "latest" file for quick access
        latest_file = self._sessions_dir / "latest.yaml"
        with open(latest_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return checkpoint_file
