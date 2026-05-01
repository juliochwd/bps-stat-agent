"""Research-wide constants for the BPS Academic Research Agent.

Centralises configuration values used across all research phases:
- Version and limits
- Phase ordering and tool constraints
- Journal templates and section ordering
- APA formatting rules
- Supported file formats
- Quality-gate thresholds
- Model routing rules
"""

from __future__ import annotations

from .project_state import ResearchPhase

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

RESEARCH_VERSION: str = "1.0.0"

# ---------------------------------------------------------------------------
# Token / step limits
# ---------------------------------------------------------------------------

DEFAULT_TOKEN_LIMIT: int = 120_000
DEFAULT_MAX_STEPS: int = 100

# ---------------------------------------------------------------------------
# Phase ordering
# ---------------------------------------------------------------------------

PHASE_ORDER: list[ResearchPhase] = [
    ResearchPhase.PLAN,
    ResearchPhase.COLLECT,
    ResearchPhase.ANALYZE,
    ResearchPhase.WRITE,
    ResearchPhase.REVIEW,
]

# ---------------------------------------------------------------------------
# Tool limits
# ---------------------------------------------------------------------------

MAX_TOOLS_PER_PHASE: int = 15
PERSISTENT_TOOLS_COUNT: int = 5

# ---------------------------------------------------------------------------
# Journal templates & methodologies
# ---------------------------------------------------------------------------

DEFAULT_TEMPLATE: str = "elsevier"

SUPPORTED_TEMPLATES: list[str] = [
    "ieee",
    "elsevier",
    "springer",
    "springer_lncs",
    "mdpi",
    "apa7",
]

SUPPORTED_METHODOLOGIES: list[str] = [
    "panel_data",
    "cross_sectional",
    "time_series",
    "mixed_methods",
    "meta_analysis",
]

# Journal template metadata (document class, bst style, columns, font size)
JOURNAL_TEMPLATES: dict[str, dict[str, object]] = {
    "ieee": {"class": "IEEEtran", "bst": "IEEEtran", "columns": 2, "font_size": 10},
    "elsevier": {"class": "elsarticle", "bst": "elsarticle-num", "columns": 1, "font_size": 12},
    "springer": {"class": "svjour3", "bst": "spbasic", "columns": 1, "font_size": 10},
    "springer_lncs": {"class": "llncs", "bst": "splncs04", "columns": 1, "font_size": 10},
    "mdpi": {"class": "mdpi", "bst": "mdpi", "columns": 1, "font_size": 10},
    "apa7": {"class": "apa7", "bst": None, "columns": 1, "font_size": 12},
}

# ---------------------------------------------------------------------------
# Paper sections (IMRaD order)
# ---------------------------------------------------------------------------

PAPER_SECTIONS: list[str] = [
    "abstract",
    "introduction",
    "literature_review",
    "methodology",
    "results",
    "discussion",
    "conclusion",
]

# Alias used in some modules
IMRAD_SECTIONS: list[str] = PAPER_SECTIONS

# ---------------------------------------------------------------------------
# Workspace directory structure
# ---------------------------------------------------------------------------

WORKSPACE_DIRS: list[str] = [
    "data/raw",
    "data/processed",
    "data/external",
    "literature/pdfs",
    "literature/notes",
    "analysis/scripts",
    "analysis/outputs",
    "analysis/figures",
    "writing/sections",
    "writing/figures",
    "writing/tables",
    "templates",
    "checkpoints",
    ".sessions",
    "logs",
]

# ---------------------------------------------------------------------------
# APA formatting
# ---------------------------------------------------------------------------

APA_DATE_FORMAT: str = "%Y, %B %d"
APA_DECIMAL_PLACES: int = 2

APA_READABILITY: dict[str, dict[str, object]] = {
    "abstract": {"flesch_kincaid_grade": (12, 16), "target": "concise, clear"},
    "introduction": {"flesch_kincaid_grade": (12, 18), "target": "accessible"},
    "methodology": {"flesch_kincaid_grade": (14, 20), "target": "precise, technical"},
    "results": {"flesch_kincaid_grade": (12, 18), "target": "clear, data-focused"},
    "discussion": {"flesch_kincaid_grade": (12, 18), "target": "analytical"},
}

# ---------------------------------------------------------------------------
# Supported file formats
# ---------------------------------------------------------------------------

SUPPORTED_DATA_FORMATS: list[str] = [
    "csv",
    "xlsx",
    "json",
    "stata",
    "spss",
    "parquet",
]

SUPPORTED_FIGURE_FORMATS: list[str] = [
    "pdf",
    "png",
    "svg",
    "eps",
]

# ---------------------------------------------------------------------------
# API rate limits (requests per second)
# ---------------------------------------------------------------------------

API_RATE_LIMITS: dict[str, float] = {
    "semantic_scholar": 1.0,
    "crossref": 50.0,
    "openalex": 10.0,
    "core": 0.5,
    "unpaywall": 1.15,
}

# Cache TTL (days)
CACHE_TTL: dict[str, int] = {
    "semantic_scholar": 30,
    "crossref": 30,
    "openalex": 7,
    "core": 30,
    "unpaywall": 7,
}

# ---------------------------------------------------------------------------
# Embedding & chunking
# ---------------------------------------------------------------------------

DEFAULT_EMBEDDING_DIMENSIONS: int = 768
CHUNK_SIZE_TOKENS: int = 768
CHUNK_OVERLAP_TOKENS: int = 128

# ---------------------------------------------------------------------------
# Quality-gate thresholds
# ---------------------------------------------------------------------------

QUALITY_GATE_THRESHOLDS: dict[str, int | float] = {
    "max_unverified_citations": 0,
    "max_grammar_warnings": 5,
    "max_style_issues": 3,
    "plagiarism_threshold": 0.05,
    "min_citation_confidence": 0.85,
    "min_statistical_power": 0.80,
    "min_section_coherence": 0.70,
    "min_citation_coverage": 0.90,
    "max_self_citation_ratio": 0.20,
    "min_recency_ratio": 0.30,
    "recency_window_years": 5,
}

# Alias for backward compatibility
QUALITY_THRESHOLDS = QUALITY_GATE_THRESHOLDS

# ---------------------------------------------------------------------------
# Model routing rules
# ---------------------------------------------------------------------------

MODEL_ROUTING_RULES: dict[str, dict[str, str]] = {
    "planning": {
        "primary": "claude-sonnet-4-20250514",
        "fallback": "gpt-4o",
    },
    "literature_search": {
        "primary": "gpt-4o",
        "fallback": "gpt-4o-mini",
    },
    "data_analysis": {
        "primary": "claude-sonnet-4-20250514",
        "fallback": "gpt-4o",
    },
    "writing": {
        "primary": "claude-sonnet-4-20250514",
        "fallback": "gpt-4o",
    },
    "review": {
        "primary": "claude-sonnet-4-20250514",
        "fallback": "gpt-4o",
    },
    "summarization": {
        "primary": "gpt-4o-mini",
        "fallback": "claude-haiku-4-20250414",
    },
    "embedding": {
        "primary": "text-embedding-3-small",
        "fallback": "text-embedding-3-small",
    },
}

# Alias for backward compatibility
MODEL_ROUTING = MODEL_ROUTING_RULES
