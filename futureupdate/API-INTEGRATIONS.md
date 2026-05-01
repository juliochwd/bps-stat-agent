# BPS Academic Research Agent — API Integrations

**Version:** 2.0  
**Updated:** 2025-07-14  
**Total APIs:** 14

---

## API Overview

| # | API | Purpose | Auth | Rate Limit | Cost | Integration |
|---|-----|---------|------|-----------|------|-------------|
| 1 | Semantic Scholar | 200M+ papers, citations, SPECTER2 embeddings | Optional API key | 1 RPS (keyed) | Free | Native tool |
| 2 | CrossRef | 150M+ DOIs, BibTeX content negotiation | Email (polite pool) | ~50 RPS | Free | Native tool |
| 3 | OpenAlex | 474M works, authors, institutions | Free API key | 10 RPS | Free | Native tool |
| 4 | CORE | 300M+ records, 40M full-text PDFs | API key required | 5-10/10sec | Free | Native tool |
| 5 | Unpaywall | 30M+ DOIs with OA status | Email param | 100K/day | Free | Native tool |
| 6 | Elicit | 138M+ papers, automated research reports | API key (OAuth 2.0) | Tier-based | Freemium | MCP server |
| 7 | ScholarAI | 200M+ papers, neural OCR, RAG | API key | Tier-based | Freemium | MCP server |
| 8 | PubMed/NCBI | Biomedical literature (36M+ citations) | API key optional | 3-10 RPS | Free | Native tool |
| 9 | arXiv | Preprints (2.4M+ papers) | None | 1 req/3sec | Free | Native tool |
| 10 | Europe PMC | European biomedical literature | None | Reasonable use | Free | Native tool |
| 11 | DBLP | Computer science bibliography | None | Reasonable use | Free | Native tool |
| 12 | E2B | Cloud code execution sandbox | API key | Tier-based | Freemium | Library (SDK) |
| 13 | LanguageTool | Grammar & style checking | None / API key | 20-80 req/min | Free/Premium | Self-hosted |
| 14 | Overleaf Git | LaTeX project access, compile, PDF | Git credentials | N/A | Subscription | MCP server |

---

## 1. Semantic Scholar API

### Base Configuration

```python
BASE_URL = "https://api.semanticscholar.org/graph/v1"
RECOMMENDATIONS_URL = "https://api.semanticscholar.org/recommendations/v1"
HEADERS = {"x-api-key": "${SEMANTIC_SCHOLAR_API_KEY}"}  # Optional but recommended
RATE_LIMIT = 1  # requests per second (with key)
COVERAGE = "200M+ papers"
```

### Key Endpoints

#### Paper Search
```
GET /paper/search
Params: query, limit (max 100), offset, fields, year, fieldsOfStudy
Fields: paperId, title, abstract, year, citationCount, authors, venue, 
        openAccessPdf, references, citations, tldr, s2FieldsOfStudy,
        embedding (SPECTER2 768-dim vector)
```

#### Paper by ID
```
GET /paper/{paper_id}
Supports: S2 ID, DOI:xxx, ArXiv:xxx, PMID:xxx, CorpusId:xxx
Fields: (same as search + embedding, references.title, citations.title)
```

#### Batch Paper Lookup
```
POST /paper/batch
Body: {"ids": ["DOI:xxx", "CorpusId:xxx", ...]}  (max 500)
Params: fields
```

#### Citations & References
```
GET /paper/{paper_id}/citations
GET /paper/{paper_id}/references
Params: fields, limit, offset
```

#### Author Search
```
GET /author/search
Params: query, fields (name, hIndex, paperCount, citationCount, papers)
```

#### Recommendations
```
GET /recommendations/v1/papers/forpaper/{paper_id}
Params: fields, limit, from (pool: recent-papers | all-papers)
```

### Response Format

```json
{
  "total": 1000,
  "offset": 0,
  "data": [
    {
      "paperId": "abc123",
      "title": "Attention Is All You Need",
      "abstract": "The dominant sequence transduction models...",
      "year": 2017,
      "citationCount": 95000,
      "authors": [{"authorId": "123", "name": "Ashish Vaswani"}],
      "venue": "NeurIPS",
      "openAccessPdf": {"url": "https://arxiv.org/pdf/1706.03762"},
      "tldr": {"text": "This paper presents the Transformer architecture..."},
      "embedding": {"model": "specter2", "vector": [0.12, -0.34, "..."]}
    }
  ]
}
```

### Python Example

```python
import aiohttp
import asyncio

class SemanticScholarClient:
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    RPS = 1
    
    def __init__(self, api_key: str = None):
        self.headers = {}
        if api_key:
            self.headers["x-api-key"] = api_key
    
    async def search_papers(self, query: str, limit: int = 10, fields: list = None):
        default_fields = ["paperId", "title", "abstract", "year", 
                         "citationCount", "authors", "venue", "openAccessPdf", "tldr"]
        params = {
            "query": query,
            "limit": min(limit, 100),
            "fields": ",".join(fields or default_fields)
        }
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.BASE_URL}/paper/search", params=params) as resp:
                resp.raise_for_status()
                return await resp.json()
    
    async def get_paper(self, paper_id: str, fields: list = None):
        default_fields = ["paperId", "title", "abstract", "year", "citationCount",
                         "authors", "references", "citations", "embedding"]
        params = {"fields": ",".join(fields or default_fields)}
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.BASE_URL}/paper/{paper_id}", params=params) as resp:
                resp.raise_for_status()
                return await resp.json()
    
    async def get_recommendations(self, paper_id: str, limit: int = 10):
        url = f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{paper_id}"
        params = {"fields": "paperId,title,year,citationCount", "limit": limit}
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                return await resp.json()
```

