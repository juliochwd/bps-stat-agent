# BPS Agent Production Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify an AllStats-first BPS agent pipeline that resolves search results into structured BPS data with normalized outputs, tested fallbacks, and production-ready MCP tools.

**Architecture:** Keep the existing `Mini-Agent` structure and harden the current BPS modules instead of replacing them wholesale. Introduce a small set of BPS-specific domain modules for resource typing, resolution, normalization, and orchestration, then route MCP tool functions through those modules so search, retrieval, and answer flows all share one contract.

**Tech Stack:** Python 3.10+, pytest, pytest-asyncio, requests, Playwright, MCP-compatible JSON tools

---

### Task 1: Lock Down BPS Contracts With Failing Tests

**Files:**
- Create: `tests/test_bps_parser.py`
- Create: `tests/test_bps_resolution.py`
- Create: `tests/test_bps_orchestrator.py`
- Modify: `pyproject.toml`

- [ ] **Step 1: Write the failing static-table parser tests**

```python
from mini_agent.bps_data_retriever import BPSDataRetriever


def test_parse_html_table_extracts_headers_and_rows():
    retriever = object.__new__(BPSDataRetriever)
    html = """
    <table>
      <tr><th>No</th></tr>
      <tr><th>Ignore</th></tr>
      <tr><th>Ignore</th></tr>
      <tr><th>Wilayah</th><th>Nilai</th></tr>
      <tr><td>Kupang</td><td>12,34</td></tr>
    </table>
    """

    headers, rows = retriever._parse_html_table(html)

    assert headers == ["Wilayah", "Nilai"]
    assert rows == [["Kupang", "12,34"]]
```

- [ ] **Step 2: Run parser test to verify it fails for the right reason**

Run: `pytest tests/test_bps_parser.py::test_parse_html_table_extracts_headers_and_rows -q`
Expected: fail because parser behavior is still tied to brittle assumptions or because test module does not exist yet.

- [ ] **Step 3: Write failing resolution tests for search-result typing**

```python
from mini_agent.bps_models import BPSResourceType
from mini_agent.bps_resolution import classify_search_result


def test_classify_search_result_detects_publication():
    result = {
        "title": "NTT Dalam Angka 2025",
        "url": "https://ntt.bps.go.id/publication/2025/01/01/abc/ntt-dalam-angka.html",
        "content_type": "publication",
    }

    resolved = classify_search_result(result)

    assert resolved.resource_type is BPSResourceType.PUBLICATION
    assert resolved.retrieval_candidates[0] == "webapi_detail"
```

- [ ] **Step 4: Run resolution test to verify it fails**

Run: `pytest tests/test_bps_resolution.py::test_classify_search_result_detects_publication -q`
Expected: fail because `bps_models` or `bps_resolution` does not exist yet.

- [ ] **Step 5: Write failing orchestrator contract tests**

```python
import pytest

from mini_agent.bps_orchestrator import BPSOrchestrator


@pytest.mark.asyncio
async def test_answer_query_uses_allstats_first_then_normalizes():
    orchestrator = BPSOrchestrator(
        search_client=FakeSearchClient(),
        resolver=FakeResolver(),
        retriever=FakeRetriever(),
    )

    result = await orchestrator.answer_query("inflasi NTT", domain="5300")

    assert result["query"] == "inflasi NTT"
    assert result["retrieval_method"] == "webapi_structured"
    assert result["rows"] == [{"wilayah": "NTT", "nilai": 1.23}]
```

- [ ] **Step 6: Run orchestrator test to verify it fails**

Run: `pytest tests/test_bps_orchestrator.py::test_answer_query_uses_allstats_first_then_normalizes -q`
Expected: fail because orchestrator module does not exist yet.

