# BPS Academic Research Agent — Tools Specification v2

**Version:** 2.0  
**Created:** 2025-07-14  
**Updated:** 2025-07-15 — Complete 52-tool specification with all discovered integrations  
**Status:** Final

---

## Overview

This document specifies **all 52 tools** available to the BPS Academic Research Agent. Each tool follows the existing `Tool` ABC pattern and is organized by functional category. Tools are phase-gated — only tools relevant to the current research phase are visible to the LLM (max ~15 at once).

```python
class Tool:
    @property
    def name(self) -> str: ...
    @property
    def description(self) -> str: ...
    @property
    def parameters(self) -> dict[str, Any]: ...  # JSON Schema
    async def execute(self, **kwargs) -> ToolResult: ...
```

### Tool Count by Category

| # | Category | Tools | IDs |
|---|----------|:-----:|-----|
| 1 | Framework & Project | 5 | 1–5 |
| 2 | Document Processing | 4 | 6–9 |
| 3 | RAG & Knowledge | 6 | 10–15 |
| 4 | Literature & Citations | 3 | 16–18 |
| 5 | Analysis (Statistical) | 11 | 19–29 |
| 6 | Paper Writing & Compilation | 8 | 30–37 |
| 7 | Visualization & Figures | 3 | 38–40 |
| 8 | Data Validation & Quality | 3 | 41–43 |
| 9 | Quality Assurance & Review | 4 | 44–47 |
| 10 | Legacy Enhanced (from v1) | 5 | 48–52 |
| | **TOTAL** | **52** | |

### Phase Visibility Matrix

| Phase | Visible Tools (max ~15) | Purpose |
|-------|------------------------|---------|
| PLAN | 1–5, 10, 16, 21 | Project setup, initial lit scan, LLM config |
| COLLECT | 6–9, 10–15, 16–18 | Document processing, RAG, citations |
| ANALYZE | 19–29, 41–43 | Statistical analysis, data validation |
| WRITE | 30–40 | Writing, compilation, figures, diagrams |
| REVIEW | 44–47, 32–34, 18 | Quality gates, peer review, reproducibility |

**Design principle:** Never exceed 15 tools visible at once per phase.

---

## Category 1: Framework & Project Tools

### Tool 1: `project_init`

**Purpose:** Initialize a new research project with standard workspace structure.  
**Phase(s):** PLAN  
**Dependencies:** `pyyaml`, `jinja2` (templates)

```python
name = "project_init"
description = """Initialize a new research project with standard workspace structure.
Creates directories: data/raw/, data/processed/, literature/, literature/pdfs/,
analysis/scripts/, analysis/results/, analysis/figures/, analysis/tables/,
writing/sections/, writing/compiled/, review/, embeddings/, knowledge_graph/.
Sets up: project.yaml (master state), references.bib, outline.yaml, main.tex template.
Configures target journal template and initializes DSPy pipeline modules.
Also creates: methodology_spec.yaml, research_questions.yaml placeholders."""

parameters = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Research paper title"
        },
        "target_journal": {
            "type": "string",
            "description": "Target journal name (e.g., 'Bulletin of Indonesian Economic Studies')"
        },
        "template": {
            "type": "string",
            "enum": ["ieee", "elsevier", "springer", "springer_lncs", "mdpi", "apa7", "nature", "plos"],
            "description": "Journal LaTeX template to use"
        },
        "research_questions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Initial research questions (can be refined later)"
        },
        "methodology": {
            "type": "string",
            "enum": ["panel_data", "cross_sectional", "time_series", "mixed_methods", "meta_analysis"],
            "description": "Primary methodology approach (optional)"
        }
    },
    "required": ["title", "template"]
}
```

**Returns:** `ToolResult` with project path, created structure tree, and initialization status.

**Example:**
```python
result = await project_init(
    title="Pengaruh Desentralisasi Fiskal terhadap Ketimpangan di Indonesia",
    template="elsevier",
    research_questions=["How does fiscal decentralization affect Gini coefficient?"],
    methodology="panel_data"
)
```

---

### Tool 2: `project_status`

**Purpose:** Show current project status and progress across all phases.  
**Phase(s):** ALL (always available)  
**Dependencies:** `pyyaml`

```python
name = "project_status"
description = """Show current research project status and progress.
Returns: current phase, progress per section, data inventory (files + sizes),
literature count (total papers, verified, with full-text), quality gate status
(pass/fail per gate), pending tasks, last activity timestamp.
Also shows: embedding count, knowledge graph stats, compilation status."""

parameters = {
    "type": "object",
    "properties": {
        "verbose": {
            "type": "boolean",
            "description": "Include detailed breakdown per category (default: false)"
        },
        "section": {
            "type": "string",
            "enum": ["all", "data", "literature", "analysis", "writing", "review"],
            "description": "Show status for specific section only (default: all)"
        }
    },
    "required": []
}
```

**Returns:** `ToolResult` with structured YAML status report.

**Example:**
```python
result = await project_status(verbose=True, section="literature")
```

---

### Tool 3: `switch_phase`

**Purpose:** Transition to a different research phase with state persistence.  
**Phase(s):** ALL (always available)  
**Dependencies:** `pyyaml`

```python
name = "switch_phase"
description = """Switch to a different research phase.
Persists current phase state (progress, artifacts, pending tasks).
Loads phase-appropriate tools (unloads current, loads target).
Injects phase-relevant context summary into LLM context.
Validates prerequisites: e.g., cannot enter ANALYZE without data.
Phases: plan -> collect -> analyze -> write -> review.
Non-linear transitions allowed (e.g., review -> analyze for revisions)."""

parameters = {
    "type": "object",
    "properties": {
        "target_phase": {
            "type": "string",
            "enum": ["plan", "collect", "analyze", "write", "review"],
            "description": "Phase to switch to"
        },
        "reason": {
            "type": "string",
            "description": "Reason for phase transition (logged in project.yaml)"
        },
        "force": {
            "type": "boolean",
            "description": "Skip prerequisite checks (default: false)"
        }
    },
    "required": ["target_phase"]
}
```

**Returns:** `ToolResult` with new phase context, loaded tools list, and prerequisite warnings.

**Example:**
```python
result = await switch_phase(target_phase="analyze", reason="Data collection complete")
```

---

### Tool 4: `litellm_config`

**Purpose:** Configure LLM routing with provider fallbacks, cost limits, and model selection.  
**Phase(s):** ALL (always available)  
**Dependencies:** `litellm>=1.40`

```python
name = "litellm_config"
description = """Configure LLM routing through LiteLLM gateway.
Manages: provider selection (Anthropic, OpenAI, Gemini, local models),
automatic fallback chains, cost tracking and budget limits,
rate limiting, caching, and model-specific parameters.
Supports 100+ LLM providers through unified interface.
Changes persist in project.yaml under 'llm_config' key."""

parameters = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": ["set_model", "set_fallbacks", "set_budget", "get_usage", "set_cache", "list_models"],
            "description": "Configuration action to perform"
        },
        "model": {
            "type": "string",
            "description": "Primary model (e.g., 'claude-sonnet-4-20250514', 'gpt-4o')"
        },
        "fallback_models": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Ordered fallback model list"
        },
        "budget_limit_usd": {
            "type": "number",
            "description": "Maximum spend in USD (alerts at 80%)"
        },
        "cache_enabled": {
            "type": "boolean",
            "description": "Enable response caching (default: true)"
        },
        "temperature": {"type": "number", "description": "Default temperature (0.0-1.0)"},
        "max_tokens": {"type": "integer", "description": "Default max tokens"}
    },
    "required": ["action"]
}
```

**Returns:** `ToolResult` with current config state, usage stats, or model list.

