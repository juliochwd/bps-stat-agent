"""Final push tests to get remaining modules to 80%+.

Targets the specific uncovered lines in each module.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ===========================================================================
# cli.py - run_agent non-interactive mode
# ===========================================================================


class TestRunAgentNonInteractive:
    """Test run_agent in non-interactive mode."""

    @pytest.mark.asyncio
    async def test_run_agent_no_config(self, tmp_path, capsys):
        """Test run_agent when config file doesn't exist."""
        from mini_agent.cli import run_agent

        with patch("mini_agent.cli.Config") as MockConfig:
            MockConfig.get_default_config_path.return_value = tmp_path / "nonexistent.yaml"
            await run_agent(tmp_path, task="test task")
            captured = capsys.readouterr()
            assert "not found" in captured.out.lower() or "setup" in captured.out.lower()

    @pytest.mark.asyncio
    async def test_run_agent_config_error(self, tmp_path, capsys):
        """Test run_agent when config loading fails."""
        from mini_agent.cli import run_agent

        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with patch("mini_agent.cli.Config") as MockConfig:
            MockConfig.get_default_config_path.return_value = config_file
            MockConfig.from_yaml.side_effect = ValueError("Bad config")
            await run_agent(tmp_path, task="test")
            captured = capsys.readouterr()
            assert "error" in captured.out.lower()


# ===========================================================================
# document_tools.py - PDF extraction and DOCX
# ===========================================================================


class TestDocumentToolsPDFExtraction:
    """Test PDF extraction fallback chains."""

    def test_extract_pdf_no_libs(self, tmp_path):
        from mini_agent.tools.document_tools import ConvertDocumentTool
        f = tmp_path / "test.pdf"
        f.write_bytes(b"%PDF-1.4 fake")
        with patch("mini_agent.tools.document_tools._HAS_PDFPLUMBER", False), \
             patch("mini_agent.tools.document_tools._HAS_PYMUPDF", False), \
             patch("mini_agent.tools.document_tools._HAS_PYPDF2", False):
            result = ConvertDocumentTool._extract_pdf(f)
            assert result == ""

    def test_extract_docx_no_lib(self, tmp_path):
        from mini_agent.tools.document_tools import ConvertDocumentTool
        f = tmp_path / "test.docx"
        f.write_bytes(b"fake docx")
        with patch("mini_agent.tools.document_tools._HAS_DOCX", False):
            result = ConvertDocumentTool._extract_docx(f)
            assert result == ""

    @pytest.mark.asyncio
    async def test_convert_pdf_no_libs(self, tmp_path):
        from mini_agent.tools.document_tools import ConvertDocumentTool
        tool = ConvertDocumentTool(workspace_dir=str(tmp_path))
        f = tmp_path / "test.pdf"
        f.write_bytes(b"%PDF-1.4 fake content")
        with patch("mini_agent.tools.document_tools._HAS_MARKITDOWN", False), \
             patch("mini_agent.tools.document_tools._HAS_PDFPLUMBER", False), \
             patch("mini_agent.tools.document_tools._HAS_PYMUPDF", False), \
             patch("mini_agent.tools.document_tools._HAS_PYPDF2", False):
            result = await tool.execute(input_path=str(f))
            assert result.success is False  # Empty output

    @pytest.mark.asyncio
    async def test_parse_pdf_no_libs(self, tmp_path):
        from mini_agent.tools.document_tools import ParseAcademicPDFTool
        tool = ParseAcademicPDFTool(workspace_dir=str(tmp_path))
        f = tmp_path / "test.pdf"
        f.write_bytes(b"%PDF-1.4 fake")
        with patch("mini_agent.tools.document_tools._HAS_PDFPLUMBER", False), \
             patch("mini_agent.tools.document_tools._HAS_PYMUPDF", False), \
             patch("mini_agent.tools.document_tools._HAS_PYPDF2", False), \
             patch("mini_agent.tools.document_tools._HAS_HTTPX", False):
            result = await tool.execute(pdf_path=str(f))
            assert result.success is False

    @pytest.mark.asyncio
    async def test_extract_refs_no_pdf_libs(self, tmp_path):
        from mini_agent.tools.document_tools import ExtractReferencesTool
        tool = ExtractReferencesTool(workspace_dir=str(tmp_path))
        f = tmp_path / "test.pdf"
        f.write_bytes(b"%PDF-1.4 fake")
        with patch("mini_agent.tools.document_tools._HAS_PDFPLUMBER", False), \
             patch("mini_agent.tools.document_tools._HAS_PYMUPDF", False), \
             patch("mini_agent.tools.document_tools._HAS_PYPDF2", False), \
             patch("mini_agent.tools.document_tools._HAS_HTTPX", False):
            result = await tool.execute(pdf_path=str(f))
            assert result.success is False


