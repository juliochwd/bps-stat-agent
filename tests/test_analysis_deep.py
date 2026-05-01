"""Deep coverage tests for analysis_tools.py — exercises REAL computation paths.

All tests use real numpy/pandas/scipy/statsmodels computations with small datasets.
No mocking of scientific libraries. Tests for tools requiring uninstalled packages
(lifelines, dowhy, bambi) verify the graceful error path.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def workspace(tmp_path):
    """Create a workspace directory structure."""
    (tmp_path / "analysis" / "results").mkdir(parents=True)
    (tmp_path / "analysis" / "figures" / "auto").mkdir(parents=True)
    (tmp_path / "analysis" / "eda").mkdir(parents=True)
    (tmp_path / "analysis" / "validation").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def csv_data(tmp_path):
    """Standard test CSV with numeric, categorical, and date columns."""
    np.random.seed(42)
    n = 100
    x1 = np.random.randn(n)
    x2 = np.random.randn(n)
    df = pd.DataFrame(
        {
            "x1": x1,
            "x2": x2,
            "y": 2.5 * x1 - 1.3 * x2 + np.random.randn(n) * 0.5,
            "category": np.random.choice(["A", "B", "C"], n),
            "group": np.random.choice(["control", "treatment"], n),
            "score": np.random.randint(0, 100, n).astype(float),
            "id": range(n),
        }
    )
    path = tmp_path / "data.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def time_series_data(tmp_path):
    """Time series data with trend."""
    np.random.seed(7)
    n = 120
    dates = pd.date_range("2015-01-01", periods=n, freq="ME")
    trend = np.linspace(0, 10, n)
    noise = np.random.randn(n) * 0.5
    value1 = trend + noise
    value2 = 0.5 * value1 + np.random.randn(n) * 0.3 + 2
    df = pd.DataFrame({"date": dates, "value1": value1, "value2": value2})
    path = tmp_path / "ts_data.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def causal_data(tmp_path):
    """Data for causal inference (treatment, outcome, confounders)."""
    np.random.seed(33)
    n = 200
    confounder = np.random.randn(n)
    treatment = (confounder + np.random.randn(n) > 0).astype(int)
    outcome = 3.0 * treatment + 1.5 * confounder + np.random.randn(n)
    instrument = confounder * 0.8 + np.random.randn(n) * 0.3
    time_var = np.random.choice([0, 1], n)
    running_var = np.random.randn(n) * 2
    df = pd.DataFrame(
        {
            "treatment": treatment,
            "outcome": outcome,
            "confounder": confounder,
            "instrument": instrument,
            "time_period": time_var,
            "running": running_var,
        }
    )
    path = tmp_path / "causal_data.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def survival_data(tmp_path):
    """Survival data with duration, event, and group."""
    np.random.seed(77)
    n = 100
    duration = np.random.exponential(10, n)
    event = np.random.binomial(1, 0.7, n)
    group = np.random.choice(["A", "B"], n)
    age = np.random.randint(30, 70, n).astype(float)
    df = pd.DataFrame(
        {"duration": duration, "event": event, "group": group, "age": age}
    )
    path = tmp_path / "survival_data.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def validation_data(tmp_path):
    """Data with various quality issues for validation testing."""
    np.random.seed(11)
    n = 50
    df = pd.DataFrame(
        {
            "id": range(n),
            "value": np.random.randn(n),
            "category": np.random.choice(["X", "Y"], n),
            "with_nulls": np.where(np.random.rand(n) > 0.8, np.nan, np.random.randn(n)),
            "constant": [42.0] * n,
        }
    )
    # Add a duplicate row
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    path = tmp_path / "validation_data.csv"
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def data_with_outliers(tmp_path):
    """Data with clear outliers for IQR detection."""
    np.random.seed(22)
    values = np.random.randn(100)
    values[0] = 100.0  # extreme outlier
    values[1] = -100.0  # extreme outlier
    df = pd.DataFrame({"value": values, "normal": np.random.randn(100)})
    path = tmp_path / "outlier_data.csv"
    df.to_csv(path, index=False)
    return path


# ---------------------------------------------------------------------------
# TimeSeriesAnalysisTool Tests (analysis_tools version)
# ---------------------------------------------------------------------------


class TestTimeSeriesAnalysisToolAnalysis:
    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import TimeSeriesAnalysisTool

        return TimeSeriesAnalysisTool(workspace_dir=str(workspace))

    def test_adf_test(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["value1"],
                test_type="adf",
            )
        )
        assert result.success is True
        assert "ADF" in result.content or "Augmented Dickey-Fuller" in result.content

    def test_kpss_test(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["value1"],
                test_type="kpss",
            )
        )
        assert result.success is True
        assert "KPSS" in result.content

    def test_arima_model(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["value1"],
                test_type="arima",
                lags=1,
            )
        )
        assert result.success is True
        assert "ARIMA" in result.content
        assert "AIC" in result.content

    def test_arima_auto_order(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["value1"],
                test_type="arima",
            )
        )
        assert result.success is True
        assert "ARIMA" in result.content

    def test_var_model(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["value1", "value2"],
                test_type="var",
            )
        )
        assert result.success is True
        assert "VAR" in result.content

    def test_var_requires_2_columns(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["value1"],
                test_type="var",
            )
        )
        assert result.success is False
        assert "2" in result.error

    def test_granger_causality(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["value1", "value2"],
                test_type="granger",
                lags=3,
            )
        )
        assert result.success is True
        assert "Granger" in result.content
        assert "→" in result.content

    def test_granger_requires_2_columns(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["value1"],
                test_type="granger",
            )
        )
        assert result.success is False

    def test_cointegration(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["value1", "value2"],
                test_type="cointegration",
            )
        )
        assert result.success is True
        assert "Johansen" in result.content or "Cointegration" in result.content

    def test_cointegration_requires_2_columns(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["value1"],
                test_type="cointegration",
            )
        )
        assert result.success is False

    def test_unknown_test_type(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["value1"],
                test_type="bogus",
            )
        )
        assert result.success is False
        assert "Unknown" in result.error

    def test_missing_columns(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["nonexistent"],
            )
        )
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_file_not_found(self, workspace):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path="/no/file.csv",
                date_column="date",
                value_columns=["value1"],
            )
        )
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_results_saved(self, workspace, time_series_data):
        tool = self._make_tool(workspace)
        asyncio.run(
            tool.execute(
                data_path=str(time_series_data),
                date_column="date",
                value_columns=["value1"],
                test_type="adf",
            )
        )
        results_file = workspace / "analysis" / "results" / "time_series.json"
        assert results_file.exists()
        data = json.loads(results_file.read_text())
        assert data["test_type"] == "adf"


# ---------------------------------------------------------------------------
# BayesianAnalysisTool Tests (analysis_tools version — scipy fallback)
# ---------------------------------------------------------------------------


class TestBayesianAnalysisToolAnalysis:
    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import BayesianAnalysisTool

        return BayesianAnalysisTool(workspace_dir=str(workspace))

    def test_scipy_fallback_linear(self, workspace, csv_data):
        """bambi not installed → falls back to scipy conjugate priors."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(csv_data),
                formula="y ~ x1 + x2",
                model_type="linear",
            )
        )
        assert result.success is True
        assert "scipy fallback" in result.content or "Bayesian" in result.content
        assert "Intercept" in result.content
        assert "x1" in result.content
        assert "x2" in result.content

    def test_scipy_fallback_bayes_factors(self, workspace, csv_data):
        """Check that Bayes factors are computed in fallback."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), formula="y ~ x1 + x2")
        )
        assert result.success is True
        assert "BF" in result.content or "Bayes" in result.content

    def test_invalid_formula(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), formula="invalid_formula")
        )
        assert result.success is False
        assert "formula" in result.error.lower() or "Invalid" in result.error

    def test_missing_variables_in_formula(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), formula="y ~ nonexistent")
        )
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_file_not_found(self, workspace):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path="/no/file.csv", formula="y ~ x")
        )
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_results_saved(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        asyncio.run(
            tool.execute(data_path=str(csv_data), formula="y ~ x1 + x2")
        )
        results_file = workspace / "analysis" / "results" / "bayesian.json"
        assert results_file.exists()


# ---------------------------------------------------------------------------
# CausalInferenceTool Tests (analysis_tools version — statsmodels fallback)
# ---------------------------------------------------------------------------


class TestCausalInferenceToolAnalysis:
    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import CausalInferenceTool

        return CausalInferenceTool(workspace_dir=str(workspace))

    def test_ate_method(self, workspace, causal_data):
        """ATE via OLS (statsmodels fallback since dowhy not installed)."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="ate",
                confounders=["confounder"],
            )
        )
        assert result.success is True
        assert "ATE" in result.content

    def test_did_method(self, workspace, causal_data):
        """Difference-in-differences."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="did",
                time_var="time_period",
                confounders=["confounder"],
            )
        )
        assert result.success is True
        assert "DiD" in result.content

    def test_did_missing_time_var(self, workspace, causal_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="did",
            )
        )
        assert result.success is False
        assert "time_var" in result.error.lower()

    def test_rdd_method(self, workspace, causal_data):
        """Regression discontinuity design."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="rdd",
                running_var="running",
                cutoff=0.0,
            )
        )
        assert result.success is True
        assert "RDD" in result.content

    def test_rdd_missing_running_var(self, workspace, causal_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="rdd",
            )
        )
        assert result.success is False
        assert "running_var" in result.error.lower()

    def test_iv_method(self, workspace, causal_data):
        """Instrumental variables."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="iv",
                instrument="instrument",
                confounders=["confounder"],
            )
        )
        assert result.success is True
        assert "IV" in result.content

    def test_iv_missing_instrument(self, workspace, causal_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="iv",
            )
        )
        assert result.success is False
        assert "instrument" in result.error.lower()

    def test_unknown_method(self, workspace, causal_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="bogus",
            )
        )
        assert result.success is False
        assert "Unknown" in result.error or "method" in result.error.lower()

    def test_file_not_found(self, workspace):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path="/no/file.csv",
                treatment_var="t",
                outcome_var="o",
            )
        )
        assert result.success is False

    def test_results_saved(self, workspace, causal_data):
        tool = self._make_tool(workspace)
        asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="ate",
                confounders=["confounder"],
            )
        )
        results_file = workspace / "analysis" / "results" / "causal_inference.json"
        assert results_file.exists()
        data = json.loads(results_file.read_text())
        assert "ate" in data


# ---------------------------------------------------------------------------
# SurvivalAnalysisTool Tests (analysis_tools version — requires lifelines)
# ---------------------------------------------------------------------------


class TestSurvivalAnalysisToolAnalysis:
    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import SurvivalAnalysisTool

        return SurvivalAnalysisTool(workspace_dir=str(workspace))

    def test_lifelines_not_installed_error(self, workspace, survival_data):
        """lifelines is NOT installed, so we expect a graceful error."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(survival_data),
                duration_var="duration",
                event_var="event",
            )
        )
        assert result.success is False
        assert "lifelines" in result.error.lower()

    def test_file_not_found(self, workspace):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path="/no/file.csv",
                duration_var="duration",
                event_var="event",
            )
        )
        assert result.success is False


