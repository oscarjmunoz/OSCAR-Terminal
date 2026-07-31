import { CandleResponse } from "../../api/market";
import { InstitutionalAnalysis } from "../pipeline/types";

export interface ValidationRecord {
  timestamp: number;
  symbol: string;
  timeframe: string;
  score: number;
  decision: "BUY" | "SELL" | "WAIT" | "NO TRADE";
  confidence: number;
}

export interface ValidationEngineInput {
  analysis: InstitutionalAnalysis;
  candles: CandleResponse[];
  symbol?: string;
  timeframe?: string;
  timestamp?: number;
}

export interface ValidationBatch {
  records: ValidationRecord[];
  source: "INSTITUTIONAL_PIPELINE";
}

export interface JournalValidationPayload {
  symbol: string;
  timeframe: string;
  records: ValidationRecord[];
}

export interface BacktesterValidationPayload {
  records: ValidationRecord[];
  candles: CandleResponse[];
}
