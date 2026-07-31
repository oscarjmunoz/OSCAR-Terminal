import { CandleResponse, TerminalStatus, TickResponse } from "../api/market";
import { MarketStructure } from "../api/smartMoney";
import { JournalEntry } from "../engine/journal/types";
import { MultiTimeframeAnalysis, TimeframeName } from "../engine/mtf/types";
import { InstitutionalAnalysis } from "../engine/pipeline/types";

export type SupportedSymbol =
  | "USDCHF.pro"
  | "EURUSD"
  | "XAUUSD"
  | "NAS100"
  | "US30"
  | string;

export interface TimeframeSnapshot {
  candles: CandleResponse[];
  structure: MarketStructure | null;
}

export interface MarketSnapshot {
  symbol: string;
  tick: TickResponse | null;
  status: TerminalStatus | null;
  timeframes: Record<TimeframeName, TimeframeSnapshot>;
  timestamp: number;
}

export interface OrchestratorConfig {
  candleCount: number;
}

export interface LiveDataSource {
  fetchTick(symbol: string): Promise<TickResponse>;
  fetchStatus(): Promise<TerminalStatus>;
  fetchCandles(symbol: string, timeframe: TimeframeName, count: number): Promise<CandleResponse[]>;
  fetchStructure(symbol: string, timeframe: TimeframeName, count: number): Promise<MarketStructure>;
}

export interface OrchestratedEngineOutput {
  snapshot: MarketSnapshot;
  institutional: Record<TimeframeName, InstitutionalAnalysis>;
  mtf: MultiTimeframeAnalysis;
  journalEntries: JournalEntry[];
}

export type ExplainableRiskLevel = "Low" | "Medium" | "High";

export interface ExplainableDecisionOutput {
  decision: "BUY" | "SELL" | "WAIT";
  confidence: number;
  score: number;
  reasons: string[];
  risk: ExplainableRiskLevel;
  invalidation: string;
  expectedRR: string;
  strategy: string;
}
