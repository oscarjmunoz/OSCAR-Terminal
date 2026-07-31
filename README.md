# OSCAR Terminal

Release target: v0.4.0-alpha

## Architecture

OSCAR Lite frontend uses a deterministic, pipeline-first architecture.

- `LiveDataOrchestrator`: single service that builds one shared `MarketSnapshot`.
- `InstitutionalPipeline`: single source of institutional analysis per timeframe.
- Engines: context, liquidity, order blocks, fair value gaps, premium/discount, score, decision.
- Strategy Framework: pluggable strategy layer (default `ICTStrategy`).
- Validation Engine: in-memory signal records from pipeline output.
- Backtest Engine: in-memory simulation from validation records + candles.

No backend logic changes are required for this architecture.

## Pipeline

Execution order inside `InstitutionalPipeline`:

1. MarketStructure input
2. Liquidity Engine
3. Market Context Engine
4. Order Block Engine
5. Fair Value Gap Engine
6. Premium/Discount Engine
7. OSCAR Score Engine
8. Decision Engine (strategy-driven)

Upper layers must consume this output instead of recomputing analysis.

## Engines

- `MarketContextEngine`: trend, bias, phase, liquidity side, session, connection status.
- `LiquidityEngine`: BSL, SSL, EQH, EQL levels.
- `OrderBlockEngine`: bullish/bearish order block + mitigation status.
- `FairValueGapEngine`: bullish/bearish FVG + open/filled status.
- `PremiumDiscountEngine`: premium/equilibrium/discount zone.
- `OscarScoreEngine`: deterministic score and confidence.
- `DecisionEngine`: delegates to active strategy and returns pipeline-compatible decision.
- `MultiTimeframeEngine`: aggregates H4/H1/M15/M5 pipeline analyses and alignment.
- `ValidationEngine`: produces `ValidationRecord` snapshots.
- `BacktestEngine`: produces `BacktestResult` summary + equity curve.

## Data Flow

1. `LiveDataOrchestrator.refreshSnapshot(symbol)` fetches tick, status, candles, and structures for H4/H1/M15/M5.
2. `LiveDataOrchestrator.runEngines(snapshot)` runs `InstitutionalPipeline` once per timeframe.
3. Multi-timeframe alignment is derived from those institutional outputs.
4. Dashboard consumes:
   - `MarketSnapshot`
   - `InstitutionalAnalysis`
   - Strategy-driven decision from pipeline
   - Validation records
   - Backtest summary

## Strategies

Strategy framework components:

- `Strategy` interface
- `ICTStrategy` (default deterministic implementation)
- `StrategyRegistry` for registration and active strategy selection

## Backtest

Backtest v1 risk model:

- Take Profit: `2R`
- Stop Loss: `1R`
- Spread model: disabled
- Slippage model: disabled

Summary metrics:

- `totalSignals`
- `wins`
- `losses`
- `winRate`
- `profitFactor`
- `expectancy`
- `averageRR`
- `equityCurve`

## Stability Notes (v0.4.0-alpha)

- Frontend stabilized around snapshot + pipeline orchestration.
- Institutional pipeline remains the canonical analysis source.
- Engines are deterministic, composable, and test-ready.
