# mini-agent-bps: BPS Statistical Data Assistant

**Objective:** Fork Mini-Agent into a specialized BPS data query agent that uses BPS WebAPI and BPS Search Engine as its primary information sources.

**Last Updated:** 2026-04-23

---

## Context

### Source Project: Mini-Agent
- **Location:** `./Mini-Agent/`
- **Architecture:** Full agent execution loop with persistent memory, intelligent context management, Claude Skills integration, MCP tool support
- **Entry point:** `mini_agent.cli:main`
- **Token limit:** 80,000 (auto-summarize)
- **Key files:** `agent.py`, `cli.py`, `config.py`, `llm/anthropic_client.py`

### Source Project: byps-agent BPS Tools (Reference)
- **Location:** `/home/ubuntu/byps-agent/`
- **WebAPI:** 67 endpoints across full_tools, detail_endpoints, missing_endpoints
- **Search Engine:** Playwright-based scraper for `searchengine.web.bps.go.id`
- **BPS Products:** Publikasi, Berita Resmi Statistik, Subjek, Tabel Dinamis, Sensus, Ekspor Impor, Direktori, Infografik, Berita, Metadata (10 products)

---

## Target: mini-agent-bps Architecture

### Core Change
Replace Mini-Agent's general-purpose agent capabilities with BPS-specific knowledge, tools, and workflows.

### New Directory Structure
```
mini-agent-bps/
├── SKILL.md                          # Main BPS agent skill
├── mini_agent/
│   ├── agent.py                      # Core agent (modified for BPS)
│   ├── cli.py                        # CLI entry point (modified)
│   ├── config.py                     # Config (BPS-specific defaults)
│   └── skills/
│       ├── bps-webapi/               # BPS WebAPI skill
│       │   ├── SKILL.md
│       │   ├── scripts/
│       │   │   ├── bps_client.py     # WebApiClient wrapper
│       │   │   └── domain_cache.py   # Domain/kode wilayah cache
│       │   └── references/
│       │       ├── endpoints.md      # Complete endpoint reference
│       │       ├── bps_products.md   # 10 BPS products guide
│       │       ├── domain_codes.md  # All 34 provinces + kab/kota
│       │       └── query_recipes.md # Common data retrieval patterns
│       ├── bps-searchengine/         # BPS Search Engine skill
│       │   ├── SKILL.md
│       │   ├── scripts/
│       │   │   └── search_scraper.py # Playwright scraper wrapper
│       │   └── references/
│       │       └── search_guide.md   # Search usage guide
│       └── bps-context/              # BPS domain knowledge skill
│           ├── SKILL.md
│           └── references/
│               ├── CSA_categories.md # Subject categories
│               ├── SDGs_vars.md      # SDG indicators
│               ├── SDDS_vars.md      # SDDS indicators
│               ├── ntt_data.md       # NTT provincial data guide
│               └── glosarium.md     # Statistical glossary
├── byps-agent-reference/
│   ├── src/tools/webapi/              # Reference: byps-agent WebAPI tools
│   ├── src/tools/searchengine/        # Reference: byps-agent search tools
│   └── docs/                         # Reference: BPS API docs
└── tests/
    └── test_bps_queries.py           # BPS-specific query tests
```

---

## Implementation Phases

### Phase 1: Setup & Core Skills (Day 1)

**1.1 Initialize mini-agent-bps from Mini-Agent**
```bash
cp -r Mini-Agent mini-agent-bps
cd mini-agent-bps
# Remove unnecessary skills (keep skill-creator for future)
rm -rf mini_agent/skills/document-skills
rm -rf mini_agent/skills/mcp-builder
rm -rf mini_agent/skills/slack-gif-creator
rm -rf mini_agent/skills/webapp-testing
```

**1.2 Create bps-webapi skill**
- SKILL.md: WebAPI usage instructions
- scripts/bps_client.py: WebApiClient based on byps-agent client
  - 67 endpoints: domain, subject, subcat, var, vervar, th, turvar, turth, unit, data, static tables, publications, press releases, news, infographics, glossary, SDGs, SDDS, KBLI, census, SIMDASI, search
  - Support domain codes: 0000 (pusat), 1100-9400 (provinces), kab/kota codes
- references/endpoints.md: Complete endpoint reference from byps-agent docs
- references/bps_products.md: 10 BPS products with API methods
- references/domain_codes.md: All domain codes (34 provinces + kab/kota)
- references/query_recipes.md: Common patterns (inflation, PDRB, poverty rate, etc.)

