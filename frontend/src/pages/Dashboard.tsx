import { useEffect, useMemo, useState } from "react";

import TerminalDashboard from "../components/terminal/TerminalDashboard";
import { DecisionContext } from "../contracts/DecisionContext";
import DecisionCenterLayout from "../layouts/DecisionCenterLayout";
import { LiveDecisionContextProvider } from "../services/decisionContext";

const DEFAULT_SYMBOL = "USDCHF.pro";

export default function Dashboard() {
  const [context, setContext] = useState<DecisionContext | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState("Dashboard");

  const provider = useMemo(() => new LiveDecisionContextProvider(), []);

  useEffect(() => {
    let mounted = true;

    async function load() {
      try {
        const nextContext = await provider.load(DEFAULT_SYMBOL);
        if (!mounted) return;
        setContext(nextContext);
      } catch (error) {
        console.error(error);
        if (mounted) {
          setContext(null);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    load();
    const timer = window.setInterval(load, 3000);

    return () => {
      mounted = false;
      window.clearInterval(timer);
    };
  }, [provider]);

  return (
    <DecisionCenterLayout
      header={
        context?.header ?? {
          symbol: DEFAULT_SYMBOL,
          timeframe: "M5",
          date: new Date().toLocaleString(),
          session: "UNKNOWN",
          connection: loading ? "DEGRADED" : "OFFLINE",
          latencyMs: null,
        }
      }
      activeSection={activeSection}
      onSelectSection={setActiveSection}
    >
      <TerminalDashboard context={context} />
    </DecisionCenterLayout>
  );
}