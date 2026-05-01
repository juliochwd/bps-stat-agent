<!-- Parent: ../AGENTS.md -->
# AGENTS.md — tests/

> **Parent:** [../AGENTS.md](../AGENTS.md)
> **Updated:** 2026-05-01
> **Test Count:** 2608 tests across 102 test files
> **Coverage:** 81% line coverage

## Purpose

Comprehensive pytest test suite for the BPS Stat Agent. Contains unit tests, integration tests, coverage-boost tests, and live BPS API smoke tests. Uses `pytest-asyncio` with `asyncio_mode = "auto"` for seamless async test support.

## Test Organization

Tests are organized by module and coverage depth:

### Core Agent & CLI Tests

| File | Description |
|---|---|
| `test_agent.py` | Core `Agent` class: tool-use loop, cancellation, token management, message history |
| `test_agent_coverage.py` | Extended agent coverage: edge cases, error paths, configuration variants |
| `test_cli_module.py` | CLI module imports and basic structure |
| `test_cli_comprehensive.py` | CLI argument parsing, subcommands, interactive mode |
| `test_cli_coverage.py` | CLI edge cases and error handling paths |
| `test_cli_full.py` | Full CLI integration: setup wizard, task mode, provider selection |
| `test_setup_wizard.py` | Setup wizard flow: API key prompts, config file creation, Playwright install |
| `test_terminal_utils.py` | Terminal utility functions: color output, progress display |

### LLM Client Tests

| File | Description |
|---|---|
| `test_llm.py` | LLM client unit tests: request/response formatting, token counting |
| `test_llm_clients.py` | Provider-specific tests: Anthropic, OpenAI client implementations |
| `test_llm_clients_comprehensive.py` | Extended LLM tests: error handling, retry logic, streaming |
| `test_litellm_client.py` | LiteLLM client: multi-provider routing, model mapping |
| `test_llm_gateway.py` | Research LLM gateway: model selection, cost tracking |
| `test_llm_bps_integration.py` | LLM + BPS tool integration: end-to-end query processing |

### BPS Data Access Tests

| File | Description |
|---|---|
| `test_bps_api.py` | BPS WebAPI client: all 62 API endpoints, pagination, error handling (largest test file: 84KB) |
| `test_bps_accuracy_audit.py` | BPS data accuracy validation: domain codes, subject mappings, data formats |
| `test_bps_normalization.py` | Domain code and subject normalization |
| `test_bps_resolution.py` | URL-to-resource resolution: table, publication, indicator, press release, infographic |
| `test_bps_resource_retriever.py` | Resource retrieval via WebAPI |
| `test_bps_data_retriever_coverage.py` | Data retriever edge cases and error paths |
| `test_bps_orchestrator.py` | Orchestrator pipeline: search -> resolve -> retrieve |
| `test_bps_parser.py` | BPS data parsing: HTML tables, JSON responses |
| `test_bps_live_smoke.py` | **Live tests** (`@pytest.mark.live`): real BPS API calls, requires network + API key |
| `test_allstats_client.py` | AllStats search client: Playwright-based scraping |
| `test_allstats_client_coverage.py` | AllStats edge cases: Cloudflare blocks, retry logic |
| `test_allstats_comprehensive.py` | AllStats comprehensive: multi-domain search, result parsing |

### BPS MCP Server Tests

| File | Description |
|---|---|
| `test_bps_mcp_server.py` | MCP server tool registration and STDIO transport |
| `test_bps_mcp_handlers.py` | MCP request handlers: all 62 tool handlers |
| `test_bps_mcp_extended.py` | MCP server edge cases and error responses |
| `test_bps_mcp_full.py` | Full MCP server integration tests |
| `test_mcp.py` | MCP tool loading from external servers |
| `test_mcp_loader_comprehensive.py` | MCP loader: server discovery, tool schema parsing, error handling |

### Research Pipeline Tests