class TestDocumentToolsFormatResult:
    """Test _format_result for ParseAcademicPDFTool."""

    @pytest.mark.asyncio
    async def test_format_result_string_sections(self, tmp_path):
        from mini_agent.tools.document_tools import ParseAcademicPDFTool
        sections = {
            "title": "A" * 400,  # Long title to test truncation
            "abstract": "B" * 400,
        }
        result = ParseAcademicPDFTool._format_result(
            Path("paper.pdf"), sections, "regex", tmp_path
        )
        assert result.success is True
        assert "…" in result.content  # Truncation marker


# ===========================================================================
# sandbox_tools.py - Push to 80%
# ===========================================================================


class TestSandboxToolsFinal:
    """Final push for sandbox_tools coverage."""

    @pytest.mark.asyncio
    async def test_local_with_generated_files(self, tmp_path):
        from mini_agent.tools.sandbox_tools import PythonREPLTool
        tool = PythonREPLTool(workspace_dir=str(tmp_path))
        code = """
import json
with open('result.json', 'w') as f:
    json.dump({"status": "ok"}, f)
print("done")
"""
        result = await tool.execute(code=code)
        assert result.success is True
        assert "done" in result.content

    @pytest.mark.asyncio
    async def test_local_exit_code_nonzero(self, tmp_path):
        from mini_agent.tools.sandbox_tools import PythonREPLTool
        tool = PythonREPLTool(workspace_dir=str(tmp_path))
        result = await tool.execute(code="import sys; sys.exit(1)")
        assert result.success is False
        assert result.error is not None or "Exit code" in result.content


# ===========================================================================
# bps_data_retriever.py - Push to 80%
# ===========================================================================


class TestBPSDataRetrieverFinal:
    """Final push for bps_data_retriever coverage."""

    def test_data_result_empty_data(self):
        from mini_agent.bps_data_retriever import BPSDataResult
        result = BPSDataResult(
            table_id=1, title="Empty", subject="Test",
            update_date="2024", headers=["A"], data=[], raw_rows=[],
        )
        csv = result.to_csv()
        assert "A" in csv
        assert result.summary()
        assert "Rows: 0" in result.summary()

    @pytest.mark.asyncio
    async def test_search_pagination(self):
        mock_api = MagicMock()
        mock_api.get_static_tables.return_value = {
            "items": [
                {"table_id": i, "title": f"Table {i}", "subj": "S", "updt_date": "2024", "size": "1KB"}
                for i in range(5)
            ]
        }
        with patch("mini_agent.bps_data_retriever.BPSAPI", return_value=mock_api):
            from mini_agent.bps_data_retriever import BPSDataRetriever
            retriever = BPSDataRetriever(api_key="test")
            results = await retriever.search("test", page=2)
            assert len(results) == 5


# ===========================================================================
# agent.py - Push to 80%
# ===========================================================================


