import { DecisionContext } from "../../contracts/DecisionContext";
import TerminalCard from "./TerminalCard";

type Props = {
    context: DecisionContext["context"];
};

function blockList(label: string, items: string[]) {
    return (
        <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
            <p className="text-[11px] uppercase tracking-[0.22em] text-slate-500">{label}</p>
            <div className="mt-2 flex flex-wrap gap-2">
                {items.map((item) => (
                    <span key={`${label}-${item}`} className="rounded-full border border-slate-700 bg-slate-950/80 px-3 py-1 text-xs text-slate-300">
                        {item}
                    </span>
                ))}
            </div>
        </div>
    );
}

export default function ContextCard({ context }: Props) {
    return (
        <TerminalCard title="Institutional Context" eyebrow="Panel 8">
            <div className="space-y-3">
                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                    {blockList("Order Blocks", context.orderBlocks)}
                    {blockList("FVG", context.fvg)}
                    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
                        <p className="text-[11px] uppercase tracking-[0.22em] text-slate-500">Breaker</p>
                        <p className="mt-2 text-sm font-semibold text-slate-100">{context.breaker}</p>
                        <p className="mt-3 text-[11px] uppercase tracking-[0.22em] text-slate-500">Mitigation</p>
                        <p className="mt-2 text-sm font-semibold text-slate-100">{context.mitigation}</p>
                    </div>
                </div>

                <div className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
                        <p className="text-[11px] uppercase tracking-[0.22em] text-slate-500">Premium</p>
                        <p className="mt-2 text-sm font-semibold text-slate-100">{context.premium}</p>
                    </div>
                    <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
                        <p className="text-[11px] uppercase tracking-[0.22em] text-slate-500">Discount</p>
                        <p className="mt-2 text-sm font-semibold text-slate-100">{context.discount}</p>
                    </div>
                </div>
            </div>
        </TerminalCard>
    );
}