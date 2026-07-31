import { useEffect, useMemo, useState } from "react";
import { ISeriesApi, PriceLine } from "lightweight-charts";

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

    const priceLines: PriceLine[] = levels.map((level) =>
      candleSeries.createPriceLine({
        price: level.price,
        color: level.type === "BSL" ? "#22c55e" : level.type === "SSL" ? "#ef4444" : "#64748b",
        lineWidth: 2,
        lineStyle: 0,
        axisLabelVisible: true,
        title: level.type,
      })
    );

    return () => {
      priceLines.forEach((line) => line.remove());
    };
  }, [candleSeries, levels]);

  return null;
}
