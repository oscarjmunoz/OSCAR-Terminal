# OSCAR Engine

## Engine Model

OSCAR uses a pipeline-first model for market interpretation and decision support.

## Core Concepts

- Input normalization: consistent market snapshot shape.
- Sequential analysis: each stage consumes previous stage outputs.
- Strategy abstraction: decisions can be swapped without rewriting the pipeline.
- Validation and backtest layers: post-analysis quality and performance checks.

## Reference Pipeline

1. Market structure input
2. Liquidity interpretation
3. Context classification
4. Order block detection
5. Fair value gap detection
6. Premium/discount zoning
7. Score synthesis
8. Decision output

## Engine Quality Targets

- Deterministic outputs for same inputs.
- Explicit contracts between stages.
- Easy observability and troubleshooting.
- Testable units by engine boundary.

## Operational Notes

- Multi-timeframe composition should consume stage outputs, not re-derive logic.
- Validation and backtest should remain derived products of primary analysis.
