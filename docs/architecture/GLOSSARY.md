# OSCAR Canonical Glossary

This glossary captures the terms used by the current OSCAR implementation and architecture documentation. It is intentionally concise and aligned with the repository rather than introducing broader institutional terminology.

## Core Terms

- **Domain**: A bounded responsibility area in OSCAR, such as Scanner, Opportunity, Journal, or Execution.
- **Repository**: A boundary abstraction that isolates domain services from persistence implementation details.
- **Source of Truth**: The authoritative state holder for a given concept. In the current architecture, Scanner snapshots and Journal entries are the primary durable sources of truth for their respective domains.
- **Derived State**: State computed from another authoritative source rather than stored independently. Opportunity state is derived from scanner snapshots and scoring rules.
- **Durable State**: State intended to survive process restarts and remain available across runs. Current durable examples are scanner snapshots and journal entries.
- **Transient State**: State that is useful only for the current runtime cycle and does not need to survive restart. Examples include scheduler runtime state and ephemeral in-memory queue results.

## Scanner Terms

- **Scanner**: The domain that collects market and structure context and produces structured opportunity snapshots for configured symbols.
- **Scanner Snapshot**: A structured record of market context, stage, health, score, and summary information for a symbol and timeframe.

## Opportunity Terms

- **Opportunity**: A prioritized setup candidate produced by evaluating scanner snapshots.
- **Opportunity Engine**: The component that converts scanner snapshots into opportunity results and scoring.

## Decision Terms

- **Decision**: A structured analysis artifact created from market context and recommendation logic.
- **Decision Engine**: The logic that turns context and opportunity signals into a decision report. In the current codebase this is represented by the decision-related schemas and supporting services rather than a single monolithic engine.

## Execution Terms

- **Execution Bridge**: The preparation layer that validates and formats execution artifacts without performing autonomous order submission.
- **Trade Ticket**: A structured execution artifact prepared for manual review and downstream execution handling.
- **Prepare-only**: A mode in which OSCAR can build and validate execution artifacts, but the system does not auto-submit orders.

## Journal and Analytics Terms

- **Journal**: The domain that stores decision snapshots and trader outcomes for traceability and analytics.
- **Analytics**: The domain that consumes journal and playbook data to produce deterministic summaries and reports.

## Lifecycle and Planning Terms

- **Planned**: A capability or feature that is documented as future work and not yet implemented in the current architecture.
- **Implemented**: A capability present in the current repository and reflected in the working architecture.

## Known Ambiguities

- The term “Decision Engine” is currently used informally in the broader architecture. In the implementation, the behavior is distributed across schemas, services, and supporting modules rather than a single named engine class. This document therefore uses the term as a conceptual label rather than a single implementation boundary.
- “Opportunity” can refer either to the raw setup candidate or to the evaluated result object. In this glossary, “Opportunity” refers to the evaluated opportunity concept, while “Scanner Snapshot” refers to the input context from which opportunities are derived.