**Example:**
```python
result = await litellm_config(
    action="set_fallbacks",
    model="claude-sonnet-4-20250514",
    fallback_models=["gpt-4o", "gemini-2.0-flash"],
    budget_limit_usd=50.0
)
```

---

### Tool 5: `dspy_optimize`

**Purpose:** Run DSPy optimization on research pipeline modules.  
**Phase(s):** PLAN, WRITE  
**Dependencies:** `dspy>=2.0`, `litellm>=1.40`

```python
name = "dspy_optimize"
description = """Run DSPy optimization on research pipeline modules.
Optimizes LLM prompts and few-shot examples for specific tasks:
- ResearchQuestionFormulator: generates structured RQs from topic + gaps
- SectionWriter: writes paper sections with citation grounding
- AbstractGenerator: generates structured abstracts from full paper
- CoherenceChecker: validates cross-section consistency
- LiteratureSynthesizer: synthesizes themes from multiple papers
Uses BootstrapFewShot or MIPRO optimizers with custom academic metrics.
Optimization results are cached and reused across the project."""

parameters = {
    "type": "object",
    "properties": {
        "module": {
            "type": "string",
            "enum": ["research_question_formulator", "section_writer", "abstract_generator",
                     "coherence_checker", "literature_synthesizer", "all"],
            "description": "DSPy module to optimize"
        },
        "optimizer": {
            "type": "string",
            "enum": ["bootstrap_fewshot", "bootstrap_fewshot_random", "mipro", "copro"],
            "description": "Optimization strategy (default: bootstrap_fewshot_random)"
        },
        "num_candidates": {"type": "integer", "description": "Candidate programs to evaluate (default: 10)"},
        "max_demos": {"type": "integer", "description": "Max bootstrapped demos (default: 4)"},
        "trainset_path": {"type": "string", "description": "Path to training examples JSON (optional)"},
        "metric": {
            "type": "string",
            "enum": ["academic_quality", "citation_density", "coherence", "factual_accuracy"],
            "description": "Optimization metric (default: academic_quality)"
        }
    },
    "required": ["module"]
}
```

**Returns:** `ToolResult` with optimization score (before/after), best program path, metric breakdown.

**Example:**
```python
result = await dspy_optimize(module="section_writer", optimizer="bootstrap_fewshot_random", num_candidates=10)
# Returns: score_before=0.62, score_after=0.84
```

---

## Category 2: Document Processing Tools

### Tool 6: `convert_document`
**Purpose:** Convert any file format to Markdown using Microsoft MarkItDown.  
**Phase(s):** COLLECT | **Dependencies:** `markitdown[all]>=0.1.5`

```python
name = "convert_document"
description = """Convert any document to clean Markdown using Microsoft MarkItDown.
Supports 29+ formats: PDF, DOCX, PPTX, XLSX, HTML, Images (OCR), Audio, Video, ZIP, YouTube, EPub.
For scientific PDFs with equations/tables, prefer parse_academic_pdf (MinerU).
Output is clean Markdown with preserved structure. Images extracted separately."""
parameters = {
    "type": "object",
    "properties": {
        "input_path": {"type": "string", "description": "Path to input file or URL"},
        "output_path": {"type": "string", "description": "Output Markdown path (default: same name .md)"},
        "extract_images": {"type": "boolean", "description": "Extract embedded images (default: true)"},
        "ocr_enabled": {"type": "boolean", "description": "Enable OCR for scanned content (default: true)"}
    },
    "required": ["input_path"]
}
```
**Returns:** `ToolResult` with Markdown content, extracted images list, conversion metadata.

---

### Tool 7: `parse_academic_pdf`
**Purpose:** Parse scientific PDFs with LaTeX equation/table preservation using MinerU.  
**Phase(s):** COLLECT | **Dependencies:** `mineru>=3.0`, `torch`

```python
name = "parse_academic_pdf"
description = """Parse scientific/academic PDFs into structured Markdown using MinerU (OpenDataLab).
Preserves LaTeX equations, handles cross-page tables, extracts figures with captions,
maintains section hierarchy, supports 109 languages. Uses ML-based layout analysis.
Returns: title, authors, abstract, sections[], equations[], tables[], figures[], references[]."""
parameters = {
    "type": "object",
    "properties": {
        "pdf_path": {"type": "string", "description": "Path to academic PDF file"},
        "output_dir": {"type": "string", "description": "Output directory (default: literature/processed/)"},
        "extract_equations": {"type": "boolean", "description": "Convert equations to LaTeX (default: true)"},
        "extract_tables": {"type": "boolean", "description": "Extract tables as structured data (default: true)"},
        "extract_figures": {"type": "boolean", "description": "Extract figures with captions (default: true)"},
        "language": {"type": "string", "description": "Document language (default: 'en')"}
    },
    "required": ["pdf_path"]
}
```
**Returns:** `ToolResult` with structured paper object (title, abstract, sections, equations, tables, figures, references).

---

### Tool 8: `extract_references`
**Purpose:** Extract structured bibliography from PDF using GROBID ML-based parser.  
**Phase(s):** COLLECT | **Dependencies:** GROBID Docker (`lfoppiano/grobid:0.8.0`)

```python
name = "extract_references"
description = """Extract structured bibliographic data from PDF using GROBID.
Returns: authors (first/last), title, journal, volume, pages, year, DOI per reference.
Also extracts paper header (title, authors, affiliations, abstract).
Cross-references with CrossRef for DOI resolution. Runs via Docker on localhost:8070."""
parameters = {
    "type": "object",
    "properties": {
        "pdf_path": {"type": "string", "description": "Path to PDF file"},
        "output_format": {"type": "string", "enum": ["bibtex", "tei_xml", "json"], "description": "Output format (default: bibtex)"},
        "include_header": {"type": "boolean", "description": "Extract paper header metadata (default: true)"},
        "consolidate_citations": {"type": "boolean", "description": "Cross-ref with CrossRef for DOIs (default: true)"}
    },
    "required": ["pdf_path"]
}
```
**Returns:** `ToolResult` with extracted references, header metadata, confidence scores.

---

### Tool 9: `chunk_document`
**Purpose:** Semantic chunking of documents for RAG using Chonkie.  
**Phase(s):** COLLECT | **Dependencies:** `chonkie>=0.4`

```python
name = "chunk_document"
description = """Split documents into semantically coherent chunks using Chonkie.
9 strategies: semantic, sentence, token, word, recursive, markdown, code, sliding_window, late.
33x faster than LangChain/LlamaIndex chunkers. For academic papers: use 'semantic' or 'markdown'.
Chunks include overlap for context continuity and metadata (section_type, position)."""
parameters = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "description": "Text content or path to .md/.txt file"},
        "strategy": {"type": "string", "enum": ["semantic", "sentence", "token", "word", "recursive", "markdown", "code", "sliding_window", "late"], "description": "Chunking strategy (default: semantic)"},
        "max_tokens": {"type": "integer", "description": "Max tokens per chunk (default: 512)"},
        "overlap_tokens": {"type": "integer", "description": "Token overlap (default: 50)"},
        "embedding_model": {"type": "string", "description": "Model for semantic boundaries (default: all-MiniLM-L6-v2)"},
        "metadata": {"type": "object", "description": "Additional metadata for all chunks"}
    },
    "required": ["text"]
}
```
**Returns:** `ToolResult` with chunks list (text, token_count, start_idx, end_idx, metadata).

---

## Category 3: RAG & Knowledge Tools

### Tool 10: `paper_qa`
**Purpose:** Ask questions about papers with citation-grounded answers (PaperQA2).  
**Phase(s):** PLAN, COLLECT, WRITE | **Dependencies:** `paper-qa>=5.0`

