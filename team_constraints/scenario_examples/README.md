# Scenario Examples

Scenarios are fixtures that prove the governance kernel works on concrete
projects. They are not the governance model itself.

Each scenario owns its own:

- `scenario.json`
- worker entrypoint
- grader entrypoint
- task notes
- project-specific vocabulary

The generic runner is:

```bash
python3 team_constraints/governance_kernel/harness/run_scenario.py \
  --scenario team_constraints/scenario_examples/teera_scholar_runtime \
  --mode no-tmux
```
