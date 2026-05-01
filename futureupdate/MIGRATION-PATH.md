# BPS Stat Agent v0.2.0 → Academic Research Agent v1.0: Migration Path

**Version:** 1.0  
**Created:** 2025-07-15  
**Status:** Definitive Implementation Guide  
**Principle:** ADDITIVE changes only — existing functionality MUST keep working at every step

---

## Table of Contents

1. [Part 1: Files That DO NOT CHANGE](#part-1-files-that-do-not-change)
2. [Part 2: Files That Get MODIFIED](#part-2-files-that-get-modified-with-exact-diffs)
3. [Part 3: NEW Files to Create](#part-3-new-files-to-create-in-dependency-order)
4. [Part 4: Configuration Files to Add](#part-4-configuration-files-to-add)
5. [Part 5: Incremental Migration Steps](#part-5-incremental-migration-steps)
6. [Part 6: Backward Compatibility Verification](#part-6-backward-compatibility-verification)
7. [Part 7: Version Checkpoints](#part-7-version-checkpoints)

---

## Part 1: Files That DO NOT CHANGE

These files remain **100% untouched**. Zero modifications.

### Core BPS Modules (Business Logic)

| # | File | Purpose | Lines |
|---|------|---------|-------|
| 1 | `mini_agent/bps_api.py` | BPS WebAPI client (HTTP calls to BPS) | ~400 |
| 2 | `mini_agent/bps_mcp_server.py` | MCP server exposing 62 BPS tools | ~600 |
| 3 | `mini_agent/bps_orchestrator.py` | BPS query orchestration logic | ~350 |
| 4 | `mini_agent/bps_data_retriever.py` | Data retrieval from BPS endpoints | ~300 |
| 5 | `mini_agent/bps_resource_retriever.py` | Resource retrieval (publications, tables) | ~250 |
| 6 | `mini_agent/bps_normalization.py` | Data normalization utilities | ~200 |
| 7 | `mini_agent/bps_models.py` | Pydantic models for BPS data | ~150 |
| 8 | `mini_agent/bps_resolution.py` | Domain/variable resolution logic | ~300 |
| 9 | `mini_agent/allstats_client.py` | AllStats search engine client | ~200 |

### Agent Core (Unchanged)

| # | File | Purpose | Lines |
|---|------|---------|-------|
| 10 | `mini_agent/agent.py` | Core agent loop (step/execute/summarize) | ~567 |
| 11 | `mini_agent/tools/base.py` | Tool ABC + ToolResult model | 55 |
| 12 | `mini_agent/tools/bash_tool.py` | BashTool, BashOutputTool, BashKillTool | ~200 |
| 13 | `mini_agent/tools/file_tools.py` | ReadTool, WriteTool, EditTool | ~300 |
| 14 | `mini_agent/tools/note_tool.py` | SessionNoteTool, RecallNoteTool | ~100 |
| 15 | `mini_agent/tools/skill_tool.py` | Skill execution tool | ~150 |
| 16 | `mini_agent/tools/skill_loader.py` | Skill discovery and loading | ~200 |
| 17 | `mini_agent/tools/mcp_loader.py` | MCP server connection + tool loading | ~250 |
| 18 | `mini_agent/tools/__init__.py` | Tools package init | ~10 |

### LLM Layer (Unchanged)

| # | File | Purpose | Lines |
|---|------|---------|-------|
| 19 | `mini_agent/llm/__init__.py` | LLM package init (re-exports LLMClient) | ~5 |
| 20 | `mini_agent/llm/base.py` | LLMClientBase ABC | ~50 |
| 21 | `mini_agent/llm/anthropic_client.py` | Anthropic API client | ~200 |
| 22 | `mini_agent/llm/openai_client.py` | OpenAI-compatible API client | ~200 |

### Infrastructure (Unchanged)

| # | File | Purpose | Lines |
|---|------|---------|-------|
| 23 | `mini_agent/retry.py` | Retry logic with exponential backoff | ~100 |
| 24 | `mini_agent/logger.py` | AgentLogger class | ~100 |
| 25 | `mini_agent/logging_config.py` | Logging configuration | ~50 |
| 26 | `mini_agent/colors.py` | Terminal color constants | ~50 |
| 27 | `mini_agent/metrics.py` | Prometheus metrics definitions | ~80 |
| 28 | `mini_agent/tracing.py` | OpenTelemetry tracing | ~100 |
| 29 | `mini_agent/health.py` | Health check endpoint | ~50 |
| 30 | `mini_agent/setup_wizard.py` | First-run configuration wizard | ~200 |
| 31 | `mini_agent/utils/__init__.py` | Utility functions | ~30 |
| 32 | `mini_agent/utils/terminal_utils.py` | Terminal width utilities | ~50 |
| 33 | `mini_agent/schema/__init__.py` | Schema package init | ~10 |
| 34 | `mini_agent/schema/schema.py` | LLMProvider, Message, ToolCall models | 55 |

### ACP Server (Unchanged)

| # | File | Purpose | Lines |
|---|------|---------|-------|
| 35 | `mini_agent/acp/__init__.py` | ACP package (Agent Communication Protocol) | ~100 |
| 36 | `mini_agent/acp/server.py` | ACP server entry point | 6 |

### Skills (Unchanged — all subdirectories)

| # | Directory | Purpose |
|---|-----------|---------|
| 37 | `mini_agent/skills/bps-master/` | BPS data query skill |
| 38 | `mini_agent/skills/document-skills/` | PDF, DOCX, PPTX, XLSX skills |
| 39 | `mini_agent/skills/slack-gif-creator/` | GIF creation skill |
| 40 | `mini_agent/skills/skill-creator/` | Skill authoring tool |
| 41 | `mini_agent/skills/mcp-builder/` | MCP server builder |
| 42 | `mini_agent/skills/webapp-testing/` | Web app testing skill |

### Tests (Unchanged — all 36 existing test files)

All files in `tests/` remain untouched. New tests go in `tests/research/`.

### Other (Unchanged)

| # | File | Purpose |
|---|------|---------|
| 43 | `Makefile` | Build commands |
| 44 | `Dockerfile` | Container build |
| 45 | `docker-compose.yml` | Service orchestration |
| 46 | `ruff.toml` | Linter config |
| 47 | `.gitignore` | Git ignore rules |
| 48 | `CHANGELOG.md` | Release notes (append-only) |
| 49 | `LICENSE` | MIT license |

---

## Part 2: Files That Get MODIFIED (with exact diffs)

### 2.1 `pyproject.toml`

**What changes:** Add optional dependency groups for research features + new entry points.  
**Why:** Research deps are heavy (~2GB); must be opt-in. Existing `pip install bps-stat-agent` stays lean.

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -2,7 +2,7 @@
 name = "bps-stat-agent"
-version = "0.2.0"
+version = "0.3.0"
 description = "BPS Indonesia Statistical Data Agent - Search and query BPS data via AllStats Search Engine and WebAPI"
 
@@ -40,6 +40,8 @@
 [project.scripts]
 bps-stat-agent = "mini_agent.cli:main"
 bpsagent = "mini_agent.cli:main"
 bps-stat-agent-acp = "mini_agent.acp.server:main"
 bps-mcp-server = "mini_agent.bps_mcp_server:main"
+bpsagent-research = "mini_agent.research.cli_entry:main"
+bps-research-mcp = "mini_agent.research.mcp_server:main"
 
 [project.optional-dependencies]
@@ -46,6 +48,52 @@
 dev = [
     "pytest>=9.0.3",
     "pytest-asyncio>=1.2.0",
 ]
+research-core = [
+    "litellm>=1.40.0",
+    "dspy>=2.5.0",
+    "lancedb>=0.9.0",
+    "chonkie>=0.4.0",
+    "great-expectations>=0.18.0",
+    "pandera>=0.20.0",
+]
+research-analysis = [
+    "bps-stat-agent[research-core]",
+    "statsmodels>=0.14.0",
+    "scipy>=1.11.0",
+    "linearmodels>=6.0.0",
+    "arch>=7.0.0",
+    "pingouin>=0.5.4",
+    "pandasai>=2.0.0",
+    "ydata-profiling>=4.6.0",
+    "scikit-learn>=1.3.0",
+    "matplotlib>=3.8.0",
+    "seaborn>=0.13.0",
+]
+research-bayesian = [
+    "bps-stat-agent[research-analysis]",
+    "pymc>=5.0.0",
+    "bambi>=0.14.0",
+    "arviz>=0.18.0",
+    "dowhy>=0.11.0",
+    "lifelines>=0.29.0",
+]
+research-rag = [
+    "bps-stat-agent[research-core]",
+    "paper-qa>=5.0.0",
+    "lightrag-hku>=1.5.0",
+    "sentence-transformers>=3.0.0",
+    "scispacy>=0.5.0",
+    "spacy>=3.7.0",
+    "networkx>=3.2.0",
+]
+research-writing = [
+    "bps-stat-agent[research-core]",
+    "pylatex>=1.4.2",
+    "python-docx>=1.2.0",
+    "citeproc-py>=0.9.0",
+    "bibtexparser>=1.4.0",
+    "pypandoc>=1.13.0",
+    "habanero>=2.3.0",
+]
+research-full = [
+    "bps-stat-agent[research-core]",
+    "bps-stat-agent[research-analysis]",
+    "bps-stat-agent[research-bayesian]",
+    "bps-stat-agent[research-rag]",
+    "bps-stat-agent[research-writing]",
+]
 metrics = [
     "prometheus-client>=0.20.0",
 ]
```

**Existing behavior preserved:** `pip install bps-stat-agent` installs ONLY the base deps (same as before).

---

### 2.2 `mini_agent/__init__.py`

**What changes:** Bump version, add conditional research import.  
**Why:** Version bump signals new capabilities; lazy import avoids import errors when research deps not installed.

```diff
--- a/mini_agent/__init__.py
+++ b/mini_agent/__init__.py
@@ -1,4 +1,4 @@
-"""BPS Stat Agent - BPS Indonesia Statistical Data Agent with 62 MCP tools."""
+"""BPS Stat Agent - BPS Indonesia Statistical Data Agent with 62 MCP tools + Academic Research capabilities."""
 
 from .agent import Agent
 from .bps_models import BPSResolvedResource, BPSResourceType
@@ -6,7 +6,17 @@
 from .schema import FunctionCall, LLMProvider, LLMResponse, Message, ToolCall
 
-__version__ = "0.2.0"
+__version__ = "0.3.0"
+
+# Lazy import for research module (only available with research-core extras)
+def get_research_orchestrator():
+    """Get ResearchOrchestrator (requires research-core extras)."""
+    try:
+        from .research.orchestrator import ResearchOrchestrator
+        return ResearchOrchestrator
+    except ImportError as e:
+        raise ImportError(
+            "Research features require extra dependencies. "
+            "Install with: pip install bps-stat-agent[research-full]"
+        ) from e
 
 __all__ = [
     "Agent",
@@ -17,4 +27,5 @@
     "LLMResponse",
     "ToolCall",
     "FunctionCall",
+    "get_research_orchestrator",
 ]
```

---

### 2.3 `mini_agent/cli.py`

**What changes:** Add `research` subcommand that delegates to research CLI.  
**Why:** Users can run `bpsagent research "topic"` to start research mode.

```diff
--- a/mini_agent/cli.py
+++ b/mini_agent/cli.py
@@ -13,6 +13,7 @@
 import argparse
 import asyncio
 import platform
+import importlib
 import subprocess
 import sys
 import threading
@@ -44,6 +45,12 @@
 def get_log_directory() -> Path:
     """Get the log directory path."""
     return Path.home() / ".bps-stat-agent" / "log"
+
+
+def _launch_research_mode(args: argparse.Namespace) -> None:
+    """Launch research mode (requires research-core extras)."""
+    research_cli = importlib.import_module("mini_agent.research.cli_entry")
+    research_cli.main_from_parent(args)
```

In the `main()` function's argument parser section, ADD:

```diff
+    # Research subcommand (only if research extras installed)
+    subparsers = parser.add_subparsers(dest="subcommand")
+    research_parser = subparsers.add_parser(
+        "research",
+        help="Start academic research mode (requires: pip install bps-stat-agent[research-full])"
+    )
+    research_parser.add_argument("topic", nargs="?", help="Research topic or question")
+    research_parser.add_argument("--resume", type=str, help="Resume project from path")
+    research_parser.add_argument("--phase", type=str, help="Start at specific phase")
+    research_parser.add_argument("--config", type=str, help="Research config YAML path")
```

In the `main()` function's dispatch section, ADD before the existing interactive/task logic:

```diff
+    # Handle research subcommand
+    if args.subcommand == "research":
+        try:
+            _launch_research_mode(args)
+        except ImportError:
+            print(f"{Colors.RED}Error: Research features not installed.{Colors.RESET}")
+            print(f"Install with: pip install bps-stat-agent[research-full]")
+            sys.exit(1)
+        return
+
     # Existing interactive/task logic continues unchanged...
```

**Existing behavior preserved:** Running `bpsagent` or `bpsagent --task "..."` follows the EXACT same code path as before. The `research` subcommand is only triggered by explicit `bpsagent research`.

---

### 2.4 `mini_agent/config.py`

**What changes:** Add `ResearchConfig` model (optional field on `Config`).  
**Why:** Research settings need a home; making it Optional means existing configs work without changes.

```diff
--- a/mini_agent/config.py
+++ b/mini_agent/config.py
@@ -8,6 +8,7 @@
 from pathlib import Path
 from typing import ClassVar, Literal
+from typing import Optional
 
 import yaml
 from dotenv import load_dotenv
@@ -78,6 +79,30 @@
     enable_mcp: bool = True
     mcp_config_path: str = "mcp.json"
     mcp: MCPConfig = Field(default_factory=MCPConfig)
+
+
+class ResearchConfig(BaseModel):
+    """Research mode configuration (optional — only used with research extras)"""
+
+    # LLM routing
+    primary_model: str = "claude-sonnet-4-20250514"
+    fallback_model: str = "gpt-4o"
+    embedding_model: str = "nomic-embed-text"
+    max_cost_per_project: float = 50.0  # USD
+
+    # Phase settings
+    max_tools_per_phase: int = 15
+    auto_phase_transition: bool = False  # Require human approval
+
+    # Workspace
+    default_workspace: str = "./research-workspace"
+    template: str = "imrad"  # imrad | thesis | report
+
+    # Sandbox
+    sandbox_backend: str = "docker"  # docker | e2b
+    sandbox_timeout: int = 120  # seconds
+    sandbox_memory_mb: int = 2048
+
+    # Quality gates
+    min_citation_confidence: float = 0.85
+    require_peer_review: bool = True
 
 
 class Config(BaseModel):
@@ -85,6 +110,7 @@
     llm: LLMConfig
     agent: AgentConfig
     tools: ToolsConfig
     logging: LoggingConfig = Field(default_factory=LoggingConfig)
     tracing: TracingConfig = Field(default_factory=TracingConfig)
+    research: Optional[ResearchConfig] = None  # Only populated when research mode active
```

In `Config.from_yaml()`, ADD after tracing config parsing:

```diff
+        # Parse research configuration (optional)
+        research_data = data.get("research", None)
+        research_config = None
+        if research_data:
+            research_config = ResearchConfig(**research_data)
+
         return cls(
             llm=llm_config,
             agent=agent_config,
             tools=tools_config,
             logging=logging_config,
             tracing=tracing_config,
+            research=research_config,
         )
```

**Existing behavior preserved:** If `research:` key is absent from config.yaml (which it will be for all existing users), `config.research` is `None`. Zero impact on existing code paths.

---

### 2.5 `mini_agent/llm/llm_wrapper.py`

**What changes:** Add LiteLLM as optional third backend.  
**Why:** Research mode needs multi-provider routing (Claude + GPT-4 + Gemini + local models).

```diff
--- a/mini_agent/llm/llm_wrapper.py
+++ b/mini_agent/llm/llm_wrapper.py
@@ -14,6 +14,16 @@
 
 logger = logging.getLogger(__name__)
 
+# Lazy import for LiteLLM (only available with research-core extras)
+_litellm_available = None
+
+def _check_litellm():
+    global _litellm_available
+    if _litellm_available is None:
+        try:
+            import litellm  # noqa: F401
+            _litellm_available = True
+        except ImportError:
+            _litellm_available = False
+    return _litellm_available
+
 
 class LLMClient:
     """LLM Client wrapper supporting multiple providers.
@@ -31,6 +41,9 @@
     For third-party APIs, it uses the api_base as-is.
+
+    When provider is "litellm", delegates to LiteLLM for multi-provider
+    routing with automatic fallback and cost tracking.
     """
```

In `__init__`, ADD a new branch:

```diff
+        # LiteLLM provider (research mode)
+        if provider == LLMProvider.LITELLM if hasattr(LLMProvider, 'LITELLM') else False:
+            if not _check_litellm():
+                raise ImportError(
+                    "LiteLLM not installed. Install with: pip install bps-stat-agent[research-core]"
+                )
+            from .litellm_client import LiteLLMClient
+            self._client = LiteLLMClient(
+                api_key=api_key,
+                model=model or self.DEFAULT_MODEL,
+                retry_config=retry_config,
+            )
+            return
```

**Existing behavior preserved:** The LiteLLM branch is ONLY entered when `provider="litellm"`. Existing `anthropic`/`openai` providers follow the exact same code path.

---

### 2.6 `mini_agent/schema/schema.py`

**What changes:** Add `LITELLM` to `LLMProvider` enum.  
**Why:** Need a provider enum value for the new backend.

```diff
--- a/mini_agent/schema/schema.py
+++ b/mini_agent/schema/schema.py
@@ -9,6 +9,7 @@
 class LLMProvider(str, Enum):
     """LLM provider types."""
 
     ANTHROPIC = "anthropic"
     OPENAI = "openai"
+    LITELLM = "litellm"
```

**Existing behavior preserved:** Adding an enum value doesn't affect existing code that uses `ANTHROPIC` or `OPENAI`.

---

## Part 3: NEW Files to Create (in dependency order)

Files are ordered so that each file's dependencies are created BEFORE it.

### Layer 0: Package Structure

| # | File | Purpose | Deps | Key Exports | ~Lines |
|---|------|---------|------|-------------|--------|
| 1 | `mini_agent/research/__init__.py` | Package init with lazy imports | None | `ResearchOrchestrator`, `ProjectState` | 25 |
| 2 | `mini_agent/research/exceptions.py` | Custom exception hierarchy | None | `ResearchError`, `PhaseError`, `BudgetExceededError` | 40 |
| 3 | `mini_agent/research/constants.py` | Enums and constants | None | `Phase`, `ProjectStatus`, `PHASE_TOOL_LIMITS` | 60 |

### Layer 1: Data Models (no deps on other new files)

| # | File | Purpose | Deps | Key Classes | ~Lines |
|---|------|---------|------|-------------|--------|
| 4 | `mini_agent/research/models/project_state.py` | Project YAML schema + persistence | `constants`, `pydantic` | `ProjectState`, `PhaseRecord`, `Citation` | 200 |
| 5 | `mini_agent/research/models/decision_log.py` | Append-only research decision log | `pydantic` | `Decision`, `DecisionLog` | 80 |
| 6 | `mini_agent/research/models/cost_tracker.py` | LLM cost tracking model | `pydantic` | `CostEntry`, `CostTracker` | 100 |
| 7 | `mini_agent/research/models/__init__.py` | Models package init | models above | Re-exports | 15 |

### Layer 2: Infrastructure (depends on models)

| # | File | Purpose | Deps | Key Classes | ~Lines |
|---|------|---------|------|-------------|--------|
| 8 | `mini_agent/research/workspace.py` | Project directory scaffolding | `models.project_state` | `WorkspaceManager` | 150 |
| 9 | `mini_agent/research/session_resume.py` | Checkpoint/resume protocol | `models.project_state` | `SessionResumeManager` | 120 |
| 10 | `mini_agent/research/approval_gates.py` | Human-in-the-loop gates | `constants`, `prompt_toolkit` | `ApprovalGate`, `gate_required()` | 100 |
| 11 | `mini_agent/llm/litellm_client.py` | LiteLLM backend client | `llm.base`, `litellm` | `LiteLLMClient` | 180 |
| 12 | `mini_agent/research/llm_gateway.py` | Multi-model router with cost tracking | `litellm_client`, `models.cost_tracker` | `LLMGateway` | 200 |

### Layer 3: Phase System (depends on infrastructure)

| # | File | Purpose | Deps | Key Classes | ~Lines |
|---|------|---------|------|-------------|--------|
| 13 | `mini_agent/research/phase_manager.py` | Dynamic tool loading per phase | `constants`, `models.project_state`, `tools.mcp_loader` | `PhaseManager` | 250 |
| 14 | `mini_agent/research/tool_registry.py` | Registry of all research tools by phase | `constants`, `tools.base` | `ToolRegistry` | 150 |

### Layer 4: Analysis Engine (depends on phase system)

| # | File | Purpose | Deps | Key Classes | ~Lines |
|---|------|---------|------|-------------|--------|
| 15 | `mini_agent/research/analysis/__init__.py` | Analysis package init | None | Re-exports | 10 |
| 16 | `mini_agent/research/analysis/sandbox.py` | Docker/E2B code execution | `docker`, `models.project_state` | `SandboxExecutor` | 250 |
| 17 | `mini_agent/research/analysis/stats_tools.py` | Statistical analysis tools | `tools.base`, `sandbox` | `DescriptiveStatsTool`, `RegressionTool`, `HypothesisTestTool` | 400 |
| 18 | `mini_agent/research/analysis/viz_tools.py` | Visualization generation tools | `tools.base`, `sandbox` | `AutoVizTool`, `PublicationFigureTool` | 200 |
| 19 | `mini_agent/research/analysis/apa_formatter.py` | APA 7th edition stat formatting | None (pure logic) | `format_apa_stats()` | 150 |

### Layer 5: RAG & Literature (depends on infrastructure)

| # | File | Purpose | Deps | Key Classes | ~Lines |
|---|------|---------|------|-------------|--------|
| 20 | `mini_agent/research/literature/__init__.py` | Literature package init | None | Re-exports | 10 |
| 21 | `mini_agent/research/literature/paper_search.py` | Academic paper search tool | `tools.base`, `paper-qa` | `PaperSearchTool` | 200 |
| 22 | `mini_agent/research/literature/rag_engine.py` | Scientific RAG with PaperQA2 | `paper-qa`, `lancedb` | `RAGEngine` | 300 |
| 23 | `mini_agent/research/literature/citation_manager.py` | Citation tracking + verification | `habanero`, `bibtexparser` | `CitationManager` | 250 |
| 24 | `mini_agent/research/literature/knowledge_graph.py` | LightRAG knowledge graph | `lightrag-hku`, `networkx` | `KnowledgeGraphBuilder` | 200 |

### Layer 6: Paper Writing (depends on literature + analysis)

| # | File | Purpose | Deps | Key Classes | ~Lines |
|---|------|---------|------|-------------|--------|
| 25 | `mini_agent/research/writing/__init__.py` | Writing package init | None | Re-exports | 10 |
| 26 | `mini_agent/research/writing/section_writer.py` | Per-section writing with focused context | `tools.base`, `llm_gateway` | `SectionWriterTool` | 250 |
| 27 | `mini_agent/research/writing/latex_compiler.py` | LaTeX/Typst compilation | `subprocess`, `pylatex` | `LaTeXCompiler` | 200 |
| 28 | `mini_agent/research/writing/template_registry.py` | Paper templates (IMRaD, thesis, etc.) | `pathlib` | `TemplateRegistry` | 150 |
| 29 | `mini_agent/research/writing/bibliography.py` | BibTeX/CSL bibliography management | `citeproc-py`, `bibtexparser` | `BibliographyManager` | 200 |

### Layer 7: Quality Gate (depends on writing + literature)

| # | File | Purpose | Deps | Key Classes | ~Lines |
|---|------|---------|------|-------------|--------|
| 30 | `mini_agent/research/quality/__init__.py` | Quality package init | None | Re-exports | 10 |
| 31 | `mini_agent/research/quality/citation_verifier.py` | Verify all citations against APIs | `literature.citation_manager`, `habanero` | `CitationVerifier` | 200 |
| 32 | `mini_agent/research/quality/stat_validator.py` | Validate statistical claims | `analysis.stats_tools` | `StatisticalValidator` | 200 |
| 33 | `mini_agent/research/quality/writing_quality.py` | Grammar, style, readability checks | `subprocess` (LanguageTool) | `WritingQualityChecker` | 150 |
| 34 | `mini_agent/research/quality/peer_reviewer.py` | Adversarial peer review simulation | `llm_gateway` | `PeerReviewer` | 200 |

### Layer 8: DSPy Modules (depends on all above)

| # | File | Purpose | Deps | Key Classes | ~Lines |
|---|------|---------|------|-------------|--------|
| 35 | `mini_agent/research/dspy_modules/__init__.py` | DSPy package init | None | Re-exports | 10 |
| 36 | `mini_agent/research/dspy_modules/signatures.py` | Typed DSPy signatures for all phases | `dspy` | `ResearchPlanner`, `DataAnalyst`, `SectionWriter`, `Reviewer` | 150 |
| 37 | `mini_agent/research/dspy_modules/research_planner.py` | Plan research methodology | `dspy`, `signatures` | `ResearchPlannerModule` | 120 |
| 38 | `mini_agent/research/dspy_modules/data_analyst.py` | Analyze data with DSPy | `dspy`, `signatures` | `DataAnalystModule` | 120 |
| 39 | `mini_agent/research/dspy_modules/section_writer.py` | Write paper sections | `dspy`, `signatures` | `SectionWriterModule` | 120 |
| 40 | `mini_agent/research/dspy_modules/reviewer.py` | Review and critique | `dspy`, `signatures` | `ReviewerModule` | 120 |

### Layer 9: Orchestrator (depends on everything)

| # | File | Purpose | Deps | Key Classes | ~Lines |
|---|------|---------|------|-------------|--------|
| 41 | `mini_agent/research/orchestrator.py` | Main research orchestration loop | `phase_manager`, `llm_gateway`, `workspace`, all tools | `ResearchOrchestrator` | 400 |
| 42 | `mini_agent/research/sub_agents.py` | Sub-agent spawning (SectionWriter, Reviewer, etc.) | `agent.Agent`, `llm_gateway` | `SubAgentDispatcher` | 200 |

### Layer 10: Entry Points

| # | File | Purpose | Deps | Key Functions | ~Lines |
|---|------|---------|------|---------------|--------|
| 43 | `mini_agent/research/cli_entry.py` | Research CLI entry point | `orchestrator`, `argparse` | `main()`, `main_from_parent()` | 150 |
| 44 | `mini_agent/research/mcp_server.py` | Research MCP server (exposes research tools) | `mcp`, `tool_registry` | `main()` | 200 |

### Tests

| # | File | Purpose | ~Lines |
|---|------|---------|--------|
| 45 | `tests/research/__init__.py` | Test package init | 1 |
| 46 | `tests/research/test_project_state.py` | ProjectState YAML load/save | 100 |
| 47 | `tests/research/test_phase_manager.py` | Phase tool loading/limits | 120 |
| 48 | `tests/research/test_workspace.py` | Workspace scaffolding | 80 |
| 49 | `tests/research/test_cost_tracker.py` | Cost tracking accuracy | 60 |
| 50 | `tests/research/test_sandbox.py` | Sandbox execution | 100 |
| 51 | `tests/research/test_apa_formatter.py` | APA formatting correctness | 80 |
| 52 | `tests/research/test_citation_verifier.py` | Citation verification | 100 |
| 53 | `tests/research/test_orchestrator.py` | End-to-end orchestration | 200 |
| 54 | `tests/research/conftest.py` | Research test fixtures | 80 |

**Total new files: 54**  
**Total new lines: ~6,500**

---

## Part 4: Configuration Files to Add

### 4.1 `mini_agent/config/research_config.yaml`

```yaml
# Research Mode Configuration (default values)
# Copy to ~/.bps-stat-agent/config/research_config.yaml to customize

research:
  # LLM routing (via LiteLLM)
  primary_model: "claude-sonnet-4-20250514"
  fallback_model: "gpt-4o"
  embedding_model: "nomic-embed-text"
  max_cost_per_project: 50.0  # USD hard limit

  # Phase system
  max_tools_per_phase: 15
  auto_phase_transition: false  # true = skip human approval

  # Workspace
  default_workspace: "./research-workspace"
  template: "imrad"  # imrad | thesis | report | custom

  # Sandbox for code execution
  sandbox_backend: "docker"  # docker | e2b
  sandbox_timeout: 120
  sandbox_memory_mb: 2048

  # Quality gates
  min_citation_confidence: 0.85
  require_peer_review: true
  max_hallucination_rate: 0.0  # Zero tolerance

  # Data sources
  enable_bps: true  # Use existing BPS tools
  enable_academic_search: true
  enable_r_analysis: true
```

### 4.2 `mini_agent/config/mcp-research.json`

```json
{
  "$schema": "https://raw.githubusercontent.com/modelcontextprotocol/specification/main/schema/mcp-config.json",
  "_comment": "Research MCP servers — loaded ONLY in research mode, in addition to existing mcp.json",
  "mcpServers": {
    "paper-search": {
      "command": "npx",
      "args": ["-y", "@openags/paper-search-mcp"],
      "env": {}
    },
    "zotero": {
      "command": "npx",
      "args": ["-y", "zotero-mcp"],
      "env": {
        "ZOTERO_API_KEY": "${ZOTERO_API_KEY}",
        "ZOTERO_USER_ID": "${ZOTERO_USER_ID}"
      }
    },
    "overleaf": {
      "command": "npx",
      "args": ["-y", "overleaf-mcp"],
      "env": {
        "OVERLEAF_EMAIL": "${OVERLEAF_EMAIL}",
        "OVERLEAF_PASSWORD": "${OVERLEAF_PASSWORD}"
      }
    },
    "jupyter": {
      "command": "npx",
      "args": ["-y", "@datalayer/jupyter-mcp-server"],
      "env": {}
    },
    "rmcp": {
      "command": "npx",
      "args": ["-y", "rmcp"],
      "env": {}
    },
    "neo4j": {
      "command": "npx",
      "args": ["-y", "@neo4j/mcp-server"],
      "env": {
        "NEO4J_URI": "${NEO4J_URI:-bolt://localhost:7687}",
        "NEO4J_PASSWORD": "${NEO4J_PASSWORD}"
      }
    },
    "qdrant": {
      "command": "npx",
      "args": ["-y", "@qdrant/mcp-server-qdrant"],
      "env": {
        "QDRANT_URL": "${QDRANT_URL:-http://localhost:6333}"
      }
    },
    "markitdown": {
      "command": "npx",
      "args": ["-y", "markitdown-mcp"],
      "env": {}
    },
    "mcp-pdf": {
      "command": "uvx",
      "args": ["mcp-pdf"],
      "env": {}
    },
    "pubmed": {
      "command": "npx",
      "args": ["-y", "pubmed-search-mcp"],
      "env": {}
    }
  }
}
```

### 4.3 `mini_agent/config/system_prompt_research.md`

```markdown
You are an Academic Research AI Agent built on the BPS Stat Agent platform.

## Your Capabilities
- Search and retrieve Indonesian statistical data from BPS (62 tools)
- Search 22+ academic databases (Semantic Scholar, arXiv, PubMed, CrossRef, etc.)
- Execute Python/R code in sandboxed environments for statistical analysis
- Build knowledge graphs from literature
- Write publication-ready papers (LaTeX/Typst/DOCX)
- Verify citations against live APIs (zero hallucination policy)

## Current Phase: {current_phase}
## Available Tools: {tool_count} (phase-limited to max 15)

## Research Workflow
You follow a 5-phase research process:
1. PLAN — Define research question, methodology, variables
2. COLLECT — Gather data from BPS + literature from academic databases
3. ANALYZE — Run statistical analysis in sandbox, generate figures
4. WRITE — Draft paper sections with verified citations
5. REVIEW — Quality gates, peer review simulation, final checks

## Rules
1. NEVER fabricate citations — every reference must be verified against CrossRef/DOI
2. NEVER skip statistical assumptions checks before running tests
3. ALWAYS log decisions in the decision log with rationale
4. ALWAYS request human approval at methodology and interpretation gates
5. Format all statistics in APA 7th edition style
6. Keep reproducibility: log every computation with inputs + outputs + hash

## Project State
- Project: {project_name}
- Status: {project_status}
- Phase: {current_phase}
- Budget remaining: ${budget_remaining}
```

### 4.4 `Dockerfile.research`

```dockerfile
# Dockerfile.research — Sandbox for statistical code execution
# NOT a replacement for the main Dockerfile (which remains unchanged)

FROM python:3.11-slim

# System deps for scientific computing
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ gfortran \
    libopenblas-dev liblapack-dev \
    texlive-base texlive-latex-extra \
    r-base r-base-dev \
    && rm -rf /var/lib/apt/lists/*

# Python scientific stack
RUN pip install --no-cache-dir \
    numpy pandas scipy statsmodels scikit-learn \
    linearmodels arch pingouin \
    matplotlib seaborn \
    pymc bambi arviz \
    dowhy lifelines \
    ydata-profiling pandera great-expectations

# R packages for rmcp
RUN R -e "install.packages(c('tidyverse', 'lme4', 'survival', 'forecast'), repos='https://cran.r-project.org')"

# Security: no network, limited resources
# (enforced at docker run time, not in Dockerfile)

WORKDIR /workspace
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

### 4.5 `mini_agent/research/templates/` (directory with template files)

| File | Purpose |
|------|---------|
| `templates/imrad.yaml` | IMRaD paper structure template |
| `templates/thesis.yaml` | Thesis/dissertation template |
| `templates/report.yaml` | Technical report template |
| `templates/latex/article.tex` | LaTeX article template |
| `templates/latex/thesis.tex` | LaTeX thesis template |
| `templates/typst/article.typ` | Typst article template |

---

## Part 5: Incremental Migration Steps

Each step produces a **WORKING system**. Run the verification suite after each step.

---

### Step 1: Add research optional deps to pyproject.toml

**Files touched:** `pyproject.toml`  
**Change:** Add `research-core`, `research-analysis`, `research-bayesian`, `research-rag`, `research-writing`, `research-full` optional dependency groups.

```bash
# Test
pip install -e "."                    # ✅ Base install still works
pip install -e ".[research-core]"     # ✅ Core research deps install
python -c "import mini_agent"         # ✅ Import works
pytest tests/ -x                      # ✅ All 417 existing tests pass
```

---

### Step 2: Create research package skeleton

**Files created:**
- `mini_agent/research/__init__.py` (empty, just docstring)
- `mini_agent/research/exceptions.py`
- `mini_agent/research/constants.py`

```bash
# Test
python -c "import mini_agent.research"                    # ✅
python -c "from mini_agent.research.constants import Phase"  # ✅
python -c "from mini_agent.research.exceptions import ResearchError"  # ✅
pytest tests/ -x                                          # ✅ Existing tests pass
```

---

### Step 3: Create ProjectState model

**Files created:**
- `mini_agent/research/models/__init__.py`
- `mini_agent/research/models/project_state.py`

**Test file:** `tests/research/__init__.py`, `tests/research/test_project_state.py`

```bash
# Test
pytest tests/research/test_project_state.py -v  # ✅ YAML load/save/validate
pytest tests/ -x                                 # ✅ All existing tests pass
```

Key test cases:
- Create ProjectState → save to YAML → reload → assert equality
- Load from existing YAML file
- Validate phase transitions (PLAN→COLLECT→ANALYZE→WRITE→REVIEW)
- Reject invalid state (e.g., ANALYZE before COLLECT)

---

### Step 4: Create DecisionLog and CostTracker models

**Files created:**
- `mini_agent/research/models/decision_log.py`
- `mini_agent/research/models/cost_tracker.py`

```bash
# Test
pytest tests/research/test_cost_tracker.py -v  # ✅
python -c "from mini_agent.research.models import ProjectState, DecisionLog, CostTracker"  # ✅
pytest tests/ -x                                # ✅ Existing tests pass
```

---

### Step 5: Create WorkspaceManager

**Files created:**
- `mini_agent/research/workspace.py`

```bash
# Test
pytest tests/research/test_workspace.py -v  # ✅ Creates IMRaD directory structure
# Verify structure:
# research-workspace/
# ├── project.yaml
# ├── data/raw/
# ├── data/processed/
# ├── literature/
# ├── analysis/
# ├── figures/
# ├── paper/
# ├── references.bib
# └── decision_log.jsonl
pytest tests/ -x                             # ✅ Existing tests pass
```

---

### Step 6: Create ApprovalGates

**Files created:**
- `mini_agent/research/approval_gates.py`

```bash
# Test (with mock stdin)
pytest tests/research/test_approval_gates.py -v  # ✅
pytest tests/ -x                                  # ✅ Existing tests pass
```

---

### Step 7: Create SessionResumeManager

**Files created:**
- `mini_agent/research/session_resume.py`

```bash
# Test
pytest tests/research/test_session_resume.py -v  # ✅ Save checkpoint → resume
pytest tests/ -x                                  # ✅ Existing tests pass
```

---

### Step 8: Add LITELLM to LLMProvider enum

**Files modified:** `mini_agent/schema/schema.py`  
**Change:** Add `LITELLM = "litellm"` to enum.

```bash
# Test
python -c "from mini_agent.schema import LLMProvider; assert LLMProvider.LITELLM == 'litellm'"  # ✅
pytest tests/ -x  # ✅ Existing tests pass (enum addition is backward-compatible)
```

---

### Step 9: Create LiteLLM client

**Files created:**
- `mini_agent/llm/litellm_client.py`

**Files modified:** `mini_agent/llm/llm_wrapper.py` (add litellm branch)

```bash
# Test (requires research-core extras)
pip install -e ".[research-core]"
pytest tests/research/test_litellm_client.py -v  # ✅ (mocked LiteLLM calls)
pytest tests/ -x                                  # ✅ Existing tests pass
# Verify existing providers still work:
pytest tests/test_llm.py tests/test_llm_clients.py -v  # ✅
```

---

### Step 10: Create LLMGateway (multi-model router)

**Files created:**
- `mini_agent/research/llm_gateway.py`

```bash
# Test
pytest tests/research/test_llm_gateway.py -v  # ✅ Routes to correct model, tracks cost
pytest tests/ -x                               # ✅ Existing tests pass
```

---

### Step 11: Create PhaseManager

**Files created:**
- `mini_agent/research/phase_manager.py`
- `mini_agent/research/tool_registry.py`

```bash
# Test
pytest tests/research/test_phase_manager.py -v  # ✅ Tool loading per phase, max 15 limit
pytest tests/ -x                                 # ✅ Existing tests pass
```

Key test cases:
- PLAN phase loads exactly 5 planning tools
- COLLECT phase loads BPS tools + paper-search tools (≤18, paginated)
- ANALYZE phase loads stats tools (≤15)
- Phase transition updates available tools
- Tool count never exceeds `max_tools_per_phase`

---

### Step 12: Add ResearchConfig to Config

**Files modified:** `mini_agent/config.py`  
**Change:** Add `ResearchConfig` class + optional field on `Config`.

```bash
# Test
pytest tests/test_config_bps.py -v  # ✅ Existing config tests pass
python -c "
from mini_agent.config import Config, ResearchConfig
# Existing config without research section still works:
# (uses the existing test config fixture)
"
pytest tests/ -x  # ✅ All existing tests pass
```

---

### Step 13: Add research config files

**Files created:**
- `mini_agent/config/research_config.yaml`
- `mini_agent/config/mcp-research.json`
- `mini_agent/config/system_prompt_research.md`

```bash
# Test
python -c "
import yaml
from pathlib import Path
config = yaml.safe_load(Path('mini_agent/config/research_config.yaml').read_text())
assert 'research' in config
assert config['research']['primary_model'] == 'claude-sonnet-4-20250514'
"  # ✅
pytest tests/ -x  # ✅ Existing tests pass
```

---

### Step 14: Create sandbox executor

**Files created:**
- `mini_agent/research/analysis/__init__.py`
- `mini_agent/research/analysis/sandbox.py`

```bash
# Test (requires Docker)
pytest tests/research/test_sandbox.py -v  # ✅ Execute Python code in container
pytest tests/ -x                           # ✅ Existing tests pass
```

---

### Step 15: Create APA formatter

**Files created:**
- `mini_agent/research/analysis/apa_formatter.py`

```bash
# Test (pure logic, no external deps)
pytest tests/research/test_apa_formatter.py -v  # ✅
# Example: format_apa_stats("F", df1=2, df2=47, value=3.45, p=0.039)
# → "F(2, 47) = 3.45, p = .039"
pytest tests/ -x  # ✅ Existing tests pass
```

---

### Step 16: Create statistical analysis tools

**Files created:**
- `mini_agent/research/analysis/stats_tools.py`
- `mini_agent/research/analysis/viz_tools.py`

```bash
# Test
pytest tests/research/test_stats_tools.py -v  # ✅ (mocked sandbox)
pytest tests/ -x                               # ✅ Existing tests pass
```

---

### Step 17: Create literature search tools

**Files created:**
- `mini_agent/research/literature/__init__.py`
- `mini_agent/research/literature/paper_search.py`

```bash
# Test
pytest tests/research/test_paper_search.py -v  # ✅ (mocked API calls)
pytest tests/ -x                                # ✅ Existing tests pass
```

---

### Step 18: Create RAG engine

**Files created:**
- `mini_agent/research/literature/rag_engine.py`

```bash
# Test
pytest tests/research/test_rag_engine.py -v  # ✅ (mocked embeddings + vector store)
pytest tests/ -x                              # ✅ Existing tests pass
```

---

### Step 19: Create citation manager

**Files created:**
- `mini_agent/research/literature/citation_manager.py`

```bash
# Test
pytest tests/research/test_citation_manager.py -v  # ✅ BibTeX parse, DOI lookup (mocked)
pytest tests/ -x                                    # ✅ Existing tests pass
```

---

### Step 20: Create knowledge graph builder

**Files created:**
- `mini_agent/research/literature/knowledge_graph.py`

```bash
# Test
pytest tests/research/test_knowledge_graph.py -v  # ✅
pytest tests/ -x                                   # ✅ Existing tests pass
```

---

### Step 21: Create paper writing tools

**Files created:**
- `mini_agent/research/writing/__init__.py`
- `mini_agent/research/writing/section_writer.py`
- `mini_agent/research/writing/template_registry.py`
- `mini_agent/research/writing/bibliography.py`

```bash
# Test
pytest tests/research/test_section_writer.py -v  # ✅
pytest tests/ -x                                  # ✅ Existing tests pass
```

---

### Step 22: Create LaTeX/Typst compiler

**Files created:**
- `mini_agent/research/writing/latex_compiler.py`
- `mini_agent/research/templates/` (all template files)

```bash
# Test
pytest tests/research/test_latex_compiler.py -v  # ✅ (requires texlive or typst)
pytest tests/ -x                                  # ✅ Existing tests pass
```

---

### Step 23: Create quality gate — citation verifier

**Files created:**
- `mini_agent/research/quality/__init__.py`
- `mini_agent/research/quality/citation_verifier.py`

```bash
# Test
pytest tests/research/test_citation_verifier.py -v  # ✅ (mocked CrossRef API)
pytest tests/ -x                                     # ✅ Existing tests pass
```

---

### Step 24: Create quality gate — statistical validator

**Files created:**
- `mini_agent/research/quality/stat_validator.py`

```bash
# Test
pytest tests/research/test_stat_validator.py -v  # ✅
pytest tests/ -x                                  # ✅ Existing tests pass
```

---

### Step 25: Create quality gate — writing quality + peer reviewer

**Files created:**
- `mini_agent/research/quality/writing_quality.py`
- `mini_agent/research/quality/peer_reviewer.py`

```bash
# Test
pytest tests/research/test_peer_reviewer.py -v  # ✅ (mocked LLM)
pytest tests/ -x                                 # ✅ Existing tests pass
```

---

### Step 26: Create DSPy modules

**Files created:**
- `mini_agent/research/dspy_modules/__init__.py`
- `mini_agent/research/dspy_modules/signatures.py`
- `mini_agent/research/dspy_modules/research_planner.py`
- `mini_agent/research/dspy_modules/data_analyst.py`
- `mini_agent/research/dspy_modules/section_writer.py`
- `mini_agent/research/dspy_modules/reviewer.py`

```bash
# Test
pytest tests/research/test_dspy_modules.py -v  # ✅ (mocked DSPy LM)
pytest tests/ -x                                # ✅ Existing tests pass
```

---

### Step 27: Create SubAgentDispatcher

**Files created:**
- `mini_agent/research/sub_agents.py`

```bash
# Test
pytest tests/research/test_sub_agents.py -v  # ✅
pytest tests/ -x                              # ✅ Existing tests pass
```

---

### Step 28: Create ResearchOrchestrator

**Files created:**
- `mini_agent/research/orchestrator.py`

```bash
# Test
pytest tests/research/test_orchestrator.py -v  # ✅ End-to-end (mocked LLM + tools)
pytest tests/ -x                                # ✅ Existing tests pass
```

---

### Step 29: Create research CLI entry point + MCP server

**Files created:**
- `mini_agent/research/cli_entry.py`
- `mini_agent/research/mcp_server.py`

**Files modified:** `mini_agent/cli.py` (add `research` subcommand)

```bash
# Test
bpsagent --help                          # ✅ Shows research subcommand
bpsagent --task "cari inflasi NTT"       # ✅ Still works (existing path)
bpsagent research --help                 # ✅ Shows research options
pytest tests/ -x                          # ✅ All existing tests pass
pytest tests/research/ -v                 # ✅ All research tests pass
```

---

### Step 30: Update __init__.py and version bump

**Files modified:**
- `mini_agent/__init__.py` (add `get_research_orchestrator`, bump version)
- `CHANGELOG.md` (append v0.3.0 entry)

```bash
# Final verification
python -c "import mini_agent; print(mini_agent.__version__)"  # "0.3.0"
bpsagent                                  # ✅ Interactive mode works
bpsagent --task "cari IPM NTT 2023"       # ✅ BPS query works
bps-mcp-server                            # ✅ MCP server starts
bpsagent research "Pengaruh IPM terhadap kemiskinan di NTT"  # ✅ Research mode
pytest tests/ -x                          # ✅ ALL tests pass
pytest tests/research/ -v                 # ✅ ALL research tests pass
```

---

## Part 6: Backward Compatibility Verification

### Verification Script (run after EVERY step)

```bash
#!/bin/bash
# scripts/verify_backward_compat.sh

set -e
echo "=== Backward Compatibility Check ==="

# 1. Base import works
echo "[1/7] Testing base import..."
python -c "from mini_agent import Agent, LLMClient, __version__; print(f'v{__version__} OK')"

# 2. BPS modules import
echo "[2/7] Testing BPS modules..."
python -c "
from mini_agent.bps_api import BPSWebAPI
from mini_agent.bps_orchestrator import BPSOrchestrator
from mini_agent.bps_mcp_server import main
from mini_agent.allstats_client import AllStatsClient
print('BPS modules OK')
"

# 3. Tools import
echo "[3/7] Testing tools..."
python -c "
from mini_agent.tools.bash_tool import BashTool
from mini_agent.tools.file_tools import ReadTool, WriteTool, EditTool
from mini_agent.tools.mcp_loader import load_mcp_tools_async
print('Tools OK')
"

# 4. CLI entry point exists
echo "[4/7] Testing CLI entry point..."
which bpsagent > /dev/null 2>&1 && echo "bpsagent OK" || echo "WARN: bpsagent not in PATH"
which bps-mcp-server > /dev/null 2>&1 && echo "bps-mcp-server OK" || echo "WARN: bps-mcp-server not in PATH"

# 5. Config loading (with test config)
echo "[5/7] Testing config loading..."
python -c "
from mini_agent.config import Config, LLMConfig, AgentConfig, ToolsConfig
# Verify Config can be instantiated with existing fields only
config = Config(
    llm=LLMConfig(api_key='test_key_for_compat_check', api_base='https://api.test.com', model='test'),
    agent=AgentConfig(),
    tools=ToolsConfig(),
)
print(f'Config OK (research={config.research})')  # Should be None
"

# 6. Schema compatibility
echo "[6/7] Testing schema..."
python -c "
from mini_agent.schema import LLMProvider, Message, ToolCall, FunctionCall
assert LLMProvider.ANTHROPIC == 'anthropic'
assert LLMProvider.OPENAI == 'openai'
print('Schema OK')
"

# 7. Existing tests pass
echo "[7/7] Running existing test suite..."
pytest tests/ -x --ignore=tests/research/ -q

echo ""
echo "=== ALL BACKWARD COMPATIBILITY CHECKS PASSED ==="
```

### What MUST Work After Every Step

| Check | Command | Expected |
|-------|---------|----------|
| Interactive mode | `bpsagent` | Starts interactive prompt |
| Task mode | `bpsagent --task "cari inflasi NTT"` | Executes BPS query |
| MCP server | `bps-mcp-server` | Starts STDIO MCP server |
| ACP server | `bps-stat-agent-acp` | Starts HTTP ACP server |
| Base import | `python -c "import mini_agent"` | No errors |
| Existing tests | `pytest tests/ --ignore=tests/research/` | All pass |
| Config load | Existing `config.yaml` without `research:` section | Loads without error |

### Compatibility Matrix

| Feature | v0.2.0 | v0.3.0+ | Notes |
|---------|--------|---------|-------|
| `bpsagent` CLI | ✅ | ✅ | Unchanged |
| `bpsagent --task` | ✅ | ✅ | Unchanged |
| `bpsagent research` | ❌ | ✅ | NEW (requires extras) |
| `bps-mcp-server` | ✅ | ✅ | Unchanged |
| `bps-research-mcp` | ❌ | ✅ | NEW |
| 62 BPS tools | ✅ | ✅ | Unchanged |
| Anthropic provider | ✅ | ✅ | Unchanged |
| OpenAI provider | ✅ | ✅ | Unchanged |
| LiteLLM provider | ❌ | ✅ | NEW (requires extras) |
| `pip install bps-stat-agent` | ✅ | ✅ | Same deps |
| `config.yaml` (no research) | ✅ | ✅ | Works unchanged |

---

## Part 7: Version Checkpoints

### v0.2.1 — MCP Server Integration (Steps 1-2)

**What's new:** Research package skeleton + optional deps declared.  
**User-visible:** Nothing changes for existing users.  
**Install:** `pip install bps-stat-agent` (unchanged)

```
Milestone: pyproject.toml has research extras; package skeleton exists
Tag: v0.2.1
```

---

### v0.2.5 — Foundation (Steps 3-7)

**What's new:** ProjectState, WorkspaceManager, ApprovalGates, SessionResume.  
**User-visible:** Nothing changes for existing users.  
**Install:** `pip install bps-stat-agent[research-core]` enables foundation.

```
Milestone: Can create/save/resume research projects
Tag: v0.2.5
```

---

### v0.3.0 — LiteLLM Integration (Steps 8-12)

**What's new:** LiteLLM provider, LLMGateway, PhaseManager, ResearchConfig.  
**User-visible:** `bpsagent` unchanged; new `litellm` provider available.  
**Install:** `pip install bps-stat-agent[research-core]`

```
Milestone: Multi-model routing works; phase system limits tools correctly
Tag: v0.3.0
```

---

### v0.4.0 — Analysis Engine (Steps 13-16)

**What's new:** Sandbox execution, statistical tools, APA formatter, visualization.  
**User-visible:** Research mode can execute Python code and run stats.  
**Install:** `pip install bps-stat-agent[research-analysis]`

```
Milestone: Can run regression on BPS data in sandbox, get APA-formatted output
Tag: v0.4.0
```

---

### v0.5.0 — Literature & RAG (Steps 17-20)

**What's new:** Paper search, RAG engine, citation manager, knowledge graph.  
**User-visible:** Research mode can search papers and build knowledge base.  
**Install:** `pip install bps-stat-agent[research-rag]`

```
Milestone: Can search papers, build citation graph, answer questions from literature
Tag: v0.5.0
```

---

### v0.7.0 — Paper Writing (Steps 21-22)

**What's new:** Section writer, LaTeX/Typst compiler, templates, bibliography.  
**User-visible:** Research mode can draft paper sections and compile to PDF.  
**Install:** `pip install bps-stat-agent[research-writing]`

```
Milestone: Can generate a complete paper draft from research data
Tag: v0.7.0
```

---

### v0.9.0 — Quality Gate (Steps 23-26)

**What's new:** Citation verifier, stat validator, writing quality, peer reviewer, DSPy modules.  
**User-visible:** Research mode validates all outputs before finalizing.  
**Install:** `pip install bps-stat-agent[research-full]`

```
Milestone: Zero-hallucination citations verified; peer review simulation works
Tag: v0.9.0
```

---

### v1.0.0 — Full Integration (Steps 27-30)

**What's new:** ResearchOrchestrator, SubAgentDispatcher, CLI entry, MCP server.  
**User-visible:** Full `bpsagent research "topic"` workflow end-to-end.  
**Install:** `pip install bps-stat-agent[research-full]`

```
Milestone: Complete research workflow from question to paper
Tag: v1.0.0
```

---

## Appendix A: File Tree (Final State at v1.0)

```
mini_agent/
├── __init__.py                          # MODIFIED (version bump + lazy import)
├── agent.py                             # UNCHANGED
├── acp/
│   ├── __init__.py                      # UNCHANGED
│   └── server.py                        # UNCHANGED
├── allstats_client.py                   # UNCHANGED
├── bps_api.py                           # UNCHANGED
├── bps_data_retriever.py                # UNCHANGED
├── bps_mcp_server.py                    # UNCHANGED
├── bps_models.py                        # UNCHANGED
├── bps_normalization.py                 # UNCHANGED
├── bps_orchestrator.py                  # UNCHANGED
├── bps_resolution.py                    # UNCHANGED
├── bps_resource_retriever.py            # UNCHANGED
├── cli.py                               # MODIFIED (add research subcommand)
├── colors.py                            # UNCHANGED
├── config.py                            # MODIFIED (add ResearchConfig)
├── config/
│   ├── config.yaml                      # UNCHANGED
│   ├── mcp.json                         # UNCHANGED
│   ├── system_prompt.md                 # UNCHANGED
│   ├── mcp-research.json                # NEW
│   ├── research_config.yaml             # NEW
│   └── system_prompt_research.md        # NEW
├── health.py                            # UNCHANGED
├── llm/
│   ├── __init__.py                      # UNCHANGED
│   ├── anthropic_client.py              # UNCHANGED
│   ├── base.py                          # UNCHANGED
│   ├── litellm_client.py               # NEW
│   ├── llm_wrapper.py                   # MODIFIED (add litellm branch)
│   └── openai_client.py                 # UNCHANGED
├── logger.py                            # UNCHANGED
├── logging_config.py                    # UNCHANGED
├── metrics.py                           # UNCHANGED
├── research/                            # NEW (entire directory)
│   ├── __init__.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── apa_formatter.py
│   │   ├── sandbox.py
│   │   ├── stats_tools.py
│   │   └── viz_tools.py
│   ├── approval_gates.py
│   ├── cli_entry.py
│   ├── constants.py
│   ├── dspy_modules/
│   │   ├── __init__.py
│   │   ├── data_analyst.py
│   │   ├── research_planner.py
│   │   ├── reviewer.py
│   │   ├── section_writer.py
│   │   └── signatures.py
│   ├── exceptions.py
│   ├── literature/
│   │   ├── __init__.py
│   │   ├── citation_manager.py
│   │   ├── knowledge_graph.py
│   │   ├── paper_search.py
│   │   └── rag_engine.py
│   ├── llm_gateway.py
│   ├── mcp_server.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cost_tracker.py
│   │   ├── decision_log.py
│   │   └── project_state.py
│   ├── orchestrator.py
│   ├── phase_manager.py
│   ├── quality/
│   │   ├── __init__.py
│   │   ├── citation_verifier.py
│   │   ├── peer_reviewer.py
│   │   ├── stat_validator.py
│   │   └── writing_quality.py
│   ├── session_resume.py
│   ├── sub_agents.py
│   ├── templates/
│   │   ├── imrad.yaml
│   │   ├── thesis.yaml
│   │   ├── report.yaml
│   │   ├── latex/
│   │   │   ├── article.tex
│   │   │   └── thesis.tex
│   │   └── typst/
│   │       └── article.typ
│   ├── tool_registry.py
│   └── workspace.py
├── retry.py                             # UNCHANGED
├── schema/
│   ├── __init__.py                      # UNCHANGED
│   └── schema.py                        # MODIFIED (add LITELLM enum)
├── setup_wizard.py                      # UNCHANGED
├── skills/                              # UNCHANGED (all subdirs)
├── tools/
│   ├── __init__.py                      # UNCHANGED
│   ├── base.py                          # UNCHANGED
│   ├── bash_tool.py                     # UNCHANGED
│   ├── file_tools.py                    # UNCHANGED
│   ├── mcp_loader.py                    # UNCHANGED
│   ├── note_tool.py                     # UNCHANGED
│   ├── skill_loader.py                  # UNCHANGED
│   └── skill_tool.py                    # UNCHANGED
├── tracing.py                           # UNCHANGED
└── utils/
    ├── __init__.py                      # UNCHANGED
    └── terminal_utils.py                # UNCHANGED

tests/
├── (all 36 existing test files)         # UNCHANGED
└── research/                            # NEW
    ├── __init__.py
    ├── conftest.py
    ├── test_apa_formatter.py
    ├── test_citation_manager.py
    ├── test_citation_verifier.py
    ├── test_cost_tracker.py
    ├── test_dspy_modules.py
    ├── test_knowledge_graph.py
    ├── test_latex_compiler.py
    ├── test_litellm_client.py
    ├── test_llm_gateway.py
    ├── test_orchestrator.py
    ├── test_paper_search.py
    ├── test_peer_reviewer.py
    ├── test_phase_manager.py
    ├── test_project_state.py
    ├── test_rag_engine.py
    ├── test_sandbox.py
    ├── test_section_writer.py
    ├── test_session_resume.py
    ├── test_stat_validator.py
    ├── test_stats_tools.py
    ├── test_sub_agents.py
    └── test_workspace.py
```

---

## Appendix B: Dependency Graph (Simplified)

```
pyproject.toml [research-full]
    │
    ├── research-core
    │   ├── litellm ──→ llm/litellm_client.py ──→ research/llm_gateway.py
    │   ├── dspy ──→ research/dspy_modules/*
    │   ├── lancedb ──→ research/literature/rag_engine.py
    │   ├── chonkie ──→ research/literature/rag_engine.py
    │   ├── great-expectations ──→ research/analysis/sandbox.py
    │   └── pandera ──→ research/analysis/stats_tools.py
    │
    ├── research-analysis
    │   ├── statsmodels ──→ research/analysis/stats_tools.py
    │   ├── scipy ──→ research/analysis/stats_tools.py
    │   ├── linearmodels ──→ research/analysis/stats_tools.py
    │   ├── matplotlib ──→ research/analysis/viz_tools.py
    │   └── seaborn ──→ research/analysis/viz_tools.py
    │
    ├── research-bayesian
    │   ├── pymc ──→ research/analysis/stats_tools.py (Bayesian)
    │   ├── bambi ──→ research/analysis/stats_tools.py (Bayesian)
    │   └── dowhy ──→ research/analysis/stats_tools.py (Causal)
    │
    ├── research-rag
    │   ├── paper-qa ──→ research/literature/rag_engine.py
    │   ├── lightrag-hku ──→ research/literature/knowledge_graph.py
    │   ├── sentence-transformers ──→ research/literature/rag_engine.py
    │   └── scispacy ──→ research/literature/knowledge_graph.py
    │
    └── research-writing
        ├── pylatex ──→ research/writing/latex_compiler.py
        ├── citeproc-py ──→ research/writing/bibliography.py
        ├── bibtexparser ──→ research/literature/citation_manager.py
        └── habanero ──→ research/quality/citation_verifier.py
```

---

## Appendix C: Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Research import breaks base install | All research imports are lazy (try/except ImportError) |
| Heavy deps slow down `pip install` | Research deps are in optional groups; base install unchanged |
| LiteLLM conflicts with existing anthropic/openai | LiteLLM is only imported when `provider="litellm"` |
| New enum value breaks serialization | String enums are forward-compatible; old code ignores unknown values |
| Config changes break existing configs | `research` field is `Optional[ResearchConfig] = None` |
| New CLI subcommand conflicts | `argparse.add_subparsers()` is additive; no existing args change |
| Test pollution | Research tests in separate `tests/research/` directory |
| MCP server conflicts | Research MCP config is a SEPARATE file (`mcp-research.json`) |

---

*End of Migration Path Document*
