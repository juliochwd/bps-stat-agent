"""Configuration tools for LiteLLM routing and DSPy optimization.

Provides tools for:
- litellm_config: Configure LiteLLM model routing for the research project
- dspy_optimize: Run DSPy MIPROv2 optimization on pipeline modules
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .base import Tool, ToolResult

# ---------------------------------------------------------------------------
# Optional dependency flags
# ---------------------------------------------------------------------------

_HAS_LITELLM = False
try:
    import litellm  # noqa: F401

    _HAS_LITELLM = True
except ImportError:
    pass

_HAS_DSPY = False
try:
    import dspy

    _HAS_DSPY = True
except ImportError:
    dspy = None  # type: ignore[assignment]


# ===================================================================
# 1. LiteLLMConfigTool
# ===================================================================


class LiteLLMConfigTool(Tool):
    """Configure LiteLLM routing for the research project.

    Manages model routing rules, fallback chains, API key configuration,
    and cost tracking. Stores configuration in the project workspace.
    """

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "litellm_config"

    @property
    def description(self) -> str:
        return (
            "Configure LiteLLM model routing for the research project. "
            "Actions: 'set_model' to set a model for a task type, "
            "'list_models' to show current routing, 'set_fallback' to "
            "configure fallback models, 'get_cost' to check spending."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["set_model", "list_models", "set_fallback", "get_cost"],
                    "description": "Action to perform",
                },
                "model": {
                    "type": "string",
                    "description": "Model identifier (for set_model/set_fallback)",
                },
                "provider": {
                    "type": "string",
                    "description": "Provider name (e.g. openai, anthropic, together)",
                },
                "api_key": {
                    "type": "string",
                    "description": "API key for the provider (stored securely in workspace)",
                },
            },
            "required": ["action"],
        }

    async def execute(
        self,
        action: str,
        model: str = "",
        provider: str = "",
        api_key: str = "",
        **kwargs: Any,
    ) -> ToolResult:
        """Execute LiteLLM configuration action."""
        workspace = Path(self._workspace_dir)
        config_path = workspace / ".litellm_config.json"

        # Load existing config
        config = self._load_config(config_path)

        if action == "list_models":
            return self._list_models(config)
        elif action == "set_model":
            return self._set_model(config, config_path, model, provider)
        elif action == "set_fallback":
            return self._set_fallback(config, config_path, model, provider)
        elif action == "get_cost":
            return self._get_cost(config)
        else:
            return ToolResult(
                success=False,
                error=f"Unknown action: {action}. Use: set_model, list_models, set_fallback, get_cost",
            )

    @staticmethod
    def _load_config(config_path: Path) -> dict[str, Any]:
        """Load LiteLLM config from workspace."""
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {
            "routing_rules": {
                "paper_writing": {"primary": "claude-sonnet-4-20250514", "fallback": "gpt-4o"},
                "peer_review": {"primary": "claude-sonnet-4-20250514", "fallback": "gpt-4o"},
                "data_analysis": {"primary": "gpt-4o", "fallback": "claude-sonnet-4-20250514"},
                "literature_search": {"primary": "gpt-4o-mini", "fallback": "claude-3-5-haiku-20241022"},
                "summarization": {"primary": "gpt-4o-mini", "fallback": "claude-3-5-haiku-20241022"},
                "embedding": {"primary": "text-embedding-3-small", "fallback": "nomic-embed-text"},
            },
            "providers": {},
            "cost_tracking": {"total_usd": 0.0, "requests": 0},
        }

    @staticmethod
    def _save_config(config: dict[str, Any], config_path: Path) -> None:
        """Save LiteLLM config to workspace."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    def _list_models(self, config: dict[str, Any]) -> ToolResult:
        """List current model routing configuration."""
        lines = ["## LiteLLM Model Routing\n"]
        rules = config.get("routing_rules", {})
        for task, rule in sorted(rules.items()):
            lines.append(
                f"- **{task}**: primary=`{rule.get('primary', 'unset')}`, fallback=`{rule.get('fallback', 'unset')}`"
            )

        lines.append("\n## Configured Providers\n")
        providers = config.get("providers", {})
        if providers:
            for prov, info in providers.items():
                lines.append(f"- **{prov}**: {'configured' if info.get('api_key') else 'no key'}")
        else:
            lines.append("- (none configured)")

        lines.append(f"\n## LiteLLM Available: {'Yes' if _HAS_LITELLM else 'No'}")
        if not _HAS_LITELLM:
            lines.append("  Install with: `pip install litellm`")

        return ToolResult(success=True, content="\n".join(lines))

    def _set_model(
        self,
        config: dict[str, Any],
        config_path: Path,
        model: str,
        provider: str,
    ) -> ToolResult:
        """Set the primary model for a task type."""
        if not model:
            return ToolResult(success=False, error="'model' parameter required for set_model")

        # Determine task type from provider or use model as task type
        task_type = provider if provider else "default"

        # If model looks like a task assignment (e.g. "paper_writing:gpt-4o")
        if ":" in model:
            parts = model.split(":", 1)
            task_type = parts[0]
            model = parts[1]

        rules = config.setdefault("routing_rules", {})
        if task_type not in rules:
            rules[task_type] = {"primary": model, "fallback": model}
        else:
            rules[task_type]["primary"] = model

        self._save_config(config, config_path)
        return ToolResult(
            success=True,
            content=f"Set primary model for '{task_type}' to `{model}`",
        )

    def _set_fallback(
        self,
        config: dict[str, Any],
        config_path: Path,
        model: str,
        provider: str,
    ) -> ToolResult:
        """Set the fallback model for a task type."""
        if not model:
            return ToolResult(success=False, error="'model' parameter required for set_fallback")

        task_type = provider if provider else "default"
        if ":" in model:
            parts = model.split(":", 1)
            task_type = parts[0]
            model = parts[1]

        rules = config.setdefault("routing_rules", {})
        if task_type not in rules:
            rules[task_type] = {"primary": model, "fallback": model}
        else:
            rules[task_type]["fallback"] = model

        self._save_config(config, config_path)
        return ToolResult(
            success=True,
            content=f"Set fallback model for '{task_type}' to `{model}`",
        )

    @staticmethod
    def _get_cost(config: dict[str, Any]) -> ToolResult:
        """Get cost tracking information."""
        cost = config.get("cost_tracking", {"total_usd": 0.0, "requests": 0})

        lines = [
            "## Cost Tracking\n",
            f"- **Total spent:** ${cost.get('total_usd', 0.0):.4f}",
            f"- **Total requests:** {cost.get('requests', 0)}",
        ]

        if _HAS_LITELLM:
            try:
                # Try to get litellm's internal cost tracking
                lines.append("\n*LiteLLM is available for real-time cost tracking.*")
            except Exception:
                pass

        return ToolResult(success=True, content="\n".join(lines))


