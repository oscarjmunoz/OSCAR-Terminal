import {
  LayoutDashboard,
  LineChart,
  BookOpen,
  Settings,
} from "lucide-react";

const items = [
  {
    icon: LayoutDashboard,
    label: "Dashboard",
  },
  {
    icon: LineChart,
    label: "Scanner",
  },
  {
    icon: BookOpen,
    label: "Journal",
  },
  {
    icon: Settings,
    label: "Settings",
  },
];

export default function Sidebar() {
  return (
    <aside className="w-20 border-r border-slate-800 bg-slate-900 min-h-[calc(100vh-64px)]">
      <nav className="flex flex-col items-center gap-6 py-6">
        {items.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.label}
              className="group flex flex-col items-center gap-2 text-slate-400 hover:text-white transition-colors"
            >
              <div className="rounded-xl border border-slate-700 p-3 group-hover:border-blue-500">
                <Icon size={22} />
              </div>

              <span className="text-[11px]">
                {item.label}
              </span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}