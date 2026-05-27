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
- Frontend stream envelope contract added:
  `build_frontend_stream_envelopes()` converts runtime JSONL into page-ready
  envelopes with `session_id`, `sequence`, `event_type`, `text`,
  `runtime_state`, and `artifact_refs`.
- Frontend stream validation added:
  `validate_frontend_stream_envelopes()` checks monotonic event ordering and
  requires terminal envelopes to link to `result/result.json`.
- Frontend-contract harness verified in no-tmux mode:
  `/tmp/org_test_main_repo_real_feature/run_20260527_133032`.
- Frontend-contract harness verified in tmux two-pane mode:
  `/tmp/org_test_main_repo_real_feature/run_20260527_133056`.
- Decision observability contract added to worker reports and change manifests:
  each worker must declare intent, expected user-visible effect, risk,
  rollback, and a falsifiable prediction before the grader accepts the run.
- Real-feature grader now checks worker decision fields and prints worker
  predictions into the acceptance summary.
- Decision-observability harness verified in no-tmux mode:
  `/tmp/org_test_main_repo_real_feature/run_20260527_140112`.
- Decision-observability harness verified in tmux two-pane mode:
  `/tmp/org_test_main_repo_real_feature/run_20260527_140144`.

## Next Highest-Leverage Weakness

The harness now verifies artifact indexing, event emission, two-pane execution,
per-session isolation, cancellation lifecycle, and frontend stream envelopes.
The harness now also verifies decision observability. The next weakness is
component observability: editable harness components are still implicit files,
not a declared component map with owners, allowed edit surfaces, and rollback
boundaries.

## Next Concrete Step

Add component observability around each editable harness component:

- component registry: workspace index, runtime executor, frontend stream,
  lifecycle, acceptance grader, governance policy
- owner and allowed edit surface per component
- rollback anchor per component
- grader check: every changed file maps to a declared component
