import { api } from "./client";
import type { DecisionChecklistItem, DecisionConfluence, DecisionSnapshot } from "./contracts";

export type { DecisionChecklistItem, DecisionConfluence, DecisionSnapshot } from "./contracts";

export interface DecisionConfluenceItem extends DecisionConfluence { }

export interface DecisionSnapshotView extends DecisionSnapshot { }

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
    decisionSnapshot: DecisionSnapshotView;
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