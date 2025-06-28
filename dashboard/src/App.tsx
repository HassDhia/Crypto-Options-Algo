import React from "react";
import Dashboard from "./Dashboard";
import KpiRibbon from "./components/KpiRibbon";
import ScoutedTable from "./components/ScoutedTable";
import ExecutedTradesTable from "./components/ExecutedTradesTable";
import RiskAlertsList from "./components/RiskAlertsList";
import RLParametersChart from "./components/RLParametersChart";
import SizingSignalsTable from "./components/SizingSignalsTable";

/** Root application component with global styling */
const App: React.FC = () => {
  console.log('App component rendered');
  return (
    <div className="min-h-screen bg-gray-100 text-gray-900">
      {/* App Header */}
      <header className="p-6 text-2xl font-bold">Crypto Options Dashboard</header>

      {/* Main Dashboard Content - Render components individually */}
      <main className="p-6 space-y-6">
        <h2 className="text-xl font-semibold">Component Debugging</h2>
        <div className="border p-4">
          <h3 className="font-medium mb-2">KpiRibbon</h3>
          <KpiRibbon />
        </div>
        <div className="border p-4">
          <h3 className="font-medium mb-2">ScoutedTable</h3>
          <ScoutedTable />
        </div>
        <div className="border p-4">
          <h3 className="font-medium mb-2">ExecutedTradesTable</h3>
          <ExecutedTradesTable />
        </div>
        <div className="border p-4">
          <h3 className="font-medium mb-2">RiskAlertsList</h3>
          <RiskAlertsList />
        </div>
        <div className="border p-4">
          <h3 className="font-medium mb-2">RLParametersChart</h3>
          <RLParametersChart />
        </div>
        <div className="border p-4">
          <h3 className="font-medium mb-2">SizingSignalsTable</h3>
          <SizingSignalsTable />
        </div>
      </main>
    </div>
  );
};

export default App;
