import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";

import Dashboard from "./Dashboard";

import { getAnalyticsBehaviour, getAnalyticsPerformance, getAnalyticsSessions, getAnalyticsSetups } from "../api/analytics";
import { getLiveDecisionReport } from "../api/decision";
import { getHealth, getOperationalReadiness } from "../api/health";
import { getJournalEntries } from "../api/journal";
import { getStatus, getTick } from "../api/market";
import { evaluatePlaybookMatches, getPlaybookSetups } from "../api/playbook";
import { getOperationalSettings } from "../api/system";

vi.mock("../api/system", () => ({
    getOperationalSettings: vi.fn(),
}));

vi.mock("../api/decision", () => ({
    getLiveDecisionReport: vi.fn(),
}));

vi.mock("../api/market", () => ({
    getStatus: vi.fn(),
    getTick: vi.fn(),
}));

vi.mock("../api/health", () => ({
    getHealth: vi.fn(),
    getOperationalReadiness: vi.fn(),
}));

vi.mock("../api/journal", () => ({
    getJournalEntries: vi.fn(),
}));

vi.mock("../api/playbook", () => ({
    getPlaybookSetups: vi.fn(),
    evaluatePlaybookMatches: vi.fn(),
}));

vi.mock("../api/analytics", () => ({
    getAnalyticsPerformance: vi.fn(),
    getAnalyticsSessions: vi.fn(),
    getAnalyticsBehaviour: vi.fn(),
    getAnalyticsSetups: vi.fn(),
}));

const liveDecisionReport = {
    context: {
        symbol: "EURUSD",
        side: "SELL",
        volume: 0.1,
        sl: 1.092,
        tp: 1.084,
        comment: "live-operational-analysis:M5",
        price: 1.089,
    },
    market_bias: {
        bias: "BEARISH",
        explanation: "Current structure is bearish.",
    },
    institutional_score: {
        score: 78,
        confidence: 68.4,
        quality_level: "A",
    },
    liquidity: {
        buy_liquidity: 3,
        sell_liquidity: 7,
        liquidity_taken: 2,
        pending_liquidity: 4,
        explanation: "Sell-side liquidity dominates.",
    },
    market_structure: {
        trend: "BEARISH",
        bos: true,
        choch: false,
        mss: true,
        explanation: "Lower highs remain intact.",
    },
    institutional_zones: {
        order_block: { active: true, explanation: "Bearish order block active." },
        breaker: { active: false, explanation: "Breaker inactive." },
        mitigation: { active: true, explanation: "Mitigation zone active." },
        fvg: { active: true, explanation: "FVG aligned." },
        premium: { active: true, explanation: "Price remains in premium." },
        discount: { active: false, explanation: "Not in discount." },
    },
    confluences: [
        { name: "Trend alignment", detected: true, importance: "HIGH", explanation: "Trend and side align." },
        { name: "Liquidity sweep", detected: false, importance: "MEDIUM", explanation: "Sweep pending." },
    ],
    risk_assessment: {
        rr_expected: 2.1,
        risk: "LOW",
        risk_percent: 0.45,
        volatility: 12.4,
        setup_quality: "A",
    },
    execution_checklist: [
        { label: "Trend aligned", checked: true, explanation: "Bias and structure are aligned." },
        { label: "Liquidity confirmed", checked: false, explanation: "Awaiting deeper sweep confirmation." },
    ],
    final_recommendation: {
        recommendation: "WAIT",
        explanation: "Context is bearish, but execution still requires confirmation.",
    },
    narrative: "Live bearish context with partial confluence. Decision remains with the trader.",
};

