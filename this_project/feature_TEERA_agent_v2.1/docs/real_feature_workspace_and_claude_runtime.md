# Real Feature: Workspace Page and Claude Agent SDK Runtime

## Feature Goal

On top of the TEERA Agent v2.1 baseline, build a user-visible workspace page
for long-horizon scholar sessions and upgrade `code_analysis` into an isolated
Claude Code Agent SDK runtime executor.

This is the first real development task used to evolve the organization
governance model. The feature is intentionally large and should be developed
over multiple days with tracked worker panes, manifests, tests, and acceptance
reports.

## Product Behavior

When a user starts a long-horizon scholar/code-analysis session:

1. The backend creates a session-scoped workspace.
2. All intermediate files, reports, traces, and generated artifacts are indexed.
3. The frontend workspace page displays the current session's workspace tree.
4. Selecting a file shows content, metadata, source step, and generated time.
5. Triggering `code_analysis` starts a Claude Code Agent SDK session in an
   isolated workspace.
6. The user sees the SDK event stream in real time, including:
   - session/system messages
   - assistant messages
   - partial stream events
   - tool calls
   - tool results
   - result/final messages
   - errors, cancellation, timeout, and compact boundaries when present
7. The final result is linked back to workspace artifacts.

## Runtime Boundary

```text
GeoGPT/TEERA request
  -> code_analysis API
    -> WorkspaceSessionManager
      -> ClaudeAgentRuntimeExecutor
        -> Claude Code Agent SDK session
          -> SDK stream events
          -> workspace artifacts
          -> event log / SSE channel
```

## Existing TEERA Anchors

The implementation must inspect and preserve existing behavior around:

- `service/GeoGPT_Scholar_Agent/tests/test_session_view_snapshot.py`
- `service/geogpt_deeper_research/recursive/agent/search_agent_main.py`
- `plugins/deeper_research_executor.py`
- `plugins/deep_research_chat_executor.py`
- `routers/sensor.py`
- `request/execute_code_request.py`
- existing OSS/write-md helpers and session_id conventions

## Claude Agent SDK Interface Assumption

Use the Claude Agent SDK streaming model:

- Python SDK exposes `query(...)`, `ClaudeAgentOptions`, and `StreamEvent`.
- Setting `include_partial_messages=True` emits raw stream events.
- Stream events include `message_start`, `content_block_start`,
  `content_block_delta`, `content_block_stop`, `message_delta`, and
  `message_stop`.
- Non-partial messages include system/session, assistant, result, and compact
  boundary messages.

Reference docs:

- `https://code.claude.com/docs/en/agent-sdk/streaming-output`
- `https://code.claude.com/docs/en/agent-sdk/python`

## Non-goals for First MVP

- No production credentials.
- No destructive filesystem writes outside the session workspace.
- No automatic push/PR.
- No full replacement of TEERA DAG engine.
- No unbounded autonomous teammate spawning.

## Evaluation Questions

1. Can two workers make independent progress without touching each other's
   workspace?
2. Can the workspace page be validated without a real browser dependency first?
3. Can the Claude Agent SDK runtime be mocked and then swapped with real SDK
   streaming?
4. Does the event model preserve enough detail to reproduce "what Claude Code
   did"?
5. Does the governance repo need new constraints after seeing this real task?

