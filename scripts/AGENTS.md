<!-- Parent: ../AGENTS.md -->
# AGENTS.md — scripts/

> **Parent:** [../AGENTS.md](../AGENTS.md)
> **Updated:** 2026-05-01

## Purpose

Development and setup utility scripts for the BPS Stat Agent project. Contains cross-platform configuration setup scripts (Bash + PowerShell) and an internal test generation helper. These scripts are NOT part of the installed package — they are development/setup utilities only.

## Key Files

| File | Purpose |
|---|---|
| `setup-config.sh` | Unix/macOS configuration setup script. Creates `~/.bps-stat-agent/config/` directory, backs up existing config if present, copies template files (`config.yaml`, `mcp.json`, system prompts) from `mini_agent/config/`. Interactive prompts for API key configuration. Executable (`chmod +x`). |
| `setup-config.ps1` | Windows PowerShell equivalent of `setup-config.sh`. Same workflow: create config directory, backup existing, copy templates, prompt for API keys. Uses PowerShell-native file operations and colored output. |
| `_gen_tests.py` | Internal test scaffold generator. Creates test files in `tests/` directory for modules that lack coverage. Checks if files exist and are >200 bytes before overwriting. Generates test classes with imports and basic assertions. Prefixed with `_` to indicate internal/private use. |

## File Details

### setup-config.sh

- **Location:** `scripts/setup-config.sh`
- **Config directory:** `$HOME/.bps-stat-agent/config`
- **Steps:**
  1. Creates config directory (backs up existing with timestamp if present)
  2. Copies template files from `mini_agent/config/`
- **Output:** Colored terminal output with status indicators
- **Usage:** `bash scripts/setup-config.sh`
- **Note:** The `bpsagent setup` command (via `mini_agent/setup_wizard.py`) is the preferred setup method. This script is an alternative for manual setup.

### setup-config.ps1

- **Location:** `scripts/setup-config.ps1`
- **Config directory:** `$env:USERPROFILE\.bps-stat-agent\config`
- **Steps:** Same as `setup-config.sh` but using PowerShell cmdlets
- **Usage:** `powershell scripts/setup-config.ps1`

### _gen_tests.py

- **Location:** `scripts/_gen_tests.py`
- **Purpose:** Generates test file scaffolds for modules lacking test coverage
- **Behavior:** Only creates files that don't exist or are smaller than 200 bytes
- **Output:** Prints file names and sizes to stdout
- **Usage:** `python scripts/_gen_tests.py` (run from project root)
- **Note:** Internal development tool. Generated tests are starting points — they need manual refinement for meaningful assertions.

## For AI Agents

### Working In This Directory

1. **Preferred setup method:** Use `bpsagent setup` (the setup wizard) instead of these scripts for first-time configuration. The wizard is more interactive and handles Playwright installation.
2. **Scripts are NOT packaged:** These files are excluded from the installed package. They exist only in the source repository.
3. **Cross-platform:** Always maintain both `setup-config.sh` and `setup-config.ps1` in sync when modifying setup logic.
4. **Test generator:** `_gen_tests.py` is a one-shot helper. It generates scaffolds, not complete tests. Always review and enhance generated test files.
5. **Adding new scripts:** Include a shebang line (`#!/bin/bash` or equivalent), make executable, and add a header comment explaining purpose and usage.
6. **Config references:** Scripts reference template files in `mini_agent/config/`. If config file names or structure change, update both scripts.

### Running

```bash
# Unix/macOS config setup
bash scripts/setup-config.sh

# Windows config setup
powershell scripts/setup-config.ps1

# Generate test scaffolds (internal use)
python scripts/_gen_tests.py
```

## Dependencies

### Internal

- References `mini_agent/config/` template files (`config-example.yaml`, `mcp.json`, system prompts)
- `_gen_tests.py` references `mini_agent/` module structure for test generation

### External

- `setup-config.sh`: Bash, standard Unix utilities (cp, mkdir, date)
- `setup-config.ps1`: PowerShell 5.0+
- `_gen_tests.py`: Python stdlib only (os, sys)