```python
name = "paper_qa"
description = """Ask questions with citation-grounded answers using PaperQA2 (superhuman performance).
Pipeline: retrieve passages -> gather evidence -> synthesize answer with citations.
Every claim backed by specific source passage with page number.
Useful for: gap analysis, methodology comparison, finding contradictions."""
parameters = {
    "type": "object",
    "properties": {
        "question": {"type": "string", "description": "Research question to answer"},
        "papers_dir": {"type": "string", "description": "PDF directory (default: literature/pdfs/)"},
        "max_sources": {"type": "integer", "description": "Max source papers (default: 10)"},
        "answer_length": {"type": "string", "enum": ["short", "medium", "long"], "description": "Answer length (default: medium)"},
        "evidence_threshold": {"type": "number", "description": "Min relevance score 0-1 (default: 0.5)"}
    },
    "required": ["question"]
}
```
**Returns:** `ToolResult` with answer, evidence passages (source, page, score), formatted citations.

---

### Tool 11: `build_knowledge_graph`
**Purpose:** Extract entities and relationships from papers using LightRAG.  
**Phase(s):** COLLECT | **Dependencies:** `lightrag-hku>=1.5`, `networkx>=3.2`

```python
name = "build_knowledge_graph"
description = """Build knowledge graph from papers using LightRAG (outperforms GraphRAG).
Extracts: entities (methods, variables, datasets, findings, authors),
relationships (uses_method, finds_result, contradicts, extends, cites).
Incremental: add new papers without rebuilding. Stored in knowledge_graph/."""
parameters = {
    "type": "object",
    "properties": {
        "documents": {"type": "array", "items": {"type": "string"}, "description": "Paths to processed Markdown files"},
        "mode": {"type": "string", "enum": ["full_rebuild", "incremental"], "description": "Build mode (default: incremental)"},
        "entity_types": {"type": "array", "items": {"type": "string"}, "description": "Entity types (default: method, variable, dataset, finding, theory)"},
        "output_dir": {"type": "string", "description": "Graph storage directory (default: knowledge_graph/)"}
    },
    "required": ["documents"]
}
```
**Returns:** `ToolResult` with graph statistics (entities, relations, communities).

---

### Tool 12: `query_knowledge_graph`
**Purpose:** Query knowledge graph with holistic/local/hybrid retrieval.  
**Phase(s):** COLLECT, WRITE | **Dependencies:** `lightrag-hku>=1.5`

```python
name = "query_knowledge_graph"
description = """Query LightRAG knowledge graph. Modes:
- 'local': precise entity/relationship lookup
- 'global': holistic questions about research landscape
- 'hybrid': combines local + global (recommended)
Useful for: synthesis, contradictions, methodology comparison, gap identification."""
parameters = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Natural language query"},
        "mode": {"type": "string", "enum": ["local", "global", "hybrid"], "description": "Query mode (default: hybrid)"},
        "max_results": {"type": "integer", "description": "Max entities/relations (default: 20)"}
    },
    "required": ["query"]
}
```
**Returns:** `ToolResult` with synthesized answer, entities, relationships, source papers.

---

### Tool 13: `embed_papers`
**Purpose:** Generate SPECTER2 embeddings for academic papers.  
**Phase(s):** COLLECT | **Dependencies:** `sentence-transformers>=3.0`

```python
name = "embed_papers"
description = """Generate paper-level embeddings using SPECTER2 (trained on 6M+ citation triplets).
Input: title + abstract -> 768-dim vector. Stored in LanceDB for ANN search.
Also supports: nomic-embed-text (8192 context), all-MiniLM-L6-v2 (fast), SciBERT."""
parameters = {
    "type": "object",
    "properties": {
        "papers": {"type": "array", "items": {"type": "object", "properties": {"paper_id": {"type": "string"}, "title": {"type": "string"}, "abstract": {"type": "string"}}, "required": ["paper_id", "title"]}, "description": "Papers to embed"},
        "model": {"type": "string", "enum": ["specter2", "nomic-embed-text", "all-MiniLM-L6-v2", "scibert"], "description": "Embedding model (default: specter2)"},
        "store_in": {"type": "string", "description": "LanceDB table name (default: papers)"},
        "batch_size": {"type": "integer", "description": "Batch size (default: 32)"}
    },
    "required": ["papers"]
}
```
**Returns:** `ToolResult` with embedding count, storage location, sample similarity pairs.

---

### Tool 14: `vector_search`
**Purpose:** Semantic search over embedded papers/chunks using LanceDB.  
**Phase(s):** COLLECT, WRITE | **Dependencies:** `lancedb>=0.9`, `sentence-transformers>=3.0`

```python
name = "vector_search"
description = """Semantic search over LanceDB vector store (serverless, no separate process).
Supports: ANN search, metadata filtering, hybrid search (vector + keyword).
Tables: 'papers' (SPECTER2 paper embeddings), 'chunks' (section-level embeddings)."""
parameters = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Natural language search query"},
        "table": {"type": "string", "enum": ["papers", "chunks"], "description": "Table to search (default: chunks)"},
        "top_k": {"type": "integer", "description": "Number of results (default: 10)"},
        "filters": {"type": "object", "description": "Metadata filters (e.g., {year_min: 2020})"},
        "rerank": {"type": "boolean", "description": "Cross-encoder reranking (default: false)"}
    },
    "required": ["query"]
}
```
**Returns:** `ToolResult` with ranked results (text, score, metadata, source paper).

---

### Tool 15: `extract_entities`
**Purpose:** Scientific named entity recognition using scispaCy.  
**Phase(s):** COLLECT | **Dependencies:** `scispacy>=0.5`, `spacy>=3.7`

```python
name = "extract_entities"
description = """Extract scientific named entities using scispaCy.
Extracts: methods, datasets, metrics, chemicals, diseases, genes/proteins.
Also: abbreviation detection, entity linking to UMLS/MeSH.
Useful for: structured summaries, knowledge graph population, methodology patterns."""
parameters = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "description": "Text or path to file"},
        "entity_types": {"type": "array", "items": {"type": "string", "enum": ["method", "dataset", "metric", "chemical", "disease", "gene_protein", "organism", "all"]}, "description": "Entity types (default: all)"},
        "link_entities": {"type": "boolean", "description": "Link to UMLS/MeSH (default: false)"},
        "detect_abbreviations": {"type": "boolean", "description": "Expand abbreviations (default: true)"}
    },
    "required": ["text"]
}
```
**Returns:** `ToolResult` with entities, abbreviations, frequency counts.

---

## Category 4: Literature & Citation Tools

### Tool 16: `literature_search`
**Purpose:** Search 22+ academic sources via paper-search-mcp. **ENHANCED from v1.**  
**Phase(s):** PLAN, COLLECT | **Dependencies:** `@openags/paper-search-mcp` (MCP)

