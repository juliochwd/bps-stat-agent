# AGENTS.md — BPS Stat Agent (Root)

> **Parent:** None (project root)
> **Updated:** 2026-05-01
> **Package:** `bps-stat-agent` v1.0.0
> **License:** MIT
> **Author:** Julio Christian Wadu Doko <juliochwd@gmail.com>

## Project Overview

BPS Stat Agent is an AI Agent for accessing BPS (Badan Pusat Statistik / Statistics Indonesia) data and conducting academic research. It combines **62+ MCP tools** for querying 1.6M+ statistical data points across all BPS domains with a **phase-gated academic research pipeline** (PLAN -> COLLECT -> ANALYZE -> WRITE -> REVIEW).

The agent supports multiple LLM providers (Anthropic, OpenAI, MiniMax, LiteLLM), runs as a CLI, MCP server, or ACP server, and includes 14 Claude Skills for document generation, data analysis, and more.

### Core Capabilities

- **BPS Data Access:** AllStats search engine + WebAPI fallback pipeline across national (0000) and provincial domains (e.g., 5300=NTT)
- **Academic Research:** 5-phase pipeline with 22+ academic sources (arXiv, PubMed, Semantic Scholar, CrossRef, OpenAlex)
- **Statistical Analysis:** Descriptive stats, regression, hypothesis testing, time series, Bayesian inference, causal inference
- **Paper Writing:** LaTeX compilation, section writing, tables, diagrams, TikZ figures
- **Quality Assurance:** Grammar, style, readability, peer review simulation, plagiarism detection
- **Knowledge Management:** Document processing, embeddings, knowledge graphs, vector search
- **Python Sandbox:** Isolated code execution (local/Docker/E2B)
- **13 MCP Servers:** Papers, PDF, Jupyter, MarkItDown, ChromaDB, PubMed, R, Memory + BPS
- **Test Suite:** 2608 tests across 102 test files, 81% code coverage

## Key Files

| File | Purpose |
|---|---|
| `pyproject.toml` | Package metadata, all dependencies (core + 14 optional extras), entry points (`bpsagent`, `bps-mcp-server`, `bps-stat-agent-acp`), pytest config (`asyncio_mode = "auto"`, `testpaths = ["tests"]`), ruff/pylint settings. Build system: setuptools >=61.0. Python >=3.10. |
| `uv.lock` | Locked dependency versions for reproducible installs via `uv sync --frozen`. |
| `Makefile` | Build automation with `uv`. Targets: `install`, `install-dev`, `setup`, `lint`, `format`, `check`, `test`, `test-cov`, `test-live`, `test-all`, `build`, `clean`, `docker-build`, `docker-up`, `docker-down`, `docker-logs`, `run`, `run-mcp`, `run-acp`, `run-task`. |
| `Dockerfile` | Multi-stage build (builder -> runtime). Python 3.11-slim base, uv-based dependency install, Playwright Chromium browser, non-root `agent` user, healthcheck via `python -c "import mini_agent"`. |
| `Dockerfile.research` | Extended image layered on top of base with research extras (numpy, scipy, statsmodels, sklearn, matplotlib). |
| `docker-compose.yml` | Three service profiles: `cli` (interactive TTY), `mcp` (MCP server, restart: unless-stopped), `acp` (ACP server, restart: unless-stopped). All services: 2 CPU / 2GB RAM limits, 0.5 CPU / 512MB reservations, 1GB tmpfs, shared volumes for config/workspace/logs. |
| `install.sh` | One-click installer for Linux/macOS. 6-step process: check Python 3.10+, install uv, clone repo, install deps, install Playwright Chromium, run setup wizard. Usage: `curl -fsSL .../install.sh \| bash`. |
| `install.ps1` | One-click installer for Windows (PowerShell). Same workflow as install.sh. |
| `ruff.toml` | Linter/formatter config. Target: py311, line-length: 120. Select rules: E (pycodestyle errors), F (pyflakes), W (warnings), I (isort), UP (pyupgrade), B (bugbear), SIM (simplify). Per-file ignores for tests and skills. |
| `.env.example` | Environment variable template: `ANTHROPIC_AUTH_TOKEN`, `OPENAI_API_KEY`, `MINIMAX_API_KEY`, `BPS_API_KEY`, `BPS_DEFAULT_DOMAIN`, `BPS_SEARCH_DELAY`, `LOG_LEVEL`, `LOG_JSON_OUTPUT`. |
| `CHANGELOG.md` | Release history and version notes. |
| `CONTRIBUTING.md` | Contribution guidelines, PR process, code style requirements. |
| `CODE_OF_CONDUCT.md` | Community code of conduct. |
| `MANIFEST.in` | Source distribution includes for non-Python files (skills, config). |
| `.gitignore` | Standard Python + workspace + coverage + .env ignores. |
| `.dockerignore` | Excludes .git, .venv, __pycache__, workspace, tests, docs from Docker build context. |
| `.gitmodules` | Git submodule references. |

