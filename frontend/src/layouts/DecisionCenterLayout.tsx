import { ReactNode } from "react";

import Header from "./Header";
import Sidebar from "./Sidebar";
import { DecisionHeaderContext } from "../contracts/DecisionContext";

type Props = {
  header: DecisionHeaderContext;
  activeSection: string;
  onSelectSection?: (section: string) => void;
  children?: ReactNode;
};

export default function DecisionCenterLayout({ header, activeSection, onSelectSection, children }: Props) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.10),_transparent_34%),radial-gradient(circle_at_top_right,_rgba(16,185,129,0.08),_transparent_24%),linear-gradient(180deg,_#020617_0%,_#020617_100%)] text-white">
      <Header context={header} />

      <div className="mx-auto flex max-w-[1800px] flex-col lg:flex-row">
        <Sidebar activeItem={activeSection} onSelect={onSelectSection} />

        <main className="min-w-0 flex-1 p-4 sm:p-5 lg:p-6 xl:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}