import React, { useEffect, useState } from "react";
import { fetchRiskAlerts } from "../api";
import type { RiskAlert } from "../api";
import { AlertTriangle, AlertCircle, CheckCircle, Loader } from "lucide-react";

const RiskAlertsList: React.FC = () => {
  const [alerts, setAlerts] = useState<RiskAlert[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Poll risk alerts every 5 seconds
  useEffect(() => {
    let isMounted = true;
    const loadAlerts = async () => {
      try {
        setError(null);
        const result = await fetchRiskAlerts();
        if (isMounted) {
          setAlerts(result);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err as Error);
          setLoading(false);
        }
      }
    };
    loadAlerts();
    const intervalId = setInterval(loadAlerts, 5000);
    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  // Helper to get icon and color for risk level
  const RiskIcon: React.FC<{ level: string }> = ({ level }) => {
    if (level === "HIGH") return <AlertTriangle className="w-4 h-4 text-red-600" />;
    if (level === "MEDIUM") return <AlertCircle className="w-4 h-4 text-orange-500" />;
    return <CheckCircle className="w-4 h-4 text-green-600" />;  // LOW
  };

  return (
    <div className="bg-white rounded shadow p-4 w-full">
      <h3 className="text-lg font-semibold mb-3">Risk Alerts</h3>
      {loading ? (
        <div className="text-gray-600 flex items-center">
          <Loader className="w-4 h-4 mr-2 animate-spin" /> Loading risk alerts...
        </div>
      ) : error ? (
        <div className="text-red-600">Error: {error.message}</div>
      ) : alerts!.length === 0 ? (
        <div className="text-gray-600">No active risk alerts.</div>
      ) : (
        <table className="w-full text-sm border-collapse">
          <thead className="border-b text-gray-700">
            <tr>
              <th className="p-2 text-left">Instrument</th>
              <th className="p-2 text-left">Level</th>
              <th className="p-2 text-left">Action</th>
              <th className="p-2 text-left">Time</th>
            </tr>
          </thead>
          <tbody>
            {alerts!.map((alert, idx) => (
              <tr key={idx} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2 flex items-center">
                  <RiskIcon level={alert.riskLevel} />
                  <span className="ml-2">{alert.instrument}</span>
                </td>
                <td className="p-2">
                  {/* Color-code risk level text */}
                  <span className={
                    alert.riskLevel === "HIGH" ? "text-red-600 font-semibold" :
                    alert.riskLevel === "MEDIUM" ? "text-orange-600 font-medium" :
                    "text-green-600 font-medium"
                  }>
                    {alert.riskLevel}
                  </span>
                </td>
                <td className="p-2">{alert.recommendedAction}</td>
                <td className="p-2">{new Date(alert.timestamp).toLocaleTimeString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default RiskAlertsList;
