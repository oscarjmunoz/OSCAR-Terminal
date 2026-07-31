export type LiquidityType = "BSL" | "SSL" | "EQH" | "EQL";

export interface LiquidityLevel {
  type: LiquidityType;
  price: number;
  index: number;
  strength: number;
}

export interface LiquidityEngineOptions {
  tolerance?: number;
  currentPrice?: number;
}
