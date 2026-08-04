import { DecisionContext } from "../../contracts/DecisionContext";
import BiasCard from "./BiasCard";
import ConfidenceCard from "./ConfidenceCard";
import ConfluencesCard from "./ConfluencesCard";
import ContextCard from "./ContextCard";
import ExecutionCard from "./ExecutionCard";
import LiquidityCard from "./LiquidityCard";
import NarrativeCard from "./NarrativeCard";
import RecommendationCard from "./RecommendationCard";
import RiskCard from "./RiskCard";
import ScoreCard from "./ScoreCard";
import StructureCard from "./StructureCard";
import WarningsCard from "./WarningsCard";

type Props = {
    context: DecisionContext | null;
};

function EmptyState() {
    return (
        <section className="rounded-2xl border border-slate-800/80 bg-slate-950/70 p-6 text-slate-300">
            <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">Terminal</p>
            <h2 className="mt-2 text-lg font-semibold text-slate-100">Waiting for DecisionContext</h2>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-400">
                The frontend is ready, but no institutional context is available yet. Connect the pipeline adapter to render live score, narrative, execution, and risk panels.
            </p>
        </section>
    );
}

export default function TerminalDashboard({ context }: Props) {
    if (!context) {
        return <EmptyState />;
    }

    return (
        <div className="space-y-4">
            <div className="grid gap-4 xl:grid-cols-4">
                <ScoreCard value={context.score.institutionalScore} />
                <ConfidenceCard value={context.score.confidence} />
                <BiasCard bias={context.score.bias} />
                <RecommendationCard recommendation={context.score.recommendation} />
            </div>

            <RiskCard risk={context.risk} />

            <div className="grid gap-4 xl:grid-cols-2">
                <LiquidityCard liquidity={context.liquidity} />
                <StructureCard structure={context.structure} />
            </div>

            <ContextCard context={context.context} />

            <div className="grid gap-4 xl:grid-cols-[1.3fr_0.7fr]">
                <NarrativeCard narrative={context.narrative} />
                <WarningsCard warnings={context.warnings} />
            </div>

            <ExecutionCard execution={context.execution} />
            <ConfluencesCard confluences={context.confluences} />
        </div>
    );
}