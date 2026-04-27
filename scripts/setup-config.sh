#!/bin/bash
# BPS Stat Agent Configuration Setup Script
# This script helps you set up BPS Stat Agent configuration files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration directory - use bps-stat-agent specific directory
CONFIG_DIR="$HOME/.bps-stat-agent/config"

echo -e "${CYAN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   BPS Stat Agent Configuration Setup        ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Create config directory
echo -e "${BLUE}[1/2]${NC} Creating configuration directory..."
if [ -d "$CONFIG_DIR" ]; then
    # Auto backup existing config
    BACKUP_DIR="$HOME/.bps-stat-agent/config.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}   Configuration directory exists, backing up to:${NC}"
    echo -e "${YELLOW}   $BACKUP_DIR${NC}"
    cp -r "$CONFIG_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}   ✓ Backup created${NC}"
else
    mkdir -p "$CONFIG_DIR"
    echo -e "${GREEN}   ✓ Created: $CONFIG_DIR${NC}"
fi

# Step 2: Download configuration files from GitHub
echo -e "${BLUE}[2/2]${NC} Downloading configuration files..."

FILES_COPIED=0
# Update URL to bps-stat-agent repo
GITHUB_RAW_URL="https://raw.githubusercontent.com/juliochwd/bps-stat-agent/main/mini_agent/config"

# Download config-example.yaml as config.yaml
if curl -fsSL "$GITHUB_RAW_URL/config-example.yaml" -o "$CONFIG_DIR/config.yaml" 2>/dev/null; then
    echo -e "${GREEN}   ✓ Downloaded: config.yaml${NC}"
    FILES_COPIED=$((FILES_COPIED + 1))
else
    echo -e "${RED}   ✗ Failed to download: config.yaml${NC}"
fi

# Download mcp-example.json as mcp.json (includes BPS MCP server)
if curl -fsSL "$GITHUB_RAW_URL/mcp-example.json" -o "$CONFIG_DIR/mcp.json" 2>/dev/null; then
    echo -e "${GREEN}   ✓ Downloaded: mcp.json (with BPS MCP server)${NC}"
    FILES_COPIED=$((FILES_COPIED + 1))
else
    echo -e "${RED}   ✗ Failed to download: mcp.json${NC}"
fi

# Download system_prompt.md
if curl -fsSL "$GITHUB_RAW_URL/system_prompt.md" -o "$CONFIG_DIR/system_prompt.md" 2>/dev/null; then
    echo -e "${GREEN}   ✓ Downloaded: system_prompt.md${NC}"
    FILES_COPIED=$((FILES_COPIED + 1))
else
    echo -e "${RED}   ✗ Failed to download: system_prompt.md${NC}"
fi

if [ $FILES_COPIED -eq 0 ]; then
    echo -e "${RED}   ✗ Failed to download configuration files${NC}"
    echo -e "${YELLOW}   Please check your internet connection${NC}"
    exit 1
fi

echo -e "${GREEN}   ✓ Configuration files ready${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Setup Complete! ✨                          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Configuration files location:"
echo -e "  ${CYAN}$CONFIG_DIR${NC}"
echo ""
echo -e "Files:"
ls -1 "$CONFIG_DIR" 2>/dev/null | sed 's/^/  📄 /' || echo "  (no files yet)"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo -e "${YELLOW}1. Install BPS Stat Agent:${NC}"
echo -e "   ${GREEN}uv tool install git+https://github.com/juliochwd/bps-stat-agent.git${NC}"
echo ""
echo -e "${YELLOW}2. Run the setup wizard:${NC}"
echo -e "   ${GREEN}bpsagent setup${NC}"
echo ""
echo -e "${YELLOW}3. Start using BPS Stat Agent:${NC}"
echo -e "   ${GREEN}bpsagent${NC}                                    # Interactive mode"
echo -e "   ${GREEN}bpsagent --task \"Cari data inflasi NTT\"${NC}     # Non-interactive"
echo -e "   ${GREEN}bpsagent --help${NC}                             # Show help"
echo ""
