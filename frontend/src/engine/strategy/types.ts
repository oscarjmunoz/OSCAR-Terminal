import { DecisionType } from "../pipeline/types";

export interface StrategyDecision {
  decision: DecisionType;
  confidence: number;
  reasons: string[];
}
