export type ScannerDecision = "BUY" | "SELL" | "WAIT";

export interface ScannerItem {
  symbol: string;
  decision: ScannerDecision;
  score: number;
  confidence: number;
  trend: string;
  timeframe: string;
  strategy: string;
}
