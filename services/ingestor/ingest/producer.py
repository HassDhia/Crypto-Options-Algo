from confluent_kafka import Producer
from fastavro import parse_schema, schemaless_writer
import io
import os
import json

SCHEMA = parse_schema(
    json.load(open("../integration-tests/tick.avsc"))
)
PROD = Producer({
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "redpanda:9092")
})


def send(msg: dict):
    buf = io.BytesIO()
    schemaless_writer(buf, SCHEMA, msg)
    PROD.produce("raw_ticks", buf.getvalue())
