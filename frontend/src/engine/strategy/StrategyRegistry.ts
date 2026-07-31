import { Strategy } from "./Strategy";
import { ICTStrategy } from "./ICTStrategy";

class StrategyRegistry {
  private strategies = new Map<string, Strategy>();
  private activeStrategyId = "ict";

  register(strategy: Strategy): void {
    this.strategies.set(strategy.id, strategy);
  }

  get(strategyId: string): Strategy | undefined {
    return this.strategies.get(strategyId);
  }

  getActive(): Strategy {
    const strategy = this.strategies.get(this.activeStrategyId);
    if (!strategy) {
      throw new Error(`Active strategy '${this.activeStrategyId}' is not registered.`);
    }

    return strategy;
  }

  setActive(strategyId: string): void {
    if (!this.strategies.has(strategyId)) {
      throw new Error(`Strategy '${strategyId}' is not registered.`);
    }

    this.activeStrategyId = strategyId;
  }

  list(): Strategy[] {
    return Array.from(this.strategies.values());
  }
}

const registry = new StrategyRegistry();
registry.register(new ICTStrategy());

export function registerStrategy(strategy: Strategy): void {
  registry.register(strategy);
}

export function getStrategy(strategyId: string): Strategy | undefined {
  return registry.get(strategyId);
}

export function getActiveStrategy(): Strategy {
  return registry.getActive();
}

export function setActiveStrategy(strategyId: string): void {
  registry.setActive(strategyId);
}

export function listStrategies(): Strategy[] {
  return registry.list();
}
