# BPS Academic Research Agent — Open-Source Tools Ecosystem

**Version:** 1.0  
**Created:** 2025-07-14  
**Status:** Deep Research Complete

---

## Executive Summary

Hasil deep research menemukan **100+ open-source tools** yang bisa diintegrasikan dengan Mini-Agent untuk transformasi ke Academic Research Agent. Dokumen ini mengkategorikan semua tools berdasarkan fungsi, dengan rekomendasi prioritas integrasi.

---

## 🏆 TOP 10 CRITICAL TOOLS (Must-Integrate)

| # | Tool | Category | Why Critical |
|---|------|----------|-------------|
| 1 | **MarkItDown** (Microsoft) | Document Processing | Universal file → Markdown, 112K⭐, MIT |
| 2 | **MinerU** (OpenDataLab) | PDF Processing | Best for scientific papers, LaTeX equations, 61K⭐ |
| 3 | **PaperQA2** (FutureHouse) | Scientific RAG | Superhuman performance on lit search, Apache 2.0 |
| 4 | **DSPy** (Stanford) | Pipeline Framework | Optimizable LLM pipelines, 25K⭐, MIT |
| 5 | **LiteLLM** | LLM Gateway | Multi-provider routing, cost tracking, 20K⭐ |
| 6 | **paper-search-mcp** (openags) | MCP Server | 22 academic sources in one MCP server |
| 7 | **Zotero MCP** (54yyyu) | Citation Management | Semantic search + Scite + BibTeX via MCP |
| 8 | **Overleaf MCP** (rangehow) | Paper Writing | 18 tools, compile, git, full CRUD |
| 9 | **Jupyter MCP** (datalayer) | Code Execution | Real-time, multimodal output, 1K⭐ |
| 10 | **ChromaDB/Qdrant MCP** | Vector Search | Official MCP servers for paper embeddings |

---

## 1. 📄 Document Processing & Knowledge Extraction

### Tier 1: Universal Converters

| Tool | Stars | License | Formats | Best For |
|------|-------|---------|---------|----------|
| **MarkItDown** (Microsoft) | 112K | MIT | PDF, DOCX, PPTX, XLSX, HTML, Images, Audio, Video, ZIP, YouTube, EPub | Universal first-pass converter |
| **Docling** (IBM) | 59K | MIT | PDF, DOCX, XLSX, PPTX, HTML, Images, Audio, Video, LaTeX | Advanced PDF with ML layout analysis |
| **MinerU** (OpenDataLab) | 61K | Apache 2.0+ | PDF, Images, DOCX, PPTX, XLSX, Web | Scientific papers (LaTeX equations, cross-page tables) |
| **Unstructured.io** | 14.5K | Apache 2.0 | 25+ formats | ETL pipeline, RAG chunking |

### Tier 2: Specialized PDF Tools

| Tool | Stars | License | Specialty |
|------|-------|---------|-----------|
| **Marker** (Datalab) | 34K | GPL-3.0 | ML-based PDF→Markdown, LaTeX equations |
| **Surya** (Datalab) | 20K | GPL-3.0 | OCR (90+ langs), layout analysis, LaTeX OCR |
| **PyMuPDF / pymupdf4llm** | 9.5K | AGPL-3.0 | Fastest PDF processing, LLM-optimized output |
| **pdfplumber** | 7K | MIT | Deterministic table extraction |
| **Nougat** (Meta) | 9K | MIT | Neural academic PDF → LaTeX (experimental) |
| **Tesseract OCR** | 65K | Apache 2.0 | Universal OCR fallback |

### Tier 3: Academic-Specific

| Tool | Purpose | Integration |
|------|---------|-------------|
| **GROBID** | ML-based bibliographic data extraction from papers | REST API, Docker |
| **PaperMage** (Allen AI) | Process/analyze scholarly PDFs (EMNLP 2023 Best Paper) | Python |
| **anystyle** | Parse references from any format | Ruby gem / REST |

### 🎯 Recommended Stack

