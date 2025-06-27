import React, { useEffect, useState } from "react";
import { fetchScoutedCandidates } from "../api";
import type { ScoutedTick } from "../api";
import { Loader } from "lucide-react";

const ScoutedTable: React.FC = () => {
  const [data, setData] = useState<ScoutedTick[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Polling effect to fetch scouted candidates every 5 seconds
  useEffect(() => {
    let isMounted = true;
    const loadData = async () => {
      try {
        setError(null);
        const result = await fetchScoutedCandidates();
        if (isMounted) {
          setData(result);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err as Error);
          setLoading(false);
        }
      }
    };
    // initial load
    loadData();
    // poll interval
    const intervalId = setInterval(loadData, 5000);
    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  return (
    <div className="bg-white rounded shadow p-4 w-full">
      <h3 className="text-lg font-semibold mb-3">Scouted Candidates</h3>
      {loading ? (
        <div className="text-gray-600 flex items-center">
          <Loader className="w-4 h-4 mr-2 animate-spin" /> Loading scouted ticks...
        </div>
      ) : error ? (
        <div className="text-red-600">Error: {error.message}</div>
      ) : (
        <table className="w-full text-sm border-collapse">
          <thead className="border-b text-gray-700">
            <tr>
              <th className="p-2 text-left">Instrument</th>
              <th className="p-2 text-right">Bid</th>
              <th className="p-2 text-right">Ask</th>
              <th className="p-2 text-left">Time</th>
            </tr>
          </thead>
          <tbody>
            {data!.map((tick) => (
              <tr key={`${tick.instrument}-${tick.timestamp}`} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2">{tick.instrument}</td>
                <td className="p-2 text-right">{tick.bid.toFixed(3)}</td>
                <td className="p-2 text-right">{tick.ask.toFixed(3)}</td>
                <td className="p-2 text-left">
                  {new Date(tick.timestamp).toLocaleTimeString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ScoutedTable;
