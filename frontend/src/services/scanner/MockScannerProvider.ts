import { ScannerItem } from "../../models/ScannerItem";
import { ScannerProvider } from "./ScannerProvider";

const MOCK_SCANNER_ITEMS: ScannerItem[] = [
  {
    symbol: "EURUSD",
    decision: "WAIT",
    score: 52,
    confidence: 58,
    trend: "RANGE",
    timeframe: "M5",
    strategy: "ICT",
  },
  {
    symbol: "GBPUSD",
    decision: "SELL",
    score: 68,
    confidence: 64,
    trend: "BEARISH",
    timeframe: "M5",
    strategy: "ICT",
  },
  {
    symbol: "USDCHF",
    decision: "BUY",
    score: 74,
    confidence: 71,
    trend: "BULLISH",
    timeframe: "M5",
    strategy: "ICT",
  },
  {
    symbol: "XAUUSD",
    decision: "WAIT",
    score: 49,
    confidence: 55,
    trend: "RANGE",
    timeframe: "M5",
    strategy: "ICT",
  },
  {
    symbol: "NAS100",
    decision: "BUY",
    score: 62,
    confidence: 60,
    trend: "BULLISH",
    timeframe: "M5",
    strategy: "ICT",
  },
];

export class MockScannerProvider implements ScannerProvider {
  async getScannerItems(): Promise<ScannerItem[]> {
    return MOCK_SCANNER_ITEMS;
  }
}
