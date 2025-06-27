import logging
from common.kafka import create_consumer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Create Kafka consumer for scouted ticks
    consumer = create_consumer("ticks.scouted")

    logger.info("Execution agent started")

    for message in consumer:
        try:
            # Print "would trade" for each tick
            print("would trade")

        except Exception as e:
            logger.error(f"Error processing scouted tick: {e}")


if __name__ == "__main__":
    main()
