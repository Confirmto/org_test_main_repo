#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
MODE="${1:---tmux}"
if [[ "$MODE" == "--no-tmux" ]]; then
  RUN_MODE="no-tmux"
else
  RUN_MODE="tmux"
fi

python3 "$ROOT/team_constraints/governance_kernel/harness/run_scenario.py" \
  --scenario "$ROOT/team_constraints/scenario_examples/toy_scholar_retrieval" \
  --mode "$RUN_MODE" \
  --run-base "${ORG_ACCEPTANCE_RUN_ROOT:-/tmp/org_test_main_repo_acceptance}"
