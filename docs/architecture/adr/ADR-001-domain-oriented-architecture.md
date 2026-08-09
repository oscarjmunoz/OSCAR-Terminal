# ADR-001: Domain-Oriented Architecture

- **Status**: Accepted
- **Date**: 2026-08-09
- **Related domains**: Scanner, Opportunity, Decision, Execution, Journal, Analytics, Playbook

## Context
OSCAR is organized as a set of bounded domains with distinct responsibilities: market context, opportunity evaluation, decision support, execution preparation, journaling, analytics, and playbook management. The repository structure reflects this separation.

## Decision
OSCAR will continue to use a domain-oriented architecture where each domain owns its own models, services, and API surface. Cross-domain interactions occur through explicit contracts rather than shared mutable state.

## Consequences
- Domain logic remains easier to reason about and test.
- Changes in one domain are less likely to cascade into unrelated modules.
- Future evolution can add new domains without collapsing existing boundaries.

## Alternatives considered
- Monolithic service design.
- Shared global state across modules.

## Notes
Historical rationale not recorded.
