"""Shared data models for retrieval feature experiments."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class QueryPlan:
    original_query: str
    expanded_queries: list[str]
    rationale: str


@dataclass(frozen=True)
class EvidenceItem:
    title: str
    source_id: str
    abstract: str = ""
    score: float = 0.0


@dataclass
class EvidenceLedger:
    query: str
    items: list[EvidenceItem] = field(default_factory=list)
    locked_item: EvidenceItem | None = None
    stop_reason: str | None = None

