# Institutional Decision Architecture

## Objective

This module provides a single institutional pipeline that orchestrates all decision engines without embedding business logic in orchestration.

## Pipeline Flow

1. Market Data
2. Liquidity Analysis
3. Structure Analysis
4. Institutional Context
5. Risk Analysis
6. Institutional Decision
7. Execution Recommendation

## Responsibilities by Module

- `InstitutionalPipeline.py`
  - Orchestrates engine execution order.
  - Aggregates typed outputs into immutable `DecisionContext`.
  - Does not implement business rules.

- `PipelineModels.py`
  - Defines strict typed inputs and immutable output models.
  - Exposes `DecisionContext` and standardized engine result models.

- `RiskEngine.py`
  - Validates risk constraints from config thresholds.

- `ConfluenceEngine.py`
  - Normalizes directional/institutional confluence checks.

- `InstitutionalScoreEngine.py`
  - Computes weighted institutional score from configurable weights.

- `ConfidenceEngine.py`
  - Computes confidence independently from score.

- `InstitutionalValidationEngine.py`
  - Detects contradictions and emits deterministic warnings.

- `ExecutionRecommendationEngine.py`
  - Produces final recommendation: BUY, SELL, WAIT, or NO_TRADE.

- `NarrativeEngine.py`
  - Produces deterministic human-readable explanation.

## Configuration

All weights and thresholds are centralized in `app/config/settings.py`:

- Score component weights.
- Confidence factor weights.
- Risk thresholds.
- Decision minimum score and confidence.
- Allowed institutional sessions.

## Compatibility

Legacy engine contracts remain unchanged:

- `LiquidityMapEngine`
- `MarketStructureEngine`
- `ContextEngine`
- `MSSEngine`
- `PremiumDiscountEngine`
- `InstitutionalDecisionEngine`

The pipeline composes them into one output context for OSCAR Terminal consumption.
