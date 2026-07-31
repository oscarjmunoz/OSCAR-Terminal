# Liquidity Map Engine

## Purpose

The Liquidity Map Engine creates an institutional liquidity map from fixed higher-timeframe references.
It identifies key liquidity levels and computes proximity and consumption state around current price.

## Scope

The engine is responsible for:

- Detecting PDH, PDL, PWH, PWL
- Detecting H4 Swing High and H4 Swing Low
- Calculating distance from current price to each level
- Calculating whether liquidity has been taken
- Returning nearest Buy Side Liquidity (BSL)
- Returning nearest Sell Side Liquidity (SSL)

## Inputs

- `currentPrice`
- `pdh`
- `pdl`
- `pwh`
- `pwl`
- `h4Candles` with `high` and `low`

## Detection Rules

### Static Levels

- `PDH`: previous day high (input)
- `PDL`: previous day low (input)
- `PWH`: previous week high (input)
- `PWL`: previous week low (input)

### H4 Swing High / Low

- Uses local pivot detection over H4 candles
- A swing high is a candle high above the two candles before and after
- A swing low is a candle low below the two candles before and after
- If no pivots are found, fallback to max high / min low of available H4 candles

## Calculations

### Distance

For each level:

- `distance = abs(level - currentPrice)`

### Liquidity Taken

- Buy Side Liquidity (`BSL`) is considered taken when `currentPrice >= level`
- Sell Side Liquidity (`SSL`) is considered taken when `currentPrice <= level`

### Nearest Liquidity

- `nearestBuySideLiquidity`: closest non-taken BSL above or at current price; if none, closest BSL by absolute distance
- `nearestSellSideLiquidity`: closest non-taken SSL below or at current price; if none, closest SSL by absolute distance

## Output Contract

The output contract is `LiquidityMap` and includes:

- `pdh`
- `pdl`
- `pwh`
- `pwl`
- `h4SwingHigh`
- `h4SwingLow`
- `liquidityTaken`
- `nearestBuySideLiquidity`
- `nearestSellSideLiquidity`

Shared model files:

- Backend: `backend/app/engines/liquidity/LiquidityMap.py`
- Frontend: `frontend/src/models/LiquidityMap.ts`
