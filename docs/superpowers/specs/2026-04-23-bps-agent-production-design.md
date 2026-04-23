# BPS Agent Production Design

**Date:** 2026-04-23
**Project:** `Mini-Agent`
**Scope:** Production-ready BPS data agent with AllStats-first discovery and multi-source retrieval fallback

## Goal

Build a production-ready BPS agent that always starts data discovery with the BPS AllStats Search Engine, then automatically selects the best available retrieval path to return structured BPS data with source provenance, consistent output, and explicit failure reporting when a resource cannot be retrieved.

## Problem Statement

The current repository already contains:

- a Playwright-based AllStats search client
- a synchronous BPS WebAPI client
- an initial data retriever for static tables
- an MCP server layer
- documentation and plans that describe broader coverage than the current verified implementation

What is still missing is a verified end-to-end system that:

- treats AllStats as the required entry point for discovery
- resolves different BPS result types into the right retrieval path
- normalizes output across data sources
- handles blocked or incomplete API paths gracefully
- is backed by focused tests and production-readiness checks

## Non-Negotiable Product Requirements

The system must:

1. Start every discovery flow from AllStats search.
2. Support BPS data access beyond NTT; NTT is the default domain, not the only domain.
3. Use the best retrieval path automatically after search results are found.
4. Prefer structured BPS WebAPI data when it is available and complete.
5. Fall back to detail pages, static table detail pages, and parsers when WebAPI list output is incomplete.
6. Return structured results with provenance, including source URL, domain, retrieval method, and confidence.
7. Never silently hallucinate missing values; failures must be explicit.
8. Be testable end-to-end with deterministic unit coverage around resolution and normalization logic.

## Constraints

### External Constraints

- BPS WebAPI has uneven behavior across models and parameters.
- Some documented interoperability and SIMDASI surfaces can trigger WAF protection.
- Search pages and detail pages may change HTML structure over time.
- Playwright search is slower and more failure-prone than direct HTTP, so retries and rate limits must be deliberate.

### Repository Constraints

- The repository already has partially implemented BPS modules that should be refined rather than replaced wholesale.
- Existing `Mini-Agent` architecture, CLI, config loading, and MCP loading patterns should be preserved unless a targeted change is necessary.
- Existing unrelated user changes in the worktree must remain untouched.

## Success Criteria

The implementation is successful when all of the following are true:

- AllStats search works as the first-step discovery mechanism.
- Search results can be resolved into a typed internal resource model.
- At least these retrieval flows are implemented and tested:
  - static table detail retrieval
  - publication listing/detail retrieval
  - press release listing/detail retrieval
  - subject/variable/data WebAPI retrieval
- a single end-to-end orchestration path can answer a query by chaining search, resolution, retrieval, and normalization
- MCP-exposed tools return machine-usable JSON and human-usable summaries
- configuration, API key handling, and runtime failures are validated and surfaced cleanly
- the repository contains BPS-focused tests that prove the supported paths work

## Recommended Architecture

### 1. Search Layer

The `AllStatsClient` remains the mandatory discovery entry point.

Responsibilities:

- execute keyword search with domain, content, page, and sort controls
- enforce rate limiting and retry policy
- parse raw search cards into normalized search results
- expose enough metadata for downstream resolution

Output contract:

- `title`
- `url`
- `snippet`
- `content_type`
- `domain_code`
- `domain_name`
- optional metadata extracted from result cards

### 2. Resolution Layer

Add a resource resolution layer that converts a search result into a typed retrieval plan.

Responsibilities:

- classify result types into one of:
  - `table`
  - `publication`
  - `pressrelease`
  - `news`
  - `infographic`
  - `glossary`
  - `subject_data`
  - `unknown`
- infer identifiers when possible from URLs or metadata
- determine the best retrieval strategy in ranked order

Retrieval strategy precedence:

1. `webapi_structured`
2. `webapi_detail`
3. `static_table_detail`
4. `detail_page_parse`
5. `search_result_only`

The resolution layer is the key boundary that decides whether the agent can retrieve structured data or only cite discoverable sources.

### 3. Retrieval Layer

Split data retrieval into adapters with narrow responsibilities.

#### `BPSWebAPIAdapter`

Responsibilities:

- wrap `BPSAPI`
- fetch list/view resources using safe parameter validation
- normalize inconsistent BPS response envelopes
- classify retryable vs terminal failures

Supported flows:

- domains
- subjects
- variables
- periods
- data
- static tables
- publications
- press releases
- indicators
- glossary

#### `StaticTableAdapter`

Responsibilities:

- fetch static table detail
- parse HTML table content robustly
- normalize header rows and data rows

This adapter is required because table detail output is often the highest-value structured source after discovery.

#### `AllStatsDetailAdapter`

Responsibilities:

- use search-result URLs when API detail is incomplete or unavailable
- extract document links and metadata from supported detail pages
- provide a controlled fallback path rather than raw scraping everywhere

### 4. Normalization Layer

All retrieval paths must produce a shared normalized response shape.

Canonical response fields:

- `query`
- `resource_type`
- `domain_code`
- `domain_name`
- `title`
- `summary`
- `period`
- `source_url`
- `retrieval_method`
- `confidence`
- `metadata`
- `columns`
- `rows`
- `artifacts`
- `errors`

