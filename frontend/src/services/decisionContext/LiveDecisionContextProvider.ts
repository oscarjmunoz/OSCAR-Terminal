import { LiveDataOrchestrator } from "../../core/LiveDataOrchestrator";
import { DecisionContext } from "../../contracts/DecisionContext";
import { DecisionContextProvider } from "./DecisionContextProvider";
import { buildDecisionContext } from "./decisionContextBuilder";

const DEFAULT_SYMBOL = "USDCHF.pro";

export class LiveDecisionContextProvider implements DecisionContextProvider {
    constructor(private readonly orchestrator = new LiveDataOrchestrator()) { }

    async load(symbol: string): Promise<DecisionContext | null> {
        try {
            const snapshot = await this.orchestrator.refreshSnapshot(symbol || DEFAULT_SYMBOL);
            const output = this.orchestrator.runEngines(snapshot);

            return buildDecisionContext(
                {
                    symbol: snapshot.symbol,
                    timeframe: "M5",
                    timestamp: snapshot.timestamp,
                    analysis: output.institutional.M5,
                    latencyMs: null,
                },
                output
            );
        } catch (error) {
            console.error(error);
            return null;
        }
    }
}

export { buildDecisionContext };