```python
name = "literature_search"
description = """Search 22 academic sources: arXiv, PubMed, bioRxiv, medRxiv, Google Scholar,
Semantic Scholar, CrossRef, OpenAlex, PMC, CORE, Europe PMC, dblp, OpenAIRE, CiteSeerX,
DOAJ, BASE, Zenodo, HAL, SSRN, Unpaywall, IEEE, ACM.
Deduplicated by DOI, ranked by relevance x citations x recency. Cached."""
parameters = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Search query"},
        "sources": {"type": "array", "items": {"type": "string", "enum": ["semantic_scholar", "crossref", "openalex", "arxiv", "pubmed", "core", "doaj", "base", "zenodo", "hal", "ssrn", "ieee", "acm", "biorxiv", "medrxiv", "google_scholar", "pmc", "europe_pmc", "dblp", "openaire", "citeseerx", "unpaywall"]}, "description": "Databases (default: semantic_scholar, crossref, openalex)"},
        "year_from": {"type": "integer", "description": "Min publication year"},
        "year_to": {"type": "integer", "description": "Max publication year"},
        "open_access_only": {"type": "boolean", "description": "OA only (default: false)"},
        "min_citations": {"type": "integer", "description": "Min citation count (default: 0)"},
        "max_results": {"type": "integer", "description": "Max results per source (default: 20)"},
        "sort_by": {"type": "string", "enum": ["relevance", "citation_count", "year_desc", "year_asc"], "description": "Sort order"}
    },
    "required": ["query"]
}
```
**Returns:** `ToolResult` with deduplicated paper list (title, authors, year, DOI, citations, abstract, OA status).

---

### Tool 17: `citation_manager`
**Purpose:** Manage bibliography with Zotero integration. **ENHANCED from v1.**  
**Phase(s):** COLLECT, WRITE | **Dependencies:** `pyzotero[mcp]`, `bibtexparser>=1.4`

```python
name = "citation_manager"
description = """Manage bibliography with Zotero via zotero-mcp.
Semantic search, Scite citation intelligence (supporting/contrasting/mentioning),
organized collections, 10,000+ citation styles.
DOI adds auto-fetch metadata from CrossRef + Semantic Scholar."""
parameters = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["add_from_doi", "add_manual", "remove", "list", "search_semantic", "search_keyword", "verify_all", "export_formatted", "organize_collection", "scite_check", "get_pdf_annotations"], "description": "Action to perform"},
        "doi": {"type": "string", "description": "DOI (for add_from_doi)"},
        "entry": {"type": "object", "description": "BibTeX fields (for add_manual)"},
        "key": {"type": "string", "description": "Citation key (for remove)"},
        "query": {"type": "string", "description": "Search query"},
        "collection": {"type": "string", "description": "Collection name"},
        "style": {"type": "string", "enum": ["apa", "ieee", "harvard", "chicago", "vancouver", "nature", "science", "elsevier"], "description": "Citation style"}
    },
    "required": ["action"]
}
```
**Returns:** `ToolResult` with action result.

---

### Tool 18: `verify_citations`
**Purpose:** Batch verify citations with retry and cross-database validation. **ENHANCED.**  
**Phase(s):** COLLECT, REVIEW | **Dependencies:** `habanero>=2.3`, `semanticscholar`

```python
name = "verify_citations"
description = """Verify all citations against CrossRef + Semantic Scholar + OpenAlex.
Checks: DOI resolves, title/authors/year match, not retracted, claim-source alignment.
BLOCKS compilation if any citation fails in strict mode. Batch with retry logic."""
parameters = {
    "type": "object",
    "properties": {
        "bib_file": {"type": "string", "description": "Path to .bib file (default: literature/references.bib)"},
        "paper_tex": {"type": "string", "description": "Path to .tex for claim-source alignment"},
        "strict": {"type": "boolean", "description": "Fail on unverifiable (default: true)"},
        "check_retractions": {"type": "boolean", "description": "Check Retraction Watch (default: true)"},
        "verify_claims": {"type": "boolean", "description": "Verify claims in source papers (default: false)"},
        "max_retries": {"type": "integer", "description": "API retries per citation (default: 3)"}
    },
    "required": []
}
```
**Returns:** `ToolResult` with verification report (per-citation pass/fail, issues, retraction alerts).

---

## Category 5: Analysis Tools (Statistical)

### Tool 19: `python_repl`
**Purpose:** Execute Python in sandboxed environment (E2B cloud + Docker local). **ENHANCED.**  
**Phase(s):** ANALYZE | **Dependencies:** `e2b-code-interpreter>=1.0`, `docker>=7.0`

```python
name = "python_repl"
description = """Execute Python in sandboxed environment. Dual backends:
- E2B (cloud): instant sandboxes, Jupyter-compatible
- Docker (local): maximum isolation, air-gapped, custom images
Pre-installed: numpy, pandas, scipy, statsmodels, matplotlib, seaborn, linearmodels,
arch, pingouin, scikit-learn, pymc, bambi, arviz, dowhy, lifelines, tikzplotlib, pandera.
Multi-cell execution (state persists within session)."""
parameters = {
    "type": "object",
    "properties": {
        "code": {"type": "string", "description": "Python code to execute"},
        "data_files": {"type": "array", "items": {"type": "string"}, "description": "Data files to mount"},
        "backend": {"type": "string", "enum": ["e2b", "docker", "auto"], "description": "Backend (default: auto)"},
        "timeout_seconds": {"type": "integer", "description": "Max execution time (default: 120)"},
        "session_id": {"type": "string", "description": "Session ID for persistent state"}
    },
    "required": ["code"]
}
```
**Returns:** `ToolResult` with stdout, stderr, artifacts (figures, CSVs), execution time.

---

### Tool 20: `conversational_analysis`
**Purpose:** Natural language data analysis using PandasAI.  
**Phase(s):** ANALYZE | **Dependencies:** `pandasai>=2.0`

```python
name = "conversational_analysis"
description = """Natural language -> pandas operations via PandasAI.
Quick exploratory analysis, hypothesis checking, data summarization.
Returns generated code + result for transparency. Use for EDA, not rigorous testing."""
parameters = {
    "type": "object",
    "properties": {
        "data_path": {"type": "string", "description": "Path to data file"},
        "question": {"type": "string", "description": "Natural language question"},
        "show_code": {"type": "boolean", "description": "Include generated code (default: true)"},
        "plot": {"type": "boolean", "description": "Generate visualization (default: true)"}
    },
    "required": ["data_path", "question"]
}
```
**Returns:** `ToolResult` with answer, generated code, optional visualization.

---

### Tool 21: `auto_visualize`
**Purpose:** Automatic visualization and goal exploration using Microsoft LIDA.  
**Phase(s):** ANALYZE | **Dependencies:** `lida>=0.0.10`

```python
name = "auto_visualize"
description = """LIDA pipeline: summarize data -> generate goals -> create visualizations -> explain.
Suggests analysis goals based on data structure. Each viz includes explanation."""
parameters = {
    "type": "object",
    "properties": {
        "data_path": {"type": "string", "description": "Path to data file"},
        "action": {"type": "string", "enum": ["summarize", "suggest_goals", "visualize", "explain", "full_pipeline"], "description": "Action (default: full_pipeline)"},
        "goal": {"type": "string", "description": "Specific goal (for 'visualize')"},
        "n_goals": {"type": "integer", "description": "Goals to suggest (default: 6)"},
        "n_visualizations": {"type": "integer", "description": "Variants per goal (default: 2)"},
        "library": {"type": "string", "enum": ["matplotlib", "seaborn", "altair"], "description": "Viz library (default: seaborn)"}
    },
    "required": ["data_path"]
}
```
**Returns:** `ToolResult` with data summary, goals, visualizations, explanations.

---

### Tool 22: `automated_eda`
**Purpose:** Comprehensive EDA using ydata-profiling.  
**Phase(s):** ANALYZE | **Dependencies:** `ydata-profiling>=4.6`

```python
name = "automated_eda"
description = """Full HTML EDA report: distributions, correlations, missing patterns, duplicates,
time series analysis, interaction effects, data quality alerts.
Supports: time_series mode, comparison mode, minimal mode (fast)."""
parameters = {
    "type": "object",
    "properties": {
        "data_path": {"type": "string", "description": "Path to data file"},
        "output_path": {"type": "string", "description": "HTML report path (default: analysis/eda_report.html)"},
        "title": {"type": "string", "description": "Report title"},
        "mode": {"type": "string", "enum": ["complete", "minimal", "time_series"], "description": "Mode (default: complete)"},
        "time_series_col": {"type": "string", "description": "Time column (for time_series mode)"},
        "compare_with": {"type": "string", "description": "Second dataset for comparison"}
    },
    "required": ["data_path"]
}
```
**Returns:** `ToolResult` with report path, key alerts, summary statistics.

