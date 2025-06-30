from confluent_kafka import Producer
from fastavro import parse_schema, schemaless_writer
import io
import os
import json
import logging


# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Load schemas
TICK_SCHEMA = parse_schema(
    json.load(open("../integration-tests/tick.avsc"))
)
OPTION_SNAP_SCHEMA = parse_schema(
    json.load(open("../avro/option_snap.avsc"))
)


PROD = Producer({
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "redpanda:9092")
})


def send(topic: str, schema: dict, msg: dict):
    """Generic function to send messages to Kafka with Avro serialization"""
    try:
        buf = io.BytesIO()
        schemaless_writer(buf, schema, msg)
        PROD.produce(topic, buf.getvalue())
        logger.debug(f"Sent message to {topic}: {msg}")
    except Exception as e:
        logger.error(f"Failed to send message to {topic}: {e}")


def send_tick(msg: dict):
    """Send tick data to raw_ticks topic"""
    send("raw_ticks", TICK_SCHEMA, msg)


def send_option_snap(msg: dict):
    """Send option snapshot data to option_snaps topic"""
    send("option_snaps", OPTION_SNAP_SCHEMA, msg)
