# BPS Stat Agent

**BPS Indonesia Statistical Data Agent** — Ainson cari data BPS (Badan Pusat Statistik) seperti inflasi, PDB, IPM, angka harapan hidup, pengangguran, kemiskinan di Indonesia. Dilengkapi **55+ MCP tools** untuk akses lengkap ke BPS WebAPI dan AllStats Search Engine.

> Query contoh: "inflasi NTT terbaru", "PDRB kabupaten kota Jawa Timur", "angka harapan hidup menurut provinsi", "IPM nasional 2024"

## Features

- 🔍 **BPS AllStats Search** - Search 1.6M+ statistical data points across all BPS domains
- 🔁 **AllStats-First Fallback Pipeline** - Search via AllStats, then retrieve structured detail through WebAPI
- 🌏 **Multi-domain Support** - Query national (0000) or provincial data (e.g., 5300=NTT)
- 📊 **Rich Content Types** - Publications, indicators, press releases, tables, infographics
- 🔄 **Auto-retry** - Automatic retry with fresh browser context on Cloudflare blocks
- 🔧 **MCP Server** - 55+ tools running as real MCP server over STDIO
- ⚡ **Fast Installation** - Single command install via uv/pip
- ✅ **Production Ready** - 290+ tests, comprehensive coverage

## Installation

### Option 1: Install via uv (Recommended)

```bash
# Install directly from GitHub
uv tool install git+https://github.com/juliochwd/bps-stat-agent.git
```

### Option 2: Install via pip

```bash
pip install git+https://github.com/juliochwd/bps-stat-agent.git
```

## Configuration

### 1. Run Setup Script

```bash
# macOS/Linux:
curl -fsSL https://raw.githubusercontent.com/juliochwd/bps-stat-agent/main/scripts/setup-config.sh | bash

# Windows (PowerShell):
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/juliochwd/bps-stat-agent/main/scripts/setup-config.ps1" -OutFile "$env:TEMP\setup-config.ps1"
powershell -ExecutionPolicy Bypass -File "$env:TEMP\setup-config.ps1"
```

### 2. Add Your API Key

Edit `~/.bps-stat-agent/config/config.yaml` and add your MiniMax API key:

```yaml
api_key: "your_api_key_here"
```

### Configuration File Locations

Config files are loaded in priority order:
1. `./mini_agent/config/config.yaml` - Current directory (development)
2. `~/.bps-stat-agent/config/config.yaml` - User config directory
3. `<package>/mini_agent/config/config.yaml` - Package installation

## Usage

### CLI Mode

```bash
# Start interactive session
bps-stat-agent

# With specific workspace
bps-stat-agent --workspace /path/to/project

# Show help
bps-stat-agent --help
```

### MCP Server Mode

BPS Stat Agent includes an MCP server that can be used with Claude desktop:

```bash
# Add to your mcp.json:
{
    "mcpServers": {
        "bps": {
            "command": "uvx",
            "args": ["--from", "git+https://github.com/juliochwd/bps-stat-agent.git", "bps-mcp-server"]
        }
    }
}
```

Or run directly:
```bash
uvx --from git+https://github.com/juliochwd/bps-stat-agent.git bps-mcp-server
```

### Python API

```python
from mini_agent.allstats_client import AllStatsClient

async def search_bps():
    client = AllStatsClient(headless=True)
    try:
        response = await client.search(
            keyword="inflasi",
            domain="5300",  # NTT province
            content="all"
        )
        for result in response.results:
            print(f"- {result.title}")
    finally:
        await client.close()
```

## BPS Domain Codes

| Code | Domain |
|:-----|:-------|
| 0000 | Nasional (National) |
| 5300 | Nusa Tenggara Timur (NTT) |
| 1100 | Aceh |
| 1200 | Sumatera Utara |
| ... | Other provinces |

## Content Types

| Type | Indonesian | Description |
|:-----|:-----------|:------------|
| `all` | Semua | All content types |
| `publication` | Publikasi | Statistical publications |
| `indicator` | Indikator | Statistical indicators |
| `table` | Tabel | Dynamic tables |
| `pressrelease` | Berita Resmi Statistik | Official press releases |
| `infographic` | Infografis | Visual data summaries |
| `news` | Berita | BPS news |
| `microdata` | Mikrodata | Raw data files |
| `glosarium` | Glosarium | Statistical glossary |

## Common Queries

```python
# Search inflation data for NTT
response = await client.search("inflasi", domain="5300")

# Search national GDP data
response = await client.search("PDB", domain="0000")

# Search specific content type
response = await client.search("penduduk", domain="5300", content="publication")

# Pagination
response = await client.search("inflasi", domain="5300", page=2)
```

## Architecture

```
bps-stat-agent/
├── mini_agent/
│   ├── __init__.py
│   ├── agent.py          # Main agent implementation
│   ├── cli.py            # CLI entry point
│   ├── config/           # Configuration files
│   │   ├── config-example.yaml
│   │   ├── mcp-example.json
│   │   └── system_prompt.md
│   ├── allstats_client.py  # BPS AllStats Playwright client
│   ├── bps_mcp_server.py   # MCP server implementation
│   └── skills/           # Agent skills
├── scripts/
│   ├── setup-config.sh
│   └── setup-config.ps1
├── pyproject.toml
└── README.md
```

## Retrieval Strategy

1. Search starts from AllStats.
2. The best candidate is ranked by query relevance.
3. The agent resolves the resource type.
4. For tables, it tries direct static-table detail first.
5. If that fails, it falls back to WebAPI keyword table search and retries detail retrieval.
6. Results are normalized with provenance and explicit errors when no supported path succeeds.

## Troubleshooting

### "Cloudflare blocked" errors

The client automatically retries with fresh browser context. If you see repeated blocks:
- Wait 10+ seconds between searches
- Check your network connection

### "API key not found"

Make sure you've configured your API key in `config.yaml` or MCP environment:
```yaml
api_key: "your_api_key_here"
```

For BPS retrieval through the MCP server, also provide:
```json
{
  "BPS_API_KEY": "your_bps_webapi_key"
}
```

### Installation fails

Ensure you have Python 3.10+ and uv/pip installed:
```bash
python --version  # Should be 3.10+
which uv          # or pip
```

## Development

```bash
# Clone the repository
git clone https://github.com/juliochwd/bps-stat-agent.git
cd bps-stat-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e .

# Run tests
pytest tests/

# Test the search client directly
.venv/bin/python -c "
import asyncio
from mini_agent.allstats_client import AllStatsClient

async def test():
    client = AllStatsClient()
    try:
        response = await client.search('inflasi', domain='5300')
        print(f'Found {len(response.results)} results')
    finally:
        await client.close()

asyncio.run(test())
"
```

## License

MIT License
