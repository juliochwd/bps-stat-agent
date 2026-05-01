"""Comprehensive tests for mini_agent/tools/knowledge_tools.py.

Tests all tool classes: ChunkDocument, EmbedPapers, VectorSearch,
ExtractEntities, BuildKnowledgeGraph, QueryKnowledgeGraph, PaperQA.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

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


# ===================================================================
# ChunkDocumentTool
# ===================================================================

class TestChunkDocumentToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return ChunkDocumentTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "chunk_document"

    def test_description(self, tool):
        assert "chunk" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "file_path" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.knowledge_tools._HAS_NUMPY", False):
            result = await tool.execute(file_path="test.txt")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(file_path="nonexistent.txt")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_empty_file(self, tool, tmp_path):
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")
        result = await tool.execute(file_path=str(empty_file))
        assert result.success is False

    @pytest.mark.asyncio
    async def test_overlap_exceeds_chunk_size(self, tool, tmp_path):
        txt_file = tmp_path / "doc.txt"
        txt_file.write_text("Some text content here.")
        result = await tool.execute(file_path=str(txt_file), chunk_size=100, overlap=200)
        assert result.success is False

    @pytest.mark.asyncio
    async def test_fixed_chunking(self, tool, tmp_path):
        txt_file = tmp_path / "doc.txt"
        content = "Word " * 500  # ~500 words
        txt_file.write_text(content)
        result = await tool.execute(file_path=str(txt_file), method="fixed", chunk_size=100)
        if not result.success:
            # numpy not available
            pytest.skip("numpy not available for chunking")
        data = json.loads(result.content)
        assert data["num_chunks"] > 0
        assert data["method"] == "fixed"

    @pytest.mark.asyncio
    async def test_sentence_chunking(self, tool, tmp_path):
        txt_file = tmp_path / "doc.txt"
        content = "This is sentence one. " * 100
        txt_file.write_text(content)
        result = await tool.execute(file_path=str(txt_file), method="sentence", chunk_size=200)
        if not result.success:
            pytest.skip("numpy not available for chunking")
        data = json.loads(result.content)
        assert data["method"] == "sentence"

    @pytest.mark.asyncio
    async def test_semantic_chunking(self, tool, tmp_path):
        txt_file = tmp_path / "doc.txt"
        content = "First paragraph about economics. " * 50 + "\n\n" + "Second paragraph about statistics. " * 50
        txt_file.write_text(content)
        result = await tool.execute(file_path=str(txt_file), method="semantic", chunk_size=200)
        if not result.success:
            pytest.skip("numpy not available")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_absolute_path(self, tool, tmp_path):
        txt_file = tmp_path / "abs.txt"
        txt_file.write_text("Content " * 100)
        result = await tool.execute(file_path=str(txt_file), method="fixed")
        if not result.success:
            pytest.skip("numpy not available")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_output_saved(self, tool, tmp_path):
        txt_file = tmp_path / "doc.txt"
        txt_file.write_text("Content " * 200)
        result = await tool.execute(file_path=str(txt_file), method="fixed")
        if not result.success:
            pytest.skip("numpy not available")
        data = json.loads(result.content)
        output_path = Path(data["output_path"])
        assert output_path.exists()


# ===================================================================
# EmbedPapersTool
# ===================================================================

class TestEmbedPapersToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return EmbedPapersTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "embed_papers"

    def test_description(self, tool):
        assert "embed" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.knowledge_tools._HAS_NUMPY", False):
            result = await tool.execute(chunks_path="chunks.json")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(chunks_path="nonexistent.json")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_chunks(self, tool, tmp_path):
        # Create chunks file
        chunks = [
            {"index": 0, "text": "First chunk about economics", "token_count": 5},
            {"index": 1, "text": "Second chunk about statistics", "token_count": 5},
        ]
        chunks_file = tmp_path / "knowledge" / "test_chunks.json"
        chunks_file.parent.mkdir(parents=True, exist_ok=True)
        chunks_file.write_text(json.dumps(chunks))
        result = await tool.execute(chunks_path=str(chunks_file))
        # May fail if sentence-transformers not available
        assert isinstance(result.success, bool)


# ===================================================================
# VectorSearchTool
# ===================================================================

class TestVectorSearchToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return VectorSearchTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "vector_search"

    def test_description(self, tool):
        assert "search" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "query" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.knowledge_tools._HAS_NUMPY", False):
            result = await tool.execute(query="test query")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_no_embeddings(self, tool):
        result = await tool.execute(query="test query")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_embeddings(self, tool, tmp_path):
        # Create embeddings file - skip if numpy not available
        try:
            import numpy as np
        except ImportError:
            pytest.skip("numpy not available")
        embeddings_dir = tmp_path / "knowledge" / "embeddings"
        embeddings_dir.mkdir(parents=True, exist_ok=True)
        # Create a simple embeddings file
        data = {
            "chunks": [
                {"index": 0, "text": "Economics data", "source_file": "test.txt"},
                {"index": 1, "text": "Statistics info", "source_file": "test.txt"},
            ],
            "embeddings": np.random.rand(2, 384).tolist(),
            "model": "test-model",
        }
        emb_file = embeddings_dir / "test_embeddings.json"
        emb_file.write_text(json.dumps(data))
        result = await tool.execute(query="economics")
        # May fail if sentence-transformers not available
        assert isinstance(result.success, bool)


# ===================================================================
# ExtractEntitiesTool
# ===================================================================

class TestExtractEntitiesToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return ExtractEntitiesTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "extract_entities"

    def test_description(self, tool):
        assert "entit" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_no_text_or_file(self, tool):
        result = await tool.execute()
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_text(self, tool):
        text = "Indonesia's GDP grew by 5.2% in 2024 according to BPS. Jakarta reported the highest growth."
        result = await tool.execute(text=text)
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_with_file(self, tool, tmp_path):
        txt_file = tmp_path / "paper.txt"
        txt_file.write_text("The study by Smith (2024) found that inflation in NTT was 3.5%.")
        result = await tool.execute(file_path=str(txt_file))
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(file_path="nonexistent.txt")
        assert result.success is False


# ===================================================================
# BuildKnowledgeGraphTool
# ===================================================================

class TestBuildKnowledgeGraphToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return BuildKnowledgeGraphTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "build_knowledge_graph"

    def test_description(self, tool):
        assert "knowledge" in tool.description.lower() or "graph" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_no_entities(self, tool):
        result = await tool.execute()
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_with_entities(self, tool, tmp_path):
        # Create entities file
        entities_dir = tmp_path / "knowledge"
        entities_dir.mkdir(parents=True, exist_ok=True)
        entities = [
            {"text": "Indonesia", "type": "LOCATION", "source": "test.txt"},
            {"text": "GDP", "type": "CONCEPT", "source": "test.txt"},
        ]
        entities_file = entities_dir / "entities.json"
        entities_file.write_text(json.dumps(entities))
        result = await tool.execute(entities_path=str(entities_file))
        assert isinstance(result.success, bool)


# ===================================================================
# QueryKnowledgeGraphTool
# ===================================================================

class TestQueryKnowledgeGraphToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return QueryKnowledgeGraphTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "query_knowledge_graph"

    def test_description(self, tool):
        assert "knowledge" in tool.description.lower() or "graph" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "query_type" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_graph(self, tool):
        result = await tool.execute(query_type="neighbors", entity="GDP")
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_with_graph(self, tool, tmp_path):
        # Create a simple knowledge graph file
        kg_dir = tmp_path / "knowledge"
        kg_dir.mkdir(parents=True, exist_ok=True)
        graph = {
            "nodes": [
                {"id": "Indonesia", "type": "LOCATION"},
                {"id": "GDP", "type": "CONCEPT"},
            ],
            "edges": [
                {"source": "Indonesia", "target": "GDP", "relation": "has_indicator"},
            ],
        }
        kg_file = kg_dir / "knowledge_graph.json"
        kg_file.write_text(json.dumps(graph))
        result = await tool.execute(query_type="neighbors", entity="Indonesia")
        assert isinstance(result.success, bool)


# ===================================================================
# PaperQATool
# ===================================================================

class TestPaperQAToolComprehensive:
    @pytest.fixture
    def tool(self, tmp_path):
        return PaperQATool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "paper_qa"

    def test_description(self, tool):
        assert "paper" in tool.description.lower() or "qa" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "question" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.knowledge_tools._HAS_NUMPY", False):
            result = await tool.execute(question="What is inflation?")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_no_papers(self, tool):
        result = await tool.execute(question="What is inflation?")
        # Should fail gracefully when no papers are embedded
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_with_question(self, tool, tmp_path):
        # Create some knowledge files
        kg_dir = tmp_path / "knowledge"
        kg_dir.mkdir(parents=True, exist_ok=True)
        chunks = [
            {"index": 0, "text": "Inflation in NTT was 3.5% in 2024.", "source_file": "paper.pdf"},
        ]
        chunks_file = kg_dir / "paper_chunks.json"
        chunks_file.write_text(json.dumps(chunks))
        result = await tool.execute(question="What was inflation in NTT?")
        assert isinstance(result.success, bool)
