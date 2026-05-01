"""Generate all 20 comprehensive test files."""
import os
import sys

TESTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests")

def write_file(name, content):
    path = os.path.join(TESTS_DIR, name)
    with open(path, "w") as f:
        f.write(content.lstrip("\n"))
    print(f"  {name}: {os.path.getsize(path)} bytes")

# Only create files that don't exist or are too small
def needs_create(name):
    path = os.path.join(TESTS_DIR, name)
    return not os.path.exists(path) or os.path.getsize(path) < 200

print("Creating test files...")

if needs_create("test_research_constants.py"):
    write_file("test_research_constants.py", """
\"\"\"Tests for mini_agent.research.constants.\"\"\"
from mini_agent.research.constants import (APA_DATE_FORMAT, CACHE_TTL, CHUNK_OVERLAP_TOKENS, CHUNK_SIZE_TOKENS,
    DEFAULT_EMBEDDING_DIMENSIONS, DEFAULT_MAX_STEPS, DEFAULT_TEMPLATE, DEFAULT_TOKEN_LIMIT, JOURNAL_TEMPLATES,
    MAX_TOOLS_PER_PHASE, MODEL_ROUTING_RULES, PAPER_SECTIONS, PHASE_ORDER, QUALITY_GATE_THRESHOLDS,
    RESEARCH_VERSION, SUPPORTED_DATA_FORMATS, SUPPORTED_FIGURE_FORMATS, SUPPORTED_METHODOLOGIES,
    SUPPORTED_TEMPLATES, WORKSPACE_DIRS)
from mini_agent.research.project_state import ResearchPhase
class TestVersion:
    def test_is_string(self): assert isinstance(RESEARCH_VERSION, str) and "." in RESEARCH_VERSION
    def test_token_limit(self): assert DEFAULT_TOKEN_LIMIT > 0
    def test_max_steps(self): assert DEFAULT_MAX_STEPS > 0
class TestTemplates:
    def test_non_empty(self): assert len(SUPPORTED_TEMPLATES) > 0
    def test_default_in_list(self): assert DEFAULT_TEMPLATE in SUPPORTED_TEMPLATES
    def test_all_strings(self): assert all(isinstance(t, str) for t in SUPPORTED_TEMPLATES)
    def test_journal_match(self):
        for t in SUPPORTED_TEMPLATES: assert t in JOURNAL_TEMPLATES
class TestWorkspace:
    def test_data_raw(self): assert "data/raw" in WORKSPACE_DIRS
    def test_writing_sections(self): assert "writing/sections" in WORKSPACE_DIRS
    def test_checkpoints(self): assert "checkpoints" in WORKSPACE_DIRS
    def test_sessions(self): assert ".sessions" in WORKSPACE_DIRS
class TestRouting:
    def test_planning(self): assert "planning" in MODEL_ROUTING_RULES
    def test_writing(self): assert "writing" in MODEL_ROUTING_RULES
    def test_embedding(self): assert "embedding" in MODEL_ROUTING_RULES
    def test_primary_fallback(self):
        for k, r in MODEL_ROUTING_RULES.items(): assert "primary" in r and "fallback" in r
class TestPhaseOrder:
    def test_five(self): assert len(PHASE_ORDER) == 5
    def test_starts_plan(self): assert PHASE_ORDER[0] == ResearchPhase.PLAN
    def test_ends_review(self): assert PHASE_ORDER[-1] == ResearchPhase.REVIEW
class TestMisc:
    def test_paper_sections(self): assert "abstract" in PAPER_SECTIONS and "methodology" in PAPER_SECTIONS
    def test_data_formats(self): assert "csv" in SUPPORTED_DATA_FORMATS
    def test_figure_formats(self): assert "pdf" in SUPPORTED_FIGURE_FORMATS
    def test_embedding_dims(self): assert DEFAULT_EMBEDDING_DIMENSIONS > 0
    def test_chunk_sizes(self): assert CHUNK_SIZE_TOKENS > CHUNK_OVERLAP_TOKENS
    def test_tools_per_phase(self): assert MAX_TOOLS_PER_PHASE > 0
    def test_cache_ttl(self): assert "semantic_scholar" in CACHE_TTL
    def test_methodologies(self): assert "panel_data" in SUPPORTED_METHODOLOGIES
""")

