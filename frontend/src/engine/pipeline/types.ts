import { MarketStructure } from "../../api/smartMoney";
import { TerminalStatus, TickResponse } from "../../api/market";
import { LiquidityLevel } from "../liquidity/types";
import { MarketContext } from "../context/types";
import { OscarScore } from "../oscarScore";

export type OrderBlockType = "BULLISH_OB" | "BEARISH_OB" | "MITIGATED" | "UNMITIGATED";
export type FairValueGapType = "BULLISH_FVG" | "BEARISH_FVG" | "FILLED" | "OPEN";
export type PremiumDiscountType = "PREMIUM" | "EQUILIBRIUM" | "DISCOUNT";
export type DecisionType = "BUY" | "SELL" | "WAIT" | "NO TRADE";

export interface OrderBlockState {
  type: OrderBlockType;
  price: number;
  index: number;
  status: "MITIGATED" | "UNMITIGATED";
}

export interface FairValueGapState {
  type: FairValueGapType;
  price: number;
  index: number;
  status: "FILLED" | "OPEN";
}

export interface PremiumDiscountState {
  type: PremiumDiscountType;
  price: number;
  index: number;
}

export interface DecisionState {
  type: DecisionType;
  confidence: number;
  reason: string[];
}

export interface InstitutionalAnalysis {
  structure: MarketStructure | null;
  liquidity: LiquidityLevel[];
  context: MarketContext | null;
  orderBlocks: OrderBlockState[];
  fairValueGaps: FairValueGapState[];
  premiumDiscount: PremiumDiscountState[];
  score: OscarScore | null;
  decision: DecisionState | null;
}

export interface PipelineInput {
  structure: MarketStructure | null;
  tick: TickResponse | null;
  status: TerminalStatus | null;
  candles: Array<{ time: string; open: number; high: number; low: number; close: number }>;
}
