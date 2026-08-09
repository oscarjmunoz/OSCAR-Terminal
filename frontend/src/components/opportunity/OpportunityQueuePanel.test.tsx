import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, within } from "@testing-library/react";

import OpportunityQueuePanel from "./OpportunityQueuePanel";

const queue = [
    {
        symbol: "EURUSD",
        timeframe: "M5",
        bias: "BEARISH",
        structure: "BEARISH|BOS=1|CHOCH=0|MSS=1",
        liquidity_target: "SELL_SIDE_LIQUIDITY",
        current_stage: "EXECUTION_WINDOW",
        opportunity_score: 88.45,
        institutional_score: 79.2,
        execution_quality: 74.3,
        priority: "HIGH",
        estimated_eta: "NOW",
        decision_summary: "Bearish structure with execution window available.",
        recommended_action: "READY",
        last_update: "2026-08-09T09:30:00Z",
        health: "GREEN",
    },
    {
        symbol: "GBPUSD",
        timeframe: "H1",
        bias: "BULLISH",
        structure: "BULLISH|BOS=0|CHOCH=1|MSS=0",
        liquidity_target: "BUY_SIDE_LIQUIDITY",
        current_stage: "WAITING_MSS",
        opportunity_score: 61.2,
        institutional_score: 58.4,
        execution_quality: 49.8,
        priority: "MEDIUM",
        estimated_eta: "30_60_MIN",
        decision_summary: "Higher-timeframe confirmation still developing.",
        recommended_action: "WATCH",
        last_update: "2026-08-09T09:20:00Z",
    },
];

const marketSummary = {
    total_assets: 2,
    ignored: 1,
    watching: 1,
    preparing: 0,
    ready: 1,
    active: 0,
    last_scan: "2026-08-09T09:30:00Z",
};

describe("OpportunityQueuePanel", () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it("renders returned opportunities and the important fields", () => {
        render(
            <OpportunityQueuePanel
                opportunities={queue as never}
                marketSummary={marketSummary}
                selectedOpportunityKey={null}
                onInspect={vi.fn()}
                onRefresh={vi.fn()}
            />
        );

        expect(screen.getByText("EURUSD · M5")).toBeInTheDocument();
        expect(screen.getByText("GBPUSD · H1")).toBeInTheDocument();
        expect(screen.getByText("Direction: BEARISH · Stage: EXECUTION_WINDOW · Health: GREEN")).toBeInTheDocument();
        expect(screen.getByText("Score: 88.45 · Institutional: 79.20 · Execution: 74.30")).toBeInTheDocument();
        expect(screen.getByText("Bearish structure with execution window available.")).toBeInTheDocument();
        expect(screen.getByText(/Last scan:/)).toBeInTheDocument();
        expect(screen.getByText("Total")).toBeInTheDocument();
        expect(screen.getByText("Ready")).toBeInTheDocument();
    });

    it("renders the loading state", () => {
        render(
            <OpportunityQueuePanel
                opportunities={[]}
                marketSummary={null}
                selectedOpportunityKey={null}
                isLoading
                onInspect={vi.fn()}
                onRefresh={vi.fn()}
            />
        );

        expect(screen.getByText("Loading opportunity queue")).toBeInTheDocument();
    });

    it("renders the empty queue state", () => {
        render(
            <OpportunityQueuePanel
                opportunities={[]}
                marketSummary={marketSummary}
                selectedOpportunityKey={null}
                onInspect={vi.fn()}
                onRefresh={vi.fn()}
            />
        );

        expect(screen.getByText("Opportunity queue is empty")).toBeInTheDocument();
    });

    it("renders the API error state", () => {
        render(
            <OpportunityQueuePanel
                opportunities={[]}
                marketSummary={null}
                selectedOpportunityKey={null}
                error="Opportunity queue is unavailable right now."
                onInspect={vi.fn()}
                onRefresh={vi.fn()}
            />
        );

        expect(screen.getByRole("alert")).toHaveTextContent("Opportunity queue unavailable");
    });

    it("marks and inspects a selected opportunity without triggering execution logic", () => {
        const onInspect = vi.fn();
        const onRefresh = vi.fn();

        render(
            <OpportunityQueuePanel
                opportunities={queue as never}
                marketSummary={marketSummary}
                selectedOpportunityKey="EURUSD:M5"
                onInspect={onInspect}
                onRefresh={onRefresh}
            />
        );

        expect(screen.getByText("Direction: BEARISH · Stage: EXECUTION_WINDOW · Health: GREEN")).toBeInTheDocument();
        expect(screen.getByText("Direction: BULLISH · Stage: WAITING_MSS · Health: N/A")).toBeInTheDocument();

        const inspectButton = screen.getByRole("button", { name: "Inspect EURUSD M5" });
        const selectedItem = inspectButton.closest("[data-testid='opportunity-item']") as HTMLElement;
        expect(within(selectedItem).getByText("INSPECTING")).toBeInTheDocument();

        fireEvent.click(screen.getByRole("button", { name: "Inspect GBPUSD H1" }));

        expect(onInspect).toHaveBeenCalledWith(expect.objectContaining({ symbol: "GBPUSD", timeframe: "H1" }));
        expect(onInspect).toHaveBeenCalledTimes(1);
        expect(onRefresh).not.toHaveBeenCalled();
    });
});