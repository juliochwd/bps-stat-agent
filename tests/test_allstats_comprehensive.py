"""Comprehensive tests for mini_agent/allstats_client.py.

Tests AllStatsClient with mocked Playwright.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_agent.allstats_client import AllStatsClient, AllStatsResult, AllStatsSearchResponse


class TestAllStatsClientInit:
    def test_init_defaults(self):
        client = AllStatsClient()
        assert client.headless is True
        assert client.timeout == 30
        assert client._browser is None
        assert client._page is None

    def test_init_custom(self):
        client = AllStatsClient(headless=False, timeout=60, search_delay=5.0)
        assert client.headless is False
        assert client.timeout == 60

    def test_build_url_default(self):
        client = AllStatsClient()
        url = client._build_url(keyword="inflasi")
        assert "inflasi" in url

    def test_build_url_with_content_type(self):
        client = AllStatsClient()
        url = client._build_url(keyword="inflasi", content="table")
        assert "inflasi" in url

    def test_build_url_with_page(self):
        client = AllStatsClient()
        url = client._build_url(keyword="inflasi", page=2)
        assert "inflasi" in url


class TestAllStatsClientSearch:
    @pytest.mark.asyncio
    async def test_search_no_browser(self):
        """Test search when browser fails to launch."""
        client = AllStatsClient()

        with patch.object(client, "_ensure_browser", new_callable=AsyncMock, side_effect=Exception("No browser")):
            with pytest.raises(Exception, match="No browser"):
                await client.search("inflasi")

    @pytest.mark.asyncio
    async def test_search_with_mock_browser(self):
        """Test search with fully mocked browser."""
        client = AllStatsClient()

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.query_selector = AsyncMock(return_value=None)

        client._page = mock_page
        client._browser = AsyncMock()

        with patch.object(client, "_ensure_browser", new_callable=AsyncMock):
            with patch.object(client, "_parse_results", new_callable=AsyncMock, return_value=[]):
                result = await client.search("inflasi")
                assert isinstance(result, AllStatsSearchResponse)
                assert result.keyword == "inflasi"

    @pytest.mark.asyncio
    async def test_search_with_results(self):
        """Test search returning results."""
        client = AllStatsClient()

        mock_results = [
            AllStatsResult(
                title="Inflasi NTT 2024",
                url="https://ntt.bps.go.id/table/1",
                snippet="Data inflasi",
                content_type="table",
                domain_name="NTT",
                domain_code="5300",
            ),
        ]

        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=None)

        client._page = mock_page
        client._browser = AsyncMock()

        with patch.object(client, "_ensure_browser", new_callable=AsyncMock):
            with patch.object(client, "_parse_results", new_callable=AsyncMock, return_value=mock_results):
                with patch.object(client, "_close_popup", new_callable=AsyncMock, return_value=False):
                    result = await client.search("inflasi")
                    assert len(result.results) == 1
                    assert result.results[0].title == "Inflasi NTT 2024"


class TestAllStatsClientGetDataPage:
    @pytest.mark.asyncio
    async def test_get_data_page_no_browser(self):
        """Test get_data_page when browser not available."""
        client = AllStatsClient()

        with patch.object(client, "_ensure_browser", new_callable=AsyncMock, side_effect=Exception("No browser")):
            with pytest.raises(Exception):
                await client.get_data_page("https://example.com/table")


class TestAllStatsClientClose:
    @pytest.mark.asyncio
    async def test_close_no_browser(self):
        """Test close when no browser is open."""
        client = AllStatsClient()
        await client.close()  # Should not raise

    @pytest.mark.asyncio
    async def test_close_with_browser(self):
        """Test close with active browser."""
        client = AllStatsClient()
        mock_browser = AsyncMock()
        mock_browser.close = AsyncMock()
        client._browser = mock_browser
        client._context = None
        client._playwright = None
        await client.close()
        mock_browser.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        client = AllStatsClient()
        client._browser = None

        with patch.object(client, "_ensure_browser", new_callable=AsyncMock):
            with patch.object(client, "close", new_callable=AsyncMock):
                async with client as c:
                    assert c is client


class TestAllStatsClientBrowserArgs:
    def test_browser_args(self):
        """Test browser arguments."""
        args = AllStatsClient._browser_args()
        assert isinstance(args, list)
        assert "--no-sandbox" in args


class TestAllStatsResultMetadata:
    def test_result_with_metadata(self):
        result = AllStatsResult(
            title="Test",
            url="http://example.com",
            snippet="Snippet",
            content_type="publication",
            domain_name="NTT",
            domain_code="5300",
            year="2024",
            metadata={"extra": "data"},
        )
        assert result.metadata == {"extra": "data"}
        assert result.year == "2024"
        assert result.domain_code == "5300"
