# BPS Academic Research Agent — Dependencies

**Version:** 2.0 (Comprehensive)  
**Updated:** 2025-07-14  
**Status:** Final — All discovered tools included

---

## Core Framework

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| `dspy` | >=2.0 | Optimizable LLM pipelines with automatic prompt tuning | MIT |
| `litellm` | >=1.40 | Multi-provider LLM gateway (OpenAI, Anthropic, Gemini, etc.) | MIT |
| `paper-qa` | >=5.0 | Scientific RAG with citation-aware retrieval | Apache 2.0 |

---

## Document Processing

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| `markitdown[all]` | >=0.1.5 | Universal file→Markdown converter (PDF, DOCX, PPTX, HTML, etc.) | MIT |
| `mineru` | >=3.0 | Scientific PDF parser with layout understanding | Apache 2.0+ |
| `docling` | >=2.0 | IBM PDF understanding with table/figure extraction | MIT |
| `unstructured[all-docs]` | >=0.22 | Document ETL pipeline for all file types | Apache 2.0 |
| `pymupdf4llm` | >=0.0.17 | LLM-optimized PDF extraction (Markdown output) | AGPL |
| `pdfplumber` | >=0.11 | PDF table extraction with precise coordinates | MIT |

---

## RAG & Knowledge

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| `llama-index` | >=0.11 | Multi-document RAG framework with composable pipelines | MIT |
| `lightrag-hku` | >=1.5 | Knowledge graph RAG with entity/relation extraction | MIT |
| `sentence-transformers` | >=3.0 | Embedding models (SBERT, E5, BGE, etc.) | Apache 2.0 |
| `chromadb` | >=0.5 | Vector database (embedded, persistent) | Apache 2.0 |
| `lancedb` | >=0.9 | Serverless vector DB (columnar, fast) | Apache 2.0 |
| `chonkie` | >=0.4 | Fast semantic chunking with overlap control | MIT |
| `scispacy` | >=0.5 | Scientific/biomedical NLP models | MIT |
| `spacy` | >=3.7 | Industrial NLP pipeline (tokenization, NER, POS) | MIT |
| `networkx` | >=3.2 | Graph analysis and knowledge graph operations | BSD |

---

## Statistical Analysis

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| `statsmodels` | >=0.14 | OLS, logistic, ARIMA, VAR, diagnostics, regression | BSD-3 |
| `scipy` | >=1.11 | Hypothesis tests, distributions, optimization | BSD-3 |
| `linearmodels` | >=6.0 | Panel data (FE, RE, Hausman, IV, GMM) | BSD-3 |
| `arch` | >=7.0 | GARCH, unit root tests (ADF, KPSS, PP) | BSD-3 |
| `pingouin` | >=0.5.4 | Effect sizes, power analysis, Bayesian stats | GPL-3 |
| `pymc` | >=5.0 | Bayesian inference with MCMC/VI | Apache 2.0 |
| `bambi` | >=0.14 | Bayesian formula interface (R-style, built on PyMC) | MIT |
| `arviz` | >=0.18 | Bayesian visualization and diagnostics | Apache 2.0 |
| `dowhy` | >=0.11 | Causal inference (DAGs, do-calculus, refutation) | MIT |
| `causalml` | >=0.15 | Treatment effect estimation (uplift, meta-learners) | Apache 2.0 |
| `lifelines` | >=0.29 | Survival analysis (KM, Cox PH, AFT) | MIT |
| `scikit-learn` | >=1.3 | ML preprocessing, clustering, model selection | BSD-3 |
| `pandasai` | >=2.0 | Conversational data analysis with LLMs | MIT |
| `lida` | >=0.0.10 | Automatic visualization generation and explanation | MIT |
| `numpy` | >=1.24 | Numerical computing (transitive dep) | BSD-3 |
| `pandas` | >=2.0 | Data manipulation (transitive dep) | BSD-3 |

---

## Data Quality

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| `ydata-profiling` | >=4.6 | Automated EDA with HTML reports | MIT |
| `great-expectations` | >=0.18 | Data quality validation and documentation | Apache 2.0 |
| `pandera` | >=0.20 | DataFrame schema validation (type-safe) | MIT |

---

