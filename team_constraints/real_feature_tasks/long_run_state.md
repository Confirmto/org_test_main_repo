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
- Managed runtime lifecycle contract added to the fake Claude Agent SDK executor:
  `run_managed_isolated_code_analysis_runtime()` can emit explicit `cancelled`
  or `timeout` terminal events while preserving session isolation.
- Real-feature grader now checks completed-vs-cancelled sessions side by side:
  completed sessions must stay `completed`, cancelled sessions must end with a
  `cancelled` terminal event, and their roots must remain separate.
- Lifecycle-aware harness verified in no-tmux mode:
  `/tmp/org_test_main_repo_real_feature/run_20260527_130044`.
- Lifecycle-aware harness verified in tmux two-pane mode:
  `/tmp/org_test_main_repo_real_feature/run_20260527_130110`.

## Next Highest-Leverage Weakness

The harness now verifies artifact indexing, event emission, two-pane execution,
per-session isolation, and cancellation lifecycle. The next weakness is that the
frontend stream contract is still implicit: we verify JSONL artifacts, but not
the shape a workspace page/SSE/WebSocket consumer would receive.

## Next Concrete Step

Add frontend-facing stream contract around the real `code_analysis` trigger path:

- normalized event envelope: `session_id`, `sequence`, `event_type`, `text`,
  `artifact_refs`, `runtime_state`
- monotonic ordering check for streamed events
- page-readiness check: every terminal event links to the result artifact
- grader check: stream envelope can reconstruct the visible workspace timeline
