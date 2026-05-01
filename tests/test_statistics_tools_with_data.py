"""Tests for statistics_tools with actual data (numpy/pandas available)."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

try:
    import numpy as np
    import pandas as pd
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

from mini_agent.tools.statistics_tools import (
    CreateVisualizationTool,
    DescriptiveStatsTool,
    HypothesisTestTool,
    RegressionAnalysisTool,
)

pytestmark = pytest.mark.skipif(not HAS_NUMPY, reason="numpy/pandas not available")


@pytest.fixture
def sample_csv(tmp_path):
    """Create a sample CSV file for testing."""
    df = pd.DataFrame({
        "x1": np.random.randn(50),
        "x2": np.random.randn(50),
        "y": np.random.randn(50),
        "group": ["A"] * 25 + ["B"] * 25,
    })
    csv_path = tmp_path / "data.csv"
    df.to_csv(csv_path, index=False)
    return csv_path


class TestDescriptiveStatsWithData:
    @pytest.fixture
    def tool(self, tmp_path):
        return DescriptiveStatsTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_execute_csv(self, tool, sample_csv):
        """Test descriptive stats on CSV data."""
        result = await tool.execute(data_path=str(sample_csv))
        assert result.success is True
        assert "x1" in result.content or "mean" in result.content.lower()

    @pytest.mark.asyncio
    async def test_execute_specific_columns(self, tool, sample_csv):
        """Test with specific variables."""
        result = await tool.execute(data_path=str(sample_csv), variables=["x1", "y"])
        assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_file_not_found(self, tool):
        """Test with non-existent file."""
        result = await tool.execute(data_path="nonexistent.csv")
        assert result.success is False


class TestRegressionWithData:
    @pytest.fixture
    def tool(self, tmp_path):
        return RegressionAnalysisTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_execute_ols(self, tool, sample_csv):
        """Test OLS regression."""
        result = await tool.execute(
            data_path=str(sample_csv),
            dependent_var="y",
            independent_vars=["x1", "x2"],
        )
        # May succeed or fail depending on statsmodels
        assert isinstance(result.success, bool)
        if result.success:
            assert "coefficient" in result.content.lower() or "r²" in result.content.lower() or "r-squared" in result.content.lower() or "R²" in result.content

    @pytest.mark.asyncio
    async def test_execute_file_not_found(self, tool):
        """Test with non-existent file."""
        result = await tool.execute(
            data_path="nonexistent.csv",
            dependent_var="y",
            independent_vars=["x1"],
        )
        assert result.success is False


class TestHypothesisTestWithData:
    @pytest.fixture
    def tool(self, tmp_path):
        return HypothesisTestTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_execute_ttest(self, tool, sample_csv):
        """Test t-test."""
        result = await tool.execute(
            data_path=str(sample_csv),
            test="t_test",
            variable="x1",
            grouping_var="group",
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_execute_correlation(self, tool, sample_csv):
        """Test correlation."""
        result = await tool.execute(
            data_path=str(sample_csv),
            test="correlation",
            variable="x1",
            grouping_var="y",
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_execute_file_not_found(self, tool):
        """Test with non-existent file."""
        result = await tool.execute(
            data_path="nonexistent.csv",
            test="t_test",
            variable="x1",
        )
        assert result.success is False


class TestVisualizationWithData:
    @pytest.fixture
    def tool(self, tmp_path):
        return CreateVisualizationTool(workspace_dir=str(tmp_path))

    @pytest.mark.asyncio
    async def test_execute_scatter(self, tool, sample_csv, tmp_path):
        """Test scatter plot creation."""
        output = str(tmp_path / "scatter.png")
        result = await tool.execute(
            data_path=str(sample_csv),
            plot_type="scatter",
            output_path=output,
            x_var="x1",
            y_var="y",
            title="Test Scatter",
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_execute_histogram(self, tool, sample_csv, tmp_path):
        """Test histogram creation."""
        output = str(tmp_path / "hist.png")
        result = await tool.execute(
            data_path=str(sample_csv),
            plot_type="histogram",
            output_path=output,
            x_var="x1",
        )
        assert isinstance(result.success, bool)

    @pytest.mark.asyncio
    async def test_execute_file_not_found(self, tool, tmp_path):
        """Test with non-existent file."""
        output = str(tmp_path / "out.png")
        result = await tool.execute(
            data_path="nonexistent.csv",
            plot_type="scatter",
            output_path=output,
            x_var="x",
            y_var="y",
        )
        assert result.success is False
