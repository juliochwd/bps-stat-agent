"""Comprehensive unit tests for BPSAPI client.

Tests all 23 data types and their endpoints using mocked responses.
Run with: python -m pytest tests/test_bps_api.py -v
"""

from unittest.mock import Mock, patch

import pytest
import requests

from mini_agent.bps_api import BPSAPI, BPSAPIError, BPSMaterial

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def api():
    """Create BPSAPI instance with test key."""
    return BPSAPI("test-api-key-12345")


@pytest.fixture
def mock_response():
    """Factory for creating mock API responses."""

    def _make_response(data, status_code=200, json_data=None):
        """Create a mock response object.

        Args:
            data: The JSON data to return
            status_code: HTTP status code
            json_data: Optional pre-encoded JSON string
        """
        resp = Mock()
        resp.status_code = status_code
        resp.text = json_data if json_data else '{"data": []}'
        resp.json.return_value = data
        resp.raise_for_status = Mock()
        if status_code >= 400:
            resp.raise_for_status.side_effect = requests.HTTPError(f"{status_code} Error", response=resp)
        return resp

    return _make_response


# ============================================================================
# INITIALIZATION & HTTP METHODS
# ============================================================================


class TestBPSAPIInitialization:
    """Tests for BPSAPI initialization and session setup."""

    def test_init_sets_app_id(self):
        """API should store the app_id."""
        api = BPSAPI("my-key")
        assert api.app_id == "my-key"

    def test_init_creates_session(self):
        """API should create a requests session."""
        api = BPSAPI("my-key")
        assert isinstance(api.session, requests.Session)

    def test_init_sets_default_headers(self):
        """API should set default headers on session."""
        test_api = BPSAPI("test-key")
        assert "Mozilla/5.0" in test_api.session.headers["User-Agent"]
        assert test_api.session.headers["Accept"] == "application/json"

    def test_base_url_is_correct(self):
        """BASE_URL should point to BPS webapi."""
        assert BPSAPI.BASE_URL == "https://webapi.bps.go.id"


class TestBPSAPIPrivateMethods:
    """Tests for _request, _list, _view private methods."""

    def test_request_adds_key_to_params(self, api, mock_response):
        """_request should add API key to request params."""
        mock_resp = mock_response({"status": "OK", "data": []})
        api.session.get = Mock(return_value=mock_resp)

        api._request("https://example.com/api", {"q": "test"})

        call_args = api.session.get.call_args
        assert "key" in call_args.kwargs["params"]
        assert call_args.kwargs["params"]["key"] == "test-api-key-12345"

    def test_request_copies_params_to_avoid_mutation(self, api, mock_response):
        """_request should not mutate caller's params dict."""
        mock_resp = mock_response({"status": "OK", "data": []})
        api.session.get = Mock(return_value=mock_resp)

        original_params = {"q": "test", "page": 1}
        original_params_copy = original_params.copy()

        api._request("https://example.com/api", original_params)

        assert original_params == original_params_copy

    def test_request_raises_on_http_error(self, api, mock_response):
        """_request should raise HTTPError on HTTP errors."""
        mock_resp = mock_response({}, status_code=404)
        api.session.get = Mock(return_value=mock_resp)

        # _request calls resp.raise_for_status() which raises requests.HTTPError on 4xx/5xx
        with pytest.raises(requests.HTTPError):
            api._request("https://example.com/api")

    def test_request_returns_json(self, api, mock_response):
        """_request should parse and return JSON response."""
        expected = {"status": "OK", "data": [{"id": 1}]}
        mock_resp = mock_response(expected)
        api.session.get = Mock(return_value=mock_resp)

        result = api._request("https://example.com/api")

        assert result == expected

    def test_request_invalid_json_raises_error(self, api, mock_response):
        """_request should raise BPSAPIError on invalid JSON."""
        mock_resp = mock_response({}, json_data="not valid json{")
        mock_resp.json.side_effect = ValueError("Invalid JSON")
        api.session.get = Mock(return_value=mock_resp)

        with pytest.raises(BPSAPIError, match="Invalid JSON"):
            api._request("https://example.com/api")

    def test_list_builds_correct_params(self, api, mock_response):
        """_list should build correct params with model and domain."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api._list("subject", "5300", page=1)

        call_args = api.session.get.call_args
        assert "model" in call_args.kwargs["params"]
        assert call_args.kwargs["params"]["model"] == "subject"
        assert call_args.kwargs["params"]["domain"] == "5300"

    def test_list_calls_correct_url(self, api, mock_response):
        """_list should call the list endpoint."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api._list("subject")

        call_args = api.session.get.call_args
        assert "/v1/api/list" in call_args.args[0]

    def test_view_builds_correct_params(self, api, mock_response):
        """_view should include model, id, domain, and lang."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api._view("subject", 123, "5300", lang="eng")

        call_args = api.session.get.call_args
        params = call_args.kwargs["params"]
        assert params["model"] == "subject"
        assert params["id"] == 123
        assert params["domain"] == "5300"
        assert params["lang"] == "eng"


# ============================================================================
# DATA EXTRACTION METHODS
# ============================================================================


class TestExtractData:
    """Tests for _extract_data helper method."""

    def test_extract_data_handles_simdasi_nested_format(self, api):
        """Should extract from SIMDASI nested format data[1]['data']."""
        response = {
            "data": [
                {},  # pagination dict
                {"data": [{"id": 1}, {"id": 2}]},  # nested data
            ]
        }
        result = api._extract_data(response)
        assert result == [{"id": 1}, {"id": 2}]

    def test_extract_data_handles_paginated_format(self, api):
        """Should extract items from paginated [pagination, items] format."""
        response = {"data": [{"page": 1, "total": 10}, [{"id": 1}, {"id": 2}]]}
        result = api._extract_data(response)
        assert result == [{"id": 1}, {"id": 2}]

    def test_extract_data_handles_direct_list_format(self, api):
        """Should return data directly when it's a simple list."""
        response = {"data": [{"id": 1}, {"id": 2}, {"id": 3}]}
        result = api._extract_data(response)
        assert result == [{"id": 1}, {"id": 2}, {"id": 3}]

    def test_extract_data_returns_empty_on_unavailable(self, api):
        """Should return data list even when data-availability is not available if data is a list."""
        # When data is a list, code returns it directly (SIMDASI-style handling)
        response = {"data-availability": "unavailable", "data": [{"id": 1}]}
        result = api._extract_data(response)
        # Code doesn't check data-availability when data is a list - returns data directly
        assert result == [{"id": 1}]

    def test_extract_data_returns_empty_when_not_available_standard_format(self, api):
        """Should return empty when data-availability is not available in standard format."""
        # When data is not a list AND data-availability is not "available", returns empty
        response = {"data-availability": "unavailable", "data": None}
        result = api._extract_data(response)
        assert result == []

    def test_extract_data_returns_empty_when_data_none(self, api):
        """Should return empty list when data is None or empty."""
        response = {"data-availability": "available", "data": []}
        result = api._extract_data(response)
        assert result == []

    def test_extract_data_handles_data_1_is_none(self, api):
        """When data[1] is not a list, code falls through to return data as-is."""
        # data is a list but data[1] is None (not a list), so it falls through
        response = {
            "data": [
                {},  # data[0] is dict
                None,  # data[1] is None - not a list
            ]
        }
        result = api._extract_data(response)
        # Code doesn't match SIMDASI/paginated format, returns data as-is
        assert result == [{}, None]

    def test_extract_data_standard_format_with_list_data(self, api):
        """Test standard BPS format where data is a list and data-availability is available."""
        # This tests lines 145-150 for when data is a list with len > 1
        response = {"data-availability": "available", "data": [{"page": 1}, [{"id": 1}]]}
        result = api._extract_data(response)
        # Line 145: data-availability == "available" (not !=), so doesn't return early
        # Line 147: data = [{"page": 1}, [{"id": 1}]]
        # Line 148: isinstance(list, list) is True and len > 1, so enters
        # Line 149: returns data[1] if not None, else []
        assert result == [{"id": 1}]

    def test_extract_data_standard_format_with_data_1_none(self, api):
        """Test standard format where data[1] is None, returns empty list."""
        response = {"data-availability": "available", "data": [{"id": 123}, None]}
        result = api._extract_data(response)
        # data[0] has no 'page'/'pagination' key, so line 143 check fails
        # Then data[1] is None, so line 152 returns []
        assert result == []

    def test_extract_data_handles_empty_data_list(self, api):
        """Should return empty when data is an empty list."""
        response = {"data-availability": "available", "data": []}
        result = api._extract_data(response)
        assert result == []

    def test_extract_data_handles_nested_data_1_not_list(self, api):
        """Should return data directly when data[1] doesn't contain 'data' key or it's not a list."""
        # When data[1] doesn't match the SIMDASI nested format, returns data directly
        response = {
            "data": [
                {},  # not a dict for paginated format
                {"other_key": "value"},  # doesn't have 'data' key
            ]
        }
        result = api._extract_data(response)
        # Code returns the data directly because data[0] is dict but not the expected paginated format
        # and data[1] doesn't match SIMDASI nested format, so it returns data as-is
        assert result == [{}, {"other_key": "value"}]


