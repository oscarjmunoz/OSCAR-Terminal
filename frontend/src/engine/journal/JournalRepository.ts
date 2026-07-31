import { CreateJournalEntryInput, JournalEntry, UpdateJournalEntryInput } from "./types";

function createEntryId(symbol: string, timeframe: string, timestamp: number): string {
  return `${symbol}-${timeframe}-${timestamp}`;
}

export class JournalRepository {
  private entries: JournalEntry[] = [];

  createEntry(input: CreateJournalEntryInput): JournalEntry {
    const decision = input.institutionalAnalysis.decision;
    const score = input.institutionalAnalysis.score;

    const entry: JournalEntry = {
      id: createEntryId(input.symbol, input.timeframe, input.marketSnapshot.timestamp),
      timestamp: input.marketSnapshot.timestamp,
      symbol: input.symbol,
      timeframe: input.timeframe,
      strategy: input.strategy,
      marketSnapshot: input.marketSnapshot,
      institutionalAnalysis: input.institutionalAnalysis,
      decision: decision?.type ?? "NO TRADE",
      confidence: decision?.confidence ?? score?.confidence ?? 0,
      score: score?.score ?? 0,
      reasons: decision?.reason ?? score?.reason ?? [],
      status: "PENDING",
    };

    this.entries.push(entry);
    return entry;
  }

  updateEntry(input: UpdateJournalEntryInput): JournalEntry | null {
    const index = this.entries.findIndex((entry) => entry.id === input.id);
    if (index === -1) {
      return null;
    }

    const current = this.entries[index];
    const updated: JournalEntry = {
      ...current,
      status: input.status ?? current.status,
      confidence: input.confidence ?? current.confidence,
      score: input.score ?? current.score,
      reasons: input.reasons ?? current.reasons,
    };

    this.entries[index] = updated;
    return updated;
  }

  getEntries(): JournalEntry[] {
    return [...this.entries];
  }

  getEntry(id: string): JournalEntry | null {
    return this.entries.find((entry) => entry.id === id) ?? null;
  }

  clear(): void {
    this.entries = [];
  }
}
