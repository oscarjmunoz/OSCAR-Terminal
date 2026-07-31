import { ValidationBatch, ValidationEngineInput, ValidationRecord } from "./types";

function resolveTimestamp(input: ValidationEngineInput): number {
  if (input.timestamp !== undefined) {
    return input.timestamp;
  }

  const lastCandle = input.candles[input.candles.length - 1];
  if (lastCandle) {
    return Math.floor(new Date(lastCandle.time).getTime() / 1000);
  }

  return Math.floor(Date.now() / 1000);
}

export function createValidationRecord(input: ValidationEngineInput): ValidationRecord {
  const { analysis } = input;

  return {
    timestamp: resolveTimestamp(input),
    symbol: input.symbol ?? "UNKNOWN",
    timeframe: input.timeframe ?? "UNKNOWN",
    score: analysis.score?.score ?? 0,
    decision: analysis.decision?.type ?? "NO TRADE",
    confidence: analysis.decision?.confidence ?? analysis.score?.confidence ?? 0,
  };
}

export function runValidationEngine(input: ValidationEngineInput): ValidationBatch {
  return {
    records: [createValidationRecord(input)],
    source: "INSTITUTIONAL_PIPELINE",
  };
}
