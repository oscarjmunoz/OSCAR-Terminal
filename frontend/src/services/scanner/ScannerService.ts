import { ScannerItem } from "../../models/ScannerItem";
import { MockScannerProvider } from "./MockScannerProvider";
import { ScannerProvider } from "./ScannerProvider";

export class ScannerService {
  constructor(private readonly provider: ScannerProvider = new MockScannerProvider()) {}

  async getScannerItems(): Promise<ScannerItem[]> {
    return this.provider.getScannerItems();
  }
}
