# IEZ Rules

This document defines the deterministic rule-set for the Institutional Entry Zone Engine.

## IEZ-001

Direction must be defined (`BULLISH` or `BEARISH`).

## IEZ-002

Entry zone boundaries must be present:

- `entryZoneLow`
- `entryZoneHigh`

## IEZ-003

Zone structure must be valid:

- `entryZoneHigh > entryZoneLow`

## IEZ-004

Current price must be inside the zone:

- `entryZoneLow <= currentPrice <= entryZoneHigh`

## IEZ-005

Directional location alignment:

- `BULLISH` requires `discountForLong == True`
- `BEARISH` requires `premiumForShort == True`

## IEZ-006

Confluence validation:

- `fvgConfluence == True`
- `obConfluence == True`

## IEZ-007

Context alignment validation:

- `liquidityContextAligned == True`
- `mssAligned == True`
- `timeframeAligned == True`

## Scores

- `IEZ Score`: percentage based on passed rules (0-100)
- `Entry Priority`: derived from score and global validity (`HIGH`, `MEDIUM`, `LOW`, `NONE`)
- `Quality Score`: IEZ score plus capped confluence/alignment bonus

## Notes

- This engine is validation-only.
- It does not generate orders, RR, or risk execution plans.