**1.3 Create bps-searchengine skill**
- SKILL.md: Search engine usage instructions
- scripts/search_scraper.py: Playwright-based scraper based on byps-agent searchengine tools
  - bps_search_allstats: Search 1.6M+ data, 236K+ publications
  - bps_search_microdata: Search 44K+ microdata variables
  - bps_search_publications_all: Cross-domain publication search
- references/search_guide.md: How to use BPS search effectively

**1.4 Create bps-context skill**
- SKILL.md: BPS domain knowledge context
- references/CSA_categories.md: Demografi, Ekonomi, Lingkungan (subcat_id 514-516)
- references/SDGs_vars.md: SDG indicators with variable IDs
- references/SDDS_vars.md: SDDS indicators
- references/ntt_data.md: NTT province data focus
- references/glosarium.md: Statistical glossary (5,078 entries)

### Phase 2: Core Agent Modification (Day 1-2)

**2.1 Modify agent.py**
- Keep core loop but add BPS-specific system prompt
- BPS agent persona: "You are a BPS statistical data assistant..."
- Remove/generalize non-BPS capabilities

**2.2 Modify cli.py**
- BPS-specific welcome message
- Pre-configured BPS API key prompt
- Example BPS queries in help

**2.3 Create bps_client.py (standalone)**
```python
# Based on byps-agent src/tools/webapi/client.py
from typing import Optional
import httpx

class BPSWebAPIClient:
    BASE_URL = "https://webapi.bps.go.id/v1/api"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=30.0)
    
    # Domain methods
    async def get_domains(self, type: str = "all") -> dict
    async def get_provinces(self) -> dict
    async def get_regencies(self, prov_id: str) -> dict
    
    # Subject/Category methods
    async def get_subjects(self, domain: str, **kwargs) -> dict
    async def get_subject_categories(self, domain: str) -> dict
    async def get_variables(self, domain: str, subject: int, **kwargs) -> dict
    
    # Dynamic Data methods
    async def get_data(self, domain: str, var: int, th: int, **kwargs) -> dict
    async def get_periods(self, domain: str, var: int) -> dict
    async def get_vertical_variables(self, domain: str, var: int) -> dict
    async def get_derived_variables(self, domain: str, var: int) -> dict
    async def get_derived_periods(self, domain: str, var: int) -> dict
    async def get_units(self, domain: str) -> dict
    
    # Content methods
    async def get_publications(self, domain: str, **kwargs) -> dict
    async def get_press_releases(self, domain: str, **kwargs) -> dict
    async def get_news(self, domain: str, **kwargs) -> dict
    async def get_infographics(self, domain: str, **kwargs) -> dict
    async def get_glossary(self, domain: str) -> dict
    
    # Special data
    async def get_sdgs(self, **kwargs) -> dict
    async def get_sdds(self) -> dict
    async def get_census_data(self, kegiatan: str, **kwargs) -> dict
    async def get_exim_data(self, sumber: int, **kwargs) -> dict
    
    # Search
    async def search(self, keyword: str, domain: Optional[str] = None) -> dict
```

**2.4 Modify config.py**
- Default BPS API key from env: `WEBAPI_APP_ID`
- Default domain: 0000 (national)
- Optional: NTT domain preset (5300)

### Phase 3: Integration & Testing (Day 2)

**3.1 Wire bps_client into agent tools**
- Create BPS tool class that wraps bps_client methods
- Register tools with Mini-Agent tool system

**3.2 Create test suite**
```python
# tests/test_bps_queries.py
import pytest
from mini_agent_bps.bps_client import BPSWebAPIClient

@pytest.fixture
def client():
    return BPSWebAPIClient(api_key=os.getenv("WEBAPI_APP_ID"))

async def test_get_ntt_subjects(client):
    result = await client.get_subjects(domain="5300")
    assert result["status"] == "OK"
    assert len(result["data"][1]) > 0

async def test_get_ntt_pdrb(client):
    # Get PDRB variables
    vars = await client.get_variables(domain="5300", subject=1)
    # Get periods
    periods = await client.get_periods(domain="5300", var=pdrb_var_id)
    # Get data
    data = await client.get_data(domain="5300", var=pdrb_var_id, th=latest_period)
    assert data["status"] == "OK"
```

