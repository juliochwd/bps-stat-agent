# BPS WebAPI — Complete Endpoint & Data Mapping

## 1. API Endpoint Overview (23+ Endpoints)

### 1.1 Master Data (2 endpoints)
| Endpoint | Model | Purpose | Returns |
|----------|-------|---------|---------|
| `/v1/api/domain` | - | Province/City domain list | 34 provinsi + pusat (domain_id, domain_name, domain_url) |
| `/v1/api/domain` (type=kabbyprov) | - | Cities in specific province | Kabupaten/kota in selected province |

### 1.2 Subject & Categories (3 endpoints)
| Endpoint | Model | Purpose | Returns |
|----------|-------|---------|---------|
| `/v1/api/list` | `subject` | Statistical subjects in domain | sub_id, title, subcat_id, subcat, ntable |
| `/v1/api/list` | `subcat` | Subject categories | subcat_id, title |
| `/v1/api/list` | `subject` + subcat | Subjects filtered by category | Filtered subject list |

### 1.3 Dynamic Data System (6 endpoints)
| Endpoint | Model | Purpose | Parameters |
|----------|-------|---------|--------------|
| `/v1/api/list` | `var` | List variables in domain/subject | domain, subject, year, vervar, page |
| `/v1/api/list` | `vervar` | Vertical variables (regions/breakdown) | domain, var, page |
| `/v1/api/list` | `th` | Period data (years) | domain, var, page |
| `/v1/api/list` | `turvar` | Derived variables (sub-categories) | domain, var, group, nopage, page |
| `/v1/api/list` | `turth` | Derived periods (monthly/quarterly) | domain, var, page |
| `/v1/api/list` | `data` | **ACTUAL DATA VALUES** | domain, var, th, vervar, turvar, turth |
| `/v1/api/list` | `unit` | Unit of measurement | domain, page |

### 1.4 Publications & Content (6 endpoints)
| Endpoint | Model | Purpose | Returns |
|----------|-------|---------|---------|
| `/v1/api/list` | `pressrelease` | Press releases | brs_id, title, rl_date, pdf, size |
| `/v1/view` | `pressrelease` | Press release detail | Full abstract, PDF link |
| `/v1/api/list` | `publication` | Publications (PDFs) | pub_id, title, issn, rl_date, pdf, cover, size |
| `/v1/view` | `publication` | Publication detail | Full abstract, ISSN, PDF/cover links |
| `/v1/api/list` | `news` | BPS news articles | news_id, title, news, rl_date, newscat_name |
| `/v1/view` | `news` | News detail | Full article content, picture |
| `/v1/api/list` | `newscategory` | News categories | newscat_id, newscat_name |

### 1.5 Tables & Static Data (4 endpoints)
| Endpoint | Model | Purpose | Returns |
|----------|-------|---------|---------|
| `/v1/api/list` | `statictable` | Static tables | table_id, title, subj_id, updt_date, excel, size |
| `/v1/view` | `statictable` | Static table detail | HTML table content, Excel download link |
| `/v1/api/list` | `indicators` | Strategic indicators | title, desc, data_source, value, unit |
| `/v1/api/list` | `infographic` | Infographics | inf_id, title, img, desc, category, dl |

### 1.6 Special Data (5 endpoints)
| Endpoint | Model | Purpose | Returns |
|----------|-------|---------|---------|
| `/v1/api/list` | `sdgs` | SDGs tables (17 goals) | SDG variable data by goal |
| `/v1/api/list` | `sdds` | SDDS tables (~60 variables) | SDDS variable data |
| `/v1/api/list` | `glosarium` | Statistical glossary | konsep, definisi, ukuran, satuan (5078 entries) |
| `/v1/view` | `glosarium` | Glossary detail | Full concept definition |
| `/v1/api/dataexim` | - | Export/Import data | value, netweight, kodehs, pod, ctr, tahun |

