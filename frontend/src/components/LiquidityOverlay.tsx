import { useEffect, useMemo, useState } from "react";
import { ISeriesApi } from "lightweight-charts";

import { CandleResponse } from "../api/market";
import { Swing } from "../api/smartMoney";
import { createLiquidityLevels } from "../engine/liquidity/LiquidityEngine";
import { LiquidityLevel } from "../engine/liquidity/types";

type Props = {
  candleSeries: ISeriesApi<"Candlestick"> | null;
  candles: CandleResponse[];
  swings: Swing[];
  currentPrice?: number;
};

export default function LiquidityOverlay({ candleSeries, candles, swings, currentPrice }: Props) {
  const [levels, setLevels] = useState<LiquidityLevel[]>([]);

  const liquidityLevels = useMemo(() => {
    return createLiquidityLevels(candles, swings, { currentPrice });
  }, [candles, swings, currentPrice]);

  useEffect(() => {
    setLevels(liquidityLevels);
  }, [liquidityLevels]);

  useEffect(() => {
    if (!candleSeries) return;

    // TODO: Re-enable liquidity line rendering after lightweight-charts overlay API migration.
    void levels;
  }, [candleSeries, levels]);

  return null;
}