const journalEntry = {
    id: "entry-1",
    createdAt: "2026-08-04T08:30:00Z",
    symbol: "USDCHF",
    timeframe: "M5",
    session: "LONDON",
    entryPrice: 0.9101,
    stopLoss: 0.908,
    takeProfit: 0.914,
    positionSize: 1,
    riskPercent: 1,
    expectedRR: 2.5,
    decisionSnapshot: {
        bias: { bias: "BULLISH", explanation: "Historical journal snapshot." },
        score: 84,
        confidence: 72.5,
        liquidity: {
            buy_liquidity: 6,
            sell_liquidity: 2,
            liquidity_taken: 3,
            pending_liquidity: 4,
            explanation: "Buy-side liquidity is dominant.",
        },
        structure: {
            trend: "BULLISH",
            bos: true,
            choch: false,
            mss: true,
            explanation: "Historical structure remains bullish.",
        },
        zones: {
            order_block: { active: true, explanation: "OB active." },
            breaker: { active: false, explanation: "Breaker inactive." },
            mitigation: { active: true, explanation: "Mitigation present." },
            fvg: { active: true, explanation: "FVG aligned." },
            premium: { active: false, explanation: "Not in premium." },
            discount: { active: true, explanation: "In discount." },
        },
        confluences: [],
        checklist: [],
        recommendation: {
            recommendation: "BUY",
            explanation: "Historical journal decision.",
        },
        narrative: "Historical journal narrative.",
    },
    traderDecision: "FOLLOWED_OSCAR",
    tradeOutcome: "WIN",
    profitLoss: 120,
    realizedRR: 2.2,
    durationMinutes: 42,
    closeReason: null,
    personalNotes: "Execution was clean.",
    tags: ["A+", "LONDON"],
};

const readiness = {
    symbol: "EURUSD",
    timeframe: "M5",
    generatedAt: "2026-08-04T10:10:00Z",
    overallStatus: "GREEN",
    items: [
        { key: "mt5", label: "MT5", status: "GREEN", detail: "Terminal connected and responding.", observedAt: null },
        { key: "broker", label: "Broker", status: "GREEN", detail: "Broker X · Demo-01", observedAt: null },
        { key: "market-feed", label: "Market Feed", status: "YELLOW", detail: "Feed is slightly delayed.", observedAt: null },
        { key: "last-tick", label: "Last Tick", status: "GREEN", detail: "Last tick observed at 2026-08-04T10:09:59Z", observedAt: "2026-08-04T10:09:59Z" },
        { key: "last-candle", label: "Last Candle", status: "GREEN", detail: "Last candle observed at 2026-08-04T10:05:00Z", observedAt: "2026-08-04T10:05:00Z" },
        { key: "decision-center", label: "Decision Center", status: "GREEN", detail: "Live context refreshed.", observedAt: "2026-08-04T10:09:59Z" },
        { key: "journal", label: "Journal", status: "GREEN", detail: "1 historical entry available.", observedAt: null },
        { key: "playbook", label: "Playbook", status: "GREEN", detail: "1 enabled setup available.", observedAt: null },
        { key: "analytics", label: "Analytics", status: "GREEN", detail: "Analytics built from 8 tracked trades.", observedAt: null },
    ],
};

beforeEach(() => {
    vi.mocked(getOperationalSettings).mockResolvedValue({
        defaultSymbol: "EURUSD",
        defaultTimeframe: "M5",
        availableSymbols: ["EURUSD", "GBPUSD", "USDJPY"],
        availableTimeframes: ["M1", "M5", "H1"],
    });
    vi.mocked(getStatus).mockResolvedValue({
        connected: true,
        account: 123456,
        company: "Broker X",
        server: "Demo-01",
    });
    vi.mocked(getTick).mockResolvedValue({
        symbol: "EURUSD",
        bid: 1.0888,
        ask: 1.089,
        spread: 2,
    });
    vi.mocked(getHealth).mockResolvedValue({
        status: "ok",
        service: "OSCAR Terminal",
        version: "1.0.0-rc1",
    });
    vi.mocked(getOperationalReadiness).mockResolvedValue(readiness);
    vi.mocked(getLiveDecisionReport).mockResolvedValue(liveDecisionReport);
    vi.mocked(getJournalEntries).mockResolvedValue([journalEntry]);
    vi.mocked(getPlaybookSetups).mockResolvedValue([
        {
            id: "setup-1",
            name: "London Breakout",
            description: "Breakout during London session.",
            category: "Trend",
            enabled: true,
            createdAt: "2026-08-04T08:00:00Z",
            updatedAt: "2026-08-04T08:00:00Z",
        },
    ]);
    vi.mocked(evaluatePlaybookMatches).mockResolvedValue([
        {
            setupId: "setup-1",
            setupName: "London Breakout",
            matched: false,
            matchPercentage: 75,
            matchedConditions: ["Bias == BEARISH"],
            missingConditions: ["Liquidity sweep"],
            explanation: "London Breakout: matched 75% - missing Liquidity sweep",
        },
    ]);
    vi.mocked(getAnalyticsPerformance).mockResolvedValue({
        totalTrades: 8,
        wins: 5,
        losses: 2,
        breakEven: 1,
        cancelled: 0,
        winRate: 62.5,
        averageRR: 1.9,
        netRR: 9.5,
        averageDuration: 38,
    });
    vi.mocked(getAnalyticsSessions).mockResolvedValue([
        { session: "ASIA", totalTrades: 2, winRate: 50, averageRR: 0.9 },
        { session: "LONDON", totalTrades: 4, winRate: 75, averageRR: 2.1 },
    ]);
    vi.mocked(getAnalyticsBehaviour).mockResolvedValue([
        { behaviour: "FOLLOWED_OSCAR", totalTrades: 5, winRate: 80, averageRR: 2.3, netRR: 11.5 },
        { behaviour: "WAITED", totalTrades: 3, winRate: 40, averageRR: 0.8, netRR: 2.1 },
    ]);
    vi.mocked(getAnalyticsSetups).mockResolvedValue([
        { setupId: "setup-1", setupName: "London Breakout", totalTrades: 8, winRate: 62.5, averageRR: 1.9, averageMatchPercentage: 88.2 },
    ]);
});

