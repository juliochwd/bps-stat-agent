"""Statistical analysis tools for the Academic Research Agent.

Provides tools for descriptive statistics, regression, hypothesis testing,
and time series analysis with APA-formatted output.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import numpy as np
    import pandas as pd

    _HAS_NUMPY = True
except ImportError:
    np = None  # type: ignore[assignment]
    pd = None  # type: ignore[assignment]
    _HAS_NUMPY = False

from .base import Tool, ToolResult


def _require_numpy() -> ToolResult | None:
    """Return an error ToolResult if numpy/pandas are not installed, else None."""
    if not _HAS_NUMPY:
        return ToolResult(
            success=False,
            error=(
                "numpy and pandas are required for statistical tools. "
                "Install with: pip install 'bps-stat-agent[research-core]'"
            ),
        )
    return None


class DescriptiveStatsTool(Tool):
    """Compute descriptive statistics with APA-formatted output."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "descriptive_stats"

    @property
    def description(self) -> str:
        return (
            "Compute descriptive statistics for a dataset. Returns mean, median, SD, "
            "min, max, skewness, kurtosis, N, missing values, and correlation matrix. "
            "Output formatted in APA 7th edition style."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "variables": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Variable names to analyze (all numeric if omitted)",
                },
                "groupby": {"type": "string", "description": "Optional grouping variable"},
            },
            "required": ["data_path"],
        }

    async def execute(
        self, data_path: str, variables: list[str] | None = None, groupby: str | None = None
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        try:
            full_path = Path(self._workspace_dir) / data_path if not Path(data_path).is_absolute() else Path(data_path)
            df = pd.read_csv(str(full_path))

            if variables:
                cols = [c for c in variables if c in df.columns]
                if not cols:
                    return ToolResult(success=False, error=f"None of {variables} found in columns: {list(df.columns)}")
                numeric_df = df[cols].select_dtypes(include=[np.number])
            else:
                numeric_df = df.select_dtypes(include=[np.number])

            if numeric_df.empty:
                return ToolResult(success=False, error="No numeric columns found in data")

            # Compute statistics
            stats = {}
            for col in numeric_df.columns:
                series = numeric_df[col].dropna()
                stats[col] = {
                    "n": int(len(series)),
                    "missing": int(numeric_df[col].isna().sum()),
                    "mean": round(float(series.mean()), 2),
                    "median": round(float(series.median()), 2),
                    "sd": round(float(series.std()), 2),
                    "min": round(float(series.min()), 2),
                    "max": round(float(series.max()), 2),
                    "skewness": round(float(series.skew()), 3),
                    "kurtosis": round(float(series.kurtosis()), 3),
                }

            # Correlation matrix
            if len(numeric_df.columns) > 1:
                corr = numeric_df.corr().round(3).to_dict()
            else:
                corr = None

            # Format output
            lines = ["## Descriptive Statistics\n"]
            lines.append("| Variable | N | M | SD | Min | Max | Skew | Kurt |")
            lines.append("|----------|---|---|----|----|-----|------|------|")
            for var, s in stats.items():
                lines.append(
                    f"| {var} | {s['n']} | {s['mean']} | {s['sd']} | {s['min']} | {s['max']} | {s['skewness']} | {s['kurtosis']} |"
                )

            if corr:
                lines.append("\n## Correlation Matrix\n")
                cols = list(corr.keys())
                lines.append("| | " + " | ".join(cols) + " |")
                lines.append("|" + "---|" * (len(cols) + 1))
                for row in cols:
                    vals = " | ".join(str(corr[row].get(c, "")) for c in cols)
                    lines.append(f"| {row} | {vals} |")

            result_text = "\n".join(lines)

            # Save results as JSON
            results_path = Path(self._workspace_dir) / "analysis" / "results" / "descriptive_stats.json"
            results_path.parent.mkdir(parents=True, exist_ok=True)
            with open(results_path, "w") as f:
                json.dump({"statistics": stats, "correlation": corr}, f, indent=2)

            result_text += f"\n\n*Results saved to: {results_path}*"
            return ToolResult(success=True, content=result_text)

        except FileNotFoundError:
            return ToolResult(success=False, error=f"Data file not found: {data_path}")
        except Exception as e:
            return ToolResult(success=False, error=f"Analysis failed: {e}")


class RegressionAnalysisTool(Tool):
    """Run regression analysis with diagnostic output."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "regression_analysis"

    @property
    def description(self) -> str:
        return (
            "Run regression analysis (OLS, logistic, panel FE/RE). Returns coefficients, "
            "std errors, t-stats, p-values, R², F-stat, and diagnostic tests. "
            "Output formatted in APA style with publication-ready regression table."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "dependent_var": {"type": "string", "description": "Dependent variable name"},
                "independent_vars": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Independent variables",
                },
                "method": {
                    "type": "string",
                    "enum": ["ols", "logistic"],
                    "description": "Regression method (default: ols)",
                },
                "robust_se": {"type": "boolean", "description": "Use robust standard errors (default: true)"},
            },
            "required": ["data_path", "dependent_var", "independent_vars"],
        }

    async def execute(
        self,
        data_path: str,
        dependent_var: str,
        independent_vars: list[str],
        method: str = "ols",
        robust_se: bool = True,
        **kwargs,
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        try:
            import statsmodels.api as sm

            full_path = Path(self._workspace_dir) / data_path if not Path(data_path).is_absolute() else Path(data_path)
            df = pd.read_csv(str(full_path))

            # Prepare data
            all_vars = [dependent_var] + independent_vars
            missing = [v for v in all_vars if v not in df.columns]
            if missing:
                return ToolResult(success=False, error=f"Variables not found: {missing}. Available: {list(df.columns)}")

            clean_df = df[all_vars].dropna()
            y = clean_df[dependent_var]
            X = sm.add_constant(clean_df[independent_vars])

            # Run regression
            if method == "logistic":
                model = sm.Logit(y, X)
            else:
                model = sm.OLS(y, X)

            cov_type = "HC3" if robust_se else "nonrobust"
            results = model.fit(cov_type=cov_type)

            # Format output
            from ..research.apa_formatter import format_p_value

            lines = [f"## {method.upper()} Regression Results\n"]
            lines.append(f"**Dependent Variable:** {dependent_var}")
            lines.append(f"**N:** {int(results.nobs)}")
            lines.append(f"**R²:** {results.rsquared:.4f}" if hasattr(results, "rsquared") else "")
            lines.append(f"**Adj. R²:** {results.rsquared_adj:.4f}" if hasattr(results, "rsquared_adj") else "")
            lines.append(
                f"**F-statistic:** {results.fvalue:.2f}, p {format_p_value(results.f_pvalue)}"
                if hasattr(results, "fvalue")
                else ""
            )
            lines.append("")

            # Coefficient table
            lines.append("| Variable | Coef. | Std. Err. | t | p | 95% CI |")
            lines.append("|----------|-------|-----------|---|---|--------|")
            conf = results.conf_int()
            for var in results.params.index:
                coef = results.params[var]
                se = results.bse[var]
                t = results.tvalues[var]
                p = results.pvalues[var]
                ci_low, ci_high = conf.loc[var]
                p_str = format_p_value(p)
                lines.append(f"| {var} | {coef:.4f} | {se:.4f} | {t:.2f} | {p_str} | [{ci_low:.4f}, {ci_high:.4f}] |")

            # Save results
            results_data = {
                "method": method,
                "dependent_var": dependent_var,
                "independent_vars": independent_vars,
                "n": int(results.nobs),
                "r_squared": float(results.rsquared) if hasattr(results, "rsquared") else None,
                "coefficients": {k: float(v) for k, v in results.params.items()},
                "p_values": {k: float(v) for k, v in results.pvalues.items()},
            }
            results_path = Path(self._workspace_dir) / "analysis" / "results" / "regression.json"
            results_path.parent.mkdir(parents=True, exist_ok=True)
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2)

            result_text = "\n".join(lines)
            result_text += f"\n\n*Results saved to: {results_path}*"
            return ToolResult(success=True, content=result_text)

        except Exception as e:
            return ToolResult(success=False, error=f"Regression failed: {e}")


class HypothesisTestTool(Tool):
    """Perform statistical hypothesis tests with APA output."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "hypothesis_test"

    @property
    def description(self) -> str:
        return (
            "Perform hypothesis tests: t-test (independent/paired), ANOVA, chi-square, "
            "Mann-Whitney, Kruskal-Wallis, Shapiro-Wilk, Levene's. Returns test statistic, "
            "df, p-value, effect size, and APA-formatted result."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "test": {
                    "type": "string",
                    "enum": [
                        "t_test_independent",
                        "t_test_paired",
                        "anova_oneway",
                        "chi_square_independence",
                        "mann_whitney",
                        "kruskal_wallis",
                        "shapiro_wilk",
                        "levene",
                    ],
                    "description": "Statistical test to perform",
                },
                "variable": {"type": "string", "description": "Test variable (dependent)"},
                "grouping_var": {"type": "string", "description": "Grouping variable"},
                "alpha": {"type": "number", "description": "Significance level (default: 0.05)"},
            },
            "required": ["data_path", "test", "variable"],
        }

    async def execute(
        self, data_path: str, test: str, variable: str, grouping_var: str | None = None, alpha: float = 0.05, **kwargs
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        try:
            from scipy import stats as scipy_stats

            from ..research.apa_formatter import format_anova, format_chi_square, format_p_value, format_ttest

            full_path = Path(self._workspace_dir) / data_path if not Path(data_path).is_absolute() else Path(data_path)
            df = pd.read_csv(str(full_path))

            result_lines = [f"## Hypothesis Test: {test}\n"]

            if test == "shapiro_wilk":
                data = df[variable].dropna()
                stat, p = scipy_stats.shapiro(data)
                result_lines.append("**Shapiro-Wilk Test for Normality**")
                result_lines.append(f"Variable: {variable} (n = {len(data)})")
                result_lines.append(f"W = {stat:.4f}, p {format_p_value(p)}")
                result_lines.append(
                    f"**Conclusion:** {'Normal distribution (fail to reject H₀)' if p > alpha else 'Non-normal distribution (reject H₀)'}"
                )

            elif test == "levene":
                if not grouping_var:
                    return ToolResult(success=False, error="grouping_var required for Levene's test")
                groups = [g[variable].dropna().values for _, g in df.groupby(grouping_var)]
                stat, p = scipy_stats.levene(*groups)
                result_lines.append("**Levene's Test for Homogeneity of Variance**")
                result_lines.append(f"F = {stat:.2f}, p {format_p_value(p)}")
                result_lines.append(
                    f"**Conclusion:** {'Equal variances (fail to reject H₀)' if p > alpha else 'Unequal variances (reject H₀)'}"
                )

            elif test == "t_test_independent":
                if not grouping_var:
                    return ToolResult(success=False, error="grouping_var required for t-test")
                group_names = df[grouping_var].dropna().unique()
                if len(group_names) != 2:
                    return ToolResult(success=False, error=f"Expected 2 groups, got {len(group_names)}")
                g1 = df[df[grouping_var] == group_names[0]][variable].dropna().values
                g2 = df[df[grouping_var] == group_names[1]][variable].dropna().values
                stat, p = scipy_stats.ttest_ind(g1, g2)
                # Cohen's d
                pooled_std = np.sqrt(
                    ((len(g1) - 1) * np.std(g1, ddof=1) ** 2 + (len(g2) - 1) * np.std(g2, ddof=1) ** 2)
                    / (len(g1) + len(g2) - 2)
                )
                d = (np.mean(g1) - np.mean(g2)) / pooled_std if pooled_std > 0 else 0
                df_val = len(g1) + len(g2) - 2
                result_lines.append("**Independent Samples t-test**")
                result_lines.append(f"APA: {format_ttest(stat, df_val, p, d)}")
                result_lines.append(
                    f"**Conclusion:** {'Significant difference' if p < alpha else 'No significant difference'} at α = {alpha}"
                )

            elif test == "anova_oneway":
                if not grouping_var:
                    return ToolResult(success=False, error="grouping_var required for ANOVA")
                groups = [g[variable].dropna().values for _, g in df.groupby(grouping_var)]
                stat, p = scipy_stats.f_oneway(*groups)
                k = len(groups)
                n_total = sum(len(g) for g in groups)
                df1, df2 = k - 1, n_total - k
                # Eta-squared
                ss_between = sum(len(g) * (np.mean(g) - df[variable].mean()) ** 2 for g in groups)
                ss_total = sum((x - df[variable].mean()) ** 2 for g in groups for x in g)
                eta_sq = ss_between / ss_total if ss_total > 0 else 0
                result_lines.append("**One-Way ANOVA**")
                result_lines.append(f"APA: {format_anova(stat, df1, df2, p, eta_sq)}")
                result_lines.append(
                    f"**Conclusion:** {'Significant difference' if p < alpha else 'No significant difference'} at α = {alpha}"
                )

            elif test == "mann_whitney":
                if not grouping_var:
                    return ToolResult(success=False, error="grouping_var required")
                groups = df.groupby(grouping_var)[variable].apply(lambda x: x.dropna().values)
                if len(groups) != 2:
                    return ToolResult(success=False, error=f"Expected 2 groups, got {len(groups)}")
                g1, g2 = list(groups.values())
                stat, p = scipy_stats.mannwhitneyu(g1, g2, alternative="two-sided")
                result_lines.append("**Mann-Whitney U Test**")
                result_lines.append(f"U = {stat:.2f}, p {format_p_value(p)}")
                result_lines.append(
                    f"**Conclusion:** {'Significant difference' if p < alpha else 'No significant difference'}"
                )

            elif test == "kruskal_wallis":
                if not grouping_var:
                    return ToolResult(success=False, error="grouping_var required")
                groups = [g[variable].dropna().values for _, g in df.groupby(grouping_var)]
                stat, p = scipy_stats.kruskal(*groups)
                result_lines.append("**Kruskal-Wallis H Test**")
                result_lines.append(f"H = {stat:.2f}, p {format_p_value(p)}")

            elif test == "chi_square_independence":
                if not grouping_var:
                    return ToolResult(success=False, error="grouping_var required")
                contingency = pd.crosstab(df[variable], df[grouping_var])
                chi2, p, dof, expected = scipy_stats.chi2_contingency(contingency)
                n = contingency.sum().sum()
                k = min(contingency.shape) - 1
                v = np.sqrt(chi2 / (n * k)) if n * k > 0 else 0
                result_lines.append("**Chi-Square Test of Independence**")
                result_lines.append(f"APA: {format_chi_square(chi2, dof, n, p, v)}")

            else:
                return ToolResult(success=False, error=f"Unknown test: {test}")

            return ToolResult(success=True, content="\n".join(result_lines))

        except Exception as e:
            return ToolResult(success=False, error=f"Hypothesis test failed: {e}")


class CreateVisualizationTool(Tool):
    """Generate publication-quality figures."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "create_visualization"

    @property
    def description(self) -> str:
        return (
            "Generate publication-quality figures for academic papers. "
            "Supports: line, bar, scatter, heatmap, violin, box, histogram. "
            "Uses colorblind-friendly palette. Output: PDF or PNG at 300+ DPI."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "plot_type": {
                    "type": "string",
                    "enum": ["line", "bar", "scatter", "heatmap", "violin", "box", "histogram"],
                },
                "x_var": {"type": "string", "description": "X-axis variable"},
                "y_var": {"type": "string", "description": "Y-axis variable"},
                "hue_var": {"type": "string", "description": "Color grouping variable (optional)"},
                "title": {"type": "string", "description": "Figure title"},
                "xlabel": {"type": "string", "description": "X-axis label"},
                "ylabel": {"type": "string", "description": "Y-axis label"},
                "output_path": {"type": "string", "description": "Output file path (e.g., analysis/figures/fig1.pdf)"},
            },
            "required": ["data_path", "plot_type", "output_path"],
        }

    async def execute(
        self,
        data_path: str,
        plot_type: str,
        output_path: str,
        x_var: str | None = None,
        y_var: str | None = None,
        hue_var: str | None = None,
        title: str = "",
        xlabel: str = "",
        ylabel: str = "",
        **kwargs,
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            import seaborn as sns

            full_data = Path(self._workspace_dir) / data_path if not Path(data_path).is_absolute() else Path(data_path)
            df = pd.read_csv(str(full_data))

            # Publication style
            OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]
            plt.rcParams.update(
                {
                    "figure.figsize": (89 / 25.4, 89 / 25.4 * 0.75),
                    "figure.dpi": 300,
                    "savefig.dpi": 300,
                    "savefig.bbox": "tight",
                    "font.family": "sans-serif",
                    "font.size": 8,
                    "axes.linewidth": 0.5,
                    "axes.spines.top": False,
                    "axes.spines.right": False,
                    "axes.prop_cycle": plt.cycler("color", OKABE_ITO),
                    "pdf.fonttype": 42,
                    "ps.fonttype": 42,
                }
            )

            fig, ax = plt.subplots()

            if plot_type == "scatter":
                sns.scatterplot(data=df, x=x_var, y=y_var, hue=hue_var, ax=ax, s=20, alpha=0.7)
            elif plot_type == "line":
                sns.lineplot(data=df, x=x_var, y=y_var, hue=hue_var, ax=ax)
            elif plot_type == "bar":
                sns.barplot(data=df, x=x_var, y=y_var, hue=hue_var, ax=ax)
            elif plot_type == "box":
                sns.boxplot(data=df, x=x_var, y=y_var, hue=hue_var, ax=ax)
            elif plot_type == "violin":
                sns.violinplot(data=df, x=x_var, y=y_var, hue=hue_var, ax=ax)
            elif plot_type == "histogram":
                col = y_var or x_var
                sns.histplot(data=df, x=col, hue=hue_var, ax=ax, kde=True)
            elif plot_type == "heatmap":
                corr = df.select_dtypes(include=[np.number]).corr()
                sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, ax=ax, square=True)

            if title:
                ax.set_title(title, fontsize=9, fontweight="bold")
            if xlabel:
                ax.set_xlabel(xlabel)
            if ylabel:
                ax.set_ylabel(ylabel)

            # Save
            full_output = (
                Path(self._workspace_dir) / output_path if not Path(output_path).is_absolute() else Path(output_path)
            )
            full_output.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(str(full_output))
            plt.close(fig)

            return ToolResult(success=True, content=f"Figure saved to: {full_output} (300 DPI, colorblind-safe)")

        except ImportError:
            return ToolResult(
                success=False, error="matplotlib/seaborn not installed. Run: pip install matplotlib seaborn"
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Visualization failed: {e}")


class TimeSeriesAnalysisTool(Tool):
    """Perform time series analysis including ARIMA, VAR, cointegration, and unit root tests.

    Supports stationarity testing (ADF, KPSS, Phillips-Perron), ARIMA/SARIMAX modeling,
    VAR/VECM multivariate models, and cointegration analysis. Results are formatted
    in APA 7th edition style with full model diagnostics.
    """

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "time_series_analysis"

    @property
    def description(self) -> str:
        return (
            "Perform time series analysis: ARIMA, VAR, VECM models with unit root tests "
            "(ADF, KPSS, Phillips-Perron), cointegration tests, and model diagnostics. "
            "Returns APA-formatted results with information criteria and residual diagnostics."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "date_column": {"type": "string", "description": "Name of the date/time column"},
                "value_columns": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Column(s) containing the time series values",
                },
                "model_type": {
                    "type": "string",
                    "enum": ["arima", "var", "vecm"],
                    "description": "Type of time series model (default: arima)",
                },
                "lags": {"type": "integer", "description": "Number of lags (default: auto-select)"},
                "test_stationarity": {
                    "type": "boolean",
                    "description": "Run unit root tests before modeling (default: true)",
                },
            },
            "required": ["data_path", "date_column", "value_columns"],
        }

    async def execute(
        self,
        data_path: str,
        date_column: str,
        value_columns: list[str],
        model_type: str = "arima",
        lags: int | None = None,
        test_stationarity: bool = True,
        **kwargs,
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        try:
            import statsmodels.api as sm
            from statsmodels.tsa.stattools import adfuller, kpss

            from ..research.apa_formatter import format_p_value
        except ImportError:
            return ToolResult(success=False, error="statsmodels is required. Run: pip install statsmodels")

        try:
            full_path = Path(self._workspace_dir) / data_path if not Path(data_path).is_absolute() else Path(data_path)
            df = pd.read_csv(str(full_path), parse_dates=[date_column])
            df = df.sort_values(date_column).set_index(date_column)

            missing = [c for c in value_columns if c not in df.columns]
            if missing:
                return ToolResult(success=False, error=f"Columns not found: {missing}. Available: {list(df.columns)}")

            ts_df = df[value_columns].dropna()
            lines: list[str] = ["## Time Series Analysis\n"]
            results_data: dict[str, Any] = {"model_type": model_type}

            # ── Unit root / stationarity tests ──
            if test_stationarity:
                lines.append("### Unit Root & Stationarity Tests\n")
                stationarity_results: dict[str, Any] = {}
                for col in value_columns:
                    series = ts_df[col].dropna()
                    lines.append(f"**{col}**")

                    # ADF test
                    adf_stat, adf_p, adf_lags, adf_nobs, adf_crit, _ = adfuller(series, autolag="AIC")
                    lines.append(f"  ADF: statistic = {adf_stat:.4f}, p {format_p_value(adf_p)}, lags = {adf_lags}")

                    # KPSS test
                    try:
                        kpss_stat, kpss_p, kpss_lags, kpss_crit = kpss(series, regression="c", nlags="auto")
                        lines.append(
                            f"  KPSS: statistic = {kpss_stat:.4f}, p {format_p_value(kpss_p)}, lags = {kpss_lags}"
                        )
                    except Exception:
                        kpss_stat, kpss_p = None, None
                        lines.append("  KPSS: could not be computed")

                    # Phillips-Perron via arch (optional)
                    pp_stat, pp_p = None, None
                    try:
                        from arch.unitroot import PhillipsPerron

                        pp = PhillipsPerron(series)
                        pp_stat, pp_p = float(pp.stat), float(pp.pvalue)
                        lines.append(f"  Phillips-Perron: statistic = {pp_stat:.4f}, p {format_p_value(pp_p)}")
                    except ImportError:
                        lines.append("  Phillips-Perron: skipped (install `arch` package)")
                    except Exception:
                        lines.append("  Phillips-Perron: could not be computed")

                    lines.append("")
                    stationarity_results[col] = {
                        "adf": {"statistic": round(adf_stat, 4), "p_value": round(adf_p, 4), "lags": adf_lags},
                        "kpss": {
                            "statistic": round(kpss_stat, 4) if kpss_stat is not None else None,
                            "p_value": round(kpss_p, 4) if kpss_p is not None else None,
                        },
                        "pp": {
                            "statistic": round(pp_stat, 4) if pp_stat is not None else None,
                            "p_value": round(pp_p, 4) if pp_p is not None else None,
                        },
                    }
                results_data["stationarity"] = stationarity_results

            # ── ARIMA ──
            if model_type == "arima":
                col = value_columns[0]
                series = ts_df[col].dropna()
                lines.append("### ARIMA Model\n")

                if lags is not None:
                    order = (lags, 1, lags)
                else:
                    # Auto-select via AIC grid search
                    best_aic = np.inf
                    order = (1, 1, 1)
                    for p in range(4):
                        for q in range(4):
                            try:
                                trial = sm.tsa.ARIMA(series, order=(p, 1, q)).fit()
                                if trial.aic < best_aic:
                                    best_aic = trial.aic
                                    order = (p, 1, q)
                            except Exception:
                                continue

                model = sm.tsa.ARIMA(series, order=order).fit()
                lines.append(f"**Order:** ARIMA{order}")
                lines.append(f"**N:** {int(model.nobs)}")
                lines.append(f"**AIC:** {model.aic:.2f}")
                lines.append(f"**BIC:** {model.bic:.2f}")
                lines.append(f"**Log-Likelihood:** {model.llf:.2f}")
                lines.append("")

                # Coefficient table
                lines.append("| Parameter | Coef. | Std. Err. | z | p |")
                lines.append("|-----------|-------|-----------|---|---|")
                for param in model.params.index:
                    coef = model.params[param]
                    se = model.bse[param]
                    z = model.tvalues[param]
                    p = model.pvalues[param]
                    lines.append(f"| {param} | {coef:.4f} | {se:.4f} | {z:.2f} | {format_p_value(p)} |")

                # Ljung-Box residual test
                lb_test = sm.stats.acorr_ljungbox(model.resid, lags=[10], return_df=True)
                lb_stat = float(lb_test["lb_stat"].iloc[0])
                lb_p = float(lb_test["lb_pvalue"].iloc[0])
                lines.append("")
                lines.append(
                    f"**Ljung-Box Q(10):** {lb_stat:.2f}, p {format_p_value(lb_p)} "
                    f"({'no serial correlation' if lb_p > 0.05 else 'serial correlation detected'})"
                )

                results_data["arima"] = {
                    "order": list(order),
                    "aic": round(model.aic, 2),
                    "bic": round(model.bic, 2),
                    "log_likelihood": round(model.llf, 2),
                    "coefficients": {k: round(float(v), 4) for k, v in model.params.items()},
                    "p_values": {k: round(float(v), 4) for k, v in model.pvalues.items()},
                    "ljung_box": {"statistic": round(lb_stat, 2), "p_value": round(lb_p, 4)},
                }

            # ── VAR ──
            elif model_type == "var":
                if len(value_columns) < 2:
                    return ToolResult(success=False, error="VAR requires at least 2 value_columns")
                from statsmodels.tsa.api import VAR as VARModel

                lines.append("### VAR Model\n")
                var_model = VARModel(ts_df[value_columns])
                if lags is not None:
                    var_result = var_model.fit(maxlags=lags)
                else:
                    var_result = var_model.fit(ic="aic")

                lines.append(f"**Lag Order:** {var_result.k_ar}")
                lines.append(f"**N:** {var_result.nobs}")
                lines.append(f"**AIC:** {var_result.aic:.2f}")
                lines.append(f"**BIC:** {var_result.bic:.2f}")
                lines.append("")

                # Granger causality
                lines.append("### Granger Causality Tests\n")
                granger_results: dict[str, Any] = {}
                for caused in value_columns:
                    for causing in value_columns:
                        if caused == causing:
                            continue
                        gc = var_result.test_causality(caused, [causing], kind="f")
                        gc_p = float(gc.pvalue)
                        lines.append(
                            f"  {causing} → {caused}: F = {float(gc.test_statistic):.2f}, p {format_p_value(gc_p)}"
                        )
                        granger_results[f"{causing}->{caused}"] = {
                            "f_statistic": round(float(gc.test_statistic), 2),
                            "p_value": round(gc_p, 4),
                        }

                # Cointegration (Johansen)
                lines.append("\n### Johansen Cointegration Test\n")
                try:
                    from statsmodels.tsa.vector_ar.vecm import coint_johansen

                    joh = coint_johansen(ts_df[value_columns].dropna(), det_order=0, k_ar_diff=var_result.k_ar)
                    lines.append("| Hypothesis | Trace Stat | 5% CV | Max-Eigen Stat | 5% CV |")
                    lines.append("|------------|-----------|-------|----------------|-------|")
                    for i in range(joh.lr1.shape[0]):
                        lines.append(
                            f"| r ≤ {i} | {joh.lr1[i]:.2f} | {joh.cvt[i, 1]:.2f} "
                            f"| {joh.lr2[i]:.2f} | {joh.cvm[i, 1]:.2f} |"
                        )
                except Exception as coint_err:
                    lines.append(f"Cointegration test could not be computed: {coint_err}")

                results_data["var"] = {
                    "lag_order": var_result.k_ar,
                    "aic": round(var_result.aic, 2),
                    "bic": round(var_result.bic, 2),
                    "granger_causality": granger_results,
                }

            # ── VECM ──
            elif model_type == "vecm":
                if len(value_columns) < 2:
                    return ToolResult(success=False, error="VECM requires at least 2 value_columns")
                from statsmodels.tsa.vector_ar.vecm import VECM as VECMModel
                from statsmodels.tsa.vector_ar.vecm import select_coint_rank

                lines.append("### VECM Model\n")
                k_ar = lags if lags is not None else 2
                vecm = VECMModel(ts_df[value_columns].dropna(), k_ar_diff=k_ar, deterministic="ci")
                vecm_result = vecm.fit()

                # Cointegration rank selection
                rank_test = select_coint_rank(ts_df[value_columns].dropna(), det_order=0, k_ar_diff=k_ar)
                lines.append(f"**Selected Cointegration Rank:** {rank_test.rank}")
                lines.append(f"**Lag Order (differences):** {k_ar}")
                lines.append("")

                # Cointegrating vectors
                lines.append("**Cointegrating Vector(s):**")
                beta = vecm_result.beta
                for i in range(beta.shape[1]):
                    vec_str = ", ".join(f"{v:.4f}" for v in beta[:, i])
                    lines.append(f"  β{i + 1} = [{vec_str}]")

                results_data["vecm"] = {
                    "lag_order": k_ar,
                    "coint_rank": int(rank_test.rank),
                    "beta": beta.tolist(),
                }

            else:
                return ToolResult(
                    success=False, error=f"Unknown model_type: {model_type}. Choose from: arima, var, vecm"
                )

            # Save results
            results_path = Path(self._workspace_dir) / "analysis" / "results" / "time_series.json"
            results_path.parent.mkdir(parents=True, exist_ok=True)
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            result_text = "\n".join(lines)
            result_text += f"\n\n*Results saved to: {results_path}*"
            return ToolResult(success=True, content=result_text)

        except Exception as e:
            return ToolResult(success=False, error=f"Time series analysis failed: {e}")


class BayesianAnalysisTool(Tool):
    """Perform Bayesian statistical analysis with posterior inference and model diagnostics.

    Uses bambi for formula-based model specification, PyMC for MCMC sampling,
    and ArviZ for convergence diagnostics and model comparison. Returns posterior
    summaries, HDI intervals, R-hat, ESS, and WAIC/LOO information criteria.
    """

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "bayesian_analysis"

    @property
    def description(self) -> str:
        return (
            "Perform Bayesian regression analysis using MCMC sampling. Supports "
            "Gaussian, Binomial, and Poisson families with configurable priors. "
            "Returns posterior summaries, HDI intervals, convergence diagnostics "
            "(R-hat, ESS), and model comparison (WAIC/LOO)."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "formula": {
                    "type": "string",
                    "description": "R-style formula (e.g., 'y ~ x1 + x2')",
                },
                "family": {
                    "type": "string",
                    "enum": ["gaussian", "binomial", "poisson"],
                    "description": "Response distribution family (default: gaussian)",
                },
                "prior_type": {
                    "type": "string",
                    "enum": ["default", "weakly_informative", "informative"],
                    "description": "Prior specification strategy (default: default)",
                },
                "n_samples": {
                    "type": "integer",
                    "description": "Number of posterior samples per chain (default: 2000)",
                },
                "n_chains": {
                    "type": "integer",
                    "description": "Number of MCMC chains (default: 4)",
                },
            },
            "required": ["data_path", "formula"],
        }

    async def execute(
        self,
        data_path: str,
        formula: str,
        family: str = "gaussian",
        prior_type: str = "default",
        n_samples: int = 2000,
        n_chains: int = 4,
        **kwargs,
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        try:
            import arviz as az
            import bambi as bmb
        except ImportError:
            return ToolResult(
                success=False,
                error=("Bayesian analysis requires bambi, pymc, and arviz. Run: pip install bambi pymc arviz"),
            )

        try:
            full_path = Path(self._workspace_dir) / data_path if not Path(data_path).is_absolute() else Path(data_path)
            df = pd.read_csv(str(full_path))

            lines: list[str] = ["## Bayesian Analysis\n"]
            lines.append(f"**Formula:** {formula}")
            lines.append(f"**Family:** {family}")
            lines.append(f"**Priors:** {prior_type}")
            lines.append(f"**Chains:** {n_chains}, Samples: {n_samples}\n")

            # Build model
            priors: dict[str, Any] | None = None
            if prior_type == "weakly_informative":
                priors = {
                    "Intercept": bmb.Prior("Normal", mu=0, sigma=10),
                    "common": bmb.Prior("Normal", mu=0, sigma=5),
                }
            elif prior_type == "informative":
                priors = {
                    "Intercept": bmb.Prior("Normal", mu=0, sigma=2.5),
                    "common": bmb.Prior("Normal", mu=0, sigma=1),
                }

            model = bmb.Model(formula, df, family=family, priors=priors)
            idata = model.fit(draws=n_samples, chains=n_chains, random_seed=42)

            # Posterior summary
            summary = az.summary(
                idata,
                hdi_prob=0.95,
                stat_funcs={"mean": np.mean, "sd": np.std},
            )
            lines.append("### Posterior Summary\n")
            header_cols = ["mean", "sd", "hdi_2.5%", "hdi_97.5%", "r_hat", "ess_bulk", "ess_tail"]
            available_cols = [c for c in header_cols if c in summary.columns]
            lines.append("| Parameter | " + " | ".join(available_cols) + " |")
            lines.append("|" + "---|" * (len(available_cols) + 1))
            for param in summary.index:
                vals = " | ".join(
                    f"{summary.loc[param, c]:.4f}" if c in summary.columns else "—" for c in available_cols
                )
                lines.append(f"| {param} | {vals} |")

            # Convergence diagnostics
            lines.append("\n### Convergence Diagnostics\n")
            if "r_hat" in summary.columns:
                max_rhat = float(summary["r_hat"].max())
                lines.append(
                    f"**Max R-hat:** {max_rhat:.4f} "
                    f"({'✓ converged' if max_rhat < 1.05 else '⚠ potential non-convergence'})"
                )
            if "ess_bulk" in summary.columns:
                min_ess = float(summary["ess_bulk"].min())
                lines.append(
                    f"**Min ESS (bulk):** {min_ess:.0f} "
                    f"({'✓ adequate' if min_ess > 400 else '⚠ low effective sample size'})"
                )

            # Model comparison (WAIC and LOO)
            lines.append("\n### Model Fit\n")
            model_fit: dict[str, Any] = {}
            try:
                waic = az.waic(idata)
                lines.append(f"**WAIC:** {waic.elpd_waic:.2f} (SE = {waic.se:.2f})")
                model_fit["waic"] = {
                    "elpd": round(float(waic.elpd_waic), 2),
                    "se": round(float(waic.se), 2),
                    "p_waic": round(float(waic.p_waic), 2),
                }
            except Exception:
                lines.append("**WAIC:** could not be computed")

            try:
                loo = az.loo(idata)
                lines.append(f"**LOO-CV:** {loo.elpd_loo:.2f} (SE = {loo.se:.2f})")
                model_fit["loo"] = {
                    "elpd": round(float(loo.elpd_loo), 2),
                    "se": round(float(loo.se), 2),
                    "p_loo": round(float(loo.p_loo), 2),
                }
            except Exception:
                lines.append("**LOO-CV:** could not be computed")

            # Save results
            results_data = {
                "formula": formula,
                "family": family,
                "prior_type": prior_type,
                "n_samples": n_samples,
                "n_chains": n_chains,
                "posterior_summary": {
                    param: {
                        col: round(float(summary.loc[param, col]), 4)
                        for col in available_cols
                        if col in summary.columns
                    }
                    for param in summary.index
                },
                "model_fit": model_fit,
            }
            results_path = Path(self._workspace_dir) / "analysis" / "results" / "bayesian.json"
            results_path.parent.mkdir(parents=True, exist_ok=True)
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            result_text = "\n".join(lines)
            result_text += f"\n\n*Results saved to: {results_path}*"
            return ToolResult(success=True, content=result_text)

        except Exception as e:
            return ToolResult(success=False, error=f"Bayesian analysis failed: {e}")


class CausalInferenceTool(Tool):
    """Perform causal inference analysis using structural causal models.

    Supports backdoor adjustment, instrumental variables, frontdoor criterion,
    and propensity score methods via the DoWhy library. Returns average treatment
    effects with confidence intervals and refutation test results.
    """

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "causal_inference"

    @property
    def description(self) -> str:
        return (
            "Perform causal inference analysis using DoWhy. Supports backdoor adjustment, "
            "instrumental variables, frontdoor criterion, and propensity score matching. "
            "Returns ATE, confidence intervals, and refutation test results."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "treatment": {"type": "string", "description": "Treatment variable name"},
                "outcome": {"type": "string", "description": "Outcome variable name"},
                "confounders": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of confounding variables",
                },
                "method": {
                    "type": "string",
                    "enum": ["backdoor", "iv", "frontdoor", "propensity_score"],
                    "description": "Causal estimation method (default: backdoor)",
                },
                "instrument": {
                    "type": "string",
                    "description": "Instrumental variable (required for iv method)",
                },
            },
            "required": ["data_path", "treatment", "outcome", "confounders"],
        }

    async def execute(
        self,
        data_path: str,
        treatment: str,
        outcome: str,
        confounders: list[str],
        method: str = "backdoor",
        instrument: str | None = None,
        **kwargs,
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        try:
            import dowhy  # noqa: F401
            from dowhy import CausalModel  # noqa: F401
        except ImportError:
            return ToolResult(
                success=False,
                error=("dowhy is required for causal inference. Run: pip install dowhy"),
            )

        try:
            from ..research.apa_formatter import format_ci, format_p_value

            full_path = Path(self._workspace_dir) / data_path if not Path(data_path).is_absolute() else Path(data_path)
            df = pd.read_csv(str(full_path))

            all_vars = [treatment, outcome] + confounders
            if instrument:
                all_vars.append(instrument)
            missing = [v for v in all_vars if v not in df.columns]
            if missing:
                return ToolResult(success=False, error=f"Variables not found: {missing}. Available: {list(df.columns)}")

            if method == "iv" and not instrument:
                return ToolResult(success=False, error="Instrumental variable (instrument) is required for iv method")

            lines: list[str] = ["## Causal Inference Analysis\n"]
            lines.append(f"**Treatment:** {treatment}")
            lines.append(f"**Outcome:** {outcome}")
            lines.append(f"**Confounders:** {', '.join(confounders)}")
            lines.append(f"**Method:** {method}")
            if instrument:
                lines.append(f"**Instrument:** {instrument}")
            lines.append("")

            # Build causal model
            instruments = [instrument] if instrument else None
            causal_model = CausalModel(
                data=df,
                treatment=treatment,
                outcome=outcome,
                common_causes=confounders,
                instruments=instruments,
            )

            # Identify estimand
            estimand = causal_model.identify_effect(proceed_when_unidentifiable=True)
            lines.append("### Identified Estimand\n")
            lines.append(f"{estimand}")
            lines.append("")

            # Estimate effect
            method_map = {
                "backdoor": "backdoor.linear_regression",
                "iv": "iv.instrumental_variable",
                "frontdoor": "frontdoor.two_stage_regression",
                "propensity_score": "backdoor.propensity_score_matching",
            }
            method_name = method_map.get(method, "backdoor.linear_regression")

            estimate = causal_model.estimate_effect(
                estimand,
                method_name=method_name,
                confidence_intervals=True,
            )

            ate = float(estimate.value)
            lines.append("### Causal Effect Estimate\n")
            lines.append(f"**Average Treatment Effect (ATE):** {ate:.4f}")

            ci_low = getattr(estimate, "get_confidence_intervals", None)
            if callable(ci_low):
                try:
                    ci = ci_low()
                    if ci is not None and len(ci) == 2:
                        lines.append(f"**{format_ci(float(ci[0]), float(ci[1]))}**")
                except Exception:
                    pass
            lines.append("")

            # Refutation tests
            lines.append("### Refutation Tests\n")
            refutation_results: dict[str, Any] = {}

            # Random common cause
            try:
                ref_random = causal_model.refute_estimate(
                    estimand,
                    estimate,
                    method_name="random_common_cause",
                )
                new_effect = float(ref_random.new_effect)
                lines.append(
                    f"**Random Common Cause:** new ATE = {new_effect:.4f}, "
                    f"p {format_p_value(float(ref_random.refutation_result['p_value']))}"
                    if hasattr(ref_random, "refutation_result") and isinstance(ref_random.refutation_result, dict)
                    else f"**Random Common Cause:** new ATE = {new_effect:.4f}"
                )
                refutation_results["random_common_cause"] = {"new_effect": round(new_effect, 4)}
            except Exception as ref_err:
                lines.append(f"**Random Common Cause:** could not be computed ({ref_err})")

            # Placebo treatment
            try:
                ref_placebo = causal_model.refute_estimate(
                    estimand,
                    estimate,
                    method_name="placebo_treatment_refuter",
                )
                placebo_effect = float(ref_placebo.new_effect)
                lines.append(f"**Placebo Treatment:** new ATE = {placebo_effect:.4f}")
                refutation_results["placebo_treatment"] = {"new_effect": round(placebo_effect, 4)}
            except Exception as ref_err:
                lines.append(f"**Placebo Treatment:** could not be computed ({ref_err})")

            # Data subset
            try:
                ref_subset = causal_model.refute_estimate(
                    estimand,
                    estimate,
                    method_name="data_subset_refuter",
                    subset_fraction=0.8,
                )
                subset_effect = float(ref_subset.new_effect)
                lines.append(f"**Data Subset (80%):** new ATE = {subset_effect:.4f}")
                refutation_results["data_subset"] = {"new_effect": round(subset_effect, 4)}
            except Exception as ref_err:
                lines.append(f"**Data Subset:** could not be computed ({ref_err})")

            # Save results
            results_data = {
                "treatment": treatment,
                "outcome": outcome,
                "confounders": confounders,
                "method": method,
                "ate": round(ate, 4),
                "refutation_tests": refutation_results,
            }
            results_path = Path(self._workspace_dir) / "analysis" / "results" / "causal_inference.json"
            results_path.parent.mkdir(parents=True, exist_ok=True)
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            result_text = "\n".join(lines)
            result_text += f"\n\n*Results saved to: {results_path}*"
            return ToolResult(success=True, content=result_text)

        except Exception as e:
            return ToolResult(success=False, error=f"Causal inference failed: {e}")


class SurvivalAnalysisTool(Tool):
    """Perform survival analysis with Kaplan-Meier, Cox PH, and AFT models.

    Uses the lifelines library for Kaplan-Meier survival curves, Cox proportional
    hazards regression, and accelerated failure time models. Returns survival
    probabilities, hazard ratios, log-rank tests, and concordance indices.
    """

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "survival_analysis"

    @property
    def description(self) -> str:
        return (
            "Perform survival analysis: Kaplan-Meier curves, Cox proportional hazards, "
            "and accelerated failure time (AFT) models. Returns survival curves, hazard "
            "ratios, log-rank tests, and concordance index with APA-formatted output."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "duration_col": {
                    "type": "string",
                    "description": "Column with time-to-event durations",
                },
                "event_col": {
                    "type": "string",
                    "description": "Column with event indicator (1 = event, 0 = censored)",
                },
                "group_col": {
                    "type": "string",
                    "description": "Optional grouping variable for stratified analysis",
                },
                "covariates": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Covariates for Cox PH or AFT models",
                },
                "model_type": {
                    "type": "string",
                    "enum": ["kaplan_meier", "cox_ph", "aft"],
                    "description": "Survival model type (default: kaplan_meier)",
                },
            },
            "required": ["data_path", "duration_col", "event_col"],
        }

    async def execute(
        self,
        data_path: str,
        duration_col: str,
        event_col: str,
        group_col: str | None = None,
        covariates: list[str] | None = None,
        model_type: str = "kaplan_meier",
        **kwargs,
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        try:
            from lifelines import (
                CoxPHFitter,  # noqa: F401
                KaplanMeierFitter,  # noqa: F401
                LogNormalAFTFitter,  # noqa: F401
                WeibullAFTFitter,  # noqa: F401
            )
            from lifelines.statistics import logrank_test
        except ImportError:
            return ToolResult(
                success=False,
                error=("lifelines is required for survival analysis. Run: pip install lifelines"),
            )

        try:
            from ..research.apa_formatter import format_p_value

            full_path = Path(self._workspace_dir) / data_path if not Path(data_path).is_absolute() else Path(data_path)
            df = pd.read_csv(str(full_path))

            required_cols = [duration_col, event_col]
            if group_col:
                required_cols.append(group_col)
            if covariates:
                required_cols.extend(covariates)
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                return ToolResult(success=False, error=f"Columns not found: {missing}. Available: {list(df.columns)}")

            lines: list[str] = ["## Survival Analysis\n"]
            results_data: dict[str, Any] = {"model_type": model_type}

            # ── Kaplan-Meier ──
            if model_type == "kaplan_meier":
                lines.append("### Kaplan-Meier Survival Estimates\n")

                if group_col:
                    groups = df[group_col].dropna().unique()
                    km_results: dict[str, Any] = {}

                    for group in sorted(groups):
                        mask = df[group_col] == group
                        kmf = KaplanMeierFitter()
                        kmf.fit(
                            df.loc[mask, duration_col],
                            event_observed=df.loc[mask, event_col],
                            label=str(group),
                        )
                        median_surv = kmf.median_survival_time_
                        lines.append(f"**Group: {group}**")
                        lines.append(f"  N = {mask.sum()}, Events = {int(df.loc[mask, event_col].sum())}")
                        lines.append(f"  Median survival time: {median_surv:.2f}")
                        lines.append("")
                        km_results[str(group)] = {
                            "n": int(mask.sum()),
                            "events": int(df.loc[mask, event_col].sum()),
                            "median_survival": round(float(median_surv), 2) if np.isfinite(median_surv) else None,
                        }

                    # Log-rank test
                    if len(groups) == 2:
                        g1_mask = df[group_col] == groups[0]
                        g2_mask = df[group_col] == groups[1]
                        lr = logrank_test(
                            df.loc[g1_mask, duration_col],
                            df.loc[g2_mask, duration_col],
                            event_observed_A=df.loc[g1_mask, event_col],
                            event_observed_B=df.loc[g2_mask, event_col],
                        )
                        lines.append("### Log-Rank Test\n")
                        lines.append(f"χ²(1) = {lr.test_statistic:.2f}, p {format_p_value(lr.p_value)}")
                        km_results["log_rank"] = {
                            "statistic": round(float(lr.test_statistic), 2),
                            "p_value": round(float(lr.p_value), 4),
                        }
                    elif len(groups) > 2:
                        # Pairwise log-rank for multiple groups
                        lines.append("### Pairwise Log-Rank Tests\n")
                        from itertools import combinations

                        for g1, g2 in combinations(sorted(groups), 2):
                            m1 = df[group_col] == g1
                            m2 = df[group_col] == g2
                            lr = logrank_test(
                                df.loc[m1, duration_col],
                                df.loc[m2, duration_col],
                                event_observed_A=df.loc[m1, event_col],
                                event_observed_B=df.loc[m2, event_col],
                            )
                            lines.append(
                                f"  {g1} vs {g2}: χ²(1) = {lr.test_statistic:.2f}, p {format_p_value(lr.p_value)}"
                            )

                    results_data["kaplan_meier"] = km_results
                else:
                    kmf = KaplanMeierFitter()
                    kmf.fit(
                        df[duration_col],
                        event_observed=df[event_col],
                    )
                    median_surv = kmf.median_survival_time_
                    n_events = int(df[event_col].sum())
                    lines.append(f"**N:** {len(df)}, **Events:** {n_events}")
                    lines.append(f"**Median Survival Time:** {median_surv:.2f}")
                    results_data["kaplan_meier"] = {
                        "n": len(df),
                        "events": n_events,
                        "median_survival": round(float(median_surv), 2) if np.isfinite(median_surv) else None,
                    }

            # ── Cox Proportional Hazards ──
            elif model_type == "cox_ph":
                if not covariates:
                    return ToolResult(success=False, error="covariates are required for Cox PH model")

                lines.append("### Cox Proportional Hazards Model\n")
                cox_cols = [duration_col, event_col] + covariates
                cox_df = df[cox_cols].dropna()

                cph = CoxPHFitter()
                cph.fit(cox_df, duration_col=duration_col, event_col=event_col)

                lines.append(f"**N:** {cph.summary.shape[0] and int(cph.event_observed.shape[0])}")
                lines.append(f"**Events:** {int(cph.event_observed.sum())}")
                lines.append(f"**Concordance Index:** {cph.concordance_index_:.4f}")
                lines.append(f"**Log-Likelihood:** {cph.log_likelihood_:.2f}")
                lines.append("")

                # Coefficient table
                lines.append("| Covariate | HR | Coef. | SE | z | p | 95% CI |")
                lines.append("|-----------|----|----|----|----|---|--------|")
                summary_df = cph.summary
                for cov in summary_df.index:
                    hr = float(summary_df.loc[cov, "exp(coef)"])
                    coef = float(summary_df.loc[cov, "coef"])
                    se = float(summary_df.loc[cov, "se(coef)"])
                    z = float(summary_df.loc[cov, "z"])
                    p = float(summary_df.loc[cov, "p"])
                    ci_low = float(summary_df.loc[cov, "exp(coef) lower 95%"])
                    ci_high = float(summary_df.loc[cov, "exp(coef) upper 95%"])
                    lines.append(
                        f"| {cov} | {hr:.4f} | {coef:.4f} | {se:.4f} "
                        f"| {z:.2f} | {format_p_value(p)} | [{ci_low:.4f}, {ci_high:.4f}] |"
                    )

                # Proportional hazards test
                lines.append("\n### Proportional Hazards Test\n")
                try:
                    ph_test = cph.check_assumptions(cox_df, p_value_threshold=0.05, show_plots=False)
                    if not ph_test:
                        lines.append("PH assumption satisfied for all covariates (p > .05)")
                    else:
                        lines.append("⚠ PH assumption may be violated for some covariates")
                except Exception:
                    lines.append("PH assumption test could not be completed")

                results_data["cox_ph"] = {
                    "concordance_index": round(cph.concordance_index_, 4),
                    "log_likelihood": round(cph.log_likelihood_, 2),
                    "hazard_ratios": {
                        cov: round(float(summary_df.loc[cov, "exp(coef)"]), 4) for cov in summary_df.index
                    },
                    "p_values": {cov: round(float(summary_df.loc[cov, "p"]), 4) for cov in summary_df.index},
                }

            # ── Accelerated Failure Time ──
            elif model_type == "aft":
                if not covariates:
                    return ToolResult(success=False, error="covariates are required for AFT model")

                lines.append("### Accelerated Failure Time Model (Weibull)\n")
                aft_cols = [duration_col, event_col] + covariates
                aft_df = df[aft_cols].dropna()

                aft = WeibullAFTFitter()
                aft.fit(aft_df, duration_col=duration_col, event_col=event_col)

                lines.append(f"**N:** {int(aft.event_observed.shape[0])}")
                lines.append(f"**Events:** {int(aft.event_observed.sum())}")
                lines.append(f"**Concordance Index:** {aft.concordance_index_:.4f}")
                lines.append(f"**AIC:** {aft.AIC_:.2f}")
                lines.append("")

                # Coefficient table
                lines.append("| Parameter | Coef. | SE | z | p | 95% CI |")
                lines.append("|-----------|-------|----|---|---|--------|")
                summary_df = aft.summary
                for idx in summary_df.index:
                    param_name = f"{idx[0]}:{idx[1]}" if isinstance(idx, tuple) else str(idx)
                    coef = float(summary_df.loc[idx, "coef"])
                    se = float(summary_df.loc[idx, "se(coef)"])
                    z = float(summary_df.loc[idx, "z"])
                    p = float(summary_df.loc[idx, "p"])
                    ci_low = float(summary_df.loc[idx, "coef lower 95%"])
                    ci_high = float(summary_df.loc[idx, "coef upper 95%"])
                    lines.append(
                        f"| {param_name} | {coef:.4f} | {se:.4f} "
                        f"| {z:.2f} | {format_p_value(p)} | [{ci_low:.4f}, {ci_high:.4f}] |"
                    )

                results_data["aft"] = {
                    "concordance_index": round(aft.concordance_index_, 4),
                    "aic": round(aft.AIC_, 2),
                    "coefficients": {
                        (f"{idx[0]}:{idx[1]}" if isinstance(idx, tuple) else str(idx)): round(
                            float(summary_df.loc[idx, "coef"]), 4
                        )
                        for idx in summary_df.index
                    },
                }

            else:
                return ToolResult(
                    success=False, error=f"Unknown model_type: {model_type}. Choose from: kaplan_meier, cox_ph, aft"
                )

            # Save results
            results_path = Path(self._workspace_dir) / "analysis" / "results" / "survival.json"
            results_path.parent.mkdir(parents=True, exist_ok=True)
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            result_text = "\n".join(lines)
            result_text += f"\n\n*Results saved to: {results_path}*"
            return ToolResult(success=True, content=result_text)

        except Exception as e:
            return ToolResult(success=False, error=f"Survival analysis failed: {e}")


class NonparametricTestTool(Tool):
    """Perform nonparametric statistical tests with effect sizes.

    Supports Mann-Whitney U, Kruskal-Wallis H, Wilcoxon signed-rank,
    Friedman, Spearman rank correlation, and Kendall's tau. Returns test
    statistics, p-values, effect sizes, and APA 7th edition formatted reports.
    """

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "nonparametric_test"

    @property
    def description(self) -> str:
        return (
            "Perform nonparametric statistical tests: Mann-Whitney U, Kruskal-Wallis H, "
            "Wilcoxon signed-rank, Friedman, Spearman correlation, and Kendall's tau. "
            "Returns test statistics, p-values, effect sizes (rank-biserial r, "
            "epsilon-squared), and APA 7th edition formatted reports."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "test_type": {
                    "type": "string",
                    "enum": [
                        "mann_whitney",
                        "kruskal_wallis",
                        "wilcoxon",
                        "friedman",
                        "spearman",
                        "kendall",
                    ],
                    "description": "Nonparametric test to perform",
                },
                "variable1": {"type": "string", "description": "First variable (or dependent variable)"},
                "variable2": {
                    "type": "string",
                    "description": "Second variable (for paired tests or correlations)",
                },
                "group_variable": {
                    "type": "string",
                    "description": "Grouping variable (for between-group tests)",
                },
            },
            "required": ["data_path", "test_type", "variable1"],
        }

    async def execute(
        self,
        data_path: str,
        test_type: str,
        variable1: str,
        variable2: str | None = None,
        group_variable: str | None = None,
        **kwargs,
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        try:
            from scipy import stats as scipy_stats

            from ..research.apa_formatter import format_p_value
        except ImportError:
            return ToolResult(success=False, error="scipy is required. Run: pip install scipy")

        try:
            full_path = Path(self._workspace_dir) / data_path if not Path(data_path).is_absolute() else Path(data_path)
            df = pd.read_csv(str(full_path))

            lines: list[str] = [f"## Nonparametric Test: {test_type}\n"]
            results_data: dict[str, Any] = {"test_type": test_type}

            # ── Mann-Whitney U ──
            if test_type == "mann_whitney":
                if not group_variable:
                    return ToolResult(success=False, error="group_variable is required for Mann-Whitney U test")
                groups = df[group_variable].dropna().unique()
                if len(groups) != 2:
                    return ToolResult(
                        success=False, error=f"Mann-Whitney U requires exactly 2 groups, got {len(groups)}"
                    )

                g1 = df[df[group_variable] == groups[0]][variable1].dropna()
                g2 = df[df[group_variable] == groups[1]][variable1].dropna()
                n1, n2 = len(g1), len(g2)
                stat, p = scipy_stats.mannwhitneyu(g1, g2, alternative="two-sided")

                # Rank-biserial correlation as effect size
                r_rb = 1 - (2 * stat) / (n1 * n2)

                lines.append("**Mann-Whitney U Test**")
                lines.append(f"Group 1 ({groups[0]}): n = {n1}, Mdn = {g1.median():.2f}")
                lines.append(f"Group 2 ({groups[1]}): n = {n2}, Mdn = {g2.median():.2f}")
                lines.append("")
                lines.append(f"*U* = {stat:.2f}, *p* {format_p_value(p)}, *r*_rb = {r_rb:.3f}")
                lines.append("")
                lines.append("**APA Report:**")
                lines.append(
                    f"A Mann-Whitney U test indicated that {variable1} was "
                    f"{'significantly' if p < 0.05 else 'not significantly'} different "
                    f"between {groups[0]} (Mdn = {g1.median():.2f}) and "
                    f"{groups[1]} (Mdn = {g2.median():.2f}), "
                    f"U = {stat:.2f}, p {format_p_value(p)}, r_rb = {r_rb:.3f}."
                )

                results_data.update(
                    {
                        "statistic": round(float(stat), 2),
                        "p_value": round(float(p), 4),
                        "effect_size": {"rank_biserial_r": round(r_rb, 3)},
                        "groups": {
                            str(groups[0]): {"n": n1, "median": round(float(g1.median()), 2)},
                            str(groups[1]): {"n": n2, "median": round(float(g2.median()), 2)},
                        },
                    }
                )

            # ── Kruskal-Wallis H ──
            elif test_type == "kruskal_wallis":
                if not group_variable:
                    return ToolResult(success=False, error="group_variable is required for Kruskal-Wallis test")
                group_data = [g[variable1].dropna().values for _, g in df.groupby(group_variable)]
                if len(group_data) < 2:
                    return ToolResult(success=False, error="Kruskal-Wallis requires at least 2 groups")

                stat, p = scipy_stats.kruskal(*group_data)
                n_total = sum(len(g) for g in group_data)
                k = len(group_data)

                # Epsilon-squared effect size: H / ((n² - 1) / (n + 1))
                epsilon_sq = float(stat) / ((n_total**2 - 1) / (n_total + 1))

                lines.append("**Kruskal-Wallis H Test**")
                lines.append(f"Number of groups: {k}, Total N: {n_total}")
                lines.append("")
                lines.append(f"*H*({k - 1}) = {stat:.2f}, *p* {format_p_value(p)}, ε² = {epsilon_sq:.3f}")
                lines.append("")
                lines.append("**Group Medians:**")
                for name, g in df.groupby(group_variable):
                    mdn = g[variable1].dropna().median()
                    lines.append(f"  {name}: Mdn = {mdn:.2f}, n = {g[variable1].dropna().shape[0]}")
                lines.append("")
                lines.append("**APA Report:**")
                lines.append(
                    f"A Kruskal-Wallis H test showed a "
                    f"{'statistically significant' if p < 0.05 else 'non-significant'} "
                    f"difference in {variable1} across groups, "
                    f"H({k - 1}) = {stat:.2f}, p {format_p_value(p)}, ε² = {epsilon_sq:.3f}."
                )

                results_data.update(
                    {
                        "statistic": round(float(stat), 2),
                        "p_value": round(float(p), 4),
                        "df": k - 1,
                        "effect_size": {"epsilon_squared": round(epsilon_sq, 3)},
                    }
                )

            # ── Wilcoxon Signed-Rank ──
            elif test_type == "wilcoxon":
                if not variable2:
                    return ToolResult(success=False, error="variable2 is required for Wilcoxon signed-rank test")
                x = df[variable1].dropna()
                y = df[variable2].dropna()
                # Align on common indices
                common = x.index.intersection(y.index)
                x, y = x.loc[common], y.loc[common]
                n = len(x)

                stat, p = scipy_stats.wilcoxon(x, y)

                # Rank-biserial r for Wilcoxon: r = 1 - (2T) / (n(n+1)/2)
                r_rb = 1 - (2 * stat) / (n * (n + 1) / 2)

                lines.append("**Wilcoxon Signed-Rank Test**")
                lines.append(f"Pair: {variable1} vs {variable2}, n = {n}")
                lines.append(f"Mdn({variable1}) = {x.median():.2f}, Mdn({variable2}) = {y.median():.2f}")
                lines.append("")
                lines.append(f"*T* = {stat:.2f}, *p* {format_p_value(p)}, *r*_rb = {r_rb:.3f}")
                lines.append("")
                lines.append("**APA Report:**")
                lines.append(
                    f"A Wilcoxon signed-rank test indicated that {variable1} "
                    f"(Mdn = {x.median():.2f}) was "
                    f"{'significantly' if p < 0.05 else 'not significantly'} different "
                    f"from {variable2} (Mdn = {y.median():.2f}), "
                    f"T = {stat:.2f}, p {format_p_value(p)}, r_rb = {r_rb:.3f}."
                )

                results_data.update(
                    {
                        "statistic": round(float(stat), 2),
                        "p_value": round(float(p), 4),
                        "n": n,
                        "effect_size": {"rank_biserial_r": round(r_rb, 3)},
                    }
                )

            # ── Friedman ──
            elif test_type == "friedman":
                if not variable2:
                    return ToolResult(
                        success=False,
                        error=(
                            "variable2 is required for Friedman test. Provide comma-separated "
                            "column names in variable1 and variable2 for repeated measures."
                        ),
                    )
                # Collect all measurement columns
                measure_cols = [variable1, variable2]
                # Support additional columns passed via kwargs
                extra_vars = kwargs.get("extra_variables", [])
                if isinstance(extra_vars, list):
                    measure_cols.extend(extra_vars)

                missing = [c for c in measure_cols if c not in df.columns]
                if missing:
                    return ToolResult(success=False, error=f"Columns not found: {missing}")

                clean = df[measure_cols].dropna()
                n = len(clean)
                k = len(measure_cols)
                arrays = [clean[c].values for c in measure_cols]
                stat, p = scipy_stats.friedmanchisquare(*arrays)

                # Kendall's W effect size: W = χ² / (n * (k - 1))
                w = float(stat) / (n * (k - 1)) if n * (k - 1) > 0 else 0

                lines.append("**Friedman Test**")
                lines.append(f"Measures: {', '.join(measure_cols)}")
                lines.append(f"n = {n}, k = {k}")
                lines.append("")
                lines.append(f"χ²_F({k - 1}) = {stat:.2f}, *p* {format_p_value(p)}, *W* = {w:.3f}")
                lines.append("")
                lines.append("**Medians:**")
                for col in measure_cols:
                    lines.append(f"  {col}: Mdn = {clean[col].median():.2f}")
                lines.append("")
                lines.append("**APA Report:**")
                lines.append(
                    f"A Friedman test showed a "
                    f"{'statistically significant' if p < 0.05 else 'non-significant'} "
                    f"difference across conditions, "
                    f"χ²_F({k - 1}) = {stat:.2f}, p {format_p_value(p)}, W = {w:.3f}."
                )

                results_data.update(
                    {
                        "statistic": round(float(stat), 2),
                        "p_value": round(float(p), 4),
                        "df": k - 1,
                        "n": n,
                        "effect_size": {"kendall_w": round(w, 3)},
                    }
                )

            # ── Spearman Rank Correlation ──
            elif test_type == "spearman":
                if not variable2:
                    return ToolResult(success=False, error="variable2 is required for Spearman correlation")
                clean = df[[variable1, variable2]].dropna()
                x, y = clean[variable1], clean[variable2]
                n = len(clean)
                rho, p = scipy_stats.spearmanr(x, y)

                lines.append("**Spearman Rank Correlation**")
                lines.append(f"Variables: {variable1} × {variable2}, n = {n}")
                lines.append("")
                lines.append(f"*r*_s({n - 2}) = {rho:.3f}, *p* {format_p_value(p)}")
                lines.append("")
                lines.append("**APA Report:**")
                lines.append(
                    f"A Spearman rank-order correlation showed a "
                    f"{'significant' if p < 0.05 else 'non-significant'} "
                    f"{'positive' if rho > 0 else 'negative'} association between "
                    f"{variable1} and {variable2}, "
                    f"r_s({n - 2}) = {rho:.3f}, p {format_p_value(p)}."
                )

                results_data.update(
                    {
                        "statistic": round(float(rho), 3),
                        "p_value": round(float(p), 4),
                        "n": n,
                        "effect_size": {"spearman_rho": round(float(rho), 3)},
                    }
                )

            # ── Kendall's Tau ──
            elif test_type == "kendall":
                if not variable2:
                    return ToolResult(success=False, error="variable2 is required for Kendall's tau")
                clean = df[[variable1, variable2]].dropna()
                x, y = clean[variable1], clean[variable2]
                n = len(clean)
                tau, p = scipy_stats.kendalltau(x, y)

                lines.append("**Kendall's Tau Correlation**")
                lines.append(f"Variables: {variable1} × {variable2}, n = {n}")
                lines.append("")
                lines.append(f"τ_b = {tau:.3f}, *p* {format_p_value(p)}")
                lines.append("")
                lines.append("**APA Report:**")
                lines.append(
                    f"Kendall's tau-b indicated a "
                    f"{'significant' if p < 0.05 else 'non-significant'} "
                    f"{'positive' if tau > 0 else 'negative'} association between "
                    f"{variable1} and {variable2}, "
                    f"τ_b = {tau:.3f}, p {format_p_value(p)}."
                )

                results_data.update(
                    {
                        "statistic": round(float(tau), 3),
                        "p_value": round(float(p), 4),
                        "n": n,
                        "effect_size": {"kendall_tau": round(float(tau), 3)},
                    }
                )

            else:
                return ToolResult(
                    success=False,
                    error=(
                        f"Unknown test_type: {test_type}. Choose from: "
                        "mann_whitney, kruskal_wallis, wilcoxon, friedman, spearman, kendall"
                    ),
                )

            # Save results
            results_path = Path(self._workspace_dir) / "analysis" / "results" / "nonparametric.json"
            results_path.parent.mkdir(parents=True, exist_ok=True)
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            result_text = "\n".join(lines)
            result_text += f"\n\n*Results saved to: {results_path}*"
            return ToolResult(success=True, content=result_text)

        except Exception as e:
            return ToolResult(success=False, error=f"Nonparametric test failed: {e}")
