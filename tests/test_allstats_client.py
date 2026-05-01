"""Tests for mini_agent/allstats_client.py — Playwright BPS search client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_agent.allstats_client import AllStatsClient, AllStatsResult, AllStatsSearchResponse


class TestAllStatsResult:
    """Test AllStatsResult dataclass."""

    def test_creation(self):
        result = AllStatsResult(
            title="Test Title",
            url="https://example.com",
            snippet="Test snippet",
            content_type="table",
        )
        assert result.title == "Test Title"
        assert result.url == "https://example.com"
        assert result.snippet == "Test snippet"
        assert result.content_type == "table"
        assert result.source == "allstats"
        assert result.metadata == {}

    def test_defaults(self):
        result = AllStatsResult(
            title="T", url="U", snippet="S", content_type="C"
        )
        assert result.domain_name == ""
        assert result.domain_code == ""
        assert result.year == ""


class TestAllStatsSearchResponse:
    """Test AllStatsSearchResponse dataclass."""

    def test_creation(self):
        response = AllStatsSearchResponse(
            keyword="inflasi",
            content_type="all",
            page=1,
            total_results=100,
            per_page=10,
            results=[],
            has_next=True,
            has_prev=False,
            search_url="https://example.com/search",
        )
        assert response.keyword == "inflasi"
        assert response.total_results == 100
        assert response.has_next is True
        assert response.has_prev is False


class TestAllStatsClient:
    """Test AllStatsClient methods."""

    def test_init_defaults(self):
        client = AllStatsClient()
        assert client.headless is True
        assert client.timeout == 30
        assert client._search_delay == AllStatsClient.DEFAULT_SEARCH_DELAY

    def test_init_custom(self):
        client = AllStatsClient(headless=False, timeout=60, search_delay=5.0)
        assert client.headless is False
        assert client.timeout == 60
        assert client._search_delay == 5.0

    def test_build_url(self):
        client = AllStatsClient()
        url = client._build_url("data inflasi", domain="5300", content="table", page=2, sort="relevansi")
        assert "mfd=5300" in url
        assert "q=data%20inflasi" in url
        assert "content=table" in url
        assert "page=2" in url
        assert "sort=relevansi" in url
        assert url.startswith(AllStatsClient.BASE_URL)

    def test_build_url_default_params(self):
        client = AllStatsClient()
        url = client._build_url("test")
        assert "mfd=0000" in url
        assert "content=all" in url
        assert "page=1" in url
        assert "sort=terbaru" in url

    def test_browser_args(self):
        args = AllStatsClient._browser_args()
        assert isinstance(args, list)
        assert "--no-sandbox" in args
        assert "--disable-blink-features=AutomationControlled" in args

    def test_content_types(self):
        assert "all" in AllStatsClient.CONTENT_TYPES
        assert "publication" in AllStatsClient.CONTENT_TYPES
        assert "table" in AllStatsClient.CONTENT_TYPES

    def test_sort_options(self):
        assert "relevansi" in AllStatsClient.SORT_OPTIONS
        assert "terbaru" in AllStatsClient.SORT_OPTIONS
        assert "terlama" in AllStatsClient.SORT_OPTIONS

    @pytest.mark.asyncio
    async def test_close_no_browser(self):
        """Close when no browser is open should not raise."""
        client = AllStatsClient()
        await client.close()

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with AllStatsClient() as client:
            assert client is not None

    @pytest.mark.asyncio
    async def test_close_popup_no_page(self):
        """Test _close_popup when page has no popup."""
        client = AllStatsClient()
        client._page = MagicMock()
        client._page.query_selector = AsyncMock(return_value=None)
        client._page.keyboard = MagicMock()
        client._page.keyboard.press = AsyncMock()

        result = await client._close_popup()
        assert result is False

    @pytest.mark.asyncio
    async def test_close_popup_found(self):
        """Test _close_popup when popup is found."""
        client = AllStatsClient()
        client._page = MagicMock()

        mock_popup = MagicMock()
        mock_popup.click = AsyncMock()

        # First selector finds the popup
        client._page.query_selector = AsyncMock(return_value=mock_popup)

        result = await client._close_popup()
        assert result is True

    @pytest.mark.asyncio
    async def test_search_with_mocked_browser(self):
        """Test search with fully mocked browser."""
        client = AllStatsClient(search_delay=0)
        client._last_search_time = 0

        # Mock browser setup
        mock_page = MagicMock()
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Results</html>")
        mock_page.title = AsyncMock(return_value="Search Results")
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.evaluate = AsyncMock(return_value=[
            {
                "title": "Test Result",
                "url": "https://bps.go.id/test",
                "snippet": "Test snippet",
                "content_type": "table",
                "domain_name": "NTT",
                "domain_code": "5300",
                "year": "2024",
            }
        ])

        client._page = mock_page
        client._browser = MagicMock()
        client._context = MagicMock()

        with patch.object(client, "_ensure_browser", new=AsyncMock()):
            response = await client.search("inflasi", domain="5300")

        assert isinstance(response, AllStatsSearchResponse)
        assert response.keyword == "inflasi"
        assert len(response.results) == 1
        assert response.results[0].title == "Test Result"

    @pytest.mark.asyncio
    async def test_get_data_page_mocked(self):
        """Test get_data_page with mocked browser."""
        client = AllStatsClient()

        mock_page = MagicMock()
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html><body>Data</body></html>")
        mock_page.title = AsyncMock(return_value="Data Page")
        mock_page.evaluate = AsyncMock(return_value="Data content text")
        mock_page.query_selector_all = AsyncMock(return_value=[])
        mock_page.query_selector = AsyncMock(return_value=None)
        mock_page.keyboard = MagicMock()
        mock_page.keyboard.press = AsyncMock()

        client._page = mock_page
        client._browser = MagicMock()
        client._context = MagicMock()

        with patch.object(client, "_ensure_browser", new=AsyncMock()):
            result = await client.get_data_page("https://bps.go.id/test")

        assert result["title"] == "Data Page"
        assert "text" in result

    @pytest.mark.asyncio
    async def test_get_data_page_error(self):
        """Test get_data_page when navigation fails."""
        client = AllStatsClient()

        mock_page = MagicMock()
        mock_page.goto = AsyncMock(side_effect=Exception("Navigation failed"))

        client._page = mock_page
        client._browser = MagicMock()
        client._context = MagicMock()

        with patch.object(client, "_ensure_browser", new=AsyncMock()):
            result = await client.get_data_page("https://bps.go.id/test")

        assert "error" in result
