# backend/app/main.py
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from . import db, scheduler, schemas

app = FastAPI()

# Enable CORS so frontend (e.g. http://localhost:3000) can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in dev, allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# On startup, launch the periodic data refresh loop (every 5 minutes)
@app.on_event("startup")
async def startup_event():
    import asyncio
    # Start the background scheduler task
    asyncio.create_task(scheduler.run())

@app.get("/options/top")
def get_top_options():
    """Get the current top 5 options ranked by profitability score."""
    return {"trades": scheduler.TOP_TRADES}

@app.post("/trades/approve")
def approve_trade(trade: schemas.TradeApproval):
    """Approve a trade: store it in the database and update portfolio P&L."""
    db.insert_trade(trade.instrument, trade.quantity, trade.entry_price)
    # (In this MVP, P&L will be recalculated on the next portfolio fetch)
    return {"status": "OK"}

@app.get("/portfolio")
def get_portfolio():
    """Return current open trades and running P&L."""
    trades = db.get_trades()  # fetch all approved trades from SQLite
    portfolio = []
    total_pnl = 0.0
    for instrument, qty, entry_price in trades:
        # Get latest price for this instrument (from the last refresh)
        price = scheduler.CURRENT_PRICES.get(instrument, entry_price)
        pnl = (price - entry_price) * qty  # profit/loss for this trade
        total_pnl += pnl
        portfolio.append({
            "instrument": instrument,
            "quantity": qty,
            "entry_price": entry_price,
            "current_price": price,
            "pnl": pnl
        })
    return {"trades": portfolio, "total_pnl": total_pnl}
