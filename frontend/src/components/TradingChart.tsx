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
import { getSwings, Swing } from "../api/smartMoney";
import SwingLayer from "./SwingLayer";

type Props = {
    candles: CandleResponse[];
    symbol: string;
    timeframe: string;
};

export default function TradingChart({
    candles,
    symbol,
    timeframe,
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

                const data = await getSwings(symbol, timeframe);

                setSwings(data);

            }

            catch (error) {

                console.error(error);

            }

        }

        loadSwings();

    }, [candles, symbol, timeframe]);

    return (

        <div className="chart-frame" data-testid="chart-area">

            <div className="chart-frame__header">

                <div>

                    <p className="panel__eyebrow">Chart Area</p>

                    <h2 className="panel__title">{symbol} · {timeframe}</h2>

                </div>

                <div className="chart-frame__live">

                    LIVE

                </div>

            </div>

            <div
                ref={containerRef}
                className="chart-frame__body"
            />

            <SwingLayer

                chart={chartRef.current}

                candleSeries={candleSeriesRef.current}

                swings={swings}

            />

        </div>

    );

}