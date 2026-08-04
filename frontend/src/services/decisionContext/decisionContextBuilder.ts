import { OrchestratedEngineOutput } from "../../core/types";
import { DecisionContext, DecisionContextInput, DecisionExecutionContext } from "../../contracts/DecisionContext";

const DEFAULT_TIMEFRAME = "M5";

function formatPrice(value: number | null | undefined): string | null {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return null;
    }

    return value.toFixed(5);
}

function resolveBias(value: string | undefined): DecisionContext["score"]["bias"] {
    if (value === "LONG") return "LONG";
    if (value === "SHORT") return "SHORT";
    return "NEUTRAL";
}

function resolveRecommendation(output: OrchestratedEngineOutput): DecisionContext["score"]["recommendation"] {
    return output.institutional[DEFAULT_TIMEFRAME].decision?.type ?? "NO TRADE";
}

function resolveRiskGrade(score: number, recommendation: DecisionContext["score"]["recommendation"]): DecisionContext["risk"]["grade"] {
    if (recommendation === "NO TRADE" || recommendation === "WAIT") {
        return "HIGH";
    }

    if (score >= 80) return "LOW";
    if (score >= 60) return "MEDIUM";
    return "HIGH";
}

function resolveRiskProfile(grade: DecisionContext["risk"]["grade"]): Pick<DecisionContext["risk"], "capitalRisk" | "rr"> {
    if (grade === "LOW") return { capitalRisk: "0.50%", rr: "1:3.0" };
    if (grade === "MEDIUM") return { capitalRisk: "0.75%", rr: "1:2.0" };
    return { capitalRisk: "1.00%", rr: "1:1.5" };
}

function resolveExecutionContext(input: DecisionContextInput, output: OrchestratedEngineOutput): DecisionExecutionContext | null {
    const analysis = output.institutional[DEFAULT_TIMEFRAME];
    const decision = analysis.decision?.type ?? "NO TRADE";

    if (decision === "WAIT" || decision === "NO TRADE") {
        return null;
    }

    const tickPrice = decision === "BUY" ? output.snapshot.tick?.ask : output.snapshot.tick?.bid;
    const stopPrice = decision === "BUY" ? analysis.structure?.last_low : analysis.structure?.last_high;

    if (tickPrice === undefined || tickPrice === null || stopPrice === undefined || stopPrice === null) {
        return null;
    }

    const distance = Math.abs(tickPrice - stopPrice);
    if (!distance) {
        return null;
    }

    const tp1 = decision === "BUY" ? tickPrice + distance : tickPrice - distance;
    const tp2 = decision === "BUY" ? tickPrice + distance * 2 : tickPrice - distance * 2;

    return {
        entry: formatPrice(tickPrice),
        stop: formatPrice(stopPrice),
        tp1: formatPrice(tp1),
        tp2: formatPrice(tp2),
        rr: "1:2.0",
    };
}

function buildNarrative(input: DecisionContextInput, output: OrchestratedEngineOutput): string {
    const analysis = output.institutional[DEFAULT_TIMEFRAME];
    const score = analysis.score?.score ?? 0;
    const confidence = analysis.decision?.confidence ?? 0;
    const trend = analysis.context?.trend ?? "UNKNOWN";
    const bias = analysis.context?.bias ?? "NEUTRAL";
    const session = analysis.context?.session ?? "UNKNOWN";

    return [
        `${input.symbol} ${input.timeframe} report for ${session} session.`,
        `Institutional score ${score}/100 with ${confidence}% confidence and ${bias} bias.`,
        `Structure trend is ${trend}.`,
        `${analysis.liquidity.length} liquidity references, ${analysis.orderBlocks.length} order blocks, and ${analysis.fairValueGaps.length} FVGs detected.`,
    ].join(" ");
}

function buildWarnings(output: OrchestratedEngineOutput): string[] {
    const analysis = output.institutional[DEFAULT_TIMEFRAME];
    const warnings: string[] = [];

    if (!analysis.structure) warnings.push("Structure unavailable.");
    if (!analysis.liquidity.length) warnings.push("No liquidity levels detected.");
    if (!analysis.orderBlocks.length) warnings.push("No order blocks detected.");
    if (!analysis.fairValueGaps.length) warnings.push("No fair value gaps detected.");
    if (!analysis.premiumDiscount.length) warnings.push("Premium/discount context unavailable.");
    if (!analysis.context?.connected) warnings.push("Connection is offline.");

    return warnings;
}