### Caching Strategy
- **TTL:** 30 days for paper metadata, 7 days for search results
- **Key:** SHA256 hash of (endpoint + sorted params)
- **Invalidation:** Citation counts refresh weekly

### Rate Limiting
- Token bucket: 1 request/second with key, 100/5min without
- Exponential backoff on 429 responses
- Retry-After header respected

### Agent Integration
- **Type:** Native tool
- **Tool name:** `semantic_scholar_search`, `semantic_scholar_paper`, `semantic_scholar_recommend`
- **Use case:** Primary citation graph analysis, paper recommendations, SPECTER2 embeddings for similarity

---

## 2. CrossRef API

### Base Configuration

```python
BASE_URL = "https://api.crossref.org"
POLITE_EMAIL = "${CROSSREF_EMAIL}"  # For polite pool (higher priority)
RATE_LIMIT = 50  # requests per second (polite pool)
COVERAGE = "150M+ DOIs"
```

### Key Endpoints

#### DOI Lookup
```
GET /works/{doi}
Headers: User-Agent: "BPSAcademicAgent/2.0 (mailto:email@example.com)"
Returns: Full metadata (title, authors, published-date, references, ISSN, license)
```

#### Works Search
```
GET /works
Params: query, rows (max 1000), offset, sort, order, filter
Filters: from-pub-date, until-pub-date, type, has-abstract, has-references, 
         is-oa, funder, ISSN, publisher-name
Sort: relevance, published, indexed, is-referenced-by-count
```

#### Content Negotiation (DOI to BibTeX)
```
GET https://doi.org/{doi}
Headers: Accept: application/x-bibtex
Returns: BibTeX entry as text

GET https://doi.org/{doi}
Headers: Accept: application/vnd.citationstyles.csl+json
Returns: CSL-JSON metadata

GET https://doi.org/{doi}
Headers: Accept: text/x-bibliography; style=apa
Returns: Formatted APA citation string
```

#### Journal Works
```
GET /journals/{issn}/works
Params: rows, offset, filter
```

### Response Format

```json
{
  "status": "ok",
  "message-type": "work",
  "message": {
    "DOI": "10.1038/nature12373",
    "title": ["Paper Title"],
    "author": [{"given": "John", "family": "Smith", "affiliation": [{"name": "MIT"}]}],
    "published-print": {"date-parts": [[2023, 6, 15]]},
    "container-title": ["Nature"],
    "volume": "498",
    "page": "255-260",
    "reference-count": 45,
    "is-referenced-by-count": 1200,
    "reference": [{"DOI": "10.xxx", "article-title": "..."}],
    "license": [{"URL": "...", "content-version": "vor"}]
  }
}
```

### Python Example

```python
import aiohttp

class CrossRefClient:
    BASE_URL = "https://api.crossref.org"
    RPS = 50
    
    def __init__(self, email: str):
        self.email = email
        self.headers = {"User-Agent": f"BPSAcademicAgent/2.0 (mailto:{email})"}
    
    async def get_work(self, doi: str) -> dict:
        url = f"{self.BASE_URL}/works/{doi}"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["message"]
    
    async def search_works(self, query: str, rows: int = 20, filters: dict = None) -> dict:
        params = {"query": query, "rows": min(rows, 1000)}
        if filters:
            filter_str = ",".join(f"{k}:{v}" for k, v in filters.items())
            params["filter"] = filter_str
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.BASE_URL}/works", params=params) as resp:
                resp.raise_for_status()
                return await resp.json()
    
    async def get_bibtex(self, doi: str) -> str:
        headers = {"Accept": "application/x-bibtex"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://doi.org/{doi}", headers=headers) as resp:
                resp.raise_for_status()
                return await resp.text()
```

### Caching Strategy
- **TTL:** 30 days for DOI lookups (metadata rarely changes), 7 days for search
- **Key:** DOI (permanent identifier) or query hash
- **BibTeX:** Cache indefinitely (immutable once published)

### Rate Limiting
- Polite pool: include email in User-Agent header -> ~50 RPS
- Without email: ~1 RPS, deprioritized
- 429 responses include Retry-After header

### Agent Integration
- **Type:** Native tool
- **Tool name:** `crossref_lookup`, `crossref_search`, `crossref_bibtex`
- **Use case:** DOI verification, BibTeX generation, reference metadata

---

## 3. OpenAlex API

### Base Configuration

```python
BASE_URL = "https://api.openalex.org"
API_KEY = "${OPENALEX_API_KEY}"  # Free, get at openalex.org/settings/api
RATE_LIMIT = 10  # requests per second
DAILY_LIMIT = 10000  # list calls per day (free tier)
COVERAGE = "474M works, 90M authors, 110K institutions"
```

### Key Endpoints

#### Works Search
```
GET /works
Params: search, filter, sort, per_page (max 200), page, cursor, group_by, api_key
Filters: publication_year, is_oa, type, institutions.ror, authorships.author.id,
         primary_topic.id, cited_by_count, from_publication_date
Sort: cited_by_count:desc, publication_date:desc, relevance_score:desc
```

#### Work by ID
```
GET /works/{openalex_id}
GET /works/doi:{doi}
GET /works/pmid:{pmid}
```

#### Authors
```
GET /authors/{id}
GET /authors?search=name&filter=...
Fields: display_name, works_count, cited_by_count, h_index, affiliations
```

#### Institutions
```
GET /institutions/{ror_id}
Fields: display_name, ror, country_code, works_count, cited_by_count
```

#### Aggregation (group_by)
```
GET /works?filter=publication_year:2020-2024&group_by=publication_year
GET /works?filter=authorships.author.id:{id}&group_by=primary_topic.field.id
Returns: counts per group for trend analysis
```

