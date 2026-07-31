import { TerminalStatus, TickResponse } from "../../api/market";
import { MarketStructure } from "../../api/smartMoney";
import { createMarketContext } from "../context/MarketContextEngine";
import { createDecision } from "../decision/DecisionEngine";
import { createFairValueGaps } from "../fairvalue/FairValueGapEngine";
import { createLiquidityLevels } from "../liquidity/LiquidityEngine";
import { createOrderBlocks } from "../orderblocks/OrderBlockEngine";
import { createPremiumDiscount } from "../premium/PremiumDiscountEngine";
import { calculateOscarScore } from "../oscarScore";
import {
  DecisionState,
  FairValueGapState,
  InstitutionalAnalysis,
  OrderBlockState,
  PipelineInput,
  PremiumDiscountState,
} from "./types";

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

  const orderBlocks = createOrderBlocks(candles as Array<{ time: string; open: number; high: number; low: number; close: number }>);
  const fairValueGaps = createFairValueGaps(candles as Array<{ time: string; open: number; high: number; low: number; close: number }>);
  const premiumDiscount = createPremiumDiscount(candles as Array<{ time: string; open: number; high: number; low: number; close: number }>, []);
  const score = calculateOscarScore(structure, tick, status, context, liquidity, orderBlocks, fairValueGaps, premiumDiscount);

  const analysis: InstitutionalAnalysis = {
    structure,
    liquidity,
    context,
    orderBlocks,
    fairValueGaps,
    premiumDiscount,
    score,
    decision: null,
  };

  const decision = createDecision(analysis);
  analysis.decision = {
    type: decision.type,
    confidence: decision.confidence,
    reason: decision.reason,
  } as DecisionState;

  return analysis;
}
