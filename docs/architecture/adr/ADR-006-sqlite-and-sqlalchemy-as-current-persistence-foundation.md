# ADR-006: SQLite and SQLAlchemy as Current Persistence Foundation

- **Status**: Accepted
- **Date**: 2026-08-09
- **Related domains**: Persistence, Scanner, Journal, Infrastructure

## Context
The repository already contains SQLAlchemy base classes, a session factory, and a SQLite configuration. A lightweight persistence foundation is required without introducing distributed or cloud-based infrastructure.

## Decision
OSCAR will use SQLite with SQLAlchemy as the current persistence foundation for durable domain state. This is sufficient for local development and current architecture scope.

## Consequences
- The persistence layer is simple and easy to operate locally.
- Existing services can adopt durable repositories with minimal change.
- The approach is intentionally conservative and can evolve later.

## Alternatives considered
- Introducing a full production relational database.
- Introducing caching or distributed state.

## Notes
Historical rationale not recorded.
