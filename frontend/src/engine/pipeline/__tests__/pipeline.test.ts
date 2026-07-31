import { describe, expect, it } from "vitest";

import { runInstitutionalPipeline } from "../InstitutionalPipeline";

describe("InstitutionalPipeline", () => {
  it("returns a complete analysis object", () => {
    const result = runInstitutionalPipeline({
      structure: null,
      tick: null,
      status: null,
      candles: [],
    });

    expect(result).toBeDefined();
    expect(result.structure).toBeNull();
    expect(result.liquidity).toEqual([]);
    expect(result.context).toBeTruthy();
    expect(result.score).toBeTruthy();
  });
});
