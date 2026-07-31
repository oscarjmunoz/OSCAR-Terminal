import { InstitutionalAnalysis } from "../pipeline/types";
import { Strategy } from "./Strategy";
import { StrategyDecision } from "./types";

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

export class ICTStrategy implements Strategy {
  id = "ict";
  name = "ICT Strategy";
  description = "Deterministic ICT confluence strategy based on institutional analysis.";

  evaluate(analysis: InstitutionalAnalysis): StrategyDecision {
    const { structure, context, liquidity, orderBlocks, fairValueGaps, premiumDiscount, score } = analysis;

    if (!structure) {
      return {
        decision: "NO TRADE",
        confidence: 0,
        reasons: ["No structure available"],
      };
    }

    const reasons: string[] = [];
    let adjustedScore = score?.score ?? 0;

    const bullishOb = orderBlocks.some((item) => item.type === "BULLISH_OB" && item.status === "UNMITIGATED");
    const bearishOb = orderBlocks.some((item) => item.type === "BEARISH_OB" && item.status === "UNMITIGATED");
    const bullishFvg = fairValueGaps.some((item) => item.type === "BULLISH_FVG" && item.status === "OPEN");
    const bearishFvg = fairValueGaps.some((item) => item.type === "BEARISH_FVG" && item.status === "OPEN");
    const discountZone = premiumDiscount.some((item) => item.type === "DISCOUNT");
    const premiumZone = premiumDiscount.some((item) => item.type === "PREMIUM");
    const hasBuyLiquidity = liquidity.some((item) => item.type === "BSL");
    const hasSellLiquidity = liquidity.some((item) => item.type === "SSL");

    if (context?.connected) {
      reasons.push("MT5 connected");
    }

    if (structure.trend === "BULLISH") {
      reasons.push("Bullish trend");
    } else if (structure.trend === "BEARISH") {
      reasons.push("Bearish trend");
    } else {
      reasons.push("Range trend");
    }

    if (structure.bos) {
      adjustedScore += 5;
      reasons.push("BOS present");
    }

    if (structure.choch) {
      adjustedScore -= 5;
      reasons.push("CHoCH present");
    }

    if (structure.mss) {
      adjustedScore += 5;
      reasons.push("MSS present");
    }

    if (bullishOb || bearishOb) {
      adjustedScore += 3;
      reasons.push("Order block confluence");
    }

    if (bullishFvg || bearishFvg) {
      adjustedScore += 3;
      reasons.push("FVG confluence");
    }

    if (discountZone || premiumZone) {
      adjustedScore += 2;
      reasons.push("Premium/discount context");
    }

    if (hasBuyLiquidity || hasSellLiquidity) {
      adjustedScore += 2;
      reasons.push("Liquidity context");
    }

    adjustedScore = clamp(adjustedScore, 0, 100);

    const bullishConfluence =
      structure.trend === "BULLISH" &&
      (context?.bias === "LONG" || context?.bias === "NEUTRAL") &&
      bullishOb &&
      bullishFvg &&
      discountZone;

    const bearishConfluence =
      structure.trend === "BEARISH" &&
      (context?.bias === "SHORT" || context?.bias === "NEUTRAL") &&
      bearishOb &&
      bearishFvg &&
      premiumZone;

    let decision: StrategyDecision["decision"] = "NO TRADE";

    if (adjustedScore >= 80) {
      if (bullishConfluence || (structure.trend === "BULLISH" && hasBuyLiquidity)) {
        decision = "BUY";
      } else if (bearishConfluence || (structure.trend === "BEARISH" && hasSellLiquidity)) {
        decision = "SELL";
      } else {
        decision = structure.trend === "BEARISH" ? "SELL" : "BUY";
      }
    } else if (adjustedScore >= 60) {
      decision = "WAIT";
    } else if (adjustedScore >= 40) {
      decision = "WAIT";
    }

    const confidence =
      decision === "BUY" || decision === "SELL"
        ? clamp(Math.max(80, adjustedScore), 0, 95)
        : decision === "WAIT"
          ? clamp(Math.max(55, Math.round(adjustedScore * 0.9)), 0, 90)
          : clamp(Math.round(adjustedScore * 0.7), 0, 60);

    return {
      decision,
      confidence,
      reasons,
    };
  }
}
