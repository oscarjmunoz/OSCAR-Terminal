# Context Engine

## Purpose

The Context Engine is the first institutional engine layer.
Its responsibility is restricted to validating context quality before any execution model.

This engine validates only:

1. H4 liquidity taken
2. H1 order block
3. H1 fair value gap

## Scope Constraints

The engine does not generate trade direction and does not calculate execution parameters.

Excluded from this engine:

- BUY generation
- SELL generation
- Entry calculation
- RR calculation

## Output Contract

The output is a `ContextResult` object with the following fields:

- `valid`: Global context validity across the three required validations.
- `contextScore`: Integer score from 0 to 100.
- `reasons`: Positive validation reasons.
- `warnings`: Missing or invalid validation warnings.
- `liquidityTaken`: Normalized H4 liquidity validation details.
- `orderBlock`: Normalized H1 order block validation details.
- `fairValueGap`: Normalized H1 fair value gap validation details.

## Validation Model

### H4 Liquidity

The liquidity input is valid only when:

- timeframe is `H4`
- liquidity sweep flag is true

### H1 Order Block

The order block input is valid only when:

- timeframe is `H1`
- order block present flag is true

### H1 Fair Value Gap

The fair value gap input is valid only when:

- timeframe is `H1`
- fair value gap present flag is true

## Scoring

The score is additive and deterministic:

- H4 liquidity valid: +34
- H1 order block valid: +33
- H1 fair value gap valid: +33

Maximum score: 100

## Shared Contract

The backend and frontend share the same shape for `ContextResult`:

- Backend: `backend/app/engines/context/ContextResult.py`
- Frontend: `frontend/src/models/ContextResult.ts`
