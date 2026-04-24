---
name: bps-master
description: Retrieve BPS (Badan Pusat Statistik / Statistics Indonesia) data including inflation, GDP, PDB, population, IPM/HDI, unemployment, poverty, and census data for Indonesian provinces and national level. Use this skill whenever users ask about BPS statistics, Indonesian economic or demographic data, inflation rates, regional development indicators, BPS publications, or when needing structured data from BPS WebAPI and AllStats Search Engine. Handles both formal queries (in Indonesian or English) and casual mentions of BPS, Statistics Indonesia, or specific indicators like IPM, PDB, inflasi.
---

# BPS Master Agent Skill

This skill provides access to all BPS (Badan Pusat Statistik) Indonesia statistical data via two integrated data sources. It exposes **55+ MCP tools** for Indonesian statistical data retrieval.

## Two Data Sources

### 1. AllStats Search Engine (Playwright — bypasses Cloudflare)
Use when WebAPI is WAF-blocked or you need to discover content.

```
URL: https://searchengine.web.bps.go.id/search?mfd={domain}&q={keyword}&content={type}&page={page}
Returns: title, URL, snippet, content_type
```

### 2. BPS WebAPI (direct HTTP — requires API key)
Use for structured, paginated data retrieval.

```
Base: https://webapi.bps.go.id
Requires: BPS_API_KEY or WEBAPI_APP_ID env var
```

## Decision Tree: Which Tool to Use

```
Need specific BPS data (inflation, GDP, IPM, etc.)
├── Know the exact variable ID and period?
│   ├── YES → bps_get_data OR bps_get_decoded_data
│   └── NO  → Use AllStats-first pattern
│
AllStats-first (recommended for discovery):
1. bps_answer_query("inflasi NTT", domain="5300") → structured data with summary
   OR
1. bps_search_allstats(keyword="inflasi", domain="5300") → search results
2. Follow result URLs to get detail

Census data (sp2020, etc.):
- bps_get_census_topics(kegiatan="sp2020")
- bps_get_census_areas(kegiatan="sp2020")
- bps_get_census_datasets(kegiatan="sp2020", topik=X)

SIMDASI regional data:
- bps_get_simdasi_regencies(parent="5300000")  # 7-digit MFD code
- bps_get_simdasi_subjects(wilayah="5300000")

KBLI/KBKI classifications:
- bps_list_kbli(year=2020, level="golongan")
- bps_get_kbli_detail(kbli_id="XX", year=2020)

Foreign trade:
- bps_get_foreign_trade(sumber=1, kodehs=84, tahun="2024", periode=1, jenishs=1)
```

## Domain Codes

| Code | Province | Common Use |
|------|----------|------------|
| 0000 | Nasional | National GDP, national indicators |
| 5300 | Nusa Tenggara Timur (NTT) | Provincial inflation, HDI, employment |
| 1100-7700 | Other provinces | Province-specific data |

## All 55+ MCP Tools Reference

### Utility Tools

| Tool | Args | Returns |
|------|------|---------|
| `bps_year_to_th` | `year: int` | Year → BPS th ID (e.g., 2024 → 124) |
| `bps_list_years` | `domain, var?, api_key?` | Available years for variable |
| `bps_list_domains` | `type="all"\|"prov"\|"kab"`, `prov?`, `api_key?` | List all domains |
| `bps_list_provinces` | `api_key?` | Province list |

### Subject & Variables

| Tool | Args | Returns |
|------|------|---------|
| `bps_list_subjects` | `domain, subcat?, lang="ind", page=1, api_key?` | Statistical subjects |
| `bps_list_subject_categories` | `domain, lang="ind", api_key?` | Subject category tree |
| `bps_get_variables` | `domain, subject?, year?, lang="ind", page=1, api_key?` | Variables for subject |
| `bps_list_periods` | `domain, var?, lang="ind", page=1, api_key?` | Time periods (tahun) |
| `bps_list_vertical_variables` | `domain, var?, lang="ind", page=1, api_key?` | Regional breakdowns (kabupaten/kota) |
| `bps_list_derived_variables` | `domain, var?, lang="ind", page=1, api_key?` | Sub-category variables |
| `bps_list_derived_periods` | `domain, var?, lang="ind", page=1, api_key?` | Monthly/quarterly periods |
| `bps_list_units` | `domain, lang="ind", page=1, api_key?` | Measurement units |

### Core Data Retrieval

| Tool | Args | Returns |
|------|------|---------|
| `bps_get_data` | `var: int, th: int, domain="5300", api_key?` | Raw numeric data |
| `bps_get_decoded_data` | `var: int, th: int, domain="5300", api_key?` | Data with region labels (recommended) |