| File | Description |
|---|---|
| `test_research_project_state.py` | Research project state persistence and phase tracking |
| `test_research_workspace.py` | Workspace scaffolding: directory creation, file templates |
| `test_research_constants.py` | Research constants: phase order, quality thresholds, tool limits |
| `test_research_exceptions.py` | Research exception hierarchy and error messages |
| `test_research_quality.py` | Quality gate evaluation: grammar, style, readability scores |
| `test_research_quality_comprehensive.py` | Extended quality tests: peer review simulation, plagiarism detection |
| `test_research_writing.py` | Paper writing: LaTeX generation, section templates |
| `test_research_writing_comprehensive.py` | Extended writing: DOCX output, citation formatting, TikZ figures |
| `test_research_tools_full.py` | Research tools: literature search, data collection |
| `test_approval_gates.py` | Phase transition approval gates |
| `test_approval_gates_extended.py` | Extended approval gate scenarios |
| `test_phase_manager.py` | Phase manager: transitions, rollback, state validation |
| `test_orchestrator.py` | Research orchestrator: full pipeline coordination |
| `test_session_resume.py` | Session persistence and resume |
| `test_sub_agents.py` | Sub-agent delegation and coordination |
| `test_cost_tracker.py` | LLM cost tracking and budget enforcement |
| `test_decision_log.py` | Decision log audit trail |
| `test_tool_registry.py` | Phase-aware tool registry: tool availability per phase |
| `test_dspy_compat.py` | DSPy compatibility layer |
| `test_dspy_modules_coverage.py` | DSPy module implementations |

### Tool Tests

| File | Description |
|---|---|
| `test_bash_tool.py` | BashTool: execution, timeout, kill, working directory |
| `test_file_tools.py` | File tools: read, write, edit operations |
| `test_note_tool.py` | SessionNoteTool / RecallNoteTool: persistent memory |
| `test_edit_file_fix.py` | Edit file edge cases and fix verification |
| `test_config_bps.py` | Configuration loading and validation |
| `test_config_extended.py` | Extended config: priority search, env var overrides |
| `test_config_tools.py` | Runtime config tools |
| `test_skill_loader.py` | Skill discovery and loading from skills/ directory |
| `test_skill_tool.py` | GetSkillTool: progressive disclosure, on-demand loading |
| `test_sandbox_tools.py` | Sandboxed Python execution: local, Docker, RestrictedPython |
| `test_sandbox_tools_coverage.py` | Sandbox edge cases and security boundaries |

### Analysis & Statistics Tool Tests

| File | Description |
|---|---|
| `test_analysis_tools_comprehensive.py` | Analysis tools: data processing, visualization |
| `test_analysis_tools_extended.py` | Extended analysis: edge cases, large datasets |
| `test_analysis_tools_full.py` | Full analysis tool coverage |
| `test_analysis_tools_mocked.py` | Analysis with mocked dependencies (no scipy/numpy required) |
| `test_analysis_deep.py` | Deep analysis tests: complex statistical operations (63KB) |
| `test_statistics_tools_comprehensive.py` | Statistics tools: descriptive, regression, hypothesis testing |
| `test_statistics_tools_extended.py` | Extended statistics: time series, panel data |
| `test_statistics_tools_full.py` | Full statistics tool coverage |
| `test_statistics_tools_mocked.py` | Statistics with mocked dependencies |
| `test_statistics_tools_with_data.py` | Statistics with real sample data |
| `test_statistics_deep.py` | Deep statistics tests: Bayesian, causal inference (50KB) |

### Citation, Document, Knowledge, Quality, Writing Tool Tests