## Entry Points

Defined in `pyproject.toml` under `[project.scripts]`:

| Command | Module | Purpose |
|---|---|---|
| `bpsagent` | `mini_agent.cli:main` | Interactive CLI agent (primary entry point). Also aliased as `bps-stat-agent`. Supports `--task "..."` for single-task mode and `setup` subcommand for configuration wizard. |
| `bps-mcp-server` | `mini_agent.bps_mcp_server:main` | MCP server exposing 62 BPS tools over STDIO transport via FastMCP. Designed for integration with Claude Desktop, Cursor, and other MCP-compatible clients. |
| `bps-stat-agent-acp` | `mini_agent.acp.server:main` | ACP (Agent Client Protocol) server for agent-to-agent communication over STDIO. |

## Subdirectories

| Directory | Purpose |
|---|---|
| `mini_agent/` | Main Python package. Contains agent core (`agent.py`), BPS API clients (`bps_api.py`, `allstats_client.py`), CLI (`cli.py`), config loader (`config.py`), MCP server (`bps_mcp_server.py`), and supporting modules (colors, health, logger, logging_config, metrics, retry, setup_wizard, tracing). |
| `mini_agent/acp/` | ACP server implementation. `server.py` bridges the agent to the Agent Client Protocol for agent-to-agent communication. |
| `mini_agent/config/` | Configuration files searched in 3-tier priority order. Contains `config.yaml`, `config-example.yaml`, `mcp.json`, `mcp-research.json`, `research_config.yaml`, `system_prompt.md`, `system_prompt_research.md`, and `system_prompts/` subdirectory. |
| `mini_agent/llm/` | LLM client implementations. `base.py` defines `LLMClientBase` abstract class. Concrete clients: `anthropic_client.py`, `openai_client.py` (also handles MiniMax via OpenAI-compatible API), `litellm_client.py`. `llm_wrapper.py` provides unified `LLMClient` with retry logic. |
| `mini_agent/research/` | Academic research pipeline. `orchestrator.py` manages the 5-phase workflow. `phase_manager.py` controls phase transitions. `approval_gates.py` enforces quality gates between phases. `project_state.py` persists research state. `sub_agents.py` delegates specialized tasks. `llm_gateway.py` routes LLM calls. `session_resume.py` enables session persistence. Subpackages: `models/` (Pydantic models), `quality/` (quality checks), `writing/` (paper generation), `dspy_modules/` (DSPy integration). |
| `mini_agent/schema/` | Pydantic v2 data models in `schema.py`: `Message`, `ToolCall`, `FunctionCall`, `LLMResponse`, `LLMProvider` enum. Re-exported via `__init__.py`. |
| `mini_agent/skills/` | 14 Claude Skills loaded on-demand via progressive disclosure. Each skill is a directory with manifest and prompt files. Skills: academic-research, algorithmic-art, artifacts-builder, bps-master, brand-guidelines, canvas-design, document-skills (docx/pdf/pptx/xlsx with OOXML schemas), internal-comms, mcp-builder, skill-creator, slack-gif-creator, template-skill, theme-factory, webapp-testing. |
| `mini_agent/tools/` | Tool implementations. `base.py` defines `Tool` abstract class with `name`, `description`, `parameters`, `execute()`. 18 tool modules: analysis_tools, bash_tool, citation_tools, config_tools, document_tools, file_tools, knowledge_tools, mcp_loader, note_tool, quality_tools, research_tools, sandbox_tools, skill_loader, skill_tool, statistics_tools, writing_tools. |
| `mini_agent/utils/` | Utility modules. `terminal_utils.py` provides terminal I/O helpers for the CLI. |
| `tests/` | Test suite: 102 test files, 2608 tests, 81% coverage. Unit, integration, and live tests. See `tests/AGENTS.md`. |
| `scripts/` | Development scripts: `_gen_tests.py` (test scaffold generator), `setup-config.sh` (Unix config setup), `setup-config.ps1` (Windows config setup). See `scripts/AGENTS.md`. |
| `docs/` | Documentation: `DEVELOPMENT_GUIDE.md`, `PRODUCTION_GUIDE.md`, `assets/` (logo, demo GIFs, social preview), `superpowers/` (specs and implementation plans). See `docs/AGENTS.md`. |
| `examples/` | 6 progressive tutorial examples from basic tool usage to full agent with provider selection. See `examples/AGENTS.md`. |
| `.github/workflows/` | CI/CD: `ci.yml` (lint + test pipeline), `docker.yml` (Docker image build and push). |
| `bps-master-workspace/` | BPS master data workspace — reference data for BPS domain codes, subjects, skill evaluation baselines. |
| `bps-webapidoc/` | BPS WebAPI documentation reference and API test results. |
| `dist/` | Built distribution artifacts (sdist + wheel) from `make build`. |
| `workspace/` | Runtime workspace for agent output, logs, temporary files, and pytest cache (`workspace/.pytest_cache`). |
| `plan/` | Development planning documents (excluded from package via `pyproject.toml`). |
| `futureupdate/` | Future feature planning and roadmap items. |