## Visualization

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| `matplotlib` | >=3.8 | Publication-quality figures | PSF |
| `seaborn` | >=0.13 | Statistical visualizations (built on matplotlib) | BSD-3 |
| `tikzplotlib` | >=0.10 | matplotlib→TikZ/PGFplots export for LaTeX | MIT |

---

## Paper Writing

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| `pylatex` | >=1.4.2 | Programmatic LaTeX document generation | MIT |
| `python-docx` | >=1.2 | DOCX document generation | MIT |
| `citeproc-py` | >=0.9 | CSL citation processing and formatting | BSD-2 |
| `bibtexparser` | >=1.4 | BibTeX parsing, writing, and management | MIT |
| `pypandoc` | >=1.13 | Pandoc Python wrapper (format conversion) | MIT |
| `habanero` | >=2.3 | CrossRef API client (DOI resolution, metadata) | MIT |

---

## Writing Quality

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| `language-tool-python` | >=2.8 | Grammar and style checker (LanguageTool wrapper) | LGPL |
| `proselint` | >=0.14 | Prose linting (jargon, clichés, redundancy) | BSD-3 |
| `textstat` | >=0.7 | Readability statistics (Flesch, Gunning Fog, etc.) | MIT |

---

## Execution Sandbox

| Package | Version | Purpose | License |
|---------|---------|---------|---------|
| `e2b-code-interpreter` | >=1.0 | Cloud sandbox for code execution (E2B platform) | MIT |
| `docker` | >=7.0 | Docker SDK for Python (local sandbox) | Apache 2.0 |
| `RestrictedPython` | >=7.0 | AST-level code restriction (fallback sandbox) | ZPL |

---

## System Dependencies

| Tool | Version | Purpose | Installation |
|------|---------|---------|-------------|
| Docker | >=24.0 | Sandboxed code execution | `apt install docker.io` |
| Tectonic | latest | Rust LaTeX engine (self-contained, no TeX Live needed) | `cargo install tectonic` or binary |
| Typst | >=0.12 | Modern LaTeX alternative (fast, simpler syntax) | `cargo install typst-cli` or binary |
| Pandoc | >=3.0 | Document format conversion | `apt install pandoc` |
| LanguageTool | latest | Grammar/style server (Java, self-hosted) | Docker or `java -jar languagetool-server.jar` |
| GROBID | latest | Scientific PDF header/reference extraction | `docker pull lfoppiano/grobid:0.8.0` |
| texlive-latex-extra | latest | Extended LaTeX packages | `apt install texlive-latex-extra` |
| texlive-publishers | latest | Journal templates (IEEE, Elsevier, Springer) | `apt install texlive-publishers` |

### LaTeX Packages (via TeX Live or Tectonic)

Required LaTeX packages (auto-downloaded by Tectonic):
- `IEEEtran` — IEEE journal template
- `elsarticle` — Elsevier journal template
- `svjour3` — Springer journal template
- `llncs` — Springer LNCS template
- `apa7` — APA 7th edition template
- `booktabs` — Publication-quality tables
- `natbib` / `biblatex` — Citation management
- `hyperref` — Hyperlinks
- `graphicx` — Figure inclusion
- `amsmath` — Mathematical typesetting
- `tikz` / `pgfplots` — Programmatic figures

---

## Docker Sandbox Image (Updated)

```dockerfile
# Dockerfile.sandbox
# Comprehensive research sandbox with ALL statistical packages
FROM python:3.11-slim

LABEL maintainer="BPS Research Agent"
LABEL description="Sandboxed execution environment with full statistical stack"

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Install full scientific/statistical stack (pinned for reproducibility)
RUN pip install --no-cache-dir \
    # Core numerical
    numpy==1.26.4 \
    pandas==2.2.0 \
    scipy==1.12.0 \
    # Statistical analysis
    statsmodels==0.14.1 \
    linearmodels==6.0 \
    arch==7.0.0 \
    pingouin==0.5.4 \
    scikit-learn==1.4.0 \
    # Bayesian
    pymc==5.10.4 \
    bambi==0.14.0 \
    arviz==0.18.0 \
    # Causal inference
    dowhy==0.11.1 \
    causalml==0.15.1 \
    # Survival analysis
    lifelines==0.29.0 \
    # Visualization
    matplotlib==3.8.3 \
    seaborn==0.13.2 \
    tikzplotlib==0.10.1 \
    # Data quality
    pandera==0.20.0 \
    # Utilities
    networkx==3.2.1 \
    sympy==1.12

# Remove pip to prevent runtime installs (security)
RUN pip uninstall -y pip setuptools wheel

# Create non-root user
RUN useradd -m -s /bin/bash sandbox
USER sandbox
WORKDIR /workspace

# Create output directories
RUN mkdir -p /home/sandbox/output /home/sandbox/figures /home/sandbox/tables

# Resource limits enforced at runtime via Docker --memory, --cpus flags
```

