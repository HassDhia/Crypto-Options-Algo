import json
import os
import logging
from datetime import datetime
from typing import AsyncGenerator, Dict
from . import producer  # Import module to avoid false unused import warning
from ..metrics import PrometheusMetrics


import aiohttp
import aioredis

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Deribit configuration
URL = "wss://www.deribit.com/ws/api/v2"
ASSETS = ["BTC", "ETH"]  # Supported assets
SNAPSHOT_CHANNEL = "book.T.{asset}-OPTION.100ms"
RAW_CHANNEL = "book.{asset}-OPTION.raw"
TICKER_CHANNEL = "ticker.{asset}-OPTION.raw"
SNAPSHOT_INTERVAL = 300  # 5 minutes in seconds
KEY_TTL = 420  # 7 minutes in seconds (longer than interval)


async def stream() -> AsyncGenerator[dict, None]:
    """Stream option data with 5-minute throttling and Redis caching"""
    # Connect to Redis
    redis = aioredis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0
    )

    # Initialize state
    last_emit_time = datetime.utcnow()
    metrics = PrometheusMetrics()  # For tracking stats

    async with aiohttp.ClientSession() as sess, sess.ws_connect(URL) as ws:
        # Subscribe to initial snapshot channels
        snapshot_channels = [
            SNAPSHOT_CHANNEL.format(asset=asset) for asset in ASSETS
        ]
        await ws.send_json({
            "method": "public/subscribe",
            "params": {"channels": snapshot_channels},
            "id": 1
        })

        async for msg in ws:
            if msg.type != aiohttp.WSMsgType.TEXT:
                continue

            data = json.loads(msg.data)
            ts = datetime.utcnow()

            # Handle incoming messages
            if "params" in data and "channel" in data["params"]:
                channel = data["params"]["channel"]
                instrument = data["params"]["data"].get("instrument_name")
                if not instrument:
                    continue

                redis_key = f"book:{instrument}"

                # Handle ticker updates (mark_iv and delta)
                if "ticker." in channel:
                    mark_iv = data["params"]["data"].get("mark_iv", 0.0)
                    delta = data["params"]["data"].get("delta", 0.0)
                    await redis.hset(
                        redis_key,
                        mapping={"mark_iv": mark_iv, "delta": delta}
                    )

                # Handle book updates (bids and asks)
                elif "book." in channel:
                    bids = json.dumps(data["params"]["data"].get("bids", []))
                    asks = json.dumps(data["params"]["data"].get("asks", []))
                    await redis.hset(
                        redis_key,
                        mapping={"bids": bids, "asks": asks}
                    )
                    await redis.expire(redis_key, KEY_TTL)
                    logger.info(f"Updated book for {instrument}")

                    # After initial snapshot, switch to raw channels
                    if "book.T" in channel:
                        raw_channels = [
                            RAW_CHANNEL.format(asset=asset)
                            for asset in ASSETS
                        ]
                        raw_channels.extend(
                            TICKER_CHANNEL.format(asset=asset)
                            for asset in ASSETS
                        )

                        await ws.send_json({
                            "method": "public/subscribe",
                            "params": {"channels": raw_channels},
                            "id": 2
                        })

            # Handle raw updates
            elif "params" in data and "data" in data["params"]:
                instrument = data["params"]["data"].get("instrument_name")
                if instrument:
                    # Update Redis cache
                    # Optimize Redis update
                    expiry = instrument.split("-")[1]
                    redis_key = f"book:{expiry}:{instrument}"
                    json_data = json.dumps(
                        data["params"]["data"]
                    )
                    await redis.set(
                        redis_key,
                        json_data,
                        ex=KEY_TTL
                    )

            # Emit aggregated data every 5 minutes
            if (ts - last_emit_time).total_seconds() >= SNAPSHOT_INTERVAL:
                last_emit_time = ts
                await emit_snapshots(redis, metrics)

        await redis.close()


async def emit_snapshots(redis: aioredis.Redis, metrics: PrometheusMetrics) -> None:
    """Emit all cached instruments as a single batch snapshot"""
    complete_snapshots = []
    incomplete_count = 0

    # Scan all instrument keys
    async for key in redis.scan_iter("book:*"):
        data = await redis.hgetall(key)
        if all(k in data for k in ["bids", "asks", "mark_iv", "delta"]):
            instrument_data = {
                "instrument_name": key.decode().split(":")[1]
            }
            for k, v in data.items():
                instrument_data[k] = (
                    json.loads(v) if k in ["bids", "asks"]
                    else float(v)
                )
            complete_snapshots.append(format_snapshot(instrument_data))
        else:
            incomplete_count += 1

    # Emit metrics
    metrics.incr("ingestor_ticks_emitted_total", len(complete_snapshots))
    metrics.incr("ingestor_snapshot_incomplete_total", incomplete_count)

    # Send batch to Kafka if we have any complete snapshots
    if complete_snapshots:
        producer.send_option_snap_batch(complete_snapshots)


def format_snapshot(data: Dict) -> Dict:
    """Format instrument data for Avro serialization"""
    # Calculate timestamp once for consistency
    timestamp = int(datetime.utcnow().timestamp() * 1000)
    return {
        "instrument": data.get("instrument_name", ""),
        "timestamp": timestamp,
        "best_bid_price": data.get("best_bid_price", 0.0),
        "best_ask_price": data.get("best_ask_price", 0.0),
        "mark_iv": data.get("mark_iv", 0.0),
        "delta": data.get("delta", 0.0),
        "underlying_price": data.get("underlying_price", 0.0),
        "last_price": data.get("last_price", 0.0),
        "bid_iv": data.get("bid_iv", 0.0),
        "ask_iv": data.get("ask_iv", 0.0),
        "stats": data.get("stats", {})
    }