### 1.7 Census Data (5 endpoints)
| Endpoint | ID | Purpose | Returns |
|----------|-----|---------|---------|
| `/v1/api/interoperabilitas/datasource/sensus/id/37/` | 37 | List census events | id, kegiatan, tahun_kegiatan |
| `/v1/api/interoperabilitas/datasource/sensus/id/38/` | 38 | Census data topics | id, topik, topic, kegiatan, event |
| `/v1/api/interoperabilitas/datasource/sensus/id/39/` | 39 | Census event areas | id, kode_mfd, nama |
| `/v1/api/interoperabilitas/datasource/sensus/id/40/` | 40 | Available datasets | id, topik, nama, deskripsi |
| `/v1/api/interoperabilitas/datasource/sensus/id/41/` | 41 | Actual census data | nilai, periode, nama_wilayah, nama_indikator |

### 1.8 SIMDASI (8 endpoints)
| Endpoint | ID | Purpose |
|----------|-----|---------|
| `/v1/api/interoperabilitas/datasource/simdasi/id/26/` | 26 | 7-digit MFD Province codes |
| `/v1/api/interoperabilitas/datasource/simdasi/id/27/` | 27 | 7-digit MFD Regency codes |
| `/v1/api/interoperabilitas/datasource/simdasi/id/28/` | 28 | 7-digit MFD District codes |
| `/v1/api/interoperabilitas/datasource/simdasi/id/22/` | 22 | SIMDASI subjects by area |
| `/v1/api/interoperabilitas/datasource/simdasi/id/34/` | 34 | Master Table list |
| `/v1/api/interoperabilitas/datasource/simdasi/id/36/` | 36 | Master Table detail |
| `/v1/api/interoperabilitas/datasource/simdasi/id/23/` | 23 | Tables by area |
| `/v1/api/interoperabilitas/datasource/simdasi/id/24/` | 24 | Tables by area+subject |
| `/v1/api/interoperabilitas/datasource/simdasi/id/25/` | 25 | Table detail with data |

### 1.9 CSA Subject (3 endpoints)
| Endpoint | Model | Purpose | Returns |
|----------|-------|---------|---------|
| `/v1/api/list` | `subcatcsa` | CSA categories | subcat_id, title |
| `/v1/api/list` | `subjectcsa` | CSA subjects | sub_id, title, subcat_id, subcat |
| `/v1/api/list` | `tablestatistic` | Tables using CSA | id, title, id_subject, tablesource (1=static, 2=dynamic, 3=SIMDASI) |
| `/v1/api/view` | `tablestatistic` | Table detail | Full table data with year filter |

### 1.10 Classifications (2 endpoints)
| Endpoint | Model | Purpose | Models |
|----------|-------|---------|--------|
| `/v1/api/list` | `kbli2009/2015/2017/2020` | Industry classification | KBLI (ISIC-based) |
| `/v1/api/list` | `kbki2015` | Commodity classification | KBKI |
| `/v1/api/view` | `kbli*/kbki*` | Classification detail | kode, judul, deskripsi, turunan |

### 1.11 Search (1 endpoint)
| Endpoint | Model | Purpose | Parameters |
|----------|-------|---------|--------------|
| `/v1/api/list` | `search` | Search website content | keyword (use + for spaces), domain, page |

---

## 2. Domain ID Reference

| Domain ID | Name | URL | Type |
|-----------|------|-----|------|
| `0000` | Pusat (National) | bps.go.id | National |
| `1100` | Aceh | aceh.bps.go.id | Province |
| `1200` | Sumatera Utara | sumut.bps.go.id | Province |
| `3100` | DKI Jakarta | jakarta.bps.go.id | Province |
| `3200` | Jawa Barat | jabar.bps.go.id | Province |
| `3300` | Jawa Tengah | jateng.bps.go.id | Province |
| `3400` | DI Yogyakarta | jogja.bps.go.id | Province |
| `3500` | Jawa Timur | jatim.bps.go.id | Province |
| `3600` | Banten | banten.bps.go.id | Province |
| `5100` | Bali | bali.bps.go.id | Province |
| `5200` | Nusa Tenggara Barat | ntb.bps.go.id | Province |
| `5300` | Nusa Tenggara Timur | ntt.bps.go.id | Province |
| `6100-6500` | Kalimantan | kal*.bps.go.id | Province |
| `7100-7600` | Sulawesi | sul*.bps.go.id | Province |
| `8100-8200` | Maluku | maluku.bps.go.id | Province |
| `9100-9400` | Papua | papua.bps.go.id | Province |

