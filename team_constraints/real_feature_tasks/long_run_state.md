# Long-Run State: Workspace + Claude Runtime Experiment

## Current Objective

Use a real TEERA feature request to evolve the organization governance base
repo into a reusable model for future projects.

## Real Feature

Build:

1. a workspace page/API showing all intermediate files and session artifacts
2. a `code_analysis` runtime executor backed by Claude Code Agent SDK
3. a full SDK event stream visible to the user
4. two-pane development trace capture and acceptance grading

## Current Phase

Day 1 / Contract and Harness.

## Completed

- Top-level repo constrained to `CLAUEDE.md`, `this_project/`, `team_constraints/`.
- TEERA v2.1 baseline summarized.
- Toy two-employee tmux acceptance harness created and verified.
- Real feature project spec added.
- Real Employee A/B task split added.
- Integrator acceptance plan added.
- Three-day execution schedule added.
- 30-minute heartbeat automation created for continued iteration.
- Real-feature acceptance harness added for workspace artifact index plus fake Claude Agent SDK runtime event stream.
- Real-feature harness verified in no-tmux mode:
  `/tmp/org_test_main_repo_real_feature/run_20260527_120831`.
- Real-feature harness verified in tmux two-pane mode:
  `/tmp/org_test_main_repo_real_feature/run_20260527_120901`.
- Workspace artifact indexing was tightened so the user-facing session result list
  includes runtime/session outputs only: `events/`, `transcript/`, `result/`,
  `files/`, and worker `artifacts/`; source, docs, schemas, caches, and tests are
  excluded from the page candidate data.
- Runtime isolation contract added to the fake Claude Agent SDK executor:
  `run_isolated_code_analysis_runtime()` writes each user session under
  `sessions/<session_id>/` and rejects path-like session ids.
- Real-feature grader now checks that two runtime sessions produce separate
  event/result/transcript roots without cross-session artifact leakage.
- Updated real-feature harness verified in no-tmux mode:
  `/tmp/org_test_main_repo_real_feature/run_20260527_123103`.
- Updated real-feature harness verified in tmux two-pane mode:
  `/tmp/org_test_main_repo_real_feature/run_20260527_123129`.

## Next Highest-Leverage Weakness

The harness now verifies artifact indexing, event emission, two-pane execution,
and per-session runtime isolation. The next weakness is that cancellation and
timeout behavior are not yet part of the contract, so a long Claude Code SDK run
could still leak resources or leave the UI in an ambiguous state.

## Next Concrete Step

Add lifecycle controls around the real `code_analysis` trigger path:

- request schema: timeout budget and cancellation token
- runtime state machine: `queued -> running -> cancelling -> cancelled|failed|completed`
- event streaming contract: cancellation/timeout terminal events are written to JSONL
- kill/timeout contract: stop one runtime without contaminating another session
- grader check: cancelled session has a terminal event and leaves completed sessions intact
