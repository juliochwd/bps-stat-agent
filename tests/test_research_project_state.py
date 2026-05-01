"""Tests for research project state management."""

import tempfile
from pathlib import Path

import pytest

from mini_agent.research.project_state import (
    ProjectState,
    QuestionStatus,
    ResearchPhase,
    SectionStatus,
)


class TestProjectStateCreation:
    """Test creating new project states."""

    def test_create_new_minimal(self):
        """Create project with just a title."""
        state = ProjectState.create_new(title="Test Paper")
        assert state.project.title == "Test Paper"
        assert state.phase == ResearchPhase.PLAN
        assert len(state.project.id) == 8
        assert state.project.created != ""
        assert state.paper.template == "elsevier"

    def test_create_new_full(self):
        """Create project with all options."""
        state = ProjectState.create_new(
            title="Impact of Inflation on Poverty",
            template="ieee",
            target_journal="IEEE Transactions",
            research_questions=["Does X affect Y?", "How does Z moderate?"],
        )
        assert state.project.title == "Impact of Inflation on Poverty"
        assert state.paper.template == "ieee"
        assert state.project.target_journal == "IEEE Transactions"
        assert len(state.research_questions) == 2
        assert state.research_questions[0].id == "rq1"
        assert state.research_questions[1].id == "rq2"

    def test_create_new_has_default_sections(self):
        """New project has all IMRaD sections."""
        state = ProjectState.create_new(title="Test")
        sections = state.paper.sections
        assert "abstract" in sections
        assert "introduction" in sections
        assert "literature_review" in sections
        assert "methodology" in sections
        assert "results" in sections
        assert "discussion" in sections
        assert "conclusion" in sections
        for section in sections.values():
            assert section.status == SectionStatus.PENDING


class TestProjectStatePersistence:
    """Test saving and loading project state."""

    def test_save_and_load(self):
        """Save state to YAML and load it back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = ProjectState.create_new(
                title="Test Paper",
                template="springer",
                research_questions=["RQ1?"],
            )
            state.save(tmpdir)

            # Verify file exists
            assert (Path(tmpdir) / "project.yaml").exists()

            # Load and verify
            loaded = ProjectState.load(tmpdir)
            assert loaded.project.title == "Test Paper"
            assert loaded.paper.template == "springer"
            assert len(loaded.research_questions) == 1
            assert loaded.phase == ResearchPhase.PLAN

    def test_load_nonexistent_raises(self):
        """Loading from empty directory raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileNotFoundError):
                ProjectState.load(tmpdir)

    def test_save_updates_last_session(self):
        """Saving updates the last_session timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = ProjectState.create_new(title="Test")
            original_session = state.project.last_session
            state.save(tmpdir)
            assert state.project.last_session != original_session or original_session != ""


class TestPhaseTransition:
    """Test phase transitions."""

    def test_transition_records_history(self):
        """Phase transition records the old phase in history."""
        state = ProjectState.create_new(title="Test")
        assert state.phase == ResearchPhase.PLAN
        assert len(state.phase_history) == 0

        state.transition_phase(ResearchPhase.COLLECT)
        assert state.phase == ResearchPhase.COLLECT
        assert len(state.phase_history) == 1
        assert state.phase_history[0].phase == ResearchPhase.PLAN

    def test_multiple_transitions(self):
        """Multiple transitions build up history."""
        state = ProjectState.create_new(title="Test")
        state.transition_phase(ResearchPhase.COLLECT)
        state.transition_phase(ResearchPhase.ANALYZE)
        state.transition_phase(ResearchPhase.WRITE)

        assert state.phase == ResearchPhase.WRITE
        assert len(state.phase_history) == 3

    def test_transition_persists(self):
        """Phase transition survives save/load cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state = ProjectState.create_new(title="Test")
            state.transition_phase(ResearchPhase.COLLECT)
            state.save(tmpdir)

            loaded = ProjectState.load(tmpdir)
            assert loaded.phase == ResearchPhase.COLLECT
            assert len(loaded.phase_history) == 1


class TestResearchQuestions:
    """Test research question management."""

    def test_add_question(self):
        """Add a research question."""
        state = ProjectState.create_new(title="Test")
        rq = state.add_research_question("Does X affect Y?")
        assert rq.id == "rq1"
        assert rq.question == "Does X affect Y?"
        assert rq.status == QuestionStatus.PENDING

    def test_add_multiple_questions(self):
        """Add multiple questions with auto-incrementing IDs."""
        state = ProjectState.create_new(title="Test")
        state.add_research_question("Q1?")
        state.add_research_question("Q2?")
        state.add_research_question("Q3?")
        assert len(state.research_questions) == 3
        assert state.research_questions[2].id == "rq3"


class TestDataInventory:
    """Test data source management."""

    def test_add_data_source(self):
        """Add a data source."""
        state = ProjectState.create_new(title="Test")
        ds = state.add_data_source(
            source="bps",
            dataset="gini_ratio",
            years=[2020, 2021, 2022],
            path="data/raw/gini.csv",
        )
        assert ds.source == "bps"
        assert ds.dataset == "gini_ratio"
        assert len(ds.years) == 3
        assert len(state.data_inventory) == 1


class TestProgressSummary:
    """Test progress summary generation."""

    def test_summary_contains_title(self):
        """Summary includes project title."""
        state = ProjectState.create_new(title="My Research Paper")
        summary = state.get_progress_summary()
        assert "My Research Paper" in summary

    def test_summary_contains_phase(self):
        """Summary includes current phase."""
        state = ProjectState.create_new(title="Test")
        summary = state.get_progress_summary()
        assert "PLAN" in summary

    def test_summary_contains_questions(self):
        """Summary includes research questions."""
        state = ProjectState.create_new(
            title="Test",
            research_questions=["Does X affect Y?"],
        )
        summary = state.get_progress_summary()
        assert "Does X affect Y?" in summary
