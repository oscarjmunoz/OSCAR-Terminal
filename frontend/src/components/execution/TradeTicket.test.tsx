import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import TradeTicket from "./TradeTicket";

function buildBridge(
    action: "PREPARE" | "REVIEW" | "BLOCK" | "DISPATCH",
    recommendation: string = action === "BLOCK" ? "NO_TRADE" : "WAIT"
) {
    const dispatchStatusByAction = {
        PREPARE: "NOT_REQUESTED",
        REVIEW: "SKIPPED",
        BLOCK: "SKIPPED",
        DISPATCH: "SUCCESS",
    } as const;

    return {
        decision: {
            source: "REPORT",
            report: {
                context: {
                    symbol: "EURUSD",
                    side: "SELL",
                    volume: 0.1,
                    sl: 1.092,
                    tp: 1.084,
                    comment: "live-operational-analysis:M5",
                    ticket: null,
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
                ],
                final_recommendation: {
                    recommendation,
                    explanation: "Backend decision recommendation.",
                },
                narrative: "Live bearish context.",
            },
        },
        playbookResult: {
            totalPlaybooks: 1,
            matches: [],
            matchedPlaybooks: [],
            bestMatch: {
                setupId: "setup-1",
                setupName: "London Breakout",
                matched: true,
                matchPercentage: 75,
                matchedConditions: ["Bias == BEARISH"],
                missingConditions: ["Liquidity sweep"],
                explanation: "London Breakout: matched 75% - missing Liquidity sweep",
            },
            bestMatchScore: 75,
            requirementsSatisfied: action !== "BLOCK",
            permitsContinuation: action === "PREPARE" || action === "DISPATCH",
            reasons: action === "REVIEW" ? ["Recommendation is WAIT"] : action === "BLOCK" ? ["Recommendation is NO_TRADE"] : [],
        },
        executionPreparation: {
            request: {
                symbol: "EURUSD",
                side: "SELL",
                entry_price: 1.089,
                stop_loss: 1.092,
                take_profit: 1.084,
                risk_percent: 0.45,
                account_balance: null,
                spread: null,
                pip_value: null,
                tick_value: null,
                leverage: null,
                contract_size: null,
                min_rr: 2,
                max_risk_percent: 2,
                max_spread: 2.5,
                min_lot: 0.01,
                max_lot: 100,
                margin_buffer: 0.7,
            },
            result: {
                symbol: "EURUSD",
                side: "SELL",
                entry: 1.089,
                stop_loss: 1.092,
                take_profit: 1.084,
                lot_size: 0.1,
                risk_percent: 0.45,
                risk_money: 45,
                reward_money: 90,
                risk_pips: 30,
                reward_pips: 60,
                rr: 2,
                pip_value: 10,
                tick_value: 1,
                margin_required: 120,
                spread: 2,
                validation_results: [],
                institutional_score: 78,
                execution_status: action === "BLOCK" ? "BLOCKED" : action === "REVIEW" ? "REVIEW" : "READY",
            },
            missingRequiredFields: action === "REVIEW" ? ["price"] : [],
            validationFailures: action === "BLOCK" ? ["Execution validation contains failures"] : [],
            validationWarnings: action === "REVIEW" ? ["Execution preparation contains warnings"] : [],
        },
        safetyGate: {
            dispatchRequested: action === "DISPATCH",
            dispatchEnabled: action === "DISPATCH",
            passed: action === "PREPARE" || action === "DISPATCH",
            action,
            reasons: action === "PREPARE" ? [] : action === "REVIEW" ? ["Recommendation is WAIT"] : action === "BLOCK" ? ["Recommendation is NO_TRADE"] : [],
        },
        executionBoundary: {
            attempted: action === "DISPATCH",
            status: dispatchStatusByAction[action],
            tradeResult: action === "DISPATCH" ? {
                success: true,
                ticket: 11001,
                order: null,
                price: 1.089,
                volume: 0.1,
                sl: 1.092,
                tp: 1.084,
                brokerMessage: "Order sent",
                executionTime: 0.31,
                error: null,
            } : null,
            journalEntry: action === "DISPATCH" ? {
                id: "journal-1",
            } : null,
            paperExecution: action === "DISPATCH" ? {
                order: {
                    order_id: "paper-order-1",
                    symbol: "EURUSD",
                    side: "SELL",
                    requested_volume: 0.1,
                    entry_price: 1.089,
                    stop_loss: 1.092,
                    take_profit: 1.084,
                    status: "FILLED",
                    created_at: "2026-08-09T09:30:00Z",
                    filled_at: "2026-08-09T09:30:01Z",
                    decision_reference_id: "decision-1",
                },
                position: {
                    position_id: "paper-position-1",
                    symbol: "EURUSD",
                    side: "SELL",
                    volume: 0.1,
                    entry_price: 1.089,
                    stop_loss: 1.092,
                    take_profit: 1.084,
                    status: "OPEN",
                    opened_at: "2026-08-09T09:30:01Z",
                    updated_at: "2026-08-09T09:30:01Z",
                    originating_order_id: "paper-order-1",
                    close_price: null,
                    closed_at: null,
                    realized_pnl: null,
                    realized_rr: null,
                    last_mark_price: null,
                    last_marked_at: null,
                    unrealized_pnl: null,
                    journal_entry_id: null,
                },
                deterministic_fill_price: 1.089,
                order_status_flow: ["PREPARED", "SUBMITTED", "FILLED"],
            } : null,
        },
        finalAction: action,
        finalStatus: action === "DISPATCH" ? "DISPATCHED" : action === "BLOCK" ? "BLOCKED" : "READY_FOR_REVIEW",
    };
}