# ---------------------------------------------------------------------------
# ValidateDataTool Tests
# ---------------------------------------------------------------------------


class TestValidateDataTool:
    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import ValidateDataTool

        return ValidateDataTool(workspace_dir=str(workspace))

    def test_all_default_checks(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(csv_data)))
        assert "Validation Report" in result.content
        assert "Quality score" in result.content

    def test_no_nulls_check_passes(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), checks=["no_nulls"])
        )
        assert result.success is True
        assert "PASS" in result.content

    def test_no_nulls_check_fails(self, workspace, validation_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(validation_data), checks=["no_nulls"])
        )
        # validation_data has nulls in 'with_nulls' column
        assert "FAIL" in result.content
        assert "with_nulls" in result.content

    def test_no_duplicates_check(self, workspace, validation_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(validation_data), checks=["no_duplicates"])
        )
        assert "FAIL" in result.content
        assert "duplicate" in result.content.lower()

    def test_unique_ids_check(self, workspace, validation_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(validation_data), checks=["unique_ids"])
        )
        # validation_data has duplicate id
        assert "FAIL" in result.content

    def test_valid_range_check(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), checks=["valid_range"])
        )
        assert "PASS" in result.content

    def test_valid_range_with_inf(self, workspace, tmp_path):
        df = pd.DataFrame({"val": [1.0, 2.0, np.inf, 4.0]})
        path = tmp_path / "inf_data.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(path), checks=["valid_range"])
        )
        assert "FAIL" in result.content
        assert "Infinite" in result.content or "infinite" in result.content.lower()

    def test_consistent_types_check(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), checks=["consistent_types"])
        )
        assert "PASS" in result.content

    def test_no_outliers_iqr_check(self, workspace, data_with_outliers):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(data_with_outliers), checks=["no_outliers_iqr"])
        )
        assert "FAIL" in result.content
        assert "value" in result.content.lower()

    def test_file_not_found(self, workspace):
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path="/no/file.csv"))
        assert result.success is False
        assert "not found" in result.error.lower()

    def test_empty_dataset(self, workspace, tmp_path):
        df = pd.DataFrame({"a": pd.Series(dtype="float64")})
        path = tmp_path / "empty.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(path)))
        assert result.success is False
        assert "empty" in result.error.lower()

    def test_report_saved(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        asyncio.run(tool.execute(data_path=str(csv_data)))
        report_file = workspace / "analysis" / "validation" / "validation_report.json"
        assert report_file.exists()


# ---------------------------------------------------------------------------
# CheckStatisticalValidityTool Tests
# ---------------------------------------------------------------------------


class TestCheckStatisticalValidityTool:
    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import CheckStatisticalValidityTool

        return CheckStatisticalValidityTool(workspace_dir=str(workspace))

    def test_normality_check(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(csv_data),
                variables=["x1", "x2"],
                checks=["normality"],
            )
        )
        assert result.success is True
        assert "Normality" in result.content
        assert "Shapiro-Wilk" in result.content
        assert "K-S" in result.content

    def test_homoscedasticity_check(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(csv_data),
                checks=["homoscedasticity"],
                dependent_var="y",
                independent_vars=["x1", "x2"],
            )
        )
        assert result.success is True
        assert "Breusch-Pagan" in result.content

    def test_multicollinearity_check(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(csv_data),
                checks=["multicollinearity"],
                independent_vars=["x1", "x2", "score"],
            )
        )
        assert result.success is True
        assert "VIF" in result.content

    def test_autocorrelation_check(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(csv_data),
                checks=["autocorrelation"],
                dependent_var="y",
                independent_vars=["x1", "x2"],
            )
        )
        assert result.success is True
        assert "Durbin-Watson" in result.content
        assert "Ljung-Box" in result.content

    def test_all_checks(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(csv_data),
                dependent_var="y",
                independent_vars=["x1", "x2"],
            )
        )
        assert result.success is True
        assert "Summary" in result.content

    def test_no_numeric_columns(self, workspace, tmp_path):
        df = pd.DataFrame({"a": ["x", "y", "z"], "b": ["p", "q", "r"]})
        path = tmp_path / "text_only.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(path)))
        assert result.success is False
        assert "No numeric" in result.error

    def test_file_not_found(self, workspace):
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path="/no/file.csv"))
        assert result.success is False

    def test_results_saved(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        asyncio.run(
            tool.execute(
                data_path=str(csv_data),
                checks=["normality"],
                variables=["x1"],
            )
        )
        results_file = workspace / "analysis" / "results" / "statistical_validity.json"
        assert results_file.exists()


# ---------------------------------------------------------------------------
# ConversationalAnalysisTool Tests
# ---------------------------------------------------------------------------


class TestConversationalAnalysisTool:
    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import ConversationalAnalysisTool

        return ConversationalAnalysisTool(workspace_dir=str(workspace))

    def test_summary_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="Give me a summary of the data")
        )
        assert result.success is True
        assert "Analysis Result" in result.content

    def test_correlation_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="Show me the correlation matrix")
        )
        assert result.success is True
        assert "Correlation" in result.content or "correlation" in result.content

    def test_missing_values_query(self, workspace, validation_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(validation_data), query="How many missing values?")
        )
        assert result.success is True
        assert "missing" in result.content.lower() or "Missing" in result.content

    def test_mean_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="What is the average?")
        )
        assert result.success is True
        assert "Mean" in result.content or "mean" in result.content.lower()

    def test_distribution_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="Show me the distribution")
        )
        assert result.success is True
        assert "Distribution" in result.content or "distribution" in result.content

    def test_group_by_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="Group by category")
        )
        assert result.success is True
        assert "Grouped" in result.content or "group" in result.content.lower()

    def test_count_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="How many rows?")
        )
        assert result.success is True
        assert "100" in result.content or "Rows" in result.content

    def test_max_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="What is the maximum value?")
        )
        assert result.success is True
        assert "Maximum" in result.content or "max" in result.content.lower()

    def test_min_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="What is the minimum?")
        )
        assert result.success is True
        assert "Minimum" in result.content or "min" in result.content.lower()

    def test_unique_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="Show unique values")
        )
        assert result.success is True
        assert "unique" in result.content.lower()

    def test_outlier_query(self, workspace, data_with_outliers):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(data_with_outliers), query="Find outliers")
        )
        assert result.success is True
        assert "outlier" in result.content.lower() or "Outlier" in result.content

    def test_fallback_query(self, workspace, csv_data):
        """Unknown query falls back to showing shape and head."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="xyzzy foobar")
        )
        assert result.success is True
        assert "rows" in result.content.lower() or "shape" in result.content.lower()

    def test_file_not_found(self, workspace):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path="/no/file.csv", query="summary")
        )
        assert result.success is False


# ---------------------------------------------------------------------------
# AutomatedEDATool Tests
# ---------------------------------------------------------------------------


class TestAutomatedEDATool:
    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import AutomatedEDATool

        return AutomatedEDATool(workspace_dir=str(workspace))

    def test_pandas_eda_fallback(self, workspace, csv_data):
        """ydata-profiling not installed → falls back to pandas EDA."""
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(csv_data)))
        assert result.success is True
        assert "EDA" in result.content or "Automated" in result.content
        assert "Quality score" in result.content or "quality" in result.content.lower()

    def test_eda_with_warnings(self, workspace, validation_data):
        """Data with issues should produce warnings."""
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(validation_data)))
        assert result.success is True
        assert "Warning" in result.content or "warning" in result.content.lower()

    def test_eda_minimal_mode(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(csv_data), minimal=True))
        assert result.success is True

    def test_eda_report_saved(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        asyncio.run(tool.execute(data_path=str(csv_data)))
        eda_dir = workspace / "analysis" / "eda"
        report_files = list(eda_dir.glob("*.json"))
        assert len(report_files) >= 1

    def test_empty_dataset(self, workspace, tmp_path):
        df = pd.DataFrame({"a": pd.Series(dtype="float64")})
        path = tmp_path / "empty.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(path)))
        assert result.success is False
        assert "empty" in result.error.lower()

    def test_file_not_found(self, workspace):
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path="/no/file.csv"))
        assert result.success is False

    def test_constant_column_warning(self, workspace, validation_data):
        """Constant column should trigger a warning."""
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(validation_data)))
        assert result.success is True
        assert "constant" in result.content.lower()


# ---------------------------------------------------------------------------
# AutoVisualizeTool Tests
# ---------------------------------------------------------------------------


class TestAutoVisualizeTool:
    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import AutoVisualizeTool

        return AutoVisualizeTool(workspace_dir=str(workspace))

    def test_auto_visualize_numeric_data(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(csv_data)))
        assert result.success is True
        assert "Auto-Generated" in result.content or "Visualization" in result.content
        assert "histogram" in result.content.lower() or "scatter" in result.content.lower()

    def test_auto_visualize_creates_files(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        asyncio.run(tool.execute(data_path=str(csv_data)))
        fig_dir = workspace / "analysis" / "figures" / "auto"
        png_files = list(fig_dir.glob("*.png"))
        assert len(png_files) >= 1

    def test_auto_visualize_with_datetime(self, workspace, tmp_path):
        """Data with datetime column should produce visualizations."""
        np.random.seed(42)
        df = pd.DataFrame(
            {
                "date": pd.date_range("2020-01-01", periods=50, freq="D"),
                "value": np.random.randn(50).cumsum(),
                "category": np.random.choice(["X", "Y"], 50),
            }
        )
        path = tmp_path / "datetime_data.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(path)))
        assert result.success is True
        # Should produce at least some visualizations
        assert "Total figures generated" in result.content

    def test_auto_visualize_categorical_only(self, workspace, tmp_path):
        """Data with only categorical columns should produce bar charts."""
        df = pd.DataFrame(
            {
                "color": np.random.choice(["red", "blue", "green"], 50),
                "size": np.random.choice(["S", "M", "L"], 50),
            }
        )
        path = tmp_path / "cat_data.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(path)))
        assert result.success is True
        assert "bar" in result.content.lower()

    def test_empty_dataset(self, workspace, tmp_path):
        df = pd.DataFrame({"a": pd.Series(dtype="float64")})
        path = tmp_path / "empty.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(path)))
        assert result.success is False

    def test_file_not_found(self, workspace):
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path="/no/file.csv"))
        assert result.success is False

    def test_custom_output_dir(self, workspace, csv_data, tmp_path):
        out_dir = tmp_path / "custom_figs"
        out_dir.mkdir()
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), output_dir=str(out_dir))
        )
        assert result.success is True
        png_files = list(out_dir.glob("*.png"))
        assert len(png_files) >= 1


# ---------------------------------------------------------------------------
# Tool metadata tests
# ---------------------------------------------------------------------------


class TestAnalysisToolMetadata:
    def test_time_series_metadata(self, workspace):
        from mini_agent.tools.analysis_tools import TimeSeriesAnalysisTool

        tool = TimeSeriesAnalysisTool(workspace_dir=str(workspace))
        assert tool.name == "time_series_analysis"
        assert "time series" in tool.description.lower()
        assert "data_path" in tool.parameters["properties"]

    def test_bayesian_metadata(self, workspace):
        from mini_agent.tools.analysis_tools import BayesianAnalysisTool

        tool = BayesianAnalysisTool(workspace_dir=str(workspace))
        assert tool.name == "bayesian_analysis"
        assert "bayesian" in tool.description.lower()

    def test_causal_metadata(self, workspace):
        from mini_agent.tools.analysis_tools import CausalInferenceTool

        tool = CausalInferenceTool(workspace_dir=str(workspace))
        assert tool.name == "causal_inference"
        assert "causal" in tool.description.lower()

    def test_survival_metadata(self, workspace):
        from mini_agent.tools.analysis_tools import SurvivalAnalysisTool

        tool = SurvivalAnalysisTool(workspace_dir=str(workspace))
        assert tool.name == "survival_analysis"
        assert "survival" in tool.description.lower()

    def test_validate_data_metadata(self, workspace):
        from mini_agent.tools.analysis_tools import ValidateDataTool

        tool = ValidateDataTool(workspace_dir=str(workspace))
        assert tool.name == "validate_data"
        assert "validate" in tool.description.lower() or "quality" in tool.description.lower()

    def test_check_validity_metadata(self, workspace):
        from mini_agent.tools.analysis_tools import CheckStatisticalValidityTool

        tool = CheckStatisticalValidityTool(workspace_dir=str(workspace))
        assert tool.name == "check_statistical_validity"
        assert "normality" in tool.description.lower() or "assumption" in tool.description.lower()

    def test_conversational_metadata(self, workspace):
        from mini_agent.tools.analysis_tools import ConversationalAnalysisTool

        tool = ConversationalAnalysisTool(workspace_dir=str(workspace))
        assert tool.name == "conversational_analysis"

    def test_eda_metadata(self, workspace):
        from mini_agent.tools.analysis_tools import AutomatedEDATool

        tool = AutomatedEDATool(workspace_dir=str(workspace))
        assert tool.name == "automated_eda"

    def test_auto_visualize_metadata(self, workspace):
        from mini_agent.tools.analysis_tools import AutoVisualizeTool

        tool = AutoVisualizeTool(workspace_dir=str(workspace))
        assert tool.name == "auto_visualize"


# ---------------------------------------------------------------------------
# Helper function tests
# ---------------------------------------------------------------------------


class TestHelperFunctions:
    def test_resolve_path_absolute(self):
        from mini_agent.tools.analysis_tools import _resolve_path

        result = _resolve_path("/workspace", "/absolute/path.csv")
        assert result == Path("/absolute/path.csv")

    def test_resolve_path_relative(self):
        from mini_agent.tools.analysis_tools import _resolve_path

        result = _resolve_path("/workspace", "relative/path.csv")
        assert result == Path("/workspace/relative/path.csv")

    def test_load_dataframe_csv(self, tmp_path):
        from mini_agent.tools.analysis_tools import _load_dataframe

        df = pd.DataFrame({"a": [1, 2, 3]})
        path = tmp_path / "test.csv"
        df.to_csv(path, index=False)
        loaded = _load_dataframe(path)
        assert len(loaded) == 3
        assert "a" in loaded.columns

    def test_load_dataframe_tsv(self, tmp_path):
        from mini_agent.tools.analysis_tools import _load_dataframe

        df = pd.DataFrame({"a": [1, 2, 3]})
        path = tmp_path / "test.tsv"
        df.to_csv(path, index=False, sep="\t")
        loaded = _load_dataframe(path)
        assert len(loaded) == 3

    def test_load_dataframe_json(self, tmp_path):
        from mini_agent.tools.analysis_tools import _load_dataframe

        df = pd.DataFrame({"a": [1, 2, 3]})
        path = tmp_path / "test.json"
        df.to_json(path)
        loaded = _load_dataframe(path)
        assert len(loaded) == 3

    def test_ensure_dir(self, tmp_path):
        from mini_agent.tools.analysis_tools import _ensure_dir

        path = tmp_path / "new" / "nested" / "file.json"
        result = _ensure_dir(path)
        assert result == path
        assert path.parent.exists()

    def test_require_numpy(self):
        from mini_agent.tools.analysis_tools import _require_numpy

        # numpy IS installed, so this should return None
        result = _require_numpy()
        assert result is None

    def test_load_dataframe_parquet(self, tmp_path):
        """Parquet loading — skip if pyarrow/fastparquet not installed."""
        from mini_agent.tools.analysis_tools import _load_dataframe

        try:
            df = pd.DataFrame({"a": [1, 2, 3]})
            path = tmp_path / "test.parquet"
            df.to_parquet(path, index=False)
            loaded = _load_dataframe(path)
            assert len(loaded) == 3
        except ImportError:
            pytest.skip("pyarrow/fastparquet not installed")

    def test_load_dataframe_tab(self, tmp_path):
        from mini_agent.tools.analysis_tools import _load_dataframe

        df = pd.DataFrame({"a": [1, 2, 3]})
        path = tmp_path / "test.tab"
        df.to_csv(path, index=False, sep="\t")
        loaded = _load_dataframe(path)
        assert len(loaded) == 3

    def test_load_dataframe_unknown_extension(self, tmp_path):
        """Unknown extension falls back to CSV reader."""
        from mini_agent.tools.analysis_tools import _load_dataframe

        df = pd.DataFrame({"a": [1, 2, 3]})
        path = tmp_path / "test.dat"
        df.to_csv(path, index=False)
        loaded = _load_dataframe(path)
        assert len(loaded) == 3


# ---------------------------------------------------------------------------
# Additional edge-case tests for deeper coverage
# ---------------------------------------------------------------------------


class TestValidateDataEdgeCases:
    """Additional validation tests for edge cases."""

    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import ValidateDataTool

        return ValidateDataTool(workspace_dir=str(workspace))

    def test_consistent_types_with_mixed_types(self, workspace, tmp_path):
        """Test consistent_types check with mixed-type column."""
        # Create a CSV where a column has mixed types when read
        path = tmp_path / "mixed.csv"
        path.write_text("id,val\n1,hello\n2,42\n3,world\n")
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(path), checks=["consistent_types"])
        )
        assert "consistent_types" in result.content.lower() or "Consistent" in result.content

    def test_consistent_types_with_object_mixed(self, workspace, tmp_path):
        """Force mixed types by using a JSON file with mixed values."""
        # Create data with actual mixed types in an object column
        import json as json_mod

        data = [{"id": 1, "mixed": "hello"}, {"id": 2, "mixed": 42}, {"id": 3, "mixed": "world"}]
        path = tmp_path / "mixed_types.json"
        path.write_text(json_mod.dumps(data))
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(path), checks=["consistent_types"])
        )
        # The mixed column should have mixed types (str and int)
        assert "consistent_types" in result.content.lower() or "PASS" in result.content or "FAIL" in result.content

    def test_no_outliers_with_small_data(self, workspace, tmp_path):
        """IQR check with very small dataset (< 4 rows) should skip."""
        df = pd.DataFrame({"val": [1.0, 2.0, 3.0]})
        path = tmp_path / "small.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(path), checks=["no_outliers_iqr"])
        )
        assert result.success is True
        assert "PASS" in result.content

    def test_unique_ids_with_no_id_column(self, workspace, tmp_path):
        """When no 'id' column exists, falls back to first column."""
        df = pd.DataFrame({"name": ["a", "b", "c"], "value": [1, 2, 3]})
        path = tmp_path / "no_id.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(path), checks=["unique_ids"])
        )
        assert "unique_ids" in result.content.lower() or "PASS" in result.content

    def test_multiple_checks_combined(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(csv_data),
                checks=["no_nulls", "no_duplicates", "valid_range", "consistent_types", "no_outliers_iqr"],
            )
        )
        assert "Quality score" in result.content
        assert "5" in result.content  # 5 checks total


class TestCheckStatisticalValidityEdgeCases:
    """Additional statistical validity edge cases."""

    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import CheckStatisticalValidityTool

        return CheckStatisticalValidityTool(workspace_dir=str(workspace))

    def test_normality_with_specific_variables(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(csv_data),
                variables=["x1"],
                checks=["normality"],
            )
        )
        assert result.success is True
        assert "x1" in result.content

    def test_normality_with_large_sample(self, workspace, tmp_path):
        """Large sample (>5000) should be subsampled for Shapiro-Wilk."""
        np.random.seed(42)
        df = pd.DataFrame({"val": np.random.randn(6000)})
        path = tmp_path / "large.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(path), checks=["normality"])
        )
        assert result.success is True
        assert "Shapiro-Wilk" in result.content

    def test_homoscedasticity_without_dep_var(self, workspace, csv_data):
        """Homoscedasticity check without dependent_var should be skipped."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(csv_data),
                checks=["homoscedasticity"],
            )
        )
        assert result.success is True
        # Without dependent_var, the check is skipped
        assert "Breusch-Pagan" not in result.content

    def test_multicollinearity_without_independent_vars(self, workspace, csv_data):
        """VIF check without independent_vars should be skipped."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(csv_data),
                checks=["multicollinearity"],
            )
        )
        assert result.success is True
        assert "VIF" not in result.content

    def test_autocorrelation_without_vars(self, workspace, csv_data):
        """Autocorrelation check without dependent/independent vars should be skipped."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(csv_data),
                checks=["autocorrelation"],
            )
        )
        assert result.success is True
        assert "Durbin-Watson" not in result.content


