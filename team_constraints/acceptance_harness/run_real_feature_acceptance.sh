#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT="$ROOT/this_project/feature_TEERA_agent_v2.1"
HARNESS="$ROOT/team_constraints/acceptance_harness"
MODE="${1:---tmux}"
RUN_BASE="${ORG_REAL_FEATURE_RUN_ROOT:-/tmp/org_test_main_repo_real_feature}"
RUN_ROOT="$RUN_BASE/run_$(date +%Y%m%d_%H%M%S)"
SESSION="org-test-real-feature"

python3 "$HARNESS/validate_main_layout.py"
mkdir -p "$RUN_ROOT/employee_a" "$RUN_ROOT/employee_b"
cp -R "$PROJECT" "$RUN_ROOT/employee_a/workspace"
cp -R "$PROJECT" "$RUN_ROOT/employee_b/workspace"

if [[ "$MODE" == "--no-tmux" ]]; then
  python3 "$HARNESS/real_feature_worker.py" --employee employee_a --workspace "$RUN_ROOT/employee_a/workspace"
  python3 "$HARNESS/real_feature_worker.py" --employee employee_b --workspace "$RUN_ROOT/employee_b/workspace"
  python3 "$HARNESS/grade_real_feature_acceptance.py" --run-root "$RUN_ROOT"
  echo "$RUN_ROOT"
  exit 0
fi

tmux kill-session -t "$SESSION" 2>/dev/null || true
PANE_A="$(tmux new-session -d -P -F '#{pane_id}' -s "$SESSION" -n real-feature \
  "clear; echo 'EMPLOYEE A REAL FEATURE PANE'; echo 'BOUNDARY: $RUN_ROOT/employee_a/workspace'; python3 '$HARNESS/real_feature_worker.py' --employee employee_a --workspace '$RUN_ROOT/employee_a/workspace'; echo done > '$RUN_ROOT/employee_a.done'; sleep 60")"
PANE_B="$(tmux split-window -P -F '#{pane_id}' -t "$SESSION:real-feature" -h \
  "clear; echo 'EMPLOYEE B REAL FEATURE PANE'; echo 'BOUNDARY: $RUN_ROOT/employee_b/workspace'; python3 '$HARNESS/real_feature_worker.py' --employee employee_b --workspace '$RUN_ROOT/employee_b/workspace'; echo done > '$RUN_ROOT/employee_b.done'; sleep 60")"
tmux select-layout -t "$SESSION:real-feature" even-horizontal

deadline=$((SECONDS + 90))
while [[ ! -f "$RUN_ROOT/employee_a.done" || ! -f "$RUN_ROOT/employee_b.done" ]]; do
  if (( SECONDS > deadline )); then
    tmux capture-pane -t "$PANE_A" -p > "$RUN_ROOT/pane_employee_a.log" || true
    tmux capture-pane -t "$PANE_B" -p > "$RUN_ROOT/pane_employee_b.log" || true
    tmux kill-session -t "$SESSION" 2>/dev/null || true
    echo "Timed out waiting for real feature worker panes" >&2
    exit 1
  fi
  sleep 1
done

tmux capture-pane -t "$PANE_A" -p > "$RUN_ROOT/pane_employee_a.log" || true
tmux capture-pane -t "$PANE_B" -p > "$RUN_ROOT/pane_employee_b.log" || true
tmux kill-session -t "$SESSION" 2>/dev/null || true
python3 "$HARNESS/grade_real_feature_acceptance.py" --run-root "$RUN_ROOT"
echo "$RUN_ROOT"

