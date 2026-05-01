"""Citation verifier for academic papers.

Verifies that citations in a bibliography are valid by checking DOIs against
CrossRef and ensuring consistency between in-text citations and the ``.bib``
file.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

try:
    import requests as _requests

    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False


class VerificationDetail(BaseModel):
    """Detail record for a single citation verification."""

    key: str
    doi: str = ""
    verified: bool = False
    error: str = ""


class VerificationReport(BaseModel):
    """Aggregated citation verification report."""

    total: int = 0
    verified: int = 0
    failed: int = 0
    missing_dois: list[str] = Field(default_factory=list)
    details: list[VerificationDetail] = Field(default_factory=list)


class CitationVerifier:
    """Verify citations in a BibTeX bibliography.

    Parameters
    ----------
    bib_path:
        Path to the ``.bib`` file.
    """

    def __init__(self, bib_path: str | Path) -> None:
        self.bib_path = Path(bib_path)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def verify_all(self) -> VerificationReport:
        """Verify every entry in the bibliography.

        For each entry that has a DOI, checks that the DOI resolves via
        CrossRef.  Entries without DOIs are recorded in *missing_dois*.

        Returns
        -------
        VerificationReport
        """
        entries = self._parse_entries()
        report = VerificationReport(total=len(entries))

        for entry in entries:
            key = entry.get("key", "")
            doi = entry.get("doi", "")

            if not doi:
                report.missing_dois.append(key)
                report.details.append(VerificationDetail(key=key, doi="", verified=False, error="No DOI"))
                continue

            ok = self.verify_doi(doi)
            detail = VerificationDetail(
                key=key,
                doi=doi,
                verified=ok,
                error="" if ok else "DOI did not resolve",
            )
            report.details.append(detail)
            if ok:
                report.verified += 1
            else:
                report.failed += 1

        return report

    def verify_doi(self, doi: str) -> bool:
        """Check whether a DOI resolves via CrossRef.

        Returns ``True`` if the DOI returns HTTP 200 from CrossRef.
        Returns ``False`` if the request fails or ``requests`` is not
        installed.
        """
        if not _HAS_REQUESTS:
            return False

        doi = doi.strip()
        if not doi:
            return False

        try:
            resp = _requests.get(
                f"https://api.crossref.org/works/{doi}",
                timeout=10,
                headers={"User-Agent": "BPSAcademicAgent/1.0"},
            )
            return resp.status_code == 200
        except Exception:
            return False

    def check_citation_consistency(
        self,
        tex_content: str,
        bib_content: str | None = None,
    ) -> list[str]:
        r"""Check that every ``\cite{key}`` in *tex_content* has a matching bib entry.

        Parameters
        ----------
        tex_content:
            LaTeX source text containing ``\cite{}`` commands.
        bib_content:
            Raw ``.bib`` file content.  If *None*, reads from
            :attr:`bib_path`.

        Returns
        -------
        list[str]
            List of issue descriptions (empty means consistent).
        """
        if bib_content is None:
            if self.bib_path.exists():
                bib_content = self.bib_path.read_text(encoding="utf-8")
            else:
                return ["Bibliography file not found."]

        # Extract cited keys from tex
        cited_keys: set[str] = set()
        for match in re.finditer(r"\\cite[tp]?\{([^}]+)\}", tex_content):
            for key in match.group(1).split(","):
                cited_keys.add(key.strip())

        # Extract defined keys from bib
        defined_keys: set[str] = set()
        for match in re.finditer(r"@\w+\s*\{\s*([^,\s]+)", bib_content):
            defined_keys.add(match.group(1).strip())

        issues: list[str] = []

        # Keys cited but not in bib
        undefined = cited_keys - defined_keys
        for key in sorted(undefined):
            issues.append(f"Citation '{key}' used in text but not defined in bibliography.")

        # Keys in bib but never cited
        uncited = defined_keys - cited_keys
        for key in sorted(uncited):
            issues.append(f"Entry '{key}' in bibliography but never cited in text.")

        return issues

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _parse_entries(self) -> list[dict[str, Any]]:
        """Parse bib file into list of dicts with at least 'key' and 'doi'."""
        if not self.bib_path.exists():
            return []

        content = self.bib_path.read_text(encoding="utf-8")
        entries: list[dict[str, Any]] = []

        # Split into entry blocks
        entry_pattern = re.compile(
            r"@(\w+)\s*\{\s*([^,\s]+)\s*,(.+?)\n\s*\}",
            re.DOTALL,
        )

        for match in entry_pattern.finditer(content):
            entry: dict[str, Any] = {
                "type": match.group(1).lower(),
                "key": match.group(2).strip(),
            }
            body = match.group(3)

            # Extract DOI field
            doi_match = re.search(
                r"doi\s*=\s*[{\"]([^}\"]+)[}\"]",
                body,
                re.IGNORECASE,
            )
            if doi_match:
                entry["doi"] = doi_match.group(1).strip()
            else:
                entry["doi"] = ""

            entries.append(entry)

        return entries
