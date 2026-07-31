export type StructureTrend = "BULLISH" | "BEARISH" | "RANGE" | "UNKNOWN";

export type StructureBreakDirection = "BULLISH" | "BEARISH" | "NONE";

export type SwingImportance = "MAJOR" | "MINOR" | "INTERNAL";

export interface MarketStructureResult {
  valid: boolean;
  trend: StructureTrend;
  breakDirection: StructureBreakDirection;
  swingHigh: number | null;
  swingLow: number | null;
  bos: boolean;
  choch: boolean;
  mss: boolean;
  liquiditySweep: boolean;
  displacement: boolean;
  timeframeAligned: boolean;
  swingImportance: SwingImportance;
  passedRules: string[];
  failedRules: string[];
  reasons: string[];
  warnings: string[];
}
