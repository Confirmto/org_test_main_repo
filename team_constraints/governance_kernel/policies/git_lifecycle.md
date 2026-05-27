# Git Lifecycle Policy

## Main Branch

Main contains contracts and acceptance harnesses, not active feature work.

## Feature Work

Feature work must happen in:

- a feature branch, or
- a separate worktree, or
- an acceptance harness worker directory.

## Local-only Data

The following must stay local:

- `CLAUDE.local.md`
- `.claude/settings.local.json`
- raw runtime traces
- secrets
- personal sandbox URLs

## Commit Requirements

A feature is commit-ready only when it has:

- implementation
- tests
- `artifacts/change_manifest.json`
- acceptance report
- no writes outside assigned scope

