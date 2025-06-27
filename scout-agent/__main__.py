import logging
from common.kafka import create_consumer, create_producer
import redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Create Kafka consumer and producer
    consumer = create_consumer("ticks.raw")
    producer = create_producer()

    # Connect to Redis
    r = redis.Redis(host='redis', port=6379, db=0)

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

            # Create scouted tick
            scouted_tick = {
                "instrument": instrument,
                "bid": bid,
                "ask": ask
            }

            # Publish to scouted topic
            producer.send("ticks.scouted", value=scouted_tick)
            logger.info(f"Processed tick for {instrument}")

        except Exception as e:
            logger.error(f"Error processing tick: {e}")


if __name__ == "__main__":
    main()