## Architecture Overview

```
User Query
    |
    v
+---------------------+
|   CLI (cli.py)      |  <-- bpsagent / bps-stat-agent
|   setup_wizard.py   |      bpsagent setup
+---------------------+
    |
    v
+---------------------+     +-------------------------+
|   Agent             |---->|  LLM Client (llm/)      |
|   (agent.py)        |     |  - AnthropicClient      |
|   - tool-use loop   |     |  - OpenAIClient         |
|   - token mgmt      |     |    (MiniMax-compatible)  |
|   - cancellation     |     |  - LiteLLMClient        |
|   - 80K summarize   |     |  - LLMWrapper (retry)   |
+---------------------+     +-------------------------+
    |
    v
+---------------------+
|   Tool Registry     |
|   (tools/)          |
+---------------------+
    |
    +---> BPS Tools
    |     - bps_api.py (WebAPI client)
    |     - allstats_client.py (Playwright search, 1.6M+ data points)
    |     - bps_orchestrator.py (search-resolve-retrieve pipeline)
    |     - bps_resolution.py (URL -> typed resource)
    |     - bps_data_retriever.py (structured data fetch)
    |     - bps_normalization.py (domain/subject normalization)
    |     - bps_models.py (BPSResolvedResource, BPSResourceType)
    |
    +---> File Tools (read, write, edit via file_tools.py)
    +---> Bash Tool (shell execution via bash_tool.py)
    +---> Note Tool (session memory via note_tool.py)
    +---> Config Tools (runtime config via config_tools.py)
    |
    +---> Research Tools (requires research extras)
    |     - analysis_tools.py (statistical analysis)
    |     - statistics_tools.py (descriptive, regression, hypothesis)
    |     - citation_tools.py (APA formatting, DOI lookup)
    |     - document_tools.py (document processing, chunking)
    |     - knowledge_tools.py (embeddings, knowledge graphs, RAG)
    |     - quality_tools.py (grammar, style, readability)
    |     - writing_tools.py (LaTeX, DOCX, section generation)
    |     - sandbox_tools.py (isolated Python execution)
    |     - research_tools.py (literature search, 22+ sources)
    |
    +---> MCP Loader (mcp_loader.py — loads external MCP server tools)
    +---> Skill Loader (skill_loader.py — 14 Claude Skills, progressive disclosure)
    |
    v
+---------------------+     +---------------------+
| BPS MCP Server      |     | ACP Server          |
| (bps_mcp_server.py) |     | (acp/server.py)     |
| 62 tools / STDIO    |     | Agent-to-agent      |
| FastMCP framework   |     | STDIO transport     |
+---------------------+     +---------------------+
```

