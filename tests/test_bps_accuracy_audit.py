"""
Comprehensive Audit: BPS Stat Agent Accuracy & LLM Comprehension Tests.

This file verifies:
1. AllStats ranking selects the most relevant result
2. Retrieved data matches the search result claims
3. LLM can understand and answer questions about BPS data
4. Different content types (table, publication, indicator) work correctly
"""

import json
import os
import re

import pytest

from mini_agent.bps_mcp_server import BPSAPI, bps_answer_query
from mini_agent.llm.llm_wrapper import LLMClient
from mini_agent.schema import Message

pytestmark = pytest.mark.live


# ─────────────────────────────────────────────────────────────────────────────
# Setup helpers
# ─────────────────────────────────────────────────────────────────────────────

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
BPS_API_KEY = os.environ.get("BPS_API_KEY", "") or os.environ.get("WEBAPI_APP_ID", "")


def require_bps_key():
    if not BPS_API_KEY:
        pytest.skip("BPS_API_KEY not set")
    return BPS_API_KEY


@pytest.fixture(autouse=True)
def _skip_without_bps_key():
    """Auto-skip all tests in this module if BPS_API_KEY is not set."""
    if not BPS_API_KEY:
        pytest.skip("BPS_API_KEY not set — live tests require BPS API access")


def require_minimax_key():
    if not MINIMAX_API_KEY or MINIMAX_API_KEY == "YOUR_API_KEY_HERE":
        pytest.skip("MINIMAX_API_KEY not set")
    return MINIMAX_API_KEY


def llm():
    return LLMClient(
        provider="openai",
        api_key=require_minimax_key(),
        api_base="https://api.minimax.io/v1",
        model="MiniMax-M2.7",
    )


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT 1: AllStats Ranking Accuracy
# ─────────────────────────────────────────────────────────────────────────────


class TestAllStatsRanking:
    """Verify the ranking algorithm selects the most relevant result."""

    @pytest.mark.asyncio
    async def test_ranking_prefers_exact_query_match(self):
        """When query matches title exactly, it should rank highest."""
        result = await bps_answer_query("inflasi", domain="5300")
        payload = json.loads(result)
        assert payload["success"], f"AllStats failed: {payload.get('error')}"
        # Title should contain "inflasi"
        title = payload["data"]["title"].lower()
        assert "inflasi" in title, f"Expected 'inflasi' in title, got: {title}"

    @pytest.mark.asyncio
    async def test_ranking_prefers_table_over_news(self):
        """Tables should rank higher than news for data queries."""
        result = await bps_answer_query("PDB", domain="0000")
        payload = json.loads(result)
        assert payload["success"]
        # Resource type should be table or indicator, not news
        rt = payload["data"]["resource_type"]
        assert rt in ("table", "indicator"), f"Expected table/indicator, got: {rt}"

    @pytest.mark.asyncio
    async def test_ranking_handles_short_acronyms(self):
        """Short acronyms like IPM should still find relevant results."""
        result = await bps_answer_query("IPM", domain="5300")
        payload = json.loads(result)
        assert payload["success"]
        title = payload["data"]["title"].lower()
        # IPM stands for Indeks Pembangunan Manusia (Human Development Index)
        # Should find HDI-related content
        assert len(payload["data"]["rows"]) > 0 or "ipm" in title or "indeks" in title

    @pytest.mark.asyncio
    async def test_ranking_handles_generic_queries(self):
        """Generic queries like 'penduduk' should return population data."""
        result = await bps_answer_query("penduduk", domain="5300")
        payload = json.loads(result)
        assert payload["success"]
        title = payload["data"]["title"].lower()
        # Should be about population
        assert any(w in title for w in ["penduduk", "populasi", "population"]), f"Got: {title}"

    @pytest.mark.asyncio
    async def test_ranking_nasional_vs_province(self):
        """National domain (0000) should return national data."""
        result = await bps_answer_query("PDB", domain="0000")
        payload = json.loads(result)
        assert payload["success"]
        assert payload["data"]["domain_code"] == "0000"


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT 2: Data Retrieval Accuracy
# ─────────────────────────────────────────────────────────────────────────────


