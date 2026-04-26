# BPS Domain Codes Reference

## Province Domain Codes

| Code | Province | Alias |
|------|----------|-------|
| 0000 | Nasional (National) | Indonesia |
| 1100 | Aceh | NAD, Nanggroe Aceh Darussalam |
| 1200 | Sumatera Utara | Sumut, North Sumatra |
| 1300 | Sumatera Barat | West Sumatra |
| 1400 | Riau | |
| 1500 | Jambi | |
| 1600 | Sumatera Selatan | South Sumatra |
| 1700 | Bengkulu | |
| 1800 | Lampung | |
| 1900 | Bangka Belitung Islands | |
| 2000 | Kepulauan Riau | Kepri, Riau Islands |
| 2100 | DKI Jakarta | Jakarta |
| 2200 | Jawa Barat | West Java |
| 2300 | Jawa Tengah | Central Java |
| 2500 | DI Yogyakarta | Yogyakarta |
| 2600 | Jawa Timur | East Java |
| 2700 | Banten | |
| 2800 | Bali | |
| 2900 | Nusa Tenggara Barat | West Nusa Tenggara |
| **5300** | **Nusa Tenggara Timur** | **NTT, East Nusa Tenggara** |
| 5400 | Kalimantan Barat | West Kalimantan |
| 5500 | Kalimantan Tengah | Central Kalimantan |
| 5600 | Kalimantan Selatan | South Kalimantan |
| 5700 | Kalimantan Timur | East Kalimantan |
| 5800 | Kalimantan Utara | North Kalimantan |
| 6100 | Sulawesi Utara | North Sulawesi |
| 6200 | Sulawesi Tengah | Central Sulawesi |
| 6300 | Sulawesi Selatan | South Sulawesi |
| 6400 | Sulawesi Tenggara | Southeast Sulawesi |
| 6500 | Gorontalo | |
| 6600 | Sulawesi Barat | West Sulawesi |
| 7100 | Maluku | |
| 7200 | Maluku Utara | North Maluku |
| 7300 | Papua Barat | West Papua |
| 7400 | Papua | |
| 7500 | Papua Tengah | Central Papua |
| 7600 | Papua Pegunungan | Highland Papua |
| 7700 | Papua Barat Daya | Southwest Papua |

## AllStats Search Parameters

### URL Template
```
https://searchengine.web.bps.go.id/search?mfd={domain}&q={keyword}&content={type}&page={page}&sort={sort}
```

### Parameters
- `mfd` — Domain code (e.g., 5300=NTT, 0000=National)
- `q` — Keyword (use `+` for spaces, e.g., `data+inflasi`)
- `content` — Filter type
- `page` — Page number (default 1)
- `sort` — `terbaru` (newest), `terlama` (oldest), `relevansi` (relevance)

### Content Types
| Type | BPS Product |
|------|------------|
| `all` | Semua tipe (All types) |
| `publication` | Publikasi |
| `table` | Tabel Statistik |
| `pressrelease` | Berita Resmi Statistik (BRS) |
| `infographic` | Infografis |
| `microdata` | Data Mikro |
| `news` | Berita |
| `glosarium` | Glosarium |

## WebAPI Base URLs

- **AllStats Search Engine**: `https://searchengine.web.bps.go.id`
- **WebAPI**: `https://webapi.bps.go.id`
- **NTT Province**: `https://ntt.bps.go.id`
- **National**: `https://web.bps.go.id`

## Common Query Patterns

| Intent | Query Keywords | Domain |
|--------|---------------|--------|
| Inflation NTT | inflasi, inflation | 5300 |
| GDP National | PDB, GDP, produk domestik bruto | 0000 |
| HDI/IPM | IPM, HDI, human development, pembangunan manusia | 5300 |
| Population | penduduk, population, sensus | 5300 |
| Employment | unemployment, pengangguran, tenaga kerja | 5300 |
| Poverty | kemiskinan, poverty | 5300 |
| Trade | ekspor, impor, export, import | 0000 |
| CPI | IHK, consumer price index, harga konsumen | 5300 |

## Key MCP Tools

| Tool | Purpose |
|------|---------|
| `bps_answer_query` | AllStats-first query → structured BPS data |
| `bps_search_allstats` | Playwright search bypassing Cloudflare |
| `bps_search_ntt` | Convenience wrapper for NTT domain |
| `bps_search_nasional` | Convenience wrapper for national domain |
| `bps_get_data` | Raw dynamic data from WebAPI |
| `bps_get_decoded_data` | Data with human-readable region labels |
| `bps_get_variables` | Variables available for a subject |
| `bps_list_periods` | Available time periods |
| `bps_get_indicators` | Strategic indicators |