// frontend/src/components/PortfolioSummary.tsx
import React from "react";

interface TradePosition {
  instrument: string;
  quantity: number;
  entry_price: number;
  current_price: number;
  pnl: number;
}
interface Props {
  trades: TradePosition[];
  totalPnl: number;
}

export const PortfolioSummary: React.FC<Props> = ({ trades, totalPnl }) => {
  return (
    <div>
      <h3>Portfolio Summary</h3>
      <p>Total P&L: <strong>{totalPnl.toFixed(2)}</strong></p>
      {trades.length === 0 ? (
        <p>No trades approved yet.</p>
      ) : (
        <ul>
          {trades.map((trade, idx) => (
            <li key={idx}>
              {trade.instrument} – Qty: {trade.quantity}, Entry: {trade.entry_price.toFixed(2)}, 
              Current: {trade.current_price.toFixed(2)}, 
              P&L: <strong>{trade.pnl.toFixed(2)}</strong>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