---

### Tool 23: `descriptive_stats`
**Purpose:** Descriptive statistics with APA-formatted output.  
**Phase(s):** ANALYZE | **Dependencies:** `pandas>=2.0`, `scipy>=1.11`, `pingouin>=0.5.4`

```python
name = "descriptive_stats"
description = """Mean, median, SD, min, max, skewness, kurtosis, N, missing values.
Correlation matrix, group comparisons with effect sizes, normality tests. APA 7th format."""
parameters = {
    "type": "object",
    "properties": {
        "data_path": {"type": "string", "description": "Path to data file"},
        "variables": {"type": "array", "items": {"type": "string"}, "description": "Variables (all numeric if omitted)"},
        "groupby": {"type": "string", "description": "Grouping variable"},
        "include_correlation": {"type": "boolean", "description": "Correlation matrix (default: true if >1 var)"},
        "output_format": {"type": "string", "enum": ["json", "latex", "markdown"], "description": "Format (default: json)"}
    },
    "required": ["data_path"]
}
```
**Returns:** `ToolResult` with statistics table, correlation matrix, normality tests.

---

### Tool 24: `regression_analysis`
**Purpose:** Regression (OLS, logistic, panel FE/RE, Hausman, IV, GMM).  
**Phase(s):** ANALYZE | **Dependencies:** `statsmodels>=0.14`, `linearmodels>=6.0`

```python
name = "regression_analysis"
description = """Full regression with diagnostics. Methods: OLS, Logistic, Panel FE, Panel RE,
Hausman test, IV (2SLS), GMM. Returns: coefficients, SE, t-stats, p-values, R2, F-stat,
diagnostic tests (heteroskedasticity, autocorrelation, normality). APA-formatted tables."""
parameters = {
    "type": "object",
    "properties": {
        "data_path": {"type": "string", "description": "Path to data file"},
        "dependent_var": {"type": "string", "description": "Dependent variable"},
        "independent_vars": {"type": "array", "items": {"type": "string"}, "description": "Independent variables"},
        "control_vars": {"type": "array", "items": {"type": "string"}, "description": "Control variables"},
        "method": {"type": "string", "enum": ["ols", "logistic", "panel_fe", "panel_re", "panel_hausman", "iv_2sls", "gmm"], "description": "Method"},
        "entity_col": {"type": "string", "description": "Entity column (panel)"},
        "time_col": {"type": "string", "description": "Time column (panel)"},
        "instruments": {"type": "array", "items": {"type": "string"}, "description": "Instruments (IV/GMM)"},
        "robust_se": {"type": "boolean", "description": "Robust SE (default: true)"},
        "cluster_var": {"type": "string", "description": "Cluster SE variable"}
    },
    "required": ["data_path", "dependent_var", "independent_vars", "method"]
}
```
**Returns:** `ToolResult` with model summary, coefficients, diagnostics.

---

### Tool 25: `time_series_analysis`
**Purpose:** Time series modeling and forecasting.  
**Phase(s):** ANALYZE | **Dependencies:** `statsmodels>=0.14`, `arch>=7.0`

```python
name = "time_series_analysis"
description = """ARIMA/SARIMA, VAR, unit root (ADF, KPSS, PP), Granger causality,
cointegration (Johansen, Engle-Granger), impulse response, GARCH.
Auto-suggests optimal lag order via AIC/BIC."""
parameters = {
    "type": "object",
    "properties": {
        "data_path": {"type": "string", "description": "Path to data file"},
        "variable": {"type": "string", "description": "Primary time series variable"},
        "time_col": {"type": "string", "description": "Time/date column"},
        "method": {"type": "string", "enum": ["arima", "sarima", "var", "unit_root", "granger_causality", "cointegration", "impulse_response", "garch"], "description": "Method"},
        "order": {"type": "array", "items": {"type": "integer"}, "description": "Model order (p,d,q)"},
        "other_variables": {"type": "array", "items": {"type": "string"}, "description": "Additional variables"},
        "forecast_periods": {"type": "integer", "description": "Periods to forecast"},
        "auto_order": {"type": "boolean", "description": "Auto-select order (default: true)"}
    },
    "required": ["data_path", "variable", "time_col", "method"]
}
```
**Returns:** `ToolResult` with model summary, test statistics, diagnostics, forecast.

---

### Tool 26: `hypothesis_test`
**Purpose:** Statistical hypothesis tests with APA results.  
**Phase(s):** ANALYZE | **Dependencies:** `scipy>=1.11`, `pingouin>=0.5.4`

```python
name = "hypothesis_test"
description = """Tests: t-test (independent/paired), ANOVA (one-way/repeated), chi-square,
Mann-Whitney, Kruskal-Wallis, Shapiro-Wilk, Levene, Wilcoxon.
Returns: statistic, df, p, effect size (d/eta2/V), CI, power, Bayes Factor.
Auto-checks assumptions, suggests non-parametric alternatives."""
parameters = {
    "type": "object",
    "properties": {
        "data_path": {"type": "string", "description": "Path to data file"},
        "test": {"type": "string", "enum": ["t_test_independent", "t_test_paired", "anova_oneway", "anova_repeated", "chi_square_gof", "chi_square_independence", "mann_whitney", "kruskal_wallis", "shapiro_wilk", "levene", "wilcoxon_signed_rank"], "description": "Test"},
        "variable": {"type": "string", "description": "Dependent variable"},
        "grouping_var": {"type": "string", "description": "Grouping variable"},
        "alpha": {"type": "number", "description": "Significance level (default: 0.05)"},
        "alternative": {"type": "string", "enum": ["two-sided", "less", "greater"], "description": "Alternative"},
        "check_assumptions": {"type": "boolean", "description": "Check assumptions (default: true)"},
        "bayesian": {"type": "boolean", "description": "Compute Bayes Factor (default: false)"}
    },
    "required": ["data_path", "test", "variable"]
}
```
**Returns:** `ToolResult` with test results, assumption checks, APA string.

---

### Tool 27: `bayesian_analysis`
**Purpose:** Bayesian modeling with PyMC/Bambi formula interface.  
**Phase(s):** ANALYZE | **Dependencies:** `pymc>=5.0`, `bambi>=0.14`, `arviz>=0.18`

```python
name = "bayesian_analysis"
description = """R-style formula interface for Bayesian models via Bambi/PyMC.
Supports: linear, logistic, hierarchical/multilevel, mixed effects, GLMs.
Returns: posterior summaries (mean, SD, HDI), convergence (R-hat, ESS),
model comparison (WAIC, LOO-CV), posterior predictive checks."""
parameters = {
    "type": "object",
    "properties": {
        "data_path": {"type": "string", "description": "Path to data file"},
        "formula": {"type": "string", "description": "Bambi formula (e.g., 'gini ~ fiscal_decentral + (1|province)')"},
        "family": {"type": "string", "enum": ["gaussian", "bernoulli", "poisson", "negativebinomial", "t", "beta"], "description": "Distribution (default: gaussian)"},
        "priors": {"type": "object", "description": "Custom priors dict"},
        "draws": {"type": "integer", "description": "Posterior draws/chain (default: 2000)"},
        "chains": {"type": "integer", "description": "MCMC chains (default: 4)"},
        "compare_models": {"type": "array", "items": {"type": "string"}, "description": "Alternative formulas"},
        "output_plots": {"type": "array", "items": {"type": "string", "enum": ["trace", "posterior", "forest", "ppc", "pair"]}, "description": "Plots (default: trace, posterior)"}
    },
    "required": ["data_path", "formula"]
}
```
**Returns:** `ToolResult` with posterior summary, convergence, model comparison, plots.