### Response Format

```json
{
  "meta": {"count": 1000, "per_page": 25, "next_cursor": "IlsxNjk..."},
  "results": [
    {
      "id": "https://openalex.org/W2741809807",
      "doi": "https://doi.org/10.48550/arXiv.1706.03762",
      "title": "Attention Is All You Need",
      "publication_year": 2017,
      "cited_by_count": 95000,
      "is_oa": true,
      "authorships": [{"author": {"id": "...", "display_name": "Ashish Vaswani"}}],
      "primary_location": {"source": {"display_name": "NeurIPS"}},
      "abstract_inverted_index": {"The": [0], "dominant": [1]},
      "topics": [{"display_name": "Transformer Models", "score": 0.98}],
      "open_access": {"is_oa": true, "oa_url": "https://arxiv.org/pdf/1706.03762"}
    }
  ]
}
```

### Python Example

```python
import aiohttp

class OpenAlexClient:
    BASE_URL = "https://api.openalex.org"
    RPS = 10
    
    def __init__(self, api_key: str = None, email: str = None):
        self.params = {}
        if api_key:
            self.params["api_key"] = api_key
        if email:
            self.params["mailto"] = email
    
    async def search_works(self, query: str, filters: dict = None, 
                           per_page: int = 25, sort: str = None) -> dict:
        params = {**self.params, "search": query, "per_page": min(per_page, 200)}
        if filters:
            params["filter"] = ",".join(f"{k}:{v}" for k, v in filters.items())
        if sort:
            params["sort"] = sort
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/works", params=params) as resp:
                resp.raise_for_status()
                return await resp.json()
    
    async def get_work(self, identifier: str) -> dict:
        if identifier.startswith("10."):
            identifier = f"doi:{identifier}"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/works/{identifier}", params=self.params
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
    
    def reconstruct_abstract(self, inverted_index: dict) -> str:
        if not inverted_index:
            return ""
        word_positions = []
        for word, positions in inverted_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        return " ".join(word for _, word in word_positions)
```

### Caching Strategy
- **TTL:** 7 days (data updates weekly from upstream sources)
- **Key:** Query + filters hash, or OpenAlex ID
- **Cursor pagination:** Cache page-by-page with cursor as part of key

### Rate Limiting
- 10 RPS with API key, lower without
- 10K list calls/day on free tier
- Use cursor-based pagination for large result sets

### Agent Integration
- **Type:** Native tool
- **Tool name:** `openalex_search`, `openalex_work`, `openalex_author`, `openalex_trends`
- **Use case:** Broad literature search, trend analysis, institutional data, topic mapping

---

## 4. CORE API

### Base Configuration

```python
BASE_URL = "https://api.core.ac.uk/v3"
HEADERS = {"Authorization": "Bearer ${CORE_API_KEY}"}
RATE_LIMIT = 0.5  # 5 requests per 10 seconds
COVERAGE = "300M+ records, 40M full-text PDFs"
```

### Key Endpoints

#### Search Works
```
GET /search/works
Params: q, limit (max 100), offset, entity_type
Query syntax: title:(machine learning) AND year:>2020
```

#### Get Work / Download PDF / Batch
```
GET /works/{core_id}
GET /works/{core_id}/download
POST /works/batch  Body: {"ids": [id1, id2, ...]}
```

### Python Example

```python
import aiohttp

class COREClient:
    BASE_URL = "https://api.core.ac.uk/v3"
    RPS = 0.5
    
    def __init__(self, api_key: str):
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    async def search(self, query: str, limit: int = 10) -> dict:
        params = {"q": query, "limit": min(limit, 100)}
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.BASE_URL}/search/works", params=params) as resp:
                resp.raise_for_status()
                return await resp.json()
    
    async def download_pdf(self, core_id: int, output_path: str) -> str:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f"{self.BASE_URL}/works/{core_id}/download") as resp:
                resp.raise_for_status()
                with open(output_path, "wb") as f:
                    f.write(await resp.read())
                return output_path
```

### Caching / Rate Limiting / Integration
- **Cache TTL:** 30 days metadata, indefinite for PDFs
- **Rate:** 5 requests per 10-second window, sliding window with backoff
- **Type:** Native tool (`core_search`, `core_fulltext`, `core_download_pdf`)

---

## 5. Unpaywall API

### Base Configuration

```python
BASE_URL = "https://api.unpaywall.org/v2"
EMAIL = "${UNPAYWALL_EMAIL}"
RATE_LIMIT = 1.15  # 100K/day
COVERAGE = "30M+ DOIs with OA status"
```

### Key Endpoints

```
GET /{doi}?email={email}
Returns: OA status, best OA location, all OA locations
```

### Python Example

```python
import aiohttp

class UnpaywallClient:
    BASE_URL = "https://api.unpaywall.org/v2"
    RPS = 1.15
    
    def __init__(self, email: str):
        self.email = email
    
    async def get_oa_status(self, doi: str) -> dict:
        params = {"email": self.email}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/{doi}", params=params) as resp:
                if resp.status == 404:
                    return {"doi": doi, "is_oa": False, "oa_locations": []}
                resp.raise_for_status()
                return await resp.json()
    
    async def find_pdf_url(self, doi: str) -> str | None:
        data = await self.get_oa_status(doi)
        if data.get("best_oa_location"):
            return data["best_oa_location"].get("url_for_pdf")
        return None
```

### Caching / Rate Limiting / Integration
- **Cache TTL:** 7 days (OA status can change as embargoes expire)
- **Rate:** 100K requests/day (~1.15/sec sustained)
- **Type:** Native tool (`unpaywall_check`, `unpaywall_find_pdf`)

---

## 6. Elicit API

### Base Configuration

