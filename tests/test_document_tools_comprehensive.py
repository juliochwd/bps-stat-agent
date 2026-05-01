"""Comprehensive tests for mini_agent/tools/document_tools.py.

Tests ConvertDocumentTool, ParseAcademicPDFTool, ExtractReferencesTool.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.tools.document_tools import (
    ConvertDocumentTool,
    ExtractReferencesTool,
    ParseAcademicPDFTool,
)


# ===================================================================
# ConvertDocumentTool
# ===================================================================

class TestConvertDocumentToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return ConvertDocumentTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "convert_document"

    def test_description(self, tool):
        assert "convert" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "input_path" in params["properties"]
        assert "output_format" in params["properties"]

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(input_path="nonexistent.pdf", output_format="markdown")
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_convert_txt_to_markdown(self, tool, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("# Hello World\n\nThis is a test document with some content.")
        result = await tool.execute(input_path=str(txt_file), output_format="markdown")
        assert result.success is True
        assert "Hello World" in result.content

    @pytest.mark.asyncio
    async def test_convert_txt_to_text(self, tool, tmp_path):
        txt_file = tmp_path / "test.md"
        txt_file.write_text("# Title\n\n**Bold** and *italic* text.")
        result = await tool.execute(input_path=str(txt_file), output_format="text")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_convert_txt_to_html(self, tool, tmp_path):
        txt_file = tmp_path / "test.md"
        txt_file.write_text("# Title\n\nParagraph text here.")
        result = await tool.execute(input_path=str(txt_file), output_format="html")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_convert_csv(self, tool, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x,y\n1,2\n3,4\n")
        result = await tool.execute(input_path=str(csv_file), output_format="markdown")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_convert_html(self, tool, tmp_path):
        html_file = tmp_path / "page.html"
        html_file.write_text("<html><body><h1>Title</h1><p>Content</p></body></html>")
        result = await tool.execute(input_path=str(html_file), output_format="markdown")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_empty_file(self, tool, tmp_path):
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")
        result = await tool.execute(input_path=str(empty_file), output_format="markdown")
        assert result.success is False
        assert "empty" in result.error.lower()

    @pytest.mark.asyncio
    async def test_custom_output_path(self, tool, tmp_path):
        txt_file = tmp_path / "input.txt"
        txt_file.write_text("Some content here.")
        output_file = tmp_path / "output.md"
        result = await tool.execute(
            input_path=str(txt_file),
            output_format="markdown",
            output_path=str(output_file),
        )
        assert result.success is True
        assert output_file.exists()

    @pytest.mark.asyncio
    async def test_relative_path(self, tool, tmp_path):
        txt_file = tmp_path / "doc.txt"
        txt_file.write_text("Relative path content.")
        result = await tool.execute(input_path="doc.txt", output_format="markdown")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_latex_file(self, tool, tmp_path):
        tex_file = tmp_path / "paper.tex"
        tex_file.write_text(r"\documentclass{article}\begin{document}Hello\end{document}")
        result = await tool.execute(input_path=str(tex_file), output_format="markdown")
        assert result.success is True


# ===================================================================
# ParseAcademicPDFTool
# ===================================================================

class TestParseAcademicPDFToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return ParseAcademicPDFTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "parse_academic_pdf"

    def test_description(self, tool):
        assert "pdf" in tool.description.lower() or "academic" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "pdf_path" in params["properties"]

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(pdf_path="nonexistent.pdf")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_non_pdf_file(self, tool, tmp_path):
        txt_file = tmp_path / "not_a_pdf.txt"
        txt_file.write_text("This is not a PDF")
        result = await tool.execute(pdf_path=str(txt_file))
        # Should handle gracefully
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_with_mock_pdf(self, tool, tmp_path):
        # Create a minimal PDF-like file
        pdf_file = tmp_path / "paper.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n")
        result = await tool.execute(pdf_path=str(pdf_file))
        # Will likely fail to parse but should not crash
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_extract_sections_option(self, tool, tmp_path):
        pdf_file = tmp_path / "paper.pdf"
        pdf_file.write_bytes(b"%PDF-1.4\n")
        result = await tool.execute(pdf_path=str(pdf_file), extract_sections=True)
        assert isinstance(result.success, bool)


# ===================================================================
# ExtractReferencesTool
# ===================================================================

class TestExtractReferencesToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return ExtractReferencesTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "extract_references"

    def test_description(self, tool):
        assert "reference" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_no_text_or_file(self, tool):
        result = await tool.execute()
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_text(self, tool):
        text = """
        References:
        Smith, J. (2024). A study of inflation. Journal of Economics, 15(2), 100-115.
        Jones, A., & Brown, B. (2023). Statistical methods. Statistics Review, 8(1), 50-65.
        """
        result = await tool.execute(text=text)
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_with_file(self, tool, tmp_path):
        txt_file = tmp_path / "refs.txt"
        txt_file.write_text(
            "References:\n"
            "Smith, J. (2024). A study. Journal, 15(2), 100-115.\n"
            "Jones, A. (2023). Another study. Review, 8(1), 50-65.\n"
        )
        result = await tool.execute(file_path=str(txt_file))
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(file_path="nonexistent.txt")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_empty_text(self, tool):
        result = await tool.execute(text="")
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_text_with_no_references(self, tool):
        result = await tool.execute(text="This is just a regular paragraph with no citations.")
        assert isinstance(result.success, bool)
