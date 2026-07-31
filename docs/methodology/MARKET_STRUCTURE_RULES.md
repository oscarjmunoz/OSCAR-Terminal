# Market Structure Rules

This document defines the deterministic rules implemented by the MarketStructureEngine.

## STR-001

Trend context must be known (`BULLISH`, `BEARISH`, or `RANGE`).

## STR-002

Both `swingHigh` and `swingLow` must be present.

## STR-003

`SwingImportance` must be classified as one of:

- `MAJOR`
- `MINOR`
- `INTERNAL`

## STR-004

Swing range coherence:

- `swingHigh > swingLow`

## STR-005

At least one structural event must exist:

- `bos` or `choch`

## STR-006

Break direction must be coherent with trend context:

- `BULLISH` trend requires `BULLISH` break direction
- `BEARISH` trend requires `BEARISH` break direction
- `RANGE` allows either directional break

## STR-007

Confirmation requires both:

- `liquiditySweep == True`
- `displacement == True`

## STR-008

Timeframe alignment must be confirmed:

- `timeframeAligned == True`

## Notes

- Only STR-001..STR-008 are evaluated in this version.
- Engine output is validation-only and does not generate execution entries or risk calculations.
