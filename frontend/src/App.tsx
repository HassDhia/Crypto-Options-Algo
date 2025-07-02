// frontend/src/App.tsx
import React, { useEffect, useState } from "react";
import { getTopTrades, getPortfolio, approveTrade } from "./api";
import { ProfitabilityTable } from "./components/ProfitabilityTable";
import { PortfolioSummary } from "./components/PortfolioSummary";

interface TradeSuggestion {
  instrument: string;
  score: number;
  price: number;
}
interface PortfolioData {
  trades: Array<{
    instrument: string;
    quantity: number;
    entry_price: number;
    current_price: number;
    pnl: number;
  }>;
  total_pnl: number;
}

function App() {
  const [topTrades, setTopTrades] = useState<TradeSuggestion[]>([]);
  const [portfolio, setPortfolio] = useState<PortfolioData>({ trades: [], total_pnl: 0 });

  // Fetch initial data and set up periodic refresh
  useEffect(() => {
    async function fetchData() {
      const topRes = await getTopTrades();
      setTopTrades(topRes.trades || []);
      const portRes = await getPortfolio();
      setPortfolio(portRes);
    }
    fetchData();
    // Refresh data every 5 minutes
    const intervalId = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(intervalId);
  }, []);

  const handleApprove = async (trade: TradeSuggestion) => {
    // We assume approving means buying 1 unit at current price
    const newTrade = { instrument: trade.instrument, quantity: 1, entry_price: trade.price };
    await approveTrade(newTrade);
    // After approval, fetch updated portfolio (new trade added, P&L updated)
    const portRes = await getPortfolio();
    setPortfolio(portRes);
  };

  return (
    <div>
      <h2>Crypto Options Dashboard</h2>
      <ProfitabilityTable trades={topTrades} onApprove={handleApprove} />
      <PortfolioSummary trades={portfolio.trades} totalPnl={portfolio.total_pnl} />
    </div>
  );
}

export default App;