Build and run:
```bash
# Build
docker build -f Dockerfile.sandbox -t research-agent-sandbox:latest .

# Run with resource limits
docker run --rm \
    --memory=4g --cpus=2 \
    --network=none \
    --read-only \
    --tmpfs /tmp:size=512m \
    -v $(pwd)/workspace:/workspace:ro \
    -v $(pwd)/output:/home/sandbox/output \
    research-agent-sandbox:latest \
    python /workspace/script.py
```

---

## pyproject.toml Extension

```toml
[project.optional-dependencies]

# Core research framework
research-core = [
    "dspy>=2.0",
    "litellm>=1.40",
    "paper-qa>=5.0",
]

# Statistical analysis (frequentist + Bayesian + causal)
research-analysis = [
    "statsmodels>=0.14",
    "scipy>=1.11",
    "linearmodels>=6.0",
    "arch>=7.0",
    "pingouin>=0.5.4",
    "pymc>=5.0",
    "bambi>=0.14",
    "arviz>=0.18",
    "dowhy>=0.11",
    "causalml>=0.15",
    "lifelines>=0.29",
    "scikit-learn>=1.3",
    "pandasai>=2.0",
    "lida>=0.0.10",
    "numpy>=1.24",
    "pandas>=2.0",
    "matplotlib>=3.8",
    "seaborn>=0.13",
    "tikzplotlib>=0.10",
    "ydata-profiling>=4.6",
    "great-expectations>=0.18",
    "pandera>=0.20",
]

# Paper writing and quality
research-writing = [
    "pylatex>=1.4.2",
    "python-docx>=1.2",
    "citeproc-py>=0.9",
    "bibtexparser>=1.4",
    "pypandoc>=1.13",
    "habanero>=2.3",
    "language-tool-python>=2.8",
    "proselint>=0.14",
    "textstat>=0.7",
]

# RAG, embeddings, and knowledge management
research-rag = [
    "llama-index>=0.11",
    "lightrag-hku>=1.5",
    "sentence-transformers>=3.0",
    "chromadb>=0.5",
    "lancedb>=0.9",
    "chonkie>=0.4",
    "scispacy>=0.5",
    "spacy>=3.7",
    "networkx>=3.2",
    "markitdown[all]>=0.1.5",
    "mineru>=3.0",
    "docling>=2.0",
    "unstructured[all-docs]>=0.22",
    "pymupdf4llm>=0.0.17",
    "pdfplumber>=0.11",
]

# Sandbox execution
research-sandbox = [
    "e2b-code-interpreter>=1.0",
    "docker>=7.0",
    "RestrictedPython>=7.0",
]

# Everything combined
research-all = [
    "bps-stat-agent[research-core]",
    "bps-stat-agent[research-analysis]",
    "bps-stat-agent[research-writing]",
    "bps-stat-agent[research-rag]",
    "bps-stat-agent[research-sandbox]",
]
```

---

## Compatibility Matrix

