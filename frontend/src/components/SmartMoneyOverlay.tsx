import { useEffect, useState } from "react";
import { ISeriesApi } from "lightweight-charts";

import { MarketStructure, Swing, getStructure, getSwings } from "../api/smartMoney";

type Props = {
  candleSeries: ISeriesApi<"Candlestick"> | null;
};

export default function SmartMoneyOverlay({ candleSeries }: Props) {
  const [swings, setSwings] = useState<Swing[]>([]);
  const [structure, setStructure] = useState<MarketStructure | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [swingsData, structureData] = await Promise.all([getSwings(), getStructure()]);
        setSwings(swingsData);
        setStructure(structureData);
      } catch (error) {
        console.error(error);
      }
    }

    load();
  }, []);

  useEffect(() => {
    if (!candleSeries) return;

    const lastHigh = [...swings].filter((swing) => swing.kind === "HIGH").at(-1);
    const lastLow = [...swings].filter((swing) => swing.kind === "LOW").at(-1);

    const markers = [];

    if (lastHigh) {
      markers.push({
        time: Math.floor(new Date(lastHigh.time).getTime() / 1000) as Time,
        position: "aboveBar",
        shape: "circle",
        color: "#64748b",
        text: "Swing High",
      });
    }

    if (lastLow) {
      markers.push({
        time: Math.floor(new Date(lastLow.time).getTime() / 1000) as Time,
        position: "belowBar",
        shape: "circle",
        color: "#64748b",
        text: "Swing Low",
      });
    }

    // TODO: Re-enable setMarkers once lightweight-charts overlay API compatibility is restored.
    void markers;

    const priceLines = [];

    if (structure?.bos && structure.last_high !== null) {
      priceLines.push({
        price: structure.last_high,
        color: "#22c55e",
        lineWidth: 2,
        lineStyle: 0,
        axisLabelVisible: true,
        title: "BOS",
      });
    }

    if (structure?.choch && structure.last_low !== null) {
      priceLines.push({
        price: structure.last_low,
        color: "#f59e0b",
        lineWidth: 2,
        lineStyle: 0,
        axisLabelVisible: true,
        title: "CHoCH",
      });
    }

    // TODO: Re-enable createPriceLine/remove after migrating to compatible chart primitives.
    void priceLines;
  }, [candleSeries, swings, structure]);

  return null;
}