**3.3 Create example queries**
```python
# examples/bps_queries.py
EXAMPLES = [
    "Berapa angka kemiskinan di NTT tahun 2024?",
    "Tampilkan PDRB kabupaten/kota se-NTT tahun 2023",
    "Cari data inflasi nasional 5 tahun terakhir",
    "Apa saja indikator SDGs untuk kesehatan?",
    "Dapatkan daftar publikasi BPS NTT terbaru",
    "Cari data ekspor-impor Sulawesi tahun 2023",
]
```

---

## BPS WebAPI Endpoint Summary

### Base URL
`https://webapi.bps.go.id/v1/api/`

### Authentication
- API Key: Query parameter `key`
- Get from: https://webapi.bps.go.id/developer
- NTT dev key (reference): `80a6bd62b0007e3c9f685346544e6afa`

### All Endpoints

| Category | Endpoint | Model/Method | Key Params |
|----------|----------|--------------|------------|
| **Domain** | `/v1/api/domain` | GET | type (all/prov/kab/kabbyprov), prov |
| **Subject** | `/v1/api/list` | GET | model=subject, domain, subcat, lang |
| **Subcategory** | `/v1/api/list` | GET | model=subcat, domain, lang |
| **Variable** | `/v1/api/list` | GET | model=var, domain, subject, year |
| **Period** | `/v1/api/list` | GET | model=th, domain, var |
| **Vertical Var** | `/v1/api/list` | GET | model=vervar, domain, var |
| **Derived Var** | `/v1/api/list` | GET | model=turvar, domain, var |
| **Derived Period** | `/v1/api/list` | GET | model=turth, domain, var |
| **Unit** | `/v1/api/list` | GET | model=unit, domain |
| **Data** | `/v1/api/list` | GET | model=data, domain, var, th, vervar, turvar, turth |
| **Publications** | `/v1/api/list` | GET | model=publication, domain, keyword, year |
| **Press Releases** | `/v1/api/list` | GET | model=pressrelease, domain, keyword, year |
| **News** | `/v1/api/list` | GET | model=news, domain, keyword, year |
| **News Categories** | `/v1/api/list` | GET | model=newscategory, domain |
| **Static Tables** | `/v1/api/list` | GET | model=statictable, domain, keyword |
| **Indicators** | `/v1/api/list` | GET | model=indicators, domain |
| **Infographics** | `/v1/api/list` | GET | model=infographic, domain |
| **Glossary** | `/v1/api/list` | GET | model=glosarium, domain |
| **SDGs** | `/v1/api/list` | GET | model=sdgs, domain |
| **SDDS** | `/v1/api/list` | GET | model=sdds, domain |
| **KBLI** | `/v1/api/list` | GET | model=kbli2020, year, level |
| **CSA Categories** | `/v1/api/list` | GET | model=subcatcsa, domain |
| **CSA Subjects** | `/v1/api/list` | GET | model=subjectcsa, domain, subcat |
| **Census** | `/v1/api/interoperabilitas/datasource/sensus/id/{id}` | GET | id=37-41 |
| **SIMDASI** | `/v1/api/interoperabilitas/datasource/simdasi/id/{id}` | GET | id=22-28 |
| **Export/Import** | `/v1/api/dataexim` | GET | sumber, kodehs, tahun, jenishs |
| **Search** | `/v1/api/list` | GET | model=search, keyword, domain |

### Key Domain Codes

| Code | Name | Type |
|------|------|------|
| 0000 | Pusat (National) | National |
| 5300 | Nusa Tenggara Timur | Province |
| 5301 | Kabupaten Kupang | Regency |
| 5302 | Kabupaten Timor Tengah Selatan | Regency |
| ... | ... | ... |
| 5371 | Kota Kupang | City |

**All province codes:** 1100, 1200, 3100, 3200, 3300, 3400, 3500, 3600, 5100, 5200, 5300, 6100-6500, 7100-7600, 8100-8200, 9100-9400

---

## Common Query Patterns (Query Recipes)

### 1. Get Province Statistics (e.g., NTT Poverty Rate)
```
Step 1: Get subjects for domain 5300
Step 2: Find "Kemiskinan" subject
Step 3: Get variables for that subject
Step 4: Get periods
Step 5: Get data with vervar for each kabupaten
```

### 2. Get Inflation Data (National)
```
GET /v1/api/list?model=indicators&domain=0000&keyword=inflasi
```

### 3. Get PDRB by Regency
```
Step 1: GET /v1/api/list?model=var&domain=5300&subject=1&keyword=PDRB
Step 2: GET /v1/api/list?model=vervar&domain=5300&var={var_id}
Step 3: GET /v1/api/list?model=th&domain=5300&var={var_id}
Step 4: GET /v1/api/list?model=data&domain=5300&var={var_id}&th={th_id}&vervar={vervar_id}
```

