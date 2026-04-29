# Development Guide

## Table of Contents

- [Development Guide](#development-guide)
  - [Table of Contents](#table-of-contents)
  - [1. Project Architecture](#1-project-architecture)
  - [2. Basic Usage](#2-basic-usage)
    - [2.1 Interactive Commands](#21-interactive-commands)
    - [2.2 Entry Points](#22-entry-points)
    - [2.3 BPS Data Pipeline](#23-bps-data-pipeline)
  - [3. Extended Abilities](#3-extended-abilities)
    - [3.1 Adding Custom Tools](#31-adding-custom-tools)
    - [3.2 Adding MCP Tools](#32-adding-mcp-tools)
    - [3.3 Customizing Note Storage](#33-customizing-note-storage)
    - [3.4 Initialize Claude Skills (Recommended)](#34-initialize-claude-skills-recommended)
    - [3.5 Adding a New Skill](#35-adding-a-new-skill)
    - [3.6 Customizing System Prompt](#36-customizing-system-prompt)
  - [4. Troubleshooting](#4-troubleshooting)
    - [4.1 Common Issues](#41-common-issues)
    - [4.2 Debugging Tips](#42-debugging-tips)

---

## 1. Project Architecture

```
bps-stat-agent/
├── mini_agent/                    # Core source code
│   ├── agent.py                   # Main agent loop (token mgmt, tool execution)
│   ├── cli.py                     # CLI entry point (interactive + non-interactive)
│   ├── config.py                  # Pydantic config loading (YAML + env vars)
│   ├── colors.py                  # ANSI terminal color constants
│   ├── logger.py                  # JSON-structured agent run logger
│   ├── retry.py                   # Async retry with exponential backoff
│   ├── setup_wizard.py            # Interactive setup wizard (bpsagent setup)
│   ├── health.py                  # HTTP health check server (/health, /ready, /metrics)
│   ├── metrics.py                 # Prometheus metrics (optional, graceful no-op)
│   ├── tracing.py                 # OpenTelemetry tracing (optional, graceful no-op)
│   ├── logging_config.py          # Centralized JSON structured logging
│   │
│   ├── bps_api.py                 # BPS WebAPI client (59 endpoints)
│   ├── bps_mcp_server.py          # FastMCP server (62 tools)
│   ├── bps_models.py              # BPSResourceType enum + BPSResolvedResource
│   ├── bps_orchestrator.py        # AllStats-first search → resolve → retrieve
│   ├── bps_resolution.py          # Classifies search results into resource types
│   ├── bps_data_retriever.py      # Table search → fetch → HTML parse pipeline
│   ├── bps_resource_retriever.py  # Unified retrieval with fallback chains
│   ├── bps_normalization.py       # Canonical response payload builder
│   ├── allstats_client.py         # Playwright browser automation for AllStats
│   │
│   ├── llm/                       # LLM abstraction layer
│   │   ├── base.py                # Abstract LLMClientBase (ABC)
│   │   ├── llm_wrapper.py         # Unified LLMClient (provider routing)
│   │   ├── anthropic_client.py    # Anthropic SDK (thinking, tool_use, caching)
│   │   └── openai_client.py       # OpenAI SDK (reasoning, tool_calls)
│   │
│   ├── schema/                    # Pydantic data models
│   │   └── schema.py              # Message, ToolCall, LLMResponse, TokenUsage
│   │
│   ├── tools/                     # Tool implementations
│   │   ├── base.py                # Tool ABC + ToolResult
│   │   ├── bash_tool.py           # BashTool (fg/bg), BashOutputTool, BashKillTool
│   │   ├── file_tools.py          # ReadTool, WriteTool, EditTool
│   │   ├── note_tool.py           # SessionNoteTool + RecallNoteTool
│   │   ├── skill_tool.py          # GetSkillTool (progressive disclosure)
│   │   ├── skill_loader.py        # SkillLoader (YAML frontmatter parser)
│   │   └── mcp_loader.py          # MCPTool + MCPServerConnection
│   │
│   ├── acp/                       # Agent Client Protocol bridge
│   │   ├── __init__.py            # BPSStatACPAgent
│   │   └── server.py              # ACP server entry point
│   │
│   ├── utils/                     # Utilities
│   │   └── terminal_utils.py      # Display width calculation (ANSI/emoji/CJK)
│   │
│   ├── config/                    # Configuration files
│   │   ├── config-example.yaml    # Full annotated config template
│   │   ├── mcp-example.json       # MCP server config template
│   │   └── system_prompt.md       # System prompt (bilingual ID/EN)
│   │
│   └── skills/                    # Agent skills (git submodule)
│       └── bps-master/            # BPS domain skill with tool docs
│
├── tests/                         # 417 tests across 34 files
├── examples/                      # 6 usage examples
├── docs/                          # Development & production guides
├── scripts/                       # Setup scripts (macOS/Linux/Windows)
├── pyproject.toml                 # Package definition
├── Dockerfile                     # Multi-stage Docker build
├── docker-compose.yml             # 3 services (CLI, MCP, ACP)
├── Makefile                       # 20 development targets
├── .github/workflows/ci.yml      # CI pipeline (lint, test, security, build)
├── ruff.toml                      # Linter configuration
├── .env.example                   # Environment variable template
└── README.md
```

## 2. Basic Usage

### 2.1 Interactive Commands

When running the agent in interactive mode (`bpsagent`), the following commands are available:

| Command                | Description                                                 |
| ---------------------- | ----------------------------------------------------------- |
| `/exit`, `/quit`, `/q` | Exit the agent and display session statistics               |
| `/help`                | Display help information and available commands             |
| `/clear`               | Clear message history and start a new session               |
| `/history`             | Show the current session message count                      |
| `/stats`               | Display session statistics (steps, tool calls, tokens used) |
| `/log [filename]`      | Show log files or read a specific log file                  |

### 2.2 Entry Points

| Command | Description |
|---------|-------------|
| `bpsagent setup` | Interactive setup wizard (run first after install) |
| `bpsagent` | Interactive CLI agent for querying BPS data |
| `bpsagent --task "query"` | Non-interactive mode with a single query |
| `bpsagent --workspace DIR` | Specify custom workspace directory |
| `bps-mcp-server` | MCP server over STDIO (62 tools) |
| `bps-stat-agent-acp` | ACP server for agent-to-agent communication |

### 2.3 BPS Data Pipeline

The agent uses an **AllStats-First Fallback Pipeline** for data retrieval:

```
Query → BPSOrchestrator.answer_query()
  ├── 1. AllStatsClient.search() [Playwright browser automation]
  │     └── Cloudflare bypass (anti-detection, fresh context retry)
  ├── 2. _select_best_result() [relevance scoring]
  ├── 3. classify_search_result() → BPSResolvedResource
  │     └── Maps to: TABLE, PUBLICATION, PRESSRELEASE, NEWS, INFOGRAPHIC, etc.
  ├── 4. BPSResourceRetriever.retrieve()
  │     ├── TABLE → get_static_table_detail() → HTML parse → structured data
  │     │     └── Fallback: keyword search → re-select → retry detail
  │     ├── PUBLICATION → get_publication_detail() → BPSMaterial (PDF/cover)
  │     ├── PRESSRELEASE → get_press_release_detail() → BPSMaterial
  │     └── OTHER → search_result_only (metadata only)
  └── 5. build_normalized_response() → canonical payload with provenance
```

## 3. Extended Abilities

### 3.1 Adding Custom Tools

#### Steps

1.  Create a new tool file under `mini_agent/tools/`.
2.  Inherit from the `Tool` base class.
3.  Implement the required properties and methods.
4.  Register the tool during Agent initialization.

#### Example

```python
# mini_agent/tools/my_tool.py
from mini_agent.tools.base import Tool, ToolResult
from typing import Dict, Any

class MyTool(Tool):
    @property
    def name(self) -> str:
        """A unique name for the tool."""
        return "my_tool"
    
    @property
    def description(self) -> str:
        """A description for the LLM to understand the tool's purpose."""
        return "My custom tool for doing something useful"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """Parameter schema in JSON Schema format."""
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "First parameter"
                },
                "param2": {
                    "type": "integer",
                    "description": "Second parameter",
                    "default": 10
                }
            },
            "required": ["param1"]
        }
    
    async def execute(self, param1: str, param2: int = 10) -> ToolResult:
        """
        The main logic of the tool.
        
        Args:
            param1: The first parameter.
            param2: The second parameter, with a default value.
        
        Returns:
            A ToolResult object.
        """
        try:
            # Implement your logic here
            result = f"Processed {param1} with param2={param2}"
            
            return ToolResult(
                success=True,
                content=result
            )
        except Exception as e:
            return ToolResult(
                success=False,
                content=f"Error: {str(e)}"
            )

# In cli.py or agent initialization code
from mini_agent.tools.my_tool import MyTool

# Add the new tool when creating the Agent
tools = [
    ReadTool(workspace_dir),
    WriteTool(workspace_dir),
    MyTool(),  # Add your custom tool
]

agent = Agent(
    llm=llm,
    tools=tools,
    max_steps=50
)
```

### 3.2 Adding MCP Tools

Edit `mcp.json` to add a new MCP Server:

```json
{
  "mcpServers": {
    "my_custom_mcp": {
      "description": "My custom MCP server",
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@my-org/my-mcp-server"],
      "env": {
        "API_KEY": "your-api-key"
      },
      "disabled": false,
      "notes": {
        "description": "This is a custom MCP server.",
        "api_key_url": "https://example.com/api-keys"
      }
    }
  }
}
```

### 3.3 Customizing Note Storage

To replace the storage backend for the `SessionNoteTool`:

```python
# Current implementation: JSON file
class SessionNoteTool:
    def __init__(self, memory_file: str = "./workspace/.agent_memory.json"):
        self.memory_file = Path(memory_file)
    
    async def _save_notes(self, notes: List[Dict]):
        with open(self.memory_file, 'w') as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)

# Example extension: PostgreSQL
class PostgresNoteTool(Tool):
    def __init__(self, db_url: str):
        self.db = PostgresDB(db_url)
    
    async def _save_notes(self, notes: List[Dict]):
        await self.db.execute(
            "INSERT INTO notes (content, category, timestamp) VALUES ($1, $2, $3)",
            notes
        )

# Example extension: Vector Database
class MilvusNoteTool(Tool):
    def __init__(self, milvus_host: str):
        self.vector_db = MilvusClient(host=milvus_host)
    
    async def _save_notes(self, notes: List[Dict]):
        # Generate embeddings
        embeddings = await self.get_embeddings([n["content"] for n in notes])
        
        # Store in the vector database
        await self.vector_db.insert(
            collection="agent_notes",
            data=notes,
            embeddings=embeddings
        )
```

### 3.4 Initialize Claude Skills (Recommended) 

This project integrates Claude's official skills repository via git submodule. Initialize it after first clone:

```bash
# Initialize submodule
git submodule update --init --recursive
```

Skills provide 20+ professional capabilities, making the Agent work like a professional:

- 📄 **Document Processing**: Create and edit PDF, DOCX, XLSX, PPTX
- 🎨 **Design Creation**: Generate artwork, posters, GIF animations
- 🧪 **Development & Testing**: Web automation testing (Playwright), MCP server development
- 🏢 **Enterprise Applications**: Internal communication, brand guidelines, theme customization

✨ **This is one of the core highlights of this project.** For details, see the "Configure Skills" section below.

**More information:**

- [Claude Skills Official Documentation](https://docs.claude.com/zh-CN/docs/agents-and-tools/agent-skills)
- [Anthropic Blog: Equipping agents for the real world](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### 3.5 Adding a New Skill

Create a custom Skill:

```bash
# Create a new skill directory under skills/
mkdir skills/my-custom-skill
cd skills/my-custom-skill

# Create the SKILL.md file
cat > SKILL.md << 'EOF'
---
name: my-custom-skill
description: My custom skill for handling specific tasks.
---

# Overview

This skill provides the following capabilities:
- Capability 1
- Capability 2

# Usage

1. Step one...
2. Step two...

# Best Practices

- Practice 1
- Practice 2

# FAQ

Q: Question 1
A: Answer 1
```

The new Skill will be automatically loaded and recognized by the Agent.

### 3.6 Customizing System Prompt

The system prompt (`system_prompt.md`) defines the Agent's behavior, capabilities, and working guidelines. You can customize it to tailor the Agent for specific use cases.

#### What You Can Customize

1. **Core Capabilities**: Add or modify tool descriptions
2. **Working Guidelines**: Define custom workflows and best practices
3. **Domain-Specific Knowledge**: Add expertise in specific areas
4. **Communication Style**: Adjust how the Agent interacts with users
5. **Task Priorities**: Set preferences for how tasks should be approached

After modifying `system_prompt.md`, be sure to restart the Agent to apply changes

## 4. Troubleshooting

### 4.1 Common Issues

#### API Key Configuration Error

```bash
# Error message
Error: Invalid API key

# Solution
1. Check that the API key in `config.yaml` is correct.
2. Ensure there are no extra spaces or quotes.
3. Verify that the API key has not expired.
```

#### Dependency Installation Failure

```bash
# Error message
uv sync failed

# Solution
1. Update uv to the latest version: `uv self update`
2. Clear the cache: `uv cache clean`
3. Try syncing again: `uv sync`
```

#### MCP Tool Loading Failure

```bash
# Error message
Failed to load MCP server

# Solution
1. Check the configuration in `mcp.json` is correct.
2. Ensure Node.js is installed (required for most MCP tools).
3. Verify that any required API keys are configured.
4. View detailed logs: `pytest tests/test_mcp.py -v -s`
```

### 4.2 Debugging Tips

#### Enable Verbose Logging

```python
# At the beginning of cli.py or a test file
from mini_agent.logging_config import configure_logging

configure_logging(level="DEBUG", json_output=False)
```

#### Using the Python Debugger

```python
# Set a breakpoint in your code
import pdb; pdb.set_trace()

# Or use ipdb for a better experience
import ipdb; ipdb.set_trace()
```

#### Inspecting Tool Calls

```python
# Add logging in the Agent to see tool interactions
logger.debug(f"Tool call: {tool_call.name}")
logger.debug(f"Tool arguments: {tool_call.arguments}")
logger.debug(f"Tool result: {result.content[:200]}")
```
