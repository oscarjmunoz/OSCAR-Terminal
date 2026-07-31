# MSS Engine

## Purpose

The Institutional MSS Engine validates a Market Structure Shift setup against a fixed six-rule framework.

This implementation is rule-validation only and does not perform trade execution logic.

## Scope

Implemented rules:

- MSS-001
- MSS-002
- MSS-003
- MSS-004
- MSS-005
- MSS-006

Excluded logic:

- Buy/Sell order generation
- Entry calculation
- RR calculation

## Input

`MSSEngine.evaluate` expects:

- `direction`: `BULLISH | BEARISH | NONE`
- `brokenStructureLevel`: `float | None`
- `liquiditySweep`: `bool`
- `displacement`: `bool`
- `fvgCreated`: `bool`
- `biasAligned`: `bool`
- `sweepSide`: `BSL | SSL | NONE`

## Output Contract

The result shape is `MSSResult` and contains:

- `valid`
- `direction`
- `brokenStructureLevel`
- `liquiditySweep`
- `displacement`
- `fvgCreated`
- `biasAligned`
- `passedRules`
- `failedRules`
- `reasons`
- `warnings`

## Validation Behavior

- Each rule appends its id to either `passedRules` or `failedRules`.
- Passed rules append a message to `reasons`.
- Failed rules append a message to `warnings`.
- `valid` is true only when all six rules pass.

## Shared Model

- Backend: `backend/app/engines/mss/MSSResult.py`
- Frontend: `frontend/src/models/MSSResult.ts`
