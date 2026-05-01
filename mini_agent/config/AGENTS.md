<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# config — Configuration Files

## Purpose

Configuration templates, MCP server definitions, and system prompts for the BPS Stat Agent. These files are the runtime configuration consumed by `mini_agent.config.Config` via a priority search mechanism: dev directory -> user home -> package install directory.

## Key Files

| File | Description |
|------|-------------|
| `config.yaml` | **Active configuration.** LLM settings (api_key, api_base, model, provider), retry config, agent settings (max_steps, workspace_dir, system_prompt_path), tools config (enable flags, MCP timeouts), logging, tracing. Contains secrets — gitignored in user config. |
| `config-example.yaml` | Template configuration with placeholder values (`YOUR_API_KEY_HERE`). Safe to commit. Used as reference for first-time setup. |
| `mcp.json` | **MCP server definitions.** Defines 13 MCP servers: `bps` (BPS data), `papers` (academic search), `pdf` (PDF processing), `jupyter` (code execution), `markitdown` (file conversion), `memory` (knowledge graph), `zotero` (citations, disabled), `overleaf` (LaTeX, disabled), `qdrant` (vector search, disabled), `neo4j` (graph DB, disabled), `chroma` (vector search), `pubmed` (biomedical), `rmcp` (R computing). Each entry: command, args, env vars, disabled flag. |
| `mcp-example.json` | Example MCP configuration template for reference. |
| `mcp-research.json` | MCP servers specific to research mode with additional academic tool servers. |
| `research_config.yaml` | Research-specific configuration: primary/fallback models, embedding model, max cost per project ($50), phase settings, sandbox backend (docker/e2b), quality gate thresholds. |
| `system_prompt.md` | **Main system prompt** for the BPS Stat Agent. Contains `{SKILLS_METADATA}` placeholder that is replaced at runtime with the skill catalog from `SkillLoader`. Defines agent persona, capabilities, BPS domain knowledge, and tool usage instructions. |
| `system_prompt_research.md` | System prompt for academic research mode. Includes phase-specific instructions, IMRaD structure guidance, citation requirements, and quality standards. |

## Subdirectories

| Directory | Description |
|-----------|-------------|
| `system_prompts/` | Specialized system prompts for research sub-agents and quality modules: `orchestrator.md`, `section_writer.md`, `peer_reviewer.md`, `citation_verifier.md`, `stat_validator.md`. |

## For AI Agents

### Working In This Directory

- **Config priority search order**: `./mini_agent/config/` (dev) -> `~/.bps-stat-agent/config/` (user) -> package install dir. Implemented in `Config.find_config_file()`.
- `config.yaml` is loaded by `Config.from_yaml()` in `mini_agent/config.py`. Pydantic validates all fields.
- **API key resolution**: env vars (`MINIMAX_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `OPENAI_API_KEY`) override placeholder values in config.yaml.
- System prompts support `{SKILLS_METADATA}` placeholder — replaced at runtime with skill catalog.
- MCP config (`mcp.json`) defines external tool servers: `command` (executable), `args`, `env` (environment variables), `disabled` flag.
- **DO NOT commit real API keys** in `config.yaml` or `mcp.json` — use `config-example.yaml` as template, or use env vars.
- Research config controls: primary/fallback models, cost limits, sandbox settings, quality gate thresholds.
- The setup wizard (`bpsagent setup`) writes config files to `~/.bps-stat-agent/config/`.

### Config File Format (config.yaml)
```yaml
api_key: "YOUR_API_KEY_HERE"    # Or use env: MINIMAX_API_KEY / ANTHROPIC_AUTH_TOKEN / OPENAI_API_KEY
api_base: "https://api.anthropic.com"
model: "claude-sonnet-4-20250514"
provider: "anthropic"           # "anthropic" | "openai"
max_steps: 50
workspace_dir: "./workspace"
system_prompt_path: "system_prompt.md"

retry:
  enabled: true
  max_retries: 3
  initial_delay: 1.0
  max_delay: 60.0
  exponential_base: 2.0

tools:
  enable_file_tools: true
  enable_bash: true
  enable_note: true
  enable_skills: true
  skills_dir: "./skills"
  enable_mcp: true
  mcp_config_path: "mcp.json"
  mcp:
    connect_timeout: 10.0
    execute_timeout: 60.0
    sse_read_timeout: 120.0

logging:
  level: "INFO"
  json_output: false

tracing:
  enabled: false
  exporter: "none"              # "none" | "console" | "otlp"
  otlp_endpoint: null
```

### MCP Server Entry Format (mcp.json)
```json
{
  "mcpServers": {
    "server_name": {
      "description": "Human-readable description",
      "command": "executable",
      "args": ["arg1", "arg2"],
      "env": { "KEY": "value" },
      "disabled": false
    }
  }
}
```

### Testing Requirements

- Test config loading with valid/invalid YAML
- Test API key resolution priority (env var > config file)
- Test priority search order (dev > user > package)
- Test that placeholder API keys are rejected (`Config.INVALID_API_KEYS`)
- Test MCP config parsing with disabled servers
- Never use real API keys in test fixtures

### Common Patterns

- Config files are static at runtime — modified only by setup wizard or manual editing
- System prompts are loaded once at agent startup and injected into the Agent constructor
- MCP servers with `"disabled": true` are skipped during tool loading

## Dependencies

### Internal
- Consumed by `mini_agent.config.Config` (Pydantic model)
- System prompts loaded by `mini_agent.cli.run_agent()`
- MCP config consumed by `mini_agent.tools.mcp_loader`
- Research config consumed by `mini_agent.research.orchestrator`

### External
- None (static configuration files)
