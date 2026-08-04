import { DecisionContext } from "../../contracts/DecisionContext";
import TerminalCard from "./TerminalCard";

type Props = {
    structure: DecisionContext["structure"];
};

export default function StructureCard({ structure }: Props) {
    const rows = [
        { label: "BOS", value: structure.bos },
        { label: "CHOCH", value: structure.choch },
        { label: "MSS", value: structure.mss },
        { label: "Trend", value: structure.trend },
    ];

    return (
        <TerminalCard title="Structure" eyebrow="Panel 7">
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                {rows.map((row) => (
                    <div key={row.label} className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
                        <p className="text-[11px] uppercase tracking-[0.22em] text-slate-500">{row.label}</p>
                        <p className="mt-2 text-sm font-semibold text-slate-100">{row.value}</p>
                    </div>
                ))}
            </div>
        </TerminalCard>
    );
}