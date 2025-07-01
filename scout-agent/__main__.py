import logging
import time
from common.kafka import create_consumer, create_producer
import redis
from .filter import OptionFilter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Create Kafka consumer and producer
    consumer = create_consumer("ticks.raw")
    producer = create_producer()

    # Connect to Redis
    r = redis.Redis(host='redis', port=6379, db=0)

    # Initialize filter with default parameters
    option_filter = OptionFilter()
    current_params = {
        "delta_min": option_filter.delta_min,
        "delta_max": option_filter.delta_max,
        "min_edge": option_filter.min_edge,
        "max_skew": option_filter.max_skew,
        "avoid_iv_crush": option_filter.avoid_iv_crush
    }

    logger.info("Scout agent started")

    for message in consumer:
        try:
            # Parse the message
            tick = message.value

            # Extract required fields
            instrument = tick.get("instrument")
            bid = tick.get("bid")
            ask = tick.get("ask")

            if not all([instrument, bid, ask]):
                logger.warning("Missing required fields in tick")
                continue

            # Write to Redis
            r.set(f"last_bid:{instrument}", bid)

            # Update filter parameters from Redis with validation
            try:
                params = r.hgetall("filter_params")
                if params:
                    # Convert and validate parameters
                    delta_min = float(params.get(b'delta_min', b'0.0'))
                    delta_max = float(params.get(b'delta_max', b'1.0'))
                    min_edge = float(params.get(b'min_edge', b'0.0'))
                    max_skew = float(params.get(b'max_skew', b'inf'))
                    avoid_iv_crush = params.get(
                        b'avoid_iv_crush', b'False'
                    ).decode('utf-8') == 'True'

                    # Validate parameter ranges
                    valid_params = (
                        0 <= delta_min <= 1 and
                        0 <= delta_max <= 1 and
                        delta_min <= delta_max and
                        min_edge >= 0 and
                        max_skew > 0
                    )

                    if valid_params:
                        # Check if parameters have changed
                        new_params = {
                            "delta_min": delta_min,
                            "delta_max": delta_max,
                            "min_edge": min_edge,
                            "max_skew": max_skew,
                            "avoid_iv_crush": avoid_iv_crush
                        }
                        if new_params != current_params:
                            # Update filter with new parameters
                            option_filter = OptionFilter(**new_params)
                            current_params = new_params
                            logger.info("Updated filter parameters")
                    else:
                        logger.warning(
                            "Invalid filter parameters from Redis. "
                            "Using defaults."
                        )
            except ValueError as ve:
                logger.error(
                    f"Invalid parameter value: {ve}. Using current filter."
                )
            except Exception as e:
                logger.error(
                    f"Error reading filter params from Redis: {e}"
                )

            # Apply deterministic filtering
            if not option_filter.is_candidate(tick):
                logger.info(f"Skipping {instrument} due to filter criteria")
                continue

            # Create scouted tick with additional metadata
            scouted_tick = {
                "instrument": instrument,
                "bid": bid,
                "ask": ask,
                "timestamp": tick.get("timestamp", int(time.time() * 1000)),
                "scout_processed_at": int(time.time() * 1000)
            }

            # Add debug logging for edge calculation when BS is enabled
            if os.getenv("SCOUT_USE_BS", "0") == "1":
                from common.quant import bs
                try:
                    # Recompute values for logging
                    parts = instrument.split('-')
                    strike = float(parts[2])
                    option_type = parts[3].lower()
                    right = 'c' if option_type == 'c' else 'p'
                    underlying_sym = parts[0]

                    # Get underlying price
                    s = option_filter._get_underlying_price(underlying_sym)
                    if s is None:
                        s = strike  # Fallback to strike price

                    # Parse expiration time
                    expiry_str = parts[1]
                    exp_day = int(expiry_str[:2])
                    exp_month_str = expiry_str[2:5]
                    exp_year = 2000 + int(expiry_str[5:])
                    exp_month = datetime.strptime(exp_month_str, "%b").month
                    exp_date = datetime(exp_year, exp_month, exp_day)
                    t = (exp_date - datetime.utcnow()).days / 365.0

                    # Placeholder values
                    r = 0.01
                    sigma = 0.7

                    # Calculate values
                    theo = bs.theo_price(right, s, strike, t, r, sigma)
                    mid_px = (bid + ask) / 2.0
                    edge_pct = (theo - mid_px) / mid_px
                    delta_val = bs.delta(right, s, strike, t, r, sigma)

                    logger.debug(
                        "CANDIDATE %s edge=%.4f Δ=%.3f theo=%.6f bid=%.6f ask=%.6f",
                        instrument, edge_pct, delta_val, theo, bid, ask
                    )
                except Exception as e:
                    logger.error(f"Debug logging failed: {e}")

            # Publish to scouted topic
            producer.send("ticks.scouted", value=scouted_tick)
            logger.info(f"Scouted candidate: {instrument} (passed filters)")

        except Exception as e:
            logger.error(f"Error processing tick: {e}")


if __name__ == "__main__":
    main()
