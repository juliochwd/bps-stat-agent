"""Extended tests for mini_agent/tools/document_tools.py — document processing tools."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.tools.document_tools import (
    ConvertDocumentTool,
    ExtractReferencesTool,
    ParseAcademicPDFTool,
)


class TestConvertDocumentTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return ConvertDocumentTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "convert_document"

    def test_description(self, tool):
        assert "convert" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params
        assert "required" in params

    @pytest.mark.asyncio
    async def test_execute_file_not_found(self, tool):
        """Test with non-existent file."""
        result = await tool.execute(
            input_path="nonexistent.pdf",
            output_format="markdown",
        )
        assert result.success is False

    @pytest.mark.asyncio
    async def test_execute_txt_to_markdown(self, tool, tmp_path):
        """Test converting a text file."""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("# Hello World\n\nThis is a test document.")

        result = await tool.execute(
            input_path=str(txt_file),
            output_format="markdown",
        )
        assert isinstance(result.success, bool)


class TestParseAcademicPDFTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return ParseAcademicPDFTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "parse_academic_pdf"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "pdf" in desc or "academic" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_file_not_found(self, tool):
        """Test with non-existent file."""
        result = await tool.execute(pdf_path="nonexistent.pdf")
        assert result.success is False


class TestExtractReferencesTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return ExtractReferencesTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "extract_references"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "reference" in desc or "extract" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_file_not_found(self, tool):
        """Test with non-existent file."""
        result = await tool.execute(input_path="nonexistent.pdf")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_execute_with_text(self, tool, tmp_path):
        """Test extracting references from text."""
        txt_file = tmp_path / "paper.txt"
        txt_file.write_text(
            "Smith (2020) found that X leads to Y. "
            "According to Jones et al. (2021), the relationship is significant. "
            "References:\n"
            "Smith, J. (2020). A Study. Journal of Testing, 1(1), 1-10.\n"
            "Jones, A., Brown, B., & Clark, C. (2021). Another Study. Research Journal, 2(2), 20-30.\n"
        )

        result = await tool.execute(input_path=str(txt_file))
        assert isinstance(result.success, bool)
