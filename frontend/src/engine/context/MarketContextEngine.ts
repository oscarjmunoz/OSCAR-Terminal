import { MarketContext, MarketContextInput } from "./types";

export function createMarketContext(input: MarketContextInput): MarketContext {
  const { structure, liquidityLevels, tick, status } = input;

  const trend = structure?.trend ?? "RANGE";
  const bias = trend === "BULLISH" ? "LONG" : trend === "BEARISH" ? "SHORT" : "NEUTRAL";

  let phase: MarketContext["phase"] = "ACCUMULATION";
  if (structure?.bos) {
    phase = "IMPULSE";
  } else if (structure?.choch) {
    phase = "PULLBACK";
  } else if (structure?.mss) {
    phase = "DISTRIBUTION";
  }

  let liquidity: MarketContext["liquidity"] = "BALANCED";
  const buySideCount = liquidityLevels.filter((level) => level.type === "BSL").length;
  const sellSideCount = liquidityLevels.filter((level) => level.type === "SSL").length;
  if (buySideCount > sellSideCount) {
    liquidity = "BUY_SIDE";
  } else if (sellSideCount > buySideCount) {
    liquidity = "SELL_SIDE";
  }

  let session: MarketContext["session"] = "CLOSED";
  const hour = new Date().getHours();
  if (hour >= 0 && hour < 8) {
    session = "ASIA";
  } else if (hour >= 8 && hour < 16) {
    session = "LONDON";
  } else {
    session = "NEW_YORK";
  }

  const premiumDiscount = tick ? (tick.ask > tick.bid ? "Premium" : "Discount") : "Placeholder";

  return {
    trend,
    bias,
    phase,
    liquidity,
    session,
    connected: status?.connected ?? false,
    premiumDiscount,
  };
}
