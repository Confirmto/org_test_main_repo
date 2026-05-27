# Team Constraints

This directory contains the organization-governance layer.

It is split into:

- `governance_kernel/`: reusable policies, templates, and scenario runner.
- `scenario_examples/`: concrete examples used to verify the kernel.
- `acceptance_harness/`: compatibility shell wrappers for common sample runs.

## Top-level Rule

Workers may read the repository contracts, but may write only inside the
workspace assigned by the scenario runner.

## Scenario Contract

Every scenario declares:

- project baseline path
- worker slots
- worker entrypoints and arguments
- grader entrypoint
- timeout and stop condition

The kernel must not assume a specific project, feature, domain, or employee
task. Scenario-specific language belongs inside `scenario_examples/`.
