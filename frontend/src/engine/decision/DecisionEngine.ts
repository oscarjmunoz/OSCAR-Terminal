import { InstitutionalAnalysis } from "../pipeline/types";

export function createDecision(analysis: InstitutionalAnalysis) {
  const { structure, liquidity, context, orderBlocks, fairValueGaps, premiumDiscount, score } = analysis;

  let decision: "BUY" | "SELL" | "WAIT" | "NO TRADE" = "NO TRADE";
  let confidence = 0;
  const reasons: string[] = [];

  if (!structure) {
    return { type: "NO TRADE" as const, confidence: 0, reason: ["No structure available"] };
  }

  if (structure.trend === "BULLISH") {
    reasons.push("Bullish trend");
  } else if (structure.trend === "BEARISH") {
    reasons.push("Bearish trend");
  }

  if (structure.bos) {
    reasons.push("BOS present");
  }

  if (structure.choch) {
    reasons.push("CHoCH present");
  }

  if (liquidity.length) {
    reasons.push("Liquidity levels detected");
  }

  if (orderBlocks.length) {
    reasons.push("Order blocks identified");
  }

  if (fairValueGaps.length) {
    reasons.push("Fair value gaps identified");
  }

  if (premiumDiscount.length) {
    reasons.push("Premium/discount zone available");
  }

  if (context?.connected) {
    reasons.push("MT5 connected");
  }

  if (score && score.score >= 80) {
    decision = structure.trend === "BEARISH" ? "SELL" : "BUY";
    confidence = Math.min(95, score.score);
  } else if (score && score.score >= 60) {
    decision = "WAIT";
    confidence = 70;
  } else if (score && score.score >= 40) {
    decision = "WAIT";
    confidence = 55;
  }

  return { type: decision, confidence, reason: reasons };
}
