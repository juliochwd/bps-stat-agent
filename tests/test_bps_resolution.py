"""Tests for BPS search-result classification."""

from mini_agent.bps_models import BPSResourceType
from mini_agent.bps_resolution import classify_search_result


def test_classify_search_result_detects_publication():
    """Publication results should be routed to the publication detail path first."""
    result = {
        "title": "NTT Dalam Angka 2025",
        "url": "https://ntt.bps.go.id/publication/2025/01/01/abc/ntt-dalam-angka.html",
        "content_type": "publication",
        "domain_code": "5300",
    }

    resolved = classify_search_result(result)

    assert resolved.resource_type is BPSResourceType.PUBLICATION
    assert resolved.domain_code == "5300"
    assert resolved.retrieval_candidates[0] == "webapi_detail"


def test_classify_search_result_detects_table_and_preserves_metadata():
    """Table results should prefer structured retrieval and keep original metadata."""
    result = {
        "title": "Laju Inflasi Bulanan Menurut Kabupaten/Kota",
        "url": "https://ntt.bps.go.id/id/statistics-table/2/abc/laju-inflasi.html",
        "content_type": "table",
        "domain_code": "5300",
        "snippet": "Data inflasi bulanan",
    }

    resolved = classify_search_result(result)

    assert resolved.resource_type is BPSResourceType.TABLE
    assert resolved.retrieval_candidates[0] == "static_table_detail"
    assert resolved.metadata["snippet"] == "Data inflasi bulanan"
