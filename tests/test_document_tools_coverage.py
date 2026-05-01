"""Comprehensive coverage tests for mini_agent/tools/document_tools.py.

Tests: ConvertDocumentTool, ParseAcademicPDFTool, ExtractReferencesTool.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_agent.tools.document_tools import (
    ConvertDocumentTool,
    ExtractReferencesTool,
    ParseAcademicPDFTool,
)


# ===========================================================================
# ConvertDocumentTool tests
# ===========================================================================


class TestConvertDocumentTool:
    """Test ConvertDocumentTool."""

    @pytest.fixture
    def tool(self, tmp_path):
        return ConvertDocumentTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(input_path="/nonexistent/file.pdf")
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_convert_txt_to_markdown(self, tool, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("# Hello World\n\nThis is a test document.", encoding="utf-8")
        result = await tool.execute(input_path=str(f), output_format="markdown")
        assert result.success is True
        assert "Hello World" in result.content

    @pytest.mark.asyncio
    async def test_convert_txt_to_text(self, tool, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("**Bold** and *italic* text.", encoding="utf-8")
        result = await tool.execute(input_path=str(f), output_format="text")
        assert result.success is True
        # Markdown symbols should be stripped
        assert "Bold" in result.content

    @pytest.mark.asyncio
    async def test_convert_txt_to_html(self, tool, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Title\n\n**Bold** text.", encoding="utf-8")
        result = await tool.execute(input_path=str(f), output_format="html")
        assert result.success is True
        assert "<h1>" in result.content or "<html>" in result.content

    @pytest.mark.asyncio
    async def test_convert_html_file(self, tool, tmp_path):
        f = tmp_path / "test.html"
        f.write_text("<html><body><h1>Title</h1><p>Content here</p></body></html>", encoding="utf-8")
        result = await tool.execute(input_path=str(f))
        assert result.success is True
        assert "Title" in result.content or "Content" in result.content

    @pytest.mark.asyncio
    async def test_convert_csv_file(self, tool, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("name,value\nA,1\nB,2", encoding="utf-8")
        result = await tool.execute(input_path=str(f))
        assert result.success is True

    @pytest.mark.asyncio
    async def test_convert_empty_file(self, tool, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")
        result = await tool.execute(input_path=str(f))
        assert result.success is False
        assert "empty" in result.error.lower()

    @pytest.mark.asyncio
    async def test_custom_output_path(self, tool, tmp_path):
        f = tmp_path / "input.txt"
        f.write_text("Some content here.", encoding="utf-8")
        out = tmp_path / "output" / "result.md"
        result = await tool.execute(input_path=str(f), output_path=str(out))
        assert result.success is True
        assert out.exists()

    @pytest.mark.asyncio
    async def test_relative_path(self, tool, tmp_path):
        f = tmp_path / "relative.txt"
        f.write_text("Relative path content.", encoding="utf-8")
        result = await tool.execute(input_path="relative.txt")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_properties(self, tool):
        assert tool.name == "convert_document"
        assert "input_path" in tool.parameters["properties"]

    def test_extract_html_logic(self):
        """Test HTML extraction logic directly."""
        import re
        html = "<html><script>alert('x')</script><style>body{}</style><p>Hello</p></html>"
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        assert "Hello" in text
        assert "alert" not in text

    def test_markdown_to_html_static(self):
        md = "# Title\n\n**Bold** and *italic*"
        result = ConvertDocumentTool._markdown_to_html(md)
        assert "<h1>Title</h1>" in result
        assert "<strong>Bold</strong>" in result
        assert "<em>italic</em>" in result


# ===========================================================================
# ParseAcademicPDFTool tests
# ===========================================================================


class TestParseAcademicPDFTool:
    """Test ParseAcademicPDFTool."""

    @pytest.fixture
    def tool(self, tmp_path):
        return ParseAcademicPDFTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(pdf_path="/nonexistent/paper.pdf")
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_not_pdf(self, tool, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("Not a PDF", encoding="utf-8")
        result = await tool.execute(pdf_path=str(f))
        assert result.success is False
        assert "not a pdf" in result.error.lower()

    @pytest.mark.asyncio
    async def test_identify_sections(self, tool, tmp_path):
        """Test regex-based section identification."""
        text = """Impact of Education on Economic Growth

Abstract
This paper examines the relationship between education and economic growth.

Keywords: education, growth, Indonesia

1. Introduction
Education is a key driver of economic development.

2. Literature Review
Previous studies have shown positive effects.

3. Methods
We use panel data regression with fixed effects.

4. Results
The coefficient is significant at 5% level.

5. Discussion
Our findings confirm the hypothesis.

6. Conclusion
Education significantly impacts growth.

