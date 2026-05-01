"""Document processing tools for the BPS Academic Research Agent.

Provides tools for:
- convert_document: Convert PDF, DOCX, HTML, and other formats to markdown/text
- parse_academic_pdf: Specialized academic PDF parser with section extraction
- extract_references: Extract bibliographic references from documents
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .base import Tool, ToolResult

# ---------------------------------------------------------------------------
# Optional dependency availability flags
# ---------------------------------------------------------------------------

_HAS_MARKITDOWN = False
try:
    from markitdown import MarkItDown

    _HAS_MARKITDOWN = True
except ImportError:
    pass

_HAS_PDFPLUMBER = False
try:
    import pdfplumber  # noqa: F401

    _HAS_PDFPLUMBER = True
except ImportError:
    pass

_HAS_PYMUPDF = False
try:
    import fitz  # noqa: F401

    _HAS_PYMUPDF = True
except ImportError:
    pass

_HAS_PYPDF2 = False
try:
    from PyPDF2 import PdfReader  # noqa: F401

    _HAS_PYPDF2 = True
except ImportError:
    pass

_HAS_DOCX = False
try:
    import docx  # noqa: F401

    _HAS_DOCX = True
except ImportError:
    pass

_HAS_HTTPX = False
try:
    import httpx  # noqa: F401

    _HAS_HTTPX = True
except ImportError:
    pass


# ===================================================================
# 1. ConvertDocumentTool
# ===================================================================


class ConvertDocumentTool(Tool):
    """Convert documents to markdown, text, or HTML.

    Uses markitdown MCP when available for high-fidelity conversion.
    Falls back to format-specific extractors:
    - PDF: pdfplumber → PyMuPDF → PyPDF2
    - DOCX: python-docx
    - Other: plain text read
    """

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "convert_document"

    @property
    def description(self) -> str:
        return (
            "Convert a document file (PDF, DOCX, HTML, TXT, etc.) to "
            "markdown, plain text, or HTML. Uses markitdown for high-fidelity "
            "conversion when available, otherwise falls back to format-specific "
            "extractors. Saves converted output to workspace."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "input_path": {
                    "type": "string",
                    "description": "Path to the input document (absolute or relative to workspace)",
                },
                "output_format": {
                    "type": "string",
                    "enum": ["markdown", "text", "html"],
                    "description": "Desired output format (default: markdown)",
                },
                "output_path": {
                    "type": "string",
                    "description": "Optional output file path (auto-generated if omitted)",
                },
            },
            "required": ["input_path"],
        }

    async def execute(
        self,
        input_path: str,
        output_format: str = "markdown",
        output_path: str = "",
        **kwargs: Any,
    ) -> ToolResult:
        """Convert a document to the requested output format."""
        workspace = Path(self._workspace_dir)
        full_path = Path(input_path) if Path(input_path).is_absolute() else workspace / input_path

        if not full_path.exists():
            return ToolResult(success=False, error=f"File not found: {full_path}")

        suffix = full_path.suffix.lower()
        converted_text = ""

        # Primary: markitdown
        if _HAS_MARKITDOWN:
            try:
                converter = MarkItDown()
                result = converter.convert(str(full_path))
                converted_text = result.text_content
            except Exception:
                converted_text = ""

        # Fallback: per-format extraction
        if not converted_text:
            if suffix == ".pdf":
                converted_text = self._extract_pdf(full_path)
            elif suffix in {".docx", ".doc"}:
                converted_text = self._extract_docx(full_path)
            elif suffix in {".html", ".htm"}:
                converted_text = self._extract_html(full_path)
            elif suffix in {".txt", ".md", ".csv", ".tsv", ".log", ".rst", ".tex"}:
                converted_text = full_path.read_text(encoding="utf-8", errors="replace")
            else:
                try:
                    converted_text = full_path.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    return ToolResult(
                        success=False,
                        error=(
                            f"Cannot convert {suffix} files. Install markitdown for "
                            "broad format support: pip install markitdown"
                        ),
                    )

        if not converted_text.strip():
            return ToolResult(success=False, error="Conversion produced empty output")

        # Format the result
        if output_format == "text":
            content = re.sub(r"[#*_`~>\[\]!]", "", converted_text)
        elif output_format == "html":
            content = self._markdown_to_html(converted_text)
        else:
            content = converted_text

        # Save converted output
        if output_path:
            out_file = Path(output_path) if Path(output_path).is_absolute() else workspace / output_path
        else:
            output_dir = workspace / "data" / "converted"
            output_dir.mkdir(parents=True, exist_ok=True)
            ext_map = {"markdown": ".md", "text": ".txt", "html": ".html"}
            out_file = output_dir / (full_path.stem + ext_map.get(output_format, ".md"))

        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(content, encoding="utf-8")

        return ToolResult(
            success=True,
            content=(
                f"Converted **{full_path.name}** → {output_format}\n"
                f"Length: {len(content):,} characters\n"
                f"Saved to: {out_file}\n\n"
                f"{content[:3000]}" + ("\n\n… (truncated)" if len(content) > 3000 else "")
            ),
        )

    @staticmethod
    def _extract_pdf(path: Path) -> str:
        """Extract text from PDF using available libraries."""
        if _HAS_PDFPLUMBER:
            try:
                import pdfplumber

                pages: list[str] = []
                with pdfplumber.open(str(path)) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            pages.append(text)
                return "\n\n".join(pages)
            except Exception:
                pass

        if _HAS_PYMUPDF:
            try:
                import fitz

                doc = fitz.open(str(path))
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            except Exception:
                pass

        if _HAS_PYPDF2:
            try:
                from PyPDF2 import PdfReader

                reader = PdfReader(str(path))
                pages = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
                return "\n\n".join(pages)
            except Exception:
                pass

        return ""

    @staticmethod
    def _extract_docx(path: Path) -> str:
        """Extract text from DOCX using python-docx."""
        if not _HAS_DOCX:
            return ""
        try:
            import docx

            doc = docx.Document(str(path))
            paragraphs: list[str] = []
            for para in doc.paragraphs:
                if para.text.strip():
                    # Preserve heading structure
                    if para.style and para.style.name.startswith("Heading"):
                        level = para.style.name.replace("Heading ", "")
                        try:
                            hashes = "#" * int(level)
                        except ValueError:
                            hashes = "##"
                        paragraphs.append(f"{hashes} {para.text}")
                    else:
                        paragraphs.append(para.text)
            return "\n\n".join(paragraphs)
        except Exception:
            return ""

    @staticmethod
    def _extract_html(path: Path) -> str:
        """Minimal HTML-to-text extraction."""
        raw = path.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _markdown_to_html(md_text: str) -> str:
        """Very basic markdown to HTML conversion."""
        html = md_text
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
        html = re.sub(r"^# (.+)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
        html = re.sub(r"\n\n", r"</p><p>", html)
        return f"<html><body><p>{html}</p></body></html>"


# ===================================================================
# 2. ParseAcademicPDFTool
# ===================================================================


class ParseAcademicPDFTool(Tool):
    """Specialized academic PDF parser with section extraction.

    Extracts structured data: title, authors, abstract, sections,
    tables, figures, and references. Uses GROBID MCP when available,
    falls back to regex-based extraction on raw text.
    """

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "parse_academic_pdf"

    @property
    def description(self) -> str:
        return (
            "Parse a scientific/academic PDF with structured extraction. "
            "Extracts title, authors, abstract, sections, tables, figures, "
            "and references. Uses GROBID service when available, otherwise "
            "falls back to regex-based section identification."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pdf_path": {
                    "type": "string",
                    "description": "Path to the PDF file (absolute or relative to workspace)",
                },
                "extract": {
                    "type": "string",
                    "enum": ["all", "text", "tables", "figures", "references"],
                    "description": "What to extract (default: all)",
                },
            },
            "required": ["pdf_path"],
        }

    async def execute(
        self,
        pdf_path: str,
        extract: str = "all",
        **kwargs: Any,
    ) -> ToolResult:
        """Parse an academic PDF and return structured sections."""
        workspace = Path(self._workspace_dir)
        full_path = Path(pdf_path) if Path(pdf_path).is_absolute() else workspace / pdf_path

        if not full_path.exists():
            return ToolResult(success=False, error=f"PDF not found: {full_path}")
        if full_path.suffix.lower() != ".pdf":
            return ToolResult(success=False, error=f"Not a PDF file: {full_path.name}")

        # Try GROBID first
        if _HAS_HTTPX:
            try:
                grobid_result = await self._parse_with_grobid(full_path, extract)
                if grobid_result:
                    return self._format_result(full_path, grobid_result, "grobid", workspace)
            except Exception:
                pass

        # Fallback: extract text and identify sections with regex
        raw_text = self._extract_pdf_text(full_path)
        if not raw_text.strip():
            return ToolResult(
                success=False,
                error=(
                    "Could not extract text from PDF. Install one of: "
                    "pip install pdfplumber; pip install PyMuPDF; pip install PyPDF2"
                ),
            )

        sections = self._identify_sections(raw_text, extract)
        return self._format_result(full_path, sections, "regex", workspace)

    @staticmethod
    def _extract_pdf_text(path: Path) -> str:
        """Extract raw text from PDF using available libraries."""
        if _HAS_PDFPLUMBER:
            try:
                import pdfplumber

                pages: list[str] = []
                with pdfplumber.open(str(path)) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            pages.append(text)
                return "\n\n".join(pages)
            except Exception:
                pass

        if _HAS_PYMUPDF:
            try:
                import fitz

                doc = fitz.open(str(path))
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            except Exception:
                pass

        if _HAS_PYPDF2:
            try:
                from PyPDF2 import PdfReader

                reader = PdfReader(str(path))
                pages = []
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        pages.append(t)
                return "\n\n".join(pages)
            except Exception:
                pass

        return ""

    async def _parse_with_grobid(self, path: Path, extract: str) -> dict[str, Any] | None:
        """Parse PDF using GROBID REST API at localhost:8070."""
        import httpx

        grobid_url = "http://localhost:8070/api/processFulltextDocument"

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                with open(path, "rb") as f:
                    response = await client.post(
                        grobid_url,
                        files={"input": (path.name, f, "application/pdf")},
                    )

                if response.status_code != 200:
                    return None

                tei_xml = response.text
                return self._parse_grobid_tei(tei_xml, extract)
        except Exception:
            return None

    @staticmethod
    def _parse_grobid_tei(tei_xml: str, extract: str) -> dict[str, Any]:
        """Parse GROBID TEI XML into structured sections."""
        sections: dict[str, Any] = {}

        # Title
        title_match = re.search(r"<title[^>]*type=\"main\"[^>]*>(.*?)</title>", tei_xml, re.DOTALL)
        if title_match:
            sections["title"] = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()

        # Abstract
        abstract_match = re.search(r"<abstract>(.*?)</abstract>", tei_xml, re.DOTALL)
        if abstract_match:
            sections["abstract"] = re.sub(r"<[^>]+>", "", abstract_match.group(1)).strip()

        # Authors
        authors: list[str] = []
        for author_match in re.finditer(r"<persName[^>]*>(.*?)</persName>", tei_xml, re.DOTALL):
            name_parts: list[str] = []
            for tag in ["forename", "surname"]:
                m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", author_match.group(1))
                if m:
                    name_parts.append(m.group(1).strip())
            if name_parts:
                authors.append(" ".join(name_parts))
        if authors:
            sections["authors"] = list(dict.fromkeys(authors))[:20]  # Deduplicate

        # Body sections
        if extract in ("all", "text"):
            body_match = re.search(r"<body>(.*?)</body>", tei_xml, re.DOTALL)
            if body_match:
                body = body_match.group(1)
                for div_match in re.finditer(r"<div[^>]*>(.*?)</div>", body, re.DOTALL):
                    head_match = re.search(r"<head[^>]*>(.*?)</head>", div_match.group(1))
                    if head_match:
                        section_name = re.sub(r"<[^>]+>", "", head_match.group(1)).strip().lower()
                        section_text = re.sub(r"<[^>]+>", "", div_match.group(1)).strip()
                        if section_name and section_text:
                            sections[section_name] = section_text

        # References
        if extract in ("all", "references"):
            refs: list[str] = []
            for bib_match in re.finditer(r"<biblStruct[^>]*>(.*?)</biblStruct>", tei_xml, re.DOTALL):
                ref_text = re.sub(r"<[^>]+>", " ", bib_match.group(1))
                ref_text = re.sub(r"\s+", " ", ref_text).strip()
                if ref_text:
                    refs.append(ref_text)
            if refs:
                sections["references"] = refs

        return sections

    def _identify_sections(self, text: str, extract: str) -> dict[str, Any]:
        """Identify standard academic paper sections from raw text."""
        sections: dict[str, Any] = {}

        # Title: first non-empty line
        lines = text.strip().split("\n")
        for line in lines[:5]:
            if line.strip() and len(line.strip()) > 5:
                sections["title"] = line.strip()
                break

        section_patterns = [
            (
                "abstract",
                r"(?:^|\n)\s*(?:abstract|ringkasan|abstrak)\s*\n(.*?)(?=\n\s*(?:\d+\.?\s*)?(?:introduction|keywords|kata kunci|pendahuluan)|\Z)",
            ),
            ("keywords", r"(?:keywords?|kata kunci)\s*[:\-]?\s*(.+?)(?:\n\n|\n\s*\d)"),
            (
                "introduction",
                r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:introduction|pendahuluan)\s*\n(.*?)(?=\n\s*(?:\d+\.?\s*)?(?:literature|related|method|data|theoretical|tinjauan|metod)|\Z)",
            ),
            (
                "literature_review",
                r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:literature\s*review|related\s*work|theoretical\s*framework|tinjauan\s*pustaka)\s*\n(.*?)(?=\n\s*(?:\d+\.?\s*)?(?:method|data|research\s*design|metod)|\Z)",
            ),
            (
                "methods",
                r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:method(?:ology|s)?|data\s*(?:and|&)\s*method|research\s*design|metode?\s*penelitian)\s*\n(.*?)(?=\n\s*(?:\d+\.?\s*)?(?:result|finding|analysis|hasil)|\Z)",
            ),
            (
                "results",
                r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:results?(?:\s*(?:and|&)\s*discussion)?|findings?|analysis|hasil)\s*\n(.*?)(?=\n\s*(?:\d+\.?\s*)?(?:discussion|conclusion|kesimpulan|implications)|\Z)",
            ),
            (
                "discussion",
                r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:discussion|pembahasan)\s*\n(.*?)(?=\n\s*(?:\d+\.?\s*)?(?:conclusion|limitation|kesimpulan|implications)|\Z)",
            ),
            (
                "conclusion",
                r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:conclusion|concluding|summary|kesimpulan)\s*\n(.*?)(?=\n\s*(?:\d+\.?\s*)?(?:reference|bibliograph|acknowledge|daftar\s*pustaka|appendix)|\Z)",
            ),
            ("references", r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:references?|bibliography|daftar\s*pustaka)\s*\n(.*)"),
        ]

        if extract in ("all", "text"):
            for section_name, pattern in section_patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                if match:
                    content = match.group(1).strip() if match.lastindex else match.group(0).strip()
                    if content:
                        sections[section_name] = content

        # Tables
        if extract in ("all", "tables"):
            tables = self._extract_tables(text)
            if tables:
                sections["tables"] = tables

        # Figures
        if extract in ("all", "figures"):
            figures = self._extract_figure_captions(text)
            if figures:
                sections["figures"] = figures

        # If no sections detected, store full text
        if not sections or (len(sections) == 1 and "title" in sections):
            sections["full_text"] = text

        return sections

    @staticmethod
    def _extract_tables(text: str) -> list[str]:
        """Extract table captions and content indicators."""
        tables: list[str] = []
        for match in re.finditer(
            r"(?:Table|Tabel)\s*\d+[.:]\s*(.+?)(?:\n\n|\n(?=[A-Z\d]))",
            text,
            re.IGNORECASE,
        ):
            tables.append(match.group(0).strip())
        return tables

    @staticmethod
    def _extract_figure_captions(text: str) -> list[str]:
        """Extract figure captions from text."""
        captions: list[str] = []
        for match in re.finditer(
            r"(?:Fig(?:ure|\.)|Gambar)\s*\d+[.:]\s*(.+?)(?:\n\n|\n(?=[A-Z\d]))",
            text,
            re.IGNORECASE,
        ):
            captions.append(match.group(0).strip())
        return captions

    @staticmethod
    def _format_result(
        pdf_path: Path,
        sections: dict[str, Any],
        method: str,
        workspace: Path,
    ) -> ToolResult:
        """Format and save the parsed result."""
        output_dir = workspace / "literature" / "parsed"
        output_dir.mkdir(parents=True, exist_ok=True)
        out_json = output_dir / (pdf_path.stem + "_parsed.json")

        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(sections, f, indent=2, ensure_ascii=False)

        lines = [
            f"## Parsed: {pdf_path.name}",
            f"**Method:** {method}",
            f"**Sections found:** {len(sections)}",
            "",
        ]
        for key, value in sections.items():
            if isinstance(value, str):
                preview = value[:300].replace("\n", " ")
                lines.append(f"### {key.replace('_', ' ').title()}")
                lines.append(preview + ("…" if len(value) > 300 else ""))
                lines.append("")
            elif isinstance(value, list):
                lines.append(f"### {key.replace('_', ' ').title()} ({len(value)} items)")
                for item in value[:5]:
                    lines.append(f"- {str(item)[:120]}")
                if len(value) > 5:
                    lines.append(f"  … and {len(value) - 5} more")
                lines.append("")

        lines.append(f"\n*Structured output saved to: {out_json}*")
        return ToolResult(success=True, content="\n".join(lines))


# ===================================================================
# 3. ExtractReferencesTool
# ===================================================================


class ExtractReferencesTool(Tool):
    """Extract bibliographic references from a document.

    Uses GROBID service when available for high-quality structured
    extraction, falls back to regex-based heuristic parsing.
    """

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "extract_references"

    @property
    def description(self) -> str:
        return (
            "Extract bibliographic references from a PDF or text document. "
            "Returns BibTeX entries or JSON metadata. Uses GROBID service "
            "when available, otherwise falls back to regex-based extraction "
            "for common citation formats."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pdf_path": {
                    "type": "string",
                    "description": "Path to the PDF file (alternative: provide 'text')",
                },
                "text": {
                    "type": "string",
                    "description": "Raw text containing references (alternative: provide 'pdf_path')",
                },
                "output_format": {
                    "type": "string",
                    "enum": ["bibtex", "json"],
                    "description": "Output format for references (default: bibtex)",
                },
            },
            "required": [],
        }

    async def execute(
        self,
        pdf_path: str = "",
        text: str = "",
        output_format: str = "bibtex",
        **kwargs: Any,
    ) -> ToolResult:
        """Extract references from a PDF or text."""
        workspace = Path(self._workspace_dir)
        source_name = "input_text"

        if pdf_path:
            full_path = Path(pdf_path) if Path(pdf_path).is_absolute() else workspace / pdf_path
            if not full_path.exists():
                return ToolResult(success=False, error=f"File not found: {full_path}")
            source_name = full_path.stem

            # Try GROBID first for PDFs
            if _HAS_HTTPX:
                try:
                    grobid_refs = await self._extract_with_grobid(full_path)
                    if grobid_refs:
                        return self._format_output(grobid_refs, output_format, source_name, workspace, "grobid")
                except Exception:
                    pass

            # Extract text from PDF for regex fallback
            text = self._get_pdf_text(full_path)

        if not text:
            return ToolResult(
                success=False,
                error="No text available. Provide 'pdf_path' or 'text' parameter.",
            )

        # Regex-based extraction
        references = self._extract_references_regex(text)
        if not references:
            return ToolResult(
                success=False,
                error="Could not extract references. Ensure the document contains a references section.",
            )

        return self._format_output(references, output_format, source_name, workspace, "regex")

    @staticmethod
    async def _extract_with_grobid(path: Path) -> list[dict[str, str]]:
        """Extract references via GROBID REST API."""
        import httpx

        grobid_url = "http://localhost:8070/api/processReferences"

        async with httpx.AsyncClient(timeout=60.0) as client:
            with open(path, "rb") as f:
                response = await client.post(
                    grobid_url,
                    files={"input": (path.name, f, "application/pdf")},
                )

            if response.status_code != 200:
                return []

            tei_xml = response.text
            return ExtractReferencesTool._parse_grobid_refs(tei_xml)

    @staticmethod
    def _parse_grobid_refs(tei_xml: str) -> list[dict[str, str]]:
        """Parse GROBID TEI XML into reference dicts."""
        references: list[dict[str, str]] = []

        bib_entries = re.findall(r"<biblStruct[^>]*>(.*?)</biblStruct>", tei_xml, re.DOTALL)

        for entry in bib_entries:
            ref: dict[str, str] = {}

            title_match = re.search(r"<title[^>]*>(.*?)</title>", entry, re.DOTALL)
            if title_match:
                ref["title"] = re.sub(r"<[^>]+>", "", title_match.group(1)).strip()

            authors: list[str] = []
            for author_match in re.finditer(r"<persName[^>]*>(.*?)</persName>", entry, re.DOTALL):
                name_parts: list[str] = []
                for tag in ["forename", "surname"]:
                    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", author_match.group(1))
                    if m:
                        name_parts.append(m.group(1).strip())
                if name_parts:
                    authors.append(" ".join(name_parts))
            if authors:
                ref["authors"] = " and ".join(authors)

            year_match = re.search(r'when="(\d{4})"', entry)
            if year_match:
                ref["year"] = year_match.group(1)

            journal_match = re.search(r"<title[^>]*level=\"j\"[^>]*>(.*?)</title>", entry, re.DOTALL)
            if journal_match:
                ref["journal"] = re.sub(r"<[^>]+>", "", journal_match.group(1)).strip()

            vol_match = re.search(r'<biblScope[^>]*unit="volume"[^>]*>(.*?)</biblScope>', entry)
            if vol_match:
                ref["volume"] = vol_match.group(1).strip()

            doi_match = re.search(r'type="DOI">(.*?)</idno>', entry)
            if doi_match:
                ref["doi"] = doi_match.group(1).strip()

            if ref.get("title") or ref.get("authors"):
                references.append(ref)

        return references

    @staticmethod
    def _get_pdf_text(path: Path) -> str:
        """Get raw text from PDF using any available library."""
        if _HAS_PDFPLUMBER:
            try:
                import pdfplumber

                pages: list[str] = []
                with pdfplumber.open(str(path)) as pdf:
                    for page in pdf.pages:
                        t = page.extract_text()
                        if t:
                            pages.append(t)
                return "\n".join(pages)
            except Exception:
                pass

        if _HAS_PYMUPDF:
            try:
                import fitz

                doc = fitz.open(str(path))
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            except Exception:
                pass

        if _HAS_PYPDF2:
            try:
                from PyPDF2 import PdfReader

                reader = PdfReader(str(path))
                pages = []
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        pages.append(t)
                return "\n".join(pages)
            except Exception:
                pass

        return ""

    @staticmethod
    def _extract_references_regex(text: str) -> list[dict[str, str]]:
        """Extract references using regex heuristics."""
        references: list[dict[str, str]] = []

        # Find the references section
        ref_match = re.search(
            r"(?:^|\n)\s*(?:references?|bibliography|daftar\s*pustaka)\s*\n(.*)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if not ref_match:
            return []

        ref_text = ref_match.group(1)

        # Split into individual references
        entries = re.split(r"\n\s*(?:\[?\d+\]?\.?\s+|•\s+)", ref_text)

        for entry in entries:
            entry = entry.strip()
            if len(entry) < 20:
                continue

            ref: dict[str, str] = {"raw": entry}

            # Authors
            author_match = re.match(
                r"^((?:[A-Z][a-z]+(?:,?\s+(?:[A-Z]\.?\s*)+)?(?:,?\s*(?:and|&|,)\s*)?)+)",
                entry,
            )
            if author_match:
                ref["authors"] = author_match.group(1).strip().rstrip(",").rstrip("&").strip()

            # Year
            year_match = re.search(r"\((\d{4}[a-z]?)\)|(\d{4})[.,]", entry)
            if year_match:
                ref["year"] = (year_match.group(1) or year_match.group(2)).strip()

            # Title
            title_match = re.search(r'["\u201c](.+?)["\u201d]', entry)
            if not title_match:
                title_match = re.search(r"\d{4}[a-z]?\)?\.\s*(.+?)[.,]\s*(?:[A-Z]|$)", entry)
            if title_match:
                ref["title"] = title_match.group(1).strip()

            # DOI
            doi_match = re.search(r"(10\.\d{4,}/[^\s]+)", entry)
            if doi_match:
                ref["doi"] = doi_match.group(1).rstrip(".")

            if ref.get("title") or ref.get("authors"):
                references.append(ref)

        return references

    @staticmethod
    def _format_output(
        references: list[dict[str, str]],
        output_format: str,
        source_name: str,
        workspace: Path,
        method: str,
    ) -> ToolResult:
        """Format and save extracted references."""
        if output_format == "bibtex":
            output_text = ExtractReferencesTool._to_bibtex(references)
            ext = ".bib"
        else:
            output_text = json.dumps(references, indent=2, ensure_ascii=False)
            ext = ".json"

        output_dir = workspace / "literature" / "references"
        output_dir.mkdir(parents=True, exist_ok=True)
        out_file = output_dir / (source_name + "_refs" + ext)
        out_file.write_text(output_text, encoding="utf-8")

        return ToolResult(
            success=True,
            content=(
                f"## Extracted References\n\n"
                f"**Source:** {source_name}\n"
                f"**Method:** {method}\n"
                f"**Count:** {len(references)} references\n"
                f"**Format:** {output_format}\n"
                f"**Saved to:** {out_file}\n\n"
                f"```{output_format}\n{output_text[:4000]}\n```"
                + ("\n\n… (truncated)" if len(output_text) > 4000 else "")
            ),
        )

    @staticmethod
    def _to_bibtex(references: list[dict[str, str]]) -> str:
        """Convert reference dicts to BibTeX format."""
        entries: list[str] = []

        for i, ref in enumerate(references):
            first_author = ""
            if ref.get("authors"):
                first_author = re.split(r"[,\s]+", ref["authors"])[0].lower()
            year = ref.get("year", "nd")
            cite_key = f"{first_author}{year}_{i + 1}" if first_author else f"ref{i + 1}"

            entry_type = "article" if ref.get("journal") else "misc"

            lines = [f"@{entry_type}{{{cite_key},"]
            if ref.get("authors"):
                lines.append(f"  author = {{{ref['authors']}}},")
            if ref.get("title"):
                lines.append(f"  title = {{{ref['title']}}},")
            if ref.get("journal"):
                lines.append(f"  journal = {{{ref['journal']}}},")
            if ref.get("year"):
                lines.append(f"  year = {{{ref['year']}}},")
            if ref.get("volume"):
                lines.append(f"  volume = {{{ref['volume']}}},")
            if ref.get("doi"):
                lines.append(f"  doi = {{{ref['doi']}}},")
            lines.append("}")

            entries.append("\n".join(lines))

        return "\n\n".join(entries)