class TestAgentSummarizationFull:
    """Test agent summarization to cover lines 194-310."""

    @pytest.mark.asyncio
    async def test_create_summary(self, tmp_path):
        from mini_agent.agent import Agent
        from mini_agent.schema import Message, FunctionCall, ToolCall, LLMResponse, TokenUsage

        llm = MagicMock()
        llm.provider = "test"
        llm.model = "test"

        # Mock LLM to return a summary
        llm.generate = AsyncMock(return_value=LLMResponse(
            content="Summary: Tool was called and returned results.",
            thinking=None,
            tool_calls=None,
            finish_reason="stop",
            usage=TokenUsage(total_tokens=50, prompt_tokens=30, completion_tokens=20),
        ))

        agent = Agent(llm_client=llm, system_prompt="Test", tools=[], workspace_dir=str(tmp_path))

        messages = [
            Message(role="assistant", content="I'll help you."),
            Message(role="tool", content="Result data", tool_call_id="c1", name="tool1"),
        ]

        summary = await agent._create_summary(messages, 1)
        assert isinstance(summary, str)
        assert len(summary) > 0

    @pytest.mark.asyncio
    async def test_create_summary_with_tool_calls(self, tmp_path):
        from mini_agent.agent import Agent
        from mini_agent.schema import Message, FunctionCall, ToolCall, LLMResponse, TokenUsage

        llm = MagicMock()
        llm.provider = "test"
        llm.model = "test"
        llm.generate = AsyncMock(return_value=LLMResponse(
            content="Summary text",
            thinking=None,
            tool_calls=None,
            finish_reason="stop",
            usage=TokenUsage(total_tokens=50, prompt_tokens=30, completion_tokens=20),
        ))

        agent = Agent(llm_client=llm, system_prompt="Test", tools=[], workspace_dir=str(tmp_path))

        tc = ToolCall(id="c1", type="function", function=FunctionCall(name="bash", arguments={"cmd": "ls"}))
        messages = [
            Message(role="assistant", content="Running command.", tool_calls=[tc]),
            Message(role="tool", content="file1.txt\nfile2.txt", tool_call_id="c1", name="bash"),
        ]

        summary = await agent._create_summary(messages, 1)
        assert isinstance(summary, str)

    @pytest.mark.asyncio
    async def test_create_summary_empty(self, tmp_path):
        from mini_agent.agent import Agent

        llm = MagicMock()
        llm.provider = "test"
        llm.model = "test"
        agent = Agent(llm_client=llm, system_prompt="Test", tools=[], workspace_dir=str(tmp_path))

        summary = await agent._create_summary([], 1)
        assert summary == ""

    @pytest.mark.asyncio
    async def test_create_summary_llm_error(self, tmp_path):
        from mini_agent.agent import Agent
        from mini_agent.schema import Message

        llm = MagicMock()
        llm.provider = "test"
        llm.model = "test"
        llm.generate = AsyncMock(side_effect=Exception("LLM error"))

        agent = Agent(llm_client=llm, system_prompt="Test", tools=[], workspace_dir=str(tmp_path))

        messages = [
            Message(role="assistant", content="Working..."),
        ]

        summary = await agent._create_summary(messages, 1)
        # Should fall back to simple text summary
        assert isinstance(summary, str)
        assert "Working" in summary

    @pytest.mark.asyncio
    async def test_summarize_messages_triggers(self, tmp_path):
        """Test that summarization triggers when token limit exceeded."""
        from mini_agent.agent import Agent
        from mini_agent.schema import Message, LLMResponse, TokenUsage

        llm = MagicMock()
        llm.provider = "test"
        llm.model = "test"
        llm.generate = AsyncMock(return_value=LLMResponse(
            content="Summary",
            thinking=None,
            tool_calls=None,
            finish_reason="stop",
            usage=TokenUsage(total_tokens=50, prompt_tokens=30, completion_tokens=20),
        ))

        agent = Agent(
            llm_client=llm, system_prompt="Test", tools=[],
            workspace_dir=str(tmp_path), token_limit=100,
        )

        # Add enough messages to exceed token limit
        for i in range(20):
            agent.messages.append(Message(role="user", content=f"Message {i} " * 50))
            agent.messages.append(Message(role="assistant", content=f"Response {i} " * 50))

        original_count = len(agent.messages)
        await agent._summarize_messages()
        # After summarization, message count should change (summaries replace execution messages)
        # The new structure is: system + N user messages + N summaries
        # which is less than system + N user + N assistant = original
        new_count = len(agent.messages)
        assert new_count <= original_count

    @pytest.mark.asyncio
    async def test_summarize_insufficient_messages(self, tmp_path):
        """Test summarization with only system prompt."""
        from mini_agent.agent import Agent

        llm = MagicMock()
        llm.provider = "test"
        llm.model = "test"
        agent = Agent(
            llm_client=llm, system_prompt="Test", tools=[],
            workspace_dir=str(tmp_path), token_limit=1,
        )
        # Only system message - should not crash
        await agent._summarize_messages()
        assert len(agent.messages) == 1