---

## 3. CSA Subject Category → Endpoint Mapping

### 3.1 Statistik Demografi dan Sosial (subcat_id=514)

| CSA Subject | Sub ID | API Access | Dynamic Table Data |
|-------------|--------|------------|-------------------|
| **Kependudukan dan Migrasi** | 528+ | `model=subject&subcat=514` | var_id → model=data → population, migration |
| **Tenaga Kerja** | 529+ | `model=subject&subcat=514` | var_id → unemployment, TPT, PAK, wages |
| **Pendidikan** | 530+ | `model=subject&subcat=514` | var_id → enrolment, APS, APK, teachers |
| **Kesehatan** | 531+ | `model=subject&subcat=514` | var_id → AKB, AKI, stunting, immunization |
| **Konsumsi dan Pendapatan** | 532+ | `model=subject&subcat=514` | var_id → expenditure, income, poverty |
| **Perlindungan Sosial** | 533+ | `model=subject&subcat=514` | var_id → social programs, beneficiaries |
| **Pemukiman dan Perumahan** | 534+ | `model=subject&subcat=514` | var_id → housing, sanitation, electricity |
| **Hukum dan Kriminal** | 535+ | `model=subject&subcat=514` | var_id → crime rates, prisoners |
| **Budaya** | 536+ | `model=subject&subcat=514` | var_id → cultural activities |
| **Aktivitas Politik** | 537+ | `model=subject&subcat=514` | var_id → political participation |
| **Penggunaan Waktu** | 538+ | `model=subject&subcat=514` | var_id → time use survey |

### 3.2 Statistik Ekonomi (subcat_id=515)

| CSA Subject | Sub ID | API Access | Dynamic Table Data |
|-------------|--------|------------|-------------------|
| **Statistik Makroekonomi** | 539+ | `model=subject&subcat=515` | var_id → PDB, PDRB, growth rates |
| **Neraca Ekonomi** | 540+ | `model=subject&subcat=515` | var_id → national accounts, I-O tables |
| **Statistik Bisnis** | 541+ | `model=subject&subcat=515` | var_id → business statistics, IBS |
| **Statistik Sektoral** | 542+ | `model=subject&subcat=515` | var_id → sector-specific data |
| **Keuangan Pemerintah** | 543+ | `model=subject&subcat=515` | var_id → APBD, fiscal data |
| **Perdagangan Internasional** | 544+ | `model=dataexim` | var_id → export/import, HS codes |
| **Harga-Harga** | 545+ | `model=indicators` | var_id → IHK, inflasi, IHPB |
| **Biaya Tenaga Kerja** | 546+ | `model=subject&subcat=515` | var_id → labor costs, wages |
| **IPTEK dan Inovasi** | 547+ | `model=subject&subcat=515` | var_id → R&D, innovation |
| **Pertanian, Kehutanan, Perikanan** | 548+ | `model=subject&subcat=515` | var_id → production, area, yield |
| **Energi** | 549+ | `model=subject&subcat=515` | var_id → electricity, oil, gas |
| **Pertambangan, Manufaktur, Konstruksi** | 550+ | `model=subject&subcat=515` | var_id → mining output, IBS, construction |
| **Transportasi** | 551+ | `model=subject&subcat=515` | var_id → passengers, ports, roads |
| **Pariwisata** | 552+ | `model=subject&subcat=515` | var_id → tourists, hotels, TPK |
| **Perbankan, Asuransi, Finansial** | 553+ | `model=subject&subcat=515` | var_id → banking, credit, insurance |

### 3.3 Statistik Lingkungan Hidup dan Multi-domain (subcat_id=516)

