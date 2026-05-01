"""Template registry for academic journal formats.

Provides pre-configured LaTeX templates for major publishers and generates
ready-to-compile ``main.tex`` files.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Template definitions
# ---------------------------------------------------------------------------

TEMPLATES: dict[str, dict[str, Any]] = {
    "ieee": {
        "document_class": r"\documentclass[conference]{IEEEtran}",
        "packages": [
            "amsmath",
            "amssymb",
            "graphicx",
            "cite",
            "hyperref",
            "booktabs",
            "algorithm2e",
        ],
        "bib_style": "IEEEtran",
        "section_order": [
            "abstract",
            "introduction",
            "literature_review",
            "methodology",
            "results",
            "discussion",
            "conclusion",
        ],
        "margins": {"top": "1in", "bottom": "1in", "left": "0.625in", "right": "0.625in"},
        "font_size": "10pt",
        "columns": 2,
        "description": "IEEE Conference / Transactions format",
    },
    "elsevier": {
        "document_class": r"\documentclass[preprint,12pt]{elsarticle}",
        "packages": [
            "amsmath",
            "amssymb",
            "graphicx",
            "hyperref",
            "booktabs",
            "natbib",
            "lineno",
        ],
        "bib_style": "elsarticle-num",
        "section_order": [
            "abstract",
            "introduction",
            "literature_review",
            "methodology",
            "results",
            "discussion",
            "conclusion",
        ],
        "margins": {"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
        "font_size": "12pt",
        "columns": 1,
        "description": "Elsevier journal format (preprint mode)",
    },
    "springer": {
        "document_class": r"\documentclass[sn-mathphys-num]{sn-jnl}",
        "packages": [
            "amsmath",
            "amssymb",
            "graphicx",
            "hyperref",
            "booktabs",
            "natbib",
        ],
        "bib_style": "sn-mathphys-num",
        "section_order": [
            "abstract",
            "introduction",
            "literature_review",
            "methodology",
            "results",
            "discussion",
            "conclusion",
        ],
        "margins": {"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
        "font_size": "10pt",
        "columns": 1,
        "description": "Springer Nature journal format",
    },
    "springer_lncs": {
        "document_class": r"\documentclass[runningheads]{llncs}",
        "packages": [
            "amsmath",
            "amssymb",
            "graphicx",
            "hyperref",
            "booktabs",
            "cite",
        ],
        "bib_style": "splncs04",
        "section_order": [
            "abstract",
            "introduction",
            "literature_review",
            "methodology",
            "results",
            "discussion",
            "conclusion",
        ],
        "margins": {"top": "1in", "bottom": "1in", "left": "1.25in", "right": "1.25in"},
        "font_size": "10pt",
        "columns": 1,
        "description": "Springer LNCS (Lecture Notes in Computer Science)",
    },
    "mdpi": {
        "document_class": r"\documentclass[journal,article]{mdpi}",
        "packages": [
            "amsmath",
            "amssymb",
            "graphicx",
            "hyperref",
            "booktabs",
            "natbib",
        ],
        "bib_style": "mdpi",
        "section_order": [
            "abstract",
            "introduction",
            "literature_review",
            "methodology",
            "results",
            "discussion",
            "conclusion",
        ],
        "margins": {"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
        "font_size": "10pt",
        "columns": 1,
        "description": "MDPI open-access journal format",
    },
    "apa7": {
        "document_class": r"\documentclass[man,12pt]{apa7}",
        "packages": [
            "amsmath",
            "graphicx",
            "hyperref",
            "booktabs",
            "csquotes",
        ],
        "bib_style": "apa",
        "section_order": [
            "abstract",
            "introduction",
            "literature_review",
            "methodology",
            "results",
            "discussion",
            "conclusion",
        ],
        "margins": {"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
        "font_size": "12pt",
        "columns": 1,
        "description": "APA 7th edition manuscript format",
    },
}


class TemplateRegistry:
    """Registry of academic journal LaTeX templates.

    Provides template metadata and generates ``main.tex`` content for a
    given template, title, and author list.
    """

    def get_template(self, name: str) -> dict[str, Any]:
        """Return the full template configuration dict.

        Parameters
        ----------
        name:
            Template identifier (e.g. ``"elsevier"``).

        Raises
        ------
        KeyError
            If the template name is not registered.
        """
        if name not in TEMPLATES:
            raise KeyError(f"Unknown template '{name}'. Available: {', '.join(sorted(TEMPLATES))}")
        return dict(TEMPLATES[name])

    def list_templates(self) -> list[str]:
        """Return sorted list of available template names."""
        return sorted(TEMPLATES)

    def get_main_tex(
        self,
        template_name: str,
        title: str,
        authors: list[str] | str,
    ) -> str:
        """Generate a complete ``main.tex`` file.

        Parameters
        ----------
        template_name:
            One of the registered template names.
        title:
            Paper title.
        authors:
            Author name(s).  A single string or list of strings.

        Returns
        -------
        str
            Ready-to-compile LaTeX source.
        """
        tmpl = self.get_template(template_name)

        if isinstance(authors, str):
            authors = [authors]

        lines: list[str] = []

        # Document class
        lines.append(tmpl["document_class"])
        lines.append("")

        # Packages
        for pkg in tmpl["packages"]:
            lines.append(rf"\usepackage{{{pkg}}}")
        lines.append("")

        # Title / author block
        if template_name == "apa7":
            lines.append(rf"\title{{{title}}}")
            for author in authors:
                lines.append(rf"\author{{{author}}}")
            lines.append(r"\authorsaffiliations{{}}")
        elif template_name == "ieee":
            lines.append(rf"\title{{{title}}}")
            lines.append(r"\author{")
            for i, author in enumerate(authors):
                if i > 0:
                    lines.append(r"\and")
                lines.append(rf"  {author}")
            lines.append("}")
        elif template_name in ("springer_lncs",):
            lines.append(rf"\title{{{title}}}")
            for author in authors:
                lines.append(rf"\author{{{author}}}")
            lines.append(r"\institute{}")
        else:
            # Elsevier, Springer, MDPI
            lines.append(rf"\title{{{title}}}")
            for author in authors:
                lines.append(rf"\author{{{author}}}")
        lines.append("")

        # Begin document
        lines.append(r"\begin{document}")
        lines.append(r"\maketitle")
        lines.append("")

        # Include sections
        for section in tmpl["section_order"]:
            lines.append(rf"\input{{sections/{section}}}")
        lines.append("")

        # Bibliography
        bib_style = tmpl["bib_style"]
        lines.append(rf"\bibliographystyle{{{bib_style}}}")
        lines.append(r"\bibliography{references}")
        lines.append("")

        lines.append(r"\end{document}")
        lines.append("")

        return "\n".join(lines)