### BPS Data Pipeline

1. **AllStats Search** — `allstats_client.py` uses Playwright to scrape BPS AllStats search engine (1.6M+ data points). Auto-retry with fresh browser context on Cloudflare blocks.
2. **Resource Resolution** — `bps_resolution.py` parses search result URLs into typed `BPSResolvedResource` objects (table, publication, indicator, press release, infographic).
3. **WebAPI Retrieval** — `bps_data_retriever.py` and `bps_api.py` fetch structured data via BPS WebAPI using resolved resource IDs and domain codes.
4. **Normalization** — `bps_normalization.py` normalizes domain codes, subject mappings, and data formats for consistent output.
5. **Orchestration** — `bps_orchestrator.py` coordinates the full AllStats-first fallback pipeline: search via AllStats, then retrieve structured detail through WebAPI.

### Research Pipeline

5-phase gated workflow managed by `research/orchestrator.py`:

| Phase | Purpose | Key Tools |
|---|---|---|
| **PLAN** | Define research questions, methodology, data requirements | research_tools |
| **COLLECT** | Literature search (22+ sources), data collection, document processing | citation_tools, document_tools, knowledge_tools |
| **ANALYZE** | Statistical analysis, hypothesis testing, visualization | analysis_tools, statistics_tools, sandbox_tools |
| **WRITE** | Paper writing (LaTeX/DOCX), section generation, citation management | writing_tools, citation_tools |
| **REVIEW** | Quality assurance, grammar check, peer review simulation | quality_tools |

Each phase has approval gates (`approval_gates.py`) and quality thresholds defined in `research/quality/`. Phase transitions are managed by `phase_manager.py`. Maximum 15 tools available per phase (`research/constants.py`). Research state persists via `project_state.py` and sessions can be resumed via `session_resume.py`.

## Configuration System

Configuration files are searched in priority order (first found wins):

1. **Development:** `mini_agent/config/config.yaml` (in-tree, for local development)
2. **User:** `~/.bps-stat-agent/config/config.yaml` (user home directory)
3. **Package:** `<site-packages>/mini_agent/config/config.yaml` (installed package fallback)

All related config files live in the same directory as `config.yaml`:

| File | Purpose |
|---|---|
| `config.yaml` | Main config: LLM provider/model/API key, retry settings (max 3, exponential backoff), agent behavior, BPS domain defaults. |
| `config-example.yaml` | Annotated template with all available options and provider examples (Anthropic, OpenAI, MiniMax Global/China). |
| `mcp.json` | MCP server definitions for external tool servers loaded by `mcp_loader.py`. |
| `mcp-research.json` | Extended MCP config with research-specific servers (Papers, Jupyter, ChromaDB, PubMed, R, Memory). |
| `system_prompt.md` | Default system prompt for the BPS data agent mode. |
| `system_prompt_research.md` | System prompt for academic research mode. |
| `research_config.yaml` | Research pipeline configuration: phase definitions, quality gate thresholds, tool limits per phase. |

