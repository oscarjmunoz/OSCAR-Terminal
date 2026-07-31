import { ReactNode } from "react";

import Header from "./Header";
import Sidebar from "./Sidebar";
import StatusBar from "./StatusBar";

type Props = {
  children?: ReactNode;
};

export default function DecisionCenterLayout({ children }: Props) {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <Header />
      <StatusBar />

      <div className="flex flex-col lg:flex-row">
        <Sidebar />

        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}