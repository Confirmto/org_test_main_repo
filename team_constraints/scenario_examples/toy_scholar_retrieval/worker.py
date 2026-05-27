#!/usr/bin/env python3
"""Simulated scenario worker for controlled acceptance tests."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, env=env)


class Boundary:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()

    def check(self, path: Path) -> Path:
        resolved = path.resolve()
        if resolved != self.workspace and self.workspace not in resolved.parents:
            raise RuntimeError(f"write outside assigned workspace: {resolved}")
        return resolved

    def write(self, relative: str, content: str) -> None:
        path = self.check(self.workspace / relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def query_planning_role(boundary: Boundary) -> dict:
    boundary.write(
        "src/scholar_retrieval/query_planning.py",
        '''"""Query planning feature for academic retrieval."""\n\nfrom __future__ import annotations\n\nfrom .models import QueryPlan\n\n\ndef _dedupe(items: list[str]) -> list[str]:\n    seen: set[str] = set()\n    result: list[str] = []\n    for item in items:\n        normalized = " ".join(item.split())\n        key = normalized.lower()\n        if normalized and key not in seen:\n            seen.add(key)\n            result.append(normalized)\n    return result\n\n\ndef build_query_plan(query: str, max_expansions: int = 5) -> QueryPlan:\n    clean = " ".join(query.split())\n    if not clean:\n        raise ValueError("query must not be empty")\n    candidates = [\n        clean,\n        f"{clean} systematic review",\n        f"{clean} methods benchmark dataset",\n        f"{clean} evidence citation survey",\n        f"{clean} recent advances",\n    ]\n    expanded = _dedupe(candidates)[:max(1, max_expansions)]\n    return QueryPlan(\n        original_query=clean,\n        expanded_queries=expanded,\n        rationale="Expanded into baseline, method-oriented, evidence-oriented, and recency-oriented academic queries.",\n    )\n''',
    )
    boundary.write(
        "tests/test_query_planning.py",
        '''import unittest\n\nfrom scholar_retrieval.query_planning import build_query_plan\n\n\nclass QueryPlanningTests(unittest.TestCase):\n    def test_build_query_plan_expands_academic_queries(self):\n        plan = build_query_plan("  graph neural network geoscience  ", max_expansions=5)\n        self.assertEqual(plan.original_query, "graph neural network geoscience")\n        self.assertGreaterEqual(len(plan.expanded_queries), 2)\n        self.assertLessEqual(len(plan.expanded_queries), 5)\n        joined = " | ".join(plan.expanded_queries).lower()\n        self.assertIn("methods", joined)\n        self.assertIn("evidence", joined)\n\n    def test_build_query_plan_dedupes_and_bounds(self):\n        plan = build_query_plan("paleoclimate reconstruction", max_expansions=3)\n        self.assertEqual(len(plan.expanded_queries), 3)\n        self.assertEqual(len(plan.expanded_queries), len(set(q.lower() for q in plan.expanded_queries)))\n\n    def test_empty_query_fails(self):\n        with self.assertRaises(ValueError):\n            build_query_plan("   ")\n\n\nif __name__ == "__main__":\n    unittest.main()\n''',
    )
    return {
        "feature": "query_planning",
        "files_changed": [
            "src/scholar_retrieval/query_planning.py",
            "tests/test_query_planning.py",
        ],
        "tests_added": ["tests/test_query_planning.py"],
    }


def evidence_lock_role(boundary: Boundary) -> dict:
    boundary.write(
        "src/scholar_retrieval/evidence_lock.py",
        '''"""Evidence ledger and candidate lock feature."""\n\nfrom __future__ import annotations\n\nfrom .baseline import naive_rank\nfrom .models import EvidenceItem, EvidenceLedger\n\n\ndef lock_best_evidence(\n    query: str,\n    items: list[EvidenceItem],\n    threshold: float = 0.8,\n) -> EvidenceLedger:\n    clean = " ".join(query.split())\n    if not clean:\n        raise ValueError("query must not be empty")\n    ranked = naive_rank(items)\n    ledger = EvidenceLedger(query=clean, items=ranked)\n    if ranked and ranked[0].score >= threshold:\n        ledger.locked_item = ranked[0]\n        ledger.stop_reason = "target_locked_stop_search"\n    else:\n        ledger.stop_reason = "no_candidate_above_threshold_continue_search"\n    return ledger\n''',
    )
    boundary.write(
        "tests/test_evidence_lock.py",
        '''import unittest\n\nfrom scholar_retrieval.evidence_lock import lock_best_evidence\nfrom scholar_retrieval.models import EvidenceItem\n\n\nclass EvidenceLockTests(unittest.TestCase):\n    def test_locks_highest_scoring_evidence(self):\n        items = [\n            EvidenceItem(title="weak", source_id="w", score=0.3),\n            EvidenceItem(title="strong", source_id="s", score=0.91),\n        ]\n        ledger = lock_best_evidence("mineral prospectivity mapping", items)\n        self.assertEqual(ledger.locked_item.title, "strong")\n        self.assertEqual(ledger.stop_reason, "target_locked_stop_search")\n        self.assertEqual([item.title for item in ledger.items], ["strong", "weak"])\n\n    def test_does_not_lock_below_threshold(self):\n        items = [EvidenceItem(title="weak", source_id="w", score=0.5)]\n        ledger = lock_best_evidence("geothermal anomaly", items, threshold=0.8)\n        self.assertIsNone(ledger.locked_item)\n        self.assertEqual(ledger.stop_reason, "no_candidate_above_threshold_continue_search")\n\n    def test_empty_query_fails(self):\n        with self.assertRaises(ValueError):\n            lock_best_evidence("   ", [])\n\n\nif __name__ == "__main__":\n    unittest.main()\n''',
    )
    return {
        "feature": "evidence_lock",
        "files_changed": [
            "src/scholar_retrieval/evidence_lock.py",
            "tests/test_evidence_lock.py",
        ],
        "tests_added": ["tests/test_evidence_lock.py"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker-role", choices=["query_planning", "evidence_lock"], required=True)
    parser.add_argument("--workspace", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    boundary = Boundary(workspace)
    print(f"[{args.worker_role}] assigned workspace: {workspace}")
    print(f"[{args.worker_role}] write boundary: {workspace}")
    print(f"[{args.worker_role}] policy: may read repo contracts; may write only inside workspace")

    if args.worker_role == "query_planning":
        feature_data = query_planning_role(boundary)
    else:
        feature_data = evidence_lock_role(boundary)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(workspace / "src")
    result = run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], workspace, env)
    test_output = result.stdout + result.stderr
    passed = result.returncode == 0
    artifacts = workspace / "artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / "test_output.txt").write_text(test_output, encoding="utf-8")
    report = {
        "worker_role": args.worker_role,
        "assigned_workspace": str(workspace),
        "allowed_write_scope": str(workspace),
        **feature_data,
        "verification_command": "PYTHONPATH=src python -m unittest discover -s tests",
        "verification_passed": passed,
        "boundary_check": {
            "wrote_outside_workspace": False,
            "modified_management_policy": False,
        },
        "feature_completion_score": 1.0 if passed else 0.4,
    }
    (artifacts / "change_manifest.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (artifacts / "acceptance_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(test_output)
    print(f"[{args.worker_role}] verification_passed={passed}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
