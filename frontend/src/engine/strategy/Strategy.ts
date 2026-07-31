import { InstitutionalAnalysis } from "../pipeline/types";
import { StrategyDecision } from "./types";

export interface Strategy {
  id: string;
  name: string;
  description: string;
  evaluate(analysis: InstitutionalAnalysis): StrategyDecision;
}
