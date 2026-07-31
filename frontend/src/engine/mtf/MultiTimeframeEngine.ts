import { TerminalStatus, TickResponse } from "../../api/market";
import { MarketStructure } from "../../api/smartMoney";
import { runInstitutionalPipeline } from "../pipeline/InstitutionalPipeline";
import { TimeframeAnalysis, MultiTimeframeAnalysis, TimeframeName } from "./types";

export interface MultiTimeframeInput {
  structureByTimeframe: Record<TimeframeName, MarketStructure | null>;
  tick: TickResponse | null;
  status: TerminalStatus | null;
  candlesByTimeframe: Record<TimeframeName, Array<{ time: string; open: number; high: number; low: number; close: number }>>;
}

export function createMultiTimeframeAnalysis(input: MultiTimeframeInput): MultiTimeframeAnalysis {
  const timeframes: TimeframeName[] = ["H4", "H1", "M15", "M5"];

  const analyses = timeframes.reduce<Record<TimeframeName, TimeframeAnalysis>>((acc, timeframe) => {
    const analysis = runInstitutionalPipeline({
      structure: input.structureByTimeframe[timeframe],
      tick: input.tick,
      status: input.status,
      candles: input.candlesByTimeframe[timeframe],
    });

    acc[timeframe] = {
      timeframe,
      structure: analysis.structure,
      liquidity: analysis.liquidity,
      context: analysis.context,
      score: analysis.score,
      decision: analysis.decision,
    };

    return acc;
  }, {} as Record<TimeframeName, TimeframeAnalysis>);

  const alignedCount = timeframes.reduce((count, timeframe) => {
    const analysis = analyses[timeframe];
    const trend = analysis.structure?.trend ?? "RANGE";
    const alignedWithH4 = trend === analyses["H4"].structure?.trend || analyses["H4"].structure?.trend === "RANGE";
    return alignedWithH4 ? count + 1 : count;
  }, 0);

  let alignment = 25;
  if (alignedCount === 4) alignment = 100;
  else if (alignedCount === 3) alignment = 75;
  else if (alignedCount === 2) alignment = 50;

  const biasVotes = timeframes.map((tf) => analyses[tf].context?.bias ?? "NEUTRAL");
  const longVotes = biasVotes.filter((bias) => bias === "LONG").length;
  const shortVotes = biasVotes.filter((bias) => bias === "SHORT").length;

  let globalBias: MultiTimeframeAnalysis["globalBias"] = "NEUTRAL";
  if (longVotes > shortVotes) globalBias = "LONG";
  else if (shortVotes > longVotes) globalBias = "SHORT";

  return {
    H4: analyses["H4"],
    H1: analyses["H1"],
    M15: analyses["M15"],
    M5: analyses["M5"],
    alignment,
    globalBias,
  };
}