```
Universal Intake:  MarkItDown (any file → Markdown)
Academic PDFs:     MinerU (equations + tables + 109 languages)
Fallback PDF:      PyMuPDF + pymupdf4llm (fastest, no ML needed)
RAG Pipeline:      Unstructured (structure-aware chunking)
OCR Fallback:      Surya (90+ langs) or Tesseract
```

---

## 2. 🔬 Academic Research Frameworks

### Core Frameworks

| Tool | Stars | License | What It Does | Integration |
|------|-------|---------|-------------|-------------|
| **PaperQA2** (FutureHouse) | 8K | Apache 2.0 | Superhuman scientific RAG — search, evidence gathering, citation-grounded answers | Python API + CLI |
| **DSPy** (Stanford) | 25K | MIT | Optimizable LLM pipeline framework — signatures, modules, auto-optimization | Python framework |
| **LiteLLM** | 20K | MIT | Multi-provider LLM gateway — 100+ providers, cost tracking, fallbacks | REST + Python |
| **OpenScholar** (Allen AI) | Research | Open | Scientific literature synthesis — outperforms GPT-4o on research tasks | Self-hosted |

### Academic Search APIs & SDKs

| Tool | Type | Coverage | Integration |
|------|------|----------|-------------|
| **Semantic Scholar API** | REST API | 200M+ papers | `pip install semanticscholar` |
| **Elicit API** | REST + MCP | 138M+ papers | MCP server + Python SDK |
| **ScholarAI** | REST + MCP | 200M+ papers | MCP server |
| **Pyzotero** | Python + MCP | Local library + S2 | Built-in MCP server |
| **CrossRef API** | REST | 150M+ DOIs | `pip install habanero` |
| **OpenAlex API** | REST | 474M works | Direct HTTP |
| **CORE API** | REST | 300M+ records, 40M PDFs | API key required |
| **Unpaywall API** | REST | 30M+ DOIs with OA | Email param |

### Reference Managers

| Tool | Type | Best For |
|------|------|----------|
| **Zotero + Pyzotero** | Open-source + MCP | Full reference management with AI integration |
| **JabRef** | Open-source (Java) | BibTeX-native, CLI scriptable |
| **bibtexparser** | Python library | Programmatic BibTeX read/write |

---

## 3. 🔌 MCP Servers (Ready to Plug In)

### Paper Discovery (22+ sources in one server!)

| Server | Sources | Tools |
|--------|---------|-------|
| **openags/paper-search-mcp** | arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, Semantic Scholar, CrossRef, OpenAlex, PMC, CORE, Europe PMC, dblp, OpenAIRE, CiteSeerX, DOAJ, BASE, Zenodo, HAL, SSRN, Unpaywall, IEEE, ACM | Multi-source unified search |
| **jdxbla/PaperMCP** | ArXiv, HuggingFace, Google Scholar, OpenReview, DBLP, PapersWithCode | 32 unified tools |
| **u9401066/pubmed-search-mcp** | PubMed, Europe PMC, CORE, OpenAlex | 40 tools! Full-text, citation networks, PICO |

### Citation Management

| Server | Features |
|--------|----------|
| **54yyyu/zotero-mcp** | Semantic search via ChromaDB, Scite citation intelligence, BibTeX, PDF annotations |
| **danielostrow/zotero-mcp-server** | Full CRUD, 10K+ citation styles (APA/MLA/IEEE/Nature), PDF text extraction |

### Paper Writing & LaTeX

| Server | Features |
|--------|----------|
| **rangehow/overleaf-mcp** | 18 tools: full CRUD, LaTeX structure, git history/diff, PDF compile/download |
| **johannesbrandenburger/typst-mcp** | LaTeX↔Typst conversion, syntax validation, image rendering |

### Document Processing

| Server | Features |
|--------|----------|
| **rsp2k/mcp-pdf** | 46 tools! Text, OCR, tables, forms, annotations, merge/split, vector graphics |
| **MarkItDown MCP** (Microsoft) | 29+ formats → Markdown |

### Knowledge & Memory

