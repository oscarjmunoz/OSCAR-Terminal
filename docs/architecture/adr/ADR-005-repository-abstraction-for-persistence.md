# ADR-005: Repository Abstraction for Persistence

- **Status**: Accepted
- **Date**: 2026-08-09
- **Related domains**: Scanner, Journal, Persistence

## Context
Domain services need to store and retrieve state without embedding persistence concerns directly in business logic.

## Decision
Domain services will depend on repository abstractions. The repository boundary isolates persistence implementation details from service behavior.

## Consequences
- Domain logic remains portable across in-memory and durable implementations.
- Future replacement of storage technology is easier.
- Tests can target repository contracts without changing service behavior.

## Alternatives considered
- Direct SQLAlchemy usage inside services.
- Embedded storage logic inside routers.

## Notes
Historical rationale not recorded.