| Package | Python 3.10 | Python 3.11 | Python 3.12 | Notes |
|---------|:-----------:|:-----------:|:-----------:|-------|
| dspy | ✅ | ✅ | ✅ | |
| litellm | ✅ | ✅ | ✅ | |
| paper-qa | ✅ | ✅ | ✅ | |
| markitdown | ✅ | ✅ | ✅ | |
| mineru | ✅ | ✅ | ⚠️ | Check PyTorch compatibility |
| docling | ✅ | ✅ | ✅ | |
| unstructured | ✅ | ✅ | ✅ | |
| pymupdf4llm | ✅ | ✅ | ✅ | AGPL license — review |
| pdfplumber | ✅ | ✅ | ✅ | |
| llama-index | ✅ | ✅ | ✅ | |
| lightrag-hku | ✅ | ✅ | ✅ | |
| sentence-transformers | ✅ | ✅ | ✅ | |
| chromadb | ✅ | ✅ | ✅ | |
| lancedb | ✅ | ✅ | ✅ | |
| chonkie | ✅ | ✅ | ✅ | |
| scispacy | ✅ | ✅ | ⚠️ | Depends on spaCy model availability |
| spacy | ✅ | ✅ | ✅ | |
| networkx | ✅ | ✅ | ✅ | |
| statsmodels | ✅ | ✅ | ✅ | |
| scipy | ✅ | ✅ | ✅ | |
| linearmodels | ✅ | ✅ | ✅ | |
| arch | ✅ | ✅ | ✅ | |
| pingouin | ✅ | ✅ | ⚠️ | GPL-3 — check 3.12 release |
| pymc | ✅ | ✅ | ⚠️ | Requires pytensor; 3.12 support improving |
| bambi | ✅ | ✅ | ⚠️ | Follows PyMC compatibility |
| arviz | ✅ | ✅ | ✅ | |
| dowhy | ✅ | ✅ | ✅ | |
| causalml | ✅ | ✅ | ⚠️ | Heavy C++ deps; check wheels |
| lifelines | ✅ | ✅ | ✅ | |
| scikit-learn | ✅ | ✅ | ✅ | |
| pandasai | ✅ | ✅ | ✅ | |
| lida | ✅ | ✅ | ✅ | |
| ydata-profiling | ✅ | ✅ | ✅ | |
| great-expectations | ✅ | ✅ | ✅ | |
| pandera | ✅ | ✅ | ✅ | |
| matplotlib | ✅ | ✅ | ✅ | |
| seaborn | ✅ | ✅ | ✅ | |
| tikzplotlib | ✅ | ✅ | ✅ | |
| pylatex | ✅ | ✅ | ✅ | |
| python-docx | ✅ | ✅ | ✅ | |
| citeproc-py | ✅ | ✅ | ✅ | |
| bibtexparser | ✅ | ✅ | ✅ | |
| pypandoc | ✅ | ✅ | ✅ | |
| habanero | ✅ | ✅ | ✅ | |
| language-tool-python | ✅ | ✅ | ✅ | Requires Java runtime |
| proselint | ✅ | ✅ | ✅ | |
| textstat | ✅ | ✅ | ✅ | |
| e2b-code-interpreter | ✅ | ✅ | ✅ | |
| docker | ✅ | ✅ | ✅ | |
| RestrictedPython | ✅ | ✅ | ✅ | |

**Legend:** ✅ = Fully supported | ⚠️ = Check latest release for compatibility

**Recommended:** Python 3.11 (best compatibility across all packages)

---

## Size Impact Estimates

| Component | Estimated Size | Notes |
|-----------|---------------|-------|
| **research-core** (DSPy, LiteLLM, PaperQA) | ~200MB | Lightweight |
| **research-analysis** (all stats) | ~1.2GB | Includes PyMC/pytensor |
| **research-writing** (LaTeX, DOCX, citations) | ~50MB | Lightweight |
| **research-rag** (embeddings, vector DB, NLP) | ~2.5GB | Includes transformer models |
| **research-sandbox** (Docker, E2B) | ~30MB | Lightweight |
| Docker sandbox image | ~1.5GB | Full statistical stack |
| Tectonic (LaTeX engine) | ~50MB | Downloads packages on demand |
| Typst | ~30MB | Self-contained binary |
| TeX Live (texlive-latex-extra + publishers) | ~1.5GB | If using pdflatex |
| TeX Live (full) | ~5GB | Not recommended |
| GROBID Docker image | ~1.2GB | Scientific PDF parsing |
| LanguageTool server | ~200MB | Java-based |
| spaCy models (en_core_web_lg) | ~560MB | Per model |
| Sentence-transformer models | ~400MB | Per model |

### Total Estimates

| Installation Profile | Disk Space | RAM (runtime) |
|---------------------|-----------|---------------|
| **Minimal** (core + analysis + writing) | ~1.5GB | ~2GB |
| **Standard** (+ RAG, no heavy models) | ~3GB | ~4GB |
| **Full** (research-all + Docker + models) | ~8GB | ~8GB |
| **Full + TeX Live** (instead of Tectonic) | ~10GB | ~8GB |

