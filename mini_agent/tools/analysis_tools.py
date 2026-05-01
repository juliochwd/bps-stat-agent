"""Analysis tools for the BPS Academic Research Agent.

Provides advanced analysis capabilities:
- time_series_analysis: ADF, KPSS, ARIMA, VAR, Granger causality, cointegration
- bayesian_analysis: Bayesian regression with posterior summaries and HDI
- causal_inference: ATE, propensity score matching, IV, DiD, RDD
- survival_analysis: Kaplan-Meier, Cox PH, log-rank, AFT
- validate_data: Data quality validation with schema checks
- check_statistical_validity: Normality, homoscedasticity, VIF, autocorrelation
- conversational_analysis: Natural language data queries via pandas
- automated_eda: Comprehensive EDA report generation
- auto_visualize: Automatic visualization suggestion and creation
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
                "numpy and pandas are required for analysis tools. "
                "Install with: pip install 'bps-stat-agent[research-core]'"
            ),
        )
    return None


def _resolve_path(workspace_dir: str, data_path: str) -> Path:
    p = Path(data_path)
    if p.is_absolute():
        return p
    return Path(workspace_dir) / data_path


def _load_dataframe(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(str(path))
    if suffix in (".xls", ".xlsx"):
        return pd.read_excel(str(path))
    if suffix == ".parquet":
        return pd.read_parquet(str(path))
    if suffix == ".json":
        return pd.read_json(str(path))
    if suffix in (".tsv", ".tab"):
        return pd.read_csv(str(path), sep="\t")
    return pd.read_csv(str(path))


def _ensure_dir(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


class TimeSeriesAnalysisTool(Tool):
    """ADF, KPSS, ARIMA, VAR, Granger causality, and cointegration analysis."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "time_series_analysis"

    @property
    def description(self) -> str:
        return (
            "Perform time series analysis: unit root tests (ADF, KPSS), "
            "ARIMA/SARIMAX modeling, VAR multivariate models, Granger causality, "
            "and Johansen/Engle-Granger cointegration tests. "
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
                "test_type": {
                    "type": "string",
                    "enum": ["adf", "kpss", "arima", "var", "granger", "cointegration"],
                    "description": "Type of analysis to perform (default: arima)",
                },
                "lags": {"type": "integer", "description": "Number of lags (default: auto-select)"},
            },
            "required": ["data_path", "date_column", "value_columns"],
        }

    async def execute(
        self,
        data_path: str,
        date_column: str,
        value_columns: list[str],
        test_type: str = "arima",
        lags: int | None = None,
        **kwargs,
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        try:
            import statsmodels.api as sm
            from statsmodels.tsa.stattools import adfuller, grangercausalitytests, kpss

            from ..research.apa_formatter import format_p_value
        except ImportError:
            return ToolResult(success=False, error="statsmodels is required. Run: pip install statsmodels")

        try:
            full_path = _resolve_path(self._workspace_dir, data_path)
            if not full_path.exists():
                return ToolResult(success=False, error=f"Data file not found: {full_path}")

            df = pd.read_csv(str(full_path), parse_dates=[date_column])
            df = df.sort_values(date_column).set_index(date_column)

            missing = [c for c in value_columns if c not in df.columns]
            if missing:
                return ToolResult(success=False, error=f"Columns not found: {missing}. Available: {list(df.columns)}")

            ts_df = df[value_columns].dropna()
            lines: list[str] = ["## Time Series Analysis\n"]
            results_data: dict[str, Any] = {"test_type": test_type}

            if test_type == "adf":
                lines.append("### Augmented Dickey-Fuller Test\n")
                for col in value_columns:
                    series = ts_df[col].dropna()
                    adf_stat, adf_p, adf_lags, adf_nobs, adf_crit, _ = adfuller(series, autolag="AIC")
                    lines.append(f"**{col}:** ADF = {adf_stat:.4f}, p {format_p_value(adf_p)}, lags = {adf_lags}")
                    conclusion = "stationary (reject H₀)" if adf_p < 0.05 else "non-stationary (fail to reject H₀)"
                    lines.append(f"  Conclusion: {conclusion}")
                    results_data[col] = {"adf_stat": round(adf_stat, 4), "p_value": round(adf_p, 4), "lags": adf_lags}

            elif test_type == "kpss":
                lines.append("### KPSS Stationarity Test\n")
                for col in value_columns:
                    series = ts_df[col].dropna()
                    kpss_stat, kpss_p, kpss_lags, kpss_crit = kpss(series, regression="c", nlags="auto")
                    lines.append(f"**{col}:** KPSS = {kpss_stat:.4f}, p {format_p_value(kpss_p)}, lags = {kpss_lags}")
                    conclusion = "stationary (fail to reject H₀)" if kpss_p > 0.05 else "non-stationary (reject H₀)"
                    lines.append(f"  Conclusion: {conclusion}")
                    results_data[col] = {"kpss_stat": round(kpss_stat, 4), "p_value": round(kpss_p, 4)}

            elif test_type == "arima":
                col = value_columns[0]
                series = ts_df[col].dropna()
                lines.append("### ARIMA Model\n")

                if lags is not None:
                    order = (lags, 1, lags)
                else:
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
                lines.append(f"**N:** {int(model.nobs)}, **AIC:** {model.aic:.2f}, **BIC:** {model.bic:.2f}")
                lines.append("")
                lines.append("| Parameter | Coef. | Std. Err. | z | p |")
                lines.append("|-----------|-------|-----------|---|---|")
                for param in model.params.index:
                    lines.append(
                        f"| {param} | {model.params[param]:.4f} | {model.bse[param]:.4f} "
                        f"| {model.tvalues[param]:.2f} | {format_p_value(model.pvalues[param])} |"
                    )

                lb_test = sm.stats.acorr_ljungbox(model.resid, lags=[10], return_df=True)
                lb_stat = float(lb_test["lb_stat"].iloc[0])
                lb_p = float(lb_test["lb_pvalue"].iloc[0])
                lines.append(f"\n**Ljung-Box Q(10):** {lb_stat:.2f}, p {format_p_value(lb_p)}")

                results_data["arima"] = {
                    "order": list(order),
                    "aic": round(model.aic, 2),
                    "bic": round(model.bic, 2),
                    "coefficients": {k: round(float(v), 4) for k, v in model.params.items()},
                    "ljung_box": {"statistic": round(lb_stat, 2), "p_value": round(lb_p, 4)},
                }

            elif test_type == "var":
                if len(value_columns) < 2:
                    return ToolResult(success=False, error="VAR requires at least 2 value_columns")
                from statsmodels.tsa.api import VAR as VARModel

                lines.append("### VAR Model\n")
                var_model = VARModel(ts_df[value_columns])
                var_result = var_model.fit(maxlags=lags) if lags else var_model.fit(ic="aic")
                lines.append(
                    f"**Lag Order:** {var_result.k_ar}, **AIC:** {var_result.aic:.2f}, **BIC:** {var_result.bic:.2f}"
                )
                results_data["var"] = {"lag_order": var_result.k_ar, "aic": round(var_result.aic, 2)}

            elif test_type == "granger":
                if len(value_columns) < 2:
                    return ToolResult(success=False, error="Granger causality requires at least 2 columns")
                lines.append("### Granger Causality Tests\n")
                max_lag = lags or 4
                granger_results: dict[str, Any] = {}
                for i, caused in enumerate(value_columns):
                    for j, causing in enumerate(value_columns):
                        if i == j:
                            continue
                        test_data = ts_df[[caused, causing]].dropna()
                        gc = grangercausalitytests(test_data, maxlag=max_lag, verbose=False)
                        best_lag = min(gc.keys(), key=lambda k: gc[k][0]["ssr_ftest"][1])
                        f_stat = gc[best_lag][0]["ssr_ftest"][0]
                        p_val = gc[best_lag][0]["ssr_ftest"][1]
                        lines.append(
                            f"  {causing} → {caused}: F = {f_stat:.2f}, p {format_p_value(p_val)} (lag={best_lag})"
                        )
                        granger_results[f"{causing}->{caused}"] = {
                            "f_statistic": round(f_stat, 2),
                            "p_value": round(p_val, 4),
                            "lag": best_lag,
                        }
                results_data["granger"] = granger_results

            elif test_type == "cointegration":
                if len(value_columns) < 2:
                    return ToolResult(success=False, error="Cointegration requires at least 2 columns")
                lines.append("### Johansen Cointegration Test\n")
                from statsmodels.tsa.vector_ar.vecm import coint_johansen

                k_ar = lags or 2
                joh = coint_johansen(ts_df[value_columns].dropna(), det_order=0, k_ar_diff=k_ar)
                lines.append("| Hypothesis | Trace Stat | 5% CV | Max-Eigen Stat | 5% CV |")
                lines.append("|------------|-----------|-------|----------------|-------|")
                for i in range(joh.lr1.shape[0]):
                    lines.append(
                        f"| r ≤ {i} | {joh.lr1[i]:.2f} | {joh.cvt[i, 1]:.2f} | {joh.lr2[i]:.2f} | {joh.cvm[i, 1]:.2f} |"
                    )
                results_data["cointegration"] = {
                    "trace_stats": [round(float(x), 2) for x in joh.lr1],
                    "max_eigen_stats": [round(float(x), 2) for x in joh.lr2],
                }
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown test_type: {test_type}. Choose from: adf, kpss, arima, var, granger, cointegration",
                )

            results_path = _ensure_dir(Path(self._workspace_dir) / "analysis" / "results" / "time_series.json")
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            result_text = "\n".join(lines)
            result_text += f"\n\n*Results saved to: {results_path}*"
            return ToolResult(success=True, content=result_text)

        except Exception as e:
            return ToolResult(success=False, error=f"Time series analysis failed: {e}")


