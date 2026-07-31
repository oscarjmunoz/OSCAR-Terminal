import { ReactNode } from "react";

import Header from "./Header";
import Sidebar from "./Sidebar";
import StatusBar from "./StatusBar";

type Props = {
  children?: ReactNode;
};

export default function DecisionCenterLayout({ children }: Props) {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Header />
      <StatusBar />

      <div className="flex">
        <Sidebar />

        <main className="flex-1 p-6">
          <div className="grid gap-6 xl:grid-cols-3">
            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Market Bias</h2>
                <span className="rounded-full bg-emerald-500/15 px-2.5 py-1 text-xs font-semibold text-emerald-400">Bullish</span>
              </div>
              <p className="text-sm leading-6 text-slate-400">
                Trend alignment, liquidity pockets, and execution context remain favorable for continuation setups.
              </p>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">OSCAR Decision</h2>
                <span className="rounded-full bg-sky-500/15 px-2.5 py-1 text-xs font-semibold text-sky-400">Ready</span>
              </div>
              <p className="text-sm leading-6 text-slate-400">
                The model is aligned with structure and risk management rules before any trade is considered.
              </p>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Trade Risk</h2>
                <span className="rounded-full bg-amber-500/15 px-2.5 py-1 text-xs font-semibold text-amber-400">1.5%</span>
              </div>
              <p className="text-sm leading-6 text-slate-400">
                Preserve capital with disciplined stop placement, position sizing, and exposure control.
              </p>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20 xl:col-span-1">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Setup Checklist</h2>
                <span className="text-xs text-slate-500">4/5</span>
              </div>
              <ul className="space-y-2 text-sm text-slate-400">
                <li>• Structure confirms bias</li>
                <li>• Entry is above key liquidity</li>
                <li>• Stop respects invalidation</li>
                <li>• Risk stays within plan</li>
              </ul>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20 xl:col-span-1">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Mini Chart</h2>
                <span className="text-xs text-slate-500">M5</span>
              </div>
              <div className="min-h-[360px] overflow-hidden rounded-xl border border-slate-800 bg-slate-950/80 p-2">
                {children}
              </div>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20 xl:col-span-1">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Trading Plan</h2>
                <span className="text-xs text-slate-500">USDCHF.pro</span>
              </div>
              <p className="text-sm leading-6 text-slate-400">
                Wait for a retracement into the order block, then confirm momentum before entering with trend alignment.
              </p>
            </section>
          </div>
        </main>
      </div>
    </div>
  );
}