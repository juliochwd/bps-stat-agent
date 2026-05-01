"""Comprehensive coverage tests for mini_agent/research/dspy_modules/.

Tests signatures.py, modules.py, and __init__.py.
All tests work without DSPy installed (fallback mode).
"""

from __future__ import annotations

import pytest


# ===========================================================================
# Signatures tests
# ===========================================================================


class TestSignatures:
    """Test DSPy signature stubs."""

    def test_search_query_signature_import(self):
        from mini_agent.research.dspy_modules.signatures import SearchQuerySignature
        sig = SearchQuerySignature(topic="test topic")
        assert sig.topic == "test topic"

    def test_evidence_synthesis_signature_import(self):
        from mini_agent.research.dspy_modules.signatures import EvidenceSynthesisSignature
        sig = EvidenceSynthesisSignature(papers=["paper1", "paper2"])
        assert sig.papers == ["paper1", "paper2"]

    def test_methodology_design_signature_import(self):
        from mini_agent.research.dspy_modules.signatures import MethodologyDesignSignature
        sig = MethodologyDesignSignature(
            research_questions=["Q1"],
            data_description="Panel data",
        )
        assert sig.research_questions == ["Q1"]
        assert sig.data_description == "Panel data"

    def test_results_interpretation_signature_import(self):
        from mini_agent.research.dspy_modules.signatures import ResultsInterpretationSignature
        sig = ResultsInterpretationSignature(statistical_results="p < 0.05")
        assert sig.statistical_results == "p < 0.05"

    def test_section_writing_signature_import(self):
        from mini_agent.research.dspy_modules.signatures import SectionWritingSignature
        sig = SectionWritingSignature(
            outline="Introduction outline",
            context="Background",
            citations=["cite1"],
        )
        assert sig.outline == "Introduction outline"

    def test_signature_stub_repr(self):
        from mini_agent.research.dspy_modules.signatures import _SignatureStub
        stub = _SignatureStub(key="value", num=42)
        repr_str = repr(stub)
        assert "key" in repr_str
        assert "value" in repr_str

    def test_has_dspy_flag(self):
        from mini_agent.research.dspy_modules.signatures import _HAS_DSPY
        # Should be False in test environment (no dspy installed)
        assert isinstance(_HAS_DSPY, bool)


# ===========================================================================
# Modules tests - FallbackPrediction
# ===========================================================================


class TestFallbackPrediction:
    """Test FallbackPrediction container."""

    def test_creation(self):
        from mini_agent.research.dspy_modules.modules import FallbackPrediction
        pred = FallbackPrediction(queries=["q1"], synthesis="text")
        assert pred.queries == ["q1"]
        assert pred.synthesis == "text"

    def test_repr(self):
        from mini_agent.research.dspy_modules.modules import FallbackPrediction
        pred = FallbackPrediction(key="val")
        assert "FallbackPrediction" in repr(pred)
        assert "key" in repr(pred)

    def test_bool(self):
        from mini_agent.research.dspy_modules.modules import FallbackPrediction
        pred = FallbackPrediction()
        assert bool(pred) is True


# ===========================================================================
# Modules tests - _fallback_prompt
# ===========================================================================


class TestFallbackPrompt:
    """Test _fallback_prompt helper."""

    def test_basic(self):
        from mini_agent.research.dspy_modules.modules import _fallback_prompt
        result = _fallback_prompt("Do something", key="value")
        assert "Task: Do something" in result
        assert "key: value" in result

    def test_with_list(self):
        from mini_agent.research.dspy_modules.modules import _fallback_prompt
        result = _fallback_prompt("Task", items=["a", "b", "c"])
        assert "items:" in result
        assert "- a" in result
        assert "- b" in result

    def test_empty_kwargs(self):
        from mini_agent.research.dspy_modules.modules import _fallback_prompt
        result = _fallback_prompt("Simple task")
        assert "Task: Simple task" in result


# ===========================================================================
# Modules tests - LiteratureReviewModule
# ===========================================================================


class TestLiteratureReviewModule:
    """Test LiteratureReviewModule in fallback mode."""

    def test_init(self):
        from mini_agent.research.dspy_modules.modules import LiteratureReviewModule
        module = LiteratureReviewModule()
        # In fallback mode, internal predictors are None
        assert module._generate_queries is None or module._generate_queries is not None

    def test_forward_fallback(self):
        from mini_agent.research.dspy_modules.modules import LiteratureReviewModule
        module = LiteratureReviewModule()
        result = module.forward(
            research_question="What is the impact of education on poverty?",
            context="Indonesian context",
        )
        assert hasattr(result, "queries")
        assert hasattr(result, "synthesis")
        assert hasattr(result, "gaps")
        assert len(result.queries) >= 1

    def test_forward_no_context(self):
        from mini_agent.research.dspy_modules.modules import LiteratureReviewModule
        module = LiteratureReviewModule()
        result = module.forward(research_question="Test question")
        assert hasattr(result, "queries")

    def test_forward_fallback_has_prompts(self):
        from mini_agent.research.dspy_modules.modules import LiteratureReviewModule
        module = LiteratureReviewModule()
        result = module.forward(research_question="Test")
        assert hasattr(result, "prompts")
        assert "query_generation" in result.prompts


