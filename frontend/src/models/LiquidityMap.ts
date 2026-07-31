export type LiquidityLevelName =
  | "PDH"
  | "PDL"
  | "PWH"
  | "PWL"
  | "H4_SWING_HIGH"
  | "H4_SWING_LOW";

export type LiquiditySide = "BSL" | "SSL";

export interface LiquidityLevel {
  name: LiquidityLevelName;
  side: LiquiditySide;
  level: number;
  distance: number;
  taken: boolean;
}

export interface LiquidityTakenSummary {
  buySideTaken: string[];
  sellSideTaken: string[];
}

export interface LiquidityMap {
  pdh: LiquidityLevel;
  pdl: LiquidityLevel;
  pwh: LiquidityLevel;
  pwl: LiquidityLevel;
  h4SwingHigh: LiquidityLevel;
  h4SwingLow: LiquidityLevel;
  liquidityTaken: LiquidityTakenSummary;
  nearestBuySideLiquidity: LiquidityLevel;
  nearestSellSideLiquidity: LiquidityLevel;
}
