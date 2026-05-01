# BPS Academic Research Agent — FINAL Transformation Roadmap

**Version:** 2.0 (Final)  
**Created:** 2025-07-14  
**Last Updated:** 2025-07-15  
**Status:** Approved for Implementation  
**Target:** Transform BPS Stat Agent v0.2.0 → BPS Academic Research Agent v1.0  
**Architecture:** Hybrid Orchestrator + Phase-Gated + DSPy Pipeline  

---

## 1. Vision Statement

Transform the existing **BPS Statistical Data Agent v0.2.0** (62 MCP tools for Indonesian statistical data retrieval) into a **full-stack Academic Research AI Agent v1.0** that autonomously:

1. **Searches** statistical data from BPS and 22+ academic databases (existing ✅ + expanded)
2. **Processes** documents — PDFs, papers, datasets — into structured knowledge
3. **Analyzes** data with production-grade statistical methods (frequentist + Bayesian + causal)
4. **Synthesizes** literature with superhuman RAG and knowledge graphs
5. **Writes** production-ready journal papers (LaTeX/Typst/DOCX) with verified citations
6. **Reviews** work through automated quality gates and adversarial peer review

**Design Principles:**
- **Zero hallucination citations** — Every reference verified against real APIs before inclusion
- **Reproducible analysis** — Every computation logged with inputs, outputs, and hashes
- **Phase-gated complexity** — Maximum 15 tools visible per phase to prevent cognitive overload
- **MCP-first architecture** — Leverage existing MCP servers before building custom tools
- **Human-in-the-loop** — Approval gates at methodology, interpretation, and submission decisions

**Inspiration:**
- AI Scientist v2 (Sakana AI) — End-to-end ML paper generation
- Robin (FutureHouse) — Scientific discovery automation
- PaperQA2 (FutureHouse) — Superhuman scientific literature QA
- Anthropic Multi-Agent Research System — Production multi-agent architecture
- OpenScholar (Allen AI) — Scientific literature synthesis

---

## 2. Architecture Pattern

### Hybrid Orchestrator + Phase-Gated Specialists + DSPy Pipeline

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR AGENT (Main Loop)                         │
│              Existing agent loop + Phase Manager + DSPy Modules                │
│                                                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   PLAN   │→ │ COLLECT  │→ │ ANALYZE  │→ │  WRITE   │→ │  REVIEW  │      │
│  │  phase   │  │  phase   │  │  phase   │  │  phase   │  │  phase   │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
│       │             │             │             │             │               │
│  [5 tools]    [18 tools]    [15 tools]    [12 tools]    [8 tools]           │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                    MCP SERVER LAYER (Plug-and-Play)                   │     │
│  │  paper-search │ zotero │ overleaf │ jupyter │ rmcp │ neo4j │ qdrant │     │
│  │  mcp-pdf │ markitdown │ pubmed │ elicit │ chroma │ ...              │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                    SUB-AGENT POOL (Spawned on demand)                 │     │
│  │  • SectionWriter — Per-section focused context window                │     │
│  │  • StatValidator — Checks methodology, assumptions, math             │     │
│  │  • PeerReviewer — Adversarial prompt, different persona from writer  │     │
│  │  • CitationVerifier — Validates ALL references against live APIs     │     │
│  │  • LiteratureSynthesizer — Cross-paper theme extraction              │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐     │
│  │                    INFRASTRUCTURE LAYER                               │     │
│  │  LiteLLM (multi-provider) │ DSPy (optimizable pipelines)            │     │
│  │  LanceDB (vectors) │ LightRAG (knowledge graph) │ E2B (sandbox)     │     │
│  │  Great Expectations (data quality) │ Pandera (validation)            │     │
│  └─────────────────────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM Gateway | LiteLLM | Multi-provider, cost tracking, fallback routing, 100+ models |
| Pipeline Framework | DSPy | Optimizable prompts, typed signatures, automatic few-shot |
| Vector Store | LanceDB + Qdrant MCP | Serverless local + managed cloud option |
| Knowledge Graph | LightRAG + Neo4j MCP | Outperforms GraphRAG; Neo4j for complex queries |
| Code Execution | E2B + Docker fallback | Cloud sandboxes (fast) + local Docker (offline) |
| Document Processing | MinerU + MarkItDown | Best PDF parsing + universal file conversion |
| Paper Compilation | Typst (primary) + Tectonic (LaTeX) | ms compilation + zero-config LaTeX |
| Embeddings | SPECTER2 + nomic-embed-text | Scientific domain + general purpose |
| Citation Format | citeproc-py + habanero | CSL processing + CrossRef API |

---

## 3. Phase Breakdown

---

### Phase 0: Quick Wins — MCP Server Integration (Week 0)

> **CAN DO TODAY — Zero custom code required!**

**Goal:** Immediately expand capabilities by connecting existing MCP servers to the agent.

#### Tasks

| # | Task | Tool/Server | Effort | Status |
|---|------|-------------|--------|--------|
| 0.1 | Add paper-search-mcp | `openags/paper-search-mcp` | 30 min | 🔲 |
| 0.2 | Add zotero-mcp | `54yyyu/zotero-mcp` | 30 min | 🔲 |
| 0.3 | Add overleaf-mcp | `rangehow/overleaf-mcp` | 30 min | 🔲 |
| 0.4 | Add mcp-pdf | `rsp2k/mcp-pdf` | 30 min | 🔲 |
| 0.5 | Add jupyter-mcp-server | `datalayer/jupyter-mcp-server` | 30 min | 🔲 |
| 0.6 | Add rmcp | `finite-sample/rmcp` | 30 min | 🔲 |
| 0.7 | Add neo4j-mcp | `neo4j-contrib/neo4j-mcp` | 30 min | 🔲 |
| 0.8 | Add qdrant-mcp | `qdrant/mcp-server-qdrant` | 30 min | 🔲 |
| 0.9 | Add chroma-mcp | `chroma-core/chroma-mcp` | 30 min | 🔲 |
| 0.10 | Add markitdown-mcp | `microsoft/markitdown-mcp` | 30 min | 🔲 |
| 0.11 | Add pubmed-search-mcp | `pubmed-search-mcp` | 30 min | 🔲 |
| 0.12 | Add Elicit MCP | `elicit-mcp` | 30 min | 🔲 |

#### What This Gives Us Immediately

| Capability | MCP Server | Tools Gained |
|-----------|------------|--------------|
| Search 22 academic databases | paper-search-mcp | ~15 tools |
| Semantic search + BibTeX + Scite | zotero-mcp | ~8 tools |
| LaTeX compilation + editing | overleaf-mcp | 18 tools |
| PDF extraction + manipulation | mcp-pdf | 46 tools |
| Code execution (Python/R/Julia) | jupyter-mcp-server | ~10 tools |
| R statistical analysis | rmcp | 52 tools (429 packages!) |
| Knowledge graph queries | neo4j-mcp | ~12 tools |
| Vector similarity search | qdrant-mcp / chroma-mcp | ~8 tools each |
| Universal file→Markdown | markitdown-mcp | ~5 tools |
| Biomedical literature | pubmed-search-mcp | 40 tools |
| Automated research reports | Elicit MCP | ~6 tools |

**Total new tools available: ~230+ (from 62 → 290+)**

#### Configuration

