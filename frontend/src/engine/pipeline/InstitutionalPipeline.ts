import { TerminalStatus, TickResponse } from "../../api/market";
import { MarketStructure } from "../../api/smartMoney";
import { createMarketContext } from "../context/MarketContextEngine";
import { createLiquidityLevels } from "../liquidity/LiquidityEngine";
import { calculateOscarScore } from "../oscarScore";
import {
  DecisionState,
  FairValueGapState,
  InstitutionalAnalysis,
  OrderBlockState,
  PipelineInput,
  PremiumDiscountState,
} from "./types";

function createOrderBlocksPlaceholder(): OrderBlockState[] {
  return [{ type: "PLACEHOLDER", value: "Pending implementation" }];
}

function createFairValueGapsPlaceholder(): FairValueGapState[] {
  return [{ type: "PLACEHOLDER", value: "Pending implementation" }];
}

function createPremiumDiscountPlaceholder(): PremiumDiscountState[] {
  return [{ type: "PLACEHOLDER", value: "Pending implementation" }];
}

function createDecisionPlaceholder(): DecisionState[] {
  return [{ type: "PLACEHOLDER", value: "Pending implementation" }];
}

export function runInstitutionalPipeline(input: PipelineInput): InstitutionalAnalysis {
  const { structure, tick, status, candles } = input;

  const liquidity = createLiquidityLevels(candles as Array<{ time: string; open: number; high: number; low: number; close: number }>, [], {
    currentPrice: tick?.ask ?? tick?.bid,
  });

  const context = createMarketContext({
    structure,
    liquidityLevels: liquidity,
    tick,
    status,
  });

  const score = calculateOscarScore(structure, tick, status);

  return {
    structure,
    liquidity,
    context,
    orderBlocks: createOrderBlocksPlaceholder(),
    fairValueGaps: createFairValueGapsPlaceholder(),
    premiumDiscount: createPremiumDiscountPlaceholder(),
    score,
    decision: createDecisionPlaceholder()[0] as DecisionState | null,
  };
}
