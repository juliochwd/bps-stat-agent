"""Full coverage tests for mini_agent/tools/citation_tools.py.

Covers LiteratureSearchTool, CitationManagerTool, VerifyCitationsTool.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock

import pytest

from mini_agent.tools.citation_tools import (
    CitationManagerTool,
    LiteratureSearchTool,
    VerifyCitationsTool,
)


# ===================================================================
# LiteratureSearchTool
# ===================================================================

class TestLiteratureSearchToolFull:
    @pytest.fixture
    def tool(self, tmp_path):
        return LiteratureSearchTool(workspace_dir=str(tmp_path))

    def test_name(self, tool):
        assert tool.name == "literature_search"

    def test_description(self, tool):
        assert "semantic scholar" in tool.description.lower() or "literature" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "query" in params["properties"]
        assert "query" in params["required"]

    @pytest.mark.asyncio
    async def test_search_success_s2(self, tool):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [
                {
                    "title": "Test Paper",
                    "year": 2023,
                    "citationCount": 10,
                    "authors": [{"name": "Author A"}, {"name": "Author B"}],
                    "externalIds": {"DOI": "10.1234/test"},
                    "abstract": "This is a test abstract",
                    "venue": "Test Journal",
                }
            ]
        }
        # CrossRef returns empty
        mock_resp_cr = MagicMock()
        mock_resp_cr.status_code = 200
        mock_resp_cr.json.return_value = {"message": {"items": []}}

        with patch("mini_agent.tools.citation_tools._SESSION") as mock_session:
            mock_session.get.side_effect = [mock_resp, mock_resp_cr]
            result = await tool.execute(query="machine learning")
            assert result.success is True
            assert "Test Paper" in result.content

    @pytest.mark.asyncio
    async def test_search_success_crossref(self, tool):
        # S2 fails, CrossRef succeeds
        mock_resp_s2 = MagicMock()
        mock_resp_s2.status_code = 429  # Rate limited

        mock_resp_cr = MagicMock()
        mock_resp_cr.status_code = 200
        mock_resp_cr.json.return_value = {
            "message": {
                "items": [
                    {
                        "title": ["CrossRef Paper"],
                        "author": [{"family": "Smith", "given": "John"}],
                        "DOI": "10.5678/cr",
                        "is-referenced-by-count": 5,
                        "container-title": ["CR Journal"],
                        "published-print": {"date-parts": [[2022]]},
                    }
                ]
            }
        }

        with patch("mini_agent.tools.citation_tools._SESSION") as mock_session:
            mock_session.get.side_effect = [mock_resp_s2, mock_resp_cr]
            result = await tool.execute(query="deep learning")
            assert result.success is True
            assert "CrossRef Paper" in result.content

    @pytest.mark.asyncio
    async def test_search_no_results(self, tool):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"data": []}

        mock_resp_cr = MagicMock()
        mock_resp_cr.status_code = 200
        mock_resp_cr.json.return_value = {"message": {"items": []}}

        with patch("mini_agent.tools.citation_tools._SESSION") as mock_session:
            mock_session.get.side_effect = [mock_resp, mock_resp_cr]
            result = await tool.execute(query="xyznonexistent123")
            assert result.success is False
            assert "No results" in result.error

    @pytest.mark.asyncio
    async def test_search_with_year_filter(self, tool):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "data": [
                {
                    "title": "Recent Paper",
                    "year": 2023,
                    "citationCount": 3,
                    "authors": [{"name": "Author"}],
                    "externalIds": {"DOI": "10.1234/recent"},
                    "abstract": "Abstract",
                    "venue": "Journal",
                }
            ]
        }
        mock_resp_cr = MagicMock()
        mock_resp_cr.status_code = 200
        mock_resp_cr.json.return_value = {"message": {"items": []}}

        with patch("mini_agent.tools.citation_tools._SESSION") as mock_session:
            mock_session.get.side_effect = [mock_resp, mock_resp_cr]
            result = await tool.execute(query="test", year_from=2020, year_to=2024)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_search_both_apis_fail(self, tool):
        with patch("mini_agent.tools.citation_tools._SESSION") as mock_session:
            mock_session.get.side_effect = Exception("Network error")
            result = await tool.execute(query="test")
            assert result.success is False


# ===================================================================
# CitationManagerTool
# ===================================================================

class TestCitationManagerToolFull:
    @pytest.fixture
    def tool(self, tmp_path):
        return CitationManagerTool(workspace_dir=str(tmp_path))

    @pytest.fixture
    def bib_file(self, tmp_path):
        bib_dir = tmp_path / "literature"
        bib_dir.mkdir()
        bib_path = bib_dir / "references.bib"
        bib_path.write_text(
            '@article{smith2023,\n  title={Test Paper},\n  author={Smith, John},\n  year={2023},\n  doi={10.1234/test}\n}\n\n'
            '@article{jones2022,\n  title={Another Paper},\n  author={Jones, Alice},\n  year={2022},\n  doi={10.5678/other}\n}\n'
        )
        return bib_path

    def test_name(self, tool):
        assert tool.name == "citation_manager"

    def test_description(self, tool):
        assert "bibtex" in tool.description.lower() or "bibliography" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "action" in params["properties"]
        assert "action" in params["required"]

    @pytest.mark.asyncio
    async def test_list_empty(self, tool):
        result = await tool.execute(action="list")
        assert result.success is True
        assert "empty" in result.content.lower()

    @pytest.mark.asyncio
    async def test_list_with_entries(self, tool, bib_file):
        result = await tool.execute(action="list")
        assert result.success is True
        assert "2 entries" in result.content

    @pytest.mark.asyncio
    async def test_count_empty(self, tool):
        result = await tool.execute(action="count")
        assert result.success is True
        assert "0" in result.content

    @pytest.mark.asyncio
    async def test_count_with_entries(self, tool, bib_file):
        result = await tool.execute(action="count")
        assert result.success is True
        assert "2" in result.content

    @pytest.mark.asyncio
    async def test_search_found(self, tool, bib_file):
        result = await tool.execute(action="search", query="Smith")
        assert result.success is True
        assert "Smith" in result.content

    @pytest.mark.asyncio
    async def test_search_not_found(self, tool, bib_file):
        result = await tool.execute(action="search", query="nonexistent_author")
        assert result.success is True
        assert "No entries" in result.content

    @pytest.mark.asyncio
    async def test_search_empty_bib(self, tool):
        result = await tool.execute(action="search", query="test")
        assert result.success is True
        assert "empty" in result.content.lower()

    @pytest.mark.asyncio
    async def test_remove_success(self, tool, bib_file):
        result = await tool.execute(action="remove", key="smith2023")
        assert result.success is True
        assert "Removed" in result.content

    @pytest.mark.asyncio
    async def test_remove_not_found(self, tool, bib_file):
        result = await tool.execute(action="remove", key="nonexistent_key")
        assert result.success is False
        assert "not found" in result.error.lower()

    @pytest.mark.asyncio
    async def test_remove_no_key(self, tool, bib_file):
        result = await tool.execute(action="remove")
        assert result.success is False
        assert "key" in result.error.lower()

    @pytest.mark.asyncio
    async def test_remove_empty_bib(self, tool):
        result = await tool.execute(action="remove", key="test")
        assert result.success is False

    @pytest.mark.asyncio
    async def test_add_from_doi_success(self, tool, tmp_path):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '@article{test2023,\n  title={Test},\n  author={Test Author},\n  year={2023}\n}'

        with patch("mini_agent.tools.citation_tools._SESSION") as mock_session:
            mock_session.get.return_value = mock_resp
            result = await tool.execute(action="add_from_doi", doi="10.1234/test")
            assert result.success is True
            assert "Added" in result.content

    @pytest.mark.asyncio
    async def test_add_from_doi_no_doi(self, tool):
        result = await tool.execute(action="add_from_doi")
        assert result.success is False
        assert "DOI" in result.error

    @pytest.mark.asyncio
    async def test_add_from_doi_failed(self, tool):
        mock_resp = MagicMock()
        mock_resp.status_code = 404

        with patch("mini_agent.tools.citation_tools._SESSION") as mock_session:
            mock_session.get.return_value = mock_resp
            result = await tool.execute(action="add_from_doi", doi="10.1234/invalid")
            assert result.success is False

    @pytest.mark.asyncio
    async def test_unknown_action(self, tool):
        result = await tool.execute(action="unknown_action")
        assert result.success is False
        assert "Unknown" in result.error


# ===================================================================
# VerifyCitationsTool
# ===================================================================

class TestVerifyCitationsToolFull:
    @pytest.fixture
    def tool(self, tmp_path):
        return VerifyCitationsTool(workspace_dir=str(tmp_path))

    @pytest.fixture
    def bib_file(self, tmp_path):
        bib_dir = tmp_path / "literature"
        bib_dir.mkdir()
        bib_path = bib_dir / "references.bib"
        bib_path.write_text(
            '@article{smith2023,\n  title={Test},\n  doi={10.1234/test}\n}\n\n'
            '@article{jones2022,\n  title={Other},\n  doi={10.5678/other}\n}\n'
        )
        return bib_path

    def test_name(self, tool):
        assert tool.name == "verify_citations"

    def test_description(self, tool):
        assert "verify" in tool.description.lower()

    def test_parameters(self, tool):
        params = tool.parameters
        assert "strict" in params["properties"]

    @pytest.mark.asyncio
    async def test_no_bib_file(self, tool):
        result = await tool.execute()
        assert result.success is True
        assert "No bibliography" in result.content

    @pytest.mark.asyncio
    async def test_no_dois(self, tool, tmp_path):
        bib_dir = tmp_path / "literature"
        bib_dir.mkdir(exist_ok=True)
        (bib_dir / "references.bib").write_text("@article{test,\n  title={No DOI}\n}\n")
        result = await tool.execute()
        assert result.success is True
        assert "No DOIs" in result.content

    @pytest.mark.asyncio
    async def test_all_verified(self, tool, bib_file):
        mock_resp = MagicMock()
        mock_resp.status_code = 200

        with patch("mini_agent.tools.citation_tools._SESSION") as mock_session:
            mock_session.get.return_value = mock_resp
            result = await tool.execute()
            assert result.success is True
            assert "verified" in result.content.lower()

    @pytest.mark.asyncio
    async def test_some_failed_strict(self, tool, bib_file):
        def side_effect(url, **kwargs):
            resp = MagicMock()
            if "10.1234" in url:
                resp.status_code = 200
            else:
                resp.status_code = 404
            return resp

        with patch("mini_agent.tools.citation_tools._SESSION") as mock_session:
            mock_session.get.side_effect = side_effect
            result = await tool.execute(strict=True)
            assert result.success is False
            assert "STRICT" in result.error or "Failed" in result.error

    @pytest.mark.asyncio
    async def test_some_failed_non_strict(self, tool, bib_file):
        def side_effect(url, **kwargs):
            resp = MagicMock()
            if "10.1234" in url:
                resp.status_code = 200
            else:
                resp.status_code = 404
            return resp

        with patch("mini_agent.tools.citation_tools._SESSION") as mock_session:
            mock_session.get.side_effect = side_effect
            result = await tool.execute(strict=False)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_network_error(self, tool, bib_file):
        with patch("mini_agent.tools.citation_tools._SESSION") as mock_session:
            mock_session.get.side_effect = Exception("Network error")
            result = await tool.execute(strict=True)
            assert result.success is False
