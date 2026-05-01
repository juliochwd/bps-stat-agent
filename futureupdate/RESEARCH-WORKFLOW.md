# BPS Academic Research Agent — End-to-End Research Workflow

**Version:** 2.0  
**Created:** 2025-07-14  
**Updated:** 2025-07-15 — Full tool integration across all phases

---

## Overview

This document describes the complete end-to-end workflow for producing a production-ready academic journal paper using the BPS Academic Research Agent. Version 2.0 integrates all discovered tools into a unified pipeline spanning literature discovery, data analysis, paper generation, and quality assurance.

---

## The 5-Phase Research Pipeline

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    PLAN      │ →  │   COLLECT    │ →  │   ANALYZE    │ →  │    WRITE     │ →  │   REVIEW     │
│              │    │              │    │              │    │              │    │              │
│ • PaperQA2   │    │ • paper-     │    │ • jupyter-   │    │ • DSPy       │    │ • CrossRef   │
│ • paper-     │    │   search-mcp │    │   mcp / E2B  │    │   modules    │    │   verify     │
│   search-mcp │    │ • MinerU     │    │ • PandasAI   │    │ • overleaf-  │    │ • proselint  │
│ • DSPy RQ    │    │ • GROBID     │    │ • LIDA       │    │   mcp        │    │ • plagiarism │
│   formulator │    │ • SPECTER2   │    │ • ydata-prof │    │ • Tectonic   │    │   detection  │
│              │    │ • Chonkie    │    │ • statsmodels │    │ • Typst      │    │ • peer sim   │
│              │    │ • scispaCy   │    │ • PyMC+Bambi │    │ • tikzplotlib│    │ • repro      │
│              │    │ • LightRAG   │    │ • DoWhy      │    │ • Pandoc     │    │   audit      │
│              │    │ • zotero-mcp │    │ • rmcp (52)  │    │ • PaperQA2   │    │              │
│              │    │ • Unpaywall  │    │ • GE+Pandera │    │ • Language-  │    │              │
│              │    │ • LanceDB    │    │              │    │   Tool       │    │              │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       │                   │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼                   ▼
  outline.yaml        data/ + bib +       results/ +          sections/ +        quality_report
  + research_qs       knowledge_graph     figures/ +          main.tex +         + revisions +
  + methodology       + embeddings        validated_data      compiled PDF       final PDF
```

### Data Flow Between Phases

```
PLAN ──────────────────────────────────────────────────────────────────────────────────────►
  │ research_questions.yaml                                                                 │
  │ methodology_spec.yaml                                                                   │
  │ initial_refs.bib (10-15 papers)                                                         │
  ▼                                                                                         │
