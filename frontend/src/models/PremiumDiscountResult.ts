export type PremiumDiscountZone = "PREMIUM" | "DISCOUNT" | "EQUILIBRIUM" | "UNKNOWN";

export interface PremiumDiscountResult {
  valid: boolean;
  zone: PremiumDiscountZone;
  currentPrice: number;
  rangeHigh: number;
  rangeLow: number;
  equilibrium: number;
  distanceToEquilibrium: number;
  inPremium: boolean;
  inDiscount: boolean;
  inEquilibrium: boolean;
  biasAligned: boolean;
  passedRules: string[];
  failedRules: string[];
  reasons: string[];
  warnings: string[];
}
