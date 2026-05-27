# Team Constraints

This directory contains organization-level constraints for the acceptance scene.

It defines how two clean workers should operate when developing academic
retrieval features from the same `this_project/feature_TEERA_agent_v2.1`
baseline.

## Top-level Rule

Workers may read the whole repository, but each worker may write only inside
their assigned work directory created by the acceptance harness.

## Acceptance Scene

- Employee A develops query planning and multi-hop query expansion.
- Employee B develops evidence ledger, candidate lock, and stop guard.
- Both start from the same clean baseline.
- Both run the same baseline tests plus their own feature tests.
- The grader compares completion under controlled variables.

