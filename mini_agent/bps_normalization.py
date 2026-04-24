"""Normalization helpers for BPS retrieval payloads."""

from typing import Any


def build_normalized_response(
    *,
    query: str,
    resource_type: str,
    domain_code: str,
    title: str,
    source_url: str,
    retrieval_method: str,
    summary: str = "",
    period: str | None = None,
    rows: list[dict[str, Any]] | None = None,
    columns: list[str] | None = None,
    domain_name: str = "",
    metadata: dict[str, Any] | None = None,
    artifacts: list[dict[str, Any]] | None = None,
    errors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the canonical BPS response payload."""
    return {
        "query": query,
        "resource_type": resource_type,
        "domain_code": domain_code,
        "domain_name": domain_name,
        "title": title,
        "summary": summary,
        "period": period,
        "source_url": source_url,
        "retrieval_method": retrieval_method,
        "confidence": "medium",
        "metadata": metadata or {},
        "columns": columns or [],
        "rows": rows or [],
        "artifacts": artifacts or [],
        "errors": errors or [],
    }
