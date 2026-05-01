#!/bin/bash
# ============================================================================
# BPS Stat Agent — One-Click Installer
# Installs everything needed and configures the agent ready-to-use.
# Usage: curl -fsSL https://raw.githubusercontent.com/juliochwd/bps-stat-agent/main/install.sh | bash
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║     🚀 BPS Stat Agent — One-Click Installer             ║${NC}"
echo -e "${CYAN}${BOLD}║     Fully automated setup — zero configuration needed   ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# Step 1: Check & Install Prerequisites
# ============================================================================
echo -e "${BLUE}[1/6]${NC} Checking prerequisites..."

# Check Python 3.10+
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 10 ]; then
        echo -e "  ${GREEN}✓${NC} Python $PY_VERSION found"
    else
        echo -e "  ${RED}✗${NC} Python 3.10+ required (found $PY_VERSION)"
        echo -e "  ${YELLOW}Install Python 3.10+: https://www.python.org/downloads/${NC}"
        exit 1
    fi
else
    echo -e "  ${RED}✗${NC} Python 3 not found"
    echo -e "  ${YELLOW}Install Python 3.10+: https://www.python.org/downloads/${NC}"
    exit 1
fi

# Check/Install uv (fast Python package manager)
if command -v uv &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} uv package manager found"
else
    echo -e "  ${YELLOW}→${NC} Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh 2>/dev/null
    export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
    if command -v uv &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} uv installed successfully"
    else
        echo -e "  ${RED}✗${NC} Failed to install uv. Install manually: https://docs.astral.sh/uv/"
        exit 1
    fi
fi

# Check Node.js (needed for some MCP servers)
if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "  ${GREEN}✓${NC} Node.js $NODE_VERSION found"
else
    echo -e "  ${YELLOW}⚠${NC} Node.js not found (optional, needed for some MCP tools)"
    echo -e "  ${YELLOW}  Install: https://nodejs.org/${NC}"
fi

# ============================================================================
# Step 2: Install BPS Stat Agent
# ============================================================================
echo ""
echo -e "${BLUE}[2/6]${NC} Installing BPS Stat Agent..."

# Install as a tool (globally available)
uv tool install "git+https://github.com/juliochwd/bps-stat-agent.git" --force 2>/dev/null && \
    echo -e "  ${GREEN}✓${NC} BPS Stat Agent installed" || {
    # Fallback: install via pip
    echo -e "  ${YELLOW}→${NC} Trying pip install..."
    pip install "git+https://github.com/juliochwd/bps-stat-agent.git" --quiet 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} BPS Stat Agent installed (via pip)" || {
        echo -e "  ${RED}✗${NC} Installation failed"
        exit 1
    }
}

# ============================================================================
# Step 3: Install Playwright Chromium
# ============================================================================
echo ""
echo -e "${BLUE}[3/6]${NC} Installing Playwright Chromium browser..."

python3 -m playwright install chromium 2>/dev/null && \
    echo -e "  ${GREEN}✓${NC} Playwright Chromium installed" || {
    # Try with deps
    python3 -m playwright install --with-deps chromium 2>/dev/null && \
        echo -e "  ${GREEN}✓${NC} Playwright Chromium installed (with deps)" || \
        echo -e "  ${YELLOW}⚠${NC} Playwright install had issues (non-fatal, will retry on first use)"
}

# ============================================================================
# Step 4: Create Configuration Directory
# ============================================================================
echo ""
echo -e "${BLUE}[4/6]${NC} Setting up configuration..."

CONFIG_DIR="$HOME/.bps-stat-agent/config"
LOG_DIR="$HOME/.bps-stat-agent/log"
mkdir -p "$CONFIG_DIR" "$LOG_DIR"

# ============================================================================
# Step 5: Write Configuration Files (Maximum Performance)
# ============================================================================
echo ""
echo -e "${BLUE}[5/6]${NC} Writing maximum-performance configuration..."

# config.yaml — ALL features enabled, max steps, max retries
cat > "$CONFIG_DIR/config.yaml" << 'YAML'
# BPS Stat Agent Configuration — Maximum Performance
# Generated by: one-click installer

api_key: "YOUR_API_KEY_HERE"
api_base: "https://platform.minimax.io"
model: "MiniMax-M2.5"
provider: "openai"

retry:
  enabled: true
  max_retries: 5
  initial_delay: 1.0
  max_delay: 60.0
  exponential_base: 2.0

max_steps: 100
workspace_dir: "./workspace"
system_prompt_path: "system_prompt.md"

tools:
  enable_file_tools: true
  enable_bash: true
  enable_note: true
  enable_skills: true
  skills_dir: "./skills"
  enable_mcp: true
  mcp_config_path: "mcp.json"
  mcp:
    connect_timeout: 15.0
    execute_timeout: 120.0
    sse_read_timeout: 120.0

logging:
  level: "INFO"
  json_output: false

tracing:
  enabled: true
  exporter: "console"
