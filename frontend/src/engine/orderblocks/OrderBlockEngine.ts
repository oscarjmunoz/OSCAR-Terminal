import { CandleResponse } from "../../api/market";
import { OrderBlockState } from "../pipeline/types";

export function createOrderBlocks(candles: CandleResponse[]): OrderBlockState[] {
  if (candles.length < 2) return [];

  const lastCandle = candles[candles.length - 1];
  const previousCandle = candles[candles.length - 2];
  const lastIndex = candles.length - 1;

  if (lastCandle.close > previousCandle.close) {
    return [
      {
        type: "BULLISH_OB",
        price: lastCandle.close,
        index: lastIndex,
        status: "UNMITIGATED",
      },
    ];
  }

  return [
    {
      type: "BEARISH_OB",
      price: lastCandle.close,
      index: lastIndex,
      status: "UNMITIGATED",
    },
  ];
}
