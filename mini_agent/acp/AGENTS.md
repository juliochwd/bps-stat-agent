<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# acp — Agent Client Protocol Bridge

## Purpose

Agent Client Protocol (ACP) server bridge that exposes the BPS Stat Agent as an ACP-compatible stdio server. Allows external ACP clients (e.g., Claude Desktop, other agent orchestrators) to create sessions, send prompts, and receive streaming updates for tool calls, thinking blocks, and agent messages.

Entry point: `bps-stat-agent-acp` CLI command.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | **Full ACP implementation.** `BPSStatACPAgent` class implementing ACP lifecycle: `initialize()` -> `newSession()` -> `prompt()` -> `cancel()`. `run_acp_server()` async function bootstraps the server. `SessionState` dataclass tracks per-session `Agent` instance and cancellation flag. Patches `InitializeRequest.protocolVersion` to handle string-to-int conversion. Alias: `MiniMaxACPAgent = BPSStatACPAgent`. Exports: `BPSStatACPAgent`, `MiniMaxACPAgent`, `run_acp_server`, `main`. |
| `server.py` | Entry point script. Calls `main()` from `__init__.py` which runs `asyncio.run(run_acp_server())`. |

## For AI Agents

### Working In This Directory

- `BPSStatACPAgent` wraps the existing `Agent` class with ACP protocol handlers
- Each session gets its own `Agent` instance with workspace-scoped tools (via `add_workspace_tools()`)
- Streaming updates sent via `session_notification()`:
  - `update_agent_thought()` — extended thinking blocks
  - `update_agent_message()` — text responses
  - `start_tool_call()` / `update_tool_call()` — tool execution with status (completed/failed)
- Tool results are prefixed with `[OK]` or `[ERROR]` for ACP client display
- Tool call labels include function name and key argument preview: `"🔧 name(key=value)"`
- Stop reasons: `end_turn` (normal), `cancelled`, `refusal` (error), `max_turn_requests` (step limit)
- Server initialization: loads config, configures logging/tracing, initializes base tools, creates LLM client
- Uses `stdio_streams()` from ACP SDK for stdin/stdout communication

### Architecture
```
ACP Client (stdio)
  |
BPSStatACPAgent
  |-- initialize() -> agent info (name="bps-stat-agent", version=__version__) + capabilities
  |-- newSession(cwd) -> create Agent with workspace tools, return session_id
  |-- prompt(sessionId, prompt) -> run agent turn, stream updates
  |   |-- update_agent_thought() -- thinking blocks
  |   |-- update_agent_message() -- text responses
  |   |-- start_tool_call() / update_tool_call() -- tool execution
  |   +-- Returns stop_reason: end_turn | cancelled | refusal | max_turn_requests
  +-- cancel(sessionId) -> set cancelled flag on session
```

### Testing Requirements

- Mock ACP `AgentSideConnection` and `stdio_streams` for unit tests
- Test session lifecycle: initialize -> newSession -> prompt -> cancel
- Test tool call streaming (start_tool_call, update_tool_call with status)
- Test error handling (unknown tool, tool execution failure, LLM error)
- Test `InitializeRequest` protocolVersion patch (string "1.0" -> int 1)
- Test multi-session isolation (each session has independent Agent)

### Common Patterns

- ACP server reuses `initialize_base_tools()` and `add_workspace_tools()` from `cli.py`
- Config loaded via `Config.load()` (same priority search as CLI)
- LLM client created with same retry config as CLI mode
- System prompt loaded and skill metadata injected identically to CLI mode
- `asyncio.Event().wait()` keeps the server running indefinitely

## Dependencies

### Internal
- `mini_agent.agent.Agent` — core agent loop
- `mini_agent.cli.initialize_base_tools`, `add_workspace_tools` — tool initialization
- `mini_agent.config.Config` — configuration loading
- `mini_agent.llm.LLMClient` — LLM client
- `mini_agent.schema.Message` — message model
- `mini_agent.retry.RetryConfig` — retry configuration
- `mini_agent.logging_config` — logging setup
- `mini_agent.tracing` — tracing setup

### External
- `acp` (agent-client-protocol >=0.6.0) — ACP protocol types, `AgentSideConnection`, `stdio_streams`, message builders
- `pydantic` — `field_validator` for protocol version patch
