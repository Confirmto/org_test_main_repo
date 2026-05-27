# CLAUEDE.md

Management-owned policy for this organization repository.

Only repository maintainers may change this file. Feature developers and their
Claude Code sessions may read it, but must not edit it in feature branches.

## Repository Shape

The top level intentionally contains only:

- `this_project/`: product facts, feature contracts, schemas, minimal baseline code.
- `team_constraints/`: organization workflow, employee boundaries, acceptance harness.
- `CLAUEDE.md`: management-owned root policy.

Do not add new top-level directories without maintainer approval.

## Operating Principle

This repository is a contract-first main branch. It defines what the team is
building, how workers may operate, how evidence is collected, and how feature
completion is judged. Actual feature work happens in isolated work directories,
branches, or worktrees.

## Current Project

`this_project/feature_TEERA_agent_v2.1` is the baseline for a GeoGPT Scholar
long-horizon academic research agent. The planned feature direction is a
runtime-in-runtime executor:

`GeoGPT/TEERA orchestration -> Claude Code SDK runtime -> controlled scholar search tools -> evidence ledger -> final report`

## Current Real Development Experiment

The active long-run experiment is:

1. build a workspace page/API that shows all intermediate files and artifacts
   for the current session
2. upgrade `code_analysis` into a Claude Code Agent SDK runtime executor with
   global session isolation
3. stream all SDK events to the user as if they were watching Claude Code work
4. capture two employee panes, diffs, manifests, tests, and acceptance reports
5. use the result to improve this governance base repo for future projects

## Non-negotiable Constraints

1. Developers must not edit `CLAUEDE.md`.
2. Developers must not write outside their assigned work directory.
3. Personal files, secrets, raw tokens, and local service endpoints must not be committed.
4. Every feature branch must include a manifest, tests, and an acceptance report.
5. Runtime/harness changes must report trace-gap metrics, not only pass/fail.
6. Multi-agent/team mode requires an explicit integrator and stop condition.
