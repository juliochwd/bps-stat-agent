"""Tests for mini_agent/research/quality/ — stat validator, peer reviewer, citation verifier, writing quality."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.research.quality.stat_validator import (
    AssumptionCheck,
    StatisticalValidator,
    ValidationReport,
)
from mini_agent.research.quality.peer_reviewer import PeerReviewer, ReviewResult
from mini_agent.research.quality.citation_verifier import (
    CitationVerifier,
    VerificationDetail,
    VerificationReport,
)
from mini_agent.research.quality.writing_quality import (
    GrammarIssue,
    QualityReport,
    ReadabilityReport,
    StyleIssue,
    WritingQualityChecker,
)


# ===================================================================
# Statistical Validator Tests
# ===================================================================


class TestAssumptionCheck:
    def test_defaults(self):
        ac = AssumptionCheck(name="test")
        assert ac.name == "test"
        assert ac.passed is False
        assert ac.statistic is None
        assert ac.p_value is None


class TestValidationReport:
    def test_defaults(self):
        vr = ValidationReport()
        assert vr.passed is True
        assert vr.issues == []
        assert vr.warnings == []


class TestStatisticalValidator:
    @pytest.fixture
    def validator(self, tmp_path):
        return StatisticalValidator(workspace_path=tmp_path)

    def test_validate_results_no_dir(self, validator):
        """Test when results directory doesn't exist."""
        report = validator.validate_results()
        assert report.passed is False
        assert "not found" in report.issues[0]

    def test_validate_results_empty_dir(self, validator, tmp_path):
        """Test when results directory is empty."""
        results_dir = tmp_path / "analysis" / "results"
        results_dir.mkdir(parents=True)

        report = validator.validate_results()
        assert "No JSON result files" in report.warnings[0]

    def test_validate_results_valid(self, validator, tmp_path):
        """Test with valid results file."""
        results_dir = tmp_path / "analysis" / "results"
        results_dir.mkdir(parents=True)

        result_data = {
            "r_squared": 0.75,
            "n": 200,
            "independent_vars": ["x1", "x2"],
            "p_value": 0.001,
            "t_statistic": 3.5,
            "confidence_intervals": [[0.1, 0.5]],
        }
        (results_dir / "regression.json").write_text(json.dumps(result_data))

        report = validator.validate_results()
        assert report.passed is True

    def test_validate_results_invalid_json(self, validator, tmp_path):
        """Test with invalid JSON file."""
        results_dir = tmp_path / "analysis" / "results"
        results_dir.mkdir(parents=True)
        (results_dir / "bad.json").write_text("not json")

        report = validator.validate_results()
        assert len(report.issues) > 0

    def test_validate_results_custom_dir(self, validator, tmp_path):
        """Test with custom results directory."""
        custom_dir = tmp_path / "custom_results"
        custom_dir.mkdir()
        result_data = {"r_squared": 0.5, "n": 100, "t_statistic": 2.0, "p_value": 0.04}
        (custom_dir / "test.json").write_text(json.dumps(result_data))

        report = validator.validate_results(results_dir=custom_dir)
        assert isinstance(report, ValidationReport)

    def test_check_assumptions_file_not_found(self, validator):
        """Test assumption checks when file doesn't exist."""
        checks = validator.check_assumptions("nonexistent.json")
        assert len(checks) == 1
        assert checks[0].name == "file_access"
        assert checks[0].passed is False

    def test_check_assumptions_invalid_json(self, validator, tmp_path):
        """Test assumption checks with invalid JSON."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json")

        checks = validator.check_assumptions(str(bad_file))
        assert len(checks) == 1
        assert checks[0].passed is False

    def test_check_assumptions_ols(self, validator, tmp_path):
        """Test OLS assumption checks."""
        data = {
            "residuals": [0.1, -0.2, 0.3, -0.1, 0.2, -0.3, 0.1, -0.1, 0.2, -0.2],
            "fitted_values": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
        }
        data_file = tmp_path / "ols_data.json"
        data_file.write_text(json.dumps(data))

        checks = validator.check_assumptions(str(data_file), test_type="ols")
        # Should have normality, homoscedasticity, multicollinearity, autocorrelation
        assert len(checks) >= 3

    def test_check_assumptions_t_test(self, validator, tmp_path):
        """Test t-test assumption checks."""
        data = {"n": 50, "residuals": list(range(50))}
        data_file = tmp_path / "ttest_data.json"
        data_file.write_text(json.dumps(data))

        checks = validator.check_assumptions(str(data_file), test_type="t_test")
        names = [c.name for c in checks]
        assert "sample_size" in names

    def test_verify_effect_sizes_none(self, validator):
        """Test when no effect sizes are reported."""
        issues = validator.verify_effect_sizes({})
        assert len(issues) == 1
        assert "No effect size" in issues[0]

    def test_verify_effect_sizes_valid(self, validator):
        """Test with valid effect sizes."""
        issues = validator.verify_effect_sizes({"r_squared": 0.5, "cohens_d": 0.8})
        assert issues == []

    def test_verify_effect_sizes_out_of_range(self, validator):
        """Test with out-of-range effect sizes."""
        issues = validator.verify_effect_sizes({"r_squared": 1.5})
        assert len(issues) == 1
        assert "outside [0, 1]" in issues[0]

    def test_verify_effect_sizes_large_cohens_d(self, validator):
        """Test with unusually large Cohen's d."""
        issues = validator.verify_effect_sizes({"cohens_d": 10.0})
        assert len(issues) == 1
        assert "unusually large" in issues[0]

    def test_verify_effect_sizes_negative_odds_ratio(self, validator):
        """Test with negative odds ratio."""
        issues = validator.verify_effect_sizes({"odds_ratio": -1.0})
        assert len(issues) == 1
        assert "positive" in issues[0]

    def test_check_power(self, validator):
        """Test power calculation."""
        power = validator.check_power(n=100, effect_size=0.5)
        assert 0.0 <= power <= 1.0
        assert power > 0.5  # Should have decent power

    def test_check_power_zero_effect(self, validator):
        """Test power with zero effect size."""
        power = validator.check_power(n=100, effect_size=0.0)
        assert power == 0.0

    def test_check_power_zero_n(self, validator):
        """Test power with zero sample size."""
        power = validator.check_power(n=0, effect_size=0.5)
        assert power == 0.0

    def test_norm_cdf(self, validator):
        """Test normal CDF approximation."""
        assert abs(validator._norm_cdf(0) - 0.5) < 0.001
        assert validator._norm_cdf(3.0) > 0.99
        assert validator._norm_cdf(-3.0) < 0.01

    def test_z_critical(self, validator):
        """Test z critical value."""
        z = validator._z_critical(0.025)
        assert abs(z - 1.96) < 0.01

    def test_z_critical_edge_cases(self, validator):
        """Test z critical edge cases."""
        assert validator._z_critical(0.0) == 0.0
        assert validator._z_critical(1.0) == 0.0


