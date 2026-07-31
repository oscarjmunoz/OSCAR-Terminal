export type LiquiditySide = "BSL" | "SSL" | "NONE";

export type ContextBlockType = "BULLISH" | "BEARISH" | "NONE";

export interface ContextLiquidityTaken {
  timeframe: "H4";
  valid: boolean;
  side: LiquiditySide;
  level: number | null;
}

export interface ContextOrderBlock {
  timeframe: "H1";
  valid: boolean;
  blockType: ContextBlockType;
  low: number | null;
  high: number | null;
}

export interface ContextFairValueGap {
  timeframe: "H1";
  valid: boolean;
  gapType: ContextBlockType;
  low: number | null;
  high: number | null;
}

export interface ContextResult {
  valid: boolean;
  contextScore: number;
  reasons: string[];
  warnings: string[];
  liquidityTaken: ContextLiquidityTaken;
  orderBlock: ContextOrderBlock;
  fairValueGap: ContextFairValueGap;
}