Add to `.claude/mcp_servers.json`:
```json
{
  "paper-search": {
    "command": "npx",
    "args": ["-y", "@openags/paper-search-mcp"]
  },
  "zotero": {
    "command": "npx",
    "args": ["-y", "zotero-mcp"],
    "env": { "ZOTERO_API_KEY": "${ZOTERO_API_KEY}" }
  },
  "overleaf": {
    "command": "npx",
    "args": ["-y", "overleaf-mcp"],
    "env": { "OVERLEAF_EMAIL": "${OVERLEAF_EMAIL}", "OVERLEAF_PASSWORD": "${OVERLEAF_PASSWORD}" }
  },
  "jupyter": {
    "command": "npx",
    "args": ["-y", "@datalayer/jupyter-mcp-server"]
  },
  "rmcp": {
    "command": "npx",
    "args": ["-y", "rmcp"]
  },
  "neo4j": {
    "command": "npx",
    "args": ["-y", "@neo4j/mcp-server"],
    "env": { "NEO4J_URI": "${NEO4J_URI}", "NEO4J_PASSWORD": "${NEO4J_PASSWORD}" }
  },
  "qdrant": {
    "command": "npx",
    "args": ["-y", "@qdrant/mcp-server-qdrant"],
    "env": { "QDRANT_URL": "${QDRANT_URL}" }
  },
  "markitdown": {
    "command": "npx",
    "args": ["-y", "markitdown-mcp"]
  }
}
```

#### Acceptance Criteria
- [ ] All 12 MCP servers configured and responding to `list_tools`
- [ ] Agent can search academic papers via paper-search-mcp
- [ ] Agent can execute R code via rmcp
- [ ] Agent can compile LaTeX via overleaf-mcp
- [ ] Agent can extract PDF content via mcp-pdf

#### Dependencies
- None (existing infrastructure supports MCP servers)

#### Estimated Time: 1 day

---

### Phase 1: Foundation Layer (Weeks 1-3)

**Goal:** Project state management, phase system, LiteLLM integration, DSPy pipeline scaffolding

#### Tasks

| # | Task | Priority | Tools/Libraries | Acceptance Criteria |
|---|------|----------|-----------------|---------------------|
| 1.1 | Project state schema (`project.yaml`) | 🔴 Critical | PyYAML, Pydantic | Load/save/resume across sessions |
| 1.2 | Phase manager (dynamic tool loading) | 🔴 Critical | Custom | Max 15 tools visible per phase; auto-switch |
| 1.3 | Workspace scaffolding tool | 🔴 Critical | Custom | Creates IMRaD project structure |
| 1.4 | LiteLLM integration | 🔴 Critical | **LiteLLM** (20K⭐) | Multi-provider routing, cost tracking, fallback |
| 1.5 | DSPy pipeline scaffolding | 🔴 Critical | **DSPy** (25K⭐) | Typed signatures for each research phase |
| 1.6 | Session resume protocol | 🟡 High | Custom | Agent resumes from any checkpoint |
| 1.7 | Research decision log (append-only) | 🟡 High | Custom | Every decision logged with rationale |
| 1.8 | Human-in-the-loop approval gates | 🟡 High | Custom | Pause at methodology/interpretation |
| 1.9 | Extend skills system with `phase` field | 🟡 High | Custom | Skills auto-load per phase |
| 1.10 | Data quality gates | 🟠 Medium | **Great Expectations** (11.3K⭐), **Pandera** (4.3K⭐) | Validate data before analysis |

#### Key Libraries

| Library | Version | Purpose | Stars | License |
|---------|---------|---------|-------|---------|
| LiteLLM | ≥1.40 | Multi-provider LLM gateway + cost tracking | 20K | MIT |
| DSPy | ≥2.5 | Optimizable LLM pipeline framework | 25K | MIT |
| Great Expectations | ≥0.18 | Data quality validation gates | 11.3K | Apache 2.0 |
| Pandera | ≥0.20 | DataFrame schema validation | 4.3K | MIT |
| PyYAML | ≥6.0 | Project state serialization | — | MIT |
| Pydantic | ≥2.5 | Schema validation | — | MIT |

#### Key Files to Create/Modify

```
mini_agent/research/
├── project_state.py          # Project YAML schema + persistence
├── phase_manager.py          # Dynamic tool loading per phase
├── workspace.py              # Scaffolding (IMRaD structure)
├── session_resume.py         # Checkpoint/resume protocol
├── decision_log.py           # Append-only research decisions
├── approval_gates.py         # Human-in-the-loop pauses
├── llm_gateway.py            # LiteLLM wrapper with cost tracking
└── dspy_modules/
    ├── __init__.py
    ├── signatures.py         # Typed DSPy signatures per phase
    ├── research_planner.py   # DSPy module: plan research
    ├── data_analyst.py       # DSPy module: analyze data
    ├── section_writer.py     # DSPy module: write sections
    └── reviewer.py           # DSPy module: review paper
```

#### DSPy Module Design

```python
# Example: Research Planner Signature
class ResearchPlanner(dspy.Signature):
    """Given a research question and available BPS data, produce a research plan."""
    research_question: str = dspy.InputField(desc="The research question to investigate")
    available_data: list[str] = dspy.InputField(desc="Available BPS datasets")
    methodology: str = dspy.OutputField(desc="Statistical methodology to use")
    variables: dict = dspy.OutputField(desc="Independent, dependent, control variables")
    analysis_plan: list[str] = dspy.OutputField(desc="Ordered analysis steps")
```

#### Acceptance Criteria
- [ ] `project.yaml` schema defined with Pydantic; load/save works
- [ ] Phase manager limits visible tools to ≤15 per phase
- [ ] LiteLLM routes to Claude/GPT-4/Gemini with automatic fallback
- [ ] DSPy signatures defined for all 5 research phases
- [ ] Cost tracking logs every LLM call with token count + cost
- [ ] Session resume works after process restart

#### Dependencies
- Phase 0 (MCP servers configured)

#### Estimated Time: 3 weeks

---

### Phase 2: Data Analysis Engine (Weeks 3-7)

**Goal:** Statistical analysis, visualization, reproducible computation in sandboxed environments

#### Tasks

| # | Task | Priority | Tools/Libraries | Acceptance Criteria |
|---|------|----------|-----------------|---------------------|
| 2.1 | Sandboxed code execution | 🔴 Critical | **E2B** (12K⭐) + Docker fallback | Execute Python/R safely; return stdout + artifacts |
| 2.2 | Natural language → analysis | 🔴 Critical | **PandasAI** (23K⭐) | "Correlate IPM with poverty rate" → code + results |
| 2.3 | Automated EDA | 🔴 Critical | **ydata-profiling** (13.5K⭐) | Full profiling report from any DataFrame |
| 2.4 | Auto-visualization | 🔴 Critical | **LIDA** (Microsoft) | Goal exploration + publication-quality figures |
| 2.5 | Descriptive statistics tool | 🔴 Critical | statsmodels, scipy | Mean, SD, skewness, kurtosis, correlation |
| 2.6 | Regression analysis tool | 🔴 Critical | statsmodels, linearmodels | OLS, logistic, panel (FE/RE), Hausman |
| 2.7 | Time series analysis tool | 🔴 Critical | statsmodels, arch | ARIMA, VAR, unit root (ADF), cointegration |
| 2.8 | Hypothesis testing tool | 🔴 Critical | scipy, pingouin | t-test, ANOVA, chi-square, Mann-Whitney |
| 2.9 | Bayesian analysis stack | 🟡 High | **PyMC** + **Bambi** + **ArviZ** | Bayesian regression, posterior analysis, diagnostics |
| 2.10 | Causal inference | 🟡 High | **DoWhy** (Microsoft, 8K⭐) + **CausalML** (Uber, 5.8K⭐) | DAG-based causal analysis, treatment effects |
| 2.11 | Survival analysis | 🟡 High | **Lifelines** | Kaplan-Meier, Cox PH, time-to-event |
| 2.12 | Publication-quality figures | 🟡 High | matplotlib + **tikzplotlib** | Figures export to TikZ (native LaTeX) |
| 2.13 | APA statistics formatter | 🟡 High | Custom | Auto-format: *F*(2, 47) = 3.45, *p* = .039 |
| 2.14 | Reproducibility logger | 🟡 High | Custom | Log every computation with hash |
| 2.15 | Data validation pipeline | 🟠 Medium | Great Expectations, Pandera | Validate before analysis |

