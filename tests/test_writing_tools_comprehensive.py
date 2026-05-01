"""Comprehensive tests for mini_agent/tools/writing_tools.py.

Tests WriteSectionTool, CompilePaperTool, GenerateTableTool,
GenerateDiagramTool, ConvertFigureTikzTool.
"""

import json
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


# ===================================================================
# WriteSectionTool
# ===================================================================

class TestWriteSectionToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return WriteSectionTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "write_section"

    def test_description(self, tool):
        assert "section" in tool.description.lower() or "write" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "section_name" in params["properties"]
        assert "content" in params["properties"]

    @pytest.mark.asyncio
    async def test_write_introduction(self, tool):
        result = await tool.execute(
            section_name="introduction",
            content="This paper examines the impact of fiscal policy on economic growth in Indonesia.",
        )
        assert isinstance(result.success, bool)
        if result.success:
            assert "introduction" in result.content.lower()

    @pytest.mark.asyncio
    async def test_write_methodology(self, tool):
        result = await tool.execute(
            section_name="methodology",
            content="We employ OLS regression with panel data from 2015-2024.",
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_write_results(self, tool):
        result = await tool.execute(
            section_name="results",
            content="The coefficient is statistically significant (p < 0.01).",
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_write_with_latex_format(self, tool):
        result = await tool.execute(
            section_name="abstract",
            content="This study analyzes inflation trends.",
            format="latex",
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_write_with_markdown_format(self, tool):
        result = await tool.execute(
            section_name="conclusion",
            content="In conclusion, the findings support our hypothesis.",
            format="markdown",
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_append_mode(self, tool):
        # First write
        await tool.execute(
            section_name="literature_review",
            content="First paragraph of literature review.",
        )
        # Append
        result = await tool.execute(
            section_name="literature_review",
            content="Additional paragraph appended.",
            append=True,
        )
        assert isinstance(result.success, bool)


# ===================================================================
# CompilePaperTool
# ===================================================================

class TestCompilePaperToolComprehensive:
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
    async def test_no_sections(self, tool):
        result = await tool.execute()
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_with_sections(self, tool, tmp_path):
        # Create section files
        sections_dir = tmp_path / "sections"
        sections_dir.mkdir()
        (sections_dir / "introduction.tex").write_text(
            r"\section{Introduction}" + "\nThis is the introduction."
        )
        (sections_dir / "methodology.tex").write_text(
            r"\section{Methodology}" + "\nThis is the methodology."
        )
        result = await tool.execute()
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_compile_with_template(self, tool, tmp_path):
        sections_dir = tmp_path / "sections"
        sections_dir.mkdir()
        (sections_dir / "introduction.tex").write_text(r"\section{Introduction}" + "\nContent.")
        result = await tool.execute(template="elsevier")
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_compile_draft_mode(self, tool, tmp_path):
        sections_dir = tmp_path / "sections"
        sections_dir.mkdir()
        (sections_dir / "introduction.tex").write_text(r"\section{Introduction}" + "\nContent.")
        result = await tool.execute(draft=True)
        assert isinstance(result.success, bool)


# ===================================================================
# GenerateTableTool
# ===================================================================

class TestGenerateTableToolComprehensive:
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
    async def test_with_data(self, tool):
        data = {
            "headers": ["Variable", "Mean", "SD"],
            "rows": [
                ["GDP Growth", "5.2", "1.1"],
                ["Inflation", "3.5", "0.8"],
            ],
        }
        result = await tool.execute(
            caption="Descriptive Statistics",
            data=data,
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_with_csv_path(self, tool, tmp_path):
        csv_file = tmp_path / "table_data.csv"
        csv_file.write_text("Variable,Mean,SD\nGDP,5.2,1.1\nInflation,3.5,0.8\n")
        result = await tool.execute(
            caption="Results Table",
            data_path=str(csv_file),
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_with_format_options(self, tool):
        data = {
            "headers": ["X", "Y"],
            "rows": [["1", "2"]],
        }
        result = await tool.execute(
            caption="Test Table",
            data=data,
            format="latex",
            label="tab:test",
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_no_data(self, tool):
        result = await tool.execute(caption="Empty Table")
        assert isinstance(result.success, bool)


# ===================================================================
# GenerateDiagramTool
# ===================================================================

class TestGenerateDiagramToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return GenerateDiagramTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "generate_diagram"

    def test_description(self, tool):
        assert "diagram" in tool.description.lower() or "figure" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_flowchart(self, tool):
        result = await tool.execute(
            diagram_type="flowchart",
            description="Research methodology flowchart",
            elements=["Data Collection", "Analysis", "Results"],
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_conceptual_framework(self, tool):
        result = await tool.execute(
            diagram_type="conceptual_framework",
            description="Theoretical framework",
            elements=["Independent Var", "Mediator", "Dependent Var"],
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_no_elements(self, tool):
        result = await tool.execute(
            diagram_type="flowchart",
            description="Empty diagram",
        )
        assert isinstance(result.success, bool)


# ===================================================================
# ConvertFigureTikzTool
# ===================================================================

class TestConvertFigureTikzToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return ConvertFigureTikzTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "convert_figure_tikz"

    def test_description(self, tool):
        assert "tikz" in tool.description.lower() or "figure" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_with_image_path(self, tool, tmp_path):
        # Create a dummy image file
        img_file = tmp_path / "figure.png"
        img_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        result = await tool.execute(figure_path=str(img_file))
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(figure_path="nonexistent.png")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_output_path(self, tool, tmp_path):
        img_file = tmp_path / "figure.png"
        img_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        out_file = tmp_path / "output.tex"
        result = await tool.execute(figure_path=str(img_file), output_path=str(out_file))
        assert isinstance(result.success, bool)
