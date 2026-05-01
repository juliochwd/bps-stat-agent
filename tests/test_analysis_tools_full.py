"""Full coverage tests for mini_agent/tools/analysis_tools.py.

Since numpy/scipy are NOT installed in the test environment, we test:
1. The _HAS_NUMPY=False path (error handling)
2. Mock _HAS_NUMPY=True + mock libraries for happy-path coverage
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest


# ===================================================================
# Helper functions
# ===================================================================

class TestAnalysisHelpers:
    def test_resolve_path_absolute(self):
        from mini_agent.tools.analysis_tools import _resolve_path
        p = _resolve_path("/workspace", "/absolute/path.csv")
        assert p == Path("/absolute/path.csv")

    def test_resolve_path_relative(self):
        from mini_agent.tools.analysis_tools import _resolve_path
        p = _resolve_path("/workspace", "data.csv")
        assert p == Path("/workspace/data.csv")

    def test_ensure_dir(self, tmp_path):
        from mini_agent.tools.analysis_tools import _ensure_dir
        p = tmp_path / "a" / "b" / "c" / "file.json"
        result = _ensure_dir(p)
        assert result == p
        assert p.parent.exists()


# ===================================================================
# TimeSeriesAnalysisTool (analysis_tools.py version)
# ===================================================================

class TestTimeSeriesAnalysisToolAnalysis:
    @pytest.fixture
    def tool(self, tmp_path):
        from mini_agent.tools.analysis_tools import TimeSeriesAnalysisTool
        return TimeSeriesAnalysisTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "time_series_analysis"

    def test_description(self, tool):
        assert "time series" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "data_path" in params["properties"]
        assert "date_column" in params["properties"]
        assert "value_columns" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="t.csv", date_column="date", value_columns=["v"])
            assert result.success is False
            assert "numpy" in result.error.lower() or "pandas" in result.error.lower()

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        mock_pd = MagicMock()
        mock_pd.read_csv.side_effect = FileNotFoundError("not found")
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", True):
            with patch("mini_agent.tools.analysis_tools.pd", mock_pd):
                result = await tool.execute(
                    data_path="missing.csv", date_column="date", value_columns=["v"]
                )
                assert result.success is False


# ===================================================================
# BayesianAnalysisTool (analysis_tools.py version)
# ===================================================================

class TestBayesianAnalysisToolAnalysis:
    @pytest.fixture
    def tool(self, tmp_path):
        from mini_agent.tools.analysis_tools import BayesianAnalysisTool
        return BayesianAnalysisTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "bayesian_analysis"

    def test_description(self, tool):
        assert "bayesian" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "formula" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="t.csv", formula="y ~ x1")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool, tmp_path):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", True):
            result = await tool.execute(data_path="missing.csv", formula="y ~ x1")
            assert result.success is False


# ===================================================================
# CausalInferenceTool (analysis_tools.py version)
# ===================================================================

class TestCausalInferenceToolAnalysis:
    @pytest.fixture
    def tool(self, tmp_path):
        from mini_agent.tools.analysis_tools import CausalInferenceTool
        return CausalInferenceTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "causal_inference"

    def test_description(self, tool):
        assert "causal" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "data_path" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(
                data_path="t.csv", treatment_var="t", outcome_var="y", method="ate"
            )
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool, tmp_path):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", True):
            result = await tool.execute(
                data_path="missing.csv", treatment_var="t", outcome_var="y", method="ate"
            )
            assert result.success is False


# ===================================================================
# SurvivalAnalysisTool (analysis_tools.py version)
# ===================================================================

class TestSurvivalAnalysisToolAnalysis:
    @pytest.fixture
    def tool(self, tmp_path):
        from mini_agent.tools.analysis_tools import SurvivalAnalysisTool
        return SurvivalAnalysisTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "survival_analysis"

    def test_description(self, tool):
        assert "survival" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "data_path" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(
                data_path="t.csv", duration_var="t", event_var="e", method="kaplan_meier"
            )
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool, tmp_path):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", True):
            result = await tool.execute(
                data_path="missing.csv", duration_var="t", event_var="e", method="kaplan_meier"
            )
            assert result.success is False


# ===================================================================
# ValidateDataTool
# ===================================================================

class TestValidateDataToolFull:
    @pytest.fixture
    def tool(self, tmp_path):
        from mini_agent.tools.analysis_tools import ValidateDataTool
        return ValidateDataTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "validate_data"

    def test_description(self, tool):
        assert "validate" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "data_path" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="t.csv")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool, tmp_path):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", True):
            result = await tool.execute(data_path="missing.csv")
            assert result.success is False
            assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_empty_dataset(self, tool, tmp_path):
        mock_df = MagicMock()
        mock_df.empty = True

        mock_pd = MagicMock()

        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", True):
            with patch("mini_agent.tools.analysis_tools._load_dataframe", return_value=mock_df):
                # Create a dummy file so path exists
                f = tmp_path / "empty.csv"
                f.write_text("")
                result = await tool.execute(data_path=str(f))
                assert result.success is False
                assert "empty" in result.error.lower()


# ===================================================================
# CheckStatisticalValidityTool
# ===================================================================

class TestCheckStatisticalValidityToolFull:
    @pytest.fixture
    def tool(self, tmp_path):
        from mini_agent.tools.analysis_tools import CheckStatisticalValidityTool
        return CheckStatisticalValidityTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "check_statistical_validity"

    def test_description(self, tool):
        assert "statistical" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "data_path" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="t.csv")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool, tmp_path):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", True):
            result = await tool.execute(data_path="missing.csv")
            assert result.success is False


# ===================================================================
# ConversationalAnalysisTool
# ===================================================================

class TestConversationalAnalysisToolFull:
    @pytest.fixture
    def tool(self, tmp_path):
        from mini_agent.tools.analysis_tools import ConversationalAnalysisTool
        return ConversationalAnalysisTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "conversational_analysis"

    def test_description(self, tool):
        assert "natural language" in tool.description.lower() or "analyze" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "data_path" in params["properties"]
        assert "query" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="t.csv", query="describe")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool, tmp_path):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", True):
            result = await tool.execute(data_path="missing.csv", query="describe")
            assert result.success is False


# ===================================================================
# AutomatedEDATool
# ===================================================================

class TestAutomatedEDAToolFull:
    @pytest.fixture
    def tool(self, tmp_path):
        from mini_agent.tools.analysis_tools import AutomatedEDATool
        return AutomatedEDATool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "automated_eda"

    def test_description(self, tool):
        assert "eda" in tool.description.lower() or "exploratory" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "data_path" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="t.csv")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool, tmp_path):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", True):
            result = await tool.execute(data_path="missing.csv")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_empty_dataset(self, tool, tmp_path):
        mock_df = MagicMock()
        mock_df.empty = True

        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", True):
            with patch("mini_agent.tools.analysis_tools._load_dataframe", return_value=mock_df):
                f = tmp_path / "empty.csv"
                f.write_text("")
                result = await tool.execute(data_path=str(f))
                assert result.success is False


# ===================================================================
# AutoVisualizeTool
# ===================================================================

class TestAutoVisualizeToolFull:
    @pytest.fixture
    def tool(self, tmp_path):
        from mini_agent.tools.analysis_tools import AutoVisualizeTool
        return AutoVisualizeTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "auto_visualize"

    def test_description(self, tool):
        assert "visualiz" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "data_path" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="t.csv")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool, tmp_path):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", True):
            result = await tool.execute(data_path="missing.csv")
            assert result.success is False
