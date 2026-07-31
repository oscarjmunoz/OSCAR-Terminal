export default function StatusBar() {
  return (
    <div className="flex items-center justify-between border-b border-slate-800 bg-slate-950 px-6 py-3 text-sm">
      <div className="flex items-center gap-6">
        <span className="text-slate-300">
          🌍 London Session
        </span>

        <span className="text-slate-300">
          🕒 09:35 NY
        </span>

        <span className="text-green-400">
          🟢 Market Open
        </span>
      </div>

      <div className="flex items-center gap-6">
        <span className="text-slate-400">
          News: None
        </span>

        <span className="text-slate-400">
          Refresh: 3s
        </span>
      </div>
    </div>
  );
}