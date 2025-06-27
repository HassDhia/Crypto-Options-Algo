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

            # Publish to scouted topic
            producer.send("ticks.scouted", value=scouted_tick)
            logger.info(f"Scouted candidate: {instrument} (passed filters)")

        except Exception as e:
            logger.error(f"Error processing tick: {e}")


if __name__ == "__main__":
    main()