| Server | Features |
|--------|----------|
| **neo4j-contrib/mcp-neo4j** (940⭐) | Cypher queries, Knowledge Graph Memory, Data Modeling, GDS |
| **qdrant/mcp-server-qdrant** (Official) | Semantic memory layer, FastEmbed |
| **chroma-core/chroma-mcp** (Official) | Collections, semantic + full-text search |

### Code Execution

| Server | Features |
|--------|----------|
| **datalayer/jupyter-mcp-server** (1023⭐) | Real-time, multimodal output, multi-notebook |
| **scooter-lacroix/sandbox-mcp** | Persistent execution, artifact capture, Manim rendering |
| **finite-sample/rmcp** | 52 statistical tools, 429 R packages! |

### RAG

| Server | Features |
|--------|----------|
| **jesse-merhi/rag-anything-mcp** | Multimodal RAG — images, tables, equations, charts |
| **arunmadhusud/arxiv-rag-mcp** | Paper-specific RAG with semantic search |

---

## 4. 📊 Data Analysis & Scientific Computing

### Code Execution Sandboxes

| Tool | Type | Best For |
|------|------|----------|
| **E2B** (e2b.dev) | Cloud sandbox | Secure AI code execution, Jupyter-compatible |
| **Open Interpreter** | Local execution | Full system access, conversational |
| **Jupyter MCP** | MCP server | Real-time notebook control |
| **Docker sandbox** | Self-hosted | Maximum isolation (our current plan) |

### AI-Powered Data Analysis

| Tool | Stars | What It Does |
|------|-------|-------------|
| **PandasAI** | 14K+ | Natural language → pandas operations |
| **LIDA** (Microsoft) | 5K+ | Automatic visualization + data analysis |
| **ydata-profiling** | 12K+ | Automated EDA reports |
| **sweetviz** | 3K+ | Beautiful EDA comparisons |

### Statistical Computing (Python)

| Package | Purpose | Key Feature |
|---------|---------|-------------|
| **statsmodels** | Regression, time series, diagnostics | Full summary tables |
| **scipy.stats** | Hypothesis tests | 30+ statistical tests |
| **linearmodels** | Panel data (FE/RE/Hausman) | Econometrics |
| **arch** | GARCH, unit root tests | Volatility modeling |
| **pingouin** | Effect sizes, Bayesian, power | APA-ready output |
| **PyMC** | Probabilistic programming | Bayesian inference |
| **DoWhy** (Microsoft) | Causal inference | DAG-based causality |
| **causalml** | Treatment effect estimation | Uplift modeling |
| **Bambi** | Bayesian models | Formula interface |
| **Lifelines** | Survival analysis | Kaplan-Meier, Cox |

### Data Validation

| Tool | Purpose |
|------|---------|
| **Great Expectations** | Data quality testing |
| **Pandera** | DataFrame schema validation |
| **Pydantic** (already in project) | Data model validation |

---

## 5. ✍️ Paper Writing & Document Generation

### LaTeX Ecosystem

| Tool | Purpose | Integration |
|------|---------|-------------|
| **PyLaTeX** | Programmatic LaTeX generation | Python API |
| **Tectonic** | Modern LaTeX engine (Rust) | CLI, no TeX Live needed |
| **latexdiff** | Track changes between versions | CLI |
| **texcount** | Word counting in LaTeX | CLI |
| **Typst** | Modern LaTeX alternative | CLI + Python |

### Writing Quality

| Tool | Stars | Purpose |
|------|-------|---------|
| **LanguageTool** | 12K+ | Open-source grammar checker (Java, REST API) |
| **proselint** | 4K+ | Linter for English prose |
| **textstat** | 2K+ | Readability statistics (Flesch-Kincaid, etc.) |
| **write-good** | 5K+ | Naive linter for English prose |

### Citation Tools

| Tool | Purpose |
|------|---------|
| **GROBID** | Extract bibliographic data from PDFs (ML-based) |
| **anystyle** | Parse references from any format |
| **citeproc-py** | CSL citation processing |
| **bibtexparser** | BibTeX read/write |
| **habanero** | Python CrossRef client |
| **scholarly** | Google Scholar scraper |

