// frontend/src/components/ChartCard.tsx

import { useEffect, useRef } from "react";
import {
    createChart,
    ColorType,
    CandlestickSeries,
    CrosshairMode,
    Time,
} from "lightweight-charts";

export type Candle = {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
};

type Props = {
    candles: Candle[];
};

export default function ChartCard({
    candles,
}: Props) {

    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {

        if (!containerRef.current) return;

        const chart = createChart(
            containerRef.current,
            {
                width: containerRef.current.clientWidth,
                height: 650,

                layout: {
                    background: {
                        type: ColorType.Solid,
                        color: "#1e293b",
                    },
                    textColor: "#cbd5e1",
                    attributionLogo: false,
                },

                crosshair: {
                    mode: CrosshairMode.Normal,
                },

                grid: {
                    vertLines: {
                        color: "#334155",
                    },
                    horzLines: {
                        color: "#334155",
                    },
                },

                rightPriceScale: {
                    borderColor: "#475569",
                },

                timeScale: {

                    borderColor: "#475569",

                    timeVisible: true,

                    secondsVisible: false,

                    tickMarkFormatter: (
                        time: Time
                    ) => {

                        const date = new Date(
                            Number(time) * 1000
                        );

                        return date.toLocaleTimeString(
                            [],
                            {
                                hour: "2-digit",
                                minute: "2-digit",
                            }
                        );

                    },

                },

            }
        );

        const series = chart.addSeries(
            CandlestickSeries,
            {

                upColor: "#00C853",

                downColor: "#FF5252",

                borderUpColor: "#00C853",

                borderDownColor: "#FF5252",

                wickUpColor: "#00C853",

                wickDownColor: "#FF5252",

            }
        );

        series.setData(

            candles.map(c => ({

                time: Math.floor(
                    new Date(c.time).getTime() / 1000
                ) as Time,

                open: c.open,

                high: c.high,

                low: c.low,

                close: c.close,

            }))

        );

        chart.timeScale().fitContent();

        chart.timeScale().scrollToRealTime();

        const resize = () => {

            if (!containerRef.current) return;

            chart.applyOptions({

                width: containerRef.current.clientWidth,

            });

        };

        window.addEventListener(
            "resize",
            resize
        );

        return () => {

            window.removeEventListener(
                "resize",
                resize
            );

            chart.remove();

        };

    }, [candles]);

    return (

        <div
            style={{
                background: "#1e293b",
                borderRadius: 12,
                padding: 15,
                boxShadow:
                    "0 0 20px rgba(0,0,0,.35)",
            }}
        >

            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: 15,
                    alignItems: "center",
                }}
            >

                <h2
                    style={{
                        margin: 0,
                    }}
                >
                    USDCHF.pro · M5
                </h2>

                <div
                    style={{
                        color: "#22c55e",
                        fontWeight: "bold",
                    }}
                >
                    LIVE
                </div>

            </div>

            <div
                ref={containerRef}
            />

        </div>

    );

}