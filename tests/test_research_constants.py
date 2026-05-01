"""Tests for mini_agent.research.constants."""

from mini_agent.research.constants import (
    CACHE_TTL,
    CHUNK_OVERLAP_TOKENS,
    CHUNK_SIZE_TOKENS,
    DEFAULT_EMBEDDING_DIMENSIONS,
    DEFAULT_MAX_STEPS,
    DEFAULT_TEMPLATE,
    DEFAULT_TOKEN_LIMIT,
    JOURNAL_TEMPLATES,
    MAX_TOOLS_PER_PHASE,
    MODEL_ROUTING_RULES,
    PAPER_SECTIONS,
    PHASE_ORDER,
    RESEARCH_VERSION,
    SUPPORTED_DATA_FORMATS,
    SUPPORTED_FIGURE_FORMATS,
    SUPPORTED_METHODOLOGIES,
    SUPPORTED_TEMPLATES,
    WORKSPACE_DIRS,
)
from mini_agent.research.project_state import ResearchPhase


class TestVersion:
    def test_is_string(self):
        assert isinstance(RESEARCH_VERSION, str) and "." in RESEARCH_VERSION

    def test_token_limit(self):
        assert DEFAULT_TOKEN_LIMIT > 0

    def test_max_steps(self):
        assert DEFAULT_MAX_STEPS > 0


class TestTemplates:
    def test_non_empty(self):
        assert len(SUPPORTED_TEMPLATES) > 0

    def test_default_in_list(self):
        assert DEFAULT_TEMPLATE in SUPPORTED_TEMPLATES

    def test_all_strings(self):
        assert all(isinstance(t, str) for t in SUPPORTED_TEMPLATES)

    def test_journal_match(self):
        for t in SUPPORTED_TEMPLATES:
            assert t in JOURNAL_TEMPLATES


class TestWorkspace:
    def test_data_raw(self):
        assert "data/raw" in WORKSPACE_DIRS

    def test_writing_sections(self):
        assert "writing/sections" in WORKSPACE_DIRS

    def test_checkpoints(self):
        assert "checkpoints" in WORKSPACE_DIRS

    def test_sessions(self):
        assert ".sessions" in WORKSPACE_DIRS


class TestRouting:
    def test_planning(self):
        assert "planning" in MODEL_ROUTING_RULES

    def test_writing(self):
        assert "writing" in MODEL_ROUTING_RULES

    def test_embedding(self):
        assert "embedding" in MODEL_ROUTING_RULES

    def test_primary_fallback(self):
        for _k, r in MODEL_ROUTING_RULES.items():
            assert "primary" in r and "fallback" in r


class TestPhaseOrder:
    def test_five(self):
        assert len(PHASE_ORDER) == 5

    def test_starts_plan(self):
        assert PHASE_ORDER[0] == ResearchPhase.PLAN

    def test_ends_review(self):
        assert PHASE_ORDER[-1] == ResearchPhase.REVIEW


class TestMisc:
    def test_paper_sections(self):
        assert "abstract" in PAPER_SECTIONS and "methodology" in PAPER_SECTIONS

    def test_data_formats(self):
        assert "csv" in SUPPORTED_DATA_FORMATS

    def test_figure_formats(self):
        assert "pdf" in SUPPORTED_FIGURE_FORMATS

    def test_embedding_dims(self):
        assert DEFAULT_EMBEDDING_DIMENSIONS > 0

    def test_chunk_sizes(self):
        assert CHUNK_SIZE_TOKENS > CHUNK_OVERLAP_TOKENS

    def test_tools_per_phase(self):
        assert MAX_TOOLS_PER_PHASE > 0

    def test_cache_ttl(self):
        assert "semantic_scholar" in CACHE_TTL

    def test_methodologies(self):
        assert "panel_data" in SUPPORTED_METHODOLOGIES
