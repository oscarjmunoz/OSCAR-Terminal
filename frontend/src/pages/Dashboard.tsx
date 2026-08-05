import axios from "axios";
import { useEffect, useRef, useState } from "react";

import { getAnalyticsBehaviour, getAnalyticsPerformance, getAnalyticsSessions, getAnalyticsSetups, BehaviourAnalytics, PerformanceReport, SessionAnalytics, SetupAnalytics } from "../api/analytics";
import { getLiveDecisionReport, LiveDecisionReport } from "../api/decision";
import { getHealth, getOperationalReadiness, HealthResponse, OperationalReadinessResponse } from "../api/health";
import { getJournalEntries, JournalEntry } from "../api/journal";
import { getStatus, getTick, TerminalStatus, TickResponse } from "../api/market";
import { evaluatePlaybookMatches, getPlaybookSetups, PlaybookMatch, PlaybookSetup } from "../api/playbook";
import { getOperationalSettings, OperationalSettings } from "../api/system";

import EmptyState from "../components/dashboard/EmptyState";
import MetricCard from "../components/dashboard/MetricCard";
import Panel from "../components/dashboard/Panel";
import SelectorField from "../components/dashboard/SelectorField";
import StatusPill from "../components/dashboard/StatusPill";

type DashboardState = {
    marketStatus: TerminalStatus | null;
    tick: TickResponse | null;
    health: HealthResponse | null;
    readiness: OperationalReadinessResponse | null;
    journalEntries: JournalEntry[];
    playbookSetups: PlaybookSetup[];
    performance: PerformanceReport | null;
    sessions: SessionAnalytics[];
    behaviour: BehaviourAnalytics[];
    setupAnalytics: SetupAnalytics[];
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
    health: null,
    readiness: null,
    journalEntries: [],
    playbookSetups: [],
    performance: null,
    sessions: [],
    behaviour: [],
    setupAnalytics: [],
};

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

    if (["OK", "ONLINE", "CONNECTED", "HEALTHY", "GREEN", "BUY", "SELL", "BULLISH", "LOW", "A+", "A"].includes(normalized)) {
        return "positive";
    }

    if (["WARNING", "YELLOW", "WAIT", "NO TRADE", "MEDIUM", "B", "IDLE"].includes(normalized)) {
        return "warning";
    }

    if (["NEUTRAL", "N/A", "RANGE", "C"].includes(normalized)) {
        return "neutral";
    }

    return "danger";
}

function statusLabel(value: string | boolean | null | undefined): string {
    if (typeof value === "boolean") {
        return value ? "ONLINE" : "OFFLINE";
    }

    return value === null || value === undefined ? "N/A" : value.toString().toUpperCase();
}

function bestSession(sessions: SessionAnalytics[]): SessionAnalytics | null {
    const ordered = [...sessions]
        .filter((session) => session.totalTrades > 0)
        .sort((left, right) => {
            if (right.winRate !== left.winRate) {
                return right.winRate - left.winRate;
            }

            return right.totalTrades - left.totalTrades;
        });

    return ordered[0] ?? null;
}

function explainAnalysisError(error: unknown): string {
    if (axios.isAxiosError(error)) {
        if (error.code === "ECONNABORTED") {
            return "Analysis timeout. OSCAR did not receive the DecisionReport in time.";
        }

        const detail = error.response?.data?.detail;

        if (typeof detail === "string") {
            return detail;
        }

        if (detail && typeof detail === "object") {
            const code = typeof detail.code === "string" ? detail.code : "";
            const message = typeof detail.message === "string" ? detail.message : "Unable to analyze the current market.";

            if (code === "mt5_disconnected") {
                return "MT5 disconnected. Reconnect the terminal before requesting a live analysis.";
            }

            if (code === "no_data") {
                return "No market data available for the selected symbol and timeframe. The market may be closed or the feed may be unavailable.";
            }

            return message;
        }

        if (!error.response) {
            return "Backend unavailable. Verify that OSCAR backend is running.";
        }
    }

    return "Unable to analyze the current market.";
}

