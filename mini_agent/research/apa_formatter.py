"""APA 7th Edition statistical result formatter.

Formats statistical test results according to APA Publication Manual standards.
"""

from __future__ import annotations


def format_p_value(p: float) -> str:
    """Format p-value in APA style."""
    if p < 0.001:
        return "< .001"
    return f"= {p:.3f}".replace("0.", ".")


def format_ttest(t: float, df: int | float, p: float, d: float | None = None) -> str:
    """Format t-test result: t(df) = value, p = value, d = value."""
    result = f"t({df:.0f}) = {t:.2f}, p {format_p_value(p)}"
    if d is not None:
        result += f", d = {d:.2f}"
    return result


def format_anova(f: float, df1: int, df2: int, p: float, eta_sq: float | None = None) -> str:
    """Format ANOVA result: F(df1, df2) = value, p = value, η² = value."""
    result = f"F({df1}, {df2}) = {f:.2f}, p {format_p_value(p)}"
    if eta_sq is not None:
        result += f", η² = {eta_sq:.3f}".replace("0.", ".")
    return result


def format_correlation(r: float, n: int, p: float) -> str:
    """Format correlation: r(df) = value, p = value."""
    df = n - 2
    return f"r({df}) = {r:.2f}, p {format_p_value(p)}".replace("r({df}) = 0.", f"r({df}) = .")


def format_chi_square(chi2: float, df: int, n: int, p: float, v: float | None = None) -> str:
    """Format chi-square: χ²(df, N = value) = value, p = value."""
    result = f"χ²({df}, N = {n}) = {chi2:.2f}, p {format_p_value(p)}"
    if v is not None:
        result += f", V = {v:.2f}"
    return result


def format_regression(r_sq: float, f: float, df1: int, df2: int, p: float) -> str:
    """Format regression: R² = value, F(df1, df2) = value, p = value."""
    return f"R² = {r_sq:.3f}, F({df1}, {df2}) = {f:.2f}, p {format_p_value(p)}".replace("R² = 0.", "R² = .")


def format_ci(lower: float, upper: float, level: int = 95) -> str:
    """Format confidence interval: 95% CI [lower, upper]."""
    return f"{level}% CI [{lower:.2f}, {upper:.2f}]"


def format_descriptive(mean: float, sd: float, n: int) -> str:
    """Format descriptive statistics: M = value, SD = value, n = value."""
    return f"M = {mean:.2f}, SD = {sd:.2f}, n = {n}"
