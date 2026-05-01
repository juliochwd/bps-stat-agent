# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v1.0.0 — Academic Research Agent

### Added
- **Research Orchestrator** (`mini_agent/research/orchestrator.py`) — Phase-gated research pipeline wrapping the core Agent
- **Phase Manager** — 5-phase workflow: PLAN → COLLECT → ANALYZE → WRITE → REVIEW with max 15 tools per phase
- **Project State** — YAML-persisted project state for multi-session research continuity
- **Workspace Scaffolder** — Auto-creates IMRaD directory structure for research projects
- **Session Resume** — Checkpoint-based session recovery for long-running research
- **Approval Gates** — Quality gate evaluator with configurable thresholds per phase
- **Sub-Agent Dispatcher** — 6 specialized sub-agents (literature_reviewer, methodology_advisor, section_writer, stat_validator, citation_verifier, peer_reviewer)
- **Tool Registry** — Phase-aware tool loading with max 15 tools per phase to prevent LLM confusion
- **LLM Gateway** — LiteLLM integration with multi-provider routing, cost tracking, fallback chains
- **DSPy Modules** — Stanford DSPy signatures for search queries, methodology design, evidence synthesis, section writing, results interpretation
- **Cost Tracker** — Per-session and per-phase cost tracking with budget alerts
- **Decision Log** — Structured logging of all research decisions with rationale

#### Statistics & Analysis Tools (13 new tools)
- `descriptive_stats` — Summary statistics, distributions, correlations
- `regression_analysis` — Linear, logistic, polynomial, multi-variate regression
- `hypothesis_test` — t-test, chi-square, ANOVA, Mann-Whitney, Kruskal-Wallis
- `create_visualization` — Charts, plots, heatmaps with matplotlib/seaborn
- `time_series_analysis` — ARIMA, seasonal decomposition, forecasting
- `bayesian_analysis` — Bayesian inference with PyMC/Bambi
- `causal_inference` — DoWhy causal models, ATE estimation
- `survival_analysis` — Kaplan-Meier, Cox PH, AFT models
- `automated_eda` — Automated exploratory data analysis
- `auto_visualize` — Smart visualization selection based on data types
- `validate_data` — Data quality checks, missing values, outliers
- `check_statistical_validity` — Assumption checking, power analysis
- `conversational_analysis` — Interactive statistical Q&A

#### Citation & Literature Tools (3 new tools)
- `literature_search` — Search 22+ academic sources (arXiv, PubMed, Semantic Scholar, CrossRef, OpenAlex, etc.)
- `citation_manager` — BibTeX management, APA/MLA/IEEE formatting
- `verify_citations` — DOI verification, retraction checking, citation accuracy

#### Writing Tools (5 new tools)
- `write_section` — AI-assisted academic section writing (IMRaD structure)
- `compile_paper` — LaTeX/Typst compilation to PDF
- `generate_table` — Academic tables with proper formatting
- `generate_diagram` — Research diagrams and flowcharts
- `convert_figure_tikz` — Convert figures to TikZ/PGFPlots

#### Quality Assurance Tools (6 new tools)
- `check_grammar` — Academic grammar and language checking
- `check_style` — Academic writing style analysis
- `check_readability` — Flesch-Kincaid, Gunning Fog, academic readability
- `simulate_peer_review` — Multi-reviewer simulation with structured feedback
- `detect_plagiarism` — Text similarity and originality checking
- `audit_reproducibility` — Reproducibility checklist and verification

#### Document & Knowledge Tools (10 new tools)
- `python_repl` — Sandboxed Python execution (local/Docker/E2B)
- `convert_document` — Universal file format conversion
- `parse_academic_pdf` — Scientific PDF parsing with metadata extraction
- `extract_references` — Reference extraction from any document
- `chunk_document` — Intelligent document chunking for RAG
- `embed_papers` — Paper embedding generation for semantic search
- `vector_search` — Semantic similarity search across papers
- `build_knowledge_graph` — Entity extraction and graph construction
- `query_knowledge_graph` — Graph traversal and relationship queries
- `paper_qa` — Question answering over paper corpus

#### MCP Ecosystem (13 servers)
- `bps` — 62 BPS Indonesia statistical data tools (enabled)
- `papers` — 22-source academic paper search (enabled)
- `pdf` — 46 PDF processing tools (enabled)
- `jupyter` — Real-time code execution (enabled)
- `markitdown` — Microsoft universal file converter (enabled)
- `memory` — Knowledge graph memory (enabled)
- `chroma` — ChromaDB vector search (enabled)
- `pubmed` — PubMed biomedical search (enabled)
- `rmcp` — R statistical computing, 52 tools (enabled)
- `zotero` — Citation management (disabled, needs API key)
- `overleaf` — LaTeX editor (disabled, needs credentials)
- `qdrant` — Vector search (disabled, needs server)
- `neo4j` — Knowledge graph (disabled, needs server)

