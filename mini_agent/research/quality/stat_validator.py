"""Statistical validator for research results.

Validates statistical analyses by checking assumptions, effect sizes, power,
and reporting completeness.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class AssumptionCheck(BaseModel):
    """Result of a single statistical assumption check."""

    name: str
    test: str = ""
    passed: bool = False
    statistic: float | None = None
    p_value: float | None = None
    details: str = ""
    recommendation: str = ""


class ValidationReport(BaseModel):
    """Aggregated validation report for statistical results."""

    passed: bool = True
    issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    checks: list[AssumptionCheck] = Field(default_factory=list)


class StatisticalValidator:
    """Validate statistical analyses in a research workspace.

    Parameters
    ----------
    workspace_path:
        Root directory of the research workspace.
    """

    def __init__(self, workspace_path: str | Path) -> None:
        self.workspace_path = Path(workspace_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate_results(self, results_dir: str | Path | None = None) -> ValidationReport:
        """Validate all JSON result files in *results_dir*.

        Parameters
        ----------
        results_dir:
            Directory containing result JSON files.  Defaults to
            ``analysis/results/`` within the workspace.

        Returns
        -------
        ValidationReport
        """
        if results_dir is None:
            rdir = self.workspace_path / "analysis" / "results"
        else:
            rdir = Path(results_dir)
            if not rdir.is_absolute():
                rdir = self.workspace_path / rdir

        report = ValidationReport()

        if not rdir.exists():
            report.passed = False
            report.issues.append(f"Results directory not found: {rdir}")
            return report

        result_files = list(rdir.glob("*.json"))
        if not result_files:
            report.warnings.append("No JSON result files found.")
            return report

        for rf in result_files:
            try:
                data = json.loads(rf.read_text(encoding="utf-8"))
                self._validate_single(data, report)
            except (json.JSONDecodeError, OSError) as exc:
                report.issues.append(f"Could not read {rf.name}: {exc}")

        report.passed = len(report.issues) == 0
        return report

    def check_assumptions(
        self,
        data_path: str | Path,
        test_type: str = "ols",
    ) -> list[AssumptionCheck]:
        """Run assumption checks appropriate for *test_type*.

        Parameters
        ----------
        data_path:
            Path to a JSON file containing residuals, fitted values, etc.
        test_type:
            Statistical test type: ``"ols"``, ``"logistic"``, ``"anova"``,
            ``"t_test"``, ``"correlation"``.

        Returns
        -------
        list[AssumptionCheck]
        """
        path = Path(data_path)
        if not path.is_absolute():
            path = self.workspace_path / path

        if not path.exists():
            return [
                AssumptionCheck(
                    name="file_access",
                    passed=False,
                    details=f"Data file not found: {path}",
                )
            ]

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            return [
                AssumptionCheck(
                    name="file_access",
                    passed=False,
                    details=f"Could not read data: {exc}",
                )
            ]

        checks: list[AssumptionCheck] = []

        if test_type in ("ols", "logistic", "anova"):
            checks.append(self._check_normality(data))
            checks.append(self._check_homoscedasticity(data))
        if test_type == "ols":
            checks.append(self._check_multicollinearity(data))
            checks.append(self._check_autocorrelation(data))
        if test_type in ("t_test", "anova"):
            checks.append(self._check_sample_size(data))

        return checks

    def verify_effect_sizes(self, results: dict[str, Any]) -> list[str]:
        """Check that effect sizes are reported and within plausible ranges.

        Returns a list of issue strings (empty if all OK).
        """
        issues: list[str] = []
        effect_keys = [
            "r_squared",
            "adj_r_squared",
            "cohens_d",
            "eta_squared",
            "partial_eta_squared",
            "omega_squared",
            "cramers_v",
            "odds_ratio",
        ]

        found = {k: results[k] for k in effect_keys if k in results and results[k] is not None}

        if not found:
            issues.append(
                "No effect size measures reported. APA 7th edition requires effect sizes for all statistical tests."
            )
            return issues

        # Range checks
        for key, value in found.items():
            try:
                v = float(value)
            except (TypeError, ValueError):
                issues.append(f"Effect size '{key}' is not numeric: {value}")
                continue

            if key in ("r_squared", "adj_r_squared", "eta_squared", "partial_eta_squared", "omega_squared"):
                if not (0.0 <= v <= 1.0):
                    issues.append(f"Effect size '{key}' = {v:.4f} is outside [0, 1].")
            elif key == "cohens_d":
                if abs(v) > 5.0:
                    issues.append(f"Cohen's d = {v:.4f} is unusually large (|d| > 5).")
            elif key == "odds_ratio":
                if v <= 0:
                    issues.append(f"Odds ratio = {v:.4f} must be positive.")

        return issues

    def check_power(
        self,
        n: int,
        effect_size: float,
        alpha: float = 0.05,
    ) -> float:
        """Approximate statistical power for a two-tailed z-test.

        Uses the normal approximation:
            power ≈ Φ(|δ| - z_{α/2})

        where δ = effect_size * √n.

        Parameters
        ----------
        n:
            Sample size.
        effect_size:
            Standardized effect size (e.g. Cohen's d).
        alpha:
            Significance level.

        Returns
        -------
        float
            Estimated power (0–1).
        """
        if n <= 0 or effect_size == 0:
            return 0.0

        # z critical value for two-tailed test
        z_alpha = self._z_critical(alpha / 2)
        # Non-centrality parameter
        delta = abs(effect_size) * math.sqrt(n)
        # Power = P(Z > z_alpha - delta) = Phi(delta - z_alpha)
        power = self._norm_cdf(delta - z_alpha)
        return min(max(power, 0.0), 1.0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_single(self, data: dict[str, Any], report: ValidationReport) -> None:
        """Validate a single results dict and append findings to *report*."""
        # Check effect size reporting
        effect_issues = self.verify_effect_sizes(data)
        for issue in effect_issues:
            report.issues.append(issue)

        # Check sample size
        n = data.get("n", 0)
        k = len(data.get("independent_vars", data.get("coefficients", {})))
        if n > 0 and k > 0:
            min_n = 10 * k + 50
            if n < min_n:
                report.warnings.append(
                    f"Sample size n={n} may be insufficient for {k} predictors "
                    f"(recommend n ≥ {min_n}, Tabachnick & Fidell)."
                )

        # Check confidence intervals
        ci_keys = ["confidence_intervals", "ci", "conf_int", "ci_lower", "ci_upper"]
        has_ci = any(k in data for k in ci_keys)
        if not has_ci:
            report.recommendations.append("Report 95% confidence intervals for key estimates.")

        # Check p-value reporting
        if "p_value" in data or "p_values" in data:
            # Ensure test statistic is also present
            stat_keys = ["t_statistic", "f_statistic", "chi_square", "z_statistic"]
            if not any(k in data for k in stat_keys):
                report.warnings.append("p-value reported without corresponding test statistic.")

    def _check_normality(self, data: dict[str, Any]) -> AssumptionCheck:
        """Check normality of residuals using Shapiro-Wilk if scipy available."""
        residuals = data.get("residuals")
        if not residuals or not isinstance(residuals, list) or len(residuals) < 3:
            return AssumptionCheck(
                name="normality",
                test="Shapiro-Wilk",
                passed=True,
                details="Insufficient residual data for normality test.",
            )

        try:
            import numpy as np
            from scipy import stats as scipy_stats

            arr = np.array(residuals[:5000], dtype=float)
            stat, p_value = scipy_stats.shapiro(arr)
            passed = p_value > 0.05
            return AssumptionCheck(
                name="normality",
                test="Shapiro-Wilk",
                passed=passed,
                statistic=round(float(stat), 4),
                p_value=round(float(p_value), 4),
                details=f"W={stat:.4f}, p={p_value:.4f}",
                recommendation="" if passed else "Consider robust methods or transformations.",
            )
        except ImportError:
            return AssumptionCheck(
                name="normality",
                test="Shapiro-Wilk",
                passed=True,
                details="scipy not available; skipped.",
            )

    def _check_homoscedasticity(self, data: dict[str, Any]) -> AssumptionCheck:
        """Check homoscedasticity using Breusch-Pagan if statsmodels available."""
        residuals = data.get("residuals")
        fitted = data.get("fitted_values")
        if not residuals or not fitted:
            return AssumptionCheck(
                name="homoscedasticity",
                test="Breusch-Pagan",
                passed=True,
                details="Insufficient data for homoscedasticity test.",
            )

        try:
            import numpy as np
            import statsmodels.api as sm
            from statsmodels.stats.diagnostic import het_breuschpagan

            resid = np.array(residuals, dtype=float)
            exog = sm.add_constant(np.array(fitted, dtype=float).reshape(-1, 1))
            lm_stat, lm_p, _, _ = het_breuschpagan(resid, exog)
            passed = lm_p > 0.05
            return AssumptionCheck(
                name="homoscedasticity",
                test="Breusch-Pagan",
                passed=passed,
                statistic=round(float(lm_stat), 4),
                p_value=round(float(lm_p), 4),
                details=f"LM={lm_stat:.4f}, p={lm_p:.4f}",
                recommendation="" if passed else "Use robust standard errors (HC3).",
            )
        except ImportError:
            return AssumptionCheck(
                name="homoscedasticity",
                test="Breusch-Pagan",
                passed=True,
                details="statsmodels not available; skipped.",
            )

    def _check_multicollinearity(self, data: dict[str, Any]) -> AssumptionCheck:
        """Check VIF for multicollinearity."""
        exog = data.get("exog")
        if not exog:
            return AssumptionCheck(
                name="multicollinearity",
                test="VIF",
                passed=True,
                details="No design matrix (exog) provided.",
            )

        try:
            import numpy as np
            import statsmodels.api as sm
            from statsmodels.stats.outliers_influence import variance_inflation_factor

            arr = np.array(exog, dtype=float)
            if not np.all(arr[:, 0] == 1.0):
                arr = sm.add_constant(arr)

            vifs = [variance_inflation_factor(arr, i) for i in range(arr.shape[1])]
            max_vif = max(vifs[1:]) if len(vifs) > 1 else 0  # skip constant
            passed = max_vif < 10
            return AssumptionCheck(
                name="multicollinearity",
                test="VIF",
                passed=passed,
                statistic=round(float(max_vif), 2),
                details=f"Max VIF={max_vif:.2f}",
                recommendation="" if passed else "Remove correlated predictors or use ridge regression.",
            )
        except ImportError:
            return AssumptionCheck(
                name="multicollinearity",
                test="VIF",
                passed=True,
                details="statsmodels not available; skipped.",
            )

    def _check_autocorrelation(self, data: dict[str, Any]) -> AssumptionCheck:
        """Check Durbin-Watson statistic."""
        residuals = data.get("residuals")
        if not residuals or len(residuals) < 3:
            return AssumptionCheck(
                name="autocorrelation",
                test="Durbin-Watson",
                passed=True,
                details="Insufficient residual data.",
            )

        try:
            import numpy as np
            from statsmodels.stats.stattools import durbin_watson

            arr = np.array(residuals, dtype=float)
            dw = float(durbin_watson(arr))
            passed = 1.5 <= dw <= 2.5
            return AssumptionCheck(
                name="autocorrelation",
                test="Durbin-Watson",
                passed=passed,
                statistic=round(dw, 4),
                details=f"DW={dw:.4f}",
                recommendation="" if passed else "Consider Newey-West standard errors.",
            )
        except ImportError:
            return AssumptionCheck(
                name="autocorrelation",
                test="Durbin-Watson",
                passed=True,
                details="statsmodels not available; skipped.",
            )

    def _check_sample_size(self, data: dict[str, Any]) -> AssumptionCheck:
        """Check sample size adequacy."""
        n = data.get("n", 0)
        if n <= 0:
            return AssumptionCheck(
                name="sample_size",
                test="Adequacy",
                passed=True,
                details="Sample size not specified.",
            )

        passed = n >= 30
        return AssumptionCheck(
            name="sample_size",
            test="Adequacy (n ≥ 30)",
            passed=passed,
            statistic=float(n),
            details=f"n={n}",
            recommendation="" if passed else "Sample size < 30; CLT may not apply.",
        )

    @staticmethod
    def _norm_cdf(x: float) -> float:
        """Standard normal CDF approximation (Abramowitz & Stegun)."""
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    @staticmethod
    def _z_critical(p: float) -> float:
        """Approximate z critical value for tail probability *p*."""
        # Rational approximation (Beasley-Springer-Moro)
        if p <= 0 or p >= 1:
            return 0.0
        if p > 0.5:
            return -StatisticalValidator._z_critical(1.0 - p)

        t = math.sqrt(-2.0 * math.log(p))
        # Coefficients for rational approximation
        c0, c1, c2 = 2.515517, 0.802853, 0.010328
        d1, d2, d3 = 1.432788, 0.189269, 0.001308
        return t - (c0 + c1 * t + c2 * t * t) / (1.0 + d1 * t + d2 * t * t + d3 * t * t * t)
