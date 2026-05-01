"""DSPy signature definitions for research pipeline steps.

Each signature defines the input/output contract for a composable
research step. When DSPy is not installed, lightweight stub classes
are provided so that imports never fail.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Optional dependency: dspy
# ---------------------------------------------------------------------------

_HAS_DSPY = False
try:
    import dspy

    _HAS_DSPY = True
except ImportError:
    dspy = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Stub base for when DSPy is not installed
# ---------------------------------------------------------------------------


class _SignatureStub:
    """Lightweight stub that mimics a DSPy Signature at the class level.

    Instances store their keyword arguments as attributes so that
    fallback code can still read ``sig.topic``, ``sig.papers``, etc.
    """

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{type(self).__name__}({attrs})"


# ===================================================================
# 1. SearchQuerySignature
# ===================================================================

if _HAS_DSPY:

    class SearchQuerySignature(dspy.Signature):  # type: ignore[misc]
        """Generate structured academic search queries from a research topic.

        Given a research topic and optional constraints, produce a list of
        diverse search queries suitable for Semantic Scholar, OpenAlex, or
        Google Scholar.
        """

        topic: str = dspy.InputField(  # type: ignore[assignment]
            desc="The research topic or question to generate queries for",
        )
        search_queries: list[str] = dspy.OutputField(  # type: ignore[assignment]
            desc=(
                "List of 3-5 diverse, well-formed academic search queries. "
                "Include synonyms, related concepts, and methodological terms."
            ),
        )

else:

    class SearchQuerySignature(_SignatureStub):  # type: ignore[no-redef]
        """Stub: Generate structured academic search queries from a topic."""

        pass


# ===================================================================
# 2. EvidenceSynthesisSignature
# ===================================================================

if _HAS_DSPY:

    class EvidenceSynthesisSignature(dspy.Signature):  # type: ignore[misc]
        """Synthesize evidence from multiple papers into a thematic summary.

        Given a collection of paper excerpts and findings, produce a
        coherent thematic synthesis that identifies consensus, contradictions,
        and gaps in the literature.
        """

        papers: list[str] = dspy.InputField(  # type: ignore[assignment]
            desc="List of paper excerpts or summaries to synthesize",
        )
        synthesis: str = dspy.OutputField(  # type: ignore[assignment]
            desc=(
                "Thematic synthesis of the evidence. Organize by theme, "
                "note consensus and contradictions, identify gaps."
            ),
        )

else:

    class EvidenceSynthesisSignature(_SignatureStub):  # type: ignore[no-redef]
        """Stub: Synthesize evidence from multiple papers."""

        pass


# ===================================================================
# 3. MethodologyDesignSignature
# ===================================================================

if _HAS_DSPY:

    class MethodologyDesignSignature(dspy.Signature):  # type: ignore[misc]
        """Design a research methodology given questions and data description.

        Produces a structured methodology section including statistical
        methods, variable definitions, and assumption checks.
        """

        research_questions: list[str] = dspy.InputField(  # type: ignore[assignment]
            desc="List of research questions to address",
        )
        data_description: str = dspy.InputField(  # type: ignore[assignment]
            desc="Description of available data (variables, types, sample size, source)",
        )
        methodology: str = dspy.OutputField(  # type: ignore[assignment]
            desc=(
                "Detailed methodology section including: research design, "
                "statistical methods, variable operationalization, "
                "assumption checks, and robustness tests."
            ),
        )

else:

    class MethodologyDesignSignature(_SignatureStub):  # type: ignore[no-redef]
        """Stub: Design a research methodology."""

        pass


# ===================================================================
# 4. ResultsInterpretationSignature
# ===================================================================

if _HAS_DSPY:

    class ResultsInterpretationSignature(dspy.Signature):  # type: ignore[misc]
        """Interpret statistical results in plain language.

        Given raw statistical output (tables, coefficients, p-values),
        produce a clear interpretation with appropriate caveats.
        """

        statistical_results: str = dspy.InputField(  # type: ignore[assignment]
            desc="Raw statistical output (regression tables, test statistics, etc.)",
        )
        interpretation: str = dspy.OutputField(  # type: ignore[assignment]
            desc=(
                "Plain-language interpretation of the results including: "
                "key findings, effect sizes, statistical significance, "
                "practical significance, and limitations."
            ),
        )

else:

    class ResultsInterpretationSignature(_SignatureStub):  # type: ignore[no-redef]
        """Stub: Interpret statistical results."""

        pass


# ===================================================================
# 5. SectionWritingSignature
# ===================================================================

if _HAS_DSPY:

    class SectionWritingSignature(dspy.Signature):  # type: ignore[misc]
        """Write a paper section from an outline with citations.

        Given a section outline, supporting context, and citation keys,
        produce a well-written academic section in LaTeX format.
        """

        outline: str = dspy.InputField(  # type: ignore[assignment]
            desc="Section outline with key points to cover",
        )
        context: str = dspy.InputField(  # type: ignore[assignment]
            desc="Supporting context: evidence, data summaries, prior sections",
        )
        citations: list[str] = dspy.InputField(  # type: ignore[assignment]
            desc="Available citation keys from the bibliography",
        )
        section_text: str = dspy.OutputField(  # type: ignore[assignment]
            desc=(
                "Well-written academic section text in LaTeX format. "
                "Use \\cite{} for citations, \\ref{} for cross-references."
            ),
        )

else:

    class SectionWritingSignature(_SignatureStub):  # type: ignore[no-redef]
        """Stub: Write a paper section from an outline."""

        pass
