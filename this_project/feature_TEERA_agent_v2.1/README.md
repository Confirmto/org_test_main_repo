# feature_TEERA_agent_v2.1

This directory is the project-fact layer for the GeoGPT Scholar / TEERA agent
v2.1 baseline and the next runtime-in-runtime feature.

It is intentionally small. The full historical TEERA codebase is not copied
into this main branch. Instead, this directory keeps the stable contracts that
new feature workers need before opening a branch or worktree.

## Baseline Summary

The v2.1 baseline is a human-orchestrated recursive DAG research workflow:

- user input
- intent detection
- search stage
- report writing stage
- graph run engine
- recursive plan/execute/aggregate nodes
- Redis progress updates
- Nacos-driven limits and model choices

Known limitations:

- fixed state machine
- serial DAG execution
- no durable layered memory
- weak failure recovery
- prompt templates are static
- trace evidence is not yet sufficient for post-hit convergence analysis

## Next Feature Theme

Develop Claude Code SDK as a controlled runtime executor for long-horizon
scholar research tasks.

The acceptance harness starts with two independent academic retrieval features:

- Feature A: query plan normalization and multi-hop query expansion.
- Feature B: evidence ledger, candidate lock, and post-hit stop guard.

