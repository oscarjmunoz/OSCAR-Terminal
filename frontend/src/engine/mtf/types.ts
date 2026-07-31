import { InstitutionalAnalysis } from "../pipeline/types";

export type TimeframeName = "H4" | "H1" | "M15" | "M5";

export interface TimeframeAnalysis {
  timeframe: TimeframeName;
  structure: InstitutionalAnalysis["structure"];
  liquidity: InstitutionalAnalysis["liquidity"];
  context: InstitutionalAnalysis["context"];
  score: InstitutionalAnalysis["score"];
  decision: InstitutionalAnalysis["decision"];
}

export interface MultiTimeframeAnalysis {
  H4: TimeframeAnalysis;
  H1: TimeframeAnalysis;
  M15: TimeframeAnalysis;
  M5: TimeframeAnalysis;
  alignment: number;
  globalBias: "LONG" | "SHORT" | "NEUTRAL";
}
