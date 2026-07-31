import { useEffect, useRef, useState } from "react";

<<<<<<< HEAD
=======
import SmartScanner from "../components/SmartScanner";
>>>>>>> feature/scanner-service
import TradingChart from "../components/TradingChart";
import { LiveDataOrchestrator } from "../core/LiveDataOrchestrator";
import { ExplainableDecisionOutput, MarketSnapshot, OrchestratedEngineOutput } from "../core/types";
import { runBacktest } from "../engine/backtest/BacktestEngine";
import { BacktestResult } from "../engine/backtest/types";
import { getActiveStrategy } from "../engine/strategy/StrategyRegistry";
import { runValidationEngine } from "../engine/validation/ValidationEngine";
import { ValidationRecord } from "../engine/validation/types";
import DecisionCenterLayout from "../layouts/DecisionCenterLayout";

<<<<<<< HEAD
const DEFAULT_SYMBOL = "USDCHF.pro";
=======
const DEFAULT_SYMBOL = "USDCHF";
const SYMBOL_TO_MARKET: Record<string, string> = {
    EURUSD: "EURUSD.pro",
    GBPUSD: "GBPUSD.pro",
    USDCHF: "USDCHF.pro",
    XAUUSD: "XAUUSD",
    NAS100: "NAS100",
};

>>>>>>> feature/scanner-service
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

<<<<<<< HEAD
=======
function resolveMarketSymbol(scannerSymbol: string): string {
    return SYMBOL_TO_MARKET[scannerSymbol] ?? scannerSymbol;
}

>>>>>>> feature/scanner-service
export default function Dashboard() {
    const orchestratorRef = useRef<LiveDataOrchestrator | null>(null);
    const validationHistoryRef = useRef<ValidationRecord[]>([]);

    const [snapshot, setSnapshot] = useState<MarketSnapshot | null>(null);
    const [output, setOutput] = useState<OrchestratedEngineOutput | null>(null);
    const [validationHistory, setValidationHistory] = useState<ValidationRecord[]>([]);
    const [backtestResult, setBacktestResult] = useState<BacktestResult>(EMPTY_BACKTEST);
    const [selectedScannerSymbol, setSelectedScannerSymbol] = useState(DEFAULT_SYMBOL);
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
    const decisionType = normalizeDecision(decision.type);
    const scoreValue = score?.score ?? 0;

    const liquidityBuckets = {
        BSL: m5Analysis.liquidity.filter((item) => item.type === "BSL").length,
        SSL: m5Analysis.liquidity.filter((item) => item.type === "SSL").length,
        EQH: m5Analysis.liquidity.filter((item) => item.type === "EQH").length,
        EQL: m5Analysis.liquidity.filter((item) => item.type === "EQL").length,
    };

    const whyReasons = decision.reason.length
        ? decision.reason
        : buildFallbackReasons({
            trend: context?.trend ?? "RANGE",
            bias: context?.bias ?? "NEUTRAL",
            score: scoreValue,
            liquidityCount: m5Analysis.liquidity.length,
            hasBos: Boolean(m5Analysis.structure?.bos),
            hasChoch: Boolean(m5Analysis.structure?.choch),
        });

    const premiumDiscountValue = m5Analysis.premiumDiscount[0]?.type ?? "EQUILIBRIUM";
    const fvgSummary = m5Analysis.fairValueGaps.map((item) => `${item.type} (${item.status})`).slice(0, 2).join(" | ") || "None";
    const orderBlockSummary = m5Analysis.orderBlocks.map((item) => `${item.type} (${item.status})`).slice(0, 2).join(" | ") || "None";

    const invalidation = (() => {
        if (decisionType === "BUY" && m5Analysis.structure?.last_low !== null && m5Analysis.structure?.last_low !== undefined) {
            return `Invalid if price closes below ${m5Analysis.structure.last_low.toFixed(5)} (last low).`;
        }

        if (decisionType === "SELL" && m5Analysis.structure?.last_high !== null && m5Analysis.structure?.last_high !== undefined) {
            return `Invalid if price closes above ${m5Analysis.structure.last_high.toFixed(5)} (last high).`;
        }

        return "Placeholder: explicit invalidation level not available in current state.";
    })();

    const explainableDecision: ExplainableDecisionOutput = {
        decision: decisionType,
        confidence: decision.confidence,
        score: scoreValue,
        reasons: whyReasons,
        risk: resolveRiskLevel(decisionType, decision.confidence, scoreValue),
        invalidation,
        expectedRR: "2.0R (placeholder: fixed from current backtest model)",
        strategy: `${strategy.name} (${strategy.id.toUpperCase()})`,
    };

    return (
        <DecisionCenterLayout>
            <div className="grid gap-4 xl:grid-cols-12">
                <div className="xl:col-span-8">
                    <DecisionExplanationCard data={explainableDecision} />
                </div>

                <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 xl:col-span-4">
                    <h2 className="mb-4 text-lg font-semibold">Watchlist</h2>
                    <div className="space-y-2">
                        {WATCHLIST_SYMBOLS.map((symbol) => {
                            const isActive = snapshot.symbol.startsWith(symbol);

                            return (
                                <button
                                    key={symbol}
                                    className={`flex w-full items-center justify-between rounded-xl border px-3 py-2 text-left text-sm transition-colors ${
                                        isActive
                                            ? "border-sky-500/40 bg-sky-500/10 text-sky-200"
                                            : "border-slate-800 bg-slate-950/60 text-slate-300 hover:border-slate-700"
                                    }`}
                                    type="button"
                                >
                                    <span className="font-semibold">{symbol}</span>
                                    <span className="text-xs text-slate-400">M5</span>
                                </button>
                            );
                        })}
                    </div>

                    <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm">
                        <div className="flex items-center justify-between">
                            <span className="text-slate-400">MT5</span>
                            <span className={snapshot.status?.connected ? "font-semibold text-emerald-400" : "font-semibold text-rose-400"}>
                                {snapshot.status?.connected ? "Connected" : "Offline"}
                            </span>
                        </div>
                        <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
                            <span>Updated</span>
                            <span>{formatTimestamp(snapshot.timestamp)}</span>
                        </div>
                    </div>
                </section>

                <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 xl:col-span-7">
                    <h2 className="mb-4 text-lg font-semibold">Market Analysis</h2>
                    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">Trend</p>
                            <p className="mt-1 text-sm font-semibold">{context?.trend ?? "RANGE"}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">Liquidity</p>
                            <p className="mt-1 text-sm font-semibold">BSL {liquidityBuckets.BSL} | SSL {liquidityBuckets.SSL}</p>
                            <p className="text-xs text-slate-500">EQH {liquidityBuckets.EQH} | EQL {liquidityBuckets.EQL}</p>
                        </div>
                        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
                            <p className="text-xs text-slate-400">BOS</p>
                            <p className="mt-1 text-sm font-semibold">{m5Analysis.structure?.bos ? "YES" : "NO"}</p>
                        </div>
                    </div>
                </section>

                <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 xl:col-span-4">
<h2 className="mb-4 text-lg font-semibold">Estado del Sistema</h2>

<SmartScanner
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

    <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-3">
        <p className="text-xs text-slate-400">FVG</p>
        <p className="mt-1 text-sm font-semibold">{fvgSummary}</p>
    </div>

    <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2">
        <span className="text-slate-400">Símbolo</span>
        <span className="font-semibold">{snapshot.symbol}</span>
    </div>

    <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2">
        <span className="text-slate-400">Timeframe</span>
        <span className="font-semibold">M5</span>
    </div>
</div>