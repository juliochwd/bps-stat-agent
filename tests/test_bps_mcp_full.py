"""Full coverage tests for mini_agent/bps_mcp_server.py.

Tests helper functions and MCP handler functions with mocked API clients.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from mini_agent.bps_mcp_server import (
    error_response,
    success_response,
    th_to_year,
    year_to_th,
    _extract_identifier_from_url,
)


# ===================================================================
# Helper functions
# ===================================================================

class TestYearToTh:
    def test_2024(self):
        assert year_to_th(2024) == 124

    def test_2017(self):
        assert year_to_th(2017) == 117

    def test_2000(self):
        assert year_to_th(2000) == 100

    def test_1990(self):
        assert year_to_th(1990) == 90

    def test_1950(self):
        assert year_to_th(1950) == 50


class TestThToYear:
    def test_124(self):
        assert th_to_year(124) == 2024

    def test_117(self):
        assert th_to_year(117) == 2017

    def test_100(self):
        assert th_to_year(100) == 2000

    def test_50(self):
        assert th_to_year(50) == 1950


class TestSuccessResponse:
    def test_basic(self):
        result = success_response({"key": "value"})
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["message"] == "OK"
        assert parsed["data"]["key"] == "value"

    def test_custom_message(self):
        result = success_response([1, 2, 3], message="Done")
        parsed = json.loads(result)
        assert parsed["message"] == "Done"
        assert parsed["data"] == [1, 2, 3]

    def test_none_data(self):
        result = success_response(None)
        parsed = json.loads(result)
        assert parsed["data"] is None

    def test_string_data(self):
        result = success_response("hello")
        parsed = json.loads(result)
        assert parsed["data"] == "hello"

    def test_nested_data(self):
        result = success_response({"a": {"b": [1, 2]}})
        parsed = json.loads(result)
        assert parsed["data"]["a"]["b"] == [1, 2]


class TestErrorResponse:
    def test_basic(self):
        result = error_response("Something went wrong")
        parsed = json.loads(result)
        assert parsed["success"] is False
        assert parsed["error"] == "Something went wrong"

    def test_with_details(self):
        result = error_response("Error", details={"code": 404})
        parsed = json.loads(result)
        assert parsed["details"]["code"] == 404

    def test_no_details(self):
        result = error_response("Error")
        parsed = json.loads(result)
        assert parsed["details"] is None

    def test_unicode(self):
        result = error_response("Data tidak ditemukan")
        parsed = json.loads(result)
        assert "tidak" in parsed["error"]


class TestExtractIdentifierFromUrl:
    def test_statistics_table_pattern(self):
        url = "https://ntt.bps.go.id/statistics-table/2/123/"
        result = _extract_identifier_from_url(url, "statistics-table")
        assert result == "123"

    def test_query_param_id(self):
        url = "https://bps.go.id/page?id=456"
        result = _extract_identifier_from_url(url, "page")
        assert result == "456"

    def test_query_param_table_id(self):
        url = "https://bps.go.id/data?table_id=789"
        result = _extract_identifier_from_url(url, "data")
        assert result == "789"

    def test_simple_pattern(self):
        url = "https://bps.go.id/statistics-table/999"
        result = _extract_identifier_from_url(url, "statistics-table")
        assert result == "999"

    def test_no_match(self):
        url = "https://bps.go.id/about"
        result = _extract_identifier_from_url(url, "statistics-table")
        assert result is None

    def test_query_param_pub_id(self):
        url = "https://bps.go.id/publication?pub_id=321"
        result = _extract_identifier_from_url(url, "publication")
        assert result == "321"

    def test_query_param_brs_id(self):
        url = "https://bps.go.id/pressrelease?brs_id=555"
        result = _extract_identifier_from_url(url, "pressrelease")
        assert result == "555"


# ===================================================================
# MCP Handler functions - using direct mocking of the handler internals
# ===================================================================

class TestBpsYearToTh:
    @pytest.mark.asyncio
    async def test_basic(self):
        from mini_agent.bps_mcp_server import bps_year_to_th
        result = await bps_year_to_th(2024)
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["th"] == 124

    @pytest.mark.asyncio
    async def test_2020(self):
        from mini_agent.bps_mcp_server import bps_year_to_th
        result = await bps_year_to_th(2020)
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["th"] == 120


class TestBpsHandlersWithMockedClient:
    """Test BPS handler functions by mocking get_api_client and _run_sync."""

    @pytest.fixture
    def mock_api(self):
        """Fixture that mocks get_api_client and _run_sync."""
        mock_client = MagicMock()

        async def mock_run_sync(func, *args, **kwargs):
            return func(*args, **kwargs)

        with patch("mini_agent.bps_mcp_server.get_api_client", return_value=mock_client):
            with patch("mini_agent.bps_mcp_server._run_sync", side_effect=mock_run_sync):
                yield mock_client

    @pytest.mark.asyncio
    async def test_list_domains(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_domains
        mock_api.get_domains.return_value = [{"domain_id": "5300", "domain_name": "NTT"}]
        result = await bps_list_domains()
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_provinces(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_provinces
        mock_api.get_domains.return_value = [{"prov_id": "53", "prov_name": "NTT"}]
        result = await bps_list_provinces()
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_subjects(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_subjects
        mock_api.get_subjects.return_value = [{"sub_id": 1, "title": "Inflasi"}]
        result = await bps_list_subjects(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_variables(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_variables
        mock_api.get_variables.return_value = [{"var_id": 1, "title": "Inflasi"}]
        result = await bps_get_variables(subject=1, domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_search(self, mock_api):
        from mini_agent.bps_mcp_server import bps_search
        mock_api.search.return_value = {"data": [{"title": "Inflasi NTT"}]}
        result = await bps_search(keyword="inflasi", domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_data(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_data
        mock_api.get_data.return_value = {"data": {"var": 1, "values": []}}
        result = await bps_get_data(var=1, th=124, domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_press_releases(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_press_releases
        mock_api.get_press_releases.return_value = [{"title": "Press Release"}]
        result = await bps_get_press_releases(year=2024, domain="0000")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_publications(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_publications
        mock_api.get_publications.return_value = [{"title": "Publication"}]
        result = await bps_get_publications(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_indicators(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_indicators
        mock_api.get_indicators.return_value = [{"indicator": "GDP"}]
        result = await bps_get_indicators(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_subject_categories(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_subject_categories
        mock_api.get_subject_categories.return_value = [{"cat_id": 1}]
        result = await bps_list_subject_categories(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_units(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_units
        mock_api.get_units.return_value = [{"unit_id": 1}]
        result = await bps_list_units(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_infographics(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_infographics
        mock_api.get_infographics.return_value = [{"title": "Infographic"}]
        result = await bps_list_infographics(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_sdgs(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_sdgs
        mock_api.get_sdgs.return_value = [{"goal": "1"}]
        result = await bps_list_sdgs()
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_sdds(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_sdds
        mock_api.get_sdds.return_value = [{"category": "National Accounts"}]
        result = await bps_list_sdds()
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_handler_error(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_domains
        mock_api.get_domains.side_effect = Exception("API Error")
        result = await bps_list_domains()
        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "API Error" in parsed["error"]


class TestGetApiClient:
    def test_no_key_raises(self):
        from mini_agent.bps_mcp_server import get_api_client
        with patch("mini_agent.bps_mcp_server.DEFAULT_API_KEY", ""):
            with pytest.raises(ValueError):
                get_api_client(api_key="")

    def test_with_key(self):
        from mini_agent.bps_mcp_server import get_api_client
        with patch("mini_agent.bps_mcp_server._api_client_cache", {}):
            with patch("mini_agent.bps_mcp_server.BPSAPI") as mock_bps:
                mock_bps.return_value = MagicMock()
                client = get_api_client(api_key="test_key_123")
                assert client is not None

    def test_caching(self):
        from mini_agent.bps_mcp_server import get_api_client
        with patch("mini_agent.bps_mcp_server._api_client_cache", {}):
            with patch("mini_agent.bps_mcp_server.BPSAPI") as mock_bps:
                mock_bps.return_value = MagicMock()
                client1 = get_api_client(api_key="key1")
                client2 = get_api_client(api_key="key1")
                assert client1 is client2
                assert mock_bps.call_count == 1


class TestBpsHandlersExtended:
    """Test additional BPS handler functions."""

    @pytest.fixture
    def mock_api(self):
        mock_client = MagicMock()

        async def mock_run_sync(func, *args, **kwargs):
            return func(*args, **kwargs)

        with patch("mini_agent.bps_mcp_server.get_api_client", return_value=mock_client):
            with patch("mini_agent.bps_mcp_server._run_sync", side_effect=mock_run_sync):
                yield mock_client

    @pytest.mark.asyncio
    async def test_get_census_topics(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_census_topics
        mock_api.get_census_topics.return_value = [{"topic": "Population"}]
        result = await bps_get_census_topics(kegiatan="sp2020")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_census_areas(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_census_areas
        mock_api.get_census_areas.return_value = [{"area": "NTT"}]
        result = await bps_get_census_areas(kegiatan="sp2020")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_census_datasets(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_census_datasets
        mock_api.get_census_datasets.return_value = [{"dataset": "pop"}]
        result = await bps_get_census_datasets(kegiatan="sp2020", topik=1)
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_census_data(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_census_data
        mock_api.get_census_data.return_value = {"data": []}
        result = await bps_get_census_data(kegiatan="sp2020", wilayah_sensus=1, dataset=1)
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_simdasi_regencies(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_simdasi_regencies
        mock_api.get_simdasi_regencies.return_value = [{"name": "Kupang"}]
        result = await bps_get_simdasi_regencies(parent="53")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_simdasi_districts(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_simdasi_districts
        mock_api.get_simdasi_districts.return_value = [{"name": "Kelapa Lima"}]
        result = await bps_get_simdasi_districts(parent="5371")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_glossary(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_glossary
        mock_api.get_glossary.return_value = [{"term": "Inflasi"}]
        result = await bps_list_glossary()
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_news_detail(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_news_detail
        mock_api.get_news_detail.return_value = {"title": "News", "content": "..."}
        result = await bps_get_news_detail(news_id=1, domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_news_categories(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_news_categories
        mock_api.get_news_categories.return_value = [{"cat": "Economy"}]
        result = await bps_list_news_categories(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_decoded_data(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_decoded_data
        mock_api.get_decoded_data.return_value = {
            "status": "OK",
            "variable": {"label": "Inflasi", "unit": "%", "note": ""},
            "year": 2024,
            "data": [{"region_label": "Kupang", "value": 5.2}],
        }
        result = await bps_get_decoded_data(var=1, th=124, domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_periods(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_periods
        mock_api.get_periods.return_value = [{"period": "2024"}]
        result = await bps_list_periods(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_vertical_variables(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_vertical_variables
        mock_api.get_vertical_variables.return_value = [{"var": "age"}]
        result = await bps_list_vertical_variables(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_derived_variables(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_derived_variables
        mock_api.get_derived_variables.return_value = [{"var": "growth"}]
        result = await bps_list_derived_variables(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_derived_periods(self, mock_api):
        from mini_agent.bps_mcp_server import bps_list_derived_periods
        mock_api.get_derived_periods.return_value = [{"period": "Q1"}]
        result = await bps_list_derived_periods(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_infographic_detail(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_infographic_detail
        mock_api.get_infographic_detail.return_value = {"title": "Info"}
        result = await bps_get_infographic_detail(infographic_id=1, domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_glossary_detail(self, mock_api):
        from mini_agent.bps_mcp_server import bps_get_glossary_detail
        mock_api.get_glossary_detail.return_value = {"term": "GDP", "definition": "..."}
        result = await bps_get_glossary_detail(glossary_id=1)
        parsed = json.loads(result)
        assert parsed["success"] is True
