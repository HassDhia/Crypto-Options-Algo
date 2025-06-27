import React, { useEffect, useState } from "react";
import { fetchExecutedTrades } from "../api";
import type { ExecutedTrade } from "../api";
import { Loader } from "lucide-react";

const ExecutedTradesTable: React.FC = () => {
  const [trades, setTrades] = useState<ExecutedTrade[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Poll executed trades every 5 seconds
  useEffect(() => {
    let isMounted = true;
    const loadTrades = async () => {
      try {
        setError(null);
        const result = await fetchExecutedTrades();
        if (isMounted) {
          setTrades(result);
          setLoading(false);
        }
      } catch (err) {
        if (isMounted) {
          setError(err as Error);
          setLoading(false);
        }
      }
    };
    loadTrades();
    const intervalId = setInterval(loadTrades, 5000);
    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  return (
    <div className="bg-white rounded shadow p-4 w-full">
      <h3 className="text-lg font-semibold mb-3">Executed Trades</h3>
      {loading ? (
        <div className="text-gray-600 flex items-center">
          <Loader className="w-4 h-4 mr-2 animate-spin" /> Loading executed trades...
        </div>
      ) : error ? (
        <div className="text-red-600">Error: {error.message}</div>
      ) : (
        <table className="w-full text-sm border-collapse">
          <thead className="border-b text-gray-700">
            <tr>
              <th className="p-2 text-left">Instrument</th>
              <th className="p-2 text-left">Side</th>
              <th className="p-2 text-right">Size</th>
              <th className="p-2 text-right">Price</th>
              <th className="p-2 text-left">Time</th>
            </tr>
          </thead>
          <tbody>
            {trades!.map((trade, idx) => (
              <tr key={idx} className="border-b last:border-0 hover:bg-gray-50">
                <td className="p-2">{trade.instrument}</td>
                <td className="p-2">{trade.side}</td>
                <td className="p-2 text-right">{trade.size}</td>
                <td className="p-2 text-right">{trade.price.toFixed(3)}</td>
                <td className="p-2 text-left">
                  {new Date(trade.timestamp).toLocaleTimeString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default ExecutedTradesTable;
