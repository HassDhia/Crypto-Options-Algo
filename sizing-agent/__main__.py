import logging
from common.kafka import create_consumer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Create Kafka consumer for scouted ticks
    consumer = create_consumer("ticks.scouted")

    logger.info("Sizing agent started")

    for message in consumer:
        try:
            # Log fixed size for each tick
            tick = message.value
            instrument = tick.get("instrument")
            logger.info(f"Fixed size 1 for {instrument}")

        except Exception as e:
            logger.error(f"Error processing scouted tick: {e}")


if __name__ == "__main__":
    main()
