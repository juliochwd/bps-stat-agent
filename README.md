<p align="center">
  <a href="https://github.com/juliochwd/bps-stat-agent">
    <img src="https://raw.githubusercontent.com/juliochwd/bps-stat-agent/main/docs/assets/logo.png" alt="BPS Stat Agent" width="180">
  </a>
</p>

<h1 align="center">BPS Stat Agent</h1>

<p align="center">
  <strong>BPS Indonesia Statistical Data Agent</strong><br>
  Agen AI untuk cari data BPS (Badan Pusat Statistik) — inflasi, PDB, IPM, angka harapan hidup, pengangguran, kemiskinan di Indonesia.<br>
  Dilengkapi <strong>62 MCP tools</strong> untuk akses lengkap ke BPS WebAPI dan AllStats Search Engine.
</p>

<p align="center">
  <a href="https://github.com/juliochwd/bps-stat-agent/releases/latest"><img src="https://img.shields.io/github/v/release/juliochwd/bps-stat-agent?color=blue&label=release" alt="Release"></a>
  <a href="https://github.com/juliochwd/bps-stat-agent/blob/main/LICENSE"><img src="https://img.shields.io/github/license/juliochwd/bps-stat-agent?color=green" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/tests-417%20passing-brightgreen" alt="Tests: 417 passing">
  <img src="https://img.shields.io/badge/MCP%20tools-62-orange" alt="MCP Tools: 62">
</p>

<p align="center">
  <a href="#installation"><strong>Installation</strong></a> ·
  <a href="#usage"><strong>Usage</strong></a> ·
  <a href="https://github.com/juliochwd/bps-stat-agent/releases"><strong>Releases</strong></a> ·
  <a href="#architecture"><strong>Architecture</strong></a>
</p>

---

> Query contoh: "inflasi NTT terbaru", "PDRB kabupaten kota Jawa Timur", "angka harapan hidup menurut provinsi", "IPM nasional 2024"

## Features

- 🔍 **BPS AllStats Search** - Search 1.6M+ statistical data points across all BPS domains
- 🔁 **AllStats-First Fallback Pipeline** - Search via AllStats, then retrieve structured detail through WebAPI
- 🌏 **Multi-domain Support** - Query national (0000) or provincial data (e.g., 5300=NTT)
- 📊 **Rich Content Types** - Publications, indicators, press releases, tables, infographics
- 🔄 **Auto-retry** - Automatic retry with fresh browser context on Cloudflare blocks
- 🔧 **MCP Server** - 62 tools running as real MCP server over STDIO
- 🤖 **ACP Server** - Agent Client Protocol bridge for agent-to-agent communication
- ⚡ **Fast Installation** - Single command install via uv/pip
- ✅ **Production Ready** - 417 tests across 34 test files, comprehensive coverage

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

### Quick Setup

After installation, run the setup wizard:

```bash
bpsagent setup
```

This will guide you through configuring your AI API key, BPS API key, and install Playwright.

## 🐳 Docker

### Quick Start
```bash
# Build the image
docker compose build

# Run CLI (interactive)
docker compose --profile cli run --rm agent

# Run MCP server
docker compose --profile mcp up -d

# Run ACP server
docker compose --profile acp up -d

# View logs
docker compose logs -f

# Stop all
docker compose down
```

### Environment Variables
Create a `.env` file (see `.env.example`):
```bash
cp .env.example .env
# Edit .env with your API keys
```

> 💡 **Tip:** If running locally before Docker, run `bpsagent setup` first to generate config files, then mount `~/.bps-stat-agent/config/` into the container. Alternatively, pass API keys via environment variables in `.env`.

## Configuration

### Automatic Setup (Recommended)

```bash
bpsagent setup
```

The setup wizard will:
- Prompt for your AI API key and BPS API key
- Write config files to `~/.bps-stat-agent/config/`
- Install Playwright chromium browser
- Configure MCP tools (62 BPS data tools)

### Manual Setup

#### 1. Run Setup Script

