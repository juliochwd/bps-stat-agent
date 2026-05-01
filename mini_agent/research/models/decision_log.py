"""Append-only decision log for research audit trail.

Records every significant research decision (methodology choices,
variable selections, statistical tests, etc.) for full reproducibility.
The log is append-only — entries are never modified or deleted.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

# Valid decision types for research audit trail
DECISION_TYPES: list[str] = [
    "methodology",
    "data_source",
    "statistical_test",
    "variable_selection",
    "model_specification",
    "writing_style",
    "citation_choice",
    "outlier_removal",
    "scope_change",
    "interpretation",
    "phase_transition",
]


class DecisionEntry(BaseModel):
    """A single research decision record.

    Attributes:
        timestamp: ISO 8601 timestamp of when the decision was made.
        phase: Research phase during which the decision occurred.
        decision_type: Category of decision (see ``DECISION_TYPES``).
        description: Human-readable description of the decision.
        rationale: Justification for the decision.
        alternatives_considered: Other options that were evaluated.
        outcome: Result or impact of the decision (filled in later).
    """

    timestamp: str = ""
    phase: str = ""
    decision_type: str = ""
    description: str = ""
    rationale: str = ""
    alternatives_considered: list[str] = Field(default_factory=list)
    outcome: str = ""

    def model_post_init(self, __context: Any) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


class DecisionLog:
    """Append-only log of research decisions for reproducibility.

    Stores entries in-memory and supports persistence via JSON-lines
    files.  Provides filtering by phase and decision type.

    Args:
        workspace_path: Path to the workspace directory.  The log file
            is stored at ``<workspace>/logs/decisions.jsonl``.
    """

    DEFAULT_FILENAME: str = "logs/decisions.jsonl"

    def __init__(self, workspace_path: Path) -> None:
        self.workspace_path = Path(workspace_path)
        self._log_path = self.workspace_path / self.DEFAULT_FILENAME
        self._entries: list[DecisionEntry] = []

        # Load existing entries if the file exists
        if self._log_path.exists():
            self._load()

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def log_decision(
        self,
        phase: str,
        decision_type: str,
        description: str,
        rationale: str = "",
        alternatives: list[str] | None = None,
    ) -> DecisionEntry:
        """Append a new decision entry to the log.

        Args:
            phase: Current research phase name.
            decision_type: Category of decision (e.g. ``"methodology"``).
            description: What was decided.
            rationale: Why this decision was made.
            alternatives: Other options that were considered.

        Returns:
            The newly created ``DecisionEntry``.
        """
        entry = DecisionEntry(
            phase=phase,
            decision_type=decision_type,
            description=description,
            rationale=rationale,
            alternatives_considered=alternatives or [],
        )
        self._entries.append(entry)
        return entry

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    def get_decisions(
        self,
        phase: str | None = None,
        decision_type: str | None = None,
    ) -> list[DecisionEntry]:
        """Retrieve decisions with optional filtering.

        Args:
            phase: Filter by research phase (e.g. ``"plan"``).
            decision_type: Filter by decision type (e.g. ``"methodology"``).

        Returns:
            List of matching ``DecisionEntry`` instances.
        """
        results = list(self._entries)

        if phase is not None:
            results = [e for e in results if e.phase == phase]

        if decision_type is not None:
            results = [e for e in results if e.decision_type == decision_type]

        return results

    def get_summary(self) -> str:
        """Generate a human-readable summary of all decisions.

        Returns:
            Formatted markdown summary.
        """
        if not self._entries:
            return "No decisions recorded yet."

        lines = [f"## Decision Log ({len(self._entries)} entries)\n"]

        for entry in self._entries:
            lines.append(f"- [{entry.timestamp[:10]}] **{entry.decision_type}**: {entry.description}")
            if entry.rationale:
                lines.append(f"  Rationale: {entry.rationale}")
            if entry.alternatives_considered:
                alts = ", ".join(entry.alternatives_considered)
                lines.append(f"  Alternatives considered: {alts}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Persist the decision log to a JSON-lines file.

        Each entry is written as a single JSON line for append-friendly
        I/O.  The parent directory is created if it does not exist.
        """
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._log_path, "w", encoding="utf-8") as f:
            for entry in self._entries:
                f.write(entry.model_dump_json() + "\n")

    def load(self) -> None:
        """Reload the decision log from disk.

        Replaces the in-memory entries with those read from the file.
        If the file does not exist, the entries list is cleared.
        """
        self._load()

    def _load(self) -> None:
        """Internal load implementation."""
        if not self._log_path.exists():
            self._entries = []
            return

        entries: list[DecisionEntry] = []
        text = self._log_path.read_text(encoding="utf-8").strip()
        if text:
            for line in text.split("\n"):
                line = line.strip()
                if line:
                    entries.append(DecisionEntry.model_validate_json(line))

        self._entries = entries

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def entries(self) -> list[DecisionEntry]:
        """Read-only access to the entries list."""
        return list(self._entries)

    @property
    def count(self) -> int:
        """Number of entries in the log."""
        return len(self._entries)
