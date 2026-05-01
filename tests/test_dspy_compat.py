"""Tests for mini_agent/research/_dspy_compat.py.

Tests DSPy compatibility layer including stubs, optimizer, and tool classes.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from mini_agent.research._dspy_compat import (
    DSPY_AVAILABLE,
    DSPyOptimizer,
    DSPyOptimizeTool,
    LiteLLMConfigTool,
    _require_dspy,
)


class TestRequireDspy:
    def test_raises_when_dspy_not_available(self):
        with patch("mini_agent.research._dspy_compat.DSPY_AVAILABLE", False):
            from mini_agent.research.exceptions import DependencyMissingError
            with pytest.raises(DependencyMissingError):
                _require_dspy()

    @pytest.mark.skipif(not DSPY_AVAILABLE, reason="DSPy not installed")
    def test_no_raise_when_available(self):
        _require_dspy()  # Should not raise


class TestDSPyStubs:
    """Test stub classes when DSPy is not installed."""

    def test_stubs_exist(self):
        from mini_agent.research._dspy_compat import (
            GenerateSearchQueries,
            AssessRelevance,
            ExtractEvidence,
            SynthesizeEvidence,
            PlanAnalysis,
            InterpretResults,
            WriteSectionDraft,
            LiteratureReviewModule,
            StatisticalAnalysisModule,
        )
        # These should be importable regardless of DSPy availability
        assert GenerateSearchQueries is not None
        assert AssessRelevance is not None
        assert ExtractEvidence is not None
        assert SynthesizeEvidence is not None
        assert PlanAnalysis is not None
        assert InterpretResults is not None
        assert WriteSectionDraft is not None
        assert LiteratureReviewModule is not None
        assert StatisticalAnalysisModule is not None

    @pytest.mark.skipif(DSPY_AVAILABLE, reason="DSPy is installed, stubs not active")
    def test_stubs_raise_on_instantiation(self):
        from mini_agent.research._dspy_compat import LiteratureReviewModule
        from mini_agent.research.exceptions import DependencyMissingError
        with pytest.raises(DependencyMissingError):
            LiteratureReviewModule()


class TestDSPyOptimizer:
    def test_init_raises_without_dspy(self):
        with patch("mini_agent.research._dspy_compat.DSPY_AVAILABLE", False):
            from mini_agent.research.exceptions import DependencyMissingError
            with pytest.raises(DependencyMissingError):
                DSPyOptimizer(strategy="bootstrap_few_shot")

    @pytest.mark.skipif(not DSPY_AVAILABLE, reason="DSPy not installed")
    def test_init_with_dspy(self):
        opt = DSPyOptimizer(strategy="bootstrap_few_shot")
        assert opt.strategy == "bootstrap_few_shot"

    @pytest.mark.skipif(not DSPY_AVAILABLE, reason="DSPy not installed")
    def test_invalid_strategy(self):
        opt = DSPyOptimizer(strategy="invalid_strategy")
        with pytest.raises(ValueError, match="Unknown optimization strategy"):
            opt.optimize(
                module=MagicMock(),
                trainset=[],
                metric=lambda e, p: 1.0,
            )


class TestLiteLLMConfigTool:
    @pytest.fixture
    def tool(self):
        return LiteLLMConfigTool()

    def test_name(self, tool):
        assert tool.name == "litellm_config"

    def test_description(self, tool):
        assert "routing" in tool.description.lower() or "model" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "action" in params["properties"]
        assert "action" in params["required"]

    @pytest.mark.asyncio
    async def test_status_action(self, tool):
        result = await tool.execute(action="status")
        assert result.success is True
        assert "Routing" in result.content

    @pytest.mark.asyncio
    async def test_set_model_action(self, tool):
        result = await tool.execute(action="set_model", task_type="test_task", model="gpt-4")
        assert result.success is True
        assert "test_task" in result.content

    @pytest.mark.asyncio
    async def test_set_model_missing_params(self, tool):
        result = await tool.execute(action="set_model")
        assert result.success is False
        assert "required" in result.error.lower()

    @pytest.mark.asyncio
    async def test_unknown_action(self, tool):
        result = await tool.execute(action="unknown")
        assert result.success is False


class TestDSPyOptimizeTool:
    @pytest.fixture
    def tool(self):
        return DSPyOptimizeTool()

    def test_name(self, tool):
        assert tool.name == "dspy_optimize"

    def test_description(self, tool):
        assert "optimize" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "module_name" in params["properties"]
        assert "trainset_path" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_dspy(self, tool):
        with patch("mini_agent.research._dspy_compat.DSPY_AVAILABLE", False):
            result = await tool.execute(
                module_name="literature_review",
                trainset_path="/tmp/train.json",
            )
            assert result.success is False

    @pytest.mark.asyncio
    async def test_trainset_not_found(self, tool):
        result = await tool.execute(
            module_name="literature_review",
            trainset_path="/nonexistent/train.json",
        )
        # Either fails due to no dspy or file not found
        assert result.success is False


class TestDSPyAvailabilityFlag:
    def test_dspy_available_is_bool(self):
        assert isinstance(DSPY_AVAILABLE, bool)


class TestLiteLLMConfigToolExtended:
    @pytest.fixture
    def tool(self):
        return LiteLLMConfigTool()

    @pytest.mark.asyncio
    async def test_set_model_new_task_type(self, tool):
        result = await tool.execute(action="set_model", task_type="new_task", model="claude-3")
        assert result.success is True
        assert "new_task" in result.content

    @pytest.mark.asyncio
    async def test_set_model_existing_task_type(self, tool):
        # First set it
        await tool.execute(action="set_model", task_type="test_type", model="gpt-4")
        # Then update it
        result = await tool.execute(action="set_model", task_type="test_type", model="gpt-4o")
        assert result.success is True
