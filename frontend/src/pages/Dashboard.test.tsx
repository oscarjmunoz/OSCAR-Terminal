import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";

import Dashboard from "./Dashboard";

import { getAnalyticsPerformance } from "../api/analytics";
import { getLiveDecisionReport } from "../api/decision";
import { getOperationalReadiness } from "../api/health";
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
    ],
};

beforeEach(() => {
    window.localStorage.clear();

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
});

describe("Dashboard", () => {
    it("renders skeleton loading state immediately", () => {
        render(<Dashboard />);

        expect(screen.getByTestId("dashboard-skeleton")).toBeInTheDocument();
    });

    it("renders institutional zones from live report", async () => {
        render(<Dashboard />);

        const decisionPanel = await screen.findByTestId("decision-center");
        expect(within(decisionPanel).getByText("WAIT")).toBeInTheDocument();
        expect(within(decisionPanel).getByText("68.40%")).toBeInTheDocument();

        expect(screen.getByTestId("trading-bar")).toBeInTheDocument();
        expect(screen.getByTestId("market-snapshot")).toHaveTextContent("Institutional Score");
        expect(screen.getByTestId("playbook-panel")).toHaveTextContent("London Breakout");
        expect(screen.getByTestId("performance-panel")).toHaveTextContent("Profit Factor");
        expect(screen.getByTestId("risk-panel")).toHaveTextContent("Expected RR");
        expect(screen.getByTestId("checklist-panel")).toHaveTextContent("Trend aligned");
    });

    it("requests a fresh live report when timeframe changes and when Analyze Market is clicked", async () => {
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

    it("activates focus mode and hides non-essential zones", async () => {
        render(<Dashboard />);

        await screen.findByTestId("decision-center");
        fireEvent.click(screen.getByRole("button", { name: "Focus Mode" }));

        await waitFor(() => {
            expect(screen.queryByTestId("market-snapshot")).not.toBeInTheDocument();
            expect(screen.queryByTestId("playbook-panel")).not.toBeInTheDocument();
            expect(screen.queryByTestId("performance-panel")).not.toBeInTheDocument();
        });

        expect(screen.getByTestId("risk-panel")).toBeInTheDocument();
        expect(screen.getByTestId("narrative-panel")).toBeInTheDocument();
        expect(screen.getByTestId("checklist-panel")).toBeInTheDocument();
    });

    it("stores symbol favorites in localStorage", async () => {
        render(<Dashboard />);

        await screen.findByTestId("favorites-panel");
        const starToggle = screen.getByLabelText("Toggle GBPUSD favorite");
        fireEvent.click(starToggle);

        const raw = window.localStorage.getItem("oscar.favoriteSymbols.v1");
        expect(raw).not.toBeNull();
        expect(raw).toContain("GBPUSD");
    });

    it("shows graceful empty states for optional history", async () => {
        vi.mocked(getJournalEntries).mockResolvedValueOnce([]);
        vi.mocked(getPlaybookSetups).mockResolvedValueOnce([]);
        vi.mocked(evaluatePlaybookMatches).mockResolvedValueOnce([]);
        vi.mocked(getAnalyticsPerformance).mockResolvedValueOnce(null as never);

        render(<Dashboard />);

        await screen.findByTestId("decision-center");
        expect(screen.getByText("Biblioteca en crecimiento")).toBeInTheDocument();
        expect(screen.getByText("Esperando track record")).toBeInTheDocument();
    });
});