#### Research Configuration
- `config/research_config.yaml` — Research-specific configuration
- `config/mcp-research.json` — Full MCP ecosystem configuration
- `config/system_prompt_research.md` — Research-mode system prompt
- `config/system_prompts/` — 5 sub-agent system prompts
- `skills/academic-research/` — Academic research skill with templates

### Changed
- **Version** bumped from 0.3.0 to **1.0.0**
- **Setup wizard** now deploys 13 MCP servers (was 1)
- **CLI** now loads 50+ tools (was 24)
- **Test suite** expanded to **471 tests** across 34 files (was 417)
- **Package description** updated to reflect academic research capabilities

### Fixed
- Module-level numpy imports causing crashes when optional deps not installed
- Sub-agent test coroutine warning (mock.add_user_message now sync)
- 220 lint errors resolved (unused imports, formatting, ambiguous variables)
- All tools now gracefully degrade when optional dependencies missing

## v0.2.0 — Production Infrastructure

### Added
- **Setup wizard** (`bpsagent setup`) — interactive configuration wizard for first-time users
- **`bpsagent` command** — primary CLI entry point (alias for bps-stat-agent)
- **Auto-redirect to setup** — running `bpsagent` without config auto-launches setup wizard
- **`platform.minimax.io`** added to recognized MiniMax API domains
- **Dockerfile** — Multi-stage build (builder + runtime) with Python 3.11, uv, Playwright chromium, non-root user
- **docker-compose.yml** — 3 services (CLI, MCP, ACP) with profiles, resource limits, tmpfs, env_file
- **.dockerignore** — Excludes secrets, dev artifacts, documentation
- **GitHub Actions CI** — Lint (ruff) → Test (pytest, Python 3.11/3.12) → Security (pip-audit) → Build pipeline
- **Docker build workflow** — Verifies Dockerfile builds on push to main
- **Makefile** — 20 targets for install, test, lint, format, build, docker, and run operations
- **Centralized JSON logging** (`mini_agent/logging_config.py`) — 12-factor structured logging to stdout, configurable JSON/human-readable format
- **Health check server** (`mini_agent/health.py`) — HTTP /health, /ready, /metrics endpoints for container orchestrators
- **Prometheus metrics** (`mini_agent/metrics.py`) — 10 application metrics (agent runs, LLM requests, tokens, tool calls) with graceful no-op fallback
- **OpenTelemetry tracing** (`mini_agent/tracing.py`) — Distributed tracing for agent runs, LLM calls, tool executions with graceful no-op fallback
- **.env support** — python-dotenv integration for environment variable loading from .env files
- **.env.example** — Template for required environment variables
- **ruff.toml** — Linter configuration (Python 3.11, line-length 120)
- **Optional dependency groups** — `metrics`, `tracing`, `observability` for production monitoring

### Changed
- **Default provider** changed from Anthropic to MiniMax (platform.minimax.io, MiniMax-M2.5, openai)
- **mcp-example.json** now uses `bps-mcp-server` directly instead of `uvx`
- **`enable_bash` default changed to `false`** — Bash tool disabled by default for security (enable explicitly in config.yaml)
- **Config** — Added `LoggingConfig` and `TracingConfig` sections
- **config-example.yaml** — Added logging and tracing configuration sections
- **agent.py** — Integrated Prometheus metrics and OpenTelemetry tracing into agent loop
- **cli.py** — Integrated centralized logging and tracing configuration
- **acp/__init__.py** — Integrated centralized logging and tracing configuration

### Fixed
- **test_search_generic_returns_paginated** — Updated test to match current `search_generic` return format
- **test_search_generic_uses_search_model** — Updated test to verify multi-model search behavior
- **test_bps_get_indicators** — Updated test to match current year-rejection behavior

### Security
- Bash command execution disabled by default (P0 security hardening)
- Non-root Docker user (`agent`)
- .env files excluded from git and Docker builds
- **Path traversal vulnerability fixed** — `str.startswith()` replaced with `Path.is_relative_to()` in ReadTool, WriteTool, EditTool
- **Error message truncation** — retry error messages truncated to 500 chars to prevent sensitive data leakage in logs
- **Bounded API client cache** — `bps_mcp_server` API cache limited to 8 entries with LRU eviction (prevents memory leak)
- **OpenAI finish_reason** — now reads actual `finish_reason` from API response (was hardcoded to `"stop"`)
- **tiktoken encoding cached** — module-level and Agent instance-level caching eliminates repeated disk I/O per step
- **BackgroundShellManager.reset()** — new classmethod for safe state cleanup between test runs
- **test_integration.py** — marked as `@pytest.mark.live` (requires API key, no longer fails in CI)
- **test_acp.py** — graceful skip when `agent-client-protocol` not installed
- **test_health.py** — fixed metrics endpoint test for Prometheus text format
- **.gitignore** — added coverage artifacts (`.coverage`, `coverage.json`, `coverage.lcov`, `*.py,cover`)