export default function Dashboard() {
    const [state, setState] = useState<DashboardState>(initialState);
    const [settings, setSettings] = useState<OperationalSettings>(fallbackSettings);
    const [selectedSymbol, setSelectedSymbol] = useState(fallbackSettings.defaultSymbol);
    const [selectedTimeframe, setSelectedTimeframe] = useState(fallbackSettings.defaultTimeframe);
    const [decisionReport, setDecisionReport] = useState<LiveDecisionReport | null>(null);
    const [playbookMatches, setPlaybookMatches] = useState<PlaybookMatch[]>([]);
    const [loading, setLoading] = useState(true);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisProgress, setAnalysisProgress] = useState("Preparing operational workspace.");
    const [analysisError, setAnalysisError] = useState<string | null>(null);
    const [lastAnalyzedAt, setLastAnalyzedAt] = useState<Date | null>(null);
    const [clock, setClock] = useState(() => new Date());

    const initializedRef = useRef(false);
    const analysisRequestRef = useRef(0);

    useEffect(() => {
        const clockTimer = window.setInterval(() => {
            setClock(new Date());
        }, 1000);

        return () => window.clearInterval(clockTimer);
    }, []);

    async function runAnalysis(symbol: string, timeframe: string) {
        const requestId = analysisRequestRef.current + 1;
        analysisRequestRef.current = requestId;

        setIsAnalyzing(true);
        setAnalysisError(null);
        setAnalysisProgress(`Analyzing ${symbol} ${timeframe}.`);

        try {
            setAnalysisProgress("Requesting live DecisionReport from the current market.");

            const [
                marketStatusResult,
                tickResult,
                healthResult,
                readinessResult,
                decisionResult,
            ] = await Promise.allSettled([
                getStatus(),
                getTick(symbol),
                getHealth(),
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

            setAnalysisProgress("Refreshing live playbook match and operational readiness.");

            const playbookMatchResult = await Promise.allSettled([
                evaluatePlaybookMatches(liveDecision),
            ]);

            if (analysisRequestRef.current !== requestId) {
                return;
            }

            const playbookMatchList = settledValue(playbookMatchResult[0]) ?? [];

            setState((previous) => ({
                ...previous,
                marketStatus: settledValue(marketStatusResult) ?? previous.marketStatus,
                tick: settledValue(tickResult) ?? previous.tick,
                health: settledValue(healthResult) ?? previous.health,
                readiness: settledValue(readinessResult) ?? previous.readiness,
            }));
            setDecisionReport(liveDecision);
            setPlaybookMatches([...playbookMatchList].sort((left, right) => right.matchPercentage - left.matchPercentage));
            setLastAnalyzedAt(new Date());
            setAnalysisProgress("Operational analysis synchronized.");
        }
        catch (error) {
            if (analysisRequestRef.current !== requestId) {
                return;
            }

            setDecisionReport(null);
            setPlaybookMatches([]);
            setAnalysisError(explainAnalysisError(error));
            setAnalysisProgress("Analysis failed.");
        }
        finally {
            if (analysisRequestRef.current === requestId) {
                setIsAnalyzing(false);
                setLoading(false);
            }
        }
    }

    useEffect(() => {
        let cancelled = false;

        async function bootstrap() {
            try {
                const [
                    settingsResult,
                    marketStatusResult,
                    healthResult,
                    journalResult,
                    playbookSetupsResult,
                    performanceResult,
                    sessionsResult,
                    behaviourResult,
                    setupAnalyticsResult,
                ] = await Promise.allSettled([
                    getOperationalSettings(),
                    getStatus(),
                    getHealth(),
                    getJournalEntries(),
                    getPlaybookSetups(),
                    getAnalyticsPerformance(),
                    getAnalyticsSessions(),
                    getAnalyticsBehaviour(),
                    getAnalyticsSetups(),
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
                setState({
                    marketStatus: settledValue(marketStatusResult),
                    tick: null,
                    health: settledValue(healthResult),
                    readiness: null,
                    journalEntries: settledValue(journalResult) ?? [],
                    playbookSetups: settledValue(playbookSetupsResult) ?? [],
                    performance: settledValue(performanceResult),
                    sessions: settledValue(sessionsResult) ?? [],
                    behaviour: settledValue(behaviourResult) ?? [],
                    setupAnalytics: settledValue(setupAnalyticsResult) ?? [],
                });

                await runAnalysis(bootstrapSymbol, bootstrapTimeframe);
                initializedRef.current = true;
            }
            catch (error) {
                if (cancelled) {
                    return;
                }

                console.error(error);
                setLoading(false);
                setAnalysisError("Unable to load the operational dashboard.");
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

        void runAnalysis(selectedSymbol, selectedTimeframe);
    }, [selectedSymbol, selectedTimeframe]);

    if (loading) {
        return (
            <div className="app-shell">
                <div className="dashboard__loading">
                    <div className="dashboard__loading-card">
                        <strong className="dashboard__loading-title">Loading OSCAR Terminal</strong>
                        <p className="dashboard__loading-copy">{analysisProgress}</p>
                    </div>
                </div>
            </div>
        );
    }

    const currentSession = state.journalEntries[0]?.session ?? "N/A";
    const bestSetupAnalytics = [...state.setupAnalytics]
        .sort((left, right) => right.averageMatchPercentage - left.averageMatchPercentage)[0] ?? null;
    const bestSessionResult = bestSession(state.sessions);
    const visibleBehaviour = [...state.behaviour].sort((left, right) => right.totalTrades - left.totalTrades).slice(0, 4);
    const visibleJournal = state.journalEntries.slice(0, 5);
    const readinessItems = state.readiness?.items ?? [];
    const bestLiveMatch = playbookMatches[0] ?? null;

    return (
        <div className="app-shell">
            <main className="dashboard">
                <div className="dashboard__grid dashboard__grid--operational">
                    <div className="dashboard__header header-bar">
                        <div>
                            <h1 className="header-bar__title">OSCAR Trade IA</h1>
                            <p className="header-bar__subtitle">
                                Operational copilot for live market analysis, playbook validation and system readiness.
                            </p>
                        </div>

                        <div className="header-bar__meta">
                            <StatusPill label="Symbol" value={selectedSymbol} tone="neutral" />
                            <StatusPill label="Timeframe" value={selectedTimeframe} tone="neutral" />
                            <StatusPill label="Session" value={currentSession} tone="neutral" />
                            <StatusPill label="MT5" value={statusLabel(state.marketStatus?.connected ?? false)} tone={toneFromStatus(state.marketStatus?.connected ?? false)} />
                            <StatusPill label="Readiness" value={state.readiness?.overallStatus ?? "N/A"} tone={toneFromStatus(state.readiness?.overallStatus)} />
                            <StatusPill label="Clock" value={clock.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })} tone="neutral" />
                        </div>
                    </div>

                    <div className="dashboard__controls">
                        <Panel
                            eyebrow="Operational Flow"
                            title="Market Context"
                            subtitle="Choose symbol and timeframe, then request a live DecisionReport. Changing either control refreshes the live analysis automatically."
                            action={<StatusPill label="Analyze" value={isAnalyzing ? "RUNNING" : "READY"} tone={isAnalyzing ? "warning" : "positive"} />}
                            testId="analysis-controls"
                        >
                            <div className="dashboard__control-grid">
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
                                    {isAnalyzing ? "Analyzing Market..." : "Analyze Market"}
                                </button>
                            </div>

                            {analysisError ? (
                                <div className="dashboard__message dashboard__message--danger" role="alert">
                                    <strong>Analysis blocked.</strong>
                                    <span>{analysisError}</span>
                                </div>
                            ) : (
                                <div className="dashboard__message dashboard__message--neutral">
                                    <strong>Progress</strong>
                                    <span>{analysisProgress}</span>
                                </div>
                            )}
                        </Panel>
                    </div>

                    <div className="dashboard__decision">
                        <Panel
                            eyebrow="Decision Center"
                            title="Live Decision Report"
                            subtitle={isAnalyzing ? "Building a report from current market conditions." : "Primary decision panel always reflects the current market, never a historical journal snapshot."}
                            action={<StatusPill label="Last Analysis" value={lastAnalyzedAt ? lastAnalyzedAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "N/A"} tone={lastAnalyzedAt ? "positive" : "neutral"} />}
                            testId="decision-center"
                        >
                            {decisionReport ? (
                                <>
                                    <div className="metric-grid">
                                        <MetricCard label="Bias" value={decisionReport.market_bias.bias} detail={decisionReport.market_bias.explanation} tone={toneFromStatus(decisionReport.market_bias.bias)} />
                                        <MetricCard label="Recommendation" value={decisionReport.final_recommendation.recommendation} detail={decisionReport.final_recommendation.explanation} tone={toneFromStatus(decisionReport.final_recommendation.recommendation)} />
                                        <MetricCard label="Institutional Score" value={String(decisionReport.institutional_score.score)} detail={`Quality ${decisionReport.institutional_score.quality_level}`} tone={decisionReport.institutional_score.score >= 70 ? "positive" : decisionReport.institutional_score.score >= 50 ? "warning" : "danger"} />
                                        <MetricCard label="Confidence" value={percentOrDash(decisionReport.institutional_score.confidence)} detail={decisionReport.market_structure.explanation} tone={decisionReport.institutional_score.confidence >= 70 ? "positive" : decisionReport.institutional_score.confidence >= 50 ? "warning" : "danger"} />
                                    </div>

                                    <div className="metric-grid">
                                        <MetricCard label="Trend" value={decisionReport.market_structure.trend} detail={`BOS ${decisionReport.market_structure.bos ? "YES" : "NO"} · CHOCH ${decisionReport.market_structure.choch ? "YES" : "NO"} · MSS ${decisionReport.market_structure.mss ? "YES" : "NO"}`} tone={toneFromStatus(decisionReport.market_structure.trend)} />
                                        <MetricCard label="Liquidity" value={String(decisionReport.liquidity.liquidity_taken)} detail={decisionReport.liquidity.explanation} tone={decisionReport.liquidity.liquidity_taken > 0 ? "positive" : "warning"} />
                                        <MetricCard label="Price" value={numberOrDash(decisionReport.context.price, 5)} detail={`SL ${numberOrDash(decisionReport.context.sl, 5)} · TP ${numberOrDash(decisionReport.context.tp, 5)}`} />
                                        <MetricCard label="Spread" value={state.tick ? numberOrDash(state.tick.spread, 1) : "-"} detail={state.tick ? `Bid ${numberOrDash(state.tick.bid, 5)} · Ask ${numberOrDash(state.tick.ask, 5)}` : "No live tick available."} tone={state.tick && state.tick.spread <= 3 ? "positive" : state.tick ? "warning" : "neutral"} />
                                    </div>

                                    <div className="decision-list">
                                        {decisionReport.execution_checklist.length > 0 ? decisionReport.execution_checklist.map((item) => (
                                            <div key={item.label} className="decision-item">
                                                <div className="decision-item__title">
                                                    <strong>{item.label}</strong>
                                                    <span className={`status-chip ${item.checked ? "status-chip--positive" : "status-chip--danger"}`}>
                                                        {item.checked ? "PASS" : "FAIL"}
                                                    </span>
                                                </div>
                                                <p className="decision-item__text">{item.explanation}</p>
                                            </div>
                                        )) : null}
                                    </div>
                                </>
                            ) : (
                                <EmptyState
                                    title="No live analysis yet"
                                    description="Select a symbol and timeframe, then run Analyze Market to generate a current DecisionReport."
                                />
                            )}
                        </Panel>
                    </div>

                    <div className="dashboard__playbook">
                        <Panel
                            eyebrow="Playbook Match"
                            title="Current Setup Alignment"
                            subtitle="Evaluated from the live DecisionReport only. Journal history is not used for the primary match panel."
                            testId="playbook-panel"
                        >
                            {state.playbookSetups.length === 0 ? (
                                <EmptyState
                                    title="No playbooks configured"
                                    description="Create or enable playbooks to evaluate the live market against your setup library."
                                />
                            ) : bestLiveMatch ? (
                                <>
                                    <div className="metric-grid">
                                        <MetricCard label="Enabled Setups" value={String(state.playbookSetups.filter((setup) => setup.enabled).length)} detail="Available for live evaluation." />
                                        <MetricCard label="Top Match" value={bestLiveMatch.setupName} detail={bestLiveMatch.explanation} tone={bestLiveMatch.matched ? "positive" : bestLiveMatch.matchPercentage >= 50 ? "warning" : "danger"} />
                                        <MetricCard label="Match %" value={`${bestLiveMatch.matchPercentage}%`} detail={bestLiveMatch.matched ? "Setup fully aligned." : "Partial live alignment."} tone={bestLiveMatch.matchPercentage >= 70 ? "positive" : bestLiveMatch.matchPercentage >= 50 ? "warning" : "danger"} />
                                        <MetricCard label="Historical Benchmark" value={percentOrDash(bestSetupAnalytics?.averageMatchPercentage)} detail={bestSetupAnalytics?.setupName ?? "No historical setup analytics."} tone={bestSetupAnalytics && bestSetupAnalytics.averageMatchPercentage >= 70 ? "positive" : "warning"} />
                                    </div>

                                    <div className="row-list">
                                        {playbookMatches.slice(0, 4).map((match) => (
                                            <div key={match.setupId} className="row-item">
                                                <div className="row-item__top">
                                                    <strong className="row-item__title">{match.setupName}</strong>
                                                    <span className={`status-chip ${match.matchPercentage >= 70 ? "status-chip--positive" : match.matchPercentage >= 50 ? "status-chip--warning" : "status-chip--danger"}`}>
                                                        {match.matchPercentage}%
                                                    </span>
                                                </div>
                                                <p className="row-item__meta">{match.explanation}</p>
                                                <p className="row-item__note">
                                                    {match.missingConditions.length > 0 ? `Missing: ${match.missingConditions.join(" · ")}` : "All required conditions matched."}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </>
                            ) : (
                                <EmptyState
                                    title="No live playbook match"
                                    description="Analyze the current market to calculate playbook alignment for the selected symbol and timeframe."
                                />
                            )}
                        </Panel>
                    </div>

                    <div className="dashboard__risk">
                        <Panel
                            eyebrow="Risk"
                            title="Risk Envelope"
                            subtitle="Projected from the live operational context only. No order is placed from this panel."
                            testId="risk-panel"
                        >
                            {decisionReport ? (
                                <div className="metric-grid">
                                    <MetricCard label="Expected RR" value={numberOrDash(decisionReport.risk_assessment.rr_expected)} detail="Projected reward-to-risk ratio." tone={decisionReport.risk_assessment.rr_expected >= 1.5 ? "positive" : decisionReport.risk_assessment.rr_expected >= 1 ? "warning" : "danger"} />
                                    <MetricCard label="Risk" value={decisionReport.risk_assessment.risk} detail={`Risk % ${numberOrDash(decisionReport.risk_assessment.risk_percent)}%`} tone={toneFromStatus(decisionReport.risk_assessment.risk)} />
                                    <MetricCard label="Volatility" value={numberOrDash(decisionReport.risk_assessment.volatility)} detail="Average range over the live analysis window." tone={decisionReport.risk_assessment.volatility <= 15 ? "positive" : decisionReport.risk_assessment.volatility <= 25 ? "warning" : "danger"} />
                                    <MetricCard label="Setup Quality" value={decisionReport.risk_assessment.setup_quality} detail="Derived from institutional score and confluence quality." tone={toneFromStatus(decisionReport.risk_assessment.setup_quality)} />
                                </div>
                            ) : (
                                <EmptyState
                                    title="Risk not available"
                                    description="Run a live market analysis to project the current risk envelope."
                                />
                            )}
                        </Panel>
                    </div>

                    <div className="dashboard__narrative">
                        <Panel
                            eyebrow="Narrative"
                            title="Market Readout"
                            subtitle="OSCAR summarizes the live market context and confluences for the trader."
                            testId="narrative-panel"
                        >
                            {decisionReport ? (
                                <>
                                    <div className="empty-state">
                                        <strong className="empty-state__title">Current Narrative</strong>
                                        <p className="empty-state__description">{decisionReport.narrative}</p>
                                    </div>

                                    <div className="row-list">
                                        {decisionReport.confluences.slice(0, 4).map((item) => (
                                            <div key={item.name} className="row-item">
                                                <div className="row-item__top">
                                                    <strong className="row-item__title">{item.name}</strong>
                                                    <span className={`status-chip ${item.detected ? "status-chip--positive" : "status-chip--warning"}`}>
                                                        {item.importance}
                                                    </span>
                                                </div>
                                                <p className="row-item__meta">{item.explanation}</p>
                                            </div>
                                        ))}
                                    </div>
                                </>
                            ) : (
                                <EmptyState
                                    title="Narrative unavailable"
                                    description="The live narrative will appear after Analyze Market completes."
                                />
                            )}
                        </Panel>
                    </div>

                    <div className="dashboard__analytics">
                        <Panel
                            eyebrow="Analytics Snapshot"
                            title="Historical Context"
                            subtitle="Read-only analytics remain historical and are not used as the primary live decision source."
                            testId="analytics-panel"
                        >
                            {state.performance ? (
                                <>
                                    <div className="metric-grid">
                                        <MetricCard label="Win Rate" value={percentOrDash(state.performance.winRate)} detail="Historical performance." tone={state.performance.winRate >= 60 ? "positive" : state.performance.winRate >= 45 ? "warning" : "danger"} />
                                        <MetricCard label="Average RR" value={numberOrDash(state.performance.averageRR)} detail="Historical realized RR." />
                                        <MetricCard label="Total Trades" value={String(state.performance.totalTrades)} detail="Tracked journal operations." />
                                        <MetricCard label="Best Session" value={bestSessionResult?.session ?? "N/A"} detail={bestSessionResult ? `${percentOrDash(bestSessionResult.winRate)} win rate` : "No session data yet."} tone={bestSessionResult ? "positive" : "neutral"} />
                                    </div>

                                    <div className="row-list">
                                        {visibleBehaviour.length > 0 ? visibleBehaviour.map((item) => (
                                            <div key={item.behaviour} className="row-item">
                                                <div className="row-item__top">
                                                    <strong className="row-item__title">{item.behaviour}</strong>
                                                    <span className={`status-chip ${item.winRate >= 60 ? "status-chip--positive" : item.winRate >= 45 ? "status-chip--warning" : "status-chip--danger"}`}>
                                                        {percentOrDash(item.winRate)}
                                                    </span>
                                                </div>
                                                <p className="row-item__meta">Trades: {item.totalTrades} · Avg RR: {numberOrDash(item.averageRR)} · Net RR: {numberOrDash(item.netRR)}</p>
                                            </div>
                                        )) : (
                                            <EmptyState title="No analytics" description="Analytics are available, but no historical breakdown exists yet." />
                                        )}
                                    </div>
                                </>
                            ) : (
                                <EmptyState
                                    title="No analytics"
                                    description="Historical analytics are not available yet."
                                />
                            )}
                        </Panel>
                    </div>

                    <div className="dashboard__journal">
                        <Panel
                            eyebrow="Journal"
                            title="Recent Operations"
                            subtitle="Optional historical reference only. The primary live decision panel never uses journal snapshots."
                            testId="journal-panel"
                        >
                            {visibleJournal.length > 0 ? (
                                <div className="row-list">
                                    {visibleJournal.map((entry) => (
                                        <div key={entry.id} className="row-item">
                                            <div className="row-item__top">
                                                <strong className="row-item__title">{entry.symbol} · {entry.timeframe} · {entry.session}</strong>
                                                <span className={`status-chip ${toneFromStatus(entry.tradeOutcome) === "positive" ? "status-chip--positive" : toneFromStatus(entry.tradeOutcome) === "warning" ? "status-chip--warning" : "status-chip--danger"}`}>
                                                    {entry.tradeOutcome}
                                                </span>
                                            </div>
                                            <p className="row-item__meta">
                                                RR: {numberOrDash(entry.realizedRR ?? entry.expectedRR)} · Decision: {entry.traderDecision} · {new Date(entry.createdAt).toLocaleString()}
                                            </p>
                                            <p className="row-item__note">{entry.personalNotes || entry.closeReason || "No notes captured."}</p>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <EmptyState
                                    title="No journal"
                                    description="No historical operations are available yet."
                                />
                            )}
                        </Panel>
                    </div>

                    <div className="dashboard__health">
                        <Panel
                            eyebrow="Health Panel"
                            title="Operational Readiness"
                            subtitle="End-to-end system status for the selected live analysis context."
                            action={<StatusPill label="Generated" value={state.readiness?.generatedAt ? new Date(state.readiness.generatedAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "N/A"} tone={toneFromStatus(state.readiness?.overallStatus)} />}
                            testId="health-panel"
                        >
                            {readinessItems.length > 0 ? (
                                <div className="dashboard__health-grid">
                                    {readinessItems.map((item) => (
                                        <MetricCard
                                            key={item.key}
                                            label={item.label}
                                            value={item.status}
                                            detail={item.detail}
                                            tone={toneFromStatus(item.status)}
                                        />
                                    ))}
                                </div>
                            ) : (
                                <EmptyState
                                    title="Health unavailable"
                                    description="Operational readiness will appear after a live market analysis."
                                />
                            )}
                        </Panel>
                    </div>
                </div>
            </main>
        </div>
    );
}