### Environment Variables

| Variable | Purpose | Required |
|---|---|---|
| `ANTHROPIC_AUTH_TOKEN` | Anthropic API key | One LLM key required |
| `OPENAI_API_KEY` | OpenAI API key (also used for MiniMax via OpenAI-compatible API) | One LLM key required |
| `MINIMAX_API_KEY` | MiniMax API key | One LLM key required |
| `BPS_API_KEY` | BPS WebAPI key for structured data access | For BPS data features |
| `BPS_DEFAULT_DOMAIN` | Default BPS domain code (e.g., `5300` for NTT) | Optional |
| `BPS_SEARCH_DELAY` | Delay between AllStats searches in seconds (default: 10) | Optional |
| `LOG_LEVEL` | Logging level (default: INFO) | Optional |
| `LOG_JSON_OUTPUT` | Enable JSON-structured logging (default: false) | Optional |

## Build, Test, and Run

### Installation

```bash
# Option 1: uv (recommended)
uv tool install git+https://github.com/juliochwd/bps-stat-agent.git

# Option 2: pip
pip install git+https://github.com/juliochwd/bps-stat-agent.git

# Option 3: With research extras
pip install 'bps-stat-agent[research-all]'

# Option 4: One-click installer (Linux/macOS)
curl -fsSL https://raw.githubusercontent.com/juliochwd/bps-stat-agent/main/install.sh | bash

# Post-install: run setup wizard
bpsagent setup
```

### Development Setup

```bash
make setup          # Full first-time setup: install-dev + Playwright + seed config
make install-dev    # Install all deps including dev group + Playwright chromium
make install        # Install production deps only (frozen lockfile)
```

### Running

```bash
# Via Makefile
make run                              # Interactive CLI agent
make run-mcp                          # Start MCP server (STDIO)
make run-acp                          # Start ACP server
make run-task TASK="Cari data IPM NTT 2023"  # Single task mode

# Direct commands
bpsagent                              # Interactive CLI
bpsagent --task "inflasi NTT terbaru" # Single task mode
bpsagent setup                        # Configuration wizard
bps-mcp-server                        # MCP server (62 BPS tools)
bps-stat-agent-acp                    # ACP server
```

### Testing

```bash
# Via Makefile
make test           # Unit tests only (excludes @pytest.mark.live)
make test-cov       # Tests with coverage report (HTML + terminal)
make test-live      # Live BPS integration tests only (requires network + API keys)
make test-all       # All tests (unit + live)

# Direct pytest
uv run pytest tests/ -x -v -m "not live"           # Unit tests
uv run pytest tests/ --run-live -m live             # Live tests with --run-live flag
uv run pytest tests/ --cov=mini_agent --cov-report=term-missing  # Coverage
uv run pytest tests/test_agent.py -v                # Specific file
uv run pytest tests/ -k "bps" -v                    # Pattern match
```

### Code Quality

```bash
make lint           # Run ruff linter on mini_agent/ and tests/
make format         # Auto-format code with ruff
make check          # lint + test combined (quality gate for CI)
```

### Docker

```bash
make docker-build   # Build images via docker compose
make docker-up      # Start MCP profile in background
make docker-down    # Stop and remove all containers
make docker-logs    # Tail logs from all services

# Individual profiles
docker compose --profile cli up -d    # Interactive CLI container
docker compose --profile mcp up -d    # MCP server container
docker compose --profile acp up -d    # ACP server container
```

### Building Distribution

```bash
make build          # Build sdist + wheel into dist/
make clean          # Remove build artifacts, __pycache__, .pytest_cache, coverage files
```

## Optional Dependency Groups

Defined in `pyproject.toml` under `[project.optional-dependencies]`:

