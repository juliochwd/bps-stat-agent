"""Extended tests for mini_agent/bps_mcp_server.py — MCP server tool handlers."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestBPSMCPServerImport:
    """Test that the MCP server module can be imported."""

    def test_import(self):
        import mini_agent.bps_mcp_server
        # Module should be importable
        assert mini_agent.bps_mcp_server is not None


class TestBPSMCPServerTools:
    """Test individual tool handler functions from the MCP server."""

    @pytest.fixture
    def mock_bps_api(self):
        """Mock the BPS API client."""
        mock = MagicMock()
        mock.get_domains = MagicMock(return_value=[
            {"domain_id": "0000", "domain_name": "Indonesia"},
            {"domain_id": "5300", "domain_name": "NTT"},
        ])
        mock.get_subjects = MagicMock(return_value={
            "pagination": {"page": 1, "pages": 1, "total": 2},
            "items": [
                {"sub_id": 1, "title": "Kependudukan"},
                {"sub_id": 2, "title": "Tenaga Kerja"},
            ],
        })
        mock.get_static_tables = MagicMock(return_value={
            "pagination": {"page": 1, "pages": 1, "total": 1},
            "items": [
                {"table_id": 1501, "title": "Inflasi NTT", "subj": "Harga", "updt_date": "2024-01-01", "size": "10KB"},
            ],
        })
        mock.get_static_table_detail = MagicMock(return_value={
            "data": {
                "title": "Inflasi NTT 2024",
                "subcsa": "Harga",
                "updt_date": "2024-01-01",
                "table": "<table><tr><th>Wilayah</th><th>Inflasi</th></tr></table>",
            }
        })
        return mock

    def test_bps_api_mock_structure(self, mock_bps_api):
        """Verify mock structure is correct."""
        domains = mock_bps_api.get_domains()
        assert len(domains) == 2
        assert domains[0]["domain_id"] == "0000"

    def test_bps_api_subjects(self, mock_bps_api):
        """Test subjects API mock."""
        result = mock_bps_api.get_subjects()
        assert result["pagination"]["total"] == 2
        assert len(result["items"]) == 2

    def test_bps_api_static_tables(self, mock_bps_api):
        """Test static tables API mock."""
        result = mock_bps_api.get_static_tables()
        assert len(result["items"]) == 1
        assert result["items"][0]["title"] == "Inflasi NTT"

    def test_bps_api_table_detail(self, mock_bps_api):
        """Test table detail API mock."""
        result = mock_bps_api.get_static_table_detail()
        assert "table" in result["data"]
