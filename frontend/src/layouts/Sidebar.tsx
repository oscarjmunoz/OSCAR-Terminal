import { BarChart3, BookOpen, ChartCandlestick, LayoutDashboard, LineChart, Settings } from "lucide-react";

const items = [
  { icon: LayoutDashboard, label: "Dashboard" },
  { icon: ChartCandlestick, label: "Terminal" },
  { icon: BookOpen, label: "Journal" },
  { icon: LineChart, label: "Backtesting" },
  { icon: BarChart3, label: "Statistics" },
  { icon: Settings, label: "Settings" },
];

type Props = {
  activeItem: string;
  onSelect?: (label: string) => void;
};

export default function Sidebar({ activeItem, onSelect }: Props) {
  return (
    <aside className="border-b border-slate-800/80 bg-slate-950/85 lg:min-h-[calc(100vh-184px)] lg:w-[280px] lg:border-b-0 lg:border-r">
      <nav className="grid grid-cols-2 gap-3 p-4 sm:grid-cols-3 lg:flex lg:flex-col lg:gap-2 lg:p-5">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = activeItem === item.label;

          return (
            <button
              key={item.label}
              type="button"
              onClick={() => onSelect?.(item.label)}
              className={`group flex items-center gap-3 rounded-2xl border px-4 py-3 text-left transition-colors ${
                isActive
                  ? "border-sky-500/30 bg-sky-500/10 text-sky-200"
                  : "border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700 hover:text-slate-100"
              }`}
            >
              <div className={`rounded-xl border p-2 ${isActive ? "border-sky-500/30 bg-sky-500/10" : "border-slate-700 bg-slate-900/70"}`}>
                <Icon size={18} />
              </div>
              <span className="text-sm font-semibold tracking-tight">{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}