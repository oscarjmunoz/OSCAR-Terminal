export type InstitutionalDecisionDirection = "BULLISH" | "BEARISH" | "NONE";

export type InstitutionalDecisionState = "VALID_LONG" | "VALID_SHORT" | "INVALID";

export type InstitutionalDecisionStatus = "PASS" | "FAIL" | "WAIT" | "WARNING" | "READY";

export type InstitutionalFailedAt = "Context" | "Liquidity" | "PremiumDiscount" | "MSS" | "Confluence" | "Score" | "Decision" | "NONE";

export interface InstitutionalDecisionResult {
    valid: boolean;
    decisionState: InstitutionalDecisionState;
    direction: InstitutionalDecisionDirection;
    institutionalScore: number;
    confidence: number;
    blockedBy: string[];
    failedAt: InstitutionalFailedAt;
    criticalFailure: string;
    engineSequence: string[];
    summary: string;
    status: InstitutionalDecisionStatus;
    reasons: string[];
    warnings: string[];
    passedRules: string[];
    failedRules: string[];
    executionTime: number;
}