| CSA Subject | Sub ID | API Access | Dynamic Table Data |
|-------------|--------|------------|-------------------|
| **Lingkungan** | 554+ | `model=subject&subcat=516` | var_id → environment, pollution |
| **Statistik Regional** | 555+ | `model=subject&subcat=516` | var_id → regional stats, small area |
| **Multi-Domain** | 556+ | `model=subject&subcat=516` | var_id → cross-sectoral indicators |
| **Buku Tahunan** | 557+ | `model=subject&subcat=516` | var_id → statistical yearbook |
| **Kemiskinan & Sosial** | 558+ | `model=subject&subcat=516` | var_id → poverty, social issues |
| **Gender & Populasi Khusus** | 559+ | `model=subject&subcat=516` | var_id → gender, disability, elderly |
| **Masyarakat Informasi** | 560+ | `model=subject&subcat=516` | var_id → ICT, internet, phones |
| **Globalisasi** | 561+ | `model=subject&subcat=516` | var_id → globalization indicators |
| **MDGs** | 562+ | `model=subject&subcat=516` | var_id → MDG indicators |
| **Perkembangan Berkelanjutan** | 563+ | `model=sdgs` | var_id → SDG indicators (300+ vars) |
| **Kewiraswastaan** | 564+ | `model=subject&subcat=516` | var_id → entrepreneurship, MSMEs |

---

## 4. Dynamic Table Data Retrieval Flow

### 4.1 Complete Retrieval Pipeline

```
Step 1: Get domain_id
  GET /v1/api/domain?type=prov → domain_id = 5300 (NTT)

Step 2: Get subject categories
  GET /v1/api/list?model=subcat&domain=5300 → subcat_id

Step 3: Get subjects in category
  GET /v1/api/list?model=subject&domain=5300&subcat=1 → sub_id

Step 4: Get variables in subject
  GET /v1/api/list?model=var&domain=5300&subject={sub_id} → var_id

Step 5: Get periods for variable
  GET /v1/api/list?model=th&domain=5300&var={var_id} → th_id (years)

Step 6: Get vertical breakdowns
  GET /v1/api/list?model=vervar&domain=5300&var={var_id} → vervar_id

Step 7: Get derived variables (sub-categories)
  GET /v1/api/list?model=turvar&domain=5300&var={var_id} → turvar_id

Step 8: Get derived periods (monthly/quarterly)
  GET /v1/api/list?model=turth&domain=5300&var={var_id} → turth_id

Step 9: Get ACTUAL DATA
  GET /v1/api/list?model=data&domain=5300&var={var_id}&th={th_id}
    &vervar={vervar_id}&turvar={turvar_id}
  → datacontent: {"99991452891000": 83.68, ...}
```

### 4.2 Key Parameter Relationships

| Parameter | What it controls | Example values |
|-----------|-----------------|----------------|
| `var` | Main variable | var=145 (Lighting source by province) |
| `th` | Time period | th=100 (2000), th=117 (2017) |
| `vervar` | Geographic/vertical breakdown | vervar=9999 (INDONESIA), vervar=3374 (Semarang) |
| `turvar` | Sub-category breakdown | turvar=289 (PLN electricity) |
| `turth` | Sub-period (monthly/quarterly) | turth=1 (January), turth=0 (Yearly) |
| `lang` | Language | lang=ind, lang=eng |

### 4.3 Data Content Format

```json
{
  "datacontent": {
    "99991452891000": 83.68,
    "vervar_id": "var_id": "turvar_id": "th_id"
  }
}
```

Key composite = vervar_id + var_id + turvar_id + th_id

---

## 5. SDGs Variable → ID Mapping (300+ Variables)

### 5.1 Goal 1: No Poverty
| Variable | Id Var | API Query |
|----------|--------|-----------|
| Percentage of Poor People by Province | 192 | model=data&domain=0000&var=192 |
| Percentage of Poor People by Region | 184 | model=data&domain=0000&var=184 |
| Percentage Below National Poverty Line by Age | 1539 | model=data&domain=0000&var=1539 |
| Percentage Below National Poverty Line by Gender | 1538 | model=data&domain=0000&var=1538 |