describe("TradeTicket", () => {
    it("renders PREPARE response as preparation only", () => {
        render(<TradeTicket ticket={null} bridge={buildBridge("PREPARE") as never} />);

        expect(screen.getByText("PREPARE only creates a validated ticket. It does not execute a trade.")).toBeInTheDocument();
        expect(screen.getByText("Final action: PREPARE · Final status: READY_FOR_REVIEW")).toBeInTheDocument();
    });

    it("renders REVIEW response as manual review state", () => {
        render(<TradeTicket ticket={null} bridge={buildBridge("REVIEW") as never} />);

        expect(screen.getByText("REVIEW means manual confirmation is still required. It is not approval.")).toBeInTheDocument();
        expect(screen.getByText("Recommendation is WAIT")).toBeInTheDocument();
    });

    it("renders BLOCK response as non-dispatchable state", () => {
        render(<TradeTicket ticket={null} bridge={buildBridge("BLOCK") as never} />);

        expect(screen.getByText("BLOCK stops dispatch until backend safety conditions are satisfied.")).toBeInTheDocument();
        expect(screen.getByText("Recommendation is NO_TRADE")).toBeInTheDocument();
    });

    it("renders DISPATCH response and backend dispatch status", () => {
        render(<TradeTicket ticket={null} bridge={buildBridge("DISPATCH") as never} />);

        expect(screen.getByText("DISPATCH reflects backend dispatch state when safety gate permits it.")).toBeInTheDocument();
        expect(screen.getByText("Final action: DISPATCH · Final status: DISPATCHED")).toBeInTheDocument();
        expect(screen.getByText("Journal entry recorded: journal-1")).toBeInTheDocument();
    });

    it("renders safety-gate status details from backend", () => {
        render(<TradeTicket ticket={null} bridge={buildBridge("REVIEW") as never} />);

        expect(screen.getByText("Gate passed: NO · Dispatch requested: NO · Dispatch enabled: NO")).toBeInTheDocument();
        expect(screen.getByText("Recommendation is WAIT")).toBeInTheDocument();
    });

    it("keeps PAPER confirmation disabled for WAIT recommendation", () => {
        render(
            <TradeTicket
                ticket={null}
                bridge={buildBridge("PREPARE", "WAIT") as never}
                canConfirmPaperTrade={false}
                confirmPaperDisabledReason="WAIT decisions cannot be confirmed for paper execution."
            />
        );

        expect(screen.getByRole("button", { name: "CONFIRM PAPER TRADE" })).toBeDisabled();
        expect(screen.getByText("WAIT decisions cannot be confirmed for paper execution.")).toBeInTheDocument();
    });

    it("allows explicit PAPER confirmation when enabled", () => {
        const onConfirm = vi.fn();

        render(
            <TradeTicket
                ticket={null}
                bridge={buildBridge("PREPARE", "SELL") as never}
                canConfirmPaperTrade
                onConfirmPaperTrade={onConfirm}
            />
        );

        fireEvent.click(screen.getByRole("button", { name: "CONFIRM PAPER TRADE" }));
        expect(onConfirm).toHaveBeenCalledTimes(1);
    });

    it("renders paper execution identifiers after successful confirmation", () => {
        render(<TradeTicket ticket={null} bridge={buildBridge("DISPATCH", "SELL") as never} />);

        expect(screen.getByTestId("paper-execution-result")).toHaveTextContent("paper-order-1");
        expect(screen.getByTestId("paper-execution-result")).toHaveTextContent("paper-position-1");
    });
});