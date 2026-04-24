"""Helpers for classifying and resolving BPS search results."""

from mini_agent.bps_models import BPSResolvedResource, BPSResourceType


def classify_search_result(result: dict) -> BPSResolvedResource:
    """Classify an AllStats-style search result into a BPS resource."""
    content_type = str(result.get("content_type") or "").lower()
    url = str(result.get("url") or "")
    title = str(result.get("title") or "")
    domain_code = str(result.get("domain_code") or "0000")

    if content_type == "publication" or "/publication/" in url:
        resource_type = BPSResourceType.PUBLICATION
        candidates = ["webapi_detail", "detail_page_parse", "search_result_only"]
    elif content_type == "pressrelease" or "/press-release/" in url or "/pressrelease/" in url:
        resource_type = BPSResourceType.PRESSRELEASE
        candidates = ["webapi_detail", "detail_page_parse", "search_result_only"]
    elif content_type == "table" or "/statistics-table/" in url or "/table/" in url:
        resource_type = BPSResourceType.TABLE
        candidates = ["static_table_detail", "webapi_structured", "search_result_only"]
    elif content_type == "news" or "/news/" in url:
        resource_type = BPSResourceType.NEWS
        candidates = ["webapi_detail", "detail_page_parse", "search_result_only"]
    elif content_type == "infographic" or "/infographic/" in url:
        resource_type = BPSResourceType.INFOGRAPHIC
        candidates = ["webapi_detail", "detail_page_parse", "search_result_only"]
    elif content_type == "glosarium" or "/glossary/" in url or "/glosarium/" in url:
        resource_type = BPSResourceType.GLOSSARY
        candidates = ["webapi_detail", "search_result_only"]
    else:
        resource_type = BPSResourceType.UNKNOWN
        candidates = ["search_result_only"]

    return BPSResolvedResource(
        resource_type=resource_type,
        title=title,
        url=url,
        domain_code=domain_code,
        retrieval_candidates=candidates,
        metadata=dict(result),
    )