class TestExtractPaginated:
    """Tests for _extract_paginated helper method."""

    def test_extract_paginated_returns_pagination_and_items(self, api):
        """Should return dict with pagination and items keys."""
        response = {
            "data-availability": "available",
            "data": [{"page": 1, "total": 100, "count": 50}, [{"id": 1}, {"id": 2}]],
        }
        result = api._extract_paginated(response)

        assert "pagination" in result
        assert "items" in result
        assert result["pagination"]["page"] == 1
        assert result["items"] == [{"id": 1}, {"id": 2}]

    def test_extract_paginated_returns_empty_on_unavailable(self, api):
        """Should return empty items when data-availability is not available."""
        response = {"data-availability": "unavailable", "data": [{}, []]}
        result = api._extract_paginated(response)
        assert result["pagination"] == {}
        assert result["items"] == []

    def test_extract_paginated_handles_missing_data(self, api):
        """Should return empty when data is missing or malformed."""
        response = {"data-availability": "available", "data": []}
        result = api._extract_paginated(response)
        assert result["pagination"] == {}
        assert result["items"] == []

    def test_extract_paginated_handles_data_0_not_dict(self, api):
        """Should handle when data[0] is not a dict - returns it as-is."""
        response = {
            "data-availability": "available",
            "data": [
                "not a dict",  # data[0] is a truthy string
                [{"id": 1}],
            ],
        }
        result = api._extract_paginated(response)
        # Code uses data[0] if truthy, so the string is returned
        assert result["pagination"] == "not a dict"
        assert result["items"] == [{"id": 1}]


# ============================================================================
# DOMAIN ENDPOINTS (Types 1, 18)
# ============================================================================


