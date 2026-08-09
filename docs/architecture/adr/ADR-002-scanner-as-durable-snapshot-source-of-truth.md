# ADR-002: Scanner as Durable Snapshot Source of Truth

- **Status**: Accepted
- **Date**: 2026-08-09
- **Related domains**: Scanner, Opportunity

## Context
The scanner domain builds structured snapshots from market and structure data. Opportunity evaluation consumes those snapshots and does not query market data directly.

## Decision
The scanner domain is the durable source of truth for the latest snapshot per symbol and timeframe. Opportunity state is derived from those snapshots rather than maintained independently.

## Consequences
- Scanner snapshots provide a stable input contract for opportunity analysis.
- Opportunity logic remains simpler and easier to replay.
- Scanner persistence can be refreshed independently of opportunity scoring.

## Alternatives considered
- Persisting opportunity state as the primary truth source.
- Recomputing scanner state on every request.

## Notes
Historical rationale not recorded.
