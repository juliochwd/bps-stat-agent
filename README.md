<p align="center">
  <a href="https://github.com/juliochwd/bps-stat-agent">
    <img src="https://raw.githubusercontent.com/juliochwd/bps-stat-agent/main/docs/assets/logo.png" alt="BPS Stat Agent" width="180">
  </a>
</p>

<h1 align="center">BPS Academic Research Agent</h1>

<p align="center">
  <strong>AI Agent untuk Riset Akademik & Data Statistik BPS Indonesia</strong><br>
  Dari pencarian data hingga paper siap submit — dilengkapi <strong>50+ native tools</strong>, <strong>13 MCP servers</strong>, dan pipeline riset 5 fase.<br>
  Mendukung <strong>22+ sumber akademik</strong> (arXiv, PubMed, Semantic Scholar, CrossRef, OpenAlex) + <strong>62 BPS tools</strong>.
</p>

<p align="center">
  <a href="https://github.com/juliochwd/bps-stat-agent/releases/latest"><img src="https://img.shields.io/github/v/release/juliochwd/bps-stat-agent?color=blue&label=release" alt="Release"></a>
  <a href="https://github.com/juliochwd/bps-stat-agent/blob/main/LICENSE"><img src="https://img.shields.io/github/license/juliochwd/bps-stat-agent?color=green" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/tests-471%20passing-brightgreen" alt="Tests: 471 passing">
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

### 🎓 Academic Research Pipeline
- 🎓 **Research Mode** - Phase-gated pipeline: PLAN → COLLECT → ANALYZE → WRITE → REVIEW
- 📊 **Statistical Analysis** - Descriptive stats, regression, hypothesis testing, time series, Bayesian, causal inference
- 📝 **Paper Writing** - LaTeX compilation, section writing, tables, diagrams, TikZ figures
- ✅ **Quality Assurance** - Grammar, style, readability, peer review simulation, plagiarism detection
- 📚 **Literature Search** - 22+ academic sources (arXiv, PubMed, Semantic Scholar, CrossRef, OpenAlex)
- 🧠 **Knowledge Management** - Document processing, embeddings, knowledge graphs, vector search
- 🐍 **Python Sandbox** - Isolated code execution (local/Docker/E2B)
- 🔌 **13 MCP Servers** - Papers, PDF, Jupyter, MarkItDown, ChromaDB, PubMed, R, Memory + BPS

### 📈 BPS Indonesia Data
- 🔍 **BPS AllStats Search** - Search 1.6M+ statistical data points across all BPS domains
- 🔁 **AllStats-First Fallback Pipeline** - Search via AllStats, then retrieve structured detail through WebAPI
- 🌏 **Multi-domain Support** - Query national (0000) or provincial data (e.g., 5300=NTT)
- 📊 **Rich Content Types** - Publications, indicators, press releases, tables, infographics
- 🔄 **Auto-retry** - Automatic retry with fresh browser context on Cloudflare blocks
- 🔧 **MCP Server** - 62 tools running as real MCP server over STDIO
- 🤖 **ACP Server** - Agent Client Protocol bridge for agent-to-agent communication

### ⚙️ Infrastructure
- ⚡ **Fast Installation** - Single command install via uv/pip
- ✅ **Production Ready** - 471 tests across 34 test files, comprehensive coverage
- 🐳 **Docker** - Multi-stage build with 3 service profiles (CLI/MCP/ACP)
- 📊 **Observability** - Prometheus metrics + OpenTelemetry tracing (optional)

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

### Option 3: Install with Research Extras

