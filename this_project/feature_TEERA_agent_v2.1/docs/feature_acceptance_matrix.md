# Feature Acceptance Matrix

## Feature A: Query Planning

| Dimension | Requirement |
| --- | --- |
| file | `src/scholar_retrieval/query_planning.py` |
| API | `build_query_plan(query: str, max_expansions: int = 5) -> QueryPlan` |
| behavior | strip query, expand 2-5 academic queries, dedupe |
| required signals | method-oriented expansion, evidence-oriented expansion |
| tests | `tests/test_query_planning.py` |

## Feature B: Evidence Lock

| Dimension | Requirement |
| --- | --- |
| file | `src/scholar_retrieval/evidence_lock.py` |
| API | `lock_best_evidence(query: str, items: list[EvidenceItem], threshold: float = 0.8) -> EvidenceLedger` |
| behavior | rank evidence, lock best candidate, stop search after lock |
| required signals | `target_locked_stop_search`, no lock below threshold |
| tests | `tests/test_evidence_lock.py` |

## Shared Acceptance

Both features must:

- pass baseline tests plus feature tests
- write only inside assigned workspace
- produce `artifacts/change_manifest.json`
- produce `artifacts/acceptance_report.json`
- keep management policy unmodified

