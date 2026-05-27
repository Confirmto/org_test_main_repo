# Three-Day Execution Schedule

## Day 1: Contract and Harness

Objective: make the real feature executable as a controlled experiment.

Tasks:

1. Map real TEERA files touched by workspace/session/code_analysis.
2. Freeze the worker split and integration contract.
3. Build a two-pane harness that copies a real-ish project baseline into two
   workspaces.
4. Add fake SDK event stream fixtures.
5. Add artifact index fixtures.
6. Run first no-tmux and tmux acceptance dry runs.

Exit criteria:

- The two workers can run independently.
- The harness captures pane logs and diffs.
- The grader can score incomplete vs complete feature work.

## Day 2: Feature Implementation Simulation

Objective: let worker A and worker B implement meaningful slices.

Tasks:

1. Worker A implements workspace artifact index and view contract.
2. Worker B implements fake-SDK-backed runtime event executor.
3. Add tests around path boundaries and event ordering.
4. Integrator runs both outputs together.
5. Record failure modes and missing constraints.

Exit criteria:

- Worker A and B both pass their own tests.
- Integration proves event artifacts appear in workspace listing.
- At least one governance model weakness is fixed.

## Day 3: Real SDK Adapter and Governance Hardening

Objective: harden the model toward real Claude Agent SDK usage.

Tasks:

1. Add a thin real Claude Agent SDK adapter behind the fake adapter interface.
2. Validate expected event types against official SDK docs.
3. Add cancellation/timeout terminal event semantics.
4. Update `CLAUEDE.md` and `team_constraints` based on the experiment.
5. Produce final report: feature completion, pane traces, quality assessment,
   and reusable onboarding recipe.

Exit criteria:

- The fake adapter path is fully tested.
- The real SDK adapter is isolated and can be enabled by config.
- The organization base repo can explain how to onboard the next project.

