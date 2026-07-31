# Trade Plan Contract

## Purpose

The Trade Plan is the central institutional contract used to describe a single trade idea without embedding execution logic.
It is shared between backend and frontend with the same field structure.

## Top-Level Fields

- Instrument
- Context
- Confirmation
- Entry
- Targets
- Risk
- Management
- Quality
- Status
- Checklist
- Reasons
- Warnings
- Invalidation

## Field Definitions

### Instrument

Identifies what is being traded and where.

- `symbol`: Broker or platform symbol.
- `market`: Market family or venue (for example, FX, Indices, Commodities).
- `timeframe`: Operating timeframe used for the plan.
- `session`: Trading session context.

### Context

Captures directional and structural background.

- `bias`: Directional bias label.
- `trend`: Current trend state.
- `phase`: Market phase label.
- `narrative`: Human-readable summary of the setup context.

### Confirmation

Defines what confirms execution readiness.

- `trigger`: Main trigger description.
- `timeframe`: Timeframe where trigger is validated.
- `timestamp`: ISO timestamp for confirmation event.
- `confluence`: List of confluence factors.

### Entry

Defines planned entry parameters.

- `orderType`: One of `MARKET`, `LIMIT`, `STOP`.
- `price`: Planned entry price.
- `window`: Entry timing window description.

### Targets

Defines profit objectives.

- `tp1`: First target level.
- `tp2`: Second target level.
- `runner`: Runner objective or destination.

### Risk

Defines risk metrics.

- `stopLoss`: Stop loss level.
- `rr`: Risk-to-reward expression.
- `riskPercent`: Risk as percent of account/equity.

### Management

Defines post-entry management rules.

- `breakEven`: Break-even rule.
- `partialExit`: Partial take-profit rule.
- `trailingRule`: Trailing management rule.

### Quality

Defines setup quality metadata.

- `score`: Numeric quality score.
- `grade`: Qualitative quality label.

### Status

Defines lifecycle state.

- `state`: One of `DRAFT`, `READY`, `ACTIVE`, `INVALIDATED`, `CLOSED`.
- `updatedAt`: ISO timestamp of last status update.

### Checklist

Defines binary readiness checks.

- `liquidityMapped`: Liquidity mapping is complete.
- `structureConfirmed`: Structure confirmation is complete.
- `imbalanceAligned`: Imbalance/FVG alignment is complete.
- `riskValidated`: Risk constraints are validated.
- `sessionValidated`: Session constraints are validated.

### Reasons

List of reasons supporting the plan.

- `reasons`: Ordered list of rationale strings.

### Warnings

List of risks or caveats.

- `warnings`: Ordered list of warning strings.

### Invalidation

Defines invalidation criteria.

- `price`: Invalidation price level.
- `condition`: Condition that triggers invalidation.
- `reason`: Human-readable invalidation explanation.

## Canonical Shape

```json
{
  "instrument": {
    "symbol": "string",
    "market": "string",
    "timeframe": "string",
    "session": "string"
  },
  "context": {
    "bias": "string",
    "trend": "string",
    "phase": "string",
    "narrative": "string"
  },
  "confirmation": {
    "trigger": "string",
    "timeframe": "string",
    "timestamp": "string",
    "confluence": ["string"]
  },
  "entry": {
    "orderType": "MARKET | LIMIT | STOP",
    "price": 0,
    "window": "string"
  },
  "targets": {
    "tp1": 0,
    "tp2": 0,
    "runner": "string"
  },
  "risk": {
    "stopLoss": 0,
    "rr": "string",
    "riskPercent": 0
  },
  "management": {
    "breakEven": "string",
    "partialExit": "string",
    "trailingRule": "string"
  },
  "quality": {
    "score": 0,
    "grade": "string"
  },
  "status": {
    "state": "DRAFT | READY | ACTIVE | INVALIDATED | CLOSED",
    "updatedAt": "string"
  },
  "checklist": {
    "liquidityMapped": true,
    "structureConfirmed": true,
    "imbalanceAligned": true,
    "riskValidated": true,
    "sessionValidated": true
  },
  "reasons": ["string"],
  "warnings": ["string"],
  "invalidation": {
    "price": 0,
    "condition": "string",
    "reason": "string"
  }
}
```
