import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import TerminalDashboard from "../TerminalDashboard";
import { DecisionContext } from "../../../contracts/DecisionContext";

function createContext(overrides: Partial<DecisionContext> = {}): DecisionContext {
    const base: DecisionContext = {
        header: {
            symbol: "USDCHF.pro",
            timeframe: "M5",
            date: "2026-08-03 10:00:00",
            session: "LONDON",
            connection: "LIVE",
            latencyMs: 84,
        },
        score: {
            institutionalScore: 87,
            confidence: 91,
            bias: "LONG",
            recommendation: "BUY",
        },
        risk: {
            grade: "LOW",
            rr: "1:3.0",
            capitalRisk: "0.50%",
            stopDistance: "0.00240",
        },
        liquidity: {
            sweep: "Liquidity sweep present",
            internal: "Internal liquidity mapped",
            external: "External liquidity mapped",
            levels: ["BSL @ 1.34500", "SSL @ 1.33840"],
        },
        structure: {
            bos: "BOS confirmed",
            choch: "No CHOCH",
            mss: "MSS confirmed",
            trend: "BULLISH",
        },
        context: {
            orderBlocks: ["BULLISH_OB (MITIGATED)"],
            fvg: ["BULLISH_FVG (OPEN)"],
            breaker: "Breaker structure active",
            mitigation: "Mitigation present",
            premium: "Premium",
            discount: "Discount",
        },
        narrative:
            "USDCHF.pro M5 snapshot for LONDON session. Institutional score is 87/100 with 91% confidence and LONG bias.",
        warnings: [],
        execution: {
            entry: "1.34210",
            stop: "1.33970",
            tp1: "1.34450",
            tp2: "1.34690",
            rr: "1:3.0",
        },
        confluences: {
            liquidity: 80,
            structure: 100,
            risk: 90,
            context: 75,
        },
        source: "INSTITUTIONAL_PIPELINE",
    };

    return {
        ...base,
        ...overrides,
        header: { ...base.header, ...overrides.header },
        score: { ...base.score, ...overrides.score },
        risk: { ...base.risk, ...overrides.risk },
        liquidity: { ...base.liquidity, ...overrides.liquidity },
        structure: { ...base.structure, ...overrides.structure },
        context: { ...base.context, ...overrides.context },
        confluences: { ...base.confluences, ...overrides.confluences },
    };
}

describe("TerminalDashboard", () => {
    it("renders the institutional terminal panels", () => {
        const html = renderToStaticMarkup(<TerminalDashboard context={createContext()} />);

        expect(html).toContain("Institutional Score");
        expect(html).toContain("Execution Recommendation");
        expect(html).toContain("Narrative");
        expect(html).toContain("Confluences");
    });

    it("renders the empty state when no DecisionContext is available", () => {
        const html = renderToStaticMarkup(<TerminalDashboard context={null} />);

        expect(html).toContain("Waiting for DecisionContext");
        expect(html).toContain("pipeline adapter");
    });

    it("shows warnings when present", () => {
        const html = renderToStaticMarkup(<TerminalDashboard context={createContext({ warnings: ["Connection offline"] })} />);

        expect(html).toContain("Connection offline");
        expect(html).toContain("Warnings");
    });

    it("shows the recommendation and score values", () => {
        const html = renderToStaticMarkup(
            <TerminalDashboard
                context={createContext({ score: { institutionalScore: 64, confidence: 72, bias: "NEUTRAL", recommendation: "WAIT" } })}
            />
        );

        expect(html).toContain("WAIT");
        expect(html).toContain("64");
        expect(html).toContain("72");
    });
});