COLLECT ───────────────────────────────────────────────────────────────────────────────────►│
  │ data/processed/panel_data.parquet                                                       │
  │ literature/references.bib (40-80 papers)                                                │
  │ knowledge_graph/ (LightRAG entities + relations)                                        │
  │ embeddings/ (LanceDB: SPECTER2 paper vectors + Chonkie chunks)                          │
  │ literature/summaries/*.yaml (per-paper structured summaries)                            │
  ▼                                                                                         │
ANALYZE ──────────────────────────────────────────────────────────────────────────────────►│
  │ analysis/results/*.json (structured statistical outputs)                                │
  │ analysis/figures/*.pdf (publication-quality, 300 DPI)                                   │
  │ analysis/tables/*.tex (booktabs format)                                                 │
  │ analysis/validation_report.yaml (Great Expectations + Pandera)                          │
  ▼                                                                                         │
WRITE ────────────────────────────────────────────────────────────────────────────────────►│
  │ writing/sections/*.tex (individual sections)                                            │
  │ writing/main.tex (master document)                                                      │
  │ writing/compiled/paper.pdf                                                              │
  ▼                                                                                         │
REVIEW ───────────────────────────────────────────────────────────────────────────────────►│
  │ review/quality_report.yaml                                                              │
  │ review/peer_review_sim.yaml                                                             │
  │ writing/compiled/paper_final.pdf                                                        │
  └─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: PLAN

### Objective
Define research scope, questions, methodology, and paper structure using AI-assisted literature scanning and structured question formulation.

### Tools Used
| Tool | Purpose |
|------|---------|
| **PaperQA2** | Quick literature scan with citation-grounded answers |
| **paper-search-mcp** (22 sources) | Broad discovery across arXiv, PubMed, Semantic Scholar, etc. |
| **DSPy** (ResearchQuestionFormulator module) | Structured research question generation and refinement |

### Steps

```
1.1 User provides research topic/question
    └── "Pengaruh desentralisasi fiskal terhadap ketimpangan di Indonesia"

1.2 Agent initializes project
    └── project_init(title=..., template="elsevier")
    └── Creates workspace structure:
        project/
        ├── data/raw/
        ├── data/processed/
        ├── literature/
        ├── analysis/scripts/
        ├── analysis/results/
        ├── analysis/figures/
        ├── writing/sections/
        ├── writing/compiled/
        ├── review/
        ├── embeddings/
        └── knowledge_graph/

1.3 Quick literature scan via PaperQA2
    ├── paperqa2_ask(
    │       question="What are the main findings on fiscal decentralization
    │                 and inequality in developing countries?",
    │       max_sources=15
    │   )
    ├── Returns: citation-grounded summary + source list
    └── Identifies: existing work, gaps, methodologies used

1.4 Broad discovery via paper-search-mcp
    ├── paper_search(
    │       query="fiscal decentralization inequality panel data",
    │       sources=["semantic_scholar", "openalex", "crossref"],
    │       max_results=30
    │   )
    ├── Deduplicate results across sources
    └── Rank by: citation count × recency × relevance

1.5 Research question formulation via DSPy
    ├── DSPy ResearchQuestionFormulator module:
    │   ├── Input: topic + literature_summary + identified_gaps
    │   ├── Signature: "topic, literature_gaps -> research_questions, hypotheses"
    │   ├── Optimized with BootstrapFewShot on exemplar RQs
    │   └── Output: 2-4 structured research questions with testable hypotheses
    ├── RQ1: "How does fiscal decentralization affect Gini coefficient?"
    ├── RQ2: "Does the effect vary by region (Java vs non-Java)?"
    └── H1: "Higher fiscal decentralization → lower inequality (β < 0)"

1.6 Choose methodology
    └── [HUMAN APPROVAL GATE]
    └── Panel data regression (Fixed Effects)
    └── Hausman test for FE vs RE selection
    └── Robustness: GMM, alternative measures

1.7 Generate paper outline
    ├── DSPy OutlineGenerator module:
    │   ├── Input: research_questions + methodology + target_journal
    │   ├── Signature: "rqs, methodology, journal_spec -> outline"
    │   └── Output: IMRaD structure with section specs
    ├── Word count targets per section
    └── Key references to cite per section

1.8 Checkpoint: plan_complete
    └── [HUMAN REVIEW: research questions + methodology + outline]
```

### Output Artifacts
- `project.yaml` — Master state
- `writing/outline.yaml` — Paper structure with section specs
- `research_questions.yaml` — Structured RQs + hypotheses
- `methodology_spec.yaml` — Statistical approach details
- `literature/references.bib` — Initial references (10-15)
- `literature/gap_analysis.yaml` — Identified research gaps

---

## Phase 2: COLLECT

### Objective
Gather all data and literature, process papers into searchable embeddings, build knowledge graph, and manage citations.

### Tools Used
| Tool | Purpose |
|------|---------|
| **paper-search-mcp** (22 sources) | Multi-source search: arXiv, PubMed, Semantic Scholar, CrossRef, OpenAlex, CORE, DOAJ, etc. |
| **Unpaywall / CORE** | Full-text PDF access (open access routes) |
| **MinerU / MarkItDown** | PDF → structured markdown extraction |
| **GROBID** | Reference extraction from PDFs (structured XML) |
| **SPECTER2** | Paper embeddings (title+abstract → 768-dim vectors) |
| **LanceDB** | Vector storage for paper embeddings |
| **Chonkie SemanticChunker** | Intelligent paper section chunking |
| **scispaCy** | Named entity extraction (methods, datasets, metrics) |
| **LightRAG** | Knowledge graph construction from extracted entities |
| **zotero-mcp** | Citation management and organization |

### Steps

```
2.1 Data Collection (BPS)
    ├── bps_search("gini ratio provinsi", domain="0000")
    ├── bps_get_data(var=..., domain="0000", years=[2015-2022])
    ├── bps_search("dana alokasi umum", domain="0000")
    ├── Collect control variables (PDRB, unemployment, education, population)
    └── Save to data/raw/ with metadata.yaml (source, date, API params)

2.2 Data Cleaning & Validation
    ├── Merge datasets by province + year
    ├── Handle missing values (document decisions in data/cleaning_log.yaml)
    ├── Create panel structure (entity × time)
    ├── Validate with Pandera schema:
    │   schema = pa.DataFrameSchema({
    │       "province_id": pa.Column(int, checks=pa.Check.in_range(11, 94)),
    │       "year": pa.Column(int, checks=pa.Check.in_range(2015, 2022)),
    │       "gini": pa.Column(float, checks=pa.Check.in_range(0, 1)),
    │   })
    └── Save to data/processed/panel_data.parquet

2.3 Literature Collection (Deep) via paper-search-mcp
    ├── paper_search(
    │       query="fiscal decentralization inequality developing countries",
    │       sources=["semantic_scholar", "openalex", "crossref", "arxiv",
    │                "pubmed", "core", "doaj", "base"],
    │       max_results=80,
    │       filters={year_min: 2014, min_citations: 5}
    │   )
    ├── paper_search(query="panel data Indonesia provinces fixed effects", ...)
    ├── paper_search(query="Gini coefficient determinants subnational", ...)
    ├── Deduplicate across sources (DOI matching + title similarity)
    ├── Filter: relevant, recent (last 10 years), high-citation
    └── Result: 50-80 unique papers

2.4 Full-Text Access
    ├── For each paper without full text:
    │   ├── unpaywall_lookup(doi=paper.doi)  → OA PDF URL
    │   ├── core_search(title=paper.title)   → Repository PDF
    │   └── Fallback: abstract-only (mark as "no_fulltext")
    ├── Download PDFs to literature/pdfs/
    └── Track access status in literature/access_log.yaml

2.5 PDF Processing Pipeline
    ├── For each PDF:
    │   ├── MinerU/MarkItDown: PDF → structured markdown
    │   │   └── mineru_extract(pdf_path) → {title, abstract, sections[], refs[]}
    │   ├── GROBID: Extract structured references
    │   │   └── grobid_process(pdf_path) → TEI XML with parsed citations
    │   ├── Chonkie SemanticChunker: Split into semantic sections
    │   │   └── chunker.chunk(markdown_text, max_tokens=512)
    │   │   └── Result: chunks[] with section_type labels
    │   └── scispaCy: Entity extraction
    │       └── nlp(text) → entities{methods, datasets, metrics, chemicals}
    └── Save structured output to literature/processed/{paper_id}.yaml

2.6 Embedding & Indexing (RAG Pipeline)
    ├── SPECTER2: Generate paper-level embeddings
    │   ├── For each paper: embed(title + " [SEP] " + abstract) → 768-dim vector
    │   └── Store in LanceDB table "papers":
    │       lancedb.connect("embeddings/").create_table("papers", [
    │           {"paper_id": ..., "vector": [...], "title": ..., "year": ...}
    │       ])
    ├── Chunk-level embeddings for retrieval:
    │   ├── For each chunk: embed(chunk_text) → 768-dim vector
    │   └── Store in LanceDB table "chunks":
    │       {"chunk_id": ..., "paper_id": ..., "vector": [...],
    │        "section_type": ..., "text": ...}
    └── Build retrieval index (IVF-PQ for fast ANN search)

2.7 Knowledge Graph Construction (LightRAG)
    ├── Extract entities from all processed papers:
    │   ├── Methods: "fixed effects", "GMM", "Hausman test"
    │   ├── Variables: "Gini coefficient", "fiscal decentralization ratio"
    │   ├── Findings: "negative relationship (β=-0.23, p<0.01)"
    │   └── Datasets: "BPS SUSENAS", "World Bank WDI"
    ├── LightRAG.insert(documents=[processed_papers])
    ├── Build entity-relation graph:
    │   ├── (Paper_A) --[uses_method]--> (Fixed Effects)
    │   ├── (Paper_A) --[finds]--> (negative_relationship)
    │   ├── (Paper_A) --[contradicts]--> (Paper_B)
    │   └── (Method_X) --[assumes]--> (no_serial_correlation)
    └── Save to knowledge_graph/

2.8 Citation Management (zotero-mcp)
    ├── zotero_add_items(items=[...])  — Batch add all papers
    ├── zotero_create_collection("fiscal_decentralization_inequality")
    ├── Organize by theme:
    │   ├── Collection: "theory" (12 papers)
    │   ├── Collection: "methodology" (8 papers)
    │   ├── Collection: "indonesia_context" (15 papers)
    │   └── Collection: "findings_comparison" (20 papers)
    ├── Export to BibTeX: zotero_export(format="bibtex")
    └── Sync references.bib

2.9 Citation Verification
    ├── For each reference in .bib:
    │   ├── crossref_verify(doi=ref.doi) → metadata match check
    │   ├── semantic_scholar_verify(paper_id=...) → citation count, abstract
    │   └── Flag: unverified, metadata_mismatch, retracted
    ├── Remove any that fail verification
    └── Result: verified_references.bib (all entries confirmed)

2.10 Checkpoint: collect_complete
    └── [HUMAN REVIEW: data quality + literature coverage + knowledge graph]
```

### Output Artifacts
- `data/raw/` — Original BPS data (immutable, with metadata)
- `data/processed/panel_data.parquet` — Cleaned panel dataset
- `literature/references.bib` — Complete verified bibliography (50-80 papers)
- `literature/processed/` — Per-paper structured extractions
- `literature/summaries/` — Per-paper YAML summaries
- `embeddings/` — LanceDB with paper + chunk vectors
- `knowledge_graph/` — LightRAG entity-relation graph
- `data/cleaning_log.yaml` — All data transformation decisions

### RAG Pipeline Detail

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Paper Processing → Embedding → Retrieval              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PDF ──► MinerU ──► Markdown ──► Chonkie ──► Chunks (512 tokens)       │
│   │                    │              │            │                     │
│   │                    │              │            ▼                     │
│   │                    │              │      SPECTER2 embed              │
│   │                    │              │            │                     │
│   │                    │              │            ▼                     │
│   │                    │              │      LanceDB "chunks"            │
│   │                    │              │                                  │
│   │                    ▼              │                                  │
│   │              scispaCy NER         │                                  │
│   │                    │              │                                  │
│   │                    ▼              │                                  │
│   │              LightRAG KG          │                                  │
│   │                                   │                                  │
│   ▼                                   │                                  │
│  GROBID ──► Parsed References         │                                  │
│                    │                   │                                  │
│                    ▼                   │                                  │
│              zotero-mcp (citation mgmt)│                                  │
│                                       │                                  │
│  At query time:                       │                                  │
│  ┌────────────────────────────────────┴──────────────┐                  │
│  │ Query ──► SPECTER2 embed ──► LanceDB ANN search   │                  │
│  │                                      │            │                  │
│  │                                      ▼            │                  │
│  │                              Top-K chunks         │                  │
│  │                                      │            │                  │
│  │                                      ▼            │                  │
│  │                              + KG context         │                  │
│  │                              (LightRAG query)     │                  │
│  │                                      │            │                  │
│  │                                      ▼            │                  │
│  │                              LLM generation       │                  │
│  │                              (with citations)     │                  │
│  └───────────────────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 3: ANALYZE

### Objective
Perform statistical analysis in sandboxed environments, generate results and publication-quality visualizations, with full data validation.

### Tools Used
| Tool | Purpose |
|------|---------|
| **jupyter-mcp / E2B** | Sandboxed code execution (isolated environments) |
| **PandasAI** | Conversational data exploration and quick analysis |
| **LIDA** | Automated visualization + goal exploration |
| **ydata-profiling** | Automated EDA report generation |
| **statsmodels / scipy / linearmodels** | Frequentist statistical analysis |
| **PyMC + Bambi** | Bayesian analysis (posterior estimation, model comparison) |
| **DoWhy** | Causal inference (DAG specification, identification, estimation) |
| **Great Expectations + Pandera** | Data validation at every step |
| **rmcp** (52 R tools) | Specialized statistics (plm, lme4, sandwich, etc.) |

### Steps

```
3.1 Data Validation (Pre-Analysis)
    ├── Great Expectations suite:
    │   ge_suite = context.add_expectation_suite("panel_data_validation")
    │   ge_suite.add_expectation(expect_column_values_to_be_between("gini", 0, 1))
    │   ge_suite.add_expectation(expect_compound_columns_to_be_unique(["province_id", "year"]))
    │   validation_result = context.run_validation(batch, ge_suite)
    ├── Pandera runtime schema enforcement
    ├── Result: validation_report.yaml (PASS/FAIL with details)
    └── BLOCK if critical validation failures

3.2 Automated EDA (ydata-profiling)
    ├── ydata_profiling.ProfileReport(df, title="Panel Data EDA",
    │       explorative=True, tsmode=True).to_file("analysis/eda_report.html")
    ├── Identifies: distributions, correlations, missing patterns, outliers
    └── Informs: transformation decisions, variable selection

3.3 Conversational Exploration (PandasAI)
    ├── pandasai.SmartDataframe(df).chat(
    │       "What is the correlation between fiscal_decentralization and gini by region group?")
    ├── Quick hypothesis testing before formal analysis
    └── Generates exploratory plots for researcher review

3.4 Goal Exploration (LIDA)
    ├── lida.Manager().summarize(df) → data summary
    ├── lida.goals(summary, n=6) → suggested analysis goals
    ├── lida.visualize(summary, goal=goal_1) → auto-generated viz
    ├── [HUMAN REVIEW: which goals to pursue formally]
    └── Informs: which relationships to test

3.5 Descriptive Statistics
    ├── Execute in jupyter-mcp sandbox:
    │   descriptive_stats(data_path="data/processed/panel_data.parquet")
    ├── Generate: Table 1 (Descriptive Statistics)
    │   ├── Mean, SD, Min, Max, N for all variables
    │   ├── By-group summaries (Java vs non-Java)
    │   └── Correlation matrix
    └── Save: analysis/results/descriptive_stats.json

3.6 Assumption Checks
    ├── Normality: scipy.stats.shapiro(residuals)
    ├── Multicollinearity: VIF via statsmodels
    ├── Heteroscedasticity: Breusch-Pagan test
    ├── Serial correlation: Wooldridge test (via rmcp)
    │   └── rmcp_execute(r_code="library(plm); pwartest(model)")
    ├── Stationarity: panel unit root tests (LLC, IPS, Fisher)
    │   └── rmcp_execute(r_code="library(plm); purtest(y ~ 1, data=pdata)")
    └── Document all assumption results in analysis/assumptions.yaml

3.7 Main Analysis (Frequentist)
    ├── Panel regression via linearmodels:
    │   from linearmodels.panel import PanelOLS, RandomEffects
    │   fe_model = PanelOLS(y, X, entity_effects=True).fit(
    │       cov_type='clustered', cluster_entity=True)
    ├── Hausman test: compare_fe_re(fe_model, re_model)
    ├── [HUMAN APPROVAL: FE vs RE based on Hausman test result]
    ├── Selected model with robust standard errors
    └── Save: analysis/results/regression_main.json

3.8 Bayesian Analysis (PyMC + Bambi)
    ├── Bambi model specification:
    │   model = bmb.Model("gini ~ fiscal_decentral + gdp_pc + unemployment + (1|province)",
    │       data=df, family="gaussian")
    │   idata = model.fit(draws=2000, chains=4, cores=4)
    ├── Posterior summaries: az.summary(idata)
    ├── Model comparison: az.compare({"model1": idata1, "model2": idata2})
    ├── Posterior predictive checks: az.plot_ppc(idata)
    └── Save: analysis/results/bayesian_results.json

3.9 Causal Inference (DoWhy)
    ├── DAG specification:
    │   model = dowhy.CausalModel(data=df, treatment="fiscal_decentralization",
    │       outcome="gini", graph="digraph { fiscal_decentralization -> gini; ... }")
    ├── Identification: model.identify_effect()
    ├── Estimation: model.estimate_effect(method="iv.instrumental_variable")
    ├── Refutation: model.refute_estimate(method="random_common_cause")
    └── Save: analysis/results/causal_inference.json

3.10 Robustness Checks
    ├── Alternative dependent variable (poverty rate instead of Gini)
    ├── Subsample analysis (Java vs non-Java)
    ├── Different time periods (pre/post 2019)
    ├── Alternative estimation (GMM via rmcp):
    │   rmcp_execute(r_code="library(plm); pgmm(gini ~ lag(gini) + fiscal_decentral |
    │       lag(gini, 2:5), data=pdata, effect='twoways', model='twosteps')")
    └── Save: analysis/results/robustness.json

3.11 Visualizations (Publication Quality)
    ├── LIDA auto-visualization for exploration
    ├── Manual publication figures:
    │   ├── fig1_trend.pdf — Time series of Gini by region
    │   ├── fig2_scatter.pdf — Fiscal decentral vs Gini (with FE line)
    │   ├── fig3_coefplot.pdf — Coefficient plot with CI
    │   ├── fig4_bayesian_posterior.pdf — Posterior distributions
    │   └── fig5_dag.pdf — Causal DAG
    ├── All figures: 300 DPI, journal preset, colorblind-safe palette
    ├── tikzplotlib export for native LaTeX figures:
    │   tikzplotlib.save("analysis/figures/fig1_trend.tex")
    └── Save to analysis/figures/

3.12 Generate Tables
    ├── generate_table(type="descriptive") → tab1_descriptive.tex
    ├── generate_table(type="regression") → tab2_regression.tex
    ├── generate_table(type="robustness") → tab3_robustness.tex
    ├── generate_table(type="bayesian") → tab4_bayesian.tex
    ├── All tables: booktabs format, APA style, stargazer-like output
    └── Save to analysis/tables/

3.13 Post-Analysis Validation
    ├── Re-validate results against expectations:
    │   ├── Effect sizes within plausible range?
    │   ├── Signs match theory?
    │   ├── No impossible values (R² > 1, negative variance)?
    │   └── Consistent across specifications?
    └── Flag anomalies for human review

3.14 Checkpoint: analyze_complete
    └── [HUMAN REVIEW: results interpretation + robustness adequacy]
```

### Output Artifacts
- `analysis/scripts/` — Reproducible Python + R scripts
- `analysis/results/` — Structured JSON results (all models)
- `analysis/figures/` — Publication-quality figures (PDF + .tex via tikzplotlib)
- `analysis/tables/` — LaTeX tables (booktabs)
- `analysis/eda_report.html` — ydata-profiling report
- `analysis/validation_report.yaml` — Data validation results
- `analysis/assumptions.yaml` — All assumption test results

---

## Phase 4: WRITE

### Objective
Generate the complete academic paper using DSPy-optimized modules, compile with multiple backends, and ensure citation-grounded writing.

### Tools Used
| Tool | Purpose |
|------|---------|
| **DSPy modules** | Structured section generation with optimized prompts |
| **PaperQA2** | Citation-grounded writing (every claim backed by source) |
| **overleaf-mcp** | LaTeX editing and compilation (collaborative) |
| **Tectonic** | Zero-config LaTeX compilation (no TeX Live needed) |
| **Typst** | Fast alternative compiler (ms compilation times) |
| **tikzplotlib** | Native LaTeX figure generation |
| **LanguageTool** | Grammar and style checking |
| **proselint** | Academic writing style enforcement |
| **Pandoc** | Format conversion (LaTeX ↔ DOCX ↔ Markdown) |

### DSPy Pipeline Detail

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DSPy Module Composition for Paper Writing             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  class SectionWriter(dspy.Module):                                      │
│      def __init__(self):                                                │
│          self.retrieve = dspy.Retrieve(k=10)  # RAG from LanceDB       │
│          self.generate = dspy.ChainOfThought(                           │
│              "context, section_spec, style_guide ->                      │
│               section_text, citations_used")                             │
│          self.refine = dspy.ChainOfThought(                             │
│              "draft, feedback -> refined_text")                           │
│                                                                         │
│      def forward(self, section_spec, outline, results):                 │
│          context = self.retrieve(section_spec.query)                     │
│          draft = self.generate(context=context,                          │
│              section_spec=section_spec, style_guide=self.style_guide)    │
│          verified = self.verify_citations(draft)                         │
│          return self.refine(draft=verified, feedback=...)                │
│                                                                         │
│  Optimization:                                                          │
│  teleprompter = BootstrapFewShotWithRandomSearch(                       │
│      metric=academic_quality_metric,                                    │
│      max_bootstrapped_demos=4, num_candidate_programs=10)               │
│  optimized_writer = teleprompter.compile(SectionWriter(),               │
│      trainset=exemplar_sections)                                        │
│                                                                         │
│  Full Paper Composition:                                                │
│  class PaperGenerator(dspy.Module):                                     │
│      def __init__(self):                                                │
│          self.intro_writer = SectionWriter(style="intro")               │
│          self.litrev_writer = SectionWriter(style="litrev")             │
│          self.method_writer = SectionWriter(style="method")             │
│          self.results_writer = SectionWriter(style="results")           │
│          self.discuss_writer = SectionWriter(style="discuss")           │
│          self.abstract_writer = AbstractGenerator()                     │
│          self.coherence_checker = CoherenceChecker()                    │
│                                                                         │
│  Quality Metric:                                                        │
│  def academic_quality_metric(example, prediction):                      │
│      scores = {                                                         │
│          "citation_density": count_citations(pred) / n_paragraphs,      │
│          "hedging_appropriate": check_hedging(pred),                     │
│          "stats_formatted": check_apa_stats(pred),                      │
│          "no_first_person": not has_first_person(pred),                  │
│          "word_count_target": abs(len(pred) - target) < 100,            │
│      }                                                                  │
│      return sum(scores.values()) / len(scores)                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Steps

```
4.1 Setup LaTeX Project
    ├── Generate main.tex with journal template (elsarticle)
    ├── Generate preamble.tex with required packages
    ├── Link bibliography (references.bib)
    ├── Configure compilation backend:
    │   ├── Primary: Tectonic (zero-config, downloads packages automatically)
    │   ├── Alternative: Typst (for fast iteration, ms compilation)
    │   └── Collaborative: overleaf-mcp (if team editing needed)
    └── Setup overleaf-mcp project (if collaborative):
        overleaf_create_project(name="fiscal_decentralization_paper")

4.2 Write Introduction (DSPy SectionWriter + PaperQA2)
    ├── Retrieve relevant context from RAG:
    │   chunks = lancedb_query("fiscal decentralization inequality gap", k=10)
    │   kg_context = lightrag_query("what gaps exist in fiscal decentral research")
    ├── PaperQA2 for citation-grounded claims:
    │   paperqa2_ask("What is the current state of research on fiscal
    │                 decentralization and inequality?")
    ├── DSPy SectionWriter generates introduction
    ├── Structure: broad context → narrow focus → gap → objectives
    ├── Citation density: 2-4 per paragraph (all verified)
    └── Target: 1,200 words

4.3 Write Literature Review (DSPy SectionWriter + Knowledge Graph)
    ├── Query knowledge graph for thematic organization:
    │   themes = lightrag_query("main themes in fiscal decentralization literature")
    ├── For each theme, retrieve relevant paper chunks
    ├── DSPy SectionWriter with thematic structure
    ├── Every claim must have \cite{} from verified bib
    ├── Synthesize (not just summarize) — identify patterns, contradictions
    └── Target: 2,500 words, 30+ citations

4.4 Write Methodology (DSPy SectionWriter)
    ├── Context: analysis scripts + data description + methodology_spec.yaml
    ├── Structure: research design → data → variables → model specification
    ├── Include: equations (LaTeX math mode), variable definitions table
    ├── Sufficient detail for replication
    └── Target: 2,000 words

4.5 Write Results (DSPy SectionWriter)
    ├── Context: analysis/results/*.json + figures + tables
    ├── Structure: descriptive → main analysis → robustness
    ├── APA-formatted statistics: t(df) = X.XX, p < .001, d = X.XX, 95% CI [X, X]
    ├── Reference all tables (\ref{tab:...}) and figures (\ref{fig:...})
    ├── Interpret effect sizes, not just significance
    └── Target: 2,500 words

4.6 Write Discussion (DSPy SectionWriter + PaperQA2)
    ├── PaperQA2: "How do my findings compare to [specific prior study]?"
    ├── Structure: summary → interpretation → comparison → implications →
    │              limitations → future research
    ├── Compare findings with prior literature (cite specific papers)
    ├── [HUMAN APPROVAL: interpretation of results]
    └── Target: 2,000 words

4.7 Write Conclusion + Abstract
    ├── Conclusion: 500 words (key findings, policy implications)
    ├── Abstract (DSPy AbstractGenerator):
    │   ├── Structured: objective, methods, results (with numbers), conclusions
    │   ├── 150-300 words
    │   └── Must include key quantitative findings
    └── Keywords: 4-6 terms

4.8 Writing Quality Checks
    ├── LanguageTool: Grammar and style
    │   languagetool_check(text, language="en-US", enabled_rules=["ACADEMIC_WRITING"])
    ├── proselint: Academic style enforcement
    │   proselint.check(text) → warnings for:
    │   ├── Weasel words, cliches, redundancy, jargon
    │   ├── Passive voice overuse
    │   └── Hedging issues
    └── Apply fixes iteratively

4.9 Coherence Pass (DSPy CoherenceChecker)
    ├── Read all sections (summaries in context)
    ├── Check: terminology consistency, logical flow, no contradictions
    ├── Verify: forward/backward references resolve
    ├── Check: abstract matches actual content
    └── Generate revision instructions if needed → re-run affected sections

4.10 Compile Paper
    ├── Primary: tectonic main.tex  # Zero-config, auto-downloads packages
    ├── Alternative: typst compile main.typ  # Millisecond compilation
    ├── Collaborative: overleaf_compile(project_id=...) → PDF
    ├── Fix any compilation errors
    ├── Verify: figures render, tables format, citations resolve
    └── Generate: writing/compiled/paper.pdf

4.11 Format Conversion (if needed)
    ├── Pandoc for alternative formats:
    │   pandoc main.tex -o paper.docx --citeproc --bibliography=refs.bib
    │   pandoc main.tex -o paper.html --mathjax
    └── Journal-specific formatting adjustments

4.12 Checkpoint: write_complete
    └── [HUMAN REVIEW: full paper draft]
```

### Output Artifacts
- `writing/sections/` — Individual .tex files per section
- `writing/main.tex` — Master document
- `writing/compiled/paper.pdf` — Compiled PDF
- `writing/compiled/paper.docx` — Word version (if needed)
- `writing/style_report.yaml` — LanguageTool + proselint results

---

## Phase 5: REVIEW

### Objective
Comprehensive quality assurance through automated checks, simulated peer review, plagiarism detection, and reproducibility audit.

### Tools Used
| Tool | Purpose |
|------|---------|
| **CrossRef / Semantic Scholar APIs** | Citation verification (DOI resolution, metadata check) |
| **Statistical validity checker** | Verify reported statistics match analysis outputs |
| **LanguageTool + proselint** | Final writing quality pass |
| **Peer review simulator** | Adversarial sub-agent with reviewer persona |
| **sentence-transformers + MinHash** | Plagiarism / similarity detection |
| **Reproducibility audit** | Re-run all analysis scripts, verify outputs match |

### Steps

```
5.1 Citation Verification (Final Pass)
    ├── For every \cite{key} in the paper:
    │   ├── crossref_works(doi=bib[key].doi) → verify metadata
    │   ├── semantic_scholar_paper(paper_id=...) → verify exists, not retracted
    │   ├── Check: cited claim actually appears in cited paper
    │   │   └── RAG retrieval: query cited paper chunks for claimed content
    │   └── Flag: citation_not_found, claim_not_supported, paper_retracted
    ├── Verify citation formatting (APA/journal style)
    ├── Check: no orphan citations (in .bib but not cited)
    ├── Check: no missing citations (cited but not in .bib)
    └── Result: PASS (all verified) or BLOCK (with specific failures)

5.2 Statistical Validity Check
    ├── Parse all reported statistics from Results section:
    │   ├── Extract: β, SE, t, p, CI, R², F, df, N
    │   └── Compare against analysis/results/*.json
    ├── Verify:
    │   ├── Reported values match computed values (within rounding)
    │   ├── Degrees of freedom correct
    │   ├── Effect sizes reported alongside p-values
    │   ├── Confidence intervals included
    │   ├── No p-hacking patterns (many tests without correction)
    │   ├── Appropriate statistical language ("significant" only when p < α)
    │   └── Sample sizes consistent throughout
    └── Result: PASS or list of discrepancies

5.3 Writing Quality (Final)
    ├── LanguageTool full scan: grammar, style, consistency, punctuation
    ├── proselint scan: weasel words, cliches, redundancy, hedging
    ├── Custom academic checks:
    │   ├── No first person (unless journal allows)
    │   ├── Consistent terminology (same term for same concept)
    │   ├── Appropriate tense (past for results, present for discussion)
    │   └── Section word counts within targets (±10%)
    └── Result: warnings list with severity

5.4 Plagiarism / Similarity Detection
    ├── sentence-transformers similarity check:
    │   ├── Embed each paragraph of the paper
    │   ├── Compare against all source paper chunks in LanceDB
    │   ├── Flag: similarity > 0.85 (potential verbatim copying)
    │   ├── Flag: similarity > 0.70 (close paraphrase, needs citation)
    │   └── Acceptable: similarity < 0.70 (original writing)
    ├── MinHash for near-duplicate detection:
    │   ├── Compute MinHash signatures for paper sentences
    │   ├── LSH query against source corpus
    │   └── Flag overlapping n-grams (n=5) above threshold
    ├── Exclude: direct quotes (properly cited), method descriptions
    └── Result: similarity_report.yaml with flagged passages

5.5 Simulated Peer Review (Adversarial Sub-Agent)
    ├── Reviewer 1: Domain expert persona
    │   ├── Evaluates: methodology rigor, statistical validity, novelty
    │   └── Output: structured review (strengths, weaknesses, questions)
    ├── Reviewer 2: Methodology specialist
    │   ├── Focus: estimation strategy, identification, assumptions
    │   └── Output: technical critique
    ├── Reviewer 3: Writing/presentation specialist
    │   ├── Focus: clarity, structure, figure quality, argument flow
    │   └── Output: presentation feedback
    ├── Synthesize reviews → revision_plan.yaml
    └── Categorize: Major (must fix) vs Minor (should fix) vs Suggestion

5.6 Address Review Feedback
    ├── For each Major issue:
    │   ├── If methodology → may re-run analysis (back to Phase 3)
    │   ├── If writing → revise section via DSPy SectionWriter
    │   ├── If logic → restructure argument
    │   └── Re-compile after each fix
    ├── For each Minor issue: apply fix, document in revision_log.yaml
    ├── Iterate until: no Major issues remain
    └── Max 3 revision cycles before human intervention

5.7 Reproducibility Audit
    ├── Re-run all analysis scripts in clean E2B sandbox:
    │   ├── e2b_sandbox.run("python analysis/scripts/main_analysis.py")
    │   ├── Compare outputs against analysis/results/*.json
    │   └── Verify: identical results (within floating-point tolerance)
    ├── Check:
    │   ├── All data files have SHA256 hashes (logged in data/checksums.yaml)
    │   ├── Package versions pinned (requirements.txt with exact versions)
    │   ├── Random seeds set and documented
    │   ├── All figures reproducible from scripts
    │   └── No manual steps undocumented
    └── Result: PASS (fully reproducible) or list of issues

5.8 Final Compilation
    ├── tectonic main.tex (clean build)
    ├── Verify: no LaTeX warnings, correct page count, all refs resolve
    ├── Generate supplementary materials:
    │   ├── Appendix with full robustness tables
    │   ├── Data availability statement
    │   └── Replication package description
    └── Generate: writing/compiled/paper_final.pdf

5.9 [HUMAN APPROVAL: Final paper ready for submission]
    ├── Present: paper_final.pdf + quality_report + peer_review_sim
    ├── Human decision: APPROVE / REQUEST CHANGES / REJECT
    └── If APPROVE → package for submission

5.10 Checkpoint: review_complete
```

### Output Artifacts
- `review/quality_report.yaml` — All automated check results
- `review/peer_review_sim.yaml` — Simulated reviews (3 reviewers)
- `review/similarity_report.yaml` — Plagiarism detection results
- `review/revision_plan.yaml` — Issues and actions taken
- `review/revision_log.yaml` — All changes made during review
- `review/reproducibility_audit.yaml` — Reproducibility check results
- `writing/compiled/paper_final.pdf` — Final paper

---

## Human-in-the-Loop Checkpoints

| # | Checkpoint | Phase | What Requires Approval | Blocking? |
|---|------------|-------|----------------------|-----------|
| 1 | Research questions | PLAN | RQs + hypotheses formulated by DSPy | Yes |
| 2 | Methodology selection | PLAN | Which statistical method to use | Yes |
| 3 | Literature coverage | COLLECT | Sufficient papers? Missing key works? | No (advisory) |
| 4 | Variable selection | COLLECT | Which variables to include/exclude | Yes |
| 5 | Data quality | COLLECT | Cleaning decisions, outlier handling | Yes |
| 6 | Hausman test decision | ANALYZE | FE vs RE based on test results | Yes |
| 7 | Causal DAG | ANALYZE | DAG specification for DoWhy | Yes |
| 8 | Results interpretation | WRITE | What the results "mean" | Yes |
| 9 | Final paper draft | WRITE | Full paper before review | No (advisory) |
| 10 | Final submission | REVIEW | Paper ready for journal | Yes |

---

## Error Recovery Procedures

### If Data Collection Fails (BPS API)
```
1. Retry with exponential backoff (3 attempts)
2. Try alternative variable IDs (bps_search for synonyms)
3. Try different domain codes (national vs provincial)
4. Fall back to cached data if available
5. If persistent: notify human, suggest alternative data sources
6. Document data limitation in paper methodology section
```

### If PDF Processing Fails (MinerU/GROBID)
```
1. Try alternative extractor (MinerU → MarkItDown → PyMuPDF)
2. For GROBID failures: fall back to regex-based reference extraction
3. For scanned PDFs: apply OCR preprocessing (Tesseract)
4. If all fail: use abstract-only (mark paper as "partial_extraction")
5. Never silently skip — log all failures in processing_errors.yaml
```

### If Analysis Fails
```
1. Check data quality (Great Expectations validation report)
2. Check assumptions (which assumption violated?)
3. Try alternative method:
   - Non-parametric if normality fails
   - Robust SE if heteroscedasticity
   - Different estimator if endogeneity suspected
   - Reduce model complexity (fewer variables)
4. If Bayesian: check convergence (R-hat, ESS, divergences)
5. If causal: check DAG specification, try alternative instruments
6. Report limitation in paper (never hide failed analyses)
```

### If LaTeX Compilation Fails
```
1. Parse error log (line number + error type)
2. Common fixes:
   - Missing packages → Tectonic auto-downloads (or add \usepackage)
   - Encoding issues → ensure UTF-8 throughout
   - Figure paths → verify relative paths from main.tex
   - Bibliography errors → check .bib syntax (balanced braces)
   - Math mode errors → check $ matching, \begin/\end pairs
3. Retry compilation
4. If persistent: try Typst as alternative backend
5. Fall back to simpler formatting (remove problematic elements)
```

### If Citation Verification Fails
```
1. Search by title (fuzzy match via Semantic Scholar)
2. Check for DOI typos (common: missing prefix, wrong suffix)
3. Try alternative databases (CrossRef → OpenAlex → Google Scholar)
4. Check if paper was retracted (Retraction Watch database)
5. If truly unverifiable: REMOVE citation, find alternative source
6. Never cite what cannot be verified
```

### If Peer Review Identifies Major Issues
```
1. Categorize: methodology | writing | logic | missing_analysis
2. For methodology: re-run analysis (back to Phase 3), add robustness
3. For writing: revise sections (DSPy SectionWriter with revision_feedback)
4. For logic: restructure argument, add missing logical steps
5. Re-run full review after revisions
6. Max 3 revision cycles before human intervention
7. If stuck: present options to human with trade-off analysis
```

### If Plagiarism Detection Flags Content
```
1. Review flagged passages manually
2. For similarity > 0.85: rewrite completely or convert to direct quote
3. For similarity 0.70-0.85: ensure citation exists, rephrase
4. Re-run detection after fixes
```

---

## Complete Example Session (End-to-End)

```
User: "Saya ingin menulis paper tentang pengaruh inflasi terhadap kemiskinan
       di provinsi-provinsi Indonesia, target jurnal BIES"

═══════════════════════════════════════════════════════════════════════════
PHASE 1: PLAN (15-30 min)
═══════════════════════════════════════════════════════════════════════════

Agent: project_init(title="Impact of Inflation on Provincial Poverty", template="taylor_francis")
Agent: [PaperQA2] → 12 papers, key finding: "Mixed results; threshold effects suggested"
Agent: [paper-search-mcp] → 45 candidate papers (deduplicated)
Agent: [DSPy] → RQ1: threshold effect? RQ2: regional variation? RQ3: COVID impact?
Agent: Proposes: Panel FE + threshold regression + GMM robustness
  → [HUMAN APPROVAL ✓]
Agent: [DSPy OutlineGenerator] → outline.yaml (IMRaD, 8-10K words)

═══════════════════════════════════════════════════════════════════════════
PHASE 2: COLLECT (30-60 min)
═══════════════════════════════════════════════════════════════════════════

Agent: [BPS API] → poverty + inflation + controls (34 prov × 8 years = 272 obs)
Agent: [Pandera] → validation pass, 3 missing handled
Agent: [paper-search-mcp] → 78 papers found, 52 retained after filtering
Agent: [Unpaywall/CORE] → 38/52 full PDFs obtained
Agent: [MinerU + GROBID + Chonkie + scispaCy] → 847 chunks from 38 PDFs
Agent: [SPECTER2 + LanceDB] → embeddings indexed (IVF-PQ)
Agent: [LightRAG] → 234 entities, 412 relations
Agent: [zotero-mcp] → 52 papers organized, references.bib exported
Agent: [CrossRef] → 52/52 verified ✓
  → [HUMAN REVIEW ✓]

═══════════════════════════════════════════════════════════════════════════
PHASE 3: ANALYZE (30-50 min)
═══════════════════════════════════════════════════════════════════════════

Agent: [Great Expectations] → validation PASS
Agent: [ydata-profiling] → EDA report (inflation right-skewed)
Agent: [PandasAI] → Eastern Indonesia correlation stronger (r=0.42 vs 0.18)
Agent: [LIDA] → 6 goals suggested → [HUMAN SELECTS 3]
Agent: [linearmodels] → FE: β=0.034 (p<0.01), Hausman → FE preferred [HUMAN ✓]
Agent: [PyMC+Bambi] → Posterior confirms: HDI [0.017, 0.049]
Agent: [DoWhy] → ATE=0.031, refutation tests pass
Agent: [rmcp] → Threshold at 7.2% inflation (below: NS, above: β=0.089***)
Agent: [tikzplotlib] → 4 publication figures (.pdf + .tex)
Agent: Tables → 4 booktabs tables
  → [HUMAN REVIEW ✓]

═══════════════════════════════════════════════════════════════════════════
PHASE 4: WRITE (40-90 min)
═══════════════════════════════════════════════════════════════════════════

Agent: [DSPy + PaperQA2] → Intro (1200w/14 cites), LitRev (2800w/38 cites),
       Method (2200w), Results (2600w), Discussion (2100w) [HUMAN ✓],
       Conclusion (600w), Abstract (245w)
Agent: [LanguageTool + proselint] → 3 grammar + 7 style fixes
Agent: [DSPy CoherenceChecker] → 1 terminology fix
Agent: [Tectonic] → paper.pdf (14 pages, no errors)
Agent: [Pandoc] → paper.docx for co-authors

═══════════════════════════════════════════════════════════════════════════
PHASE 5: REVIEW (30-50 min)
═══════════════════════════════════════════════════════════════════════════

Agent: [CrossRef] → 52/52 citations verified ✓
Agent: Statistical validity → all values match ✓
Agent: [LanguageTool + proselint] → PASS
Agent: [sentence-transformers + MinHash] → max similarity 0.62 ✓
Agent: [Peer Review Sim] → 3 reviewers: "Minor revisions"
Agent: Address 3 minor issues → re-compile
Agent: [E2B] → Reproducibility audit PASS ✓
Agent: Final: paper_final.pdf (14 pages)
  → [HUMAN APPROVAL ✓]

OUTPUT: paper_final.pdf + .docx + supplementary + replication_package/
```

---

## Timing Estimates

| Phase | Estimated Time | Bottleneck | Key Tools |
|-------|---------------|-----------|-----------|
| PLAN | 15-30 min | Human approval | PaperQA2, paper-search-mcp, DSPy |
| COLLECT | 30-60 min | API rate limits, PDF processing | paper-search-mcp, MinerU, SPECTER2, LightRAG |
| ANALYZE | 30-50 min | Computation, human approval | jupyter-mcp, linearmodels, PyMC, rmcp |
| WRITE | 40-90 min | LLM generation (section by section) | DSPy, PaperQA2, Tectonic, LanguageTool |
| REVIEW | 30-50 min | Revision cycles | CrossRef, peer sim, sentence-transformers |
| **Total** | **~2.5-4.5 hours** | (with human-in-the-loop) |

*Note: Times assume human is available for approval gates. Without human gates, automated portion takes ~1.5-2.5 hours.*

---

## Tool Summary (All Phases)

| Category | Tools | Count |
|----------|-------|-------|
| Literature Discovery | PaperQA2, paper-search-mcp (22 sources) | 2 |
| PDF Processing | MinerU, MarkItDown, GROBID | 3 |
| Embeddings & RAG | SPECTER2, LanceDB, Chonkie SemanticChunker | 3 |
| Knowledge Graph | LightRAG, scispaCy | 2 |
| Citation Management | zotero-mcp, CrossRef API, Semantic Scholar API, Unpaywall, CORE | 5 |
| Data Validation | Great Expectations, Pandera | 2 |
| Exploratory Analysis | PandasAI, LIDA, ydata-profiling | 3 |
| Statistical Analysis | statsmodels, scipy, linearmodels, PyMC, Bambi, DoWhy, rmcp (52 R tools) | 7 |
| Code Execution | jupyter-mcp, E2B | 2 |
| Paper Writing | DSPy modules, PaperQA2 | 2 |
| LaTeX/Compilation | Tectonic, Typst, overleaf-mcp, tikzplotlib | 4 |
| Writing Quality | LanguageTool, proselint | 2 |
| Format Conversion | Pandoc | 1 |
| Plagiarism Detection | sentence-transformers, MinHash/LSH | 2 |
| Research Formulation | DSPy (ResearchQuestionFormulator, OutlineGenerator) | 1 |
| **Total unique tools** | | **~40+** |
