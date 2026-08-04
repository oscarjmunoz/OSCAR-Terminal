import { getCandles, getStatus, getTick } from "../api/market";
import { getStructure } from "../api/smartMoney";
import { DecisionContext } from "../contracts/DecisionContext";
import { JournalEngine } from "../engine/journal/JournalEngine";
import { TimeframeName } from "../engine/mtf/types";
import { runInstitutionalPipeline } from "../engine/pipeline/InstitutionalPipeline";
import { InstitutionalAnalysis } from "../engine/pipeline/types";
import { getActiveStrategy } from "../engine/strategy/StrategyRegistry";
import { buildDecisionContext } from "../services/decisionContext/decisionContextBuilder";
import { CandleStream } from "./marketData/CandleStream";
import { ConnectionManager } from "./marketData/ConnectionManager";
import { MarketDataEvent } from "./marketData/events";
import { MarketDataEventBus } from "./marketData/EventBus";
import { ConsoleLogger } from "./marketData/logger";
import { MarketDataService } from "./marketData/MarketDataService";
import { DEFAULT_MARKET_DATA_SETTINGS } from "./marketData/settings";
import { Logger, MarketDataSettings } from "./marketData/types";
import { TickStream } from "./marketData/TickStream";
import { TimeframeSynchronizer } from "./marketData/TimeframeSynchronizer";
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
  private readonly journalEngine = new JournalEngine();
  private readonly snapshots = new Map<string, MarketSnapshot>();
  private readonly logger: Logger;
  private eventBus: MarketDataEventBus | null = null;
  private marketDataService: MarketDataService | null = null;
  private tickStream: TickStream | null = null;
  private candleStream: CandleStream | null = null;
  private timeframeSynchronizer: TimeframeSynchronizer | null = null;
  private liveSettings: MarketDataSettings = DEFAULT_MARKET_DATA_SETTINGS;
  private liveRunning = false;
  private droppedEvents = 0;
  private pendingSymbol: string | null = null;
  private debounceHandle: ReturnType<typeof setTimeout> | null = null;
  private rateLimitHandle: ReturnType<typeof setTimeout> | null = null;
  private lastPipelineExecutionAt = 0;
  private unsubscribeCandleClosed: (() => void) | null = null;
  private unsubscribeConnectionLost: (() => void) | null = null;
  private readonly decisionContexts = new Map<string, DecisionContext>();

  constructor(
    dataSource: LiveDataSource = defaultDataSource,
    config: Partial<OrchestratorConfig> = {},
    logger: Logger = new ConsoleLogger()
  ) {
    this.dataSource = dataSource;
    this.config = {
      ...DEFAULT_CONFIG,
      ...config,
    };
    this.logger = logger;
  }

  attachLiveEngine(dependencies: {
    eventBus: MarketDataEventBus;
    marketDataService: MarketDataService;
    connectionManager: ConnectionManager;
    settings?: Partial<MarketDataSettings>;
    tickStream?: TickStream;
    candleStream?: CandleStream;
    timeframeSynchronizer?: TimeframeSynchronizer;
  }): void {
    const settings: MarketDataSettings = {
      ...DEFAULT_MARKET_DATA_SETTINGS,
      ...dependencies.settings,
      credentials: {
        ...DEFAULT_MARKET_DATA_SETTINGS.credentials,
        ...dependencies.settings?.credentials,
      },
    };

    this.eventBus = dependencies.eventBus;
    this.marketDataService = dependencies.marketDataService;
    this.liveSettings = settings;

    this.tickStream = dependencies.tickStream ?? new TickStream(
      dependencies.marketDataService,
      dependencies.connectionManager,
      dependencies.eventBus,
      settings,
      this.logger
    );

    this.candleStream = dependencies.candleStream ?? new CandleStream(
      dependencies.marketDataService,
      dependencies.eventBus,
      this.logger
    );

    this.timeframeSynchronizer = dependencies.timeframeSynchronizer ?? new TimeframeSynchronizer(
      dependencies.eventBus,
      this.logger
    );
  }

  async startLive(symbol: SupportedSymbol = DEFAULT_SYMBOL): Promise<void> {
    if (!this.eventBus || !this.marketDataService || !this.tickStream || !this.candleStream || !this.timeframeSynchronizer) {
      throw new Error("LiveDataOrchestrator requires attachLiveEngine before startLive");
    }

    if (this.liveRunning) {
      return;
    }

    this.liveRunning = true;
    this.lastPipelineExecutionAt = 0;
    this.droppedEvents = 0;
    this.pendingSymbol = symbol;

    this.unsubscribeCandleClosed = this.eventBus.subscribe("CandleClosed", (event) => {
      this.onCandleClosed(event);
    });

    this.unsubscribeConnectionLost = this.eventBus.subscribe("ConnectionLost", () => {
      this.logger.warn("LiveDataOrchestrator reconnect detected");
    });

    this.timeframeSynchronizer.start();
    this.candleStream.start();
    await this.tickStream.start(symbol);

    this.logger.info("LiveDataOrchestrator live mode started", { symbol });
  }

  stopLive(): void {
    if (!this.liveRunning) {
      return;
    }

    this.liveRunning = false;

    if (this.unsubscribeCandleClosed) {
      this.unsubscribeCandleClosed();
      this.unsubscribeCandleClosed = null;
    }

    if (this.unsubscribeConnectionLost) {
      this.unsubscribeConnectionLost();
      this.unsubscribeConnectionLost = null;
    }

    if (this.debounceHandle) {
      clearTimeout(this.debounceHandle);
      this.debounceHandle = null;
    }

    if (this.rateLimitHandle) {
      clearTimeout(this.rateLimitHandle);
      this.rateLimitHandle = null;
    }

    this.tickStream?.stop();
    this.candleStream?.stop();
    this.timeframeSynchronizer?.stop();
    this.logger.info("LiveDataOrchestrator live mode stopped", { droppedEvents: this.droppedEvents });
  }

  getDecisionContext(symbol: SupportedSymbol = DEFAULT_SYMBOL): DecisionContext | null {
    return this.decisionContexts.get(symbol) ?? null;
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

  getJournalEngine(): JournalEngine {
    return this.journalEngine;
  }

  private onCandleClosed(event: MarketDataEvent<"CandleClosed">): void {
    if (!this.liveRunning) {
      return;
    }

    this.pendingSymbol = event.payload.symbol;

    if (this.debounceHandle) {
      clearTimeout(this.debounceHandle);
      this.debounceHandle = null;
    }

    this.debounceHandle = setTimeout(() => {
      this.debounceHandle = null;
      void this.tryExecutePipeline();
    }, this.liveSettings.liveDebounceMs);
  }

  private async tryExecutePipeline(): Promise<void> {
    if (!this.liveRunning || !this.eventBus || !this.marketDataService || !this.pendingSymbol) {
      return;
    }

    const now = Date.now();
    const elapsedSinceLastExecution = now - this.lastPipelineExecutionAt;

    if (elapsedSinceLastExecution < this.liveSettings.liveRateLimitMs) {
      this.droppedEvents += 1;
      this.logger.warn("LiveDataOrchestrator dropped event due to rate limit", {
        droppedEvents: this.droppedEvents,
        elapsedSinceLastExecution,
      });

      if (!this.rateLimitHandle) {
        this.rateLimitHandle = setTimeout(() => {
          this.rateLimitHandle = null;
          void this.tryExecutePipeline();
        }, this.liveSettings.liveRateLimitMs - elapsedSinceLastExecution);
      }

      return;
    }

    const symbol = this.pendingSymbol;
    this.pendingSymbol = null;

    const pipelineStartedAt = Date.now();

    try {
      const snapshot = await this.refreshSnapshotFromMarketEngine(symbol);
      const output = this.runEngines(snapshot);
      const pipelineLatencyMs = Date.now() - pipelineStartedAt;
      const contextStartedAt = Date.now();

      const decisionContext = buildDecisionContext(
        {
          symbol,
          timeframe: "M5",
          timestamp: snapshot.timestamp,
          analysis: output.institutional.M5,
          latencyMs: pipelineLatencyMs,
        },
        output
      );

      const decisionLatencyMs = Date.now() - contextStartedAt;

      this.decisionContexts.set(symbol, decisionContext);
      this.lastPipelineExecutionAt = Date.now();

      this.eventBus.publish("PipelineExecuted", {
        symbol,
        timeframe: "M5",
        latencyMs: pipelineLatencyMs,
        droppedEvents: this.droppedEvents,
        executedAt: this.lastPipelineExecutionAt,
      });

      this.eventBus.publish("DecisionContextUpdated", {
        symbol,
        timeframe: "M5",
        context: decisionContext,
        latencyMs: decisionLatencyMs,
        pipelineLatencyMs,
        updatedAt: Date.now(),
      });

      this.logger.info("LiveDataOrchestrator pipeline executed", {
        symbol,
        pipelineLatencyMs,
        decisionLatencyMs,
        droppedEvents: this.droppedEvents,
      });
    } catch (error) {
      this.logger.error("LiveDataOrchestrator pipeline execution failed", {
        symbol,
        reason: error instanceof Error ? error.message : "unknown",
      });
    }
  }

  private async refreshSnapshotFromMarketEngine(symbol: string): Promise<MarketSnapshot> {
    if (!this.marketDataService) {
      throw new Error("MarketDataService is not attached");
    }

    const [tick, status] = await Promise.all([
      this.marketDataService.get_latest_tick(symbol),
      this.marketDataService.get_market_status(symbol),
    ]);

    const timeframePairs = await Promise.all(
      DEFAULT_TIMEFRAMES.map(async (timeframe) => {
        const candles = await this.marketDataService?.get_candles(symbol, timeframe, this.config.candleCount);
        const structure = await this.dataSource.fetchStructure(symbol, timeframe, this.config.candleCount);

        return [
          timeframe,
          {
            candles: (candles ?? []).map((candle) => ({
              time: candle.time,
              open: candle.open,
              high: candle.high,
              low: candle.low,
              close: candle.close,
              tick_volume: candle.tickVolume,
            })),
            structure,
          },
        ] as const;
      })
    );

    const timeframes = Object.fromEntries(timeframePairs) as MarketSnapshot["timeframes"];

    const snapshot: MarketSnapshot = {
      symbol,
      tick: tick
        ? {
          symbol: tick.symbol,
          bid: tick.bid,
          ask: tick.ask,
          spread: tick.spread,
        }
        : null,
      status: status
        ? {
          connected: status.connected,
          account: 0,
          company: status.session,
          server: status.serverTime,
        }
        : null,
      timeframes,
      timestamp: Date.now(),
    };

    this.snapshots.set(symbol, snapshot);
    return snapshot;
  }

  runEngines(snapshot: MarketSnapshot): OrchestratedEngineOutput {
    const strategy = getActiveStrategy();

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

    DEFAULT_TIMEFRAMES.forEach((timeframe) => {
      this.journalEngine.registerSignal(snapshot, timeframe, institutional[timeframe], strategy.id);
    });

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
      journalEntries: this.journalEngine.getEntries(),
    };
  }
}