### Changed
- Test suite expanded from 379 to **417 tests** across **34 test files** (was 29)

## [v0.1.3] - 2026-04-27

### Added
- **BPS data retriever** with comprehensive statistics support (poverty, unemployment, HDI, life expectancy, GDP, population, inflation)
- **ANSI color module** (`colors.py`) for consistent terminal output styling
- **JSON-structured logger** for agent run tracing and debugging
- **Logo & branding** — project logo (`docs/assets/logo.png`), social preview banner, shields.io badges in README

### Changed
- MCP tools expanded from 55 to **62 registered tools**
- Test suite expanded from 290+ to **379 test functions** across 29 files
- Enhanced file tools with improved path traversal protection
- Enhanced note tool with better JSON persistence

### Fixed
- File tools edge cases for edit operations

### Security
- Fixed **18 Dependabot vulnerabilities** across all dependencies:
  - `mcp` ≥1.23.0 — DNS rebinding protection (HIGH)
  - `requests` ≥2.33.0 — insecure temp file reuse (MODERATE)
  - `pytest` ≥9.0.3 — vulnerable tmpdir handling (MODERATE)
  - `python-dotenv` ≥1.2.2 — symlink following in set_key (MODERATE)
  - `Pygments` ≥2.20.0 — ReDoS via GUID matching (LOW)
  - `urllib3` ≥2.6.3 — decompression bomb bypass (HIGH)
  - `python-multipart` ≥0.0.26 — arbitrary file write (HIGH)
  - `starlette` ≥0.49.0 — O(n²) DoS via Range header (HIGH)
  - `pip` — interpretation conflict with tar/ZIP files (MODERATE)

## [v0.1.2] - 2026-04-24

### Added
- **20 accuracy audit tests** covering ranking, retrieval, and LLM comprehension
- **MiniMax LLM + BPS integration tests** for end-to-end validation
- **bps-master skill** enhanced with complete tool documentation and domain codes

### Changed
- Improved BPS resolution classification accuracy

## [v0.1.1] - 2026-04-24

### Fixed
- **Complete rebrand** from `mini-agent` to `bps-stat-agent` across all files
- Config path updated from `mini-agent-bps` to `bps-stat-agent`
- Clone URL and README SEO improvements
- All remaining `mini-agent` references replaced with `bps-stat-agent`

## [v0.1.0] - 2026-04-24

### Added
- **55 MCP tools** for BPS WebAPI and AllStats Search Engine access
- **BPS AllStats Search** via Playwright - search 1.6M+ statistical data points
- **AllStats-First Fallback Pipeline** - search via AllStats, then retrieve via WebAPI
- **Multi-domain support** - national (0000) and provincial data (5300=NTT, etc.)
- **Rich content types** - publications, indicators, press releases, tables, infographics
- **Auto-retry mechanism** - fresh browser context on Cloudflare blocks
- **Full BPS WebAPI coverage** - domains, subjects, variables, periods, data retrieval
- **SIMDASI support** - regional statistics for kabupaten/kota
- **CSA (Custom Statistical Areas)** - specialized area statistics
- **KBLI/KBKI classifications** - industry and commodity classifications
- **Census data access** - SP2020 and census datasets
- **SDGs/SDDS indicators** - sustainable development goal indicators
- **Glossary and news** - BPS terminology and press releases
- **Foreign trade data** - export/import statistics via dataexim
- **Python API** - `AllStatsClient` for direct programmatic access
- **MCP server mode** - run as stdio MCP server for Claude Desktop
- **CLI mode** - interactive BPS data querying session

### Features
- Domain code validation and formatting
- Pagination handling for large datasets
- Region ID decoding for dynamic data
- Multi-language support (Indonesian/English)
- Configurable search delay to avoid rate limiting
- Playwright-based browser automation for AllStats

### Installation
- Single command install via `uv` or `pip`
- Setup script for automatic configuration
- Example config files included

### Documentation
- Complete API reference in SKILL.md
- Installation and usage guides
- BPS domain codes reference
- Content types documentation
- Common query examples
- Architecture overview

---

## [v0.0.0] - 2026-04-23

### Added
- Initial project setup
- Base BPS API client
- AllStats search engine integration
- MCP server infrastructure
