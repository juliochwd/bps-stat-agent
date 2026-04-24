"""Tests for normalized BPS resource retrieval."""

import pytest

from mini_agent.bps_models import BPSResolvedResource, BPSResourceType
from mini_agent.bps_resource_retriever import BPSResourceRetriever


class FakeAPIClient:
    """Minimal WebAPI client for publication and press release tests."""

    def get_publications(self, *, domain: str, keyword: str | None = None, page: int = 1):
        """Return one publication match."""
        assert domain == "5300"
        assert keyword == "kemiskinan"
        assert page == 1
        return {
            "items": [
                {
                    "pub_id": "pub-123",
                    "title": "Kemiskinan NTT 2025",
                    "rl_date": "2025-01-01",
                    "pdf": "https://example.com/pub.pdf",
                }
            ]
        }

    def get_publication_detail(self, pub_id: str, domain: str = "0000", lang: str = "ind"):
        """Return publication detail for the chosen publication."""
        assert pub_id == "pub-123"
        assert domain == "5300"
        return {
            "data": {
                "title": "Kemiskinan NTT 2025",
                "abstract": "Ringkasan publikasi kemiskinan NTT.",
                "pdf": "https://example.com/pub.pdf",
                "cover": "https://example.com/pub-cover.jpg",
                "rl_date": "2025-01-01",
            }
        }

    def get_press_releases(self, *, domain: str, keyword: str | None = None, page: int = 1):
        """Return one press release match."""
        assert domain == "5300"
        assert keyword == "inflasi"
        assert page == 1
        return {
            "items": [
                {
                    "brs_id": 42,
                    "title": "Perkembangan Inflasi NTT",
                    "rl_date": "2025-02-01",
                }
            ]
        }

    def get_press_release_detail(self, brs_id: int, domain: str = "0000", lang: str = "ind"):
        """Return press release detail for the chosen release."""
        assert brs_id == 42
        assert domain == "5300"
        return {
            "data": {
                "title": "Perkembangan Inflasi NTT",
                "abstract": "Inflasi bulan berjalan di NTT.",
                "pdf": "https://example.com/brs.pdf",
                "rl_date": "2025-02-01",
            }
        }


class UnusedTableRetriever:
    """Guard to ensure non-table tests do not hit table retrieval."""

    async def get_table_data(self, table_id: int, domain: str = "5300"):
        raise AssertionError("Table retrieval should not be used in this test")


class FallbackTableRetriever:
    """Table retriever that fails for the first candidate and succeeds for fallback."""

    def __init__(self):
        self.calls: list[int] = []

    async def get_table_data(self, table_id: int, domain: str = "5300"):
        self.calls.append(table_id)
        if table_id == 230:
            raise ValueError("Static table detail missing structured data")

        class Result:
            title = "Inflasi Bulanan Menurut Kelompok Pengeluaran"
            headers = ["wilayah", "nilai"]
            data = [{"wilayah": "Kota Kupang", "nilai": "0,81"}]

            @staticmethod
            def summary() -> str:
                return "Fallback table summary"

        return Result()


@pytest.mark.asyncio
async def test_retrieve_publication_returns_normalized_detail():
    """Publication retrieval should use WebAPI list+detail and normalize the payload."""
    retriever = BPSResourceRetriever(
        api_client=FakeAPIClient(),
        table_retriever=UnusedTableRetriever(),
    )
    resolved = BPSResolvedResource(
        resource_type=BPSResourceType.PUBLICATION,
        title="Kemiskinan NTT 2025",
        url="https://ntt.bps.go.id/publication/2025/01/01/abc/kemiskinan-ntt.html",
        domain_code="5300",
        retrieval_candidates=["webapi_detail", "search_result_only"],
    )

    result = await retriever.retrieve(query="kemiskinan", resolved=resolved)

    assert result["resource_type"] == "publication"
    assert result["retrieval_method"] == "webapi_detail"
    assert result["title"] == "Kemiskinan NTT 2025"
    assert result["artifacts"][0]["type"] == "pdf"


@pytest.mark.asyncio
async def test_retrieve_press_release_returns_normalized_detail():
    """Press release retrieval should use WebAPI list+detail and normalize the payload."""
    retriever = BPSResourceRetriever(
        api_client=FakeAPIClient(),
        table_retriever=UnusedTableRetriever(),
    )
    resolved = BPSResolvedResource(
        resource_type=BPSResourceType.PRESSRELEASE,
        title="Perkembangan Inflasi NTT",
        url="https://ntt.bps.go.id/pressrelease/2025/02/01/abc/inflasi-ntt.html",
        domain_code="5300",
        retrieval_candidates=["webapi_detail", "search_result_only"],
    )

    result = await retriever.retrieve(query="inflasi", resolved=resolved)

    assert result["resource_type"] == "pressrelease"
    assert result["retrieval_method"] == "webapi_detail"
    assert result["summary"] == "Inflasi bulan berjalan di NTT."
    assert result["artifacts"][0]["url"] == "https://example.com/brs.pdf"


@pytest.mark.asyncio
async def test_retrieve_table_falls_back_to_keyword_static_table_search():
    """Table retrieval should retry via keyword static-table search when direct detail fails."""

    class FallbackAPIClient(FakeAPIClient):
        def __init__(self):
            self.keywords: list[str] = []

        def get_static_tables(self, *, domain: str, keyword: str | None = None, page: int = 1):
            assert domain == "5300"
            assert page == 1
            self.keywords.append(keyword or "")
            if keyword != "inflasi":
                return {"items": []}
            return {
                "items": [
                    {
                        "table_id": 1501,
                        "title": "Inflasi Bulanan Menurut Kelompok Pengeluaran",
                    }
                ]
            }

    api_client = FallbackAPIClient()
    table_retriever = FallbackTableRetriever()
    retriever = BPSResourceRetriever(
        api_client=api_client,
        table_retriever=table_retriever,
    )
    resolved = BPSResolvedResource(
        resource_type=BPSResourceType.TABLE,
        title="Jumlah Peserta KB Aktif",
        url="https://ntt.bps.go.id/statistics-table/2/MjMwIzI=/jumlah-peserta-kb-aktif.html",
        domain_code="5300",
        retrieval_candidates=["static_table_detail", "webapi_structured", "search_result_only"],
        identifiers={"table_id": "230"},
    )

    result = await retriever.retrieve(query="inflasi NTT", resolved=resolved)

    assert api_client.keywords == ["inflasi NTT", "inflasi"]
    assert table_retriever.calls == [230, 1501]
    assert result["retrieval_method"] == "static_table_search_fallback"
    assert result["rows"] == [{"wilayah": "Kota Kupang", "nilai": "0,81"}]
