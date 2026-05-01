"""Quality assurance tools for the BPS Academic Research Agent.

Provides tools for:
- check_grammar: Grammar checking via LanguageTool or regex fallback
- check_style: Academic prose linting
- check_readability: Readability scoring via textstat or manual computation
- simulate_peer_review: Simulate adversarial peer review of paper sections
- detect_plagiarism: Detect potential plagiarism using text similarity
- audit_reproducibility: Audit computation reproducibility
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .base import Tool, ToolResult

# ---------------------------------------------------------------------------
# 1. CheckGrammarTool
# ---------------------------------------------------------------------------


class CheckGrammarTool(Tool):
    """Check grammar using LanguageTool or regex fallback."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "check_grammar"

    @property
    def description(self) -> str:
        return (
            "Check grammar and style using LanguageTool. In academic mode, "
            "applies stricter rules for passive voice, hedging, and formal "
            "tone. Returns issues with position, message, and suggestion."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to check for grammar issues",
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file to check (alternative to text)",
                },
                "language": {
                    "type": "string",
                    "description": "Language code (default: en-US)",
                    "default": "en-US",
                },
            },
            "required": [],
        }

    async def execute(
        self,
        text: str | None = None,
        file_path: str | None = None,
        language: str = "en-US",
        **kwargs: Any,
    ) -> ToolResult:
        """Check grammar."""
        try:
            from mini_agent.research.quality.writing_quality import WritingQualityChecker

            content = self._get_text(text, file_path)
            if content is None:
                return ToolResult(
                    success=False,
                    error="No text provided. Supply either text or file_path.",
                )

            checker = WritingQualityChecker(self._workspace_dir)
            issues = checker.check_grammar(content, language)

            if not issues:
                return ToolResult(success=True, content="✅ No grammar issues found.")

            lines = [f"## Grammar Check: {len(issues)} issue(s)\n"]
            for i, issue in enumerate(issues[:30], 1):
                severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue.severity, "⚠️")
                lines.append(f"{i}. {severity_icon} **{issue.rule}** (pos {issue.offset}): {issue.message}")
                if issue.suggestion:
                    lines.append(f"   → Suggestion: {issue.suggestion}")

            if len(issues) > 30:
                lines.append(f"\n... and {len(issues) - 30} more issues.")

            return ToolResult(success=True, content="\n".join(lines))
        except Exception as e:
            return ToolResult(success=False, error=f"Grammar check failed: {e}")

    def _get_text(self, text: str | None, file_path: str | None) -> str | None:
        """Get text from parameter or file."""
        if text:
            return text
        if file_path:
            ws = Path(self._workspace_dir)
            fp = ws / file_path if not Path(file_path).is_absolute() else Path(file_path)
            if fp.exists():
                return fp.read_text(encoding="utf-8")
        return None


# ---------------------------------------------------------------------------
# 2. CheckStyleTool
# ---------------------------------------------------------------------------


