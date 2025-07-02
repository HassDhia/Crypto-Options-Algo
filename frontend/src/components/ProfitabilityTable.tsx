// frontend/src/components/ProfitabilityTable.tsx
import React from "react";

interface TradeSuggestion {
  instrument: string;
  score: number;
  price: number;
}
interface Props {
  trades: TradeSuggestion[];
  onApprove: (trade: TradeSuggestion) => void;
}

export const ProfitabilityTable: React.FC<Props> = ({ trades, onApprove }) => {
  return (
    <div>
      <h3>Top 5 Options</h3>
      <table border={1} cellPadding={6}>
        <thead>
          <tr><th>Instrument</th><th>Score</th><th>Action</th></tr>
        </thead>
        <tbody>
          {trades.map(trade => (
            <tr key={trade.instrument}>
              <td>{trade.instrument}</td>
              <td>{trade.score.toFixed(2)}</td>
              <td>
                <button onClick={() => onApprove(trade)}>Approve</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