```python
BASE_URL = "https://elicit.com/api/v1"
HEADERS = {"Authorization": "Bearer ${ELICIT_API_KEY}"}
MCP_URL = "https://elicit.com/api/mcp"  # OAuth 2.0 MCP server
COVERAGE = "138M+ papers"
```

### Key Endpoints

#### Paper Search
```
POST /api/v1/search
Body: {
  "query": "effects of sleep deprivation on cognitive performance",
  "filters": {"year_min": 2018, "year_max": 2024, "study_type": ["rct", "meta-analysis"]},
  "num_results": 20
}
Returns: Papers with extracted claims, study details, relevance scores
```

#### Automated Research Reports
```
POST /api/v1/reports
Body: {
  "query": "What are the effects of intermittent fasting on metabolic health?",
  "report_type": "systematic_review",
  "max_papers": 50
}
Returns: Structured report with synthesized findings, evidence tables
```

#### Extract Data from Papers
```
POST /api/v1/extract
Body: {
  "paper_ids": ["doi:10.xxx", ...],
  "columns": ["sample_size", "intervention", "outcome", "effect_size"]
}
Returns: Structured extraction table
```

### Python Example

```python
import aiohttp

class ElicitClient:
    BASE_URL = "https://elicit.com/api/v1"
    
    def __init__(self, api_key: str):
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    async def search(self, query: str, num_results: int = 20, 
                     year_min: int = None, year_max: int = None) -> dict:
        body = {"query": query, "num_results": num_results, "filters": {}}
        if year_min: body["filters"]["year_min"] = year_min
        if year_max: body["filters"]["year_max"] = year_max
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(f"{self.BASE_URL}/search", json=body) as resp:
                resp.raise_for_status()
                return await resp.json()
    
    async def generate_report(self, query: str, max_papers: int = 50) -> dict:
        body = {"query": query, "report_type": "systematic_review", "max_papers": max_papers}
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(f"{self.BASE_URL}/reports", json=body) as resp:
                resp.raise_for_status()
                return await resp.json()
    
    async def extract_data(self, paper_ids: list, columns: list) -> dict:
        body = {"paper_ids": paper_ids, "columns": columns}
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(f"{self.BASE_URL}/extract", json=body) as resp:
                resp.raise_for_status()
                return await resp.json()
```

### MCP Server Configuration

```json
{
  "mcpServers": {
    "elicit": {
      "url": "https://elicit.com/api/mcp",
      "auth": {
        "type": "oauth2",
        "client_id": "${ELICIT_CLIENT_ID}",
        "client_secret": "${ELICIT_CLIENT_SECRET}",
        "token_url": "https://elicit.com/oauth/token",
        "scopes": ["search", "reports", "extract"]
      }
    }
  }
}
```

### Caching / Rate Limiting / Integration
- **Cache TTL:** 7 days search, 30 days reports (cache reports indefinitely)
- **Rate:** Tier-based: Free (100/month), Pro (10K/month). Respect X-RateLimit-Remaining
- **Type:** MCP server (preferred) or native tool. Tools: `elicit_search`, `elicit_report`, `elicit_extract`
- **Use case:** AI-powered paper search with claim extraction, automated literature reviews

---

## 7. ScholarAI API

### Base Configuration

```python
MCP_PACKAGE = "scholarai-mcp"  # npm install scholarai-mcp
API_KEY = "${SCHOLARAI_API_KEY}"
COVERAGE = "200M+ papers with neural OCR and RAG"
```

### Key MCP Tools

```
search_papers: Semantic search across 200M+ papers
  Params: query, num_results, year_range, sort_by

literature_map: Citation network visualization
  Params: seed_paper_doi, depth, max_papers

summarize_paper: Neural OCR full-text summarization
  Params: paper_id, summary_type (abstract|methods|results|full)

ask_paper: Question answering over paper content
  Params: paper_id, question
```

### MCP Configuration

```json
{
  "mcpServers": {
    "scholarai": {
      "command": "npx",
      "args": ["scholarai-mcp"],
      "env": {"SCHOLARAI_API_KEY": "${SCHOLARAI_API_KEY}"}
    }
  }
}
```

### Python Example (Direct API)

```python
import aiohttp

class ScholarAIClient:
    BASE_URL = "https://api.scholarai.io/v1"
    
    def __init__(self, api_key: str):
        self.headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    async def semantic_search(self, query: str, num_results: int = 20) -> dict:
        body = {"query": query, "num_results": num_results}
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(f"{self.BASE_URL}/search", json=body) as resp:
                resp.raise_for_status()
                return await resp.json()
    
    async def summarize(self, paper_id: str, summary_type: str = "full") -> dict:
        body = {"paper_id": paper_id, "summary_type": summary_type}
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(f"{self.BASE_URL}/summarize", json=body) as resp:
                resp.raise_for_status()
                return await resp.json()
```

### Caching / Rate Limiting / Integration
- **Cache TTL:** 30 days search, indefinite for summaries
- **Rate:** Tier-based with rate limit headers
- **Type:** MCP server (primary). Install: `npm install scholarai-mcp`
- **Use case:** Semantic search with RAG, full-text analysis, literature mapping

---

## 8. PubMed/NCBI E-utilities

### Base Configuration

```python
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
API_KEY = "${NCBI_API_KEY}"  # Optional but recommended
RATE_LIMIT_NO_KEY = 3   # requests per second without key
RATE_LIMIT_WITH_KEY = 10  # requests per second with key
COVERAGE = "36M+ biomedical citations"
```

### Key Endpoints

#### ESearch (find PMIDs)
```
GET /esearch.fcgi?db=pubmed&term={query}&retmax=100&retmode=json&api_key={key}
Params: sort=relevance|pub_date, datetype=pdat, mindate, maxdate
```

