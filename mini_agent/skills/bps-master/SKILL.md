# BPS Master Agent Skill

## Overview
BPS (Badan Pusat Statistik) Indonesia data retrieval agent. Provides access to all BPS statistical data via WebAPI and AllStats Search Engine.

## Architecture

### Two Data Sources
1. **BPS AllStats Search Engine** (`searchengine.web.bps.go.id`) — via Playwright
   - Search-only, bypasses Cloudflare protection
   - Returns: title, URL, snippet, content_type
   - URL: `https://searchengine.web.bps.go.id/search?mfd={domain}&q={keyword}&content={type}&page={page}&sort={sort}`

2. **BPS WebAPI** (`webapi.bps.go.id`) — direct HTTP
   - Structured data: indicators, publications, subjects, etc.
   - Requires API key
   - Status: WAF-blocked from some IPs

### Domain Codes
- `0000` = Nasional (National)
- `5300` = Nusa Tenggara Timur (NTT Province)
- Other provinces: 1100=Aceh, 1200=Sumatera Utara, 3100=DKI Jakarta, etc.

## Quick Usage

```python
from mini_agent.allstats_client import AllStatsClient
from dataclasses import asdict

async def search_bps():
    client = AllStatsClient(headless=True)
    try:
        # Search for inflation data in NTT
        response = await client.search(
            keyword="inflasi",
            domain="5300",
            content="all"  # all/publication/table/pressrelease/infographic
        )

        for r in response.results:
            print(f"{r.title}")
            print(f"  URL: {r.url}")
            print(f"  Type: {r.content_type}")

        return [asdict(r) for r in response.results]
    finally:
        await client.close()
```

## Content Types for Search

| Type | BPS Product |
|------|------------|
| `all` | Semua tipe |
| `publication` | Publikasi |
| `table` | Tabel Statistik |
| `pressrelease` | Berita Resmi Statistik (BRS) |
| `infographic` | Infografis |
| `microdata` | Data Mikro |
| `news` | Berita |
| `glosarium` | Glosarium |

## Search URL Parameters

```
mfd     = Domain code (5300=NTT, 0000=nasional)
q       = Keyword (use + for spaces: "data+inflasi")
content = Content type filter
page    = Page number (default 1)
sort    = Sort: terbaru (newest), terlama (oldest), relevansi (relevance)
title   = 0 (search everywhere)
from    = start date filter
to      = end date filter
```

## BPS WebAPI - Complete Endpoint Coverage

### 55+ MCP Tools Available

#### Domain & Province
| Tool | Description |
|------|-------------|
| `bps_list_domains` | List all BPS domains (provinces, cities) |
| `bps_list_provinces` | List all province domains |
| `bps_year_to_th` | Convert year to BPS time period ID |
| `bps_list_years` | List available years for a variable |

#### Subject & Categories
| Tool | Description |
|------|-------------|
| `bps_list_subjects` | List statistical subjects |
| `bps_list_subject_categories` | List subject categories (subjek) |

#### Variables & Data
| Tool | Description |
|------|-------------|
| `bps_get_variables` | List variables in a subject |
| `bps_list_periods` | List available time periods (tahun) |
| `bps_list_vertical_variables` | List regional breakdowns (kabupaten/kota) |
| `bps_list_derived_variables` | List derived variables (sub-categories) |
| `bps_list_derived_periods` | List monthly/quarterly periods |
| `bps_list_units` | List units of measurement |
| `bps_get_data` | Get raw dynamic data values |
| `bps_get_decoded_data` | Get decoded data with region labels |

#### Search
| Tool | Description |
|------|-------------|
| `bps_search` | Search static tables via WebAPI |
| `bps_search_allstats` | Search via AllStats (Playwright, bypasses Cloudflare) |
| `bps_search_ntt` | Convenience: search for NTT (domain 5300) |
| `bps_search_nasional` | Convenience: search national (domain 0000) |
| `bps_search_and_get_data` | Complete flow: search + retrieve actual data |
| `bps_answer_query` | AllStats-first query pipeline with AI answer |

