import { getCandles, getStatus, getTick } from "../api/market";
import { getStructure } from "../api/smartMoney";
import { TimeframeName } from "../engine/mtf/types";
import { runInstitutionalPipeline } from "../engine/pipeline/InstitutionalPipeline";
import { InstitutionalAnalysis } from "../engine/pipeline/types";
import {
  LiveDataSource,
  MarketSnapshot,
  OrchestratedEngineOutput,
  OrchestratorConfig,
  SupportedSymbol,
} from "./types";

const DEFAULT_SYMBOL: SupportedSymbol = "USDCHF.pro";
const DEFAULT_TIMEFRAMES: TimeframeName[] = ["H4", "H1", "M15", "M5"];
const DEFAULT_CONFIG: OrchestratorConfig = {
  candleCount: 300,
};

const defaultDataSource: LiveDataSource = {
  async fetchTick(symbol: string) {
    const raw = await getTick();
    return {
      ...raw,
      symbol: raw.symbol || symbol,
    };
  },
  fetchStatus: getStatus,
  fetchCandles(symbol: string, timeframe: TimeframeName, count: number) {
    return getCandles(timeframe, count);
  },
  fetchStructure(symbol: string, timeframe: TimeframeName, count: number) {
    return getStructure(symbol, timeframe, count);
  },
};

export class LiveDataOrchestrator {
  private readonly dataSource: LiveDataSource;
  private readonly config: OrchestratorConfig;
  private readonly snapshots = new Map<string, MarketSnapshot>();

  constructor(dataSource: LiveDataSource = defaultDataSource, config: Partial<OrchestratorConfig> = {}) {
    this.dataSource = dataSource;
    this.config = {
      ...DEFAULT_CONFIG,
      ...config,
    };
  }

  async refreshSnapshot(symbol: SupportedSymbol = DEFAULT_SYMBOL): Promise<MarketSnapshot> {
    const [tick, status] = await Promise.all([
      this.dataSource.fetchTick(symbol),
      this.dataSource.fetchStatus(),
    ]);

    const timeframePairs = await Promise.all(
      DEFAULT_TIMEFRAMES.map(async (timeframe) => {
        const [candles, structure] = await Promise.all([
          this.dataSource.fetchCandles(symbol, timeframe, this.config.candleCount),
          this.dataSource.fetchStructure(symbol, timeframe, this.config.candleCount),
        ]);

        return [
          timeframe,
          {
            candles,
            structure,
          },
        ] as const;
      })
    );

    const timeframes = Object.fromEntries(timeframePairs) as MarketSnapshot["timeframes"];

    const snapshot: MarketSnapshot = {
      symbol,
      tick,
      status,
      timeframes,
      timestamp: Date.now(),
    };

    this.snapshots.set(symbol, snapshot);

    return snapshot;
  }

  getSnapshot(symbol: SupportedSymbol = DEFAULT_SYMBOL): MarketSnapshot | null {
    return this.snapshots.get(symbol) ?? null;
  }

  clearSnapshot(symbol: SupportedSymbol): void {
    this.snapshots.delete(symbol);
  }

  clearAllSnapshots(): void {
    this.snapshots.clear();
  }

  runEngines(snapshot: MarketSnapshot): OrchestratedEngineOutput {
    const institutional = DEFAULT_TIMEFRAMES.reduce<Record<TimeframeName, InstitutionalAnalysis>>((acc, timeframe) => {
      const frame = snapshot.timeframes[timeframe];

      acc[timeframe] = runInstitutionalPipeline({
        structure: frame.structure,
        tick: snapshot.tick,
        status: snapshot.status,
        candles: frame.candles,
      });

      return acc;
    }, {} as Record<TimeframeName, InstitutionalAnalysis>);

    const h4Trend = institutional.H4.structure?.trend ?? "RANGE";
    const alignedCount = DEFAULT_TIMEFRAMES.reduce((count, timeframe) => {
      const trend = institutional[timeframe].structure?.trend ?? "RANGE";
      const alignedWithH4 = trend === h4Trend || h4Trend === "RANGE";
      return alignedWithH4 ? count + 1 : count;
    }, 0);

    let alignment = 25;
    if (alignedCount === 4) alignment = 100;
    else if (alignedCount === 3) alignment = 75;
    else if (alignedCount === 2) alignment = 50;

    const biasVotes = DEFAULT_TIMEFRAMES.map((timeframe) => institutional[timeframe].context?.bias ?? "NEUTRAL");
    const longVotes = biasVotes.filter((bias) => bias === "LONG").length;
    const shortVotes = biasVotes.filter((bias) => bias === "SHORT").length;

    let globalBias: OrchestratedEngineOutput["mtf"]["globalBias"] = "NEUTRAL";
    if (longVotes > shortVotes) globalBias = "LONG";
    else if (shortVotes > longVotes) globalBias = "SHORT";

    const mtf = {
      H4: {
        timeframe: "H4" as const,
        structure: institutional.H4.structure,
        liquidity: institutional.H4.liquidity,
        context: institutional.H4.context,
        score: institutional.H4.score,
        decision: institutional.H4.decision,
      },
      H1: {
        timeframe: "H1" as const,
        structure: institutional.H1.structure,
        liquidity: institutional.H1.liquidity,
        context: institutional.H1.context,
        score: institutional.H1.score,
        decision: institutional.H1.decision,
      },
      M15: {
        timeframe: "M15" as const,
        structure: institutional.M15.structure,
        liquidity: institutional.M15.liquidity,
        context: institutional.M15.context,
        score: institutional.M15.score,
        decision: institutional.M15.decision,
      },
      M5: {
        timeframe: "M5" as const,
        structure: institutional.M5.structure,
        liquidity: institutional.M5.liquidity,
        context: institutional.M5.context,
        score: institutional.M5.score,
        decision: institutional.M5.decision,
      },
      alignment,
      globalBias,
    };

    return {
      snapshot,
      institutional,
      mtf,
    };
  }
}
