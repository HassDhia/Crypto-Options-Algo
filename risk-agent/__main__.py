import os
import json
import logging
import redis
from common.kafka import create_consumer, create_producer
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load risk limits from environment JSON, or use defaults
default_limits = {"max_notional": 100000.0, "max_position_contracts": 5}
limits = default_limits
if os.getenv("RISK_LIMITS_JSON"):
    try:
        limits = json.loads(os.getenv("RISK_LIMITS_JSON"))
    except Exception as e:
        logger.error(f"Failed to parse RISK_LIMITS_JSON, using defaults. Error: {e}")

# Connect to Redis for portfolio data (if any stored)
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0
)

# Kafka consumer for scouted ticks and producer for risk alerts
consumer = create_consumer("ticks.scouted")
producer = create_producer()
logger.info("Risk agent started with limits: %s", limits)


def get_underlying_price(instrument: str) -> float:
    """Get underlying price for notional calculation from Redis or other source."""
    underlying = None
    try:
        underlying_sym = instrument.split('-')[0]  # e.g. "BTC"
        price = redis_client.get(f"last_price:{underlying_sym}")
        if price:
            underlying = float(price)
    except Exception as e:
        logger.warning(
            f"Could not fetch underlying price for {instrument}: {e}"
        )
    return underlying

for message in consumer:
    try:
        tick = message.value  # scouted tick candidate
        instrument = tick.get("instrument")
        if instrument is None:
            continue
        # Determine notional exposure of 1 contract of this option
        # (For simplicity, assume 1 option contract = 1 unit of underlying exposure)
        underlying_price = get_underlying_price(instrument)
        if underlying_price is None:
            # Fallback: use strike as proxy if underlying price not available
            try:
                strike = float(instrument.split('-')[2])
            except (IndexError, ValueError):
                strike = 0.0
            underlying_price = strike
        notional = underlying_price  # notional for 1 contract ~ price of underlying * 1 unit

        # Determine desired trade size (if sizing agent suggests later, we could use that; here assume 1 contract)
        desired_size = 1
        # Current position for this instrument (if any, from Redis portfolio data)
        try:
            current_position = 0
            pos = redis_client.hget("positions", instrument)
            if pos:
                current_position = int(pos)
        except Exception:
            current_position = 0

        # Risk checks:
        violation = False
        violation_reasons = []
        max_notional = limits.get("max_notional", default_limits["max_notional"])
        max_position = limits.get(
            "max_position_contracts", default_limits["max_position_contracts"]
        )

        # 1. Max notional exposure per trade
        if notional * desired_size > max_notional:
            violation = True
            violation_reasons.append("notional")

        # 2. Max contracts per position
        if current_position + desired_size > max_position:
            violation = True
            violation_reasons.append("position_size")

        if violation:
            # If any risk limit is violated, publish a risk alert and do not allow this trade
            alert = {
                "instrument": instrument,
                "risk_level": "HIGH",
                "recommended_action": "HOLD",
                "timestamp": int(datetime.utcnow().timestamp() * 1000)
            }
            producer.send("risk.alerts", value=alert)
            logger.warning(
                "Risk violation for %s! Reasons: %s. Alert sent.",
                instrument, violation_reasons
            )
            # (We do not forward this trade to execution; effectively dropped from pipeline except for the alert)
        else:
            # Trade is within risk limits
            logger.info(
                "Risk OK for %s (notional=%.2f, pos_after_trade=%d)",
                instrument, notional, current_position + desired_size
            )
            # (Optionally, could send a low-risk alert or simply proceed. Here we just log.)
    except Exception as e:
        logger.error(f"Error processing scouted tick in Risk agent: {e}")