#### Key Libraries

| Library | Version | Purpose | Stars | License |
|---------|---------|---------|-------|---------|
| E2B | ≥1.0 | Cloud sandboxes for AI code execution | 12K | MIT |
| PandasAI | ≥2.0 | Natural language → data analysis | 23K | MIT |
| ydata-profiling | ≥4.6 | Automated EDA reports | 13.5K | MIT |
| LIDA | ≥0.0.10 | Auto-visualization + goal exploration | — | MIT |
| statsmodels | ≥0.14 | OLS, ARIMA, VAR, diagnostics | — | BSD |
| scipy | ≥1.11 | Hypothesis tests, distributions | — | BSD |
| linearmodels | ≥6.0 | Panel data (FE, RE, Hausman) | — | BSD |
| arch | ≥7.0 | GARCH, unit root tests | — | BSD |
| pingouin | ≥0.5.4 | Effect sizes, Bayesian stats, power | — | GPL-3 |
| PyMC | ≥5.10 | Bayesian modeling | 8.7K | Apache 2.0 |
| Bambi | ≥0.13 | Bayesian regression (formula interface) | — | MIT |
| ArviZ | ≥0.17 | Bayesian diagnostics + visualization | — | Apache 2.0 |
| DoWhy | ≥0.11 | Causal inference (DAG-based) | 8K | MIT |
| CausalML | ≥0.15 | Treatment effect estimation | 5.8K | Apache 2.0 |
| Lifelines | ≥0.28 | Survival analysis | — | MIT |
| tikzplotlib | ≥0.10 | matplotlib → TikZ (native LaTeX) | — | MIT |
| seaborn | ≥0.13 | Statistical visualizations | — | BSD |

#### Key Files to Create

```
mini_agent/tools/
├── python_sandbox.py         # E2B + Docker execution wrapper
├── statistics_tools.py       # Descriptive, regression, time series, hypothesis
├── bayesian_tools.py         # PyMC + Bambi + ArviZ integration
├── causal_tools.py           # DoWhy + CausalML integration
├── visualization_tool.py     # LIDA + matplotlib + tikzplotlib
├── data_profiling_tool.py    # ydata-profiling + PandasAI
├── data_cleaning_tool.py     # Missing values, outliers, normalization

mini_agent/research/
├── apa_formatter.py          # APA 7th statistics formatting
├── reproducibility.py        # Computation logging + hashing
└── analysis_registry.py      # Registry of available methods + assumptions

config/
├── Dockerfile.sandbox        # Python sandbox with all stats packages
└── e2b.toml                  # E2B sandbox configuration
```

#### Acceptance Criteria
- [ ] Code executes in isolated sandbox (no host filesystem access)
- [ ] PandasAI converts natural language queries to analysis code
- [ ] All standard statistical tests available (t-test through panel regression)
- [ ] Bayesian analysis produces posterior plots + diagnostics
- [ ] Causal inference generates DAG + estimates treatment effects
- [ ] Figures export as both PNG and TikZ (for LaTeX)
- [ ] Every analysis step logged with reproducibility hash
- [ ] APA formatter produces correct statistical notation

#### Dependencies
- Phase 1 (project state, LiteLLM, DSPy modules)
- Phase 0 (jupyter-mcp-server for fallback execution, rmcp for R)

#### Estimated Time: 4 weeks

---

### Phase 3: Knowledge & Literature Engine (Weeks 7-11)

**Goal:** Document processing, RAG pipeline, literature synthesis, citation management

#### Tasks

| # | Task | Priority | Tools/Libraries | Acceptance Criteria |
|---|------|----------|-----------------|---------------------|
| 3.1 | Scientific PDF parsing | 🔴 Critical | **MinerU** (61K⭐) + **Docling** (IBM, 59K⭐) | Extract text, equations, tables from papers |
| 3.2 | Universal file conversion | 🔴 Critical | **MarkItDown** (Microsoft, 112K⭐) | Any file → structured Markdown |
| 3.3 | Bibliographic extraction | 🔴 Critical | **GROBID** (5K⭐) | Extract structured references from PDFs |
| 3.4 | Scientific RAG pipeline | 🔴 Critical | **PaperQA2** (8K⭐) | Superhuman literature QA with citations |
| 3.5 | Knowledge graph extraction | 🔴 Critical | **LightRAG** (34K⭐) | Entity/relation extraction from papers |
| 3.6 | Scientific embeddings | 🔴 Critical | **SPECTER2** + **nomic-embed-text** | Domain-specific paper similarity |
| 3.7 | Semantic chunking | 🟡 High | **Chonkie** | 33x faster than LangChain; semantic boundaries |
| 3.8 | Scientific NLP | 🟡 High | **scispaCy** | Entity extraction (chemicals, diseases, genes) |
| 3.9 | Multi-document RAG | 🟡 High | **LlamaIndex** | Agentic RAG across multiple papers |
| 3.10 | Document ETL pipeline | 🟡 High | **Unstructured.io** (14.5K⭐) | Batch document processing |
| 3.11 | Vector storage | 🟡 High | **LanceDB** (serverless) | Local vector DB, no server needed |
| 3.12 | Literature synthesis | 🟡 High | **OpenScholar** (Allen AI) | Cross-paper theme identification |
| 3.13 | Citation manager (BibTeX) | 🔴 Critical | bibtexparser + **habanero** | Read/write/validate .bib; CrossRef lookup |
| 3.14 | Citation verification | 🔴 Critical | habanero + Semantic Scholar API | Verify ALL citations against live APIs |
| 3.15 | Deep document understanding | 🟠 Medium | **RAGFlow** (Paper mode) | Table extraction + cross-page reasoning |
| 3.16 | API rate limiter + cache | 🟡 High | Custom + Redis/SQLite | Respect limits, cache responses 24h |

#### Key Libraries

