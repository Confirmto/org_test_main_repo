# Employee B Task: Claude Agent SDK Runtime Executor

## Mission

Upgrade `code_analysis` into a Claude Code Agent SDK runtime executor with
session isolation and full event capture.

Employee B owns the runtime side: invoking the SDK, capturing all events, and
writing runtime artifacts into the assigned session workspace.

## Allowed Scope

Employee B may work only inside their assigned worktree/workspace.

Expected code areas in the real TEERA codebase:

- `code_analysis` API/handler
- runtime executor adapter
- session workspace manager
- event serializer
- tests with a fake Claude Agent SDK stream

## Required Deliverables

1. Runtime executor interface:
   - start session
   - stream events
   - cancel session
   - timeout session
   - return final result
2. Claude Agent SDK adapter:
   - `ClaudeAgentOptions(include_partial_messages=True, cwd=<workspace>)`
   - allowed tools scoped to safe defaults
   - real SDK path behind an adapter so tests can use a fake stream
3. Event model:
   - event id
   - session id
   - sequence number
   - event type
   - raw payload
   - normalized text/tool fields
   - parent tool use id when present
4. Workspace writes:
   - append `events.jsonl`
   - append `transcript.md`
   - write `result.json`
5. Tests:
   - fake stream produces ordered events
   - partial text deltas accumulate correctly
   - tool call/tool result events are preserved
   - runtime cwd is the isolated workspace
   - cancellation/timeout produces terminal event

## Acceptance Criteria

- The executor can be tested without a real Claude API key.
- Real SDK integration point is explicit and thin.
- All SDK events are forwarded to the event stream, not silently swallowed.
- No runtime writes occur outside the session workspace.
- The final event stream can drive Employee A's workspace page.

## Control Variables

Employee B gets the same starting baseline and same time budget as Employee A.
Completion is judged by tests, manifest quality, boundary cleanliness, and
whether the event stream can integrate with Employee A's artifact model.

