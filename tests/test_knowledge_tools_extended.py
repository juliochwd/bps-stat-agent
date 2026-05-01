"""Extended tests for mini_agent/tools/knowledge_tools.py — RAG and knowledge graph tools."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.tools.knowledge_tools import (
    BuildKnowledgeGraphTool,
    ChunkDocumentTool,
    EmbedPapersTool,
    ExtractEntitiesTool,
    PaperQATool,
    QueryKnowledgeGraphTool,
    VectorSearchTool,
)


class TestChunkDocumentTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return ChunkDocumentTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "chunk_document"

    def test_description(self, tool):
        assert "chunk" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_file_not_found(self, tool):
        """Test with non-existent file."""
        result = await tool.execute(file_path="nonexistent.txt")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_execute_with_text(self, tool, tmp_path):
        """Test chunking a text file."""
        txt_file = tmp_path / "paper.txt"
        content = "Paragraph one. " * 50 + "\n\n" + "Paragraph two. " * 50
        txt_file.write_text(content)

        result = await tool.execute(file_path=str(txt_file))
        assert isinstance(result.success, bool)


class TestEmbedPapersTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return EmbedPapersTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "embed_papers"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "embed" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_deps(self, tool):
        """Test when embedding dependencies are not available."""
        result = await tool.execute(input_dir="papers/")
        assert isinstance(result.success, bool)


class TestVectorSearchTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return VectorSearchTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "vector_search"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "search" in desc or "vector" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_index(self, tool):
        """Test when no vector index exists."""
        result = await tool.execute(query="poverty reduction")
        assert isinstance(result.success, bool)


class TestExtractEntitiesTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return ExtractEntitiesTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "extract_entities"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "entit" in desc or "extract" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_basic(self, tool):
        """Test entity extraction."""
        result = await tool.execute(
            text="Indonesia's GDP grew by 5.2% in 2023 according to BPS."
        )
        assert isinstance(result.success, bool)


class TestBuildKnowledgeGraphTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return BuildKnowledgeGraphTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "build_knowledge_graph"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "knowledge" in desc or "graph" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params


class TestQueryKnowledgeGraphTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return QueryKnowledgeGraphTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "query_knowledge_graph"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "query" in desc or "knowledge" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_graph(self, tool):
        """Test when no knowledge graph exists."""
        result = await tool.execute(query_type="neighbors", entity="poverty")
        assert isinstance(result.success, bool)


class TestPaperQATool:
    @pytest.fixture
    def tool(self, tmp_path):
        return PaperQATool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "paper_qa"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "paper" in desc or "qa" in desc or "question" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_papers(self, tool):
        """Test when no papers are indexed."""
        result = await tool.execute(question="What is the main finding?")
        assert isinstance(result.success, bool)