| Library | Version | Purpose | Stars | License |
|---------|---------|---------|-------|---------|
| MinerU | ≥0.9 | Best scientific PDF parser (LaTeX, tables) | 61K | AGPL-3 |
| MarkItDown | ≥0.1 | Universal file → Markdown | 112K | MIT |
| Docling | ≥2.0 | Advanced PDF with ML layout analysis | 59K | MIT |
| GROBID | ≥0.8 | ML bibliographic extraction | 5K | Apache 2.0 |
| PaperQA2 | ≥5.0 | Superhuman scientific RAG | 8K | Apache 2.0 |
| LightRAG | ≥1.0 | Knowledge graph (outperforms GraphRAG) | 34K | MIT |
| Unstructured | ≥0.14 | Document ETL pipeline | 14.5K | Apache 2.0 |
| LlamaIndex | ≥0.10 | Multi-document agentic RAG | 37K | MIT |
| Chonkie | ≥0.3 | Fast semantic chunking | — | MIT |
| scispaCy | ≥0.5 | Scientific NLP entities | — | MIT |
| LanceDB | ≥0.6 | Serverless vector database | — | Apache 2.0 |
| SPECTER2 | — | Scientific paper embeddings | — | Apache 2.0 |
| nomic-embed-text | — | 8192-token general embeddings | — | Apache 2.0 |
| habanero | ≥1.2 | Python CrossRef client | — | MIT |
| bibtexparser | ≥1.4 | BibTeX parsing/writing | — | MIT |

#### Key Files to Create

```
mini_agent/research/
├── document_processing/
│   ├── pdf_parser.py         # MinerU + Docling integration
│   ├── file_converter.py     # MarkItDown wrapper
│   ├── biblio_extractor.py   # GROBID client
│   └── etl_pipeline.py       # Unstructured.io batch processing
├── rag/
│   ├── paper_qa.py           # PaperQA2 integration
│   ├── knowledge_graph.py    # LightRAG extraction + Neo4j storage
│   ├── embeddings.py         # SPECTER2 + nomic-embed-text
│   ├── chunker.py            # Chonkie semantic chunking
│   ├── vector_store.py       # LanceDB + Qdrant MCP bridge
│   └── multi_doc_rag.py      # LlamaIndex agentic RAG
├── literature/
│   ├── synthesis.py          # Cross-paper theme extraction
│   ├── scientific_nlp.py     # scispaCy entity extraction
│   └── open_scholar.py       # OpenScholar integration
├── apis/
│   ├── base_client.py        # Rate limiting + caching layer
│   ├── semantic_scholar.py   # Semantic Scholar API
│   ├── crossref.py           # CrossRef via habanero
│   ├── openalex.py           # OpenAlex API
│   ├── core_api.py           # CORE full-text access
│   └── unpaywall.py          # Open access finder
└── citation/
    ├── manager.py            # BibTeX read/write/validate
    ├── verifier.py           # Verify citations against APIs
    └── csl_processor.py      # citeproc-py formatting

mini_agent/tools/
├── literature_search_tool.py # Unified search across all databases
├── citation_tool.py          # Citation management MCP tool
├── document_tool.py          # PDF/file processing tool
└── knowledge_graph_tool.py   # KG query/update tool
```

#### RAG Pipeline Architecture

```
Input Paper (PDF)
    │
    ├─→ MinerU (equations, tables, figures)
    ├─→ GROBID (structured references)
    └─→ MarkItDown (fallback text extraction)
         │
         ▼
    Chonkie (semantic chunking, 33x faster)
         │
         ├─→ SPECTER2 embeddings (scientific similarity)
         └─→ nomic-embed-text (general semantic search)
              │
              ▼
    LanceDB (local vector store)
    + LightRAG (knowledge graph)
    + Neo4j MCP (complex graph queries)
              │
              ▼
    PaperQA2 (superhuman QA with citations)
    + LlamaIndex (multi-document reasoning)
              │
              ▼
    Literature Synthesis (themes, gaps, contradictions)
```

#### Acceptance Criteria
- [ ] PDF parsing extracts LaTeX equations and cross-page tables correctly
- [ ] PaperQA2 answers questions with inline citations from loaded papers
- [ ] Knowledge graph captures entities and relations from 50+ papers
- [ ] SPECTER2 embeddings find semantically similar papers (>0.85 recall@10)
- [ ] Citation verification catches 100% of hallucinated references
- [ ] Literature synthesis identifies themes across 20+ papers
- [ ] Rate limiter respects all API limits; cache reduces calls by >60%

#### Dependencies
- Phase 1 (project state, LiteLLM for embeddings)
- Phase 0 (paper-search-mcp, zotero-mcp, neo4j-mcp, qdrant-mcp)

#### Estimated Time: 4 weeks

---

### Phase 4: Paper Writing Engine (Weeks 11-15)

**Goal:** Generate production-ready academic papers in LaTeX/Typst/DOCX with verified citations

#### Tasks

| # | Task | Priority | Tools/Libraries | Acceptance Criteria |
|---|------|----------|-----------------|---------------------|
| 4.1 | Typst integration (primary) | 🔴 Critical | **Typst** (38K⭐) | Millisecond compilation; modern syntax |
| 4.2 | LaTeX via Tectonic | 🔴 Critical | **Tectonic** (4.7K⭐) | Zero-config LaTeX (no TeX Live install) |
| 4.3 | Template registry | 🔴 Critical | Custom | IEEE, Springer, Elsevier, MDPI, APA7, BPS |
| 4.4 | Paper outline generator (DSPy) | 🔴 Critical | DSPy module | IMRaD structure with section specifications |
| 4.5 | Section writer sub-agent | 🔴 Critical | DSPy + LiteLLM | Write one section with focused context |
| 4.6 | Hierarchical generation | 🔴 Critical | Custom orchestration | Plan → sections → coherence → assembly |
| 4.7 | Citation insertion | 🔴 Critical | citeproc-py + habanero | Insert verified \cite{} references |
| 4.8 | CSL citation processing | 🟡 High | **citeproc-py** | 10,000+ citation styles (APA, Chicago, etc.) |
| 4.9 | Academic table generator | 🟡 High | Custom + booktabs | DataFrame → publication-quality tables |
| 4.10 | Figure management | 🟡 High | tikzplotlib + Custom | Auto-reference, caption, placement |
| 4.11 | Abstract generator | 🟡 High | DSPy module | Structured abstract from paper content |
| 4.12 | Grammar & style check | 🟡 High | **LanguageTool** (12K⭐) + **proselint** (4.5K⭐) | Academic prose quality |
| 4.13 | Document conversion | 🟠 Medium | **Pandoc** (35K⭐) | LaTeX ↔ DOCX ↔ Typst with templates |
| 4.14 | DOCX export | 🟠 Medium | python-docx | Journal-formatted Word documents |
| 4.15 | Overleaf integration | 🟠 Medium | overleaf-mcp | Push to Overleaf for collaboration |

#### Key Libraries

| Library | Version | Purpose | Stars | License |
|---------|---------|---------|-------|---------|
| Typst | ≥0.11 | Modern typesetting (ms compilation!) | 38K | Apache 2.0 |
| Tectonic | ≥0.15 | Zero-config LaTeX engine | 4.7K | MIT |
| LanguageTool | ≥6.3 | Open-source grammar checker | 12K | LGPL |
| proselint | ≥0.14 | Academic prose linter | 4.5K | BSD |
| Pandoc | ≥3.1 | Universal document converter | 35K | GPL-2 |
| citeproc-py | ≥0.9 | CSL citation processing | — | BSD |
| tikzplotlib | ≥0.10 | matplotlib → TikZ figures | — | MIT |
| python-docx | ≥1.2 | DOCX generation | — | MIT |
| pylatex | ≥1.4 | LaTeX document generation | — | MIT |

#### Key Files to Create

