import { ScannerItem } from "../../models/ScannerItem";

export interface ScannerProvider {
  getScannerItems(): Promise<ScannerItem[]>;
}