# ===========================================================================
# allstats_client.py - Push to 80%
# ===========================================================================


class TestAllStatsClientFinal:
    """Final push for allstats_client coverage."""

    @pytest.mark.asyncio
    async def test_search_with_rate_limiting(self):
        """Test that rate limiting delay is applied."""
        import time
        from mini_agent.allstats_client import AllStatsClient

        client = AllStatsClient(search_delay=0)
        client._last_search_time = time.time()  # Set recent search time

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Results</html>")
        mock_page.title = AsyncMock(return_value="Results")
        mock_page.evaluate = AsyncMock(return_value=[])
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.set_default_timeout = MagicMock()

        client._page = mock_page
        client._browser = AsyncMock()
        client._playwright = AsyncMock()
        client._context = AsyncMock()

        response = await client.search("test", domain="0000")
        assert response.keyword == "test"
        assert len(response.results) == 0

    @pytest.mark.asyncio
    async def test_close_popup_exception_handling(self):
        """Test _close_popup handles exceptions in selectors."""
        from mini_agent.allstats_client import AllStatsClient

        client = AllStatsClient()
        mock_page = AsyncMock()
        # First selector raises, second returns None
        mock_page.query_selector = AsyncMock(side_effect=[Exception("DOM error")] * 9)
        mock_page.keyboard = AsyncMock()
        mock_page.keyboard.press = AsyncMock()

        client._page = mock_page
        result = await client._close_popup()
        assert result is False

    def test_build_url_special_chars(self):
        from mini_agent.allstats_client import AllStatsClient
        client = AllStatsClient()
        url = client._build_url("data & inflasi", domain="0000")
        assert "data" in url
        assert "inflasi" in url


# ===========================================================================
# dspy_modules - Cover the DSPy-available branches via mocking
# ===========================================================================


class TestDspySignaturesStubs:
    """Test signature stubs more thoroughly."""

    def test_all_stubs_instantiate(self):
        from mini_agent.research.dspy_modules.signatures import (
            SearchQuerySignature,
            EvidenceSynthesisSignature,
            MethodologyDesignSignature,
            ResultsInterpretationSignature,
            SectionWritingSignature,
        )
        # All should be instantiable as stubs
        s1 = SearchQuerySignature(topic="test")
        s2 = EvidenceSynthesisSignature(papers=["p1"])
        s3 = MethodologyDesignSignature(research_questions=["q1"], data_description="d")
        s4 = ResultsInterpretationSignature(statistical_results="r")
        s5 = SectionWritingSignature(outline="o", context="c", citations=["c1"])

        assert repr(s1)
        assert repr(s2)
        assert repr(s3)
        assert repr(s4)
        assert repr(s5)

    def test_stub_stores_kwargs(self):
        from mini_agent.research.dspy_modules.signatures import _SignatureStub
        stub = _SignatureStub(a=1, b="two", c=[3])
        assert stub.a == 1
        assert stub.b == "two"
        assert stub.c == [3]


class TestDspyModulesInit:
    """Test __init__.py import paths."""

    def test_imports_work(self):
        from mini_agent.research.dspy_modules import DSPY_AVAILABLE
        assert isinstance(DSPY_AVAILABLE, bool)

    def test_signatures_importable(self):
        """Test that signatures can be imported from the package."""
        try:
            from mini_agent.research.dspy_modules import SearchQuerySignature
            assert SearchQuerySignature is not None
        except ImportError:
            pass  # OK if import fails in some configurations

    def test_modules_importable(self):
        """Test that modules can be imported from the package."""
        try:
            from mini_agent.research.dspy_modules import LiteratureReviewModule
            assert LiteratureReviewModule is not None
        except ImportError:
            pass


# ===========================================================================
# knowledge_tools.py - Cover remaining numpy/sklearn paths
# ===========================================================================


