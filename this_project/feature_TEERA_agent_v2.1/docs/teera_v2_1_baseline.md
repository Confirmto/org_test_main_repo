# TEERA Agent v2.1 Baseline

## One-line Positioning

TEERA v2.1 is a human-engineered DAG-driven recursive
decompose-execute-aggregate framework, not an unconstrained free-form agent
loop.

## Core Flow

```text
User input
  -> DeeperResearchExecutor.execute()
    -> intent detection
    -> deeper_search_agent_writing()
    -> report_writing()
      -> GraphRunEngine.forward_one_step_until_done()
```

## Data Model

The core abstraction is a recursively nested graph:

```text
root_node
  -> inner_graph
    -> plan node
      -> inner_graph
    -> execute node
    -> aggregate node
```

Each node carries:

- graph info
- task info
- node status
- optional inner graph
- collected search/write evidence

## State Machine

```text
NOT_READY -> READY -> PLAN_DONE -> DOING -> FINAL_TO_FINISH
  -> NEED_POST_REFLECT -> FINISH
```

The state transition logic is mostly hard-coded. This makes the system stable
but rigid.

## Search Subsystem

The search agent follows a ReAct-like loop:

- observe previous search results
- identify missing information
- plan current search queries
- call paper/web/RAG search tools
- aggregate candidate evidence

## Baseline Value

The baseline gives us a realistic production workflow to compare against. New
runtime executor work must show improvement against at least one controlled
dimension:

- feature completion
- evidence coverage
- post-hit convergence
- runtime isolation
- trace quality
- cancellation/timeout behavior

