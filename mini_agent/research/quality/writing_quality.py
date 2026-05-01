"""Writing quality checker for academic text.

Provides grammar, style, and readability analysis using ``language_tool_python``
and ``textstat`` when available, with regex-based fallbacks.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class GrammarIssue(BaseModel):
    """A single grammar issue."""

    rule: str = ""
    message: str = ""
    suggestion: str = ""
    offset: int = 0
    length: int = 0
    severity: str = "warning"  # error | warning | info


class StyleIssue(BaseModel):
    """A single style issue."""

    rule: str = ""
    message: str = ""
    suggestion: str = ""
    position: int = 0
    severity: str = "warning"


class ReadabilityReport(BaseModel):
    """Readability scores and statistics."""

    flesch_kincaid_grade: float = 0.0
    gunning_fog: float = 0.0
    coleman_liau: float = 0.0
    smog: float = 0.0
    ari: float = 0.0
    flesch_reading_ease: float = 0.0
    word_count: int = 0
    sentence_count: int = 0
    avg_words_per_sentence: float = 0.0
    avg_syllables_per_word: float = 0.0


class QualityReport(BaseModel):
    """Combined quality report."""

    grammar_issues: list[GrammarIssue] = Field(default_factory=list)
    style_issues: list[StyleIssue] = Field(default_factory=list)
    readability: ReadabilityReport = Field(default_factory=ReadabilityReport)
    overall_score: float = 0.0  # 0-100
    summary: str = ""


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------


class WritingQualityChecker:
    """Check grammar, style, and readability of academic text.

    Parameters
    ----------
    workspace_path:
        Root directory of the research workspace (used for resolving
        relative file paths).
    """

    def __init__(self, workspace_path: str | Path) -> None:
        self.workspace_path = Path(workspace_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_grammar(self, text: str, language: str = "en-US") -> list[GrammarIssue]:
        """Check grammar using language_tool_python or regex fallback.

        Parameters
        ----------
        text:
            Text to check.
        language:
            Language code (default ``"en-US"``).

        Returns
        -------
        list[GrammarIssue]
        """
        issues = self._check_language_tool(text, language)
        if issues is not None:
            return issues
        return self._check_grammar_regex(text)

    def check_style(self, text: str) -> list[StyleIssue]:
        """Check academic writing style.

        Detects jargon, clichés, hedging, redundancy, contractions, and
        excessive first-person usage.
        """
        issues: list[StyleIssue] = []

        # Jargon / buzzwords
        jargon_map: dict[str, str] = {
            "leverage": "use",
            "utilize": "use",
            "novel": "new (specify what is new)",
            "robust": "strong/reliable (be specific)",
            "cutting-edge": "recent/advanced",
            "state-of-the-art": "current/latest",
            "paradigm shift": "change/transformation",
            "synergy": "collaboration/combined effect",
            "holistic": "comprehensive",
            "groundbreaking": "significant (provide evidence)",
        }
        for word, suggestion in jargon_map.items():
            for m in re.finditer(rf"\b{re.escape(word)}\b", text, re.IGNORECASE):
                issues.append(
                    StyleIssue(
                        rule="jargon",
                        message=f"Jargon/buzzword: '{m.group()}'",
                        suggestion=f"Consider: '{suggestion}'",
                        position=m.start(),
                    )
                )

        # Hedging
        hedging_words = [
            "somewhat",
            "arguably",
            "perhaps",
            "might",
            "possibly",
            "tends to",
            "appears to",
            "seems to",
        ]
        for hedge in hedging_words:
            for m in re.finditer(rf"\b{re.escape(hedge)}\b", text, re.IGNORECASE):
                issues.append(
                    StyleIssue(
                        rule="hedging",
                        message=f"Hedging language: '{m.group()}'",
                        suggestion="Be more assertive where evidence supports the claim.",
                        position=m.start(),
                    )
                )

        # Contractions
        contractions = re.findall(r"\b\w+'\w+\b", text)
        if contractions:
            issues.append(
                StyleIssue(
                    rule="contractions",
                    message=f"Contractions found ({len(contractions)}): {', '.join(contractions[:5])}",
                    suggestion="Expand contractions in academic writing (e.g., don't → do not).",
                    position=0,
                )
            )

        # Redundancy
        redundancies = [
            ("completely eliminate", "eliminate"),
            ("end result", "result"),
            ("future plans", "plans"),
            ("past history", "history"),
            ("each and every", "each"),
            ("new innovation", "innovation"),
        ]
        for phrase, replacement in redundancies:
            for m in re.finditer(re.escape(phrase), text, re.IGNORECASE):
                issues.append(
                    StyleIssue(
                        rule="redundancy",
                        message=f"Redundant phrase: '{phrase}'",
                        suggestion=f"Use '{replacement}' instead.",
                        position=m.start(),
                    )
                )

        # First person
        first_person = re.findall(r"\b(I|we|my|our|me|us)\b", text, re.IGNORECASE)
        if len(first_person) > 5:
            issues.append(
                StyleIssue(
                    rule="first_person",
                    message=f"Frequent first-person usage ({len(first_person)} instances).",
                    suggestion="Consider third person or passive voice for objectivity.",
                    position=0,
                    severity="info",
                )
            )

        return issues

    def check_readability(self, text: str) -> ReadabilityReport:
        """Compute readability scores.

        Uses ``textstat`` if available, otherwise falls back to manual
        computation.
        """
        clean = self._strip_markup(text)
        if len(clean.split()) < 10:
            return ReadabilityReport(word_count=len(clean.split()))

        report = self._readability_textstat(clean)
        if report is not None:
            return report
        return self._readability_manual(clean)

    def check_all(self, text: str) -> QualityReport:
        """Run all checks and return a combined report."""
        grammar = self.check_grammar(text)
        style = self.check_style(text)
        readability = self.check_readability(text)

        # Compute overall score (100 = perfect)
        grammar_penalty = min(len(grammar) * 2, 30)
        style_penalty = min(len(style) * 1.5, 20)

        # Readability penalty: distance from ideal range (12-16)
        fk = readability.flesch_kincaid_grade
        if 12 <= fk <= 16:
            readability_penalty = 0.0
        else:
            readability_penalty = min(abs(fk - 14) * 2, 20)

        score = max(100 - grammar_penalty - style_penalty - readability_penalty, 0)

        # Summary
        parts: list[str] = []
        if grammar:
            parts.append(f"{len(grammar)} grammar issue(s)")
        if style:
            parts.append(f"{len(style)} style issue(s)")
        parts.append(f"readability grade {fk:.1f}")

        return QualityReport(
            grammar_issues=grammar,
            style_issues=style,
            readability=readability,
            overall_score=round(score, 1),
            summary=f"Score: {score:.0f}/100. " + "; ".join(parts) + ".",
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_markup(text: str) -> str:
        """Remove LaTeX/Markdown markup."""
        text = re.sub(r"(?m)^%.*$", "", text)
        text = re.sub(r"\\[a-zA-Z]+\*?(\{[^}]*\})?", "", text)
        text = re.sub(r"[{}$%\\#]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _check_language_tool(text: str, language: str) -> list[GrammarIssue] | None:
        """Try language_tool_python."""
        try:
            import language_tool_python  # type: ignore[import-untyped]

            tool = language_tool_python.LanguageTool(language)
            matches = tool.check(text)
            issues: list[GrammarIssue] = []
            for m in matches:
                issues.append(
                    GrammarIssue(
                        rule=m.ruleId,
                        message=m.message,
                        suggestion=m.replacements[0] if m.replacements else "",
                        offset=m.offset,
                        length=m.errorLength,
                        severity="error" if m.ruleIssueType == "grammar" else "warning",
                    )
                )
            tool.close()
            return issues
        except ImportError:
            return None
        except Exception:
            return None

    @staticmethod
    def _check_grammar_regex(text: str) -> list[GrammarIssue]:
        """Regex-based grammar checks (fallback)."""
        issues: list[GrammarIssue] = []
        patterns: list[tuple[str, str, str]] = [
            (r"\s{2,}", "Multiple consecutive spaces", "whitespace"),
            (r"\.\s*\.", "Double period", "punctuation"),
            (r",\s*,", "Double comma", "punctuation"),
            (r"\b(very|really|basically|actually|literally)\b", "Weak/filler word", "style"),
            (r"\b(alot)\b", "Misspelling: 'alot' → 'a lot'", "spelling"),
        ]
        for pattern, message, rule in patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                issues.append(
                    GrammarIssue(
                        rule=rule,
                        message=message,
                        offset=m.start(),
                        length=m.end() - m.start(),
                        severity="warning",
                    )
                )
        return issues

    @staticmethod
    def _readability_textstat(text: str) -> ReadabilityReport | None:
        """Compute readability with textstat."""
        try:
            import textstat  # type: ignore[import-untyped]

            wc = textstat.lexicon_count(text)
            sc = textstat.sentence_count(text)
            return ReadabilityReport(
                flesch_kincaid_grade=textstat.flesch_kincaid_grade(text),
                gunning_fog=textstat.gunning_fog(text),
                coleman_liau=textstat.coleman_liau_index(text),
                smog=textstat.smog_index(text),
                ari=textstat.automated_readability_index(text),
                flesch_reading_ease=textstat.flesch_reading_ease(text),
                word_count=wc,
                sentence_count=sc,
                avg_words_per_sentence=wc / max(sc, 1),
                avg_syllables_per_word=textstat.avg_syllables_per_word(text),
            )
        except ImportError:
            return None

    @staticmethod
    def _readability_manual(text: str) -> ReadabilityReport:
        """Manual readability computation."""
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        words = text.split()
        wc = len(words)
        sc = max(len(sentences), 1)
        avg_wps = wc / sc

        def syllables(word: str) -> int:
            w = word.lower().strip(".,!?;:'\"")
            if len(w) <= 3:
                return 1
            count = len(re.findall(r"[aeiouy]+", w))
            if w.endswith("e") and not w.endswith("le"):
                count -= 1
            return max(count, 1)

        total_syl = sum(syllables(w) for w in words)
        avg_syl = total_syl / max(wc, 1)
        complex_words = sum(1 for w in words if syllables(w) >= 3)
        total_chars = sum(len(w) for w in words)

        fk = 0.39 * avg_wps + 11.8 * avg_syl - 15.59
        fre = 206.835 - 1.015 * avg_wps - 84.6 * avg_syl
        fog = 0.4 * (avg_wps + 100 * (complex_words / max(wc, 1)))
        avg_c100 = (total_chars / max(wc, 1)) * 100
        avg_s100 = (sc / max(wc, 1)) * 100
        cli = 0.0588 * avg_c100 - 0.296 * avg_s100 - 15.8
        smog = 1.0430 * math.sqrt(complex_words * (30 / max(sc, 1))) + 3.1291
        ari = 4.71 * (total_chars / max(wc, 1)) + 0.5 * avg_wps - 21.43

        return ReadabilityReport(
            flesch_kincaid_grade=round(fk, 2),
            gunning_fog=round(fog, 2),
            coleman_liau=round(cli, 2),
            smog=round(smog, 2),
            ari=round(ari, 2),
            flesch_reading_ease=round(fre, 2),
            word_count=wc,
            sentence_count=sc,
            avg_words_per_sentence=round(avg_wps, 2),
            avg_syllables_per_word=round(avg_syl, 2),
        )
