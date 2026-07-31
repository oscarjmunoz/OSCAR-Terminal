import { CandleResponse } from "../../api/market";
import { Swing } from "../../api/smartMoney";
import { PremiumDiscountState } from "../pipeline/types";

export function createPremiumDiscount(candles: CandleResponse[], swings: Swing[]): PremiumDiscountState[] {
  if (!candles.length) return [];

  const mainSwing = [...swings].sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime())[0];
  const last = candles[candles.length - 1];
  const currentPrice = last.close;
  const referencePrice = mainSwing?.price ?? currentPrice;

  if (currentPrice > referencePrice) {
    return [{ type: "PREMIUM", price: currentPrice, index: candles.length - 1 }];
  }

  if (currentPrice < referencePrice) {
    return [{ type: "DISCOUNT", price: currentPrice, index: candles.length - 1 }];
  }

  return [{ type: "EQUILIBRIUM", price: currentPrice, index: candles.length - 1 }];
}