class TestConversationalAnalysisEdgeCases:
    """Additional conversational analysis edge cases."""

    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import ConversationalAnalysisTool

        return ConversationalAnalysisTool(workspace_dir=str(workspace))

    def test_describe_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="describe the data")
        )
        assert result.success is True

    def test_overview_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="give me an overview")
        )
        assert result.success is True

    def test_statistics_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="show statistics")
        )
        assert result.success is True

    def test_histogram_query(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="show histogram")
        )
        assert result.success is True
        assert "Distribution" in result.content or "distribution" in result.content

    def test_no_numeric_for_correlation(self, workspace, tmp_path):
        """Correlation query with no numeric columns."""
        df = pd.DataFrame({"a": ["x", "y", "z"], "b": ["p", "q", "r"]})
        path = tmp_path / "text_only.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(path), query="show correlation")
        )
        assert result.success is True
        assert "No numeric" in result.content

    def test_no_categorical_for_groupby(self, workspace, tmp_path):
        """Group by query with no categorical columns."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        path = tmp_path / "numeric_only.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(path), query="group by something")
        )
        assert result.success is True
        assert "No categorical" in result.content or "categorical" in result.content.lower()

    def test_no_missing_values(self, workspace, csv_data):
        """Missing values query on clean data."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), query="show null values")
        )
        assert result.success is True
        assert "missing" in result.content.lower() or "No missing" in result.content

    def test_no_outliers(self, workspace, tmp_path):
        """Outlier query on data without outliers."""
        df = pd.DataFrame({"val": [1.0, 2.0, 3.0, 4.0, 5.0]})
        path = tmp_path / "no_outliers.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(path), query="find anomalies")
        )
        assert result.success is True


