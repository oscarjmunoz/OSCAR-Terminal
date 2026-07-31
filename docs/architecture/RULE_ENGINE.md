# Rule Engine

## Purpose

The Rule Engine layer provides a unified registry and execution vocabulary for institutional validations.

## Architecture

### Rule Registry Modules

The registry is split by domain:

- `ContextRules.py`
- `LiquidityRules.py`
- `StructureRules.py`
- `PremiumDiscountRules.py`
- `MSSRules.py`
- `IEZRules.py`
- `EntryRules.py`
- `RiskRules.py`
- `ManagementRules.py`

Each module exposes:

- a list of `Rule`
- a `*_RULES_BY_ID` map

### Rule IDs

Standardized identifiers include:

- `CTX-*`
- `LIQ-*`
- `STR-*`
- `PD-*`
- `MSS-*`
- `IEZ-*`
- `ENT-*`
- `RISK-*`
- `MANAGEMENT-*`

## Responsibilities

- Centralize rule definitions and metadata.
- Keep rule weighting and criticality explicit.
- Enable deterministic, auditable rule evaluation.

## Integration Flow

1. An engine loads relevant rule definitions from registry.
2. The engine evaluates market data and returns `RuleResult` objects.
3. Rule results are aggregated in an `EngineResult`.
4. `EngineResult` is inserted as `DecisionNode` into `DecisionTree`.

## Pipeline Integration

InstitutionalTradePipeline can use the registry and framework to:

- enforce mandatory critical rules
- block progression on specific failed rule families
- score and rank institutional opportunities consistently

## Extensibility

To add new rule families:

1. Create a new registry module under `backend/app/rules`.
2. Add typed `Rule` definitions.
3. Expose list and ID map.
4. Consume in target engine with `RuleResult` aggregation.
