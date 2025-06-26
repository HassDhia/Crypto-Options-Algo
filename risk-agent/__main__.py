import logging
from common.kafka import create_consumer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Create Kafka consumer for scouted ticks
    consumer = create_consumer("ticks.scouted")

    logger.info("Risk agent started")

    for message in consumer:
        try:
            # Log risk OK for each tick
            tick = message.value
            instrument = tick.get("instrument")
            logger.info(f"risk OK for {instrument}")

        except Exception as e:
            logger.error(f"Error processing scouted tick: {e}")


if __name__ == "__main__":
    main()
