"""Section writer for academic paper generation.

Manages individual paper sections (abstract, introduction, etc.) as files
within the ``paper/sections/`` directory of a research workspace.  Supports
both LaTeX and Markdown output and tracks word counts.
"""

from __future__ import annotations

import re
from pathlib import Path

VALID_SECTIONS: list[str] = [
    "abstract",
    "introduction",
    "literature_review",
    "methodology",
    "results",
    "discussion",
    "conclusion",
]

_LATEX_SECTION_COMMANDS: dict[str, str] = {
    "abstract": r"\begin{abstract}",
    "introduction": r"\section{Introduction}",
    "literature_review": r"\section{Literature Review}",
    "methodology": r"\section{Methodology}",
    "results": r"\section{Results}",
    "discussion": r"\section{Discussion}",
    "conclusion": r"\section{Conclusion}",
}

_LATEX_SECTION_END: dict[str, str] = {
    "abstract": r"\end{abstract}",
}

_SECTION_GUIDELINES: dict[str, str] = {
    "abstract": "150-300 words. Structure: Objective → Methods → Results → Conclusions.",
    "introduction": ("Broad context → Current knowledge → Gap → Objectives/hypotheses. Funnel structure."),
    "literature_review": ("Thematic organization. Every claim needs \\cite{}. Group by framework, methods, findings."),
    "methodology": ("Study design → Population → Instruments → Procedures → Variables → Analysis. Past tense."),
    "results": ("Preliminary analyses → Descriptive stats → Main analyses → Robustness checks."),
    "discussion": ("Summary → Interpretation vs literature → Implications → Limitations → Future research."),
    "conclusion": ("200-400 words. Restate findings. No new data. Practical implications. Future directions."),
}


