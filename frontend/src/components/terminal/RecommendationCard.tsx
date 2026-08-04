import { DecisionContext } from "../../contracts/DecisionContext";
import TerminalCard from "./TerminalCard";

type Props = {
    recommendation: DecisionContext["score"]["recommendation"];
};

function tone(recommendation: Props["recommendation"]): string {
    if (recommendation === "BUY") return "border-emerald-500/30 bg-emerald-500/10 text-emerald-200";
    if (recommendation === "SELL") return "border-rose-500/30 bg-rose-500/10 text-rose-200";
    if (recommendation === "WAIT") return "border-amber-500/30 bg-amber-500/10 text-amber-200";
    return "border-slate-700 bg-slate-900/80 text-slate-200";
}

export default function RecommendationCard({ recommendation }: Props) {
    return (
        <TerminalCard title="Execution Recommendation" eyebrow="Panel 4">
            <div className={`flex min-h-[118px] items-center justify-between rounded-xl border p-4 ${tone(recommendation)}`}>
                <div>
                    <p className="text-[11px] uppercase tracking-[0.24em] text-white/60">Action</p>
                    <p className="mt-2 text-3xl font-black tracking-tight">{recommendation}</p>
                </div>
                <div className="text-right text-xs uppercase tracking-[0.24em] text-white/60">Institutional filter</div>
            </div>
        </TerminalCard>
    );
}