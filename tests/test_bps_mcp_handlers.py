"""Comprehensive tests for bps_mcp_server.py handler functions.

Tests the 60+ MCP tool handlers by mocking the BPS API client.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from mini_agent import bps_mcp_server
from mini_agent.bps_mcp_server import (
    _extract_identifier_from_url,
    error_response,
    get_api_client,
    success_response,
    th_to_year,
    year_to_th,
)


# ===================================================================
# Helper function tests
# ===================================================================

class TestHelperFunctions:
    def test_year_to_th(self):
        assert year_to_th(2024) == 124
        assert year_to_th(2017) == 117
        assert year_to_th(1900) == 0

    def test_th_to_year(self):
        assert th_to_year(124) == 2024
        assert th_to_year(117) == 2017
        assert th_to_year(0) == 1900

    def test_success_response(self):
        result = success_response({"key": "value"}, "Test message")
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["message"] == "Test message"
        assert parsed["data"]["key"] == "value"

    def test_error_response(self):
        result = error_response("Something failed", {"detail": "info"})
        parsed = json.loads(result)
        assert parsed["success"] is False
        assert parsed["error"] == "Something failed"
        assert parsed["details"]["detail"] == "info"

    def test_error_response_no_details(self):
        result = error_response("fail")
        parsed = json.loads(result)
        assert parsed["success"] is False
        assert parsed["details"] is None

    def test_get_api_client_no_key(self):
        with patch.dict("os.environ", {}, clear=True):
            with patch.object(bps_mcp_server, "DEFAULT_API_KEY", ""):
                with pytest.raises(ValueError, match="API key"):
                    get_api_client(None)

    def test_get_api_client_caches(self):
        bps_mcp_server._api_client_cache.clear()
        with patch("mini_agent.bps_mcp_server.BPSAPI") as mock_cls:
            mock_cls.return_value = MagicMock()
            c1 = get_api_client("test-key-123")
            c2 = get_api_client("test-key-123")
            assert c1 is c2
            mock_cls.assert_called_once_with("test-key-123")
        bps_mcp_server._api_client_cache.clear()

    def test_get_api_client_evicts_oldest(self):
        bps_mcp_server._api_client_cache.clear()
        with patch("mini_agent.bps_mcp_server.BPSAPI") as mock_cls:
            mock_cls.return_value = MagicMock()
            # Fill cache to max
            for i in range(bps_mcp_server._API_CLIENT_CACHE_MAX_SIZE):
                get_api_client(f"key-{i}")
            assert len(bps_mcp_server._api_client_cache) == bps_mcp_server._API_CLIENT_CACHE_MAX_SIZE
            # Adding one more should evict oldest
            get_api_client("new-key")
            assert "key-0" not in bps_mcp_server._api_client_cache
            assert "new-key" in bps_mcp_server._api_client_cache
        bps_mcp_server._api_client_cache.clear()

    def test_extract_identifier_from_url_pattern1(self):
        url = "https://ntt.bps.go.id/statistics-table/2/MTQ3MCMy/produksi.html"
        result = _extract_identifier_from_url(url, "statistics-table")
        # Should extract from base64 or pattern
        assert result is not None

    def test_extract_identifier_from_url_no_match(self):
        url = "https://example.com/no-match"
        result = _extract_identifier_from_url(url, "statistics-table")
        assert result is None


# ===================================================================
# Async handler tests
# ===================================================================

@pytest.fixture
def mock_api_client():
    """Create a mock BPS API client."""
    mock = MagicMock()
    mock.get_domains = MagicMock(return_value=[
        {"domain_id": "0000", "domain_name": "Indonesia"},
        {"domain_id": "5300", "domain_name": "NTT"},
    ])
    mock.get_provinces = MagicMock(return_value=[
        {"prov_id": "53", "prov_name": "Nusa Tenggara Timur"},
    ])
    mock.get_subjects = MagicMock(return_value={
        "pagination": {"page": 1, "pages": 2, "total": 10},
        "items": [{"sub_id": 1, "title": "Kependudukan"}],
    })
    mock.get_variables = MagicMock(return_value={
        "pagination": {"page": 1, "pages": 1, "total": 5},
        "items": [{"var_id": 522, "title": "TPT"}],
    })
    mock.get_data = MagicMock(return_value={
        "status": "OK",
        "datacontent": {"1_124": 5.2, "2_124": 3.1},
    })
    mock.get_decoded_data = MagicMock(return_value={
        "status": "OK",
        "data": [{"region": "Kupang", "value": 5.2}],
    })
    mock.get_indicators = MagicMock(return_value={
        "items": [{"title": "Inflasi"}],
        "pagination": {"page": 1, "pages": 1},
    })
    mock.get_subject_categories = MagicMock(return_value=[
        {"subcat_id": 1, "title": "Sosial dan Kependudukan"},
    ])
    mock.get_periods = MagicMock(return_value=[
        {"period_id": 1, "title": "Tahunan"},
    ])
    mock.get_vertical_variables = MagicMock(return_value=[
        {"vervar_id": 1, "title": "Jenis Kelamin"},
    ])
    mock.get_derived_variables = MagicMock(return_value=[
        {"turvar_id": 1, "title": "Derived Var 1"},
    ])
    mock.get_derived_periods = MagicMock(return_value=[
        {"turth_id": 1, "title": "Derived Period 1"},
    ])
    mock.get_units = MagicMock(return_value=[
        {"unit_id": 1, "title": "Persen"},
    ])
    mock.get_infographics = MagicMock(return_value={
        "items": [{"ig_id": 1, "title": "Infographic 1"}],
        "pagination": {"page": 1},
    })
    mock.get_infographic_detail = MagicMock(return_value={
        "ig_id": 1, "title": "Detail", "image": "url",
    })
    mock.get_glossary = MagicMock(return_value={
        "items": [{"glossary_id": 1, "title": "GDP"}],
        "pagination": {"page": 1},
    })
    mock.get_glossary_detail = MagicMock(return_value={
        "glossary_id": 1, "title": "GDP", "definition": "Gross Domestic Product",
    })
    mock.get_sdgs = MagicMock(return_value=[
        {"goal": "1", "title": "No Poverty"},
    ])
    mock.get_sdds = MagicMock(return_value=[
        {"sdds_id": 1, "title": "SDDS Item"},
    ])
    mock.get_news_detail = MagicMock(return_value={
        "news_id": 1, "title": "News", "content": "Content",
    })
    mock.get_news_categories = MagicMock(return_value=[
        {"newscat_id": 1, "title": "Ekonomi"},
    ])
    mock.get_press_releases = MagicMock(return_value={
        "items": [{"pr_id": 1, "title": "Press Release"}],
        "pagination": {"page": 1},
    })
    mock.get_publications = MagicMock(return_value={
        "items": [{"pub_id": 1, "title": "Publication"}],
        "pagination": {"page": 1},
    })
    mock.get_static_tables = MagicMock(return_value={
        "items": [{"table_id": 1501, "title": "Table 1"}],
        "pagination": {"page": 1, "pages": 1, "total": 1},
    })
    mock.get_static_table_detail = MagicMock(return_value={
        "data": {"title": "Table Detail", "table": "<table></table>", "updt_date": "2024-01-01"},
    })
    mock.get_regencies = MagicMock(return_value=[
        {"kab_id": "5301", "kab_name": "Kab. Kupang"},
    ])
    mock.get_news = MagicMock(return_value={
        "items": [{"news_id": 1, "title": "News Item"}],
        "pagination": {"page": 1},
    })
    mock.get_press_release_detail = MagicMock(return_value={
        "pr_id": 1, "title": "PR Detail", "content": "Content",
    })
    mock.get_publication_detail = MagicMock(return_value={
        "pub_id": 1, "title": "Pub Detail", "abstract": "Abstract",
    })
    mock.get_census_events = MagicMock(return_value=[
        {"kegiatan": "sp2020", "title": "Sensus Penduduk 2020"},
    ])
    mock.get_census_topics = MagicMock(return_value=[
        {"topik_id": 1, "title": "Demografi"},
    ])
    mock.get_census_areas = MagicMock(return_value=[
        {"wilayah_id": 1, "title": "NTT"},
    ])
    mock.get_census_datasets = MagicMock(return_value=[
        {"dataset_id": 1, "title": "Dataset 1"},
    ])
    mock.get_census_data = MagicMock(return_value={
        "data": [{"label": "Total", "value": 1000}],
    })
    mock.search = MagicMock(return_value={
        "items": [{"title": "Inflasi", "url": "http://example.com"}],
        "pagination": {"page": 1, "pages": 1, "total": 1},
    })
    # SIMDASI methods
    mock.get_simdasi_provinces = MagicMock(return_value=[
        {"prov_id": "53", "prov_name": "NTT"},
    ])
    mock.get_simdasi_regencies = MagicMock(return_value=[
        {"kab_id": "5301", "kab_name": "Kupang"},
    ])
    mock.get_simdasi_districts = MagicMock(return_value=[
        {"kec_id": "530101", "kec_name": "Alak"},
    ])
    mock.get_simdasi_subjects = MagicMock(return_value=[
        {"subj_id": "1", "title": "Kependudukan"},
    ])
    mock.get_simdasi_master_tables = MagicMock(return_value=[
        {"table_id": "T1", "title": "Master Table 1"},
    ])
    mock.get_simdasi_table_detail = MagicMock(return_value={
        "table_id": "T1", "title": "Detail", "data": [],
    })
    mock.get_simdasi_tables_by_area = MagicMock(return_value=[
        {"table_id": "T1", "title": "Table by Area"},
    ])
    mock.get_simdasi_tables_by_area_and_subject = MagicMock(return_value=[
        {"table_id": "T1", "title": "Table by Area+Subject"},
    ])
    mock.get_simdasi_master_table_detail = MagicMock(return_value={
        "table_id": "T1", "title": "Master Detail",
    })
    # CSA methods
    mock.get_csa_categories = MagicMock(return_value=[
        {"cat_id": 1, "title": "Category 1"},
    ])
    mock.get_csa_subjects = MagicMock(return_value=[
        {"subj_id": 1, "title": "CSA Subject"},
    ])
    mock.get_csa_tables = MagicMock(return_value={
        "items": [{"table_id": 1, "title": "CSA Table"}],
        "pagination": {"page": 1},
    })
    mock.get_csa_table_detail = MagicMock(return_value={
        "table_id": 1, "title": "CSA Detail", "data": [],
    })
    # KBLI/KBKI
    mock.get_kbli = MagicMock(return_value={
        "items": [{"kbli_id": "01", "title": "Agriculture"}],
        "pagination": {"page": 1},
    })
    mock.get_kbli_detail = MagicMock(return_value={
        "kbli_id": "01", "title": "Agriculture", "description": "Desc",
    })
    mock.get_kbki = MagicMock(return_value={
        "items": [{"kbki_id": "01", "title": "Product 1"}],
        "pagination": {"page": 1},
    })
    mock.get_kbki_detail = MagicMock(return_value={
        "kbki_id": "01", "title": "Product 1", "description": "Desc",
    })
    # Foreign trade
    mock.get_foreign_trade = MagicMock(return_value={
        "items": [{"hs_code": "01", "value": 1000}],
        "pagination": {"page": 1},
    })
    # Dynamic tables
    mock.get_dynamic_tables = MagicMock(return_value={
        "items": [{"table_id": 1, "title": "Dynamic Table"}],
        "pagination": {"page": 1},
    })
    mock.get_dynamic_table_detail = MagicMock(return_value={
        "table_id": 1, "title": "Dynamic Detail", "data": [],
    })
    return mock


@pytest.fixture
def patch_api(mock_api_client):
    """Patch get_api_client to return our mock."""
    with patch("mini_agent.bps_mcp_server.get_api_client", return_value=mock_api_client):
        yield mock_api_client


class TestBPSYearToTh:
    @pytest.mark.asyncio
    async def test_basic_conversion(self):
        result = await bps_mcp_server.bps_year_to_th(2024)
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["th"] == 124
        assert parsed["data"]["year"] == 2024


class TestBPSListYears:
    @pytest.mark.asyncio
    async def test_without_var(self, patch_api):
        result = await bps_mcp_server.bps_list_years(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert "year_range" in parsed["data"]
        assert parsed["data"]["year_range"]["min_year"] == 2017

    @pytest.mark.asyncio
    async def test_with_var(self, patch_api):
        result = await bps_mcp_server.bps_list_years(domain="5300", var=522)
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert "available_years" in parsed["data"]

    @pytest.mark.asyncio
    async def test_error_handling(self):
        with patch("mini_agent.bps_mcp_server.get_api_client", side_effect=ValueError("No key")):
            result = await bps_mcp_server.bps_list_years(domain="5300")
            parsed = json.loads(result)
            assert parsed["success"] is False


class TestBPSListDomains:
    @pytest.mark.asyncio
    async def test_list_all(self, patch_api):
        result = await bps_mcp_server.bps_list_domains(type="all")
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert len(parsed["data"]) == 2

    @pytest.mark.asyncio
    async def test_error(self):
        with patch("mini_agent.bps_mcp_server.get_api_client", side_effect=Exception("fail")):
            result = await bps_mcp_server.bps_list_domains()
            parsed = json.loads(result)
            assert parsed["success"] is False


class TestBPSListProvinces:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_provinces()
        parsed = json.loads(result)
        assert parsed["success"] is True
        assert len(parsed["data"]) == 1


class TestBPSListSubjects:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_subjects(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_error(self):
        with patch("mini_agent.bps_mcp_server.get_api_client", side_effect=Exception("err")):
            result = await bps_mcp_server.bps_list_subjects()
            parsed = json.loads(result)
            assert parsed["success"] is False


class TestBPSGetVariables:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_variables(domain="5300", subject=1)
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_error(self):
        with patch("mini_agent.bps_mcp_server.get_api_client", side_effect=Exception("err")):
            result = await bps_mcp_server.bps_get_variables()
            parsed = json.loads(result)
            assert parsed["success"] is False


class TestBPSGetDecodedData:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_decoded_data(var=522, th=124, domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_api_error_status(self, patch_api):
        patch_api.get_decoded_data = MagicMock(return_value={"status": "ERROR"})
        result = await bps_mcp_server.bps_get_decoded_data(var=522, th=124)
        parsed = json.loads(result)
        assert parsed["success"] is False

    @pytest.mark.asyncio
    async def test_exception(self):
        with patch("mini_agent.bps_mcp_server.get_api_client", side_effect=Exception("err")):
            result = await bps_mcp_server.bps_get_decoded_data(var=522, th=124)
            parsed = json.loads(result)
            assert parsed["success"] is False


class TestBPSGetData:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_data(var=522, th=124, domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_error(self):
        with patch("mini_agent.bps_mcp_server.get_api_client", side_effect=Exception("err")):
            result = await bps_mcp_server.bps_get_data(var=522, th=124)
            parsed = json.loads(result)
            assert parsed["success"] is False


class TestBPSSearch:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_search(keyword="inflasi", domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_error(self):
        with patch("mini_agent.bps_mcp_server.get_api_client", side_effect=Exception("err")):
            result = await bps_mcp_server.bps_search(keyword="inflasi")
            parsed = json.loads(result)
            assert parsed["success"] is False


class TestBPSSearchNTT:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_search_ntt(keyword="inflasi")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_error(self):
        with patch("mini_agent.bps_mcp_server.get_api_client", side_effect=Exception("err")):
            result = await bps_mcp_server.bps_search_ntt(keyword="inflasi")
            parsed = json.loads(result)
            assert parsed["success"] is False


class TestBPSSearchNasional:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_search_nasional(keyword="inflasi")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSGetPressReleases:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_press_releases(year=2024, domain="0000")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_error(self):
        with patch("mini_agent.bps_mcp_server.get_api_client", side_effect=Exception("err")):
            result = await bps_mcp_server.bps_get_press_releases()
            parsed = json.loads(result)
            assert parsed["success"] is False


class TestBPSGetPublications:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_publications(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSGetIndicators:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_indicators(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_rejects_year(self, patch_api):
        result = await bps_mcp_server.bps_get_indicators(domain="5300", year=2025)
        parsed = json.loads(result)
        assert parsed["success"] is False


class TestBPSListSubjectCategories:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_subject_categories(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListPeriods:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_periods(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListVerticalVariables:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_vertical_variables(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListDerivedVariables:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_derived_variables(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListDerivedPeriods:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_derived_periods(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListUnits:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_units(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListInfographics:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_infographics(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSGetInfographicDetail:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_infographic_detail(infographic_id=1)
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListGlossary:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_glossary()
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSGetGlossaryDetail:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_glossary_detail(glossary_id=1)
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListSDGs:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_sdgs()
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListSDDS:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_sdds()
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSGetNewsDetail:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_news_detail(news_id=1)
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListNewsCategories:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_news_categories(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSGetCensusTopics:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_census_topics(kegiatan="sp2020")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSGetCensusAreas:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_census_areas(kegiatan="sp2020")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSGetCensusDatasets:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_census_datasets(kegiatan="sp2020", topik=1)
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSGetCensusData:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_census_data(kegiatan="sp2020", wilayah_sensus=1, dataset=1)
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSSimdasi:
    @pytest.mark.asyncio
    async def test_get_regencies(self, patch_api):
        result = await bps_mcp_server.bps_get_simdasi_regencies(parent="53")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_districts(self, patch_api):
        result = await bps_mcp_server.bps_get_simdasi_districts(parent="5301")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_subjects(self, patch_api):
        result = await bps_mcp_server.bps_get_simdasi_subjects(wilayah="53")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_master_tables(self, patch_api):
        result = await bps_mcp_server.bps_get_simdasi_master_tables()
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_table_detail(self, patch_api):
        result = await bps_mcp_server.bps_get_simdasi_table_detail(wilayah="53", tahun=2024, id_tabel="T1")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_tables_by_area(self, patch_api):
        result = await bps_mcp_server.bps_get_simdasi_tables_by_area(wilayah="53")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_tables_by_area_and_subject(self, patch_api):
        result = await bps_mcp_server.bps_get_simdasi_tables_by_area_and_subject(wilayah="53", id_subjek="1")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_master_table_detail(self, patch_api):
        result = await bps_mcp_server.bps_get_simdasi_master_table_detail(id_tabel="T1")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSCSA:
    @pytest.mark.asyncio
    async def test_list_categories(self, patch_api):
        result = await bps_mcp_server.bps_list_csa_categories(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_subjects(self, patch_api):
        result = await bps_mcp_server.bps_list_csa_subjects(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_tables(self, patch_api):
        result = await bps_mcp_server.bps_list_csa_tables(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_table_detail(self, patch_api):
        result = await bps_mcp_server.bps_get_csa_table_detail(domain="5300", table_id=1)
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSKBLI:
    @pytest.mark.asyncio
    async def test_list_kbli(self, patch_api):
        result = await bps_mcp_server.bps_list_kbli()
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_kbli_detail(self, patch_api):
        result = await bps_mcp_server.bps_get_kbli_detail(kbli_id="01")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_list_kbki(self, patch_api):
        result = await bps_mcp_server.bps_list_kbki()
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_kbki_detail(self, patch_api):
        result = await bps_mcp_server.bps_get_kbki_detail(kbki_id="01")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSForeignTrade:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_get_foreign_trade(sumber=1, kodehs=1, tahun="2024")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSDynamicTables:
    @pytest.mark.asyncio
    async def test_list(self, patch_api):
        result = await bps_mcp_server.bps_list_dynamic_tables(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_get_detail(self, patch_api):
        result = await bps_mcp_server.bps_get_dynamic_table_detail(domain="5300", table_id=1)
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListRegencies:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_regencies()
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListNews:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_news(domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSGetPressReleaseDetail:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        mock_material = MagicMock()
        mock_material.desc.return_value = {"title": "PR Detail", "content": "Content", "pdf": "http://example.com/pr.pdf"}
        patch_api.get_press_release_detail = MagicMock(return_value=mock_material)
        result = await bps_mcp_server.bps_get_press_release_detail(brs_id=1, domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSGetPublicationDetail:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        mock_material = MagicMock()
        mock_material.desc.return_value = {"title": "Pub Detail", "abstract": "Abstract", "pdf": "http://example.com/pub.pdf"}
        patch_api.get_publication_detail = MagicMock(return_value=mock_material)
        result = await bps_mcp_server.bps_get_publication_detail(pub_id="1", domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListCensusEvents:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_census_events()
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSListSimdasiProvinces:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_list_simdasi_provinces()
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSSearchGeneric:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_search_generic(keyword="inflasi", domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True


class TestBPSGetTableData:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        # Mock returns a table with actual data
        patch_api.get_static_table_detail = MagicMock(return_value={
            "data": {
                "title": "Inflasi NTT",
                "table": "<table><tr><th>Wilayah</th><th>Nilai</th></tr><tr><td>Kupang</td><td>3.5</td></tr></table>",
                "updt_date": "2024-01-01",
            }
        })
        result = await bps_mcp_server.bps_get_table_data(table_id=1501, domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_error(self):
        with patch("mini_agent.bps_mcp_server.get_api_client", side_effect=Exception("err")):
            result = await bps_mcp_server.bps_get_table_data(table_id=1501)
            parsed = json.loads(result)
            assert parsed["success"] is False


class TestBPSSearchAndGetData:
    @pytest.mark.asyncio
    async def test_success(self, patch_api):
        result = await bps_mcp_server.bps_search_and_get_data(keyword="inflasi", domain="5300")
        parsed = json.loads(result)
        assert parsed["success"] is True

    @pytest.mark.asyncio
    async def test_error(self):
        with patch("mini_agent.bps_mcp_server.get_api_client", side_effect=Exception("err")):
            result = await bps_mcp_server.bps_search_and_get_data(keyword="inflasi")
            parsed = json.loads(result)
            assert parsed["success"] is False


class TestParseHtmlTable:
    def test_basic_table(self):
        html = "<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>"
        headers, rows = bps_mcp_server._parse_html_table(html)
        assert headers == ["A", "B"]
        assert rows == [["1", "2"]]

    def test_empty_table(self):
        html = "<table></table>"
        headers, rows = bps_mcp_server._parse_html_table(html)
        assert headers == []
        assert rows == []

    def test_no_table(self):
        html = "<p>No table here</p>"
        headers, rows = bps_mcp_server._parse_html_table(html)
        assert headers == []
        assert rows == []
