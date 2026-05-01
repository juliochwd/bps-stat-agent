"""Comprehensive coverage tests for mini_agent/allstats_client.py.

Tests AllStatsClient, AllStatsResult, AllStatsSearchResponse with mocked Playwright.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_agent.allstats_client import (
    AllStatsClient,
    AllStatsResult,
    AllStatsSearchResponse,
)


# ===========================================================================
# AllStatsResult tests
# ===========================================================================


class TestAllStatsResult:
    """Test AllStatsResult dataclass."""

    def test_creation(self):
        result = AllStatsResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            content_type="table",
            domain_name="NTT",
            domain_code="5300",
            year="2024",
        )
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.source == "allstats"

    def test_defaults(self):
        result = AllStatsResult(
            title="Title",
            url="",
            snippet="",
            content_type="",
        )
        assert result.domain_name == ""
        assert result.domain_code == ""
        assert result.year == ""
        assert result.metadata == {}


# ===========================================================================
# AllStatsSearchResponse tests
# ===========================================================================


class TestAllStatsSearchResponse:
    """Test AllStatsSearchResponse dataclass."""

    def test_creation(self):
        results = [
            AllStatsResult(title="R1", url="u1", snippet="s1", content_type="table"),
            AllStatsResult(title="R2", url="u2", snippet="s2", content_type="publication"),
        ]
        response = AllStatsSearchResponse(
            keyword="inflasi",
            content_type="all",
            page=1,
            total_results=100,
            per_page=10,
            results=results,
            has_next=True,
            has_prev=False,
            search_url="https://example.com/search?q=inflasi",
        )
        assert response.keyword == "inflasi"
        assert len(response.results) == 2
        assert response.has_next is True
        assert response.has_prev is False


# ===========================================================================
# AllStatsClient tests
# ===========================================================================


class TestAllStatsClient:
    """Test AllStatsClient with mocked Playwright."""

    def test_init_defaults(self):
        client = AllStatsClient()
        assert client.headless is True
        assert client.timeout == 30
        assert client._browser is None

    def test_init_custom(self):
        client = AllStatsClient(headless=False, timeout=60, search_delay=5)
        assert client.headless is False
        assert client.timeout == 60
        assert client._search_delay == 5

    def test_build_url(self):
        client = AllStatsClient()
        url = client._build_url("inflasi", domain="5300", content="table", page=2, sort="relevansi")
        assert "mfd=5300" in url
        assert "q=inflasi" in url
        assert "content=table" in url
        assert "page=2" in url
        assert "sort=relevansi" in url

    def test_build_url_encodes_spaces(self):
        client = AllStatsClient()
        url = client._build_url("data inflasi", domain="0000")
        assert "data%20inflasi" in url or "data+inflasi" in url

    def test_browser_args(self):
        args = AllStatsClient._browser_args()
        assert isinstance(args, list)
        assert "--no-sandbox" in args
        assert "--disable-blink-features=AutomationControlled" in args

    def test_content_types(self):
        assert "all" in AllStatsClient.CONTENT_TYPES
        assert "table" in AllStatsClient.CONTENT_TYPES
        assert "publication" in AllStatsClient.CONTENT_TYPES

    def test_sort_options(self):
        assert "terbaru" in AllStatsClient.SORT_OPTIONS
        assert "relevansi" in AllStatsClient.SORT_OPTIONS

    @pytest.mark.asyncio
    async def test_close_no_browser(self):
        client = AllStatsClient()
        await client.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_context_manager(self):
        client = AllStatsClient()
        async with client as c:
            assert c is client
        # After exit, should be cleaned up

    @pytest.mark.asyncio
    async def test_search_mocked(self):
        """Test search with fully mocked browser."""
        client = AllStatsClient(search_delay=0)

        # Mock page
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html><body>Results</body></html>")
        mock_page.title = AsyncMock(return_value="Search Results")
        mock_page.evaluate = AsyncMock(return_value=[
            {
                "title": "Inflasi NTT 2024",
                "url": "https://ntt.bps.go.id/table/1501",
                "snippet": "Data inflasi",
                "content_type": "table",
                "domain_name": "NTT",
                "domain_code": "5300",
                "year": "2024",
            }
        ])
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.set_default_timeout = MagicMock()

        # Mock context
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.add_init_script = AsyncMock()
        mock_context.close = AsyncMock()

        # Mock browser
        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        # Mock playwright
        mock_pw = AsyncMock()
        mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_pw.stop = AsyncMock()

        with patch("mini_agent.allstats_client.async_playwright") as mock_async_pw:
            mock_async_pw.return_value.start = AsyncMock(return_value=mock_pw)
            # Directly set internal state
            client._playwright = mock_pw
            client._browser = mock_browser
            client._context = mock_context
            client._page = mock_page

            response = await client.search("inflasi", domain="5300")
            assert len(response.results) == 1
            assert response.results[0].title == "Inflasi NTT 2024"
            assert response.keyword == "inflasi"

    @pytest.mark.asyncio
    async def test_close_popup_mocked(self):
        """Test _close_popup with mocked page."""
        client = AllStatsClient()

        mock_page = AsyncMock()
        mock_popup = AsyncMock()
        mock_popup.click = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=mock_popup)
        mock_page.keyboard = AsyncMock()
        mock_page.keyboard.press = AsyncMock()

        client._page = mock_page
        result = await client._close_popup()
        assert result is True

    @pytest.mark.asyncio
    async def test_close_popup_none_found(self):
        """Test _close_popup when no popup exists."""
        client = AllStatsClient()

        mock_page = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.keyboard = AsyncMock()
        mock_page.keyboard.press = AsyncMock()

        client._page = mock_page
        result = await client._close_popup()
        assert result is False

    @pytest.mark.asyncio
    async def test_get_data_page_mocked(self):
        """Test get_data_page with mocked browser."""
        client = AllStatsClient()

        mock_table = AsyncMock()
        mock_row = AsyncMock()
        mock_cell = AsyncMock()
        mock_cell.inner_text = AsyncMock(return_value="Cell Value")
        mock_row.query_selector_all = AsyncMock(return_value=[mock_cell])
        mock_table.query_selector_all = AsyncMock(return_value=[mock_row])

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Page content</html>")
        mock_page.title = AsyncMock(return_value="Data Page")
        mock_page.evaluate = AsyncMock(return_value="Page text content")
        mock_page.query_selector_all = AsyncMock(return_value=[mock_table])
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.keyboard = AsyncMock()
        mock_page.keyboard.press = AsyncMock()
        mock_page.set_default_timeout = MagicMock()

        client._page = mock_page
        client._browser = AsyncMock()
        client._playwright = AsyncMock()
        client._context = AsyncMock()

        data = await client.get_data_page("https://example.com/table/1")
        assert data["title"] == "Data Page"
        assert "tables" in data
        assert len(data["tables"]) == 1

    @pytest.mark.asyncio
    async def test_get_data_page_error(self):
        """Test get_data_page handles errors."""
        client = AllStatsClient()

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=Exception("Navigation failed"))
        mock_page.set_default_timeout = MagicMock()
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.keyboard = AsyncMock()
        mock_page.keyboard.press = AsyncMock()

        client._page = mock_page
        client._browser = AsyncMock()
        client._playwright = AsyncMock()
        client._context = AsyncMock()

        data = await client.get_data_page("https://example.com/bad")
        assert "error" in data

    @pytest.mark.asyncio
    async def test_parse_results_error(self):
        """Test _parse_results handles evaluation errors."""
        client = AllStatsClient()

        mock_page = AsyncMock()
        mock_page.evaluate = AsyncMock(side_effect=Exception("JS error"))

        client._page = mock_page
        results = await client._parse_results()
        assert results == []