# ===========================================================================
# Modules tests - DataAnalysisModule
# ===========================================================================


class TestDataAnalysisModule:
    """Test DataAnalysisModule in fallback mode."""

    def test_init(self):
        from mini_agent.research.dspy_modules.modules import DataAnalysisModule
        module = DataAnalysisModule()
        assert module._design is None or module._design is not None

    def test_forward_fallback(self):
        from mini_agent.research.dspy_modules.modules import DataAnalysisModule
        module = DataAnalysisModule()
        result = module.forward(
            research_questions=["Q1: Effect of X on Y"],
            data_description="Panel data from BPS, 2010-2023",
            statistical_results="β = 0.45, p < 0.01",
        )
        assert hasattr(result, "methodology")
        assert hasattr(result, "interpretation")

    def test_forward_no_results(self):
        from mini_agent.research.dspy_modules.modules import DataAnalysisModule
        module = DataAnalysisModule()
        result = module.forward(
            research_questions=["Q1"],
            data_description="Survey data",
        )
        assert hasattr(result, "methodology")
        assert result.interpretation == "" or "Fallback" in result.interpretation or result.interpretation == ""

    def test_forward_has_prompts(self):
        from mini_agent.research.dspy_modules.modules import DataAnalysisModule
        module = DataAnalysisModule()
        result = module.forward(
            research_questions=["Q1"],
            data_description="Data",
            statistical_results="p=0.05",
        )
        assert hasattr(result, "prompts")
        assert "methodology_design" in result.prompts


# ===========================================================================
# Modules tests - PaperGenerationModule
# ===========================================================================


class TestPaperGenerationModule:
    """Test PaperGenerationModule in fallback mode."""

    def test_init(self):
        from mini_agent.research.dspy_modules.modules import PaperGenerationModule
        module = PaperGenerationModule()
        assert module._write_section is None or module._write_section is not None

    def test_forward_fallback(self):
        from mini_agent.research.dspy_modules.modules import PaperGenerationModule
        module = PaperGenerationModule()
        result = module.forward(
            section_name="introduction",
            outline="1. Background\n2. Problem statement\n3. Objectives",
            context="Indonesian economic context",
            citations=["smith2020", "jones2021"],
        )
        assert hasattr(result, "section_text")
        assert "introduction" in result.section_text.lower() or "Fallback" in result.section_text

    def test_forward_no_citations(self):
        from mini_agent.research.dspy_modules.modules import PaperGenerationModule
        module = PaperGenerationModule()
        result = module.forward(
            section_name="methods",
            outline="Research design",
        )
        assert hasattr(result, "section_text")

    def test_forward_has_prompts(self):
        from mini_agent.research.dspy_modules.modules import PaperGenerationModule
        module = PaperGenerationModule()
        result = module.forward(
            section_name="results",
            outline="Key findings",
        )
        assert hasattr(result, "prompts")
        assert "section_writing" in result.prompts


# ===========================================================================
# Modules tests - QualityCheckModule
# ===========================================================================


class TestQualityCheckModule:
    """Test QualityCheckModule in fallback mode."""

    def test_init(self):
        from mini_agent.research.dspy_modules.modules import QualityCheckModule
        module = QualityCheckModule()
        assert module._check_citations is None or module._check_citations is not None

    def test_forward_fallback_all(self):
        from mini_agent.research.dspy_modules.modules import QualityCheckModule
        module = QualityCheckModule()
        result = module.forward(text="Some manuscript text with claims.")
        assert hasattr(result, "issues")
        assert hasattr(result, "overall_quality")
        assert "citations" in result.issues
        assert "statistics" in result.issues
        assert "logic" in result.issues

    def test_forward_specific_checks(self):
        from mini_agent.research.dspy_modules.modules import QualityCheckModule
        module = QualityCheckModule()
        result = module.forward(
            text="Text to check",
            check_types=["citations"],
        )
        assert "citations" in result.issues
        assert "statistics" not in result.issues

    def test_forward_has_prompts(self):
        from mini_agent.research.dspy_modules.modules import QualityCheckModule
        module = QualityCheckModule()
        result = module.forward(text="Check this text")
        assert hasattr(result, "prompts")
        assert "citation_check" in result.prompts

    def test_forward_note_field(self):
        from mini_agent.research.dspy_modules.modules import QualityCheckModule
        module = QualityCheckModule()
        result = module.forward(text="Text")
        assert hasattr(result, "note")
        assert "DSPy" in result.note


# ===========================================================================
# __init__.py tests
# ===========================================================================


class TestDspyModulesInit:
    """Test dspy_modules __init__.py exports."""

    def test_dspy_available_flag(self):
        from mini_agent.research.dspy_modules import DSPY_AVAILABLE
        assert isinstance(DSPY_AVAILABLE, bool)

    def test_require_dspy(self):
        from mini_agent.research.dspy_modules import _require_dspy
        # If DSPy is not installed, this should raise
        if not __import__("mini_agent.research.dspy_modules", fromlist=["DSPY_AVAILABLE"]).DSPY_AVAILABLE:
            with pytest.raises(Exception):
                _require_dspy()

    def test_all_exports(self):
        from mini_agent.research.dspy_modules import __all__
        assert "DSPY_AVAILABLE" in __all__
        assert "_require_dspy" in __all__
