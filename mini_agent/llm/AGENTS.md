<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-30 | Updated: 2026-04-30 -->
# llm — LLM Client Abstraction Layer

## Purpose

Unified LLM client abstraction supporting multiple providers (Anthropic, OpenAI, LiteLLM) through a single `LLMClient` interface. Handles provider-specific message formatting, tool schema conversion, extended thinking extraction, retry logic, and MiniMax API endpoint routing.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package exports: `LLMClientBase`, `AnthropicClient`, `OpenAIClient`, `LLMClient`. |
| `base.py` | **Abstract base class** `LLMClientBase`. Defines the contract: `generate(messages, tools) -> LLMResponse`, `_prepare_request()`, `_convert_messages()`. Accepts `RetryConfig` and `retry_callback` for retry instrumentation. |
| `llm_wrapper.py` | **Unified wrapper** `LLMClient`. Routes to the correct provider client based on `LLMProvider` enum. Auto-detects MiniMax API domains (`api.minimax.io`, `api.minimaxi.com`, `platform.minimax.io`) and appends `/anthropic` or `/v1` suffix. For third-party APIs, uses `api_base` as-is. Defaults: `api_base="https://api.minimaxi.com"`, `model="MiniMax-M2.5"`. |
| `anthropic_client.py` | **Anthropic SDK client** (`AnthropicClient`). Uses `anthropic.AsyncAnthropic` with custom `base_url` and Bearer auth header. Extracts `thinking` content blocks into `LLMResponse.thinking`. Converts tools via `to_schema()` (Anthropic format). Supports extended thinking and tool_use content blocks. |
| `openai_client.py` | **OpenAI SDK client** (`OpenAIClient`). Uses `openai.AsyncOpenAI`. Handles chat completions with function calling format. Converts tools via `to_openai_schema()`. Parses `tool_calls` from response choices. |
| `litellm_client.py` | **LiteLLM multi-provider client** (`LiteLLMClient`). Provides unified access to 100+ LLM providers. Features: automatic fallback chain (e.g., Claude -> GPT-4 -> Gemini), per-project cost tracking with budget enforcement (`budget_limit` default $50), configurable `fallback_models`. Requires `pip install bps-stat-agent[research-llm]`. |

## For AI Agents

### Working In This Directory

- **Adding a new provider**: Subclass `LLMClientBase` from `base.py`, implement `generate()`, `_prepare_request()`, `_convert_messages()`. Add routing in `llm_wrapper.py` under the new `LLMProvider` enum value.
- **`LLMClient`** in `llm_wrapper.py` is the only class used by `Agent` — it delegates to the appropriate provider client.
- All clients accept `RetryConfig` for exponential backoff on transient failures.
- `retry_callback` attribute allows the CLI to display retry status to the user (set via `LLMClient.retry_callback = on_retry`).
- Response format: `LLMResponse(content=str, thinking=str|None, tool_calls=list[ToolCall]|None, finish_reason=str, usage=TokenUsage|None)`.
- Tool schemas are converted per-provider: `tool.to_schema()` for Anthropic, `tool.to_openai_schema()` for OpenAI.
- Extended thinking (Anthropic) is extracted from `thinking` content blocks and returned in `LLMResponse.thinking`.
- MiniMax API routing: domains containing `minimax` get auto-suffixed (`/anthropic` or `/v1`). Other APIs pass through unchanged.

### Architecture
```
Agent.run()
  |
LLMClient (llm_wrapper.py)
  |-- provider == ANTHROPIC -> AnthropicClient (anthropic SDK)
  |-- provider == OPENAI    -> OpenAIClient (openai SDK)
  +-- provider == LITELLM   -> LiteLLMClient (litellm)
  |
generate(messages, tools) -> LLMResponse
```

### Testing Requirements

- Mock the underlying SDK clients (`anthropic.AsyncAnthropic`, `openai.AsyncOpenAI`) in unit tests
- Test MiniMax API base URL routing (suffix appending for minimax domains, passthrough for others)
- Test retry behavior: verify `RetryExhaustedError` after max retries, verify `on_retry` callback invocation
- Test tool schema conversion for both Anthropic and OpenAI formats
- Test extended thinking extraction from Anthropic responses
- Use `pytest-asyncio` for all `generate()` tests

### Common Patterns

- Messages converted from internal `Message` format to provider-specific format in `_convert_messages()`
- System message extracted separately (Anthropic uses `system` param, OpenAI uses system role message)
- Tool calls parsed from provider-specific response format into unified `ToolCall` model
- Token usage tracked via `TokenUsage` model when available from API response
- LiteLLM client reads API keys from environment variables (standard LiteLLM behavior)

## Dependencies

### Internal
- `mini_agent.schema` — `Message`, `ToolCall`, `FunctionCall`, `LLMResponse`, `TokenUsage`, `LLMProvider`
- `mini_agent.retry` — `RetryConfig`, `async_retry` decorator, `RetryExhaustedError`

### External
- `anthropic` (>=0.39.0) — Anthropic Messages API async client
- `openai` (>=1.57.4) — OpenAI Chat Completions async client
- `litellm` (optional, >=1.40) — multi-provider routing (requires `research-llm` extras)
