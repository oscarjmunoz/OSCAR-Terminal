import { TerminalStatus, TickResponse } from "../api/market";
import { MarketStructure } from "../api/smartMoney";

export interface OscarScore {
  score: number;
  decision: "BUY" | "SELL" | "WAIT" | "NO TRADE";
  confidence: number;
  reason: string[];
}

export function calculateOscarScore(
  structure: MarketStructure | null,
  tick: TickResponse | null,
  status: TerminalStatus | null
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
    score += 25;
    reason.push("Bullish trend");
  } else if (structure.trend === "BEARISH") {
    score += 25;
    reason.push("Bearish trend");
  } else {
    reason.push("Range or unknown trend");
  }

  if (structure.bos) {
    score += 20;
    reason.push("BOS confirmed");
  }

  if (structure.choch) {
    score -= 10;
    reason.push("CHoCH detected");
  }

  if (structure.mss) {
    score += 15;
    reason.push("MSS confirmed");
  }

  if (status?.connected) {
    score += 10;
    reason.push("MT5 connected");
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
