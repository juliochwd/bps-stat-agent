"""Tests for mini_agent/research/phase_manager.py — Phase-gated tool loading."""

import pytest

from mini_agent.research.phase_manager import (
    CORE_TOOLS,
    PHASE_TOOLS,
    PhaseManager,
)
from mini_agent.research.project_state import ResearchPhase


class TestPhaseManager:
    """Tests for PhaseManager."""

    def setup_method(self):
        self.pm = PhaseManager()

    def test_initial_phase(self):
        assert self.pm.current_phase == ResearchPhase.PLAN

    def test_set_phase(self):
        self.pm.current_phase = ResearchPhase.ANALYZE
        assert self.pm.current_phase == ResearchPhase.ANALYZE

    def test_get_tool_names_for_phase_plan(self):
        tools = self.pm.get_tool_names_for_phase(ResearchPhase.PLAN)
        # Should include core tools
        for core in CORE_TOOLS:
            assert core in tools
        # Should include plan-specific tools
        assert "project_init" in tools

    def test_get_tool_names_for_phase_collect(self):
        tools = self.pm.get_tool_names_for_phase(ResearchPhase.COLLECT)
        assert "literature_search" in tools
        assert "citation_manager" in tools

    def test_get_tool_names_for_phase_analyze(self):
        tools = self.pm.get_tool_names_for_phase(ResearchPhase.ANALYZE)
        assert "python_repl" in tools
        assert "regression_analysis" in tools

    def test_get_tool_names_for_phase_write(self):
        tools = self.pm.get_tool_names_for_phase(ResearchPhase.WRITE)
        assert "write_section" in tools
        assert "compile_paper" in tools

    def test_get_tool_names_for_phase_review(self):
        tools = self.pm.get_tool_names_for_phase(ResearchPhase.REVIEW)
        assert "verify_citations" in tools
        assert "simulate_peer_review" in tools

    def test_get_tool_names_defaults_to_current(self):
        self.pm.current_phase = ResearchPhase.WRITE
        tools = self.pm.get_tool_names_for_phase()
        assert "write_section" in tools

    def test_no_duplicates(self):
        tools = self.pm.get_tool_names_for_phase(ResearchPhase.COLLECT)
        assert len(tools) == len(set(tools))

    def test_filter_tools(self):
        """Test filtering tool objects by phase."""
        from unittest.mock import MagicMock

        mock_tools = []
        for name in ["read_file", "write_file", "python_repl", "unknown_tool"]:
            t = MagicMock()
            t.name = name
            mock_tools.append(t)

        # PLAN phase should not include python_repl
        filtered = self.pm.filter_tools(mock_tools, ResearchPhase.PLAN)
        names = [t.name for t in filtered]
        assert "read_file" in names
        assert "write_file" in names
        assert "python_repl" not in names
        assert "unknown_tool" not in names

    def test_get_phase_description_plan(self):
        desc = self.pm.get_phase_description(ResearchPhase.PLAN)
        assert "PLAN" in desc

    def test_get_phase_description_all_phases(self):
        for phase in ResearchPhase:
            desc = self.pm.get_phase_description(phase)
            assert desc  # Not empty

    def test_get_phase_description_defaults_to_current(self):
        self.pm.current_phase = ResearchPhase.REVIEW
        desc = self.pm.get_phase_description()
        assert "REVIEW" in desc

    def test_get_next_phase(self):
        assert self.pm.get_next_phase(ResearchPhase.PLAN) == ResearchPhase.COLLECT
        assert self.pm.get_next_phase(ResearchPhase.COLLECT) == ResearchPhase.ANALYZE
        assert self.pm.get_next_phase(ResearchPhase.ANALYZE) == ResearchPhase.WRITE
        assert self.pm.get_next_phase(ResearchPhase.WRITE) == ResearchPhase.REVIEW
        assert self.pm.get_next_phase(ResearchPhase.REVIEW) is None

    def test_get_next_phase_defaults_to_current(self):
        self.pm.current_phase = ResearchPhase.COLLECT
        assert self.pm.get_next_phase() == ResearchPhase.ANALYZE

    def test_can_transition_to_different(self):
        assert self.pm.can_transition_to(ResearchPhase.COLLECT) is True
        assert self.pm.can_transition_to(ResearchPhase.REVIEW) is True

    def test_can_transition_to_same(self):
        assert self.pm.can_transition_to(ResearchPhase.PLAN) is False


class TestCoreTools:
    """Test CORE_TOOLS constant."""

    def test_core_tools_is_frozenset(self):
        assert isinstance(CORE_TOOLS, frozenset)

    def test_core_tools_contains_essentials(self):
        assert "read_file" in CORE_TOOLS
        assert "write_file" in CORE_TOOLS
        assert "edit_file" in CORE_TOOLS
        assert "bash" in CORE_TOOLS


class TestPhaseTools:
    """Test PHASE_TOOLS constant."""

    def test_all_phases_have_tools(self):
        for phase in ResearchPhase:
            assert phase in PHASE_TOOLS
            assert len(PHASE_TOOLS[phase]) > 0