| File | Description |
|---|---|
| `test_citation_tools_extended.py` | Citation tools: APA formatting, DOI lookup |
| `test_citation_tools_full.py` | Full citation tool coverage |
| `test_apa_formatter.py` | APA formatter: author names, dates, titles, DOIs |
| `test_document_tools_comprehensive.py` | Document tools: processing, chunking, conversion |
| `test_document_tools_coverage.py` | Document tool edge cases |
| `test_document_tools_extended.py` | Extended document processing |
| `test_knowledge_tools_comprehensive.py` | Knowledge tools: embeddings, graphs, vector search |
| `test_knowledge_tools_coverage.py` | Knowledge tool edge cases |
| `test_knowledge_tools_extended.py` | Extended knowledge management |
| `test_knowledge_tools_full.py` | Full knowledge tool coverage |
| `test_quality_tools_comprehensive.py` | Quality tools: grammar, style, readability |
| `test_quality_tools_extended.py` | Extended quality checks |
| `test_writing_tools_comprehensive.py` | Writing tools: LaTeX, DOCX, sections |
| `test_writing_tools_extended.py` | Extended writing tool tests |

### Infrastructure Tests

| File | Description |
|---|---|
| `test_health.py` | Health check endpoint |
| `test_health_extended.py` | Extended health: dependency checks, degraded states |
| `test_metrics.py` | Prometheus metrics: counters, histograms, gauges |
| `test_metrics_extended.py` | Extended metrics scenarios |
| `test_tracing.py` | OpenTelemetry tracing: spans, context propagation |
| `test_tracing_comprehensive.py` | Extended tracing: exporters, sampling |
| `test_logger.py` | Logger configuration and output |
| `test_logging_config.py` | Structured logging: JSON output, log levels |
| `test_retry_extended.py` | Retry logic: exponential backoff, max retries, jitter |
| `test_acp.py` | ACP server protocol: STDIO transport, message handling |

### Coverage Boost Tests

| File | Description |
|---|---|
| `test_coverage_boost.py` | Targeted tests to increase coverage on under-tested modules |
| `test_coverage_final_push.py` | Final coverage push: remaining uncovered lines |
| `test_coverage_max_push.py` | Maximum coverage push: comprehensive edge cases (85KB) |
| `test_coverage_max_push2.py` | Additional coverage: remaining gaps (29KB) |

## Key Files

| File | Purpose |
|---|---|
| `conftest.py` | Shared pytest fixtures and configuration hooks |
| `__init__.py` | Package marker (empty) |

### conftest.py Fixtures

| Fixture | Type | Purpose |
|---|---|---|
| `tmp_workspace` | `function` | Creates a temporary `workspace/` directory via `tmp_path`. Isolated per test. |
| `tmp_memory_file` | `function` | Returns a temporary file path for note tool memory (`.agent_memory.json`). |
| `mock_bps_api` | `function` | Returns a `MagicMock` BPS API client with pre-configured responses: domains (Indonesia, NTT), provinces, subjects (Kependudukan, Tenaga Kerja), static tables (Inflasi NTT), and table detail. |
| `sample_search_result` | `function` | Returns a sample AllStats search result dict with title, URL, snippet, content_type, domain info, and year. |

### conftest.py Hooks

| Hook | Purpose |
|---|---|
| `pytest_addoption` | Adds `--run-live` CLI flag to pytest |
| `pytest_collection_modifyitems` | Auto-skips tests marked `@pytest.mark.live` unless `--run-live` is passed |

## How to Run Tests

### Quick Commands

```bash
# All unit tests (excludes live/network tests)
make test
# Equivalent: uv run pytest tests/ -x -v -m "not live"

# With coverage report (HTML + terminal)
make test-cov
# Equivalent: uv run pytest tests/ --cov=mini_agent --cov-report=term-missing --cov-report=html -m "not live"

# Live BPS integration tests only (requires network + BPS_API_KEY)
make test-live
# Equivalent: uv run pytest tests/ -x -v -m live

# All tests (unit + live)
make test-all
# Equivalent: uv run pytest tests/ -x -v
```

### Running Specific Tests

