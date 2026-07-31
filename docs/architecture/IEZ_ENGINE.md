# Institutional Entry Zone Engine

## Purpose

The Institutional Entry Zone (IEZ) Engine validates whether current price is positioned inside a qualified institutional entry zone with confluence and context alignment.

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

## Output Contract

The output contract is `InstitutionalEntryZone` and includes:

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

## Scoring

- `IEZ Score`: percentage based on number of passed rules
- `Entry Priority`:
  - `HIGH`: valid and score >= 90
  - `MEDIUM`: valid and score >= 75
  - `LOW`: valid below 75 or invalid with score >= 70
  - `NONE`: invalid with score < 70
- `Quality Score`: IEZ score plus confluence/alignment bonus, capped at 100

## Shared Model

- Backend: `backend/app/engines/iez/InstitutionalEntryZone.py`
- Frontend: `frontend/src/models/InstitutionalEntryZone.ts`
