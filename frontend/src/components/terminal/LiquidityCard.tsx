import { DecisionContext } from "../../contracts/DecisionContext";
import TerminalCard from "./TerminalCard";

type Props = {
    liquidity: DecisionContext["liquidity"];
};

export default function LiquidityCard({ liquidity }: Props) {
    const rows = [
        { label: "Liquidity Sweep", value: liquidity.sweep },
        { label: "Internal Liquidity", value: liquidity.internal },
        { label: "External Liquidity", value: liquidity.external },
    ];

    return (
        <TerminalCard title="Liquidity" eyebrow="Panel 6">
            <div className="space-y-3">
                <div className="grid gap-3 md:grid-cols-3">
                    {rows.map((row) => (
                        <div key={row.label} className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
                            <p className="text-[11px] uppercase tracking-[0.22em] text-slate-500">{row.label}</p>
                            <p className="mt-2 text-sm font-semibold text-slate-100">{row.value}</p>
                        </div>
                    ))}
                </div>

                <div className="rounded-xl border border-slate-800 bg-slate-900/70 p-3">
                    <p className="text-[11px] uppercase tracking-[0.22em] text-slate-500">Detected Levels</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                        {liquidity.levels.map((level) => (
                            <span key={level} className="rounded-full border border-slate-700 bg-slate-950/80 px-3 py-1 text-xs text-slate-300">
                                {level}
                            </span>
                        ))}
                    </div>
                </div>
            </div>
        </TerminalCard>
    );
}