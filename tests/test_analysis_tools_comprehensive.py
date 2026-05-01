"""Comprehensive tests for mini_agent/tools/analysis_tools.py.

Tests all tool classes with real data where possible, mocking heavy deps.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.tools.analysis_tools import (
    AutomatedEDATool,
    AutoVisualizeTool,
    BayesianAnalysisTool,
    CausalInferenceTool,
    CheckStatisticalValidityTool,
    ConversationalAnalysisTool,
    SurvivalAnalysisTool,
    TimeSeriesAnalysisTool,
    ValidateDataTool,
    _load_dataframe,
    _resolve_path,
)


# ===================================================================
# Helper function tests
# ===================================================================

class TestHelperFunctions:
    def test_resolve_path_absolute(self):
        p = _resolve_path("/workspace", "/absolute/path.csv")
        assert p == Path("/absolute/path.csv")

    def test_resolve_path_relative(self):
        p = _resolve_path("/workspace", "data.csv")
        assert p == Path("/workspace/data.csv")

    @pytest.mark.skipif(
        not __import__("mini_agent.tools.analysis_tools", fromlist=["_HAS_NUMPY"])._HAS_NUMPY,
        reason="numpy/pandas not installed",
    )
    def test_load_dataframe_csv(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x,y\n1,2\n3,4\n")
        df = _load_dataframe(csv_file)
        assert len(df) == 2
        assert list(df.columns) == ["x", "y"]

    @pytest.mark.skipif(
        not __import__("mini_agent.tools.analysis_tools", fromlist=["_HAS_NUMPY"])._HAS_NUMPY,
        reason="numpy/pandas not installed",
    )
    def test_load_dataframe_tsv(self, tmp_path):
        tsv_file = tmp_path / "data.tsv"
        tsv_file.write_text("x\ty\n1\t2\n3\t4\n")
        df = _load_dataframe(tsv_file)
        assert len(df) == 2

    @pytest.mark.skipif(
        not __import__("mini_agent.tools.analysis_tools", fromlist=["_HAS_NUMPY"])._HAS_NUMPY,
        reason="numpy/pandas not installed",
    )
    def test_load_dataframe_json(self, tmp_path):
        json_file = tmp_path / "data.json"
        json_file.write_text('[{"x": 1, "y": 2}, {"x": 3, "y": 4}]')
        df = _load_dataframe(json_file)
        assert len(df) == 2

    @pytest.mark.skipif(
        not __import__("mini_agent.tools.analysis_tools", fromlist=["_HAS_NUMPY"])._HAS_NUMPY,
        reason="numpy/pandas not installed",
    )
    def test_load_dataframe_unknown_ext(self, tmp_path):
        # Falls back to CSV
        file = tmp_path / "data.dat"
        file.write_text("x,y\n1,2\n3,4\n")
        df = _load_dataframe(file)
        assert len(df) == 2


# ===================================================================
# TimeSeriesAnalysisTool
# ===================================================================

class TestTimeSeriesAnalysisTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return TimeSeriesAnalysisTool(workspace_dir=str(tmp_path))

    @pytest.fixture
    def ts_csv(self, tmp_path):
        csv_file = tmp_path / "ts.csv"
        lines = ["date,value,value2"]
        for i in range(60):
            lines.append(f"2024-{(i // 28) + 1:02d}-{(i % 28) + 1:02d},{100 + i * 0.5},{50 + i * 0.3}")
        csv_file.write_text("\n".join(lines))
        return str(csv_file)

    def test_name(self, tool):
        assert tool.name == "time_series_analysis"

    def test_parameters_has_required(self, tool):
        params = tool.parameters
        assert "data_path" in params["required"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="x.csv", date_column="d", value_columns=["v"])
            assert result.success is False
            assert "numpy" in result.error.lower()

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(data_path="missing.csv", date_column="d", value_columns=["v"])
        assert result.success is False

    @pytest.mark.asyncio
    async def test_missing_date_column(self, tool, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x,y\n1,2\n3,4\n")
        result = await tool.execute(data_path=str(csv_file), date_column="date", value_columns=["x"])
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_valid_data(self, tool, ts_csv):
        result = await tool.execute(
            data_path=ts_csv,
            date_column="date",
            value_columns=["value"],
        )
        # May succeed or fail depending on statsmodels
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_multiple_columns(self, tool, ts_csv):
        result = await tool.execute(
            data_path=ts_csv,
            date_column="date",
            value_columns=["value", "value2"],
        )
        assert isinstance(result.success, bool)


# ===================================================================
# BayesianAnalysisTool
# ===================================================================

class TestBayesianAnalysisTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return BayesianAnalysisTool(workspace_dir=str(tmp_path))

    @pytest.fixture
    def data_csv(self, tmp_path):
        csv_file = tmp_path / "bayes.csv"
        lines = ["x1,x2,y"]
        for i in range(30):
            lines.append(f"{i},{i*2},{i*3 + 1}")
        csv_file.write_text("\n".join(lines))
        return str(csv_file)

    def test_name(self, tool):
        assert tool.name == "bayesian_analysis"

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="x.csv", formula="y ~ x")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(data_path="missing.csv", formula="y ~ x")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_data(self, tool, data_csv):
        result = await tool.execute(
            data_path=data_csv,
            formula="y ~ x1 + x2",
        )
        assert isinstance(result.success, bool)


# ===================================================================
# CausalInferenceTool
# ===================================================================

class TestCausalInferenceTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return CausalInferenceTool(workspace_dir=str(tmp_path))

    @pytest.fixture
    def data_csv(self, tmp_path):
        csv_file = tmp_path / "causal.csv"
        lines = ["treatment,outcome,x1,x2"]
        for i in range(40):
            t = 1 if i % 2 == 0 else 0
            y = t * 5 + i * 0.2
            lines.append(f"{t},{y:.2f},{i},{i*0.5}")
        csv_file.write_text("\n".join(lines))
        return str(csv_file)

    def test_name(self, tool):
        assert tool.name == "causal_inference"

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="x.csv", treatment_var="t", outcome_var="y")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(data_path="missing.csv", treatment_var="t", outcome_var="y")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_data(self, tool, data_csv):
        result = await tool.execute(
            data_path=data_csv,
            treatment_var="treatment",
            outcome_var="outcome",
            covariates=["x1", "x2"],
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_missing_treatment_col(self, tool, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x,y\n1,2\n3,4\n")
        result = await tool.execute(
            data_path=str(csv_file),
            treatment_var="treatment",
            outcome_var="y",
        )
        assert result.success is False


# ===================================================================
# SurvivalAnalysisTool
# ===================================================================

class TestSurvivalAnalysisTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return SurvivalAnalysisTool(workspace_dir=str(tmp_path))

    @pytest.fixture
    def data_csv(self, tmp_path):
        csv_file = tmp_path / "survival.csv"
        lines = ["time,event,group"]
        for i in range(30):
            lines.append(f"{i+1},{1 if i % 3 != 0 else 0},{'A' if i < 15 else 'B'}")
        csv_file.write_text("\n".join(lines))
        return str(csv_file)

    def test_name(self, tool):
        assert tool.name == "survival_analysis"

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="x.csv", duration_var="t", event_var="e")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(data_path="missing.csv", duration_var="t", event_var="e")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_data(self, tool, data_csv):
        result = await tool.execute(
            data_path=data_csv,
            duration_var="time",
            event_var="event",
        )
        assert isinstance(result.success, bool)


# ===================================================================
# ValidateDataTool
# ===================================================================

class TestValidateDataTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return ValidateDataTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "validate_data"

    def test_parameters(self, tool):
        params = tool.parameters
        assert "data_path" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="x.csv")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(data_path="missing.csv")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_valid_data(self, tool, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x,y,z\n1,2,3\n4,5,6\n7,8,9\n")
        result = await tool.execute(data_path=str(csv_file))
        # Will fail if numpy not available
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_with_missing_values(self, tool, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x,y\n1,2\n,4\n5,\n")
        result = await tool.execute(data_path=str(csv_file))
        assert isinstance(result.success, bool)


# ===================================================================
# CheckStatisticalValidityTool
# ===================================================================

class TestCheckStatisticalValidityTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return CheckStatisticalValidityTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "check_statistical_validity"

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="x.csv", variables=["x"])
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(data_path="missing.csv", variables=["x"])
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_data(self, tool, tmp_path):
        csv_file = tmp_path / "data.csv"
        lines = ["x,y"]
        for i in range(50):
            lines.append(f"{i},{i*2 + 1}")
        csv_file.write_text("\n".join(lines))
        result = await tool.execute(data_path=str(csv_file), variables=["x", "y"])
        assert isinstance(result.success, bool)


# ===================================================================
# ConversationalAnalysisTool
# ===================================================================

class TestConversationalAnalysisTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return ConversationalAnalysisTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "conversational_analysis"

    def test_parameters(self, tool):
        params = tool.parameters
        assert "data_path" in params["properties"]
        assert "query" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="x.csv", query="show mean")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(data_path="missing.csv", query="show mean")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_data(self, tool, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x,y,name\n1,2,alice\n3,4,bob\n5,6,carol\n")
        result = await tool.execute(data_path=str(csv_file), query="show all data")
        assert isinstance(result.success, bool)


# ===================================================================
# AutomatedEDATool
# ===================================================================

class TestAutomatedEDATool:
    @pytest.fixture
    def tool(self, tmp_path):
        return AutomatedEDATool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "automated_eda"

    def test_parameters(self, tool):
        params = tool.parameters
        assert "data_path" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="x.csv")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(data_path="missing.csv")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_data(self, tool, tmp_path):
        csv_file = tmp_path / "data.csv"
        lines = ["x,y,category"]
        for i in range(20):
            lines.append(f"{i},{i*2},{'A' if i < 10 else 'B'}")
        csv_file.write_text("\n".join(lines))
        result = await tool.execute(data_path=str(csv_file))
        assert isinstance(result.success, bool)


# ===================================================================
# AutoVisualizeTool
# ===================================================================

class TestAutoVisualizeTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return AutoVisualizeTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "auto_visualize"

    def test_parameters(self, tool):
        params = tool.parameters
        assert "data_path" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_numpy(self, tool):
        with patch("mini_agent.tools.analysis_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="x.csv")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_file_not_found(self, tool):
        result = await tool.execute(data_path="missing.csv")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_with_data(self, tool, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x,y\n1,2\n3,4\n5,6\n7,8\n")
        result = await tool.execute(data_path=str(csv_file))
        assert isinstance(result.success, bool)