#### EFetch (get records)
```
GET /efetch.fcgi?db=pubmed&id={pmids}&rettype=abstract&retmode=xml&api_key={key}
Max 200 PMIDs per request. Returns: title, abstract, MeSH terms, authors, journal
```

#### ELink (related articles)
```
GET /elink.fcgi?dbfrom=pubmed&db=pubmed&id={pmid}&cmd=neighbor_score&api_key={key}
```

#### ESummary (brief metadata)
```
GET /esummary.fcgi?db=pubmed&id={pmids}&retmode=json&api_key={key}
```

### Python Example

```python
import aiohttp
import xml.etree.ElementTree as ET

class PubMedClient:
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, api_key: str = None):
        self.params = {}
        if api_key:
            self.params["api_key"] = api_key
            self.rps = 10
        else:
            self.rps = 3
    
    async def search(self, query: str, max_results: int = 20) -> list[str]:
        params = {**self.params, "db": "pubmed", "term": query,
                  "retmax": min(max_results, 10000), "retmode": "json", "sort": "relevance"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/esearch.fcgi", params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["esearchresult"]["idlist"]
    
    async def fetch_abstracts(self, pmids: list[str]) -> list[dict]:
        params = {**self.params, "db": "pubmed", "id": ",".join(pmids[:200]),
                  "rettype": "abstract", "retmode": "xml"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/efetch.fcgi", params=params) as resp:
                resp.raise_for_status()
                return self._parse_pubmed_xml(await resp.text())
    
    def _parse_pubmed_xml(self, xml_text: str) -> list[dict]:
        root = ET.fromstring(xml_text)
        papers = []
        for article in root.findall(".//PubmedArticle"):
            medline = article.find("MedlineCitation")
            art = medline.find("Article")
            papers.append({
                "pmid": medline.find("PMID").text,
                "title": art.find("ArticleTitle").text or "",
                "authors": [f"{a.find('LastName').text} {a.find('ForeName').text}"
                           for a in art.findall(".//Author") if a.find("LastName") is not None],
                "journal": art.find("Journal/Title").text if art.find("Journal/Title") is not None else "",
                "mesh_terms": [m.find("DescriptorName").text 
                              for m in medline.findall(".//MeshHeading")
                              if m.find("DescriptorName") is not None]
            })
        return papers
```

### Caching / Rate Limiting / Integration
- **Cache TTL:** 30 days for records, 7 days for search
- **Rate:** 3 RPS without key, 10 RPS with key. Batch PMIDs (up to 200/request)
- **Type:** Native tool (`pubmed_search`, `pubmed_fetch`, `pubmed_related`)
- **Use case:** Biomedical literature, MeSH-based queries, clinical evidence

---

## 9. arXiv API

### Base Configuration

```python
BASE_URL = "http://export.arxiv.org/api/query"
RATE_LIMIT = 0.33  # 1 request per 3 seconds
BULK_ACCESS = "s3://arxiv"  # For bulk downloads
COVERAGE = "2.4M+ preprints (physics, CS, math, biology)"
FORMAT = "Atom 1.0 XML feed"
```

### Key Endpoints

#### Search
```
GET http://export.arxiv.org/api/query
Params: search_query, start, max_results (max 30000), sortBy, sortOrder

Query prefixes: ti: (title), au: (author), abs: (abstract), cat: (category), all: (all)
Boolean: AND, OR, ANDNOT
Categories: cs.CL, cs.AI, cs.LG, stat.ML, q-bio, math, physics, etc.
```

#### By ID / PDF Access
```
GET http://export.arxiv.org/api/query?id_list=2301.12345
GET https://arxiv.org/pdf/{arxiv_id}.pdf
GET https://arxiv.org/e-print/{arxiv_id}  (LaTeX source)
```

### Python Example

```python
import aiohttp
import xml.etree.ElementTree as ET

class ArXivClient:
    BASE_URL = "http://export.arxiv.org/api/query"
    RPS = 0.33
    ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    
    async def search(self, query: str, max_results: int = 10, category: str = None) -> list[dict]:
        search_query = f"{query}+AND+cat:{category}" if category else query
        params = {"search_query": search_query, "start": 0,
                  "max_results": min(max_results, 100), "sortBy": "relevance"}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL, params=params) as resp:
                resp.raise_for_status()
                return self._parse_feed(await resp.text())
    
    def _parse_feed(self, xml_text: str) -> list[dict]:
        root = ET.fromstring(xml_text)
        papers = []
        for entry in root.findall("atom:entry", self.ATOM_NS):
            arxiv_id = entry.find("atom:id", self.ATOM_NS).text.split("/abs/")[-1]
            papers.append({
                "arxiv_id": arxiv_id,
                "title": entry.find("atom:title", self.ATOM_NS).text.strip(),
                "abstract": entry.find("atom:summary", self.ATOM_NS).text.strip(),
                "authors": [a.find("atom:name", self.ATOM_NS).text 
                           for a in entry.findall("atom:author", self.ATOM_NS)],
                "published": entry.find("atom:published", self.ATOM_NS).text,
                "categories": [c.get("term") for c in entry.findall("atom:category", self.ATOM_NS)],
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            })
        return papers
```

### Caching / Rate Limiting / Integration
- **Cache TTL:** 7 days search, 30 days paper metadata. Track version updates
- **Rate:** 1 request per 3 seconds (strict). For bulk: use S3 bucket or OAI-PMH
- **Type:** Native tool (`arxiv_search`, `arxiv_paper`, `arxiv_download`)
- **Use case:** Preprint discovery, CS/physics/math, latest research before peer review

---

## 10. Europe PMC API

### Base Configuration