### Figure & Diagram Generation

| Tool | Purpose |
|------|---------|
| **Mermaid** | Diagrams from text (flowcharts, sequence, etc.) |
| **tikzplotlib** | matplotlib → TikZ (LaTeX-native figures) |
| **Manim** | Mathematical animations |
| **PlantUML** | UML diagrams from text |

---

## 6. 🧠 RAG & Knowledge Management

### RAG Frameworks

| Tool | Stars | Best For |
|------|-------|----------|
| **LlamaIndex** | 40K+ | Data framework for LLM apps, best indexing |
| **LangChain** | 100K+ | General LLM framework, broadest ecosystem |
| **Haystack** (deepset) | 18K+ | Production NLP/RAG pipelines |
| **RAGFlow** | 30K+ | Deep document understanding RAG |
| **PaperQA2** | 8K | Scientific paper RAG (superhuman) |

### Vector Databases

| Tool | Stars | Type | Best For |
|------|-------|------|----------|
| **ChromaDB** | 18K+ | Embedded | Simple, local-first |
| **Qdrant** | 22K+ | Server | Production, filtering |
| **Milvus** | 32K+ | Distributed | Scale |
| **LanceDB** | 5K+ | Serverless | Embedded, multimodal |
| **FAISS** (Meta) | 33K+ | Library | Pure similarity search |

### Embedding Models for Academic Papers

| Model | Source | Best For |
|-------|--------|----------|
| **SPECTER2** | Semantic Scholar | Scientific paper embeddings |
| **SciBERT** | Allen AI | Scientific text |
| **all-MiniLM-L6-v2** | Sentence-Transformers | General purpose (fast) |
| **nomic-embed-text** | Nomic AI | Open-source, good quality |
| **voyage-3** | Voyage AI | Best retrieval quality |

### Knowledge Graphs

| Tool | Purpose |
|------|---------|
| **Neo4j** (Community) | Graph database for citation networks |
| **GraphRAG** (Microsoft) | Graph-based RAG |
| **LightRAG** | Lightweight graph RAG |
| **NetworkX** | Python graph analysis |

### Academic NLP

| Tool | Purpose |
|------|---------|
| **scispaCy** | Scientific/biomedical NLP |
| **stanza** (Stanford) | Multi-language NLP |
| **spaCy** | Industrial NLP pipeline |

---

## 7. 🔗 Integration Architecture

### How Everything Connects