| Extra | Key Packages | Purpose |
|---|---|---|
| `dev` | pytest >=9.0.3, pytest-asyncio >=1.2.0 | Development and testing |
| `metrics` | prometheus-client >=0.20.0 | Prometheus metrics endpoint |
| `tracing` | opentelemetry-api/sdk/exporter-otlp >=1.20.0 | Distributed tracing |
| `observability` | metrics + tracing combined | Full observability stack |
| `research-core` | statsmodels, scipy, scikit-learn, matplotlib, seaborn, networkx, bibtexparser | Core statistical analysis and visualization |
| `research-analysis` | research-core + linearmodels, arch, pingouin | Advanced econometrics and panel data |
| `research-advanced-stats` | research-analysis + pymc, bambi, arviz, dowhy, lifelines | Bayesian inference, causal inference, survival analysis |
| `research-document` | markitdown[all], chonkie | Document processing and text chunking |
| `research-rag` | sentence-transformers, lancedb, lightrag-hku | RAG pipeline with vector search |
| `research-writing` | pylatex, python-docx, bibtexparser, habanero, textstat, proselint | Paper writing and citation management |
| `research-quality` | language-tool-python, pandera | Grammar checking and data validation |
| `research-sandbox` | docker, RestrictedPython | Sandboxed Python code execution |
| `research-nlp` | spacy, scispacy | NLP processing for scientific text |
| `research-llm` | litellm, dspy | Multi-LLM routing and DSPy modules |
| `research-all` | All research extras combined | Full research capabilities |

Install extras: `pip install 'bps-stat-agent[research-all,observability]'`

## For AI Agents

### Working with This Codebase

1. **Public API:** `mini_agent/__init__.py` exports: `Agent`, `LLMClient`, `LLMProvider`, `Message`, `LLMResponse`, `ToolCall`, `FunctionCall`, `BPSResolvedResource`, `BPSResourceType`, `get_research_orchestrator()`.
2. **Agent core:** `mini_agent/agent.py` implements the main agent loop — LLM call -> tool selection -> tool execution -> message history update -> token summarization at 80K limit.
3. **Adding tools:** Subclass `mini_agent/tools/base.py:Tool`. Implement `name` (str), `description` (str), `parameters` (JSON Schema dict), and `execute()` method. Tools return `ToolResult(success=bool, content=str, error=str|None)`. Use explicit kwargs in `execute()` (NOT `**kwargs`). Register in `mini_agent/tools/__init__.py`.
4. **Adding LLM providers:** Subclass `mini_agent/llm/base.py:LLMClientBase`. Implement `chat()` method. Add to `mini_agent/llm/__init__.py`. The `LLMWrapper` in `llm_wrapper.py` adds retry logic automatically.
5. **BPS data flow:** Query enters via `bps_orchestrator.py` -> `allstats_client.py` (Playwright search) -> `bps_resolution.py` (parse URLs to typed resources) -> `bps_data_retriever.py` / `bps_api.py` (WebAPI fetch) -> `bps_normalization.py` (normalize output).
6. **Research mode:** Activated via CLI flag or config. Uses `research/orchestrator.py` which manages 5 phases, sub-agents, approval gates, and quality thresholds. Requires `research-*` extras.
7. **Configuration:** Always use `mini_agent/config.py` to load config. It handles the 3-tier priority search (dev -> user -> package) automatically. Never hardcode API keys.
8. **Testing:** Run `make test` before committing. Tests use `conftest.py` fixtures: `tmp_workspace` (isolated dir), `mock_bps_api` (mocked BPS client), `sample_search_result` (sample data), `tmp_memory_file` (note tool path). Mark network-dependent tests with `@pytest.mark.live`.
9. **Linting:** Run `make lint` or `uvx ruff check mini_agent/ tests/`. Line length is 120 chars. Target Python 3.11.
10. **Skills:** Each skill is a directory under `mini_agent/skills/` with manifest and prompt files. Loaded by `mini_agent/tools/skill_loader.py` via progressive disclosure — metadata injected at startup, full content loaded on-demand via `get_skill` tool.
11. **Package naming:** Published as `bps-stat-agent` on PyPI. Internal module is `mini_agent`. Always `import mini_agent`, never `import bps_stat_agent`.
12. **Async:** MCP server and ACP server are async. Tests use `pytest-asyncio` with `asyncio_mode = "auto"` (no `@pytest.mark.asyncio` decorator needed).

