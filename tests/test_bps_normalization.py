"""Tests for BPS normalization module."""

from mini_agent.bps_normalization import build_normalized_response


class TestBuildNormalizedResponse:
    def test_basic_response(self):
        result = build_normalized_response(
            query="inflasi",
            resource_type="table",
            domain_code="5300",
            title="Inflasi NTT",
            source_url="https://ntt.bps.go.id/table/1",
            retrieval_method="static_table_detail",
        )
        assert result["query"] == "inflasi"
        assert result["resource_type"] == "table"
        assert result["domain_code"] == "5300"
        assert result["title"] == "Inflasi NTT"
        assert result["source_url"] == "https://ntt.bps.go.id/table/1"
        assert result["retrieval_method"] == "static_table_detail"
        assert result["confidence"] == "medium"
        assert result["columns"] == []
        assert result["rows"] == []
        assert result["errors"] == []
        assert result["artifacts"] == []

    def test_with_data(self):
        result = build_normalized_response(
            query="inflasi",
            resource_type="table",
            domain_code="5300",
            title="Inflasi NTT",
            source_url="https://example.com",
            retrieval_method="static_table_detail",
            summary="Data inflasi",
            period="2024",
            rows=[{"wilayah": "Kupang", "value": 3.5}],
            columns=["wilayah", "value"],
            domain_name="NTT",
            metadata={"source": "webapi"},
            artifacts=[{"type": "pdf", "url": "https://example.com/file.pdf"}],
            errors=[{"type": "warning", "message": "partial data"}],
        )
        assert result["summary"] == "Data inflasi"
        assert result["period"] == "2024"
        assert len(result["rows"]) == 1
        assert result["columns"] == ["wilayah", "value"]
        assert result["domain_name"] == "NTT"
        assert result["metadata"]["source"] == "webapi"
        assert len(result["artifacts"]) == 1
        assert len(result["errors"]) == 1

    def test_defaults(self):
        result = build_normalized_response(
            query="test",
            resource_type="unknown",
            domain_code="0000",
            title="Test",
            source_url="",
            retrieval_method="search_result_only",
        )
        assert result["summary"] == ""
        assert result["period"] is None
        assert result["metadata"] == {}
