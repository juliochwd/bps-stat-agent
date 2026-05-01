"""Per-project cost tracking for LLM API usage.

Tracks token consumption and estimated costs across all models used
during a research project.  Supports budget limits, per-phase and
per-model breakdowns, and persistent storage.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

# Per-1M-token pricing (USD) for common models
MODEL_COSTS: dict[str, dict[str, float]] = {
    # Anthropic
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-20250414": {"input": 0.80, "output": 4.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    # OpenAI
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    # Embeddings
    "text-embedding-3-small": {"input": 0.02, "output": 0.00},
    "text-embedding-3-large": {"input": 0.13, "output": 0.00},
}

# Default cost for unknown models (conservative estimate)
_DEFAULT_COST: dict[str, float] = {"input": 1.00, "output": 3.00}


class CostEntry(BaseModel):
    """A single LLM usage cost record.

    Attributes:
        timestamp: ISO 8601 timestamp of the usage event.
        model: Model identifier (e.g. ``"claude-sonnet-4-20250514"``).
        provider: Provider name (e.g. ``"anthropic"``, ``"openai"``).
        input_tokens: Number of prompt / input tokens consumed.
        output_tokens: Number of completion / output tokens consumed.
        cost_usd: Calculated cost in USD for this entry.
        task_type: Category of task (e.g. ``"planning"``, ``"writing"``).
    """

    timestamp: str = ""
    model: str = ""
    provider: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    task_type: str = "general"

    def model_post_init(self, __context: Any) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(UTC).isoformat()


class CostTracker:
    """Tracks LLM API costs for a research project.

    Maintains an in-memory list of ``CostEntry`` records and provides
    budget monitoring with configurable limits.

    Args:
        workspace_path: Path to the workspace directory.  The cost file
            is stored at ``<workspace>/logs/costs.json``.
    """

    DEFAULT_FILENAME: str = "logs/costs.json"
    BUDGET_LIMIT_USD: float = 50.0

    def __init__(self, workspace_path: Path) -> None:
        self.workspace_path = Path(workspace_path)
        self._cost_path = self.workspace_path / self.DEFAULT_FILENAME
        self._entries: list[CostEntry] = []

        # Load existing entries if the file exists
        if self._cost_path.exists():
            self._load()

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record(
        self,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
        task_type: str = "general",
    ) -> CostEntry:
        """Record a new LLM usage event.

        Calculates the cost automatically from the ``MODEL_COSTS``
        lookup table.

        Args:
            model: Model identifier.
            provider: Provider name (e.g. ``"anthropic"``).
            input_tokens: Number of input tokens consumed.
            output_tokens: Number of output tokens consumed.
            task_type: Category of task (e.g. ``"planning"``).

        Returns:
            The created ``CostEntry``.
        """
        cost_usd = self._calculate_cost(model, input_tokens, output_tokens)

        entry = CostEntry(
            model=model,
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
            task_type=task_type,
        )
        self._entries.append(entry)
        return entry

    # ------------------------------------------------------------------
    # Cost calculations
    # ------------------------------------------------------------------

    def get_total_cost(self) -> float:
        """Total estimated cost across all recorded usage.

        Returns:
            Cumulative cost in USD, rounded to 6 decimal places.
        """
        return round(sum(e.cost_usd for e in self._entries), 6)

    def get_cost_by_phase(self) -> dict[str, float]:
        """Breakdown of costs grouped by task type / phase.

        Returns:
            Dict mapping task type to total cost in USD.
        """
        breakdown: dict[str, float] = {}
        for entry in self._entries:
            key = entry.task_type
            breakdown[key] = round(breakdown.get(key, 0.0) + entry.cost_usd, 6)
        return breakdown

    def get_cost_by_model(self) -> dict[str, float]:
        """Breakdown of costs grouped by model.

        Returns:
            Dict mapping model name to total cost in USD.
        """
        breakdown: dict[str, float] = {}
        for entry in self._entries:
            breakdown[entry.model] = round(breakdown.get(entry.model, 0.0) + entry.cost_usd, 6)
        return breakdown

    def get_summary(self) -> str:
        """Generate a human-readable cost summary.

        Returns:
            Formatted summary string.
        """
        total = self.get_total_cost()
        remaining = round(self.BUDGET_LIMIT_USD - total, 6)

        lines = [
            f"Total cost: ${total:.4f} USD",
            f"Budget: ${self.BUDGET_LIMIT_USD:.2f} USD (${remaining:.4f} remaining)",
        ]

        if total >= self.BUDGET_LIMIT_USD:
            lines.append("⚠️  OVER BUDGET")
        elif remaining <= 10.0:
            lines.append("⚠️  Approaching budget limit")

        by_model = self.get_cost_by_model()
        if by_model:
            lines.append("Cost by model:")
            for model, cost in sorted(by_model.items()):
                lines.append(f"  - {model}: ${cost:.6f}")

        by_phase = self.get_cost_by_phase()
        if by_phase:
            lines.append("Cost by task type:")
            for task_type, cost in sorted(by_phase.items()):
                lines.append(f"  - {task_type}: ${cost:.6f}")

        total_input = sum(e.input_tokens for e in self._entries)
        total_output = sum(e.output_tokens for e in self._entries)
        lines.append(f"Total tokens: {total_input:,} input / {total_output:,} output")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Budget checks
    # ------------------------------------------------------------------

    @property
    def is_over_budget(self) -> bool:
        """Check whether total spend exceeds the budget limit."""
        return self.get_total_cost() >= self.BUDGET_LIMIT_USD

    @property
    def remaining_budget(self) -> float:
        """Remaining budget in USD."""
        return round(self.BUDGET_LIMIT_USD - self.get_total_cost(), 6)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Persist the cost tracker to a JSON file.

        The parent directory is created if it does not exist.
        """
        self._cost_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "budget_limit_usd": self.BUDGET_LIMIT_USD,
            "entries": [e.model_dump(mode="json") for e in self._entries],
        }

        with open(self._cost_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        """Reload the cost tracker from disk.

        Replaces the in-memory entries with those read from the file.
        """
        self._load()

    def _load(self) -> None:
        """Internal load implementation."""
        if not self._cost_path.exists():
            self._entries = []
            return

        with open(self._cost_path, encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            self.BUDGET_LIMIT_USD = data.get("budget_limit_usd", self.BUDGET_LIMIT_USD)
            raw_entries = data.get("entries", [])
        elif isinstance(data, list):
            raw_entries = data
        else:
            self._entries = []
            return

        self._entries = [CostEntry.model_validate(e) for e in raw_entries]

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def entries(self) -> list[CostEntry]:
        """Read-only access to the entries list."""
        return list(self._entries)

    @property
    def count(self) -> int:
        """Number of entries in the tracker."""
        return len(self._entries)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_cost(
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate cost for a single usage event.

        Args:
            model: Model identifier.
            input_tokens: Number of input tokens.
            output_tokens: Number of output tokens.

        Returns:
            Estimated cost in USD.
        """
        costs = MODEL_COSTS.get(model, _DEFAULT_COST)
        input_cost = (input_tokens / 1_000_000) * costs["input"]
        output_cost = (output_tokens / 1_000_000) * costs["output"]
        return round(input_cost + output_cost, 6)