export function buildDecisionContext(input: DecisionContextInput, output: OrchestratedEngineOutput): DecisionContext {
    const analysis = output.institutional[DEFAULT_TIMEFRAME];
    const score = analysis.score?.score ?? 0;
    const confidence = analysis.decision?.confidence ?? analysis.score?.confidence ?? 0;
    const recommendation = resolveRecommendation(output);
    const grade = resolveRiskGrade(score, recommendation);
    const riskProfile = resolveRiskProfile(grade);
    const execution = resolveExecutionContext(input, output);

    return {
        header: {
            symbol: input.symbol,
            timeframe: input.timeframe,
            date: new Date(input.timestamp).toLocaleString(),
            session: analysis.context?.session ?? "UNKNOWN",
            connection: analysis.context?.connected ? "LIVE" : "OFFLINE",
            latencyMs: input.latencyMs ?? null,
        },
        score: {
            institutionalScore: score,
            confidence,
            bias: resolveBias(analysis.context?.bias),
            recommendation,
        },
        risk: {
            grade,
            rr: riskProfile.rr,
            capitalRisk: riskProfile.capitalRisk,
            stopDistance: execution?.entry && execution.stop ? Math.abs(Number(execution.entry) - Number(execution.stop)).toFixed(5) : "N/A",
        },
        liquidity: {
            sweep: analysis.liquidity.length ? "Liquidity sweep present" : "No sweep detected",
            internal: analysis.liquidity.some((item) => item.type === "EQH" || item.type === "EQL")
                ? "Internal liquidity mapped"
                : "No internal liquidity mapped",
            external: analysis.liquidity.some((item) => item.type === "BSL" || item.type === "SSL")
                ? "External liquidity mapped"
                : "No external liquidity mapped",
            levels: analysis.liquidity.length ? analysis.liquidity.slice(0, 4).map((item) => `${item.type} @ ${item.price.toFixed(5)}`) : ["No liquidity levels detected."],
        },
        structure: {
            bos: analysis.structure?.bos ? "BOS confirmed" : "No BOS",
            choch: analysis.structure?.choch ? "CHoCH detected" : "No CHoCH",
            mss: analysis.structure?.mss ? "MSS confirmed" : "No MSS",
            trend: analysis.structure?.trend ?? "UNKNOWN",
        },
        context: {
            orderBlocks: analysis.orderBlocks.length ? analysis.orderBlocks.map((item) => `${item.type} (${item.status})`) : ["No order blocks detected."],
            fvg: analysis.fairValueGaps.length ? analysis.fairValueGaps.map((item) => `${item.type} (${item.status})`) : ["No FVG detected."],
            breaker: analysis.structure?.choch ? "Breaker structure active" : "Breaker not confirmed",
            mitigation: analysis.orderBlocks.some((item) => item.status === "MITIGATED") ? "Mitigation present" : "No mitigation confirmed",
            premium: analysis.premiumDiscount.some((item) => item.type === "PREMIUM") ? "Premium" : "Not in premium",
            discount: analysis.premiumDiscount.some((item) => item.type === "DISCOUNT") ? "Discount" : "Not in discount",
        },
        narrative: buildNarrative(input, output),
        warnings: buildWarnings(output),
        execution,
        confluences: {
            liquidity: analysis.liquidity.length ? Math.min(100, analysis.liquidity.length * 20) : 0,
            structure: [analysis.structure?.bos, analysis.structure?.choch, analysis.structure?.mss].filter(Boolean).length * 33,
            risk: grade === "LOW" ? 90 : grade === "MEDIUM" ? 65 : 35,
            context: [analysis.orderBlocks.length, analysis.fairValueGaps.length, analysis.premiumDiscount.length].filter((count) => count > 0).length * 33,
        },
        source: "INSTITUTIONAL_PIPELINE",
    };
}
