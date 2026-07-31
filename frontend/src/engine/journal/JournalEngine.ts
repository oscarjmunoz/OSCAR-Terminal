import { MarketSnapshot } from "../../core/types";
import { InstitutionalAnalysis } from "../pipeline/types";
import { JournalRepository } from "./JournalRepository";
import { CreateJournalEntryInput, JournalEntry, UpdateJournalEntryInput } from "./types";

export class JournalEngine {
  constructor(private readonly repository: JournalRepository = new JournalRepository()) {}

  registerSignal(snapshot: MarketSnapshot, timeframe: string, analysis: InstitutionalAnalysis, strategy: string): JournalEntry {
    const payload: CreateJournalEntryInput = {
      symbol: snapshot.symbol,
      timeframe,
      strategy,
      marketSnapshot: snapshot,
      institutionalAnalysis: analysis,
    };

    return this.repository.createEntry(payload);
  }

  updateEntry(input: UpdateJournalEntryInput): JournalEntry | null {
    return this.repository.updateEntry(input);
  }

  getEntries(): JournalEntry[] {
    return this.repository.getEntries();
  }

  getEntry(id: string): JournalEntry | null {
    return this.repository.getEntry(id);
  }

  clear(): void {
    this.repository.clear();
  }
}