class CheckStyleTool(Tool):
    """Check academic writing style for jargon, hedging, etc."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "check_style"

    @property
    def description(self) -> str:
        return (
            "Check academic writing style. Detects jargon, clichés, "
            "redundancy, hedging, contractions, and first-person usage."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to check for style issues",
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file to check (alternative to text)",
                },
            },
            "required": [],
        }

    async def execute(
        self,
        text: str | None = None,
        file_path: str | None = None,
        **kwargs: Any,
    ) -> ToolResult:
        """Check writing style."""
        try:
            from mini_agent.research.quality.writing_quality import WritingQualityChecker

            content = self._get_text(text, file_path)
            if content is None:
                return ToolResult(
                    success=False,
                    error="No text provided. Supply either text or file_path.",
                )

            checker = WritingQualityChecker(self._workspace_dir)
            issues = checker.check_style(content)

            if not issues:
                return ToolResult(
                    success=True,
                    content="✅ No style issues found. Writing quality is good.",
                )

            lines = [f"## Style Check: {len(issues)} issue(s)\n"]
            for i, issue in enumerate(issues[:25], 1):
                lines.append(f"{i}. **{issue.rule}** (pos {issue.position}): {issue.message}")
                if issue.suggestion:
                    lines.append(f"   → Suggestion: {issue.suggestion}")

            if len(issues) > 25:
                lines.append(f"\n... and {len(issues) - 25} more issues.")

            return ToolResult(success=True, content="\n".join(lines))
        except Exception as e:
            return ToolResult(success=False, error=f"Style check failed: {e}")

    def _get_text(self, text: str | None, file_path: str | None) -> str | None:
        """Get text from parameter or file."""
        if text:
            return text
        if file_path:
            ws = Path(self._workspace_dir)
            fp = ws / file_path if not Path(file_path).is_absolute() else Path(file_path)
            if fp.exists():
                return fp.read_text(encoding="utf-8")
        return None


# ---------------------------------------------------------------------------
# 3. CheckReadabilityTool
# ---------------------------------------------------------------------------


class CheckReadabilityTool(Tool):
    """Compute readability statistics."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "check_readability"

    @property
    def description(self) -> str:
        return (
            "Compute readability statistics: Flesch-Kincaid Grade, Gunning Fog, "
            "Coleman-Liau, SMOG, and ARI. Academic target: Grade 12-16."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to analyze for readability",
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file to analyze (alternative to text)",
                },
            },
            "required": [],
        }

    async def execute(
        self,
        text: str | None = None,
        file_path: str | None = None,
        **kwargs: Any,
    ) -> ToolResult:
        """Compute readability scores."""
        try:
            from mini_agent.research.quality.writing_quality import WritingQualityChecker

            content = self._get_text(text, file_path)
            if content is None:
                return ToolResult(
                    success=False,
                    error="No text provided. Supply either text or file_path.",
                )

            checker = WritingQualityChecker(self._workspace_dir)
            report = checker.check_readability(content)

            if report.word_count < 10:
                return ToolResult(
                    success=False,
                    error="Text too short for reliable readability analysis.",
                )

            # Assessment
            fk = report.flesch_kincaid_grade
            if 12 <= fk <= 16:
                assessment = f"✅ Appropriate for academic audience (Grade {fk:.1f})"
            elif fk < 12:
                assessment = f"⚠️ May be too simple for academic audience (Grade {fk:.1f}, target: 12-16)"
            else:
                assessment = f"⚠️ May be too complex (Grade {fk:.1f}, target: 12-16)"

            lines = [
                "## Readability Analysis\n",
                "### Scores:",
                f"- **Flesch-Kincaid Grade Level:** {report.flesch_kincaid_grade:.1f}",
                f"- **Gunning Fog Index:** {report.gunning_fog:.1f}",
                f"- **Coleman-Liau Index:** {report.coleman_liau:.1f}",
                f"- **SMOG Index:** {report.smog:.1f}",
                f"- **Automated Readability Index:** {report.ari:.1f}",
                f"- **Flesch Reading Ease:** {report.flesch_reading_ease:.1f}",
                "\n### Text Statistics:",
                f"- **Word count:** {report.word_count}",
                f"- **Sentence count:** {report.sentence_count}",
                f"- **Avg words/sentence:** {report.avg_words_per_sentence:.1f}",
                f"- **Avg syllables/word:** {report.avg_syllables_per_word:.2f}",
                f"\n### Assessment:\n{assessment}",
            ]

            return ToolResult(success=True, content="\n".join(lines))
        except Exception as e:
            return ToolResult(success=False, error=f"Readability check failed: {e}")

    def _get_text(self, text: str | None, file_path: str | None) -> str | None:
        """Get text from parameter or file."""
        if text:
            return text
        if file_path:
            ws = Path(self._workspace_dir)
            fp = ws / file_path if not Path(file_path).is_absolute() else Path(file_path)
            if fp.exists():
                return fp.read_text(encoding="utf-8")
        return None


