import { api } from "./client";
import type { LiveDecisionReport } from "./decision";

export interface PlaybookSetupStatistics {
    setupId: string;
    setupName: string;
    totalTrades: number;
    wins: number;
    losses: number;
    breakEven: number;
    cancelled: number;
    winRate: number;
    averageRR: number;
    averageDuration: number;
}

export interface PlaybookSetup {
    id: string;
    name: string;
    description: string;
    category: string;
    enabled: boolean;
    createdAt: string;
    updatedAt: string;
}

export interface PlaybookMatch {
    setupId: string;
    setupName: string;
    matched: boolean;
    matchPercentage: number;
    matchedConditions: string[];
    missingConditions: string[];
    explanation: string;
}

export async function getPlaybookStatistics(): Promise<PlaybookSetupStatistics[]> {

    const response = await api.get<PlaybookSetupStatistics[]>(
        "/playbook/statistics"
    );

    return response.data;

}

export async function getPlaybookSetups(): Promise<PlaybookSetup[]> {

    const response = await api.get<PlaybookSetup[]>(
        "/playbook"
    );

    return response.data;

}

export async function evaluatePlaybookMatches(decisionReport: LiveDecisionReport): Promise<PlaybookMatch[]> {

    const response = await api.post<PlaybookMatch[]>(
        "/playbook/evaluate",
        {
            decisionReport,
        }
    );

    return response.data;

}