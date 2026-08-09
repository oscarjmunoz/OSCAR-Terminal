import { api } from "./client";

export interface PerformanceReport {
    totalTrades: number;
    wins: number;
    losses: number;
    breakEven: number;
    cancelled: number;
    winRate: number;
    averageRR: number;
    averageProfit: number;
    averageLoss: number;
    expectancy: number;
    profitFactor: number;
}

export interface SessionAnalytics {
    session: string;
    trades: number;
    winRate: number;
    averageRR: number;
    averageDuration: number;
}

export interface BehaviourAnalytics {
    recommendation: string;
    trades: number;
    winRate: number;
    averageRR: number;
    profitFactor: number;
}

export interface SetupAnalytics {
    setupId: string;
    setupName: string;
    totalTrades: number;
    winRate: number;
    averageRR: number;
    expectancy: number;
}

export async function getAnalyticsPerformance(): Promise<PerformanceReport> {

    const response = await api.get<PerformanceReport>(
        "/analytics/performance"
    );

    return response.data;

}

export async function getAnalyticsSessions(): Promise<SessionAnalytics[]> {

    const response = await api.get<SessionAnalytics[]>(
        "/analytics/sessions"
    );

    return response.data;

}

export async function getAnalyticsBehaviour(): Promise<BehaviourAnalytics[]> {

    const response = await api.get<BehaviourAnalytics[]>(
        "/analytics/behaviour"
    );

    return response.data;

}

export async function getAnalyticsSetups(): Promise<SetupAnalytics[]> {

    const response = await api.get<SetupAnalytics[]>(
        "/analytics/setups"
    );

    return response.data;

}