---

### Tool 28: `causal_inference`
**Purpose:** DAG-based causal analysis using DoWhy (4-step).  
**Phase(s):** ANALYZE | **Dependencies:** `dowhy>=0.11`

```python
name = "causal_inference"
description = """DoWhy 4-step: Model (DAG) -> Identify (adjustment sets) -> Estimate (effect) -> Refute.
Methods: backdoor, IV, frontdoor, regression discontinuity, diff-in-diff, propensity score.
Returns: causal effect estimate, CI, refutation test results."""
parameters = {
    "type": "object",
    "properties": {
        "data_path": {"type": "string", "description": "Path to data file"},
        "treatment": {"type": "string", "description": "Treatment variable"},
        "outcome": {"type": "string", "description": "Outcome variable"},
        "dag": {"type": "string", "description": "Causal DAG in DOT format"},
        "method": {"type": "string", "enum": ["backdoor.linear_regression", "backdoor.propensity_score_matching", "iv.instrumental_variable", "frontdoor.two_stage_regression", "regression_discontinuity", "diff_in_diff"], "description": "Estimation method"},
        "instruments": {"type": "array", "items": {"type": "string"}, "description": "Instruments (for IV)"},
        "refutation_methods": {"type": "array", "items": {"type": "string", "enum": ["random_common_cause", "placebo_treatment", "data_subset", "bootstrap", "add_unobserved_common_cause"]}, "description": "Refutation tests (default: all)"}
    },
    "required": ["data_path", "treatment", "outcome", "dag"]
}
```
**Returns:** `ToolResult` with estimand, causal effect, CI, refutation results.

---

### Tool 29: `survival_analysis`
**Purpose:** Survival analysis (Kaplan-Meier, Cox PH, AFT).  
**Phase(s):** ANALYZE | **Dependencies:** `lifelines>=0.29`

```python
name = "survival_analysis"
description = """Kaplan-Meier, Cox Proportional Hazards, AFT (Weibull/Lognormal),
Nelson-Aalen, log-rank test, time-varying covariates.
Includes PH assumption test (Schoenfeld residuals)."""
parameters = {
    "type": "object",
    "properties": {
        "data_path": {"type": "string", "description": "Path to data file"},
        "duration_col": {"type": "string", "description": "Duration/time column"},
        "event_col": {"type": "string", "description": "Event indicator (1=event, 0=censored)"},
        "method": {"type": "string", "enum": ["kaplan_meier", "cox_ph", "aft_weibull", "aft_lognormal", "nelson_aalen", "log_rank_test"], "description": "Method"},
        "covariates": {"type": "array", "items": {"type": "string"}, "description": "Covariates"},
        "group_col": {"type": "string", "description": "Grouping variable"},
        "check_assumptions": {"type": "boolean", "description": "Test PH assumption (default: true)"}
    },
    "required": ["data_path", "duration_col", "event_col", "method"]
}
```
**Returns:** `ToolResult` with survival estimates, hazard ratios, test statistics, plots.

---

## Category 6: Paper Writing & Compilation Tools

### Tool 30: `write_section`
**Purpose:** Write sections using DSPy-optimized modules with RAG. **ENHANCED.**  
**Phase(s):** WRITE | **Dependencies:** `dspy>=2.0`, `paper-qa>=5.0`, `lightrag-hku>=1.5`

```python
name = "write_section"
description = """DSPy-optimized SectionWriter with RAG from LanceDB, KG context from LightRAG,
PaperQA2 for citation-grounded claims, auto citation insertion from verified bib.
Follows IMRaD structure and target journal formatting. Supports revision mode."""
parameters = {
    "type": "object",
    "properties": {
        "section": {"type": "string", "enum": ["abstract", "introduction", "literature_review", "methodology", "results", "discussion", "conclusion"], "description": "Section to write"},
        "instructions": {"type": "string", "description": "Specific instructions"},
        "max_words": {"type": "integer", "description": "Maximum word count"},
        "citation_density": {"type": "string", "enum": ["low", "medium", "high"], "description": "Citation density (default: medium)"},
        "revision": {"type": "boolean", "description": "Revision mode (default: false)"},
        "revision_feedback": {"type": "string", "description": "Feedback to address"},
        "use_rag": {"type": "boolean", "description": "Use RAG context (default: true)"}
    },
    "required": ["section"]
}
```
**Returns:** `ToolResult` with section text (LaTeX), citations used, word count, quality metrics.

---

### Tool 31: `compile_paper`
**Purpose:** Compile with Tectonic/Typst/pdflatex backends. **ENHANCED.**  
**Phase(s):** WRITE | **Dependencies:** `tectonic`, `typst`, or `texlive`

```python
name = "compile_paper"
description = """Three backends: Tectonic (zero-config, ~50MB), Typst (ms compilation),
pdflatex/latexmk (traditional). Auto-handles multiple passes. Fixes common errors on retry."""
parameters = {
    "type": "object",
    "properties": {
        "source_file": {"type": "string", "description": "Main source file (default: writing/main.tex)"},
        "backend": {"type": "string", "enum": ["tectonic", "typst", "latexmk", "pdflatex", "xelatex", "lualatex"], "description": "Backend (default: tectonic)"},
        "output_dir": {"type": "string", "description": "Output dir (default: writing/compiled/)"},
        "clean": {"type": "boolean", "description": "Clean aux files first"},
        "draft_mode": {"type": "boolean", "description": "Skip images for speed"}
    },
    "required": []
}
```
**Returns:** `ToolResult` with status, PDF path, warnings, errors, page count.

---

### Tool 32: `check_grammar`
**Purpose:** Grammar/style checking via LanguageTool.  
**Phase(s):** WRITE, REVIEW | **Dependencies:** `language-tool-python>=2.8`

```python
name = "check_grammar"
description = """LanguageTool: grammar, style, punctuation, spelling, consistency, academic conventions.
Supports LaTeX (strips commands). 30+ languages. Custom academic rules."""
parameters = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "description": "Text or path to file"},
        "language": {"type": "string", "description": "Language (default: en-US)"},
        "enabled_categories": {"type": "array", "items": {"type": "string", "enum": ["grammar", "style", "punctuation", "spelling", "redundancy", "typography", "academic"]}, "description": "Categories (default: all)"},
        "disabled_rules": {"type": "array", "items": {"type": "string"}, "description": "Rules to disable"},
        "strip_latex": {"type": "boolean", "description": "Strip LaTeX (default: true for .tex)"}
    },
    "required": ["text"]
}
```
**Returns:** `ToolResult` with issues (position, message, suggestion, category, severity).

---

### Tool 33: `check_style`
**Purpose:** Academic prose linting via proselint.  
**Phase(s):** WRITE, REVIEW | **Dependencies:** `proselint>=0.14`

```python
name = "check_style"
description = """Checks: weasel words, cliches, redundancy, jargon, hedging, sexism,
corporate speak, mixed metaphors. Complements check_grammar (style vs correctness)."""
parameters = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "description": "Text or path to file"},
        "checks": {"type": "array", "items": {"type": "string", "enum": ["weasel_words", "cliches", "redundancy", "jargon", "hedging", "sexism", "corporate_speak", "mixed_metaphors", "all"]}, "description": "Checks (default: all)"}
    },
    "required": ["text"]
}
```
**Returns:** `ToolResult` with style issues (line, column, message, severity).