#### Table Data
| Tool | Description |
|------|-------------|
| `bps_get_table_data` | Get actual data from static table |
| `bps_list_dynamic_tables` | List dynamic tables |
| `bps_get_dynamic_table_detail` | Get dynamic table detail |

#### Publications & Press Releases
| Tool | Description |
|------|-------------|
| `bps_get_press_releases` | List BPS press releases (BRS) |
| `bps_get_publications` | List BPS publications |

#### News & Media
| Tool | Description |
|------|-------------|
| `bps_list_news_categories` | List news categories |
| `bps_get_news_detail` | Get news article detail |

#### Indicators & Infographics
| Tool | Description |
|------|-------------|
| `bps_get_indicators` | Get strategic indicators |
| `bps_list_infographics` | List infographics |
| `bps_get_infographic_detail` | Get infographic detail |

#### Glossary
| Tool | Description |
|------|-------------|
| `bps_list_glossary` | List glossary terms |
| `bps_get_glossary_detail` | Get glossary term detail |

#### SDGs & SDDS
| Tool | Description |
|------|-------------|
| `bps_list_sdgs` | List SDGs indicators (by goal 1-17) |
| `bps_list_sdds` | List SDDS indicators |

#### Census Data
| Tool | Description |
|------|-------------|
| `bps_get_census_topics` | Get census topics |
| `bps_get_census_areas` | Get census areas (wilayah sensus) |
| `bps_get_census_datasets` | Get available census datasets |
| `bps_get_census_data` | Get actual census microdata |

#### SIMDASI Data
| Tool | Description |
|------|-------------|
| `bps_get_simdasi_regencies` | Get regency MFD codes |
| `bps_get_simdasi_districts` | Get district MFD codes |
| `bps_get_simdasi_subjects` | Get SIMDASI subjects by area |
| `bps_get_simdasi_master_tables` | List master tables |
| `bps_get_simdasi_table_detail` | Get table detail with data |
| `bps_get_simdasi_tables_by_area` | Get tables by area |
| `bps_get_simdasi_tables_by_area_and_subject` | Get tables by area + subject |
| `bps_get_simdasi_master_table_detail` | Get master table detail |

#### CSA (Custom Statistical Areas)
| Tool | Description |
|------|-------------|
| `bps_list_csa_categories` | List CSA categories |
| `bps_list_csa_subjects` | List CSA subjects |
| `bps_list_csa_tables` | List CSA table statistics |
| `bps_get_csa_table_detail` | Get CSA table detail |

#### Classifications
| Tool | Description |
|------|-------------|
| `bps_list_kbli` | List KBLI codes (ISIC-based, 2009/2015/2017/2020) |
| `bps_get_kbli_detail` | Get KBLI classification detail |
| `bps_list_kbki` | List KBKI codes (commodity classification) |
| `bps_get_kbki_detail` | Get KBKI classification detail |

#### Foreign Trade
| Tool | Description |
|------|-------------|
| `bps_get_foreign_trade` | Get export/import data (dataexim) |

## Installation

```bash
cd /home/ubuntu/Mini-Agent
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/playwright install chromium
```

## Running as MCP Server

```bash
# Via uvx (recommended)
uvx --from git+https://github.com/MiniMax-AI/mini-agent-bps.git bps-mcp-server

# Or directly
python -m mini_agent.bps_mcp_server
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `BPS_API_KEY` | BPS WebAPI key |
| `WEBAPI_APP_ID` | Alternative API key variable |

## WAF Bypass Notes

Some SIMDASI regional endpoints (id/27, id/28, id/29) are blocked by BPS LTM WAF when using regional parameters. Workarounds:
- Use Census data (id/41) instead of blocked SIMDASI endpoints
- Use wilayah=0000000 (national) instead of regional codes
- AllStats search works through Cloudflare

## Verified Working (2026-04-24)

✅ All 55+ MCP tools implemented and registered
✅ AllStats search with Playwright (10 results per page)
✅ Domain filtering (5300=NTT, 0000=National)
✅ Content type filtering
✅ Title/snippet extraction
✅ Full BPS WebAPI coverage
