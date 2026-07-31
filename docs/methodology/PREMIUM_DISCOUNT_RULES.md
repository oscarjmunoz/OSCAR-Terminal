# Premium Discount Rules

This document defines the deterministic rules used by the PremiumDiscountEngine.

## PD-001

The dealing range is valid when `rangeHigh > rangeLow`.

## PD-002

The current price must remain inside the dealing range:

- `rangeLow <= currentPrice <= rangeHigh`

## PD-003

A premium/discount classification must be available:

- `PREMIUM`
- `DISCOUNT`
- `EQUILIBRIUM`

If the range is invalid, classification is `UNKNOWN` and this rule fails.

## PD-004

Zone flags must be coherent and mutually exclusive:

- Exactly one of `inPremium`, `inDiscount`, `inEquilibrium` must be true.

## PD-005

Bias must align with the zone:

- `BULLISH` aligns with `DISCOUNT` or `EQUILIBRIUM`
- `BEARISH` aligns with `PREMIUM` or `EQUILIBRIUM`
- `NEUTRAL` always aligns when zone is known

If zone is `UNKNOWN`, this rule fails.

## Notes

- Only PD-001..PD-005 are evaluated.
- The engine is validation-only and does not produce entries, RR, or execution signals.
