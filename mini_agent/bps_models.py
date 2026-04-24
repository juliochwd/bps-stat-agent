"""Shared data models for BPS search and retrieval flows."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class BPSResourceType(str, Enum):
    """Canonical BPS resource types."""

    TABLE = "table"
    PUBLICATION = "publication"
    PRESSRELEASE = "pressrelease"
    NEWS = "news"
    INFOGRAPHIC = "infographic"
    GLOSSARY = "glossary"
    SUBJECT_DATA = "subject_data"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class BPSResolvedResource:
    """Typed search result with ranked retrieval candidates."""

    resource_type: BPSResourceType
    title: str
    url: str
    domain_code: str
    retrieval_candidates: list[str] = field(default_factory=list)
    identifiers: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
