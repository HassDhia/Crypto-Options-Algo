from fastapi import FastAPI
from fastapi.responses import EventSourceResponse
import json, asyncio, logging

app = FastAPI()
log = logging.getLogger(__name__)
_top: list[dict] = []
_trades: list[dict] = []

# Called from scheduler
def push_top_options(opts: list[dict]):
    global _top
    _top = opts

@app.get("/sse/top")
async def stream_top():
    async def event_gen():
        while True:
            yield f"data: {json.dumps(_top)}\n\n"
            await asyncio.sleep(1)
    return EventSourceResponse(event_gen())

@app.post("/trades/approve")
async def approve_trade(trade: dict):
    """trade json includes instrument_name, qty, entry_price"""
    _trades.append(trade)
    return {"status": "OK"}

@app.get("/trades")
async def trades():
    return dict(trades=_trades)