- [ ] **Step 7: Ensure pytest config covers the new test files**

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
cache_dir = "workspace/.pytest_cache"
asyncio_mode = "auto"
```

- [ ] **Step 8: Run the focused red suite**

Run: `pytest tests/test_bps_parser.py tests/test_bps_resolution.py tests/test_bps_orchestrator.py -q`
Expected: multiple failing tests, all in the new BPS contract surface.

### Task 2: Introduce Shared BPS Resource Models, Resolution, and Normalization

**Files:**
- Create: `mini_agent/bps_models.py`
- Create: `mini_agent/bps_resolution.py`
- Create: `mini_agent/bps_normalization.py`
- Modify: `mini_agent/__init__.py`

- [ ] **Step 1: Implement the shared BPS resource datatypes**

```python
from dataclasses import dataclass, field
from enum import Enum


class BPSResourceType(str, Enum):
    TABLE = "table"
    PUBLICATION = "publication"
    PRESSRELEASE = "pressrelease"
    NEWS = "news"
    INFOGRAPHIC = "infographic"
    GLOSSARY = "glossary"
    SUBJECT_DATA = "subject_data"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class BPSResolvedResource:
    resource_type: BPSResourceType
    title: str
    url: str
    domain_code: str
    retrieval_candidates: list[str] = field(default_factory=list)
    identifiers: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, object] = field(default_factory=dict)
```

- [ ] **Step 2: Implement deterministic result classification**

```python
from mini_agent.bps_models import BPSResolvedResource, BPSResourceType


def classify_search_result(result: dict) -> BPSResolvedResource:
    content_type = (result.get("content_type") or "").lower()
    url = result.get("url") or ""
    title = result.get("title") or ""
    domain_code = result.get("domain_code") or "0000"

    if content_type == "publication" or "/publication/" in url:
        resource_type = BPSResourceType.PUBLICATION
        candidates = ["webapi_detail", "detail_page_parse", "search_result_only"]
    elif content_type == "pressrelease" or "/pressrelease/" in url:
        resource_type = BPSResourceType.PRESSRELEASE
        candidates = ["webapi_detail", "detail_page_parse", "search_result_only"]
    elif content_type == "table" or "/table/" in url:
        resource_type = BPSResourceType.TABLE
        candidates = ["static_table_detail", "webapi_structured", "search_result_only"]
    else:
        resource_type = BPSResourceType.UNKNOWN
        candidates = ["search_result_only"]

    return BPSResolvedResource(
        resource_type=resource_type,
        title=title,
        url=url,
        domain_code=domain_code,
        retrieval_candidates=candidates,
        metadata=result,
    )
```

- [ ] **Step 3: Implement the shared normalized response builder**

```python
def build_normalized_response(
    *,
    query: str,
    resource_type: str,
    domain_code: str,
    title: str,
    source_url: str,
    retrieval_method: str,
    rows: list[dict] | None = None,
    columns: list[str] | None = None,
    metadata: dict | None = None,
    errors: list[dict] | None = None,
) -> dict:
    return {
        "query": query,
        "resource_type": resource_type,
        "domain_code": domain_code,
        "domain_name": (metadata or {}).get("domain_name", ""),
        "title": title,
        "summary": (metadata or {}).get("summary", ""),
        "period": (metadata or {}).get("period"),
        "source_url": source_url,
        "retrieval_method": retrieval_method,
        "confidence": (metadata or {}).get("confidence", "medium"),
        "metadata": metadata or {},
        "columns": columns or [],
        "rows": rows or [],
        "artifacts": (metadata or {}).get("artifacts", []),
        "errors": errors or [],
    }
```

- [ ] **Step 4: Run the new resolution and normalization tests**

Run: `pytest tests/test_bps_resolution.py -q`
Expected: pass.

- [ ] **Step 5: Export shared BPS symbols if package-level import coverage needs it**

```python
from mini_agent.bps_models import BPSResolvedResource, BPSResourceType
```

- [ ] **Step 6: Re-run the focused suite**

Run: `pytest tests/test_bps_parser.py tests/test_bps_resolution.py tests/test_bps_orchestrator.py -q`
Expected: parser and orchestrator tests still failing, resolution tests passing.

### Task 3: Harden Table Retrieval and Introduce the AllStats-First Orchestrator

**Files:**
- Modify: `mini_agent/bps_data_retriever.py`
- Create: `mini_agent/bps_orchestrator.py`
- Modify: `mini_agent/allstats_client.py`

- [ ] **Step 1: Refactor table parsing into reusable, deterministic helpers**

```python
def _normalize_cell(text: str) -> str:
    return " ".join(text.replace("\xa0", " ").split()).strip()