# ===================================================================
# Peer Reviewer Tests
# ===================================================================


class TestReviewResult:
    def test_defaults(self):
        rr = ReviewResult()
        assert rr.score == 3
        assert rr.strengths == []
        assert rr.weaknesses == []


class TestPeerReviewer:
    @pytest.fixture
    def reviewer(self, tmp_path):
        return PeerReviewer(workspace_path=tmp_path)

    def test_review_methodology(self, reviewer):
        """Test methodology review."""
        text = """
        This study uses a cross-sectional design with a sample size of n=500 respondents.
        Data was collected through questionnaires distributed to participants.
        We employ OLS regression analysis with dependent variable poverty_rate
        and independent variables education_spending and gdp_per_capita.
        """
        result = reviewer.review_methodology(text)
        assert isinstance(result, ReviewResult)
        assert result.score >= 1

    def test_review_methodology_minimal(self, reviewer):
        """Test methodology review with minimal content."""
        result = reviewer.review_methodology("Short text.")
        assert isinstance(result, ReviewResult)
        assert len(result.weaknesses) > 0 or len(result.suggestions) > 0

    def test_review_statistics(self, reviewer):
        """Test statistics/results review."""
        text = """
        The regression results show a significant relationship (β = 0.45, p < 0.001).
        The R-squared value is 0.72, indicating good model fit.
        Cohen's d = 0.8 suggests a large effect size.
        """
        result = reviewer.review_section("results", text)
        assert isinstance(result, ReviewResult)

    def test_review_generic_section(self, reviewer):
        """Test generic section review."""
        result = reviewer.review_section("introduction", "This paper examines poverty in Indonesia.")
        assert isinstance(result, ReviewResult)


# ===================================================================
# Citation Verifier Tests
# ===================================================================


class TestVerificationDetail:
    def test_defaults(self):
        vd = VerificationDetail(key="smith2020")
        assert vd.key == "smith2020"
        assert vd.verified is False
        assert vd.doi == ""


class TestVerificationReport:
    def test_defaults(self):
        vr = VerificationReport()
        assert vr.total == 0
        assert vr.verified == 0
        assert vr.failed == 0


class TestCitationVerifier:
    @pytest.fixture
    def bib_file(self, tmp_path):
        bib_content = """
@article{smith2020,
  author = {Smith, John},
  title = {A Study},
  journal = {Journal of Testing},
  year = {2020},
  doi = {10.1234/test.2020}
}

@article{jones2021,
  author = {Jones, Jane},
  title = {Another Study},
  journal = {Journal of Research},
  year = {2021}
}
"""
        bib_path = tmp_path / "references.bib"
        bib_path.write_text(bib_content)
        return bib_path

    def test_init(self, bib_file):
        verifier = CitationVerifier(bib_file)
        assert verifier.bib_path == bib_file

    def test_verify_all_no_network(self, bib_file):
        """Test verify_all without network (mocked)."""
        verifier = CitationVerifier(bib_file)
        with patch("mini_agent.research.quality.citation_verifier._HAS_REQUESTS", False):
            report = verifier.verify_all()
            assert isinstance(report, VerificationReport)


# ===================================================================
# Writing Quality Tests
# ===================================================================


class TestGrammarIssue:
    def test_defaults(self):
        gi = GrammarIssue()
        assert gi.rule == ""
        assert gi.severity == "warning"


class TestStyleIssue:
    def test_defaults(self):
        si = StyleIssue()
        assert si.rule == ""
        assert si.severity == "warning"


class TestReadabilityReport:
    def test_defaults(self):
        rr = ReadabilityReport()
        assert rr.word_count == 0
        assert rr.flesch_kincaid_grade == 0.0


class TestQualityReport:
    def test_defaults(self):
        qr = QualityReport()
        assert qr.grammar_issues == []
        assert qr.overall_score == 0.0


class TestWritingQualityChecker:
    @pytest.fixture
    def checker(self, tmp_path):
        return WritingQualityChecker(workspace_path=tmp_path)

    def test_init(self, checker, tmp_path):
        assert checker.workspace_path == tmp_path
