# Market Structure Engine

## Purpose

The MarketStructureEngine validates institutional structure state using a fixed eight-rule framework.

## Scope

Implemented rules:

- STR-001
- STR-002
- STR-003
- STR-004
- STR-005
- STR-006
- STR-007
- STR-008

## Swing Importance

The engine includes `SwingImportance` classification:

- `MAJOR`
- `MINOR`
- `INTERNAL`

## Input

`MarketStructureEngine.evaluate` expects:

- `trend`: `BULLISH | BEARISH | RANGE | UNKNOWN`
- `breakDirection`: `BULLISH | BEARISH | NONE`
- `swingHigh`: `float | None`
- `swingLow`: `float | None`
- `bos`: `bool`
- `choch`: `bool`
- `liquiditySweep`: `bool`
- `displacement`: `bool`
- `timeframeAligned`: `bool`
- `swingImportance`: `MAJOR | MINOR | INTERNAL`

## Output Contract

The result contract is `MarketStructureResult` and contains:

- `valid`
- `trend`
- `breakDirection`
- `swingHigh`
- `swingLow`
- `bos`
- `choch`
- `mss`
- `liquiditySweep`
- `displacement`
- `timeframeAligned`
- `swingImportance`
- `passedRules`
- `failedRules`
- `reasons`
- `warnings`

## Validation Behavior

- Each rule writes to `passedRules` or `failedRules`.
- Passed rules append explanatory text to `reasons`.
- Failed rules append explanatory text to `warnings`.
- `valid` is true only when all eight rules pass.

## Shared Model

- Backend: `backend/app/engines/structure/MarketStructureResult.py`
- Frontend: `frontend/src/models/MarketStructureResult.ts`
