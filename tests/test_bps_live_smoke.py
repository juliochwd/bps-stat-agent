"""Live smoke tests for upstream BPS integrations."""

import json
import os

import pytest

from mini_agent.bps_api import BPSAPI
from mini_agent.bps_mcp_server import bps_answer_query

pytestmark = pytest.mark.live


def require_bps_api_key() -> str:
    """Return the live BPS API key or skip the test."""
    api_key = os.environ.get("BPS_API_KEY")
    if not api_key:
        pytest.skip("BPS_API_KEY is not set")
    return api_key


def test_live_webapi_subjects_smoke():
    """WebAPI should return NTT subjects with a valid key."""
    api = BPSAPI(require_bps_api_key())

    result = api.get_subjects(domain="5300")

    assert result["pagination"]["count"] > 0
    assert result["items"]


@pytest.mark.asyncio
async def test_live_answer_query_smoke():
    """AllStats-first answer flow should return a normalized success payload."""
    require_bps_api_key()

    raw = await bps_answer_query("inflasi NTT", domain="5300")
    payload = json.loads(raw)

    assert payload["success"] is True
    assert payload["data"]["resource_type"] == "table"
    assert payload["data"]["domain_code"] == "5300"
    assert payload["data"]["rows"]
