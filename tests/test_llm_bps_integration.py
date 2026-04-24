"""
Integration tests for BPS Stat Agent with MiniMax LLM.

These tests verify the full pipeline: MiniMax LLM + BPS AllStats + WebAPI.
Requires MINIMAX_API_KEY and BPS_API_KEY environment variables.
"""

import json
import os

import pytest

from mini_agent.bps_mcp_server import BPSAPI, bps_answer_query
from mini_agent.llm.llm_wrapper import LLMClient
from mini_agent.schema import Message


pytestmark = pytest.mark.live


def require_minimax_api_key() -> str:
    """Return the MiniMax API key or skip the test."""
    key = os.environ.get("MINIMAX_API_KEY") or os.environ.get("api_key")
    if not key or key == "YOUR_API_KEY_HERE":
        pytest.skip("MINIMAX_API_KEY is not set")
    return key


def require_bps_api_key() -> str:
    """Return the BPS API key or skip the test."""
    key = os.environ.get("BPS_API_KEY") or os.environ.get("WEBAPI_APP_ID")
    if not key:
        pytest.skip("BPS_API_KEY is not set")
    return key


class TestMiniMaxLLMIntegration:
    """Test MiniMax LLM with BPS data."""

    async def test_llm_basic(self):
        """MiniMax LLM should respond to basic prompts."""
        api_key = require_minimax_api_key()
        llm = LLMClient(
            provider="openai",
            api_key=api_key,
            api_base="https://api.minimax.io/v1",
            model="MiniMax-M2.7",
        )
        messages = [Message(role="user", content="Say exactly: MINIMAX_WORKS")]
        result = await llm.generate(messages)
        content = result.content if hasattr(result, "content") else str(result)
        assert "MINIMAX_WORKS" in content, f"Expected MINIMAX_WORKS in response, got: {content}"

    async def test_llm_with_bps_context(self):
        """MiniMax LLM should answer questions about BPS data."""
        api_key = require_minimax_api_key()
        bps_key = require_bps_api_key()

        # Get BPS data first
        bps_result = await bps_answer_query("inflasi NTT", domain="5300")
        bps_payload = json.loads(bps_result)
        assert bps_payload["success"], "BPS query should succeed"

        bps_data = bps_payload["data"]
        summary = bps_data.get("summary", "")

        # Use LLM to analyze the BPS data
        llm = LLMClient(
            provider="openai",
            api_key=api_key,
            api_base="https://api.minimax.io/v1",
            model="MiniMax-M2.7",
        )
        messages = [
            Message(
                role="user",
                content=f"""Based on this BPS data:

{summary}

Question: What was the inflation rate for Food/Beverages in January 2024?
Respond with just the number and unit (e.g., '3.56%').""",
            )
        ]
        result = await llm.generate(messages)
        content = result.content if hasattr(result, "content") else str(result)
        # Should contain a number followed by %
        assert "%" in content or any(c.isdigit() for c in content), f"Expected numeric response with %, got: {content}"


class TestBPSAllStatsPipeline:
    """Test BPS AllStats-first pipeline."""

    async def test_allstats_search_ntt(self):
        """AllStats should find inflation data for NTT."""
        bps_key = require_bps_api_key()
        result = await bps_answer_query("inflasi NTT", domain="5300")
        payload = json.loads(result)
        assert payload["success"] is True
        assert payload["data"]["domain_code"] == "5300"
        assert payload["data"]["resource_type"] == "table"

    async def test_allstats_search_nasional(self):
        """AllStats should find national data."""
        bps_key = require_bps_api_key()
        result = await bps_answer_query("PDB", domain="0000")
        payload = json.loads(result)
        assert payload["success"] is True
        assert payload["data"]["domain_code"] == "0000"

    async def test_allstats_search_publication(self):
        """AllStats should find publications."""
        bps_key = require_bps_api_key()
        result = await bps_answer_query("statistik daerah NTT", domain="5300")
        payload = json.loads(result)
        assert payload["success"] is True
        assert payload["data"]["resource_type"] in ("publication", "table")


class TestBPSWebAPIDirect:
    """Test direct BPS WebAPI calls."""

    def test_bps_api_subjects(self):
        """BPS WebAPI should return subjects."""
        api_key = require_bps_api_key()
        bps = BPSAPI(api_key)
        result = bps.get_subjects(domain="5300")
        assert result["pagination"]["count"] > 0
        assert result["items"]

    def test_bps_api_variables(self):
        """BPS WebAPI should return variables for a subject."""
        api_key = require_bps_api_key()
        bps = BPSAPI(api_key)
        result = bps.get_variables(domain="5300")
        assert result["pagination"]["count"] > 0

    def test_bps_api_periods(self):
        """BPS WebAPI should return time periods."""
        api_key = require_bps_api_key()
        bps = BPSAPI(api_key)
        result = bps.get_periods(domain="5300")
        assert result["pagination"]["count"] > 0

    def test_bps_api_domains(self):
        """BPS WebAPI should return domain list."""
        api_key = require_bps_api_key()
        bps = BPSAPI(api_key)
        result = bps.get_domains(type="prov")
        assert len(result) > 0
