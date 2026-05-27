#!/usr/bin/env python3
"""Grade the real workspace + Claude runtime two-worker scene."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def run(cmd: list[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, env=env)


def load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def decision_observability_check(report: dict) -> dict:
    decision = report.get("decision_observability", {})
    required = [
        "intent",
        "expected_user_visible_effect",
        "risk",
        "rollback",
        "prediction",
    ]
    missing = [field for field in required if not str(decision.get(field, "")).strip()]
    return {
        "passed": not missing,
        "missing_fields": missing,
        "prediction": decision.get("prediction", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", required=True)
    args = parser.parse_args()
    run_root = Path(args.run_root).resolve()
    workspace_a = run_root / "employee_a" / "workspace"
    workspace_b = run_root / "employee_b" / "workspace"
    integration = run_root / "integration_workspace"
    if integration.exists():
        shutil.rmtree(integration)
    shutil.copytree(workspace_a, integration)
    shutil.copy2(
        workspace_b / "src" / "scholar_retrieval" / "claude_runtime.py",
        integration / "src" / "scholar_retrieval" / "claude_runtime.py",
    )

    report_a = load_report(workspace_a / "artifacts" / "acceptance_report.json")
    report_b = load_report(workspace_b / "artifacts" / "acceptance_report.json")
    decision_checks = {
        "employee_a": decision_observability_check(report_a),
        "employee_b": decision_observability_check(report_b),
    }

    # Integrate by importing Employee B's runtime and Employee A's indexer from
    # a merged workspace, mirroring what an integrator branch would do.
    env = os.environ.copy()
    env["PYTHONPATH"] = str(integration / "src")
    code = f'''
import json
from pathlib import Path
from scholar_retrieval.claude_runtime import (
    build_frontend_stream_envelopes,
    FakeClaudeAgentSDKStream,
    run_code_analysis_runtime,
    run_isolated_code_analysis_runtime,
    run_managed_isolated_code_analysis_runtime,
    validate_frontend_stream_envelopes,
)
from scholar_retrieval.workspace_index import artifact_dicts

root = Path({str(integration)!r})
stream = FakeClaudeAgentSDKStream([
    {{"type": "message_start", "text": "start"}},
    {{"type": "content_block_delta", "delta": "read workspace"}},
    {{"type": "tool_use", "text": "List files"}},
    {{"type": "tool_result", "text": "3 files"}},
    {{"type": "result", "message": "analysis complete"}},
])
result = run_code_analysis_runtime("integration-session", root, "analyze current session", stream)
artifacts = artifact_dicts(root, "integration-session")
base = root / "isolated_runtime"
session_a = run_isolated_code_analysis_runtime(
    "session-a",
    base,
    "analyze A",
    FakeClaudeAgentSDKStream([{{"type": "result", "message": "A complete"}}]),
)
session_b = run_isolated_code_analysis_runtime(
    "session-b",
    base,
    "analyze B",
    FakeClaudeAgentSDKStream([{{"type": "result", "message": "B complete"}}]),
)
session_a_artifacts = artifact_dicts(Path(session_a["session_workspace_root"]), "session-a")
session_b_artifacts = artifact_dicts(Path(session_b["session_workspace_root"]), "session-b")
completed = run_managed_isolated_code_analysis_runtime(
    "session-completed",
    base,
    "complete normally",
    FakeClaudeAgentSDKStream([{{"type": "result", "message": "done"}}]),
)
cancelled = run_managed_isolated_code_analysis_runtime(
    "session-cancelled",
    base,
    "cancel long run",
    FakeClaudeAgentSDKStream([
        {{"type": "message_start", "text": "start"}},
        {{"type": "content_block_delta", "delta": "working"}},
        {{"type": "content_block_delta", "delta": "still working"}},
    ]),
    cancel_after_events=2,
)
cancelled_events_path = Path(cancelled["session_workspace_root"]) / "events" / "events.jsonl"
cancelled_last_event = json.loads(cancelled_events_path.read_text(encoding="utf-8").splitlines()[-1])
frontend_stream = build_frontend_stream_envelopes(completed["session_workspace_root"])
frontend_stream_check = validate_frontend_stream_envelopes(frontend_stream)
session_isolation = {{
    "session_a_root": session_a["session_workspace_root"],
    "session_b_root": session_b["session_workspace_root"],
    "separate_roots": session_a["session_workspace_root"] != session_b["session_workspace_root"],
    "a_paths": [item["relative_path"] for item in session_a_artifacts],
    "b_paths": [item["relative_path"] for item in session_b_artifacts],
}}
lifecycle = {{
    "completed_state": completed["runtime_state"],
    "completed_root": completed["session_workspace_root"],
    "cancelled_state": cancelled["runtime_state"],
    "cancelled_terminal_event": cancelled_last_event["event_type"],
    "cancelled_root": cancelled["session_workspace_root"],
    "separate_roots": completed["session_workspace_root"] != cancelled["session_workspace_root"],
}}
frontend_contract = {{
    "check": frontend_stream_check,
    "terminal_envelope": frontend_stream[-1] if frontend_stream else {{}},
}}
print(json.dumps({{
    "result": result,
    "artifacts": artifacts,
    "session_isolation": session_isolation,
    "lifecycle": lifecycle,
    "frontend_contract": frontend_contract,
}}, ensure_ascii=False))
'''
    proc = run([sys.executable, "-c", code], run_root, env)
    integration_passed = proc.returncode == 0
    payload = json.loads(proc.stdout) if integration_passed else {"error": proc.stderr}
    artifact_paths = [item["relative_path"] for item in payload.get("artifacts", [])]
    required_paths = {"events/events.jsonl", "transcript/transcript.md", "result/result.json"}
    event_artifacts_visible = required_paths.issubset(set(artifact_paths))
    isolation = payload.get("session_isolation", {})
    isolated_paths_ok = required_paths.issubset(set(isolation.get("a_paths", []))) and required_paths.issubset(
        set(isolation.get("b_paths", []))
    )
    session_isolation_passed = bool(isolation.get("separate_roots")) and isolated_paths_ok
    lifecycle = payload.get("lifecycle", {})
    lifecycle_passed = (
        lifecycle.get("completed_state") == "completed"
        and lifecycle.get("cancelled_state") == "cancelled"
        and lifecycle.get("cancelled_terminal_event") == "cancelled"
        and bool(lifecycle.get("separate_roots"))
    )
    frontend_contract = payload.get("frontend_contract", {})
    frontend_check = frontend_contract.get("check", {})
    frontend_contract_passed = (
        bool(frontend_check.get("monotonic"))
        and bool(frontend_check.get("terminal_has_result"))
        and frontend_check.get("runtime_state") == "completed"
    )
    decision_observability_passed = all(check["passed"] for check in decision_checks.values())
    summary = {
        "run_root": str(run_root),
        "workers": {
            "employee_a": report_a,
            "employee_b": report_b,
        },
        "integration": {
            "passed": integration_passed and event_artifacts_visible,
            "event_artifacts_visible": event_artifacts_visible,
            "artifact_paths": artifact_paths,
            "session_isolation_passed": session_isolation_passed,
            "session_isolation": isolation,
            "lifecycle_passed": lifecycle_passed,
            "lifecycle": lifecycle,
            "frontend_contract_passed": frontend_contract_passed,
            "frontend_contract": frontend_contract,
            "decision_observability_passed": decision_observability_passed,
            "decision_observability": decision_checks,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        },
        "comparison": {
            "both_verified": report_a["verification_passed"] and report_b["verification_passed"],
            "both_boundary_clean": all(
                not report["boundary_check"]["wrote_outside_workspace"]
                and not report["boundary_check"]["modified_management_policy"]
                for report in [report_a, report_b]
            ),
            "real_feature_acceptance_passed": (
                report_a["verification_passed"]
                and report_b["verification_passed"]
                and integration_passed
                and event_artifacts_visible
                and session_isolation_passed
                and lifecycle_passed
                and frontend_contract_passed
                and decision_observability_passed
            ),
        },
    }
    (run_root / "real_feature_acceptance_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (run_root / "real_feature_acceptance_summary.md").write_text(
        "\n".join(
            [
                "# Real Feature Acceptance Summary",
                "",
                f"Run root: `{run_root}`",
                "",
                "## Results",
                "",
                f"- employee_a verified: {report_a['verification_passed']}",
                f"- employee_b verified: {report_b['verification_passed']}",
                f"- event artifacts visible: {event_artifacts_visible}",
                f"- session isolation passed: {session_isolation_passed}",
                f"- lifecycle passed: {lifecycle_passed}",
                f"- frontend contract passed: {frontend_contract_passed}",
                f"- decision observability passed: {decision_observability_passed}",
                f"- real feature acceptance passed: {summary['comparison']['real_feature_acceptance_passed']}",
                "",
                "## Worker Predictions",
                "",
                f"- employee_a: {decision_checks['employee_a']['prediction']}",
                f"- employee_b: {decision_checks['employee_b']['prediction']}",
                "",
                "## Integrated Artifact Paths",
                "",
                *[f"- `{path}`" for path in artifact_paths],
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(run_root / "real_feature_acceptance_summary.json")
    print(run_root / "real_feature_acceptance_summary.md")
    return 0 if summary["comparison"]["real_feature_acceptance_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
