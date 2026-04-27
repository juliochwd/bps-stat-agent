# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## v0.2.0 — Production Infrastructure

### Added
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