### 5.2 Goal 3: Good Health
| Variable | Id Var | API Query |
|----------|--------|-----------|
| Maternal Mortality Rate (AKI) | 1349 | model=data&domain=0000&var=1349 |
| Infant Mortality Rate (AKB) | 1584 | model=data&domain=0000&var=1584 |
| Under-5 Mortality Rate | 1379 | model=data&domain=0000&var=1379 |
| Stunting Prevalence | 1325 | model=data&domain=0000&var=1325 |
| Anemia in Pregnant Women | 1333 | model=data&domain=0000&var=1333 |
| Tuberculosis Incidence | 1763 | model=data&domain=0000&var=1763 |
| Malaria Cases | 1393 | model=data&domain=0000&var=1393 |
| Health Worker Density | 1477 | model=data&domain=0000&var=1477 |

### 5.3 Goal 4: Quality Education
| Variable | Id Var | API Query |
|----------|--------|-----------|
| Literacy Rate (15+) by Province | 1458 | model=data&domain=0000&var=1458 |
| Literacy Rate (15+) by Gender | 1460 | model=data&domain=0000&var=1460 |
| Gross Enrollment Rate (University) | 1443 | model=data&domain=0000&var=1443 |
| School Participation Rate (organized learning) | 1990 | model=data&domain=0000&var=1990 |
| Education Completion Rate | 1980 | model=data&domain=0000&var=1980 |
| Children Out of School | 1984 | model=data&domain=0000&var=1984 |
| School Electricity Access | 1794 | model=data&domain=0000&var=1794 |
| School Computer Access | 1796 | model=data&domain=0000&var=1796 |

### 5.4 Goal 8: Decent Work
| Variable | Id Var | API Query |
|----------|--------|-----------|
| Unemployment Rate by Age | 1180 | model=data&domain=0000&var=1180 |
| Unemployment Rate by Education | 1179 | model=data&domain=0000&var=1179 |
| Informal Employment by Age | 2156 | model=data&domain=0000&var=2156 |
| Tourism Contribution to GDP | 1188 | model=data&domain=0000&var=1188 |
| MSME Credit Proportion | 1192 | model=data&domain=0000&var=1192 |
| GDP per Labor Growth | 1161 | model=data&domain=0000&var=1161 |

### 5.5 Goal 10: Reduced Inequalities
| Variable | Id Var | API Query |
|----------|--------|-----------|
| Gini Ratio | 98 | model=data&domain=0000&var=98 |
| Women in Managerial Positions | 2003 | model=data&domain=0000&var=2003 |
| Population Below 50% Median Income | 2011 | model=data&domain=0000&var=2011 |
| Birth Certificate Coverage | 2014 | model=data&domain=0000&var=2014 |

### 5.6 Goal 11: Sustainable Cities
| Variable | Id Var | API Query |
|----------|--------|-----------|
| Access to Decent Housing | 1241 | model=data&domain=0000&var=1241 |
| Access to Public Transport | 2012 | model=data&domain=0000&var=2012 |
| Air Quality / Pollution | 1310 | model=data&domain=0000&var=1310 |
| Safety Walking Alone | 1312 | model=data&domain=0000&var=1312 |

### 5.7 Goal 13: Climate Action
| Variable | Id Var | API Query |
|----------|--------|-----------|
| Disaster Victims | 1804 | model=data&domain=0000&var=1804 |
| Disaster Victims per 100K | 1246 | model=data&domain=0000&var=1246 |
| Water Conservation Areas | 1289 | model=data&domain=0000&var=1289 |

### 5.8 Goal 16: Peace and Justice
| Variable | Id Var | API Query |
|----------|--------|-----------|
| Democracy Index (IDI) | 598 | model=data&domain=0000&var=598 |
| Corruption Perception (IPAK) | 635 | model=data&domain=0000&var=635 |
| Violence Against Women | 1375 | model=data&domain=0000&var=1375 |
| Homicide Cases | 1306 | model=data&domain=0000&var=1306 |
| Birth Registration Coverage | 1412 | model=data&domain=0000&var=1412 |

