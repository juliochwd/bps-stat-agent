"""Simulated peer reviewer for academic papers.

Provides rule-based adversarial review of paper sections, checking citation
density, statistical reporting, methodology completeness, logical flow, and
unsupported claims.
"""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, Field


class ReviewResult(BaseModel):
    """Result of a peer review for a single section or aspect."""

    score: int = 3  # 1-5 scale
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    major_issues: list[str] = Field(default_factory=list)
    minor_issues: list[str] = Field(default_factory=list)


class PeerReviewer:
    """Simulate adversarial peer review of academic paper sections.

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

    def review_section(self, section_name: str, content: str) -> ReviewResult:
        """Review a named section.

        Dispatches to specialized review logic based on *section_name*.
        """
        if section_name == "methodology":
            return self.review_methodology(content)
        if section_name == "results":
            return self.review_statistics(content)
        return self._review_generic(section_name, content)

    def review_methodology(self, methodology_text: str) -> ReviewResult:
        """Review methodology section for completeness and rigour."""
        result = ReviewResult()
        text = methodology_text

        # Check for key methodology elements
        elements: dict[str, re.Pattern[str]] = {
            "study_design": re.compile(
                r"cross.?sectional|longitudinal|experimental|quasi.?experimental|"
                r"survey|case\s+study|mixed.?method|qualitative|quantitative",
                re.IGNORECASE,
            ),
            "sample_description": re.compile(
                r"sample\s+(?:size|of)|participants|respondents|n\s*=\s*\d+|subjects",
                re.IGNORECASE,
            ),
            "data_collection": re.compile(
                r"collected|gathered|obtained|questionnaire|interview|survey|secondary\s+data",
                re.IGNORECASE,
            ),
            "analysis_method": re.compile(
                r"regression|ANOVA|t-test|correlation|factor\s+analysis|SEM|OLS|logistic",
                re.IGNORECASE,
            ),
            "variables": re.compile(
                r"dependent\s+variable|independent\s+variable|control\s+variable|predictor|covariate",
                re.IGNORECASE,
            ),
        }

        present: list[str] = []
        missing: list[str] = []
        for element, pattern in elements.items():
            if pattern.search(text):
                present.append(element.replace("_", " "))
            else:
                missing.append(element.replace("_", " "))

        if present:
            result.strengths.append(f"Methodology addresses: {', '.join(present)}.")
        if missing:
            result.major_issues.append(f"Missing methodology elements: {', '.join(missing)}.")
            result.suggestions.append("Ensure the methodology is replicable by another researcher.")

        # Check for ethical considerations
        if not re.search(r"ethic|IRB|consent|approval", text, re.IGNORECASE):
            result.minor_issues.append("No mention of ethical approval or informed consent.")

        # Check for limitations acknowledgment
        if not re.search(r"limitation|constraint|caveat", text, re.IGNORECASE):
            result.minor_issues.append("Consider acknowledging methodological limitations.")

        # Score
        if len(result.major_issues) == 0:
            result.score = 4 if len(result.minor_issues) <= 1 else 3
        elif len(result.major_issues) == 1:
            result.score = 3
        else:
            result.score = 2

        if not missing:
            result.score = min(result.score + 1, 5)

        return result

    def review_statistics(self, results_text: str) -> ReviewResult:
        """Review statistical reporting in results section."""
        result = ReviewResult()
        text = results_text

        # Check for complete statistical reporting
        has_p = bool(re.search(r"p\s*[<>=]\s*\.?\d+", text, re.IGNORECASE))
        has_test_stat = bool(re.search(r"[tFzχ²]\s*[\(=]|chi-square|t-test|F-test", text, re.IGNORECASE))
        has_df = bool(re.search(r"df\s*=\s*\d+|\(\d+(?:,\s*\d+)?\)", text, re.IGNORECASE))
        has_effect = bool(re.search(r"[dηω]²?\s*=|Cohen|eta.?squared|R²\s*=", text, re.IGNORECASE))
        has_ci = bool(re.search(r"CI|confidence\s+interval|\[.*,.*\]", text, re.IGNORECASE))

        if has_test_stat:
            result.strengths.append("Test statistics reported.")
        if has_effect:
            result.strengths.append("Effect sizes reported.")
        if has_ci:
            result.strengths.append("Confidence intervals reported.")

        if has_p and not has_test_stat:
            result.major_issues.append("p-values reported without test statistics. Report full test results.")
        if has_p and not has_effect:
            result.major_issues.append("No effect sizes reported. APA 7th edition requires effect sizes.")
        if has_p and not has_df:
            result.minor_issues.append("Degrees of freedom not consistently reported.")
        if has_test_stat and not has_ci:
            result.suggestions.append("Consider adding 95% confidence intervals.")

        # Check for descriptive statistics
        if not re.search(r"mean|median|M\s*=|SD\s*=|standard\s+deviation", text, re.IGNORECASE):
            result.minor_issues.append("No descriptive statistics (M, SD) found.")

        # Score
        issues_count = len(result.major_issues) + len(result.minor_issues) * 0.5
        if issues_count == 0:
            result.score = 5
        elif issues_count <= 1:
            result.score = 4
        elif issues_count <= 3:
            result.score = 3
        elif issues_count <= 5:
            result.score = 2
        else:
            result.score = 1

        return result

    def generate_review_report(self, paper_sections: dict[str, str]) -> str:
        """Generate a full review report for all paper sections.

        Parameters
        ----------
        paper_sections:
            Mapping of section name to content.

        Returns
        -------
        str
            Formatted review report in Markdown.
        """
        lines: list[str] = ["# Peer Review Report", ""]
        overall_scores: list[int] = []

        for section_name, content in paper_sections.items():
            if not content.strip():
                continue
            review = self.review_section(section_name, content)
            overall_scores.append(review.score)

            title = section_name.replace("_", " ").title()
            lines.append(f"## {title} — Score: {review.score}/5")
            lines.append("")

            if review.strengths:
                lines.append("**Strengths:**")
                for s in review.strengths:
                    lines.append(f"- {s}")
                lines.append("")

            if review.major_issues:
                lines.append("**Major Issues:**")
                for issue in review.major_issues:
                    lines.append(f"- {issue}")
                lines.append("")

            if review.minor_issues:
                lines.append("**Minor Issues:**")
                for issue in review.minor_issues:
                    lines.append(f"- {issue}")
                lines.append("")

            if review.suggestions:
                lines.append("**Suggestions:**")
                for s in review.suggestions:
                    lines.append(f"- {s}")
                lines.append("")

            lines.append("---")
            lines.append("")

        # Overall verdict
        if overall_scores:
            avg = sum(overall_scores) / len(overall_scores)
            if avg >= 4.0:
                verdict = "Accept (Minor Revisions)"
            elif avg >= 3.0:
                verdict = "Major Revisions"
            elif avg >= 2.0:
                verdict = "Revise and Resubmit"
            else:
                verdict = "Reject"

            lines.insert(1, "")
            lines.insert(
                2,
                f"**Overall Verdict: {verdict}** (Average score: {avg:.1f}/5, {len(overall_scores)} sections reviewed)",
            )
            lines.insert(3, "")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _review_generic(self, section_name: str, content: str) -> ReviewResult:
        """Generic review for sections without specialized logic."""
        result = ReviewResult()
        word_count = len(content.split())

        # Citation density
        citations = re.findall(
            r"\\cite\{[^}]+\}|\([A-Z][a-z]+.*?\d{4}\)|\[\d+\]",
            content,
        )
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", content) if len(p.strip()) > 50]
        para_count = max(len(paragraphs), 1)

        cite_density = len(citations) / para_count
        if cite_density >= 2:
            result.strengths.append(f"Good citation density ({len(citations)} citations).")
        elif cite_density >= 1:
            result.minor_issues.append("Citation density could be improved.")
        else:
            result.major_issues.append(f"Low citation density ({len(citations)} citations in {para_count} paragraphs).")

        # Word count assessment
        min_words: dict[str, int] = {
            "abstract": 150,
            "introduction": 500,
            "literature_review": 1000,
            "methodology": 800,
            "results": 600,
            "discussion": 800,
            "conclusion": 200,
        }
        expected = min_words.get(section_name, 300)
        if word_count >= expected:
            result.strengths.append(f"Adequate length ({word_count} words).")
        else:
            result.weaknesses.append(f"Section may be underdeveloped ({word_count} words, expected ≥{expected}).")

        # Transition words
        transitions = re.findall(
            r"\b(?:however|therefore|moreover|furthermore|consequently|"
            r"nevertheless|additionally|specifically|thus|hence)\b",
            content,
            re.IGNORECASE,
        )
        if len(transitions) >= para_count:
            result.strengths.append("Good use of transition words.")
        elif para_count > 3 and len(transitions) < para_count * 0.5:
            result.minor_issues.append("Improve logical flow with more transition words.")

        # Unsupported claims
        claim_pattern = re.compile(
            r"(?:shows?\s+that|demonstrates?\s+that|proves?\s+that|"
            r"significantly\s+(?:higher|lower|more|less|different))",
            re.IGNORECASE,
        )
        citation_nearby = re.compile(
            r"\\cite\{[^}]+\}|\([A-Z][a-z]+.*?\d{4}\)|\[\d+\]|"
            r"Table\s+\d+|Figure\s+\d+|p\s*[<>=]",
        )
        sentences = [s.strip() for s in re.split(r"[.!?]+", content) if s.strip()]
        unsupported = 0
        for sent in sentences:
            if claim_pattern.search(sent) and not citation_nearby.search(sent):
                unsupported += 1
        if unsupported > 0:
            result.major_issues.append(f"{unsupported} claim(s) without supporting evidence or citations.")

        # Score
        total_issues = len(result.major_issues) + len(result.minor_issues) * 0.5
        if total_issues == 0:
            result.score = 5
        elif total_issues <= 1:
            result.score = 4
        elif total_issues <= 3:
            result.score = 3
        elif total_issues <= 5:
            result.score = 2
        else:
            result.score = 1

        return result