```
mini_agent/research/paper/
├── template_registry.py      # Journal templates (IEEE, Springer, etc.)
├── outline_generator.py      # DSPy: research question → IMRaD outline
├── section_writer.py         # DSPy: section spec → academic prose
├── hierarchical_gen.py       # Orchestrate: plan → write → cohere → assemble
├── typst_generator.py        # Typst document generation (PRIMARY)
├── latex_generator.py        # LaTeX document generation (via Tectonic)
├── docx_generator.py         # DOCX generation (python-docx)
├── table_generator.py        # DataFrame → booktabs/Typst tables
├── figure_manager.py         # Figure placement, captions, references
├── citation_inserter.py      # Verified citation insertion
├── csl_processor.py          # citeproc-py: format citations per style
├── compiler.py               # Typst/Tectonic compilation + error recovery
├── style_checker.py          # LanguageTool + proselint integration
└── converter.py              # Pandoc: cross-format conversion

mini_agent/research/paper/templates/
├── ieee/                     # IEEE conference/journal templates
├── springer/                 # Springer Nature templates
├── elsevier/                 # Elsevier journal templates
├── mdpi/                     # MDPI open access templates
├── apa7/                     # APA 7th edition
├── bps/                      # BPS Indonesia report format
└── typst/                    # Typst equivalents of all above

mini_agent/tools/
├── paper_writing_tool.py     # Main paper writing MCP tool
├── compilation_tool.py       # Compile LaTeX/Typst → PDF
└── style_check_tool.py       # Grammar + academic style
```

#### Paper Generation Pipeline

```
Research Results (Phase 2) + Literature (Phase 3)
    │
    ▼
┌─────────────────────────────────────────┐
│  1. OUTLINE GENERATION (DSPy Module)     │
│     Input: RQ + results + literature     │
│     Output: IMRaD outline with specs     │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  2. SECTION WRITING (Sub-agents)         │
│     Each section: focused context window │
│     • Introduction (lit review + RQ)     │
│     • Methods (analysis plan + tools)    │
│     • Results (stats + figures + tables) │
│     • Discussion (interpretation + lit)  │
│     • Conclusion (summary + future)      │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  3. COHERENCE PASS                       │
│     • Cross-section consistency          │
│     • Citation deduplication             │
│     • Terminology standardization        │
│     • LanguageTool + proselint           │
└─────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────┐
│  4. ASSEMBLY & COMPILATION               │
│     • Insert citations (citeproc-py)     │
│     • Place figures (tikzplotlib)        │
│     • Generate tables (booktabs)         │
│     • Compile: Typst (ms) or Tectonic   │
│     • Export: PDF + source + .bib        │
└─────────────────────────────────────────┘
```

#### Acceptance Criteria
- [ ] Typst compiles paper in <1 second
- [ ] Tectonic compiles LaTeX without requiring TeX Live installation
- [ ] Templates available for 6+ journal formats
- [ ] Section writer produces coherent academic prose (human evaluation >7/10)
- [ ] All citations verified before insertion (0% hallucinated)
- [ ] Figures render correctly in compiled PDF
- [ ] Tables follow booktabs style (no vertical lines)
- [ ] LanguageTool catches >90% of grammar issues
- [ ] Pandoc converts between formats without loss

#### Dependencies
- Phase 2 (analysis results, figures, tables)
- Phase 3 (literature, citations, knowledge graph)
- Phase 0 (overleaf-mcp for collaboration)

#### Estimated Time: 4 weeks

---

### Phase 5: Quality Gate & Review (Weeks 15-17)

**Goal:** Automated quality assurance, adversarial peer review, and iterative refinement

#### Tasks

| # | Task | Priority | Tools/Libraries | Acceptance Criteria |
|---|------|----------|-----------------|---------------------|
| 5.1 | Statistical validity checker | 🔴 Critical | Custom + DSPy | Assumptions, sample size, effect sizes verified |
| 5.2 | Citation verification (full) | 🔴 Critical | habanero + S2 API | 100% citations resolve via DOI/API |
| 5.3 | Peer review simulator | 🔴 Critical | DSPy (adversarial) | Reviewer 1, 2, 3 with different expertise |
| 5.4 | Academic style checker | 🟡 High | LanguageTool + proselint | Tone, hedging, terminology consistency |
| 5.5 | Reproducibility audit | 🟡 High | Custom | All analysis steps re-runnable from log |
| 5.6 | Consistency checker | 🟡 High | Custom | Numbers match between text/tables/figures |
| 5.7 | JARS compliance checker | 🟡 High | Custom | APA reporting standards compliance |
| 5.8 | Plagiarism detection | 🟡 High | Custom + embeddings | Semantic similarity against source papers |
| 5.9 | Iterative refinement loop | 🟡 High | Custom orchestration | Review → revise → re-review (max 3 cycles) |
| 5.10 | Quality score dashboard | 🟠 Medium | Custom | Aggregate quality metrics visualization |

#### Quality Gate Pipeline

```
Draft Paper (from Phase 4)
    │
    ▼
┌─────────────────────────────────────────┐
│  GATE 1: STATISTICAL VALIDITY            │
│  • Are assumptions met? (normality, etc.)│
│  • Sample size adequate? (power ≥ 0.80)  │
│  • Effect sizes reported?                │
│  • Multiple comparisons corrected?       │
│  • JARS compliance checked?              │
│  PASS/FAIL → feedback to Phase 2         │
└─────────────────────────────────────────┘
    │ PASS
    ▼
┌─────────────────────────────────────────┐
│  GATE 2: CITATION INTEGRITY             │
│  • Every \cite{} resolves to real paper  │
│  • DOIs valid and accessible             │
│  • No self-plagiarism detected           │
│  • Proper attribution for all claims     │
│  PASS/FAIL → feedback to Phase 3         │
└─────────────────────────────────────────┘
    │ PASS
    ▼
┌─────────────────────────────────────────┐
│  GATE 3: WRITING QUALITY                 │
│  • Grammar (LanguageTool score ≥ 95%)    │
│  • Academic style (proselint clean)      │
│  • Consistency (numbers, terminology)    │
│  • Coherence across sections             │
│  PASS/FAIL → feedback to Phase 4         │
└─────────────────────────────────────────┘
    │ PASS
    ▼
┌─────────────────────────────────────────┐
│  GATE 4: ADVERSARIAL PEER REVIEW         │
│  • Reviewer 1: Methodology expert        │
│  • Reviewer 2: Domain specialist         │
│  • Reviewer 3: Statistics reviewer       │
│  • Generate: Major/Minor revisions list  │
│  ITERATE → back to writing (max 3x)     │
└─────────────────────────────────────────┘
    │ ACCEPT
    ▼
┌─────────────────────────────────────────┐
│  GATE 5: FINAL HUMAN APPROVAL            │
│  • Present quality scores                │
│  • Show reviewer comments + responses    │
│  • Human decides: submit / revise / stop │
└─────────────────────────────────────────┘
```

#### Key Files to Create

```
mini_agent/research/quality/
├── statistical_validator.py  # Check assumptions, power, effect sizes
├── citation_verifier.py      # Verify all citations against APIs
├── style_checker.py          # LanguageTool + proselint integration
├── consistency_checker.py    # Cross-reference numbers/claims
├── jars_compliance.py        # APA JARS reporting standards
├── plagiarism_detector.py    # Semantic similarity check
├── peer_reviewer.py          # Adversarial DSPy reviewer agents
├── refinement_loop.py        # Review → revise → re-review orchestration
└── quality_dashboard.py      # Aggregate quality metrics

mini_agent/tools/
└── quality_gate_tool.py      # Main quality gate MCP tool
```

