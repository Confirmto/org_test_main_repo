# CLAUEDE.md

Management-owned policy for this organization repository.

Only repository maintainers may change this file. Worker agents may read it,
but must not edit it in feature branches.

## Repository Shape

The top level intentionally contains only:

- `this_project/`: project facts, contracts, schemas, and minimal baseline code.
- `team_constraints/`: reusable governance kernel plus optional scenario examples.
- `CLAUEDE.md`: management-owned root policy.

Do not add new top-level directories without maintainer approval.

## Operating Principle

This repository is a contract-first main branch. It defines how workers may
operate, how evidence is collected, and how feature completion is judged.

The governance layer must be project-agnostic. Product names, feature names,
domain vocabulary, SDK choices, and worker task details belong in scenario
manifests or project-owned folders, not in the root policy.

## Reusable Governance Model

Generic governance lives under:

`team_constraints/governance_kernel/`

Concrete examples live under:

`team_constraints/scenario_examples/`

A scenario may point at any project baseline under `this_project/` and define
its own workers, roles, entrypoints, grader, timeout, and acceptance contract.

## Non-negotiable Constraints

1. Workers must not edit `CLAUEDE.md`.
2. Workers must not write outside their assigned work directory.
3. Personal files, secrets, raw tokens, and local service endpoints must not be committed.
4. Every scenario run must include a manifest, tests, and an acceptance report.
5. Harness changes must preserve component, experience, and decision observability.
6. Multi-worker/team mode requires an explicit integrator or grader and stop condition.