# ---------------------------------------------------------------------------
# 4. SimulatePeerReviewTool
# ---------------------------------------------------------------------------


class SimulatePeerReviewTool(Tool):
    """Simulate adversarial peer review of paper sections."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "simulate_peer_review"

    @property
    def description(self) -> str:
        return (
            "Simulate adversarial peer review. Reviews citation density, "
            "statistical reporting, methodology, unsupported claims, and "
            "logical flow. Returns structured review with verdict."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "section": {
                    "type": "string",
                    "description": "Section name to review (reviews all if omitted)",
                },
                "text": {
                    "type": "string",
                    "description": "Direct text to review (alternative to reading from file)",
                },
            },
            "required": [],
        }

    async def execute(
        self,
        section: str | None = None,
        text: str | None = None,
        **kwargs: Any,
    ) -> ToolResult:
        """Execute peer review simulation."""
        try:
            from mini_agent.research.quality.peer_reviewer import PeerReviewer
            from mini_agent.research.writing.section_writer import SectionWriter

            ws = Path(self._workspace_dir)
            reviewer = PeerReviewer(ws)
            writer = SectionWriter(ws)

            if text and not section:
                # Review provided text directly
                section = "provided_text"
            if section:
                # Review single section
                if text:
                    content = text
                else:
                    content = writer.get_section(section)
                    if content is None:
                        return ToolResult(
                            success=False,
                            error=f"Section '{section}' not found.",
                        )
                result = reviewer.review_section(section, content)
                lines = [
                    f"## Peer Review: {section.replace('_', ' ').title()}\n",
                    f"**Score:** {result.score}/5\n",
                ]
                if result.strengths:
                    lines.append("**Strengths:**")
                    for s in result.strengths:
                        lines.append(f"  - {s}")
                if result.major_issues:
                    lines.append("\n**Major Issues:**")
                    for issue in result.major_issues:
                        lines.append(f"  - {issue}")
                if result.minor_issues:
                    lines.append("\n**Minor Issues:**")
                    for issue in result.minor_issues:
                        lines.append(f"  - {issue}")
                if result.suggestions:
                    lines.append("\n**Suggestions:**")
                    for s in result.suggestions:
                        lines.append(f"  - {s}")

                # Add recommendation
                verdict = "Accept" if result.score >= 4 else "Revise" if result.score >= 3 else "Major Revision"
                lines.append(f"\n**Recommendation:** {verdict}")

                return ToolResult(success=True, content="\n".join(lines))
            else:
                # Review all sections
                all_sections = writer.get_all_sections()
                if not all_sections:
                    return ToolResult(
                        success=False,
                        error="No sections found. Write sections first.",
                    )

                report = reviewer.generate_review_report(all_sections)
                return ToolResult(success=True, content=report)

        except Exception as e:
            return ToolResult(success=False, error=f"Peer review failed: {e}")


# ---------------------------------------------------------------------------
# 5. DetectPlagiarismTool
# ---------------------------------------------------------------------------


class DetectPlagiarismTool(Tool):
    """Detect potential plagiarism using text similarity."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "detect_plagiarism"

    @property
    def description(self) -> str:
        return (
            "Detect potential plagiarism using text similarity. Uses "
            "sentence-transformers for semantic similarity if available, "
            "falls back to n-gram overlap detection."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to check for plagiarism",
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to file to check (alternative to text)",
                },
                "threshold": {
                    "type": "number",
                    "description": "Similarity threshold for flagging (0-1, default: 0.85)",
                    "default": 0.85,
                },
            },
            "required": [],
        }

    async def execute(
        self,
        text: str | None = None,
        file_path: str | None = None,
        threshold: float = 0.85,
        **kwargs: Any,
    ) -> ToolResult:
        """Execute plagiarism detection."""
        try:
            content = self._get_text(text, file_path)
            if content is None:
                return ToolResult(
                    success=False,
                    error="No text provided. Supply either text or file_path.",
                )

            ws = Path(self._workspace_dir)

            # Gather reference texts from literature summaries
            references: list[tuple[str, str]] = []
            lit_dir = ws / "literature" / "summaries"
            if lit_dir.exists():
                for f in lit_dir.glob("*.txt"):
                    references.append((f.name, f.read_text(encoding="utf-8")))
                for f in lit_dir.glob("*.md"):
                    references.append((f.name, f.read_text(encoding="utf-8")))

            # Also check other sections for self-plagiarism
            sections_dir = ws / "paper" / "sections"
            if sections_dir.exists():
                for f in sections_dir.iterdir():
                    if f.is_file() and f.suffix in (".tex", ".md"):
                        sec_content = f.read_text(encoding="utf-8")
                        # Don't compare file against itself
                        if sec_content.strip() != content.strip():
                            references.append((f"section:{f.stem}", sec_content))

            if not references:
                return ToolResult(
                    success=True,
                    content=(
                        "## Plagiarism Check\n\n"
                        "⚠️ No reference texts available for comparison.\n"
                        f"**Source text:** {len(content.split())} words\n\n"
                        "Add reference texts to literature/summaries/ for comparison."
                    ),
                )

            # Try semantic similarity first
            results = self._check_semantic(content, references, threshold)
            if results is None:
                # Fall back to n-gram
                results = self._check_ngram(content, references, threshold)

            # Format output
            overall_sim = results.get("max_similarity", 0.0)
            exceeded = overall_sim > threshold

            lines = [
                "## Plagiarism Detection Report\n",
                f"**Threshold:** {threshold:.0%}",
                f"**Overall Max Similarity:** {overall_sim:.2%}",
                f"**Status:** {'⚠️ EXCEEDS THRESHOLD' if exceeded else '✅ BELOW THRESHOLD'}\n",
            ]

            comparisons = results.get("comparisons", [])
            if comparisons:
                lines.append("### Comparison Results")
                lines.append("| Reference | Similarity |")
                lines.append("|-----------|-----------|")
                for comp in comparisons[:10]:
                    flag = " ⚠️" if comp["similarity"] > threshold else ""
                    lines.append(f"| {comp['reference']} | {comp['similarity']:.2%}{flag} |")

            flagged = results.get("flagged", [])
            if flagged:
                lines.append(f"\n### Flagged Passages ({len(flagged)})")
                for i, f in enumerate(flagged[:5], 1):
                    lines.append(f'  {i}. [{f["similarity"]:.0%}] "{f["passage"][:150]}..."')

            return ToolResult(success=True, content="\n".join(lines))
        except Exception as e:
            return ToolResult(success=False, error=f"Plagiarism detection failed: {e}")

    def _get_text(self, text: str | None, file_path: str | None) -> str | None:
        """Get text from parameter or file."""
        if text:
            return text
        if file_path:
            ws = Path(self._workspace_dir)
            fp = ws / file_path if not Path(file_path).is_absolute() else Path(file_path)
            if fp.exists():
                return fp.read_text(encoding="utf-8")
        return None

    def _check_semantic(
        self,
        source: str,
        references: list[tuple[str, str]],
        threshold: float,
    ) -> dict[str, Any] | None:
        """Try sentence-transformers for semantic similarity."""
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]
            from sentence_transformers import util as st_util

            model = SentenceTransformer("all-MiniLM-L6-v2")

            source_sents = [s.strip() for s in re.split(r"[.!?]+", source) if len(s.strip()) > 20]
            if not source_sents:
                return {"max_similarity": 0.0, "comparisons": [], "flagged": []}

            source_emb = model.encode(source_sents, convert_to_tensor=True)

            comparisons: list[dict[str, Any]] = []
            flagged: list[dict[str, Any]] = []
            max_sim = 0.0

            for ref_name, ref_content in references:
                ref_sents = [s.strip() for s in re.split(r"[.!?]+", ref_content) if len(s.strip()) > 20]
                if not ref_sents:
                    continue

                ref_emb = model.encode(ref_sents, convert_to_tensor=True)
                scores = st_util.cos_sim(source_emb, ref_emb)
                max_scores = scores.max(dim=1).values.cpu().numpy()
                avg_sim = float(max_scores.mean())
                max_sim = max(max_sim, avg_sim)

                comparisons.append({"reference": ref_name, "similarity": round(avg_sim, 4)})

                for i, score in enumerate(max_scores):
                    if float(score) > threshold:
                        flagged.append(
                            {
                                "passage": source_sents[i][:200],
                                "similarity": round(float(score), 4),
                                "reference": ref_name,
                            }
                        )

            return {"max_similarity": max_sim, "comparisons": comparisons, "flagged": flagged}
        except ImportError:
            return None

    def _check_ngram(
        self,
        source: str,
        references: list[tuple[str, str]],
        threshold: float,
    ) -> dict[str, Any]:
        """N-gram overlap detection (fallback)."""

        def get_ngrams(text: str, n: int = 5) -> set[str]:
            text = re.sub(r"\s+", " ", text.lower().strip())
            return {text[i : i + n] for i in range(len(text) - n + 1)}

        def jaccard(a: set[str], b: set[str]) -> float:
            if not a or not b:
                return 0.0
            return len(a & b) / len(a | b)

        source_ngrams = get_ngrams(source)
        comparisons: list[dict[str, Any]] = []
        flagged: list[dict[str, Any]] = []
        max_sim = 0.0

        for ref_name, ref_content in references:
            ref_ngrams = get_ngrams(ref_content)
            sim = jaccard(source_ngrams, ref_ngrams)
            max_sim = max(max_sim, sim)
            comparisons.append({"reference": ref_name, "similarity": round(sim, 4)})

            # Check individual sentences
            source_sents = [s.strip() for s in re.split(r"[.!?]+", source) if len(s.strip()) > 30]
            for sent in source_sents:
                sent_ngrams = get_ngrams(sent)
                sent_sim = jaccard(sent_ngrams, ref_ngrams)
                if sent_sim > 0.3:
                    flagged.append(
                        {
                            "passage": sent[:200],
                            "similarity": round(sent_sim, 4),
                            "reference": ref_name,
                        }
                    )

        flagged.sort(key=lambda x: x["similarity"], reverse=True)
        return {"max_similarity": max_sim, "comparisons": comparisons, "flagged": flagged[:10]}


