"""DSPy module implementations for research pipeline steps.

Each module wraps one or more DSPy signatures into a composable pipeline
with a ``forward()`` method. When DSPy is not installed, each module
provides a fallback that assembles a simple prompt string instead.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional dependency: dspy
# ---------------------------------------------------------------------------

_HAS_DSPY = False
try:
    import dspy

    _HAS_DSPY = True
except ImportError:
    dspy = None  # type: ignore[assignment]

# Import signatures (works regardless of DSPy availability)
from .signatures import (  # noqa: E402
    EvidenceSynthesisSignature,
    MethodologyDesignSignature,
    ResultsInterpretationSignature,
    SearchQuerySignature,
    SectionWritingSignature,
)

# ===================================================================
# Helper: simple prompt assembly for fallback mode
# ===================================================================


def _fallback_prompt(task: str, **kwargs: Any) -> str:
    """Build a simple prompt string from task description and kwargs.

    Used when DSPy is not available to provide a structured prompt
    that can be sent to any LLM via the gateway.
    """
    parts = [f"Task: {task}\n"]
    for key, value in kwargs.items():
        if isinstance(value, list):
            items = "\n".join(f"  - {item}" for item in value)
            parts.append(f"{key}:\n{items}")
        else:
            parts.append(f"{key}: {value}")
    return "\n\n".join(parts)


# ===================================================================
# Fallback result container
# ===================================================================


class FallbackPrediction:
    """Minimal prediction container for fallback mode.

    Mimics ``dspy.Prediction`` so downstream code can access
    attributes uniformly.
    """

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"FallbackPrediction({attrs})"

    def __bool__(self) -> bool:
        return True


# ===================================================================
# 1. LiteratureReviewModule
# ===================================================================


class LiteratureReviewModule:
    """End-to-end literature review pipeline.

    When DSPy is available, chains:
        SearchQuerySignature → EvidenceSynthesisSignature

    Fallback mode assembles structured prompts for each step.
    """

    def __init__(self) -> None:
        if _HAS_DSPY:
            self._generate_queries = dspy.Predict(SearchQuerySignature)
            self._synthesize = dspy.Predict(EvidenceSynthesisSignature)
        else:
            self._generate_queries = None
            self._synthesize = None

    def forward(
        self,
        research_question: str,
        context: str = "",
    ) -> Any:
        """Run the literature review pipeline.

        Args:
            research_question: The research question to review literature for.
            context: Optional background context or constraints.

        Returns:
            Prediction with ``queries``, ``synthesis``, and ``gaps`` attributes.
        """
        if _HAS_DSPY and self._generate_queries is not None:
            return self._forward_dspy(research_question, context)
        return self._forward_fallback(research_question, context)

    def _forward_dspy(self, research_question: str, context: str) -> Any:
        """DSPy-powered forward pass."""
        queries_result = self._generate_queries(topic=research_question)
        queries = queries_result.search_queries if hasattr(queries_result, "search_queries") else [research_question]

        synthesis_result = self._synthesize(papers=queries)
        synthesis = synthesis_result.synthesis if hasattr(synthesis_result, "synthesis") else ""

        return dspy.Prediction(
            queries=queries,
            synthesis=synthesis,
            gaps=[],
        )

    @staticmethod
    def _forward_fallback(research_question: str, context: str) -> FallbackPrediction:
        """Fallback: assemble prompts for manual LLM invocation."""
        query_prompt = _fallback_prompt(
            "Generate 3-5 diverse academic search queries for the following research question.",
            research_question=research_question,
            context=context or "(none)",
        )

        synthesis_prompt = _fallback_prompt(
            "Synthesize the literature on this topic into a thematic narrative.",
            research_question=research_question,
        )

        return FallbackPrediction(
            queries=[research_question],
            synthesis=f"[Fallback mode — send these prompts to an LLM]\n\n{query_prompt}\n\n---\n\n{synthesis_prompt}",
            gaps=["DSPy not installed — run pip install dspy-ai for optimizable pipelines"],
            prompts={"query_generation": query_prompt, "synthesis": synthesis_prompt},
        )


# ===================================================================
# 2. DataAnalysisModule
# ===================================================================


class DataAnalysisModule:
    """Statistical analysis planning and interpretation pipeline.

    When DSPy is available, chains:
        MethodologyDesignSignature → ResultsInterpretationSignature

    Fallback mode assembles structured prompts.
    """

    def __init__(self) -> None:
        if _HAS_DSPY:
            self._design = dspy.Predict(MethodologyDesignSignature)
            self._interpret = dspy.Predict(ResultsInterpretationSignature)
        else:
            self._design = None
            self._interpret = None

    def forward(
        self,
        research_questions: list[str],
        data_description: str,
        statistical_results: str = "",
    ) -> Any:
        """Run the data analysis pipeline.

        Args:
            research_questions: List of research questions.
            data_description: Description of available data.
            statistical_results: Optional raw statistical output to interpret.

        Returns:
            Prediction with ``methodology``, ``interpretation`` attributes.
        """
        if _HAS_DSPY and self._design is not None:
            return self._forward_dspy(research_questions, data_description, statistical_results)
        return self._forward_fallback(research_questions, data_description, statistical_results)

    def _forward_dspy(
        self,
        research_questions: list[str],
        data_description: str,
        statistical_results: str,
    ) -> Any:
        """DSPy-powered forward pass."""
        design_result = self._design(
            research_questions=research_questions,
            data_description=data_description,
        )
        methodology = design_result.methodology if hasattr(design_result, "methodology") else ""

        interpretation = ""
        if statistical_results:
            interp_result = self._interpret(statistical_results=statistical_results)
            interpretation = interp_result.interpretation if hasattr(interp_result, "interpretation") else ""

        return dspy.Prediction(
            methodology=methodology,
            interpretation=interpretation,
        )

    @staticmethod
    def _forward_fallback(
        research_questions: list[str],
        data_description: str,
        statistical_results: str,
    ) -> FallbackPrediction:
        """Fallback: assemble prompts."""
        design_prompt = _fallback_prompt(
            "Design a research methodology for the following questions and data.",
            research_questions=research_questions,
            data_description=data_description,
        )

        interpretation_prompt = ""
        if statistical_results:
            interpretation_prompt = _fallback_prompt(
                "Interpret the following statistical results in plain language.",
                statistical_results=statistical_results,
            )

        return FallbackPrediction(
            methodology=f"[Fallback mode]\n\n{design_prompt}",
            interpretation=f"[Fallback mode]\n\n{interpretation_prompt}" if interpretation_prompt else "",
            prompts={
                "methodology_design": design_prompt,
                "results_interpretation": interpretation_prompt,
            },
        )


# ===================================================================
# 3. PaperGenerationModule
# ===================================================================


class PaperGenerationModule:
    """Section generation pipeline for academic papers.

    When DSPy is available, uses SectionWritingSignature.
    Fallback mode assembles a structured writing prompt.
    """

    def __init__(self) -> None:
        if _HAS_DSPY:
            self._write_section = dspy.Predict(SectionWritingSignature)
        else:
            self._write_section = None

    def forward(
        self,
        section_name: str,
        outline: str,
        context: str = "",
        citations: list[str] | None = None,
    ) -> Any:
        """Generate a paper section.

        Args:
            section_name: Name of the section (e.g. 'introduction', 'methods').
            outline: Section outline with key points.
            context: Supporting context (evidence, data summaries).
            citations: Available citation keys.

        Returns:
            Prediction with ``section_text`` attribute.
        """
        cite_list = citations or []

        if _HAS_DSPY and self._write_section is not None:
            return self._forward_dspy(section_name, outline, context, cite_list)
        return self._forward_fallback(section_name, outline, context, cite_list)

    def _forward_dspy(
        self,
        section_name: str,
        outline: str,
        context: str,
        citations: list[str],
    ) -> Any:
        """DSPy-powered forward pass."""
        result = self._write_section(
            outline=f"Section: {section_name}\n\n{outline}",
            context=context,
            citations=citations,
        )
        section_text = result.section_text if hasattr(result, "section_text") else ""
        return dspy.Prediction(section_text=section_text)

    @staticmethod
    def _forward_fallback(
        section_name: str,
        outline: str,
        context: str,
        citations: list[str],
    ) -> FallbackPrediction:
        """Fallback: assemble a writing prompt."""
        prompt = _fallback_prompt(
            f"Write the '{section_name}' section of an academic paper in LaTeX format.",
            outline=outline,
            context=context or "(none provided)",
            available_citations=citations or ["(none)"],
            instructions=(
                "Use \\cite{} for all citations. Follow APA 7th edition style. Write in formal academic English."
            ),
        )

        return FallbackPrediction(
            section_text=f"[Fallback mode — send this prompt to an LLM]\n\n{prompt}",
            prompts={"section_writing": prompt},
        )


# ===================================================================
# 4. QualityCheckModule
# ===================================================================


class QualityCheckModule:
    """Quality verification pipeline for research outputs.

    Checks for:
    - Citation completeness and consistency
    - Statistical reporting standards
    - Logical flow and argumentation
    - Methodology-results alignment

    When DSPy is available, uses a chain of Predict calls.
    Fallback mode assembles structured review prompts.
    """

    def __init__(self) -> None:
        if _HAS_DSPY:
            self._check_citations = dspy.ChainOfThought(  # type: ignore[attr-defined]
                "text -> citation_issues: list[str]"
            )
            self._check_stats = dspy.ChainOfThought(  # type: ignore[attr-defined]
                "text -> statistical_issues: list[str]"
            )
            self._check_logic = dspy.ChainOfThought(  # type: ignore[attr-defined]
                "text -> logical_issues: list[str]"
            )
        else:
            self._check_citations = None
            self._check_stats = None
            self._check_logic = None

    def forward(
        self,
        text: str,
        check_types: list[str] | None = None,
    ) -> Any:
        """Run quality checks on the provided text.

        Args:
            text: The manuscript text to check.
            check_types: Which checks to run. Options: 'citations',
                'statistics', 'logic', 'all'. Default: 'all'.

        Returns:
            Prediction with ``issues`` dict and ``overall_quality`` score.
        """
        checks = check_types or ["all"]
        if "all" in checks:
            checks = ["citations", "statistics", "logic"]

        if _HAS_DSPY and self._check_citations is not None:
            return self._forward_dspy(text, checks)
        return self._forward_fallback(text, checks)

    def _forward_dspy(self, text: str, checks: list[str]) -> Any:
        """DSPy-powered forward pass."""
        issues: dict[str, list[str]] = {}

        if "citations" in checks:
            result = self._check_citations(text=text)
            issues["citations"] = result.citation_issues if hasattr(result, "citation_issues") else []

        if "statistics" in checks:
            result = self._check_stats(text=text)
            issues["statistics"] = result.statistical_issues if hasattr(result, "statistical_issues") else []

        if "logic" in checks:
            result = self._check_logic(text=text)
            issues["logic"] = result.logical_issues if hasattr(result, "logical_issues") else []

        total_issues = sum(len(v) for v in issues.values())
        quality_score = max(0.0, 1.0 - (total_issues * 0.1))

        return dspy.Prediction(
            issues=issues,
            total_issues=total_issues,
            overall_quality=round(quality_score, 2),
        )

    @staticmethod
    def _forward_fallback(text: str, checks: list[str]) -> FallbackPrediction:
        """Fallback: assemble review prompts."""
        prompts: dict[str, str] = {}

        if "citations" in checks:
            prompts["citation_check"] = _fallback_prompt(
                "Check the following text for citation issues.",
                text=text[:3000],
                check_for=[
                    "Missing citations for claims",
                    "Inconsistent citation formatting",
                    "Citations not in reference list",
                    "Self-citation ratio",
                ],
            )

        if "statistics" in checks:
            prompts["statistics_check"] = _fallback_prompt(
                "Check the following text for statistical reporting issues.",
                text=text[:3000],
                check_for=[
                    "Missing p-values or confidence intervals",
                    "Incorrect test selection",
                    "Missing effect sizes",
                    "Assumption violations not addressed",
                ],
            )

        if "logic" in checks:
            prompts["logic_check"] = _fallback_prompt(
                "Check the following text for logical flow issues.",
                text=text[:3000],
                check_for=[
                    "Non-sequitur arguments",
                    "Unsupported conclusions",
                    "Methodology-results misalignment",
                    "Missing limitations discussion",
                ],
            )

        return FallbackPrediction(
            issues={check: ["[Run prompt through LLM for results]"] for check in checks},
            total_issues=0,
            overall_quality=0.0,
            prompts=prompts,
            note="DSPy not installed — send prompts to an LLM for quality assessment",
        )
