"""Project state management for academic research projects.

Provides persistent state across sessions via YAML serialization.
Each research project has a project.yaml that tracks:
- Current phase and phase history
- Research questions and their status
- Data inventory (sources, paths, hashes)
- Literature state (papers found, bibliography)
- Paper writing progress (sections, word counts)
- Quality gate results
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ResearchPhase(str, Enum):
    """Research workflow phases."""

    PLAN = "plan"
    COLLECT = "collect"
    ANALYZE = "analyze"
    WRITE = "write"
    REVIEW = "review"


class SectionStatus(str, Enum):
    """Paper section writing status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DRAFT_V1 = "draft_v1"
    DRAFT_V2 = "draft_v2"
    FINAL = "final"


class QuestionStatus(str, Enum):
    """Research question status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ANSWERED = "answered"


class ResearchQuestion(BaseModel):
    """A research question with tracking."""

    id: str
    question: str
    status: QuestionStatus = QuestionStatus.PENDING
    findings_ref: str | None = None


class DataSource(BaseModel):
    """A data source in the project inventory."""

    source: str  # e.g., "bps", "world_bank"
    dataset: str  # e.g., "gini_ratio_province"
    description: str = ""
    years: list[int] = Field(default_factory=list)
    path: str | None = None  # Relative path in workspace
    sha256: str | None = None  # Hash for reproducibility


class LiteratureState(BaseModel):
    """Literature collection state."""

    total_papers: int = 0
    key_papers: int = 0
    bib_file: str = "literature/references.bib"
    verified: bool = False  # All citations verified?


class SectionState(BaseModel):
    """State of a paper section."""

    status: SectionStatus = SectionStatus.PENDING
    path: str = ""
    word_count: int = 0
    last_modified: str | None = None


class PaperState(BaseModel):
    """Paper writing state."""

    template: str = "elsevier"
    target_journal: str = ""
    outline_file: str = "writing/outline.yaml"
    sections: dict[str, SectionState] = Field(
        default_factory=lambda: {
            "abstract": SectionState(path="writing/sections/00_abstract.tex"),
            "introduction": SectionState(path="writing/sections/01_introduction.tex"),
            "literature_review": SectionState(path="writing/sections/02_literature.tex"),
            "methodology": SectionState(path="writing/sections/03_methodology.tex"),
            "results": SectionState(path="writing/sections/04_results.tex"),
            "discussion": SectionState(path="writing/sections/05_discussion.tex"),
            "conclusion": SectionState(path="writing/sections/06_conclusion.tex"),
        }
    )


class QualityState(BaseModel):
    """Quality gate results."""

    last_run: str | None = None
    statistical_validity: str = "not_run"
    citation_verification: str = "not_run"
    style_compliance: str = "not_run"
    peer_review: str = "not_run"


class PhaseHistoryEntry(BaseModel):
    """Record of a phase completion."""

    phase: ResearchPhase
    completed: str  # ISO datetime
    checkpoint: str | None = None


class ProjectMetadata(BaseModel):
    """Project metadata."""

    id: str = ""
    title: str = ""
    created: str = ""
    last_session: str = ""
    target_journal: str = ""
    template: str = "elsevier"


class ProjectState(BaseModel):
    """Complete research project state.

    Persisted as project.yaml in the workspace root.
    Supports load/save for cross-session continuity.
    """

    project: ProjectMetadata = Field(default_factory=ProjectMetadata)
    phase: ResearchPhase = ResearchPhase.PLAN
    phase_history: list[PhaseHistoryEntry] = Field(default_factory=list)
    research_questions: list[ResearchQuestion] = Field(default_factory=list)
    data_inventory: list[DataSource] = Field(default_factory=list)
    literature: LiteratureState = Field(default_factory=LiteratureState)
    paper: PaperState = Field(default_factory=PaperState)
    quality: QualityState = Field(default_factory=QualityState)

    @classmethod
    def create_new(
        cls,
        title: str,
        template: str = "elsevier",
        target_journal: str = "",
        research_questions: list[str] | None = None,
    ) -> ProjectState:
        """Create a new research project state.

        Args:
            title: Research paper title
            template: Journal template (ieee, elsevier, springer, mdpi, apa7)
            target_journal: Target journal name
            research_questions: Initial research questions

        Returns:
            New ProjectState instance
        """
        import uuid

        now = datetime.now(UTC).isoformat()
        project_id = str(uuid.uuid4())[:8]

        questions = []
        if research_questions:
            for i, q in enumerate(research_questions, 1):
                questions.append(ResearchQuestion(id=f"rq{i}", question=q))

        return cls(
            project=ProjectMetadata(
                id=project_id,
                title=title,
                created=now,
                last_session=now,
                target_journal=target_journal,
                template=template,
            ),
            phase=ResearchPhase.PLAN,
            research_questions=questions,
            paper=PaperState(template=template, target_journal=target_journal),
        )

    @classmethod
    def load(cls, workspace_path: str | Path) -> ProjectState:
        """Load project state from workspace.

        Args:
            workspace_path: Path to workspace directory

        Returns:
            Loaded ProjectState

        Raises:
            FileNotFoundError: If project.yaml doesn't exist
        """
        project_file = Path(workspace_path) / "project.yaml"
        if not project_file.exists():
            raise FileNotFoundError(f"No project.yaml found in {workspace_path}")

        with open(project_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not data:
            raise ValueError("project.yaml is empty")

        return cls.model_validate(data)

    def save(self, workspace_path: str | Path) -> Path:
        """Save project state to workspace.

        Args:
            workspace_path: Path to workspace directory

        Returns:
            Path to saved project.yaml
        """
        # Update last_session timestamp
        self.project.last_session = datetime.now(UTC).isoformat()

        project_file = Path(workspace_path) / "project.yaml"
        project_file.parent.mkdir(parents=True, exist_ok=True)

        data = self.model_dump(mode="json")

        with open(project_file, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return project_file

    def transition_phase(self, new_phase: ResearchPhase) -> None:
        """Transition to a new research phase.

        Records the current phase in history before transitioning.

        Args:
            new_phase: The phase to transition to
        """
        # Record current phase completion
        now = datetime.now(UTC).isoformat()
        self.phase_history.append(
            PhaseHistoryEntry(
                phase=self.phase,
                completed=now,
            )
        )
        self.phase = new_phase

    def add_research_question(self, question: str) -> ResearchQuestion:
        """Add a new research question.

        Args:
            question: The research question text

        Returns:
            The created ResearchQuestion
        """
        next_id = f"rq{len(self.research_questions) + 1}"
        rq = ResearchQuestion(id=next_id, question=question)
        self.research_questions.append(rq)
        return rq

    def add_data_source(self, source: str, dataset: str, **kwargs: Any) -> DataSource:
        """Add a data source to the inventory.

        Args:
            source: Data source name (e.g., "bps")
            dataset: Dataset identifier
            **kwargs: Additional DataSource fields

        Returns:
            The created DataSource
        """
        ds = DataSource(source=source, dataset=dataset, **kwargs)
        self.data_inventory.append(ds)
        return ds

    def get_progress_summary(self) -> str:
        """Generate a human-readable progress summary.

        Returns:
            Formatted progress string
        """
        lines = [
            f"## Project: {self.project.title}",
            f"**Phase:** {self.phase.value.upper()}",
            f"**Created:** {self.project.created}",
            f"**Last Session:** {self.project.last_session}",
            "",
            "### Research Questions:",
        ]

        for rq in self.research_questions:
            status_icon = {"pending": "⏳", "in_progress": "🔄", "answered": "✅"}
            lines.append(f"  {status_icon.get(rq.status, '?')} {rq.id}: {rq.question}")

        lines.extend(
            [
                "",
                f"### Data: {len(self.data_inventory)} sources",
                f"### Literature: {self.literature.total_papers} papers ({self.literature.key_papers} key)",
                f"### Paper: {self.project.target_journal} ({self.paper.template})",
            ]
        )

        # Section progress
        for name, section in self.paper.sections.items():
            status_icon = {"pending": "⬜", "in_progress": "🟡", "draft_v1": "🟠", "draft_v2": "🟢", "final": "✅"}
            lines.append(
                f"  {status_icon.get(section.status, '?')} {name}: {section.status} ({section.word_count} words)"
            )

        return "\n".join(lines)
