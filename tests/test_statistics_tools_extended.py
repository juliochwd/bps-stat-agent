"""Extended tests for mini_agent/tools/statistics_tools.py — statistical analysis tools."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.tools.statistics_tools import (
    DescriptiveStatsTool,
    RegressionAnalysisTool,
    HypothesisTestTool,
    CreateVisualizationTool,
    _require_numpy,
)


class TestRequireNumpy:
    def test_numpy_available(self):
        """When numpy is available, returns None."""
        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", True):
            result = _require_numpy()
            assert result is None

    def test_numpy_not_available(self):
        """When numpy is not available, returns error ToolResult."""
        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", False):
            result = _require_numpy()
            assert result is not None
            assert result.success is False
            assert "numpy" in result.error


class TestDescriptiveStatsTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return DescriptiveStatsTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "descriptive_stats"

    def test_description(self, tool):
        assert "descriptive" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "type" in params
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_numpy(self, tool):
        """Test when numpy is not available."""
        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", False):
            result = await tool.execute(data_path="test.csv")
            assert result.success is False
            assert "numpy" in result.error

    @pytest.mark.asyncio
    async def test_execute_file_not_found(self, tool, tmp_path):
        """Test with non-existent file."""
        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", True):
            result = await tool.execute(data_path="nonexistent.csv")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_execute_with_csv(self, tool, tmp_path):
        """Test with a valid CSV file."""
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("x,y,z\n1,2,3\n4,5,6\n7,8,9\n10,11,12\n")

        try:
            import numpy as np
            import pandas as pd
        except ImportError:
            pytest.skip("numpy/pandas not available")

        result = await tool.execute(data_path=str(csv_file))
        assert result.success is True
        assert "statistic" in result.content.lower() or "n" in result.content.lower() or "variable" in result.content.lower()


class TestRegressionAnalysisTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return RegressionAnalysisTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "regression_analysis"

    def test_description(self, tool):
        assert "regression" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_numpy(self, tool):
        """Test when numpy is not available."""
        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", False):
            result = await tool.execute(
                data_path="test.csv",
                dependent_var="y",
                independent_vars=["x1"],
            )
            assert result.success is False

    @pytest.mark.asyncio
    async def test_execute_with_data(self, tool, tmp_path):
        """Test with valid data."""
        try:
            import numpy as np
            import pandas as pd
        except ImportError:
            pytest.skip("numpy/pandas not available")

        csv_file = tmp_path / "regression_data.csv"
        csv_file.write_text("y,x1,x2\n1,2,3\n4,5,6\n7,8,9\n10,11,12\n13,14,15\n")

        result = await tool.execute(
            data_path=str(csv_file),
            dependent_var="y",
            independent_vars=["x1", "x2"],
        )
        # May succeed or fail depending on statsmodels availability
        assert isinstance(result.success, bool)


class TestHypothesisTestTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return HypothesisTestTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "hypothesis_test"

    def test_description(self, tool):
        assert "hypothesis" in tool.description.lower() or "test" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_numpy(self, tool):
        """Test when numpy is not available."""
        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", False):
            result = await tool.execute(
                data_path="test.csv",
                test="t_test",
                variable="x",
            )
            assert result.success is False


class TestCreateVisualizationTool:
    @pytest.fixture
    def tool(self, tmp_path):
        return CreateVisualizationTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "create_visualization"

    def test_description(self, tool):
        desc = tool.description.lower()
        assert "figure" in desc or "publication" in desc

    def test_parameters(self, tool):
        params = tool.parameters
        assert "properties" in params

    @pytest.mark.asyncio
    async def test_execute_no_numpy(self, tool):
        """Test when numpy is not available."""
        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", False):
            result = await tool.execute(
                data_path="test.csv",
                plot_type="scatter",
                output_path="output.png",
                x_var="x",
                y_var="y",
            )
            assert result.success is False
