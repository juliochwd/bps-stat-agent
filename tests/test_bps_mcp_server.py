"""Tests for BPS MCP server helpers."""

import json

import pytest

from mini_agent import bps_mcp_server


@pytest.mark.asyncio
async def test_bps_answer_query_returns_normalized_json(monkeypatch):
    """The MCP helper should wrap orchestrator output in a success payload."""

    async def fake_answer_query(*, keyword: str, domain: str, content: str, api_key=None):
        assert keyword == "inflasi"
        assert domain == "5300"
        assert content == "all"
        return {
            "query": keyword,
            "resource_type": "table",
            "rows": [{"nilai": 1.2}],
            "errors": [],
        }

    monkeypatch.setattr(bps_mcp_server, "_answer_query", fake_answer_query, raising=False)

    raw = await bps_mcp_server.bps_answer_query("inflasi", domain="5300")
    payload = json.loads(raw)

    assert payload["success"] is True
    assert payload["data"]["resource_type"] == "table"
    assert payload["data"]["rows"] == [{"nilai": 1.2}]


@pytest.mark.asyncio
async def test_bps_get_indicators_rejects_unsupported_year_arg(monkeypatch):
    """Indicator endpoint should return an error when year is provided (unsupported)."""

    class FakeAPIClient:
        def get_indicators(self, *, domain: str, page: int = 1):
            return {"items": [{"title": "Inflasi"}], "pagination": {"page": 2}}

    monkeypatch.setattr(bps_mcp_server, "get_api_client", lambda api_key=None: FakeAPIClient())

    raw = await bps_mcp_server.bps_get_indicators(domain="5300", year=2025, page=2)
    payload = json.loads(raw)

    assert payload["success"] is False
    assert "year" in payload["error"].lower()


@pytest.mark.asyncio
async def test_build_mcp_server_registers_core_tools():
    """The MCP server factory should expose the main BPS tools."""
    server = bps_mcp_server.build_mcp_server()
    tools = await server.list_tools()
    tool_names = {tool.name for tool in tools}

    assert "bps_answer_query" in tool_names
    assert "bps_search_allstats" in tool_names
    assert "bps_get_table_data" in tool_names


def test_resolve_search_result_extracts_table_id_from_encoded_url():
    """Encoded statistics-table URLs should yield a usable numeric table_id."""
    resolved = bps_mcp_server._resolve_search_result(
        {
            "title": "Produksi Jagung menurut Kabupaten/Kota",
            "url": "https://ntt.bps.go.id/statistics-table/2/MTQ3MCMy/produksi-jagung-menurut-kabupaten-kota.html",
            "content_type": "Indikator",
            "domain_code": "5300",
        }
    )

    assert resolved.resource_type.value == "table"
    assert resolved.identifiers["table_id"] == "1470"