describe("Dashboard", () => {
    it("renders the loading state immediately", () => {
        render(<Dashboard />);

        expect(screen.getByText("Loading OSCAR Terminal")).toBeInTheDocument();
    });

    it("renders empty states for missing optional historical data", async () => {
        vi.mocked(getJournalEntries).mockResolvedValueOnce([]);
        vi.mocked(getPlaybookSetups).mockResolvedValueOnce([]);
        vi.mocked(evaluatePlaybookMatches).mockResolvedValueOnce([]);
        vi.mocked(getAnalyticsPerformance).mockResolvedValueOnce(null as never);
        vi.mocked(getAnalyticsSessions).mockResolvedValueOnce([]);
        vi.mocked(getAnalyticsBehaviour).mockResolvedValueOnce([]);
        vi.mocked(getAnalyticsSetups).mockResolvedValueOnce([]);
        vi.mocked(getOperationalReadiness).mockResolvedValueOnce({
            ...readiness,
            items: readiness.items.map((item) => item.key === "journal" ? { ...item, status: "YELLOW", detail: "No historical entries exist yet." } : item),
        });

        render(<Dashboard />);

        expect(await screen.findByTestId("decision-center")).toBeInTheDocument();
        expect(screen.getByText("No playbooks configured")).toBeInTheDocument();
        expect(screen.getByText("No analytics")).toBeInTheDocument();
        expect(screen.getByText("No journal")).toBeInTheDocument();
    });

    it("renders the live dashboard using the current DecisionReport instead of the journal snapshot", async () => {
        render(<Dashboard />);

        const decisionPanel = await screen.findByTestId("decision-center");
        expect(within(decisionPanel).getByText("WAIT")).toBeInTheDocument();
        expect(within(decisionPanel).getByText("BEARISH")).toBeInTheDocument();
        expect(within(decisionPanel).getByText("78")).toBeInTheDocument();
        expect(within(decisionPanel).getByText("68.40%")).toBeInTheDocument();

        expect(screen.getByTestId("playbook-panel")).toHaveTextContent("London Breakout");
        expect(screen.getByTestId("risk-panel")).toHaveTextContent("2.10");
        expect(screen.getByTestId("narrative-panel")).toHaveTextContent("Live bearish context");
        expect(screen.getByTestId("analytics-panel")).toHaveTextContent("62.50%");
        expect(screen.getByTestId("journal-panel")).toHaveTextContent("Execution was clean.");
        expect(screen.getByTestId("health-panel")).toHaveTextContent("Decision Center");
    });

    it("requests a fresh live report when the trader changes timeframe and when Analyze Market is clicked", async () => {
        render(<Dashboard />);

        await screen.findByTestId("analysis-controls");
        expect(getLiveDecisionReport).toHaveBeenCalledWith("EURUSD", "M5");

        fireEvent.change(screen.getByLabelText("Timeframe"), {
            target: { value: "H1" },
        });

        await waitFor(() => {
            expect(getLiveDecisionReport).toHaveBeenCalledWith("EURUSD", "H1");
        });

        const callsAfterSelection = vi.mocked(getLiveDecisionReport).mock.calls.length;

        fireEvent.click(screen.getByRole("button", { name: "Analyze Market" }));

        await waitFor(() => {
            expect(vi.mocked(getLiveDecisionReport).mock.calls.length).toBeGreaterThan(callsAfterSelection);
        });
    });
});
