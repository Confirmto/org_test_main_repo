# Repository Layout Policy

The main branch top level must contain only:

- `this_project/`
- `team_constraints/`
- `CLAUEDE.md`

No feature worker may add another top-level item.

## Project Layer

`this_project/` stores product facts:

- PRD
- baseline notes
- schemas
- config examples
- minimal source/test skeletons

## Constraint Layer

`team_constraints/` stores:

- workflow policy
- employee workspace boundaries
- acceptance harness
- grading scripts

## Management Layer

`CLAUEDE.md` is management-owned. Treat it as read-only unless explicitly acting
as a repository maintainer.

