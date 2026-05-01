# BPS Academic Research Agent — System Architecture v1.0

**Version:** 1.0 (FINAL)  
**Status:** Definitive Implementation Reference  
**Created:** 2025-07-14  
**Last Updated:** 2025-07-15  
**Base:** BPS Stat Agent v0.2.0 → Academic Research AI Agent v1.0

---

## Table of Contents

1. [High-Level System Diagram](#1-high-level-system-diagram)
2. [Layer Architecture](#2-layer-architecture)
3. [Module & Package Structure](#3-module--package-structure)
4. [Data Flow Diagram](#4-data-flow-diagram)
5. [Phase-Gated Tool Loading](#5-phase-gated-tool-loading)
6. [Token Management Strategy](#6-token-management-strategy)
7. [Sub-Agent Architecture](#7-sub-agent-architecture)
8. [DSPy Pipeline Design](#8-dspy-pipeline-design)
9. [RAG Pipeline Design](#9-rag-pipeline-design)
10. [Embedding Strategy](#10-embedding-strategy)
11. [Safety & Integrity](#11-safety--integrity)
12. [Project State Schema](#12-project-state-schema)
13. [Workspace Structure](#13-workspace-structure)
14. [MCP Configuration](#14-mcp-configuration)
15. [Configuration Extension](#15-configuration-extension)
16. [Deployment & Infrastructure](#16-deployment--infrastructure)

---

## 1. High-Level System Diagram

```
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                     BPS ACADEMIC RESEARCH AGENT v1.0                                ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                      ║
║  ┌─────────────────────────── INTERFACES ──────────────────────────────────────┐    ║
║  │  CLI (interactive + batch)  │  MCP Server (STDIO)  │  ACP Server (HTTP)     │    ║
║  └─────────────────────────────────────────────────────────────────────────────┘    ║
║                                        │                                             ║
║  ┌─────────────────────────── ORCHESTRATION ───────────────────────────────────┐    ║
║  │  ResearchOrchestrator                                                        │    ║
║  │  ├── Phase Manager (PLAN → COLLECT → ANALYZE → WRITE → REVIEW)              │    ║
║  │  ├── Sub-Agent Dispatcher (SectionWriter, PeerReviewer, StatValidator, etc.) │    ║
║  │  ├── Human-in-the-Loop Gates                                                 │    ║
║  │  ├── Project State Manager (project.yaml)                                    │    ║
║  │  └── Session Resume Protocol                                                 │    ║
║  └─────────────────────────────────────────────────────────────────────────────┘    ║
║                                        │                                             ║
║  ┌──── Layer 0 ────┐  ┌──── Layer 3 ────┐  ┌──── Layer 4 ──────────────────┐       ║
║  │  LLM GATEWAY    │  │  DSPy PIPELINE   │  │  MCP SERVER ECOSYSTEM         │       ║
║  │  ┌────────────┐ │  │  ┌────────────┐  │  │  ┌─────────────────────────┐  │       ║
║  │  │  LiteLLM   │ │  │  │ Signatures │  │  │  │ BPS (62 tools)          │  │       ║
║  │  │  ├─Claude  │ │  │  │ Modules    │  │  │  │ paper-search-mcp (22)   │  │       ║
║  │  │  ├─GPT-4o  │ │  │  │ MIPROv2    │  │  │  │ zotero-mcp             │  │       ║
║  │  │  ├─Gemini  │ │  │  │ Optimizers │  │  │  │ overleaf-mcp           │  │       ║
║  │  │  ├─Mistral │ │  │  └────────────┘  │  │  │ jupyter-mcp            │  │       ║
║  │  │  └─Local   │ │  └──────────────────┘  │  │ mcp-pdf (46 tools)     │  │       ║
║  │  │  Sem.Cache │ │                         │  │ qdrant-mcp             │  │       ║
║  │  │  Cost Track│ │                         │  │ neo4j-mcp              │  │       ║
║  │  └────────────┘ │                         │  │ markitdown-mcp         │  │       ║
║  └─────────────────┘                         │  │ rmcp (52 R tools)      │  │       ║
║                                              │  └─────────────────────────┘  │       ║
║  ┌──── Layer 1 ────────────────────────┐     └───────────────────────────────┘       ║
║  │  DOCUMENT PROCESSING                 │                                            ║
║  │  ┌──────────┐ ┌──────────┐          │    ┌──── Layer 5 ──────────────────┐       ║
║  │  │MarkItDown│ │  MinerU  │          │    │  STATISTICAL ANALYSIS ENGINE   │       ║
║  │  │(29+ fmt) │ │(Sci.PDF) │          │    │  ┌─────────────────────────┐  │       ║
║  │  └──────────┘ └──────────┘          │    │  │ Sandbox (E2B / Docker)  │  │       ║
║  │  ┌──────────┐ ┌──────────────┐      │    │  │ PandasAI + LIDA        │  │       ║
║  │  │  GROBID  │ │ Unstructured │      │    │  │ statsmodels + scipy    │  │       ║
║  │  │(Biblio.) │ │  (ETL pipe)  │      │    │  │ PyMC + Bambi + ArviZ   │  │       ║
║  │  └──────────┘ └──────────────┘      │    │  │ DoWhy + CausalML       │  │       ║
║  └──────────────────────────────────────┘    │  │ Lifelines + pingouin  │  │       ║
║                                              │  │ ydata-profiling        │  │       ║
║  ┌──── Layer 2 ────────────────────────┐     │  │ Great Expectations     │  │       ║
║  │  KNOWLEDGE & RAG                     │    │  └─────────────────────────┘  │       ║
║  │  ┌──────────┐ ┌──────────┐          │    └───────────────────────────────┘       ║
║  │  │ PaperQA2 │ │ LightRAG │          │                                            ║
║  │  │(Sci.RAG) │ │(KG Extr.)│          │    ┌──── Layer 6 ──────────────────┐       ║
║  │  └──────────┘ └──────────┘          │    │  PAPER WRITING ENGINE          │       ║
║  │  ┌──────────┐ ┌──────────────┐      │    │  ┌─────────────────────────┐  │       ║
║  │  │SPECTER2  │ │nomic-embed   │      │    │  │ Tectonic / Typst        │  │       ║
║  │  │(paper)   │ │(chunk 8192)  │      │    │  │ PyLaTeX + python-docx   │  │       ║
║  │  └──────────┘ └──────────────┘      │    │  │ Pandoc (conversion)     │  │       ║
║  │  ┌──────────┐ ┌──────────┐          │    │  │ LanguageTool + proselint│  │       ║
║  │  │ LanceDB  │ │ Chonkie  │          │    │  │ tikzplotlib             │  │       ║
║  │  │(vectors) │ │(chunking)│          │    │  │ Template Registry       │  │       ║
║  │  └──────────┘ └──────────┘          │    │  └─────────────────────────┘  │       ║
║  │  ┌──────────┐ ┌──────────┐          │    └───────────────────────────────┘       ║
║  │  │ scispaCy │ │NetworkX  │          │                                            ║
║  │  │(NER)     │ │(citation)│          │    ┌──── Layer 7 ──────────────────┐       ║
║  │  └──────────┘ └──────────┘          │    │  QUALITY GATE                  │       ║
║  └──────────────────────────────────────┘    │  ┌─────────────────────────┐  │       ║
║                                              │  │ Citation Verification   │  │       ║
║                                              │  │ Statistical Validity    │  │       ║
║                                              │  │ Writing Quality         │  │       ║
║                                              │  │ Peer Review Simulator   │  │       ║
║                                              │  │ Reproducibility Audit   │  │       ║
║                                              │  │ Plagiarism Detection    │  │       ║
║                                              │  └─────────────────────────┘  │       ║
║                                              └───────────────────────────────┘       ║
║                                                                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════╣
║  EXISTING INFRASTRUCTURE (preserved):                                                ║
║  Agent Loop │ LLM (Anthropic/OpenAI) │ Tool ABC │ Skills │ Observability │ Docker   ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
                                    │
                          ┌─────────▼──────────┐
                          │   PROJECT STATE     │
                          │   project.yaml      │
                          │   + workspace/      │
                          └────────────────────┘
```

---

## 2. Layer Architecture

### Layer 0: LLM Gateway

**Purpose:** Unified multi-model access with cost optimization and reliability.

| Component | Role | Key Feature |
|-----------|------|-------------|
| **LiteLLM** | Provider gateway | 100+ model support, unified API |
| **Router** | Task-model mapping | Expensive tasks → Claude/GPT-4o, cheap → mini |
| **Cost Tracker** | Per-project billing | Token counts + USD per research project |
| **Fallback Chain** | Reliability | Claude → GPT-4o → Gemini → local |
| **Semantic Cache** | Deduplication | GPTCache with embedding similarity |

```python
# Model routing strategy
ROUTING_RULES = {
    "paper_writing":     {"primary": "claude-sonnet-4-20250514", "fallback": "gpt-4o"},
    "peer_review":       {"primary": "claude-sonnet-4-20250514", "fallback": "gpt-4o"},
    "data_analysis":     {"primary": "gpt-4o", "fallback": "claude-sonnet-4-20250514"},
    "literature_search": {"primary": "gpt-4o-mini", "fallback": "claude-3-5-haiku-20241022"},
    "summarization":     {"primary": "gpt-4o-mini", "fallback": "claude-3-5-haiku-20241022"},
    "citation_verify":   {"primary": "gpt-4o-mini", "fallback": "claude-3-5-haiku-20241022"},
    "embedding":         {"primary": "nomic-embed-text", "fallback": "text-embedding-3-small"},
}
```

### Layer 1: Document Processing

**Purpose:** Ingest any document format into structured, searchable content.

| Component | Role | Formats |
|-----------|------|---------|
| **MarkItDown** | Universal intake | PDF, DOCX, PPTX, XLSX, HTML, images (29+) |
| **MinerU** | Scientific PDF | LaTeX equations, complex tables, figures |
| **GROBID** | Bibliographic extraction | Author, title, DOI, abstract from PDF headers |
| **Unstructured** | ETL pipeline | Structure-aware chunking, element classification |

### Layer 2: Knowledge & RAG

**Purpose:** Scientific literature understanding, retrieval, and knowledge graph construction.

| Component | Role | Key Capability |
|-----------|------|----------------|
| **PaperQA2** | Scientific RAG engine | Multi-paper QA with citation provenance |
| **LightRAG** | Knowledge graph extraction | Entity-relation triples from papers |
| **SPECTER2** | Paper embeddings | Citation-aware, 768-dim, trained on S2ORC |
| **nomic-embed-text** | Chunk embeddings | 8192 context, 768-dim, Matryoshka |
| **LanceDB** | Vector store | Serverless, embedded, multimodal, Lance format |
| **Chonkie** | Semantic chunking | 33x faster than LangChain, boundary-aware |
| **scispaCy** | Scientific NER | Biomedical/scientific entity extraction |
| **NetworkX** | Citation networks | Graph analysis, centrality, community detection |

### Layer 3: DSPy Pipeline Framework

**Purpose:** Optimizable, composable research pipeline modules.

| Component | Role |
|-----------|------|
| **Signatures** | Typed I/O contracts for each research step |
| **Modules** | Composable pipeline stages |
| **MIPROv2** | Automatic prompt optimization |
| **Assertions** | Runtime quality constraints |

### Layer 4: MCP Server Ecosystem

**Purpose:** Extended tool access through Model Context Protocol.

| Server | Tools | Purpose |
|--------|-------|---------|
| **BPS (existing)** | 62 | Indonesian statistical data |
| **paper-search-mcp** | 22 | Multi-source literature search |
| **zotero-mcp** | ~15 | Citation/bibliography management |
| **overleaf-mcp** | ~10 | LaTeX compilation + collaboration |
| **jupyter-mcp** | ~12 | Code execution + notebooks |
| **mcp-pdf** | 46 | PDF manipulation + extraction |
| **qdrant-mcp** | ~8 | Vector similarity search |
| **neo4j-mcp** | ~10 | Knowledge graph queries |
| **markitdown-mcp** | ~5 | Document format conversion |
| **rmcp** | 52 | R statistical computing |

### Layer 5: Statistical Analysis Engine

**Purpose:** Rigorous statistical computation in sandboxed environments.

| Component | Role |
|-----------|------|
| **E2B / Docker** | Sandboxed execution (cloud or local) |
| **PandasAI** | Conversational data analysis |
| **LIDA** | Auto-visualization + goal exploration |
| **statsmodels** | Classical statistics (OLS, GLM, time series) |
| **scipy.stats** | Hypothesis testing, distributions |
| **linearmodels** | Panel data, IV, system estimation |
| **arch** | GARCH, volatility modeling |
| **pingouin** | Simple statistical tests (APA-formatted) |
| **PyMC + Bambi** | Bayesian inference + formula API |
| **ArviZ** | Bayesian diagnostics + visualization |
| **DoWhy** | Causal inference framework |
| **CausalML** | Uplift modeling, treatment effects |
| **Lifelines** | Survival analysis |
| **ydata-profiling** | Automated EDA reports |
| **Great Expectations** | Data validation pipelines |
| **Pandera** | DataFrame schema validation |

### Layer 6: Paper Writing Engine

**Purpose:** End-to-end academic document generation.

| Component | Role |
|-----------|------|
| **Tectonic** | Zero-config LaTeX compilation (auto-downloads packages) |
| **Typst** | Modern alternative (millisecond compilation, simpler syntax) |
| **PyLaTeX** | Programmatic LaTeX document generation |
| **python-docx** | DOCX output for journals requiring Word |
| **Pandoc** | Universal format conversion hub |
| **LanguageTool** | Grammar + style checking (academic mode) |
| **proselint** | Academic prose linting |
| **tikzplotlib** | matplotlib to TikZ (vector figures in LaTeX) |
| **Template Registry** | IEEE, Elsevier, Springer, MDPI, APA7, Chicago |

### Layer 7: Quality Gate

**Purpose:** Automated verification before any output is finalized.

| Component | Role | Threshold |
|-----------|------|-----------|
| **Citation Verification** | CrossRef + Semantic Scholar DOI resolution | 0 unverified |
| **Statistical Validity** | Assumption checks, effect sizes, power | All tests pass |
| **LanguageTool** | Grammar, spelling, style | < 5 warnings |
| **proselint** | Academic writing conventions | < 3 issues |
| **Peer Review Simulator** | Adversarial sub-agent critique | Address all major |
| **Reproducibility Audit** | All computations logged + reproducible | 100% reproducible |
| **Plagiarism Detection** | sentence-transformers + MinHash (LSH) | < 5% similarity |


---

## 3. Module & Package Structure

```
mini_agent/
├── (EXISTING — unchanged) ─────────────────────────────────────────────
│   ├── __init__.py
│   ├── agent.py                        # Core agent loop (80K token mgmt)
│   ├── cli.py                          # Interactive + non-interactive CLI
│   ├── config.py                       # Configuration management
│   ├── bps_mcp_server.py              # MCP server (STDIO)
│   ├── bps_acp_server.py             # ACP server (HTTP)
│   ├── bps_skills.py                  # Skills system
│   ├── bps_data_tools.py             # BPS data tools
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py                    # LLMClient ABC
│   │   ├── anthropic_provider.py      # Anthropic implementation
│   │   └── openai_provider.py         # OpenAI implementation
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py                    # Tool ABC (name/desc/params/execute)
│   │   └── tool_result.py            # ToolResult dataclass
│   └── observability/
│       ├── prometheus.py              # Prometheus metrics
│       ├── otel.py                    # OpenTelemetry tracing
│       └── logging.py                 # Structured logging
│
├── (NEW) ──────────────────────────────────────────────────────────────
│
├── gateway/                            # Layer 0: LLM Gateway
│   ├── __init__.py
│   ├── router.py                      # LiteLLM multi-model router
│   ├── cost_tracker.py                # Per-project cost accounting
│   ├── fallback_chain.py             # Automatic provider failover
│   ├── semantic_cache.py             # GPTCache integration
│   └── model_config.py               # Model routing rules
│
├── document/                           # Layer 1: Document Processing
│   ├── __init__.py
│   ├── ingestion.py                   # Unified ingestion orchestrator
│   ├── markitdown_adapter.py         # MarkItDown wrapper (29+ formats)
│   ├── mineru_adapter.py             # MinerU scientific PDF processor
│   ├── grobid_client.py              # GROBID bibliographic extraction
│   ├── unstructured_pipeline.py      # Unstructured ETL pipeline
│   ├── equation_extractor.py         # LaTeX equation extraction
│   └── table_extractor.py            # Table to DataFrame conversion
│
├── knowledge/                          # Layer 2: Knowledge & RAG
│   ├── __init__.py
│   ├── rag_engine.py                  # PaperQA2 integration
│   ├── knowledge_graph.py            # LightRAG graph extraction
│   ├── embeddings/
│   │   ├── __init__.py
│   │   ├── specter2.py               # Paper-level embeddings
│   │   ├── nomic.py                   # Chunk-level embeddings
│   │   └── dual_encoder.py           # Dual embedding strategy
│   ├── vectorstore/
│   │   ├── __init__.py
│   │   ├── lancedb_store.py          # LanceDB vector operations
│   │   ├── indexing.py                # Index management
│   │   └── retrieval.py              # Hybrid search (vector + keyword)
│   ├── chunking/
│   │   ├── __init__.py
│   │   ├── chonkie_chunker.py        # Semantic chunking (fast)
│   │   └── scientific_splitter.py    # Section-aware splitting
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── scispacy_ner.py           # Scientific entity extraction
│   │   └── entity_linker.py          # Entity disambiguation
│   └── citation_network/
│       ├── __init__.py
│       ├── graph_builder.py           # NetworkX citation graph
│       ├── centrality.py              # Influence metrics
│       └── community.py               # Research cluster detection
│
├── pipeline/                           # Layer 3: DSPy Pipeline
│   ├── __init__.py
│   ├── signatures/
│   │   ├── __init__.py
│   │   ├── search.py                  # SearchQuery to Papers
│   │   ├── evidence.py                # Papers to Evidence
│   │   ├── synthesis.py               # Evidence to Synthesis
│   │   ├── analysis.py                # Data to StatisticalResults
│   │   └── writing.py                 # Outline + Context to Section
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── literature_review.py       # End-to-end lit review module
│   │   ├── data_analysis.py           # Statistical analysis module
│   │   ├── paper_generation.py        # Section generation module
│   │   └── quality_check.py           # Quality verification module
│   ├── optimizers/
│   │   ├── __init__.py
│   │   ├── mipro_config.py           # MIPROv2 configuration
│   │   └── metrics.py                 # Custom evaluation metrics
│   └── pipeline_runner.py             # Composable pipeline executor
│
├── mcp_servers/                        # Layer 4: MCP Ecosystem
│   ├── __init__.py
│   ├── registry.py                    # MCP server registry + lifecycle
│   ├── paper_search/
│   │   ├── __init__.py
│   │   └── client.py                  # paper-search-mcp adapter
│   ├── zotero/
│   │   ├── __init__.py
│   │   └── client.py                  # zotero-mcp adapter
│   ├── overleaf/
│   │   ├── __init__.py
│   │   └── client.py                  # overleaf-mcp adapter
│   ├── jupyter/
│   │   ├── __init__.py
│   │   └── client.py                  # jupyter-mcp adapter
│   └── r_stats/
│       ├── __init__.py
│       └── client.py                  # rmcp adapter
│
├── analysis/                           # Layer 5: Statistical Engine
│   ├── __init__.py
│   ├── sandbox/
│   │   ├── __init__.py
│   │   ├── docker_sandbox.py          # Docker-based execution
│   │   ├── e2b_sandbox.py            # E2B cloud execution
│   │   ├── sandbox_factory.py        # Sandbox selection logic
│   │   └── Dockerfile                 # Pre-built scientific image
│   ├── conversational/
│   │   ├── __init__.py
│   │   ├── pandasai_adapter.py       # PandasAI integration
│   │   └── lida_adapter.py           # LIDA visualization
│   ├── classical/
│   │   ├── __init__.py
│   │   ├── descriptive.py            # Descriptive statistics
│   │   ├── regression.py             # OLS, logistic, panel, IV
│   │   ├── time_series.py            # ARIMA, VAR, cointegration
│   │   ├── hypothesis.py             # t-test, ANOVA, chi-square
│   │   └── nonparametric.py          # Mann-Whitney, Kruskal-Wallis
│   ├── bayesian/
│   │   ├── __init__.py
│   │   ├── pymc_models.py            # PyMC model definitions
│   │   ├── bambi_formulas.py         # Bambi formula interface
│   │   └── arviz_diagnostics.py      # ArviZ posterior analysis
│   ├── causal/
│   │   ├── __init__.py
│   │   ├── dowhy_models.py           # DoWhy causal graphs
│   │   ├── causalml_effects.py       # Treatment effect estimation
│   │   └── dag_builder.py            # DAG specification
│   ├── survival/
│   │   ├── __init__.py
│   │   └── lifelines_models.py       # Kaplan-Meier, Cox PH
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── great_expectations_suite.py  # Data quality rules
│   │   ├── pandera_schemas.py        # DataFrame schemas
│   │   └── profiling.py              # ydata-profiling reports
│   └── visualization/
│       ├── __init__.py
│       ├── publication_plots.py       # Publication-quality figures
│       ├── tikz_export.py            # tikzplotlib conversion
│       └── style_presets.py           # Journal-specific styles
│
├── writing/                            # Layer 6: Paper Writing Engine
│   ├── __init__.py
│   ├── templates/
│   │   ├── __init__.py
│   │   ├── registry.py               # Template discovery + loading
│   │   ├── ieee/                      # IEEE conference/journal
│   │   ├── elsevier/                  # Elsevier journals
│   │   ├── springer/                  # Springer Nature
│   │   ├── mdpi/                      # MDPI open access
│   │   ├── apa7/                      # APA 7th edition
│   │   └── chicago/                   # Chicago style
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── latex_generator.py         # PyLaTeX document assembly
│   │   ├── typst_generator.py        # Typst document generation
│   │   ├── docx_generator.py         # python-docx output
│   │   └── table_generator.py        # DataFrame to academic tables
│   ├── compilation/
│   │   ├── __init__.py
│   │   ├── tectonic_compiler.py      # Tectonic (zero-config LaTeX)
│   │   ├── typst_compiler.py         # Typst (millisecond builds)
│   │   └── pandoc_converter.py       # Universal format conversion
│   ├── bibliography/
│   │   ├── __init__.py
│   │   ├── bibtex_manager.py         # BibTeX CRUD operations
│   │   ├── csl_formatter.py          # Citation Style Language
│   │   └── doi_resolver.py           # DOI to full metadata
│   ├── figures/
│   │   ├── __init__.py
│   │   ├── figure_manager.py         # Placement + captions
│   │   ├── tikz_converter.py         # matplotlib to TikZ
│   │   └── format_optimizer.py       # DPI/format per journal
│   └── linting/
│       ├── __init__.py
│       ├── language_tool.py           # LanguageTool integration
│       ├── proselint_checker.py      # Academic style linting
│       └── readability.py             # Flesch-Kincaid, etc.
│
├── quality/                            # Layer 7: Quality Gate
│   ├── __init__.py
│   ├── gate_runner.py                 # Orchestrates all quality checks
│   ├── citation_verifier.py          # CrossRef + S2 verification
│   ├── statistical_validator.py      # Assumption + validity checks
│   ├── writing_quality.py            # Grammar + style composite
│   ├── peer_reviewer.py              # Adversarial review sub-agent
│   ├── reproducibility_audit.py     # Computation log verification
│   ├── plagiarism_detector.py        # sentence-transformers + MinHash
│   └── report_generator.py           # Quality report (YAML + readable)
│
├── orchestration/                      # Orchestration Layer
│   ├── __init__.py
│   ├── research_orchestrator.py      # Main orchestrator (extends Agent)
│   ├── phase_manager.py              # Phase transitions + tool loading
│   ├── sub_agent_dispatcher.py       # Sub-agent lifecycle management
│   ├── project_state.py              # ProjectState (YAML persistence)
│   ├── workspace_manager.py          # Workspace scaffolding
│   ├── session_resume.py             # Cross-session continuity
│   ├── approval_gates.py             # Human-in-the-loop gates
│   └── tool_registry.py              # Phase-aware tool registration
│
├── research_tools/                     # Research-specific Tool impls
│   ├── __init__.py
│   ├── project_tools.py              # project_init, project_status
│   ├── literature_tools.py           # search, download, summarize
│   ├── data_tools.py                 # load, clean, transform
│   ├── analysis_tools.py             # statistical methods
│   ├── writing_tools.py              # write_section, compile
│   ├── citation_tools.py             # add_citation, verify
│   ├── visualization_tools.py       # create_figure, export
│   └── quality_tools.py              # check_*, validate_*
│
└── config/
    ├── (existing configs)
    ├── research_config.yaml           # Research-specific configuration
    ├── mcp.json                       # MCP server definitions
    ├── system_prompts/
    │   ├── orchestrator.md            # Main orchestrator prompt
    │   ├── section_writer.md          # SectionWriter sub-agent
    │   ├── peer_reviewer.md           # PeerReviewer sub-agent
    │   ├── stat_validator.md          # StatValidator sub-agent
    │   └── citation_verifier.md       # CitationVerifier sub-agent
    └── dspy/
        ├── signatures.yaml            # DSPy signature definitions
        └── optimized/                 # MIPROv2 optimized prompts
```


---

## 4. Data Flow Diagram

```
                    ┌──────────────────────────────────┐
                    │         EXTERNAL SOURCES          │
                    ├──────────────────────────────────┤
                    │ BPS WebAPI (62 endpoints)         │
                    │ Semantic Scholar API              │
                    │ CrossRef API                      │
                    │ OpenAlex API                      │
                    │ CORE API (full-text)              │
                    │ Unpaywall (OA links)              │
                    │ arXiv API                         │
                    │ PubMed/MEDLINE                    │
                    └──────────┬───────────────────────┘
                               │
                    ┌──────────▼───────────────────────┐
                    │       INGESTION LAYER             │
                    │  Rate Limiter + Retry Logic       │
                    │  Response Cache (disk, TTL)       │
                    │  Format Detection + Routing       │
                    └──────────┬───────────────────────┘
                               │
              ┌────────────────┼────────────────────┐
              │                │                     │
    ┌─────────▼────┐  ┌───────▼──────┐  ┌──────────▼─────┐
    │  DOCUMENTS   │  │  DATASETS    │  │  METADATA      │
    │  (PDFs)      │  │  (CSV/JSON)  │  │  (BibTeX)      │
    └─────────┬────┘  └───────┬──────┘  └──────────┬─────┘
              │                │                     │
    ┌─────────▼────┐  ┌───────▼──────┐  ┌──────────▼─────┐
    │ Doc Process  │  │ Data Valid.  │  │ GROBID Extract │
    │ MinerU /     │  │ Pandera /    │  │ → references   │
    │ MarkItDown   │  │ Great Expect │  │   .bib         │
    └─────────┬────┘  └───────┬──────┘  └──────────┬─────┘
              │                │                     │
    ┌─────────▼────────────────▼─────────────────────▼─────┐
    │                  KNOWLEDGE LAYER                       │
    │  Chunking (Chonkie) → Dual Embeddings                │
    │  ┌─────────────┐    ┌──────────────────────┐         │
    │  │ SPECTER2    │    │ nomic-embed-text     │         │
    │  │ (paper-lvl) │    │ (chunk-level, 8192)  │         │
    │  └──────┬──────┘    └──────────┬───────────┘         │
    │         └──────────┬───────────┘                      │
    │                    ▼                                   │
    │          ┌──────────────────┐                         │
    │          │    LanceDB       │                         │
    │          │  (vector store)  │                         │
    │          └──────────────────┘                         │
    │                                                       │
    │  Entity Extraction (scispaCy) → Knowledge Graph       │
    │          ┌──────────────────┐                         │
    │          │   LightRAG /     │                         │
    │          │   NetworkX       │                         │
    │          └──────────────────┘                         │
    └──────────────────────────┬───────────────────────────┘
                               │
              ┌────────────────┼────────────────────┐
              │                │                     │
    ┌─────────▼────┐  ┌───────▼──────┐  ┌──────────▼─────┐
    │  PaperQA2    │  │  DSPy        │  │  Statistical   │
    │  (RAG Q&A)   │  │  Pipeline    │  │  Engine        │
    │              │  │  (optimized) │  │  (sandboxed)   │
    └─────────┬────┘  └───────┬──────┘  └──────────┬─────┘
              │                │                     │
              └────────────────┼────────────────────┘
                               │
                    ┌──────────▼───────────────────────┐
                    │       PAPER WRITING ENGINE        │
                    │  Section-by-section generation    │
                    │  Template application             │
                    │  Bibliography assembly            │
                    │  Figure/table placement           │
                    └──────────┬───────────────────────┘
                               │
                    ┌──────────▼───────────────────────┐
                    │       QUALITY GATE                │
                    │  Citation verification            │
                    │  Statistical validity             │
                    │  Writing quality                  │
                    │  Plagiarism check                 │
                    │  Peer review simulation           │
                    └──────────┬───────────────────────┘
                               │
                    ┌──────────▼───────────────────────┐
                    │       COMPILATION + OUTPUT        │
                    │  Tectonic/Typst → PDF             │
                    │  Pandoc → DOCX                    │
                    │  • paper.pdf (publication-ready)  │
                    │  • paper.docx (Word submission)   │
                    │  • supplementary.zip              │
                    │  • reproducibility_package.tar.gz │
                    └──────────────────────────────────┘
```

---

## 5. Phase-Gated Tool Loading

### Design Principle

LLMs degrade significantly with >20 tools. Each research phase loads only relevant tools (max 15), plus 5 persistent core tools.

### Persistent Tools (always loaded, 5 slots)

| Tool | Purpose |
|------|---------|
| `project_status` | View current project state |
| `read_file` | Read any project file |
| `write_file` | Write to project workspace |
| `transition_phase` | Move to next/previous phase |
| `request_approval` | Human-in-the-loop gate |

### Phase: PLAN (10 tools)

| Tool | Purpose |
|------|---------|
| `project_init` | Create new research project |
| `set_research_questions` | Define RQs + hypotheses |
| `choose_methodology` | Select statistical approach |
| `literature_quick_scan` | Rapid literature landscape |
| `outline_paper` | Generate paper structure |
| `identify_variables` | Define dependent/independent vars |
| `select_data_sources` | Choose BPS datasets + external |
| `define_scope` | Temporal/geographic boundaries |
| `estimate_timeline` | Project timeline estimation |
| `search_similar_papers` | Find methodological precedents |

### Phase: COLLECT (12 tools)

| Tool | Purpose |
|------|---------|
| `bps_search` | Search BPS statistical data |
| `bps_get_data` | Retrieve specific BPS datasets |
| `semantic_scholar_search` | Search academic papers |
| `crossref_lookup` | Verify/find papers by DOI |
| `openalex_search` | OpenAlex literature search |
| `download_paper` | Download PDF (Unpaywall/CORE) |
| `extract_paper_content` | Process PDF to structured text |
| `add_to_bibliography` | Add verified entry to .bib |
| `summarize_paper` | Generate paper summary |
| `cache_dataset` | Store processed data |
| `build_citation_network` | Construct citation graph |
| `synthesize_literature` | Thematic synthesis of papers |

### Phase: ANALYZE (13 tools)

| Tool | Purpose |
|------|---------|
| `python_repl` | Sandboxed Python execution |
| `descriptive_stats` | Summary statistics + distributions |
| `regression_analysis` | OLS/logistic/panel regression |
| `time_series_analysis` | ARIMA, VAR, cointegration |
| `hypothesis_test` | t-test, ANOVA, chi-square |
| `bayesian_analysis` | PyMC/Bambi posterior inference |
| `causal_analysis` | DoWhy causal effect estimation |
| `create_figure` | Publication-quality visualization |
| `create_table` | Academic table generation |
| `data_profiling` | Automated EDA report |
| `validate_data` | Schema + quality validation |
| `robustness_check` | Sensitivity analysis |
| `save_results` | Persist analysis outputs |

### Phase: WRITE (12 tools)

| Tool | Purpose |
|------|---------|
| `write_section` | Generate paper section |
| `update_section` | Revise existing section |
| `insert_citation` | Add \cite{} with verification |
| `insert_figure_ref` | Add figure reference + caption |
| `insert_table_ref` | Add table reference |
| `generate_abstract` | Create structured abstract |
| `latex_compile` | Compile to PDF (Tectonic/Typst) |
| `check_word_count` | Section/total word counts |
| `format_references` | Apply citation style |
| `coherence_check` | Cross-section consistency |
| `export_docx` | Generate Word document |
| `apply_template` | Apply journal template |

### Phase: REVIEW (11 tools)

| Tool | Purpose |
|------|---------|
| `verify_citations` | Batch DOI verification |
| `check_stat_validity` | Statistical assumption audit |
| `check_style` | LanguageTool + proselint |
| `simulate_peer_review` | Adversarial reviewer agent |
| `check_reproducibility` | Computation log audit |
| `detect_plagiarism` | Similarity detection |
| `suggest_revisions` | Generate revision plan |
| `check_formatting` | Journal compliance check |
| `generate_cover_letter` | Submission cover letter |
| `generate_response` | Reviewer response letter |
| `final_quality_report` | Comprehensive quality summary |

### Phase Transition Protocol

```python
class PhaseManager:
    """Manages research phase transitions with state persistence."""

    PHASE_ORDER = ["plan", "collect", "analyze", "write", "review"]

    async def transition(self, target_phase: str) -> PhaseTransitionResult:
        """
        1. Validate transition (sequential or back-one)
        2. Run phase completion checks
        3. Create checkpoint (serialize current state)
        4. Unload current phase tools
        5. Load target phase tools
        6. Update project.yaml
        7. Summarize context for new phase
        """
        current_idx = self.PHASE_ORDER.index(self.current_phase)
        target_idx = self.PHASE_ORDER.index(target_phase)
        if target_idx > current_idx + 1:
            raise PhaseSkipError("Cannot skip phases")

        checkpoint = await self.create_checkpoint()
        self.tool_registry.unload_phase(self.current_phase)
        self.tool_registry.load_phase(target_phase)
        summary = await self.summarize_for_phase(target_phase)

        return PhaseTransitionResult(
            from_phase=self.current_phase,
            to_phase=target_phase,
            checkpoint=checkpoint,
            context_summary=summary,
        )
```

---

## 6. Token Management Strategy

### Problem Statement

Academic papers are 5,000-10,000 words. With context (data, references, instructions), this exceeds any single context window. The existing agent has an 80K token limit with message summarization.

### Solution: Hierarchical Decomposition

```
Level 1: PROJECT LEVEL (persisted to disk)
├── project.yaml — full state (never in context)
├── Summaries of completed phases
└── Checkpoint files for each phase

Level 2: PHASE LEVEL (in orchestrator context)
├── Phase-specific system prompt
├── Relevant project state subset
├── Phase tools (max 15)
└── Running conversation (with summarization at 60K)

Level 3: TASK LEVEL (in sub-agent context)
├── Task-specific system prompt
├── Focused context (only what is needed)
├── Task tools (max 8)
└── Short conversation (max 20 steps)
```

### Context Budget Per Section Generation (80K window)

| Component | Tokens |
|-----------|--------|
| System prompt + role instructions | ~3,000 |
| Paper outline + current section spec | ~2,000 |
| Relevant data/findings (compressed) | ~15,000 |
| Adjacent section summaries (prev + next) | ~4,000 |
| Style guide + template requirements | ~3,000 |
| Key citation excerpts (RAG-retrieved) | ~8,000 |
| **TOTAL CONTEXT** | **~35,000** |
| **REMAINING FOR GENERATION** | **~45,000** |
| *(approx 11,000 words — more than sufficient)* | |

### Generation Workflow

```
Step 1: PLAN — Generate paper outline (fits in one window)
    Input:  Research questions + methodology + literature synthesis
    Output: outline.yaml with section specs, target word counts

Step 2: COLLECT — Build knowledge base (iterative, disk-persisted)
    Input:  Search queries derived from outline
    Output: references.bib + paper summaries + data files

Step 3: ANALYZE — Statistical analysis (sandboxed execution)
    Input:  Data files + methodology spec
    Output: results/*.json + figures/*.pdf

Step 4: WRITE — Section-by-section generation (sub-agent per section)
    Input:  Section spec + relevant data + adjacent summaries + citations
    Output: sections/*.tex (written to disk immediately)

Step 5: COHERENCE — Cross-section consistency pass
    Input:  Summaries of ALL sections (compressed)
    Output: Revision instructions per section

Step 6: REVIEW — Quality verification
    Input:  Full paper (section by section) + quality criteria
    Output: quality_report.yaml + revision_plan.yaml
```


---

## 7. Sub-Agent Architecture

### When to Spawn Sub-Agents

| Scenario | Sub-Agent | Reason | Model |
|----------|-----------|--------|-------|
| Writing a section | **SectionWriter** | Focused context + writer persona | Claude Sonnet |
| Reviewing paper | **PeerReviewer** | Must be adversarial (different from writer) | Claude Sonnet |
| Validating statistics | **StatValidator** | Specialized checking logic | GPT-4o |
| Verifying citations | **CitationVerifier** | Batch API calls + matching | GPT-4o-mini |
| Literature synthesis | **LitSynthesizer** | Thematic analysis across papers | Claude Sonnet |
| Data exploration | **DataExplorer** | Conversational EDA | GPT-4o |

### Sub-Agent Implementation

```python
from dataclasses import dataclass
from mini_agent.agent import Agent
from mini_agent.gateway.router import LLMRouter


@dataclass
class SubAgentConfig:
    """Configuration for a specialist sub-agent."""
    role: str
    system_prompt_file: str
    tools: list[str]
    model_preference: str
    max_steps: int = 20
    token_limit: int = 80_000
    temperature: float = 0.3


class SubAgentDispatcher:
    """Manages sub-agent lifecycle and context passing."""

    AGENT_CONFIGS = {
        "section_writer": SubAgentConfig(
            role="SectionWriter",
            system_prompt_file="config/system_prompts/section_writer.md",
            tools=["write_file", "read_file", "insert_citation",
                   "insert_figure_ref", "check_word_count"],
            model_preference="paper_writing",
            max_steps=15, temperature=0.4,
        ),
        "peer_reviewer": SubAgentConfig(
            role="PeerReviewer",
            system_prompt_file="config/system_prompts/peer_reviewer.md",
            tools=["read_file", "verify_citations",
                   "check_stat_validity", "check_style"],
            model_preference="peer_review",
            max_steps=20, temperature=0.2,
        ),
        "stat_validator": SubAgentConfig(
            role="StatValidator",
            system_prompt_file="config/system_prompts/stat_validator.md",
            tools=["python_repl", "read_file", "check_stat_validity"],
            model_preference="data_analysis",
            max_steps=15, temperature=0.1,
        ),
        "citation_verifier": SubAgentConfig(
            role="CitationVerifier",
            system_prompt_file="config/system_prompts/citation_verifier.md",
            tools=["crossref_lookup", "semantic_scholar_search",
                   "read_file", "write_file"],
            model_preference="citation_verify",
            max_steps=30, temperature=0.0,
        ),
    }

    async def dispatch(self, agent_type: str, task: str,
                       context: dict, parent_project: "ProjectState") -> "SubAgentResult":
        """Dispatch a sub-agent with focused context."""
        config = self.AGENT_CONFIGS[agent_type]
        system_prompt = self._load_prompt(config.system_prompt_file)
        tools = self.tool_registry.resolve(config.tools)
        llm_client = self.router.get_client(config.model_preference)

        agent = Agent(
            llm_client=llm_client,
            system_prompt=system_prompt,
            tools=tools,
            max_steps=config.max_steps,
            token_limit=config.token_limit,
        )

        context_str = self._format_context(context, config.role)
        agent.add_user_message(f"{context_str}\n\n---\n\nTask: {task}")
        result = await agent.run()

        return SubAgentResult(
            agent_type=agent_type,
            output=result,
            artifacts=self._collect_artifacts(parent_project),
            token_usage=agent.token_usage,
            cost=self.router.get_cost(agent.token_usage),
        )
```

### Communication Pattern

**KEY PRINCIPLE:** Sub-agents communicate via FILES, not messages. The orchestrator passes file paths, not content, between agents.

```
Orchestrator
    ├── SectionWriter("Write Introduction")
    │     Context: outline, lit synthesis, adjacent summaries
    │     Output:  sections/01_introduction.tex
    │
    ├── PeerReviewer("Review Introduction")
    │     Context: section text, quality criteria
    │     Output:  review_feedback.yaml
    │
    ├── SectionWriter("Revise based on feedback")
    │     Context: original + feedback + revision plan
    │     Output:  sections/01_introduction.tex (v2)
    │
    └── (continues for each section...)
```

---

## 8. DSPy Pipeline Design

### Overview

DSPy provides optimizable, composable modules for each research step. Instead of hand-crafted prompts, we define typed signatures and let MIPROv2 optimize them.

### Signatures

```python
import dspy

class GenerateSearchQueries(dspy.Signature):
    """Generate diverse academic search queries from a research question."""
    research_question: str = dspy.InputField(desc="The research question")
    methodology_hint: str = dspy.InputField(desc="Preferred methodology")
    search_queries: list[str] = dspy.OutputField(
        desc="5-8 diverse search queries covering different aspects"
    )

class AssessRelevance(dspy.Signature):
    """Assess whether a paper is relevant to the research question."""
    research_question: str = dspy.InputField()
    paper_title: str = dspy.InputField()
    paper_abstract: str = dspy.InputField()
    relevance_score: float = dspy.OutputField(desc="0.0-1.0 relevance score")
    reasoning: str = dspy.OutputField(desc="Brief justification")

class ExtractEvidence(dspy.Signature):
    """Extract structured evidence from a paper."""
    research_question: str = dspy.InputField()
    paper_content: str = dspy.InputField(desc="Full or relevant section text")
    paper_metadata: str = dspy.InputField(desc="Author, year, title, DOI")
    evidence: list[dict] = dspy.OutputField(
        desc="List of {claim, support, methodology, limitations, page}"
    )

class SynthesizeEvidence(dspy.Signature):
    """Synthesize evidence from multiple papers into thematic findings."""
    research_question: str = dspy.InputField()
    evidence_items: list[dict] = dspy.InputField()
    synthesis: str = dspy.OutputField(desc="Thematic synthesis paragraph")
    themes: list[str] = dspy.OutputField(desc="Identified themes")
    gaps: list[str] = dspy.OutputField(desc="Research gaps identified")

class PlanAnalysis(dspy.Signature):
    """Plan statistical analysis for given data and research question."""
    research_question: str = dspy.InputField()
    data_description: str = dspy.InputField(desc="Variables, types, N")
    methodology: str = dspy.InputField()
    analysis_plan: str = dspy.OutputField(desc="Step-by-step plan")
    python_code: str = dspy.OutputField(desc="Python code to execute")
    assumptions_to_check: list[str] = dspy.OutputField()

class InterpretResults(dspy.Signature):
    """Interpret statistical results in research context."""
    research_question: str = dspy.InputField()
    statistical_output: str = dspy.InputField(desc="Raw output")
    methodology: str = dspy.InputField()
    interpretation: str = dspy.OutputField(desc="Plain-language interpretation")
    apa_report: str = dspy.OutputField(desc="APA-formatted report")
    limitations: list[str] = dspy.OutputField()

class WriteSectionDraft(dspy.Signature):
    """Write a section of an academic paper."""
    section_spec: str = dspy.InputField(desc="Section name, target words")
    outline_points: list[str] = dspy.InputField(desc="Key points to cover")
    evidence: str = dspy.InputField(desc="Relevant evidence and citations")
    adjacent_context: str = dspy.InputField(desc="Prev/next section summaries")
    style_guide: str = dspy.InputField(desc="Journal style requirements")
    section_text: str = dspy.OutputField(desc="LaTeX-formatted section text")
```

### Modules

```python
class LiteratureReviewModule(dspy.Module):
    """End-to-end literature review pipeline."""

    def __init__(self):
        self.query_gen = dspy.ChainOfThought(GenerateSearchQueries)
        self.relevance = dspy.ChainOfThought(AssessRelevance)
        self.extract = dspy.ChainOfThought(ExtractEvidence)
        self.synthesize = dspy.ChainOfThought(SynthesizeEvidence)

    def forward(self, research_question: str, methodology: str = ""):
        queries = self.query_gen(
            research_question=research_question,
            methodology_hint=methodology,
        )
        papers = self._search_papers(queries.search_queries)

        relevant = []
        for paper in papers:
            score = self.relevance(
                research_question=research_question,
                paper_title=paper["title"],
                paper_abstract=paper["abstract"],
            )
            if score.relevance_score > 0.6:
                relevant.append(paper)

        all_evidence = []
        for paper in relevant[:20]:
            ev = self.extract(
                research_question=research_question,
                paper_content=paper["content"],
                paper_metadata=paper["metadata"],
            )
            all_evidence.extend(ev.evidence)

        synthesis = self.synthesize(
            research_question=research_question,
            evidence_items=all_evidence,
        )
        return dspy.Prediction(
            synthesis=synthesis.synthesis,
            themes=synthesis.themes,
            gaps=synthesis.gaps,
            papers_reviewed=len(relevant),
        )


class StatisticalAnalysisModule(dspy.Module):
    """Statistical analysis with sandboxed execution."""

    def __init__(self):
        self.planner = dspy.ChainOfThought(PlanAnalysis)
        self.interpreter = dspy.ChainOfThought(InterpretResults)

    def forward(self, research_question, data_desc, methodology):
        plan = self.planner(
            research_question=research_question,
            data_description=data_desc,
            methodology=methodology,
        )
        result = self.sandbox.execute(plan.python_code)
        interp = self.interpreter(
            research_question=research_question,
            statistical_output=result.output,
            methodology=methodology,
        )
        return dspy.Prediction(
            analysis_plan=plan.analysis_plan,
            code=plan.python_code,
            raw_output=result.output,
            interpretation=interp.interpretation,
            apa_report=interp.apa_report,
            limitations=interp.limitations,
        )
```

### Optimization with MIPROv2

```python
from dspy.teleprompt import MIPROv2

def research_quality_metric(example, prediction, trace=None):
    scores = []
    scores.append(verify_citations(prediction.synthesis))
    scores.append(check_grounding(prediction.synthesis, prediction.evidence))
    scores.append(len(prediction.themes) / example.expected_themes)
    return sum(scores) / len(scores)

optimizer = MIPROv2(
    metric=research_quality_metric,
    num_candidates=10,
    max_bootstrapped_demos=4,
    max_labeled_demos=8,
)
optimized = optimizer.compile(
    LiteratureReviewModule(),
    trainset=research_examples,
)
optimized.save("config/dspy/optimized/literature_review.json")
```

---

## 9. RAG Pipeline Design

### Architecture: PaperQA2 + LightRAG Hybrid

**Ingestion Flow:**

```
PDF --> MinerU --> Structured Sections
                    |
                    +-- Full paper --> SPECTER2 --> paper_embeddings (LanceDB)
                    |
                    +-- Sections --> Chonkie --> Chunks
                    |                (semantic, 512-1024 tokens)
                    |                    |
                    |                    +-- nomic-embed-text --> chunk_embeddings (LanceDB)
                    |
                    +-- Entities --> scispaCy --> NER --> LightRAG (Knowledge Graph)
                    |
                    +-- Metadata --> GROBID --> BibTeX
```

**Retrieval Routes:**

| Route | Method | Use Case |
|-------|--------|----------|
| **Paper Discovery** | Query -> SPECTER2 embed -> LanceDB (paper table) -> Top-K | "Find papers about X methodology" |
| **Evidence Retrieval** | Query -> nomic-embed -> LanceDB (chunk table) + BM25 hybrid -> Top-K | "What evidence supports claim Y?" |
| **Knowledge Graph** | Query -> Entity extraction -> LightRAG graph traversal | "How are concepts A and B related?" |
| **PaperQA2 Full** | Query -> PaperQA2 (search + gather + answer) -> Cited answer | Complex multi-paper questions |

### PaperQA2 Integration

```python
from paperqa import Settings, Docs, ask

class ScientificRAGEngine:
    """PaperQA2-based scientific question answering."""

    def __init__(self, project_path: Path):
        self.settings = Settings(
            llm="litellm/claude-sonnet-4-20250514",
            summary_llm="litellm/gpt-4o-mini",
            embedding="nomic-embed-text",
            answer_max_sources=8,
            evidence_k=15,
            max_concurrent=4,
        )
        self.docs = Docs()

    async def add_papers(self, pdf_paths: list[Path]):
        for path in pdf_paths:
            await self.docs.aadd(
                path,
                citation=self._get_citation(path),
                docname=path.stem,
            )

    async def query(self, question: str) -> "RAGAnswer":
        answer = await ask(question, docs=self.docs, settings=self.settings)
        return RAGAnswer(
            answer=answer.answer,
            confidence=answer.confidence,
            sources=[
                Source(citation=ctx.citation, text=ctx.text, relevance=ctx.score)
                for ctx in answer.contexts
            ],
        )
```

### LightRAG Knowledge Graph

```python
from lightrag import LightRAG, QueryParam

class KnowledgeGraphEngine:
    """LightRAG-based knowledge graph extraction and querying."""

    def __init__(self, working_dir: Path):
        self.rag = LightRAG(
            working_dir=str(working_dir),
            llm_model_func=self._litellm_complete,
            embedding_func=self._nomic_embed,
        )

    async def ingest_paper(self, text: str, metadata: dict):
        await self.rag.ainsert(text)

    async def query(self, question: str, mode: str = "hybrid") -> str:
        """
        Modes: local (entity-centric), global (theme-centric),
               hybrid (combined), naive (direct RAG)
        """
        return await self.rag.aquery(question, param=QueryParam(mode=mode))
```


---

## 10. Embedding Strategy

### Dual Embedding Architecture

| Aspect | SPECTER2 (Paper-Level) | nomic-embed-text (Chunk-Level) |
|--------|------------------------|-------------------------------|
| **Model** | allenai/specter2 | nomic-ai/nomic-embed-text-v1.5 |
| **Input** | Title + Abstract | Text chunks (512-1024 tokens) |
| **Dimensions** | 768 | 768 (Matryoshka: truncatable to 256/128) |
| **Context** | 512 tokens | 8192 tokens |
| **Training** | Citation graph (S2ORC) | Contrastive on diverse text |
| **Strength** | Topical similarity between papers | Semantic similarity within text |

### LanceDB Schema: Papers Table

```python
import lancedb
import pyarrow as pa

papers_schema = pa.schema([
    pa.field("id", pa.string()),           # DOI or hash
    pa.field("vector", pa.list_(pa.float32(), 768)),  # SPECTER2
    pa.field("title", pa.string()),
    pa.field("abstract", pa.string()),
    pa.field("authors", pa.list_(pa.string())),
    pa.field("year", pa.int32()),
    pa.field("doi", pa.string()),
    pa.field("citation_count", pa.int32()),
    pa.field("bibtex_key", pa.string()),
    pa.field("source", pa.string()),       # "semantic_scholar", "crossref", etc.
])
```

### LanceDB Schema: Chunks Table

```python
chunks_schema = pa.schema([
    pa.field("id", pa.string()),           # hash
    pa.field("vector", pa.list_(pa.float32(), 768)),  # nomic-embed-text
    pa.field("text", pa.string()),
    pa.field("paper_id", pa.string()),     # FK to papers table
    pa.field("section", pa.string()),      # Introduction, Methods, etc.
    pa.field("chunk_index", pa.int32()),
    pa.field("token_count", pa.int32()),
    pa.field("entities", pa.list_(pa.string())),  # scispaCy NER
    pa.field("bibtex_key", pa.string()),
])
```

### Retrieval Strategy

```python
class DualEmbeddingRetriever:
    """Hybrid retrieval using both embedding spaces."""

    def __init__(self, db: lancedb.DBConnection):
        self.papers_table = db.open_table("papers")
        self.chunks_table = db.open_table("chunks")

    async def find_similar_papers(self, query: str, k: int = 10):
        """Use SPECTER2 for paper-level similarity."""
        query_vec = await self.specter2.embed(query)
        return self.papers_table.search(query_vec).limit(k).to_pandas()

    async def find_evidence(self, query: str, k: int = 20):
        """Use nomic-embed for chunk-level evidence retrieval."""
        query_vec = await self.nomic.embed(query)
        # Hybrid: vector + BM25 keyword search
        vector_results = self.chunks_table.search(query_vec).limit(k * 2)
        keyword_results = self.chunks_table.search(query, query_type="fts").limit(k)
        return self._reciprocal_rank_fusion(vector_results, keyword_results, k)

    def _reciprocal_rank_fusion(self, vec_results, kw_results, k):
        """Combine vector and keyword results with RRF."""
        scores = {}
        for rank, row in enumerate(vec_results):
            scores[row["id"]] = scores.get(row["id"], 0) + 1 / (60 + rank)
        for rank, row in enumerate(kw_results):
            scores[row["id"]] = scores.get(row["id"], 0) + 1 / (60 + rank)
        sorted_ids = sorted(scores, key=scores.get, reverse=True)[:k]
        return [self._get_chunk(id) for id in sorted_ids]
```

---

## 11. Safety & Integrity

### Citation Integrity Pipeline (Zero Tolerance)

```
1. Literature Agent retrieves papers
   --> Stores in references.bib with DOIs

2. Writing Agent inserts \cite{key}
   --> Can ONLY cite keys in references.bib
   --> NEVER generates citations from memory

3. CitationVerifier (post-generation)
   --> Resolves every DOI via CrossRef API
   --> Matches title/author/year
   --> Flags unverifiable citations

4. Quality Gate
   --> BLOCKS compilation if unverified
   --> Reports which citations failed

RULE: 0 unverified citations = PASS
      1+ unverified = BLOCK
```

### Sandboxed Execution

```
┌─────────────────────────────────────────────────────────────┐
│ DOCKER SANDBOX (or E2B Cloud Sandbox)                        │
├─────────────────────────────────────────────────────────────┤
│ Network:     DISABLED                                        │
│ Filesystem:  READ-ONLY (except /output and /tmp)            │
│ Memory:      2GB limit                                       │
│ CPU:         50% of one core                                 │
│ Timeout:     120 seconds                                     │
│ User:        non-root (sandbox)                              │
│ Runtime:     No pip/setuptools (pre-installed only)          │
│ Pre-installed: numpy, pandas, scipy, statsmodels,           │
│   matplotlib, seaborn, linearmodels, arch, pingouin,        │
│   pymc, bambi, arviz, dowhy, causalml, lifelines,           │
│   ydata-profiling, great-expectations, pandera              │
└─────────────────────────────────────────────────────────────┘
```

### Human-in-the-Loop Gates

| Decision | Why Human Required |
|----------|-------------------|
| Methodology selection | Which statistical method to use |
| Variable selection | Include/exclude decisions affect results |
| Outlier removal | Removing data points changes conclusions |
| Interpretation of results | What findings "mean" is subjective |
| Scope changes | Narrowing/broadening research questions |
| Final paper submission | Researcher takes responsibility |

### Reproducibility Guarantees

```python
class ReproducibilityLog:
    """Append-only computation log for full reproducibility."""

    def log_computation(self, entry: ComputationEntry):
        """Every statistical computation is logged."""
        self.entries.append(ComputationEntry(
            timestamp=datetime.utcnow(),
            tool="regression_analysis",
            inputs={
                "data_file": "data/processed/panel_data.csv",
                "data_sha256": "abc123...",
                "model": "OLS",
                "dependent_var": "gini_ratio",
                "independent_vars": ["gdp_per_capita", "education_index"],
            },
            code="import statsmodels.api as sm\n...",
            outputs={
                "r_squared": 0.73,
                "coefficients": {...},
                "p_values": {...},
            },
            output_files=["results/regression_01.json"],
            random_seed=42,
            package_versions={"statsmodels": "0.14.1", "pandas": "2.1.4"},
        ))
```

---

## 12. Project State Schema

```yaml
# project.yaml — Single source of truth for research project
project:
  id: "uuid-v4"
  title: "Impact of Digital Infrastructure on Regional Economic Growth in Indonesia"
  created: "2025-01-15T10:00:00Z"
  last_session: "2025-01-18T14:30:00Z"
  target_journal: "Bulletin of Indonesian Economic Studies"
  template: "elsevier"
  language: "en"

phase: "analyze"  # Current active phase
phase_history:
  - phase: "plan"
    started: "2025-01-15T10:00:00Z"
    completed: "2025-01-15T12:00:00Z"
    checkpoint: "checkpoints/plan_complete.json"
  - phase: "collect"
    started: "2025-01-15T12:05:00Z"
    completed: "2025-01-16T18:00:00Z"
    checkpoint: "checkpoints/collect_complete.json"
  - phase: "analyze"
    started: "2025-01-16T18:05:00Z"
    completed: null  # In progress

research_questions:
  - id: "rq1"
    question: "How does digital infrastructure investment affect regional GDP growth?"
    hypothesis: "Positive relationship, stronger in urban areas"
    status: "in_progress"  # pending | in_progress | answered
    findings_ref: "analysis/results/rq1_findings.json"
  - id: "rq2"
    question: "Does the effect vary by province development level?"
    hypothesis: "Heterogeneous effects across development tiers"
    status: "pending"

methodology:
  approach: "panel_data_regression"
  model: "Fixed Effects with clustered standard errors"
  robustness:
    - "Random Effects (Hausman test)"
    - "GMM (Arellano-Bond)"
    - "Spatial panel (contiguity weights)"
  time_period: "2015-2023"
  geographic_scope: "34 provinces"
  unit_of_analysis: "province-year"

data_inventory:
  - source: "bps"
    dataset: "gini_ratio_province"
    var_id: 28
    years: [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    path: "data/processed/gini_province.csv"
    sha256: "a1b2c3d4..."
    rows: 306
    columns: 5
  - source: "bps"
    dataset: "pdrb_per_capita"
    var_id: 108
    years: [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    path: "data/processed/pdrb_capita.csv"
    sha256: "e5f6g7h8..."
    rows: 306
    columns: 4

literature:
  total_papers: 47
  key_papers: 12
  bib_file: "literature/references.bib"
  verified: true
  last_search: "2025-01-16T15:00:00Z"
  themes:
    - "Digital divide and economic growth"
    - "Infrastructure investment multipliers"
    - "Regional convergence in developing countries"

paper:
  outline_file: "writing/outline.yaml"
  target_words: 8000
  sections:
    abstract:
      status: "pending"
      path: "writing/sections/00_abstract.tex"
      target_words: 250
    introduction:
      status: "draft_v2"
      path: "writing/sections/01_introduction.tex"
      actual_words: 1200
      target_words: 1500
    literature_review:
      status: "draft_v1"
      path: "writing/sections/02_literature.tex"
      actual_words: 2500
      target_words: 2000
    methodology:
      status: "in_progress"
      path: "writing/sections/03_methodology.tex"
      actual_words: 800
      target_words: 1500
    results:
      status: "pending"
      path: "writing/sections/04_results.tex"
      target_words: 2000
    discussion:
      status: "pending"
      path: "writing/sections/05_discussion.tex"
      target_words: 1500
    conclusion:
      status: "pending"
      path: "writing/sections/06_conclusion.tex"
      target_words: 500

quality:
  last_run: "2025-01-18T14:00:00Z"
  citation_verification: "pass"  # pass | fail | not_run
  statistical_validity: "pass"
  style_compliance: "3 warnings"
  plagiarism_score: 0.02
  reproducibility: "pass"

cost:
  total_usd: 4.72
  breakdown:
    claude_sonnet: 3.10
    gpt_4o: 0.95
    gpt_4o_mini: 0.42
    embeddings: 0.25
  token_usage:
    input: 1_250_000
    output: 380_000
```

---

## 13. Workspace Structure

```
research_projects/
└── {project_id}/
    ├── project.yaml              # Master state (single source of truth)
    ├── .research_log             # Append-only decision log
    ├── .lancedb/                 # Vector store (embedded)
    │   ├── papers.lance          # Paper-level embeddings
    │   └── chunks.lance          # Chunk-level embeddings
    │
    ├── data/
    │   ├── raw/                  # Immutable original data (never modified)
    │   │   ├── bps_gini_2015_2023.json
    │   │   └── bps_pdrb_2015_2023.json
    │   ├── processed/            # Cleaned, merged datasets
    │   │   ├── panel_data.csv
    │   │   └── processing_log.yaml
    │   └── cache/                # API response cache (.gitignore)
    │
    ├── literature/
    │   ├── references.bib        # BibTeX (single source of truth)
    │   ├── papers/               # Downloaded PDFs (.gitignore)
    │   │   ├── smith2020.pdf
    │   │   └── jones2021.pdf
    │   ├── summaries/            # Per-paper extracted summaries
    │   │   ├── smith2020.yaml
    │   │   └── jones2021.yaml
    │   ├── synthesis.yaml        # Literature themes + gaps
    │   └── knowledge_graph/      # LightRAG working directory
    │
    ├── analysis/
    │   ├── scripts/              # Reproducible analysis scripts
    │   │   ├── 01_descriptive.py
    │   │   ├── 02_regression.py
    │   │   ├── 03_robustness.py
    │   │   └── 04_visualization.py
    │   ├── results/              # Structured outputs (JSON)
    │   │   ├── descriptive_stats.json
    │   │   ├── regression_01.json
    │   │   └── rq1_findings.json
    │   ├── figures/              # Generated visualizations
    │   │   ├── fig1_trend.pdf
    │   │   ├── fig2_scatter.pdf
    │   │   └── fig3_coefficients.pdf
    │   └── computation_log.yaml  # Full reproducibility log
    │
    ├── writing/
    │   ├── outline.yaml          # Paper structure + section specs
    │   ├── sections/             # Individual section drafts (.tex)
    │   │   ├── 00_abstract.tex
    │   │   ├── 01_introduction.tex
    │   │   ├── 02_literature.tex
    │   │   ├── 03_methodology.tex
    │   │   ├── 04_results.tex
    │   │   ├── 05_discussion.tex
    │   │   └── 06_conclusion.tex
    │   ├── main.tex              # Master file (\input{sections/...})
    │   ├── preamble.tex          # LaTeX packages/config
    │   └── compiled/             # Output PDF/DOCX
    │       ├── paper.pdf
    │       └── paper.docx
    │
    ├── review/
    │   ├── quality_report.yaml   # Quality gate results
    │   ├── peer_review_sim.yaml  # Simulated reviewer feedback
    │   ├── revision_plan.yaml    # Planned revisions
    │   └── cover_letter.tex      # Submission cover letter
    │
    └── checkpoints/              # Phase completion snapshots
        ├── plan_complete.json
        ├── collect_complete.json
        └── analyze_complete.json
```

---

## 14. MCP Configuration

```json
{
  "mcpServers": {
    "bps-stat": {
      "command": "python",
      "args": ["-m", "mini_agent.bps_mcp_server"],
      "env": {
        "BPS_API_KEY": "${BPS_API_KEY}"
      }
    },
    "paper-search": {
      "command": "npx",
      "args": ["-y", "@anthropic/paper-search-mcp"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": "${SEMANTIC_SCHOLAR_API_KEY}",
        "CROSSREF_EMAIL": "${CROSSREF_EMAIL}",
        "CORE_API_KEY": "${CORE_API_KEY}"
      }
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
        "OVERLEAF_TOKEN": "${OVERLEAF_TOKEN}"
      }
    },
    "jupyter": {
      "command": "npx",
      "args": ["-y", "@anthropic/jupyter-mcp"],
      "env": {
        "JUPYTER_TOKEN": "${JUPYTER_TOKEN}"
      }
    },
    "mcp-pdf": {
      "command": "npx",
      "args": ["-y", "mcp-pdf"],
      "env": {}
    },
    "qdrant": {
      "command": "npx",
      "args": ["-y", "qdrant-mcp"],
      "env": {
        "QDRANT_URL": "${QDRANT_URL}",
        "QDRANT_API_KEY": "${QDRANT_API_KEY}"
      }
    },
    "neo4j": {
      "command": "npx",
      "args": ["-y", "neo4j-mcp"],
      "env": {
        "NEO4J_URI": "${NEO4J_URI}",
        "NEO4J_USER": "${NEO4J_USER}",
        "NEO4J_PASSWORD": "${NEO4J_PASSWORD}"
      }
    },
    "markitdown": {
      "command": "npx",
      "args": ["-y", "markitdown-mcp"],
      "env": {}
    },
    "rmcp": {
      "command": "Rscript",
      "args": ["--vanilla", "-e", "rmcp::serve()"],
      "env": {
        "R_LIBS_USER": "${R_LIBS_USER}"
      }
    }
  }
}
```

---

## 15. Configuration Extension

```yaml
# research_config.yaml
research:
  # Phase configuration
  phases:
    max_tools_per_phase: 15
    persistent_tools: 5
    auto_checkpoint: true
    allow_phase_skip: false

  # LLM Gateway
  gateway:
    provider: "litellm"
    default_model: "claude-sonnet-4-20250514"
    fallback_chain:
      - "claude-sonnet-4-20250514"
      - "gpt-4o"
      - "gemini-1.5-pro"
    semantic_cache:
      enabled: true
      similarity_threshold: 0.95
      backend: "lancedb"
    cost_tracking:
      enabled: true
      budget_alert_usd: 10.0
      hard_limit_usd: 50.0

  # Sandbox configuration
  sandbox:
    provider: "docker"  # "docker" or "e2b"
    docker:
      image: "research-agent-sandbox:latest"
      memory_limit: "2g"
      cpu_quota: 50000
      timeout_seconds: 120
      network_disabled: true
      read_only_root: true
    e2b:
      template: "research-sandbox"
      timeout_seconds: 300

  # Academic API configuration
  apis:
    semantic_scholar:
      api_key: "${SEMANTIC_SCHOLAR_API_KEY}"
      rate_limit_rps: 3
      cache_ttl_days: 30
    crossref:
      polite_email: "${CROSSREF_EMAIL}"
      rate_limit_rps: 50
      cache_ttl_days: 30
    openalex:
      api_key: "${OPENALEX_API_KEY}"
      rate_limit_rps: 10
      cache_ttl_days: 7
    core:
      api_key: "${CORE_API_KEY}"
      rate_limit_rps: 1
      cache_ttl_days: 30
    unpaywall:
      email: "${UNPAYWALL_EMAIL}"
      rate_limit_rps: 10

  # Document processing
  document_processing:
    pdf_processor: "mineru"  # "mineru" or "markitdown"
    grobid_url: "http://localhost:8070"
    chunk_size_tokens: 768
    chunk_overlap_tokens: 128
    chunking_strategy: "semantic"  # "semantic" or "fixed"

  # Embedding configuration
  embeddings:
    paper_level:
      model: "allenai/specter2"
      dimensions: 768
      batch_size: 32
    chunk_level:
      model: "nomic-ai/nomic-embed-text-v1.5"
      dimensions: 768
      batch_size: 64
      prefix: "search_document: "
    query_prefix: "search_query: "

  # Vector store
  vectorstore:
    provider: "lancedb"
    path: ".lancedb"
    metric: "cosine"

  # Knowledge graph
  knowledge_graph:
    provider: "lightrag"  # "lightrag" or "neo4j"
    working_dir: "literature/knowledge_graph"

  # Paper writing configuration
  paper:
    default_template: "elsevier"
    compiler: "tectonic"  # "tectonic" or "typst" or "latexmk"
    figure_dpi: 300
    figure_format: "pdf"
    table_format: "booktabs"
    citation_style: "apa"
    max_abstract_words: 250

  # Quality gate configuration
  quality:
    citation_verification: true
    statistical_validity: true
    style_check: true
    plagiarism_check: true
    reproducibility_audit: true
    min_citation_density: 2  # per paragraph in intro/discussion
    max_unverified_citations: 0  # zero tolerance
    max_grammar_warnings: 5
    max_style_issues: 3
    plagiarism_threshold: 0.05  # 5% max similarity

  # Human approval gates
  approval_gates:
    methodology_selection: true
    variable_selection: true
    outlier_removal: true
    result_interpretation: true
    scope_changes: true
    final_submission: true

  # Observability
  observability:
    prometheus:
      enabled: true
      port: 9090
      metrics:
        - research_phase_duration_seconds
        - research_tool_calls_total
        - research_tokens_used_total
        - research_cost_usd_total
        - research_citations_verified_total
        - research_quality_score
    opentelemetry:
      enabled: true
      endpoint: "${OTEL_ENDPOINT}"
      service_name: "bps-research-agent"
    logging:
      level: "INFO"
      format: "structured"
      file: "logs/research_agent.jsonl"
```

---

## 16. Deployment & Infrastructure

### Docker Compose (Development)

```yaml
version: "3.9"
services:
  research-agent:
    build: .
    volumes:
      - ./research_projects:/app/research_projects
      - ./config:/app/config
    environment:
      - ANTHROPIC_API_KEY
      - OPENAI_API_KEY
      - SEMANTIC_SCHOLAR_API_KEY
      - CROSSREF_EMAIL
    ports:
      - "8080:8080"   # ACP server
      - "9090:9090"   # Prometheus metrics

  grobid:
    image: lfoppiano/grobid:0.8.0
    ports:
      - "8070:8070"

  sandbox:
    build: ./analysis/sandbox
    network_mode: "none"
    read_only: true
    mem_limit: 2g
    cpus: 0.5
    tmpfs:
      - /tmp:size=512m

  neo4j:
    image: neo4j:5-community
    environment:
      - NEO4J_AUTH=neo4j/research_password
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data

volumes:
  neo4j_data:
```

### Sandbox Dockerfile

```dockerfile
FROM python:3.11-slim

# Install scientific stack (no pip at runtime)
RUN pip install --no-cache-dir \
    numpy==1.26.4 \
    pandas==2.1.4 \
    scipy==1.12.0 \
    statsmodels==0.14.1 \
    matplotlib==3.8.2 \
    seaborn==0.13.1 \
    linearmodels==6.0 \
    arch==6.3.0 \
    pingouin==0.5.4 \
    pymc==5.10.3 \
    bambi==0.13.0 \
    arviz==0.17.0 \
    dowhy==0.11.1 \
    causalml==0.15.0 \
    lifelines==0.28.0 \
    ydata-profiling==4.6.4 \
    great-expectations==0.18.8 \
    pandera==0.18.0 \
    scikit-learn==1.4.0 \
    && pip cache purge \
    && rm -rf /root/.cache

# Remove pip to prevent runtime installs
RUN pip uninstall -y pip setuptools wheel

# Create non-root user
RUN useradd -m -s /bin/bash sandbox
USER sandbox
WORKDIR /workspace

# Read-only filesystem except /output and /tmp
VOLUME ["/output"]
```

### Production Considerations

| Concern | Solution |
|---------|----------|
| **Secrets** | Environment variables via vault (never in config files) |
| **Scaling** | Stateless agent + persistent workspace on shared storage |
| **Cost control** | Per-project budget with hard limits in gateway |
| **Monitoring** | Prometheus + Grafana dashboards for research metrics |
| **Backup** | project.yaml + .lancedb + literature/ backed up daily |
| **Multi-user** | Project isolation via workspace directories |
| **Rate limits** | Centralized rate limiter with token bucket per API |
| **Caching** | Disk-based response cache with configurable TTL |

---

## Design Decisions Summary

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Hybrid orchestrator (not pure multi-agent) | Preserves existing 417 tests, avoids coordination overhead |
| 2 | Phase-gated tool loading (max 15) | LLMs degrade past ~20 tools |
| 3 | Hierarchical paper generation | Full paper exceeds token limits |
| 4 | Verify-before-use citations | Zero tolerance for hallucinated references |
| 5 | Docker-based code execution | Security isolation for arbitrary code |
| 6 | Dual embedding strategy | Paper discovery vs. evidence retrieval are different tasks |
| 7 | DSPy over hand-crafted prompts | Optimizable, composable, measurable |
| 8 | LanceDB over Qdrant/Pinecone | Serverless, embedded, no infrastructure |
| 9 | PaperQA2 + LightRAG hybrid | Best-in-class scientific RAG + knowledge graphs |
| 10 | LiteLLM gateway | Multi-model routing, cost optimization, fallbacks |
| 11 | File-based sub-agent communication | Avoids context pollution, enables resume |
| 12 | Append-only computation log | Full reproducibility without overhead |

---

*This document is the definitive architecture reference for the BPS Academic Research Agent v1.0. All implementation must conform to the structures, patterns, and constraints defined herein.*