### 5.9 Goal 17: Partnerships
| Variable | Id Var | API Query |
|----------|--------|-----------|
| Tax Revenue to GDP Ratio | 1529 | model=data&domain=0000&var=1529 |
| Government Revenue to GDP | 1588 | model=data&domain=0000&var=1588 |
| Debt Service to Exports | 1260 | model=data&domain=0000&var=1260 |
| Broadband Internet Coverage | 2015 | model=data&domain=0000&var=2015 |

---

## 6. SDDS Variable → ID Mapping (~60 Variables)

### 6.1 Macroeconomic
| Variable | Id Var | API Query |
|----------|--------|-----------|
| GDP by Industry (2010=100) | 65 | model=data&domain=0000&var=65 |
| GDP Growth by Industry | 104 | model=data&domain=0000&var=104 |
| GDP Distribution by Expenditure | 110 | model=data&domain=0000&var=110 |
| Mid Year Population | 1975 | model=data&domain=0000&var=1975 |
| Population Growth Rate | 1976 | model=data&domain=0000&var=1976 |

### 6.2 Prices
| Variable | Id Var | API Query |
|----------|--------|-----------|
| IHK 90 Kota | 1709 | model=data&domain=0000&var=1709 |
| IHK Makanan Minuman (2018) | 1905 | model=data&domain=0000&var=1905 |
| IHK Makanan Minuman (2022) | 2212 | model=data&domain=0000&var=2212 |
| IHK Transportasi (2022) | 2217 | model=data&domain=0000&var=2217 |
| IHK Kesehatan (2018) | 1909 | model=data&domain=0000&var=1909 |
| IHK Pendidikan (2022) | 2220 | model=data&domain=0000&var=2220 |
| IHPB Indonesia (2018) | 1721 | model=data&domain=0000&var=1721 |
| IHPB Indonesia (2023) | 2498 | model=data&domain=0000&var=2498 |

### 6.3 Labor
| Variable | Id Var | API Query |
|----------|--------|-----------|
| Unemployment Rate by Province | 543 | model=data&domain=0000&var=543 |
| Employment & Unemployment | 1953 | model=data&domain=0000&var=1953 |
| Average Wage/Salary | 1521 | model=data&domain=0000&var=1521 |
| Population 15+ by Activity | 529 | model=data&domain=0000&var=529 |

### 6.4 Trade
| Variable | Id Var | API Query |
|----------|--------|-----------|
| Export Oil&Gas - Non Oil&Gas | 1753 | model=dataexim&sumber=1&periode=2 |
| Import Oil&Gas - Non Oil&Gas | 1754 | model=dataexim&sumber=2&periode=2 |
| Export Price Index (2023) | 2487 | model=data&domain=0000&var=2487 |
| Import Price Index (2023) | 2490 | model=data&domain=0000&var=2490 |

---

## 7. WebAPI Tools → Endpoint Mapping (Current + Missing)

### 7.1 Currently Implemented (14 tools)
| Tool | Endpoint | Parameters |
|------|----------|------------|
| `webapi_list_domains` | `/v1/api/domain` | type, prov |
| `webapi_list_subjects` | `/v1/api/list?model=subject` | domain, subcat, lang, page |
| `webapi_list_variables` | `/v1/api/list?model=var` | domain, subject, year, page |
| `webapi_get_data` | `/v1/api/list?model=data` | var, th, vervar, turvar, turth |
| `webapi_get_static_table` | `/v1/api/list?model=statictable` | domain, keyword, year, month, page |
| `webapi_list_press_releases` | `/v1/api/list?model=pressrelease` | domain, keyword, year, month, page |
| `webapi_list_publications` | `/v1/api/list?model=publication` | domain, keyword, year, month, page |
| `webapi_list_news` | `/v1/api/list?model=news` | domain, newscat, keyword, year, month, page |
| `webapi_get_indicators` | `/v1/api/list?model=indicators` | domain, var, page |
| `webapi_get_exim_data` | `/v1/api/dataexim` | sumber, kodehs, tahun, periode, jenishs |
| `webapi_get_census_events` | `/v1/api/interoperabilitas/datasource/sensus/id/37` | - |
| `webapi_get_simdasi_provinces` | `/v1/api/interoperabilitas/datasource/simdasi/id/26` | - |
| `webapi_get_kbli` | `/v1/api/list?model=kbli2009/2015/2017/2020` | year, level, page |
| `webapi_search_all` | Multi-endpoint search | keyword, domain |

