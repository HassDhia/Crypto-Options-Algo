import React, { useEffect, useState } from "react";
import { fetchSizingSignals } from "../api";
import type { SizeSignal } from "../api";
import { Loader } from "lucide-react";

const SizingSignalsTable: React.FC = () => {
  const [signals, setSignals] = useState<SizeSignal[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Poll sizing signals every 5 seconds
  useEffect(() => {
    let isMounted = true;
    const loadSignals = async () => {
      try {
        setError(null);
        const result = await fetchSizingSignals();
        if (isMounted) {
          setSignals(result);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err as Error);
          setLoading(false);
        }
      }
    };
    loadSignals();
    const intervalId = setInterval(loadSignals, 5000);
    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  return (
    <div className="bg-white rounded shadow p-4 w-full">
      <h3 className="text-lg font-semibold mb-3">Sizing Signals</h3>
      {loading ? (
        <div className="text-gray-600 flex items-center">
          <Loader className="w-4 h-4 mr-2 animate-spin" /> Loading sizing signals...
        </div>
      ) : error ? (
        <div className="text-red-600">Error: {error.message}</div>
      ) : signals!.length === 0 ? (
        <div className="text-gray-600">No sizing signals available.</div>
      ) : (
        <table className="w-full text-sm border-collapse">
          <thead className="border-b text-gray-700">
            <tr>
              <th className="p-2 text-left">Instrument</th>
              <th className="p-2 text-right">Size</th>
              <th className="p-2 text-left">Time</th>
            </tr>
          </thead>
          <tbody>
            {signals!.map((sig, idx) => (
              <tr key={idx} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2">{sig.instrument}</td>
                <td className="p-2 text-right">{sig.size}</td>
                <td className="p-2 text-left">
                  {new Date(sig.timestamp).toLocaleTimeString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default SizingSignalsTable;
