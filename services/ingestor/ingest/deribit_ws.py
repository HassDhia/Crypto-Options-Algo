import json
import os
import logging
import ssl
import uuid
from datetime import datetime, timedelta
from typing import AsyncGenerator, Dict, List

import aiohttp
import redis.asyncio as aioredis
from services.ingestor.metrics import PrometheusMetrics
import services.ingestor.ingest.logging_conf  # noqa: F401

logger = logging.getLogger(__name__)

# ──────────────────────────────
# Constants & config
# ──────────────────────────────
URL = "wss://www.deribit.com/ws/api/v2"
ASSETS = ("BTC", "ETH")
SNAPSHOT_CHANNEL = "book.T.{asset}-OPTION.100ms"
RAW_CHANNEL = "book.{asset}-OPTION.raw"
TICKER_CHANNEL = "ticker.{asset}-OPTION.raw"

SNAPSHOT_INTERVAL = timedelta(minutes=5).total_seconds()
KEY_TTL = int(SNAPSHOT_INTERVAL * 1.4)          # 7 min > 5 min interval

_latest_snapshot: List[Dict] = []               # module‑level cache


# ──────────────────────────────
# Public helpers
# ──────────────────────────────
def get_live_data() -> List[Dict]:
    """Return the most recent full snapshot batch."""
    return _latest_snapshot


# ──────────────────────────────
# Core streaming coroutine
# ──────────────────────────────
async def stream() -> AsyncGenerator[List[Dict], None]:
    """
    Yield aggregated Deribit option snapshots every ``SNAPSHOT_INTERVAL`` seconds.

    The coroutine:
        1. Subscribes to thin book channels for an initial snapshot.
        2. Switches to raw + ticker channels for incremental updates.
        3. Caches every update in Redis (TTL = KEY_TTL).
        4. Emits a *batch* of fully‑populated instruments at the configured cadence.
    """
    redis = aioredis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        decode_responses=False,   # work with bytes, decode only when needed
    )
    metrics = PrometheusMetrics()
    last_emit = datetime.utcnow()

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    async with aiohttp.ClientSession() as sess:
        try:
            async with sess.ws_connect(URL, ssl=ssl_ctx) as ws:
                logger.info("Connected to Deribit WebSocket")

                # ---- 1️⃣ initial snapshot subscription ------------------------
                await ws.send_json(
                    {
                        "jsonrpc": "2.0",
                        "id": str(uuid.uuid4()),
                        "method": "public/subscribe",
                        "params": {
                            "channels": [
                                SNAPSHOT_CHANNEL.format(asset=a) for a in ASSETS
                            ]
                        },
                    }
                )

                # Track whether we've switched to raw feeds
                raw_subscribed = False

                async for msg in ws:
                    if msg.type != aiohttp.WSMsgType.TEXT:
                        continue

                    data = json.loads(msg.data)
                    now = datetime.utcnow()

                    # ---- 2️⃣ handle channel messages ------------------------
                    if "params" in data and "channel" in data["params"]:
                        await _handle_channel_msg(data["params"], redis)

                        # Once we process ANY thin book update we can subscribe to raw feeds
                        if not raw_subscribed and data["params"]["channel"].startswith("book.T"):
                            raw_subscribed = True
                            await ws.send_json(
                                {
                                    "jsonrpc": "2.0",
                                    "id": str(uuid.uuid4()),
                                    "method": "public/subscribe",
                                    "params": {
                                        "channels": [
                                            *(RAW_CHANNEL.format(asset=a) for a in ASSETS),
                                            *(TICKER_CHANNEL.format(asset=a) for a in ASSETS),
                                        ]
                                    },
                                }
                            )

                    # ---- 3️⃣ periodic snapshot emission ----------------------
                    if (now - last_emit).total_seconds() >= SNAPSHOT_INTERVAL:
                        last_emit = now
                        batch = await emit_snapshots(redis, metrics)
                        if batch:          # only yield when we have data
                            yield batch

        finally:
            await redis.close()


