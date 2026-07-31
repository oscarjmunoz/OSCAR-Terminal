import { useEffect, useState } from "react";

import DecisionCenterLayout from "../layouts/DecisionCenterLayout";
import {
    CandleResponse,
    TerminalStatus,
    TickResponse,
    getCandles,
    getStatus,
    getTick,
} from "../api/market";
import { MarketStructure, getStructure } from "../api/smartMoney";
import StatusCard from "../components/StatusCard";
import TickCard from "../components/TickCard";
import TradingChart from "../components/TradingChart";

export default function Dashboard() {
    const [status, setStatus] = useState<TerminalStatus | null>(null);
    const [tick, setTick] = useState<TickResponse | null>(null);
    const [candles, setCandles] = useState<CandleResponse[]>([]);
    const [structure, setStructure] = useState<MarketStructure | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const load = async () => {
            try {
                const [statusData, tickData, candleData, structureData] = await Promise.all([
                    getStatus(),
                    getTick(),
                    getCandles("M5", 300),
                    getStructure(),
                ]);

                setStatus(statusData);
                setTick(tickData);
                setCandles(candleData);
                setStructure(structureData);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };

        load();
        const timer = window.setInterval(load, 1000);

        return () => window.clearInterval(timer);
    }, []);

    if (loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-slate-950 text-lg font-semibold text-white">
                Loading OSCAR Terminal...
            </div>
        );
    }

    return (
        <DecisionCenterLayout>
            <div className="flex h-full flex-col gap-4">
                <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/70 px-4 py-3">
                    <div>
                        <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Market Snapshot</p>
                        <p className="text-sm font-semibold text-white">
                            {structure?.trend ?? "UNKNOWN"}
                        </p>
                    </div>
                    <div className="flex gap-2 text-xs font-semibold">
                        {structure?.bos ? <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-emerald-400">BOS</span> : null}
                        {structure?.choch ? <span className="rounded-full bg-amber-500/15 px-3 py-1 text-amber-400">CHoCH</span> : null}
                        {structure?.mss ? <span className="rounded-full bg-sky-500/15 px-3 py-1 text-sky-400">MSS</span> : null}
                    </div>
                </div>

                <div className="grid gap-4 lg:grid-cols-2">
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

                <div className="min-h-[320px] overflow-hidden rounded-xl border border-slate-800 bg-slate-950/60">
                    <TradingChart candles={candles} />
                </div>
            </div>
        </DecisionCenterLayout>
    );
}