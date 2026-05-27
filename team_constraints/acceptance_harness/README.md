# Acceptance Harness Wrappers

This folder keeps short compatibility wrappers for sample scenarios.

The reusable runner lives in:

`team_constraints/governance_kernel/harness/run_scenario.py`

Preferred usage:

```bash
python3 team_constraints/governance_kernel/harness/run_scenario.py \
  --scenario team_constraints/scenario_examples/teera_scholar_runtime \
  --mode no-tmux
```

Compatibility wrappers:

- `run_two_worker_acceptance.sh`: legacy wrapper for the toy scholar retrieval scenario.
- `run_real_feature_acceptance.sh`: runs the runtime-streaming example scenario.

Do not add project-specific governance logic here. New project examples should
be added as scenario folders under `team_constraints/scenario_examples/` or as
project-owned scenario folders.
