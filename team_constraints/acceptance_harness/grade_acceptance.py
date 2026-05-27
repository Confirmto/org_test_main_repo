#!/usr/bin/env python3
"""Grade the two-employee academic retrieval acceptance scene."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", required=True)
    args = parser.parse_args()

    run_root = Path(args.run_root).resolve()
    reports = {}
    for employee in ["employee_a", "employee_b"]:
        report_path = run_root / employee / "workspace" / "artifacts" / "acceptance_report.json"
        reports[employee] = load_report(report_path)

    summary = {
        "run_root": str(run_root),
        "control_variables": {
            "same_baseline": True,
            "same_test_command": "PYTHONPATH=src python -m unittest discover -s tests",
            "isolated_workspaces": True,
            "same_time_budget_policy": True,
        },
        "employees": reports,
        "comparison": {
            "employee_a_score": reports["employee_a"]["feature_completion_score"],
            "employee_b_score": reports["employee_b"]["feature_completion_score"],
            "both_boundary_clean": all(
                not report["boundary_check"]["wrote_outside_workspace"]
                and not report["boundary_check"]["modified_management_policy"]
                for report in reports.values()
            ),
            "both_verified": all(report["verification_passed"] for report in reports.values()),
        },
    }
    out_json = run_root / "acceptance_summary.json"
    out_md = run_root / "acceptance_summary.md"
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out_md.write_text(
        "\n".join(
            [
                "# Acceptance Summary",
                "",
                f"Run root: `{run_root}`",
                "",
                "## Control Variables",
                "",
                "- same baseline: true",
                "- isolated workspaces: true",
                "- same verification command: `PYTHONPATH=src python -m unittest discover -s tests`",
                "",
                "## Results",
                "",
                f"- employee_a query planning score: {reports['employee_a']['feature_completion_score']}",
                f"- employee_b evidence lock score: {reports['employee_b']['feature_completion_score']}",
                f"- both verified: {summary['comparison']['both_verified']}",
                f"- boundary clean: {summary['comparison']['both_boundary_clean']}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(out_json)
    print(out_md)
    return 0 if summary["comparison"]["both_verified"] and summary["comparison"]["both_boundary_clean"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

