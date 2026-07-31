export type IEZDirection = "BULLISH" | "BEARISH" | "NONE";

export type IEZEntryPriority = "HIGH" | "MEDIUM" | "LOW" | "NONE";

export interface InstitutionalEntryZone {
  valid: boolean;
  direction: IEZDirection;
  entryZoneLow: number | null;
  entryZoneHigh: number | null;
  currentPrice: number;
  inZone: boolean;
  discountForLong: boolean;
  premiumForShort: boolean;
  fvgConfluence: boolean;
  obConfluence: boolean;
  liquidityContextAligned: boolean;
  mssAligned: boolean;
  timeframeAligned: boolean;
  iezScore: number;
  entryPriority: IEZEntryPriority;
  qualityScore: number;
  passedRules: string[];
  failedRules: string[];
  reasons: string[];
  warnings: string[];
}
