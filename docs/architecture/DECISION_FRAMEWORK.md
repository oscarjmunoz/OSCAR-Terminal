# Decision Framework

## Overview

The institutional Decision Framework standardizes how each engine reports and contributes to the final institutional decision process in OSCAR Terminal v0.7.0-alpha.

The framework is shared by:

- ContextEngine
- LiquidityMapEngine
- PremiumDiscountEngine
- MarketStructureEngine
- MSSEngine
- IEZEngine
- EntryEngine
- TradeManagementEngine
- InstitutionalTradePipeline

## Core Objects

### DecisionStatus

Canonical state model used across all validations:

- `PASS`
- `FAIL`
- `WAIT`
- `WARNING`
- `READY`

### Rule

Atomic rule definition with metadata:

- `id`
- `code`
- `title`
- `description`
- `category`
- `weight`
- `critical`

### RuleResult

Result for each rule execution:

- `rule`
- `status`
- `score`
- `reason`
- `warning`

### EngineResult

Base result contract for every decision engine:

- `engine`
- `status`
- `score`
- `passedRules`
- `failedRules`
- `reasons`
- `warnings`
- `executionTime`

### DecisionNode

Represents one completed engine in the decision pipeline:

- `engine`
- `status`
- `score`
- `rules`
- `timestamp`
- `duration`

### DecisionTree

Represents complete institutional reasoning:

- `nodes`
- `overallScore`
- `currentStep`
- `nextStep`
- `blockedBy`
- `timeline`

### Score

Utility object for normalized score representation (`value`, `max_value`, `percentage`).

## Object Relationships

1. `Rule` defines validation behavior and semantics.
2. Engines execute rules and return `RuleResult` objects.
3. Engine-level aggregation is produced via `EngineResult`.
4. `EngineResult` is converted into a `DecisionNode`.
5. `DecisionNode` objects are appended into a `DecisionTree`.
6. `DecisionTree` tracks progression, blockers, and overall score.

## Responsibilities

- Ensure every engine uses the same status language.
- Ensure every rule execution has a typed result.
- Ensure pipeline orchestration can reason over a uniform node graph.
- Provide deterministic structure for audits and explainability.

## Future Integration with InstitutionalTradePipeline

The InstitutionalTradePipeline will consume `DecisionTree` as the canonical reasoning timeline.
Each stage engine will publish an `EngineResult` node.
Pipeline gating can use `blockedBy`, `overallScore`, and status transitions to stop, wait, or continue processing.
