#!/usr/bin/env python3
"""Generic scenario runner for isolated multi-worker governance acceptance."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import time


REPO_ROOT = Path(__file__).resolve().parents[3]


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, env=env)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def scenario_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = REPO_ROOT / value
    if path.is_dir():
        path = path / "scenario.json"
    return path.resolve()


def worker_command(scenario_dir: Path, worker: dict, workspace: Path) -> list[str]:
    entrypoint = (scenario_dir / worker["entrypoint"]).resolve()
    cmd = [sys.executable, str(entrypoint)]
    for key, value in worker.get("entrypoint_args", {}).items():
        cmd.extend([key, str(value)])
    cmd.extend(["--workspace", str(workspace)])
    return cmd


def copy_project(project_path: Path, workspace: Path) -> None:
    if workspace.exists():
        shutil.rmtree(workspace)
    shutil.copytree(project_path, workspace)


def run_worker_sync(scenario_dir: Path, worker: dict, workspace: Path) -> None:
    proc = subprocess.run(worker_command(scenario_dir, worker, workspace), text=True)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def run_no_tmux(config: dict, scenario_dir: Path, run_root: Path) -> None:
    project_path = (REPO_ROOT / config["project_path"]).resolve()
    for worker in config["workers"]:
        workspace = run_root / worker["run_dir"] / "workspace"
        workspace.parent.mkdir(parents=True, exist_ok=True)
        copy_project(project_path, workspace)
        run_worker_sync(scenario_dir, worker, workspace)


def run_tmux(config: dict, scenario_dir: Path, run_root: Path) -> None:
    project_path = (REPO_ROOT / config["project_path"]).resolve()
    session = f"org-scenario-{config['scenario_id']}"
    workers = config["workers"]
    for worker in workers:
        workspace = run_root / worker["run_dir"] / "workspace"
        workspace.parent.mkdir(parents=True, exist_ok=True)
        copy_project(project_path, workspace)

    subprocess.run(["tmux", "kill-session", "-t", session], stderr=subprocess.DEVNULL)
    pane_ids: list[tuple[str, str]] = []
    first = True
    for worker in workers:
        workspace = run_root / worker["run_dir"] / "workspace"
        done = run_root / f"{worker['id']}.done"
        cmd = " ".join(shlex.quote(part) for part in worker_command(scenario_dir, worker, workspace))
        shell_cmd = (
            f"clear; echo 'WORKER {worker['id']} PANE'; "
            f"echo 'ROLE: {worker.get('role', worker['id'])}'; "
            f"echo 'BOUNDARY: {workspace}'; "
            f"{cmd}; echo done > '{done}'; sleep 60"
        )
        if first:
            pane = subprocess.check_output(
                ["tmux", "new-session", "-d", "-P", "-F", "#{pane_id}", "-s", session, "-n", "workers", shell_cmd],
                text=True,
            ).strip()
            first = False
        else:
            pane = subprocess.check_output(
                ["tmux", "split-window", "-P", "-F", "#{pane_id}", "-t", f"{session}:workers", "-h", shell_cmd],
                text=True,
            ).strip()
        pane_ids.append((worker["id"], pane))
    subprocess.run(["tmux", "select-layout", "-t", f"{session}:workers", "even-horizontal"], check=False)

    deadline = time.time() + int(config.get("timeout_seconds", 90))
    done_files = [run_root / f"{worker['id']}.done" for worker in workers]
    while not all(path.exists() for path in done_files):
        if time.time() > deadline:
            for worker_id, pane in pane_ids:
                capture_pane(pane, run_root / f"pane_{worker_id}.log")
            subprocess.run(["tmux", "kill-session", "-t", session], stderr=subprocess.DEVNULL)
            raise SystemExit("Timed out waiting for scenario worker panes")
        time.sleep(1)

    for worker_id, pane in pane_ids:
        capture_pane(pane, run_root / f"pane_{worker_id}.log")
    subprocess.run(["tmux", "kill-session", "-t", session], stderr=subprocess.DEVNULL)


def capture_pane(pane_id: str, output_path: Path) -> None:
    proc = subprocess.run(["tmux", "capture-pane", "-t", pane_id, "-p"], text=True, capture_output=True)
    output_path.write_text(proc.stdout, encoding="utf-8")


def run_grader(config: dict, scenario_dir: Path, run_root: Path) -> None:
    grader = (scenario_dir / config["grader"]).resolve()
    proc = subprocess.run([sys.executable, str(grader), "--run-root", str(run_root)], text=True)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--mode", choices=["tmux", "no-tmux"], default="tmux")
    parser.add_argument("--run-base")
    args = parser.parse_args()

    layout = run([sys.executable, str(REPO_ROOT / "team_constraints/governance_kernel/harness/validate_main_layout.py")], REPO_ROOT)
    print(layout.stdout, end="", flush=True)
    if layout.returncode != 0:
        print(layout.stderr, end="", file=sys.stderr)
        return layout.returncode

    manifest = scenario_path(args.scenario)
    config = load_json(manifest)
    scenario_dir = manifest.parent
    run_base = Path(args.run_base or os.environ.get("ORG_SCENARIO_RUN_ROOT", f"/tmp/org_test_main_repo_{config['scenario_id']}"))
    run_root = run_base / f"run_{time.strftime('%Y%m%d_%H%M%S')}"
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "scenario_manifest.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    if args.mode == "no-tmux":
        run_no_tmux(config, scenario_dir, run_root)
    else:
        run_tmux(config, scenario_dir, run_root)
    run_grader(config, scenario_dir, run_root)
    print(run_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
