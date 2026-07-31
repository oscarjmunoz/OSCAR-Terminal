import { MarketSnapshot } from "../../core/types";
import { DecisionType, InstitutionalAnalysis } from "../pipeline/types";

export type JournalEntryStatus = "PENDING" | "WIN" | "LOSS" | "CANCELLED";

export interface JournalEntry {
  id: string;
  timestamp: number;
  symbol: string;
  timeframe: string;
  strategy: string;
  marketSnapshot: MarketSnapshot;
  institutionalAnalysis: InstitutionalAnalysis;
  decision: DecisionType;
  confidence: number;
  score: number;
  reasons: string[];
  status: JournalEntryStatus;
}

export interface CreateJournalEntryInput {
  symbol: string;
  timeframe: string;
  strategy: string;
  marketSnapshot: MarketSnapshot;
  institutionalAnalysis: InstitutionalAnalysis;
}

export interface UpdateJournalEntryInput {
  id: string;
  status?: JournalEntryStatus;
  confidence?: number;
  score?: number;
  reasons?: string[];
}

export interface ReplayJournalPayload {
  entries: JournalEntry[];
}

export interface BacktestJournalPayload {
  entries: JournalEntry[];
}

export interface ScannerJournalPayload {
  latest: JournalEntry | null;
}

export interface DashboardJournalPayload {
  entries: JournalEntry[];
  latest: JournalEntry | null;
}
