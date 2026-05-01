# BPS Academic Research Agent — Comprehensive Test Plan

**Version:** 1.0  
**Created:** 2025-07-15  
**Status:** Implementation Reference  
**Scope:** All new tests for Academic Research Agent v1.0  
**Existing Baseline:** 417 tests across 34 files (NEVER remove existing tests)

---

## Table of Contents

1. [Testing Strategy](#1-testing-strategy)
2. [Test Infrastructure Additions](#2-test-infrastructure-additions)
3. [Phase 0 Tests — MCP Servers](#3-phase-0-tests--mcp-servers)
4. [Phase 1 Tests — Foundation](#4-phase-1-tests--foundation)
5. [Phase 2 Tests — Analysis](#5-phase-2-tests--analysis)
6. [Phase 3 Tests — Literature/RAG](#6-phase-3-tests--literaturerag)
7. [Phase 4 Tests — Paper Writing](#7-phase-4-tests--paper-writing)
8. [Phase 5 Tests — Quality Gate](#8-phase-5-tests--quality-gate)
9. [Integration Tests](#9-integration-tests)
10. [Performance Benchmarks](#10-performance-benchmarks)
11. [Test Data](#11-test-data)

---

## 1. Testing Strategy

### 1.1 Test Pyramid

```
                    ╭─────────────╮
                    │   E2E (5%)  │  Full pipeline runs
                   ╭┴─────────────┴╮
                   │ Integration    │  Tool chains, phase transitions
                  ╭┴───────────────┴╮
                  │   Unit (80%)     │  Individual modules, functions
                  ╰──────────────────╯
```

### 1.2 Test Categories

| Category | Description | Markers | Run Frequency |
|----------|-------------|---------|---------------|
| Unit | Single function/class | (default) | Every commit |
| Integration | Multi-module interaction |  | Every PR |
| E2E | Full pipeline |  | Nightly |
| Live | Hits real APIs |  | Manual/weekly |
| Slow | >10s execution |  | Nightly |
| Docker | Requires Docker |  | CI only |

### 1.3 Mock Strategy

**ALWAYS mock:**
- External API calls (Semantic Scholar, CrossRef, OpenAlex, Elicit)
- LLM calls (use deterministic mock responses)
- File system operations that create large artifacts
- Docker/E2B sandbox calls (unless testing sandbox itself)
- Network requests (use  or )

**NEVER mock:**
- Internal business logic
- Data transformations
- State management
- File parsing (use real sample files)
- Configuration loading

### 1.4 Fixture Patterns

```python
# Shared fixtures follow this hierarchy:
# conftest.py (root) -> tests/conftest.py -> tests/phase_X/conftest.py

# Pattern 1: Factory fixtures (for parameterized creation)
@pytest.fixture
def make_project_state():
    def _factory(phase="PLAN", topic="test", **overrides):
        state = ProjectState(phase=phase, topic=topic)
        for k, v in overrides.items():
            setattr(state, k, v)
        return state
    return _factory

# Pattern 2: Mock response fixtures (loaded from JSON files)
@pytest.fixture
def mock_semantic_scholar_response():
    return json.loads(
        Path("tests/data/mock_responses/semantic_scholar_search.json").read_text()
    )

# Pattern 3: Temporary workspace fixtures
@pytest.fixture
def research_workspace(tmp_path):
    """Create a full research workspace structure."""
    for d in ["data", "output", "literature", "figures", "references", "drafts", "reviews"]:
        (tmp_path / d).mkdir()
    return tmp_path
```

### 1.5 Async Testing Convention

```python
# All async tests use pytest-asyncio with auto mode (from pyproject.toml)
# No need for @pytest.mark.asyncio decorator

async def test_async_function():
    result = await some_async_call()
    assert result is not None
```

### 1.6 Assertion Patterns

```python
# Prefer specific assertions over generic ones
assert result.status == "success"          # Good
assert result                              # Bad - unclear what is being tested

# For complex objects, use snapshot testing or structured comparison
assert result.model_dump() == expected_dict

# For floating point, use pytest.approx
assert result.p_value == pytest.approx(0.05, abs=1e-4)

# For file outputs, verify structure not exact content
assert output_path.exists()
assert output_path.stat().st_size > 0
```

---

## 2. Test Infrastructure Additions

### 2.1 New Fixtures (conftest.py additions)

```python
# === tests/conftest.py additions ===

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest


# --- Project State Fixtures ---

@pytest.fixture
def sample_project_yaml(tmp_path):
    """Create a sample project.yaml for testing."""
    project_data = {
        "id": "test-project-001",
        "title": "Impact of Fiscal Policy on Regional Growth in Indonesia",
        "phase": "PLAN",
        "created_at": "2025-07-15T10:00:00Z",
        "methodology": "panel_regression",
        "data_sources": ["bps", "world_bank"],
        "checkpoints": [],
    }
    yaml_path = tmp_path / "project.yaml"
    import yaml
    yaml_path.write_text(yaml.dump(project_data))
    return yaml_path


@pytest.fixture
def research_workspace(tmp_path):
    """Create a complete research workspace directory structure."""
    dirs = ["data", "output", "literature", "figures", "references", "drafts", "reviews"]
    for d in dirs:
        (tmp_path / d).mkdir()
    return tmp_path


# --- Mock API Response Fixtures ---

@pytest.fixture
def mock_semantic_scholar():
    """Mock Semantic Scholar API client."""
    mock = AsyncMock()
    mock.search.return_value = {
        "total": 150, "offset": 0,
        "data": [{
            "paperId": "abc123",
            "title": "Fiscal Decentralization and Economic Growth",
            "authors": [{"name": "Smith, J."}, {"name": "Doe, A."}],
            "year": 2023, "citationCount": 45,
            "abstract": "This paper examines the relationship between...",
            "doi": "10.1234/example.2023.001",
            "isOpenAccess": True, "fieldsOfStudy": ["Economics"],
        }],
    }
    mock.get_paper.return_value = {
        "paperId": "abc123",
        "title": "Fiscal Decentralization and Economic Growth",
        "references": [{"paperId": "ref1"}, {"paperId": "ref2"}],
        "citations": [{"paperId": "cit1"}],
    }
    return mock


@pytest.fixture
def mock_crossref():
    """Mock CrossRef API client."""
    mock = AsyncMock()
    mock.lookup_doi.return_value = {
        "DOI": "10.1234/example.2023.001",
        "title": ["Fiscal Decentralization and Economic Growth"],
        "author": [{"given": "John", "family": "Smith"}, {"given": "Alice", "family": "Doe"}],
        "published-print": {"date-parts": [[2023, 6, 15]]},
        "container-title": ["Journal of Development Economics"],
        "volume": "45", "issue": "2", "page": "123-145",
        "type": "journal-article", "is-referenced-by-count": 45,
    }
    mock.get_bibtex.return_value = (
        "@article{smith2023fiscal,\n"
        "  title={Fiscal Decentralization and Economic Growth},\n"
        "  author={Smith, John and Doe, Alice},\n"
        "  journal={Journal of Development Economics},\n"
        "  volume={45}, number={2}, pages={123--145}, year={2023}\n"
        "}"
    )
    return mock


@pytest.fixture
def mock_openai_embedding():
    """Mock embedding API responses."""
    mock = AsyncMock()
    mock.embed.return_value = [[0.1] * 768]  # SPECTER2 dimension
    return mock


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for deterministic testing."""
    mock = AsyncMock()
    mock.generate.return_value = {
        "content": "This is a mock LLM response for testing.",
        "usage": {"prompt_tokens": 100, "completion_tokens": 50},
        "model": "mock-model",
    }
    return mock


@pytest.fixture
def sample_csv_data(tmp_path):
    """Create sample CSV data for statistical testing."""
    import pandas as pd
    import numpy as np
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "province_id": np.repeat(range(1, 11), 10),
        "year": np.tile(range(2014, 2024), 10),
        "gdp_growth": np.random.normal(5.0, 1.5, n),
        "fiscal_transfer": np.random.uniform(1000, 5000, n),
        "education_spending": np.random.uniform(200, 800, n),
        "population": np.random.randint(500000, 5000000, n),
        "unemployment_rate": np.random.uniform(3.0, 12.0, n),
    })
    csv_path = tmp_path / "data" / "panel_data.csv"
    csv_path.parent.mkdir(exist_ok=True)
    df.to_csv(csv_path, index=False)
    return csv_path


@pytest.fixture
def sample_bibtex(tmp_path):
    """Create sample BibTeX file."""
    bib_content = """@article{smith2023fiscal,
  title={Fiscal Decentralization and Economic Growth},
  author={Smith, John and Doe, Alice and Rahman, Budi},
  journal={Journal of Development Economics},
  volume={45}, number={2}, pages={123--145}, year={2023},
  doi={10.1234/example.2023.001}
}

@article{jones2022panel,
  title={Panel Data Methods for Regional Analysis},
  author={Jones, Robert and Lee, Sarah},
  journal={Econometrica},
  volume={90}, number={4}, pages={1567--1599}, year={2022},
  doi={10.3982/ECTA19456}
}

@book{wooldridge2020introductory,
  title={Introductory Econometrics: A Modern Approach},
  author={Wooldridge, Jeffrey M.},
  year={2020}, edition={7}, publisher={Cengage Learning}
}
"""
    bib_path = tmp_path / "references" / "references.bib"
    bib_path.parent.mkdir(exist_ok=True)
    bib_path.write_text(bib_content)
    return bib_path


@pytest.fixture
def mock_sandbox():
    """Mock sandbox execution environment."""
    mock = AsyncMock()
    mock.execute.return_value = {
        "stdout": "Analysis complete.\nR-squared = 0.85\np < 0.001",
        "stderr": "", "exit_code": 0, "artifacts": [], "execution_time_ms": 1500,
    }
    return mock


@pytest.fixture
def mock_mcp_client():
    """Mock MCP client for testing tool discovery."""
    mock = AsyncMock()
    mock.list_tools.return_value = [
        {"name": "search_papers", "description": "Search academic papers"},
        {"name": "get_paper_details", "description": "Get paper metadata"},
    ]
    mock.call_tool.return_value = {"result": "mock_result"}
    mock.is_connected.return_value = True
    return mock
```

### 2.2 Test Data Files Needed

```
tests/
├── data/
│   ├── sample_paper.pdf              # 2-page academic paper (generated via reportlab)
│   ├── sample_data.csv               # Panel data (10 provinces x 10 years)
│   ├── sample_time_series.csv        # Monthly inflation data (120 months)
│   ├── sample_references.bib         # 10 BibTeX entries (all verified DOIs)
│   ├── sample_project.yaml           # Complete project state
│   ├── sample_latex_template.tex     # Minimal LaTeX template
│   ├── sample_typst_template.typ     # Minimal Typst template
│   ├── mock_responses/
│   │   ├── semantic_scholar_search.json
│   │   ├── semantic_scholar_paper.json
│   │   ├── crossref_doi_lookup.json
│   │   ├── crossref_search.json
│   │   ├── openai_embedding.json
│   │   ├── llm_section_generation.json
│   │   └── llm_review_response.json
│   ├── expected_outputs/
│   │   ├── apa_table_regression.txt
│   │   ├── apa_table_descriptive.txt
│   │   ├── bibtex_formatted.bib
│   │   └── latex_section_intro.tex
│   └── invalid/
│       ├── corrupted.pdf
│       ├── malformed.csv
│       ├── invalid.bib
│       └── empty.yaml
```

### 2.3 Docker Test Setup

```yaml
# tests/docker-compose.test.yml
version: "3.8"
services:
  sandbox:
    build:
      context: .
      dockerfile: Dockerfile.sandbox
    volumes:
      - ./tests/data:/data:ro
      - /tmp/test_output:/output
    mem_limit: 2g
    cpus: 1.0
    network_mode: none
    security_opt:
      - no-new-privileges:true
```

### 2.4 pyproject.toml Marker Additions

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
cache_dir = "workspace/.pytest_cache"
asyncio_mode = "auto"
markers = [
    "live: tests that hit real upstream services",
    "integration: multi-module integration tests",
    "e2e: end-to-end pipeline tests",
    "slow: tests taking >10 seconds",
    "docker: tests requiring Docker",
    "phase0: MCP server tests",
    "phase1: foundation module tests",
    "phase2: analysis tool tests",
    "phase3: literature/RAG tests",
    "phase4: paper writing tests",
    "phase5: quality gate tests",
]
```

---

## 3. Phase 0 Tests — MCP Servers

### File: `tests/test_mcp_research_servers.py`

**Purpose:** Verify new MCP server integration (paper-search, zotero, overleaf, mcp-pdf, qdrant, neo4j, markitdown, rmcp).

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_paper_search_mcp_connects` | MCP config | Connection established | MCP transport |
| `test_paper_search_mcp_tool_discovery` | Connected client | 22 tools listed | MCP list_tools |
| `test_zotero_mcp_connects` | MCP config | Connection established | MCP transport |
| `test_mcp_pdf_tool_discovery` | Connected client | 46 tools listed | MCP list_tools |
| `test_qdrant_mcp_connects` | MCP config | Connection established | MCP transport |
| `test_neo4j_mcp_connects` | MCP config | Connection established | MCP transport |
| `test_rmcp_connects` | MCP config | Connection established | MCP transport |
| `test_markitdown_mcp_connects` | MCP config | Connection established | MCP transport |
| `test_unavailable_server_returns_error` | Disconnected server | Clear error message | ConnectionError |
| `test_timeout_handling` | Slow server | TimeoutError caught | asyncio.TimeoutError |
| `test_partial_server_failure_continues` | One server down | Partial results returned | Mixed mock |
| `test_server_reconnection_after_failure` | Recovered server | Reconnection succeeds | Sequential mock |
| `test_all_servers_down_still_functional` | All research MCPs down | Core BPS tools work | All fail |
| `test_paper_search_returns_structured_results` | Search query | Papers with DOI, title, year | MCP call_tool |
| `test_mcp_tool_error_propagation` | Invalid params | Error with message | MCP error response |
| `test_large_result_set_handling` | Broad query | 100 results handled | Large response |

```python
"""Tests for new MCP server integration."""

import pytest
from unittest.mock import AsyncMock


class TestMCPServerConnectivity:
    """Test that new MCP servers can be discovered and connected."""

    async def test_paper_search_mcp_connects(self, mock_mcp_client):
        """paper-search-mcp server responds to initialize."""
        result = await mock_mcp_client.is_connected()
        assert result is True

    async def test_paper_search_mcp_tool_discovery(self, mock_mcp_client):
        """paper-search-mcp exposes expected tools (22 tools)."""
        tools = await mock_mcp_client.list_tools()
        tool_names = [t["name"] for t in tools]
        assert "search_papers" in tool_names

    async def test_zotero_mcp_connects(self, mock_mcp_client):
        """zotero-mcp server responds to initialize."""
        result = await mock_mcp_client.is_connected()
        assert result is True

    async def test_mcp_pdf_tool_discovery(self, mock_mcp_client):
        """mcp-pdf exposes PDF processing tools (46 expected)."""
        tools = await mock_mcp_client.list_tools()
        assert len(tools) >= 2

    async def test_qdrant_mcp_connects(self, mock_mcp_client):
        """qdrant-mcp server responds to initialize."""
        result = await mock_mcp_client.is_connected()
        assert result is True


class TestMCPGracefulDegradation:
    """Test system behavior when MCP servers are unavailable."""

    async def test_unavailable_server_returns_error(self):
        """When MCP server is down, tool call returns clear error."""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = ConnectionError("Server unavailable")
        with pytest.raises(ConnectionError):
            await mock_client.call_tool("search_papers", {"query": "test"})

    async def test_timeout_handling(self):
        """MCP server timeout is handled gracefully."""
        import asyncio
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = asyncio.TimeoutError()
        with pytest.raises(asyncio.TimeoutError):
            await mock_client.call_tool("search_papers", {"query": "test"})

    async def test_partial_server_failure_continues(self):
        """If one MCP server fails, others continue working."""
        working_client = AsyncMock()
        working_client.call_tool.return_value = {"results": ["paper1"]}
        result = await working_client.call_tool("search_papers", {"query": "test"})
        assert result["results"] == ["paper1"]

    async def test_server_reconnection_after_failure(self):
        """System attempts reconnection after server failure."""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = [
            ConnectionError("Temporary failure"),
            {"results": ["paper1"]},
        ]
        with pytest.raises(ConnectionError):
            await mock_client.call_tool("search_papers", {"query": "test"})
        result = await mock_client.call_tool("search_papers", {"query": "test"})
        assert result["results"] == ["paper1"]


class TestMCPToolInvocation:
    """Test actual tool invocation through MCP protocol."""

    async def test_paper_search_returns_structured_results(self, mock_mcp_client):
        """paper-search tool returns properly structured results."""
        mock_mcp_client.call_tool.return_value = {
            "papers": [{"title": "Test Paper", "doi": "10.1234/test", "year": 2023}]
        }
        result = await mock_mcp_client.call_tool(
            "search_papers", {"query": "fiscal decentralization"}
        )
        assert "papers" in result
        assert result["papers"][0]["doi"] == "10.1234/test"

    async def test_mcp_tool_error_propagation(self, mock_mcp_client):
        """MCP tool errors are properly propagated to caller."""
        mock_mcp_client.call_tool.return_value = {
            "error": {"code": -32602, "message": "Invalid params"}
        }
        result = await mock_mcp_client.call_tool("search_papers", {})
        assert "error" in result
```

---

## 4. Phase 1 Tests — Foundation

### File: `tests/test_project_state.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_create_new_project` | topic, methodology | project.yaml with all fields | None |
| `test_create_project_generates_unique_id` | Two init calls | Different UUIDs | None |
| `test_load_existing_project` | Valid YAML path | ProjectState object | None |
| `test_load_nonexistent_project_raises` | Bad path | FileNotFoundError | None |
| `test_load_corrupted_yaml_raises` | Invalid YAML | ValueError/YAMLError | None |
| `test_phase_transition` | PLAN -> COLLECT | Updated YAML | None |
| `test_phase_transition_order_enforced` | PLAN -> ANALYZE | InvalidPhaseTransition | None |
| `test_phase_transition_backward_allowed` | ANALYZE -> COLLECT | Phase updated, iteration++ | None |
| `test_checkpoint_save` | Active project | Checkpoint file created | None |
| `test_checkpoint_restore` | Checkpoint ID | State matches checkpoint | None |
| `test_checkpoint_list` | Multiple checkpoints | Ordered list with metadata | None |
| `test_state_includes_data_sources` | Used BPS + S2 | data_sources list | None |
| `test_state_includes_collected_papers` | 5 papers | papers list with DOIs | None |

### File: `tests/test_phase_manager.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_tool_loading_per_phase_plan` | Phase=PLAN | 5 tools loaded | Tool registry |
| `test_tool_loading_per_phase_collect` | Phase=COLLECT | 18 tools loaded | Tool registry |
| `test_tool_loading_per_phase_analyze` | Phase=ANALYZE | 15 tools loaded | Tool registry |
| `test_tool_loading_per_phase_write` | Phase=WRITE | 12 tools loaded | Tool registry |
| `test_tool_loading_per_phase_review` | Phase=REVIEW | 8 tools loaded | Tool registry |
| `test_max_15_tools_per_phase` | All phases | Each <= 15 tools | Tool registry |
| `test_core_tools_always_available` | All phases | read_file, write_file present | Tool registry |
| `test_phase_transition_persists_state` | COLLECT->ANALYZE | State saved before swap | State manager |
| `test_phase_transition_unloads_previous_tools` | PLAN->COLLECT | PLAN tools removed | Tool registry |
| `test_duplicate_tool_names_rejected` | Duplicate name | DuplicateToolError | None |
| `test_unknown_phase_raises` | "INVALID" | ValueError | None |
| `test_tool_loading_is_idempotent` | Load twice | Same tool set | Tool registry |

### File: `tests/test_research_orchestrator.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_orchestrator_initializes_with_project` | Existing project.yaml | Correct phase loaded | LLM, tools |
| `test_orchestrator_creates_new_project` | Empty workspace + topic | project.yaml created | LLM |
| `test_orchestrator_dispatches_to_correct_phase` | ANALYZE + regression request | ANALYZE handler called | Phase handlers |
| `test_orchestrator_handles_phase_transition` | "proceed to collection" | Phase = COLLECT | LLM, phase mgr |
| `test_orchestrator_human_in_the_loop_gate` | Methodology decision | Pauses for approval | LLM, user input |
| `test_orchestrator_session_resume` | Saved session | Resumes from checkpoint | LLM, tools |
| `test_orchestrator_error_recovery` | Tool raises error | State preserved, error msg | Failing tool |
| `test_orchestrator_token_budget_tracking` | Multiple calls | Token count reported | LLM with usage |
| `test_section_writer_dispatch` | Write Introduction | SectionWriter created | LLM |
| `test_peer_reviewer_dispatch` | Review draft | PeerReviewer with diff persona | LLM |
| `test_stat_validator_dispatch` | Validate results | Validation report | LLM |
| `test_citation_verifier_dispatch` | Verify bibliography | Verification report | CrossRef, S2 |

### File: `tests/test_session_manager.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_session_auto_save` | Tool execution | Session file updated | Tool mock |
| `test_session_resume_from_checkpoint` | Checkpoint ID | Exact state restored | None |
| `test_session_resume_preserves_context` | Resume session | Context window correct | LLM context |
| `test_session_handles_concurrent_access` | Concurrent writes | No corruption | None |
| `test_session_cleanup_old_checkpoints` | 20 checkpoints | Only 10 remain | None |
| `test_session_metadata_tracked` | Multiple calls | Duration, tokens, calls | None |

---

## 5. Phase 2 Tests — Analysis

### File: `tests/test_python_repl.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_basic_execution` | `print(2+2)` | stdout="4\n", exit=0 | Sandbox |
| `test_pandas_available` | `import pandas` | Version string | Sandbox |
| `test_scipy_available` | `import scipy` | Version string | Sandbox |
| `test_statsmodels_available` | `import statsmodels` | Version string | Sandbox |
| `test_timeout_enforcement` | `time.sleep(200)` | TimeoutError | Sandbox |
| `test_memory_limit_enforcement` | Allocate >2GB | MemoryError/exit=137 | Sandbox |
| `test_no_network_access` | `urlopen(...)` | Network error | Sandbox |
| `test_data_file_mounting` | Read /data/file.csv | File contents | Sandbox |
| `test_output_artifact_capture` | Save to /output/ | Artifact in response | Sandbox |
| `test_syntax_error_returns_stderr` | `def foo(:` | SyntaxError in stderr | Sandbox |
| `test_multiple_artifacts_captured` | Save 3 files | 3 artifacts | Sandbox |

### File: `tests/test_statistics_tools.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_basic_descriptive_stats` | CSV + variable | mean, sd, min, max | None (pure) |
| `test_descriptive_stats_all_variables` | CSV, no vars | Stats for all columns | None |
| `test_descriptive_stats_with_groupby` | CSV + groupby | Per-group stats | None |
| `test_correlation_matrix` | 3 variables | 3x3 matrix, [-1,1] | None |
| `test_missing_values_reported` | CSV with NaN | Missing count | None |
| `test_ols_regression` | DV + IVs | Coefficients, R-sq, p-values | None |
| `test_ols_with_robust_se` | + robust_se=True | Different SEs | None |
| `test_logistic_regression` | Binary DV | Odds ratios, pseudo-R-sq | None |
| `test_panel_fixed_effects` | Panel data + FE | Within-R-sq, F-test | None |
| `test_panel_random_effects` | Panel data + RE | Variance components | None |
| `test_hausman_test` | Panel data | Chi-sq, p-value, recommendation | None |
| `test_diagnostic_tests_included` | OLS | BP, DW, JB tests | None |
| `test_invalid_variable_name_raises` | Bad column name | ValueError | None |
| `test_multicollinearity_warning` | Correlated IVs | VIF warning | None |
| `test_independent_t_test` | Two groups | t, df, p, Cohen's d | None |
| `test_paired_t_test` | Pre-post data | t, df, p, effect size | None |
| `test_one_way_anova` | 3+ groups | F, df, p, eta-sq | None |
| `test_chi_square_independence` | Categorical data | chi-sq, df, p, Cramer's V | None |
| `test_assumption_checking` | + check=True | Normality + homogeneity | None |
| `test_nonparametric_suggestion` | Skewed data | Mann-Whitney suggestion | None |
| `test_effect_size_always_reported` | Any test | Effect size present | None |
| `test_power_analysis` | t-test | Power in [0,1] | None |
| `test_unit_root_adf` | Time series | ADF stat, p-value | None |
| `test_arima_model` | Stationary series | AIC, BIC, coefficients | None |
| `test_granger_causality` | Two series | F-stats per lag | None |
| `test_cointegration_johansen` | Non-stationary | Trace stat, rank | None |
| `test_forecast_output` | ARIMA + periods | Forecasts with CI | None |

### File: `tests/test_visualization_tool.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_generates_pdf_output` | Scatter + pdf | Valid PDF file | Sandbox |
| `test_generates_png_output` | Bar + png | Valid PNG file | Sandbox |
| `test_generates_tiff_output` | Plot + tiff | TIFF >= 300 DPI | Sandbox |
| `test_journal_preset_nature` | preset=nature | 89mm width, Helvetica | Sandbox |
| `test_journal_preset_apa` | preset=apa | APA formatting | Sandbox |
| `test_colorblind_friendly_palette` | Default palette | Okabe-Ito colors | Sandbox |
| `test_all_plot_types_supported` | Each of 12 types | No errors | Sandbox |
| `test_invalid_plot_type_raises` | "invalid_type" | ValueError | None |
| `test_figsize_presets` | Each preset | Correct dimensions | Sandbox |
| `test_empty_data_raises` | Empty CSV | ValueError | None |

### File: `tests/test_apa_formatter.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_t_test_apa_format` | t=2.45, df=98, p=.016 | "t(98) = 2.45, p = .016, d = 0.49" | None |
| `test_anova_apa_format` | F=4.56, df1=2, df2=97 | "F(2, 97) = 4.56, p = .013" | None |
| `test_chi_square_apa_format` | chi2=12.34, df=4 | Correct format | None |
| `test_correlation_apa_format` | r=.45, n=100 | "r(98) = .45, p < .001" | None |
| `test_p_value_less_than_001` | p=0.0003 | "p < .001" | None |
| `test_p_value_no_leading_zero` | p=0.045 | "p = .045" | None |
| `test_regression_table_format` | Results dict | APA table structure | None |
| `test_significance_stars` | Various p-values | Correct stars | None |
| `test_confidence_interval_format` | CI bounds | "95% CI [1.23, 4.56]" | None |

---

## 6. Phase 3 Tests — Literature/RAG

### File: `tests/test_semantic_scholar_client.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_basic_search` | Query string | Papers with title, DOI, year | S2 API mock |
| `test_search_with_year_filter` | Query + years | Only papers in range | S2 API mock |
| `test_search_with_field_filter` | Query + field | Only matching field | S2 API mock |
| `test_search_pagination` | offset=10, limit=10 | Next page | S2 API mock |
| `test_empty_search_results` | Obscure query | Empty list, no error | S2 API mock |
| `test_get_paper_citations` | Paper ID | Citation list | S2 API mock |
| `test_get_paper_references` | Paper ID | Reference list | S2 API mock |
| `test_citation_graph_traversal` | Paper ID, depth=2 | 2-level graph | S2 API mock |
| `test_rate_limit_429_retry` | 429 response | Retry with backoff | S2 API mock |
| `test_max_retries_exceeded` | Always 429 | RateLimitError | S2 API mock |
| `test_network_error_handling` | Network timeout | ConnectionError | S2 API mock |
| `test_invalid_paper_id` | Bad ID | None returned | S2 API mock |

### File: `tests/test_crossref_client.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_valid_doi_lookup` | Valid DOI | Full metadata | CrossRef mock |
| `test_invalid_doi_returns_none` | Bad DOI | None | CrossRef mock |
| `test_doi_metadata_completeness` | Valid DOI | All fields present | CrossRef mock |
| `test_bibtex_generation` | Valid DOI | Valid BibTeX string | CrossRef mock |
| `test_bibtex_key_generation` | Smith 2023 paper | "smith2023..." key | CrossRef mock |
| `test_bibtex_special_characters_escaped` | Title with & | Escaped characters | CrossRef mock |
| `test_search_by_title` | Title query | Matching works | CrossRef mock |
| `test_search_by_author` | Author name | Author's works | CrossRef mock |

### File: `tests/test_citation_manager.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_add_citation_by_doi` | DOI string | Citation stored | CrossRef mock |
| `test_add_citation_manual` | Metadata dict | Citation with manual flag | None |
| `test_remove_citation` | Citation key | Removed from bibliography | None |
| `test_remove_nonexistent_citation_raises` | Bad key | KeyError | None |
| `test_verify_citation_exists` | Real DOI | status="verified" | CrossRef mock |
| `test_verify_citation_not_found` | Fake DOI | status="unverified" | CrossRef mock |
| `test_export_bibtex` | 3 citations | Valid .bib file | None |
| `test_export_apa_reference_list` | Citations | APA formatted text | None |
| `test_duplicate_detection` | Same DOI twice | "already exists" warning | CrossRef mock |
| `test_verify_all_citations` | 10 citations | 8 verified, 2 unverified | CrossRef + S2 |
| `test_verify_detects_fabricated_citation` | Fake metadata | "potentially fabricated" | All return None |
| `test_verify_detects_metadata_mismatch` | Wrong year/author | "metadata mismatch" | CrossRef mock |

### File: `tests/test_literature_search.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_multi_source_search` | Query | Results from S2 + CrossRef | Both mocks |
| `test_deduplication_by_doi` | Same DOI from 2 sources | Single entry | Both mocks |
| `test_deduplication_by_title_similarity` | Similar titles | Merged entry | Both mocks |
| `test_relevance_ranking` | Mixed results | Sorted by relevance | Both mocks |
| `test_search_with_citation_count_filter` | min_citations=10 | Only high-cited | Both mocks |
| `test_search_open_access_filter` | open_access=True | Only OA papers | Both mocks |
| `test_empty_query_raises` | "" | ValueError | None |

### File: `tests/test_rag_pipeline.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_embed_text_chunk` | Text string | 768-dim vector | Embedding API |
| `test_embed_batch` | 10 chunks | 10 vectors | Embedding API |
| `test_embed_empty_text_raises` | "" | ValueError | Embedding API |
| `test_store_embedding` | Vector + metadata | Stored, retrievable | Vector store |
| `test_similarity_search` | Query vector, k=5 | 5 similar docs | Vector store |
| `test_similarity_search_with_filter` | Query + year>=2020 | Filtered results | Vector store |
| `test_delete_by_paper_id` | Paper ID | All chunks removed | Vector store |
| `test_retrieve_relevant_context` | Research question | Relevant chunks | Embedding + store |
| `test_synthesize_answer` | Question + chunks | Coherent answer | LLM mock |
| `test_synthesis_includes_citations` | Question + 3 papers | [1], [2], [3] markers | LLM mock |
| `test_no_hallucination_in_synthesis` | Limited context | Only context-based claims | LLM mock |

---

## 7. Phase 4 Tests — Paper Writing

### File: `tests/test_latex_generator.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_generates_valid_latex` | Paper metadata | Valid .tex file | None |
| `test_article_template` | template=article | documentclass{article} | None |
| `test_includes_bibliography` | Paper + refs | bibliography commands | None |
| `test_includes_packages` | Paper with tables | booktabs, graphicx, amsmath | None |
| `test_section_structure` | Full paper | All 6 sections in order | None |
| `test_table_uses_booktabs` | Table data | toprule, midrule, bottomrule | None |
| `test_figure_inclusion` | Figure paths | includegraphics with captions | None |
| `test_cross_references` | Refs to tables/figs | Valid LaTeX refs | None |
| `test_special_characters_escaped` | Text with &, % | Properly escaped | None |

### File: `tests/test_section_writer.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_write_introduction` | Topic + methodology | Background, gap, objectives | LLM mock |
| `test_write_literature_review` | Paper summaries | Thematic review with citations | LLM mock |
| `test_write_methodology` | Methods + data desc | Equations, variable defs | LLM mock |
| `test_write_results` | Stats results | Narrative with table refs | LLM mock |
| `test_write_discussion` | Results + literature | Interpretation, implications | LLM mock |
| `test_write_conclusion` | Key findings | Summary, limitations, future | LLM mock |
| `test_section_includes_citations` | Any section | Citation markers present | LLM mock |
| `test_section_respects_word_limit` | limit=500 | Output <= 500 words | LLM mock |

### File: `tests/test_table_generator.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_booktabs_format` | Table data | No vertical lines | None |
| `test_apa_style_table` | Table data | APA 7th formatting | None |
| `test_regression_table` | Regression results | Coefficients, stars, R-sq, N | None |
| `test_descriptive_stats_table` | Stats dict | M, SD, Min, Max columns | None |
| `test_correlation_matrix_table` | Correlation data | Significance indicators | None |
| `test_table_notes` | Table + notes | Proper note formatting | None |
| `test_multi_model_comparison_table` | 3 models | Side-by-side comparison | None |

### File: `tests/test_compilation.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_tectonic_compiles_latex` | Valid .tex | PDF file | Docker (real) |
| `test_typst_compiles_to_pdf` | Valid .typ | PDF file | Docker (real) |
| `test_compilation_with_bibliography` | .tex + .bib | PDF with references | Docker (real) |
| `test_compilation_with_figures` | .tex + figures | PDF with figures | Docker (real) |
| `test_compilation_error_reporting` | Invalid .tex | Error with line number | Docker/mock |
| `test_compilation_timeout` | Complex doc | Completes < 60s | Docker/mock |

### File: `tests/test_bibliography.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_bibtex_valid_syntax` | Generated .bib | Parseable by bibtexparser | None |
| `test_all_entries_have_required_fields` | .bib file | Required fields per type | None |
| `test_no_duplicate_keys` | .bib file | All keys unique | None |
| `test_all_cited_entries_present` | .tex + .bib | Every cite has entry | None |
| `test_no_orphan_entries` | .tex + .bib | Every entry is cited | None |
| `test_doi_present_when_available` | .bib file | DOI field present | None |

---

## 8. Phase 5 Tests — Quality Gate

### File: `tests/test_statistical_validity.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_catches_p_hacking` | 20 tests, no correction | Multiple comparisons warning | None |
| `test_catches_wrong_test_for_data` | t-test on skewed data | Assumption violation warning | None |
| `test_catches_small_sample_issues` | n=15, k=10 | Overfitting risk warning | None |
| `test_catches_multicollinearity` | VIF > 10 | Multicollinearity warning | None |
| `test_catches_endogeneity_concerns` | OLS where IV needed | IV suggestion | None |
| `test_validates_effect_sizes` | Results without ES | Missing effect size warning | None |
| `test_validates_confidence_intervals` | Results without CI | Missing CI warning | None |
| `test_generates_validity_report` | Full results | Structured report | None |

### File: `tests/test_citation_verification.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_detects_fabricated_citations` | 2 fake entries | Both flagged | CrossRef + S2 |
| `test_detects_wrong_year` | Citation year=2023, actual=2021 | Metadata mismatch | CrossRef |
| `test_detects_wrong_author` | Wrong author name | Metadata mismatch | CrossRef |
| `test_detects_wrong_journal` | Wrong journal | Metadata mismatch | CrossRef |
| `test_all_citations_verified_passes` | All real | Gate passes | CrossRef + S2 |
| `test_any_fabricated_citation_fails` | 1 fake | Gate fails | CrossRef + S2 |
| `test_verification_percentage_reported` | 45/47 verified | "95.7%" reported | CrossRef + S2 |

### File: `tests/test_style_checker.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_flags_passive_voice_overuse` | >40% passive | Passive voice warning | None |
| `test_flags_informal_language` | "a lot of", "stuff" | Formal alternatives | None |
| `test_flags_hedging_language` | "might possibly" | Be more direct | None |
| `test_flags_first_person_overuse` | Many "I"/"we" | Reduce first-person | None |
| `test_checks_paragraph_length` | Very long paragraph | Length warning | None |
| `test_checks_sentence_length` | >40 word sentence | Length warning | None |
| `test_generates_style_report` | Full text | Structured report | None |

### File: `tests/test_peer_review.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_generates_structured_review` | Paper draft | Summary, Strengths, Weaknesses | LLM mock |
| `test_review_covers_methodology` | Draft | Methodology evaluation | LLM mock |
| `test_review_covers_statistics` | Draft | Statistics evaluation | LLM mock |
| `test_review_covers_writing_quality` | Draft | Writing evaluation | LLM mock |
| `test_reviewer_persona_differs_from_writer` | Draft | Different persona used | LLM mock |
| `test_review_actionable_feedback` | Draft | Specific suggestions | LLM mock |
| `test_review_severity_levels` | Draft | Major/minor categorization | LLM mock |

### File: `tests/test_plagiarism_detection.py`

| Test | Input | Expected Output | Mock Strategy |
|------|-------|-----------------|---------------|
| `test_detects_exact_copy` | Verbatim paragraph | Flagged as exact match | None |
| `test_detects_close_paraphrase` | Minor word changes | Flagged as close paraphrase | None |
| `test_allows_proper_quotation` | Quoted + cited text | Not flagged | None |
| `test_allows_common_phrases` | "The results suggest..." | Not flagged | None |
| `test_generates_similarity_report` | Full text | Similarity percentage | None |

---

## 9. Integration Tests

### File: `tests/test_full_pipeline.py`

```python
"""End-to-end pipeline integration tests."""

import pytest


@pytest.mark.e2e
@pytest.mark.slow
class TestFullPipeline:
    """Test complete research pipeline: PLAN -> COLLECT -> ANALYZE -> WRITE -> REVIEW."""

    async def test_plan_to_collect_transition(self, research_workspace, mock_llm_response):
        """PLAN phase produces valid research plan, transitions to COLLECT."""
        # Verify: Plan has methodology, data sources, timeline
        pass

    async def test_collect_to_analyze_transition(self, research_workspace, mock_semantic_scholar):
        """COLLECT phase gathers papers, transitions to ANALYZE."""
        # Verify: Papers in workspace, bibliography populated
        pass

    async def test_analyze_to_write_transition(self, research_workspace, mock_sandbox):
        """ANALYZE phase produces results, transitions to WRITE."""
        # Verify: Results files exist, figures generated
        pass

    async def test_write_to_review_transition(self, research_workspace, mock_llm_response):
        """WRITE phase produces draft, transitions to REVIEW."""
        # Verify: All sections present, bibliography complete
        pass

    async def test_review_produces_final_output(self, research_workspace, mock_llm_response):
        """REVIEW phase produces final reviewed paper."""
        # Verify: Review report, revised draft, quality gate results
        pass

    async def test_full_pipeline_end_to_end(self, research_workspace, mock_llm_response,
                                             mock_semantic_scholar, mock_crossref, mock_sandbox):
        """Complete pipeline from topic to reviewed paper."""
        # Input: Research topic
        # Expected: Final PDF with all quality gates passed
        # This is the ultimate integration test
        pass
```

### File: `tests/test_backward_compatibility.py`

```python
"""Backward compatibility tests - ensure existing BPS functionality works."""

import pytest


class TestBackwardCompatibility:
    """Verify all existing BPS functionality still works after research agent additions."""

    async def test_bps_search_still_works(self, mock_bps_api):
        """BPS data search functionality unchanged."""
        # Verify: All 62 existing BPS tools still functional
        pass

    async def test_bps_domain_resolution_unchanged(self, mock_bps_api):
        """BPS domain resolution (province/city) unchanged."""
        pass

    async def test_bps_table_retrieval_unchanged(self, mock_bps_api):
        """BPS static table retrieval unchanged."""
        pass

    async def test_existing_tools_not_removed(self):
        """No existing tools have been removed."""
        # Verify: All 62 BPS tools still registered
        pass

    async def test_existing_config_format_compatible(self):
        """Existing configuration files still work."""
        pass

    async def test_existing_session_format_compatible(self):
        """Existing session files can still be loaded."""
        pass

    async def test_cli_interface_unchanged(self):
        """CLI commands and flags unchanged."""
        pass
```

### File: `tests/test_session_resume.py`

```python
"""Session resume integration tests."""

import pytest


@pytest.mark.integration
class TestSessionResume:
    """Test resuming from any checkpoint in the pipeline."""

    async def test_resume_from_plan_checkpoint(self, research_workspace):
        """Can resume from PLAN phase checkpoint."""
        # Input: Checkpoint saved during PLAN
        # Expected: Resumes with plan context, correct tools loaded
        pass

    async def test_resume_from_collect_checkpoint(self, research_workspace):
        """Can resume from COLLECT phase checkpoint."""
        # Input: Checkpoint with 10 papers collected
        # Expected: Papers still available, continues collection
        pass

    async def test_resume_from_analyze_checkpoint(self, research_workspace):
        """Can resume from ANALYZE phase checkpoint."""
        # Input: Checkpoint with partial analysis
        # Expected: Previous results available, continues analysis
        pass

    async def test_resume_from_write_checkpoint(self, research_workspace):
        """Can resume from WRITE phase checkpoint."""
        # Input: Checkpoint with 3/6 sections written
        # Expected: Written sections preserved, continues writing
        pass

    async def test_resume_from_review_checkpoint(self, research_workspace):
        """Can resume from REVIEW phase checkpoint."""
        # Input: Checkpoint during review
        # Expected: Review progress preserved
        pass

    async def test_resume_preserves_all_artifacts(self, research_workspace):
        """Resume preserves all generated artifacts (figures, tables, data)."""
        pass

    async def test_resume_after_crash(self, research_workspace):
        """Can resume even after unexpected termination."""
        # Input: Simulated crash (incomplete checkpoint)
        # Expected: Recovers to last complete checkpoint
        pass
```

---

## 10. Performance Benchmarks

### File: `tests/test_performance.py`

```python
"""Performance benchmark tests."""

import pytest
import time


@pytest.mark.slow
class TestPerformanceBenchmarks:
    """Performance targets for the research agent."""

    # --- Token Usage Targets ---

    async def test_plan_phase_token_budget(self):
        """PLAN phase uses < 50K tokens total."""
        # Target: < 50,000 tokens for complete research plan
        pass

    async def test_collect_phase_token_budget(self):
        """COLLECT phase uses < 100K tokens total."""
        # Target: < 100,000 tokens for literature collection
        pass

    async def test_analyze_phase_token_budget(self):
        """ANALYZE phase uses < 80K tokens total."""
        # Target: < 80,000 tokens for statistical analysis
        pass

    async def test_write_phase_token_budget(self):
        """WRITE phase uses < 200K tokens total."""
        # Target: < 200,000 tokens for paper writing
        pass

    async def test_review_phase_token_budget(self):
        """REVIEW phase uses < 100K tokens total."""
        # Target: < 100,000 tokens for quality review
        pass

    # --- API Call Targets ---

    async def test_semantic_scholar_call_count(self):
        """Literature search uses < 50 S2 API calls per project."""
        pass

    async def test_crossref_call_count(self):
        """Citation verification uses < 100 CrossRef calls per project."""
        pass

    # --- Execution Time Targets ---

    async def test_phase_transition_time(self):
        """Phase transitions complete in < 5 seconds."""
        pass

    async def test_tool_loading_time(self):
        """Tool loading per phase completes in < 2 seconds."""
        pass

    async def test_checkpoint_save_time(self):
        """Checkpoint save completes in < 1 second."""
        pass

    async def test_checkpoint_restore_time(self):
        """Checkpoint restore completes in < 3 seconds."""
        pass

    async def test_sandbox_startup_time(self):
        """Sandbox container starts in < 10 seconds."""
        pass

    # --- Memory Usage Targets ---

    async def test_memory_usage_under_limit(self):
        """Agent memory usage stays under 2GB during normal operation."""
        pass

    async def test_no_memory_leak_across_phases(self):
        """Memory doesn't grow unbounded across phase transitions."""
        pass

    async def test_vector_store_memory_bounded(self):
        """Vector store memory bounded for 1000 paper chunks."""
        pass
```

---

## 11. Test Data

### Required Test Data Files

| File | Description | Size | How to Generate |
|------|-------------|------|-----------------|
| `tests/data/sample_paper.pdf` | 2-page academic paper | ~50KB | reportlab script |
| `tests/data/sample_data.csv` | Panel data (10 provinces x 10 years) | ~15KB | pandas with seed=42 |
| `tests/data/sample_time_series.csv` | Monthly inflation (120 months) | ~5KB | numpy with seed=42 |
| `tests/data/sample_references.bib` | 10 BibTeX entries | ~3KB | Manual (verified DOIs) |
| `tests/data/sample_project.yaml` | Complete project state | ~2KB | Manual |
| `tests/data/sample_latex_template.tex` | Minimal LaTeX template | ~1KB | Manual |
| `tests/data/sample_typst_template.typ` | Minimal Typst template | ~1KB | Manual |
| `tests/data/mock_responses/semantic_scholar_search.json` | S2 search response | ~5KB | Captured from API |
| `tests/data/mock_responses/semantic_scholar_paper.json` | S2 paper detail | ~3KB | Captured from API |
| `tests/data/mock_responses/crossref_doi_lookup.json` | CrossRef DOI response | ~4KB | Captured from API |
| `tests/data/mock_responses/crossref_search.json` | CrossRef search response | ~5KB | Captured from API |
| `tests/data/mock_responses/openai_embedding.json` | Embedding response | ~10KB | Generated |
| `tests/data/mock_responses/llm_section_generation.json` | LLM section output | ~3KB | Generated |
| `tests/data/mock_responses/llm_review_response.json` | LLM review output | ~4KB | Generated |
| `tests/data/expected_outputs/apa_table_regression.txt` | Expected APA table | ~1KB | Manual |
| `tests/data/expected_outputs/apa_table_descriptive.txt` | Expected descriptive table | ~1KB | Manual |
| `tests/data/expected_outputs/bibtex_formatted.bib` | Expected BibTeX output | ~2KB | Manual |
| `tests/data/expected_outputs/latex_section_intro.tex` | Expected LaTeX section | ~2KB | Manual |
| `tests/data/invalid/corrupted.pdf` | Corrupted PDF file | ~1KB | Random bytes |
| `tests/data/invalid/malformed.csv` | Malformed CSV | ~500B | Manual |
| `tests/data/invalid/invalid.bib` | Invalid BibTeX | ~500B | Manual |
| `tests/data/invalid/empty.yaml` | Empty YAML file | 0B | touch |

### Test Data Generation Script

```python
"""Generate test data files. Run once to create test fixtures."""
# tests/generate_test_data.py

import json
import numpy as np
import pandas as pd
from pathlib import Path


def generate_panel_data():
    """Generate sample panel data CSV."""
    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        "province_id": np.repeat(range(1, 11), 10),
        "year": np.tile(range(2014, 2024), 10),
        "gdp_growth": np.random.normal(5.0, 1.5, n),
        "fiscal_transfer": np.random.uniform(1000, 5000, n),
        "education_spending": np.random.uniform(200, 800, n),
        "population": np.random.randint(500000, 5000000, n),
        "unemployment_rate": np.random.uniform(3.0, 12.0, n),
    })
    return df


def generate_time_series_data():
    """Generate sample time series CSV."""
    np.random.seed(42)
    dates = pd.date_range("2010-01", periods=120, freq="M")
    df = pd.DataFrame({
        "date": dates,
        "inflation": np.cumsum(np.random.randn(120) * 0.3) + 5,
        "gdp_index": 100 + np.cumsum(np.random.randn(120) * 0.5),
        "interest_rate": np.random.uniform(4, 8, 120),
    })
    return df


def generate_mock_responses():
    """Generate mock API response JSON files."""
    s2_search = {
        "total": 150, "offset": 0, "next": 10,
        "data": [
            {
                "paperId": f"paper_{i}",
                "title": f"Paper Title {i}",
                "authors": [{"name": f"Author {i}"}],
                "year": 2020 + (i % 5),
                "citationCount": i * 10,
                "abstract": f"Abstract for paper {i}...",
                "doi": f"10.1234/paper.{i}",
                "isOpenAccess": i % 2 == 0,
                "fieldsOfStudy": ["Economics"],
            }
            for i in range(10)
        ],
    }
    return {"semantic_scholar_search": s2_search}


if __name__ == "__main__":
    data_dir = Path("tests/data")
    data_dir.mkdir(parents=True, exist_ok=True)

    # Generate CSV files
    generate_panel_data().to_csv(data_dir / "sample_data.csv", index=False)
    generate_time_series_data().to_csv(data_dir / "sample_time_series.csv", index=False)

    # Generate mock responses
    mock_dir = data_dir / "mock_responses"
    mock_dir.mkdir(exist_ok=True)
    responses = generate_mock_responses()
    for name, data in responses.items():
        (mock_dir / f"{name}.json").write_text(json.dumps(data, indent=2))

    # Generate invalid files
    invalid_dir = data_dir / "invalid"
    invalid_dir.mkdir(exist_ok=True)
    (invalid_dir / "corrupted.pdf").write_bytes(b"\x00\x01\x02\x03" * 100)
    (invalid_dir / "malformed.csv").write_text("col1,col2\n1,2,3\n4\n")
    (invalid_dir / "invalid.bib").write_text("@article{broken\ntitle = missing brace\n")
    (invalid_dir / "empty.yaml").write_text("")

    print("Test data generated successfully!")
```

---

## Summary: Test Count Estimates

| Section | Test Files | Estimated Tests |
|---------|-----------|-----------------|
| Phase 0: MCP Servers | 1 | 16 |
| Phase 1: Foundation | 4 | 48 |
| Phase 2: Analysis | 4 | 65 |
| Phase 3: Literature/RAG | 5 | 55 |
| Phase 4: Paper Writing | 5 | 40 |
| Phase 5: Quality Gate | 5 | 38 |
| Integration | 3 | 25 |
| Performance | 1 | 15 |
| **TOTAL NEW TESTS** | **28** | **~302** |
| **Existing Tests** | 34 | 417 |
| **GRAND TOTAL** | **62** | **~719** |

---

## Running Tests

```bash
# Run all tests
pytest

# Run by phase
pytest -m phase0
pytest -m phase1
pytest -m phase2
pytest -m phase3
pytest -m phase4
pytest -m phase5

# Run integration tests
pytest -m integration

# Run E2E tests (slow)
pytest -m e2e

# Run without live/docker tests
pytest -m "not live and not docker"

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_statistics_tools.py -v

# Run specific test class
pytest tests/test_statistics_tools.py::TestRegressionAnalysis -v
```