### Key Patterns

- **Pydantic v2 models** for all data structures (`schema/schema.py`, `bps_models.py`, `research/models/`)
- **Tool-use loop** in `agent.py`: LLM call -> parse tool calls -> execute tools -> append results -> repeat until done
- **Progressive disclosure** for skills: lightweight metadata at startup, full content loaded on-demand
- **Retry with exponential backoff** via `mini_agent/retry.py` (configurable: max_retries, initial_delay, max_delay, exponential_base)
- **Structured logging** via `mini_agent/logging_config.py` with optional JSON output
- **Prometheus metrics** via `mini_agent/metrics.py` (optional, requires `metrics` extra)
- **OpenTelemetry tracing** via `mini_agent/tracing.py` (optional, requires `tracing` extra)
- **Health checks** via `mini_agent/health.py` (used in Docker HEALTHCHECK)
- **Token management** in agent loop: summarizes conversation at 80K token limit using tiktoken (cl100k_base)
- **Phase-gated tools** in research mode: max 15 tools per phase, controlled by `research/tool_registry.py`

### Common Tasks

| Task | Command |
|---|---|
| Run all unit tests | `make test` |
| Run with coverage | `make test-cov` |
| Run live BPS tests | `make test-live` |
| Format code | `make format` |
| Lint code | `make lint` |
| Quality gate (lint + test) | `make check` |
| Start interactive agent | `make run` |
| Start MCP server | `make run-mcp` |
| Start ACP server | `make run-acp` |
| Run single task | `make run-task TASK="query here"` |
| Build package | `make build` |
| Clean artifacts | `make clean` |
| Docker build + run | `make docker-build && make docker-up` |
| Full setup from scratch | `make setup` |

### Dependencies (Internal)

- `mini_agent.agent.Agent` — core agent loop with tool-use, token management, and cancellation
- `mini_agent.llm.LLMClient` — unified LLM wrapper with retry (wraps Anthropic/OpenAI/LiteLLM)
- `mini_agent.config.Config` — YAML configuration loader with 3-tier priority search
- `mini_agent.schema` — shared Pydantic models (Message, ToolCall, FunctionCall, LLMResponse, LLMProvider)
- `mini_agent.tools` — all 18 tool modules with `Tool` base class
- `mini_agent.research` — academic research orchestration (optional, requires research extras)
- `mini_agent.bps_*` — BPS data access layer (API, AllStats, orchestrator, resolution, retrieval, normalization)

### Dependencies (External)

- `anthropic` / `openai` — LLM API clients
- `mcp` (>=1.23.0) — Model Context Protocol client and server framework
- `agent-client-protocol` (>=0.6.0) — ACP bridge for agent-to-agent communication
- `pydantic` (>=2.0) — data validation and serialization
- `tiktoken` (>=0.5.0) — token counting (cl100k_base encoding)
- `prompt-toolkit` (>=3.0.0) — interactive CLI with history and completion
- `playwright` (>=1.40.0) — browser automation for AllStats search
- `pyyaml` (>=6.0.0) / `python-dotenv` — config loading
- `requests` (>=2.33.0) — HTTP client for BPS WebAPI
- Optional: `litellm`, `dspy`, `statsmodels`, `scipy`, `matplotlib`, `pylatex`, `bibtexparser`, `prometheus-client`, `opentelemetry-*` (see extras above)
