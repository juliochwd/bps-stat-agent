"""LiteLLM-based LLM client for multi-provider routing.

Provides unified access to 100+ LLM providers through LiteLLM,
with automatic fallback, cost tracking, and budget enforcement.

Requires: pip install bps-stat-agent[research-llm]
"""

from __future__ import annotations

import logging
from typing import Any

from ..retry import RetryConfig
from ..schema import FunctionCall, LLMResponse, Message, TokenUsage, ToolCall
from .base import LLMClientBase

logger = logging.getLogger(__name__)


class LiteLLMClient(LLMClientBase):
    """LLM client using LiteLLM for unified multi-provider access.

    Features:
    - Supports 100+ LLM providers through a single interface
    - Automatic fallback chain (e.g., Claude → GPT-4 → Gemini)
    - Per-project cost tracking with budget enforcement
    - Same generate() interface as Anthropic/OpenAI clients
    - Configurable temperature and max_tokens per call
    """

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: str | None = None,
        api_base: str = "",
        retry_config: RetryConfig | None = None,
        fallback_models: list[str] | None = None,
        budget_limit: float = 50.0,
        **kwargs: Any,
    ) -> None:
        """Initialize LiteLLM client.

        Args:
            model: Primary model name (default: claude-sonnet-4-20250514)
            api_key: API key (used as default; LiteLLM also reads env vars)
            api_base: Base URL (optional, LiteLLM auto-detects)
            retry_config: Retry configuration
            fallback_models: Ordered fallback model list
            budget_limit: Maximum spend in USD (raises error at limit)
            **kwargs: Additional configuration passed to litellm
        """
        super().__init__(
            api_key=api_key or "",
            api_base=api_base,
            model=model,
            retry_config=retry_config,
        )
        self.fallback_models = fallback_models or []
        self.budget_limit = budget_limit
        self._extra_kwargs = kwargs

        # Cost tracking
        self.total_cost: float = 0.0
        self.call_count: int = 0
        self.call_costs: list[dict[str, Any]] = []

        # Lazy import check
        self._litellm = None

    def _ensure_litellm(self):
        """Lazy import litellm to avoid import errors when not installed."""
        if self._litellm is None:
            try:
                import litellm

                self._litellm = litellm
                # Suppress litellm's verbose logging
                litellm.suppress_debug_info = True
            except ImportError:
                raise ImportError("LiteLLM is not installed. Install with: pip install litellm")
        return self._litellm

    async def generate(
        self,
        messages: list[Message],
        tools: list[Any] | None = None,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Generate response using LiteLLM with fallback chain.

        Args:
            messages: List of conversation messages
            tools: Optional list of Tool objects or dicts
            temperature: Sampling temperature (default: 0.3)
            max_tokens: Maximum output tokens (default: 4096)

        Returns:
            LLMResponse with content, tool calls, and usage
        """
        litellm = self._ensure_litellm()

        # Budget check
        if self.total_cost >= self.budget_limit:
            raise RuntimeError(
                f"Budget limit reached: ${self.total_cost:.2f} >= ${self.budget_limit:.2f}. "
                f"Increase budget_limit or start a new project."
            )

        # Prepare request
        request = self._prepare_request(messages, tools)
        request["temperature"] = temperature
        request["max_tokens"] = max_tokens

        # Try primary model, then fallbacks
        models_to_try = [self.model] + self.fallback_models
        last_error = None

        for model in models_to_try:
            try:
                request["model"] = model
                response = await litellm.acompletion(**request)

                # Track cost via litellm.completion_cost()
                cost = 0.0
                try:
                    cost = litellm.completion_cost(completion_response=response)
                except Exception:
                    cost = 0.0

                self.total_cost += cost
                self.call_count += 1
                self.call_costs.append(
                    {
                        "model": model,
                        "cost": cost,
                        "total": self.total_cost,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    }
                )

                if cost > 0:
                    logger.debug(
                        "LiteLLM call: model=%s, cost=$%.4f, total=$%.2f",
                        model,
                        cost,
                        self.total_cost,
                    )

                return self._parse_response(response)

            except Exception as e:
                last_error = e
                logger.warning(
                    "LiteLLM model %s failed: %s. Trying next fallback...",
                    model,
                    str(e)[:200],
                )
                continue

        # All models failed
        raise RuntimeError(f"All LiteLLM models failed. Last error: {last_error}")

    def _prepare_request(
        self,
        messages: list[Message],
        tools: list[Any] | None = None,
    ) -> dict[str, Any]:
        """Prepare LiteLLM request payload.

        Args:
            messages: List of conversation messages
            tools: Optional list of Tool objects or dicts

        Returns:
            Request dictionary for litellm.acompletion()
        """
        system_msg, api_messages = self._convert_messages(messages)

        request: dict[str, Any] = {
            "model": self.model,
            "messages": api_messages,
        }

        # Only include api_key if provided
        if self.api_key:
            request["api_key"] = self.api_key

        if self.api_base:
            request["api_base"] = self.api_base

        if system_msg:
            request["messages"] = [{"role": "system", "content": system_msg}] + api_messages

        # Convert tools to OpenAI format (LiteLLM uses OpenAI tool format)
        if tools:
            tool_schemas = []
            for tool in tools:
                if isinstance(tool, dict):
                    tool_schemas.append(tool)
                elif hasattr(tool, "to_openai_schema"):
                    tool_schemas.append(tool.to_openai_schema())
                elif hasattr(tool, "to_schema"):
                    # Convert Anthropic schema to OpenAI format
                    schema = tool.to_schema()
                    tool_schemas.append(
                        {
                            "type": "function",
                            "function": {
                                "name": schema["name"],
                                "description": schema.get("description", ""),
                                "parameters": schema.get("input_schema", {}),
                            },
                        }
                    )
            if tool_schemas:
                request["tools"] = tool_schemas

        return request

    def _convert_messages(self, messages: list[Message]) -> tuple[str | None, list[dict[str, Any]]]:
        """Convert internal Message format to LiteLLM/OpenAI format.

        Args:
            messages: List of internal Message objects

        Returns:
            Tuple of (system_message, api_messages)
        """
        system_msg = None
        api_messages = []

        for msg in messages:
            if msg.role == "system":
                # Extract system message
                if isinstance(msg.content, str):
                    system_msg = msg.content
                elif isinstance(msg.content, list):
                    system_msg = " ".join(
                        block.get("text", "")
                        for block in msg.content
                        if isinstance(block, dict) and block.get("type") == "text"
                    )
                continue

            api_msg: dict[str, Any] = {"role": msg.role}

            # Handle content
            if isinstance(msg.content, str):
                api_msg["content"] = msg.content
            elif isinstance(msg.content, list):
                # Convert content blocks to text
                text_parts = []
                for block in msg.content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                        elif block.get("type") == "tool_result":
                            text_parts.append(str(block.get("content", "")))
                api_msg["content"] = "\n".join(text_parts) if text_parts else ""
            else:
                api_msg["content"] = str(msg.content) if msg.content else ""

            # Handle tool calls (assistant messages)
            if msg.tool_calls:
                api_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": _safe_json_dumps(tc.function.arguments),
                        },
                    }
                    for tc in msg.tool_calls
                ]

            # Handle tool responses
            if msg.role == "tool" and msg.tool_call_id:
                api_msg["tool_call_id"] = msg.tool_call_id

            api_messages.append(api_msg)

        return system_msg, api_messages

    def _parse_response(self, response: Any) -> LLMResponse:
        """Parse LiteLLM response into LLMResponse.

        Args:
            response: LiteLLM completion response

        Returns:
            Parsed LLMResponse
        """
        choice = response.choices[0]
        message = choice.message

        # Extract content
        content = message.content or ""

        # Extract tool calls
        tool_calls = None
        if message.tool_calls:
            tool_calls = []
            for tc in message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        type="function",
                        function=FunctionCall(
                            name=tc.function.name,
                            arguments=_safe_json_loads(tc.function.arguments),
                        ),
                    )
                )

        # Extract usage
        usage = None
        if response.usage:
            usage = TokenUsage(
                prompt_tokens=response.usage.prompt_tokens or 0,
                completion_tokens=response.usage.completion_tokens or 0,
                total_tokens=response.usage.total_tokens or 0,
            )

        # Determine finish reason
        finish_reason = choice.finish_reason or "stop"
        if finish_reason == "tool_calls":
            finish_reason = "tool_use"

        return LLMResponse(
            content=content,
            thinking=None,
            tool_calls=tool_calls,
            finish_reason=finish_reason,
            usage=usage,
        )

    def get_cost_report(self) -> dict[str, Any]:
        """Get cost tracking report.

        Returns:
            Dict with total cost, call count, per-call costs, budget remaining
        """
        return {
            "total_cost_usd": round(self.total_cost, 4),
            "call_count": self.call_count,
            "budget_limit_usd": self.budget_limit,
            "budget_remaining_usd": round(self.budget_limit - self.total_cost, 4),
            "recent_calls": self.call_costs[-10:],  # Last 10 calls
        }


def _safe_json_dumps(obj: Any) -> str:
    """Safely serialize to JSON string."""
    import json

    if isinstance(obj, str):
        return obj
    try:
        return json.dumps(obj)
    except (TypeError, ValueError):
        return str(obj)


def _safe_json_loads(s: str | dict) -> dict:
    """Safely deserialize from JSON string."""
    import json

    if isinstance(s, dict):
        return s
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return {"raw": s}
