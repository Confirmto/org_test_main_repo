# Two-Employee Acceptance Harness

## Purpose

Validate whether the organization main branch can support controlled feature
development by multiple workers without workspace contamination.

## Scene

Two clean tmux panes simulate two employees.

- Employee A works on query planning.
- Employee B works on evidence lock.

Both employees start from the same `this_project/feature_TEERA_agent_v2.1`
baseline copied into separate workspaces under `/tmp`.

## Control Variables

- Same baseline code.
- Same verification command.
- Same workspace boundary rule.
- Same artifact requirements.
- Same time budget policy.

## Variable Under Test

Feature completion under isolated development:

- Did the employee implement the assigned feature?
- Did tests pass?
- Did they write only inside their assigned workspace?
- Did they produce manifest and acceptance report?

## Commands

Run with actual tmux panes:

```bash
bash team_constraints/acceptance_harness/run_two_employee_acceptance.sh --tmux
```

Run without tmux for CI/debug:

```bash
bash team_constraints/acceptance_harness/run_two_employee_acceptance.sh --no-tmux
```

Validate main layout:

```bash
python3 team_constraints/acceptance_harness/validate_main_layout.py
```

## Outputs

The harness writes a run directory under:

```text
/tmp/org_test_main_repo_acceptance/run_<timestamp>/
```

Important files:

- `pane_employee_a.log`
- `pane_employee_b.log`
- `employee_a/workspace/artifacts/acceptance_report.json`
- `employee_b/workspace/artifacts/acceptance_report.json`
- `acceptance_summary.json`
- `acceptance_summary.md`

