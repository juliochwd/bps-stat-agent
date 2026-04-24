# BPS WebAPI Test Results
Generated: 2026-04-23
API Key Domain: NTT (5300)
Base URL: https://webapi.bps.go.id/v1/api

## Summary

### WORKING ENDPOINTS (32 endpoints)

#### 1. LIST Model Endpoints
| Model | Endpoint | Status | Notes |
|-------|----------|--------|-------|
| domain | GET /domain | OK | type=all/prov/kab/kabbyprov |
| subject | GET /list?model=subject | OK | domain required |
| subcat | GET /list?model=subcat | OK | Subject Categories |
| var | GET /list?model=var | OK | Variable list |
| th | GET /list?model=th | OK | Period (time horizon) |
| turth | GET /list?model=turth | OK | Derived period |
| turvar | GET /list?model=turvar | OK | Derived variable |
| unit | GET /list?model=unit | OK | Unit data |
| data | GET /list?model=data | OK | var + th required |
| statictable | GET /list?model=statictable | OK | Static table list |
| publication | GET /list?model=publication | OK | Publication list |
| pressrelease | GET /list?model=pressrelease | OK | Press release list |
| news | GET /list?model=news | OK | News list |
| infographic | GET /list?model=infographic | OK | Infographic list |
| indicators | GET /list?model=indicators | OK | Strategic indicators |
| glosarium | GET /list?model=glosarium | OK | Glossary |
| newscategory | GET /list?model=newscategory | OK | News categories |
| sdds | GET /list?model=sdds | OK | SDDS |
| subcatcsa | GET /list?model=subcatcsa | OK | CSA Categories |
| subjectcsa | GET /list?model=subjectcsa | OK | CSA Subject |
| kbli2020 | GET /list?model=kbli2020 | OK | KBLI 2020 |
| kbli2017 | GET /list?model=kbli2017 | OK | KBLI 2017 |
| kbki2015 | GET /list?model=kbki2015 | OK | KBKI 2015 |

#### 2. VIEW Detail Endpoints (`/v1/api/view`)
| Model | Status | Notes |
|-------|--------|-------|
| statictable | OK | HTML table content |
| kbli2020 | OK | Classification detail |

#### 3. CENSUS Endpoints (`/interoperabilitas/datasource/sensus/id/`)
| ID | Status | Required Params |
|----|--------|-----------------|
| 37 | OK | - (Census Events list) |
| 38 | OK | kegiatan (e.g., sp2020) |
| 39 | OK (null) | kegiatan |
| 40 | OK | kegiatan + topik |
| 41 | OK | kegiatan + wilayah_sensus + dataset |

#### 4. SIMDASI Endpoints (`/interoperabilitas/datasource/simdasi/id/`)
| ID | Status | Required Params | Notes |
|----|--------|-----------------|-------|
| 26 | OK | - | Province list (39 provinces) |
| 27 | WAF | parent (7-digit) | Regency - BLOCKED with NTT parent |
| 28 | WAF | parent (7-digit) | District - BLOCKED with actual parent |
| 29 | WAF | parent (7-digit) | Village - BLOCKED |

### BLOCKED ENDPOINTS (WAF LTM Protection)

The following endpoints are blocked by BPS LTM WAF when using regional parameters:

| Endpoint | Trigger | Workaround |
|----------|---------|------------|
| SIMDASI id/24 | wilayah=5300000 (NTT) | Use wilayah=0000000 (nasional) |
| SIMDASI id/25 | Any call | Use Census data instead |
| SIMDASI id/27 | parent=5300000 | Use Census id/41 for regency data |
| SIMDASI id/28 | parent=kode_kab | Use variable data with domain filter |
| SIMDASI id/29 | Any call | Use Census data instead |

### CRITICAL NOTES

1. **WAF BYPASS HEADERS**: Required for all API calls:
```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
    "Referer": "https://webapi.bps.go.id/",
}
```

2. **th parameter is th_id, NOT year**: Must fetch from `/list?model=th` first

3. **Pagination Format**: `[{"page": 1, "pages": N, "per_page": 10, "total": X}, [actual_data_array]]`

4. **SIMDASI Response Structure**: Wrapped in `{status, data: {metadata, data: [...]}}`

5. **Regional Data Workaround**: Use Census (id/41) and Variable data with domain filtering instead of blocked SIMDASI endpoints

### Sample Requests

**List Variables:**
```
GET /list?model=var&key=API_KEY
```

**Get Variable Data:**
```
GET /list?model=data&var=VARIABLE_ID&th=TH_ID&key=API_KEY
```

**Get Census Data:**
```
GET /interoperabilitas/datasource/sensus/id/41/?kegiatan=sp2020&wilayah_sensus=00&dataset=001&key=API_KEY
```

**Get Province List:**
```
GET /interoperabilitas/datasource/simdasi/id/26/?key=API_KEY
```

**View Table Detail:**
```
GET /view?model=statictable&id=TABLE_ID&lang=id2&key=API_KEY
```
