# backend/app/scheduler.py
import asyncio, os
from . import deribit_api, calculator

REFRESH_INTERVAL = int(os.getenv("REFRESH_SECS", 300))  # 5 minutes by default

# Global state updated by the scheduler
TOP_TRADES: list[dict] = []
CURRENT_PRICES: dict[str, float] = {}

async def run():
    """Background task to periodically fetch data and update top trades."""
    global TOP_TRADES, CURRENT_PRICES
    while True:
        # 1. Fetch latest options data from Deribit
        options = deribit_api.fetch_options_snapshot(currency="BTC")
        # 2. Calculate profitability scores and get top 5
        top5 = calculator.rank_options(options, top_n=5)
        # 3. Update global state for API endpoints
        TOP_TRADES = [ 
            { "instrument": opt["instrument_name"], "score": opt["score"], 
              "price": opt["mark_price"] } for opt in top5 
        ]
        # Also store current prices for *all* options to compute P&L
        CURRENT_PRICES = { opt["instrument_name"]: opt["mark_price"] for opt in options }
        # (The portfolio P&L calculation will use CURRENT_PRICES for each trade's instrument)
        print(f"Refreshed top trades: {[opt['instrument_name'] for opt in top5]}")
        await asyncio.sleep(REFRESH_INTERVAL)
