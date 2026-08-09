import { api } from "./client";
import type { DecisionChecklistItem, DecisionConfluence, DecisionContext, DecisionMultiTimeframeBias, DecisionSnapshot } from "./contracts";

export type { DecisionChecklistItem, DecisionConfluence, DecisionContext, DecisionMultiTimeframeBias, DecisionSnapshot } from "./contracts";

export interface LiveDecisionReport extends DecisionSnapshot {
    context: DecisionContext;
    market_bias: {
        bias: string;
        explanation: string;
    };
    institutional_score: {
        score: number;
        confidence: number;
        quality_level: string;
    };
    liquidity: {
        buy_liquidity: number;
        sell_liquidity: number;
        liquidity_taken: number;
        pending_liquidity: number;
        explanation: string;
    };
    market_structure: {
        trend: string;
        bos: boolean;
        choch: boolean;
        mss: boolean;
        explanation: string;
    };
    institutional_zones: {
        order_block: { active: boolean; explanation: string };
        breaker: { active: boolean; explanation: string };
        mitigation: { active: boolean; explanation: string };
        fvg: { active: boolean; explanation: string };
        premium: { active: boolean; explanation: string };
        discount: { active: boolean; explanation: string };
    };
    confluences: DecisionConfluence[];
    risk_assessment: {
        rr_expected: number;
        risk: string;
        risk_percent: number;
        volatility: number;
        setup_quality: string;
    };
    execution_checklist: DecisionChecklistItem[];
    final_recommendation: {
        recommendation: string;
        explanation: string;
    };
    narrative: string;
    multi_timeframe_bias?: DecisionMultiTimeframeBias;
}

export async function getLiveDecisionReport(symbol: string, timeframe: string): Promise<LiveDecisionReport> {
    const response = await api.post<LiveDecisionReport>(
        "/decision/live-report",
        {
            symbol,
            timeframe,
        },
    );

    return response.data;
}
