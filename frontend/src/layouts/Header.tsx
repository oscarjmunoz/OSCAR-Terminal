// frontend/src/components/layout/Header.tsx

import { Bell, Activity, Wifi } from "lucide-react";

export default function Header() {
    return (
        <header className="h-16 border-b border-slate-800 bg-slate-900 px-6">

            <div className="flex h-full items-center justify-between">

                <div>

                    <h1 className="text-xl font-bold tracking-wide text-white">
                        OSCAR Lite
                    </h1>

                    <p className="text-xs text-slate-400">
                        Decision Center
                    </p>

                </div>

                <div className="flex items-center gap-8">

                    <div className="text-right">

                        <p className="text-xs text-slate-500">
                            Symbol
                        </p>

                        <p className="font-semibold text-white">
                            USDCHF.pro
                        </p>

                    </div>

                    <div className="text-right">

                        <p className="text-xs text-slate-500">
                            Timeframe
                        </p>

                        <p className="font-semibold text-white">
                            M5
                        </p>

                    </div>

                    <div className="flex items-center gap-2 rounded-lg bg-emerald-500/15 px-3 py-2">

                        <Activity
                            size={16}
                            className="text-emerald-400"
                        />

                        <span className="text-sm font-semibold text-emerald-400">
                            LIVE
                        </span>

                    </div>

                    <button
                        className="rounded-lg border border-slate-700 p-2 text-slate-300 transition hover:border-blue-500 hover:text-white"
                    >
                        <Bell size={18} />
                    </button>

                    <button
                        className="rounded-lg border border-slate-700 p-2 text-slate-300 transition hover:border-blue-500 hover:text-white"
                    >
                        <Wifi size={18} />
                    </button>

                </div>

            </div>

        </header>
    );
}