---

### Tool 34: `check_readability`
**Purpose:** Readability scoring via textstat.  
**Phase(s):** WRITE, REVIEW | **Dependencies:** `textstat>=0.7`

```python
name = "check_readability"
description = """Flesch Reading Ease, Flesch-Kincaid Grade, Gunning Fog, SMOG, Coleman-Liau, ARI, Dale-Chall.
Also: avg sentence length, syllable count, difficult word %, reading time.
Academic target: FK Grade 12-16, Gunning Fog 12-18."""
parameters = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "description": "Text or path to file"},
        "target_audience": {"type": "string", "enum": ["general_public", "undergraduate", "graduate", "expert"], "description": "Audience (default: graduate)"},
        "per_section": {"type": "boolean", "description": "Per-section breakdown (default: false)"}
    },
    "required": ["text"]
}
```
**Returns:** `ToolResult` with readability scores, assessment, recommendations.

---

### Tool 35: `generate_table`
**Purpose:** Publication-ready academic tables.  
**Phase(s):** WRITE | **Dependencies:** `pandas>=2.0`, `pylatex>=1.4.2`

```python
name = "generate_table"
description = """Descriptive stats, regression results, correlation matrix, comparison, custom.
Output: LaTeX (booktabs) or DOCX. APA formatting (no vertical lines, proper headers)."""
parameters = {
    "type": "object",
    "properties": {
        "table_type": {"type": "string", "enum": ["descriptive", "regression", "correlation", "comparison", "custom"], "description": "Table type"},
        "data_source": {"type": "string", "description": "Path to data/results"},
        "caption": {"type": "string", "description": "Table caption"},
        "label": {"type": "string", "description": "LaTeX label"},
        "note": {"type": "string", "description": "Table note"},
        "output_format": {"type": "string", "enum": ["latex", "docx", "markdown"], "description": "Format (default: latex)"},
        "output_path": {"type": "string", "description": "Output path"}
    },
    "required": ["table_type", "data_source", "caption"]
}
```
**Returns:** `ToolResult` with formatted table and output path.

---

### Tool 36: `generate_diagram`
**Purpose:** Text-to-diagram using Mermaid.  
**Phase(s):** WRITE | **Dependencies:** `mermaid-cli` (npm)

```python
name = "generate_diagram"
description = """Mermaid: flowcharts, sequence, class, state, ER, Gantt, pie, mindmap.
Output: SVG/PNG/PDF. Use for: research frameworks, methodology flowcharts, causal DAGs."""
parameters = {
    "type": "object",
    "properties": {
        "diagram_code": {"type": "string", "description": "Mermaid diagram code"},
        "diagram_type": {"type": "string", "enum": ["flowchart", "sequence", "class", "state", "er", "gantt", "pie", "mindmap"], "description": "Type (auto-detected if omitted)"},
        "output_format": {"type": "string", "enum": ["svg", "png", "pdf"], "description": "Format (default: svg)"},
        "output_path": {"type": "string", "description": "Output file path"},
        "theme": {"type": "string", "enum": ["default", "neutral", "dark", "forest"], "description": "Theme (default: neutral)"},
        "width": {"type": "integer", "description": "Width in px (PNG, default: 800)"}
    },
    "required": ["diagram_code", "output_path"]
}
```
**Returns:** `ToolResult` with diagram file path.

---

### Tool 37: `convert_figure_tikz`
**Purpose:** matplotlib -> TikZ/PGFplots for native LaTeX figures.  
**Phase(s):** WRITE | **Dependencies:** `tikzplotlib>=0.10`, `matplotlib>=3.8`

```python
name = "convert_figure_tikz"
description = """Convert matplotlib to LaTeX-native PGFplots. Benefits: perfect scaling,
matching fonts, editable in source, true vector output.
Supports: line, scatter, bar, histogram, error bars."""
parameters = {
    "type": "object",
    "properties": {
        "figure_path": {"type": "string", "description": "Path to figure (.py script or .pkl)"},
        "output_path": {"type": "string", "description": "Output .tex path"},
        "standalone": {"type": "boolean", "description": "Standalone compilable .tex (default: false)"},
        "extra_axis_parameters": {"type": "array", "items": {"type": "string"}, "description": "PGFplots axis params"}
    },
    "required": ["figure_path", "output_path"]
}
```
**Returns:** `ToolResult` with TikZ code and output path.

---

## Category 7: Visualization Tools

### Tool 38: `create_visualization`
**Purpose:** Publication-quality figures with journal presets.  
**Phase(s):** ANALYZE, WRITE | **Dependencies:** `matplotlib>=3.8`, `seaborn>=0.13`

```python
name = "create_visualization"
description = """Journal presets: Nature, Science, IEEE, PLOS, Elsevier, APA.
Colorblind-friendly Okabe-Ito palette. Output: PDF/TIFF/PNG/SVG (300+ DPI).
Types: line, bar, scatter, heatmap, violin, box, histogram, regression, time_series,
forest_plot, correlation_matrix, pair_plot."""
parameters = {
    "type": "object",
    "properties": {
        "data_path": {"type": "string", "description": "Path to data"},
        "plot_type": {"type": "string", "enum": ["line", "bar", "scatter", "heatmap", "violin", "box", "histogram", "regression", "time_series", "forest_plot", "correlation_matrix", "pair_plot"], "description": "Plot type"},
        "x_var": {"type": "string", "description": "X-axis variable"},
        "y_var": {"type": "string", "description": "Y-axis variable"},
        "hue_var": {"type": "string", "description": "Color grouping"},
        "title": {"type": "string", "description": "Figure title"},
        "xlabel": {"type": "string", "description": "X-axis label"},
        "ylabel": {"type": "string", "description": "Y-axis label"},
        "journal_preset": {"type": "string", "enum": ["nature", "science", "ieee", "plos", "elsevier", "apa"], "description": "Preset (default: nature)"},
        "output_format": {"type": "string", "enum": ["pdf", "tiff", "png", "svg"], "description": "Format (default: pdf)"},
        "output_path": {"type": "string", "description": "Output path"},
        "figsize": {"type": "string", "enum": ["single_column", "double_column", "full_page"], "description": "Size (default: single_column)"}
    },
    "required": ["data_path", "plot_type", "output_path"]
}
```
**Returns:** `ToolResult` with figure file path and metadata.

---

### Tool 39–40: *(Reserved for future specialized visualization tools)*

> Slots 39-40 reserved. Use `create_visualization` (38), `auto_visualize` (21), `generate_diagram` (36), or `convert_figure_tikz` (37).

---

## Category 8: Data Validation & Quality Tools

### Tool 41: `validate_data`
**Purpose:** Data quality gates (Great Expectations + Pandera).  
**Phase(s):** ANALYZE | **Dependencies:** `great-expectations>=0.18`, `pandera>=0.20`

```python
name = "validate_data"
description = """Great Expectations: declarative data quality testing.
Pandera: runtime DataFrame schema validation.
Checks: ranges, uniqueness, nulls, types, referential integrity, statistical properties.
BLOCKS analysis on critical failures. Generates HTML validation report."""
parameters = {
    "type": "object",
    "properties": {
        "data_path": {"type": "string", "description": "Path to data file"},
        "schema": {"type": "object", "description": "Pandera schema definition"},
        "expectations": {"type": "array", "items": {"type": "object"}, "description": "GE expectations list"},
        "output_report": {"type": "string", "description": "HTML report path"},
        "fail_on_error": {"type": "boolean", "description": "Block on failure (default: true)"}
    },
    "required": ["data_path"]
}
```
**Returns:** `ToolResult` with validation results (pass/fail per check), report path.

