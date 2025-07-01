import logging
from common.kafka import create_consumer
from metrics import edge_capture, slip_bp, cum_pnl, start_metrics_server


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Start metrics server
start_metrics_server()


def handle_fill(fill):
    """Process a trade fill and update metrics"""

    try:
        # Calculate metrics
        realised_edge = fill['price'] - fill['theoretical_mid']
        theoretical_edge = fill['theoretical_edge']

        edge_capture.set(realised_edge / theoretical_edge)
        slip_bp.set(abs(realised_edge - theoretical_edge) * 10000)

        # Update cumulative PnL
        current_pnl = cum_pnl._value.get() or 0
        cum_pnl.set(current_pnl + (fill['size'] * realised_edge))
    except Exception as e:
        logger.error(f"Error processing fill: {e}")


def main():
    # Create Kafka consumer for scouted ticks
    consumer = create_consumer("ticks.scouted")

    logger.info("Execution agent started")

    for message in consumer:
        try:
            # Process message and update metrics
            handle_fill(message.value)
        except Exception as e:
            logger.error(f"Error processing scouted tick: {e}")


if __name__ == "__main__":
    main()
