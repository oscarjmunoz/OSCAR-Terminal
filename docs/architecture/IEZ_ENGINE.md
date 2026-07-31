# Institutional Entry Zone Engine

## Purpose

The Institutional Entry Zone (IEZ) Engine validates whether current price is positioned inside a qualified institutional entry zone with confluence and context alignment.

This engine is now integrated into the institutional decision framework.

## Scope

Implemented rules:

- IEZ-001
- IEZ-002
- IEZ-003
- IEZ-004
- IEZ-005
- IEZ-006
- IEZ-007

## Input

`IEZEngine.evaluate` expects:

- `direction`: `BULLISH | BEARISH | NONE`
- `entryZoneLow`: `float | None`
- `entryZoneHigh`: `float | None`
- `currentPrice`: `float`
- `discountForLong`: `bool`
- `premiumForShort`: `bool`
- `fvgConfluence`: `bool`
- `obConfluence`: `bool`
- `liquidityContextAligned`: `bool`
- `mssAligned`: `bool`
- `timeframeAligned`: `bool`

`IEZEngine.run` accepts the same input plus an optional `DecisionTree` instance.

## Output Contract

`InstitutionalEntryZone` inherits from `EngineResult` and includes:

- `valid`
- `direction`
- `entryZoneLow`
- `entryZoneHigh`
- `currentPrice`
- `inZone`
- `discountForLong`
- `premiumForShort`
- `fvgConfluence`
- `obConfluence`
- `liquidityContextAligned`
- `mssAligned`
- `timeframeAligned`
- `iezScore`
- `entryPriority`
- `qualityScore`
- `passedRules`
- `failedRules`
- `reasons`
- `warnings`

Framework fields inherited from `EngineResult`:

- `engine`
- `status`
- `score`
- `passedRules` (`RuleResult[]`)
- `failedRules` (`RuleResult[]`)
- `executionTime`

## Scoring

- `IEZ Score`: percentage based on number of passed rules
- `Entry Priority`:
  - `HIGH`: valid and score >= 90
  - `MEDIUM`: valid and score >= 75
  - `LOW`: valid below 75 or invalid with score >= 70
  - `NONE`: invalid with score < 70
- `Quality Score`: IEZ score plus confluence/alignment bonus, capped at 100

## Rule Registry Integration

IEZ validation uses centralized rules from `RuleRegistry`.
Each IEZ rule id (`IEZ-001`..`IEZ-007`) is resolved into metadata before building `RuleResult` entries.

## Decision Node and Decision Tree Integration

- `IEZEngine.evaluate` returns `InstitutionalEntryZone` (`EngineResult`-based object).
- `IEZEngine.run` returns a `DecisionNode`.
- If a `DecisionTree` is provided to `run`, the node is appended to the tree and `nextStep` is set to `EntryEngine`.

## Shared Model

- Backend: `backend/app/engines/iez/InstitutionalEntryZone.py`
- Frontend: `frontend/src/models/InstitutionalEntryZone.ts`