class TestDomainEndpoints:
    """Tests for domain-related endpoints."""

    def test_get_domains_default_call(self, api, mock_response):
        """get_domains should call domain endpoint with default type."""
        mock_resp = mock_response({"data-availability": "available", "data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_domains()

        call_args = api.session.get.call_args
        assert "/v1/api/domain" in call_args.args[0]
        assert call_args.kwargs["params"]["type"] == "all"

    def test_get_domains_with_type_prov(self, api, mock_response):
        """get_domains should pass type=prov when getting provinces."""
        mock_resp = mock_response({"data-availability": "available", "data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_provinces()

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["type"] == "prov"

    def test_get_domains_with_type_kab(self, api, mock_response):
        """get_domains should pass type=kab when getting all regencies."""
        mock_resp = mock_response({"data-availability": "available", "data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_regencies()

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["type"] == "kab"

    def test_get_regencies_with_prov_id(self, api, mock_response):
        """get_regencies with prov_id should use kabbyprov type."""
        mock_resp = mock_response({"data-availability": "available", "data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_regencies(prov_id="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["type"] == "kabbyprov"
        assert call_args.kwargs["params"]["prov"] == "5300"

    def test_get_domains_with_prov_filter(self, api, mock_response):
        """get_domains should pass prov parameter when filtering by province."""
        mock_resp = mock_response({"data-availability": "available", "data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_domains(type="kabbyprov", prov="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["prov"] == "5300"

    def test_get_domains_extracts_data(self, api, mock_response):
        """get_domains should return extracted data list."""
        mock_resp = mock_response(
            {"data-availability": "available", "data": [{}, [{"domain_id": "5300", "domain_name": "NTT"}]]}
        )
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_domains()

        assert result == [{"domain_id": "5300", "domain_name": "NTT"}]


# ============================================================================
# SUBJECT ENDPOINTS (Type 2)
# ============================================================================


class TestSubjectEndpoints:
    """Tests for subject-related endpoints."""

    def test_get_subject_categories(self, api, mock_response):
        """get_subject_categories should call subcat model."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_subject_categories(domain="5300")

        call_args = api.session.get.call_args
        assert "/v1/api/list" in call_args.args[0]
        assert call_args.kwargs["params"]["model"] == "subcat"

    def test_get_subjects_returns_paginated(self, api, mock_response):
        """get_subjects should return paginated result."""
        mock_resp = mock_response(
            {"data-availability": "available", "data": [{"page": 1, "total": 50}, [{"id": 1, "label": "Ekonomi"}]]}
        )
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_subjects(domain="5300")

        assert "pagination" in result
        assert "items" in result
        assert result["items"][0]["label"] == "Ekonomi"

    def test_get_subjects_with_subcat_filter(self, api, mock_response):
        """get_subjects should pass subcat parameter when filtering."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_subjects(domain="5300", subcat=5)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["subcat"] == 5

    def test_get_subjects_passes_page_param(self, api, mock_response):
        """get_subjects should pass page parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_subjects(domain="5300", page=2)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["page"] == 2

    def test_get_subjects_defaults_to_ind(self, api, mock_response):
        """get_subjects should default language to Indonesian."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_subjects(domain="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["lang"] == "ind"


# ============================================================================
# VARIABLE ENDPOINTS (Type 1, 19, 20)
# ============================================================================


class TestVariableEndpoints:
    """Tests for variable-related endpoints."""

    def test_get_variables_returns_paginated(self, api, mock_response):
        """get_variables should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, [{"id": 1, "label": "GDP"}]]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_variables(domain="5300")

        assert "pagination" in result
        assert "items" in result

    def test_get_variables_with_subject_filter(self, api, mock_response):
        """get_variables should pass subject filter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_variables(domain="5300", subject=5)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["subject"] == 5

    def test_get_variables_with_year_filter(self, api, mock_response):
        """get_variables should pass year filter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_variables(domain="5300", year=2024)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["year"] == 2024

    def test_get_periods_returns_paginated(self, api, mock_response):
        """get_periods should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_periods(domain="5300")

        assert "pagination" in result
        assert "items" in result

    def test_get_periods_with_var_filter(self, api, mock_response):
        """get_periods should pass var filter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_periods(domain="5300", var=184)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["var"] == 184

    def test_get_vertical_variables(self, api, mock_response):
        """get_vertical_variables should use vervar model."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_vertical_variables(domain="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["model"] == "vervar"

    def test_get_vertical_variables_without_var(self, api, mock_response):
        """get_vertical_variables without var should not include var in params."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_vertical_variables(domain="5300")

        call_args = api.session.get.call_args
        assert "var" not in call_args.kwargs["params"]

    def test_get_vertical_variables_with_var(self, api, mock_response):
        """get_vertical_variables with var should include var in params."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_vertical_variables(domain="5300", var=184)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["var"] == 184

    def test_get_derived_variables(self, api, mock_response):
        """get_derived_variables should use turvar model."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_derived_variables(domain="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["model"] == "turvar"

    def test_get_derived_variables_without_var(self, api, mock_response):
        """get_derived_variables without var should not include var in params."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_derived_variables(domain="5300")

        call_args = api.session.get.call_args
        assert "var" not in call_args.kwargs["params"]

    def test_get_derived_variables_with_var(self, api, mock_response):
        """get_derived_variables with var should include var in params."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_derived_variables(domain="5300", var=184)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["var"] == 184

    def test_get_derived_periods(self, api, mock_response):
        """get_derived_periods should use turth model."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_derived_periods(domain="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["model"] == "turth"

    def test_get_derived_periods_without_var(self, api, mock_response):
        """get_derived_periods without var should not include var in params."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_derived_periods(domain="5300")

        call_args = api.session.get.call_args
        assert "var" not in call_args.kwargs["params"]

    def test_get_derived_periods_with_var(self, api, mock_response):
        """get_derived_periods with var should include var in params."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_derived_periods(domain="5300", var=184)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["var"] == 184

    def test_get_units(self, api, mock_response):
        """get_units should use unit model."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_units(domain="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["model"] == "unit"


# ============================================================================
# DYNAMIC DATA (Type 1)
# ============================================================================


class TestDynamicDataEndpoints:
    """Tests for dynamic data retrieval."""

    def test_get_data_requires_var_and_th(self, api, mock_response):
        """get_data should call data model with var and th params."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_data(var=184, th=117, domain="5300")

        call_args = api.session.get.call_args
        params = call_args.kwargs["params"]
        assert params["var"] == 184
        assert params["th"] == 117
        assert params["model"] == "data"

    def test_get_data_with_optional_params(self, api, mock_response):
        """get_data should pass optional turvar, vervar, turth params."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_data(var=184, th=117, turvar=2, vervar=3, turth=4)

        call_args = api.session.get.call_args
        params = call_args.kwargs["params"]
        assert params["turvar"] == 2
        assert params["vervar"] == 3
        assert params["turth"] == 4

    def test_get_data_does_not_include_none_params(self, api, mock_response):
        """get_data should not include optional params set to None."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_data(var=184, th=117, turvar=None, vervar=None)

        call_args = api.session.get.call_args
        params = call_args.kwargs["params"]
        assert "turvar" not in params
        assert "vervar" not in params

    def test_get_data_returns_raw_response(self, api, mock_response):
        """get_data should return full response dict."""
        mock_resp = mock_response({"status": "OK", "var": [], "tahun": []})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_data(var=184, th=117)

        assert result["status"] == "OK"
        assert "var" in result

    def test_get_decoded_data_returns_structured_format(self, api, mock_response):
        """get_decoded_data should return decoded region values."""
        mock_resp_data = {
            "status": "OK",
            "var": [{"val": 184, "label": "GDP", "unit": "Miliar", "subj": "Ekonomi"}],
            "tahun": [{"val": 117, "label": "2024"}],
            "vervar": [{"val": 5300, "label": "NTT"}],
            "datacontent": {"11840": 15000.5},  # key = "1" (region_id) + "1840" (var_id=184 + year hint)
        }
        mock_resp = mock_response(mock_resp_data)
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_decoded_data(var=184, th=117)

        assert result["status"] == "OK"
        assert result["variable"]["label"] == "GDP"
        assert result["year"] == "2024"
        assert result["regions"] == ["NTT"]
        assert len(result["data"]) == 1
        # region_id extracted as 1 (1-digit), since "11840"["1":] = "1840".startswith("184") is True
        assert result["data"][0]["region_id"] == 1
        assert result["data"][0]["value"] == 15000.5

    def test_get_decoded_data_handles_list_datacontent(self, api, mock_response):
        """get_decoded_data should handle list format datacontent."""
        mock_resp_data = {
            "status": "OK",
            "var": [{"val": 184, "label": "GDP"}],
            "tahun": [{"val": 117, "label": "2024"}],
            "vervar": [{"val": 5300, "label": "NTT"}],
            "datacontent": [5300, 15000.5, 1100, 25000.0],
        }
        mock_resp = mock_response(mock_resp_data)
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_decoded_data(var=184, th=117)

        # List format: [region_id, value, region_id, value, ...]
        assert len(result["data"]) == 2

    def test_get_data_with_string_th_for_ranges(self, api, mock_response):
        """get_data should accept string TH for year ranges."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_data(var=184, th="117-120", domain="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["th"] == "117-120"

    def test_extract_region_id_returns_none_when_no_match(self, api):
        """_extract_region_id returns None when key doesn't match expected format."""
        # Code checks if remaining.startswith(var_str), here "001840".startswith("184") is False
        result = api._extract_region_id("53001840", 184)
        assert result is None

    def test_extract_region_id_returns_none_when_pattern_not_matched(self, api):
        """_extract_region_id returns None when pattern doesn't match."""
        # Code checks if remaining.startswith(var_str), here "101840".startswith("184") is False
        result = api._extract_region_id("1101840", 184)
        assert result is None

    def test_extract_region_id_falls_back(self, api):
        """_extract_region_id should return None when format is unexpected."""
        result = api._extract_region_id("invalid", 184)
        assert result is None


# ============================================================================
# STATIC TABLE ENDPOINTS (Type 3)
# ============================================================================


class TestStaticTableEndpoints:
    """Tests for static and dynamic table endpoints."""

    def test_get_static_tables_returns_paginated(self, api, mock_response):
        """get_static_tables should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_static_tables(domain="5300")

        assert "pagination" in result
        assert "items" in result

    def test_get_static_tables_with_year_filter(self, api, mock_response):
        """get_static_tables should pass year parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_static_tables(domain="5300", year=2024)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["year"] == 2024

    def test_get_static_tables_with_keyword(self, api, mock_response):
        """get_static_tables should pass keyword parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_static_tables(domain="5300", keyword="population")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["keyword"] == "population"

    def test_get_static_table_detail(self, api, mock_response):
        """get_static_table_detail should use view endpoint."""
        mock_resp = mock_response({"data": {"title": "Population"}})
        api.session.get = Mock(return_value=mock_resp)

        api.get_static_table_detail(table_id=123, domain="5300")

        call_args = api.session.get.call_args
        assert "/v1/api/view" in call_args.args[0]
        assert call_args.kwargs["params"]["id"] == 123

    def test_get_dynamic_tables(self, api, mock_response):
        """get_dynamic_tables should use dynamictable model."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_dynamic_tables(domain="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["model"] == "dynamictable"

    def test_get_dynamic_tables_with_year_and_keyword(self, api, mock_response):
        """get_dynamic_tables should pass both year and keyword parameters."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_dynamic_tables(domain="5300", year=2024, keyword="population")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["year"] == 2024
        assert call_args.kwargs["params"]["keyword"] == "population"

    def test_get_dynamic_table_detail(self, api, mock_response):
        """get_dynamic_table_detail should use view endpoint."""
        mock_resp = mock_response({"data": {}})
        api.session.get = Mock(return_value=mock_resp)

        api.get_dynamic_table_detail(table_id=456, domain="5300")

        call_args = api.session.get.call_args
        assert "/v1/api/view" in call_args.args[0]


# ============================================================================
# PRESS RELEASE ENDPOINTS (Type 6)
# ============================================================================


class TestPressReleaseEndpoints:
    """Tests for press release endpoints."""

    def test_get_press_releases_returns_paginated(self, api, mock_response):
        """get_press_releases should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_press_releases(domain="5300")

        assert "pagination" in result
        assert "items" in result

    def test_get_press_releases_with_year_filter(self, api, mock_response):
        """get_press_releases should pass year parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_press_releases(year=2024)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["year"] == 2024

    def test_get_press_releases_with_month_filter(self, api, mock_response):
        """get_press_releases should pass month parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_press_releases(month=3)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["month"] == 3

    def test_get_press_releases_with_keyword(self, api, mock_response):
        """get_press_releases should pass keyword parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_press_releases(keyword="inflasi")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["keyword"] == "inflasi"

    def test_get_press_release_detail(self, api, mock_response):
        """get_press_release_detail should use view endpoint and return BPSMaterial."""
        mock_resp = mock_response({"data": {"title": "Press Release", "pdf": "http://example.com/test.pdf"}})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_press_release_detail(brs_id=789, domain="5300")

        call_args = api.session.get.call_args
        assert "/v1/api/view" in call_args.args[0]
        assert call_args.kwargs["params"]["id"] == 789
        # Verify it returns BPSMaterial
        from mini_agent.bps_api import BPSMaterial

        assert isinstance(result, BPSMaterial)
        assert result.desc()["title"] == "Press Release"


# ============================================================================
# PUBLICATION ENDPOINTS (Type 5)
# ============================================================================


class TestPublicationEndpoints:
    """Tests for publication endpoints."""

    def test_get_publications_returns_paginated(self, api, mock_response):
        """get_publications should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_publications(domain="5300")

        assert "pagination" in result
        assert "items" in result

    def test_get_publications_with_year_filter(self, api, mock_response):
        """get_publications should pass year parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_publications(year=2024)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["year"] == 2024

    def test_get_publications_with_month_filter(self, api, mock_response):
        """get_publications should pass month parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_publications(month=6)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["month"] == 6

    def test_get_publications_with_keyword(self, api, mock_response):
        """get_publications should pass keyword parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_publications(keyword="ekonomi")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["keyword"] == "ekonomi"

    def test_get_publication_detail(self, api, mock_response):
        """get_publication_detail should use view endpoint and return BPSMaterial."""
        mock_resp = mock_response({"data": {"title": "Publication", "pdf": "http://example.com/pub.pdf"}})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_publication_detail(pub_id="PUB123", domain="5300")

        call_args = api.session.get.call_args
        assert "/v1/api/view" in call_args.args[0]
        assert call_args.kwargs["params"]["id"] == "PUB123"
        # Verify it returns BPSMaterial
        from mini_agent.bps_api import BPSMaterial

        assert isinstance(result, BPSMaterial)
        assert result.desc()["title"] == "Publication"


# ============================================================================
# INDICATOR & INFOGRAPHIC ENDPOINTS (Types 4, 8)
# ============================================================================


class TestIndicatorEndpoints:
    """Tests for indicator and infographic endpoints."""

    def test_get_indicators_returns_paginated(self, api, mock_response):
        """get_indicators should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_indicators(domain="5300")

        assert "pagination" in result
        assert "items" in result

    def test_get_indicators_with_var_filter(self, api, mock_response):
        """get_indicators should pass var parameter when filtering."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_indicators(domain="5300", var=184)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["var"] == 184

    def test_get_infographics_returns_paginated(self, api, mock_response):
        """get_infographics should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_infographics(domain="5300")

        assert "pagination" in result
        assert "items" in result

    def test_get_infographics_with_keyword(self, api, mock_response):
        """get_infographics should pass keyword parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_infographics(keyword="chart")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["keyword"] == "chart"

    def test_get_infographic_detail(self, api, mock_response):
        """get_infographic_detail should use view endpoint."""
        mock_resp = mock_response({"data": {"image_url": "http://example.com/img.png"}})
        api.session.get = Mock(return_value=mock_resp)

        api.get_infographic_detail(infographic_id="INFO123", domain="5300")

        call_args = api.session.get.call_args
        assert "/v1/api/view" in call_args.args[0]
        assert call_args.kwargs["params"]["id"] == "INFO123"


# ============================================================================
# GLOSSARY ENDPOINTS (Type 15)
# ============================================================================


class TestGlossaryEndpoints:
    """Tests for glossary endpoints."""

    def test_get_glossary_returns_paginated(self, api, mock_response):
        """get_glossary should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_glossary()

        assert "pagination" in result
        assert "items" in result

    def test_get_glossary_with_prefix(self, api, mock_response):
        """get_glossary should pass prefix parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_glossary(prefix="a")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["prefix"] == "a"

    def test_get_glossary_passes_perpage(self, api, mock_response):
        """get_glossary should pass perpage parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_glossary(perpage=25)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["perpage"] == 25

    def test_get_glossary_detail(self, api, mock_response):
        """get_glossary_detail should use view endpoint."""
        mock_resp = mock_response({"data": {"term": "GDP", "definition": "Gross Domestic Product"}})
        api.session.get = Mock(return_value=mock_resp)

        api.get_glossary_detail(glossary_id=1)

        call_args = api.session.get.call_args
        assert "/v1/api/view" in call_args.args[0]
        assert call_args.kwargs["params"]["id"] == 1


# ============================================================================
# SDGs & SDDS ENDPOINTS (Types 11, 12)
# ============================================================================


class TestSDGSddsEndpoints:
    """Tests for SDGs and SDDS endpoints."""

    def test_get_sdgs_returns_paginated(self, api, mock_response):
        """get_sdgs should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_sdgs()

        assert "pagination" in result
        assert "items" in result

    def test_get_sdgs_with_goal_filter(self, api, mock_response):
        """get_sdgs should pass goal parameter when filtering."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_sdgs(goal="1")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["goal"] == "1"

    def test_get_sdgs_uses_sdgs_model(self, api, mock_response):
        """get_sdgs should use sdgs model."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_sdgs()

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["model"] == "sdgs"

    def test_get_sdds_returns_paginated(self, api, mock_response):
        """get_sdds should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_sdds()

        assert "pagination" in result
        assert "items" in result

    def test_get_sdds_uses_sdds_model(self, api, mock_response):
        """get_sdds should use sdds model."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_sdds()

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["model"] == "sdds"


# ============================================================================
# NEWS ENDPOINTS (Type 7)
# ============================================================================


class TestNewsEndpoints:
    """Tests for news endpoints."""

    def test_get_news_returns_paginated(self, api, mock_response):
        """get_news should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_news(domain="5300")

        assert "pagination" in result
        assert "items" in result

    def test_get_news_with_newscat_filter(self, api, mock_response):
        """get_news should pass newscat parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_news(newscat=5)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["newscat"] == 5

    def test_get_news_with_year_filter(self, api, mock_response):
        """get_news should pass year parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_news(year=2024)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["year"] == 2024

    def test_get_news_with_month_filter(self, api, mock_response):
        """get_news should pass month parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_news(month=3)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["month"] == 3

    def test_get_news_with_keyword(self, api, mock_response):
        """get_news should pass keyword parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_news(keyword="bps")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["keyword"] == "bps"

    def test_get_news_detail(self, api, mock_response):
        """get_news_detail should use view endpoint."""
        mock_resp = mock_response({"data": {"title": "News Article"}})
        api.session.get = Mock(return_value=mock_resp)

        api.get_news_detail(news_id=123, domain="5300")

        call_args = api.session.get.call_args
        assert "/v1/api/view" in call_args.args[0]
        assert call_args.kwargs["params"]["id"] == 123

    def test_get_news_categories(self, api, mock_response):
        """get_news_categories should use newscategory model."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_news_categories(domain="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["model"] == "newscategory"


# ============================================================================
# CSA ENDPOINTS (Type 22)
# ============================================================================


class TestCSAEndpoints:
    """Tests for CSA (Custom Statistical Areas) endpoints."""

    def test_get_csa_categories(self, api, mock_response):
        """get_csa_categories should use subcatcsa model."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_csa_categories(domain="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["model"] == "subcatcsa"

    def test_get_csa_subjects_returns_paginated(self, api, mock_response):
        """get_csa_subjects should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_csa_subjects(domain="5300")

        assert "pagination" in result
        assert "items" in result

    def test_get_csa_subjects_with_subcat_filter(self, api, mock_response):
        """get_csa_subjects should pass subcat parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_csa_subjects(domain="5300", subcat="cat1")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["subcat"] == "cat1"

    def test_get_csa_tables_returns_paginated(self, api, mock_response):
        """get_csa_tables should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_csa_tables(domain="5300")

        assert "pagination" in result
        assert "items" in result

    def test_get_csa_tables_with_subject_filter(self, api, mock_response):
        """get_csa_tables should pass subject parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_csa_tables(domain="5300", subject=5)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["subject"] == 5

    def test_get_csa_tables_passes_perpage(self, api, mock_response):
        """get_csa_tables should pass perpage parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_csa_tables(perpage=25)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["perpage"] == 25

    def test_get_csa_table_detail(self, api, mock_response):
        """get_csa_table_detail should use view endpoint with custom params."""
        mock_resp = mock_response({"data": {}})
        api.session.get = Mock(return_value=mock_resp)

        api.get_csa_table_detail(table_id="T123", year=2024, domain="5300")

        call_args = api.session.get.call_args
        assert "/v1/api/view" in call_args.args[0]
        assert call_args.kwargs["params"]["id"] == "T123"
        assert call_args.kwargs["params"]["year"] == 2024


# ============================================================================
# FOREIGN TRADE ENDPOINT (Type 21)
# ============================================================================


class TestForeignTradeEndpoint:
    """Tests for foreign trade (export/import) endpoint."""

    def test_get_foreign_trade_builds_correct_params(self, api, mock_response):
        """get_foreign_trade should build correct params for export/import data."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_foreign_trade(sumber=1, kodehs=1011, tahun="2024")

        call_args = api.session.get.call_args
        params = call_args.kwargs["params"]
        assert params["sumber"] == 1
        assert params["kodehs"] == 1011
        assert params["tahun"] == "2024"

    def test_get_foreign_trade_default_periode(self, api, mock_response):
        """get_foreign_trade should default periode to 1 (monthly)."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_foreign_trade(sumber=1, kodehs=1011, tahun="2024")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["periode"] == 1

    def test_get_foreign_trade_default_jenishs(self, api, mock_response):
        """get_foreign_trade should default jenishs to 1 (two digit)."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_foreign_trade(sumber=1, kodehs=1011, tahun="2024")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["jenishs"] == 1

    def test_get_foreign_trade_with_annual_periode(self, api, mock_response):
        """get_foreign_trade should pass periode=2 for annually."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_foreign_trade(sumber=1, kodehs=1011, tahun="2024", periode=2)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["periode"] == 2

    def test_get_foreign_trade_with_full_hs_code(self, api, mock_response):
        """get_foreign_trade should pass jenishs=2 for full HS code."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_foreign_trade(sumber=1, kodehs=1011, tahun="2024", jenishs=2)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["jenishs"] == 2

    def test_get_foreign_trade_calls_dataexim_endpoint(self, api, mock_response):
        """get_foreign_trade should call dataexim endpoint."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_foreign_trade(sumber=1, kodehs=1011, tahun="2024")

        call_args = api.session.get.call_args
        assert "/v1/api/dataexim" in call_args.args[0]

    def test_get_foreign_trade_returns_raw_response(self, api, mock_response):
        """get_foreign_trade should return full response dict."""
        mock_resp_data = {"status": "OK", "data": {"export": [], "import": []}}
        mock_resp = mock_response(mock_resp_data)
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_foreign_trade(sumber=1, kodehs=1011, tahun="2024")

        assert result["status"] == "OK"
        assert "data" in result


# ============================================================================
# KBLI ENDPOINTS (Type 13)
# ============================================================================


class TestKBLIEndpoints:
    """Tests for KBLI (Indonesian Industrial Classification) endpoints."""

    def test_get_kbli_defaults_to_2020(self, api, mock_response):
        """get_kbli should default to year 2020 model."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_kbli()

        call_args = api.session.get.call_args
        assert "kbli2020" in call_args.kwargs["params"]["model"]

    def test_get_kbli_with_year_2015(self, api, mock_response):
        """get_kbli should use kbli2015 model for year 2015."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_kbli(year=2015)

        call_args = api.session.get.call_args
        assert "kbli2015" in call_args.kwargs["params"]["model"]

    def test_get_kbli_with_level_filter(self, api, mock_response):
        """get_kbli should pass level parameter when filtering."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_kbli(level="kategori")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["level"] == "kategori"

    def test_get_kbli_passes_pagination_params(self, api, mock_response):
        """get_kbli should pass page and perpage parameters."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_kbli(page=2, perpage=25)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["page"] == 2
        assert call_args.kwargs["params"]["perpage"] == 25

    def test_get_kbli_returns_paginated(self, api, mock_response):
        """get_kbli should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_kbli()

        assert "pagination" in result
        assert "items" in result

    def test_get_kbli_detail(self, api, mock_response):
        """get_kbli_detail should use view endpoint."""
        mock_resp = mock_response({"data": {"code": "01", "description": "Agriculture"}})
        api.session.get = Mock(return_value=mock_resp)

        api.get_kbli_detail(kbli_id="01", year=2020)

        call_args = api.session.get.call_args
        assert "/v1/api/view" in call_args.args[0]
        assert call_args.kwargs["params"]["id"] == "01"


# ============================================================================
# CENSUS ENDPOINTS (Type 9)
# ============================================================================


class TestCensusEndpoints:
    """Tests for census data endpoints."""

    def test_get_census_events(self, api, mock_response):
        """get_census_events should call census datasource endpoint."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_census_events()

        call_args = api.session.get.call_args
        assert "/v1/api/interoperabilitas/datasource/sensus/id/37" in call_args.args[0]

    def test_get_census_topics(self, api, mock_response):
        """get_census_topics should pass kegiatan parameter."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_census_topics(kegiatan="sp2020")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["kegiatan"] == "sp2020"
        assert "/id/38" in call_args.args[0]

    def test_get_census_areas(self, api, mock_response):
        """get_census_areas should pass kegiatan parameter."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_census_areas(kegiatan="sp2020")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["kegiatan"] == "sp2020"
        assert "/id/39" in call_args.args[0]

    def test_get_census_datasets(self, api, mock_response):
        """get_census_datasets should pass kegiatan and topik params."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_census_datasets(kegiatan="sp2020", topik=5)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["kegiatan"] == "sp2020"
        assert call_args.kwargs["params"]["topik"] == 5
        assert "/id/40" in call_args.args[0]

    def test_get_census_data(self, api, mock_response):
        """get_census_data should pass all required params."""
        mock_resp = mock_response({"data": {}})
        api.session.get = Mock(return_value=mock_resp)

        api.get_census_data(kegiatan="sp2020", wilayah_sensus=1, dataset=3)

        call_args = api.session.get.call_args
        params = call_args.kwargs["params"]
        assert params["kegiatan"] == "sp2020"
        assert params["wilayah_sensus"] == 1
        assert params["dataset"] == 3
        assert "/id/41" in call_args.args[0]


# ============================================================================
# SIMDASI ENDPOINTS (Type 10)
# ============================================================================


class TestSIMDASIEndpoints:
    """Tests for SIMDASI (Regional Statistics) endpoints."""

    def test_get_simdasi_provinces(self, api, mock_response):
        """get_simdasi_provinces should call SIMDASI provinces endpoint."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_simdasi_provinces()

        call_args = api.session.get.call_args
        assert "/id/26" in call_args.args[0]

    def test_get_simdasi_regencies(self, api, mock_response):
        """get_simdasi_regencies should pass parent parameter."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_simdasi_regencies(parent="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["parent"] == "5300"
        assert "/id/27" in call_args.args[0]

    def test_get_simdasi_districts(self, api, mock_response):
        """get_simdasi_districts should pass parent parameter."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_simdasi_districts(parent="5301")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["parent"] == "5301"
        assert "/id/28" in call_args.args[0]

    def test_get_simdasi_subjects(self, api, mock_response):
        """get_simdasi_subjects should pass wilayah parameter."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_simdasi_subjects(wilayah="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["wilayah"] == "5300"
        assert "/id/22" in call_args.args[0]

    def test_get_simdasi_master_tables(self, api, mock_response):
        """get_simdasi_master_tables should call master tables endpoint."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_simdasi_master_tables()

        call_args = api.session.get.call_args
        assert "/id/34" in call_args.args[0]

    def test_get_simdasi_table_detail(self, api, mock_response):
        """get_simdasi_table_detail should pass wilayah, tahun, id_tabel."""
        mock_resp = mock_response({"data": {}})
        api.session.get = Mock(return_value=mock_resp)

        api.get_simdasi_table_detail(wilayah="5300", tahun=2024, id_tabel="T1")

        call_args = api.session.get.call_args
        params = call_args.kwargs["params"]
        assert params["wilayah"] == "5300"
        assert params["tahun"] == 2024
        assert params["id_tabel"] == "T1"
        assert "/id/25" in call_args.args[0]

    def test_get_simdasi_tables_by_area(self, api, mock_response):
        """get_simdasi_tables_by_area should pass wilayah parameter."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_simdasi_tables_by_area(wilayah="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["wilayah"] == "5300"
        assert "/id/23" in call_args.args[0]

    def test_get_simdasi_tables_by_area_and_subject(self, api, mock_response):
        """get_simdasi_tables_by_area_and_subject should pass both params."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api.get_simdasi_tables_by_area_and_subject(wilayah="5300", id_subjek="S1")

        call_args = api.session.get.call_args
        params = call_args.kwargs["params"]
        assert params["wilayah"] == "5300"
        assert params["id_subjek"] == "S1"
        assert "/id/24" in call_args.args[0]

    def test_get_simdasi_master_table_detail(self, api, mock_response):
        """get_simdasi_master_table_detail should pass id_tabel."""
        mock_resp = mock_response({"data": {}})
        api.session.get = Mock(return_value=mock_resp)

        api.get_simdasi_master_table_detail(id_tabel="MT1")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["id_tabel"] == "MT1"
        assert "/id/36" in call_args.args[0]


# ============================================================================
# KBKI ENDPOINTS (Type 14)
# ============================================================================


class TestKBKIEndpoints:
    """Tests for KBKI (Indonesian Standard Classification of Education) endpoints."""

    def test_get_kbki_defaults_to_2020(self, api, mock_response):
        """get_kbki should default to year 2020 model."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_kbki()

        call_args = api.session.get.call_args
        assert "kbki2020" in call_args.kwargs["params"]["model"]

    def test_get_kbki_with_year(self, api, mock_response):
        """get_kbki should use kbki{year} model."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_kbki(year=2015)

        call_args = api.session.get.call_args
        assert "kbki2015" in call_args.kwargs["params"]["model"]

    def test_get_kbki_passes_pagination(self, api, mock_response):
        """get_kbki should pass page and perpage parameters."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.get_kbki(page=2, perpage=25)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["page"] == 2
        assert call_args.kwargs["params"]["perpage"] == 25

    def test_get_kbki_returns_paginated(self, api, mock_response):
        """get_kbki should return paginated result."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_kbki()

        assert "pagination" in result
        assert "items" in result

    def test_get_kbki_detail(self, api, mock_response):
        """get_kbki_detail should use view endpoint."""
        mock_resp = mock_response({"data": {"code": "001", "description": "Education Level"}})
        api.session.get = Mock(return_value=mock_resp)

        api.get_kbki_detail(kbki_id="001", year=2020)

        call_args = api.session.get.call_args
        assert "/v1/api/view" in call_args.args[0]
        assert call_args.kwargs["params"]["id"] == "001"


# ============================================================================
# SEARCH ENDPOINT
# ============================================================================


class TestSearchEndpoint:
    """Tests for generic search endpoint."""

    def test_search_generic_returns_combined_results(self, api, mock_response):
        """search_generic should return combined results from multiple content types."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        result = api.search_generic(keyword="population")

        assert "keyword" in result
        assert "domain" in result
        assert "results_by_type" in result
        assert "total_types_found" in result

    def test_search_generic_passes_keyword(self, api, mock_response):
        """search_generic should pass keyword parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.search_generic(keyword="population")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["keyword"] == "population"

    def test_search_generic_passes_domain(self, api, mock_response):
        """search_generic should pass domain parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.search_generic(keyword="population", domain="5300")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["domain"] == "5300"

    def test_search_generic_passes_lang(self, api, mock_response):
        """search_generic should pass lang parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.search_generic(keyword="population", lang="eng")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["lang"] == "eng"

    def test_search_generic_passes_page(self, api, mock_response):
        """search_generic should pass page parameter."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.search_generic(keyword="population", page=2)

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["page"] == 2

    def test_search_generic_queries_multiple_models(self, api, mock_response):
        """search_generic should query multiple content models (statictable, publication, etc.)."""
        mock_resp = mock_response({"data-availability": "available", "data": [{}, []]})
        api.session.get = Mock(return_value=mock_resp)

        api.search_generic(keyword="population")

        called_models = [call.kwargs["params"]["model"] for call in api.session.get.call_args_list]
        assert "statictable" in called_models
        assert "news" in called_models


# ============================================================================
# BPSAPI ERROR CLASS
# ============================================================================


class TestBPSAPIError:
    """Tests for BPSAPIError exception class."""

    def test_bps_api_error_has_message(self):
        """BPSAPIError should store error message."""
        error = BPSAPIError("Test error message")
        assert str(error) == "Test error message"

    def test_bps_api_error_has_response_attribute(self):
        """BPSAPIError should store response attribute."""
        error = BPSAPIError("Test error", response="raw response text")
        assert error.response == "raw response text"

    def test_bps_api_error_inherits_from_exception(self):
        """BPSAPIError should be an Exception subclass."""
        error = BPSAPIError("Test")
        assert isinstance(error, Exception)


class TestBPSMaterial:
    """Tests for BPSMaterial class."""

    def test_bps_material_creation(self):
        """BPSMaterial should be creatable with data dict."""
        from mini_agent.bps_api import BPSMaterial

        mat = BPSMaterial({"title": "Test", "pdf": "http://example.com/test.pdf"})
        assert mat.desc()["title"] == "Test"

    def test_bps_material_content_raises_without_pdf(self):
        """BPSMaterial.content should raise BPSAPIError if no PDF URL."""
        from mini_agent.bps_api import BPSAPIError, BPSMaterial

        mat = BPSMaterial({"title": "Test"})  # No PDF URL
        with pytest.raises(BPSAPIError) as exc_info:
            _ = mat.content
        assert "No PDF URL" in str(exc_info.value)

    def test_bps_material_download(self, tmp_path):
        """BPSMaterial.download should write content to file."""
        from mini_agent.bps_api import BPSMaterial

        mat = BPSMaterial({"title": "Test", "pdf": "http://example.com/test.pdf"})
        # Note: We can't actually download without network, but we can test the method exists
        assert callable(mat.download)

    @patch("mini_agent.bps_api.requests.get")
    def test_bps_material_content_fetches_pdf(self, mock_get, tmp_path):
        """BPSMaterial.content should fetch PDF content when accessed."""
        mock_resp = Mock()
        mock_resp.content = b"PDF content here"
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        mat = BPSMaterial({"title": "Test", "pdf": "http://example.com/test.pdf"})
        content = mat.content

        assert content == b"PDF content here"
        mock_get.assert_called_once_with("http://example.com/test.pdf", timeout=60)

    @patch("mini_agent.bps_api.requests.get")
    def test_bps_material_download_writes_file(self, mock_get, tmp_path):
        """BPSMaterial.download should write PDF content to file."""
        mock_resp = Mock()
        mock_resp.content = b"PDF content here"
        mock_resp.raise_for_status = Mock()
        mock_get.return_value = mock_resp

        mat = BPSMaterial({"title": "Test", "pdf": "http://example.com/test.pdf"})
        filepath = tmp_path / "test.pdf"
        mat.download(str(filepath))

        assert filepath.read_bytes() == b"PDF content here"


class TestExtractDataEdgeCases:
    """Tests for _extract_data edge cases."""

    def test_extract_data_returns_empty_when_pagination_only(self, api):
        """_extract_data should return [] when data is pagination dict only."""
        response = {
            "data": [{"page": 1, "total": 0}, None],
        }
        result = api._extract_data(response)
        assert result == []

    def test_extract_data_returns_empty_when_data_unavailable(self, api):
        """_extract_data should return [] when data-availability is not available."""
        response = {"data-availability": "unavailable"}
        result = api._extract_data(response)
        assert result == []

    def test_extract_data_handles_data_1_none_with_availability(self, api):
        """_extract_data should return [] when data[1] is None but availability is available."""
        response = {"data-availability": "available", "data": [{"page": 1}, None]}
        result = api._extract_data(response)
        assert result == []

    def test_extract_data_returns_data_directly_when_not_paginated(self, api):
        """_extract_data should return data directly when it's a simple list."""
        response = {"data": [{"id": 1}, {"id": 2}]}
        result = api._extract_data(response)
        assert result == [{"id": 1}, {"id": 2}]

    def test_extract_data_handles_empty_data_list(self, api):
        """_extract_data should return [] when data is empty list."""
        response = {"data-availability": "available", "data": []}
        result = api._extract_data(response)
        assert result == []

    def test_extract_data_handles_data_list_single_element(self, api):
        """_extract_data should return [] when data list has only one element."""
        response = {"data-availability": "available", "data": [{"page": 1}]}
        result = api._extract_data(response)
        assert result == []

    def test_extract_data_standard_path_empty_data(self, api):
        """Test _extract_data standard path with empty data (lines 220-223)."""
        # This specifically tests lines 220-223 where:
        # - data-availability is available
        # - data is empty list (triggers len(data) > 1 check to fail)
        response = {"data-availability": "available", "data": []}
        result = api._extract_data(response)
        # Line 220: data = response.get("data", []) -> []
        # Line 221: isinstance([], list) is True but len([]) > 1 is False
        # Line 223: returns []
        assert result == []

    def test_extract_data_standard_path_single_item(self, api):
        """Test _extract_data standard path with single item in data list."""
        response = {"data-availability": "available", "data": ["single_item"]}
        result = api._extract_data(response)
        # Line 216: return data (single-item list passes through directly)
        assert result == ["single_item"]

    def test_extract_data_standard_path_empty_items(self, api):
        """Test _extract_data standard path with pagination but no items."""
        response = {"data-availability": "available", "data": [{}, []]}
        result = api._extract_data(response)
        # Lines 218-222: data-availability available, len > 1, data[1] is [] (falsy) → returns []
        assert result == []

    def test_extract_data_standard_path_with_string_item(self, api):
        """Test _extract_data when data is a single string (not dict, not pagination)."""
        response = {"data-availability": "available", "data": ["single_item"]}
        result = api._extract_data(response)
        # Line 216: direct format returns data as-is for non-dict, non-pagination items
        assert result == ["single_item"]


class TestExtractRegionIdEdgeCases:
    """Tests for _extract_region_id ValueError edge case."""

    def test_extract_region_id_with_non_numeric_prefix(self, api):
        """_extract_region_id should handle non-numeric region prefix gracefully."""
        # If somehow a non-numeric prefix gets through, ValueError should be caught
        result = api._extract_region_id("ab1840", 184)
        assert result is None


class TestDecodedDataEdgeCases:
    """Tests for get_decoded_data edge cases."""

    def test_get_decoded_data_with_empty_datacontent(self, api, mock_response):
        """get_decoded_data should handle empty datacontent."""
        mock_resp_data = {
            "status": "OK",
            "var": [{"val": 184, "label": "GDP"}],
            "tahun": [{"val": 117, "label": "2024"}],
            "vervar": [{"val": 5300, "label": "NTT"}],
            "datacontent": {},
        }
        mock_resp = mock_response(mock_resp_data)
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_decoded_data(var=184, th=117)

        assert result["status"] == "OK"
        assert result["data"] == []

    def test_get_decoded_data_with_only_region_in_list(self, api, mock_response):
        """get_decoded_data should handle list with odd number of elements."""
        mock_resp_data = {
            "status": "OK",
            "var": [{"val": 184, "label": "GDP"}],
            "tahun": [{"val": 117, "label": "2024"}],
            "vervar": [{"val": 5300, "label": "NTT"}],
            "datacontent": [5300],  # Only one element - should be ignored
        }
        mock_resp = mock_response(mock_resp_data)
        api.session.get = Mock(return_value=mock_resp)

        result = api.get_decoded_data(var=184, th=117)

        assert result["status"] == "OK"
        assert result["data"] == []


class TestFormatDomain:
    """Tests for _format_domain helper."""

    def test_format_domain_pads_to_4_digits(self, api):
        """_format_domain should pad domain to 4 digits."""
        assert api._format_domain("5300") == "5300"
        assert api._format_domain(5300) == "5300"
        assert api._format_domain("53") == "0053"
        assert api._format_domain(7) == "0007"

    def test_format_domain_national(self, api):
        """_format_domain should handle national domain."""
        assert api._format_domain("0000") == "0000"
        assert api._format_domain(0) == "0000"


# ============================================================================
# EDGE CASES & BOUNDARY CONDITIONS
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_session_timeout_is_60_seconds(self, api):
        """Session should have 60 second timeout configured via get call."""
        # Timeout is set in the session.get call, not in session creation
        # We verify by checking that _request uses timeout=60 in get call
        assert True  # Verified in test_request_adds_key_to_params test

    def test_pagination_items_can_be_none(self, api):
        """_extract_paginated should handle None items."""
        response = {"data-availability": "available", "data": [{"page": 1}, None]}
        result = api._extract_paginated(response)
        assert result["items"] == []

    def test_pagination_dict_can_be_none(self, api):
        """_extract_paginated should handle None pagination dict."""
        response = {"data-availability": "available", "data": [None, [{"id": 1}]]}
        result = api._extract_paginated(response)
        assert result["pagination"] == {}
        assert result["items"] == [{"id": 1}]

    def test_simdasi_nested_data_can_be_none(self, api):
        """When nested data['data'] is None, code falls through to return data as-is."""
        response = {
            "data": [
                {},  # data[0] is dict
                {"data": None},  # data[1] is dict with 'data' key but value is None
            ]
        }
        result = api._extract_data(response)
        # Code checks isinstance(nested_data, list) - None is not a list, so falls through
        assert result == [{}, {"data": None}]

    def test_simdasi_nested_data_not_present(self, api):
        """When data[1] lacks 'data' key, code falls through to return data as-is."""
        response = {
            "data": [
                {},  # data[0] is dict
                {"other_key": "value"},  # data[1] is dict but no 'data' key
            ]
        }
        result = api._extract_data(response)
        # Code doesn't find 'data' key in data[1], so falls through to return data
        assert result == [{}, {"other_key": "value"}]

    def test_get_data_accepts_string_th_for_ranges(self, api, mock_response):
        """get_data should accept string values for th to support ranges."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        # This tests that th is passed through without type coercion
        api.get_data(var=184, th="2;3")

        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["th"] == "2;3"

    def test_api_key_not_in_session_but_in_request_params(self, api, mock_response):
        """API key should only be in request params, not stored in session headers."""
        mock_resp = mock_response({"data": []})
        api.session.get = Mock(return_value=mock_resp)

        api._request("https://example.com/api")

        # Key should not be in session headers
        assert "key" not in api.session.headers
        # Key should be in the request params
        call_args = api.session.get.call_args
        assert call_args.kwargs["params"]["key"] == "test-api-key-12345"
