# Institutional Decision Rules

This file defines the deterministic validation rules used by `InstitutionalDecisionEngine`.

The Decision Engine is orchestration-only and consumes outputs from upstream engines.
It does not perform market analysis or trade execution.

## IDE-001 Context Valid (Critical)

`context.valid` must be `True`.

## IDE-002 Liquidity Available (Critical)

`liquidity` must contain the required map levels and nearest liquidity references.

## IDE-003 Premium/Discount Valid (Critical)

`premiumDiscount.valid` must be `True`.

## IDE-004 MSS Valid (Critical)

`mss.valid` must be `True`.

## IDE-005 Confluence Active (Critical)

Both conditions are required:

- `confluence.valid == True`
- `confluence.inInstitutionalZone == True`

## IDE-006 Directional Coherence (Critical)

Directional modules must agree and none can be `NONE`:

- `mss.direction`
- `confluence.direction`

## IDE-007 Directional Location Coherence (Non-Critical)

Direction must align with PD zone:

- `BULLISH` => `DISCOUNT` or `EQUILIBRIUM`
- `BEARISH` => `PREMIUM` or `EQUILIBRIUM`

## IDE-008 Score Valid (Non-Critical)

`score.valid` must be `True`.

## Critical vs Non-Critical Behavior

- Critical failures invalidate immediately.
- On critical failure, orchestration stops and sets:
	- `failedAt`
	- `criticalFailure`
- Non-critical failures produce warnings and keep rule traceability.

## Scoring

Rule weights are fixed and sum to 100:

- `IDE-001`: 15
- `IDE-002`: 15
- `IDE-003`: 12
- `IDE-004`: 12
- `IDE-005`: 14
- `IDE-006`: 12
- `IDE-007`: 10
- `IDE-008`: 10

Institutional score is consumed from Score Engine (`score.institutionalScore`).

Confidence is consumed from Score Engine (`score.confidence`).

The Decision Engine does not calculate a new institutional score.

## Decision States

- `VALID_LONG`
- `VALID_SHORT`
- `INVALID`

These states are decision outputs only and are later translated by Execution Engine.

## Engine Sequence

Ordered orchestration sequence:

- `Liquidity`
- `Context`
- `PremiumDiscount`
- `MSS`
- `Confluence`
- `Score`
- `Decision`

This sequence is exposed as `engineSequence` for debugging and future visualization.

## Resolution

- All rules pass => valid setup (`PASS`)
- Any critical rule fails => blocked (`FAIL`)
- Only non-critical failures => conditional setup (`WARNING`)
