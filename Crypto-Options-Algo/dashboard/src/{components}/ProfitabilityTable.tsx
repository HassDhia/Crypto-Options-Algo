import { useEffect, useState } from "react";
import { approve } from "../api";

export default function ProfitabilityTable() {
  const [rows, setRows] = useState<any[]>([]);

  useEffect(() => {
    const es = new EventSource("/sse/top");
    es.onmessage = (e) => setRows(JSON.parse(e.data));
    return () => es.close();
  }, []);

  if (!rows.length) return <p>No candidates yet…</p>;

  return (
    <table>
      <thead>
        <tr>
          <th>Instrument</th><th>Score</th><th>Approve</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.instrument_name}>
            <td>{r.instrument_name}</td>
            <td>{r.score.toFixed(3)}</td>
            <td>
              <button onClick={() => approve({instrument_name: r.instrument_name, qty:1, entry_price:r.ask_price})}>
                Approve
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