```bash
# macOS/Linux:
curl -fsSL https://raw.githubusercontent.com/juliochwd/bps-stat-agent/main/scripts/setup-config.sh | bash

# Windows (PowerShell):
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/juliochwd/bps-stat-agent/main/scripts/setup-config.ps1" -OutFile "$env:TEMP\setup-config.ps1"
powershell -ExecutionPolicy Bypass -File "$env:TEMP\setup-config.ps1"
```

#### 2. Add Your API Key

Edit `~/.bps-stat-agent/config/config.yaml` and add your LLM API key:

```yaml
api_key: "your_api_key_here"
```

### Security Note

> ⚠️ **`enable_bash` is `false` by default** for security. Bash tool access is disabled unless you explicitly enable it in `config.yaml`:
> ```yaml
> enable_bash: true  # Only enable if you trust the execution environment
> ```

### Configuration File Locations

Config files are loaded in priority order:
1. `./mini_agent/config/config.yaml` - Current directory (development)
2. `~/.bps-stat-agent/config/config.yaml` - User config directory
3. `<package>/mini_agent/config/config.yaml` - Package installation

## Usage

### CLI Mode

```bash
# Interactive mode
bpsagent

# Specific workspace
bpsagent --workspace /path/to/project

# Non-interactive
bpsagent --task "Cari data inflasi NTT 2024"

# Setup wizard
bpsagent setup

# Show log files
bpsagent log

# Show help
bpsagent --help
```

### MCP Server Mode

BPS Stat Agent includes an MCP server with 62 tools that can be used with Claude Desktop or any MCP client:

```json
{
    "mcpServers": {
        "bps": {
            "command": "uvx",
            "args": ["--from", "git+https://github.com/juliochwd/bps-stat-agent.git", "bps-mcp-server"],
            "env": {
                "BPS_API_KEY": "your_bps_webapi_key"
            }
        }
    }
}
```

Or run directly:
```bash
uvx --from git+https://github.com/juliochwd/bps-stat-agent.git bps-mcp-server
```

### ACP Server Mode

BPS Stat Agent also supports the Agent Client Protocol for agent-to-agent communication:

```bash
bps-stat-agent-acp
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
│   ├── __init__.py             # Package exports & version
│   ├── agent.py                # Core agent loop (token mgmt, tool execution)
│   ├── cli.py                  # CLI entry point (interactive + non-interactive)
│   ├── config.py               # Pydantic config loading (YAML + env vars)
│   ├── colors.py               # ANSI terminal color constants
│   ├── logger.py               # JSON-structured agent run logger
│   ├── retry.py                # Async retry with exponential backoff
│   │
│   ├── bps_api.py              # BPS WebAPI client (59 endpoints)
│   ├── bps_mcp_server.py       # FastMCP server with 62 registered tools
│   ├── bps_models.py           # BPSResourceType enum + BPSResolvedResource
│   ├── bps_orchestrator.py     # AllStats-first search → resolve → retrieve
│   ├── bps_resolution.py       # Classifies search results into resource types
│   ├── bps_data_retriever.py   # Table search → fetch → HTML parse pipeline
│   ├── bps_resource_retriever.py # Unified retrieval with fallback chains
│   ├── bps_normalization.py    # Canonical response payload builder
│   ├── allstats_client.py      # Playwright browser automation for AllStats
│   │
│   ├── llm/                    # LLM abstraction layer
│   │   ├── base.py             # Abstract LLMClientBase (ABC)
│   │   ├── llm_wrapper.py      # Unified LLMClient (provider routing)
│   │   ├── anthropic_client.py # Anthropic SDK (thinking, tool_use, caching)
│   │   └── openai_client.py    # OpenAI SDK (reasoning, tool_calls)
│   │
│   ├── schema/                 # Pydantic data models
│   │   └── schema.py           # Message, ToolCall, LLMResponse, TokenUsage
│   │
│   ├── tools/                  # Tool implementations
│   │   ├── base.py             # Tool ABC + ToolResult
│   │   ├── bash_tool.py        # BashTool (fg/bg), BashOutputTool, BashKillTool
│   │   ├── file_tools.py       # ReadTool, WriteTool, EditTool
│   │   ├── note_tool.py        # SessionNoteTool + RecallNoteTool
│   │   ├── skill_tool.py       # GetSkillTool (progressive disclosure)
│   │   ├── skill_loader.py     # SkillLoader (YAML frontmatter parser)
│   │   └── mcp_loader.py       # MCPTool + MCPServerConnection
│   │
│   ├── acp/                    # Agent Client Protocol bridge
│   │   ├── __init__.py         # BPSStatACPAgent
│   │   └── server.py           # ACP server entry point
│   │
│   ├── utils/                  # Utilities
│   │   └── terminal_utils.py   # Display width calculation (ANSI/emoji/CJK)
│   │
│   ├── config/                 # Configuration files
│   │   ├── config-example.yaml # Full annotated config template
│   │   ├── mcp-example.json    # MCP server config template
│   │   └── system_prompt.md    # System prompt (bilingual ID/EN)
│   │
│   └── skills/                 # Agent skills (git submodule)
│       └── bps-master/         # BPS domain skill with tool docs
│
├── tests/                      # 417 tests across 34 files
├── examples/                   # 6 usage examples
├── docs/                       # Development & production guides
├── scripts/                    # Setup scripts (macOS/Linux/Windows)
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

## 📊 Observability

### Logging
Configure structured JSON logging for production:
```yaml
# config.yaml
logging:
  level: "INFO"
  json_output: true   # JSON to stdout (production)