class SectionWriter:
    """Write, update, and read individual paper sections.

    Sections are stored as files under ``<workspace>/paper/sections/``.

    Parameters
    ----------
    workspace_path:
        Root directory of the research workspace.
    template:
        Journal template name (used for LaTeX preamble hints).
    """

    def __init__(self, workspace_path: str | Path, template: str = "elsevier") -> None:
        self.workspace_path = Path(workspace_path)
        self.template = template
        self._sections_dir = self.workspace_path / "paper" / "sections"
        self._sections_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def write_section(
        self,
        section_name: str,
        content: str,
        citations: list[str] | None = None,
        output_format: str = "latex",
    ) -> Path:
        """Write a new section file.

        Parameters
        ----------
        section_name:
            One of :data:`VALID_SECTIONS` or an arbitrary name.
        content:
            Body text for the section.
        citations:
            Optional list of citation keys to append as ``\\cite{}``.
        output_format:
            ``"latex"`` (default) or ``"markdown"``.

        Returns
        -------
        Path
            Absolute path to the written file.
        """
        self._validate_section_name(section_name)
        ext = ".tex" if output_format == "latex" else ".md"
        output_path = self._sections_dir / f"{section_name}{ext}"

        if output_format == "latex":
            text = self._build_latex(section_name, content, citations)
        else:
            text = self._build_markdown(section_name, content, citations)

        output_path.write_text(text, encoding="utf-8")
        return output_path

    def update_section(self, section_name: str, content: str) -> Path:
        """Replace the body of an existing section, preserving the header.

        If the section file does not exist yet, it is created via
        :meth:`write_section`.

        Returns
        -------
        Path
            Absolute path to the updated file.
        """
        tex_path = self._sections_dir / f"{section_name}.tex"
        md_path = self._sections_dir / f"{section_name}.md"

        if tex_path.exists():
            existing = tex_path.read_text(encoding="utf-8")
            section_end = _LATEX_SECTION_END.get(section_name, "")
            section_cmd = _LATEX_SECTION_COMMANDS.get(
                section_name,
                rf"\section{{{section_name.replace('_', ' ').title()}}}",
            )

            # Rebuild: keep header comment lines, replace body
            header_lines: list[str] = []
            for line in existing.splitlines():
                if line.startswith("%"):
                    header_lines.append(line)
                else:
                    break

            body_parts = ["\n".join(header_lines), "", section_cmd]
            if section_name != "abstract":
                body_parts.append(rf"\label{{sec:{section_name}}}")
            body_parts.append("")
            body_parts.append(content)
            if section_end:
                body_parts.append(section_end)
            body_parts.append("")

            tex_path.write_text("\n".join(body_parts), encoding="utf-8")
            return tex_path

        if md_path.exists():
            title = section_name.replace("_", " ").title()
            md_path.write_text(f"## {title}\n\n{content}\n", encoding="utf-8")
            return md_path

        # Section doesn't exist yet – create it
        return self.write_section(section_name, content)

    def get_section(self, section_name: str) -> str | None:
        """Return the raw text of a section, or ``None`` if it doesn't exist."""
        for ext in (".tex", ".md"):
            path = self._sections_dir / f"{section_name}{ext}"
            if path.exists():
                return path.read_text(encoding="utf-8")
        return None

    def get_word_count(self, section_name: str) -> int:
        """Return the approximate word count of a section (LaTeX commands stripped)."""
        raw = self.get_section(section_name)
        if raw is None:
            return 0
        return self._count_words(raw)

    def get_all_sections(self) -> dict[str, str]:
        """Return ``{section_name: content}`` for every section on disk."""
        sections: dict[str, str] = {}
        for path in sorted(self._sections_dir.iterdir()):
            if path.suffix in (".tex", ".md") and path.is_file():
                sections[path.stem] = path.read_text(encoding="utf-8")
        return sections

    def get_guidelines(self, section_name: str) -> str:
        """Return writing guidelines for a section."""
        return _SECTION_GUIDELINES.get(section_name, "")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_section_name(name: str) -> None:
        """Raise ``ValueError`` for clearly invalid names."""
        if not name or not re.match(r"^[a-z][a-z0-9_]*$", name):
            raise ValueError(f"Invalid section name '{name}'. Use lowercase alphanumeric with underscores.")

    @staticmethod
    def _count_words(text: str) -> int:
        """Strip LaTeX/Markdown markup and count words."""
        plain = re.sub(r"\\[a-zA-Z]+(\{[^}]*\})?", "", text)
        plain = re.sub(r"[{}%\\$#]", "", plain)
        plain = re.sub(r"\s+", " ", plain).strip()
        return len(plain.split())

    def _build_latex(
        self,
        section_name: str,
        content: str,
        citations: list[str] | None,
    ) -> str:
        section_cmd = _LATEX_SECTION_COMMANDS.get(
            section_name,
            rf"\section{{{section_name.replace('_', ' ').title()}}}",
        )
        section_end = _LATEX_SECTION_END.get(section_name, "")
        guideline = _SECTION_GUIDELINES.get(section_name, "")

        lines: list[str] = [
            f"% Section: {section_name}",
            f"% Template: {self.template}",
        ]
        if guideline:
            lines.append(f"% Guidelines: {guideline}")
        lines.append("")
        lines.append(section_cmd)

        if section_name != "abstract":
            lines.append(rf"\label{{sec:{section_name}}}")
            lines.append("")

        body = content
        if citations:
            cite_str = ", ".join(citations)
            body += rf" \cite{{{cite_str}}}"

        lines.append(body)

        if section_end:
            lines.append(section_end)
        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _build_markdown(
        section_name: str,
        content: str,
        citations: list[str] | None,
    ) -> str:
        title = section_name.replace("_", " ").title()
        lines: list[str] = [f"## {title}", ""]
        body = content
        if citations:
            refs = "; ".join(f"@{c}" for c in citations)
            body += f" [{refs}]"
        lines.append(body)
        lines.append("")
        return "\n".join(lines)
