import { DecisionContext } from "../../contracts/DecisionContext";

export interface DecisionContextProvider {
    load(symbol: string): Promise<DecisionContext | null>;
}