```python
BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"
RATE_LIMIT = 10  # reasonable use
AUTH = None  # No authentication required
COVERAGE = "40M+ biomedical and life sciences articles"
```

### Key Endpoints

#### Search
```
GET /search?query={query}&resultType=core&pageSize=25&format=json&synonym=true
Query syntax: TITLE:"...", AUTH:"...", PUB_YEAR:[2020 TO 2024], HAS_FT:Y, OPEN_ACCESS:Y
```

#### Full Text XML / Citations / Annotations
```
GET /articles/PMC/{pmcid}/fullTextXML  (JATS XML)
GET /citations/{id}/{source}?format=json
GET /annotations/PMC/{pmcid}?format=json  (genes, diseases, chemicals)
```

### Python Example

```python
import aiohttp

class EuropePMCClient:
    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    RPS = 10
    
    async def search(self, query: str, page_size: int = 25) -> dict:
        params = {"query": query, "resultType": "core", "pageSize": min(page_size, 1000),
                  "format": "json", "synonym": "true"}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/search", params=params) as resp:
                resp.raise_for_status()
                return await resp.json()
    
    async def get_full_text_xml(self, pmcid: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/articles/PMC/{pmcid}/fullTextXML") as resp:
                resp.raise_for_status()
                return await resp.text()
    
    async def get_annotations(self, pmcid: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/annotations/PMC/{pmcid}", params={"format": "json"}
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
```

### Caching / Rate Limiting / Integration
- **Cache TTL:** 14 days search, 30 days full text (indefinite post-publication)
- **Rate:** ~10 RPS recommended, cursor-based pagination for large sets
- **Type:** Native tool (`europepmc_search`, `europepmc_fulltext`, `europepmc_citations`, `europepmc_annotations`)
- **Use case:** Biomedical full-text access, entity extraction, European research

---

## 11. DBLP API

### Base Configuration

```python
BASE_URL = "https://dblp.org/search"
RATE_LIMIT = 5  # reasonable use
AUTH = None  # No authentication required
COVERAGE = "6.5M+ computer science publications"
```

### Key Endpoints

#### Publication Search
```
GET /publ/api?q={query}&h=30&f=0&format=json&c=0
Query: author:vaswani, venue:neurips, year:2023, type:Conference_and_Workshop_Papers
```

#### Author / Venue / BibTeX
```
GET /search/author/api?q={name}&format=json
GET https://dblp.org/pid/{author_pid}.json
GET https://dblp.org/rec/{dblp_key}.bib
```

### Python Example

```python
import aiohttp

class DBLPClient:
    BASE_URL = "https://dblp.org/search"
    RPS = 5
    
    async def search_publications(self, query: str, max_results: int = 30) -> dict:
        params = {"q": query, "h": min(max_results, 1000), "f": 0, "format": "json", "c": 0}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/publ/api", params=params) as resp:
                resp.raise_for_status()
                return await resp.json()
    
    async def get_bibtex(self, dblp_key: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://dblp.org/rec/{dblp_key}.bib") as resp:
                resp.raise_for_status()
                return await resp.text()
```

### Caching / Rate Limiting / Integration
- **Cache TTL:** 7 days search, BibTeX cached indefinitely
- **Rate:** ~5 RPS (community resource, be respectful)
- **Type:** Native tool (`dblp_search`, `dblp_author`, `dblp_bibtex`)
- **Use case:** CS-specific search, author disambiguation, venue discovery, BibTeX export

---

## 12. E2B API (Code Execution Sandbox)

### Base Configuration

```python
# pip install e2b-code-interpreter
from e2b_code_interpreter import Sandbox

API_KEY = "${E2B_API_KEY}"
DEFAULT_TIMEOUT = 300  # seconds
MAX_SESSION_DURATION = 86400  # 24 hours
```

### Key Capabilities

```python
# Create sandbox with isolated Jupyter kernel
sandbox = Sandbox(api_key=E2B_API_KEY)

# Execute code
execution = sandbox.run_code("import pandas as pd; print(pd.__version__)")
print(execution.text)    # stdout
print(execution.error)   # stderr/exceptions
print(execution.results) # rich outputs (images, dataframes)

# File operations
sandbox.files.write("/home/user/data.csv", csv_content)
content = sandbox.files.read("/home/user/output.pdf")

# Install packages
sandbox.run_code("!pip install scikit-learn transformers")
```

### Python Example

```python
from e2b_code_interpreter import Sandbox

class E2BSandboxManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._sandbox = None
    
    def get_sandbox(self) -> Sandbox:
        if self._sandbox is None:
            self._sandbox = Sandbox(api_key=self.api_key)
        return self._sandbox
    
    def execute_analysis(self, code: str, files: dict = None) -> dict:
        sandbox = self.get_sandbox()
        if files:
            for path, content in files.items():
                sandbox.files.write(path, content)
        execution = sandbox.run_code(code)
        return {
            "stdout": execution.text,
            "error": execution.error,
            "results": execution.results,
            "success": execution.error is None
        }
    
    def close(self):
        if self._sandbox:
            self._sandbox.close()
            self._sandbox = None
```

### Caching / Rate Limiting / Integration
- **Cache:** No caching (non-deterministic execution)
- **Rate:** Tier-based, limited concurrent sandboxes, 300s default timeout
- **Type:** Library SDK. Install: `pip install e2b-code-interpreter`
- **Tools:** `e2b_execute`, `e2b_analyze`, `e2b_visualize`
- **Use case:** Statistical analysis, data visualization, research computations

---

## 13. LanguageTool API

### Base Configuration