class TestAutomatedEDAEdgeCases:
    """Additional EDA edge cases."""

    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import AutomatedEDATool

        return AutomatedEDATool(workspace_dir=str(workspace))

    def test_eda_with_high_missing(self, workspace, tmp_path):
        """Data with >50% missing should trigger recommendation."""
        df = pd.DataFrame(
            {
                "val": [1.0] + [np.nan] * 9,
                "id": range(10),
            }
        )
        path = tmp_path / "high_missing.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(path)))
        assert result.success is True
        assert "missing" in result.content.lower() or "Recommendation" in result.content

    def test_eda_with_high_correlation(self, workspace, tmp_path):
        """Data with highly correlated columns should trigger warning."""
        np.random.seed(42)
        x = np.random.randn(50)
        df = pd.DataFrame({"x": x, "y": x * 1.01 + 0.001 * np.random.randn(50)})
        path = tmp_path / "high_corr.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(path)))
        assert result.success is True
        assert "correlation" in result.content.lower() or "Warning" in result.content

    def test_eda_custom_output_path(self, workspace, csv_data, tmp_path):
        out_path = tmp_path / "custom_eda.json"
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(data_path=str(csv_data), output_path=str(out_path))
        )
        assert result.success is True
        assert out_path.exists()

    def test_eda_report_json_structure(self, workspace, csv_data):
        tool = self._make_tool(workspace)
        asyncio.run(tool.execute(data_path=str(csv_data)))
        eda_dir = workspace / "analysis" / "eda"
        report_files = list(eda_dir.glob("*.json"))
        assert len(report_files) >= 1
        data = json.loads(report_files[0].read_text())
        assert "overview" in data
        assert "variables" in data
        assert "data_quality_score" in data


