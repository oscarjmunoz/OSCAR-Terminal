import { api } from "./client";

export interface DecisionChecklistItem {
    label: string;
    checked: boolean;
    explanation: string;
}

export interface DecisionConfluenceItem {
    name: string;
    detected: boolean;
    importance: string;
    explanation: string;
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
    confluences: DecisionConfluenceItem[];
    checklist: DecisionChecklistItem[];
    recommendation: {
        recommendation: string;
        explanation: string;
    };
    narrative: string;
}

export interface JournalEntry {
    id: string;
    createdAt: string;
    symbol: string;
    timeframe: string;
    session: string;
    entryPrice: number;
    stopLoss: number;
    takeProfit: number;
    positionSize: number;
    riskPercent: number;
    expectedRR: number;
    decisionSnapshot: DecisionSnapshot;
    traderDecision: string;
    tradeOutcome: string;
    profitLoss?: number | null;
    realizedRR?: number | null;
    durationMinutes?: number | null;
    closeReason?: string | null;
    personalNotes: string;
    tags: string[];
}

export async function getJournalEntries(): Promise<JournalEntry[]> {

    const response = await api.get<JournalEntry[]>(
        "/journal"
    );

    return response.data;

}