**Example:**
```python
# Get TPT ( unemployment rate) for NTT 2024
bps_get_decoded_data(var=522, th=124, domain="5300")
# var=522 from bps_get_variables, th=124 = year_to_th(2024)
```

### Search Tools

| Tool | Args | Returns |
|------|------|---------|
| `bps_search` | `keyword, domain="5300", content="all", page=1, api_key?` | Static table search (WebAPI) |
| `bps_search_allstats` | `keyword, domain="5300", content="all", page=1, api_key?` | Playwright search (bypasses WAF) |
| `bps_search_ntt` | `keyword, page=1, api_key?` | Shortcut: domain=5300 |
| `bps_search_nasional` | `keyword, page=1, api_key?` | Shortcut: domain=0000 |
| `bps_search_and_get_data` | `keyword, domain="5300", max_tables=3, format="json", api_key?` | Search + retrieve data |
| `bps_answer_query` | `keyword, domain="5300", content="all", api_key?` | AI-powered AllStats-first answer |

**AllStats content types:** `all`, `publication`, `table`, `pressrelease`, `infographic`, `microdata`, `news`, `glosarium`

### Table Data

| Tool | Args | Returns |
|------|------|---------|
| `bps_get_table_data` | `table_id: int, domain="5300", format="json"\|"csv", api_key?` | Static table with actual data |
| `bps_list_dynamic_tables` | `domain, year?, keyword?, lang="ind", page=1, api_key?` | Dynamic tables list |

### Publications & Press Releases

| Tool | Args | Returns |
|------|------|---------|
| `bps_get_press_releases` | `year=2024, domain="0000", api_key?` | Berita Resmi Statistik (BRS) list |
| `bps_get_publications` | `domain="5300", page=1, api_key?` | Publication list |

### News & Media

| Tool | Args | Returns |
|------|------|---------|
| `bps_list_news_categories` | `domain="5300", lang="ind", api_key?` | News categories |
| `bps_get_news_detail` | `news_id: int, domain="5300", lang="ind", api_key?` | News article |

### Indicators & Infographics

| Tool | Args | Returns |
|------|------|---------|
| `bps_get_indicators` | `domain="5300", year?, page=1, api_key?` | Strategic indicators |
| `bps_list_infographics` | `domain="5300", keyword?, lang="ind", page=1, api_key?` | Infographic list |
| `bps_get_infographic_detail` | `infographic_id: str, domain="5300", lang="ind", api_key?` | Infographic with image URL |

### Glossary

| Tool | Args | Returns |
|------|------|---------|
| `bps_list_glossary` | `prefix?, perpage=10, page=1, api_key?` | Glossary terms (no domain param) |
| `bps_get_glossary_detail` | `glossary_id: int, lang="ind", api_key?` | Glossary term detail |

### SDGs & SDDS

| Tool | Args | Returns |
|------|------|---------|
| `bps_list_sdgs` | `goal?` ("1"-"17"), `api_key?` | SDG indicators (no domain) |
| `bps_list_sdds` | `api_key?` | SDDS indicators (no domain) |

### Census Data (uses `kegiatan` not domain)

| Tool | Args | Returns |
|------|------|---------|
| `bps_get_census_topics` | `kegiatan: str` (e.g., "sp2020") | Census topics |
| `bps_get_census_areas` | `kegiatan: str` | Wilayah sensus areas |
| `bps_get_census_datasets` | `kegiatan: str, topik: int` | Available datasets |
| `bps_get_census_data` | `kegiatan: str, wilayah_sensus: int, dataset: int` | Census microdata |

**Census kegiatan values:** `"sp2020"` (Population Census 2020), others depending on available census events

### SIMDASI Data (uses 7-digit MFD codes, not domain)

| Tool | Args | Returns |
|------|------|---------|
| `bps_get_simdasi_regencies` | `parent: str` (7-digit MFD, e.g., "5300000" for NTT) | Regency MFD codes |
| `bps_get_simdasi_districts` | `parent: str` (7-digit regency MFD) | District MFD codes |
| `bps_get_simdasi_subjects` | `wilayah: str` (7-digit area MFD) | SIMDASI subjects |
| `bps_get_simdasi_master_tables` | `api_key?` | Master table list (no domain) |
| `bps_get_simdasi_table_detail` | `wilayah: str, tahun: int, id_tabel: str` | Table with data |
| `bps_get_simdasi_tables_by_area` | `wilayah: str` | Tables for area |
| `bps_get_simdasi_tables_by_area_and_subject` | `wilayah: str, id_subjek: str` | Tables by area+subject |
| `bps_get_simdasi_master_table_detail` | `id_tabel: str` | Master table detail |

