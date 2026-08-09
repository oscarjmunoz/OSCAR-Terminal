import { beforeEach, describe, expect, it, vi } from "vitest";
import axios from "axios";

vi.mock("./client", () => ({
    api: {
        post: vi.fn(),
    },
}));

import { api } from "./client";
import { executeDecisionBridge } from "./decisionExecution";

describe("decision execution bridge client", () => {
    beforeEach(() => {
        vi.mocked(api.post).mockReset();
    });

    it("posts decision report to /decision/execute and returns PREPARE response", async () => {
        const payload = {
            decisionReport: {
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
                    recommendation: "WAIT",
                    explanation: "Context is bearish, but execution still requires confirmation.",
                },
                narrative: "Live bearish context with partial confluence. Decision remains with the trader.",
            },
            dispatch: false,
            timeframe: "M5",
        } as const;

        vi.mocked(api.post).mockResolvedValueOnce({
            data: {
                decision: {
                    source: "REPORT",
                    report: payload.decisionReport,
                },
                playbookResult: {
                    totalPlaybooks: 1,
                    matches: [],
                    matchedPlaybooks: [],
                    bestMatch: null,
                    bestMatchScore: 0,
                    requirementsSatisfied: true,
                    permitsContinuation: true,
                    reasons: [],
                },
                executionPreparation: {
                    request: null,
                    result: null,
                    missingRequiredFields: [],
                    validationFailures: [],
                    validationWarnings: [],
                },
                safetyGate: {
                    dispatchRequested: false,
                    dispatchEnabled: false,
                    passed: true,
                    action: "PREPARE",
                    reasons: [],
                },
                executionBoundary: {
                    attempted: false,
                    status: "NOT_REQUESTED",
                    tradeResult: null,
                    journalEntry: null,
                },
                finalAction: "PREPARE",
                finalStatus: "READY_FOR_REVIEW",
            },
        } as never);

        const result = await executeDecisionBridge(payload);

        expect(api.post).toHaveBeenCalledWith("/decision/execute", payload);
        expect(result.finalAction).toBe("PREPARE");
        expect(result.safetyGate.action).toBe("PREPARE");
    });

    it("propagates backend API errors without frontend-side fallback calculation", async () => {
        const error = axios.AxiosError.from(new Error("Request failed"));
        vi.mocked(api.post).mockRejectedValueOnce(error as never);

        await expect(executeDecisionBridge({
            decisionContext: {
                symbol: "EURUSD",
                side: "BUY",
                volume: 0.1,
            },
        })).rejects.toBe(error);
    });

    it("sends explicit PAPER confirmation payload without forcing dispatch", async () => {
        const payload = {
            decisionContext: {
                symbol: "EURUSD",
                side: "SELL",
                volume: 0.1,
            },
            executionMode: "PAPER",
            confirmed: true,
            timeframe: "M5",
        } as const;

        vi.mocked(api.post).mockResolvedValueOnce({
            data: {
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
                        confluences: [],
                        risk_assessment: {
                            rr_expected: 2.1,
                            risk: "LOW",
                            risk_percent: 0.45,
                            volatility: 12.4,
                            setup_quality: "A",
                        },
                        execution_checklist: [],
                        final_recommendation: {
                            recommendation: "SELL",
                            explanation: "Tradable setup.",
                        },
                        narrative: "Live bearish context.",
                    },
                },
                playbookResult: {
                    totalPlaybooks: 0,
                    matches: [],
                    matchedPlaybooks: [],
                    bestMatch: null,
                    bestMatchScore: 0,
                    requirementsSatisfied: true,
                    permitsContinuation: true,
                    reasons: [],
                },
                executionPreparation: {
                    request: null,
                    result: null,
                    missingRequiredFields: [],
                    validationFailures: [],
                    validationWarnings: [],
                },
                safetyGate: {
                    dispatchRequested: false,
                    dispatchEnabled: false,
                    passed: true,
                    action: "PREPARE",
                    reasons: [],
                },
                executionBoundary: {
                    executionMode: "PAPER",
                    attempted: true,
                    status: "SUCCESS",
                    tradeResult: null,
                    journalEntry: null,
                    paperExecution: null,
                },
                finalAction: "DISPATCH",
                finalStatus: "DISPATCHED",
            },
        } as never);

        await executeDecisionBridge(payload);

        expect(api.post).toHaveBeenCalledWith("/decision/execute", payload);
        expect(vi.mocked(api.post).mock.calls[0][1]).not.toHaveProperty("dispatch");
    });
});