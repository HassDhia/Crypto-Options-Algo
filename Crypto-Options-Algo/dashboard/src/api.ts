export async function fetchTop() {
  const res = await fetch("/sse/top");
  // caller uses EventSource; helper kept for compatibility
  return res.json();
}
export async function fetchTrades() {
  return fetch("/trades").then((r) => r.json());
}
export async function approve(trade: any) {
  return fetch("/trades/approve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(trade),
  });
}