#### Acceptance Criteria
- [ ] Statistical validator catches missing assumptions/corrections
- [ ] Citation verifier achieves 100% verification rate
- [ ] Peer review simulator generates actionable revision suggestions
- [ ] Iterative loop converges within 3 cycles
- [ ] Final paper passes all 4 automated gates
- [ ] Human approval gate presents clear quality summary
- [ ] Plagiarism detector flags >80% semantic overlap

#### Dependencies
- Phase 4 (paper drafts to review)
- Phase 3 (citation APIs for verification)
- Phase 2 (statistical methods for validation)

#### Estimated Time: 2 weeks

---

### Phase 6: Integration & Polish (Weeks 17-20)

**Goal:** End-to-end workflow, performance optimization, documentation, testing

#### Tasks

| # | Task | Priority | Tools/Libraries | Acceptance Criteria |
|---|------|----------|-----------------|---------------------|
| 6.1 | End-to-end integration testing | 🔴 Critical | pytest + fixtures | Full pipeline: search → analyze → write → review |
| 6.2 | Academic research system prompt | 🔴 Critical | Custom | Bilingual (ID/EN), covers all phases |
| 6.3 | Academic research skill | 🟡 High | Skill system | Progressive disclosure for research workflow |
| 6.4 | CLI enhancements | 🟡 High | Click/Typer | `bpsagent research start/resume/status` |
| 6.5 | Progress dashboard | 🟡 High | Rich (terminal) | Visual progress of research project |
| 6.6 | Export to Overleaf | 🟡 High | overleaf-mcp | ZIP with .tex + figures + .bib |
| 6.7 | Performance optimization | 🟡 High | asyncio + caching | Parallel API calls, response caching |
| 6.8 | DSPy optimization run | 🟡 High | DSPy optimizers | Optimize prompts on evaluation set |
| 6.9 | Cost optimization | 🟠 Medium | LiteLLM routing | Route simple tasks to cheaper models |
| 6.10 | Documentation | 🟡 High | MkDocs | User guide, API docs, examples |
| 6.11 | Example research projects | 🟠 Medium | Custom | 3 complete examples (economics, health, education) |
| 6.12 | Error recovery & resilience | 🟡 High | Custom | Graceful degradation, retry logic |

#### Key Files to Create/Modify

```
mini_agent/
├── research/
│   ├── orchestrator.py       # End-to-end research orchestration
│   ├── progress_tracker.py   # Visual progress dashboard
│   └── cost_tracker.py       # LLM cost monitoring + alerts
├── skills/
│   └── academic-research/    # Full research workflow skill
│       ├── skill.yaml
│       ├── plan.md
│       ├── collect.md
│       ├── analyze.md
│       ├── write.md
│       └── review.md
├── cli/
│   └── research_commands.py  # CLI: research start/resume/status
└── prompts/
    └── academic_system.md    # Bilingual academic system prompt

tests/
├── integration/
│   ├── test_full_pipeline.py
│   ├── test_phase_transitions.py
│   └── test_error_recovery.py
├── unit/
│   ├── test_statistics.py
│   ├── test_citation.py
│   ├── test_paper_gen.py
│   └── test_quality_gate.py
└── fixtures/
    ├── sample_bps_data/
    ├── sample_papers/
    └── expected_outputs/

docs/
├── user-guide/
│   ├── quickstart.md
│   ├── research-workflow.md
│   ├── configuration.md
│   └── troubleshooting.md
├── examples/
│   ├── economics-ipm-poverty/
│   ├── health-stunting-analysis/
│   └── education-enrollment-study/
└── api-reference/
```

#### Acceptance Criteria
- [ ] Full pipeline completes: BPS data → published-quality paper in <2 hours
- [ ] System prompt handles bilingual (Indonesian/English) research
- [ ] CLI provides intuitive research project management
- [ ] DSPy optimization improves output quality by >15% on eval set
- [ ] Cost tracking shows per-paper LLM cost (<$5 target)
- [ ] 3 example projects demonstrate complete workflow
- [ ] Documentation covers all features with examples
- [ ] Error recovery handles API failures gracefully

#### Dependencies
- All previous phases (integration testing)

#### Estimated Time: 3 weeks

---

## 4. Version Milestones

| Version | Phase | Milestone | Key Capabilities | Target Date |
|---------|-------|-----------|-----------------|-------------|
| **v0.2.0** | Current | BPS Stat Agent | 62 BPS data tools, search & retrieval | ✅ Done |
| **v0.2.5** | Phase 0 | MCP Expansion | +230 tools via MCP servers (zero code) | Week 0 |
| **v0.3.0** | Phase 1 | Foundation | Project state, phase manager, LiteLLM, DSPy | Week 3 |
| **v0.5.0** | Phase 2 | Analysis Engine | Statistical analysis, Bayesian, causal, viz | Week 7 |
| **v0.7.0** | Phase 3 | Knowledge Engine | RAG, embeddings, literature synthesis, citations | Week 11 |
| **v0.8.0** | Phase 4 | Paper Writer | LaTeX/Typst generation, compilation, export | Week 15 |
| **v0.9.0** | Phase 5 | Quality Gates | Automated review, peer simulation, validation | Week 17 |
| **v1.0.0** | Phase 6 | Full Agent | End-to-end integration, optimization, docs | Week 20 |

### Version Capability Matrix

```
Feature                    v0.2  v0.2.5  v0.3  v0.5  v0.7  v0.8  v0.9  v1.0
─────────────────────────────────────────────────────────────────────────────
BPS Data Search             ✅     ✅     ✅    ✅    ✅    ✅    ✅    ✅
Academic Paper Search        ❌     ✅     ✅    ✅    ✅    ✅    ✅    ✅
R Statistical Analysis       ❌     ✅     ✅    ✅    ✅    ✅    ✅    ✅
LaTeX Compilation            ❌     ✅     ✅    ✅    ✅    ✅    ✅    ✅
Project State Management     ❌     ❌     ✅    ✅    ✅    ✅    ✅    ✅
Phase-Gated Tools            ❌     ❌     ✅    ✅    ✅    ✅    ✅    ✅
Multi-Provider LLM           ❌     ❌     ✅    ✅    ✅    ✅    ✅    ✅
Sandboxed Code Execution     ❌     ❌     ❌    ✅    ✅    ✅    ✅    ✅
Bayesian Analysis            ❌     ❌     ❌    ✅    ✅    ✅    ✅    ✅
Causal Inference             ❌     ❌     ❌    ✅    ✅    ✅    ✅    ✅
Publication Figures          ❌     ❌     ❌    ✅    ✅    ✅    ✅    ✅
Scientific PDF Parsing       ❌     ❌     ❌    ❌    ✅    ✅    ✅    ✅
Knowledge Graph              ❌     ❌     ❌    ❌    ✅    ✅    ✅    ✅
Literature Synthesis         ❌     ❌     ❌    ❌    ✅    ✅    ✅    ✅
Citation Verification        ❌     ❌     ❌    ❌    ✅    ✅    ✅    ✅
Paper Generation             ❌     ❌     ❌    ❌    ❌    ✅    ✅    ✅
Typst (ms compilation)       ❌     ❌     ❌    ❌    ❌    ✅    ✅    ✅
Automated Peer Review        ❌     ❌     ❌    ❌    ❌    ❌    ✅    ✅
Quality Gates                ❌     ❌     ❌    ❌    ❌    ❌    ✅    ✅
End-to-End Pipeline          ❌     ❌     ❌    ❌    ❌    ❌    ❌    ✅
DSPy Optimization            ❌     ❌     ❌    ❌    ❌    ❌    ❌    ✅
```

