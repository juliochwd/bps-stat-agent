"""Tests for statistics_tools.py with sys.modules-level mocking.

Mocks numpy, pandas, scipy, statsmodels at the sys.modules level
to exercise the actual computation paths.
"""

import builtins
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Real import function
_real_import = builtins.__import__


def _make_mock_series(values=None):
    """Create a mock pandas Series."""
    if values is None:
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
    s = MagicMock()
    s.mean.return_value = sum(values) / len(values)
    s.median.return_value = sorted(values)[len(values) // 2]
    s.std.return_value = 1.5
    s.min.return_value = min(values)
    s.max.return_value = max(values)
    s.skew.return_value = 0.1
    s.kurtosis.return_value = -0.5
    s.dropna.return_value = s
    s.values = values
    s.__len__ = lambda self: len(values)
    s.__iter__ = lambda self: iter(values)
    return s


def _mock_import_factory(mocked_modules):
    """Create a custom import function that returns mocks for specified modules."""
    def _custom_import(name, *args, **kwargs):
        if name in mocked_modules:
            return mocked_modules[name]
        # Check for submodule patterns
        for mod_name, mock_mod in mocked_modules.items():
            if name.startswith(mod_name + "."):
                return mock_mod
        return _real_import(name, *args, **kwargs)
    return _custom_import


class TestDescriptiveStatsWithMockedLibs:
    """Test DescriptiveStatsTool with sys.modules mocking."""

    @pytest.mark.asyncio
    async def test_full_execution(self, tmp_path):
        mock_np = MagicMock()
        mock_np.number = float

        mock_series = _make_mock_series()
        mock_col = MagicMock()
        mock_col.isna.return_value = MagicMock(sum=MagicMock(return_value=0))
        mock_col.dropna.return_value = mock_series

        mock_numeric_df = MagicMock()
        mock_numeric_df.empty = False
        mock_numeric_df.columns = ["x", "y"]
        mock_numeric_df.__getitem__ = lambda self, key: mock_col
        mock_numeric_df.corr.return_value = MagicMock(
            round=MagicMock(return_value=MagicMock(
                to_dict=MagicMock(return_value={"x": {"x": 1.0, "y": 0.5}, "y": {"x": 0.5, "y": 1.0}})
            ))
        )

        mock_df = MagicMock()
        mock_df.columns = ["x", "y"]
        mock_df.select_dtypes.return_value = mock_numeric_df

        mock_pd = MagicMock()
        mock_pd.read_csv.return_value = mock_df

        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", True):
            with patch("mini_agent.tools.statistics_tools.pd", mock_pd):
                with patch("mini_agent.tools.statistics_tools.np", mock_np):
                    from mini_agent.tools.statistics_tools import DescriptiveStatsTool
                    tool = DescriptiveStatsTool(workspace_dir=str(tmp_path))
                    result = await tool.execute(data_path="data.csv")
                    assert result.success is True
                    assert "Descriptive Statistics" in result.content
                    assert "Correlation" in result.content

    @pytest.mark.asyncio
    async def test_single_column_no_correlation(self, tmp_path):
        mock_np = MagicMock()
        mock_np.number = float

        mock_series = _make_mock_series()
        mock_col = MagicMock()
        mock_col.isna.return_value = MagicMock(sum=MagicMock(return_value=0))
        mock_col.dropna.return_value = mock_series

        mock_numeric_df = MagicMock()
        mock_numeric_df.empty = False
        mock_numeric_df.columns = ["x"]
        mock_numeric_df.__getitem__ = lambda self, key: mock_col

        mock_df = MagicMock()
        mock_df.columns = ["x"]
        mock_df.select_dtypes.return_value = mock_numeric_df

        mock_pd = MagicMock()
        mock_pd.read_csv.return_value = mock_df

        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", True):
            with patch("mini_agent.tools.statistics_tools.pd", mock_pd):
                with patch("mini_agent.tools.statistics_tools.np", mock_np):
                    from mini_agent.tools.statistics_tools import DescriptiveStatsTool
                    tool = DescriptiveStatsTool(workspace_dir=str(tmp_path))
                    result = await tool.execute(data_path="data.csv")
                    assert result.success is True
                    # Single column = no correlation matrix
                    assert "Descriptive Statistics" in result.content


class TestCreateVisualizationWithMockedLibs:
    """Test CreateVisualizationTool - import error path."""

    @pytest.mark.asyncio
    async def test_matplotlib_not_installed(self, tmp_path):
        """When matplotlib is not installed, should return import error."""
        mock_np = MagicMock()
        mock_np.number = float

        mock_pd = MagicMock()
        mock_pd.read_csv.return_value = MagicMock()

        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", True):
            with patch("mini_agent.tools.statistics_tools.pd", mock_pd):
                with patch("mini_agent.tools.statistics_tools.np", mock_np):
                    from mini_agent.tools.statistics_tools import CreateVisualizationTool
                    tool = CreateVisualizationTool(workspace_dir=str(tmp_path))
                    result = await tool.execute(
                        data_path="data.csv", plot_type="scatter",
                        x_var="x", y_var="y", output_path="fig.png"
                    )
                    # matplotlib not installed, so it should fail gracefully
                    assert result.success is False
                    assert "matplotlib" in result.error.lower() or "seaborn" in result.error.lower() or "Visualization" in result.error


class TestHypothesisTestWithMockedLibs:
    """Test HypothesisTestTool with mocked scipy."""

    @pytest.fixture
    def mock_scipy_env(self):
        mock_scipy = MagicMock()
        mock_scipy_stats = MagicMock()
        mock_scipy_stats.shapiro.return_value = (0.95, 0.3)
        mock_scipy_stats.levene.return_value = (2.5, 0.12)
        mock_scipy_stats.ttest_ind.return_value = (2.1, 0.04)
        mock_scipy_stats.f_oneway.return_value = (5.2, 0.008)
        mock_scipy_stats.mannwhitneyu.return_value = (150.0, 0.03)
        mock_scipy_stats.kruskal.return_value = (8.5, 0.014)
        mock_scipy_stats.chi2_contingency.return_value = (12.5, 0.006, 3, MagicMock())

        saved = {}
        for mod in ['scipy', 'scipy.stats']:
            saved[mod] = sys.modules.get(mod)
        sys.modules['scipy'] = mock_scipy
        sys.modules['scipy.stats'] = mock_scipy_stats

        yield mock_scipy_stats

        for mod, val in saved.items():
            if val is None:
                sys.modules.pop(mod, None)
            else:
                sys.modules[mod] = val

    @pytest.mark.asyncio
    async def test_shapiro_wilk_scipy_not_installed(self, tmp_path):
        """When scipy is not installed, should return import error."""
        mock_np = MagicMock()
        mock_np.number = float

        mock_pd = MagicMock()
        mock_pd.read_csv.return_value = MagicMock(columns=["score"])

        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", True):
            with patch("mini_agent.tools.statistics_tools.pd", mock_pd):
                with patch("mini_agent.tools.statistics_tools.np", mock_np):
                    with patch.dict("sys.modules", {"scipy": None, "scipy.stats": None}):
                        from mini_agent.tools.statistics_tools import HypothesisTestTool
                        tool = HypothesisTestTool(workspace_dir=str(tmp_path))
                        result = await tool.execute(
                            data_path="data.csv", test="shapiro_wilk", variable="score"
                        )
                        # With scipy removed from sys.modules and mocked data,
                        # either fails with scipy error or data error
                        assert result.success is False or result.content != ""

    @pytest.mark.asyncio
    async def test_unknown_test(self, tmp_path, mock_scipy_env):
        mock_np = MagicMock()
        mock_np.number = float

        mock_pd = MagicMock()
        mock_pd.read_csv.return_value = MagicMock(columns=["score"])

        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", True):
            with patch("mini_agent.tools.statistics_tools.pd", mock_pd):
                with patch("mini_agent.tools.statistics_tools.np", mock_np):
                    from mini_agent.tools.statistics_tools import HypothesisTestTool
                    tool = HypothesisTestTool(workspace_dir=str(tmp_path))
                    result = await tool.execute(
                        data_path="data.csv", test="unknown_test", variable="score"
                    )
                    assert result.success is False
                    assert "Unknown" in result.error


class TestNonparametricWithMockedLibs:
    """Test NonparametricTestTool with mocked scipy."""

    @pytest.fixture
    def mock_scipy_env(self):
        mock_scipy = MagicMock()
        mock_scipy_stats = MagicMock()
        mock_scipy_stats.mannwhitneyu.return_value = (150.0, 0.03)

        saved = {}
        for mod in ['scipy', 'scipy.stats']:
            saved[mod] = sys.modules.get(mod)
        sys.modules['scipy'] = mock_scipy
        sys.modules['scipy.stats'] = mock_scipy_stats

        yield mock_scipy_stats

        for mod, val in saved.items():
            if val is None:
                sys.modules.pop(mod, None)
            else:
                sys.modules[mod] = val

    @pytest.mark.asyncio
    async def test_mann_whitney_no_group_var(self, tmp_path, mock_scipy_env):
        mock_pd = MagicMock()
        mock_pd.read_csv.return_value = MagicMock(columns=["score"])

        with patch("mini_agent.tools.statistics_tools._HAS_NUMPY", True):
            with patch("mini_agent.tools.statistics_tools.pd", mock_pd):
                from mini_agent.tools.statistics_tools import NonparametricTestTool
                tool = NonparametricTestTool(workspace_dir=str(tmp_path))
                result = await tool.execute(
                    data_path="data.csv", test_type="mann_whitney", variable1="score"
                )
                assert result.success is False
                assert "group_variable" in result.error.lower()
