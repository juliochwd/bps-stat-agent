"""Comprehensive coverage tests for mini_agent/bps_data_retriever.py.

Tests BPSDataRetriever and BPSDataResult with mocked BPSAPI.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


# ===========================================================================
# BPSDataResult tests
# ===========================================================================


class TestBPSDataResult:
    """Test BPSDataResult dataclass."""

    @pytest.fixture
    def sample_result(self):
        from mini_agent.bps_data_retriever import BPSDataResult
        return BPSDataResult(
            table_id=1501,
            title="Inflasi NTT 2024",
            subject="Harga",
            update_date="2024-01-01",
            headers=["Wilayah", "Inflasi", "Tahun"],
            data=[
                {"Wilayah": "Kupang", "Inflasi": "3.5", "Tahun": "2024"},
                {"Wilayah": "Ende", "Inflasi": "2.8", "Tahun": "2024"},
                {"Wilayah": "Maumere", "Inflasi": "3.1", "Tahun": "2024"},
            ],
            raw_rows=[
                ["Kupang", "3.5", "2024"],
                ["Ende", "2.8", "2024"],
                ["Maumere", "3.1", "2024"],
            ],
        )

    def test_to_json(self, sample_result):
        json_str = sample_result.to_json()
        data = json.loads(json_str)
        assert data["table_id"] == 1501
        assert data["title"] == "Inflasi NTT 2024"
        assert len(data["data"]) == 3
        assert data["headers"] == ["Wilayah", "Inflasi", "Tahun"]

    def test_to_csv(self, sample_result):
        csv_str = sample_result.to_csv()
        lines = csv_str.strip().split("\n")
        assert len(lines) == 4  # header + 3 data rows
        assert "Wilayah" in lines[0]
        assert "Kupang" in lines[1]

    def test_summary(self, sample_result):
        summary = sample_result.summary()
        assert "1501" in summary
        assert "Inflasi NTT 2024" in summary
        assert "Rows: 3" in summary
        assert "Columns: 3" in summary

    def test_preview(self, sample_result):
        preview = sample_result._preview(max_rows=2)
        lines = preview.strip().split("\n")
        assert len(lines) == 3  # header + 2 rows


# ===========================================================================
# BPSDataRetriever tests
# ===========================================================================


class TestBPSDataRetriever:
    """Test BPSDataRetriever with mocked BPSAPI."""

    @pytest.fixture
    def mock_api(self):
        mock = MagicMock()
        mock.get_static_tables.return_value = {
            "items": [
                {"table_id": 1501, "title": "Inflasi NTT", "subj": "Harga", "updt_date": "2024-01-01", "size": "10KB"},
                {"table_id": 1502, "title": "GDP NTT", "subj": "Ekonomi", "updt_date": "2024-02-01", "size": "15KB"},
            ]
        }
        mock.get_static_table_detail.return_value = {
            "data": {
                "title": "Inflasi NTT 2024",
                "subcsa": "Harga",
                "updt_date": "2024-01-01",
                "table": "<table><tr><th>Wilayah</th><th>Inflasi</th></tr><tr><td>Kupang</td><td>3.5</td></tr><tr><td>Ende</td><td>2.8</td></tr></table>",
            }
        }
        return mock

    @pytest.fixture
    def retriever(self, mock_api):
        with patch("mini_agent.bps_data_retriever.BPSAPI", return_value=mock_api):
            from mini_agent.bps_data_retriever import BPSDataRetriever
            return BPSDataRetriever(api_key="test-key")

    def test_init_with_api_key(self, mock_api):
        with patch("mini_agent.bps_data_retriever.BPSAPI", return_value=mock_api):
            from mini_agent.bps_data_retriever import BPSDataRetriever
            retriever = BPSDataRetriever(api_key="my-key")
            assert retriever.api_key == "my-key"

    def test_init_no_api_key(self, mock_api):
        with patch("mini_agent.bps_data_retriever.BPSAPI", return_value=mock_api), \
             patch.dict("os.environ", {"BPS_API_KEY": "", "WEBAPI_APP_ID": ""}, clear=False):
            from mini_agent.bps_data_retriever import BPSDataRetriever
            with pytest.raises(ValueError, match="API key required"):
                BPSDataRetriever(api_key="")

    def test_init_from_env(self, mock_api):
        with patch("mini_agent.bps_data_retriever.BPSAPI", return_value=mock_api), \
             patch.dict("os.environ", {"BPS_API_KEY": "env-key"}, clear=False):
            from mini_agent.bps_data_retriever import BPSDataRetriever
            retriever = BPSDataRetriever()
            assert retriever.api_key == "env-key"

    @pytest.mark.asyncio
    async def test_search(self, retriever, mock_api):
        results = await retriever.search("inflasi", domain="5300")
        assert len(results) == 2
        assert results[0]["table_id"] == 1501
        assert results[0]["title"] == "Inflasi NTT"
        mock_api.get_static_tables.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_empty(self, retriever, mock_api):
        mock_api.get_static_tables.return_value = {"items": []}
        results = await retriever.search("nonexistent")
        assert results == []

    @pytest.mark.asyncio
    async def test_get_table_data(self, retriever, mock_api):
        result = await retriever.get_table_data(table_id=1501, domain="5300")
        assert result.table_id == 1501
        assert result.title == "Inflasi NTT 2024"
        assert len(result.headers) == 2
        assert len(result.data) == 2
        assert result.data[0]["Wilayah"] == "Kupang"

    @pytest.mark.asyncio
    async def test_search_and_get_data(self, retriever, mock_api):
        results = await retriever.search_and_get_data("inflasi", domain="5300", max_tables=1)
        assert len(results) == 1
        assert results[0].table_id == 1501

    @pytest.mark.asyncio
    async def test_search_and_get_data_error_handling(self, retriever, mock_api, capsys):
        """Test that errors in individual table fetches don't crash the whole flow."""
        mock_api.get_static_table_detail.side_effect = Exception("API error")
        results = await retriever.search_and_get_data("inflasi", max_tables=2)
        assert results == []