---

## 5. Risk Mitigation

| # | Risk | Severity | Probability | Mitigation Strategy |
|---|------|----------|-------------|---------------------|
| 1 | **Citation hallucination** | 🔴 Critical | High | Verify-before-use pipeline; NEVER cite from LLM memory; all citations must resolve via DOI/API |
| 2 | **Statistical errors** | 🔴 Critical | Medium | Automated validity checker; human approval at methodology; assumption testing before every test |
| 3 | **Token context overflow** | 🟡 High | High | Hierarchical decomposition; section-by-section generation; DSPy context management |
| 4 | **Tool overload (>100 tools)** | 🟡 High | High | Phase-gated loading (max 15/phase); dynamic tool selection via embeddings |
| 5 | **API rate limits** | 🟡 High | Medium | Caching layer (24h TTL); rate limiter per API; graceful degradation |
| 6 | **Sandbox escape** | 🔴 Critical | Low | E2B cloud isolation; Docker with no-network; read-only filesystem; no secrets in sandbox |
| 7 | **Scope creep** | 🟡 High | High | Phase gates; clear acceptance criteria; version milestones; weekly review |
| 8 | **MCP server instability** | 🟠 Medium | Medium | Fallback to custom implementations; health checks; circuit breaker pattern |
| 9 | **LLM cost explosion** | 🟡 High | Medium | LiteLLM cost tracking; route simple tasks to Haiku/GPT-4-mini; budget alerts |
| 10 | **PDF parsing failures** | 🟠 Medium | Medium | Multi-parser fallback (MinerU → Docling → MarkItDown → raw text) |
| 11 | **Knowledge graph noise** | 🟠 Medium | Medium | Confidence scoring on extracted relations; human validation for key claims |
| 12 | **Reproducibility drift** | 🟡 High | Low | Hash every computation; pin all library versions; Docker reproducibility |
| 13 | **GROBID/MinerU AGPL license** | 🟠 Medium | Low | Use as external service (not linked); document license compliance |
| 14 | **Indonesian language support** | 🟠 Medium | Medium | Bilingual prompts; Indonesian NLP models; BPS-specific terminology dictionary |

### Contingency Plans

| Scenario | Primary Plan | Fallback |
|----------|-------------|----------|
| E2B unavailable | E2B cloud sandbox | Local Docker sandbox |
| MinerU fails on PDF | MinerU parser | Docling → MarkItDown → mcp-pdf |
| Semantic Scholar rate limited | S2 API | OpenAlex → CrossRef → paper-search-mcp |
| Typst template missing | Typst compilation | Tectonic (LaTeX) → Pandoc conversion |
| LLM provider outage | Claude (primary) | GPT-4 → Gemini (via LiteLLM fallback) |
| Neo4j unavailable | Neo4j MCP | LightRAG local graph + LanceDB |

---

## 6. Success Metrics

### Primary Metrics (Must Achieve for v1.0)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Paper generation time** | < 2 hours (with human gates) | End-to-end timing from RQ to PDF |
| **Citation accuracy** | 100% verified | All citations resolve via DOI/API lookup |
| **Statistical validity** | 0 errors in quality gate | Automated checker passes all tests |
| **Journal format compliance** | Compiles without errors | Typst/Tectonic exit code 0 |
| **Reproducibility** | All steps re-runnable | Reproducibility audit passes from log |
| **Tool selection accuracy** | > 90% correct first try | Agent selects right tool for task |

### Secondary Metrics (Quality of Life)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **LLM cost per paper** | < $5 USD | LiteLLM cost tracking |
| **Literature coverage** | > 30 relevant papers found | Recall against expert-curated list |
| **Writing quality** | > 7/10 human evaluation | Blind review by domain expert |
| **Peer review realism** | > 6/10 human evaluation | Compare to real reviewer comments |
| **Phase transition accuracy** | > 95% correct | Agent moves to right phase |
| **Error recovery rate** | > 90% self-healed | Errors resolved without human intervention |
| **Knowledge graph precision** | > 85% correct relations | Manual validation of extracted triples |

### Benchmark Comparisons

| Capability | Current (v0.2) | Target (v1.0) | Comparison |
|-----------|----------------|---------------|------------|
| Data sources | 1 (BPS) | 23+ (BPS + academic DBs) | 23x expansion |
| Statistical methods | 0 | 50+ (freq + Bayesian + causal) | New capability |
| Paper output | None | LaTeX + Typst + DOCX | New capability |
| Citation verification | None | 100% automated | New capability |
| Literature synthesis | None | 50+ papers synthesized | New capability |
| Quality assurance | None | 4-gate automated review | New capability |
| Available tools | 62 | 290+ (via MCP) | 4.7x expansion |

---

## 7. Timeline Summary

```
Week 0:     ██ Phase 0: Quick Wins (MCP servers — 1 day!)
Week 1-3:   ████████████ Phase 1: Foundation (state, phases, LiteLLM, DSPy)
Week 3-7:   ████████████████ Phase 2: Data Analysis Engine
Week 7-11:  ████████████████ Phase 3: Knowledge & Literature
Week 11-15: ████████████████ Phase 4: Paper Writing Engine
Week 15-17: ████████ Phase 5: Quality Gate & Review
Week 17-20: ████████████ Phase 6: Integration & Polish
```

**Total estimated effort: 20 weeks (5 months)**  
**Critical path: Phase 0 → 1 → 2 → 3 → 4 → 5 → 6**  
**Parallelizable: Phase 2 and Phase 3 can overlap (weeks 7-11)**

### Resource Requirements

| Resource | Specification | Purpose |
|----------|--------------|---------|
| Development machine | 16GB+ RAM, GPU optional | Local development + testing |
| E2B account | Free tier sufficient initially | Cloud code sandboxes |
| LLM API keys | Claude + GPT-4 + Gemini | Multi-provider via LiteLLM |
| Semantic Scholar API | Free (100 req/5min) | Literature search |
| CrossRef API | Free (polite pool) | DOI/metadata lookup |
| OpenAlex API | Free (unlimited) | Works/author search |
| Neo4j Aura | Free tier (50K nodes) | Knowledge graph |
| Qdrant Cloud | Free tier (1GB) | Vector search |

---

## 8. References

