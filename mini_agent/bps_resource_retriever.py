"""Shared retrieval logic for normalized BPS resources."""

import re
from typing import Any

from mini_agent.bps_models import BPSResolvedResource, BPSResourceType
from mini_agent.bps_normalization import build_normalized_response


class BPSResourceRetriever:
    """Retrieve typed BPS resources and normalize the result."""

    def __init__(self, api_client: Any, table_retriever: Any):
        self._api_client = api_client
        self._table_retriever = table_retriever

    async def retrieve(self, *, query: str, resolved: BPSResolvedResource) -> dict[str, Any]:
        """Retrieve a resolved resource through the best supported path."""
        if resolved.resource_type is BPSResourceType.TABLE:
            return await self._retrieve_table(query=query, resolved=resolved)
        if resolved.resource_type is BPSResourceType.PUBLICATION:
            return await self._retrieve_publication(query=query, resolved=resolved)
        if resolved.resource_type is BPSResourceType.PRESSRELEASE:
            return await self._retrieve_press_release(query=query, resolved=resolved)
        return build_normalized_response(
            query=query,
            resource_type=resolved.resource_type.value,
            domain_code=resolved.domain_code,
            title=resolved.title,
            source_url=resolved.url,
            retrieval_method="search_result_only",
            summary=resolved.metadata.get("snippet", ""),
            domain_name=str(resolved.metadata.get("domain_name", "")),
            metadata=resolved.metadata,
        )

    async def _retrieve_table(
        self,
        *,
        query: str,
        resolved: BPSResolvedResource,
    ) -> dict[str, Any]:
        table_id = resolved.identifiers.get("table_id")
        if table_id is None:
            return build_normalized_response(
                query=query,
                resource_type=resolved.resource_type.value,
                domain_code=resolved.domain_code,
                title=resolved.title,
                source_url=resolved.url,
                retrieval_method="search_result_only",
                summary=resolved.metadata.get("snippet", ""),
                domain_name=str(resolved.metadata.get("domain_name", "")),
                metadata=resolved.metadata,
                errors=[{"type": "incomplete_resource", "message": "Missing table_id"}],
            )

        try:
            table = await self._table_retriever.get_table_data(
                int(table_id),
                domain=resolved.domain_code,
            )
            return build_normalized_response(
                query=query,
                resource_type=resolved.resource_type.value,
                domain_code=resolved.domain_code,
                title=table.title,
                source_url=resolved.url,
                retrieval_method="static_table_detail",
                summary=table.summary(),
                rows=table.data,
                columns=table.headers,
                domain_name=str(resolved.metadata.get("domain_name", "")),
                metadata=resolved.metadata,
            )
        except Exception as exc:
            fallback_items: list[dict[str, Any]] = []
            for keyword in self._iter_fallback_keywords(query, resolved.domain_code):
                fallback_listing = self._api_client.get_static_tables(
                    domain=resolved.domain_code,
                    keyword=keyword,
                    page=1,
                )
                fallback_items = fallback_listing.get("items", [])
                if fallback_items:
                    break
            selected = self._select_best_match(
                fallback_items,
                resolved.title,
                "table_id",
            )
            if selected is None:
                selected = fallback_items[0] if fallback_items else None
            if selected is None or "table_id" not in selected:
                return build_normalized_response(
                    query=query,
                    resource_type=resolved.resource_type.value,
                    domain_code=resolved.domain_code,
                    title=resolved.title,
                    source_url=resolved.url,
                    retrieval_method="search_result_only",
                    summary=resolved.metadata.get("snippet", ""),
                    domain_name=str(resolved.metadata.get("domain_name", "")),
                    metadata=resolved.metadata,
                    errors=[
                        {
                            "type": "not_found",
                            "message": f"Table detail failed and no fallback table found: {exc}",
                        }
                    ],
                )

            table = await self._table_retriever.get_table_data(
                int(selected["table_id"]),
                domain=resolved.domain_code,
            )
            return build_normalized_response(
                query=query,
                resource_type=resolved.resource_type.value,
                domain_code=resolved.domain_code,
                title=table.title,
                source_url=resolved.url,
                retrieval_method="static_table_search_fallback",
                summary=table.summary(),
                rows=table.data,
                columns=table.headers,
                domain_name=str(resolved.metadata.get("domain_name", "")),
                metadata={"search_result": resolved.metadata, "fallback_table": selected},
            )

    @staticmethod
    def _iter_fallback_keywords(query: str, domain_code: str) -> list[str]:
        """Generate progressively simpler fallback keywords for static-table search."""
        keywords = [query.strip()]
        lowered = query.casefold()

        aliases_by_domain = {
            "5300": ["ntt", "nusa tenggara timur"],
            "0000": ["nasional", "indonesia", "pusat"],
        }
        aliases = aliases_by_domain.get(domain_code, [])

        simplified = lowered
        for alias in aliases:
            simplified = re.sub(rf"\b{re.escape(alias)}\b", " ", simplified)
        simplified = " ".join(simplified.split())
        if simplified and simplified not in keywords:
            keywords.append(simplified)

        return keywords

    async def _retrieve_publication(
        self,
        *,
        query: str,
        resolved: BPSResolvedResource,
    ) -> dict[str, Any]:
        listing = self._api_client.get_publications(
            domain=resolved.domain_code,
            keyword=query,
            page=1,
        )
        items = listing.get("items", [])
        selected = self._select_best_match(items, resolved.title, "pub_id")
        if selected is None:
            return self._search_only_fallback(query=query, resolved=resolved)

        detail = self._api_client.get_publication_detail(
            selected["pub_id"],
            domain=resolved.domain_code,
        )
        data = detail.get("data", {})
        artifacts = []
        if data.get("pdf"):
            artifacts.append({"type": "pdf", "url": data["pdf"]})
        if data.get("cover"):
            artifacts.append({"type": "cover", "url": data["cover"]})
        return build_normalized_response(
            query=query,
            resource_type=resolved.resource_type.value,
            domain_code=resolved.domain_code,
            title=data.get("title", resolved.title),
            source_url=resolved.url,
            retrieval_method="webapi_detail",
            summary=data.get("abstract", ""),
            period=data.get("rl_date"),
            domain_name=str(resolved.metadata.get("domain_name", "")),
            metadata={"listing": selected, "detail": data},
            artifacts=artifacts,
        )

    async def _retrieve_press_release(
        self,
        *,
        query: str,
        resolved: BPSResolvedResource,
    ) -> dict[str, Any]:
        listing = self._api_client.get_press_releases(
            domain=resolved.domain_code,
            keyword=query,
            page=1,
        )
        items = listing.get("items", [])
        selected = self._select_best_match(items, resolved.title, "brs_id")
        if selected is None:
            return self._search_only_fallback(query=query, resolved=resolved)

        detail = self._api_client.get_press_release_detail(
            selected["brs_id"],
            domain=resolved.domain_code,
        )
        data = detail.get("data", {})
        artifacts = []
        if data.get("pdf"):
            artifacts.append({"type": "pdf", "url": data["pdf"]})
        return build_normalized_response(
            query=query,
            resource_type=resolved.resource_type.value,
            domain_code=resolved.domain_code,
            title=data.get("title", resolved.title),
            source_url=resolved.url,
            retrieval_method="webapi_detail",
            summary=data.get("abstract", ""),
            period=data.get("rl_date"),
            domain_name=str(resolved.metadata.get("domain_name", "")),
            metadata={"listing": selected, "detail": data},
            artifacts=artifacts,
        )

    @staticmethod
    def _select_best_match(
        items: list[dict[str, Any]],
        title: str,
        identifier_key: str,
    ) -> dict[str, Any] | None:
        normalized_title = title.casefold()
        for item in items:
            if identifier_key not in item:
                continue
            if str(item.get("title", "")).casefold() == normalized_title:
                return item
        for item in items:
            if identifier_key in item:
                return item
        return None

    @staticmethod
    def _search_only_fallback(
        *,
        query: str,
        resolved: BPSResolvedResource,
    ) -> dict[str, Any]:
        return build_normalized_response(
            query=query,
            resource_type=resolved.resource_type.value,
            domain_code=resolved.domain_code,
            title=resolved.title,
            source_url=resolved.url,
            retrieval_method="search_result_only",
            summary=resolved.metadata.get("snippet", ""),
            domain_name=str(resolved.metadata.get("domain_name", "")),
            metadata=resolved.metadata,
            errors=[{"type": "not_found", "message": "No matching WebAPI detail found"}],
        )