# ===========================================================================
# HTML table parsing tests
# ===========================================================================


class TestHTMLTableParsing:
    """Test _parse_html_table method."""

    @pytest.fixture
    def retriever(self):
        mock_api = MagicMock()
        with patch("mini_agent.bps_data_retriever.BPSAPI", return_value=mock_api):
            from mini_agent.bps_data_retriever import BPSDataRetriever
            return BPSDataRetriever(api_key="test")

    def test_simple_table(self, retriever):
        html = "<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>"
        headers, rows = retriever._parse_html_table(html)
        assert headers == ["A", "B"]
        assert rows == [["1", "2"]]

    def test_empty_table(self, retriever):
        html = "<table></table>"
        headers, rows = retriever._parse_html_table(html)
        assert headers == []
        assert rows == []

    def test_table_with_html_entities(self, retriever):
        """Test that HTML entities are unescaped properly."""
        html = "<table><tr><th>Col1</th><th>Col2</th></tr><tr><td>Name&amp;Value</td><td>A&lt;B</td></tr></table>"
        headers, rows = retriever._parse_html_table(html)
        assert len(headers) == 2
        assert len(rows) == 1

    def test_table_with_nested_tags(self, retriever):
        """Test that nested HTML tags are stripped from cell content."""
        html = "<table><tr><th>H1</th><th>H2</th></tr><tr><td><b>Bold</b></td><td><span>Text</span></td></tr></table>"
        headers, rows = retriever._parse_html_table(html)
        assert len(headers) == 2
        assert len(rows) == 1

    def test_normalize_cell(self):
        from mini_agent.bps_data_retriever import BPSDataRetriever
        assert BPSDataRetriever._normalize_cell("  hello   world  ") == "hello world"
        assert BPSDataRetriever._normalize_cell("non\xa0breaking") == "non breaking"

    def test_multi_row_header(self, retriever):
        html = """<table>
            <tr><th>Col1</th><th>Col2</th><th>Col3</th></tr>
            <tr><td>A</td><td>B</td><td>C</td></tr>
            <tr><td>D</td><td>E</td><td>F</td></tr>
        </table>"""
        headers, rows = retriever._parse_html_table(html)
        assert len(headers) == 3
        assert len(rows) == 2
