"""DSPy pipeline modules for optimizable research workflows.

Provides composable, optimizable modules for each research step.
Falls back gracefully if DSPy is not installed.
"""

from __future__ import annotations

import logging
from typing import Any

from ..tools.base import Tool, ToolResult
from .exceptions import DependencyMissingError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency: dspy
# ---------------------------------------------------------------------------

try:
    import dspy

    DSPY_AVAILABLE = True
except ImportError:
    dspy = None  # type: ignore[assignment]
    DSPY_AVAILABLE = False


def _require_dspy() -> None:
    """Raise if DSPy is not installed."""
    if not DSPY_AVAILABLE:
        raise DependencyMissingError(
            "dspy",
            install_hint="pip install dspy-ai",
        )


# ===========================================================================
# DSPy Signatures — define input/output contracts for each research step
# ===========================================================================

if DSPY_AVAILABLE:

    class GenerateSearchQueries(dspy.Signature):  # type: ignore[misc]
        """Generate academic search queries from a research question.

        Given a research question and optional context, produce a set of
        diverse search queries suitable for Semantic Scholar / OpenAlex.
        """

        research_question: str = dspy.InputField(  # type: ignore[assignment]
            desc="The research question to generate queries for",
        )
        context: str = dspy.InputField(  # type: ignore[assignment]
            desc="Optional background context or methodology notes",
            default="",
        )
        queries: list[str] = dspy.OutputField(  # type: ignore[assignment]
            desc="List of 3-5 diverse academic search queries",
        )

    class AssessRelevance(dspy.Signature):  # type: ignore[misc]
        """Assess whether a paper is relevant to the research question."""

        research_question: str = dspy.InputField(  # type: ignore[assignment]
            desc="The research question",
        )
        paper_title: str = dspy.InputField(  # type: ignore[assignment]
            desc="Title of the candidate paper",
        )
        paper_abstract: str = dspy.InputField(  # type: ignore[assignment]
            desc="Abstract of the candidate paper",
        )
        relevance_score: float = dspy.OutputField(  # type: ignore[assignment]
            desc="Relevance score from 0.0 (irrelevant) to 1.0 (highly relevant)",
        )
        reasoning: str = dspy.OutputField(  # type: ignore[assignment]
            desc="Brief explanation of the relevance assessment",
        )

    class ExtractEvidence(dspy.Signature):  # type: ignore[misc]
        """Extract key evidence and claims from a paper section."""

        paper_text: str = dspy.InputField(  # type: ignore[assignment]
            desc="Text from a paper section to extract evidence from",
        )
        research_question: str = dspy.InputField(  # type: ignore[assignment]
            desc="The research question guiding extraction",
        )
        claims: list[str] = dspy.OutputField(  # type: ignore[assignment]
            desc="Key claims or findings extracted from the text",
        )
        evidence: list[str] = dspy.OutputField(  # type: ignore[assignment]
            desc="Supporting evidence for each claim",
        )
        methodology_notes: str = dspy.OutputField(  # type: ignore[assignment]
            desc="Notes on the methodology used in the source",
        )

    class SynthesizeEvidence(dspy.Signature):  # type: ignore[misc]
        """Synthesize evidence from multiple sources into a coherent narrative."""

        research_question: str = dspy.InputField(  # type: ignore[assignment]
            desc="The research question being addressed",
        )
        evidence_items: list[str] = dspy.InputField(  # type: ignore[assignment]
            desc="List of evidence items from different sources",
        )
        synthesis: str = dspy.OutputField(  # type: ignore[assignment]
            desc="Synthesized narrative combining the evidence",
        )
        gaps: list[str] = dspy.OutputField(  # type: ignore[assignment]
            desc="Identified gaps in the current evidence",
        )

    class PlanAnalysis(dspy.Signature):  # type: ignore[misc]
        """Plan a statistical analysis approach for the research data."""

        research_question: str = dspy.InputField(  # type: ignore[assignment]
            desc="The research question to analyze",
        )
        data_description: str = dspy.InputField(  # type: ignore[assignment]
            desc="Description of available data (variables, types, size)",
        )
        methodology: str = dspy.InputField(  # type: ignore[assignment]
            desc="Chosen methodology (e.g., panel_data, time_series)",
        )
        analysis_steps: list[str] = dspy.OutputField(  # type: ignore[assignment]
            desc="Ordered list of analysis steps to perform",
        )
        assumptions_to_check: list[str] = dspy.OutputField(  # type: ignore[assignment]
            desc="Statistical assumptions that must be verified",
        )
        python_code: str = dspy.OutputField(  # type: ignore[assignment]
            desc="Python code skeleton for the analysis",
        )

    class InterpretResults(dspy.Signature):  # type: ignore[misc]
        """Interpret statistical results in the context of the research question."""

        research_question: str = dspy.InputField(  # type: ignore[assignment]
            desc="The research question",
        )
        statistical_output: str = dspy.InputField(  # type: ignore[assignment]
            desc="Raw statistical output (tables, coefficients, p-values)",
        )
        interpretation: str = dspy.OutputField(  # type: ignore[assignment]
            desc="Plain-language interpretation of the results",
        )
        limitations: list[str] = dspy.OutputField(  # type: ignore[assignment]
            desc="Limitations and caveats of the analysis",
        )

    class WriteSectionDraft(dspy.Signature):  # type: ignore[misc]
        """Write a draft of a paper section following academic conventions."""

        section_name: str = dspy.InputField(  # type: ignore[assignment]
            desc="Section name (e.g., 'introduction', 'methodology')",
        )
        outline: str = dspy.InputField(  # type: ignore[assignment]
            desc="Section outline or key points to cover",
        )
        evidence: str = dspy.InputField(  # type: ignore[assignment]
            desc="Evidence and references to incorporate",
        )
        style_guide: str = dspy.InputField(  # type: ignore[assignment]
            desc="Target journal style requirements",
            default="APA 7th edition",
        )
        draft: str = dspy.OutputField(  # type: ignore[assignment]
            desc="LaTeX-formatted section draft with citations",
        )

    # -----------------------------------------------------------------------
    # DSPy Modules — composable pipelines built from signatures
    # -----------------------------------------------------------------------

    class LiteratureReviewModule(dspy.Module):  # type: ignore[misc]
        """End-to-end literature review pipeline.

        Chains: GenerateSearchQueries → AssessRelevance → ExtractEvidence
        → SynthesizeEvidence to produce a literature synthesis from a
        research question.
        """

        def __init__(self) -> None:
            super().__init__()
            self.generate_queries = dspy.Predict(GenerateSearchQueries)
            self.assess_relevance = dspy.Predict(AssessRelevance)
            self.extract_evidence = dspy.Predict(ExtractEvidence)
            self.synthesize = dspy.Predict(SynthesizeEvidence)

        def forward(
            self,
            research_question: str,
            context: str = "",
        ) -> dspy.Prediction:  # type: ignore[name-defined]
            queries_result = self.generate_queries(
                research_question=research_question,
                context=context,
            )

            all_evidence: list[str] = []
            for query in queries_result.queries[:5]:
                extraction = self.extract_evidence(
                    paper_text=query,
                    research_question=research_question,
                )
                all_evidence.extend(extraction.claims)

            synthesis = self.synthesize(
                research_question=research_question,
                evidence_items=all_evidence,
            )

            return dspy.Prediction(
                queries=queries_result.queries,
                evidence=all_evidence,
                synthesis=synthesis.synthesis,
                gaps=synthesis.gaps,
            )

    class StatisticalAnalysisModule(dspy.Module):  # type: ignore[misc]
        """Statistical analysis planning and interpretation pipeline.

        Chains: PlanAnalysis → InterpretResults to produce an analysis
        plan and interpret the resulting output.
        """

        def __init__(self) -> None:
            super().__init__()
            self.plan = dspy.Predict(PlanAnalysis)
            self.interpret = dspy.Predict(InterpretResults)

        def forward(
            self,
            research_question: str,
            data_description: str,
            methodology: str = "panel_data",
            statistical_output: str = "",
        ) -> dspy.Prediction:  # type: ignore[name-defined]
            plan_result = self.plan(
                research_question=research_question,
                data_description=data_description,
                methodology=methodology,
            )

            interpretation = None
            if statistical_output:
                interp_result = self.interpret(
                    research_question=research_question,
                    statistical_output=statistical_output,
                )
                interpretation = interp_result.interpretation

            return dspy.Prediction(
                analysis_steps=plan_result.analysis_steps,
                assumptions_to_check=plan_result.assumptions_to_check,
                python_code=plan_result.python_code,
                interpretation=interpretation,
            )

