import { LiquidityLevel } from "../liquidity/types";
import { MarketStructure } from "../../api/smartMoney";
import { TerminalStatus, TickResponse } from "../../api/market";

export type MarketTrend = "BULLISH" | "BEARISH" | "RANGE";
export type MarketBias = "LONG" | "SHORT" | "NEUTRAL";
export type MarketPhase = "IMPULSE" | "PULLBACK" | "ACCUMULATION" | "DISTRIBUTION";
export type LiquiditySide = "BUY_SIDE" | "SELL_SIDE" | "BALANCED";
export type MarketSession = "ASIA" | "LONDON" | "NEW_YORK" | "CLOSED";

export interface MarketContext {
  trend: MarketTrend;
  bias: MarketBias;
  phase: MarketPhase;
  liquidity: LiquiditySide;
  session: MarketSession;
  connected: boolean;
  premiumDiscount: string;
}

export interface MarketContextInput {
  structure: MarketStructure | null;
  liquidityLevels: LiquidityLevel[];
  tick: TickResponse | null;
  status: TerminalStatus | null;
}
