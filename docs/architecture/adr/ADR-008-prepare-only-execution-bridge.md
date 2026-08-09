# ADR-008: Prepare-Only Execution Bridge

- **Status**: Accepted
- **Date**: 2026-08-09
- **Related domains**: Execution, Decision

## Context
OSCAR is an institutional trading copilot, not an autonomous trading robot. Execution preparation is required, but the system must not auto-submit trades.

## Decision
The execution bridge remains prepare-only. It may generate and validate trade tickets and execution artifacts, but it does not perform autonomous order submission as part of the current architecture.

## Consequences
- Safety and human control remain explicit.
- The architecture aligns with the OSCAR constitution.
- Future broker-facing execution layers can be introduced later without redefining the current bridge semantics.

## Alternatives considered
- Direct broker execution from the opportunity flow.
- Mixed manual and autonomous execution paths.

## Notes
Historical rationale not recorded.
