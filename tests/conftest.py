"""Shared test fixtures for BPS Stat Agent."""

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def tmp_workspace(tmp_path):
    """Create a temporary workspace directory."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def tmp_memory_file(tmp_path):
    """Create a temporary memory file path for note tools."""
    return str(tmp_path / ".agent_memory.json")


@pytest.fixture
def mock_bps_api():
    """Create a mock BPSAPI client."""
    mock = MagicMock()
    mock.get_domains.return_value = [
        {"domain_id": "0000", "domain_name": "Indonesia", "domain_url": "bps.go.id"},
        {"domain_id": "5300", "domain_name": "Nusa Tenggara Timur", "domain_url": "ntt.bps.go.id"},
    ]
    mock.get_provinces.return_value = [
        {"domain_id": "5300", "domain_name": "Nusa Tenggara Timur"},
    ]
    mock.get_subjects.return_value = {
        "pagination": {"page": 1, "pages": 1, "total": 2},
        "items": [
            {"sub_id": 1, "title": "Kependudukan"},
            {"sub_id": 2, "title": "Tenaga Kerja"},
        ],
    }
    mock.get_static_tables.return_value = {
        "pagination": {"page": 1, "pages": 1, "total": 1},
        "items": [
            {"table_id": 1501, "title": "Inflasi NTT", "subj": "Harga", "updt_date": "2024-01-01", "size": "10KB"},
        ],
    }
    mock.get_static_table_detail.return_value = {
        "data": {
            "title": "Inflasi NTT 2024",
            "subcsa": "Harga",
            "updt_date": "2024-01-01",
            "table": "<table><tr><th>Wilayah</th><th>Inflasi</th></tr><tr><td>Kupang</td><td>3.5</td></tr></table>",
        }
    }
    return mock


@pytest.fixture
def sample_search_result():
    """Sample AllStats search result."""
    return {
        "title": "Inflasi NTT 2024",
        "url": "https://ntt.bps.go.id/statistics-table/5300/1501/inflasi.html",
        "snippet": "Data inflasi Nusa Tenggara Timur tahun 2024",
        "content_type": "table",
        "domain_name": "Nusa Tenggara Timur",
        "domain_code": "5300",
        "year": "2024",
    }
