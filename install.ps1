# ============================================================================
# BPS Stat Agent — One-Click Installer (Windows PowerShell)
# Installs everything needed and configures the agent ready-to-use.
# Usage: irm https://raw.githubusercontent.com/juliochwd/bps-stat-agent/main/install.ps1 | iex
# ============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     🚀 BPS Stat Agent — One-Click Installer             ║" -ForegroundColor Cyan
Write-Host "║     Fully automated setup — zero configuration needed   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# Step 1: Check Prerequisites
# ============================================================================
Write-Host "[1/6] Checking prerequisites..." -ForegroundColor Blue

# Check Python
try {
    $pyVersion = python --version 2>&1
    if ($pyVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -ge 3 -and $minor -ge 10) {
            Write-Host "  ✓ $pyVersion found" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Python 3.10+ required (found $pyVersion)" -ForegroundColor Red
            Write-Host "  Install: https://www.python.org/downloads/" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "  ✗ Python not found" -ForegroundColor Red
    Write-Host "  Install Python 3.10+: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check/Install uv
try {
    $null = Get-Command uv -ErrorAction Stop
    Write-Host "  ✓ uv package manager found" -ForegroundColor Green
} catch {
    Write-Host "  → Installing uv package manager..." -ForegroundColor Yellow
    try {
        irm https://astral.sh/uv/install.ps1 | iex
        Write-Host "  ✓ uv installed" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Failed to install uv" -ForegroundColor Red
        exit 1
    }
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✓ Node.js $nodeVersion found" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Node.js not found (optional, needed for some MCP tools)" -ForegroundColor Yellow
}

# ============================================================================
# Step 2: Install BPS Stat Agent
# ============================================================================
Write-Host ""
Write-Host "[2/6] Installing BPS Stat Agent..." -ForegroundColor Blue

try {
    uv tool install "git+https://github.com/juliochwd/bps-stat-agent.git" --force 2>$null
    Write-Host "  ✓ BPS Stat Agent installed" -ForegroundColor Green
} catch {
    try {
        pip install "git+https://github.com/juliochwd/bps-stat-agent.git" --quiet 2>$null
        Write-Host "  ✓ BPS Stat Agent installed (via pip)" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Installation failed" -ForegroundColor Red
        exit 1
    }
}

# ============================================================================
# Step 3: Install Playwright
# ============================================================================
Write-Host ""
Write-Host "[3/6] Installing Playwright Chromium..." -ForegroundColor Blue

try {
    python -m playwright install chromium 2>$null
    Write-Host "  ✓ Playwright Chromium installed" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Playwright install had issues (non-fatal)" -ForegroundColor Yellow
}

# ============================================================================
# Step 4: Create Configuration
# ============================================================================
Write-Host ""
Write-Host "[4/6] Setting up configuration..." -ForegroundColor Blue

$configDir = Join-Path $env:USERPROFILE ".bps-stat-agent\config"
$logDir = Join-Path $env:USERPROFILE ".bps-stat-agent\log"
New-Item -ItemType Directory -Force -Path $configDir | Out-Null
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

# ============================================================================
# Step 5: Write Config Files
# ============================================================================
Write-Host ""
Write-Host "[5/6] Writing maximum-performance configuration..." -ForegroundColor Blue

# config.yaml
$configYaml = @"
# BPS Stat Agent Configuration — Maximum Performance
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
"@
Set-Content -Path (Join-Path $configDir "config.yaml") -Value $configYaml -Encoding UTF8
Write-Host "  ✓ config.yaml" -ForegroundColor Green

# mcp.json
$mcpJson = @"
{
    "mcpServers": {
        "bps": {
            "description": "BPS Indonesia Statistical Data Search",
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
            "description": "Academic Paper Search - 22 sources",
            "command": "npx",
            "args": ["-y", "@openags/paper-search-mcp"],
            "env": {},
            "disabled": false
        },
        "pdf": {
            "description": "PDF Processing - text extraction, OCR, tables",
            "command": "uvx",
            "args": ["mcp-pdf"],
            "env": {},
            "disabled": false
        },
        "markitdown": {
            "description": "MarkItDown - Convert any file to Markdown",
            "command": "uvx",
            "args": ["markitdown-mcp"],
            "env": {},
            "disabled": false
        },
        "memory": {
            "description": "Knowledge Graph Memory",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-memory"],
            "env": {},
            "disabled": false
        }
    }
}
"@
Set-Content -Path (Join-Path $configDir "mcp.json") -Value $mcpJson -Encoding UTF8
Write-Host "  ✓ mcp.json" -ForegroundColor Green

# Copy system prompt
try {
    $promptSrc = python -c "from mini_agent.config import Config; print(Config.get_package_dir() / 'config' / 'system_prompt.md')" 2>$null
    if ($promptSrc -and (Test-Path $promptSrc)) {
        Copy-Item $promptSrc (Join-Path $configDir "system_prompt.md")
        Write-Host "  ✓ system_prompt.md" -ForegroundColor Green
    }
} catch {}

# ============================================================================
# Step 6: Verify
# ============================================================================
Write-Host ""
Write-Host "[6/6] Verifying installation..." -ForegroundColor Blue

try {
    $version = bpsagent --version 2>&1
    Write-Host "  ✓ bpsagent available ($version)" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ bpsagent not in PATH (restart terminal)" -ForegroundColor Yellow
}

# ============================================================================
# Done!
# ============================================================================
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║     ✅ Installation Complete!                            ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Configuration: $configDir" -ForegroundColor White
Write-Host ""
Write-Host "Quick Start:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Run setup wizard:" -ForegroundColor White
Write-Host "     bpsagent setup" -ForegroundColor Cyan
Write-Host ""
Write-Host "  2. Start the agent:" -ForegroundColor White
Write-Host "     bpsagent" -ForegroundColor Cyan
Write-Host ""
