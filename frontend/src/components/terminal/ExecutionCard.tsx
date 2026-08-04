import { DecisionContext } from "../../contracts/DecisionContext";
import TerminalCard from "./TerminalCard";

type Props = {
    execution: DecisionContext["execution"];
};

export default function ExecutionCard({ execution }: Props) {
    const rows = [
        { label: "Entry", value: execution?.entry ?? "N/A" },
        { label: "Stop", value: execution?.stop ?? "N/A" },
        { label: "TP1", value: execution?.tp1 ?? "N/A" },
        { label: "TP2", value: execution?.tp2 ?? "N/A" },
        { label: "RR", value: execution?.rr ?? "N/A" },
    ];

    return (
        <TerminalCard title="Execution" eyebrow="Panel 11">
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
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