Normalization rules:

- list-like resources still return structured metadata even when no tabular rows exist
- tabular resources must return `columns` and `rows`
- provenance is always present
- failures are accumulated in `errors` instead of being hidden

### 5. Orchestration Layer

Introduce a higher-level orchestrator that owns the end-to-end flow:

1. search AllStats
2. rank candidate results
3. resolve top candidates
4. execute best retrieval strategy
5. normalize output
6. return structured answer payload

The orchestrator must support:

- direct resource retrieval from an already selected search result
- full query answering from a raw user question
- configurable maximum candidate count
- deterministic fallback order

### 6. Tool Layer

Expose the architecture through stable tools instead of ad hoc helper functions.

Required tools:

- `bps_search`
- `bps_resolve_result`
- `bps_get_resource`
- `bps_answer_query`
- `bps_list_domains`
- `bps_list_subjects`
- `bps_get_variables`
- `bps_get_data`

Tool design requirements:

- JSON-safe return values
- explicit error payloads
- small, composable contracts
- no hidden process-wide global state beyond validated config

## Error Handling Design

Errors must be categorized so the agent and MCP consumers can act on them.

Required categories:

- `configuration_error`
- `auth_error`
- `upstream_http_error`
- `waf_blocked`
- `parse_error`
- `not_found`
- `unsupported_resource`
- `incomplete_resource`

Rules:

- upstream failures must include the attempted method and target
- parser failures must preserve enough raw context for debugging
- unsupported resources must fail fast and clearly
- timeouts and retries must stop after bounded attempts

## Caching and Rate Limiting

The production-ready baseline should include lightweight caching and request throttling.

Required behavior:

- in-process TTL cache for repeated domain/subject/detail lookups
- bounded retry behavior for Playwright and HTTP requests
- search throttling to reduce Cloudflare challenges
- no infinite retry loops

Persistent cache storage is not required for the first production-ready version.

## Configuration Design

Configuration must be explicit and validated.

Required additions or corrections:

- BPS API key source and naming must be consistent
- default BPS domain must be configurable
- search delay, timeout, candidate limit, and retry settings must be configurable
- config loading paths must be aligned with the `mini-agent-bps` naming used by scripts and docs

This resolves the current mismatch between general `Mini-Agent` config conventions and the BPS-specialized setup scripts.

## Testing Strategy

The implementation must be driven by tests before production changes.

### Unit Tests

Required coverage:

- AllStats result parsing
- resource classification and resolution
- response normalization
- static table HTML parsing
- error classification

Use fixtures and mocked upstream responses for deterministic behavior.

### Integration Tests

Required coverage:

- BPS WebAPI wrapper against representative mocked envelopes
- orchestrator flow from search result to normalized resource
- MCP tool return contracts

### Live Verification Checks

Required smoke checks after implementation:

- AllStats search for a known NTT query
- WebAPI subject/variable/data retrieval with a valid key
- static table detail retrieval and parsing
- end-to-end answer flow for at least one real query

Live checks prove runtime viability; unit and integration tests prove code stability.

## Production Readiness Definition

The first production-ready milestone does not mean universal success against every BPS surface. It means:

- supported paths are explicitly defined
- those paths are verified
- failure cases are explicit and bounded
- fallback behavior is deterministic
- the system does not silently return fabricated data

Unsupported or blocked surfaces are acceptable only if:

- they are detected clearly
- a fallback was attempted where appropriate
- the returned payload explains the limitation

## Scope Boundaries

Included in scope:

- AllStats-first query pipeline
- WebAPI-backed structured retrieval
- static table parsing
- normalized response schema
- MCP tool hardening
- BPS-specific tests
- config cleanup needed for BPS runtime

Excluded from this milestone:

- bypassing every WAF-protected BPS endpoint directly
- full OCR extraction from arbitrary PDFs
- distributed crawling of all BPS websites
- background indexing of all BPS data into a local warehouse

These may be future extensions, but they are not required for the first production-ready milestone.

## Implementation Order

The work should proceed in this order:

1. establish normalized contracts and tests
2. harden existing clients and parsers
3. add the resolution/orchestration layer
4. expose the stable tool surface
5. run integration and live verification
6. fix production-readiness gaps in config, docs, and runtime behavior

## Risks

### Risk 1: Search HTML changes

Mitigation:

- parser tests with fixtures
- narrow selectors with graceful fallback
- explicit parse errors

### Risk 2: WebAPI envelope inconsistency

Mitigation:

- centralize response unwrapping in one adapter
- build tests from captured sample responses

### Risk 3: Static table parsing fragility

Mitigation:

- isolate parser logic
- test multi-row headers and sparse cells
- preserve raw rows for debugging

### Risk 4: Config mismatch between docs, scripts, and runtime

Mitigation:

- unify config path and environment variable names
- add validation tests

## Final Recommendation

Implement an AllStats-first orchestrated BPS agent that uses WebAPI and controlled detail-page parsing as layered retrieval strategies behind a normalized response contract. This design meets the user requirement that search starts from AllStats while still maximizing structured data coverage and keeping unsupported or blocked surfaces explicit instead of hidden.