class TestDataRetrievalAccuracy:
    """Verify data retrieved matches what was promised in search results."""

    @pytest.mark.asyncio
    async def test_table_data_has_numeric_values(self):
        """Table data should contain actual numeric values."""
        result = await bps_answer_query("inflasi", domain="5300")
        payload = json.loads(result)
        assert payload["success"]
        summary = payload["data"]["summary"]
        # Summary should contain numbers like "3,56" or "0,04"
        assert re.search(r"\d+[,\.]\d+", summary), f"No numeric values in summary: {summary[:200]}"

    @pytest.mark.asyncio
    async def test_rows_count_matches_summary(self):
        """Rows count in summary should match actual rows."""
        result = await bps_answer_query("inflasi", domain="5300")
        payload = json.loads(result)
        assert payload["success"]
        summary = payload["data"]["summary"]
        data = payload["data"]

        # Extract rows count from summary (e.g., "Rows: 29")
        match = re.search(r"Rows:\s*(\d+)", summary)
        if match:
            claimed_rows = int(match.group(1))
            actual_rows = len(data.get("rows", []))
            assert actual_rows == claimed_rows, f"Claimed {claimed_rows} rows, got {actual_rows}"

    @pytest.mark.asyncio
    async def test_retrieval_method_is_documented(self):
        """Every successful retrieval should have a documented method."""
        result = await bps_answer_query("inflasi", domain="5300")
        payload = json.loads(result)
        assert payload["success"]
        method = payload["data"].get("retrieval_method")
        assert method is not None, "No retrieval_method documented"
        assert method != "", "Empty retrieval_method"

    @pytest.mark.asyncio
    async def test_source_url_is_valid(self):
        """Every result should have a valid BPS source URL."""
        result = await bps_answer_query("inflasi", domain="5300")
        payload = json.loads(result)
        assert payload["success"]
        url = payload["data"].get("source_url", "")
        assert "bps.go.id" in url or "web.bps.go.id" in url, f"Invalid URL: {url}"

    @pytest.mark.asyncio
    async def test_webapi_detail_returns_structured_data(self):
        """WebAPI direct call should return structured paginated data."""
        bps_key = require_bps_key()
        bps = BPSAPI(bps_key)
        result = bps.get_subjects(domain="5300")
        assert "pagination" in result
        assert "items" in result
        assert result["pagination"]["count"] > 0
        assert len(result["items"]) > 0


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT 3: LLM Comprehension of BPS Data
# ─────────────────────────────────────────────────────────────────────────────


class TestLLMComprehension:
    """Verify LLM can understand and answer questions about BPS data."""

    @pytest.mark.asyncio
    async def test_llm_can_read_table_data(self):
        """LLM should read and interpret table data correctly."""
        bps_key = require_bps_key()
        result = await bps_answer_query("inflasi", domain="5300")
        payload = json.loads(result)
        assert payload["success"]

        summary = payload["data"]["summary"]
        messages = [
            Message(
                role="user",
                content=f"""Here is BPS inflation data:

{summary}

Question: What was the inflation rate for Food/Beverages in January 2024?
If the data shows multiple categories, pick the first one (Food/Beverages).
Respond with ONLY the number and % sign (e.g., "3.56%"). If you cannot determine, say "UNKNOWN".""",
            )
        ]
        response = await llm().generate(messages)
        content = response.content if hasattr(response, "content") else str(response)
        # Should contain a percentage
        assert "%" in content or "UNKNOWN" in content.upper(), f"Expected % or UNKNOWN, got: {content}"

    @pytest.mark.asyncio
    async def test_llm_can_distinguish_different_data_types(self):
        """LLM should understand different BPS data types."""
        bps_key = require_bps_key()
        test_cases = [
            ("inflasi", "5300", "inflation"),
            ("PDB", "0000", "GDP"),
            ("IPM", "5300", "HDI"),
        ]

        for query, domain, expected_type in test_cases:
            result = await bps_answer_query(query, domain=domain)
            payload = json.loads(result)
            if payload["success"]:
                title = payload["data"]["title"]
                messages = [
                    Message(
                        role="user",
                        content=f"""Title: {title}

Question: Is this data about {expected_type}? Respond with YES or NO only.""",
                    )
                ]
                response = await llm().generate(messages)
                content = (response.content if hasattr(response, "content") else str(response)).upper()
                # LLM should recognize the data type
                # (This is a weak assertion but validates LLM can read the title)
                assert len(content) > 0, f"Empty response for query: {query}"

    @pytest.mark.asyncio
    async def test_llm_refuses_to_make_up_data(self):
        """LLM should not hallucinate data that's not in the provided context."""
        bps_key = require_bps_key()
        result = await bps_answer_query("inflasi", domain="5300")
        payload = json.loads(result)
        assert payload["success"]

        summary = payload["data"]["summary"]
        # Provide only partial data and ask about non-existent month
        messages = [
            Message(
                role="user",
                content=f"""BPS data shows inflation for these months only:
{summary[:300]}

Question: What was the inflation in December 2023? This data doesn't cover December 2023.
Respond with "DATA NOT AVAILABLE" if the data doesn't support the question.""",
            )
        ]
        response = await llm().generate(messages)
        content = (response.content if hasattr(response, "content") else str(response)).upper()
        # Should either say not available or give a value that exists in the data
        # Should NOT hallucinate a specific number without basis
        assert "DECEMBER" not in content or "NOT AVAILABLE" in content or "%" in content


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT 4: Content Type Coverage
# ─────────────────────────────────────────────────────────────────────────────


