import axios from "axios";
import { useEffect, useRef, useState } from "react";

import { getAnalyticsPerformance, PerformanceReport } from "../api/analytics";
import { getLiveDecisionReport, LiveDecisionReport } from "../api/decision";
import { DecisionExecutionBridgeResult, executeDecisionBridge } from "../api/decisionExecution";
import { getOperationalReadiness, OperationalReadinessResponse } from "../api/health";
import { getJournalEntries, JournalEntry } from "../api/journal";
import { getStatus, getTick, TerminalStatus, TickResponse } from "../api/market";
import { getOpportunityQueue, OpportunityQueueResponse, OpportunityResult } from "../api/opportunity";
import { evaluatePlaybookMatches, getPlaybookSetups, PlaybookMatch, PlaybookSetup } from "../api/playbook";
import { getOperationalSettings, OperationalSettings } from "../api/system";

import EmptyState from "../components/dashboard/EmptyState";
import MetricCard from "../components/dashboard/MetricCard";
import Panel from "../components/dashboard/Panel";
import SelectorField from "../components/dashboard/SelectorField";
import OpportunityQueuePanel from "../components/opportunity/OpportunityQueuePanel";
import TradeTicket from "../components/execution/TradeTicket";

type DashboardState = {
    marketStatus: TerminalStatus | null;
    tick: TickResponse | null;
    readiness: OperationalReadinessResponse | null;
    journalEntries: JournalEntry[];
    playbookSetups: PlaybookSetup[];
    performance: PerformanceReport | null;
    opportunityQueue: OpportunityResult[];
    opportunityQueueMarketSummary: OpportunityQueueResponse["market_summary"] | null;
};

const fallbackSettings: OperationalSettings = {
    defaultSymbol: "EURUSD",
    defaultTimeframe: "M5",
    availableSymbols: ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "NAS100", "US30", "USDCHF"],
    availableTimeframes: ["M1", "M5", "M15", "M30", "H1", "H4", "D1"],
};

const initialState: DashboardState = {
    marketStatus: null,
    tick: null,
    readiness: null,
    journalEntries: [],
    playbookSetups: [],
    performance: null,
    opportunityQueue: [],
    opportunityQueueMarketSummary: null,
};

const FAVORITES_STORAGE_KEY = "oscar.favoriteSymbols.v1";

function settledValue<T>(result: PromiseSettledResult<T>): T | null {
    return result.status === "fulfilled" ? result.value : null;
}

function percentOrDash(value: number | null | undefined): string {
    return value === null || value === undefined ? "-" : `${value.toFixed(2)}%`;
}

function numberOrDash(value: number | null | undefined, digits: number = 2): string {
    return value === null || value === undefined ? "-" : value.toFixed(digits);
}

function toneFromStatus(value: string | boolean | null | undefined): "positive" | "warning" | "danger" | "neutral" {
    if (typeof value === "boolean") {
        return value ? "positive" : "danger";
    }

    if (value === null || value === undefined) {
        return "neutral";
    }

    const normalized = value.toString().trim().toUpperCase();

    if (["OK", "ONLINE", "CONNECTED", "HEALTHY", "GREEN", "BUY", "SELL", "BULLISH", "LOW", "A+", "A", "WIN"].includes(normalized)) {
        return "positive";
    }

    if (["WARNING", "YELLOW", "WAIT", "NO TRADE", "MEDIUM", "B", "IDLE", "BREAK_EVEN"].includes(normalized)) {
        return "warning";
    }

    if (["NEUTRAL", "N/A", "RANGE", "C"].includes(normalized)) {
        return "neutral";
    }

    return "danger";
}

function statusLabel(value: boolean | null | undefined): string {
    if (value === null || value === undefined) {
        return "N/A";
    }

    return value ? "ONLINE" : "OFFLINE";
}

function explainAnalysisError(error: unknown): string {
    if (axios.isAxiosError(error)) {
        if (error.code === "ECONNABORTED") {
            return "El mercado no devolvio datos a tiempo. Intenta de nuevo en unos segundos.";
        }

        const detail = error.response?.data?.detail;

        if (typeof detail === "string") {
            return detail;
        }

        if (detail && typeof detail === "object") {
            const code = typeof detail.code === "string" ? detail.code : "";
            const message = typeof detail.message === "string" ? detail.message : "No fue posible actualizar el panorama actual.";

            if (code === "mt5_disconnected") {
                return "MT5 esta desconectado. Reconecta el terminal para continuar.";
            }

            if (code === "no_data") {
                return "No hay velas recientes para ese simbolo y timeframe en este momento.";
            }

            return message;
        }

        if (!error.response) {
            return "El workspace no pudo hablar con OSCAR. Verifica que el backend este activo.";
        }
    }

    return "No fue posible actualizar el contexto en vivo.";
}

