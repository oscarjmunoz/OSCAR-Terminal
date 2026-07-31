import { ReactNode } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Circle,
  TrendingDown,
  TrendingUp,
  Wifi,
  WifiOff,
} from "lucide-react";

import Header from "./Header";
import Sidebar from "./Sidebar";
import StatusBar from "./StatusBar";

type Props = {
  children?: ReactNode;
  trend?: "BULLISH" | "BEARISH" | "RANGE" | "UNKNOWN";
  bos?: boolean;
  choch?: boolean;
  mss?: boolean;
  connected?: boolean;
  spread?: number;
  symbol?: string;
  timeframe?: string;
};

export default function DecisionCenterLayout({
  children,
  trend = "UNKNOWN",
  bos = false,
  choch = false,
  mss = false,
  connected = false,
  spread,
  symbol = "USDCHF.pro",
  timeframe = "M5",
}: Props) {
  const normalizedTrend = trend.toUpperCase();
  const isBullish = normalizedTrend === "BULLISH";
  const isBearish = normalizedTrend === "BEARISH";
  const isRange = normalizedTrend === "RANGE";

  const biasColor = isBullish
    ? "bg-emerald-500/15 text-emerald-400"
    : isBearish
      ? "bg-rose-500/15 text-rose-400"
      : isRange
        ? "bg-amber-500/15 text-amber-400"
        : "bg-slate-500/15 text-slate-300";

  const strength = bos || choch || mss ? "High" : normalizedTrend === "UNKNOWN" ? "Medium" : "Medium";

  let decision = "NO TRADE";
  let decisionTone = "bg-slate-500/15 text-slate-300";
  let explanation = "No structure is clear enough to justify participation.";

  if (isBullish && bos) {
    decision = "BUY";
    decisionTone = "bg-emerald-500/15 text-emerald-400";
    explanation = "Bullish trend with BOS confirms continuation intent.";
  } else if (isBearish && bos) {
    decision = "SELL";
    decisionTone = "bg-rose-500/15 text-rose-400";
    explanation = "Bearish trend with BOS supports downside continuation.";
  } else if (choch) {
    decision = "WAIT";
    decisionTone = "bg-amber-500/15 text-amber-400";
    explanation = "CHoCH suggests a pause while structure re-evaluates.";
  }

  const plan =
    decision === "BUY"
      ? "Wait for pullback. Buy only. Respect risk."
      : decision === "SELL"
        ? "Wait for pullback. Sell only. Respect risk."
        : decision === "WAIT"
          ? "Wait for confirmation. Avoid premature entries."
          : "No trade. Observe structure and wait for clarity.";

  const checklist = [
    { label: "BOS", done: bos },
    { label: "CHoCH", done: choch },
    { label: "MSS", done: mss },
    { label: "Trend", done: normalizedTrend !== "UNKNOWN" },
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Header />
      <StatusBar />

      <div className="flex flex-col lg:flex-row">
        <Sidebar />

        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <div className="grid gap-6 xl:grid-cols-3">
            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Market Bias</h2>
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${biasColor}`}>
                  {normalizedTrend || "UNKNOWN"}
                </span>
              </div>
              <p className="text-sm text-slate-400">Trend</p>
              <p className="mt-1 text-2xl font-semibold text-white">{normalizedTrend}</p>
              <div className="mt-4 flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/70 px-3 py-2">
                <span className="text-sm text-slate-400">Strength</span>
                <span className="text-sm font-semibold text-white">{strength}</span>
              </div>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20 xl:col-span-1">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">OSCAR Decision</h2>
                <span className={`rounded-full px-2.5 py-1 text-xs font-semibold ${decisionTone}`}>
                  {decision}
                </span>
              </div>
              <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                <p className="text-4xl font-black tracking-wide text-white">{decision}</p>
                <p className="mt-3 text-sm leading-6 text-slate-400">{explanation}</p>
              </div>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Trade Risk</h2>
                <span className="rounded-full bg-amber-500/15 px-2.5 py-1 text-xs font-semibold text-amber-400">Live</span>
              </div>
              <div className="space-y-3 text-sm text-slate-400">
                <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/70 px-3 py-2">
                  <span>Spread</span>
                  <span className="font-semibold text-white">{spread !== undefined ? `${spread.toFixed(1)} pips` : "-"}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/70 px-3 py-2">
                  <span>Symbol</span>
                  <span className="font-semibold text-white">{symbol}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/70 px-3 py-2">
                  <span>Timeframe</span>
                  <span className="font-semibold text-white">{timeframe}</span>
                </div>
                <div className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/70 px-3 py-2">
                  <span>MT5</span>
                  <span className={`flex items-center gap-2 font-semibold ${connected ? "text-emerald-400" : "text-rose-400"}`}>
                    {connected ? <Wifi size={16} /> : <WifiOff size={16} />}
                    {connected ? "Connected" : "Offline"}
                  </span>
                </div>
              </div>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20 xl:col-span-1">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Setup Checklist</h2>
                <span className="text-xs text-slate-500">{checklist.filter((item) => item.done).length}/{checklist.length}</span>
              </div>
              <ul className="space-y-2 text-sm text-slate-400">
                {checklist.map((item) => (
                  <li key={item.label} className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-950/70 px-3 py-2">
                    {item.done ? <CheckCircle2 size={16} className="text-emerald-400" /> : <Circle size={16} className="text-slate-500" />}
                    <span>{item.label}</span>
                  </li>
                ))}
              </ul>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20 xl:col-span-1">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Mini Chart</h2>
                <span className="text-xs text-slate-500">{timeframe}</span>
              </div>
              <div className="min-h-[360px] overflow-hidden rounded-xl border border-slate-800 bg-slate-950/80 p-2">
                {children}
              </div>
            </section>

            <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5 shadow-2xl shadow-black/20 xl:col-span-1">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Trading Plan</h2>
                <span className="text-xs text-slate-500">Auto</span>
              </div>
              <div className="rounded-2xl border border-slate-800 bg-slate-950/70 p-4">
                <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-white">
                  {decision === "BUY" ? <TrendingUp size={18} className="text-emerald-400" /> : null}
                  {decision === "SELL" ? <TrendingDown size={18} className="text-rose-400" /> : null}
                  {decision === "WAIT" ? <AlertTriangle size={18} className="text-amber-400" /> : null}
                  {decision === "NO TRADE" ? <Circle size={18} className="text-slate-400" /> : null}
                  <span>{decision}</span>
                </div>
                <p className="text-sm leading-6 text-slate-400">{plan}</p>
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>
  );
}