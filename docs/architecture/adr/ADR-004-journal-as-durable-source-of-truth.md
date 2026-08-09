# ADR-004: Journal as Durable Source of Truth

- **Status**: Accepted
- **Date**: 2026-08-09
- **Related domains**: Journal, Analytics, Playbook

## Context
The journal domain captures decision snapshots and trader outcomes for later review and analytics. Analytics and playbook services consume these records.

## Decision
The journal domain is the durable source of truth for recorded trading decisions and outcomes. Journal entries preserve immutable decision snapshots and user-updated outcome data.

## Consequences
- Analytics can operate on persisted artifacts rather than requiring live recomputation.
- Decision history becomes auditable and reviewable.
- Journal storage must remain explicit and governed.

## Alternatives considered
- Storing decision history only in transient runtime memory.
- Reconstructing journal data from external systems on demand.

## Notes
Historical rationale not recorded.
