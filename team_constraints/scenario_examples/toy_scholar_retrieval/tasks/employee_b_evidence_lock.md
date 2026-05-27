# Employee B Task: Evidence Lock

## Goal

Implement an evidence ledger and candidate lock for academic retrieval.

## Required Feature

Create `src/scholar_retrieval/evidence_lock.py` with:

```python
def lock_best_evidence(query: str, items: list[EvidenceItem], threshold: float = 0.8) -> EvidenceLedger:
    ...
```

## Expected Behavior

- Sort evidence by score descending.
- Lock the highest-scoring item when it meets threshold.
- Set `stop_reason` to `target_locked_stop_search` after lock.
- Do not lock when no item meets threshold.
- Preserve all evidence items in the ledger.

## Required Tests

Create `tests/test_evidence_lock.py`.

## Completion Evidence

Write `artifacts/change_manifest.json` and `artifacts/acceptance_report.json`.