```

### Health Checks
Built-in HTTP health server for container orchestrators:
```python
from mini_agent.health import start_health_server
start_health_server(port=8080)
# GET /health → liveness check
# GET /ready  → readiness check
# GET /metrics → Prometheus metrics
```

### Metrics (Optional)
```bash
pip install bps-stat-agent[metrics]  # Install Prometheus client
```
Tracks: agent runs, LLM requests, token usage, tool call duration.

### Tracing (Optional)
```bash
pip install bps-stat-agent[tracing]  # Install OpenTelemetry
```
```yaml
# config.yaml
tracing:
  enabled: true
  exporter: "otlp"
  otlp_endpoint: "http://localhost:4317"
```

## Troubleshooting

### "Cloudflare blocked" errors

The client automatically retries with fresh browser context. If you see repeated blocks:
- Wait 10+ seconds between searches
- Check your network connection

### "API key not found"

Run the setup wizard to configure your API keys:
```bash
bpsagent setup
```

Or manually add your API key in `config.yaml`:
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

## 🛠️ Development

```bash
# Clone the repository
git clone https://github.com/juliochwd/bps-stat-agent.git
cd bps-stat-agent

# Install all dependencies + Playwright (recommended)
make install-dev

# Or manually with uv:
uv sync --frozen --group dev
uv run playwright install --with-deps chromium

# Run setup wizard to configure API keys
bpsagent setup

# Run tests
make test

# Run tests with coverage
make test-cov

# Lint + test quality gate
make check
```

### Makefile
```bash
make help          # Show all available targets
make install-dev   # Install deps + Playwright
make test          # Run tests (excluding live)
make test-cov      # Run tests with coverage
make lint          # Run ruff linter
make format        # Auto-format code
make check         # Lint + test (quality gate)
make build         # Build package
make clean         # Remove build artifacts
```

### CI/CD
The project includes GitHub Actions workflows:
- **CI** (`ci.yml`): Lint → Test → Security audit → Build (Python 3.11/3.12 matrix)
- **Docker** (`docker.yml`): Verifies Docker image builds on push to main

## Entry Points

| Command | Description |
|:--------|:------------|
| `bpsagent` | Interactive CLI agent for querying BPS data |
| `bpsagent setup` | Run interactive setup wizard |
| `bpsagent --task "query"` | Non-interactive mode with a single query |
| `bpsagent log` | Show log files |
| `bps-mcp-server` | MCP server over STDIO (62 tools) |
| `bps-stat-agent-acp` | ACP server for agent-to-agent communication |

## License

MIT License
