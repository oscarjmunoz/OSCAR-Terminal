import { useEffect, useRef, useState } from "react";

import SmartScanner, { SmartScannerDecision, SmartScannerRow } from "../components/SmartScanner";
import TradingChart from "../components/TradingChart";
import { LiveDataOrchestrator } from "../core/LiveDataOrchestrator";
import { MarketSnapshot, OrchestratedEngineOutput } from "../core/types";
import { runBacktest } from "../engine/backtest/BacktestEngine";
import { BacktestResult } from "../engine/backtest/types";
import { getActiveStrategy } from "../engine/strategy/StrategyRegistry";
import { runValidationEngine } from "../engine/validation/ValidationEngine";
import { ValidationRecord } from "../engine/validation/types";
import DecisionCenterLayout from "../layouts/DecisionCenterLayout";

const DEFAULT_SYMBOL = "USDCHF";
const SYMBOL_TO_MARKET: Record<string, string> = {
    EURUSD: "EURUSD.pro",
    GBPUSD: "GBPUSD.pro",
    USDCHF: "USDCHF.pro",
    XAUUSD: "XAUUSD",
    NAS100: "NAS100",
};

const MOCK_SCANNER_ROWS: SmartScannerRow[] = [
    { symbol: "EURUSD", decision: "WAIT", score: 52, confidence: 58, trend: "RANGE", source: "MOCK" },
    { symbol: "GBPUSD", decision: "SELL", score: 68, confidence: 64, trend: "BEARISH", source: "MOCK" },
    { symbol: "USDCHF", decision: "BUY", score: 74, confidence: 71, trend: "BULLISH", source: "MOCK" },
    { symbol: "XAUUSD", decision: "WAIT", score: 49, confidence: 55, trend: "RANGE", source: "MOCK" },
    { symbol: "NAS100", decision: "BUY", score: 62, confidence: 60, trend: "BULLISH", source: "MOCK" },
];

const EMPTY_BACKTEST: BacktestResult = {
    totalSignals: 0,
    wins: 0,
    losses: 0,
    winRate: 0,
    profitFactor: 0,
    expectancy: 0,
    averageRR: 0,
    equityCurve: [],
};

function mergeValidationHistory(current: ValidationRecord[], next: ValidationRecord): ValidationRecord[] {
    const key = `${next.timeframe}-${next.timestamp}-${next.decision}`;
    const exists = current.some((item) => `${item.timeframe}-${item.timestamp}-${item.decision}` === key);

    if (exists) {
        return current;
    }

    const merged = [...current, next];
    return merged.slice(-250);
}

function formatTimestamp(value: number): string {
    return new Date(value).toLocaleTimeString();
}

function resolveMarketSymbol(scannerSymbol: string): string {
    return SYMBOL_TO_MARKET[scannerSymbol] ?? scannerSymbol;
}

function normalizeScannerDecision(decision: string | undefined): SmartScannerDecision {
    if (decision === "BUY" || decision === "SELL") {
        return decision;
    }

    return "WAIT";
}

