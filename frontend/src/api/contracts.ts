export type DecisionSide = "BUY" | "SELL";

export interface DecisionContext {
    symbol: string;
    side: DecisionSide;
    volume: number;
    sl: number | null;
    tp: number | null;
    comment: string | null;
    ticket?: number | null;
    price?: number | null;
}

export interface DecisionChecklistItem {
    label: string;
    checked: boolean;
    explanation: string;
}

export interface DecisionConfluence {
    name: string;
    detected: boolean;
    importance: "HIGH" | "MEDIUM" | "LOW";
    explanation: string;
}

export interface DecisionMultiTimeframeBiasItem {
    timeframe: string;
    bias: string;
    bos: boolean;
    choch: boolean;
    mss: boolean;
    structure_confidence: string;
    data_availability: string;
    explanation: string;
}

export interface DecisionMultiTimeframeBias {
    h4: DecisionMultiTimeframeBiasItem;
    h1: DecisionMultiTimeframeBiasItem;
    m5: DecisionMultiTimeframeBiasItem;
    alignment: string;
    conflict: boolean;
    confidence: string;
    summary: string;
}

export interface DecisionSnapshot {
    bias: {
        bias: string;
        explanation: string;
    };
    score: number;
    confidence: number;
    liquidity: {
        buy_liquidity: number;
        sell_liquidity: number;
        liquidity_taken: number;
        pending_liquidity: number;
        explanation: string;
    };
    structure: {
        trend: string;
        bos: boolean;
        choch: boolean;
        mss: boolean;
        explanation: string;
    };
    zones: {
        order_block: { active: boolean; explanation: string };
        breaker: { active: boolean; explanation: string };
        mitigation: { active: boolean; explanation: string };
        fvg: { active: boolean; explanation: string };
        premium: { active: boolean; explanation: string };
        discount: { active: boolean; explanation: string };
    };
    confluences: DecisionConfluence[];
    checklist: DecisionChecklistItem[];
    recommendation: {
        recommendation: string;
        explanation: string;
    };
    narrative: string;
    multi_timeframe_bias?: DecisionMultiTimeframeBias;
}
