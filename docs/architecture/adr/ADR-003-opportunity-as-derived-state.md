# ADR-003: Opportunity as Derived State

- **Status**: Accepted
- **Date**: 2026-08-09
- **Related domains**: Opportunity, Scanner

## Context
Opportunity results depend on scanner snapshots and scoring rules. They are useful for prioritization and user-facing queueing but do not represent a separate authoritative domain state.

## Decision
Opportunity state remains derived from scanner snapshots and the opportunity engine. It should not be treated as a separate durable source of truth in the current architecture.

## Consequences
- Opportunity outputs remain reproducible from scanner data.
- Storage requirements are reduced.
- The architecture remains consistent with the current implementation.

## Alternatives considered
- Maintaining a distinct opportunity store.
- Persisting every intermediate opportunity state.

## Notes
Historical rationale not recorded.
