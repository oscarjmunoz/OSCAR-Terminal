import { DecisionContext } from "../../contracts/DecisionContext";
import TerminalCard from "./TerminalCard";

type Props = {
    bias: DecisionContext["score"]["bias"];
};

function biasTone(bias: Props["bias"]): string {
    if (bias === "LONG") return "border-emerald-500/30 bg-emerald-500/10 text-emerald-300";
    if (bias === "SHORT") return "border-rose-500/30 bg-rose-500/10 text-rose-300";
    return "border-slate-700 bg-slate-900/80 text-slate-300";
}

export default function BiasCard({ bias }: Props) {
    return (
        <TerminalCard title="Bias" eyebrow="Panel 3">
            <div className="flex min-h-[118px] flex-col justify-between rounded-xl border border-slate-800 bg-slate-900/70 p-4">
                <span className={`inline-flex w-fit rounded-full border px-3 py-1 text-sm font-semibold ${biasTone(bias)}`}>{bias}</span>
                <p className="mt-3 text-sm text-slate-400">Directional regime extracted from the institutional context.</p>
            </div>
        </TerminalCard>
    );
}