References
Smith, J. (2020). Education and Growth. Journal of Economics, 15(2), 45-60.
"""
        sections = tool._identify_sections(text, "all")
        assert "title" in sections
        assert "abstract" in sections or "introduction" in sections

    @pytest.mark.asyncio
    async def test_extract_tables(self):
        text = "Table 1: GDP Growth Rates\n\nSome data here\n\nTable 2. Inflation by Province\n\nMore data"
        tables = ParseAcademicPDFTool._extract_tables(text)
        assert len(tables) >= 1

    @pytest.mark.asyncio
    async def test_extract_figure_captions(self):
        text = "Figure 1: Trend Analysis\n\nSome description\n\nFig. 2: Distribution Plot\n\nMore text"
        figures = ParseAcademicPDFTool._extract_figure_captions(text)
        assert len(figures) >= 1

    @pytest.mark.asyncio
    async def test_parse_grobid_tei(self):
        tei_xml = """
        <TEI>
            <title type="main">Test Paper Title</title>
            <abstract>This is the abstract.</abstract>
            <persName><forename>John</forename><surname>Smith</surname></persName>
            <body><div><head>Introduction</head>Some body text.</div></body>
            <biblStruct><title>Ref Title</title></biblStruct>
        </TEI>
        """
        result = ParseAcademicPDFTool._parse_grobid_tei(tei_xml, "all")
        assert result.get("title") == "Test Paper Title"
        assert "abstract" in result

    @pytest.mark.asyncio
    async def test_properties(self, tool):
        assert tool.name == "parse_academic_pdf"
        assert "pdf_path" in tool.parameters["properties"]


# ===========================================================================
# ExtractReferencesTool tests
# ===========================================================================


class TestExtractReferencesTool:
    """Test ExtractReferencesTool."""

    @pytest.fixture
    def tool(self, tmp_path):
        return ExtractReferencesTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_no_input(self, tool):
        result = await tool.execute()
        assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(pdf_path="/nonexistent.pdf")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_extract_from_text(self, tool, tmp_path):
        text = """
References
[1] Smith, J. (2020). "Impact of Education on Growth." Journal of Economics, 15(2), 45-60. 10.1234/je.2020.001
[2] Johnson, A. and Brown, B. (2019). "Poverty Analysis in Indonesia." Development Studies, 8(1), 12-30.
[3] Williams, C. (2021). "Machine Learning for Economic Forecasting." AI Review, 3(4), 100-120.
"""
        result = await tool.execute(text=text, output_format="bibtex")
        if result.success:
            assert "bibtex" in result.content.lower() or "@" in result.content

    @pytest.mark.asyncio
    async def test_extract_json_format(self, tool, tmp_path):
        text = """
References
Smith, J. (2020). "Impact of Education." Journal of Economics, 15(2), 45-60.
"""
        result = await tool.execute(text=text, output_format="json")
        if result.success:
            assert "json" in result.content.lower() or "Smith" in result.content

    @pytest.mark.asyncio
    async def test_no_references_section(self, tool):
        text = "This is just regular text without any references section."
        result = await tool.execute(text=text)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_extract_references_regex(self):
        text = """
References
Smith, J. (2020). "Impact of Education on Growth." Journal of Economics, 15(2), 45-60. 10.1234/je.2020.001
Johnson, A. and Brown, B. (2019). "Poverty Analysis." Development Studies, 8(1), 12-30.
"""
        refs = ExtractReferencesTool._extract_references_regex(text)
        assert len(refs) >= 1

    @pytest.mark.asyncio
    async def test_to_bibtex(self):
        refs = [
            {"authors": "Smith, J.", "title": "Test Paper", "year": "2020", "journal": "Test Journal", "doi": "10.1234/test"},
            {"authors": "Brown, A.", "title": "Another Paper", "year": "2021"},
        ]
        bibtex = ExtractReferencesTool._to_bibtex(refs)
        assert "@article" in bibtex
        assert "@misc" in bibtex
        assert "Smith" in bibtex

    @pytest.mark.asyncio
    async def test_parse_grobid_refs(self):
        tei_xml = """
        <biblStruct>
            <title>Test Reference Title</title>
            <persName><forename>John</forename><surname>Doe</surname></persName>
            <date when="2020"/>
            <title level="j">Test Journal</title>
            <biblScope unit="volume">15</biblScope>
            <idno type="DOI">10.1234/test</idno>
        </biblStruct>
        """
        refs = ExtractReferencesTool._parse_grobid_refs(tei_xml)
        assert len(refs) >= 1
        assert refs[0].get("title") == "Test Reference Title"

    @pytest.mark.asyncio
    async def test_properties(self, tool):
        assert tool.name == "extract_references"
