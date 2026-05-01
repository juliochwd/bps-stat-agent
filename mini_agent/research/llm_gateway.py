"""LLM Gateway for multi-model routing with cost optimization.

Uses LiteLLM for unified access to multiple LLM providers.
Falls back gracefully if LiteLLM is not installed.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .exceptions import (
    BudgetExceededError,
    DependencyMissingError,
    GatewayError,
    ModelNotAvailableError,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency: litellm
# ---------------------------------------------------------------------------

try:
    import litellm

    litellm.set_verbose = False
    LITELLM_AVAILABLE = True
except ImportError:
    litellm = None  # type: ignore[assignment]
    LITELLM_AVAILABLE = False

# ---------------------------------------------------------------------------
# Model routing rules
# ---------------------------------------------------------------------------

ROUTING_RULES: dict[str, dict[str, str]] = {
    "paper_writing": {"primary": "claude-sonnet-4-20250514", "fallback": "gpt-4o"},
    "peer_review": {"primary": "claude-sonnet-4-20250514", "fallback": "gpt-4o"},
    "data_analysis": {"primary": "gpt-4o", "fallback": "claude-sonnet-4-20250514"},
    "literature_search": {"primary": "gpt-4o-mini", "fallback": "claude-3-5-haiku-20241022"},
    "summarization": {"primary": "gpt-4o-mini", "fallback": "claude-3-5-haiku-20241022"},
    "citation_verify": {"primary": "gpt-4o-mini", "fallback": "claude-3-5-haiku-20241022"},
    "embedding": {"primary": "nomic-embed-text", "fallback": "text-embedding-3-small"},
}

# ---------------------------------------------------------------------------
# Model costs per 1M tokens (USD)
# ---------------------------------------------------------------------------

MODEL_COSTS: dict[str, dict[str, float]] = {
    "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-3-5-haiku-20241022": {"input": 0.80, "output": 4.0},
    "nomic-embed-text": {"input": 0.10, "output": 0.0},
    "text-embedding-3-small": {"input": 0.02, "output": 0.0},
}


# ---------------------------------------------------------------------------
# Response dataclass
# ---------------------------------------------------------------------------


@dataclass
class GatewayResponse:
    """Response from the LLM Gateway.

    Attributes:
        content: The generated text content.
        model_used: Which model actually served the request.
        input_tokens: Number of input tokens consumed.
        output_tokens: Number of output tokens generated.
        cost_usd: Estimated cost in USD for this request.
    """

    content: str
    model_used: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


# ---------------------------------------------------------------------------
# Fallback chain
# ---------------------------------------------------------------------------


class FallbackChain:
    """Automatic provider failover for model requests.

    Maintains an ordered list of models to try for a given task type.
    If the primary model fails, the chain tries each fallback in order.
    """

    def __init__(self, models: list[str]) -> None:
        """Initialize the fallback chain.

        Args:
            models: Ordered list of model identifiers to try.
        """
        if not models:
            raise ValueError("FallbackChain requires at least one model")
        self.models = list(models)

    @classmethod
    def for_task(cls, task_type: str) -> FallbackChain:
        """Create a fallback chain from routing rules for a task type.

        Args:
            task_type: The task type key (e.g. ``"paper_writing"``).

        Returns:
            FallbackChain with primary and fallback models.
        """
        rule = ROUTING_RULES.get(task_type)
        if rule is None:
            # Default chain for unknown task types
            return cls(["gpt-4o-mini"])
        models = [rule["primary"]]
        if rule.get("fallback") and rule["fallback"] != rule["primary"]:
            models.append(rule["fallback"])
        return cls(models)

    def __iter__(self):
        return iter(self.models)

    def __repr__(self) -> str:
        return f"FallbackChain({self.models!r})"


# ---------------------------------------------------------------------------
# LLM Gateway
# ---------------------------------------------------------------------------


def _estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate the USD cost for a request.

    Args:
        model: Model identifier.
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.

    Returns:
        Estimated cost in USD.
    """
    costs = MODEL_COSTS.get(model, {"input": 0.0, "output": 0.0})
    input_cost = (input_tokens / 1_000_000) * costs["input"]
    output_cost = (output_tokens / 1_000_000) * costs["output"]
    return round(input_cost + output_cost, 8)


