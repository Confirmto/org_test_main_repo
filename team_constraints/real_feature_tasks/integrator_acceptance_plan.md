# Integrator Acceptance Plan: Workspace + Claude Runtime

## Purpose

Integrate the two worker streams and use the result to improve the organization
governance model.

## Worker Split

- Employee A: workspace page, artifact index, workspace API.
- Employee B: Claude Agent SDK runtime executor, event stream, session isolation.

## Integration Contract

Employee B writes runtime artifacts:

```text
<session_workspace>/
  events/events.jsonl
  transcript/transcript.md
  result/result.json
  files/<generated artifacts>
```

Employee A reads the same workspace through an artifact index:

```text
WorkspaceArtifact {
  artifact_id
  session_id
  relative_path
  kind
  source
  created_at
  size
  preview
}
```

The integration layer must prove:

1. Runtime event stream creates visible artifacts.
2. Workspace page/API can list and preview those artifacts.
3. Both components enforce the same workspace root.
4. The session id connects API, event stream, artifacts, and final result.

## Development Trace Requirements

For each pane:

- capture tmux pane log
- record command transcript
- save git diff
- save test output
- save manifest
- save acceptance report

## Completion Rubric

| Dimension | Weight | Meaning |
| --- | ---: | --- |
| Functional completion | 30 | Required behavior implemented and demoable |
| Test quality | 20 | Unit/integration tests cover boundary cases |
| Event/artifact observability | 20 | User can inspect process, not just final answer |
| Workspace isolation | 15 | No path traversal or cross-session writes |
| Governance feedback | 15 | Findings are fed back into `team_constraints` |

## Governance Feedback Questions

After integration, update the organization model with answers to:

- Which constraints were missing from `CLAUEDE.md`?
- Which files did workers need but could not find in `this_project`?
- Which acceptance checks caught real issues?
- Which checks were too weak or too toy-like?
- Should future projects start with a runtime event schema by default?

