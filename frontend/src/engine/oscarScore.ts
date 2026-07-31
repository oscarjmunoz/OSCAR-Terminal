import { TerminalStatus, TickResponse } from "../api/market";
import { MarketStructure } from "../api/smartMoney";
import { LiquidityLevel } from "./liquidity/types";
import { MarketContext } from "./context/types";

export interface OscarScore {
  score: number;
  decision: "BUY" | "SELL" | "WAIT" | "NO TRADE";
  confidence: number;
  reason: string[];
}

export function calculateOscarScore(
  structure: MarketStructure | null,
  tick: TickResponse | null,
  status: TerminalStatus | null,
  context?: MarketContext | null,
  liquidity?: LiquidityLevel[],
  orderBlocks?: Array<{ type: string; status: string }> | null,
  fairValueGaps?: Array<{ type: string; status: string }> | null,
  premiumDiscount?: Array<{ type: string }> | null
): OscarScore {
  let score = 0;
  const reason: string[] = [];

  if (!structure) {
    return {
      score: 0,
      decision: "NO TRADE",
      confidence: 0,
      reason: ["No structure available"],
    };
  }

  if (structure.trend === "BULLISH") {
    score += 20;
    reason.push("Bullish trend");
  } else if (structure.trend === "BEARISH") {
    score += 20;
    reason.push("Bearish trend");
  } else {
    reason.push("Range or unknown trend");
  }

  if (structure.bos) {
    score += 15;
    reason.push("BOS confirmed");
  }

  if (structure.choch) {
    score -= 10;
    reason.push("CHoCH detected");
  }

  if (structure.mss) {
    score += 10;
    reason.push("MSS confirmed");
  }

  if (context?.connected) {
    score += 10;
    reason.push("MT5 connected");
  }

  if (liquidity && liquidity.length) {
    score += 10;
    reason.push("Liquidity identified");
  }

  if (orderBlocks && orderBlocks.length) {
    score += 10;
    reason.push("Order blocks identified");
  }

  if (fairValueGaps && fairValueGaps.length) {
    score += 10;
    reason.push("FVGs detected");
  }

  if (premiumDiscount && premiumDiscount.length) {
    score += 5;
    reason.push("Premium/discount context available");
  }

  if (tick?.spread !== undefined) {
    if (tick.spread <= 2) {
      score += 10;
      reason.push("Low spread");
    } else {
      score -= 15;
      reason.push("High spread");
    }
  }

  score = Math.max(0, Math.min(100, score));

  let decision: OscarScore["decision"] = "NO TRADE";
  let confidence = Math.min(100, Math.round(score * 0.9));

  if (score >= 80) {
    decision = structure.trend === "BEARISH" ? "SELL" : "BUY";
    confidence = Math.max(confidence, 80);
  } else if (score >= 60) {
    decision = "WAIT";
    confidence = Math.max(confidence, 70);
  } else if (score >= 40) {
    decision = "WAIT";
    confidence = Math.max(confidence, 60);
  }

  return {
    score,
    decision,
    confidence,
    reason,
  };
}
