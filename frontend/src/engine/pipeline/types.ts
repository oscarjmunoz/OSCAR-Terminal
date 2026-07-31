import { MarketStructure } from "../../api/smartMoney";
import { TerminalStatus, TickResponse } from "../../api/market";
import { LiquidityLevel } from "../liquidity/types";
import { MarketContext } from "../context/types";
import { OscarScore } from "../oscarScore";

export interface OrderBlockState {
  type: "PLACEHOLDER";
  value: string;
}

export interface FairValueGapState {
  type: "PLACEHOLDER";
  value: string;
}

export interface PremiumDiscountState {
  type: "PLACEHOLDER";
  value: string;
}

export interface DecisionState {
  type: "PLACEHOLDER";
  value: string;
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
