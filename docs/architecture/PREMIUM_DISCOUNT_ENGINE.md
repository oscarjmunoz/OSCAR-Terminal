# Premium Discount Engine

## Purpose

The PremiumDiscountEngine validates price location inside a dealing range and classifies whether price is in premium, discount, or equilibrium.

## Scope

Implemented rules:

- PD-001
- PD-002
- PD-003
- PD-004
- PD-005

This engine does not implement execution logic.

## Input

`PremiumDiscountEngine.evaluate` expects:

- `currentPrice`: float
- `rangeHigh`: float
- `rangeLow`: float
- `bias`: `BULLISH | BEARISH | NEUTRAL`

## Output

The output shape is `PremiumDiscountResult` with:

- `valid`
- `zone`
- `currentPrice`
- `rangeHigh`
- `rangeLow`
- `equilibrium`
- `distanceToEquilibrium`
- `inPremium`
- `inDiscount`
- `inEquilibrium`
- `biasAligned`
- `passedRules`
- `failedRules`
- `reasons`
- `warnings`

## Validation Behavior

- Each rule appends its id to `passedRules` or `failedRules`.
- Passed rules add explanatory entries to `reasons`.
- Failed rules add explanatory entries to `warnings`.
- `valid` is true only when all rules pass.

## Shared Contract

- Backend: `backend/app/engines/premium_discount/PremiumDiscountResult.py`
- Frontend: `frontend/src/models/PremiumDiscountResult.ts`