```bash
# Full research capabilities (numpy, scipy, statsmodels, sklearn, matplotlib, seaborn)
pip install 'bps-stat-agent[research-core]'

# All extras (research + metrics + tracing)
pip install 'bps-stat-agent[research-all]'

# Individual extras
pip install 'bps-stat-agent[metrics]'    # Prometheus monitoring
pip install 'bps-stat-agent[tracing]'    # OpenTelemetry tracing
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

# Research mode - start new project
bpsagent research --title "Analisis Hubungan IPM dan Kemiskinan di NTT 2019-2023"

# Resume existing research project
bpsagent research --resume ./workspace/project.yaml

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

## 🔌 MCP Server Ecosystem

The agent ships with **13 MCP servers** pre-configured (9 enabled by default):

| # | Server | Tools | Status | Description |
|---|--------|-------|--------|-------------|
| 1 | **bps** | 62 | ✅ Enabled | BPS Indonesia statistical data (AllStats + WebAPI) |
| 2 | **papers** | 22 sources | ✅ Enabled | Academic paper search (arXiv, PubMed, Semantic Scholar, CrossRef, OpenAlex, etc.) |
| 3 | **pdf** | 46 | ✅ Enabled | PDF processing (text, OCR, tables, annotations, merge/split) |
| 4 | **jupyter** | — | ✅ Enabled | Jupyter code execution (real-time, multimodal output) |
| 5 | **markitdown** | 29+ formats | ✅ Enabled | Microsoft universal file → Markdown converter |
| 6 | **memory** | — | ✅ Enabled | Knowledge graph memory (persistent research context) |
| 7 | **chroma** | — | ✅ Enabled | ChromaDB vector search (semantic + full-text) |
| 8 | **pubmed** | 40 | ✅ Enabled | PubMed biomedical search (PubMed, Europe PMC, CORE, OpenAlex) |
| 9 | **rmcp** | 52 | ✅ Enabled | R statistical computing (429 R packages) |
| 10 | **zotero** | — | 🔧 Disabled | Zotero citation manager (needs `ZOTERO_API_KEY`) |
| 11 | **overleaf** | 18 | 🔧 Disabled | Overleaf LaTeX editor (needs credentials) |
| 12 | **qdrant** | — | 🔧 Disabled | Qdrant vector search (needs running server) |
| 13 | **neo4j** | — | 🔧 Disabled | Neo4j knowledge graph (needs running server) |

> 💡 Disabled servers can be enabled by adding credentials in `~/.bps-stat-agent/config/mcp.json`


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
│   │   ├── litellm_client.py   # LiteLLM multi-provider gateway
│   │   ├── anthropic_client.py # Anthropic SDK (thinking, tool_use, caching)
│   │   └── openai_client.py    # OpenAI SDK (reasoning, tool_calls)
│   │
│   ├── research/               # Academic Research Pipeline (v1.0)
│   │   ├── orchestrator.py     # ResearchOrchestrator (phase-gated agent)
│   │   ├── phase_manager.py    # 5-phase workflow (PLAN→COLLECT→ANALYZE→WRITE→REVIEW)
│   │   ├── project_state.py    # YAML-persisted project state
│   │   ├── workspace.py        # IMRaD workspace scaffolder
│   │   ├── session_resume.py   # Checkpoint-based session recovery
│   │   ├── approval_gates.py   # Quality gate evaluator
│   │   ├── sub_agents.py       # 6 specialized sub-agents
│   │   ├── tool_registry.py    # Phase-aware tool registry (max 15/phase)
│   │   ├── llm_gateway.py      # LiteLLM cost tracking + fallback chains
│   │   ├── constants.py        # Research constants & config
│   │   ├── dspy_modules/       # DSPy signatures & modules
│   │   ├── models/             # CostTracker, DecisionLog
│   │   ├── quality/            # Citation verifier, peer reviewer, stat validator
│   │   └── writing/            # Bibliography, LaTeX compiler, section writer
│   │
│   ├── schema/                 # Pydantic data models
│   │   └── schema.py           # Message, ToolCall, LLMResponse, TokenUsage
│   │
│   ├── tools/                  # Tool implementations (50+ tools)
│   │   ├── base.py             # Tool ABC + ToolResult
│   │   ├── bash_tool.py        # BashTool (fg/bg), BashOutputTool, BashKillTool
│   │   ├── file_tools.py       # ReadTool, WriteTool, EditTool
│   │   ├── statistics_tools.py # Descriptive, regression, hypothesis, visualization
│   │   ├── analysis_tools.py   # TimeSeries, Bayesian, Causal, Survival, EDA
│   │   ├── citation_tools.py   # Literature search, citation manager, verify
│   │   ├── writing_tools.py    # Section writer, LaTeX compile, tables, diagrams
│   │   ├── quality_tools.py    # Grammar, style, readability, peer review
│   │   ├── sandbox_tools.py    # PythonREPL (local/Docker/E2B)
│   │   ├── document_tools.py   # Convert, parse PDF, extract references
│   │   ├── knowledge_tools.py  # Chunk, embed, vector search, knowledge graph
│   │   ├── research_tools.py   # Project init, status, switch phase
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
├── tests/                      # 471 tests across 34 files
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
| `bpsagent` | Interactive CLI agent (BPS data + research) |
| `bpsagent setup` | Run interactive setup wizard (API keys + 13 MCP servers) |
| `bpsagent --task "query"` | Non-interactive mode with a single query |
| `bpsagent research --title "..."` | Start a new academic research project |
| `bpsagent research --resume path` | Resume an existing research project |
| `bpsagent log` | Show log files |
| `bps-mcp-server` | MCP server over STDIO (62 BPS tools) |
| `bps-stat-agent-acp` | ACP server for agent-to-agent communication |

## License

MIT License
