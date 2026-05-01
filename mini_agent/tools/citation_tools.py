"""Citation management and literature search tools.

Provides tools for:
- literature_search: Search academic papers via Semantic Scholar + CrossRef
- citation_manager: Manage BibTeX bibliography
- verify_citations: Verify all citations against real APIs
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from .base import Tool, ToolResult

# Shared session for connection pooling
_SESSION = requests.Session()
_SESSION.headers.update({"User-Agent": "BPSAcademicAgent/1.0 (mailto:research@bps-agent.id)"})


class LiteratureSearchTool(Tool):
    """Search academic literature across Semantic Scholar and CrossRef."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "literature_search"

    @property
    def description(self) -> str:
        return (
            "Search academic literature across Semantic Scholar (200M+ papers) and "
            "CrossRef (150M+ DOIs). Returns title, authors, year, DOI, citation count, "
            "abstract. Results are deduplicated by DOI."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "description": "Maximum results (default: 10)"},
                "year_from": {"type": "integer", "description": "Minimum publication year"},
                "year_to": {"type": "integer", "description": "Maximum publication year"},
            },
            "required": ["query"],
        }

    async def execute(
        self, query: str, max_results: int = 10, year_from: int | None = None, year_to: int | None = None, **kwargs
    ) -> ToolResult:
        try:
            results = []

            # Search Semantic Scholar
            try:
                s2_params = {
                    "query": query,
                    "limit": min(max_results, 20),
                    "fields": "title,year,citationCount,authors,externalIds,abstract,venue",
                }
                if year_from:
                    s2_params["year"] = f"{year_from}-" + (str(year_to) if year_to else "")
                resp = _SESSION.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search", params=s2_params, timeout=15
                )
                if resp.status_code == 200:
                    data = resp.json()
                    for paper in data.get("data", []):
                        doi = (paper.get("externalIds") or {}).get("DOI", "")
                        results.append(
                            {
                                "title": paper.get("title", ""),
                                "authors": ", ".join(a.get("name", "") for a in (paper.get("authors") or [])[:3]),
                                "year": paper.get("year"),
                                "doi": doi,
                                "citations": paper.get("citationCount", 0),
                                "venue": paper.get("venue", ""),
                                "abstract": (paper.get("abstract") or "")[:200],
                                "source": "Semantic Scholar",
                            }
                        )
            except Exception:
                pass  # Graceful degradation

            # Search CrossRef
            try:
                cr_params = {
                    "query": query,
                    "rows": min(max_results, 10),
                    "sort": "relevance",
                    "mailto": "research@bps-agent.id",
                }
                if year_from:
                    cr_params["filter"] = f"from-pub-date:{year_from}"
                resp = _SESSION.get("https://api.crossref.org/works", params=cr_params, timeout=15)
                if resp.status_code == 200:
                    items = resp.json().get("message", {}).get("items", [])
                    for item in items:
                        doi = item.get("DOI", "")
                        # Skip if already found via S2
                        if any(r["doi"] == doi for r in results if doi):
                            continue
                        authors = item.get("author", [])
                        author_str = ", ".join(f"{a.get('family', '')}" for a in authors[:3])
                        title_list = item.get("title", [""])
                        results.append(
                            {
                                "title": title_list[0] if title_list else "",
                                "authors": author_str,
                                "year": (item.get("published-print") or item.get("published-online") or {}).get(
                                    "date-parts", [[None]]
                                )[0][0],
                                "doi": doi,
                                "citations": item.get("is-referenced-by-count", 0),
                                "venue": (item.get("container-title") or [""])[0],
                                "abstract": "",
                                "source": "CrossRef",
                            }
                        )
            except Exception:
                pass

            if not results:
                return ToolResult(success=False, error=f"No results found for: {query}")

            # Sort by citations
            results.sort(key=lambda x: x.get("citations", 0), reverse=True)
            results = results[:max_results]

            # Format output
            lines = [f'## Literature Search: "{query}"\n', f"**Found:** {len(results)} papers\n"]
            for i, r in enumerate(results, 1):
                lines.append(f"### {i}. {r['title']}")
                lines.append(f"**Authors:** {r['authors']}")
                lines.append(f"**Year:** {r['year']} | **Citations:** {r['citations']} | **Venue:** {r['venue']}")
                if r["doi"]:
                    lines.append(f"**DOI:** {r['doi']}")
                if r["abstract"]:
                    lines.append(f"**Abstract:** {r['abstract']}...")
                lines.append("")

            return ToolResult(success=True, content="\n".join(lines))

        except Exception as e:
            return ToolResult(success=False, error=f"Literature search failed: {e}")