```
┌─────────────────────────────────────────────────────────────────┐
│                    BPS ACADEMIC RESEARCH AGENT v1.0               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─── DSPy Pipeline Framework ──────────────────────────────┐   │
│  │  Optimizable modules: Search → Evidence → Synthesis       │   │
│  └───────────────────────────────────────────────────────────┘   │
│                              │                                    │
│  ┌─── LiteLLM Gateway ──────▼───────────────────────────────┐   │
│  │  Anthropic | OpenAI | Gemini | Local | Cost tracking       │   │
│  └───────────────────────────────────────────────────────────┘   │
│                              │                                    │
│  ┌─── MCP Server Layer ─────▼───────────────────────────────┐   │
│  │                                                            │   │
│  │  EXISTING:                                                 │   │
│  │  • BPS WebAPI (62 tools)                                   │   │
│  │                                                            │   │
│  │  NEW - Paper Discovery:                                    │   │
│  │  • paper-search-mcp (22 academic sources)                  │   │
│  │  • pubmed-search-mcp (40 tools, biomedical)                │   │
│  │                                                            │   │
│  │  NEW - Citation Management:                                │   │
│  │  • zotero-mcp (semantic search + Scite + BibTeX)           │   │
│  │                                                            │   │
│  │  NEW - Paper Writing:                                      │   │
│  │  • overleaf-mcp (18 tools, compile, git)                   │   │
│  │                                                            │   │
│  │  NEW - Document Processing:                                │   │
│  │  • mcp-pdf (46 tools, OCR, tables)                         │   │
│  │  • markitdown-mcp (29+ formats)                            │   │
│  │                                                            │   │
│  │  NEW - Knowledge:                                          │   │
│  │  • neo4j-mcp (knowledge graph)                             │   │
│  │  • qdrant-mcp (vector search)                              │   │
│  │                                                            │   │
│  │  NEW - Computation:                                        │   │
│  │  • jupyter-mcp (code execution)                            │   │
│  │  • rmcp (52 R statistical tools)                           │   │
│  │                                                            │   │
│  └───────────────────────────────────────────────────────────┘   │
│                              │                                    │
│  ┌─── Native Tools ─────────▼───────────────────────────────┐   │
│  │  PaperQA2 (scientific RAG) | MinerU (PDF processing)      │   │
│  │  MarkItDown (universal converter) | Unstructured (ETL)     │   │
│  │  statsmodels | scipy | pingouin | matplotlib               │   │
│  └───────────────────────────────────────────────────────────┘   │
│                              │                                    │
│  ┌─── Storage Layer ────────▼───────────────────────────────┐   │
│  │  ChromaDB/Qdrant (embeddings) | Neo4j (citation graph)    │   │
│  │  Disk (project.yaml, .bib, .tex, figures, data)            │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. 📋 Integration Priority Matrix

### Phase 1 (Foundation) — Add These First

| Tool | Integration Method | Effort | Impact |
|------|-------------------|--------|--------|
| MarkItDown | `pip install markitdown[all]` + native tool | Low | High — universal document intake |
| LiteLLM | Replace direct LLM calls with LiteLLM proxy | Medium | High — multi-provider, cost tracking |
| ChromaDB | `pip install chromadb` + vector store for papers | Medium | High — semantic search over literature |

### Phase 2 (Research) — Add These Next

| Tool | Integration Method | Effort | Impact |
|------|-------------------|--------|--------|
| paper-search-mcp | MCP config (already have MCP support!) | Low | Very High — 22 sources instantly |
| zotero-mcp | MCP config | Low | High — citation management |
| PaperQA2 | `pip install paper-qa` + native tool | Medium | Very High — superhuman lit search |
| SPECTER2 embeddings | sentence-transformers + ChromaDB | Medium | High — paper similarity |

### Phase 3 (Analysis) — Add These

| Tool | Integration Method | Effort | Impact |
|------|-------------------|--------|--------|
| jupyter-mcp | MCP config | Low | High — code execution |
| MinerU | `pip install mineru` + native tool | Medium | High — scientific PDF processing |
| DSPy | Restructure pipeline as DSPy modules | High | Very High — optimizable workflows |

### Phase 4 (Writing) — Add These

| Tool | Integration Method | Effort | Impact |
|------|-------------------|--------|--------|
| overleaf-mcp | MCP config | Low | High — LaTeX compilation |
| mcp-pdf | MCP config | Low | Medium — PDF manipulation |
| LanguageTool | REST API or Java server | Medium | Medium — grammar checking |
| Neo4j MCP | MCP config + Docker | Medium | High — citation graph |

---

## 9. 🚀 Quick Wins (Can Add TODAY via MCP Config)

Since Mini-Agent already has full MCP support, these can be added by simply updating `mcp.json`:

```json
{
  "mcpServers": {
    "bps": { "...existing BPS config..." },
    
    "papers": {
      "command": "npx",
      "args": ["-y", "@openags/paper-search-mcp"],
      "env": {}
    },
    "zotero": {
      "command": "uvx",
      "args": ["pyzotero[mcp]"],
      "env": { "ZOTERO_API_KEY": "..." }
    },
    "pdf": {
      "command": "uvx",
      "args": ["mcp-pdf"],
      "env": {}
    },
    "jupyter": {
      "command": "uvx",
      "args": ["jupyter-mcp-server"],
      "env": {}
    },
    "qdrant": {
      "command": "uvx",
      "args": ["mcp-server-qdrant"],
      "env": { "QDRANT_URL": "http://localhost:6333" }
    }
  }
}
```

**This alone would add 100+ new tools to the agent with ZERO code changes!**

---

## 10. ❌ Tools NOT Worth Integrating

| Tool | Reason to Skip |
|------|---------------|
| Galactica (Meta) | Abandoned, superseded by modern LLMs |
| SciSpace/Typeset | No API, fully proprietary |
| ResearchRabbit | No API, web-only |
| Connected Papers | No API |
| Mendeley | Declining, features being removed |
| Google Scholar (direct) | No official API, scraping is fragile |

---

## 11. License Compatibility Summary

| License | Tools | Commercial OK? |
|---------|-------|---------------|
| **MIT** | MarkItDown, Docling, PaperQA2, DSPy, LiteLLM, ChromaDB, pdfplumber, Nougat, bibtexparser | ✅ Yes |
| **Apache 2.0** | MinerU, Unstructured, Tesseract, Semantic Scholar SDK, Haystack | ✅ Yes |
| **GPL-3.0** | Marker, Surya | ⚠️ Copyleft (derivatives must be GPL) |
| **AGPL-3.0** | PyMuPDF | ⚠️ Network copyleft |

**Recommendation:** Prefer MIT/Apache tools. Use GPL tools only if your project is also open-source (which it is — MIT license).

---

---

## 12. 🧠 RAG & Knowledge Stack (Detailed Recommendations)

### Recommended RAG Architecture for Academic Papers

```
┌─────────────────────────────────────────────────────────────┐
│  ACADEMIC PAPER RAG PIPELINE                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PDF Input → RAGFlow DepDoc (Paper mode)                     │
│  → Structured sections, tables, figures, equations           │
│                                                              │
│  Embedding Strategy (DUAL):                                  │
│  • Paper-level: SPECTER2 (title+abstract, citation-aware)    │
│  • Chunk-level: nomic-embed-text (8192 token context!)       │
│                                                              │
│  Vector Store: LanceDB (embedded, serverless, multimodal)    │
│  OR Qdrant (server-mode, rich metadata filtering)            │
│                                                              │
│  Knowledge Graph: LightRAG (34K⭐, outperforms GraphRAG)     │
│  → Auto-extract entities/relationships from papers           │
│  → Answer holistic questions about research landscape        │
│                                                              │
│  Chunking: Chonkie SemanticChunker (33x faster, 9 strategies)│
│                                                              │
│  Scientific NLP: scispaCy (entity extraction from papers)    │
│                                                              │
│  Orchestration: LlamaIndex (multi-document agentic RAG)      │
│                                                              │
│  Citation Analysis: NetworkX (PageRank, community detection) │
└─────────────────────────────────────────────────────────────┘
```

### Key Embedding Models for Academic Papers

| Model | Context | Best For | Source |
|-------|---------|----------|--------|
| **SPECTER2** | 512 tokens | Paper similarity (trained on 6M citation triplets) | Semantic Scholar |
| **nomic-embed-text** | **8192 tokens** | Chunk retrieval (full paragraphs/sections) | Nomic AI |
| **SciBERT** | 512 tokens | Scientific NER, classification | Allen AI |

### Graph RAG Comparison

| Tool | Stars | Performance | Best For |
|------|-------|-------------|----------|
| **LightRAG** | 34K | Outperforms GraphRAG on all benchmarks | Primary choice |
| **GraphRAG** (Microsoft) | 25K | Good but heavier | If you need hierarchical communities |
| **Neo4j** | N/A | Explicit structured queries | Citation network storage |

---

## 13. 📊 Complete Tool Count Summary

| Category | Tools Researched | Recommended | Quick Win (MCP) |
|----------|:---------------:|:-----------:|:---------------:|
| Document Processing | 11 | 4 | 2 |
| Academic Frameworks | 15 | 6 | 3 |
| MCP Servers | 80+ | 12 | 12 |
| Data Analysis | 27 | 15 | 1 |
| Paper Writing | 18 | 10 | 2 |
| RAG & Knowledge | 25 | 10 | 2 |
| **TOTAL** | **176+** | **57** | **22** |

---

*This document represents findings from 6 parallel Librarian agents researching 176+ tools across document processing, academic frameworks, MCP servers, data analysis, paper writing, and RAG/knowledge management.*
