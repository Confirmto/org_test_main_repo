# Employee A Task: Workspace Page and Artifact Index

## Mission

Build the session workspace display surface.

Employee A owns the user-facing and backend-contract side of workspace
visibility. The goal is not a decorative page; the page must let the user audit
what the long-horizon agent produced during the current session.

## Allowed Scope

Employee A may work only inside their assigned worktree/workspace.

Expected code areas in the real TEERA codebase:

- frontend workspace route/components if present
- backend session workspace view API
- workspace artifact index model
- tests for workspace tree/content snapshots

## Required Deliverables

1. Workspace artifact schema:
   - artifact id
   - session id
   - relative path
   - kind: markdown/json/text/log/image/unknown
   - source step
   - created/updated time
   - size
   - preview
2. Workspace list API contract:
   - list artifacts for current session
   - fetch file content by artifact id/path
3. Workspace page contract:
   - file tree/list
   - selected file preview
   - event-linked artifact metadata
4. Tests:
   - index session artifacts from a temp directory
   - hide files outside workspace
   - render/serialize workspace snapshot
5. Evidence:
   - pane log
   - diff
   - test report
   - acceptance report

## Acceptance Criteria

- Existing session view tests still pass.
- New workspace tests pass.
- Artifact listing cannot escape the session workspace via `../`.
- The page/API distinguishes intermediate artifacts from final report files.
- The report explains where real TEERA OSS artifacts would be indexed.

## Control Variables

Employee A gets the same starting baseline and same time budget as Employee B.
Completion is judged by tests, manifest quality, boundary cleanliness, and
whether the artifact model can integrate with Employee B's event stream.