---

## Installation Commands

```bash
# ─── Quick Install (recommended) ───────────────────────────────────────────

# Install everything
pip install "bps-stat-agent[research-all]"

# Or with uv (faster)
uv pip install "bps-stat-agent[research-all]"

# ─── Selective Install ──────────────────────────────────────────────────────

# Core framework only
pip install "bps-stat-agent[research-core]"

# Statistical analysis only
pip install "bps-stat-agent[research-analysis]"

# Paper writing only
pip install "bps-stat-agent[research-writing]"

# RAG and knowledge management only
pip install "bps-stat-agent[research-rag]"

# ─── System Dependencies (Ubuntu/Debian) ───────────────────────────────────

# Essential system packages
sudo apt update && sudo apt install -y \
    docker.io \
    pandoc \
    default-jre \
    texlive-latex-extra \
    texlive-publishers \
    texlive-science \
    texlive-bibtex-extra \
    texlive-fonts-recommended

# OR use Tectonic instead of TeX Live (much smaller)
curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net | sh

# OR install Typst (modern alternative)
curl -fsSL https://typst.community/typst-install/install.sh | sh

# ─── Docker Setup ──────────────────────────────────────────────────────────

# Build sandbox image
docker build -f Dockerfile.sandbox -t research-agent-sandbox:latest .

# Pull GROBID for scientific PDF parsing
docker pull lfoppiano/grobid:0.8.0

# ─── NLP Models ────────────────────────────────────────────────────────────

# spaCy English model
python -m spacy download en_core_web_lg

# SciSpaCy biomedical model
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_lg-0.5.4.tar.gz

# ─── LanguageTool Server ───────────────────────────────────────────────────

# Option A: Docker
docker run -d -p 8081:8010 erikvl87/languagetool

# Option B: Direct (requires Java)
wget https://languagetool.org/download/LanguageTool-stable.zip
unzip LanguageTool-stable.zip
java -cp languagetool-server.jar org.languagetool.server.HTTPServer --port 8081

# ─── Verification ──────────────────────────────────────────────────────────

# Verify installation
python -c "
import dspy, litellm, statsmodels, scipy, pymc
import sklearn, matplotlib, networkx
print('✅ All core packages imported successfully')
"

# Setup wizard (interactive)
bpsagent setup --research
```

---

## License Summary

| License | Packages | Commercial Use | Notes |
|---------|----------|:--------------:|-------|
| MIT | 28 packages | ✅ | No restrictions |
| Apache 2.0 | 10 packages | ✅ | Patent grant included |
| BSD-2/BSD-3 | 8 packages | ✅ | No restrictions |
| PSF | 1 package (matplotlib) | ✅ | No restrictions |
| LGPL | 1 package (language-tool-python) | ✅ | Dynamic linking OK |
| GPL-3 | 1 package (pingouin) | ⚠️ | Copyleft — review for distribution |
| AGPL | 1 package (pymupdf4llm) | ⚠️ | Network copyleft — review for SaaS |
| ZPL | 1 package (RestrictedPython) | ✅ | Permissive |

**⚠️ License Review Required:**
- `pingouin` (GPL-3): If distributing the agent as proprietary software, consider isolating in subprocess
- `pymupdf4llm` (AGPL): If serving over network, AGPL requires source disclosure; consider `pdfplumber` as alternative

---

## Architecture Decision Records

### ADR-001: Tectonic over TeX Live
- **Decision:** Default to Tectonic for LaTeX compilation
- **Rationale:** 50MB vs 1.5-5GB; auto-downloads packages; reproducible builds
- **Fallback:** TeX Live for edge cases requiring obscure packages

### ADR-002: LanceDB over Pinecone/Weaviate
- **Decision:** Use LanceDB as primary vector store, ChromaDB as alternative
- **Rationale:** Serverless (no separate process), Apache Arrow-based, fast
- **Trade-off:** Less mature ecosystem than Pinecone

### ADR-003: E2B + Docker dual sandbox
- **Decision:** E2B for cloud execution, Docker for local/air-gapped
- **Rationale:** E2B provides instant sandboxes; Docker for offline/privacy
- **Fallback:** RestrictedPython for lightweight AST-level restriction
