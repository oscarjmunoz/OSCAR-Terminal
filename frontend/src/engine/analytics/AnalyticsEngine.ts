import { BacktestResult } from "../backtest/types";
import { JournalEntry } from "../journal/types";
import {
  AnalyticsInput,
  AnalyticsReport,
  AnalyticsStat,
  AnalyticsSummary,
  SessionLabel,
} from "./types";

function normalizeTimestamp(timestamp: number): number {
  return timestamp > 10_000_000_000 ? Math.floor(timestamp / 1000) : timestamp;
}

function toSessionLabel(timestamp: number): SessionLabel {
  const seconds = normalizeTimestamp(timestamp);
  const hour = new Date(seconds * 1000).getUTCHours();

  if (hour >= 0 && hour < 8) {
    return "ASIA";
  }

  if (hour >= 8 && hour < 16) {
    return "LONDON";
  }

  if (hour >= 16 && hour < 22) {
    return "NEW_YORK";
  }

  return "CLOSED";
}

function round(value: number, decimals = 2): number {
  const factor = 10 ** decimals;
  return Math.round(value * factor) / factor;
}

function computeRates(wins: number, losses: number): { winRate: number; lossRate: number } {
  const resolved = wins + losses;
  if (!resolved) {
    return { winRate: 0, lossRate: 0 };
  }

  return {
    winRate: round((wins / resolved) * 100),
    lossRate: round((losses / resolved) * 100),
  };
}

function computeProfitFactor(wins: number, losses: number): number {
  if (losses === 0) {
    return wins > 0 ? Number.POSITIVE_INFINITY : 0;
  }

  return round(wins / losses, 4);
}

function computeExpectancy(wins: number, losses: number): number {
  const resolved = wins + losses;
  if (!resolved) {
    return 0;
  }

  return round((wins - losses) / resolved, 4);
}

function aggregateStat(key: string, entries: JournalEntry[]): AnalyticsStat {
  const wins = entries.filter((entry) => entry.status === "WIN").length;
  const losses = entries.filter((entry) => entry.status === "LOSS").length;
  const totalSignals = entries.length;

  const confidenceSum = entries.reduce((sum, entry) => sum + entry.confidence, 0);
  const scoreSum = entries.reduce((sum, entry) => sum + entry.score, 0);

  const rates = computeRates(wins, losses);

  return {
    key,
    totalSignals,
    wins,
    losses,
    winRate: rates.winRate,
    lossRate: rates.lossRate,
    averageConfidence: totalSignals ? round(confidenceSum / totalSignals) : 0,
    averageOscarScore: totalSignals ? round(scoreSum / totalSignals) : 0,
    profitFactor: computeProfitFactor(wins, losses),
    expectancy: computeExpectancy(wins, losses),
  };
}

function groupBy(entries: JournalEntry[], selector: (entry: JournalEntry) => string): Map<string, JournalEntry[]> {
  return entries.reduce((acc, entry) => {
    const key = selector(entry);
    const current = acc.get(key) ?? [];
    current.push(entry);
    acc.set(key, current);
    return acc;
  }, new Map<string, JournalEntry[]>());
}

function mapGroupStats(groups: Map<string, JournalEntry[]>): AnalyticsStat[] {
  return Array.from(groups.entries())
    .map(([key, entries]) => aggregateStat(key, entries))
    .sort((a, b) => b.totalSignals - a.totalSignals);
}

function summaryFromBacktests(backtestResults: BacktestResult[]): Pick<AnalyticsSummary, "profitFactor" | "expectancy"> {
  if (!backtestResults.length) {
    return { profitFactor: 0, expectancy: 0 };
  }

  const totalSignals = backtestResults.reduce((sum, item) => sum + item.totalSignals, 0);

  if (!totalSignals) {
    return { profitFactor: 0, expectancy: 0 };
  }

  const weightedProfitFactor = backtestResults.reduce(
    (sum, item) => sum + (Number.isFinite(item.profitFactor) ? item.profitFactor : 0) * item.totalSignals,
    0
  );
  const weightedExpectancy = backtestResults.reduce(
    (sum, item) => sum + item.expectancy * item.totalSignals,
    0
  );

  return {
    profitFactor: round(weightedProfitFactor / totalSignals, 4),
    expectancy: round(weightedExpectancy / totalSignals, 4),
  };
}

export function buildAnalyticsReport(input: AnalyticsInput): AnalyticsReport {
  const entries = input.journalEntries;

  const totalSignals = entries.length;
  const wins = entries.filter((entry) => entry.status === "WIN").length;
  const losses = entries.filter((entry) => entry.status === "LOSS").length;

  const rates = computeRates(wins, losses);
  const confidenceSum = entries.reduce((sum, entry) => sum + entry.confidence, 0);
  const scoreSum = entries.reduce((sum, entry) => sum + entry.score, 0);

  const backtestSummary = summaryFromBacktests(input.backtestResults);

  const summary: AnalyticsSummary = {
    totalSignals,
    winRate: rates.winRate,
    lossRate: rates.lossRate,
    profitFactor: backtestSummary.profitFactor || computeProfitFactor(wins, losses),
    expectancy: backtestSummary.expectancy || computeExpectancy(wins, losses),
    averageConfidence: totalSignals ? round(confidenceSum / totalSignals) : 0,
    averageOscarScore: totalSignals ? round(scoreSum / totalSignals) : 0,
  };

  const strategyStats = mapGroupStats(groupBy(entries, (entry) => entry.strategy || "UNKNOWN"));
  const timeframeStats = mapGroupStats(groupBy(entries, (entry) => entry.timeframe || "UNKNOWN"));
  const sessionStats = mapGroupStats(groupBy(entries, (entry) => toSessionLabel(entry.timestamp)));
  const symbolStats = mapGroupStats(groupBy(entries, (entry) => entry.symbol || "UNKNOWN"));

  return {
    summary,
    strategyStats,
    timeframeStats,
    sessionStats,
    symbolStats,
  };
}
