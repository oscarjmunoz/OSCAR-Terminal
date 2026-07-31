import { BacktestResult } from "../backtest/types";
import { JournalEntry } from "../journal/types";

export type SessionLabel = "ASIA" | "LONDON" | "NEW_YORK" | "CLOSED";

export interface AnalyticsSummary {
  totalSignals: number;
  winRate: number;
  lossRate: number;
  profitFactor: number;
  expectancy: number;
  averageConfidence: number;
  averageOscarScore: number;
}

export interface AnalyticsStat {
  key: string;
  totalSignals: number;
  wins: number;
  losses: number;
  winRate: number;
  lossRate: number;
  averageConfidence: number;
  averageOscarScore: number;
  profitFactor: number;
  expectancy: number;
}

export interface AnalyticsReport {
  summary: AnalyticsSummary;
  strategyStats: AnalyticsStat[];
  timeframeStats: AnalyticsStat[];
  sessionStats: AnalyticsStat[];
  symbolStats: AnalyticsStat[];
}

export interface AnalyticsInput {
  journalEntries: JournalEntry[];
  backtestResults: BacktestResult[];
}

export interface DashboardAnalyticsPayload {
  report: AnalyticsReport;
}

export interface JournalAnalyticsPayload {
  report: AnalyticsReport;
  entries: JournalEntry[];
}

export interface StrategyOptimizerPayload {
  report: AnalyticsReport;
}
