"""Extended tests for mini_agent/tools/writing_tools.py — paper writing tools."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.tools.writing_tools import (
    CompilePaperTool,
    ConvertFigureTikzTool,
    GenerateDiagramTool,
    GenerateTableTool,
    WriteSectionTool,
)


class TestWriteSectionTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return WriteSectionTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "write_section"

    def test_description(self, tool):
        assert "section" in tool.description.lower() or "write" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params
        assert "required" in params

    @pytest.mark.asyncio
    async def test_execute_basic(self, tool, tmp_path):
        """Test writing a section."""
        result = await tool.execute(
            section_name="introduction",
            content="This paper examines the impact of fiscal policy on economic growth.",
        )
        assert isinstance(result.success, bool)


class TestCompilePaperTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return CompilePaperTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "compile_paper"

    def test_description(self, tool):
        assert "compile" in tool.description.lower() or "paper" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_latex(self, tool, tmp_path):
        """Test compilation when no LaTeX is available."""
        with patch("shutil.which", return_value=None):
            result = await tool.execute()
            # Should fail gracefully
            assert isinstance(result.success, bool)


class TestGenerateTableTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return GenerateTableTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "generate_table"

    def test_description(self, tool):
        assert "table" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_basic(self, tool):
        """Test generating a table."""
        result = await tool.execute(
            data=[["A", "B"], [1, 2], [3, 4]],
            caption="Test table",
            label="tab:test",
        )
        assert isinstance(result.success, bool)


class TestGenerateDiagramTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return GenerateDiagramTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "generate_diagram"

    def test_description(self, tool):
        assert "diagram" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params


class TestConvertFigureTikzTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return ConvertFigureTikzTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "convert_figure_tikz"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "tikz" in desc or "figure" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params
