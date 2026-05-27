# Agent Team Usage Policy

## Use a Single Agent

Use a single Claude Code session for small implementation or review work.

## Use Subagents

Use subagents for read-only exploration, test review, or narrow implementation
that can return a single result to the parent.

## Use Worktree Isolation

Use worktree isolation when an agent may write code and its changes should not
touch the parent workspace.

## Use Teammate / Team Mode

Use teammate/team mode only when:

- work can be split into independent streams
- every teammate has a named owner role
- each stream has a stop condition
- an integrator owns final merge

Teammates must not spawn unbounded teammate chains.

