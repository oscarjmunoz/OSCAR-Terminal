# MSS Rules

This document defines the institutional MSS rules used by the first MSS engine implementation.

## MSS-001

Structure break is valid only if direction is not `NONE` and `brokenStructureLevel` is present.

## MSS-002

Liquidity sweep must be confirmed.

## MSS-003

Displacement must be confirmed.

## MSS-004

A fair value gap must be created after the shift.

## MSS-005

Directional bias must be aligned with the shift direction.

## MSS-006

Sweep side must be coherent with direction:

- `BULLISH` requires sweep side `SSL`
- `BEARISH` requires sweep side `BSL`

If direction is `NONE`, this rule fails.

## Notes

- Only these six rules are evaluated in this version.
- The rules do not generate entries, RR, or trade execution signals.
