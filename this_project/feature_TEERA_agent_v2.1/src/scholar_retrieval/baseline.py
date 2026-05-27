"""Baseline retrieval behavior before employee features."""

from __future__ import annotations

from .models import EvidenceItem


def naive_query(query: str) -> list[str]:
    return [query.strip()]


def naive_rank(items: list[EvidenceItem]) -> list[EvidenceItem]:
    return sorted(items, key=lambda item: item.score, reverse=True)

