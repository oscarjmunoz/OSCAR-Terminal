# ADR-007: Backend and Frontend Contract Separation

- **Status**: Accepted
- **Date**: 2026-08-09
- **Related domains**: Frontend, API, Contracts

## Context
The frontend consumes backend APIs through typed clients and response schemas. The architecture requires public contract stability and clear separation between backend implementation and frontend consumption.

## Decision
Backend and frontend will continue to share explicit contracts through typed schemas and API responses. The frontend should depend on the documented API contract rather than backend implementation details.

## Consequences
- Contract changes are easier to review and govern.
- Frontend and backend can evolve with clearer boundaries.
- Versioning and deprecation become more important as the product grows.

## Alternatives considered
- Frontend coupling directly to backend implementation classes.
- Unstructured ad-hoc payloads.

## Notes
Historical rationale not recorded.
