# Institutional Decision Engine

## Purpose

The Institutional Decision Engine is a pure orchestration layer.

It does not detect structure, liquidity, MSS, premium/discount, or confluence.
It only consumes validated engine outputs and emits one institutional decision state.

Execution is explicitly outside this engine. A future Execution Engine translates decision states into orders.

## Inputs

The engine expects already-evaluated outputs from:

- Liquidity Map Engine (`liquidity`)
- Context Engine (`context`)
- Premium/Discount Engine (`premiumDiscount`)
- MSS Engine (`mss`)
- Confluence Engine (`confluence`)
- Score Engine (`score`)

The Decision Engine consumes these outputs as contracts and does not depend on internal implementation details.

## Output

`InstitutionalDecisionResult` is an `EngineResult`-derived model with:

- `valid`
- `decisionState` (`VALID_LONG | VALID_SHORT | INVALID`)
- `direction` (`BULLISH | BEARISH | NONE`)
- `institutionalScore`
- `confidence`
- `blockedBy`
- `failedAt`
- `criticalFailure`
- `engineSequence`
- `summary`
- `status`
- `passedRules`
- `failedRules`
- `reasons`
- `warnings`
- `executionTime`

## Rule Families

Rule identifiers for this engine are `IDE-*`:

- `IDE-001`: Context valid
- `IDE-002`: Liquidity map available
- `IDE-003`: Premium/Discount valid
- `IDE-004`: MSS valid
- `IDE-005`: Confluence valid and in-zone
- `IDE-006`: Directional coherence (MSS and Confluence)
- `IDE-007`: Directional location coherence
- `IDE-008`: Score output valid

## Decision States

- `VALID_LONG`: valid setup with bullish direction
- `VALID_SHORT`: valid setup with bearish direction
- `INVALID`: setup not tradable at decision layer

## Decision vs Execution Responsibilities

Decision Engine responsibilities:

- evaluate cross-engine validation consistency
- classify the setup as `VALID_LONG`, `VALID_SHORT`, or `INVALID`
- expose traceability and failure context

Execution Engine responsibilities:

- translate decision state into order actions
- handle order placement, risk, and lifecycle

## Status Model

- `PASS`: all rules pass
- `FAIL`: one or more critical rules fail
- `WARNING`: only non-critical rules fail

Critical failures stop orchestration immediately and mark `failedAt` and `criticalFailure`.

## Institutional Score

- `institutionalScore` is consumed from Score Engine output.
- The Decision Engine does not calculate a new institutional score.
- `confidence` is consumed from Score Engine output.

## Traceability

- `failedAt`: engine stage where validation stopped (`Context`, `Liquidity`, `PremiumDiscount`, `MSS`, `Confluence`, `Score`, `Decision`, `NONE`)
- `criticalFailure`: normalized blocker identifier, such as `MSS_NOT_CONFIRMED` or `PREMIUM_NOT_VALID`
- `engineSequence`: ordered orchestration path used for debugging and future dashboard visualization:
	- `Liquidity`
	- `Context`
	- `PremiumDiscount`
	- `MSS`
	- `Confluence`
	- `Score`
	- `Decision`

## Decision Tree Integration

`InstitutionalDecisionEngine.run(...)` emits a `DecisionNode` and, when a `DecisionTree` is passed:

- appends the node to the tree
- sets `nextStep` to `ExecutionEngine` when valid
- sets `nextStep` to `WAIT` when invalid
