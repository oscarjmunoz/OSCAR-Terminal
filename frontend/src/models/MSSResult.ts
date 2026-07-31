export type MSSDirection = "BULLISH" | "BEARISH" | "NONE";

export interface MSSResult {
  valid: boolean;
  direction: MSSDirection;
  brokenStructureLevel: number | null;
  liquiditySweep: boolean;
  displacement: boolean;
  fvgCreated: boolean;
  biasAligned: boolean;
  passedRules: string[];
  failedRules: string[];
  reasons: string[];
  warnings: string[];
}
