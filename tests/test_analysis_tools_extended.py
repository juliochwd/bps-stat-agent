"""Extended tests for mini_agent/tools/analysis_tools.py — advanced analysis tools."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.tools.analysis_tools import (
    AutomatedEDATool,
    BayesianAnalysisTool,
    CausalInferenceTool,
    CheckStatisticalValidityTool,
    ConversationalAnalysisTool,
    SurvivalAnalysisTool,
    TimeSeriesAnalysisTool,
    ValidateDataTool,
)


class TestTimeSeriesAnalysisTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return TimeSeriesAnalysisTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "time_series_analysis"

    def test_description(self, tool):
        assert "time series" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params
        assert "required" in params

    @pytest.mark.asyncio
    async def test_execute_no_deps(self, tool):
        """Test when dependencies are not available."""
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(
                data_path="test.csv",
                date_column="date",
                value_columns=["value"],
            )
            assert result.success is False


class TestBayesianAnalysisTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return BayesianAnalysisTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "bayesian_analysis"

    def test_description(self, tool):
        assert "bayesian" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_deps(self, tool):
        """Test when dependencies are not available."""
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(
                data_path="test.csv",
                formula="y ~ x1 + x2",
            )
            assert result.success is False


class TestCausalInferenceTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return CausalInferenceTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "causal_inference"

    def test_description(self, tool):
        assert "causal" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_deps(self, tool):
        """Test when dependencies are not available."""
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(
                data_path="test.csv",
                method="did",
                treatment_var="treatment",
                outcome_var="outcome",
            )
            assert result.success is False


class TestSurvivalAnalysisTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return SurvivalAnalysisTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "survival_analysis"

    def test_description(self, tool):
        assert "survival" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_deps(self, tool):
        """Test when dependencies are not available."""
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(
                data_path="test.csv",
                duration_var="time",
                event_var="event",
            )
            assert result.success is False


class TestValidateDataTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return ValidateDataTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "validate_data"

    def test_description(self, tool):
        assert "validate" in tool.description.lower() or "data" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_deps(self, tool):
        """Test when dependencies are not available."""
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="test.csv")
            assert result.success is False


class TestCheckStatisticalValidityTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return CheckStatisticalValidityTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "check_statistical_validity"

    def test_description(self, tool):
        assert "statistical" in tool.description.lower() or "validity" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_deps(self, tool):
        """Test when dependencies are not available."""
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="results.json")
            assert result.success is False


class TestConversationalAnalysisTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return ConversationalAnalysisTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "conversational_analysis"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "analyze" in desc or "natural language" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_deps(self, tool):
        """Test when dependencies are not available."""
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(
                data_path="test.csv",
                query="What is the mean?",
            )
            assert result.success is False


class TestAutomatedEDATool:
    @pytest.fixture
    def tool(self, tmp_path):
        return AutomatedEDATool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "automated_eda"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "eda" in desc or "exploratory" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_deps(self, tool):
        """Test when dependencies are not available."""
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="test.csv")
            assert result.success is False
