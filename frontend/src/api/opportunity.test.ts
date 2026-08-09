import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("./client", () => ({
    api: {
        get: vi.fn(),
    },
}));

import { api } from "./client";
import { getOpportunityQueue } from "./opportunity";

describe("opportunity queue client", () => {
    beforeEach(() => {
        vi.mocked(api.get).mockReset();
    });

    it("requests the canonical opportunity queue endpoint", async () => {
        vi.mocked(api.get).mockResolvedValueOnce({
            data: {
                market_summary: {
                    total_assets: 1,
                    ignored: 0,
                    watching: 0,
                    preparing: 0,
                    ready: 1,
                    active: 0,
                    last_scan: "2026-08-09T00:00:00Z",
                },
                opportunity_queue: [],
            },
        } as never);

        const response = await getOpportunityQueue();

        expect(api.get).toHaveBeenCalledWith("/opportunity/queue");
        expect(response.market_summary.ready).toBe(1);
    });
});