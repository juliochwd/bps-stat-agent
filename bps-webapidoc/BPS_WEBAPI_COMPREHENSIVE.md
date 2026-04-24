# BPS WebAPI Comprehensive Documentation
## NTT BPS Data Integration Guide

**Last Updated:** 2026-04-22
**API Version:** BPS WebAPI v1
**API Base URL:** `https://webapi.bps.go.id/v1/api/`

---

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [10 BPS Products Coverage](#10-bps-products-coverage)
4. [NTT Domain Codes](#ntt-domain-codes)
5. [API Methods Reference](#api-methods-reference)
6. [Data Formats](#data-formats)
7. [Pagination](#pagination)
8. [Error Handling](#error-handling)
9. [Usage Examples](#usage-examples)

---

## Overview

The BPS (Badan Pusat Statistik / Statistics Indonesia) WebAPI provides programmatic access to BPS statistical data. All data displayed on BPS websites originates from this same API.

### Key Facts
- **Base URL:** `https://webapi.bps.go.id/v1/api/`
- **Authentication:** API Key required (get from API Portal)
- **Response Format:** JSON
- **Rate Limiting:** Circuit breaker with resilience patterns

---

## Authentication

### API Key
```python
# Via environment variable
WEBAPI_APP_ID=your_api_key

# Or directly in code
app_id = "your_api_key"
```

### NTT WebAPI Key (Development)
```
80a6bd62b0007e3c9f685346544e6afa
```

---

## 10 BPS Products Coverage

All BPS websites contain exactly these 10 products:

| # | Product | Description | Endpoint/Method |
|---|---------|-------------|----------------|
| 1 | **Publikasi** | Publications/Catalog | `get_publications()` |
| 2 | **Berita Resmi Statistik** | Press Releases | `get_press_releases()` |
| 3 | **Statistik menurut Subjek** | Statistics by Subject | `get_subjects()` |
| 4 | **Tabel Dinamis** | Dynamic Tables | `get_variables()` + `get_data()` |
| 5 | **Data Sensus** | Census Data | `get_census_events()` |
| 6 | **Data Ekspor Impor** | Export/Import Data | `get_foreign_trade()` |
| 7 | **Direktori** | Directories (SDGs, SDDS) | `get_sdgs()` |
| 8 | **Infografik** | Infographics | `get_infographics()` |
| 9 | **Berita dan Siaran Pers** | News | `get_news()` |
| 10 | **Metadata** | Metadata/Glossary | `get_glossary()` |

---

## NTT Domain Codes

### Province + 22 Kabupaten/Kota

```python
NTT_DOMAINS = {
    '5300': 'ntt_provinsi',       # Nusa Tenggara Timur (Province)
    '5301': 'kab_kupang',          # Kabupaten Kupang
    '5302': 'kab_timor_tengah_selatan',  # Kabupaten Timor Tengah Selatan
    '5303': 'kab_timor_tengah_utara',    # Kabupaten Timor Tengah Utara
    '5304': 'kab_belu',            # Kabupaten Belu
    '5305': 'kab_alor',            # Kabupaten Alor
    '5306': 'kab_lembata',         # Kabupaten Lembata
    '5307': 'kab_flores_timur',    # Kabupaten Flores Timur
    '5308': 'kab_sikka',           # Kabupaten Sikka
    '5309': 'kab_ende',            # Kabupaten Ende
    '5310': 'kab_ngada',           # Kabupaten Ngada
    '5311': 'kab_manggarai',       # Kabupaten Manggarai
    '5312': 'kab_rote_ndao',       # Kabupaten Rote Ndao
    '5313': 'kab_manggarai_timur', # Kabupaten Manggarai Timur
    '5314': 'kab_nagekeo',         # Kabupaten Nagekeo
    '5315': 'kab_sumba_barat_daya', # Kabupaten Sumba Barat Daya
    '5316': 'kab_manggarai_barat',  # Kabupaten Manggarai Barat
    '5317': 'kab_sumba_tengah',    # Kabupaten Sumba Tengah
    '5318': 'kab_sumba_timur',     # Kabupaten Sumba Timur
    '5319': 'kab_sumba_barat',     # Kabupaten Sumba Barat
    '5320': 'kab_sabu_raijua',     # Kabupaten Sabu Raijua
    '5321': 'kab_malaka',          # Kabupaten Malaka
    '5371': 'kota_kupang',         # Kota Kupang
}
```

### Domain Code Structure
- **Province (5300):** Full coverage - all products available
- **Kabupaten (5301-5321):** Full coverage - all products available
- **Kota (5371):** Full coverage - all products available

---

## API Methods Reference

### Complete WebApiClient Methods

```python
from src.tools.webapi.client import WebApiClient

api = WebApiClient(app_id="your_key")
```

#### Publication Methods
```python
# Get all publications for a domain
await api.get_publications(domain='5300')

# Get publication detail
await api.get_publication_detail(domain='5300', id='pub_id')
```

#### Press Release Methods
```python
# Get all press releases
await api.get_press_releases(domain='5300')

# Get press release detail
await api.get_press_release_detail(domain='5300', id='brs_id')
```

#### News Methods
```python
# Get all news
await api.get_news(domain='5300')

# Get news detail
await api.get_news_detail(domain='5300', id='news_id')
```

#### Statistics Methods
```python
# Get all subjects
await api.get_subjects(domain='5300')

# Get variables for a subject
await api.get_variables(domain='5300', subject=40)

# Get data for a variable
await api.get_data(domain='5300', var=123, th=1)

# Get subject categories
await api.get_subject_categories(domain='5300')

# Get periods
await api.get_periods(domain='5300')

# Get vertical variables
await api.get_vertical_variables(domain='5300')

# Get derived variables
await api.get_derived_variables(domain='5300')

# Get derived periods
await api.get_derived_periods(domain='5300')

# Get units
await api.get_units(domain='5300')
```

#### Indicators Methods
```python
# Get strategic indicators (province only)
await api.get_indicators(domain='5300')
```

#### Census Methods
```python
# Get census events
await api.get_census_events()

# Get census topics
await api.get_census_topics('sp2020')

# Get census areas
await api.get_census_areas('sp2020')

# Get census datasets
await api.get_census_datasets('sp2020', topik=1)

# Get census data
await api.get_census_data(kegiatan='sp2020', topik=1, wilayah='5300')
```

#### Foreign Trade Methods
```python
# Get export/import data
await api.get_foreign_trade(sumber=1, kodehs='01', jenishs=1, tahun='2024')

# sumber: 1=Export, 2=Import
# jenishs: 1=2-digit, 2=Full HS code
```

#### Directory Methods (SDGs/SDDS)
```python
# Get SDGs indicators
await api.get_sdgs()

# Get SDDS data
await api.get_sdds()

# Get KBLI classifications
await api.get_kbli(model='kbli2020')

# Get CSA categories
await api.get_csa_categories(domain='5300')

# Get CSA subjects
await api.get_csa_subjects(domain='5300', subcat='514')
```

#### Infographic Methods
```python
# Get all infographics
await api.get_infographics(domain='5300')

# Get infographic detail
await api.get_infographic_detail(domain='5300', id='infographic_id')
```

#### Metadata Methods
```python
# Get glossary/metadata
await api.get_glossary(domain='5300')

# Get glossary detail
await api.get_glossary_detail(domain='5300', id='glossary_id')
```

#### Static Table Methods
```python
# Get static tables
await api.get_static_tables(domain='5300')

# Get static table detail
await api.get_static_table_detail(domain='5300', var=123)
```

#### Domain Methods
```python
# Get all domains
await api.get_domains()

# Get provinces
await api.get_provinces()

# Get regencies
await api.get_regencies(prov_id='53')
```

---

## Data Formats

### Standard Response Format
```json
{
  "_meta": {
    "source": "webapi",
    "timestamp": "2026-04-22T10:00:00+00:00",
    "cache_hit": false,
    "endpoint": "get_subjects"
  },
  "pagination": {
    "page": 1,
    "pages": 5,
    "per_page": 10,
    "total": 48
  },
  "items": [
    {
      "sub_id": 40,
      "title": "Gender",
      "subcat_id": 1,
      "subcat": "Sosial dan Kependudukan"
    }
  ]
}
```

### Subject Structure
```python
{
    "sub_id": 40,           # Subject ID
    "title": "Gender",        # Subject title
    "subcat_id": 1,          # Sub-category ID
    "subcat": "Sosial dan Kependudukan"  # Sub-category name
}
```

### Variable Structure
```python
{
    "var_id": 123,
    "title": "Jumlah Penduduk",
    "sub_id": 40,
    "sub_name": "Gender",
    "unit": "Orang",
    "notes": "Sumber: Sensus Penduduk"
}
```

### Data Point Structure
```python
{
    "year": 2024,
    "value": 5535000
}
```

### Publication Structure
```python
{
    "pub_id": "pub-12345",
    "title": "Provinsi NTT Dalam Angka 2025",
    "rl_date": "2025-02-15",
    "size": "5.2 MB",
    "cover": "url_to_cover_image",
    "pdf": "url_to_pdf"
}
```

### Press Release Structure
```python
{
    "brs_id": "brs-12345",
    "title": "Neraca Perdagangan NTT Januari 2025",
    "rl_date": "2025-02-15",
    "updt_date": null,
    "pdf": "url_to_pdf",
    "size": "500 KB"
}
```

---

## Pagination

### How Pagination Works
```python
# Most list endpoints support pagination
result = await api.get_subjects(domain='5300', page=1)

# Pagination info in response
pagination = result.get('pagination', {})
total = pagination.get('total', 0)
pages = pagination.get('pages', 1)
current_page = pagination.get('page', 1)

# Iterate through pages
page = 1
while True:
    result = await api.get_subjects(domain='5300', page=page)
    items = result.get('items', [])
    if not items:
        break
    # Process items
    page += 1
```

---

## Error Handling

### WebAPI Error Types
```python
from src.shared.errors import WebAPIError

try:
    result = await api.get_subjects(domain='5300')
except WebAPIError as e:
    print(f"API Error: {e}")
```

### Common Errors
- `401 Unauthorized` - Invalid API key
- `429 Too Many Requests` - Rate limited
- `500 Internal Server Error` - Server error
- `404 Not Found` - Resource not found

---

## Usage Examples

### Complete NTT Data Fetch Example
```python
import asyncio
import os
from src.tools.webapi.client import WebApiClient
from src.tools.rag.context_tree import ContextTree

NTT_DOMAINS = {
    '5300': 'ntt_provinsi',
    '5301': 'kab_kupang',
    # ... all 23 domains
}

async def fetch_ntt_data():
    app_id = os.getenv('WEBAPI_APP_ID', '80a6bd62b0007e3c9f685346544e6afa')
    api = WebApiClient(app_id=app_id)
    tree = ContextTree()
    
    for domain_code, domain_name in NTT_DOMAINS.items():
        # Fetch publications
        pubs = await api.get_publications(domain=domain_code)
        for pub in pubs.get('items', []):
            tree.upsert(
                domain=domain_name,
                topic="publikasi",
                subtopic=pub.get('rl_date', 'general'),
                title=pub.get('title', ''),
                content=f"# Publikasi\n{pub.get('title', '')}",
                tags=["bps", "ntt"],
                source="webapi.bps.go.id"
            )
        
        # Fetch subjects and variables
        subjects = await api.get_subjects(domain=domain_code)
        for subj in subjects.get('items', []):
            subj_id = subj.get('sub_id')
            vars = await api.get_variables(domain=domain_code, subject=subj_id)
            for var in vars.get('items', []):
                tree.upsert(
                    domain=domain_name,
                    topic=f"statistik/{subj.get('title', '')}",
                    subtopic=var.get('title', ''),
                    title=var.get('title', ''),
                    content=f"#{var.get('title', '')}",
                    tags=["bps", "ntt"],
                    source="webapi.bps.go.id"
                )

asyncio.run(fetch_ntt_data())
```

### Fetching Time Series Data
```python
# Get variable data with time series
result = await api.get_data(domain='5300', var=123, th=1)
periods = result.get('items', [])

for period in periods:
    year = period.get('year')
    value = period.get('value')
    print(f"{year}: {value}")
```

---

## Quick Reference

### All BPS Products by Domain Level

| Product | Province (5300) | Kabkot (5301-5321, 5371) |
|---------|-----------------|---------------------------|
| Publikasi | ✅ | ✅ |
| Berita Resmi Statistik | ✅ | ✅ |
| Statistik Subjek | ✅ | ✅ |
| Tabel Dinamis | ✅ | ✅ |
| Data Sensus | ✅ | ✅ (via central API) |
| Ekspor Impor | ✅ | ❌ (central only) |
| Direktori/SDGs | ✅ | ✅ |
| Infografik | ✅ | ✅ |
| Berita | ✅ | ✅ |
| Metadata | ✅ | ✅ |

### Key Endpoints Summary

| Endpoint | Purpose |
|----------|---------|
| `GET /v1/api/list/` | List subjects, variables, etc. |
| `GET /v1/api/view/` | View detail of specific item |
| `GET /v1/api/domain/` | Get domain list |
| `GET /v1/api/dataexim/` | Foreign trade data |

---

## Notes

- **Website = API Source:** All BPS website data comes from the WebAPI
- **Domain Codes:** NTT Province = 5300, Kabupatens = 5301-5321, Kota = 5371
- **Rate Limiting:** Built-in circuit breaker handles rate limits
- **Caching:** WebApiClient has optional caching for development

---

## Related Documentation

- [WebAPI Official Documentation](webapidoc.md)
- [BPS WebAPI Complete Mapping](BPS_WEBAPI_COMPLEMENTARY_MAPPING.md)
- [NTT Data QA System Plan](../plans/bps-ntt-data-qa-system.md)