if needs_create("test_tool_registry.py"):
    write_file("test_tool_registry.py", """
\"\"\"Tests for mini_agent.research.tool_registry.\"\"\"
from __future__ import annotations
import pytest
from mini_agent.research.project_state import ResearchPhase
from mini_agent.research.tool_registry import ToolRegistry
from mini_agent.tools.base import Tool, ToolResult

class _Stub(Tool):
    def __init__(self, n): self._name = n
    @property
    def name(self): return self._name
    @property
    def description(self): return f"Stub: {self._name}"
    @property
    def parameters(self): return {"type": "object", "properties": {}}
    async def execute(self, **kw): return ToolResult(success=True, content="ok")

@pytest.fixture
def reg(): return ToolRegistry()

class TestRegister:
    def test_adds(self, reg):
        reg.register(_Stub("p"), phases=["plan"]); assert reg.tool_count == 1
    def test_core_when_no_phases(self, reg):
        reg.register(_Stub("c")); assert reg.get_tool_by_name("c") is not None
        assert "c" in reg.list_all()["core"]
    def test_multi_phases(self, reg):
        reg.register(_Stub("p"), phases=["plan", "collect"])
        assert any(t.name == "p" for t in reg.get_tools_for_phase("plan"))
        assert any(t.name == "p" for t in reg.get_tools_for_phase("collect"))

class TestCore:
    def test_always_available(self, reg):
        reg.register(_Stub("c")); reg.register(_Stub("p"), phases=["plan"])
        for ph in ["plan", "collect", "analyze", "write", "review"]:
            assert "c" in [t.name for t in reg.get_tools_for_phase(ph)]
    def test_first(self, reg):
        reg.register(_Stub("c")); reg.register(_Stub("p"), phases=["plan"])
        assert reg.get_tools_for_phase("plan")[0].name == "c"

class TestPhaseTools:
    def test_correct(self, reg):
        reg.register(_Stub("p"), phases=["plan"]); reg.register(_Stub("a"), phases=["analyze"])
        assert len(reg.get_tools_for_phase("plan")) == 1
    def test_no_dupes(self, reg):
        reg.register(_Stub("c")); reg.register(_Stub("c"), phases=["plan"])
        assert [t.name for t in reg.get_tools_for_phase("plan")].count("c") == 1
    def test_empty(self, reg): assert reg.get_tools_for_phase("review") == []

class TestGetTool:
    def test_found(self, reg):
        t = _Stub("p"); reg.register(t, phases=["plan"]); assert reg.get_tool_by_name("p") is t
    def test_not_found(self, reg): assert reg.get_tool_by_name("x") is None

class TestUnregister:
    def test_removes(self, reg):
        reg.register(_Stub("p"), phases=["plan"]); reg.unregister("p")
        assert reg.get_tool_by_name("p") is None and reg.tool_count == 0
    def test_safe(self, reg): reg.unregister("x")

class TestLoadUnload:
    def test_load(self, reg):
        reg.register(_Stub("p"), phases=["plan"]); assert len(reg.load_phase("plan")) == 1
    def test_unload(self, reg): reg.unload_phase("plan")

class TestIntrospection:
    def test_list_all(self, reg):
        reg.register(_Stub("c")); reg.register(_Stub("p"), phases=["plan"])
        l = reg.list_all(); assert "c" in l["core"] and "p" in l["plan"]
    def test_count(self, reg):
        reg.register(_Stub("c")); reg.register(_Stub("p"), phases=["plan"]); reg.register(_Stub("a"), phases=["analyze"])
        assert reg.tool_count == 3
    def test_phase_count(self, reg):
        reg.register(_Stub("c")); reg.register(_Stub("p"), phases=["plan"])
        assert reg.get_phase_tool_count("plan") == 2
""")

# For the remaining files that need complex content, read from existing if available
for fname in ["test_analysis_tools.py", "test_writing_tools.py", "test_quality_tools.py",
              "test_knowledge_tools.py", "test_document_tools.py", "test_writing_engine.py",
              "test_quality_engine.py", "test_llm_gateway.py", "test_dspy_modules.py",
              "test_research_integration.py"]:
    path = os.path.join(TESTS_DIR, fname)
    if not os.path.exists(path) or os.path.getsize(path) < 200:
        print(f"  NEEDS: {fname}")

print("Done!")
