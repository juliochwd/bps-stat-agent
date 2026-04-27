"""Tests for the AllStats-first BPS orchestrator."""

from dataclasses import dataclass

import pytest

from mini_agent.bps_models import BPSResolvedResource, BPSResourceType
from mini_agent.bps_orchestrator import BPSOrchestrator


@dataclass
class FakeSearchResult:
    """Minimal AllStats-like result object for orchestrator tests."""

    title: str
    url: str
    snippet: str
    content_type: str
    domain_code: str
    domain_name: str = "Nusa Tenggara Timur"
    year: str = "2025"

    def to_dict(self) -> dict[str, str]:
        """Return a dict representation mirroring the production object."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "content_type": self.content_type,
            "domain_code": self.domain_code,
            "domain_name": self.domain_name,
            "year": self.year,
        }


@dataclass
class FakeSearchResponse:
    """Search response wrapper with a results list."""

    results: list[FakeSearchResult]


class FakeSearchClient:
    """Search client that records calls."""

    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    async def search(self, **kwargs) -> FakeSearchResponse:
        """Record the search call and return one fake result."""
        self.calls.append(kwargs)
        return FakeSearchResponse(
            results=[
                FakeSearchResult(
                    title="Inflasi NTT",
                    url="https://ntt.bps.go.id/id/statistics-table/2/abc/inflasi-ntt.html",
                    snippet="Laju inflasi NTT",
                    content_type="table",
                    domain_code="5300",
                )
            ]
        )


def fake_resolver(result: dict[str, str]) -> BPSResolvedResource:
    """Return a resolved table resource."""
    assert result["content_type"] == "table"
    return BPSResolvedResource(
        resource_type=BPSResourceType.TABLE,
        title=result["title"],
        url=result["url"],
        domain_code=result["domain_code"],
        retrieval_candidates=["static_table_detail"],
        identifiers={"table_id": "123"},
        metadata=result,
    )


class FakeRetriever:
    """Retriever that records the resolved resource it receives."""

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def __call__(self, *, query: str, resolved: BPSResolvedResource) -> dict[str, object]:
        """Return a normalized answer payload."""
        self.calls.append({"query": query, "resolved": resolved})
        return {
            "query": query,
            "resource_type": resolved.resource_type.value,
            "domain_code": resolved.domain_code,
            "title": resolved.title,
            "source_url": resolved.url,
            "retrieval_method": "webapi_structured",
            "rows": [{"wilayah": "NTT", "nilai": 1.23}],
            "columns": ["wilayah", "nilai"],
            "errors": [],
        }


@pytest.mark.asyncio
async def test_answer_query_uses_allstats_first_then_normalizes():
    """The orchestrator must search AllStats before calling the retriever."""
    search_client = FakeSearchClient()
    retriever = FakeRetriever()
    orchestrator = BPSOrchestrator(
        search_client=search_client,
        resolver=fake_resolver,
        retriever=retriever,
    )

    result = await orchestrator.answer_query("inflasi NTT", domain="5300")

    assert search_client.calls == [{"keyword": "inflasi NTT", "domain": "5300", "content": "all"}]
    assert retriever.calls[0]["query"] == "inflasi NTT"
    assert result["query"] == "inflasi NTT"
    assert result["retrieval_method"] == "webapi_structured"
    assert result["rows"] == [{"wilayah": "NTT", "nilai": 1.23}]


@pytest.mark.asyncio
async def test_answer_query_injects_requested_domain_when_result_domain_missing():
    """Search results without domain_code should inherit the requested domain."""

    class MissingDomainSearchClient(FakeSearchClient):
        async def search(self, **kwargs) -> FakeSearchResponse:
            self.calls.append(kwargs)
            return FakeSearchResponse(
                results=[
                    FakeSearchResult(
                        title="Inflasi NTT",
                        url="https://ntt.bps.go.id/id/statistics-table/2/abc/inflasi-ntt.html",
                        snippet="Laju inflasi NTT",
                        content_type="table",
                        domain_code="",
                    )
                ]
            )

    def resolver_with_assertion(result: dict[str, str]) -> BPSResolvedResource:
        assert result["domain_code"] == "5300"
        return fake_resolver(result)

    orchestrator = BPSOrchestrator(
        search_client=MissingDomainSearchClient(),
        resolver=resolver_with_assertion,
        retriever=FakeRetriever(),
    )

    result = await orchestrator.answer_query("inflasi NTT", domain="5300")

    assert result["domain_code"] == "5300"


@pytest.mark.asyncio
async def test_answer_query_prefers_more_relevant_search_result():
    """The orchestrator should rank candidates instead of blindly taking the first result."""

    class RankedSearchClient(FakeSearchClient):
        async def search(self, **kwargs) -> FakeSearchResponse:
            self.calls.append(kwargs)
            return FakeSearchResponse(
                results=[
                    FakeSearchResult(
                        title="Produksi Jagung menurut Kabupaten/Kota",
                        url="https://ntt.bps.go.id/id/statistics-table/2/abc/jagung.html",
                        snippet="Data jagung provinsi",
                        content_type="table",
                        domain_code="5300",
                    ),
                    FakeSearchResult(
                        title="Inflasi Menurut Kabupaten/Kota di NTT",
                        url="https://ntt.bps.go.id/id/statistics-table/2/def/inflasi.html",
                        snippet="Data inflasi NTT terbaru",
                        content_type="table",
                        domain_code="5300",
                    ),
                ]
            )

    seen_titles: list[str] = []

    def resolver_with_title_capture(result: dict[str, str]) -> BPSResolvedResource:
        seen_titles.append(result["title"])
        return fake_resolver(result)

    orchestrator = BPSOrchestrator(
        search_client=RankedSearchClient(),
        resolver=resolver_with_title_capture,
        retriever=FakeRetriever(),
    )

    await orchestrator.answer_query("inflasi NTT", domain="5300")

    assert seen_titles == ["Inflasi Menurut Kabupaten/Kota di NTT"]