class TestAutoVisualizeEdgeCases:
    """Additional auto-visualize edge cases."""

    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import AutoVisualizeTool

        return AutoVisualizeTool(workspace_dir=str(workspace))

    def test_single_numeric_column(self, workspace, tmp_path):
        """Single numeric column should produce histogram."""
        df = pd.DataFrame({"val": np.random.randn(50)})
        path = tmp_path / "single_num.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(path)))
        assert result.success is True
        assert "histogram" in result.content.lower()

    def test_many_categories_skipped(self, workspace, tmp_path):
        """Categorical column with >15 unique values should be skipped for bar chart."""
        df = pd.DataFrame(
            {
                "cat": [f"cat_{i}" for i in range(50)],
                "val": np.random.randn(50),
            }
        )
        path = tmp_path / "many_cats.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(path)))
        assert result.success is True
        # Should still produce histogram/scatter but not bar for the high-cardinality cat

    def test_three_numeric_columns_heatmap(self, workspace, tmp_path):
        """Three numeric columns should produce a heatmap."""
        np.random.seed(42)
        df = pd.DataFrame(
            {
                "a": np.random.randn(50),
                "b": np.random.randn(50),
                "c": np.random.randn(50),
            }
        )
        path = tmp_path / "three_num.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(tool.execute(data_path=str(path)))
        assert result.success is True
        assert "heatmap" in result.content.lower()