def _row_to_record(headers: list[str], row: list[str]) -> dict[str, str]:
    return {
        header: row[index]
        for index, header in enumerate(headers)
        if index < len(row)
    }
```

- [ ] **Step 2: Implement robust table-result normalization in `BPSDataRetriever`**

```python
return BPSDataResult(
    table_id=table_id,
    title=title,
    subject=subject,
    update_date=update_date,
    headers=headers,
    data=[_row_to_record(headers, row) for row in raw_rows],
    raw_rows=raw_rows,
    source="webapi",
)
```

- [ ] **Step 3: Implement the orchestrator that always starts from AllStats**

```python
class BPSOrchestrator:
    def __init__(self, search_client, resolver, retriever):
        self._search_client = search_client
        self._resolver = resolver
        self._retriever = retriever

    async def answer_query(self, query: str, domain: str = "5300", content: str = "all") -> dict:
        search_response = await self._search_client.search(
            keyword=query,
            domain=domain,
            content=content,
        )
        first_result = search_response.results[0]
        resolved = self._resolver(first_result.__dict__ if hasattr(first_result, "__dict__") else first_result)
        return await self._retriever(query=query, resolved=resolved)
```

- [ ] **Step 4: Add retrieval logic for table and metadata-first resources**

```python
if resolved.resource_type is BPSResourceType.TABLE:
    table_id = resolved.identifiers.get("table_id")
    table = await self._table_retriever.get_table_data(int(table_id), domain=resolved.domain_code)
    return build_normalized_response(
        query=query,
        resource_type=resolved.resource_type.value,
        domain_code=resolved.domain_code,
        title=table.title,
        source_url=resolved.url,
        retrieval_method="static_table_detail",
        rows=table.data,
        columns=table.headers,
        metadata={"summary": table.summary()},
    )
```

- [ ] **Step 5: Add a small `AllStatsClient` adapter convenience if orchestration needs a dict-safe result**

```python
def to_dict(self) -> dict[str, object]:
    return {
        "title": self.title,
        "url": self.url,
        "snippet": self.snippet,
        "content_type": self.content_type,
        "domain_name": self.domain_name,
        "domain_code": self.domain_code,
        "year": self.year,
        "metadata": self.metadata,
    }
```

- [ ] **Step 6: Run the orchestrator-focused suite**

Run: `pytest tests/test_bps_parser.py tests/test_bps_orchestrator.py -q`
Expected: pass.

### Task 4: Route MCP Tool Functions Through the Shared Pipeline

**Files:**
- Modify: `mini_agent/bps_mcp_server.py`
- Create: `tests/test_bps_mcp_server.py`

- [ ] **Step 1: Write failing MCP contract tests for JSON-safe tool output**

```python
import json
import pytest

from mini_agent import bps_mcp_server


@pytest.mark.asyncio
async def test_bps_answer_query_returns_normalized_json(monkeypatch):
    async def fake_answer_query(**kwargs):
        return {"query": "inflasi", "resource_type": "table", "rows": [{"nilai": 1.2}]}

    monkeypatch.setattr(bps_mcp_server, "_answer_query", fake_answer_query)

    raw = await bps_mcp_server.bps_answer_query("inflasi", domain="5300")
    payload = json.loads(raw)

    assert payload["success"] is True
    assert payload["data"]["resource_type"] == "table"
```

- [ ] **Step 2: Run the MCP contract test to verify it fails**

Run: `pytest tests/test_bps_mcp_server.py::test_bps_answer_query_returns_normalized_json -q`
Expected: fail because `bps_answer_query` is not implemented yet.

- [ ] **Step 3: Introduce a single orchestrator factory in the MCP module**

```python
def create_orchestrator(api_key: str | None = None) -> BPSOrchestrator:
    search_client = AllStatsClient(headless=True, search_delay=3)
    data_retriever = BPSDataRetriever(api_key=api_key or DEFAULT_API_KEY)
    return BPSOrchestrator.from_runtime(
        search_client=search_client,
        data_retriever=data_retriever,
    )
