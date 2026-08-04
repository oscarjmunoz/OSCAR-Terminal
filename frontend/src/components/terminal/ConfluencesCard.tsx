import { DecisionContext } from "../../contracts/DecisionContext";
import TerminalCard from "./TerminalCard";

type Props = {
    confluences: DecisionContext["confluences"];
};

function clamp(value: number): number {
    return Math.max(0, Math.min(100, value));
}

function barTone(value: number): string {
    if (value >= 80) return "bg-emerald-400";
    if (value >= 60) return "bg-sky-400";
    if (value >= 40) return "bg-amber-400";
    return "bg-rose-400";
}

export default function ConfluencesCard({ confluences }: Props) {
    const rows = [
        { label: "Liquidity", value: confluences.liquidity },
        { label: "Structure", value: confluences.structure },
        { label: "Risk", value: confluences.risk },
        { label: "Context", value: confluences.context },
    ];

    return (
        <TerminalCard title="Confluences" eyebrow="Panel 12">
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {rows.map((row) => (
                    <div key={row.label} className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
                        <div className="mb-2 flex items-center justify-between">
                            <span className="text-[11px] uppercase tracking-[0.22em] text-slate-500">{row.label}</span>
                            <span className="text-xs font-semibold text-slate-300">{clamp(row.value)}%</span>
                        </div>
                        <div className="h-2 overflow-hidden rounded-full bg-slate-800">
                            <div className={`h-full rounded-full ${barTone(row.value)}`} style={{ width: `${clamp(row.value)}%` }} />
                        </div>
                    </div>
                ))}
            </div>
        </TerminalCard>
    );
}