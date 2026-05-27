#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT="$ROOT/this_project/feature_TEERA_agent_v2.1"
HARNESS="$ROOT/team_constraints/acceptance_harness"
MODE="${1:---tmux}"
RUN_BASE="${ORG_ACCEPTANCE_RUN_ROOT:-/tmp/org_test_main_repo_acceptance}"
RUN_ROOT="$RUN_BASE/run_$(date +%Y%m%d_%H%M%S)"
SESSION="org-test-two-employees"

python3 "$HARNESS/validate_main_layout.py"

mkdir -p "$RUN_ROOT/employee_a" "$RUN_ROOT/employee_b"
cp -R "$PROJECT" "$RUN_ROOT/employee_a/workspace"
cp -R "$PROJECT" "$RUN_ROOT/employee_b/workspace"

run_worker() {
  local employee="$1"
  local workspace="$2"
  python3 "$HARNESS/employee_worker.py" --employee "$employee" --workspace "$workspace"
}

if [[ "$MODE" == "--no-tmux" ]]; then
  run_worker employee_a "$RUN_ROOT/employee_a/workspace"
  run_worker employee_b "$RUN_ROOT/employee_b/workspace"
  python3 "$HARNESS/grade_acceptance.py" --run-root "$RUN_ROOT"
  echo "$RUN_ROOT"
  exit 0
fi

tmux kill-session -t "$SESSION" 2>/dev/null || true
PANE_A="$(tmux new-session -d -P -F '#{pane_id}' -s "$SESSION" -n employees \
  "clear; echo 'EMPLOYEE A PANE'; echo 'BOUNDARY: $RUN_ROOT/employee_a/workspace'; python3 '$HARNESS/employee_worker.py' --employee employee_a --workspace '$RUN_ROOT/employee_a/workspace'; echo done > '$RUN_ROOT/employee_a.done'; sleep 60")"
PANE_B="$(tmux split-window -P -F '#{pane_id}' -t "$SESSION:employees" -h \
  "clear; echo 'EMPLOYEE B PANE'; echo 'BOUNDARY: $RUN_ROOT/employee_b/workspace'; python3 '$HARNESS/employee_worker.py' --employee employee_b --workspace '$RUN_ROOT/employee_b/workspace'; echo done > '$RUN_ROOT/employee_b.done'; sleep 60")"
tmux select-layout -t "$SESSION:employees" even-horizontal

deadline=$((SECONDS + 60))
while [[ ! -f "$RUN_ROOT/employee_a.done" || ! -f "$RUN_ROOT/employee_b.done" ]]; do
  if (( SECONDS > deadline )); then
    tmux capture-pane -t "$PANE_A" -p > "$RUN_ROOT/pane_employee_a.log" || true
    tmux capture-pane -t "$PANE_B" -p > "$RUN_ROOT/pane_employee_b.log" || true
    tmux kill-session -t "$SESSION" 2>/dev/null || true
    echo "Timed out waiting for employee panes" >&2
    exit 1
  fi
  sleep 1
done

tmux capture-pane -t "$PANE_A" -p > "$RUN_ROOT/pane_employee_a.log" || true
tmux capture-pane -t "$PANE_B" -p > "$RUN_ROOT/pane_employee_b.log" || true
tmux kill-session -t "$SESSION" 2>/dev/null || true
python3 "$HARNESS/grade_acceptance.py" --run-root "$RUN_ROOT"
echo "$RUN_ROOT"
