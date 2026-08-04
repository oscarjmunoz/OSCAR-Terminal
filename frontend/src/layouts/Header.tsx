import { Activity, AlertTriangle, Clock3, Gauge, Sigma, Waves } from "lucide-react";

import { DecisionHeaderContext } from "../contracts/DecisionContext";

type Props = {
    context: DecisionHeaderContext;
};

function metaItem(label: string, value: string | number | null) {
    return (
        <div className="rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2">
            <p className="text-[10px] uppercase tracking-[0.24em] text-slate-500">{label}</p>
            <p className="mt-1 text-sm font-semibold text-slate-100">{value ?? "N/A"}</p>
        </div>
    );
}

export default function Header({ context }: Props) {
    const connectionClass =
        context.connection === "LIVE"
            ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
            : context.connection === "DEGRADED"
                ? "border-amber-500/30 bg-amber-500/10 text-amber-300"
                : "border-rose-500/30 bg-rose-500/10 text-rose-300";

    return (
        <header className="border-b border-slate-800/80 bg-slate-950/90 backdrop-blur-xl">
            <div className="mx-auto flex max-w-[1800px] flex-col gap-4 px-4 py-4 lg:px-6 xl:px-8">
                <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
                    <div className="flex items-center gap-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-sky-500/20 bg-sky-500/10 text-sky-300 shadow-[0_0_40px_rgba(56,189,248,0.18)]">
                            <Sigma size={22} />
                        </div>
                        <div>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.34em] text-slate-500">OSCAR</p>
                            <h1 className="text-xl font-black tracking-tight text-slate-50 sm:text-2xl">OSCAR Terminal IA</h1>
                            <p className="mt-1 text-xs text-slate-400">Institutional DecisionContext viewer</p>
                        </div>
                    </div>

                    <div className={`inline-flex w-fit items-center gap-2 rounded-full border px-3 py-2 text-xs font-semibold uppercase tracking-[0.22em] ${connectionClass}`}>
                        <Activity size={14} />
                        {context.connection}
                    </div>
                </div>

                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-6">
                    {metaItem("Active Symbol", context.symbol)}
                    {metaItem("Timeframe", context.timeframe)}
                    {metaItem("Date", context.date)}
                    {metaItem("Session", context.session)}
                    {metaItem("Latency", context.latencyMs === null ? "N/A" : `${context.latencyMs} ms`)}
                    <div className="rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2">
                        <p className="text-[10px] uppercase tracking-[0.24em] text-slate-500">State</p>
                        <div className="mt-1 flex items-center gap-2 text-sm font-semibold text-slate-100">
                            <Gauge size={14} className="text-sky-300" />
                            {context.connection === "LIVE" ? "Connected to pipeline" : "Waiting for pipeline"}
                        </div>
                    </div>
                </div>

                <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-3">
                    <div className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-300">
                        <Clock3 size={14} className="text-sky-300" />
                        Institutional clock synchronized
                    </div>
                    <div className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-300">
                        <Waves size={14} className="text-emerald-300" />
                        Market structure visible
                    </div>
                    <div className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-slate-300">
                        <AlertTriangle size={14} className="text-amber-300" />
                        Warnings surfaced in panel 10
                    </div>
                </div>
            </div>
        </header>
    );
}