#!/usr/bin/env python3
"""Workers for the real workspace + Claude runtime acceptance scene."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


WORKSPACE_INDEX_CODE = '''"""Session workspace artifact indexing for TEERA runtime artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib


SESSION_ARTIFACT_ROOTS = {"events", "transcript", "result", "files", "artifacts"}


@dataclass(frozen=True)
class WorkspaceArtifact:
    artifact_id: str
    session_id: str
    relative_path: str
    kind: str
    source: str
    size: int
    preview: str


def _kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".md", ".markdown"}:
        return "markdown"
    if suffix == ".json":
        return "json"
    if suffix == ".jsonl":
        return "event_log"
    if suffix in {".txt", ".log"}:
        return "text"
    return "unknown"


def _source(relative_path: str) -> str:
    if relative_path.startswith("events/"):
        return "claude_agent_sdk_event_stream"
    if relative_path.startswith("transcript/"):
        return "claude_agent_sdk_transcript"
    if relative_path.startswith("result/"):
        return "claude_agent_sdk_result"
    if relative_path.startswith("files/"):
        return "session_intermediate_file"
    if relative_path.startswith("artifacts/"):
        return "worker_acceptance_artifact"
    return "workspace_file"


def _preview(path: Path, limit: int = 160) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return " ".join(text.split())[:limit]


def _is_indexable(root: Path, path: Path) -> bool:
    ignored_parts = {"__pycache__", ".git", ".pytest_cache"}
    if any(part in ignored_parts for part in path.parts):
        return False
    if path.suffix in {".pyc", ".pyo"}:
        return False
    relative = path.resolve().relative_to(root).as_posix()
    top_level = relative.split("/", 1)[0]
    return top_level in SESSION_ARTIFACT_ROOTS


def list_workspace_artifacts(workspace_root: str | Path, session_id: str) -> list[WorkspaceArtifact]:
    root = Path(workspace_root).resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"workspace root not found: {root}")
    artifacts: list[WorkspaceArtifact] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and _is_indexable(root, p)):
        resolved = path.resolve()
        if root not in resolved.parents:
            raise ValueError(f"path escaped workspace: {path}")
        rel = resolved.relative_to(root).as_posix()
        digest = hashlib.sha1(f"{session_id}:{rel}".encode("utf-8")).hexdigest()[:12]
        artifacts.append(
            WorkspaceArtifact(
                artifact_id=f"artifact_{digest}",
                session_id=session_id,
                relative_path=rel,
                kind=_kind(resolved),
                source=_source(rel),
                size=resolved.stat().st_size,
                preview=_preview(resolved),
            )
        )
    return artifacts


def artifact_dicts(workspace_root: str | Path, session_id: str) -> list[dict]:
    return [asdict(item) for item in list_workspace_artifacts(workspace_root, session_id)]
'''


WORKSPACE_INDEX_TESTS = '''import json
import tempfile
import unittest
from pathlib import Path

from scholar_retrieval.workspace_index import artifact_dicts, list_workspace_artifacts


class WorkspaceIndexTests(unittest.TestCase):
    def test_indexes_runtime_artifacts_with_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "events").mkdir()
            (root / "transcript").mkdir()
            (root / "result").mkdir()
            (root / "events" / "events.jsonl").write_text('{"type":"assistant"}\\n', encoding="utf-8")
            (root / "transcript" / "transcript.md").write_text("# hello\\n", encoding="utf-8")
            (root / "result" / "result.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
            artifacts = list_workspace_artifacts(root, "s1")
            self.assertEqual(len(artifacts), 3)
            by_path = {item.relative_path: item for item in artifacts}
            self.assertEqual(by_path["events/events.jsonl"].source, "claude_agent_sdk_event_stream")
            self.assertEqual(by_path["transcript/transcript.md"].kind, "markdown")
            self.assertEqual(by_path["result/result.json"].kind, "json")

    def test_artifact_dicts_are_json_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "artifacts").mkdir()
            (root / "artifacts" / "note.txt").write_text("abc", encoding="utf-8")
            payload = artifact_dicts(root, "session-x")
            self.assertEqual(payload[0]["session_id"], "session-x")
            json.dumps(payload)

    def test_ignores_runtime_cache_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "x.pyc").write_bytes(b"cache")
            (root / "events").mkdir()
            (root / "events" / "events.jsonl").write_text("{}", encoding="utf-8")
            payload = artifact_dicts(root, "session-x")
            self.assertEqual([item["relative_path"] for item in payload], ["events/events.jsonl"])

    def test_excludes_project_source_and_docs_from_session_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "docs").mkdir()
            (root / "events").mkdir()
            (root / "src" / "implementation.py").write_text("print('not a result')", encoding="utf-8")
            (root / "docs" / "prd.md").write_text("not a session artifact", encoding="utf-8")
            (root / "events" / "events.jsonl").write_text("{}", encoding="utf-8")
            payload = artifact_dicts(root, "session-x")
            self.assertEqual([item["relative_path"] for item in payload], ["events/events.jsonl"])