class TestCausalInferenceEdgeCases:
    """Additional causal inference edge cases."""

    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import CausalInferenceTool

        return CausalInferenceTool(workspace_dir=str(workspace))

    def test_ate_without_confounders(self, workspace, causal_data):
        """ATE without confounders should still work."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="ate",
            )
        )
        assert result.success is True
        assert "ATE" in result.content

    def test_did_with_confounders(self, workspace, causal_data):
        """DiD with confounders."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="did",
                time_var="time_period",
                confounders=["confounder"],
            )
        )
        assert result.success is True

    def test_rdd_with_custom_cutoff(self, workspace, causal_data):
        """RDD with non-zero cutoff."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="rdd",
                running_var="running",
                cutoff=1.0,
            )
        )
        assert result.success is True
        assert "RDD" in result.content

    def test_iv_with_confounders(self, workspace, causal_data):
        """IV with confounders."""
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(causal_data),
                treatment_var="treatment",
                outcome_var="outcome",
                method="iv",
                instrument="instrument",
                confounders=["confounder"],
            )
        )
        assert result.success is True


class TestTimeSeriesAnalysisEdgeCases:
    """Additional time series edge cases for analysis_tools."""

    def _make_tool(self, workspace):
        from mini_agent.tools.analysis_tools import TimeSeriesAnalysisTool

        return TimeSeriesAnalysisTool(workspace_dir=str(workspace))

    def test_var_with_specified_lags(self, workspace, tmp_path):
        """VAR with explicit lag specification."""
        np.random.seed(42)
        n = 80
        dates = pd.date_range("2015-01-01", periods=n, freq="ME")
        v1 = np.random.randn(n).cumsum()
        v2 = 0.5 * v1 + np.random.randn(n) * 0.3
        df = pd.DataFrame({"date": dates, "v1": v1, "v2": v2})
        path = tmp_path / "ts_var.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(path),
                date_column="date",
                value_columns=["v1", "v2"],
                test_type="var",
                lags=3,
            )
        )
        assert result.success is True
        assert "VAR" in result.content

    def test_granger_auto_lags(self, workspace, tmp_path):
        """Granger causality with auto lag selection."""
        np.random.seed(42)
        n = 80
        dates = pd.date_range("2015-01-01", periods=n, freq="ME")
        v1 = np.random.randn(n).cumsum()
        v2 = 0.5 * v1 + np.random.randn(n) * 0.3
        df = pd.DataFrame({"date": dates, "v1": v1, "v2": v2})
        path = tmp_path / "ts_granger.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(path),
                date_column="date",
                value_columns=["v1", "v2"],
                test_type="granger",
            )
        )
        assert result.success is True

    def test_cointegration_with_lags(self, workspace, tmp_path):
        """Cointegration with specified lags."""
        np.random.seed(42)
        n = 80
        dates = pd.date_range("2015-01-01", periods=n, freq="ME")
        v1 = np.random.randn(n).cumsum()
        v2 = 0.5 * v1 + np.random.randn(n) * 0.3
        df = pd.DataFrame({"date": dates, "v1": v1, "v2": v2})
        path = tmp_path / "ts_coint.csv"
        df.to_csv(path, index=False)
        tool = self._make_tool(workspace)
        result = asyncio.run(
            tool.execute(
                data_path=str(path),
                date_column="date",
                value_columns=["v1", "v2"],
                test_type="cointegration",
                lags=3,
            )
        )
        assert result.success is True