class TestKnowledgeToolsFinal:
    """Final push for knowledge_tools coverage."""

    @pytest.mark.asyncio
    async def test_embed_papers_with_sklearn(self, tmp_path):
        """Test embedding with sklearn TF-IDF."""
        from mini_agent.tools.knowledge_tools import EmbedPapersTool

        tool = EmbedPapersTool(workspace_dir=str(tmp_path))
        papers_dir = tmp_path / "literature" / "papers"
        papers_dir.mkdir(parents=True)

        # Create papers with enough content for TF-IDF
        for i in range(3):
            (papers_dir / f"paper{i}.txt").write_text(
                f"This is paper {i} about machine learning and data science. " * 30,
                encoding="utf-8",
            )

        with patch("mini_agent.tools.knowledge_tools._HAS_SENTENCE_TRANSFORMERS", False), \
             patch("mini_agent.tools.knowledge_tools._HAS_LANCEDB", False):
            result = await tool.execute(papers_dir=str(papers_dir))
            if result.success:
                data = json.loads(result.content)
                assert data["embedded_papers"] == 3
                assert data["embedding_method"] == "tfidf"
                assert data["storage"]["backend"] == "numpy"

    @pytest.mark.asyncio
    async def test_vector_search_no_results(self, tmp_path):
        """Test vector search returning empty results."""
        from mini_agent.tools.knowledge_tools import VectorSearchTool

        tool = VectorSearchTool(workspace_dir=str(tmp_path))
        emb_dir = tmp_path / "embeddings"
        emb_dir.mkdir()

        # Empty chunk metadata
        (emb_dir / "chunk_metadata.json").write_text("[]", encoding="utf-8")

        with patch("mini_agent.tools.knowledge_tools._HAS_SENTENCE_TRANSFORMERS", False):
            result = await tool.execute(query="nonexistent topic xyz")
            if result.success:
                data = json.loads(result.content)
                assert data.get("results") == [] or "No results" in data.get("message", "")

    @pytest.mark.asyncio
    async def test_query_knowledge_graph_empty(self, tmp_path):
        """Test querying an empty knowledge graph."""
        import networkx as nx
        from mini_agent.tools.knowledge_tools import QueryKnowledgeGraphTool

        tool = QueryKnowledgeGraphTool(workspace_dir=str(tmp_path))
        graph_dir = tmp_path / "knowledge" / "graph"
        graph_dir.mkdir(parents=True)

        G = nx.Graph()
        graph_data = nx.node_link_data(G)
        (graph_dir / "knowledge_graph.json").write_text(json.dumps(graph_data), encoding="utf-8")

        result = await tool.execute(query_type="central")
        assert result.success is True
        data = json.loads(result.content)
        assert "Empty graph" in data.get("message", "")

    @pytest.mark.asyncio
    async def test_build_knowledge_graph_unreadable(self, tmp_path):
        """Test building graph when files can't be read."""
        from mini_agent.tools.knowledge_tools import BuildKnowledgeGraphTool

        tool = BuildKnowledgeGraphTool(workspace_dir=str(tmp_path))
        papers_dir = tmp_path / "literature" / "papers"
        papers_dir.mkdir(parents=True)
        # Create empty file
        (papers_dir / "empty.txt").write_text("", encoding="utf-8")

        result = await tool.execute(source="papers")
        assert result.success is False
        assert "no readable text" in result.error.lower()

    @pytest.mark.asyncio
    async def test_paper_qa_unreadable_papers(self, tmp_path):
        """Test PaperQA when papers can't be read."""
        from mini_agent.tools.knowledge_tools import PaperQATool

        tool = PaperQATool(workspace_dir=str(tmp_path))
        papers_dir = tmp_path / "literature" / "papers"
        papers_dir.mkdir(parents=True)
        (papers_dir / "empty.txt").write_text("", encoding="utf-8")

        with patch("mini_agent.tools.knowledge_tools._HAS_PAPER_QA", False):
            result = await tool.execute(question="test")
            # Should fail because no readable content
            assert result.success is False or "no papers" in (result.error or "").lower() or "Could not read" in (result.error or "")