YAML
echo -e "  ${GREEN}✓${NC} config.yaml (all features enabled)"

# mcp.json — All MCP servers enabled
cat > "$CONFIG_DIR/mcp.json" << 'JSON'
{
    "mcpServers": {
        "bps": {
            "description": "BPS Indonesia Statistical Data Search - AllStats Search Engine",
            "command": "bps-mcp-server",
            "args": [],
            "env": {
                "BPS_API_KEY": "",
                "BPS_DEFAULT_DOMAIN": "5300",
                "BPS_SEARCH_DELAY": "3"
            },
            "disabled": false
        },
        "papers": {
            "description": "Academic Paper Search - 22 sources (arXiv, PubMed, Semantic Scholar, CrossRef, OpenAlex, etc.)",
            "command": "npx",
            "args": ["-y", "@openags/paper-search-mcp"],
            "env": {},
            "disabled": false
        },
        "pdf": {
            "description": "PDF Processing - text extraction, OCR, tables, annotations, merge/split",
            "command": "uvx",
            "args": ["mcp-pdf"],
            "env": {},
            "disabled": false
        },
        "markitdown": {
            "description": "MarkItDown (Microsoft) - Convert any file to Markdown: PDF, DOCX, PPTX, XLSX, HTML, images",
            "command": "uvx",
            "args": ["markitdown-mcp"],
            "env": {},
            "disabled": false
        },
        "memory": {
            "description": "Knowledge Graph Memory - persistent memory system",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
            "env": {},
            "disabled": false
        }
    }
}
JSON
echo -e "  ${GREEN}✓${NC} mcp.json (BPS + Papers + PDF + MarkItDown + Memory)"

# Copy system prompt from package if available
SYSTEM_PROMPT_SRC=$(python3 -c "from mini_agent.config import Config; print(Config.get_package_dir() / 'config' / 'system_prompt.md')" 2>/dev/null || echo "")
if [ -n "$SYSTEM_PROMPT_SRC" ] && [ -f "$SYSTEM_PROMPT_SRC" ]; then
    cp "$SYSTEM_PROMPT_SRC" "$CONFIG_DIR/system_prompt.md"
    echo -e "  ${GREEN}✓${NC} system_prompt.md"
fi

# ============================================================================
# Step 6: Verify Installation
# ============================================================================
echo ""
echo -e "${BLUE}[6/6]${NC} Verifying installation..."

# Check bpsagent command
if command -v bpsagent &>/dev/null; then
    AGENT_VERSION=$(bpsagent --version 2>/dev/null || echo "installed")
    echo -e "  ${GREEN}✓${NC} bpsagent command available ($AGENT_VERSION)"
elif [ -f "$HOME/.local/bin/bpsagent" ]; then
    echo -e "  ${GREEN}✓${NC} bpsagent installed at ~/.local/bin/bpsagent"
    echo -e "  ${YELLOW}→${NC} Add to PATH: export PATH=\"\$HOME/.local/bin:\$PATH\""
else
    echo -e "  ${YELLOW}⚠${NC} bpsagent not in PATH yet (restart terminal or run: hash -r)"
fi

# Check bps-mcp-server
if command -v bps-mcp-server &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} bps-mcp-server command available"
fi

# ============================================================================
# Done!
# ============================================================================
echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║     ✅ Installation Complete!                            ║${NC}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}Configuration:${NC} $CONFIG_DIR"
echo -e "  ${BOLD}Log directory:${NC} $LOG_DIR"
echo ""
echo -e "${YELLOW}${BOLD}Quick Start:${NC}"
echo ""
echo -e "  ${GREEN}1.${NC} Run the setup wizard (enter your API keys):"
echo -e "     ${CYAN}bpsagent setup${NC}"
echo ""
echo -e "  ${GREEN}2.${NC} Start using the agent:"
echo -e "     ${CYAN}bpsagent${NC}                                    # Interactive mode"
echo -e "     ${CYAN}bpsagent --task \"Cari data inflasi NTT 2024\"${NC} # One-shot mode"
echo ""
echo -e "  ${GREEN}3.${NC} Or use as MCP server (for Claude Desktop, etc.):"
echo -e "     ${CYAN}bps-mcp-server${NC}"
echo ""
echo -e "${BOLD}Features Enabled:${NC}"
echo -e "  ✅ BPS Statistical Data (62+ tools via AllStats + WebAPI)"
echo -e "  ✅ Academic Paper Search (22 sources)"
echo -e "  ✅ PDF Processing (OCR, tables, annotations)"
echo -e "  ✅ Document Conversion (DOCX, PPTX, XLSX → Markdown)"
echo -e "  ✅ Knowledge Graph Memory"
echo -e "  ✅ File Operations (read/write/edit)"
echo -e "  ✅ Bash Command Execution"
echo -e "  ✅ Claude Skills System"
echo -e "  ✅ Session Notes & Memory"
echo -e "  ✅ Retry with Exponential Backoff (5 retries)"
echo -e "  ✅ 100 max execution steps"
echo ""