export default function Dashboard() {
    const orchestratorRef = useRef<LiveDataOrchestrator | null>(null);
    const validationHistoryRef = useRef<ValidationRecord[]>([]);

    const [snapshot, setSnapshot] = useState<MarketSnapshot | null>(null);
    const [output, setOutput] = useState<OrchestratedEngineOutput | null>(null);
    const [validationHistory, setValidationHistory] = useState<ValidationRecord[]>([]);
    const [backtestResult, setBacktestResult] = useState<BacktestResult>(EMPTY_BACKTEST);
    const [selectedScannerSymbol, setSelectedScannerSymbol] = useState(DEFAULT_SYMBOL);
    const [scannerRows, setScannerRows] = useState<SmartScannerRow[]>(MOCK_SCANNER_ROWS);
    const [loading, setLoading] = useState(true);

    if (!orchestratorRef.current) {
        orchestratorRef.current = new LiveDataOrchestrator();
    }

    const strategy = getActiveStrategy();

    const m5Analysis = output?.institutional.M5 ?? null;

    useEffect(() => {
        const load = async () => {
            try {
                const orchestrator = orchestratorRef.current;
                if (!orchestrator) return;

                const marketSymbol = resolveMarketSymbol(selectedScannerSymbol);
                const newSnapshot = await orchestrator.refreshSnapshot(marketSymbol);
                const engineOutput = orchestrator.runEngines(newSnapshot);
                setSnapshot(newSnapshot);
                setOutput(engineOutput);

                setScannerRows((current) =>
                    current.map((row) => {
                        if (row.symbol !== selectedScannerSymbol) {
                            return row;
                        }

                        const liveDecision = engineOutput.institutional.M5.decision;
                        const liveContext = engineOutput.institutional.M5.context;
                        const liveScore = engineOutput.institutional.M5.score;

                        return {
                            ...row,
                            decision: normalizeScannerDecision(liveDecision?.type),
                            confidence: liveDecision?.confidence ?? row.confidence,
                            score: liveScore?.score ?? row.score,
                            trend: liveContext?.trend ?? row.trend,
                            source: "PIPELINE",
                        };
                    })
                );

                const latestValidation = runValidationEngine({
                    analysis: engineOutput.institutional.M5,
                    candles: newSnapshot.timeframes.M5.candles,
                    symbol: newSnapshot.symbol,
                    timeframe: "M5",
                }).records[0];

                const nextHistory = mergeValidationHistory(validationHistoryRef.current, latestValidation);
                validationHistoryRef.current = nextHistory;
                setValidationHistory(nextHistory);

                const summary = runBacktest({
                    records: nextHistory,
                    candles: newSnapshot.timeframes.M5.candles,
                });
                setBacktestResult(summary);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };

        setLoading(true);
        load();
        const timer = window.setInterval(load, 3000);

        return () => window.clearInterval(timer);
    }, [selectedScannerSymbol]);

    if (loading || !snapshot || !output || !m5Analysis) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-slate-950 text-lg font-semibold text-white">
                Loading OSCAR Terminal...
            </div>
        );
    }

    const latestSignal = validationHistory[validationHistory.length - 1] ?? null;
    const context = m5Analysis.context;
    const score = m5Analysis.score;
    const decision = m5Analysis.decision ?? { type: "NO TRADE", confidence: 0, reason: [] };

    const liquidityBuckets = {
        BSL: m5Analysis.liquidity.filter((item) => item.type === "BSL").length,
        SSL: m5Analysis.liquidity.filter((item) => item.type === "SSL").length,
        EQH: m5Analysis.liquidity.filter((item) => item.type === "EQH").length,
        EQL: m5Analysis.liquidity.filter((item) => item.type === "EQL").length,
    };

    return (
        <DecisionCenterLayout>
            <div className="grid gap-4 xl:grid-cols-12">
                <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 xl:col-span-8">
                    <div className="mb-4 flex items-center justify-between">
                        <h2 className="text-lg font-semibold">Trading Workspace</h2>
                        <span className="rounded-full bg-sky-500/15 px-3 py-1 text-xs font-semibold text-sky-300">
                            {snapshot.symbol}
                        </span>
                    </div>
                    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">Market Snapshot</p>
                            <p className="mt-1 text-sm font-semibold">Bid {snapshot.tick?.bid?.toFixed(5) ?? "-"}</p>
                            <p className="text-sm font-semibold">Ask {snapshot.tick?.ask?.toFixed(5) ?? "-"}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">MTF Alignment</p>
                            <p className="mt-1 text-2xl font-bold">{output.mtf.alignment}%</p>
                            <p className="text-xs text-slate-400">Bias: {output.mtf.globalBias}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">OSCAR Score</p>
                            <p className="mt-1 text-2xl font-bold">{score?.score ?? 0}</p>
                            <p className="text-xs text-slate-400">Decision: {score?.decision ?? "NO TRADE"}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">Strategy Activa</p>
                            <p className="mt-1 text-sm font-semibold">{strategy.name}</p>
                            <p className="text-xs text-slate-400">{strategy.id.toUpperCase()}</p>
                        </div>
                    </div>
                    <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">Decision</p>
                            <p className="mt-1 text-lg font-semibold">{decision.type}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">Confidence</p>
                            <p className="mt-1 text-lg font-semibold">{decision.confidence}%</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">Liquidity</p>
                            <p className="mt-1 text-sm font-semibold">BSL {liquidityBuckets.BSL} | SSL {liquidityBuckets.SSL}</p>
                            <p className="text-xs text-slate-400">EQH {liquidityBuckets.EQH} | EQL {liquidityBuckets.EQL}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">Context</p>
                            <p className="mt-1 text-sm font-semibold">{context?.trend ?? "RANGE"} / {context?.bias ?? "NEUTRAL"}</p>
                            <p className="text-xs text-slate-400">{context?.phase ?? "ACCUMULATION"}</p>
                        </div>
                    </div>
                </section>

                <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 xl:col-span-4">
                    <SmartScanner
                        rows={scannerRows}
                        selectedSymbol={selectedScannerSymbol}
                        onSelect={setSelectedScannerSymbol}
                    />
                    <div className="mt-4 space-y-2 text-sm">
                        <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2">
                            <span className="text-slate-400">MT5</span>
                            <span className={snapshot.status?.connected ? "font-semibold text-emerald-400" : "font-semibold text-rose-400"}>
                                {snapshot.status?.connected ? "Conectado" : "Offline"}
                            </span>
                        </div>
                        <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2">
                            <span className="text-slate-400">Ultima actualizacion</span>
                            <span className="font-semibold">{formatTimestamp(snapshot.timestamp)}</span>
                        </div>
                        <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2">
                            <span className="text-slate-400">Simbolo Activo</span>
                            <span className="font-semibold">{selectedScannerSymbol}</span>
                        </div>
                    </div>
                </section>

                <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 xl:col-span-7">
                    <h2 className="mb-4 text-lg font-semibold">Panel de Analisis</h2>
                    <div className="grid gap-3 sm:grid-cols-2">
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-sm">
                            <p className="text-xs text-slate-400">Trend / Bias / Phase</p>
                            <p className="mt-1 font-semibold">{context?.trend ?? "RANGE"}</p>
                            <p className="font-semibold">{context?.bias ?? "NEUTRAL"}</p>
                            <p className="font-semibold">{context?.phase ?? "ACCUMULATION"}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-sm">
                            <p className="text-xs text-slate-400">Premium / Discount</p>
                            <p className="mt-1 font-semibold">{m5Analysis.premiumDiscount[0]?.type ?? "EQUILIBRIUM"}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-sm">
                            <p className="text-xs text-slate-400">Order Blocks</p>
                            <p className="mt-1 font-semibold">{m5Analysis.orderBlocks.map((item) => item.type).join(" | ") || "None"}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-sm">
                            <p className="text-xs text-slate-400">FVG</p>
                            <p className="mt-1 font-semibold">{m5Analysis.fairValueGaps.map((item) => item.type).join(" | ") || "None"}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3 text-sm sm:col-span-2">
                            <p className="text-xs text-slate-400">Liquidity</p>
                            <p className="mt-1 font-semibold">{m5Analysis.liquidity.map((item) => `${item.type}@${item.price.toFixed(5)}`).slice(0, 4).join(" | ") || "None"}</p>
                        </div>
                    </div>
                </section>

                <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 xl:col-span-5">
                    <h2 className="mb-4 text-lg font-semibold">Panel de Validacion</h2>
                    <div className="space-y-2 text-sm">
                        <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2">
                            <span className="text-slate-400">Ultima senal</span>
                            <span className="font-semibold">{latestSignal?.decision ?? "NO TRADE"}</span>
                        </div>
                        <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2">
                            <span className="text-slate-400">Resultado esperado</span>
                            <span className="font-semibold">TP 2R / SL 1R</span>
                        </div>
                        <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2">
                            <span className="text-slate-400">Confidence</span>
                            <span className="font-semibold">{latestSignal?.confidence ?? decision.confidence}%</span>
                        </div>
                        <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2">
                            <span className="text-slate-400">Score</span>
                            <span className="font-semibold">{latestSignal?.score ?? score?.score ?? 0}</span>
                        </div>
                    </div>
                </section>

                <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 xl:col-span-5">
                    <h2 className="mb-4 text-lg font-semibold">Panel de Backtest</h2>
                    <div className="grid gap-3 sm:grid-cols-2 text-sm">
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">Win Rate</p>
                            <p className="mt-1 text-xl font-semibold">{backtestResult.winRate}%</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">Profit Factor</p>
                            <p className="mt-1 text-xl font-semibold">{backtestResult.profitFactor}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">Expectancy</p>
                            <p className="mt-1 text-xl font-semibold">{backtestResult.expectancy}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">Total Signals</p>
                            <p className="mt-1 text-xl font-semibold">{backtestResult.totalSignals}</p>
                        </div>
                    </div>
                </section>

                <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-2 xl:col-span-7">
                    <TradingChart candles={snapshot.timeframes.M5.candles} />
                </section>
            </div>
        </DecisionCenterLayout>
    );
}