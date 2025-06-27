import React, { useEffect, useState } from "react";
import { fetchRLParameters } from "../api";
import type { FilterParamPoint } from "../api";
import { Loader } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

const RLParametersChart: React.FC = () => {
  const [data, setData] = useState<FilterParamPoint[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  // Poll RL parameters every 10 seconds (slower, as these might update less frequently)
  useEffect(() => {
    let isMounted = true;
    const loadParams = async () => {
      try {
        setError(null);
        const result = await fetchRLParameters();
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
    loadParams();
    const intervalId = setInterval(loadParams, 10000);
    return () => {
      isMounted = false;
      clearInterval(intervalId);
    };
  }, []);

  return (
    <div className="bg-white rounded shadow p-4 w-full">
      <h3 className="text-lg font-semibold mb-3">RL-Tuned Filter Parameters</h3>
      {loading ? (
        <div className="text-gray-600 flex items-center">
          <Loader className="w-4 h-4 mr-2 animate-spin" /> Loading parameter trends...
        </div>
      ) : error ? (
        <div className="text-red-600">Error: {error.message}</div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data!}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="volThreshold" name="Vol Threshold" stroke="#8884d8" strokeWidth={2} />
            <Line type="monotone" dataKey="momentumWindow" name="Momentum Window" stroke="#82ca9d" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
};

export default RLParametersChart;
