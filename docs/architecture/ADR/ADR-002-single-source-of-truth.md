# ADR-002: Single Source of Truth for Analysis

- Status: Accepted
- Date: 2026-07-31

## Context

Duplicated calculations across modules produce divergence and harder debugging.

## Decision

Use a single canonical analysis pipeline output as the source of truth for upper layers.

## Consequences

- UI and secondary engines consume canonical outputs.
- Reduced risk of contradictory states.
- Lower maintenance cost for strategy and validation evolution.