class LLMGateway:
    """Multi-model LLM gateway with cost tracking and automatic failover.

    Routes requests to the most appropriate model based on task type,
    tracks cumulative costs, and falls back to alternative providers
    when the primary is unavailable.

    Supports two usage patterns:

    1. Direct completion via :meth:`complete`:

        >>> gateway = LLMGateway({"budget_limit_usd": 5.0})
        >>> response = await gateway.complete(
        ...     prompt="Summarize this paper...",
        ...     task_type="summarization",
        ... )
        >>> print(response.content, response.cost_usd)

    2. Client-based routing via :meth:`get_client_for_task`:

        >>> client = gateway.get_client_for_task("paper_writing")
        >>> # Use client.generate() with full Message/Tool support
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the LLM Gateway.

        Args:
            config: Optional configuration dict. Supported keys:
                - ``budget_limit_usd`` (float): Maximum spend before raising
                  :class:`BudgetExceededError`. Default ``10.0``.
                - ``default_temperature`` (float): Default sampling temperature.
                  Default ``0.3``.
                - ``default_max_tokens`` (int): Default max output tokens.
                  Default ``4096``.
                - ``timeout`` (int): Request timeout in seconds. Default ``120``.
                - ``routing_overrides`` (dict): Override default routing rules.
        """
        config = config or {}
        self.budget_limit_usd: float = config.get("budget_limit_usd", 10.0)
        self.default_temperature: float = config.get("default_temperature", 0.3)
        self.default_max_tokens: int = config.get("default_max_tokens", 4096)
        self.timeout: int = config.get("timeout", 120)

        # Apply routing overrides if provided
        routing_overrides = config.get("routing_overrides", {})
        if routing_overrides:
            for task_type, rule in routing_overrides.items():
                ROUTING_RULES[task_type] = rule

        # Cumulative cost tracking
        self._total_cost_usd: float = 0.0
        self._request_count: int = 0
        self._request_log: list[dict[str, Any]] = []

        # Per-task-type cost tracking
        self._cost_by_task: dict[str, float] = {}

        # Client cache for get_client_for_task()
        self._client_cache: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Client-based routing API
    # ------------------------------------------------------------------

    def get_client_for_task(self, task_type: str):
        """Get an LLMClientBase instance configured for a specific task type.

        Returns a :class:`~mini_agent.llm.litellm_client.LiteLLMClient`
        pre-configured with the primary model and fallback chain for the
        given task type.

        Args:
            task_type: Task type key. Supported values:
                ``"paper_writing"``, ``"peer_review"``, ``"data_analysis"``,
                ``"literature_search"``, ``"summarization"``, ``"citation_verify"``

        Returns:
            LLMClientBase instance configured for the task.

        Raises:
            DependencyMissingError: If LiteLLM is not installed.
        """
        if task_type in self._client_cache:
            return self._client_cache[task_type]

        try:
            from ..llm.litellm_client import LiteLLMClient
        except ImportError:
            raise DependencyMissingError(
                "litellm",
                install_hint="pip install litellm",
            )

        rule = ROUTING_RULES.get(task_type, {"primary": "gpt-4o-mini"})
        primary = rule["primary"]
        fallback = rule.get("fallback")
        fallback_models = [fallback] if fallback and fallback != primary else []

        client = LiteLLMClient(
            model=primary,
            fallback_models=fallback_models,
            budget_limit=self.budget_limit_usd,
        )

        self._client_cache[task_type] = client
        return client

    # ------------------------------------------------------------------
    # Direct completion API
    # ------------------------------------------------------------------

    async def complete(
        self,
        prompt: str,
        task_type: str = "summarization",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> GatewayResponse:
        """Generate a completion using the best model for the task.

        Selects the model via routing rules, attempts the primary model
        first, then falls back to alternatives on failure.

        Args:
            prompt: The input prompt text.
            task_type: Task type for model routing (see ``ROUTING_RULES``).
            temperature: Sampling temperature override.
            max_tokens: Max output tokens override.

        Returns:
            GatewayResponse with content, model info, and cost.

        Raises:
            BudgetExceededError: If the cumulative cost would exceed the budget.
            GatewayError: If all models in the fallback chain fail.
        """
        temp = temperature if temperature is not None else self.default_temperature
        tokens = max_tokens if max_tokens is not None else self.default_max_tokens

        chain = FallbackChain.for_task(task_type)
        last_error: Exception | None = None

        for model in chain:
            try:
                response = await self._try_litellm(model, prompt, temp, tokens)
                self._record_request(response, task_type)
                return response
            except Exception as exc:
                last_error = exc
                logger.warning(
                    "Model %s failed for task %s: %s — trying fallback",
                    model,
                    task_type,
                    exc,
                )

        # All models failed — try the explicit fallback path
        try:
            response = await self._try_fallback(task_type, prompt, temp, tokens)
            self._record_request(response, task_type)
            return response
        except Exception as exc:
            raise GatewayError(
                f"All models failed for task '{task_type}'. Last error: {last_error or exc}",
            ) from exc

    async def embed(
        self,
        text: str,
        model: str | None = None,
    ) -> list[float]:
        """Generate an embedding vector for the given text.

        Args:
            text: Input text to embed.
            model: Embedding model override. Defaults to the routing
                rule for ``"embedding"`` task type.

        Returns:
            List of floats representing the embedding vector.

        Raises:
            DependencyMissingError: If LiteLLM is not installed.
            GatewayError: If the embedding request fails.
        """
        if not LITELLM_AVAILABLE:
            raise DependencyMissingError(
                "litellm",
                install_hint="pip install litellm",
            )

        target_model = model or self.get_model_for_task("embedding")

        try:
            response = await litellm.aembedding(  # type: ignore[union-attr]
                model=target_model,
                input=[text],
                timeout=self.timeout,
            )
            embedding = response.data[0]["embedding"]

            # Track cost
            usage = getattr(response, "usage", None)
            input_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
            cost = _estimate_cost(target_model, input_tokens, 0)
            self._total_cost_usd += cost
            self._request_count += 1

            return embedding
        except Exception as exc:
            raise GatewayError(
                f"Embedding failed with model '{target_model}': {exc}",
            ) from exc

    def get_model_for_task(self, task_type: str) -> str:
        """Look up the primary model for a given task type.

        Args:
            task_type: Task type key from ``ROUTING_RULES``.

        Returns:
            Model identifier string.
        """
        rule = ROUTING_RULES.get(task_type)
        if rule is None:
            return "gpt-4o-mini"
        return rule["primary"]

    # ------------------------------------------------------------------
    # Cost tracking
    # ------------------------------------------------------------------

    @property
    def total_cost_usd(self) -> float:
        """Cumulative cost across all requests in this gateway instance."""
        return round(self._total_cost_usd, 6)

    @property
    def request_count(self) -> int:
        """Total number of completed requests."""
        return self._request_count

    def get_cost_summary(self) -> dict[str, Any]:
        """Return a comprehensive summary of cost tracking state.

        Returns:
            Dict with ``total_cost_usd``, ``request_count``,
            ``budget_limit_usd``, ``budget_remaining_usd``,
            ``cost_by_task``, and ``recent_requests``.
        """
        return {
            "total_cost_usd": self.total_cost_usd,
            "request_count": self._request_count,
            "budget_limit_usd": self.budget_limit_usd,
            "budget_remaining_usd": round(self.budget_limit_usd - self._total_cost_usd, 6),
            "cost_by_task": dict(self._cost_by_task),
            "recent_requests": self._request_log[-20:],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _try_litellm(
        self,
        model: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> GatewayResponse:
        """Attempt a completion via LiteLLM.

        Args:
            model: Model identifier.
            prompt: Input prompt.
            temperature: Sampling temperature.
            max_tokens: Maximum output tokens.

        Returns:
            GatewayResponse on success.

        Raises:
            DependencyMissingError: If LiteLLM is not installed.
            ModelNotAvailableError: If the model request fails.
        """
        if not LITELLM_AVAILABLE:
            raise DependencyMissingError(
                "litellm",
                install_hint="pip install litellm",
            )

        # Budget guard
        self._check_budget()

        try:
            response = await litellm.acompletion(  # type: ignore[union-attr]
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout,
            )

            content = response.choices[0].message.content or ""
            usage = response.usage
            input_tokens = getattr(usage, "prompt_tokens", 0) if usage else 0
            output_tokens = getattr(usage, "completion_tokens", 0) if usage else 0
            cost = _estimate_cost(model, input_tokens, output_tokens)

            return GatewayResponse(
                content=content,
                model_used=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
            )
        except Exception as exc:
            if hasattr(exc, "__module__") and "litellm" in getattr(exc, "__module__", ""):
                raise ModelNotAvailableError(
                    f"Model '{model}' unavailable: {exc}",
                ) from exc
            raise

    async def _try_fallback(
        self,
        task_type: str,
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> GatewayResponse:
        """Attempt completion using the fallback model for a task type.

        This is a last-resort path when the primary chain has been
        exhausted. It looks up the fallback model from routing rules
        and makes one final attempt.

        Args:
            task_type: Task type key.
            prompt: Input prompt.
            temperature: Sampling temperature.
            max_tokens: Maximum output tokens.

        Returns:
            GatewayResponse on success.

        Raises:
            GatewayError: If the fallback also fails.
        """
        rule = ROUTING_RULES.get(task_type, {})
        fallback_model = rule.get("fallback", "gpt-4o-mini")

        logger.info("Attempting final fallback with model %s", fallback_model)
        return await self._try_litellm(fallback_model, prompt, temperature, max_tokens)

    def _check_budget(self) -> None:
        """Raise if cumulative cost has exceeded the budget limit.

        Raises:
            BudgetExceededError: If budget is exceeded.
        """
        if self._total_cost_usd >= self.budget_limit_usd:
            raise BudgetExceededError(
                f"Budget exhausted: ${self._total_cost_usd:.4f} / ${self.budget_limit_usd:.2f}",
            )

    def _record_request(self, response: GatewayResponse, task_type: str = "unknown") -> None:
        """Record a successful request for cost tracking.

        Args:
            response: The completed gateway response.
            task_type: The task type that triggered this request.
        """
        self._total_cost_usd += response.cost_usd
        self._request_count += 1

        # Track per-task costs
        self._cost_by_task[task_type] = self._cost_by_task.get(task_type, 0.0) + response.cost_usd

        self._request_log.append(
            {
                "model": response.model_used,
                "task_type": task_type,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd,
            }
        )
