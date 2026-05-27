# Employee A Task: Query Planning

## Goal

Implement query planning for academic retrieval.

## Required Feature

Create `src/scholar_retrieval/query_planning.py` with:

```python
def build_query_plan(query: str, max_expansions: int = 5) -> QueryPlan:
    ...
```

## Expected Behavior

- Preserve the original query.
- Strip extra whitespace.
- Generate 2-5 expanded academic search queries.
- Include at least one method-oriented expansion.
- Include at least one evidence-oriented expansion.
- Deduplicate expansions.

## Required Tests

Create `tests/test_query_planning.py`.

## Completion Evidence

Write `artifacts/change_manifest.json` and `artifacts/acceptance_report.json`.