else:
    # -----------------------------------------------------------------------
    # Stub classes when DSPy is not installed
    # -----------------------------------------------------------------------

    class _DSPyStub:
        """Base stub that raises on instantiation when DSPy is missing."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            _require_dspy()

        def __init_subclass__(cls, **kwargs: Any) -> None:
            super().__init_subclass__(**kwargs)

    GenerateSearchQueries = type("GenerateSearchQueries", (_DSPyStub,), {})  # type: ignore[misc]
    AssessRelevance = type("AssessRelevance", (_DSPyStub,), {})  # type: ignore[misc]
    ExtractEvidence = type("ExtractEvidence", (_DSPyStub,), {})  # type: ignore[misc]
    SynthesizeEvidence = type("SynthesizeEvidence", (_DSPyStub,), {})  # type: ignore[misc]
    PlanAnalysis = type("PlanAnalysis", (_DSPyStub,), {})  # type: ignore[misc]
    InterpretResults = type("InterpretResults", (_DSPyStub,), {})  # type: ignore[misc]
    WriteSectionDraft = type("WriteSectionDraft", (_DSPyStub,), {})  # type: ignore[misc]
    LiteratureReviewModule = type("LiteratureReviewModule", (_DSPyStub,), {})  # type: ignore[misc]
    StatisticalAnalysisModule = type("StatisticalAnalysisModule", (_DSPyStub,), {})  # type: ignore[misc]


# ===========================================================================
# DSPy Optimizer wrapper
# ===========================================================================


class DSPyOptimizer:
    """Wrapper for DSPy optimization (prompt tuning / bootstrapping).

    Provides a simplified interface to DSPy's optimization capabilities,
    allowing research modules to be tuned against a training set and
    evaluation metric.
    """

    def __init__(self, strategy: str = "bootstrap_few_shot") -> None:
        """Initialize the optimizer.

        Args:
            strategy: Optimization strategy. One of ``"bootstrap_few_shot"``,
                ``"mipro"``, or ``"random_search"``.
        """
        _require_dspy()
        self.strategy = strategy

    def optimize(
        self,
        module: Any,
        trainset: list[Any],
        metric: Any,
        max_bootstrapped_demos: int = 4,
        max_labeled_demos: int = 8,
    ) -> Any:
        """Optimize a DSPy module against a training set.

        Args:
            module: A ``dspy.Module`` instance to optimize.
            trainset: List of ``dspy.Example`` training examples.
            metric: Evaluation function ``(example, prediction) -> float``.
            max_bootstrapped_demos: Max bootstrapped few-shot demos.
            max_labeled_demos: Max labeled demos to include.

        Returns:
            The optimized module.

        Raises:
            DependencyMissingError: If DSPy is not installed.
            ValueError: If the strategy is not recognized.
        """
        _require_dspy()

        if self.strategy == "bootstrap_few_shot":
            optimizer = dspy.BootstrapFewShot(  # type: ignore[union-attr]
                metric=metric,
                max_bootstrapped_demos=max_bootstrapped_demos,
                max_labeled_demos=max_labeled_demos,
            )
        elif self.strategy == "mipro":
            optimizer = dspy.MIPROv2(  # type: ignore[union-attr]
                metric=metric,
                num_candidates=7,
            )
        elif self.strategy == "random_search":
            optimizer = dspy.BootstrapFewShotWithRandomSearch(  # type: ignore[union-attr]
                metric=metric,
                max_bootstrapped_demos=max_bootstrapped_demos,
                num_candidate_programs=10,
            )
        else:
            raise ValueError(
                f"Unknown optimization strategy: {self.strategy!r}. "
                f"Choose from: bootstrap_few_shot, mipro, random_search"
            )

        logger.info(
            "Optimizing module %s with strategy=%s, trainset_size=%d",
            type(module).__name__,
            self.strategy,
            len(trainset),
        )

        return optimizer.compile(module, trainset=trainset)


# ===========================================================================
# Tool subclasses for agent integration
# ===========================================================================


class LiteLLMConfigTool(Tool):
    """Tool for configuring LiteLLM model routing at runtime.

    Allows the agent to inspect and modify model routing rules
    and check gateway cost status.
    """

    @property
    def name(self) -> str:
        return "litellm_config"

    @property
    def description(self) -> str:
        return (
            "Configure LLM model routing. Actions: 'status' to see current "
            "routing rules and cost tracking, 'set_model' to override the "
            "model for a task type."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "set_model"],
                    "description": "Action to perform",
                },
                "task_type": {
                    "type": "string",
                    "description": "Task type to configure (for set_model)",
                },
                "model": {
                    "type": "string",
                    "description": "Model identifier to set (for set_model)",
                },
            },
            "required": ["action"],
        }

    async def execute(
        self,
        action: str,
        task_type: str = "",
        model: str = "",
    ) -> ToolResult:
        from .llm_gateway import ROUTING_RULES

        if action == "status":
            lines = ["**LLM Routing Rules:**"]
            for task, rule in ROUTING_RULES.items():
                lines.append(f"  {task}: primary={rule['primary']}, fallback={rule['fallback']}")
            return ToolResult(success=True, content="\n".join(lines))

        if action == "set_model":
            if not task_type or not model:
                return ToolResult(
                    success=False,
                    error="Both 'task_type' and 'model' are required for set_model",
                )
            if task_type not in ROUTING_RULES:
                ROUTING_RULES[task_type] = {"primary": model, "fallback": model}
            else:
                ROUTING_RULES[task_type]["primary"] = model
            return ToolResult(
                success=True,
                content=f"Set primary model for '{task_type}' to '{model}'",
            )

        return ToolResult(success=False, error=f"Unknown action: {action}")


class DSPyOptimizeTool(Tool):
    """Tool for triggering DSPy module optimization from the agent.

    Exposes optimization capabilities so the agent can tune its own
    research pipelines when training data is available.
    """

    @property
    def name(self) -> str:
        return "dspy_optimize"

    @property
    def description(self) -> str:
        return (
            "Optimize a DSPy research module using training examples. "
            "Requires DSPy to be installed. Supported modules: "
            "'literature_review', 'statistical_analysis'."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "module_name": {
                    "type": "string",
                    "enum": ["literature_review", "statistical_analysis"],
                    "description": "Which module to optimize",
                },
                "strategy": {
                    "type": "string",
                    "enum": ["bootstrap_few_shot", "mipro", "random_search"],
                    "description": "Optimization strategy (default: bootstrap_few_shot)",
                },
                "trainset_path": {
                    "type": "string",
                    "description": "Path to JSON file with training examples",
                },
            },
            "required": ["module_name", "trainset_path"],
        }

    async def execute(
        self,
        module_name: str,
        trainset_path: str,
        strategy: str = "bootstrap_few_shot",
    ) -> ToolResult:
        try:
            _require_dspy()
        except DependencyMissingError as exc:
            return ToolResult(success=False, error=str(exc))

        import json
        from pathlib import Path

        trainset_file = Path(trainset_path)
        if not trainset_file.exists():
            return ToolResult(
                success=False,
                error=f"Training set file not found: {trainset_path}",
            )

        try:
            with open(trainset_file, encoding="utf-8") as f:
                raw_examples = json.load(f)

            trainset = [dspy.Example(**ex).with_inputs(*ex.keys()) for ex in raw_examples]  # type: ignore[union-attr]

            if module_name == "literature_review":
                module = LiteratureReviewModule()
            elif module_name == "statistical_analysis":
                module = StatisticalAnalysisModule()
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown module: {module_name}",
                )

            def default_metric(example: Any, prediction: Any, trace: Any = None) -> float:
                return 1.0 if prediction else 0.0

            optimizer = DSPyOptimizer(strategy=strategy)
            optimized = optimizer.optimize(
                module=module,
                trainset=trainset,
                metric=default_metric,
            )

            output_path = trainset_file.parent / f"{module_name}_optimized.json"
            optimized.save(str(output_path))

            return ToolResult(
                success=True,
                content=(
                    f"Optimized '{module_name}' with strategy='{strategy}', "
                    f"{len(trainset)} examples. Saved to {output_path}"
                ),
            )
        except Exception as exc:
            return ToolResult(success=False, error=f"Optimization failed: {exc}")
