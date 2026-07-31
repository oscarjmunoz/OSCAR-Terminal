import { useEffect, useMemo, useState } from "react";

import { ScannerItem } from "../models/ScannerItem";
import { ScannerService } from "../services/scanner";

type Props = {
  selectedSymbol: string;
  onSelect: (symbol: string) => void;
};

function decisionTone(decision: ScannerItem["decision"]): string {
  if (decision === "BUY") return "text-emerald-300";
  if (decision === "SELL") return "text-rose-300";
  return "text-amber-300";
}

export default function SmartScanner({ selectedSymbol, onSelect }: Props) {
  const service = useMemo(() => new ScannerService(), []);
  const [rows, setRows] = useState<ScannerItem[]>([]);

  useEffect(() => {
    let mounted = true;

    async function loadRows() {
      try {
        const scannerItems = await service.getScannerItems();
        if (!mounted) return;
        setRows(scannerItems);
      } catch (error) {
        console.error(error);
      }
    }

    loadRows();

    return () => {
      mounted = false;
    };
  }, [service]);

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/80 p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Smart Market Scanner</h2>
        <span className="rounded-full border border-slate-700 bg-slate-950/70 px-3 py-1 text-xs font-semibold text-slate-300">
          MOCK
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr className="text-xs uppercase tracking-wide text-slate-400">
              <th className="px-3 py-2">Symbol</th>
              <th className="px-3 py-2">Decision</th>
              <th className="px-3 py-2">Oscar Score</th>
              <th className="px-3 py-2">Confidence</th>
              <th className="px-3 py-2">Trend</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const active = row.symbol === selectedSymbol;

              return (
                <tr
                  key={row.symbol}
                  className={
                    active
                      ? "border-t border-slate-800 bg-sky-500/10"
                      : "border-t border-slate-800 bg-slate-950/40"
                  }
                >
                  <td className="px-3 py-2">
                    <button
                      type="button"
                      onClick={() => onSelect(row.symbol)}
                      className={
                        active
                          ? "font-semibold text-sky-200"
                          : "font-semibold text-slate-200 hover:text-white"
                      }
                    >
                      {row.symbol}
                    </button>
                  </td>
                  <td className={`px-3 py-2 font-semibold ${decisionTone(row.decision)}`}>{row.decision}</td>
                  <td className="px-3 py-2 text-slate-200">{row.score}</td>
                  <td className="px-3 py-2 text-slate-200">{row.confidence}%</td>
                  <td className="px-3 py-2 text-slate-300">{row.trend}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
