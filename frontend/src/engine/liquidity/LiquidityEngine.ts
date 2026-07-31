import { CandleResponse } from "../../api/market";
import { Swing } from "../../api/smartMoney";
import { LiquidityEngineOptions, LiquidityLevel } from "./types";

export function createLiquidityLevels(
  candles: CandleResponse[],
  swings: Swing[],
  options: LiquidityEngineOptions = {}
): LiquidityLevel[] {
  const tolerance = options.tolerance ?? 0.0005;
  const currentPrice = options.currentPrice;

  const highs = candles.map((candle, index) => ({ index, price: candle.high }));
  const lows = candles.map((candle, index) => ({ index, price: candle.low }));

  const levels: LiquidityLevel[] = [];

  const equalHighs = highs.filter((item, index, array) => {
    const next = array[index + 1];
    return next !== undefined && Math.abs(item.price - next.price) <= tolerance;
  });

  equalHighs.forEach((item) => {
    levels.push({
      type: "EQH",
      price: item.price,
      index: item.index,
      strength: 1,
    });
  });

  const equalLows = lows.filter((item, index, array) => {
    const next = array[index + 1];
    return next !== undefined && Math.abs(item.price - next.price) <= tolerance;
  });

  equalLows.forEach((item) => {
    levels.push({
      type: "EQL",
      price: item.price,
      index: item.index,
      strength: 1,
    });
  });

  if (currentPrice !== undefined) {
    const swingHighs = swings.filter((swing) => swing.kind === "HIGH");
    const swingLows = swings.filter((swing) => swing.kind === "LOW");

    swingHighs.forEach((swing) => {
      if (swing.price > currentPrice) {
        levels.push({
          type: "BSL",
          price: swing.price,
          index: swing.index,
          strength: 1,
        });
      }
    });

    swingLows.forEach((swing) => {
      if (swing.price < currentPrice) {
        levels.push({
          type: "SSL",
          price: swing.price,
          index: swing.index,
          strength: 1,
        });
      }
    });
  }

  return levels;
}
