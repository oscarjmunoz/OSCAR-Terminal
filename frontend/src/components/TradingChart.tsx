// frontend/src/components/TradingChart.tsx
// REEMPLAZAR COMPLETAMENTE EL ARCHIVO

import { useEffect, useRef, useState } from "react";
import {
    CandlestickSeries,
    ColorType,
    createChart,
    CrosshairMode,
    IChartApi,
    ISeriesApi,
    Time,
} from "lightweight-charts";

import { CandleResponse } from "../api/market";
import { Swing, getSwings } from "../api/smartMoney";
import LiquidityOverlay from "./LiquidityOverlay";
import SmartMoneyOverlay from "./SmartMoneyOverlay";

type Props = {
    candles: CandleResponse[];
};

export default function TradingChart({
    candles,
}: Props) {

    const containerRef = useRef<HTMLDivElement>(null);

    const chartRef = useRef<IChartApi | null>(null);

    const candleSeriesRef =
        useRef<ISeriesApi<"Candlestick"> | null>(null);

    const [swings, setSwings] = useState<Swing[]>([]);

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
                },

            }
        );

        const series = chart.addSeries(
            CandlestickSeries,
            {
                upColor: "#16a34a",
                downColor: "#dc2626",

                borderUpColor: "#16a34a",
                borderDownColor: "#dc2626",

                wickUpColor: "#16a34a",
                wickDownColor: "#dc2626",
            }
        );

        chartRef.current = chart;

        candleSeriesRef.current = series;

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

    }, []);

    useEffect(() => {

        if (!candleSeriesRef.current) return;

        candleSeriesRef.current.setData(

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

        chartRef.current
            ?.timeScale()
            .fitContent();

    }, [candles]);

    useEffect(() => {
        async function loadSwings() {
            try {
                const data = await getSwings();
                setSwings(data);
            } catch (error) {
                console.error(error);
            }
        }

        loadSwings();
    }, []);

    return (

        <>

            <div
                ref={containerRef}
            />

            <SmartMoneyOverlay
                candleSeries={candleSeriesRef.current}
            />

            <LiquidityOverlay
                candleSeries={candleSeriesRef.current}
                candles={candles}
                swings={swings}
                currentPrice={candles[candles.length - 1]?.close}
            />

        </>

    );

}