---

### Tool 42: `check_statistical_validity`
**Purpose:** Validate statistical methodology and reporting.  
**Phase(s):** REVIEW | **Dependencies:** `scipy>=1.11`, `statsmodels>=0.14`

```python
name = "check_statistical_validity"
description = """Validates: assumptions tested, sample size adequate, effect sizes reported,
CIs included, multiple comparisons corrected, df correct, causality language appropriate.
Compares reported statistics against analysis/results/*.json."""
parameters = {
    "type": "object",
    "properties": {
        "results_path": {"type": "string", "description": "Path to analysis results (JSON)"},
        "methodology_section": {"type": "string", "description": "Path to methodology .tex"},
        "results_section": {"type": "string", "description": "Path to results .tex"}
    },
    "required": ["results_path"]
}
```
**Returns:** `ToolResult` with validity report (pass/fail per criterion, issues, recommendations).

---

### Tool 43: `simulate_peer_review`
**Purpose:** Adversarial peer review simulation.  
**Phase(s):** REVIEW | **Dependencies:** LLM (via LiteLLM)

```python
name = "simulate_peer_review"
description = """Adversarial reviewer prompts evaluating: novelty, methodology rigor,
statistical reporting, writing quality, citation adequacy, logical flow, limitations.
Returns structured review: summary, strengths, weaknesses, major/minor issues,
recommendation (accept/revise/reject). Multiple reviewer personas."""
parameters = {
    "type": "object",
    "properties": {
        "paper_path": {"type": "string", "description": "Path to PDF or main.tex"},
        "review_focus": {"type": "array", "items": {"type": "string", "enum": ["methodology", "statistics", "writing", "citations", "novelty", "logic", "completeness"]}, "description": "Focus areas (default: all)"},
        "reviewer_expertise": {"type": "string", "description": "Domain expertise (e.g., 'econometrics')"},
        "num_reviewers": {"type": "integer", "description": "Number of reviewers (default: 3)"}
    },
    "required": []
}
```
**Returns:** `ToolResult` with structured reviews, synthesized revision plan.

---

## Category 9: Quality Assurance & Review Tools

### Tool 44: `detect_plagiarism`
**Purpose:** Similarity detection (sentence-transformers + MinHash).  
**Phase(s):** REVIEW | **Dependencies:** `sentence-transformers>=3.0`, `datasketch`

```python
name = "detect_plagiarism"
description = """Dual approach: semantic similarity (embedding cosine) + MinHash LSH (n-gram overlap).
Compares paragraphs against source corpus in LanceDB.
Thresholds: >0.85 = verbatim copying, >0.70 = close paraphrase, <0.70 = original.
Excludes: direct quotes (cited), standard method descriptions."""
parameters = {
    "type": "object",
    "properties": {
        "paper_path": {"type": "string", "description": "Path to paper (.tex or .md)"},
        "source_corpus": {"type": "string", "description": "Source corpus dir (default: literature/processed/)"},
        "similarity_threshold": {"type": "number", "description": "Flagging threshold (default: 0.70)"},
        "exclude_quotes": {"type": "boolean", "description": "Exclude cited quotes (default: true)"},
        "method": {"type": "string", "enum": ["semantic", "minhash", "both"], "description": "Detection method (default: both)"}
    },
    "required": ["paper_path"]
}
```
**Returns:** `ToolResult` with similarity report (flagged passages, scores, sources).

---

### Tool 45: `audit_reproducibility`
**Purpose:** Re-run analysis scripts and verify outputs match.  
**Phase(s):** REVIEW | **Dependencies:** `e2b-code-interpreter>=1.0` or `docker>=7.0`

```python
name = "audit_reproducibility"
description = """Re-run all analysis scripts in clean sandbox, verify outputs match.
Checks: results identical (within float tolerance), data files have SHA256 hashes,
package versions pinned, random seeds set, all figures reproducible, no manual steps."""
parameters = {
    "type": "object",
    "properties": {
        "scripts_dir": {"type": "string", "description": "Analysis scripts directory (default: analysis/scripts/)"},
        "results_dir": {"type": "string", "description": "Expected results directory (default: analysis/results/)"},
        "tolerance": {"type": "number", "description": "Float comparison tolerance (default: 1e-6)"},
        "check_hashes": {"type": "boolean", "description": "Verify data file checksums (default: true)"},
        "check_versions": {"type": "boolean", "description": "Verify package versions pinned (default: true)"}
    },
    "required": []
}
```
**Returns:** `ToolResult` with reproducibility report (PASS/FAIL, discrepancies, missing seeds).

---

### Tool 46–47: *(Reserved for future QA tools)*

> Slots 46-47 reserved for: automated journal submission formatting checker, reference completeness validator.

---

## Category 10: Legacy Enhanced Tools (from v1)

### Tool 48: `create_visualization` (v1 enhanced)
> See Tool 38. This is the enhanced version of the original v1 `create_visualization` with journal presets.

### Tool 49: `generate_table` (v1 enhanced)
> See Tool 35. Enhanced with more table types and format options.

### Tool 50: `latex_compile` (v1 → `compile_paper`)
> See Tool 31. Renamed and enhanced with multi-backend support.

### Tool 51: `literature_search` (v1 enhanced)
> See Tool 16. Enhanced from 3 sources to 22 sources via paper-search-mcp.

### Tool 52: `citation_manager` (v1 enhanced)
> See Tool 17. Enhanced with Zotero integration, semantic search, Scite intelligence.

---

## Tool Count Summary

| Phase | New Tools (v2) | Enhanced (from v1) | Total Visible |
|-------|:--------------:|:------------------:|:-------------:|
| PLAN | 4 (litellm, dspy, paper_qa, auto_viz) | 3 (init, status, switch) | ~10 |
| COLLECT | 10 (doc processing, RAG, KG, entities) | 3 (lit_search, citation, verify) | ~15 |
| ANALYZE | 8 (pandas_ai, lida, eda, bayesian, causal, survival, validate) | 5 (repl, stats, regression, ts, hypothesis) | ~14 |
| WRITE | 5 (grammar, style, readability, diagram, tikz) | 3 (write_section, compile, table) | ~11 |
| REVIEW | 3 (plagiarism, reproducibility, validity) | 1 (peer_review) | ~8 |

**Total unique tools: 52** (35 new + 17 enhanced from v1)

---

## Dependencies Summary

| Category | Key Packages | License |
|----------|-------------|---------|
| Framework | `dspy>=2.0`, `litellm>=1.40`, `paper-qa>=5.0` | MIT, MIT, Apache |
| Document | `markitdown[all]>=0.1.5`, `mineru>=3.0`, `chonkie>=0.4` | MIT, Apache, MIT |
| RAG | `lightrag-hku>=1.5`, `lancedb>=0.9`, `sentence-transformers>=3.0` | MIT, Apache, Apache |
| Analysis | `statsmodels>=0.14`, `pymc>=5.0`, `dowhy>=0.11`, `lifelines>=0.29` | BSD, Apache, MIT, MIT |
| Writing | `language-tool-python>=2.8`, `proselint>=0.14`, `textstat>=0.7` | LGPL, BSD, MIT |
| Execution | `e2b-code-interpreter>=1.0`, `docker>=7.0` | MIT, Apache |
| System | Tectonic, Typst, GROBID (Docker), LanguageTool (Java) | — |

See `DEPENDENCIES.md` for full compatibility matrix and installation instructions.

---

*This specification covers all 52 tools discovered through deep research of 176+ open-source tools, MCP servers, and academic frameworks. Implementation priority follows the phased approach in ROADMAP.md.*
