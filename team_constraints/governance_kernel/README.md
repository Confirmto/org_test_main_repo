# Governance Kernel

This is the reusable organization-governance layer. It must stay independent of
any single project, product, feature, or domain.

The kernel provides:

- top-level layout validation
- scenario-driven worker orchestration
- isolated workspaces
- pane trace capture
- acceptance summary handoff
- reusable templates and policies

Project-specific tasks belong under `team_constraints/scenario_examples/` or a
project-owned scenario directory, not inside this kernel.
