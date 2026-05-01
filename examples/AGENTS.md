<!-- Parent: ../AGENTS.md -->
# AGENTS.md — examples/

> **Parent:** [../AGENTS.md](../AGENTS.md)
> **Updated:** 2026-05-01

## Purpose

Progressive tutorial examples demonstrating how to use the BPS Stat Agent framework programmatically. Examples are numbered in learning order (01-06), progressing from basic tool usage to full agent configuration with multi-provider selection. Each example is self-contained and runnable.

## Key Files

| File | Difficulty | Purpose |
|---|---|---|
| `README.md` | — | Overview of all examples with descriptions, run instructions, prerequisites, and key learnings for each. |
| `01_basic_tools.py` | Beginner | Direct tool usage without Agent or LLM. Demonstrates `ReadTool`, `WriteTool`, `EditTool`, `BashTool` individually. Shows `ToolResult` return structure and error handling. No API key required. |
| `02_simple_agent.py` | Beginner-Intermediate | Minimal Agent setup with a single LLM provider. Creates an Agent, gives it file creation and bash command tasks. Demonstrates agent initialization, task assignment, and autonomous tool selection. Requires API key. |
| `03_session_notes.py` | Intermediate | Using `SessionNoteTool` and `RecallNoteTool` for persistent memory across agent turns. Shows how the agent stores and retrieves information between interactions. Requires API key. |
| `04_full_agent.py` | Intermediate-Advanced | Complete agent setup with all tools enabled: file tools, bash, MCP tools, skills, and note tools. Demonstrates full configuration including MCP server loading and skill progressive disclosure. Requires API key + MCP config. |
| `05_provider_selection.py` | Intermediate | Switching between LLM providers at runtime: Anthropic (Claude), OpenAI (GPT), MiniMax (via OpenAI-compatible API), LiteLLM (multi-provider). Shows provider-specific configuration and model selection. Requires at least one API key. |
| `06_tool_schema_demo.py` | Advanced | Inspecting tool schemas in both Anthropic and OpenAI formats. Shows how tools are serialized for different LLM providers, JSON Schema structure, and parameter validation. No API key required (schema inspection only). |

## Learning Path

```
01_basic_tools.py          Tools only, no Agent, no LLM
        |
02_simple_agent.py         Agent + LLM + basic tools
        |
03_session_notes.py        Agent + persistent memory
        |
04_full_agent.py           Agent + all tools + MCP + skills
        |
05_provider_selection.py   Multi-provider LLM configuration
        |
06_tool_schema_demo.py     Tool schema internals
```

## For AI Agents

### Working In This Directory

1. **Examples are numbered in learning order.** Start with `01_` for basics, progress through to `06_`.
2. **Running examples:**
   ```bash
   # No API key needed
   uv run python examples/01_basic_tools.py
   uv run python examples/06_tool_schema_demo.py

   # Requires API key in environment or config
   uv run python examples/02_simple_agent.py
   uv run python examples/03_session_notes.py
   uv run python examples/04_full_agent.py
   uv run python examples/05_provider_selection.py
   ```
3. **Each example is self-contained.** All imports, configuration, and execution are within the single file.
4. **Entry points:** Each file has a `main()` or `async def main()` function called via `if __name__ == "__main__"`.
5. **Output:** Examples print results to stdout for easy verification and learning.
6. **Adding new examples:** Follow the `0N_descriptive_name.py` naming convention. Include docstring header explaining purpose, difficulty, prerequisites, and key learnings. Update `README.md` with the new example description.
7. **These are reference implementations.** Modify them to demonstrate new features or patterns when the framework evolves.
8. **All examples import from `mini_agent`** — they depend on the package being installed (`pip install -e .` or `uv sync`).

### Key Patterns Demonstrated

| Pattern | Example |
|---|---|
| Direct tool execution | `01_basic_tools.py` |
| Agent initialization and task loop | `02_simple_agent.py` |
| Persistent memory across turns | `03_session_notes.py` |
| MCP server tool loading | `04_full_agent.py` |
| Skill progressive disclosure | `04_full_agent.py` |
| Provider switching (Anthropic/OpenAI/MiniMax/LiteLLM) | `05_provider_selection.py` |
| Tool schema serialization (Anthropic vs OpenAI format) | `06_tool_schema_demo.py` |
| ToolResult handling (success/error) | `01_basic_tools.py` |

## Dependencies

### Internal

- `mini_agent` — all examples import from the main package
- `mini_agent.tools` — tool classes (ReadTool, WriteTool, BashTool, etc.)
- `mini_agent.agent` — Agent class
- `mini_agent.llm` — LLMClient and provider classes
- `mini_agent.schema` — Message, ToolCall, LLMProvider

### External

- Same as main package core dependencies
- Provider-specific: `anthropic` (for Anthropic examples), `openai` (for OpenAI/MiniMax examples), `litellm` (for LiteLLM examples)
- No additional dependencies beyond the installed package
