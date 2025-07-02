// frontend/src/api.ts
export async function getTopTrades() {
  const res = await fetch("http://localhost:8000/options/top");
  return res.json();  // expects { trades: [...] }
}

export async function getPortfolio() {
  const res = await fetch("http://localhost:8000/portfolio");
  return res.json();  // expects { trades: [...], total_pnl: ... }
}

export async function approveTrade(trade: { instrument: string, quantity: number, entry_price: number }) {
  // Send a trade approval to the backend
  await fetch("http://localhost:8000/trades/approve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(trade)
  });
}
