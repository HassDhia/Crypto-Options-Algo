import React from "react";
import ScoutedTable from "./components/ScoutedTable";
import ExecutedTradesTable from "./components/ExecutedTradesTable";
import RiskAlertsList from "./components/RiskAlertsList";
import RLParametersChart from "./components/RLParametersChart";
import SizingSignalsTable from "./components/SizingSignalsTable";

/** Dashboard layout grouping all sections */
const Dashboard: React.FC = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Left column: Scouted and Executed sections */}
      <div className="space-y-6">
        <ScoutedTable />
        <ExecutedTradesTable />
      </div>
      {/* Right column: RL Parameters, Risk Alerts, and Sizing Signals sections */}
      <div className="space-y-6">
        <RLParametersChart />
        <RiskAlertsList />
        <SizingSignalsTable />
      </div>
    </div>
  );
};

export default Dashboard;
