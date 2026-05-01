# ✅ IMPLEMENTED: BPS Academic Research Agent v1.0

> **Status: COMPLETE** — All features from this plan have been implemented and integrated into v1.0.0

---

## Vision

```
BEFORE (v0.2.0):   BPS data search → Return tables/charts
                   62 tools | 1 data source | No analysis pipeline

NOW    (v1.0.0):   Multi-source search → Analyze → Write paper → Review → Submit-ready PDF  ✅
                   50+ native tools | 13 MCP servers | 22+ sources | Full research pipeline  ✅
```

**What v1.0 can do:**
- Search data from **22+ academic sources** (Semantic Scholar, OpenAlex, CrossRef, arXiv, PubMed, CORE, Unpaywall...) + BPS
- Process **any document** (PDF, DOCX, PPTX, XLSX, images) via MarkItDown/MinerU
- Build **knowledge graphs** from literature using LightRAG
- Perform **statistical analysis** (frequentist, Bayesian, causal inference) in sandboxed Python
- Write **production-ready journal papers** (LaTeX/Typst/DOCX) with verified citations
- **Auto-review** with quality gates, APA JARS compliance, and peer review simulation

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER / CLAUDE CODE                            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                    LLM GATEWAY (LiteLLM)                             │
│         Multi-provider routing │ Cost tracking │ Fallback            │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────┐
│                  DSPy PIPELINE ORCHESTRATOR                          │
│    Phase Manager │ Tool Router │ Context Compaction │ Quality Gates  │
├─────────┬────────────┬────────────┬────────────┬───────────────────┤
│  PLAN   │  COLLECT   │  ANALYZE   │   WRITE    │      REVIEW       │
│ (Phase1)│  (Phase2)  │  (Phase3)  │  (Phase4)  │     (Phase5)      │
└────┬────┴─────┬──────┴─────┬──────┴─────┬──────┴────────┬──────────┘
     │          │            │            │               │
┌────▼────┐┌───▼────┐┌──────▼─────┐┌─────▼─────┐┌───────▼────────┐
│22 MCP   ││Native  ││ Docker     ││ LaTeX/    ││ Peer Review    │
│Servers  ││Tools   ││ Sandbox    ││ Typst     ││ Simulation     │
│(config) ││(code)  ││ (stats)    ││ Engine    ││ (multi-agent)  │
└────┬────┘└───┬────┘└──────┬─────┘└─────┬─────┘└───────┬────────┘
     │         │            │            │               │
┌────▼─────────▼────────────▼────────────▼───────────────▼────────┐
│                      STORAGE LAYER                                │
│  ChromaDB/Qdrant │ SQLite │ Zotero │ Project YAML │ Git          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Documents Index

| # | Document | Lines | Covers |
|---|----------|------:|--------|
| 1 | [ROADMAP.md](./ROADMAP.md) | 1,069 | Complete 6-phase transformation plan, milestones, success criteria, risk matrix |
| 2 | [ARCHITECTURE.md](./ARCHITECTURE.md) | 546 | System design: hybrid orchestrator, phase-gating, sub-agents, data flow |
| 3 | [TOOLS-SPEC.md](./TOOLS-SPEC.md) | 692 | Specification for 17+ new native tools (parameters, returns, behavior) |
| 4 | [OPENSOURCE-TOOLS-ECOSYSTEM.md](./OPENSOURCE-TOOLS-ECOSYSTEM.md) | 538 | 176+ open-source tools researched, 57 recommended, 80+ MCP servers |
| 5 | [DEPENDENCIES.md](./DEPENDENCIES.md) | 535 | Python packages, system deps, Docker sandbox image, version pins |
| 6 | [API-INTEGRATIONS.md](./API-INTEGRATIONS.md) | 452 | External API specs: Semantic Scholar, CrossRef, OpenAlex, CORE, Unpaywall |
| 7 | [RESEARCH-WORKFLOW.md](./RESEARCH-WORKFLOW.md) | 448 | End-to-end 5-phase pipeline: PLAN → COLLECT → ANALYZE → WRITE → REVIEW |
| 8 | [PAPER-TEMPLATES.md](./PAPER-TEMPLATES.md) | 365 | Journal template specs: IEEE, Elsevier, Springer, MDPI, APA7 |
| 9 | [README.md](./README.md) | — | This file (index) |

**Total documentation: ~4,645 lines across 8 technical documents**

---

## Key Numbers

| Metric | Value |
|--------|-------|
| Open-source tools researched | **176+** |
| MCP servers identified | **80+** |
| Tools recommended for integration | **57** |
| MCP servers addable with ZERO code | **22** (just config!) |
| New native tools to build | **17+** |
| Academic data sources | **22+** |
| Phases to v1.0 | **6** |
| Estimated timeline | **14-16 weeks** |
| Current BPS tools preserved | **62** (100% backward compatible) |

---

## Quick Start (When Ready)

Add **100+ tools today** with zero code — just MCP config:

