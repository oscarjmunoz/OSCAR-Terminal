export type TradePlanOrderType = "MARKET" | "LIMIT" | "STOP";

export type TradePlanState = "DRAFT" | "READY" | "ACTIVE" | "INVALIDATED" | "CLOSED";

export interface TradePlanInstrument {
  symbol: string;
  market: string;
  timeframe: string;
  session: string;
}

export interface TradePlanContext {
  bias: string;
  trend: string;
  phase: string;
  narrative: string;
}

export interface TradePlanConfirmation {
  trigger: string;
  timeframe: string;
  timestamp: string;
  confluence: string[];
}

export interface TradePlanEntry {
  orderType: TradePlanOrderType;
  price: number;
  window: string;
}

export interface TradePlanTargets {
  tp1: number;
  tp2: number;
  runner: string;
}

export interface TradePlanRisk {
  stopLoss: number;
  rr: string;
  riskPercent: number;
}

export interface TradePlanManagement {
  breakEven: string;
  partialExit: string;
  trailingRule: string;
}

export interface TradePlanQuality {
  score: number;
  grade: string;
}

export interface TradePlanStatus {
  state: TradePlanState;
  updatedAt: string;
}

export interface TradePlanChecklist {
  liquidityMapped: boolean;
  structureConfirmed: boolean;
  imbalanceAligned: boolean;
  riskValidated: boolean;
  sessionValidated: boolean;
}

export interface TradePlanInvalidation {
  price: number;
  condition: string;
  reason: string;
}

export interface TradePlan {
  instrument: TradePlanInstrument;
  context: TradePlanContext;
  confirmation: TradePlanConfirmation;
  entry: TradePlanEntry;
  targets: TradePlanTargets;
  risk: TradePlanRisk;
  management: TradePlanManagement;
  quality: TradePlanQuality;
  status: TradePlanStatus;
  checklist: TradePlanChecklist;
  reasons: string[];
  warnings: string[];
  invalidation: TradePlanInvalidation;
}
