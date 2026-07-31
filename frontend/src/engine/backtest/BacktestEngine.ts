import { CandleResponse } from "../../api/market";
import { ValidationRecord } from "../validation/types";
import { BacktestConfig, BacktestInput, BacktestResult, BacktestTradeResult } from "./types";

const DEFAULT_CONFIG: BacktestConfig = {
  takeProfitR: 2,
  stopLossR: 1,
  minRisk: 0.00001,
};

function normalizeTimestamp(timestamp: number): number {
  return timestamp > 10_000_000_000 ? Math.floor(timestamp / 1000) : timestamp;
}

function candleTimestampSeconds(candle: CandleResponse): number {
  return Math.floor(new Date(candle.time).getTime() / 1000);
}

function findEntryIndex(candles: CandleResponse[], timestamp: number): number {
  const target = normalizeTimestamp(timestamp);
  const exact = candles.findIndex((candle) => candleTimestampSeconds(candle) === target);
  if (exact !== -1) {
    return exact;
  }

  let closestIndex = 0;
  let closestDelta = Number.POSITIVE_INFINITY;

  candles.forEach((candle, index) => {
    const delta = Math.abs(candleTimestampSeconds(candle) - target);
    if (delta < closestDelta) {
      closestDelta = delta;
      closestIndex = index;
    }
  });

  return closestIndex;
}

function simulateTrade(
  record: ValidationRecord,
  candles: CandleResponse[],
  entryIndex: number,
  config: BacktestConfig
): BacktestTradeResult {
  const entryCandle = candles[entryIndex];
  const entryPrice = entryCandle.close;
  const risk = Math.max(Math.abs(entryCandle.high - entryCandle.low), config.minRisk);

  const isBuy = record.decision === "BUY";
  const takeProfit = isBuy
    ? entryPrice + config.takeProfitR * risk
    : entryPrice - config.takeProfitR * risk;
  const stopLoss = isBuy
    ? entryPrice - config.stopLossR * risk
    : entryPrice + config.stopLossR * risk;

  for (let index = entryIndex + 1; index < candles.length; index += 1) {
    const candle = candles[index];

    if (isBuy) {
      const stopHit = candle.low <= stopLoss;
      const tpHit = candle.high >= takeProfit;

      if (stopHit && tpHit) {
        return {
          record,
          entryIndex,
          exitIndex: index,
          entryPrice,
          exitPrice: stopLoss,
          outcome: "LOSS",
          rr: -config.stopLossR,
        };
      }

      if (tpHit) {
        return {
          record,
          entryIndex,
          exitIndex: index,
          entryPrice,
          exitPrice: takeProfit,
          outcome: "WIN",
          rr: config.takeProfitR,
        };
      }

      if (stopHit) {
        return {
          record,
          entryIndex,
          exitIndex: index,
          entryPrice,
          exitPrice: stopLoss,
          outcome: "LOSS",
          rr: -config.stopLossR,
        };
      }
    } else {
      const stopHit = candle.high >= stopLoss;
      const tpHit = candle.low <= takeProfit;

      if (stopHit && tpHit) {
        return {
          record,
          entryIndex,
          exitIndex: index,
          entryPrice,
          exitPrice: stopLoss,
          outcome: "LOSS",
          rr: -config.stopLossR,
        };
      }

      if (tpHit) {
        return {
          record,
          entryIndex,
          exitIndex: index,
          entryPrice,
          exitPrice: takeProfit,
          outcome: "WIN",
          rr: config.takeProfitR,
        };
      }

      if (stopHit) {
        return {
          record,
          entryIndex,
          exitIndex: index,
          entryPrice,
          exitPrice: stopLoss,
          outcome: "LOSS",
          rr: -config.stopLossR,
        };
      }
    }
  }

  const lastIndex = candles.length - 1;
  const lastClose = candles[lastIndex].close;
  const rawRR = isBuy ? (lastClose - entryPrice) / risk : (entryPrice - lastClose) / risk;
  const outcome = rawRR >= 0 ? "WIN" : "LOSS";

  return {
    record,
    entryIndex,
    exitIndex: lastIndex,
    entryPrice,
    exitPrice: lastClose,
    outcome,
    rr: rawRR,
  };
}

export function runBacktest(input: BacktestInput): BacktestResult {
  const config: BacktestConfig = {
    ...DEFAULT_CONFIG,
    ...input.config,
  };

  const tradeRecords = input.records.filter(
    (record) => record.decision === "BUY" || record.decision === "SELL"
  );

  const trades: BacktestTradeResult[] = tradeRecords
    .map((record) => {
      if (!input.candles.length) {
        return null;
      }

      const entryIndex = findEntryIndex(input.candles, record.timestamp);
      return simulateTrade(record, input.candles, entryIndex, config);
    })
    .filter((trade): trade is BacktestTradeResult => trade !== null);

  const wins = trades.filter((trade) => trade.outcome === "WIN");
  const losses = trades.filter((trade) => trade.outcome === "LOSS");

  const grossProfit = wins.reduce((sum, trade) => sum + trade.rr, 0);
  const grossLoss = losses.reduce((sum, trade) => sum + Math.abs(trade.rr), 0);
  const totalSignals = trades.length;
  const winRate = totalSignals ? (wins.length / totalSignals) * 100 : 0;
  const profitFactor = grossLoss > 0 ? grossProfit / grossLoss : grossProfit > 0 ? Number.POSITIVE_INFINITY : 0;
  const expectancy = totalSignals ? trades.reduce((sum, trade) => sum + trade.rr, 0) / totalSignals : 0;

  const avgWin = wins.length ? grossProfit / wins.length : 0;
  const avgLossAbs = losses.length ? grossLoss / losses.length : 0;
  const averageRR = avgLossAbs > 0 ? avgWin / avgLossAbs : avgWin > 0 ? avgWin : 0;

  let equity = 0;
  const equityCurve = trades.map((trade) => {
    equity += trade.rr;
    return Number(equity.toFixed(4));
  });

  return {
    totalSignals,
    wins: wins.length,
    losses: losses.length,
    winRate: Number(winRate.toFixed(2)),
    profitFactor: Number.isFinite(profitFactor) ? Number(profitFactor.toFixed(2)) : Number.POSITIVE_INFINITY,
    expectancy: Number(expectancy.toFixed(4)),
    averageRR: Number(averageRR.toFixed(4)),
    equityCurve,
  };
}
