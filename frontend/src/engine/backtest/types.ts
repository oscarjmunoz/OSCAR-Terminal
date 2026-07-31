import { CandleResponse } from "../../api/market";
import { ValidationRecord } from "../validation/types";

export interface BacktestConfig {
  takeProfitR: number;
  stopLossR: number;
  minRisk: number;
}

export interface BacktestTradeResult {
  record: ValidationRecord;
  entryIndex: number;
  exitIndex: number;
  entryPrice: number;
  exitPrice: number;
  outcome: "WIN" | "LOSS";
  rr: number;
}

export interface BacktestResult {
  totalSignals: number;
  wins: number;
  losses: number;
  winRate: number;
  profitFactor: number;
  expectancy: number;
  averageRR: number;
  equityCurve: number[];
}

export interface BacktestInput {
  records: ValidationRecord[];
  candles: CandleResponse[];
  config?: Partial<BacktestConfig>;
}

export interface JournalBacktestPayload {
  summary: BacktestResult;
  trades: BacktestTradeResult[];
}

export interface DashboardBacktestPayload {
  summary: BacktestResult;
  equityCurve: number[];
}

export interface ReportingBacktestPayload {
  summary: BacktestResult;
  trades: BacktestTradeResult[];
  candles: CandleResponse[];
}

export interface AIBacktestPayload {
  summary: BacktestResult;
  trades: BacktestTradeResult[];
}
