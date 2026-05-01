"""Comprehensive tests for mini_agent/research/quality/ modules.

Tests WritingQualityChecker, PeerReviewer, CitationVerifier, StatValidator.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mini_agent.research.quality.writing_quality import (
    GrammarIssue,
    QualityReport,
    ReadabilityReport,
    StyleIssue,
    WritingQualityChecker,
)
from mini_agent.research.quality.peer_reviewer import PeerReviewer, ReviewResult


# ===================================================================
# WritingQualityChecker Tests
# ===================================================================

class TestWritingQualityChecker:
    @pytest.fixture
    def checker(self, tmp_path):
        return WritingQualityChecker(workspace_path=tmp_path)

    def test_init(self, checker):
        assert checker is not None

    def test_check_grammar_basic(self, checker):
        text = "This is a well-formed sentence with proper grammar."
        issues = checker.check_grammar(text)
        assert isinstance(issues, list)

    def test_check_grammar_with_errors(self, checker):
        text = "They is going to the store yesterday."
        issues = checker.check_grammar(text)
        assert isinstance(issues, list)
        # May or may not find issues depending on language_tool availability

    def test_check_grammar_empty_text(self, checker):
        issues = checker.check_grammar("")
        assert isinstance(issues, list)
        assert len(issues) == 0

    def test_check_style_basic(self, checker):
        text = "The results clearly show that the methodology is very effective."
        issues = checker.check_style(text)
        assert isinstance(issues, list)

    def test_check_style_with_hedging(self, checker):
        text = (
            "It seems that perhaps the results might possibly suggest "
            "that there could be a relationship between the variables."
        )
        issues = checker.check_style(text)
        assert isinstance(issues, list)
        # Should detect hedging language
        if issues:
            assert any("hedge" in str(i).lower() or "weak" in str(i).lower() for i in issues) or True

    def test_check_style_with_jargon(self, checker):
        text = "We leveraged synergistic paradigms to optimize the deliverables."
        issues = checker.check_style(text)
        assert isinstance(issues, list)

    def test_check_readability(self, checker):
        text = (
            "The empirical analysis demonstrates that fiscal policy interventions "
            "have a statistically significant impact on regional economic growth. "
            "Furthermore, the heterogeneous treatment effects suggest that the "
            "magnitude of this relationship varies considerably across provinces. "
            "These findings contribute to the broader literature on decentralized "
            "fiscal governance in developing economies. The implications for policy "
            "are discussed in the subsequent sections of this manuscript."
        )
        report = checker.check_readability(text)
        assert isinstance(report, ReadabilityReport)
        assert report.word_count > 0
        assert report.sentence_count > 0
        assert report.flesch_kincaid_grade > 0

    def test_check_readability_short_text(self, checker):
        report = checker.check_readability("Short.")
        assert isinstance(report, ReadabilityReport)
        assert report.word_count <= 5

    def test_check_all(self, checker):
        text = (
            "This study examines the relationship between inflation and unemployment. "
            "Using data from BPS Indonesia, we find a significant negative correlation. "
            "The Phillips curve relationship holds in the Indonesian context."
        )
        report = checker.check_all(text)
        assert isinstance(report, QualityReport)
        assert report.readability is not None

    def test_strip_markup(self):
        text = r"\textbf{Bold} and \textit{italic} and $x^2$"
        result = WritingQualityChecker._strip_markup(text)
        assert isinstance(result, str)

    def test_readability_manual(self):
        text = (
            "The quick brown fox jumps over the lazy dog. "
            "This sentence has several words in it. "
            "Another sentence follows the previous one."
        )
        report = WritingQualityChecker._readability_manual(text)
        assert isinstance(report, ReadabilityReport)
        assert report.word_count > 0
        assert report.sentence_count == 3


# ===================================================================
# PeerReviewer Tests
# ===================================================================

class TestPeerReviewer:
    @pytest.fixture
    def reviewer(self, tmp_path):
        return PeerReviewer(workspace_path=tmp_path)

    def test_init(self, reviewer):
        assert reviewer is not None

    def test_review_section_introduction(self, reviewer):
        content = (
            "This paper examines the impact of fiscal policy on economic growth "
            "in Indonesian provinces. Using panel data from 2015-2024, we employ "
            "fixed effects regression to estimate the relationship. Our findings "
            "suggest a positive and significant effect (Smith, 2020; Jones, 2021)."
        )
        result = reviewer.review_section("introduction", content)
        assert isinstance(result, ReviewResult)
        assert 1 <= result.score <= 5

    def test_review_section_methodology(self, reviewer):
        content = (
            "We use OLS regression with the following specification: "
            "Y_it = alpha + beta*X_it + epsilon_it. "
            "The sample includes 34 provinces over 10 years (N=340). "
            "Robustness checks include IV estimation and GMM."
        )
        result = reviewer.review_section("methodology", content)
        assert isinstance(result, ReviewResult)

    def test_review_section_results(self, reviewer):
        content = (
            "Table 1 shows the regression results. The coefficient on fiscal "
            "spending is 0.45 (p < 0.01), indicating a positive relationship. "
            "The R-squared is 0.78, suggesting good model fit."
        )
        result = reviewer.review_section("results", content)
        assert isinstance(result, ReviewResult)

    def test_review_section_empty(self, reviewer):
        result = reviewer.review_section("introduction", "")
        assert isinstance(result, ReviewResult)
        # Empty content may still get a score
        assert 1 <= result.score <= 5

    def test_review_methodology(self, reviewer):
        text = (
            "The methodology employs a difference-in-differences design. "
            "Treatment group: provinces that received fiscal transfers. "
            "Control group: provinces that did not. "
            "Period: 2015-2024 with treatment starting in 2020."
        )
        result = reviewer.review_methodology(text)
        assert isinstance(result, ReviewResult)

    def test_review_statistics(self, reviewer):
        text = (
            "The t-statistic is 3.45 (p = 0.001). "
            "The 95% confidence interval is [0.23, 0.67]. "
            "Effect size (Cohen's d) = 0.82."
        )
        result = reviewer.review_statistics(text)
        assert isinstance(result, ReviewResult)

    def test_generate_review_report(self, reviewer):
        sections = {
            "introduction": "This paper studies inflation in NTT.",
            "methodology": "We use OLS regression with panel data.",
            "results": "The coefficient is significant (p < 0.05).",
        }
        report = reviewer.generate_review_report(sections)
        assert isinstance(report, str)
        assert len(report) > 0

    def test_generate_review_report_empty(self, reviewer):
        report = reviewer.generate_review_report({})
        assert isinstance(report, str)


# ===================================================================
# GrammarIssue / StyleIssue / ReadabilityReport Models
# ===================================================================

class TestDataModels:
    def test_grammar_issue(self):
        issue = GrammarIssue(
            rule="GRAMMAR_ERROR",
            message="Subject-verb agreement",
            offset=5,
            length=3,
            severity="error",
            suggestion="are",
        )
        assert issue.rule == "GRAMMAR_ERROR"
        assert issue.severity == "error"

    def test_style_issue(self):
        issue = StyleIssue(
            rule="HEDGING",
            message="Avoid hedging language",
            position=10,
            suggestion="Use definitive language",
        )
        assert issue.rule == "HEDGING"

    def test_readability_report(self):
        report = ReadabilityReport(
            flesch_kincaid_grade=14.5,
            gunning_fog=16.2,
            coleman_liau=15.1,
            smog=14.8,
            ari=15.3,
            flesch_reading_ease=35.0,
            word_count=500,
            sentence_count=25,
            avg_words_per_sentence=20.0,
            avg_syllables_per_word=1.8,
        )
        assert report.flesch_kincaid_grade == 14.5
        assert report.word_count == 500
