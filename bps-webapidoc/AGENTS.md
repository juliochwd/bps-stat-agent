<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# bps-webapidoc

## Purpose
Comprehensive documentation and test results for the BPS (Badan Pusat Statistik) Indonesia Web API. Serves as the authoritative reference for all BPS API endpoints, parameters, and response formats used by the agent.

## Key Files
| File | Description |
|------|-------------|
| `webapidoc.md` | Original BPS WebAPI documentation (endpoint reference) |
| `BPS_WEBAPI_COMPREHENSIVE.md` | Comprehensive API documentation with all endpoints and parameters |
| `BPS_WEBAPI_COMPLETE_MAPPING.md` | Complete mapping of API endpoints to agent tool implementations |
| `BPS_WEBAPI_TEST_RESULTS.md` | API endpoint test results and validation status |

## For AI Agents

### Working In This Directory
- This is the REFERENCE for BPS API integration — consult when modifying `mini_agent/bps_*.py` modules
- `BPS_WEBAPI_COMPLETE_MAPPING.md` maps API endpoints → agent tools (most useful for development)
- `BPS_WEBAPI_TEST_RESULTS.md` documents which endpoints are verified working
- Update test results when BPS API behavior changes
- BPS API base URL: `https://webapi.bps.go.id/v1/api/`

### Key API Domains
- Domain/subject/variable listing and search
- Statistical data tables (statictable, dynamictable)
- Publications and press releases
- SDG indicators
- Census data (SIMDASI)
- Strategic indicators

## Dependencies

### Internal
- Referenced by `mini_agent/bps_api.py`, `mini_agent/bps_mcp_server.py`

### External
- None (static documentation)

<!-- MANUAL: -->