if __name__ == "__main__":
    unittest.main()
'''


CLAUDE_RUNTIME_CODE = '''"""Fake-SDK-backed Claude runtime executor for acceptance testing."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping
import json


@dataclass(frozen=True)
class RuntimeEvent:
    event_id: str
    session_id: str
    sequence: int
    event_type: str
    text: str
    raw: Mapping[str, Any]


class FakeClaudeAgentSDKStream:
    def __init__(self, events: Iterable[Mapping[str, Any]]) -> None:
        self.events = list(events)

    def __iter__(self):
        return iter(self.events)


def normalize_event(session_id: str, sequence: int, raw: Mapping[str, Any]) -> RuntimeEvent:
    event_type = str(raw.get("type", "unknown"))
    text = str(raw.get("text") or raw.get("delta") or raw.get("message") or "")
    return RuntimeEvent(
        event_id=f"{session_id}_{sequence:04d}",
        session_id=session_id,
        sequence=sequence,
        event_type=event_type,
        text=text,
        raw=raw,
    )


def run_code_analysis_runtime(
    session_id: str,
    workspace_root: str | Path,
    prompt: str,
    sdk_stream: Iterable[Mapping[str, Any]],
) -> dict:
    root = Path(workspace_root).resolve()
    root.mkdir(parents=True, exist_ok=True)
    events_dir = root / "events"
    transcript_dir = root / "transcript"
    result_dir = root / "result"
    events_dir.mkdir(exist_ok=True)
    transcript_dir.mkdir(exist_ok=True)
    result_dir.mkdir(exist_ok=True)

    events: list[RuntimeEvent] = []
    for idx, raw in enumerate(sdk_stream, start=1):
        events.append(normalize_event(session_id, idx, raw))

    (events_dir / "events.jsonl").write_text(
        "".join(json.dumps(asdict(event), ensure_ascii=False) + "\\n" for event in events),
        encoding="utf-8",
    )
    transcript_lines = [f"# Claude runtime transcript for {session_id}", "", f"Prompt: {prompt}", ""]
    transcript_lines.extend(f"- [{event.sequence}] {event.event_type}: {event.text}" for event in events)
    (transcript_dir / "transcript.md").write_text("\\n".join(transcript_lines) + "\\n", encoding="utf-8")
    terminal = events[-1].event_type if events else "empty"
    result = {
        "session_id": session_id,
        "event_count": len(events),
        "terminal_event_type": terminal,
        "workspace_root": str(root),
    }
    (result_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
    return result


def run_isolated_code_analysis_runtime(
    user_session_id: str,
    base_workspace_root: str | Path,
    prompt: str,
    sdk_stream: Iterable[Mapping[str, Any]],
) -> dict:
    if not user_session_id or "/" in user_session_id or ".." in user_session_id:
        raise ValueError(f"invalid user session id: {user_session_id!r}")
    session_root = Path(base_workspace_root).resolve() / "sessions" / user_session_id
    result = run_code_analysis_runtime(user_session_id, session_root, prompt, sdk_stream)
    result["base_workspace_root"] = str(Path(base_workspace_root).resolve())
    result["session_workspace_root"] = str(session_root)
    return result


def run_managed_isolated_code_analysis_runtime(
    user_session_id: str,
    base_workspace_root: str | Path,
    prompt: str,
    sdk_stream: Iterable[Mapping[str, Any]],
    cancel_after_events: int | None = None,
    timeout_after_events: int | None = None,
) -> dict:
    if cancel_after_events is not None and timeout_after_events is not None:
        raise ValueError("cancel_after_events and timeout_after_events are mutually exclusive")
    forwarded: list[Mapping[str, Any]] = []
    for idx, raw in enumerate(sdk_stream, start=1):
        forwarded.append(raw)
        if cancel_after_events is not None and idx >= cancel_after_events:
            forwarded.append({"type": "cancelled", "message": "cancelled by user"})
            break
        if timeout_after_events is not None and idx >= timeout_after_events:
            forwarded.append({"type": "timeout", "message": "runtime timeout"})
            break
    result = run_isolated_code_analysis_runtime(
        user_session_id,
        base_workspace_root,
        prompt,
        FakeClaudeAgentSDKStream(forwarded),
    )
    terminal = result["terminal_event_type"]
    if terminal == "cancelled":
        result["runtime_state"] = "cancelled"
    elif terminal == "timeout":
        result["runtime_state"] = "failed"
    elif terminal == "result":
        result["runtime_state"] = "completed"
    else:
        result["runtime_state"] = "running"
    result_path = Path(result["session_workspace_root"]) / "result" / "result.json"
    result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
    return result
'''


CLAUDE_RUNTIME_TESTS = '''import json
import tempfile
import unittest
from pathlib import Path

from scholar_retrieval.claude_runtime import (
    FakeClaudeAgentSDKStream,
    normalize_event,
    run_code_analysis_runtime,
    run_isolated_code_analysis_runtime,
    run_managed_isolated_code_analysis_runtime,
)


class ClaudeRuntimeTests(unittest.TestCase):
    def test_normalize_event_preserves_sequence_and_raw(self):
        event = normalize_event("s1", 2, {"type": "content_block_delta", "delta": "hello"})
        self.assertEqual(event.event_id, "s1_0002")
        self.assertEqual(event.event_type, "content_block_delta")
        self.assertEqual(event.text, "hello")
        self.assertEqual(event.raw["delta"], "hello")

    def test_runtime_writes_events_transcript_and_result(self):
        stream = FakeClaudeAgentSDKStream([
            {"type": "message_start", "text": "start"},
            {"type": "content_block_delta", "delta": "thinking"},
            {"type": "tool_use", "text": "Read file"},
            {"type": "result", "message": "done"},
        ])
        with tempfile.TemporaryDirectory() as tmp:
            result = run_code_analysis_runtime("session-1", tmp, "analyze code", stream)
            self.assertEqual(result["event_count"], 4)
            root = Path(tmp)
            events = (root / "events" / "events.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(events), 4)
            self.assertEqual(json.loads(events[1])["text"], "thinking")
            self.assertIn("tool_use", (root / "transcript" / "transcript.md").read_text(encoding="utf-8"))
            self.assertTrue((root / "result" / "result.json").exists())

    def test_isolated_runtime_keeps_two_sessions_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            run_isolated_code_analysis_runtime(
                "session-a",
                base,
                "analyze A",
                FakeClaudeAgentSDKStream([{"type": "result", "message": "A done"}]),
            )
            run_isolated_code_analysis_runtime(
                "session-b",
                base,
                "analyze B",
                FakeClaudeAgentSDKStream([{"type": "result", "message": "B done"}]),
            )
            a_result = json.loads((base / "sessions" / "session-a" / "result" / "result.json").read_text())
            b_result = json.loads((base / "sessions" / "session-b" / "result" / "result.json").read_text())
            self.assertEqual(a_result["session_id"], "session-a")
            self.assertEqual(b_result["session_id"], "session-b")
            self.assertFalse((base / "events" / "events.jsonl").exists())

    def test_isolated_runtime_rejects_path_like_session_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                run_isolated_code_analysis_runtime(
                    "../escape",
                    tmp,
                    "bad",
                    FakeClaudeAgentSDKStream([]),
                )

    def test_managed_runtime_writes_cancel_terminal_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_managed_isolated_code_analysis_runtime(
                "session-cancel",
                tmp,
                "long run",
                FakeClaudeAgentSDKStream([
                    {"type": "message_start", "text": "start"},
                    {"type": "content_block_delta", "delta": "working"},
                    {"type": "content_block_delta", "delta": "still working"},
                ]),
                cancel_after_events=2,
            )
            self.assertEqual(result["runtime_state"], "cancelled")
            self.assertEqual(result["terminal_event_type"], "cancelled")
            lines = (
                Path(result["session_workspace_root"]) / "events" / "events.jsonl"
            ).read_text(encoding="utf-8").splitlines()
            self.assertEqual(json.loads(lines[-1])["event_type"], "cancelled")

    def test_managed_runtime_writes_timeout_terminal_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_managed_isolated_code_analysis_runtime(
                "session-timeout",
                tmp,
                "long run",
                FakeClaudeAgentSDKStream([
                    {"type": "message_start", "text": "start"},
                    {"type": "content_block_delta", "delta": "working"},
                ]),
                timeout_after_events=1,
            )
            self.assertEqual(result["runtime_state"], "failed")
            self.assertEqual(result["terminal_event_type"], "timeout")


if __name__ == "__main__":
    unittest.main()
'''


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, env=env)


class Boundary:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()

    def write(self, relative: str, content: str) -> None:
        path = (self.workspace / relative).resolve()
        if path != self.workspace and self.workspace not in path.parents:
            raise RuntimeError(f"write outside assigned workspace: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def employee_a(boundary: Boundary) -> dict:
    boundary.write("src/scholar_retrieval/workspace_index.py", WORKSPACE_INDEX_CODE)
    boundary.write("tests/test_workspace_index.py", WORKSPACE_INDEX_TESTS)
    return {
        "feature": "workspace_artifact_index",
        "files_changed": [
            "src/scholar_retrieval/workspace_index.py",
            "tests/test_workspace_index.py",
        ],
        "tests_added": ["tests/test_workspace_index.py"],
    }


def employee_b(boundary: Boundary) -> dict:
    boundary.write("src/scholar_retrieval/claude_runtime.py", CLAUDE_RUNTIME_CODE)
    boundary.write("tests/test_claude_runtime.py", CLAUDE_RUNTIME_TESTS)
    return {
        "feature": "claude_runtime_event_stream",
        "files_changed": [
            "src/scholar_retrieval/claude_runtime.py",
            "tests/test_claude_runtime.py",
        ],
        "tests_added": ["tests/test_claude_runtime.py"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--employee", choices=["employee_a", "employee_b"], required=True)
    parser.add_argument("--workspace", required=True)
    args = parser.parse_args()

    workspace = Path(args.workspace).resolve()
    boundary = Boundary(workspace)
    print(f"[{args.employee}] assigned workspace: {workspace}")
    print(f"[{args.employee}] policy: may write only inside assigned workspace")
    feature = employee_a(boundary) if args.employee == "employee_a" else employee_b(boundary)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(workspace / "src")
    test = run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], workspace, env)
    output = test.stdout + test.stderr
    passed = test.returncode == 0
    artifacts = workspace / "artifacts"
    artifacts.mkdir(exist_ok=True)
    (artifacts / "test_output.txt").write_text(output, encoding="utf-8")
    report = {
        "employee": args.employee,
        "assigned_workspace": str(workspace),
        "allowed_write_scope": str(workspace),
        **feature,
        "verification_command": "PYTHONPATH=src python -m unittest discover -s tests",
        "verification_passed": passed,
        "boundary_check": {
            "wrote_outside_workspace": False,
            "modified_management_policy": False,
        },
        "feature_completion_score": 1.0 if passed else 0.4,
    }
    (artifacts / "acceptance_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (artifacts / "change_manifest.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(output)
    print(f"[{args.employee}] verification_passed={passed}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
