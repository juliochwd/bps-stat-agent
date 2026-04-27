"""AllStats-first orchestration for BPS retrieval flows."""

import re
from collections.abc import Callable
from typing import Any


class BPSOrchestrator:
    """Search first, resolve the top result, then delegate retrieval."""

    def __init__(self, search_client: Any, resolver: Callable[[dict], Any], retriever: Any):
        self._search_client = search_client
        self._resolver = resolver
        self._retriever = retriever

    async def answer_query(
        self,
        query: str,
        domain: str = "5300",
        content: str = "all",
    ) -> dict[str, Any]:
        """Run the AllStats-first query flow and return normalized data."""
        search_response = await self._search_client.search(
            keyword=query,
            domain=domain,
            content=content,
        )
        if not getattr(search_response, "results", None):
            raise ValueError(f"No search results found for query '{query}'")

        first_result = self._select_best_result(query, search_response.results)
        if hasattr(first_result, "to_dict"):
            result_dict = first_result.to_dict()
        elif hasattr(first_result, "__dict__"):
            result_dict = dict(first_result.__dict__)
        else:
            result_dict = dict(first_result)

        if not result_dict.get("domain_code"):
            result_dict["domain_code"] = domain

        resolved = self._resolver(result_dict)
        return await self._retriever(query=query, resolved=resolved)

    @staticmethod
    def _select_best_result(query: str, results: list[Any]) -> Any:
        """Choose the most relevant result for the query."""
        ranked = sorted(
            results,
            key=lambda result: BPSOrchestrator._score_result(query, result),
            reverse=True,
        )
        return ranked[0]

    @staticmethod
    def _score_result(query: str, result: Any) -> tuple[int, int]:
        """Score a result by title/snippet relevance and deterministic tiebreakers."""
        if hasattr(result, "to_dict"):
            payload = result.to_dict()
        elif hasattr(result, "__dict__"):
            payload = dict(result.__dict__)
        else:
            payload = dict(result)

        normalized_query = query.casefold()
        query_tokens = [token for token in re.split(r"\W+", normalized_query) if token]
        title = str(payload.get("title", "")).casefold()
        snippet = str(payload.get("snippet", "")).casefold()
        content_type = str(payload.get("content_type", "")).casefold()

        score = 0
        if normalized_query and normalized_query in title:
            score += 20
        if normalized_query and normalized_query in snippet:
            score += 10

        for token in query_tokens:
            if token in title:
                score += 5
            if token in snippet:
                score += 2

        if content_type in {"table", "indikator", "indicator"}:
            score += 1

        return score, -len(title)