```python
SELF_HOSTED_URL = "http://localhost:8081/v2"  # Unlimited
CLOUD_URL = "https://api.languagetoolplus.com/v2"
CLOUD_API_KEY = "${LANGUAGETOOL_API_KEY}"  # Optional for premium
RATE_LIMIT_FREE = 20      # req/min (cloud)
RATE_LIMIT_PREMIUM = 80   # req/min (cloud premium)
```

### Key Endpoints

#### Check Text
```
POST /check
Body: text={text}&language=en-US&level=picky
Returns: matches with rule ID, message, replacements, offset, length
```

#### Check with Markup (LaTeX)
```
POST /check
Body: data={"annotation": [{"text": "..."}, {"markup": "\\textbf{", "interpretAs": ""}]}
```

### Self-Hosted Setup

```bash
docker run -d --name languagetool -p 8081:8010 -e JAVA_OPTS="-Xmx2g" erikvl87/languagetool
```

### Python Example

```python
import aiohttp
import json

class LanguageToolClient:
    def __init__(self, url: str = None, api_key: str = None):
        self.url = url or "http://localhost:8081/v2"
        self.api_key = api_key
    
    async def check_text(self, text: str, language: str = "en-US", level: str = "picky") -> dict:
        data = {"text": text, "language": language, "level": level}
        if self.api_key:
            data["apiKey"] = self.api_key
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.url}/check", data=data) as resp:
                resp.raise_for_status()
                return await resp.json()
    
    async def apply_corrections(self, text: str, matches: list) -> str:
        corrected = text
        for match in sorted(matches, key=lambda m: m["offset"], reverse=True):
            if match["replacements"]:
                start = match["offset"]
                end = start + match["length"]
                corrected = corrected[:start] + match["replacements"][0]["value"] + corrected[end:]
        return corrected
```

### Caching / Rate Limiting / Integration
- **Cache:** No caching (text changes between checks)
- **Rate:** Self-hosted unlimited; Cloud free 20/min, premium 80/min
- **Type:** Self-hosted service (preferred) or cloud API
- **Tools:** `grammar_check`, `style_check`, `latex_check`
- **Use case:** Academic writing quality, LaTeX proofreading, style consistency

---

## 14. Overleaf Git API (via MCP)

### Base Configuration

```python
OVERLEAF_GIT_URL = "https://git.overleaf.com/{project_id}"
AUTH = "git credentials (username: email, password: Overleaf token)"
MCP_PACKAGE = "overleaf-mcp"
```

### Key Capabilities

```bash
# Clone, edit, push
git clone https://git.overleaf.com/{project_id} ./my-paper
# Edit files...
git add . && git commit -m "Updated methodology" && git push
```

### MCP Configuration

```json
{
  "mcpServers": {
    "overleaf": {
      "command": "npx",
      "args": ["overleaf-mcp"],
      "env": {
        "OVERLEAF_EMAIL": "${OVERLEAF_EMAIL}",
        "OVERLEAF_TOKEN": "${OVERLEAF_TOKEN}",
        "OVERLEAF_PROJECT_ID": "${OVERLEAF_PROJECT_ID}"
      }
    }
  }
}
```

### MCP Tools

```
overleaf_read_file:   Read file from project
overleaf_write_file:  Write file and sync to collaborators
overleaf_compile:     Compile LaTeX, return PDF URL + errors
overleaf_list_files:  List project file tree
overleaf_get_pdf:     Download compiled PDF
```

### Python Example

```python
import subprocess
import tempfile
import os

class OverleafClient:
    def __init__(self, email: str, token: str, project_id: str):
        self.git_url = f"https://{email}:{token}@git.overleaf.com/{project_id}"
        self.local_path = None
    
    def clone_project(self, local_path: str = None) -> str:
        self.local_path = local_path or tempfile.mkdtemp(prefix="overleaf_")
        subprocess.run(["git", "clone", self.git_url, self.local_path],
                      check=True, capture_output=True)
        return self.local_path
    
    def write_file(self, file_path: str, content: str) -> None:
        if not self.local_path: self.clone_project()
        full_path = os.path.join(self.local_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f: f.write(content)
        subprocess.run(["git", "add", file_path], cwd=self.local_path, check=True)
        subprocess.run(["git", "commit", "-m", f"Update {file_path}"],
                      cwd=self.local_path, check=True)
        subprocess.run(["git", "push"], cwd=self.local_path, check=True)
```

### Caching / Rate Limiting / Integration
- **Cache:** No caching (always pull latest). PDF compilation cached 5 min
- **Rate:** No strict limit; avoid rapid push/pull. ~1 compile/10sec
- **Type:** MCP server (preferred) or Git-based library
- **Use case:** Direct LaTeX editing, collaborative writing, PDF compilation

---

## 15. Rate Limiting & Caching Architecture

### Base Client Pattern

```python
import asyncio, hashlib, json, time
from pathlib import Path

class AsyncRateLimiter:
    def __init__(self, requests_per_second: float):
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self._last_request = 0.0
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        async with self._lock:
            elapsed = time.monotonic() - self._last_request
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
            self._last_request = time.monotonic()

class DiskCache:
    def __init__(self, cache_dir: str, ttl_days: int = 30):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_days * 86400
    
    def get(self, key: str):
        path = self.cache_dir / f"{hashlib.sha256(key.encode()).hexdigest()}.json"
        if not path.exists(): return None
        data = json.loads(path.read_text())
        if time.time() - data["timestamp"] > self.ttl_seconds:
            path.unlink()
            return None
        return data["value"]
    
    def set(self, key: str, value):
        path = self.cache_dir / f"{hashlib.sha256(key.encode()).hexdigest()}.json"
        path.write_text(json.dumps({"timestamp": time.time(), "value": value}))

class AcademicAPIClient:
    RPS: float = 1.0
    CACHE_TTL_DAYS: int = 30
    
    def __init__(self, cache_dir: str):
        self.cache = DiskCache(cache_dir, ttl_days=self.CACHE_TTL_DAYS)
        self.rate_limiter = AsyncRateLimiter(self.RPS)
    
    async def _request(self, method: str, url: str, **kwargs) -> dict:
        cache_key = hashlib.sha256(
            json.dumps({"method": method, "url": url, **kwargs}, sort_keys=True).encode()
        ).hexdigest()
        cached = self.cache.get(cache_key)
        if cached is not None: return cached
        await self.rate_limiter.acquire()
        import aiohttp
        for attempt in range(3):
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, **kwargs) as resp:
                    if resp.status == 429:
                        await asyncio.sleep(int(resp.headers.get('Retry-After', 60)))
                        continue
                    resp.raise_for_status()
                    data = await resp.json()
            self.cache.set(cache_key, data)
            return data
```