class BayesianAnalysisTool(Tool):
    """Bayesian regression with posterior summaries, HDI, ROPE, and Bayes factors."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "bayesian_analysis"

    @property
    def description(self) -> str:
        return (
            "Perform Bayesian analysis: linear regression, logistic regression, "
            "or hierarchical models. Uses bambi/PyMC when available, falls back "
            "to scipy.stats for simple Bayesian tests. Returns posterior summaries, "
            "HDI intervals, ROPE analysis, and Bayes factors."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "model_type": {
                    "type": "string",
                    "enum": ["linear", "logistic", "hierarchical"],
                    "description": "Bayesian model type (default: linear)",
                },
                "formula": {"type": "string", "description": "R-style formula (e.g., 'y ~ x1 + x2')"},
                "priors": {
                    "type": "string",
                    "enum": ["default", "weakly_informative", "informative"],
                    "description": "Prior specification strategy (default: default)",
                },
                "n_samples": {
                    "type": "integer",
                    "description": "Number of posterior samples per chain (default: 2000)",
                },
                "n_chains": {"type": "integer", "description": "Number of MCMC chains (default: 4)"},
                "rope": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "ROPE interval [lower, upper] for practical equivalence testing",
                },
            },
            "required": ["data_path", "formula"],
        }

    async def execute(
        self,
        data_path: str,
        formula: str,
        model_type: str = "linear",
        priors: str = "default",
        n_samples: int = 2000,
        n_chains: int = 4,
        rope: list[float] | None = None,
        **kwargs,
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        full_path = _resolve_path(self._workspace_dir, data_path)
        if not full_path.exists():
            return ToolResult(success=False, error=f"Data file not found: {full_path}")

        try:
            df = pd.read_csv(str(full_path))
        except Exception as exc:
            return ToolResult(success=False, error=f"Failed to load data: {exc}")

        _has_bambi = False
        try:
            import arviz as az  # noqa: F401
            import bambi as bmb  # noqa: F401

            _has_bambi = True
        except ImportError:
            pass

        if _has_bambi:
            return await self._run_bambi(df, formula, model_type, priors, n_samples, n_chains, rope)
        return await self._run_scipy_fallback(df, formula, rope)

    async def _run_bambi(
        self,
        df: pd.DataFrame,
        formula: str,
        model_type: str,
        priors: str,
        n_samples: int,
        n_chains: int,
        rope: list[float] | None,
    ) -> ToolResult:
        try:
            import arviz as az
            import bambi as bmb

            lines: list[str] = ["## Bayesian Analysis\n"]
            lines.append(f"**Formula:** {formula}")
            lines.append(f"**Model:** {model_type}, **Priors:** {priors}")
            lines.append(f"**Chains:** {n_chains}, **Samples:** {n_samples}\n")

            family_map = {"linear": "gaussian", "logistic": "bernoulli", "hierarchical": "gaussian"}
            family = family_map.get(model_type, "gaussian")

            prior_spec: dict[str, Any] | None = None
            if priors == "weakly_informative":
                prior_spec = {
                    "Intercept": bmb.Prior("Normal", mu=0, sigma=10),
                    "common": bmb.Prior("Normal", mu=0, sigma=5),
                }
            elif priors == "informative":
                prior_spec = {
                    "Intercept": bmb.Prior("Normal", mu=0, sigma=2.5),
                    "common": bmb.Prior("Normal", mu=0, sigma=1),
                }

            model = bmb.Model(formula, df, family=family, priors=prior_spec)
            idata = model.fit(draws=n_samples, chains=n_chains, random_seed=42)

            summary = az.summary(idata, hdi_prob=0.95)
            lines.append("### Posterior Summary\n")
            header_cols = [
                c for c in ["mean", "sd", "hdi_2.5%", "hdi_97.5%", "r_hat", "ess_bulk"] if c in summary.columns
            ]
            lines.append("| Parameter | " + " | ".join(header_cols) + " |")
            lines.append("|" + "---|" * (len(header_cols) + 1))
            for param in summary.index:
                vals = " | ".join(f"{summary.loc[param, c]:.4f}" for c in header_cols)
                lines.append(f"| {param} | {vals} |")

            if "r_hat" in summary.columns:
                max_rhat = float(summary["r_hat"].max())
                lines.append(
                    f"\n**Max R-hat:** {max_rhat:.4f} ({'converged' if max_rhat < 1.05 else 'potential non-convergence'})"
                )

            if rope is not None and len(rope) == 2:
                lines.append(f"\n### ROPE Analysis [{rope[0]}, {rope[1]}]\n")
                posterior = idata.posterior
                for var_name in posterior.data_vars:
                    samples = posterior[var_name].values.flatten()
                    in_rope = float(np.mean((samples >= rope[0]) & (samples <= rope[1])))
                    lines.append(f"  {var_name}: {in_rope:.1%} of posterior in ROPE")

            try:
                waic = az.waic(idata)
                lines.append(f"\n**WAIC:** {waic.elpd_waic:.2f} (SE = {waic.se:.2f})")
            except Exception:
                pass

            results_data = {
                "formula": formula,
                "model_type": model_type,
                "posterior_summary": {
                    str(p): {c: round(float(summary.loc[p, c]), 4) for c in header_cols} for p in summary.index
                },
            }
            results_path = _ensure_dir(Path(self._workspace_dir) / "analysis" / "results" / "bayesian.json")
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            return ToolResult(success=True, content="\n".join(lines) + f"\n\n*Results saved to: {results_path}*")

        except Exception as e:
            return ToolResult(success=False, error=f"Bayesian analysis (bambi) failed: {e}")

    async def _run_scipy_fallback(
        self,
        df: pd.DataFrame,
        formula: str,
        rope: list[float] | None,
    ) -> ToolResult:
        try:
            from scipy import stats as scipy_stats

            lines: list[str] = ["## Bayesian Analysis (scipy fallback)\n"]
            lines.append(f"**Formula:** {formula}")
            lines.append("*Note: bambi/pymc not installed. Using scipy conjugate priors.*\n")

            parts = formula.replace(" ", "").split("~")
            if len(parts) != 2:
                return ToolResult(success=False, error=f"Invalid formula: {formula}. Expected 'y ~ x1 + x2'")

            dep_var = parts[0]
            indep_vars = [v.strip() for v in parts[1].split("+")]

            all_vars = [dep_var] + indep_vars
            missing_vars = [v for v in all_vars if v not in df.columns]
            if missing_vars:
                return ToolResult(success=False, error=f"Variables not found: {missing_vars}")

            clean = df[all_vars].dropna()
            y = clean[dep_var].values
            X = clean[indep_vars].values

            X_with_const = np.column_stack([np.ones(len(X)), X])
            try:
                beta_hat = np.linalg.lstsq(X_with_const, y, rcond=None)[0]
                residuals = y - X_with_const @ beta_hat
                sigma2 = float(np.sum(residuals**2) / (len(y) - X_with_const.shape[1]))
                cov_beta = sigma2 * np.linalg.inv(X_with_const.T @ X_with_const)
            except np.linalg.LinAlgError:
                return ToolResult(success=False, error="Singular matrix — cannot compute OLS estimates")

            param_names = ["Intercept"] + indep_vars
            lines.append("### Posterior Approximation (Normal-Inverse-Gamma conjugate)\n")
            lines.append("| Parameter | Mean | SD | 95% HDI |")
            lines.append("|-----------|------|----|---------|")
            results_data: dict[str, Any] = {}
            for i, name in enumerate(param_names):
                mean_val = float(beta_hat[i])
                sd_val = float(np.sqrt(cov_beta[i, i]))
                hdi_low = mean_val - 1.96 * sd_val
                hdi_high = mean_val + 1.96 * sd_val
                lines.append(f"| {name} | {mean_val:.4f} | {sd_val:.4f} | [{hdi_low:.4f}, {hdi_high:.4f}] |")
                results_data[name] = {"mean": round(mean_val, 4), "sd": round(sd_val, 4)}

            bf_lines: list[str] = []
            for i, name in enumerate(param_names):
                if name == "Intercept":
                    continue
                mean_val = float(beta_hat[i])
                sd_val = float(np.sqrt(cov_beta[i, i]))
                if sd_val > 0:
                    bf10 = scipy_stats.norm.pdf(0, loc=mean_val, scale=sd_val)
                    prior_density = scipy_stats.norm.pdf(0, loc=0, scale=10)
                    if bf10 > 0:
                        bf = prior_density / bf10
                        bf_lines.append(f"  {name}: BF₁₀ ≈ {bf:.2f}")

            if bf_lines:
                lines.append("\n### Approximate Bayes Factors (Savage-Dickey)\n")
                lines.extend(bf_lines)

            results_path = _ensure_dir(Path(self._workspace_dir) / "analysis" / "results" / "bayesian.json")
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            return ToolResult(success=True, content="\n".join(lines) + f"\n\n*Results saved to: {results_path}*")

        except Exception as e:
            return ToolResult(success=False, error=f"Bayesian analysis (scipy) failed: {e}")


class CausalInferenceTool(Tool):
    """ATE estimation, propensity score matching, IV, DiD, and RDD."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "causal_inference"

    @property
    def description(self) -> str:
        return (
            "Perform causal inference: ATE estimation via backdoor adjustment, "
            "propensity score matching, instrumental variables (IV), "
            "difference-in-differences (DiD), and regression discontinuity (RDD). "
            "Uses DoWhy when available, falls back to statsmodels for basic IV/DiD."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "treatment_var": {"type": "string", "description": "Treatment variable name"},
                "outcome_var": {"type": "string", "description": "Outcome variable name"},
                "method": {
                    "type": "string",
                    "enum": ["ate", "propensity_score", "iv", "did", "rdd"],
                    "description": "Causal estimation method (default: ate)",
                },
                "confounders": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of confounding variables",
                },
                "instrument": {"type": "string", "description": "Instrumental variable (required for iv)"},
                "time_var": {"type": "string", "description": "Time variable (required for did)"},
                "running_var": {"type": "string", "description": "Running variable (required for rdd)"},
                "cutoff": {"type": "number", "description": "RDD cutoff value (default: 0)"},
            },
            "required": ["data_path", "treatment_var", "outcome_var"],
        }

    async def execute(
        self,
        data_path: str,
        treatment_var: str,
        outcome_var: str,
        method: str = "ate",
        confounders: list[str] | None = None,
        instrument: str | None = None,
        time_var: str | None = None,
        running_var: str | None = None,
        cutoff: float = 0.0,
        **kwargs,
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        full_path = _resolve_path(self._workspace_dir, data_path)
        if not full_path.exists():
            return ToolResult(success=False, error=f"Data file not found: {full_path}")

        try:
            df = pd.read_csv(str(full_path))
        except Exception as exc:
            return ToolResult(success=False, error=f"Failed to load data: {exc}")

        confounders = confounders or []

        _has_dowhy = False
        try:
            from dowhy import CausalModel  # noqa: F401

            _has_dowhy = True
        except ImportError:
            pass

        if _has_dowhy and method in ("ate", "propensity_score"):
            return await self._run_dowhy(df, treatment_var, outcome_var, method, confounders, instrument)

        return await self._run_statsmodels_fallback(
            df,
            treatment_var,
            outcome_var,
            method,
            confounders,
            instrument,
            time_var,
            running_var,
            cutoff,
        )

    async def _run_dowhy(
        self,
        df: pd.DataFrame,
        treatment: str,
        outcome: str,
        method: str,
        confounders: list[str],
        instrument: str | None,
    ) -> ToolResult:
        try:
            from dowhy import CausalModel

            lines: list[str] = ["## Causal Inference Analysis (DoWhy)\n"]
            lines.append(f"**Treatment:** {treatment}, **Outcome:** {outcome}")
            lines.append(f"**Method:** {method}, **Confounders:** {', '.join(confounders) or 'none'}\n")

            instruments = [instrument] if instrument else None
            causal_model = CausalModel(
                data=df,
                treatment=treatment,
                outcome=outcome,
                common_causes=confounders if confounders else None,
                instruments=instruments,
            )

            estimand = causal_model.identify_effect(proceed_when_unidentifiable=True)

            method_map = {
                "ate": "backdoor.linear_regression",
                "propensity_score": "backdoor.propensity_score_matching",
            }
            estimate = causal_model.estimate_effect(
                estimand,
                method_name=method_map.get(method, "backdoor.linear_regression"),
                confidence_intervals=True,
            )

            ate = float(estimate.value)
            lines.append(f"**Average Treatment Effect (ATE):** {ate:.4f}")

            try:
                ref_random = causal_model.refute_estimate(estimand, estimate, method_name="random_common_cause")
                lines.append(f"**Refutation (random common cause):** new ATE = {float(ref_random.new_effect):.4f}")
            except Exception:
                pass

            results_data = {"method": method, "ate": round(ate, 4), "treatment": treatment, "outcome": outcome}
            results_path = _ensure_dir(Path(self._workspace_dir) / "analysis" / "results" / "causal_inference.json")
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            return ToolResult(success=True, content="\n".join(lines) + f"\n\n*Results saved to: {results_path}*")

        except Exception as e:
            return ToolResult(success=False, error=f"Causal inference (DoWhy) failed: {e}")

    async def _run_statsmodels_fallback(
        self,
        df: pd.DataFrame,
        treatment: str,
        outcome: str,
        method: str,
        confounders: list[str],
        instrument: str | None,
        time_var: str | None,
        running_var: str | None,
        cutoff: float,
    ) -> ToolResult:
        try:
            import statsmodels.api as sm

            from ..research.apa_formatter import format_p_value

            lines: list[str] = ["## Causal Inference Analysis (statsmodels fallback)\n"]
            results_data: dict[str, Any] = {"method": method}

            if method == "iv":
                if not instrument:
                    return ToolResult(success=False, error="instrument is required for IV method")
                from statsmodels.sandbox.regression.gmm import IV2SLS

                clean = df[[outcome, treatment, instrument] + confounders].dropna()
                y = clean[outcome]
                endog = clean[[treatment] + confounders]
                instruments = clean[[instrument] + confounders]
                endog_with_const = sm.add_constant(endog)
                instruments_with_const = sm.add_constant(instruments)
                iv_result = IV2SLS(y, endog_with_const, instruments_with_const).fit()
                lines.append(f"**IV Estimate ({treatment}):** {iv_result.params[treatment]:.4f}")
                lines.append(
                    f"**SE:** {iv_result.bse[treatment]:.4f}, **p:** {format_p_value(iv_result.pvalues[treatment])}"
                )
                results_data["iv_estimate"] = round(float(iv_result.params[treatment]), 4)

            elif method == "did":
                if not time_var:
                    return ToolResult(success=False, error="time_var is required for DiD method")
                clean = df[[outcome, treatment, time_var] + confounders].dropna()
                clean["interaction"] = clean[treatment] * clean[time_var]
                X = sm.add_constant(clean[[treatment, time_var, "interaction"] + confounders])
                result = sm.OLS(clean[outcome], X).fit(cov_type="HC3")
                did_effect = float(result.params["interaction"])
                did_p = float(result.pvalues["interaction"])
                lines.append(f"**DiD Estimate:** {did_effect:.4f}")
                lines.append(f"**SE:** {result.bse['interaction']:.4f}, **p:** {format_p_value(did_p)}")
                results_data["did_estimate"] = round(did_effect, 4)
                results_data["p_value"] = round(did_p, 4)

            elif method == "rdd":
                if not running_var:
                    return ToolResult(success=False, error="running_var is required for RDD method")
                clean = df[[outcome, running_var] + confounders].dropna()
                clean["above_cutoff"] = (clean[running_var] >= cutoff).astype(int)
                clean["centered"] = clean[running_var] - cutoff
                clean["interaction"] = clean["above_cutoff"] * clean["centered"]
                X = sm.add_constant(clean[["above_cutoff", "centered", "interaction"] + confounders])
                result = sm.OLS(clean[outcome], X).fit(cov_type="HC3")
                rdd_effect = float(result.params["above_cutoff"])
                rdd_p = float(result.pvalues["above_cutoff"])
                lines.append(f"**RDD Estimate (LATE):** {rdd_effect:.4f}")
                lines.append(f"**SE:** {result.bse['above_cutoff']:.4f}, **p:** {format_p_value(rdd_p)}")
                results_data["rdd_estimate"] = round(rdd_effect, 4)

            elif method == "ate":
                clean = df[[outcome, treatment] + confounders].dropna()
                X = sm.add_constant(clean[[treatment] + confounders])
                result = sm.OLS(clean[outcome], X).fit(cov_type="HC3")
                ate = float(result.params[treatment])
                lines.append(f"**ATE (OLS):** {ate:.4f}")
                lines.append(f"**SE:** {result.bse[treatment]:.4f}, **p:** {format_p_value(result.pvalues[treatment])}")
                results_data["ate"] = round(ate, 4)

            else:
                return ToolResult(success=False, error=f"Unknown method: {method}")

            results_path = _ensure_dir(Path(self._workspace_dir) / "analysis" / "results" / "causal_inference.json")
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            return ToolResult(success=True, content="\n".join(lines) + f"\n\n*Results saved to: {results_path}*")

        except Exception as e:
            return ToolResult(success=False, error=f"Causal inference (statsmodels) failed: {e}")


class SurvivalAnalysisTool(Tool):
    """Kaplan-Meier, Cox PH, log-rank test, and AFT models."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "survival_analysis"

    @property
    def description(self) -> str:
        return (
            "Perform survival analysis: Kaplan-Meier curves, Cox proportional hazards, "
            "log-rank tests, and accelerated failure time (AFT) models. "
            "Returns survival curves, hazard ratios, concordance index, and APA-formatted output."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to CSV data file"},
                "duration_var": {"type": "string", "description": "Column with time-to-event durations"},
                "event_var": {"type": "string", "description": "Column with event indicator (1=event, 0=censored)"},
                "method": {
                    "type": "string",
                    "enum": ["kaplan_meier", "cox_ph", "log_rank", "aft"],
                    "description": "Survival analysis method (default: kaplan_meier)",
                },
                "covariates": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Covariates for Cox PH or AFT models",
                },
                "group_var": {"type": "string", "description": "Grouping variable for stratified analysis"},
            },
            "required": ["data_path", "duration_var", "event_var"],
        }

    async def execute(
        self,
        data_path: str,
        duration_var: str,
        event_var: str,
        method: str = "kaplan_meier",
        covariates: list[str] | None = None,
        group_var: str | None = None,
        **kwargs,
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        try:
            from lifelines import CoxPHFitter, KaplanMeierFitter, WeibullAFTFitter
            from lifelines.statistics import logrank_test
        except ImportError:
            return ToolResult(success=False, error="lifelines is required. Run: pip install lifelines")

        try:
            from ..research.apa_formatter import format_p_value

            full_path = _resolve_path(self._workspace_dir, data_path)
            if not full_path.exists():
                return ToolResult(success=False, error=f"Data file not found: {full_path}")

            df = pd.read_csv(str(full_path))
            lines: list[str] = ["## Survival Analysis\n"]
            results_data: dict[str, Any] = {"method": method}

            if method == "kaplan_meier":
                lines.append("### Kaplan-Meier Survival Estimates\n")
                if group_var and group_var in df.columns:
                    groups = df[group_var].dropna().unique()
                    for group in sorted(groups):
                        mask = df[group_var] == group
                        kmf = KaplanMeierFitter()
                        kmf.fit(df.loc[mask, duration_var], event_observed=df.loc[mask, event_var], label=str(group))
                        median_surv = kmf.median_survival_time_
                        lines.append(
                            f"**{group}:** N={mask.sum()}, Events={int(df.loc[mask, event_var].sum())}, Median={median_surv:.2f}"
                        )

                    if len(groups) == 2:
                        g1_mask = df[group_var] == groups[0]
                        g2_mask = df[group_var] == groups[1]
                        lr = logrank_test(
                            df.loc[g1_mask, duration_var],
                            df.loc[g2_mask, duration_var],
                            event_observed_A=df.loc[g1_mask, event_var],
                            event_observed_B=df.loc[g2_mask, event_var],
                        )
                        lines.append(
                            f"\n**Log-Rank Test:** χ²(1) = {lr.test_statistic:.2f}, p {format_p_value(lr.p_value)}"
                        )
                        results_data["log_rank"] = {
                            "statistic": round(float(lr.test_statistic), 2),
                            "p_value": round(float(lr.p_value), 4),
                        }
                else:
                    kmf = KaplanMeierFitter()
                    kmf.fit(df[duration_var], event_observed=df[event_var])
                    lines.append(f"**N:** {len(df)}, **Events:** {int(df[event_var].sum())}")
                    lines.append(f"**Median Survival Time:** {kmf.median_survival_time_:.2f}")

            elif method == "log_rank":
                if not group_var:
                    return ToolResult(success=False, error="group_var is required for log-rank test")
                groups = df[group_var].dropna().unique()
                if len(groups) != 2:
                    return ToolResult(
                        success=False, error=f"Log-rank test requires exactly 2 groups, got {len(groups)}"
                    )
                g1_mask = df[group_var] == groups[0]
                g2_mask = df[group_var] == groups[1]
                lr = logrank_test(
                    df.loc[g1_mask, duration_var],
                    df.loc[g2_mask, duration_var],
                    event_observed_A=df.loc[g1_mask, event_var],
                    event_observed_B=df.loc[g2_mask, event_var],
                )
                lines.append("### Log-Rank Test\n")
                lines.append(f"χ²(1) = {lr.test_statistic:.2f}, p {format_p_value(lr.p_value)}")
                results_data["log_rank"] = {
                    "statistic": round(float(lr.test_statistic), 2),
                    "p_value": round(float(lr.p_value), 4),
                }

            elif method == "cox_ph":
                if not covariates:
                    return ToolResult(success=False, error="covariates are required for Cox PH model")
                cox_cols = [duration_var, event_var] + covariates
                cox_df = df[cox_cols].dropna()
                cph = CoxPHFitter()
                cph.fit(cox_df, duration_col=duration_var, event_col=event_var)
                lines.append("### Cox Proportional Hazards Model\n")
                lines.append(f"**Concordance Index:** {cph.concordance_index_:.4f}")
                lines.append("")
                lines.append("| Covariate | HR | Coef. | SE | z | p |")
                lines.append("|-----------|----|----|----|----|---|")
                summary_df = cph.summary
                for cov in summary_df.index:
                    hr = float(summary_df.loc[cov, "exp(coef)"])
                    coef = float(summary_df.loc[cov, "coef"])
                    se = float(summary_df.loc[cov, "se(coef)"])
                    z = float(summary_df.loc[cov, "z"])
                    p = float(summary_df.loc[cov, "p"])
                    lines.append(f"| {cov} | {hr:.4f} | {coef:.4f} | {se:.4f} | {z:.2f} | {format_p_value(p)} |")
                results_data["cox_ph"] = {
                    "concordance_index": round(cph.concordance_index_, 4),
                    "hazard_ratios": {
                        cov: round(float(summary_df.loc[cov, "exp(coef)"]), 4) for cov in summary_df.index
                    },
                }

            elif method == "aft":
                if not covariates:
                    return ToolResult(success=False, error="covariates are required for AFT model")
                aft_cols = [duration_var, event_var] + covariates
                aft_df = df[aft_cols].dropna()
                aft = WeibullAFTFitter()
                aft.fit(aft_df, duration_col=duration_var, event_col=event_var)
                lines.append("### Accelerated Failure Time Model (Weibull)\n")
                lines.append(f"**Concordance Index:** {aft.concordance_index_:.4f}, **AIC:** {aft.AIC_:.2f}")
                results_data["aft"] = {"concordance_index": round(aft.concordance_index_, 4), "aic": round(aft.AIC_, 2)}

            else:
                return ToolResult(success=False, error=f"Unknown method: {method}")

            results_path = _ensure_dir(Path(self._workspace_dir) / "analysis" / "results" / "survival.json")
            with open(results_path, "w") as f:
                json.dump(results_data, f, indent=2, default=str)

            return ToolResult(success=True, content="\n".join(lines) + f"\n\n*Results saved to: {results_path}*")

        except Exception as e:
            return ToolResult(success=False, error=f"Survival analysis failed: {e}")


class ValidateDataTool(Tool):
    """Data quality validation with schema checks, missing values, outliers, and distributions."""

    PREDEFINED_CHECKS = {
        "no_nulls",
        "unique_ids",
        "valid_range",
        "no_duplicates",
        "consistent_types",
        "no_outliers_iqr",
    }

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "validate_data"

    @property
    def description(self) -> str:
        return (
            "Validate data quality: missing values, outliers, data types, distributions. "
            "Uses pandera for schema validation if available. "
            "Predefined checks: no_nulls, unique_ids, valid_range, no_duplicates, "
            "consistent_types, no_outliers_iqr. Returns validation report with pass/fail."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to data file (CSV, Excel, Parquet, JSON)"},
                "schema": {
                    "type": "object",
                    "description": "Pandera schema definition as dict. Keys=column names, values={dtype, nullable, checks}",
                },
                "checks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Predefined check names: no_nulls, unique_ids, valid_range, no_duplicates, consistent_types, no_outliers_iqr",
                },
            },
            "required": ["data_path"],
        }

    async def execute(
        self, data_path: str, schema: dict[str, Any] | None = None, checks: list[str] | None = None, **kwargs
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        full_path = _resolve_path(self._workspace_dir, data_path)
        if not full_path.exists():
            return ToolResult(success=False, error=f"Data file not found: {full_path}")

        try:
            df = _load_dataframe(full_path)
        except Exception as exc:
            return ToolResult(success=False, error=f"Failed to load data: {exc}")

        if df.empty:
            return ToolResult(success=False, error="Dataset is empty.")

        all_check_details: list[dict[str, Any]] = []

        if schema:
            try:
                import pandera as pa

                columns: dict[str, Any] = {}
                for col_name, col_spec in schema.items():
                    dtype = col_spec.get("dtype")
                    nullable = col_spec.get("nullable", True)
                    columns[col_name] = pa.Column(dtype=dtype, nullable=nullable)
                pa_schema = pa.DataFrameSchema(columns=columns, coerce=True)
                try:
                    pa_schema.validate(df, lazy=True)
                    all_check_details.append(
                        {"name": "pandera_schema", "passed": True, "details": "All schema checks passed."}
                    )
                except pa.errors.SchemaErrors as exc:
                    all_check_details.append({"name": "pandera_schema", "passed": False, "details": str(exc)[:200]})
            except ImportError:
                all_check_details.append(
                    {
                        "name": "pandera_schema",
                        "passed": False,
                        "details": "pandera not installed. Run: pip install pandera",
                    }
                )

        check_list = checks or sorted(self.PREDEFINED_CHECKS)
        for check_name in check_list:
            if check_name == "no_nulls":
                missing = df.isnull().sum()
                cols_with_nulls = missing[missing > 0]
                passed = cols_with_nulls.empty
                details = (
                    "No null values."
                    if passed
                    else "Nulls: " + ", ".join(f"{c}({int(v)})" for c, v in cols_with_nulls.items())
                )
                all_check_details.append({"name": check_name, "passed": passed, "details": details})

            elif check_name == "unique_ids":
                id_cols = [c for c in df.columns if "id" in c.lower()] or [df.columns[0]]
                passed = all(df[c].duplicated().sum() == 0 for c in id_cols)
                all_check_details.append(
                    {"name": check_name, "passed": passed, "details": f"Checked: {', '.join(id_cols)}"}
                )

            elif check_name == "valid_range":
                numeric = df.select_dtypes(include=[np.number])
                has_inf = any(np.isinf(numeric[c]).any() for c in numeric.columns)
                all_check_details.append(
                    {
                        "name": check_name,
                        "passed": not has_inf,
                        "details": "Infinite values found" if has_inf else "All finite",
                    }
                )

            elif check_name == "no_duplicates":
                n_dup = int(df.duplicated().sum())
                all_check_details.append(
                    {
                        "name": check_name,
                        "passed": n_dup == 0,
                        "details": f"{n_dup} duplicate rows" if n_dup else "No duplicates",
                    }
                )

            elif check_name == "consistent_types":
                issues = []
                for col in df.columns:
                    non_null = df[col].dropna()
                    if len(non_null) > 0 and len(non_null.apply(type).unique()) > 1:
                        issues.append(col)
                all_check_details.append(
                    {
                        "name": check_name,
                        "passed": len(issues) == 0,
                        "details": f"Mixed types in: {issues}" if issues else "Consistent",
                    }
                )

            elif check_name == "no_outliers_iqr":
                numeric = df.select_dtypes(include=[np.number])
                outlier_cols = []
                for col in numeric.columns:
                    series = numeric[col].dropna()
                    if len(series) < 4:
                        continue
                    q1, q3 = series.quantile(0.25), series.quantile(0.75)
                    iqr = q3 - q1
                    n_out = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())
                    if n_out > 0:
                        outlier_cols.append(f"{col}({n_out})")
                all_check_details.append(
                    {
                        "name": check_name,
                        "passed": len(outlier_cols) == 0,
                        "details": "Outliers: " + ", ".join(outlier_cols) if outlier_cols else "No outliers",
                    }
                )

        passed_checks = sum(1 for c in all_check_details if c["passed"])
        total_checks = len(all_check_details)
        quality_score = round(passed_checks / total_checks * 100, 1) if total_checks > 0 else 0
        overall_passed = all(c["passed"] for c in all_check_details)

        lines = [
            "## Data Validation Report\n",
            f"**Dataset:** {full_path.name}",
            f"**Overall:** {'PASSED' if overall_passed else 'FAILED'}",
            f"**Checks passed:** {passed_checks}/{total_checks}",
            f"**Quality score:** {quality_score}/100\n",
            "| # | Check | Status | Details |",
            "|---|-------|--------|---------|",
        ]
        for i, chk in enumerate(all_check_details, 1):
            status = "PASS" if chk["passed"] else "FAIL"
            lines.append(f"| {i} | {chk['name']} | {status} | {chk['details'][:120]} |")

        report_data = {"overall_passed": overall_passed, "quality_score": quality_score, "checks": all_check_details}
        out_path = _ensure_dir(Path(self._workspace_dir) / "analysis" / "validation" / "validation_report.json")
        out_path.write_text(json.dumps(report_data, indent=2, default=str))
        lines.append(f"\n*Report saved to: {out_path}*")

        return ToolResult(success=overall_passed, content="\n".join(lines))


class CheckStatisticalValidityTool(Tool):
    """Check normality, homoscedasticity, multicollinearity (VIF), and autocorrelation."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "check_statistical_validity"

    @property
    def description(self) -> str:
        return (
            "Check statistical assumptions: normality (Shapiro-Wilk, Kolmogorov-Smirnov), "
            "homoscedasticity (Breusch-Pagan, White), multicollinearity (VIF), "
            "and autocorrelation (Durbin-Watson, Ljung-Box). "
            "Returns pass/fail per check with diagnostic details."
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
                    "description": "Variables to check (all numeric if omitted)",
                },
                "checks": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["normality", "homoscedasticity", "multicollinearity", "autocorrelation"],
                    },
                    "description": "Which assumption checks to run (default: all)",
                },
                "dependent_var": {
                    "type": "string",
                    "description": "Dependent variable (needed for homoscedasticity/autocorrelation)",
                },
                "independent_vars": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Independent variables (needed for VIF, homoscedasticity)",
                },
            },
            "required": ["data_path"],
        }

    async def execute(
        self,
        data_path: str,
        variables: list[str] | None = None,
        checks: list[str] | None = None,
        dependent_var: str | None = None,
        independent_vars: list[str] | None = None,
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
            full_path = _resolve_path(self._workspace_dir, data_path)
            if not full_path.exists():
                return ToolResult(success=False, error=f"Data file not found: {full_path}")

            df = pd.read_csv(str(full_path))
            check_list = checks or ["normality", "homoscedasticity", "multicollinearity", "autocorrelation"]

            if variables:
                numeric_cols = [c for c in variables if c in df.columns and pd.api.types.is_numeric_dtype(df[c])]
            else:
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

            if not numeric_cols:
                return ToolResult(success=False, error="No numeric columns found")

            lines: list[str] = ["## Statistical Validity Check\n"]
            all_results: list[dict[str, Any]] = []

            if "normality" in check_list:
                lines.append("### Normality Tests\n")
                lines.append("| Variable | Shapiro-Wilk W | p | K-S D | p | Result |")
                lines.append("|----------|---------------|---|-------|---|--------|")
                for col in numeric_cols:
                    series = df[col].dropna()
                    if len(series) < 3:
                        continue
                    sample = series.sample(min(5000, len(series)), random_state=42) if len(series) > 5000 else series
                    sw_stat, sw_p = scipy_stats.shapiro(sample)
                    ks_stat, ks_p = scipy_stats.kstest(series, "norm", args=(series.mean(), series.std()))
                    passed = sw_p > 0.05 and ks_p > 0.05
                    result_str = "Normal" if passed else "Non-normal"
                    lines.append(
                        f"| {col} | {sw_stat:.4f} | {format_p_value(sw_p)} | {ks_stat:.4f} | {format_p_value(ks_p)} | {result_str} |"
                    )
                    all_results.append(
                        {
                            "check": "normality",
                            "variable": col,
                            "passed": passed,
                            "shapiro_p": round(sw_p, 4),
                            "ks_p": round(ks_p, 4),
                        }
                    )
                lines.append("")

            if "homoscedasticity" in check_list and dependent_var and independent_vars:
                lines.append("### Homoscedasticity Tests\n")
                try:
                    import statsmodels.api as sm
                    from statsmodels.stats.diagnostic import het_breuschpagan, het_white

                    all_vars = [dependent_var] + independent_vars
                    clean = df[all_vars].dropna()
                    y = clean[dependent_var]
                    X = sm.add_constant(clean[independent_vars])
                    result = sm.OLS(y, X).fit()
                    resid = result.resid

                    bp_stat, bp_p, _, _ = het_breuschpagan(resid, X)
                    lines.append(f"**Breusch-Pagan:** LM = {bp_stat:.2f}, p {format_p_value(bp_p)}")
                    bp_passed = bp_p > 0.05
                    lines.append(f"  {'Homoscedastic (pass)' if bp_passed else 'Heteroscedastic (fail)'}")
                    all_results.append(
                        {
                            "check": "breusch_pagan",
                            "passed": bp_passed,
                            "statistic": round(bp_stat, 2),
                            "p_value": round(bp_p, 4),
                        }
                    )

                    try:
                        white_stat, white_p, _, _ = het_white(resid, X)
                        lines.append(f"**White:** LM = {white_stat:.2f}, p {format_p_value(white_p)}")
                        white_passed = white_p > 0.05
                        all_results.append(
                            {
                                "check": "white",
                                "passed": white_passed,
                                "statistic": round(white_stat, 2),
                                "p_value": round(white_p, 4),
                            }
                        )
                    except Exception:
                        lines.append("**White test:** could not be computed")
                except ImportError:
                    lines.append("*statsmodels required for homoscedasticity tests*")
                lines.append("")

            if "multicollinearity" in check_list and independent_vars:
                lines.append("### Multicollinearity (VIF)\n")
                try:
                    import statsmodels.api as sm
                    from statsmodels.stats.outliers_influence import variance_inflation_factor

                    clean = df[independent_vars].dropna()
                    X = sm.add_constant(clean)
                    lines.append("| Variable | VIF | Status |")
                    lines.append("|----------|-----|--------|")
                    for i, var in enumerate(independent_vars):
                        vif = variance_inflation_factor(X.values, i + 1)
                        status = "OK" if vif < 5 else ("Moderate" if vif < 10 else "High")
                        passed = vif < 10
                        lines.append(f"| {var} | {vif:.2f} | {status} |")
                        all_results.append({"check": "vif", "variable": var, "passed": passed, "vif": round(vif, 2)})
                except ImportError:
                    lines.append("*statsmodels required for VIF computation*")
                lines.append("")

            if "autocorrelation" in check_list and dependent_var and independent_vars:
                lines.append("### Autocorrelation Tests\n")
                try:
                    import statsmodels.api as sm

                    all_vars = [dependent_var] + independent_vars
                    clean = df[all_vars].dropna()
                    y = clean[dependent_var]
                    X = sm.add_constant(clean[independent_vars])
                    result = sm.OLS(y, X).fit()
                    resid = result.resid

                    from statsmodels.stats.stattools import durbin_watson

                    dw = durbin_watson(resid)
                    dw_passed = 1.5 < dw < 2.5
                    lines.append(
                        f"**Durbin-Watson:** {dw:.4f} ({'no autocorrelation' if dw_passed else 'autocorrelation detected'})"
                    )
                    all_results.append({"check": "durbin_watson", "passed": dw_passed, "statistic": round(dw, 4)})

                    lb_test = sm.stats.acorr_ljungbox(resid, lags=[10], return_df=True)
                    lb_stat = float(lb_test["lb_stat"].iloc[0])
                    lb_p = float(lb_test["lb_pvalue"].iloc[0])
                    lb_passed = lb_p > 0.05
                    lines.append(
                        f"**Ljung-Box Q(10):** {lb_stat:.2f}, p {format_p_value(lb_p)} ({'pass' if lb_passed else 'fail'})"
                    )
                    all_results.append(
                        {
                            "check": "ljung_box",
                            "passed": lb_passed,
                            "statistic": round(lb_stat, 2),
                            "p_value": round(lb_p, 4),
                        }
                    )
                except ImportError:
                    lines.append("*statsmodels required for autocorrelation tests*")
                lines.append("")

            n_passed = sum(1 for r in all_results if r["passed"])
            n_total = len(all_results)
            lines.append(f"\n**Summary:** {n_passed}/{n_total} checks passed")

            results_path = _ensure_dir(Path(self._workspace_dir) / "analysis" / "results" / "statistical_validity.json")
            with open(results_path, "w") as f:
                json.dump({"checks": all_results, "passed": n_passed, "total": n_total}, f, indent=2, default=str)

            return ToolResult(success=True, content="\n".join(lines) + f"\n\n*Results saved to: {results_path}*")

        except Exception as e:
            return ToolResult(success=False, error=f"Statistical validity check failed: {e}")


class ConversationalAnalysisTool(Tool):
    """Natural language data queries using pandas operations (no pandasai dependency)."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "conversational_analysis"

    @property
    def description(self) -> str:
        return (
            "Analyze data using natural language questions. Translates queries "
            "to pandas operations via pattern matching. Supports: summary, "
            "correlation, missing values, distribution, group by, outliers, "
            "mean, max, min, unique values, and more."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to data file (CSV, Excel, Parquet, JSON)"},
                "query": {"type": "string", "description": "Natural language question about the data"},
                "output_type": {
                    "type": "string",
                    "enum": ["table", "chart", "stat"],
                    "description": "Desired output format (default: table)",
                },
            },
            "required": ["data_path", "query"],
        }

    async def execute(self, data_path: str, query: str, output_type: str = "table", **kwargs) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        full_path = _resolve_path(self._workspace_dir, data_path)
        if not full_path.exists():
            return ToolResult(success=False, error=f"Data file not found: {full_path}")

        try:
            df = _load_dataframe(full_path)
        except Exception as exc:
            return ToolResult(success=False, error=f"Failed to load data: {exc}")

        q = query.lower()
        parts: list[str] = ["## Analysis Result\n"]

        try:
            if any(kw in q for kw in ("describe", "summary", "overview", "statistics")):
                desc = df.describe(include="all").to_string()
                parts.append(f"```\n{desc}\n```")

            elif any(kw in q for kw in ("correlation", "correlate", "relationship")):
                numeric = df.select_dtypes(include=[np.number])
                if numeric.empty:
                    parts.append("No numeric columns available for correlation.")
                else:
                    corr = numeric.corr().round(3)
                    parts.append(f"**Correlation matrix:**\n```\n{corr.to_string()}\n```")

            elif any(kw in q for kw in ("missing", "null", "na ", "nan")):
                missing = df.isnull().sum()
                pct = (missing / len(df) * 100).round(2)
                info = pd.DataFrame({"missing": missing, "pct": pct})
                info = info[info["missing"] > 0].sort_values("missing", ascending=False)
                parts.append(
                    f"**Missing values:**\n```\n{info.to_string() if not info.empty else 'No missing values'}\n```"
                )

            elif any(kw in q for kw in ("mean", "average")):
                numeric = df.select_dtypes(include=[np.number])
                parts.append(f"**Means:**\n```\n{numeric.mean().round(4).to_string()}\n```")

            elif any(kw in q for kw in ("distribution", "histogram", "frequency")):
                numeric = df.select_dtypes(include=[np.number])
                desc = numeric.describe().T[["mean", "std", "min", "25%", "50%", "75%", "max"]]
                parts.append(f"**Distribution summary:**\n```\n{desc.to_string()}\n```")

            elif any(kw in q for kw in ("group", "by", "per", "each")):
                cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
                if cat_cols:
                    group_col = cat_cols[0]
                    for col in cat_cols:
                        if col.lower() in q:
                            group_col = col
                            break
                    grouped = df.groupby(group_col).mean(numeric_only=True).round(3)
                    parts.append(f"**Grouped by `{group_col}`:**\n```\n{grouped.to_string()}\n```")
                else:
                    parts.append("No categorical columns found for grouping.")

            elif any(kw in q for kw in ("count", "how many", "number of", "rows")):
                parts.append(f"**Rows:** {len(df)}, **Columns:** {len(df.columns)}")
                parts.append(f"**Column names:** {', '.join(df.columns.tolist())}")

            elif any(kw in q for kw in ("max", "maximum", "highest", "largest", "top")):
                numeric = df.select_dtypes(include=[np.number])
                parts.append(f"**Maximum values:**\n```\n{numeric.max().to_string()}\n```")

            elif any(kw in q for kw in ("min", "minimum", "lowest", "smallest", "bottom")):
                numeric = df.select_dtypes(include=[np.number])
                parts.append(f"**Minimum values:**\n```\n{numeric.min().to_string()}\n```")

            elif any(kw in q for kw in ("unique", "distinct", "categories")):
                info_lines = [f"{col}: {df[col].nunique()} unique values" for col in df.columns]
                parts.append("**Unique value counts:**\n" + "\n".join(info_lines))

            elif any(kw in q for kw in ("outlier", "anomal")):
                numeric = df.select_dtypes(include=[np.number])
                outlier_info = []
                for col in numeric.columns:
                    q1, q3 = numeric[col].quantile(0.25), numeric[col].quantile(0.75)
                    iqr = q3 - q1
                    n_outliers = int(((numeric[col] < q1 - 1.5 * iqr) | (numeric[col] > q3 + 1.5 * iqr)).sum())
                    if n_outliers > 0:
                        outlier_info.append(f"{col}: {n_outliers} outliers (IQR)")
                parts.append("**Outliers:**\n" + ("\n".join(outlier_info) if outlier_info else "No outliers detected."))

            else:
                parts.append(f"**Data shape:** {df.shape[0]} rows x {df.shape[1]} columns")
                parts.append(f"**Columns:** {', '.join(df.columns.tolist())}")
                parts.append(f"**First 5 rows:**\n```\n{df.head().to_string()}\n```")
                parts.append(
                    "\n*Tip: Try 'summary', 'correlation', 'missing values', 'distribution', 'group by', 'outliers'*"
                )

            return ToolResult(success=True, content="\n".join(parts))

        except Exception as exc:
            return ToolResult(success=False, error=f"Conversational analysis failed: {exc}")


class AutomatedEDATool(Tool):
    """Comprehensive EDA report using ydata-profiling or custom pandas-based analysis."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "automated_eda"

    @property
    def description(self) -> str:
        return (
            "Generate a comprehensive Exploratory Data Analysis report. "
            "Uses ydata-profiling when available; falls back to pandas-based EDA "
            "covering distributions, correlations, missing values, outliers, "
            "data types, warnings, and recommendations."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to data file (CSV, Excel, Parquet, JSON)"},
                "output_path": {
                    "type": "string",
                    "description": "Output file path for the report (default: analysis/eda/)",
                },
                "minimal": {"type": "boolean", "description": "Generate a minimal (faster) report (default: false)"},
            },
            "required": ["data_path"],
        }

    async def execute(
        self, data_path: str, output_path: str | None = None, minimal: bool = False, **kwargs
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        full_path = _resolve_path(self._workspace_dir, data_path)
        if not full_path.exists():
            return ToolResult(success=False, error=f"Data file not found: {full_path}")

        try:
            df = _load_dataframe(full_path)
        except Exception as exc:
            return ToolResult(success=False, error=f"Failed to load data: {exc}")

        if df.empty:
            return ToolResult(success=False, error="Dataset is empty.")

        _has_ydata = False
        try:
            from ydata_profiling import ProfileReport  # noqa: F401

            _has_ydata = True
        except ImportError:
            pass

        if _has_ydata:
            return await self._run_ydata(df, full_path.stem, output_path, minimal)
        return await self._run_pandas_eda(df, full_path.stem, output_path, minimal)

    async def _run_ydata(
        self,
        df: pd.DataFrame,
        data_name: str,
        output_path: str | None,
        minimal: bool,
    ) -> ToolResult:
        try:
            from ydata_profiling import ProfileReport

            profile = ProfileReport(df, title=f"EDA Report: {data_name}", minimal=minimal)
            out_dir = Path(self._workspace_dir) / "analysis" / "eda"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = Path(output_path) if output_path else out_dir / "eda_report.html"
            _ensure_dir(out_file)
            profile.to_file(str(out_file))
            return ToolResult(
                success=True,
                content=f"## EDA Report Generated\n\nFull HTML report saved to: {out_file}\n*Engine: ydata-profiling*",
            )
        except Exception as exc:
            return ToolResult(success=False, error=f"ydata-profiling failed: {exc}")

    async def _run_pandas_eda(
        self,
        df: pd.DataFrame,
        data_name: str,
        output_path: str | None,
        minimal: bool,
    ) -> ToolResult:
        try:
            n_rows, n_cols = df.shape
            report: dict[str, Any] = {
                "title": f"EDA Report: {data_name}",
                "overview": {
                    "n_rows": n_rows,
                    "n_columns": n_cols,
                    "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
                    "duplicate_rows": int(df.duplicated().sum()),
                    "total_missing": int(df.isnull().sum().sum()),
                    "total_missing_pct": round(df.isnull().sum().sum() / (n_rows * n_cols) * 100, 2)
                    if n_rows * n_cols > 0
                    else 0,
                },
                "variables": {},
                "warnings": [],
                "recommendations": [],
            }

            for col in df.columns:
                var_info: dict[str, Any] = {
                    "dtype": str(df[col].dtype),
                    "n_unique": int(df[col].nunique()),
                    "n_missing": int(df[col].isnull().sum()),
                    "missing_pct": round(df[col].isnull().sum() / n_rows * 100, 2) if n_rows > 0 else 0,
                }
                if pd.api.types.is_numeric_dtype(df[col]):
                    series = df[col].dropna()
                    if len(series) > 0:
                        var_info.update(
                            {
                                "mean": round(float(series.mean()), 4),
                                "std": round(float(series.std()), 4),
                                "min": round(float(series.min()), 4),
                                "median": round(float(series.median()), 4),
                                "max": round(float(series.max()), 4),
                                "skewness": round(float(series.skew()), 4),
                                "kurtosis": round(float(series.kurtosis()), 4),
                            }
                        )
                report["variables"][col] = var_info

            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) >= 2:
                corr = numeric_df.corr()
                for i, c1 in enumerate(corr.columns):
                    for c2 in corr.columns[i + 1 :]:
                        r = abs(corr.loc[c1, c2])
                        if r > 0.9:
                            report["warnings"].append(f"High correlation ({r:.3f}) between '{c1}' and '{c2}'")

            if not minimal:
                for col in numeric_df.columns:
                    series = numeric_df[col].dropna()
                    if len(series) < 4:
                        continue
                    q1, q3 = series.quantile(0.25), series.quantile(0.75)
                    iqr = q3 - q1
                    n_out = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())
                    if n_out > 0:
                        report["warnings"].append(f"'{col}': {n_out} outliers detected (IQR)")

            if report["overview"]["duplicate_rows"] > 0:
                report["warnings"].append(f"{report['overview']['duplicate_rows']} duplicate rows")
            for col, info in report["variables"].items():
                if info["missing_pct"] > 50:
                    report["warnings"].append(f"'{col}' has {info['missing_pct']}% missing — consider dropping")
                if info["n_unique"] == 1:
                    report["warnings"].append(f"'{col}' is constant — no analytical value")

            if report["overview"]["total_missing_pct"] > 0:
                report["recommendations"].append("Handle missing values before analysis")
            if report["overview"]["duplicate_rows"] > 0:
                report["recommendations"].append("Investigate and remove duplicate rows")

            score = 100.0
            score -= min(report["overview"]["total_missing_pct"], 30)
            score -= min(report["overview"]["duplicate_rows"] / max(n_rows, 1) * 100, 20)
            score -= min(len(report["warnings"]) * 2, 20)
            report["data_quality_score"] = round(max(score, 0), 1)

            out_dir = Path(self._workspace_dir) / "analysis" / "eda"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = Path(output_path) if output_path else out_dir / "eda_report.json"
            _ensure_dir(out_file)
            out_file.write_text(json.dumps(report, indent=2, default=str))

            lines = [
                "## Automated EDA Report\n",
                f"**Dataset:** {data_name}",
                f"**Rows:** {n_rows} | **Columns:** {n_cols}",
                f"**Missing:** {report['overview']['total_missing']} ({report['overview']['total_missing_pct']}%)",
                f"**Duplicates:** {report['overview']['duplicate_rows']}",
                f"**Quality score:** {report['data_quality_score']}/100\n",
            ]
            if report["warnings"]:
                lines.append("### Warnings")
                for w in report["warnings"][:10]:
                    lines.append(f"- {w}")
                lines.append("")
            if report["recommendations"]:
                lines.append("### Recommendations")
                for r in report["recommendations"]:
                    lines.append(f"- {r}")
            lines.append(f"\n*Full report saved to: {out_file}*")

            return ToolResult(success=True, content="\n".join(lines))

        except Exception as exc:
            return ToolResult(success=False, error=f"Pandas EDA failed: {exc}")


