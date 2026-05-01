"""Bibliography manager for BibTeX files.

Provides CRUD operations on a ``.bib`` file.  Uses ``bibtexparser`` when
available and falls back to regex-based parsing otherwise.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

try:
    import bibtexparser  # type: ignore[import-untyped]

    _HAS_BIBTEXPARSER = True
except ImportError:
    _HAS_BIBTEXPARSER = False


class BibliographyManager:
    """Manage a BibTeX bibliography file.

    Parameters
    ----------
    bib_path:
        Path to the ``.bib`` file.  Created on first write if it does not
        exist.
    """

    def __init__(self, bib_path: str | Path) -> None:
        self.bib_path = Path(bib_path)
        self.bib_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.bib_path.exists():
            self.bib_path.write_text(
                "% BibTeX bibliography\n% Managed by BPS Academic Research Agent\n\n",
                encoding="utf-8",
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_entry(self, bibtex_str: str) -> str:
        """Append a BibTeX entry and return its citation key.

        Parameters
        ----------
        bibtex_str:
            A complete BibTeX entry string (e.g. ``@article{key, ...}``).

        Returns
        -------
        str
            The citation key extracted from the entry.

        Raises
        ------
        ValueError
            If no valid entry could be parsed from *bibtex_str*.
        """
        bibtex_str = bibtex_str.strip()
        key = self._extract_key(bibtex_str)
        if key is None:
            raise ValueError("Could not parse citation key from BibTeX entry.")

        # Avoid duplicates
        if self.get_entry(key) is not None:
            return key

        content = self.bib_path.read_text(encoding="utf-8")
        if not content.endswith("\n"):
            content += "\n"
        content += "\n" + bibtex_str + "\n"
        self.bib_path.write_text(content, encoding="utf-8")
        return key

    def remove_entry(self, key: str) -> bool:
        """Remove the entry with the given citation key.

        Returns ``True`` if the entry was found and removed.
        """
        content = self.bib_path.read_text(encoding="utf-8")
        entries = self._split_entries(content)
        new_entries: list[str] = []
        removed = False
        for entry in entries:
            entry_key = self._extract_key(entry)
            if entry_key == key:
                removed = True
            else:
                new_entries.append(entry)

        if removed:
            # Preserve any leading comments
            header = self._extract_header(content)
            self.bib_path.write_text(
                header + "\n".join(new_entries) + "\n",
                encoding="utf-8",
            )
        return removed

    def get_entry(self, key: str) -> dict[str, Any] | None:
        """Return a parsed dict for the entry with *key*, or ``None``."""
        entries = self.get_all_entries()
        for entry in entries:
            if entry.get("key") == key:
                return entry
        return None

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search entries by matching *query* against all field values."""
        query_lower = query.lower()
        results: list[dict[str, Any]] = []
        for entry in self.get_all_entries():
            for value in entry.values():
                if isinstance(value, str) and query_lower in value.lower():
                    results.append(entry)
                    break
        return results

    def get_all_entries(self) -> list[dict[str, Any]]:
        """Return all entries as a list of dicts."""
        if not self.bib_path.exists():
            return []
        content = self.bib_path.read_text(encoding="utf-8")

        if _HAS_BIBTEXPARSER:
            return self._parse_bibtexparser(content)
        return self._parse_regex(content)

    def get_count(self) -> int:
        """Return the number of entries in the bibliography."""
        if not self.bib_path.exists():
            return 0
        content = self.bib_path.read_text(encoding="utf-8")
        return len(self._split_entries(content))

    def validate(self) -> list[str]:
        """Validate the bibliography and return a list of issues.

        Checks for:
        - Duplicate keys
        - Missing required fields (title, author/editor, year)
        - Unbalanced braces
        """
        issues: list[str] = []
        content = self.bib_path.read_text(encoding="utf-8")
        entries = self.get_all_entries()

        # Check for duplicate keys
        keys: list[str] = []
        for entry in entries:
            k = entry.get("key", "")
            if k in keys:
                issues.append(f"Duplicate citation key: {k}")
            keys.append(k)

        # Check required fields
        for entry in entries:
            key = entry.get("key", "<unknown>")
            _entry_type = entry.get("type", "").lower()
            if not entry.get("title"):
                issues.append(f"[{key}] Missing 'title' field.")
            if not entry.get("author") and not entry.get("editor"):
                issues.append(f"[{key}] Missing 'author' or 'editor' field.")
            if not entry.get("year"):
                issues.append(f"[{key}] Missing 'year' field.")

        # Check brace balance
        open_braces = content.count("{")
        close_braces = content.count("}")
        if open_braces != close_braces:
            issues.append(f"Unbalanced braces: {open_braces} opening vs {close_braces} closing.")

        return issues

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_key(entry_text: str) -> str | None:
        """Extract the citation key from a BibTeX entry string."""
        m = re.search(r"@\w+\s*\{\s*([^,\s]+)", entry_text)
        return m.group(1) if m else None

    @staticmethod
    def _split_entries(content: str) -> list[str]:
        """Split raw bib content into individual entry strings."""
        entries: list[str] = []
        current: list[str] = []
        depth = 0
        in_entry = False

        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("@") and not stripped.startswith("@comment"):
                in_entry = True
                current = [line]
                depth = line.count("{") - line.count("}")
                if depth <= 0 and "{" in line:
                    entries.append("\n".join(current))
                    current = []
                    in_entry = False
                continue

            if in_entry:
                current.append(line)
                depth += line.count("{") - line.count("}")
                if depth <= 0:
                    entries.append("\n".join(current))
                    current = []
                    in_entry = False

        # Handle unclosed entry
        if current:
            entries.append("\n".join(current))

        return entries

    @staticmethod
    def _extract_header(content: str) -> str:
        """Extract leading comment lines from bib content."""
        header_lines: list[str] = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("%") or stripped == "":
                header_lines.append(line)
            else:
                break
        result = "\n".join(header_lines)
        if result and not result.endswith("\n"):
            result += "\n"
        return result

    @staticmethod
    def _parse_bibtexparser(content: str) -> list[dict[str, Any]]:
        """Parse using bibtexparser library."""
        try:
            bib_db = bibtexparser.parse(content)
        except AttributeError:
            # bibtexparser < 2.0 API
            parser = bibtexparser.bparser.BibTexParser(common_strings=True)
            bib_db = bibtexparser.loads(content, parser=parser)
            results: list[dict[str, Any]] = []
            for entry in bib_db.entries:
                parsed: dict[str, Any] = {"key": entry.get("ID", ""), "type": entry.get("ENTRYTYPE", "")}
                for k, v in entry.items():
                    if k not in ("ID", "ENTRYTYPE"):
                        parsed[k.lower()] = v
                results.append(parsed)
            return results

        # bibtexparser >= 2.0 API
        results = []
        for entry in bib_db.entries:
            parsed = {"key": entry.key, "type": entry.entry_type}
            for field in entry.fields:
                parsed[field.key.lower()] = field.value
            results.append(parsed)
        return results

    @staticmethod
    def _parse_regex(content: str) -> list[dict[str, Any]]:
        """Fallback regex-based BibTeX parser."""
        results: list[dict[str, Any]] = []

        # Match entry blocks
        entry_pattern = re.compile(
            r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.+?)\}",
            re.DOTALL,
        )

        for match in entry_pattern.finditer(content):
            entry_type = match.group(1).lower()
            key = match.group(2).strip()
            body = match.group(3)

            parsed: dict[str, Any] = {"key": key, "type": entry_type}

            # Extract fields
            field_pattern = re.compile(
                r"(\w+)\s*=\s*(?:\{((?:[^{}]|\{[^{}]*\})*)\}|\"([^\"]*)\"|(\d+))",
            )
            for fm in field_pattern.finditer(body):
                field_name = fm.group(1).lower()
                field_value = fm.group(2) or fm.group(3) or fm.group(4) or ""
                parsed[field_name] = field_value.strip()

            results.append(parsed)

        return results