```bash
# Single file
uv run pytest tests/test_agent.py -v

# Pattern match
uv run pytest tests/ -k "bps" -v              # All BPS-related tests
uv run pytest tests/ -k "research" -v          # All research tests
uv run pytest tests/ -k "statistics" -v        # All statistics tests
uv run pytest tests/ -k "mcp" -v               # All MCP tests
uv run pytest tests/ -k "cli" -v               # All CLI tests

# Single test function
uv run pytest tests/test_agent.py::TestAgent::test_tool_use_loop -v

# Live smoke tests (requires --run-live flag)
uv run pytest tests/test_bps_live_smoke.py --run-live -v
```

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist from dev group)
uv run pytest tests/ -x -v -m "not live" -n auto
```

## Coverage Information

- **Total tests:** 2608
- **Line coverage:** 81%
- **Coverage data:** `coverage.json` (538KB) and `.coverage` (78KB) in project root
- **HTML report:** Generated by `make test-cov` into `htmlcov/`
- **pytest cache:** `workspace/.pytest_cache` (not project root, configured in `pyproject.toml`)

### Coverage Configuration

From `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
cache_dir = "workspace/.pytest_cache"
asyncio_mode = "auto"
markers = ["live: tests that hit real upstream BPS services"]
filterwarnings = [
    "ignore::pytest.PytestUnraisableExceptionWarning",
    "ignore::DeprecationWarning:mcp.*",
]
```

## Test Categories

### Unit Tests (default, no network required)
- All tests NOT marked with `@pytest.mark.live`
- Run with: `make test` or `uv run pytest tests/ -m "not live"`
- Mock all external dependencies (LLM APIs, BPS API, Playwright)
- Safe to run in CI without API keys

### Integration Tests (no network required)
- Tests that exercise multiple modules together
- Examples: `test_llm_bps_integration.py`, `test_bps_orchestrator.py`
- Still use mocks for external services

### Live Tests (network + API keys required)
- Marked with `@pytest.mark.live`
- Auto-skipped unless `--run-live` flag is passed
- Hit real BPS services (bps.go.id, ntt.bps.go.id)
- Require `BPS_API_KEY` environment variable
- Example: `test_bps_live_smoke.py`
- Run with: `make test-live` or `uv run pytest tests/ --run-live -m live`

## For AI Agents

### Working In This Directory

1. **Run tests before committing:** Always run `make test` to verify changes don't break existing tests.
2. **Async tests:** `asyncio_mode = "auto"` means no `@pytest.mark.asyncio` decorator needed. Just write `async def test_*()` functions.
3. **Fixtures:** Use `conftest.py` fixtures for common setup. `tmp_workspace` for file operations, `mock_bps_api` for BPS tests, `tmp_memory_file` for note tool tests.
4. **Mocking:** Mock LLM responses for agent tests — never hit real APIs in unit tests. Use `unittest.mock.MagicMock` and `patch`.
5. **Live tests:** Mark network-dependent tests with `@pytest.mark.live`. They will be auto-skipped in CI.
6. **Naming:** Follow `test_<module>.py` for basic tests, `test_<module>_<variant>.py` for extended/comprehensive/coverage variants.
7. **Coverage:** Check coverage with `make test-cov`. Target: maintain or improve 81% line coverage.
8. **Research tests:** Use temporary project state files. Research tools may require optional extras — mock dependencies if not installed.
9. **Warning filters:** `PytestUnraisableExceptionWarning` and MCP `DeprecationWarning` are suppressed in config.

### Adding New Tests

1. Create `test_<module_name>.py` in this directory
2. Import from `mini_agent.<module>` 
3. Use fixtures from `conftest.py` where applicable
4. Mark live tests with `@pytest.mark.live`
5. Run `uv run pytest tests/test_<module_name>.py -v` to verify
6. Check coverage: `uv run pytest tests/ --cov=mini_agent.<module> --cov-report=term-missing`
