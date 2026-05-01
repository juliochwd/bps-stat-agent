<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# mini_agent — BPS Stat Agent v1.0.0

## Purpose

Core Python package for **BPS Stat Agent v1.0.0** — an LLM-powered tool-use agent specialized in querying and analyzing statistical data from BPS (Badan Pusat Statistik / Statistics Indonesia). The agent combines a multi-step agentic loop (LLM generation + tool execution) with 62 MCP tools for BPS data access, a full academic research pipeline, and 40+ built-in analysis/writing/quality tools.

Key capabilities:
- **Agent loop** with cancellation, token management (tiktoken cl100k_base), and automatic message summarization at 80K tokens
- **Interactive CLI** via prompt_toolkit with history, auto-suggest, Esc-to-cancel, and multi-line input
- **Non-interactive mode** (`--task`) for scripted execution
- **BPS data access** via AllStats search engine (Playwright headless Chromium) and WebAPI REST client (44+ endpoints)
- **Academic research** with 5-phase gating (PLAN -> COLLECT -> ANALYZE -> WRITE -> REVIEW)
- **ACP bridge** for Agent Client Protocol interoperability
- **Production observability**: Prometheus metrics, OpenTelemetry tracing, HTTP health checks

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package entry point. Exports `Agent`, `LLMClient`, schema types. `__version__ = "1.0.0"`. Lazy-imports `ResearchOrchestrator` via `get_research_orchestrator()`. |
| `agent.py` | **Core agent loop.** `Agent` class with `run()` method: LLM call -> parse tool_calls -> execute tools -> append results -> repeat (max 50 steps). Supports cancellation via `asyncio.Event` checked at step boundaries and after each tool. Token estimation via tiktoken with char-based fallback. Auto-summarizes message history when tokens exceed `token_limit` (default 80K). All operations instrumented with Prometheus counters/histograms. |
| `cli.py` | **CLI entry point** (`bpsagent` command). Subcommands: `setup`, `log`, `research`. Interactive mode uses `PromptSession` with `FileHistory`, `AutoSuggestFromHistory`, `WordCompleter`, custom `KeyBindings` (Ctrl+U clear, Ctrl+J newline, Ctrl+L clear screen). Esc-to-cancel runs a background thread listening for escape key. Tool initialization in two phases: `initialize_base_tools()` (bash aux, skills, MCP) and `add_workspace_tools()` (bash, file, research, statistics, citation, writing, analysis, quality, sandbox, document, knowledge, notes). |
| `config.py` | **Configuration management.** Pydantic v2 models: `Config`, `LLMConfig`, `AgentConfig`, `ToolsConfig`, `MCPConfig`, `LoggingConfig`, `TracingConfig`, `ResearchConfig`, `RetryConfig`. Loads from YAML with `.env` override via `python-dotenv`. API key resolution: env vars (`MINIMAX_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `OPENAI_API_KEY`) override placeholder values. Priority search via `find_config_file()`: dev `./mini_agent/config/` -> user `~/.bps-stat-agent/config/` -> package install dir. |
| `health.py` | HTTP health check server for Docker/K8s. Endpoints: `/health` (liveness with uptime), `/ready` (readiness with optional callable check), `/metrics` (Prometheus text). Runs as daemon thread on port 8080. |
| `metrics.py` | Prometheus metrics with no-op `_NoOpMetric` fallback. Counters: `agent_runs_total` (by status), `agent_steps_total`, `llm_requests_total` (by provider/model/status), `llm_tokens_total` (by type), `llm_retries_total`, `tool_calls_total` (by name/status). Histograms: `agent_run_duration_seconds`, `llm_request_duration_seconds`, `tool_call_duration_seconds`. Gauge: `agent_active_runs`. Info: `bps_stat_agent` app info. |
| `tracing.py` | OpenTelemetry distributed tracing with no-op fallback. `configure_tracing()` supports console and OTLP (gRPC) exporters. Convenience context managers: `trace_span()`, `trace_agent_run()`, `trace_llm_call()`, `trace_tool_call()`. Env var overrides: `OTEL_EXPORTER`, `OTEL_EXPORTER_OTLP_ENDPOINT`. |
| `retry.py` | Async retry with exponential backoff. `RetryConfig` (enabled, max_retries=3, initial_delay=1.0s, max_delay=60s, exponential_base=2.0, retryable_exceptions). `@async_retry` decorator with `on_retry` callback. `RetryExhaustedError` carries `last_exception` and `attempts` count. |
| `setup_wizard.py` | Interactive first-run wizard (`bpsagent setup`). Prompts: AI API key (masked), API base URL, model name, provider (openai/anthropic), BPS API key. Writes `config.yaml` and `mcp.json` (with 13 MCP servers including BPS, papers, PDF, Jupyter, MarkItDown, memory, Zotero, Overleaf, Qdrant, Neo4j, ChromaDB, PubMed, R) to `~/.bps-stat-agent/config/`. Copies `system_prompt.md`. Auto-installs Playwright chromium. |
| `bps_mcp_server.py` | **FastMCP server** exposing 62 BPS tools via MCP protocol. Wraps `BPSAPI`, `BPSOrchestrator`, `BPSResourceRetriever`. Entry point: `bps-mcp-server` CLI command. Env vars: `BPS_API_KEY`, `BPS_DEFAULT_DOMAIN`, `BPS_SEARCH_DELAY`. |
| `bps_api.py` | **BPS WebAPI client** (`BPSAPI` class). 44+ methods covering all BPS REST endpoints: domains, subjects, variables, dynamic data (var+th), static tables, press releases, publications, SDGs, census events, SIMDASI provinces/indicators, infographics, glossary, strategic indicators, news, and more. Uses `requests` with `BPSAPIError` exception. Includes `BPSMaterial` for lazy PDF download. |
| `bps_orchestrator.py` | **AllStats-first query orchestration.** `BPSOrchestrator.answer_query()`: search -> rank by relevance score (title/snippet token matching + content-type bonuses) -> resolve resource type -> delegate to retriever. |
| `allstats_client.py` | **Playwright-based BPS search.** `AllStatsClient` drives headless Chromium against `searchengine.web.bps.go.id`. Returns `AllStatsSearchResponse` with paginated `AllStatsResult` items (title, url, snippet, content_type, domain, year). |
| `bps_models.py` | Shared data models. `BPSResourceType` enum: TABLE, PUBLICATION, PRESSRELEASE, NEWS, INFOGRAPHIC, GLOSSARY, SUBJECT_DATA, UNKNOWN. `BPSResolvedResource` dataclass with `retrieval_candidates` list and `identifiers` dict. |
| `bps_normalization.py` | `build_normalized_response()` — canonical response payload with query, resource_type, domain, title, summary, period, rows, columns, metadata, artifacts, errors. |
| `bps_resolution.py` | `classify_search_result()` — maps AllStats results to `BPSResolvedResource` with typed retrieval candidate chains (e.g., TABLE -> static_table_detail -> webapi_structured -> search_result_only). |
| `bps_data_retriever.py` | Full data retrieval: search -> get table -> parse HTML to structured CSV/JSON. `BPSDataRetriever` class. |
| `bps_resource_retriever.py` | `BPSResourceRetriever` — dispatches retrieval by resource type (table, publication, press release) and normalizes via `build_normalized_response()`. |
| `colors.py` | ANSI terminal color constants. `Colors` class with RESET, BOLD, DIM, standard colors (RED-WHITE), bright colors (BRIGHT_RED-BRIGHT_WHITE). |
| `logger.py` | `AgentLogger` — per-run structured JSON logger. Writes to `~/.bps-stat-agent/log/`. Records LLM requests/responses, tool calls/results with timestamps. |
| `logging_config.py` | Centralized logging. `JSONFormatter` for structured production logs. `configure_logging(level, json_output, log_file)`. Suppresses noisy httpx/httpcore/urllib3/asyncio loggers. |

## Subdirectories

| Directory | Description |
|-----------|-------------|
| `llm/` | LLM client abstraction layer. Unified `LLMClient` wrapper routing to Anthropic, OpenAI, or LiteLLM provider clients. |
| `tools/` | Tool implementations (17 modules, 40+ tool classes). Base framework, file ops, bash (fg/bg), MCP loader, skills, statistics, analysis, citation, writing, quality, sandbox, documents, knowledge. |
| `config/` | Configuration files: `config.yaml`, `mcp.json`, system prompts, research config. Priority-searched at runtime. |
| `research/` | Academic research engine. Phase-gated workflow (PLAN->COLLECT->ANALYZE->WRITE->REVIEW), project state persistence, sub-agents, quality gates, DSPy modules, LaTeX compilation, writing pipeline. |
| `schema/` | Pydantic data models: `Message`, `LLMResponse`, `ToolCall`, `FunctionCall`, `LLMProvider`, `TokenUsage`. |
| `acp/` | Agent Client Protocol bridge. Exposes the agent as an ACP-compatible stdio server for external orchestration. |
| `skills/` | Claude Skills directory. 13 skill packages for progressive disclosure (academic-research, bps-master, document-skills, etc.). |
| `utils/` | Utility modules. Terminal display width calculation with ANSI/emoji/CJK support. |

## For AI Agents

### Working In This Directory

- **Entry points**: `cli.py:main()` is the primary CLI entry (`bpsagent`). `bps_mcp_server.py` is the MCP server entry (`bps-mcp-server`). `acp/server.py` is the ACP entry (`bps-stat-agent-acp`).
- **Configuration**: Always use `Config.from_yaml()` or `Config.load()`. Never hardcode paths — use `Config.find_config_file()` for priority search (dev -> user -> package).
- **Tool registration**: Tools are registered in `cli.py:initialize_base_tools()` (MCP, skills) and `cli.py:add_workspace_tools()` (workspace-dependent). All tools extend `tools.base.Tool`.
- **Agent loop**: `Agent.run()` is the core loop. It checks cancellation at step boundaries, summarizes messages when tokens exceed limits, and instruments all operations with Prometheus metrics.
- **BPS data flow**: Query -> `AllStatsClient.search()` -> `BPSOrchestrator.answer_query()` -> `classify_search_result()` -> `BPSResourceRetriever.retrieve()` -> `build_normalized_response()`.
- **BPS modules**: All `bps_*.py` files are self-contained BPS data access modules. Do not mix with agent/tool logic.

### Architecture
```
User Input (CLI / MCP / ACP)
  |
Agent.run() loop (agent.py)
  |-- LLM call via LLMClient (llm/)
  |-- Parse tool_calls from response
  |-- Execute tools (tools/)
  |-- Append results to message history
  |-- Token check -> summarize if > 80K
  +-- Repeat until no tool_calls or max_steps
```

### Testing Requirements

- Unit tests should mock LLM responses (`LLMResponse`) and tool execution (`ToolResult`)
- BPS API tests require a valid `BPS_API_KEY` or should use recorded fixtures
- Playwright tests require chromium (`python -m playwright install chromium`)
- Use `pytest-asyncio` for all async test functions
- Config tests should use temporary directories to avoid polluting `~/.bps-stat-agent/`
- Metrics/tracing tests should verify no-op behavior when optional deps are missing

### Common Patterns

- **Graceful degradation**: All optional dependencies (prometheus_client, opentelemetry, research extras) use try/except with no-op fallbacks
- **Lazy imports**: Research module, statistics tools, and other heavy dependencies are lazy-imported to keep base install lightweight
- **Pydantic v2 models**: All configuration and schema types use Pydantic v2 `BaseModel`
- **Async-first**: Agent loop, LLM clients, tool execution, and MCP communication are all async
- **Token management**: `Agent._estimate_tokens()` uses tiktoken (cl100k_base) with char-based fallback (2.5 chars/token)
- **Retry pattern**: `RetryConfig` + `@async_retry` decorator with exponential backoff and callback

## Dependencies

### Internal
- `mini_agent.llm` — LLM client abstraction
- `mini_agent.tools` — tool implementations
- `mini_agent.schema` — shared data models
- `mini_agent.config/` — config templates

### External (Core)
- `anthropic` (>=0.39.0) — Anthropic Messages API
- `openai` (>=1.57.4) — OpenAI Chat Completions API
- `pydantic` (>=2.0) — data validation
- `pyyaml` — YAML config parsing
- `python-dotenv` — .env file loading
- `tiktoken` — token counting
- `requests` — HTTP client (BPS API)
- `prompt-toolkit` — interactive CLI
- `mcp` (>=1.23.0) — Model Context Protocol
- `playwright` — headless browser (BPS AllStats search)

### External (Optional)
- `prometheus_client` — Prometheus metrics
- `opentelemetry-sdk`, `opentelemetry-exporter-otlp` — distributed tracing
- `litellm` — multi-provider LLM routing (research extras)
- `numpy`, `pandas`, `scipy`, `matplotlib` — statistics/analysis (research extras)
- `dspy-ai` — optimizable research pipelines (research extras)
