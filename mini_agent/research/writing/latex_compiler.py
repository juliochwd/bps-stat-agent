"""LaTeX compiler with graceful fallback chain.

Tries compilers in order: tectonic → pdflatex → error with install instructions.
Also supports compiling individual sections to plain text for preview.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

# Ordered list of compilers to attempt
_COMPILER_CHAIN: list[str] = ["tectonic", "pdflatex"]


class LaTeXCompiler:
    """Compile LaTeX documents to PDF.

    Parameters
    ----------
    workspace_path:
        Root directory of the research workspace.
    """

    def __init__(self, workspace_path: str | Path) -> None:
        self.workspace_path = Path(workspace_path)
        self._compiled_dir = self.workspace_path / "writing" / "compiled"
        self._compiled_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compile_pdf(self, main_tex_path: str | Path | None = None) -> Path:
        """Compile a ``.tex`` file to PDF.

        Parameters
        ----------
        main_tex_path:
            Path to the main ``.tex`` file.  Resolved relative to
            *workspace_path* when not absolute.  Defaults to
            ``writing/main.tex``.

        Returns
        -------
        Path
            Absolute path to the generated PDF.

        Raises
        ------
        FileNotFoundError
            If the source ``.tex`` file does not exist.
        RuntimeError
            If no compiler is available or compilation fails.
        """
        if main_tex_path is None:
            tex_path = self.workspace_path / "writing" / "main.tex"
        else:
            tex_path = Path(main_tex_path)
            if not tex_path.is_absolute():
                tex_path = self.workspace_path / tex_path

        if not tex_path.exists():
            raise FileNotFoundError(f"TeX file not found: {tex_path}")

        for compiler in _COMPILER_CHAIN:
            if not self._compiler_available(compiler):
                continue
            pdf_path = self._run_compiler(compiler, tex_path)
            if pdf_path is not None:
                return pdf_path

        raise RuntimeError(
            "No LaTeX compiler available. Install one of:\n"
            "  tectonic : curl --proto '=https' --tlsv1.2 -fsSL "
            "https://drop-sh.fullyjustified.net | sh\n"
            "  pdflatex : sudo apt-get install texlive-full\n\n"
            "Or upload the .tex files to Overleaf."
        )

    def compile_section(self, section_name: str) -> str:
        """Return the raw text of a section file (no actual compilation).

        This is a convenience method that reads the section file and strips
        LaTeX commands so the caller can preview the plain-text content.

        Returns
        -------
        str
            Plain-text approximation of the section.

        Raises
        ------
        FileNotFoundError
            If the section file does not exist.
        """
        sections_dir = self.workspace_path / "paper" / "sections"
        for ext in (".tex", ".md"):
            path = sections_dir / f"{section_name}{ext}"
            if path.exists():
                raw = path.read_text(encoding="utf-8")
                return self._strip_latex(raw)

        # Also check writing/sections/ (alternate layout)
        alt_dir = self.workspace_path / "writing" / "sections"
        for ext in (".tex", ".md"):
            path = alt_dir / f"{section_name}{ext}"
            if path.exists():
                raw = path.read_text(encoding="utf-8")
                return self._strip_latex(raw)

        raise FileNotFoundError(f"Section '{section_name}' not found in paper/sections/ or writing/sections/")

    def check_compilation_errors(self, log_path: str | Path | None = None) -> list[str]:
        """Parse a ``.log`` file and return error/warning lines.

        Parameters
        ----------
        log_path:
            Path to the ``.log`` file.  When *None*, looks for the most
            recent log in ``writing/compiled/``.

        Returns
        -------
        list[str]
            Lines containing errors or warnings.
        """
        if log_path is None:
            logs = sorted(self._compiled_dir.glob("*.log"), key=lambda p: p.stat().st_mtime)
            if not logs:
                return []
            log_file = logs[-1]
        else:
            log_file = Path(log_path)
            if not log_file.is_absolute():
                log_file = self.workspace_path / log_file

        if not log_file.exists():
            return []

        issues: list[str] = []
        for line in log_file.read_text(encoding="utf-8", errors="replace").splitlines():
            lower = line.lower()
            if "error" in lower or line.startswith("!") or "warning" in lower or "undefined" in lower:
                issues.append(line.strip())
        return issues

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compiler_available(name: str) -> bool:
        """Return ``True`` if *name* is on ``$PATH``."""
        try:
            result = subprocess.run(
                ["which", name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _run_compiler(self, compiler: str, tex_path: Path) -> Path | None:
        """Attempt compilation with *compiler*.  Returns PDF path or ``None``."""
        out_dir = self._compiled_dir

        if compiler == "tectonic":
            cmd = [
                "tectonic",
                "-X",
                "compile",
                str(tex_path),
                "--outdir",
                str(out_dir),
            ]
        elif compiler == "pdflatex":
            cmd = [
                "pdflatex",
                f"-output-directory={out_dir}",
                "-interaction=nonstopmode",
                "-halt-on-error",
                str(tex_path),
            ]
        else:
            return None

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(tex_path.parent),
            )

            # pdflatex needs a second pass for cross-references
            if compiler == "pdflatex" and proc.returncode == 0:
                subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(tex_path.parent),
                )

            pdf_path = out_dir / (tex_path.stem + ".pdf")
            if pdf_path.exists():
                return pdf_path

        except (subprocess.TimeoutExpired, OSError):
            pass

        return None

    @staticmethod
    def _strip_latex(text: str) -> str:
        """Remove LaTeX commands and return approximate plain text."""
        # Remove comments
        text = re.sub(r"(?m)^%.*$", "", text)
        # Remove common environments
        text = re.sub(r"\\begin\{[^}]+\}", "", text)
        text = re.sub(r"\\end\{[^}]+\}", "", text)
        # Remove commands but keep their arguments
        text = re.sub(r"\\[a-zA-Z]+\*?\{([^}]*)\}", r"\1", text)
        # Remove remaining backslash commands
        text = re.sub(r"\\[a-zA-Z]+\*?", "", text)
        # Remove braces, dollar signs
        text = re.sub(r"[{}$]", "", text)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text