# ──────────────────────────────
# Internal helpers
# ──────────────────────────────
async def _handle_channel_msg(params: Dict, redis: aioredis.Redis) -> None:
    """Dispatch Deribit channel data to the correct Redis structure."""
    channel = params["channel"]
    pdata = params["data"]
    instrument = pdata.get("instrument_name")
    if not instrument:
        return

    if channel.startswith("ticker."):
        await redis.hset(f"book:{instrument}", mapping={
            "mark_iv": pdata.get("mark_iv", 0.0),
            "delta": pdata.get("delta", 0.0),
        })

    elif channel.startswith("book."):
        # bids/asks come as nested lists -> store JSON string
        await redis.hset(
            f"book:{instrument}",
            mapping={
                "bids": json.dumps(pdata.get("bids", [])),
                "asks": json.dumps(pdata.get("asks", [])),
                "best_bid_price": pdata.get("best_bid_price", 0.0),
                "best_ask_price": pdata.get("best_ask_price", 0.0),
                "underlying_price": pdata.get("underlying_price", 0.0),
                "last_price": pdata.get("last_price", 0.0),
                "bid_iv": pdata.get("bid_iv", 0.0),
                "ask_iv": pdata.get("ask_iv", 0.0),
                "stats": json.dumps(pdata.get("stats", {})),
            },
        )
        await redis.expire(f"book:{instrument}", KEY_TTL)


async def emit_snapshots(redis: aioredis.Redis, metrics: PrometheusMetrics) -> List[Dict]:
    """
    Collect all fully‑populated instruments from Redis and return them as a list.

    An entry is "complete" when it contains every field expected by ``format_snapshot``.
    """
    complete, incomplete = [], 0
    required = {
        b"bids", b"asks", b"mark_iv", b"delta",
        b"best_bid_price", b"best_ask_price",
        b"underlying_price", b"last_price", b"bid_iv", b"ask_iv", b"stats",
    }

    async for key in redis.scan_iter(match="book:*"):
        data = await redis.hgetall(key)
        if required.issubset(data.keys()):
            snapshot = {
                k.decode(): v for k, v in data.items()
            }
            # Decode nested JSON fields back to Python objects
            snapshot["bids"] = json.loads(snapshot["bids"])
            snapshot["asks"] = json.loads(snapshot["asks"])
            snapshot["stats"] = json.loads(snapshot["stats"])
            snapshot["instrument_name"] = key.decode().split(":", 1)[1]
            complete.append(format_snapshot(snapshot))
        else:
            incomplete += 1

    # Prometheus counters
    metrics.incr("ingestor_ticks_emitted_total", len(complete))
    if incomplete:
        metrics.incr("ingestor_snapshot_incomplete_total", incomplete)

    logger.debug("Emit | complete=%d incomplete=%d", len(complete), incomplete)

    # Update module‑wide cache
    global _latest_snapshot
    if complete:
        _latest_snapshot = complete

    return complete


def format_snapshot(data: Dict) -> Dict:
    """Transform Deribit raw record into a flat structure ready for Avro / downstream use."""
    ts = int(datetime.utcnow().timestamp() * 1000)
    return {
        "instrument": data.get("instrument_name", ""),
        "timestamp": ts,
        "best_bid_price": float(data.get("best_bid_price", 0.0)),
        "best_ask_price": float(data.get("best_ask_price", 0.0)),
        "mark_iv": float(data.get("mark_iv", 0.0)),
        "delta": float(data.get("delta", 0.0)),
        "underlying_price": float(data.get("underlying_price", 0.0)),
        "last_price": float(data.get("last_price", 0.0)),
        "bid_iv": float(data.get("bid_iv", 0.0)),
        "ask_iv": float(data.get("ask_iv", 0.0)),
        "stats": data.get("stats", {}),
        "bids": data.get("bids", []),  # keep L2 data if you need it later
        "asks": data.get("asks", []),
    }
