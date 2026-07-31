import { CandleResponse } from "../../api/market";
import { FairValueGapState } from "../pipeline/types";

export function createFairValueGaps(candles: CandleResponse[]): FairValueGapState[] {
  if (candles.length < 3) return [];

  const last = candles[candles.length - 1];
  const previous = candles[candles.length - 2];
  const beforePrevious = candles[candles.length - 3];
  const index = candles.length - 1;

  const bullishGap = last.low > beforePrevious.high;
  const bearishGap = last.high < beforePrevious.low;

  if (bullishGap) {
    return [
      {
        type: "BULLISH_FVG",
        price: (previous.low + last.low) / 2,
        index,
        status: "OPEN",
      },
    ];
  }

  if (bearishGap) {
    return [
      {
        type: "BEARISH_FVG",
        price: (previous.high + last.high) / 2,
        index,
        status: "OPEN",
      },
    ];
  }

  return [
    {
      type: "OPEN",
      price: last.close,
      index,
      status: "OPEN",
    },
  ];
}
