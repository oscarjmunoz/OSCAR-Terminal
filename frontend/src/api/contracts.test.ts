import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("./client", () => ({
    api: {
        get: vi.fn(),
        post: vi.fn(),
    },
}));

import { api } from "./client";
import { getScannerOpportunities } from "./scanner";

describe("scanner contract client", () => {
    beforeEach(() => {
        vi.mocked(api.get).mockReset();
    });

    it("maps the scanner opportunities response to the backend contract", async () => {
        vi.mocked(api.get).mockResolvedValueOnce({
            data: {
                opportunities: [
                    {
                        symbol: "EURUSD",
                        timeframe: "M5",
                        bias: "BULLISH",
                        structure: "TREND",
                        liquidity_target: "SWEEP",
                        stage: "WAITING_SWEEP",
                        institutional_score: 78.2,
                        execution_quality: 72.1,
                        last_update: "2026-08-09T00:00:00Z",
                        health: "GREEN",
                        decision_summary: "Context is aligned.",
                    },
                ],
            },
        } as never);

        const response = await getScannerOpportunities();

        expect(api.get).toHaveBeenCalledWith("/scanner/opportunities");
        expect(response.opportunities[0]).toMatchObject({
            symbol: "EURUSD",
            stage: "WAITING_SWEEP",
            institutional_score: 78.2,
            decision_summary: "Context is aligned.",
        });
    });
});
