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

## Next Highest-Leverage Weakness

The real-feature harness now verifies the two core slices independently and as
an integration. The next weakness is that the runtime contract is still a
fake-SDK Python module rather than an executable adapter boundary for the actual
Claude Code Agent SDK process/session lifecycle.

## Next Concrete Step

Add an adapter contract around the real `code_analysis` trigger path:

- request schema: user session id, workspace id, task prompt, allowed root
- runtime session isolation: per-session workspace and event log
- event streaming contract: normalized SDK events written to JSONL and frontend stream
- kill/timeout contract: stop one runtime without contaminating another session
- grader check: two sessions run side by side and cannot see each other's artifacts