class AutoVisualizeTool(Tool):
    """Automatically suggest and create appropriate visualizations."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "auto_visualize"

    @property
    def description(self) -> str:
        return (
            "Automatically suggest and create appropriate visualizations based on "
            "data types and relationships. Analyzes column types to pick best chart "
            "types (histogram, scatter, heatmap, box, bar, line). "
            "Generates publication-quality figures at 300 DPI."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "data_path": {"type": "string", "description": "Path to data file (CSV, Excel, Parquet, JSON)"},
                "goal": {"type": "string", "description": "Describe what to visualize (auto-detected if omitted)"},
                "output_dir": {
                    "type": "string",
                    "description": "Output directory for figures (default: analysis/figures/auto)",
                },
            },
            "required": ["data_path"],
        }

    async def execute(
        self, data_path: str, goal: str | None = None, output_dir: str | None = None, **kwargs
    ) -> ToolResult:
        if (err := _require_numpy()) is not None:
            return err
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
        except ImportError:
            return ToolResult(success=False, error="matplotlib is required. Run: pip install matplotlib")

        try:
            import seaborn as sns

            _has_seaborn = True
        except ImportError:
            _has_seaborn = False

        full_path = _resolve_path(self._workspace_dir, data_path)
        if not full_path.exists():
            return ToolResult(success=False, error=f"Data file not found: {full_path}")

        try:
            df = _load_dataframe(full_path)
        except Exception as exc:
            return ToolResult(success=False, error=f"Failed to load data: {exc}")

        if df.empty:
            return ToolResult(success=False, error="Dataset is empty.")

        fig_dir = Path(output_dir) if output_dir else Path(self._workspace_dir) / "analysis" / "figures" / "auto"
        fig_dir.mkdir(parents=True, exist_ok=True)

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        suggestions: list[dict[str, Any]] = []

        for col in numeric_cols[:3]:
            suggestions.append({"type": "histogram", "cols": [col], "title": f"Distribution of {col}"})

        if len(numeric_cols) >= 2:
            suggestions.append(
                {
                    "type": "scatter",
                    "cols": [numeric_cols[0], numeric_cols[1]],
                    "title": f"{numeric_cols[0]} vs {numeric_cols[1]}",
                }
            )

        if len(numeric_cols) >= 3:
            suggestions.append({"type": "heatmap", "cols": numeric_cols, "title": "Correlation Matrix"})

        if numeric_cols and categorical_cols:
            cat = categorical_cols[0]
            num = numeric_cols[0]
            if df[cat].nunique() <= 10:
                suggestions.append({"type": "box", "cols": [cat, num], "title": f"{num} by {cat}"})

        for col in categorical_cols[:2]:
            if df[col].nunique() <= 15:
                suggestions.append({"type": "bar", "cols": [col], "title": f"Counts of {col}"})

        if datetime_cols and numeric_cols:
            suggestions.append(
                {"type": "line", "cols": [datetime_cols[0], numeric_cols[0]], "title": f"{numeric_cols[0]} over time"}
            )

        if not suggestions:
            return ToolResult(success=False, error="Could not determine suitable visualizations for this dataset.")

        OKABE_ITO = ["#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#000000"]
        plt.rcParams.update(
            {
                "figure.dpi": 300,
                "savefig.dpi": 300,
                "savefig.bbox": "tight",
                "font.family": "sans-serif",
                "font.size": 9,
                "axes.spines.top": False,
                "axes.spines.right": False,
                "axes.prop_cycle": plt.cycler("color", OKABE_ITO),
            }
        )

        all_parts: list[str] = ["## Auto-Generated Visualizations\n"]
        image_paths: list[str] = []

        for i, s in enumerate(suggestions[:6]):
            fig, ax = plt.subplots(figsize=(8, 5))
            plot_type = s["type"]
            cols = s["cols"]

            try:
                if plot_type == "histogram" and _has_seaborn:
                    sns.histplot(data=df, x=cols[0], kde=True, ax=ax)
                elif plot_type == "histogram":
                    ax.hist(df[cols[0]].dropna(), bins=30, edgecolor="black", alpha=0.7)
                elif plot_type == "scatter" and _has_seaborn:
                    sns.scatterplot(data=df, x=cols[0], y=cols[1], ax=ax, alpha=0.6, s=20)
                elif plot_type == "scatter":
                    ax.scatter(df[cols[0]], df[cols[1]], alpha=0.6, s=20)
                elif plot_type == "heatmap" and _has_seaborn:
                    corr = df[cols].corr()
                    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", vmin=-1, vmax=1, ax=ax, square=True)
                elif plot_type == "box" and _has_seaborn:
                    sns.boxplot(data=df, x=cols[0], y=cols[1], ax=ax)
                elif plot_type == "bar":
                    counts = df[cols[0]].value_counts()
                    ax.bar(counts.index.astype(str), counts.values)
                elif plot_type == "line":
                    sorted_df = df.sort_values(cols[0])
                    ax.plot(sorted_df[cols[0]], sorted_df[cols[1]])

                ax.set_title(s["title"], fontsize=11, fontweight="bold")
                fig.tight_layout()
                img_path = fig_dir / f"auto_viz_{i + 1}.png"
                fig.savefig(str(img_path), dpi=300, bbox_inches="tight")
                plt.close(fig)

                all_parts.append(f"### {i + 1}. {s['title']}")
                all_parts.append(f"*Type: {plot_type} | Saved to: {img_path}*\n")
                image_paths.append(str(img_path))

            except Exception as exc:
                plt.close(fig)
                all_parts.append(f"### {i + 1}. {s['title']} — failed: {exc}\n")

        all_parts.append(f"\n**Total figures generated:** {len(image_paths)}")
        return ToolResult(success=True, content="\n".join(all_parts))


# Backward-compatible alias for sandbox tool import
try:
    from .sandbox_tools import PythonREPLTool as PythonReplTool  # noqa: F401
except ImportError:
    pass
