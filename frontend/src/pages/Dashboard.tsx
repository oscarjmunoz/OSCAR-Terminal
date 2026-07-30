// frontend/src/pages/Dashboard.tsx
// REEMPLAZAR COMPLETAMENTE EL ARCHIVO

import { useEffect, useState } from "react";

import {
    getStatus,
    getTick,
    getCandles,
    TerminalStatus,
    TickResponse,
    CandleResponse,
} from "../api/market";

import {
    getStructure,
    MarketStructure,
} from "../api/smartMoney";

import StatusCard from "../components/StatusCard";
import TickCard from "../components/TickCard";
import TradingChart from "../components/TradingChart";

export default function Dashboard() {

    const [status, setStatus] =
        useState<TerminalStatus | null>(null);

    const [tick, setTick] =
        useState<TickResponse | null>(null);

    const [candles, setCandles] =
        useState<CandleResponse[]>([]);

    const [structure, setStructure] =
        useState<MarketStructure | null>(null);

    const [loading, setLoading] =
        useState(true);

    useEffect(() => {

        load();

        const timer = setInterval(
            load,
            1000
        );

        return () => clearInterval(timer);

    }, []);

    async function load() {

        try {

            const [

                statusData,

                tickData,

                candleData,

                structureData,

            ] = await Promise.all([

                getStatus(),

                getTick(),

                getCandles("M5", 300),

                getStructure(),

            ]);

            setStatus(statusData);

            setTick(tickData);

            setCandles(candleData);

            setStructure(structureData);

        }

        catch (error) {

            console.error(error);

        }

        finally {

            setLoading(false);

        }

    }

    if (loading) {

        return (

            <div
                style={{
                    height: "100vh",
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    background: "#0f172a",
                    color: "white",
                    fontSize: 22,
                    fontFamily: "Segoe UI",
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
                color: "#fff",
                padding: 25,
                fontFamily: "Segoe UI",
            }}
        >

            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: 25,
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
                        display: "flex",
                        gap: 15,
                        alignItems: "center",
                    }}
                >

                    <strong>

                        {structure?.trend}

                    </strong>

                    {

                        structure?.bos &&
                        <span>🟢 BOS</span>

                    }

                    {

                        structure?.choch &&
                        <span>🟠 CHoCH</span>

                    }

                    {

                        structure?.mss &&
                        <span>🔵 MSS</span>

                    }

                </div>

            </div>

            <div
                style={{
                    display: "grid",
                    gridTemplateColumns:
                        "1fr 1fr",
                    gap: 20,
                    marginBottom: 20,
                }}
            >

                <StatusCard

                    connected={
                        status?.connected ?? false
                    }

                    account={
                        status?.account
                    }

                    company={
                        status?.company
                    }

                    server={
                        status?.server
                    }

                />

                <TickCard

                    symbol={
                        tick?.symbol
                    }

                    bid={
                        tick?.bid
                    }

                    ask={
                        tick?.ask
                    }

                    spread={
                        tick?.spread
                    }

                />

            </div>

            <TradingChart

                candles={candles}

            />

        </div>

    );

}