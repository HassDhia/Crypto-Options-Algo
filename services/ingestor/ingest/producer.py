from confluent_kafka import Producer
from fastavro import parse_schema, schemaless_writer
import io
import os
import json
import logging


# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Get project root
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    '..', '..', '..'
))

# Load schemas
TICK_SCHEMA = parse_schema(
    json.load(open(os.path.join(PROJECT_ROOT, 'integration-tests', 'tick.avsc')))
)
OPTION_SNAP_SCHEMA = parse_schema(
    json.load(open(os.path.join(PROJECT_ROOT, 'services', 'ingestor', 'avro', 'option_snap.avsc')))
)


PROD = Producer({
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "redpanda:9092")
})


def send_batch(topic: str, schema: dict, messages: list):
    """Send batch of messages to Kafka with Avro serialization"""
    if not messages:
        return

    try:
        # Serialize all messages first
        serialized = []
        for msg in messages:
            buf = io.BytesIO()
            schemaless_writer(buf, schema, msg)
            serialized.append(buf.getvalue())

        # Send batch
        for data in serialized:
            PROD.produce(topic, data)

        # Flush to ensure delivery
        PROD.flush()
        logger.info(f"Sent batch of {len(messages)} messages to {topic}")
    except Exception as e:
        logger.error(f"Failed to send batch to {topic}: {e}")


def send_tick(msg: dict):
    """Send tick data to raw_ticks topic"""
    send_batch("raw_ticks", TICK_SCHEMA, [msg])


def send_option_snap(msg: dict):
    """Send option snapshot data to option_snaps topic"""
    send_batch("option_snaps", OPTION_SNAP_SCHEMA, [msg])


def send_option_snap_batch(messages: list):
    """Send batch of option snapshots to option_snaps topic"""
    send_batch("option_snaps", OPTION_SNAP_SCHEMA, messages)
