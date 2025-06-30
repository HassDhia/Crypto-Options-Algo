import json
import os
import logging
from datetime import datetime
from typing import AsyncGenerator, Dict
from . import producer  # Import module to avoid false unused import warning


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

            # Handle snapshot data (initial hydration)
            if "params" in data and "channel" in data["params"]:
                channel = data["params"]["channel"]
                instrument = data["params"]["data"].get("instrument_name")

                # Break long condition for readability
                is_option_channel = any(asset in channel for asset in ASSETS)
                if is_option_channel and "book.T" in channel:
                    # Store snapshot in Redis with expiry bucket
                    if instrument:
                        expiry = instrument.split("-")[1]
                        redis_key = f"book:{expiry}:{instrument}"
                        # Break long Redis operation
                        json_data = json.dumps(
                            data["params"]["data"]
                        )
                        await redis.set(
                            redis_key,
                            json_data,
                            ex=KEY_TTL
                        )
                        logger.info("Cached snapshot for %s", instrument)

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
                await emit_snapshots(redis)

        await redis.close()


async def emit_snapshots(redis: aioredis.Redis) -> AsyncGenerator[Dict, None]:
    """Emit all cached instruments as snapshots"""
    keys = await redis.keys("book:*")
    for key in keys:
        data = await redis.get(key)
        if data:
            instrument_data = json.loads(data)
            snapshot = format_snapshot(instrument_data)
            # Send snapshot to Kafka
            producer.send_option_snap(snapshot)
            yield snapshot


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