# ---------------------------------------------------------------------------
# 6. AuditReproducibilityTool
# ---------------------------------------------------------------------------


class AuditReproducibilityTool(Tool):
    """Audit computation reproducibility of the entire project."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "audit_reproducibility"

    @property
    def description(self) -> str:
        return (
            "Audit computation reproducibility. Checks: all data files have "
            "SHA256 hashes, all analyses have scripts, all figures are "
            "reproducible. Returns reproducibility score and issues."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {},
            "required": [],
        }

    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute reproducibility audit."""
        ws = Path(self._workspace_dir)
        if not ws.exists():
            return ToolResult(success=False, error=f"Workspace not found: {ws}")

        checklist: list[dict[str, Any]] = []
        score = 0
        max_score = 0

        # --- Data Integrity ---
        data_dirs = [ws / "data" / "raw", ws / "data" / "processed", ws / "data"]
        data_files: list[Path] = []
        for d in data_dirs:
            if d.exists():
                data_files.extend(
                    f
                    for f in d.rglob("*")
                    if f.is_file() and f.suffix in (".csv", ".xlsx", ".json", ".parquet", ".dta")
                )

        if data_files:
            # Check if hashes are recorded
            project_config = self._load_project_config(ws)
            recorded_hashes = project_config.get("data_hashes", {})
            verified = 0
            missing_hash = 0

            for data_file in data_files:
                rel_path = str(data_file.relative_to(ws))
                current_hash = self._compute_sha256(data_file)
                if rel_path in recorded_hashes:
                    if recorded_hashes[rel_path] == current_hash:
                        verified += 1
                else:
                    missing_hash += 1

            if missing_hash == 0 and verified > 0:
                checklist.append(
                    {
                        "item": "Data integrity (SHA256 hashes)",
                        "status": "pass",
                        "details": f"All {verified} data files verified.",
                    }
                )
                score += 20
            elif missing_hash > 0:
                checklist.append(
                    {
                        "item": "Data integrity (SHA256 hashes)",
                        "status": "warn",
                        "details": f"{missing_hash} file(s) without recorded hashes.",
                    }
                )
                score += 10
            else:
                checklist.append(
                    {
                        "item": "Data integrity (SHA256 hashes)",
                        "status": "fail",
                        "details": "No hashes recorded in project.yaml.",
                    }
                )
        else:
            checklist.append(
                {
                    "item": "Data integrity (SHA256 hashes)",
                    "status": "fail",
                    "details": "No data files found.",
                }
            )
        max_score += 20

        # --- Analysis Scripts ---
        script_dirs = [ws / "analysis" / "scripts", ws / "scripts", ws / "analysis"]
        scripts: list[Path] = []
        for d in script_dirs:
            if d.exists():
                scripts.extend(f for f in d.rglob("*.py") if f.is_file())
                scripts.extend(f for f in d.rglob("*.R") if f.is_file())

        if scripts:
            # Check syntax
            valid = 0
            for script in scripts:
                if script.suffix == ".py":
                    if self._check_python_syntax(script):
                        valid += 1
                else:
                    valid += 1  # Can't validate R easily

            checklist.append(
                {
                    "item": "Analysis scripts present and valid",
                    "status": "pass" if valid == len(scripts) else "warn",
                    "details": f"{valid}/{len(scripts)} scripts valid.",
                }
            )
            score += 15 if valid == len(scripts) else 8

            # Check random seeds
            seeded = sum(1 for s in scripts if self._has_random_seed(s))
            if seeded == len(scripts):
                checklist.append(
                    {
                        "item": "Random seeds set",
                        "status": "pass",
                        "details": f"All {len(scripts)} scripts set random seeds.",
                    }
                )
                score += 15
            elif seeded > 0:
                checklist.append(
                    {
                        "item": "Random seeds set",
                        "status": "warn",
                        "details": f"{seeded}/{len(scripts)} scripts set random seeds.",
                    }
                )
                score += 8
            else:
                checklist.append(
                    {
                        "item": "Random seeds set",
                        "status": "fail",
                        "details": "No scripts set random seeds.",
                    }
                )
        else:
            checklist.append(
                {
                    "item": "Analysis scripts",
                    "status": "fail",
                    "details": "No analysis scripts found.",
                }
            )
        max_score += 30

        # --- Figures Reproducibility ---
        figures_dir = ws / "analysis" / "figures"
        if figures_dir.exists():
            figure_files = list(figures_dir.glob("*.png")) + list(figures_dir.glob("*.pdf"))
            # Check if there are corresponding scripts
            figure_scripts = [
                f for f in scripts if "figure" in f.stem.lower() or "plot" in f.stem.lower() or "fig" in f.stem.lower()
            ]
            if figure_files and figure_scripts:
                checklist.append(
                    {
                        "item": "Figures reproducible",
                        "status": "pass",
                        "details": f"{len(figure_files)} figures with {len(figure_scripts)} generation scripts.",
                    }
                )
                score += 15
            elif figure_files:
                checklist.append(
                    {
                        "item": "Figures reproducible",
                        "status": "warn",
                        "details": f"{len(figure_files)} figures but no generation scripts found.",
                    }
                )
                score += 5
            else:
                checklist.append(
                    {
                        "item": "Figures reproducible",
                        "status": "pass",
                        "details": "No figures to check.",
                    }
                )
                score += 15
        else:
            checklist.append(
                {
                    "item": "Figures reproducible",
                    "status": "pass",
                    "details": "No figures directory.",
                }
            )
            score += 15
        max_score += 15

        # --- Environment File ---
        env_files = [
            ws / "requirements.txt",
            ws / "environment.yml",
            ws / "pyproject.toml",
        ]
        found_env = [f for f in env_files if f.exists()]
        if found_env:
            checklist.append(
                {
                    "item": "Environment recorded",
                    "status": "pass",
                    "details": f"Found: {', '.join(f.name for f in found_env)}",
                }
            )
            score += 15
        else:
            checklist.append(
                {
                    "item": "Environment recorded",
                    "status": "fail",
                    "details": "No requirements.txt or environment file found.",
                }
            )
        max_score += 15

        # --- Results Files ---
        results_dir = ws / "analysis" / "results"
        if results_dir.exists() and list(results_dir.glob("*.json")):
            checklist.append(
                {
                    "item": "Results files present",
                    "status": "pass",
                    "details": f"{len(list(results_dir.glob('*.json')))} result files.",
                }
            )
            score += 20
        else:
            checklist.append(
                {
                    "item": "Results files present",
                    "status": "fail",
                    "details": "No JSON result files in analysis/results/.",
                }
            )
        max_score += 20

        # --- Final Score ---
        final_score = round((score / max_score) * 100) if max_score > 0 else 0

        # Format output
        lines = [
            "## Reproducibility Audit\n",
            f"### Score: **{final_score}/100**\n",
        ]

        if final_score >= 80:
            lines.append("🟢 **Excellent** — Research is highly reproducible.\n")
        elif final_score >= 60:
            lines.append("🟡 **Good** — Mostly reproducible with minor gaps.\n")
        elif final_score >= 40:
            lines.append("🟠 **Fair** — Significant reproducibility concerns.\n")
        else:
            lines.append("🔴 **Poor** — Major reproducibility issues.\n")

        lines.append("### Checklist")
        for c in checklist:
            icon = {"pass": "✅", "fail": "❌", "warn": "⚠️"}.get(c["status"], "•")
            lines.append(f"  {icon} **{c['item']}**: {c['details']}")

        # Save report
        review_dir = ws / "review"
        review_dir.mkdir(parents=True, exist_ok=True)
        report = {
            "reproducibility_score": final_score,
            "checklist": checklist,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        report_path = review_dir / "reproducibility_audit.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        lines.append(f"\n*Report saved to: {report_path}*")
        return ToolResult(success=True, content="\n".join(lines))

    @staticmethod
    def _compute_sha256(file_path: Path) -> str:
        """Compute SHA256 hash of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    @staticmethod
    def _check_python_syntax(file_path: Path) -> bool:
        """Check if a Python file is syntactically valid."""
        try:
            import ast

            ast.parse(file_path.read_text(encoding="utf-8"))
            return True
        except (SyntaxError, Exception):
            return False

    @staticmethod
    def _has_random_seed(file_path: Path) -> bool:
        """Check if a script sets random seeds."""
        try:
            content = file_path.read_text(encoding="utf-8")
            patterns = [
                r"random\.seed\(",
                r"np\.random\.seed\(",
                r"torch\.manual_seed\(",
                r"random_state\s*=",
                r"seed\s*=\s*\d+",
            ]
            return any(re.search(p, content) for p in patterns)
        except Exception:
            return False

    @staticmethod
    def _load_project_config(ws: Path) -> dict[str, Any]:
        """Load project.yaml config."""
        try:
            import yaml

            yaml_path = ws / "project.yaml"
            if yaml_path.exists():
                return yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
        except Exception:
            pass
        return {}


# Re-export from analysis_tools for convenience
try:
    from .analysis_tools import CheckStatisticalValidityTool  # noqa: F401
except ImportError:
    pass