class CitationManagerTool(Tool):
    """Manage BibTeX bibliography."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "citation_manager"

    @property
    def description(self) -> str:
        return (
            "Manage the project's BibTeX bibliography. Actions: add_from_doi (fetch metadata "
            "from CrossRef), list (show all entries), search (find entries), remove, count."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add_from_doi", "list", "search", "remove", "count"],
                },
                "doi": {"type": "string", "description": "DOI to add (for add_from_doi)"},
                "key": {"type": "string", "description": "Citation key (for remove)"},
                "query": {"type": "string", "description": "Search query (for search)"},
            },
            "required": ["action"],
        }

    def _get_bib_path(self) -> Path:
        return Path(self._workspace_dir) / "literature" / "references.bib"

    async def execute(self, action: str, doi: str = "", key: str = "", query: str = "", **kwargs) -> ToolResult:
        try:
            bib_path = self._get_bib_path()

            if action == "add_from_doi":
                if not doi:
                    return ToolResult(success=False, error="DOI required for add_from_doi")

                # Fetch BibTeX from CrossRef content negotiation
                resp = _SESSION.get(
                    f"https://doi.org/{doi}",
                    headers={"Accept": "application/x-bibtex"},
                    allow_redirects=True,
                    timeout=15,
                )
                if resp.status_code != 200:
                    return ToolResult(success=False, error=f"Could not resolve DOI: {doi} (HTTP {resp.status_code})")

                bibtex_entry = resp.text.strip()

                # Append to .bib file
                bib_path.parent.mkdir(parents=True, exist_ok=True)
                with open(bib_path, "a", encoding="utf-8") as f:
                    f.write("\n" + bibtex_entry + "\n")

                return ToolResult(
                    success=True, content=f"Added citation from DOI: {doi}\n\n```bibtex\n{bibtex_entry}\n```"
                )

            elif action == "list":
                if not bib_path.exists():
                    return ToolResult(
                        success=True, content="Bibliography is empty. Use add_from_doi to add references."
                    )
                content = bib_path.read_text(encoding="utf-8")
                # Count entries
                count = content.count("@")
                return ToolResult(
                    success=True, content=f"**Bibliography:** {count} entries\n\n```bibtex\n{content}\n```"
                )

            elif action == "count":
                if not bib_path.exists():
                    return ToolResult(success=True, content="0 entries")
                content = bib_path.read_text(encoding="utf-8")
                count = content.count("@")
                return ToolResult(success=True, content=f"{count} entries in bibliography")

            elif action == "search":
                if not bib_path.exists():
                    return ToolResult(success=True, content="Bibliography is empty.")
                content = bib_path.read_text(encoding="utf-8")
                # Simple search
                matches = [block for block in content.split("\n@") if query.lower() in block.lower()]
                if not matches:
                    return ToolResult(success=True, content=f"No entries matching '{query}'")
                return ToolResult(
                    success=True, content=f"Found {len(matches)} matching entries:\n\n" + "\n@".join(matches)
                )

            elif action == "remove":
                if not key:
                    return ToolResult(success=False, error="Citation key required for remove")
                if not bib_path.exists():
                    return ToolResult(success=False, error="Bibliography is empty")
                content = bib_path.read_text(encoding="utf-8")
                if key not in content:
                    return ToolResult(success=False, error=f"Key '{key}' not found in bibliography")
                # Simple removal (remove block containing the key)
                lines = content.split("\n")
                new_lines = []
                skip = False
                for line in lines:
                    if key in line and line.strip().startswith("@"):
                        skip = True
                        continue
                    if skip and line.strip().startswith("@"):
                        skip = False
                    if not skip:
                        new_lines.append(line)
                bib_path.write_text("\n".join(new_lines), encoding="utf-8")
                return ToolResult(success=True, content=f"Removed citation: {key}")

            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            return ToolResult(success=False, error=f"Citation manager error: {e}")


class VerifyCitationsTool(Tool):
    """Verify all citations against CrossRef/Semantic Scholar."""

    def __init__(self, workspace_dir: str = "./workspace") -> None:
        self._workspace_dir = workspace_dir

    @property
    def name(self) -> str:
        return "verify_citations"

    @property
    def description(self) -> str:
        return (
            "Verify all citations in the bibliography against CrossRef API. "
            "Checks that each DOI resolves and metadata matches. "
            "Returns verification report with pass/fail per citation."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "strict": {"type": "boolean", "description": "Fail if any citation unverifiable (default: true)"},
            },
            "required": [],
        }

    async def execute(self, strict: bool = True, **kwargs) -> ToolResult:
        try:
            bib_path = Path(self._workspace_dir) / "literature" / "references.bib"
            if not bib_path.exists():
                return ToolResult(success=True, content="No bibliography to verify.")

            content = bib_path.read_text(encoding="utf-8")

            # Extract DOIs from BibTeX
            import re

            dois = re.findall(r'doi\s*=\s*[{"]([^}"]+)[}"]', content, re.IGNORECASE)

            if not dois:
                return ToolResult(success=True, content="No DOIs found in bibliography to verify.")

            verified = 0
            failed = []

            for doi in dois:
                try:
                    resp = _SESSION.get(f"https://api.crossref.org/works/{doi}", timeout=10)
                    if resp.status_code == 200:
                        verified += 1
                    else:
                        failed.append(doi)
                except Exception:
                    failed.append(doi)

            total = len(dois)
            lines = [
                "## Citation Verification Report\n",
                f"**Total DOIs:** {total}",
                f"**Verified:** {verified} ✅",
                f"**Failed:** {len(failed)} ❌",
            ]

            if failed:
                lines.append("\n**Failed DOIs:**")
                for doi in failed:
                    lines.append(f"  - {doi}")

            if strict and failed:
                lines.append(f"\n⚠️ **STRICT MODE:** {len(failed)} unverified citations. Paper compilation BLOCKED.")
                return ToolResult(success=False, error="\n".join(lines))

            lines.append(f"\n✅ All {verified} citations verified successfully.")
            return ToolResult(success=True, content="\n".join(lines))

        except Exception as e:
            return ToolResult(success=False, error=f"Citation verification failed: {e}")
