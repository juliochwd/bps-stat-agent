"""Tests for mini_agent/research/orchestrator.py — Research Orchestrator."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_agent.research.orchestrator import ResearchOrchestrator
from mini_agent.research.phase_manager import PhaseManager
from mini_agent.research.project_state import ResearchPhase


@pytest.fixture
def mock_llm_client():
    return MagicMock()


@pytest.fixture
def mock_tools():
    """Create mock tools."""
    tools = []
    for name in ["read_file", "write_file", "edit_file", "bash", "project_status", "switch_phase"]:
        tool = MagicMock()
        tool.name = name
        tools.append(tool)
    return tools


@pytest.fixture
def orchestrator(mock_llm_client, mock_tools, tmp_path):
    """Create a ResearchOrchestrator instance."""
    return ResearchOrchestrator(
        llm_client=mock_llm_client,
        system_prompt="You are a research assistant.",
        all_tools=mock_tools,
        workspace_dir=str(tmp_path),
        max_steps=10,
    )


class TestResearchOrchestrator:
    def test_init(self, orchestrator, tmp_path):
        assert orchestrator.workspace_dir == tmp_path
        assert orchestrator.max_steps == 10
        assert orchestrator.project_state is None
        assert orchestrator._agent is None

    def test_init_loads_existing_state(self, mock_llm_client, mock_tools, tmp_path):
        """Test that existing project state is loaded."""
        with patch("mini_agent.research.orchestrator.ProjectState.load") as mock_load:
            mock_state = MagicMock()
            mock_state.phase = ResearchPhase.ANALYZE
            mock_load.return_value = mock_state

            orch = ResearchOrchestrator(
                llm_client=mock_llm_client,
                system_prompt="test",
                all_tools=mock_tools,
                workspace_dir=str(tmp_path),
            )
            assert orch.project_state == mock_state
            assert orch.phase_manager.current_phase == ResearchPhase.ANALYZE

    def test_init_no_existing_state(self, orchestrator):
        """No existing state means project_state is None."""
        assert orchestrator.project_state is None
        assert orchestrator.phase_manager.current_phase == ResearchPhase.PLAN

    def test_build_agent(self, orchestrator):
        """Test building an agent for the current phase."""
        agent = orchestrator._build_agent()
        assert agent is not None

    def test_build_phase_prompt(self, orchestrator):
        """Test phase prompt generation."""
        prompt = orchestrator._build_phase_prompt()
        assert "Current Research Phase" in prompt
        assert "PLAN" in prompt

    def test_build_phase_prompt_with_state(self, orchestrator):
        """Test phase prompt with project state."""
        mock_state = MagicMock()
        mock_state.get_progress_summary.return_value = "50% complete"
        orchestrator.project_state = mock_state

        prompt = orchestrator._build_phase_prompt()
        assert "50% complete" in prompt

    def test_init_project(self, orchestrator):
        """Test project initialization."""
        with patch("mini_agent.research.orchestrator.WorkspaceScaffolder") as mock_scaffolder:
            mock_scaffolder.return_value.scaffold = MagicMock()
            with patch("mini_agent.research.orchestrator.ProjectState.create_new") as mock_create:
                mock_state = MagicMock()
                mock_create.return_value = mock_state

                result = orchestrator.init_project(
                    title="Test Paper",
                    template="imrad",
                    target_journal="Nature",
                    research_questions=["Q1"],
                )
                assert result == mock_state

    def test_switch_phase(self, orchestrator):
        """Test phase switching."""
        orchestrator.project_state = MagicMock()
        result = orchestrator.switch_phase(ResearchPhase.COLLECT)

        assert "PLAN" in result
        assert "COLLECT" in result
        assert orchestrator.phase_manager.current_phase == ResearchPhase.COLLECT
        assert orchestrator._agent is None  # Force rebuild

    def test_switch_phase_same_phase(self, orchestrator):
        """Test switching to same phase."""
        result = orchestrator.switch_phase(ResearchPhase.PLAN)
        assert "Already in phase" in result

    @pytest.mark.asyncio
    async def test_run(self, orchestrator):
        """Test running the orchestrator."""
        with patch("mini_agent.research.orchestrator.Agent") as mock_agent_cls:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value="Agent response")
            mock_agent.add_user_message = MagicMock()
            mock_agent_cls.return_value = mock_agent

            result = await orchestrator.run("Hello")
            assert result == "Agent response"

    @pytest.mark.asyncio
    async def test_run_without_message(self, orchestrator):
        """Test running without a user message."""
        with patch("mini_agent.research.orchestrator.Agent") as mock_agent_cls:
            mock_agent = MagicMock()
            mock_agent.run = AsyncMock(return_value="Response")
            mock_agent_cls.return_value = mock_agent

            result = await orchestrator.run()
            assert result == "Response"
            mock_agent.add_user_message.assert_not_called()

    def test_get_status_no_project(self, orchestrator):
        """Test status when no project exists."""
        result = orchestrator.get_status()
        assert "No active research project" in result

    def test_get_status_with_project(self, orchestrator):
        """Test status with active project."""
        mock_state = MagicMock()
        mock_state.get_progress_summary.return_value = "Project: Test Paper\nPhase: PLAN"
        orchestrator.project_state = mock_state

        result = orchestrator.get_status()
        assert "Project: Test Paper" in result