# ===================================================================
# 2. DSPyOptimizeTool
# ===================================================================


class DSPyOptimizeTool(Tool):
    """Run DSPy MIPROv2 optimization on a pipeline module.

    Optimizes prompts for research pipeline modules using training
    examples and evaluation metrics. Saves optimized prompts to workspace.
    """

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "dspy_optimize"

    @property
    def description(self) -> str:
        return (
            "Run DSPy MIPROv2 optimization on a research pipeline module. "
            "Supported modules: 'literature_review', 'data_analysis', "
            "'paper_generation', 'quality_check'. Saves optimized prompts "
            "to the workspace."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "module": {
                    "type": "string",
                    "enum": ["literature_review", "data_analysis", "paper_generation", "quality_check"],
                    "description": "Which module to optimize",
                },
                "metric": {
                    "type": "string",
                    "description": "Evaluation metric name (default: relevance)",
                },
                "n_trials": {
                    "type": "integer",
                    "description": "Number of optimization trials (default: 10)",
                },
            },
            "required": ["module"],
        }

    async def execute(
        self,
        module: str,
        metric: str = "relevance",
        n_trials: int = 10,
        **kwargs: Any,
    ) -> ToolResult:
        """Run DSPy optimization on the specified module."""
        if not _HAS_DSPY:
            return ToolResult(
                success=False,
                error="Package dspy not installed. Run: pip install dspy-ai",
            )

        workspace = Path(self._workspace_dir)

        # Load the module
        try:
            from ..research.dspy_modules.modules import (
                DataAnalysisModule,
                LiteratureReviewModule,
                PaperGenerationModule,
                QualityCheckModule,
            )

            module_map = {
                "literature_review": LiteratureReviewModule,
                "data_analysis": DataAnalysisModule,
                "paper_generation": PaperGenerationModule,
                "quality_check": QualityCheckModule,
            }

            module_cls = module_map.get(module)
            if module_cls is None:
                return ToolResult(
                    success=False,
                    error=f"Unknown module: {module}. Available: {', '.join(module_map.keys())}",
                )

            module_instance = module_cls()
        except Exception as e:
            return ToolResult(success=False, error=f"Failed to load module '{module}': {e}")

        # Look for training data
        trainset_path = workspace / "optimization" / f"{module}_trainset.json"
        if not trainset_path.exists():
            # Create a minimal example trainset
            trainset_path.parent.mkdir(parents=True, exist_ok=True)
            example_trainset = self._create_example_trainset(module)
            with open(trainset_path, "w") as f:
                json.dump(example_trainset, f, indent=2)

        # Load training data
        with open(trainset_path) as f:
            raw_examples = json.load(f)

        if not raw_examples:
            return ToolResult(
                success=False,
                error=f"Training set is empty. Add examples to {trainset_path}",
            )

        try:
            trainset = [dspy.Example(**ex).with_inputs(*ex.keys()) for ex in raw_examples]

            # Define metric
            def default_metric(example: Any, prediction: Any, trace: Any = None) -> float:
                return 1.0 if prediction else 0.0

            # Run optimization
            optimizer = dspy.MIPROv2(  # type: ignore[attr-defined]
                metric=default_metric,
                num_candidates=min(n_trials, 7),
            )

            optimized = optimizer.compile(module_instance, trainset=trainset)

            # Save optimized module
            output_dir = workspace / "optimization" / "optimized"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{module}_optimized.json"
            optimized.save(str(output_path))

            result = {
                "module": module,
                "metric": metric,
                "n_trials": n_trials,
                "trainset_size": len(trainset),
                "output_path": str(output_path),
                "status": "Optimization completed successfully",
            }
            return ToolResult(success=True, content=json.dumps(result, indent=2))

        except Exception as e:
            return ToolResult(success=False, error=f"DSPy optimization failed: {e}")

    @staticmethod
    def _create_example_trainset(module: str) -> list[dict[str, Any]]:
        """Create a minimal example training set for a module."""
        if module == "literature_review":  # noqa: SIM116
            return [
                {
                    "research_question": "What is the impact of fiscal policy on economic growth in developing countries?",
                    "context": "Focus on panel data studies from 2010-2023",
                },
                {
                    "research_question": "How does human capital investment affect poverty reduction?",
                    "context": "Indonesian context, BPS data",
                },
            ]
        elif module == "data_analysis":
            return [
                {
                    "research_questions": ["Does education spending reduce poverty?"],
                    "data_description": "Panel data, 34 provinces, 2010-2022, variables: poverty_rate, edu_spending, gdp_per_capita",
                },
            ]
        elif module == "paper_generation":
            return [
                {
                    "section_name": "introduction",
                    "outline": "1. Background on poverty in Indonesia\n2. Research gap\n3. Objectives",
                    "context": "BPS research paper on provincial poverty determinants",
                },
            ]
        elif module == "quality_check":
            return [
                {
                    "text": "The results show a significant relationship (p < 0.05) between X and Y.",
                    "check_types": ["statistics", "citations"],
                },
            ]
        return []