**MFD code examples:** NTT province="5300000", Kota Kupang="5371000", Kabupaten Ngada="5306000"

### CSA (Custom Statistical Areas)

| Tool | Args | Returns |
|------|------|---------|
| `bps_list_csa_categories` | `domain="5300", api_key?` | CSA categories |
| `bps_list_csa_subjects` | `domain="5300", subcat?, api_key?` | CSA subjects |
| `bps_list_csa_tables` | `domain="5300", subject?, page=1, perpage=10, api_key?` | CSA table statistics |
| `bps_get_csa_table_detail` | `table_id: str, year?, lang="ind", domain="5300", api_key?` | CSA table detail |

### Classifications (KBLI/KBKI)

| Tool | Args | Returns |
|------|------|---------|
| `bps_list_kbli` | `year=2020, level?, page=1, perpage=10, api_key?` | KBLI codes (ISIC-based) |
| `bps_get_kbli_detail` | `kbli_id: str, year=2020, lang="ind", api_key?` | KBLI classification detail |
| `bps_list_kbki` | `year=2015, page=1, perpage=10, api_key?` | KBKI commodity codes |
| `bps_get_kbki_detail` | `kbki_id: str, year=2015, lang="ind", api_key?` | KBKI classification detail |

**KBLI years:** 2009, 2015, 2017, 2020
**KBLI levels:** "kategori", "golongan pokok", "golongan", "subgolongan", "kelompok"

### Foreign Trade

| Tool | Args | Returns |
|------|------|---------|
| `bps_get_foreign_trade` | `sumber: int, kodehs: int, tahun: str, periode=1, jenishs=1, api_key?` | Export/import data |

**Foreign trade params:**
- `sumber`: 1=Export, 2=Import
- `kodehs`: HS code (2-digit for summary, full for detail)
- `tahun`: Year string e.g., "2024"
- `periode`: 1=monthly, 2=annually
- `jenishs`: 1=Two-digit HS summary, 2=Full HS code

## Common Query Templates

| Intent | Tool to Use | Example |
|--------|-------------|---------|
| "inflasi NTT terbaru" | `bps_answer_query` | `bps_answer_query("inflasi", domain="5300")` |
| "PDB nasional 2024" | `bps_answer_query` or `bps_search_and_get_data` | `bps_answer_query("PDB", domain="0000")` |
| "IPM kabupaten NTT" | `bps_get_decoded_data` with variable ID | `bps_get_decoded_data(var=X, th=124, domain="5300")` |
| "statistik penduduk" | `bps_list_subjects` then `bps_get_variables` | explore subject ID 14 |
| "publikasi BPS terbaru" | `bps_get_publications` | `bps_get_publications(domain="5300")` |
| "KBLI classification" | `bps_list_kbli` / `bps_get_kbli_detail` | `bps_list_kbli(year=2020, level="golongan")` |
| "ekspor-impor" | `bps_get_foreign_trade` | `bps_get_foreign_trade(sumber=1, kodehs=84, tahun="2024", ...)` |
| "SDGs NTT goal 1" | `bps_list_sdgs` | `bps_list_sdgs(goal="1")` |
| "Sensus 2020" | `bps_get_census_topics` | `bps_get_census_topics(kegiatan="sp2020")` |

## Environment Variables

```bash
# Required for WebAPI
BPS_API_KEY=your_key_here
# or
WEBAPI_APP_ID=your_key_here

# BPS_API_KEY takes precedence when both set
```

## WAF Bypass Notes

BPS LTM WAF blocks some regional SIMDASI endpoints. Workarounds:

| Blocked | Workaround |
|---------|-----------|
| SIMDASI id/27-29 with regional params | Use Census data (id/41) instead |
| SIMDASI regional (wilayah ≠ 0000000) | Try wilayah="5300000" (NTT MFD) |
| AllStats always works | `bps_search_allstats` bypasses Cloudflare |

## Installation

```bash
git clone https://github.com/juliochwd/bps-stat-agent.git
cd bps-stat-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
playwright install chromium
```

## Running as MCP Server

```bash
# Via uvx (no install needed)
uvx --from git+https://github.com/juliochwd/bps-stat-agent.git bps-mcp-server

# Or directly
python -m mini_agent.bps_mcp_server
```

## Quick Reference: BPS th Values

| Year | th (year - 1900) |
|------|------------------|
| 2017 | 117 |
| 2018 | 118 |
| 2019 | 119 |
| 2020 | 120 |
| 2021 | 121 |
| 2022 | 122 |
| 2023 | 123 |
| 2024 | 124 |
| 2025 | 125 |

Use `bps_year_to_th(year)` to convert, or `bps_list_years` to discover available periods.