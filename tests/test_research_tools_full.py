"""Full coverage tests for mini_agent/tools/research_tools.py.

Covers ProjectInitTool, ProjectStatusTool, SwitchPhaseTool.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from mini_agent.tools.research_tools import (
    ProjectInitTool,
    ProjectStatusTool,
    SwitchPhaseTool,
)


# ===================================================================
# ProjectInitTool
# ===================================================================

class TestProjectInitToolFull:
    @pytest.fixture
    def tool(self, tmp_path):
        return ProjectInitTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "project_init"

    def test_description(self, tool):
        assert "initialize" in tool.description.lower() or "research" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "title" in params["properties"]
        assert "title" in params["required"]
        assert "template" in params["properties"]
        assert "target_journal" in params["properties"]

    @pytest.mark.asyncio
    async def test_init_basic(self, tool, tmp_path):
        result = await tool.execute(title="Test Research Paper")
        assert result.success is True
        assert "Test Research Paper" in result.content
        assert "PLAN" in result.content

    @pytest.mark.asyncio
    async def test_init_with_template(self, tool):
        result = await tool.execute(title="Paper", template="ieee")
        assert result.success is True
        assert "ieee" in result.content.lower()

    @pytest.mark.asyncio
    async def test_init_with_journal(self, tool):
        result = await tool.execute(title="Paper", target_journal="Nature")
        assert result.success is True
        assert "Nature" in result.content

    @pytest.mark.asyncio
    async def test_init_with_research_questions(self, tool):
        rqs = ["What is the effect of X on Y?", "How does Z mediate the relationship?"]
        result = await tool.execute(title="Paper", research_questions=rqs)
        assert result.success is True
        assert "RQ1" in result.content
        assert "RQ2" in result.content

    @pytest.mark.asyncio
    async def test_init_failure(self, tool):
        with patch("mini_agent.tools.research_tools.ProjectInitTool.execute") as mock_exec:
            # Simulate an error in the actual implementation
            pass
        # Test with a mock that raises
        with patch("mini_agent.research.project_state.ProjectState.create_new", side_effect=Exception("fail")):
            result = await tool.execute(title="Paper")
            assert result.success is False


# ===================================================================
# ProjectStatusTool
# ===================================================================

class TestProjectStatusToolFull:
    @pytest.fixture
    def tool(self, tmp_path):
        return ProjectStatusTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "project_status"

    def test_description(self, tool):
        assert "status" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "verbose" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_project(self, tool):
        result = await tool.execute()
        assert result.success is False
        assert "No active" in result.error or "project_init" in result.error

    @pytest.mark.asyncio
    async def test_with_project(self, tool, tmp_path):
        # First init a project
        init_tool = ProjectInitTool(workspace_dir=str(tmp_path))
        await init_tool.execute(title="Test Paper")
        # Now check status
        result = await tool.execute()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_verbose(self, tool, tmp_path):
        init_tool = ProjectInitTool(workspace_dir=str(tmp_path))
        await init_tool.execute(title="Test Paper")
        result = await tool.execute(verbose=True)
        assert result.success is True


# ===================================================================
# SwitchPhaseTool
# ===================================================================

class TestSwitchPhaseToolFull:
    @pytest.fixture
    def tool(self, tmp_path):
        return SwitchPhaseTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "switch_phase"

    def test_description(self, tool):
        assert "phase" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "target_phase" in params["properties"]
        assert "target_phase" in params["required"]

    @pytest.mark.asyncio
    async def test_no_project(self, tool):
        result = await tool.execute(target_phase="collect")
        assert result.success is False
        assert "No active" in result.error

    @pytest.mark.asyncio
    async def test_switch_to_collect(self, tmp_path):
        init_tool = ProjectInitTool(workspace_dir=str(tmp_path))
        await init_tool.execute(title="Test Paper")
        tool = SwitchPhaseTool(workspace_dir=str(tmp_path))
        result = await tool.execute(target_phase="collect")
        assert result.success is True
        assert "collect" in result.content.lower() or "COLLECT" in result.content

    @pytest.mark.asyncio
    async def test_switch_same_phase(self, tmp_path):
        init_tool = ProjectInitTool(workspace_dir=str(tmp_path))
        await init_tool.execute(title="Test Paper")
        tool = SwitchPhaseTool(workspace_dir=str(tmp_path))
        result = await tool.execute(target_phase="plan")
        assert result.success is True
        assert "Already" in result.content

    @pytest.mark.asyncio
    async def test_switch_with_reason(self, tmp_path):
        init_tool = ProjectInitTool(workspace_dir=str(tmp_path))
        await init_tool.execute(title="Test Paper")
        tool = SwitchPhaseTool(workspace_dir=str(tmp_path))
        result = await tool.execute(target_phase="collect", reason="Data collection ready")
        assert result.success is True
        assert "Data collection ready" in result.content

    @pytest.mark.asyncio
    async def test_invalid_phase(self, tmp_path):
        init_tool = ProjectInitTool(workspace_dir=str(tmp_path))
        await init_tool.execute(title="Test Paper")
        tool = SwitchPhaseTool(workspace_dir=str(tmp_path))
        result = await tool.execute(target_phase="invalid_phase")
        assert result.success is False
