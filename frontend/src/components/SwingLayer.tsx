import { useEffect, useState } from "react";
import {
    ISeriesApi,
    PriceLine,
    SeriesMarker,
    Time,
} from "lightweight-charts";

import { MarketStructure, Swing, getStructure } from "../api/smartMoney";

type Props = {
    candleSeries: ISeriesApi<"Candlestick"> | null;
    swings: Swing[];
};

export default function SwingLayer({
    candleSeries,
    swings,
}: Props) {
    const [structure, setStructure] = useState<MarketStructure | null>(null);

    useEffect(() => {
        async function loadStructure() {
            try {
                const data = await getStructure();
                setStructure(data);
            } catch (error) {
                console.error(error);
            }
        }

        loadStructure();
    }, []);

    useEffect(() => {
        if (!candleSeries) return;

        const lastHigh = [...swings].filter((swing) => swing.kind === "HIGH").at(-1);
        const lastLow = [...swings].filter((swing) => swing.kind === "LOW").at(-1);

        const markers: SeriesMarker<Time>[] = [];

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

        candleSeries.setMarkers(markers);

        const priceLines: PriceLine[] = [];

        if (structure?.bos && structure.last_high !== null) {
            priceLines.push(
                candleSeries.createPriceLine({
                    price: structure.last_high,
                    color: "#22c55e",
                    lineWidth: 2,
                    lineStyle: 0,
                    axisLabelVisible: true,
                    title: "BOS",
                })
            );
        }

        if (structure?.choch && structure.last_low !== null) {
            priceLines.push(
                candleSeries.createPriceLine({
                    price: structure.last_low,
                    color: "#f59e0b",
                    lineWidth: 2,
                    lineStyle: 0,
                    axisLabelVisible: true,
                    title: "CHoCH",
                })
            );
        }

        return () => {
            candleSeries.setMarkers([]);
            priceLines.forEach((line) => line.remove());
        };
    }, [candleSeries, swings, structure]);

    return null;
}