function explainBridgeError(error: unknown): string {
    if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail;

        if (typeof detail === "string") {
            return detail;
        }

        if (detail && typeof detail === "object" && typeof detail.message === "string") {
            return detail.message;
        }

        if (error.code === "ECONNABORTED") {
            return "Decision execution bridge timed out. Try again in a few seconds.";
        }
    }

    return "Decision execution bridge is unavailable right now.";
}

function explainOpportunityQueueError(error: unknown): string {
    if (axios.isAxiosError(error)) {
        const detail = error.response?.data?.detail;

        if (typeof detail === "string") {
            return detail;
        }

        if (detail && typeof detail === "object" && typeof detail.message === "string") {
            return detail.message;
        }

        if (!error.response) {
            return "Opportunity queue could not be loaded from OSCAR.";
        }
    }

    return "Opportunity queue is unavailable right now.";
}

function getInitialFavorites(symbols: string[]): string[] {
    if (typeof window === "undefined") {
        return symbols.slice(0, 3);
    }

    const fallback = symbols.slice(0, 3);
    const raw = window.localStorage.getItem(FAVORITES_STORAGE_KEY);

    if (!raw) {
        return fallback;
    }

    try {
        const parsed = JSON.parse(raw);

        if (!Array.isArray(parsed)) {
            return fallback;
        }

        const filtered = parsed
            .map((item) => (typeof item === "string" ? item : ""))
            .filter((item) => symbols.includes(item));

        return filtered.length > 0 ? filtered : fallback;
    }
    catch {
        return fallback;
    }
}

function getProfitFactor(report: PerformanceReport | null): string {
    if (!report || report.losses <= 0) {
        return "-";
    }

    const winRate = report.winRate / 100;
    const lossRate = 1 - winRate;

    if (lossRate <= 0) {
        return "-";
    }

    const estimated = (winRate * report.averageRR) / lossRate;
    return Number.isFinite(estimated) ? estimated.toFixed(2) : "-";
}

function getExpectancy(report: PerformanceReport | null): string {
    if (!report) {
        return "-";
    }

    const winRate = report.winRate / 100;
    const lossRate = 1 - winRate;
    const expectancy = (winRate * report.averageRR) - lossRate;
    return Number.isFinite(expectancy) ? expectancy.toFixed(2) : "-";
}

function DashboardLoadingState() {
    return (
        <div className="dashboard-skeleton" data-testid="dashboard-skeleton">
            <div className="dashboard-skeleton__bar" />
            <div className="dashboard-skeleton__grid">
                <div className="dashboard-skeleton__panel dashboard-skeleton__panel--wide" />
                <div className="dashboard-skeleton__panel" />
                <div className="dashboard-skeleton__panel" />
                <div className="dashboard-skeleton__panel" />
                <div className="dashboard-skeleton__panel" />
            </div>
        </div>
    );
}

