import { useEffect, useState } from "react";
import { fetchTrades } from "../api";

export default function PortfolioSummary() {
  const [trades, setTrades] = useState<any[]>([]);
  useEffect(() => {
    const id = setInterval(() => fetchTrades().then((d) => setTrades(d.trades)), 5000);
    return () => clearInterval(id);
  }, []);

  const pnl = trades.reduce((s, t) => s + (t.current_price ?? t.entry_price) - t.entry_price, 0);

  return <h3>Portfolio P&L (paper): {pnl.toFixed(4)} BTC</h3>;
}
