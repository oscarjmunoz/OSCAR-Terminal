// frontend/src/components/SwingLayer.tsx
// REEMPLAZAR COMPLETAMENTE EL ARCHIVO

import { useEffect } from "react";
import {
    ISeriesApi,
    SeriesMarker,
    Time,
} from "lightweight-charts";

import { Swing } from "../api/smartMoney";

type Props = {
    candleSeries: ISeriesApi<"Candlestick"> | null;
    swings: Swing[];
};

export default function SwingLayer({
    candleSeries,
    swings,
}: Props) {

    useEffect(() => {

        if (!candleSeries) return;

        const markers: SeriesMarker<Time>[] = swings.map((swing) => ({

            time: Math.floor(
                new Date(swing.time).getTime() / 1000
            ) as Time,

            position:
                swing.kind === "HIGH"
                    ? "aboveBar"
                    : "belowBar",

            shape:
                swing.kind === "HIGH"
                    ? "arrowDown"
                    : "arrowUp",

            color:
                swing.structure === "HH" ||
                swing.structure === "HL"
                    ? "#22c55e"
                    : "#ef4444",

            text: swing.structure,

        }));

        candleSeries.setMarkers(markers);

        return () => {

            candleSeries.setMarkers([]);

        };

    }, [candleSeries, swings]);

    return null;

}