### 4. Get SDGs Indicators
```
GET /v1/api/list?model=sdgs&domain=0000
GET /v1/api/list?model=data&domain=0000&var=192&th={th_id}&vervar=9999
```

---

## Success Metrics

1. Agent can answer "Tunjukkan data kemiskinan NTT 5 tahun terakhir" without manual API calls
2. Agent can navigate BPS WebAPI structure autonomously
3. Agent can use BPS Search Engine to find relevant data
4. Agent has BPS domain knowledge (CSA categories, SDGs, SDDS) in context
5. All 10 BPS products accessible via agent tools

---

## Files to Create/Modify

### New Files
- `mini-agent-bps/SKILL.md`
- `mini-agent-bps/mini_agent/skills/bps-webapi/SKILL.md`
- `mini-agent-bps/mini_agent/skills/bps-webapi/scripts/bps_client.py`
- `mini-agent-bps/mini_agent/skills/bps-webapi/scripts/domain_cache.py`
- `mini-agent-bps/mini_agent/skills/bps-webapi/references/endpoints.md`
- `mini-agent-bps/mini_agent/skills/bps-webapi/references/bps_products.md`
- `mini-agent-bps/mini_agent/skills/bps-webapi/references/domain_codes.md`
- `mini-agent-bps/mini_agent/skills/bps-webapi/references/query_recipes.md`
- `mini-agent-bps/mini_agent/skills/bps-searchengine/SKILL.md`
- `mini-agent-bps/mini_agent/skills/bps-searchengine/scripts/search_scraper.py`
- `mini-agent-bps/mini_agent/skills/bps-searchengine/references/search_guide.md`
- `mini-agent-bps/mini_agent/skills/bps-context/SKILL.md`
- `mini-agent-bps/mini_agent/skills/bps-context/references/CSA_categories.md`
- `mini-agent-bps/mini_agent/skills/bps-context/references/SDGs_vars.md`
- `mini-agent-bps/mini_agent/skills/bps-context/references/SDDS_vars.md`
- `mini-agent-bps/mini_agent/skills/bps-context/references/ntt_data.md`
- `mini-agent-bps/mini_agent/skills/bps-context/references/glosarium.md`
- `mini-agent-bps/mini_agent/bps_client.py`
- `mini-agent-bps/examples/bps_queries.py`
- `mini-agent-bps/tests/test_bps_queries.py`

### Modified Files
- `mini-agent-bps/mini_agent/agent.py` (BPS system prompt)
- `mini-agent-bps/mini_agent/cli.py` (BPS welcome message)
- `mini-agent-bps/mini_agent/config.py` (BPS defaults)
- `mini-agent-bps/mini_agent/__init__.py` (export bps_client)

### Reference Files (from byps-agent)
- Copy from `/home/ubuntu/byps-agent/webapidoc.md`
- Copy from `/home/ubuntu/byps-agent/docs/BPS_WEBAPI_COMPLETE_MAPPING.md`
- Copy from `/home/ubuntu/byps-agent/docs/guides/BPS_WEBAPI_COMPREHENSIVE.md`
- Copy from `/home/ubuntu/byps-agent/src/tools/webapi/client.py`
- Copy from `/home/ubuntu/byps-agent/src/tools/searchengine/` tools

---

## Execution Commands

```bash
# Phase 1: Setup
cp -r Mini-Agent mini-agent-bps
cd mini-agent-bps
rm -rf mini_agent/skills/document-skills
rm -rf mini_agent/skills/mcp-builder
rm -rf mini_agent/skills/slack-gif-creator
rm -rf mini_agent/skills/webapp-testing

# Phase 2: Create skills directory structure
mkdir -p mini_agent/skills/bps-webapi/{scripts,references}
mkdir -p mini_agent/skills/bps-searchengine/{scripts,references}
mkdir -p mini_agent/skills/bps-context/references
mkdir -p examples tests

# Phase 3: Build bps_client
# (create mini_agent/bps_client.py based on byps-agent client)

# Phase 4: Create skills
# (populate SKILL.md and references/ from byps-agent docs)

# Phase 5: Modify core files
# (agent.py, cli.py, config.py for BPS-specific behavior)

# Phase 6: Test
WEBAPI_APP_ID=your_api_key python -m mini_agent.cli
```
