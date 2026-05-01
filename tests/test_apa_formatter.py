"""Tests for mini_agent/research/apa_formatter.py.

Covers all APA formatting functions.
"""

import pytest

from mini_agent.research.apa_formatter import (
    format_anova,
    format_chi_square,
    format_ci,
    format_correlation,
    format_descriptive,
    format_p_value,
    format_regression,
    format_ttest,
)


class TestFormatPValue:
    def test_very_small(self):
        assert format_p_value(0.0001) == "< .001"

    def test_small(self):
        result = format_p_value(0.001)
        # 0.001 is not < 0.001, so it should be "= .001"
        assert "001" in result

    def test_medium(self):
        result = format_p_value(0.05)
        assert "= .050" in result

    def test_large(self):
        result = format_p_value(0.5)
        assert "= .500" in result

    def test_zero(self):
        assert format_p_value(0.0) == "< .001"

    def test_one(self):
        result = format_p_value(1.0)
        assert "1.000" in result


class TestFormatTtest:
    def test_basic(self):
        result = format_ttest(2.5, 30, 0.02)
        assert "t(30)" in result
        assert "2.50" in result

    def test_with_effect_size(self):
        result = format_ttest(2.5, 30, 0.02, d=0.8)
        assert "d = 0.80" in result

    def test_without_effect_size(self):
        result = format_ttest(1.5, 20, 0.15)
        assert "d" not in result


class TestFormatAnova:
    def test_basic(self):
        result = format_anova(5.2, 2, 57, 0.008)
        assert "F(2, 57)" in result
        assert "5.20" in result

    def test_with_eta_squared(self):
        result = format_anova(5.2, 2, 57, 0.008, eta_sq=0.15)
        assert "η²" in result or "eta" in result.lower()

    def test_without_eta_squared(self):
        result = format_anova(3.0, 1, 50, 0.09)
        assert "η²" not in result


class TestFormatCorrelation:
    def test_basic(self):
        result = format_correlation(0.65, 50, 0.001)
        assert "r(" in result
        assert "48)" in result  # df = n - 2


class TestFormatChiSquare:
    def test_basic(self):
        result = format_chi_square(12.5, 3, 100, 0.006)
        assert "χ²" in result
        assert "N = 100" in result

    def test_with_cramers_v(self):
        result = format_chi_square(12.5, 3, 100, 0.006, v=0.35)
        assert "V = 0.35" in result

    def test_without_cramers_v(self):
        result = format_chi_square(5.0, 1, 50, 0.025)
        assert "V" not in result


class TestFormatRegression:
    def test_basic(self):
        result = format_regression(0.45, 15.3, 2, 47, 0.001)
        assert "R²" in result
        assert "F(2, 47)" in result


class TestFormatCI:
    def test_default_95(self):
        result = format_ci(1.5, 3.5)
        assert "95% CI" in result
        assert "[1.50, 3.50]" in result

    def test_custom_level(self):
        result = format_ci(1.0, 4.0, level=99)
        assert "99% CI" in result


class TestFormatDescriptive:
    def test_basic(self):
        result = format_descriptive(5.5, 1.2, 100)
        assert "M = 5.50" in result
        assert "SD = 1.20" in result
        assert "n = 100" in result
