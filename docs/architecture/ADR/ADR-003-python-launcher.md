# ADR-003: Python Launcher as Operational Entrypoint

- Status: Accepted
- Date: 2026-07-31

## Context

Batch-only launch logic is hard to scale, test, and port to Linux.

## Decision

Adopt a Python launcher as the primary startup orchestration layer; keep BAT scripts as thin wrappers.

## Consequences

- Better cross-platform readiness.
- Centralized startup, health checks, and process lifecycle logic.
- Cleaner operational documentation and easier future extensions.