```

- [ ] **Step 4: Implement `bps_answer_query` on top of the shared orchestrator**

```python
async def bps_answer_query(
    keyword: str,
    domain: str = "5300",
    content: str = "all",
    api_key: str | None = None,
) -> str:
    orchestrator = create_orchestrator(api_key)
    result = await orchestrator.answer_query(keyword, domain=domain, content=content)
    return success_response(result, f"Retrieved {result['resource_type']} for '{keyword}'")
```

- [ ] **Step 5: Refactor table-search helpers to reuse the shared retrieval code**

```python
async def bps_search_and_get_data(
    keyword: str,
    domain: str = "5300",
    max_tables: int = 3,
    format: str = "json",
    api_key: str | None = None,
) -> str:
    orchestrator = create_orchestrator(api_key)
    result = await orchestrator.answer_query(keyword, domain=domain, content="table")
    return success_response(result, "AllStats-first retrieval completed")
```

- [ ] **Step 6: Run MCP and orchestrator tests**

Run: `pytest tests/test_bps_mcp_server.py tests/test_bps_orchestrator.py -q`
Expected: pass.

### Task 5: Fix Configuration Drift and Run Verification

**Files:**
- Modify: `mini_agent/config.py`
- Modify: `mini_agent/config/config-example.yaml`
- Modify: `mini_agent/config/mcp-example.json`
- Modify: `mini_agent/config/system_prompt.md`
- Modify: `README.md`

- [ ] **Step 1: Write failing config-path tests if current behavior mismatches BPS docs**

```python
from pathlib import Path

from mini_agent.config import Config


def test_find_config_file_checks_bps_user_directory(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    config_dir = tmp_path / ".mini-agent-bps" / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "config.yaml").write_text("api_key: test\n")

    found = Config.find_config_file("config.yaml")

    assert found == config_dir / "config.yaml"
```

- [ ] **Step 2: Run the config test to verify it fails**

Run: `pytest tests/test_config_bps.py::test_find_config_file_checks_bps_user_directory -q`
Expected: fail because runtime still prefers `.mini-agent`.

- [ ] **Step 3: Implement config-path and naming alignment**

```python
user_config = Path.home() / ".mini-agent-bps" / "config" / filename
legacy_user_config = Path.home() / ".mini-agent" / "config" / filename
if user_config.exists():
    return user_config
if legacy_user_config.exists():
    return legacy_user_config
```

- [ ] **Step 4: Align example config keys and docs with the BPS runtime**

```yaml
bps_api_key: "YOUR_BPS_API_KEY_HERE"
bps_default_domain: "5300"
bps_search_delay: 3
bps_candidate_limit: 5
```

- [ ] **Step 5: Run the full automated verification suite**

Run: `pytest tests/test_bps_parser.py tests/test_bps_resolution.py tests/test_bps_orchestrator.py tests/test_bps_mcp_server.py tests/test_config_bps.py -q`
Expected: all pass.

- [ ] **Step 6: Run a broader regression slice**

Run: `pytest tests/test_tools.py tests/test_mcp.py tests/test_bash_tool.py tests/test_bps_parser.py tests/test_bps_resolution.py tests/test_bps_orchestrator.py tests/test_bps_mcp_server.py tests/test_config_bps.py -q`
Expected: all selected tests pass.

- [ ] **Step 7: Run live smoke verification with real upstreams**

Run: `BPS_API_KEY="$BPS_API_KEY" pytest tests/test_bps_live_smoke.py -q -m live`
Expected: pass for AllStats search, a representative WebAPI retrieval, and one end-to-end query.

- [ ] **Step 8: Review the final diff and summarize production readiness gaps if any remain**

Run: `git status --short && git diff --stat`
Expected: only intentional BPS implementation, config, docs, and test changes remain.