export default function Dashboard() {
    const [state, setState] = useState<DashboardState>(initialState);
    const [settings, setSettings] = useState<OperationalSettings>(fallbackSettings);
    const [selectedSymbol, setSelectedSymbol] = useState(fallbackSettings.defaultSymbol);
    const [selectedTimeframe, setSelectedTimeframe] = useState(fallbackSettings.defaultTimeframe);
    const [decisionReport, setDecisionReport] = useState<LiveDecisionReport | null>(null);
    const [playbookMatches, setPlaybookMatches] = useState<PlaybookMatch[]>([]);
    const [decisionExecution, setDecisionExecution] = useState<DecisionExecutionBridgeResult | null>(null);
    const [decisionExecutionError, setDecisionExecutionError] = useState<string | null>(null);
    const [selectedOpportunity, setSelectedOpportunity] = useState<OpportunityResult | null>(null);
    const [opportunityQueueError, setOpportunityQueueError] = useState<string | null>(null);
    const [opportunityQueueLoading, setOpportunityQueueLoading] = useState(true);
    const [opportunityQueueRefreshing, setOpportunityQueueRefreshing] = useState(false);
    const [loading, setLoading] = useState(true);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisProgress, setAnalysisProgress] = useState("Preparando workspace institucional.");
    const [analysisError, setAnalysisError] = useState<string | null>(null);
    const [focusMode, setFocusMode] = useState(false);
    const [favorites, setFavorites] = useState<string[]>(fallbackSettings.availableSymbols.slice(0, 3));
    const [lastAnalyzedAt, setLastAnalyzedAt] = useState<Date | null>(null);

    const initializedRef = useRef(false);
    const analysisRequestRef = useRef(0);
    const suppressAutoAnalysisRef = useRef(false);

    async function refreshOpportunityQueue() {
        setOpportunityQueueRefreshing(true);
        setOpportunityQueueError(null);

        try {
            const response = await getOpportunityQueue();

            setState((previous) => ({
                ...previous,
                opportunityQueue: response.opportunity_queue,
                opportunityQueueMarketSummary: response.market_summary,
            }));
        }
        catch (error) {
            setOpportunityQueueError(explainOpportunityQueueError(error));
        }
        finally {
            setOpportunityQueueLoading(false);
            setOpportunityQueueRefreshing(false);
        }
    }

    useEffect(() => {
        const initializedFavorites = getInitialFavorites(fallbackSettings.availableSymbols);
        setFavorites(initializedFavorites);
    }, []);

    useEffect(() => {
        if (typeof window === "undefined") {
            return;
        }

        window.localStorage.setItem(FAVORITES_STORAGE_KEY, JSON.stringify(favorites));
    }, [favorites]);

    async function runAnalysis(symbol: string, timeframe: string) {
        const requestId = analysisRequestRef.current + 1;
        analysisRequestRef.current = requestId;

        setIsAnalyzing(true);
        setAnalysisError(null);
        setAnalysisProgress(`Analizando ${symbol} ${timeframe}.`);

        try {
            const [
                marketStatusResult,
                tickResult,
                readinessResult,
                decisionResult,
            ] = await Promise.allSettled([
                getStatus(),
                getTick(symbol),
                getOperationalReadiness(symbol, timeframe),
                getLiveDecisionReport(symbol, timeframe),
            ]);

            if (analysisRequestRef.current !== requestId) {
                return;
            }

            const liveDecision = settledValue(decisionResult);

            if (!liveDecision) {
                throw decisionResult.status === "rejected" ? decisionResult.reason : new Error("Live analysis failed.");
            }

            setAnalysisProgress("Contrastando setup actual con Playbook.");
            const [playbookMatchResult, executionBridgeResult] = await Promise.allSettled([
                evaluatePlaybookMatches(liveDecision),
                executeDecisionBridge({
                    decisionReport: liveDecision,
                    dispatch: false,
                    timeframe,
                }),
            ]);

            if (analysisRequestRef.current !== requestId) {
                return;
            }

            const playbookMatchList = settledValue(playbookMatchResult) ?? [];
            const bridgeResult = settledValue(executionBridgeResult);

            setState((previous) => ({
                ...previous,
                marketStatus: settledValue(marketStatusResult) ?? previous.marketStatus,
                tick: settledValue(tickResult) ?? previous.tick,
                readiness: settledValue(readinessResult) ?? previous.readiness,
            }));

            setDecisionReport(liveDecision);
            setPlaybookMatches([...playbookMatchList].sort((left, right) => right.matchPercentage - left.matchPercentage));
            setDecisionExecution(bridgeResult);
            setDecisionExecutionError(
                executionBridgeResult.status === "rejected"
                    ? explainBridgeError(executionBridgeResult.reason)
                    : null
            );
            setLastAnalyzedAt(new Date());
            setAnalysisProgress(
                bridgeResult
                    ? "Workspace listo para decidir con execution bridge validado."
                    : "Workspace listo para decidir. Execution bridge temporalmente no disponible."
            );
        }
        catch (error) {
            if (analysisRequestRef.current !== requestId) {
                return;
            }

            setDecisionReport(null);
            setPlaybookMatches([]);
            setDecisionExecution(null);
            setDecisionExecutionError(null);
            setAnalysisError(explainAnalysisError(error));
            setAnalysisProgress("Sin actualizacion de contexto.");
        }
        finally {
            if (analysisRequestRef.current === requestId) {
                setIsAnalyzing(false);
                setLoading(false);
            }
        }
    }

    function inspectOpportunity(opportunity: OpportunityResult) {
        const key = `${opportunity.symbol}:${opportunity.timeframe}`;
        setSelectedOpportunity(opportunity);
        setSelectedSymbol(opportunity.symbol);
        setSelectedTimeframe(opportunity.timeframe);
        setAnalysisProgress(`Inspecting ${key} from the opportunity queue.`);
        suppressAutoAnalysisRef.current = true;
        void runAnalysis(opportunity.symbol, opportunity.timeframe);
    }

    useEffect(() => {
        let cancelled = false;

        async function bootstrap() {
            try {
                const [
                    settingsResult,
                    marketStatusResult,
                    journalResult,
                    playbookSetupsResult,
                    performanceResult,
                    opportunityQueueResult,
                ] = await Promise.allSettled([
                    getOperationalSettings(),
                    getStatus(),
                    getJournalEntries(),
                    getPlaybookSetups(),
                    getAnalyticsPerformance(),
                    getOpportunityQueue(),
                ]);

                if (cancelled) {
                    return;
                }

                const operationalSettings = settledValue(settingsResult) ?? fallbackSettings;
                const bootstrapSymbol = operationalSettings.defaultSymbol;
                const bootstrapTimeframe = operationalSettings.defaultTimeframe;

                setSettings(operationalSettings);
                setSelectedSymbol(bootstrapSymbol);
                setSelectedTimeframe(bootstrapTimeframe);
                setFavorites((previous) => {
                    const raw = getInitialFavorites(operationalSettings.availableSymbols);
                    return previous.length > 0 ? previous.filter((item) => operationalSettings.availableSymbols.includes(item)) : raw;
                });
                setState({
                    marketStatus: settledValue(marketStatusResult),
                    tick: null,
                    readiness: null,
                    journalEntries: settledValue(journalResult) ?? [],
                    playbookSetups: settledValue(playbookSetupsResult) ?? [],
                    performance: settledValue(performanceResult),
                    opportunityQueue: settledValue(opportunityQueueResult)?.opportunity_queue ?? [],
                    opportunityQueueMarketSummary: settledValue(opportunityQueueResult)?.market_summary ?? null,
                });

                setOpportunityQueueError(opportunityQueueResult.status === "rejected" ? explainOpportunityQueueError(opportunityQueueResult.reason) : null);
                setOpportunityQueueLoading(false);

                await runAnalysis(bootstrapSymbol, bootstrapTimeframe);
                initializedRef.current = true;
            }
            catch (error) {
                if (cancelled) {
                    return;
                }

                console.error(error);
                setLoading(false);
                setAnalysisError("No fue posible abrir el workspace. Intenta nuevamente.");
            }
        }

        void bootstrap();

        return () => {
            cancelled = true;
        };
    }, []);

    useEffect(() => {
        if (!initializedRef.current) {
            return;
        }

        if (suppressAutoAnalysisRef.current) {
            suppressAutoAnalysisRef.current = false;
            return;
        }

        void runAnalysis(selectedSymbol, selectedTimeframe);
    }, [selectedSymbol, selectedTimeframe]);

    function toggleFavorite(symbol: string) {
        setFavorites((previous) => {
            if (previous.includes(symbol)) {
                return previous.filter((item) => item !== symbol);
            }

            return [...previous, symbol];
        });
    }

    if (loading) {
        return (
            <div className="app-shell">
                <DashboardLoadingState />
            </div>
        );
    }

    const currentSession = state.journalEntries[0]?.session ?? "N/A";
    const selectedOpportunityKey = selectedOpportunity ? `${selectedOpportunity.symbol}:${selectedOpportunity.timeframe}` : null;
    const bestLiveMatch = playbookMatches[0] ?? null;
    const topSetupAnalytics = bestLiveMatch
        ? state.performance && state.performance.totalTrades > 0
            ? state.performance
            : null
        : null;
    const recentTrades = state.journalEntries.slice(0, 5);

    const zones = {
        showSnapshot: !focusMode,
        showPlaybook: !focusMode,
        showPerformance: !focusMode,
    };

    return (
        <div className="app-shell">
            <main className="dashboard">
                <div className="workspace-grid">
                    <section className="workspace-zone workspace-zone--opportunity" data-testid="opportunity-panel">
                        <OpportunityQueuePanel
                            opportunities={state.opportunityQueue}
                            marketSummary={state.opportunityQueueMarketSummary}
                            selectedOpportunityKey={selectedOpportunityKey}
                            isLoading={opportunityQueueLoading && loading}
                            isRefreshing={opportunityQueueRefreshing}
                            error={opportunityQueueError}
                            onInspect={inspectOpportunity}
                            onRefresh={() => {
                                void refreshOpportunityQueue();
                            }}
                        />
                    </section>

                    <section className="workspace-zone workspace-zone--bar" data-testid="trading-bar">
                        <div className="trading-bar__brand">
                            <span className="trading-bar__logo">OSCAR</span>
                            <span className="trading-bar__caption">Trade IA Workspace</span>
                        </div>

                        <div className="trading-bar__controls" data-testid="analysis-controls">
                            <SelectorField
                                label="Symbol"
                                value={selectedSymbol}
                                options={settings.availableSymbols.map((symbol) => ({ value: symbol }))}
                                onChange={setSelectedSymbol}
                                disabled={isAnalyzing}
                                testId="symbol-selector"
                            />

                            <SelectorField
                                label="Timeframe"
                                value={selectedTimeframe}
                                options={settings.availableTimeframes.map((timeframe) => ({ value: timeframe }))}
                                onChange={setSelectedTimeframe}
                                disabled={isAnalyzing}
                                testId="timeframe-selector"
                            />

                            <button
                                type="button"
                                className="action-button"
                                onClick={() => void runAnalysis(selectedSymbol, selectedTimeframe)}
                                disabled={isAnalyzing}
                            >
                                {isAnalyzing ? "Analyzing..." : "Analyze Market"}
                            </button>

                            <button
                                type="button"
                                className={`focus-toggle ${focusMode ? "focus-toggle--active" : ""}`}
                                onClick={() => setFocusMode((previous) => !previous)}
                                aria-pressed={focusMode}
                            >
                                {focusMode ? "Focus Mode On" : "Focus Mode"}
                            </button>

                            <div className="mt5-status" data-testid="mt5-status">
                                <span className={`status-chip status-chip--${toneFromStatus(state.marketStatus?.connected ?? false)}`}>
                                    MT5 {statusLabel(state.marketStatus?.connected)}
                                </span>
                            </div>
                        </div>

                        <div className="trading-bar__favorites" data-testid="favorites-panel">
                            <p className="trading-bar__favorites-label">Favorites</p>
                            <div className="trading-bar__favorites-list">
                                {settings.availableSymbols.map((symbol) => {
                                    const active = favorites.includes(symbol);
                                    const selected = selectedSymbol === symbol;

                                    return (
                                        <button
                                            key={symbol}
                                            type="button"
                                            className={`favorite-chip ${active ? "favorite-chip--active" : ""} ${selected ? "favorite-chip--selected" : ""}`}
                                            onClick={() => setSelectedSymbol(symbol)}
                                        >
                                            <span>{symbol}</span>
                                            <span
                                                role="button"
                                                tabIndex={0}
                                                className="favorite-chip__star"
                                                onClick={(event) => {
                                                    event.stopPropagation();
                                                    toggleFavorite(symbol);
                                                }}
                                                onKeyDown={(event) => {
                                                    if (event.key === "Enter" || event.key === " ") {
                                                        event.preventDefault();
                                                        toggleFavorite(symbol);
                                                    }
                                                }}
                                                aria-label={`Toggle ${symbol} favorite`}
                                            >
                                                {active ? "★" : "☆"}
                                            </span>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    </section>

                    {analysisError ? (
                        <section className="workspace-zone workspace-zone--message" role="alert">
                            <strong>No pudimos leer el mercado ahora mismo.</strong>
                            <span>{analysisError}</span>
                        </section>
                    ) : (
                        <section className="workspace-zone workspace-zone--message workspace-zone--message-neutral">
                            <strong>Estado de analisis</strong>
                            <span>{analysisProgress}</span>
                        </section>
                    )}

                    {zones.showSnapshot ? (
                        <section className="workspace-zone workspace-zone--snapshot" data-testid="market-snapshot">
                            <Panel
                                eyebrow="Zona 2"
                                title="Market Snapshot"
                                subtitle="Panorama institucional instantaneo para validar contexto antes de ejecutar."
                            >
                                {decisionReport ? (
                                    <>
                                        <div className="metric-grid metric-grid--three">
                                            <MetricCard
                                                label="Bias"
                                                value={decisionReport.market_bias.bias}
                                                detail={decisionReport.market_bias.explanation}
                                                tone={toneFromStatus(decisionReport.market_bias.bias)}
                                            />
                                            <MetricCard
                                                label="Structure"
                                                value={decisionReport.market_structure.trend}
                                                detail={`BOS ${decisionReport.market_structure.bos ? "YES" : "NO"} · CHOCH ${decisionReport.market_structure.choch ? "YES" : "NO"} · MSS ${decisionReport.market_structure.mss ? "YES" : "NO"}`}
                                                tone={toneFromStatus(decisionReport.market_structure.trend)}
                                            />
                                            <MetricCard
                                                label="Liquidity"
                                                value={`Taken ${decisionReport.liquidity.liquidity_taken}`}
                                                detail={`Pending ${decisionReport.liquidity.pending_liquidity} · Buy ${decisionReport.liquidity.buy_liquidity} · Sell ${decisionReport.liquidity.sell_liquidity}`}
                                                tone={decisionReport.liquidity.liquidity_taken > 0 ? "positive" : "warning"}
                                            />
                                            <MetricCard label="Session" value={currentSession} detail="Sesion operativa mas reciente." tone="neutral" />
                                            <MetricCard
                                                label="Premium / Discount"
                                                value={decisionReport.institutional_zones.premium.active ? "PREMIUM" : decisionReport.institutional_zones.discount.active ? "DISCOUNT" : "NEUTRAL"}
                                                detail={decisionReport.institutional_zones.premium.active ? decisionReport.institutional_zones.premium.explanation : decisionReport.institutional_zones.discount.explanation}
                                                tone={decisionReport.institutional_zones.premium.active || decisionReport.institutional_zones.discount.active ? "positive" : "neutral"}
                                            />
                                            <MetricCard
                                                label="Institutional Score"
                                                value={String(decisionReport.institutional_score.score)}
                                                detail={`Confidence ${percentOrDash(decisionReport.institutional_score.confidence)}`}
                                                tone={decisionReport.institutional_score.score >= 70 ? "positive" : decisionReport.institutional_score.score >= 50 ? "warning" : "danger"}
                                            />
                                        </div>

                                        {decisionReport.multi_timeframe_bias ? (
                                            <div className="decision-block" data-testid="multitimeframe-panel">
                                                <h3 className="decision-block__title">Multi-Timeframe Bias</h3>
                                                <div className="metric-grid metric-grid--three">
                                                    <MetricCard
                                                        label="H4"
                                                        value={decisionReport.multi_timeframe_bias.h4.bias}
                                                        detail={decisionReport.multi_timeframe_bias.h4.explanation}
                                                        tone="neutral"
                                                    />
                                                    <MetricCard
                                                        label="H1"
                                                        value={decisionReport.multi_timeframe_bias.h1.bias}
                                                        detail={decisionReport.multi_timeframe_bias.h1.explanation}
                                                        tone="neutral"
                                                    />
                                                    <MetricCard
                                                        label="M5"
                                                        value={decisionReport.multi_timeframe_bias.m5.bias}
                                                        detail={decisionReport.multi_timeframe_bias.m5.explanation}
                                                        tone="neutral"
                                                    />
                                                    <MetricCard
                                                        label="Alignment"
                                                        value={decisionReport.multi_timeframe_bias.alignment}
                                                        detail={decisionReport.multi_timeframe_bias.summary}
                                                        tone={decisionReport.multi_timeframe_bias.conflict ? "warning" : "positive"}
                                                    />
                                                    <MetricCard
                                                        label="Conflict"
                                                        value={decisionReport.multi_timeframe_bias.conflict ? "YES" : "NO"}
                                                        detail={`Confidence ${decisionReport.multi_timeframe_bias.confidence}`}
                                                        tone={decisionReport.multi_timeframe_bias.conflict ? "warning" : "neutral"}
                                                    />
                                                </div>
                                            </div>
                                        ) : null}
                                    </>
                                ) : (
                                    <EmptyState
                                        title="Esperando claridad"
                                        description="Cuando el mercado entregue contexto, aqui veras una foto institucional limpia en segundos."
                                    />
                                )}
                            </Panel>
                        </section>
                    ) : null}

                    <section className="workspace-zone workspace-zone--decision" data-testid="decision-center">
                        <Panel
                            eyebrow="Zona 3"
                            title="Decision Center"
                            subtitle="Panel principal de recomendacion, confianza, calidad, narrativa, checklist y riesgo."
                        >
                            {decisionReport ? (
                                <>
                                    <div className="metric-grid metric-grid--three">
                                        <MetricCard
                                            label="Recommendation"
                                            value={decisionReport.final_recommendation.recommendation}
                                            detail={decisionReport.final_recommendation.explanation}
                                            tone={toneFromStatus(decisionReport.final_recommendation.recommendation)}
                                        />
                                        <MetricCard
                                            label="Confidence"
                                            value={percentOrDash(decisionReport.institutional_score.confidence)}
                                            detail="Nivel de conviccion institucional del contexto actual."
                                            tone={decisionReport.institutional_score.confidence >= 70 ? "positive" : decisionReport.institutional_score.confidence >= 50 ? "warning" : "danger"}
                                        />
                                        <MetricCard
                                            label="Quality"
                                            value={decisionReport.institutional_score.quality_level}
                                            detail={`Score ${decisionReport.institutional_score.score}`}
                                            tone={toneFromStatus(decisionReport.institutional_score.quality_level)}
                                        />
                                    </div>

                                    <div className="decision-layout">
                                        <section className="decision-block" data-testid="narrative-panel">
                                            <h3 className="decision-block__title">Narrative</h3>
                                            <p className="decision-block__copy">{decisionReport.narrative}</p>
                                        </section>

                                        <section className="decision-block" data-testid="checklist-panel">
                                            <h3 className="decision-block__title">Checklist</h3>
                                            <div className="decision-list">
                                                {decisionReport.execution_checklist.length > 0 ? decisionReport.execution_checklist.map((item) => (
                                                    <article key={item.label} className="decision-item">
                                                        <div className="decision-item__title">
                                                            <strong>{item.label}</strong>
                                                            <span className={`status-chip ${item.checked ? "status-chip--positive" : "status-chip--danger"}`}>
                                                                {item.checked ? "PASS" : "REVIEW"}
                                                            </span>
                                                        </div>
                                                        <p className="decision-item__text">{item.explanation}</p>
                                                    </article>
                                                )) : (
                                                    <EmptyState
                                                        title="Checklist en preparacion"
                                                        description="Cuando el contexto este completo, aqui veras las validaciones clave de ejecucion."
                                                    />
                                                )}
                                            </div>
                                        </section>

                                        <section className="decision-block" data-testid="risk-panel">
                                            <h3 className="decision-block__title">Risk</h3>
                                            <div className="metric-grid">
                                                <MetricCard
                                                    label="Expected RR"
                                                    value={numberOrDash(decisionReport.risk_assessment.rr_expected)}
                                                    detail="Relacion esperada recompensa/riesgo."
                                                    tone={decisionReport.risk_assessment.rr_expected >= 1.5 ? "positive" : decisionReport.risk_assessment.rr_expected >= 1 ? "warning" : "danger"}
                                                />
                                                <MetricCard
                                                    label="Risk"
                                                    value={decisionReport.risk_assessment.risk}
                                                    detail={`Risk % ${numberOrDash(decisionReport.risk_assessment.risk_percent)}%`}
                                                    tone={toneFromStatus(decisionReport.risk_assessment.risk)}
                                                />
                                                <MetricCard
                                                    label="Volatility"
                                                    value={numberOrDash(decisionReport.risk_assessment.volatility)}
                                                    detail="Presion de rango actual."
                                                    tone={decisionReport.risk_assessment.volatility <= 15 ? "positive" : decisionReport.risk_assessment.volatility <= 25 ? "warning" : "danger"}
                                                />
                                                <MetricCard
                                                    label="Spread"
                                                    value={state.tick ? numberOrDash(state.tick.spread, 1) : "-"}
                                                    detail={state.tick ? `Bid ${numberOrDash(state.tick.bid, 5)} · Ask ${numberOrDash(state.tick.ask, 5)}` : "Esperando cotizacion en vivo."}
                                                    tone={state.tick && state.tick.spread <= 3 ? "positive" : state.tick ? "warning" : "neutral"}
                                                />
                                            </div>
                                        </section>
                                    </div>

                                    <div data-testid="decision-execution-panel">
                                        <TradeTicket
                                            ticket={decisionExecution?.executionPreparation.result ?? null}
                                            bridge={decisionExecution}
                                            bridgeError={decisionExecutionError}
                                        />
                                    </div>
                                </>
                            ) : (
                                <EmptyState
                                    title="Sin lectura operativa"
                                    description="Pulsa Analyze Market para abrir un escenario claro con recomendacion, riesgo y checklist."
                                />
                            )}
                        </Panel>
                    </section>

                    {zones.showPlaybook ? (
                        <section className="workspace-zone workspace-zone--playbook" data-testid="playbook-panel">
                            <Panel
                                eyebrow="Zona 4"
                                title="Playbook"
                                subtitle="Comparacion directa entre el contexto actual y tus setups ganadores."
                            >
                                {state.playbookSetups.length === 0 ? (
                                    <EmptyState
                                        title="Biblioteca en crecimiento"
                                        description="Cuando tengas setups habilitados, aqui veras coincidencias y calidad historica."
                                    />
                                ) : bestLiveMatch ? (
                                    <div className="metric-grid">
                                        <MetricCard label="Setup" value={bestLiveMatch.setupName} detail={bestLiveMatch.explanation} tone={bestLiveMatch.matched ? "positive" : "warning"} />
                                        <MetricCard label="Match %" value={`${bestLiveMatch.matchPercentage}%`} detail={bestLiveMatch.missingConditions.length > 0 ? `Falta: ${bestLiveMatch.missingConditions[0]}` : "Alineacion completa."} tone={bestLiveMatch.matchPercentage >= 70 ? "positive" : bestLiveMatch.matchPercentage >= 50 ? "warning" : "danger"} />
                                        <MetricCard label="Win Rate" value={percentOrDash(topSetupAnalytics?.winRate)} detail="Referencia historica del setup." tone={topSetupAnalytics && topSetupAnalytics.winRate >= 60 ? "positive" : "warning"} />
                                        <MetricCard label="Trades" value={String(topSetupAnalytics?.totalTrades ?? state.performance?.totalTrades ?? 0)} detail="Muestra historica utilizada." />
                                    </div>
                                ) : (
                                    <EmptyState
                                        title="Sin match por ahora"
                                        description="Aun no hay una coincidencia clara. Reanaliza en la siguiente zona de liquidez."
                                    />
                                )}
                            </Panel>
                        </section>
                    ) : null}

                    {zones.showPerformance ? (
                        <section className="workspace-zone workspace-zone--performance" data-testid="performance-panel">
                            <Panel
                                eyebrow="Zona 5"
                                title="Performance Snapshot"
                                subtitle="KPIs historicos para medir consistencia sin distraer la lectura actual."
                            >
                                {state.performance ? (
                                    <>
                                        <div className="metric-grid metric-grid--five">
                                            <MetricCard label="Win Rate" value={percentOrDash(state.performance.winRate)} tone={state.performance.winRate >= 60 ? "positive" : state.performance.winRate >= 45 ? "warning" : "danger"} />
                                            <MetricCard label="Profit Factor" value={getProfitFactor(state.performance)} detail="Estimado desde win rate y average RR." />
                                            <MetricCard label="Average RR" value={numberOrDash(state.performance.averageRR)} />
                                            <MetricCard label="Expectancy" value={getExpectancy(state.performance)} detail="Valor esperado por trade en R." />
                                            <MetricCard label="Last Analysis" value={lastAnalyzedAt ? lastAnalyzedAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "N/A"} />
                                        </div>

                                        <div className="row-list">
                                            {recentTrades.length > 0 ? recentTrades.map((entry) => (
                                                <article key={entry.id} className="row-item">
                                                    <div className="row-item__top">
                                                        <strong className="row-item__title">{entry.symbol} · {entry.timeframe}</strong>
                                                        <span className={`status-chip status-chip--${toneFromStatus(entry.tradeOutcome)}`}>
                                                            {entry.tradeOutcome}
                                                        </span>
                                                    </div>
                                                    <p className="row-item__meta">
                                                        RR {numberOrDash(entry.realizedRR ?? entry.expectedRR)} · {new Date(entry.createdAt).toLocaleDateString()}
                                                    </p>
                                                </article>
                                            )) : (
                                                <EmptyState
                                                    title="Aun sin historial"
                                                    description="Cuando cierres operaciones, aqui veras los ultimos cinco trades con su resultado."
                                                />
                                            )}
                                        </div>
                                    </>
                                ) : (
                                    <EmptyState
                                        title="Esperando track record"
                                        description="Cuando OSCAR tenga historial suficiente, este bloque mostrara tus KPIs clave."
                                    />
                                )}
                            </Panel>
                        </section>
                    ) : null}
                </div>
            </main>
        </div>
    );
}
