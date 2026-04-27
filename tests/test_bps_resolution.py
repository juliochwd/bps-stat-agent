"""Tests for BPS resolution module."""

from mini_agent.bps_models import BPSResourceType
from mini_agent.bps_resolution import classify_search_result


class TestClassifySearchResult:
    def test_table_by_content_type(self):
        result = classify_search_result(
            {
                "content_type": "table",
                "url": "https://ntt.bps.go.id/some-page",
                "title": "Inflasi NTT",
                "domain_code": "5300",
            }
        )
        assert result.resource_type == BPSResourceType.TABLE
        assert result.title == "Inflasi NTT"
        assert result.domain_code == "5300"

    def test_table_by_url(self):
        result = classify_search_result(
            {
                "content_type": "",
                "url": "https://ntt.bps.go.id/statistics-table/5300/1501/inflasi.html",
                "title": "Inflasi",
            }
        )
        assert result.resource_type == BPSResourceType.TABLE

    def test_publication_by_content_type(self):
        result = classify_search_result(
            {
                "content_type": "publication",
                "url": "https://bps.go.id/pub/123",
                "title": "Statistik Indonesia 2024",
            }
        )
        assert result.resource_type == BPSResourceType.PUBLICATION

    def test_publication_by_url(self):
        result = classify_search_result(
            {
                "content_type": "",
                "url": "https://bps.go.id/publication/2024/01/01/abc123",
                "title": "Pub",
            }
        )
        assert result.resource_type == BPSResourceType.PUBLICATION

    def test_pressrelease_by_content_type(self):
        result = classify_search_result(
            {
                "content_type": "pressrelease",
                "url": "https://bps.go.id/brs/123",
                "title": "BRS Inflasi",
            }
        )
        assert result.resource_type == BPSResourceType.PRESSRELEASE

    def test_pressrelease_by_url(self):
        result = classify_search_result(
            {
                "content_type": "",
                "url": "https://bps.go.id/press-release/2024/01/01/abc",
                "title": "BRS",
            }
        )
        assert result.resource_type == BPSResourceType.PRESSRELEASE

    def test_news_by_content_type(self):
        result = classify_search_result(
            {
                "content_type": "news",
                "url": "https://bps.go.id/news/123",
                "title": "Berita BPS",
            }
        )
        assert result.resource_type == BPSResourceType.NEWS

    def test_infographic_by_content_type(self):
        result = classify_search_result(
            {
                "content_type": "infographic",
                "url": "https://bps.go.id/infographic/123",
                "title": "Infografis",
            }
        )
        assert result.resource_type == BPSResourceType.INFOGRAPHIC

    def test_glossary_by_content_type(self):
        result = classify_search_result(
            {
                "content_type": "glosarium",
                "url": "https://bps.go.id/glossary/abc",
                "title": "Glosarium",
            }
        )
        assert result.resource_type == BPSResourceType.GLOSSARY

    def test_unknown_type(self):
        result = classify_search_result(
            {
                "content_type": "something_else",
                "url": "https://bps.go.id/other",
                "title": "Other",
            }
        )
        assert result.resource_type == BPSResourceType.UNKNOWN

    def test_default_domain_code(self):
        result = classify_search_result(
            {
                "content_type": "table",
                "url": "https://bps.go.id/table/1",
                "title": "Test",
            }
        )
        assert result.domain_code == "0000"

    def test_metadata_preserved(self):
        input_data = {
            "content_type": "table",
            "url": "https://bps.go.id/table/1",
            "title": "Test",
            "snippet": "Some snippet",
            "domain_name": "Indonesia",
        }
        result = classify_search_result(input_data)
        assert result.metadata["snippet"] == "Some snippet"
        assert result.metadata["domain_name"] == "Indonesia"

    def test_retrieval_candidates_for_table(self):
        result = classify_search_result(
            {
                "content_type": "table",
                "url": "https://bps.go.id/table/1",
                "title": "Test",
            }
        )
        assert "static_table_detail" in result.retrieval_candidates

    def test_none_values_handled(self):
        result = classify_search_result(
            {
                "content_type": None,
                "url": None,
                "title": None,
                "domain_code": None,
            }
        )
        assert result.resource_type == BPSResourceType.UNKNOWN
        assert result.title == ""
        assert result.domain_code == "0000"
