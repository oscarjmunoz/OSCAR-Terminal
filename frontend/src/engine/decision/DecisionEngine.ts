import { InstitutionalAnalysis } from "../pipeline/types";
import { getActiveStrategy, getStrategy } from "../strategy/StrategyRegistry";

export function createDecision(analysis: InstitutionalAnalysis, strategyId?: string) {
  const strategy = strategyId ? getStrategy(strategyId) ?? getActiveStrategy() : getActiveStrategy();
  const evaluated = strategy.evaluate(analysis);

  return {
    type: evaluated.decision,
    confidence: evaluated.confidence,
    reason: evaluated.reasons,
  };
}