### Inspiration & Architecture
- [AI Scientist v2](https://github.com/SakanaAI/AI-Scientist-v2) — End-to-end ML paper generation (Sakana AI)
- [Robin](https://github.com/Future-House/robin) — Scientific discovery automation (FutureHouse)
- [Anthropic Multi-Agent Research](https://www.anthropic.com/engineering/built-multi-agent-research-system) — Production architecture
- [GPT-Researcher](https://github.com/assafelovic/gpt-researcher) — Deep research reports
- [OpenScholar](https://github.com/AkariAsai/OpenScholar) — Scientific literature synthesis (Allen AI)

### Document Processing
- [MarkItDown](https://github.com/microsoft/markitdown) — Universal file→Markdown (Microsoft, 112K⭐, MIT)
- [MinerU](https://github.com/opendatalab/MinerU) — Scientific PDF parser (61K⭐, AGPL-3)
- [Docling](https://github.com/DS4SD/docling) — Advanced PDF with ML layout (IBM, 59K⭐, MIT)
- [Unstructured](https://github.com/Unstructured-IO/unstructured) — Document ETL (14.5K⭐, Apache 2.0)
- [GROBID](https://github.com/kermitt2/grobid) — Bibliographic extraction (5K⭐, Apache 2.0)

### RAG & Knowledge
- [PaperQA2](https://github.com/Future-House/paper-qa) — Superhuman scientific RAG (8K⭐, Apache 2.0)
- [LightRAG](https://github.com/HKUDS/LightRAG) — Knowledge graph extraction (34K⭐, MIT)
- [LlamaIndex](https://github.com/run-llama/llama_index) — Multi-document RAG (37K⭐, MIT)
- [DSPy](https://github.com/stanfordnlp/dspy) — Optimizable LLM pipelines (Stanford, 25K⭐, MIT)
- [LiteLLM](https://github.com/BerriAI/litellm) — Multi-provider gateway (20K⭐, MIT)
- [Chonkie](https://github.com/bhavnicksm/chonkie) — Fast semantic chunking (MIT)
- [SPECTER2](https://github.com/allenai/specter) — Scientific embeddings (Allen AI)
- [LanceDB](https://github.com/lancedb/lancedb) — Serverless vector DB (Apache 2.0)
- [RAGFlow](https://github.com/infiniflow/ragflow) — Deep document understanding

### Data Analysis
- [PandasAI](https://github.com/Sinaptik-AI/pandas-ai) — NL→data analysis (23K⭐, MIT)
- [LIDA](https://github.com/microsoft/lida) — Auto-visualization (Microsoft, MIT)
- [E2B](https://github.com/e2b-dev/e2b) — Cloud sandboxes (12K⭐, MIT)
- [ydata-profiling](https://github.com/ydataai/ydata-profiling) — Automated EDA (13.5K⭐)
- [PyMC](https://github.com/pymc-devs/pymc) — Bayesian modeling (8.7K⭐, Apache 2.0)
- [DoWhy](https://github.com/py-why/dowhy) — Causal inference (Microsoft, 8K⭐, MIT)
- [CausalML](https://github.com/uber/causalml) — Treatment effects (Uber, 5.8K⭐, Apache 2.0)
- [Great Expectations](https://github.com/great-expectations/great_expectations) — Data quality (11.3K⭐)
- [Pandera](https://github.com/unionai-oss/pandera) — DataFrame validation (4.3K⭐, MIT)

### Paper Writing
- [Typst](https://github.com/typst/typst) — Modern typesetting (38K⭐, Apache 2.0)
- [Tectonic](https://github.com/tectonic-typesetting/tectonic) — Zero-config LaTeX (4.7K⭐, MIT)
- [Pandoc](https://github.com/jgm/pandoc) — Universal converter (35K⭐, GPL-2)
- [LanguageTool](https://github.com/languagetool-org/languagetool) — Grammar checker (12K⭐, LGPL)
- [proselint](https://github.com/amperser/proselint) — Academic prose linter (4.5K⭐, BSD)
- [tikzplotlib](https://github.com/nschloe/tikzplotlib) — matplotlib→TikZ (MIT)
- [citeproc-py](https://github.com/brechtm/citeproc-py) — CSL citation processing (BSD)
- [habanero](https://github.com/sckott/habanero) — Python CrossRef client (MIT)

### MCP Servers
- [paper-search-mcp](https://github.com/openags/paper-search-mcp) — 22 academic sources
- [zotero-mcp](https://github.com/54yyyu/zotero-mcp) — Semantic search + Scite + BibTeX
- [overleaf-mcp](https://github.com/rangehow/overleaf-mcp) — 18 LaTeX tools
- [mcp-pdf](https://github.com/rsp2k/mcp-pdf) — 46 PDF tools
- [jupyter-mcp-server](https://github.com/datalayer/jupyter-mcp-server) — Code execution (1K⭐)
- [rmcp](https://github.com/finite-sample/rmcp) — 52 R tools, 429 packages
- [neo4j-mcp](https://github.com/neo4j-contrib/neo4j-mcp) — Knowledge graph (940⭐)
- [qdrant-mcp](https://github.com/qdrant/mcp-server-qdrant) — Vector search (official)
- [chroma-mcp](https://github.com/chroma-core/chroma-mcp) — Vector search (official)
- [markitdown-mcp](https://github.com/microsoft/markitdown-mcp) — File→Markdown (Microsoft)
- [pubmed-search-mcp](https://github.com/search/pubmed-mcp) — 40 biomedical tools
- [Elicit MCP](https://github.com/elicit/elicit-mcp) — Automated research reports

### Standards & Guidelines
- [APA JARS](https://apastyle.apa.org/jars) — Journal Article Reporting Standards
- [CONSORT](http://www.consort-statement.org/) — Reporting standards for trials
- [PRISMA](http://www.prisma-statement.org/) — Systematic review reporting
- [CRediT](https://credit.niso.org/) — Contributor roles taxonomy

---

## 9. Appendix: Tool Count Summary

| Phase | Custom Tools | MCP Tools | Total Available |
|-------|-------------|-----------|-----------------|
| Phase 0 | 62 (existing) | +230 (MCP servers) | 292 |
| Phase 1 | +10 (foundation) | — | 302 |
| Phase 2 | +15 (analysis) | — | 317 |
| Phase 3 | +12 (knowledge) | — | 329 |
| Phase 4 | +12 (writing) | — | 341 |
| Phase 5 | +8 (quality) | — | 349 |
| Phase 6 | +5 (integration) | — | 354 |

**Note:** Phase-gated loading ensures only 15 tools are visible at any time, preventing cognitive overload while maintaining access to 354 total capabilities.

---

## 10. Decision Log

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| 2025-07-15 | Typst as primary compiler | ms compilation, modern syntax, growing ecosystem | LaTeX (slower), Pandoc (less control) |
| 2025-07-15 | LightRAG over GraphRAG | Outperforms on benchmarks, simpler setup, MIT license | GraphRAG (Microsoft, heavier), custom KG |
| 2025-07-15 | E2B over local Docker | Faster spin-up, no local resource drain, better isolation | Docker (offline fallback), Jupyter MCP |
| 2025-07-15 | DSPy over raw prompts | Optimizable, typed, reproducible; automatic few-shot | LangChain (heavier), raw prompts (fragile) |
| 2025-07-15 | MCP-first architecture | Zero code for 230+ tools; community maintained | Custom implementations (more control, more work) |
| 2025-07-15 | SPECTER2 for scientific embeddings | Domain-trained on 8M papers; best for citation prediction | OpenAI embeddings (general), nomic (backup) |
| 2025-07-15 | PaperQA2 for literature QA | Superhuman performance on benchmarks; Apache 2.0 | Custom RAG (more work), Elicit (less control) |

---

*This roadmap is a living document. Update after each phase completion.*  
*Last reviewed: 2025-07-15 | Next review: After Phase 0 completion*