### 7.2 Missing Endpoints to Add
| Endpoint | Missing Tool | Purpose |
|----------|-------------|---------|
| `/v1/api/list?model=subcat` | `webapi_list_subcategories` | Subject categories |
| `/v1/api/list?model=vervar` | `webapi_list_vertical_vars` | Vertical variable breakdowns |
| `/v1/api/list?model=th` | `webapi_list_periods` | Available years/periods |
| `/v1/api/list?model=turvar` | `webapi_list_derived_vars` | Derived/sub-category variables |
| `/v1/api/list?model=turth` | `webapi_list_derived_periods` | Monthly/quarterly periods |
| `/v1/api/list?model=unit` | `webapi_list_units` | Units of measurement |
| `/v1/api/list?model=sdgs` | `webapi_list_sdgs` | SDGs tables by goal |
| `/v1/api/list?model=sdds` | `webapi_list_sdds` | SDDS tables |
| `/v1/api/list?model=glosarium` | `webapi_list_glosarium` | Statistical glossary |
| `/v1/api/list?model=infographic` | `webapi_list_infographics` | Infographics |
| `/v1/api/list?model=subcatcsa` | `webapi_list_csa_categories` | CSA categories |
| `/v1/api/list?model=subjectcsa` | `webapi_list_csa_subjects` | CSA subjects |
| `/v1/api/list?model=newscategory` | `webapi_list_news_categories` | News categories |
| `/v1/view` (various) | `webapi_get_detail` | Detail endpoints |

---

## 8. Query Recipes — How to Get Specific Data

### 8.1 Inflation Data (IHK)
```
# Step 1: Get IHK variable
GET /v1/api/list?model=var&domain=0000&subject=26&keyword=inflasi
→ Find var_id (e.g., 2262 for MoM, 2263 for YoY)

# Step 2: Get periods
GET /v1/api/list?model=th&domain=0000&var=2262
→ Get th_id for latest year

# Step 3: Get data
GET /v1/api/list?model=data&domain=0000&var=2262&th={th_id}
→ Returns IHK values

# Alternative: Use indicators endpoint
GET /v1/api/list?model=indicators&domain=0000&keyword=inflasi
→ Returns ready-made inflation indicators
```

### 8.2 PDRB by Province
```
# Step 1: Get PDRB variables
GET /v1/api/list?model=var&domain=5300&subject=1&keyword=PDRB
→ Find var_id for PDRB

# Step 2: Get vertical breakdown (kabupaten)
GET /v1/api/list?model=vervar&domain=5300&var={var_id}
→ Get vervar_id for each kabupaten

# Step 3: Get periods
GET /v1/api/list?model=th&domain=5300&var={var_id}
→ Get th_id for years

# Step 4: Get data
GET /v1/api/list?model=data&domain=5300&var={var_id}&th={th_id}&vervar={vervar_id}
→ Returns PDRB values per kabupaten
```

### 8.3 Poverty Rate by Province
```
# Using SDGs endpoint
GET /v1/api/list?model=data&domain=0000&var=192&th={th_id}&vervar=9999
→ Poverty rate by province

# Using indicators
GET /v1/api/list?model=indicators&domain=0000&keyword=poverty
→ Ready-made poverty indicators
```

### 8.4 Unemployment by Education Level
```
GET /v1/api/list?model=data&domain=0000&var=1179&th={th_id}
→ Unemployment rate by education level
```

### 8.5 School Enrollment by Province
```
GET /v1/api/list?model=data&domain=0000&var=1443&th={th_id}&vervar={vervar_id}
→ Gross enrollment rate (university) by province
```

---

*Last updated: 2026-04-11*
*Complete BPS WebAPI mapping with CSA Subject categories, SDGs, SDDS, and dynamic table retrieval guide*