### Cache Strategy Summary

| API | Cache TTL | Notes |
|-----|-----------|-------|
| Semantic Scholar | 30 days | Citation counts refresh weekly |
| CrossRef | 30 days | BibTeX cached indefinitely |
| OpenAlex | 7 days | Data updates weekly |
| CORE | 30 days | PDFs cached indefinitely |
| Unpaywall | 7 days | OA status can change |
| Elicit | 7-30 days | Reports cached longer |
| ScholarAI | 30 days | Summaries indefinite |
| PubMed | 30 days | Records rarely change |
| arXiv | 7-30 days | Track version updates |
| Europe PMC | 14 days | Full text cached longer |
| DBLP | 7-30 days | BibTeX indefinite |
| E2B | None | Non-deterministic |
| LanguageTool | None | Text changes |
| Overleaf | None | Always pull latest |

### Graceful Degradation

```python
async def search_with_fallback(query: str, domain: str = "general") -> list:
    if domain == "biomedical":
        apis = [pubmed, europe_pmc, semantic_scholar]
    elif domain == "cs":
        apis = [dblp, semantic_scholar, openalex]
    elif domain == "preprints":
        apis = [arxiv, semantic_scholar, openalex]
    else:
        apis = [openalex, semantic_scholar, crossref]
    
    results = []
    for api in apis:
        try:
            results.extend(await api.search(query))
            if len(results) >= 20: break
        except Exception as e:
            logger.warning(f"{api.__class__.__name__} failed: {e}")
    return deduplicate_by_doi(results)

async def find_pdf_with_fallback(doi: str) -> str | None:
    for name, getter in [
        ("Unpaywall", lambda: unpaywall.find_pdf_url(doi)),
        ("CORE", lambda: core.find_pdf_by_doi(doi)),
        ("S2", lambda: s2.get_pdf_url(doi)),
        ("EuropePMC", lambda: europepmc.find_pdf(doi)),
        ("arXiv", lambda: arxiv.find_pdf_by_doi(doi)),
    ]:
        try:
            url = await getter()
            if url: return url
        except: pass
    return None
```

---

## 16. Authentication Setup

### Environment Variables

```bash
# .env file

# Core Academic APIs
SEMANTIC_SCHOLAR_API_KEY=your_key_here       # Optional (free)
CROSSREF_EMAIL=your@email.com                # Required for polite pool
OPENALEX_API_KEY=your_key_here               # Free at openalex.org
CORE_API_KEY=your_key_here                   # Required, free registration
UNPAYWALL_EMAIL=your@email.com               # Required

# AI-Powered Research APIs
ELICIT_API_KEY=your_key_here                 # From elicit.com/api
ELICIT_CLIENT_ID=your_client_id              # For MCP OAuth
ELICIT_CLIENT_SECRET=your_client_secret      # For MCP OAuth
SCHOLARAI_API_KEY=your_key_here              # From scholarai.io

# Domain-Specific APIs
NCBI_API_KEY=your_key_here                   # From ncbi.nlm.nih.gov/account
NCBI_EMAIL=your@email.com                    # Required by NCBI policy

# Utility APIs
E2B_API_KEY=your_key_here                    # From e2b.dev
LANGUAGETOOL_API_KEY=your_key_here           # Optional (premium cloud)
OVERLEAF_EMAIL=your@email.com                # Overleaf account
OVERLEAF_TOKEN=your_token_here               # Overleaf API token
OVERLEAF_PROJECT_ID=project_id               # Target project
```

---

## 17. API Selection Guide

| Need | Best API | Why |
|------|----------|-----|
| Find papers by topic | OpenAlex | Best coverage (474M works), free |
| Get citation graph | Semantic Scholar | Best citation data, SPECTER2 embeddings |
| Verify DOI / get BibTeX | CrossRef | Authoritative DOI registry |
| Download full-text PDF | CORE | 40M+ full-text papers |
| Find OA version | Unpaywall | 30M+ DOIs with OA status |
| AI-powered literature review | Elicit | Automated reports, claim extraction |
| Semantic search + RAG | ScholarAI | Neural OCR, question answering |
| Biomedical literature | PubMed | MeSH terms, 36M+ citations |
| Latest preprints | arXiv | Fastest access to new research |
| European biomedical | Europe PMC | Full-text XML, annotations |
| CS papers + BibTeX | DBLP | Author disambiguation, venues |
| Run analysis code | E2B | Isolated sandbox, scientific stack |
| Grammar/style check | LanguageTool | LaTeX-aware, self-hostable |
| LaTeX collaboration | Overleaf Git | Direct project access, compile |
| Author metrics | Semantic Scholar | h-index, citation count |
| Institution data | OpenAlex | ROR integration, aggregation |
| Funding information | CrossRef | Funder registry integration |
| Trend analysis | OpenAlex | group_by aggregation |