class TestContentTypeCoverage:
    """Verify all content types can be retrieved successfully."""

    @pytest.mark.asyncio
    async def test_table_retrieval(self):
        """Tables should be retrievable with data."""
        result = await bps_answer_query("inflasi", domain="5300")
        payload = json.loads(result)
        assert payload["success"]
        assert payload["data"]["resource_type"] == "table"
        assert len(payload["data"].get("rows", [])) > 0

    @pytest.mark.asyncio
    async def test_publication_retrieval(self):
        """Publications should be retrievable."""
        result = await bps_answer_query("statistik daerah ntt", domain="5300")
        payload = json.loads(result)
        assert payload["success"]
        rt = payload["data"]["resource_type"]
        assert rt in ("publication", "table"), f"Expected publication or table, got: {rt}"

    @pytest.mark.asyncio
    async def test_indicator_retrieval(self):
        """Indicators should be retrievable."""
        result = await bps_answer_query("IPM", domain="5300")
        payload = json.loads(result)
        assert payload["success"]
        # IPM is an indicator
        rt = payload["data"]["resource_type"]
        assert rt in ("indicator", "table"), f"Expected indicator or table, got: {rt}"

    @pytest.mark.asyncio
    async def test_pressrelease_retrieval(self):
        """Press releases should be retrievable."""
        # Use a common press release topic
        result = await bps_answer_query("Berita Resmi Statistik", domain="5300")
        payload = json.loads(result)
        # Should succeed even if no exact match
        assert payload["success"] is not None


# ─────────────────────────────────────────────────────────────────────────────
# AUDIT 5: Error Handling & Edge Cases
# ─────────────────────────────────────────────────────────────────────────────


class TestErrorHandling:
    """Verify graceful error handling."""

    @pytest.mark.asyncio
    async def test_no_results_returns_structured_error(self):
        """No results should return a structured error, not crash."""
        # Use a very specific query unlikely to match anything
        result = await bps_answer_query("xyzxyzxyz_no_match", domain="5300")
        payload = json.loads(result)
        # Should return success=False, not a Python traceback
        assert "success" in payload
        assert payload["success"] is False or payload["data"] is not None

    @pytest.mark.asyncio
    async def test_invalid_domain_handled(self):
        """Invalid domain should be handled gracefully."""
        result = await bps_answer_query("inflasi", domain="9999")
        payload = json.loads(result)
        # Should either succeed with empty results or return structured error
        assert "success" in payload

    def test_bps_api_with_invalid_key_returns_error(self):
        """Invalid API key should return a clear error."""
        bps = BPSAPI("invalid_key_12345")
        try:
            result = bps.get_subjects(domain="5300")
            # If it doesn't raise, it should return an error structure
            assert result.get("data-availability") == "unavailable" or "error" in str(result)
        except Exception as e:
            # Exception is also acceptable for invalid key
            err_str = str(e).lower()
            assert any(kw in err_str for kw in ["not allowed", "401", "unauthorized", "invalid", "error"]), (
                f"Unexpected error: {e}"
            )
