// frontend/src/pages/Dashboard.tsx

import { useEffect, useState } from "react";

import {
    getStatus,
    getTick,
    getCandles,
    TerminalStatus,
    TickResponse,
    CandleResponse,
} from "../api/market";

import StatusCard from "../components/StatusCard";
import TickCard from "../components/TickCard";
import ChartCard from "../components/ChartCard";

export default function Dashboard() {

    const [status, setStatus] = useState<TerminalStatus | null>(null);
    const [tick, setTick] = useState<TickResponse | null>(null);
    const [candles, setCandles] = useState<CandleResponse[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {

        load();

        const timer = setInterval(load, 1000);

        return () => clearInterval(timer);

    }, []);

    async function load() {

        try {

            const [statusData, tickData, candleData] = await Promise.all([

                getStatus(),

                getTick(),

                getCandles("M5", 300),

            ]);

            setStatus(statusData);

            setTick(tickData);

            setCandles(candleData);

        } catch (error) {

            console.error(error);

        } finally {

            setLoading(false);

        }

    }

    if (loading) {

        return (

            <div
                style={{
                    background: "#0f172a",
                    color: "white",
                    minHeight: "100vh",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    fontFamily: "Segoe UI",
                    fontSize: 22,
                }}
            >

                Loading OSCAR Terminal...

            </div>

        );

    }

    return (

        <div
            style={{
                background: "#0f172a",
                minHeight: "100vh",
                color: "#ffffff",
                padding: 30,
                fontFamily: "Segoe UI",
            }}
        >

            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: 30,
                }}
            >

                <h1
                    style={{
                        margin: 0,
                    }}
                >
                    OSCAR TERMINAL
                </h1>

                <div
                    style={{
                        color: "#22c55e",
                        fontWeight: "bold",
                    }}
                >
                    ● LIVE
                </div>

            </div>

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 20,
                    marginBottom: 20,
                }}
            >

                <StatusCard

                    connected={status?.connected ?? false}

                    account={status?.account}

                    company={status?.company}

                    server={status?.server}

                />

                <TickCard

                    symbol={tick?.symbol}

                    bid={tick?.bid}

                    ask={tick?.ask}

                    spread={tick?.spread}

                />

            </div>

            <ChartCard

                candles={candles}

            />

        </div>

    );

}