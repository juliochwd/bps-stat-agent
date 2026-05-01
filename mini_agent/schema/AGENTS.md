<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# schema — Pydantic Data Models

## Purpose

Shared Pydantic data models that form the contract between the agent loop, LLM clients, and tools. Defines the core types for messages, tool calls, LLM responses, provider enums, and token usage tracking used throughout the entire framework.

This is a **leaf module** with no internal dependencies — it can be imported by any other module safely.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Re-exports all models from `schema.py`: `FunctionCall`, `LLMProvider`, `LLMResponse`, `Message`, `TokenUsage`, `ToolCall`. |
| `schema.py` | All Pydantic v2 model definitions. `LLMProvider` enum (ANTHROPIC, OPENAI, LITELLM). `FunctionCall` (name + arguments dict). `ToolCall` (id + type + FunctionCall). `Message` (role + content + thinking + tool_calls + tool_call_id + name). `TokenUsage` (prompt/completion/total tokens). `LLMResponse` (content + thinking + tool_calls + finish_reason + usage). |

## For AI Agents

### Working In This Directory

- These models are the **shared contract** between agent, LLM clients, and tools — changes here affect the entire system
- `Message` supports multiple content types: plain `str` or `list[dict[str, Any]]` (for multimodal content blocks)
- `Message.thinking` holds extended thinking content from Anthropic models (None for OpenAI)
- `Message.tool_calls` is set on assistant messages that request tool execution
- `Message.tool_call_id` and `Message.name` are set on tool-role messages (responses to tool calls)
- `ToolCall` wraps `FunctionCall` with an `id` (for matching responses) and `type` field (always "function")
- `LLMResponse` is returned by all LLM clients — contains content, thinking, tool_calls, finish_reason, usage
- `LLMProvider` enum: `ANTHROPIC`, `OPENAI`, `LITELLM` — used for provider routing in `LLMClient`
- `TokenUsage` tracks prompt/completion/total tokens from API responses (used for billing and summarization triggers)

### Model Definitions
```python
class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    LITELLM = "litellm"

class FunctionCall(BaseModel):
    name: str
    arguments: dict[str, Any]

class ToolCall(BaseModel):
    id: str
    type: str  # "function"
    function: FunctionCall

class Message(BaseModel):
    role: str  # "system", "user", "assistant", "tool"
    content: str | list[dict[str, Any]]
    thinking: str | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None
    name: str | None = None  # For tool role

class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class LLMResponse(BaseModel):
    content: str
    thinking: str | None = None
    tool_calls: list[ToolCall] | None = None
    finish_reason: str
    usage: TokenUsage | None = None
```

### Testing Requirements

- Test Pydantic model validation (required fields, optional fields, type coercion)
- Test `Message` with both `str` and `list[dict]` content types
- Test `LLMProvider` enum string conversion
- Test serialization/deserialization round-trips
- Verify `ToolCall.function.arguments` accepts arbitrary dict values

### Common Patterns

- Import from `mini_agent.schema` (not `mini_agent.schema.schema`) for clean API
- `Message(role="tool", content=result, tool_call_id=call_id, name=tool_name)` for tool responses
- `LLMResponse.tool_calls` being `None` or empty signals task completion (no more tools to call)
- `LLMResponse.usage.total_tokens` used by `Agent._summarize_messages()` to trigger summarization

## Dependencies

### Internal
- None (leaf module — no internal dependencies)

### External
- `pydantic` (>=2.0) — BaseModel, validation, serialization