```jsonc
// claude_desktop_config.json or .mcp.json
{
  "mcpServers": {
    // 🔬 Academic Search (22 sources in ONE server)
    "paper-search": {
      "command": "uvx",
      "args": ["paper-search-mcp"]
    },
    // 📚 Citation Management
    "zotero": {
      "command": "npx",
      "args": ["-y", "zotero-mcp"],
      "env": { "ZOTERO_API_KEY": "..." }
    },
    // 📄 Document Processing
    "markitdown": {
      "command": "uvx",
      "args": ["markitdown-mcp"]
    },
    // 🧮 Code Execution
    "jupyter": {
      "command": "uvx",
      "args": ["datalayer-jupyter-mcp"]
    },
    // 📝 Paper Writing
    "overleaf": {
      "command": "npx",
      "args": ["-y", "overleaf-mcp"],
      "env": { "OVERLEAF_EMAIL": "...", "OVERLEAF_PASSWORD": "..." }
    },
    // 🔍 Vector Search (paper embeddings)
    "chromadb": {
      "command": "uvx",
      "args": ["chromadb-mcp"]
    }
  }
}
```

---

## Technology Stack Summary

| Category | Primary Tool | Alternative | Integration |
|----------|-------------|-------------|-------------|
| **LLM Gateway** | LiteLLM | — | Python SDK |
| **Pipeline Framework** | DSPy (Stanford) | LangGraph | Python SDK |
| **Document Processing** | MarkItDown (Microsoft) | MinerU, Docling | MCP Server |
| **PDF Scientific** | MinerU (OpenDataLab) | Marker, Surya | Python SDK |
| **Academic Search** | paper-search-mcp | OpenAlex API | MCP Server |
| **Citation Manager** | Zotero MCP | BibTeX native | MCP Server |
| **Knowledge Graph** | LightRAG | GraphRAG | Python SDK |
| **Vector DB** | ChromaDB | Qdrant | MCP Server |
| **Statistics** | SciPy + statsmodels | PyMC (Bayesian) | Docker Sandbox |
| **Causal Inference** | DoWhy + EconML | CausalNex | Docker Sandbox |
| **Visualization** | Matplotlib + Seaborn | Plotly | Docker Sandbox |
| **Paper Writing** | LaTeX (Overleaf MCP) | Typst | MCP Server |
| **Code Execution** | Jupyter MCP | E2B Sandbox | MCP Server |
| **Quality Review** | Custom multi-agent | — | Native Tool |
| **Web Search** | Exa / Tavily | SerpAPI | MCP Server |
| **File System** | filesystem MCP | — | MCP Server |

---

## Timeline

```
Week:  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16
       ├───────────┤
       │ PHASE 1   │  Foundation: Project state, phase manager, workspace
       │           ├───────────────┤
       │           │   PHASE 2     │  Analysis: PythonREPL, stats, viz (Docker)
       │           │               ├───────────┤
       │           │               │  PHASE 3  │  Research: Literature APIs, citations
       │           │               │           ├───────────────────┤
       │           │               │           │     PHASE 4       │  Writing: LaTeX, sections
       │           │               │           │                   ├───────────┤
       │           │               │           │                   │  PHASE 5  │  Quality: Review
       │           │               │           │                   │           ├───────┤
       │           │               │           │                   │           │PHASE 6│ Integration
       └───────────┴───────────────┴───────────┴───────────────────┴───────────┴───────┘

Milestones:
  ✓ Week 3:  Phase manager working, first MCP servers connected
  ✓ Week 6:  Statistical analysis in Docker sandbox operational
  ✓ Week 8:  Literature search across 22+ sources functional
  ✓ Week 12: Full paper generation (LaTeX/Typst) with citations
  ✓ Week 14: Quality gates + peer review simulation passing
  ✓ Week 16: End-to-end: question → submit-ready PDF ← THE GOAL
```

---

## Key Architecture Decisions

1. **Extend, Don't Rewrite** — Build on existing Mini-Agent + 62 BPS tools
2. **Phase-Gated Tools** — Max 15 tools visible per phase (prevents LLM confusion)
3. **MCP-First Integration** — 22 servers via config before writing any code
4. **Docker Sandbox** — Isolated statistical computation (no network, read-only)
5. **Section-by-Section Writing** — Hierarchical decomposition for token management
6. **Verify-Before-Use Citations** — Zero tolerance for hallucinated references
7. **Human-in-the-Loop** — Approval gates at methodology and interpretation

---

## References

| Project | What We Learn From It |
|---------|----------------------|
| [AI Scientist v2](https://github.com/SakanaAI/AI-Scientist) (Sakana AI) | First AI to produce peer-review-accepted papers |
| [Robin](https://github.com/FutureHouse/robin) (FutureHouse) | Autonomous scientific discovery architecture |
| [PaperQA2](https://github.com/Future-House/paper-qa) (FutureHouse) | Superhuman literature search & RAG |
| [Anthropic Multi-Agent](https://www.anthropic.com/engineering/built-multi-agent-research-system) | Production multi-agent patterns |
| [DSPy](https://github.com/stanfordnlp/dspy) (Stanford) | Optimizable LLM pipeline framework |
| [GPT-Researcher](https://github.com/assafelovic/gpt-researcher) | Deep research report generation |
| [LightRAG](https://github.com/HKUDS/LightRAG) | Graph-based RAG for knowledge synthesis |
| [MarkItDown](https://github.com/microsoft/markitdown) (Microsoft) | Universal document → Markdown (112K stars) |
| [MinerU](https://github.com/opendatalab/MinerU) (OpenDataLab) | Scientific PDF processing (61K stars) |

---

*Generated: 2025-07-14 | Total research: 4,645 lines of technical documentation*  
*Based on: Comprehensive codebase analysis + deep research into 176+ open-source tools*
