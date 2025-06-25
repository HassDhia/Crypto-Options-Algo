from confluent_kafka import Producer
from fastavro import parse_schema, schemaless_writer
import io, os, json

SCHEMA = parse_schema(json.load(open("avro/tick.avsc")))
PROD = Producer({"bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP", "redpanda:9092")})

def send(msg: dict):
    buf = io.BytesIO()
    schemaless_writer(buf, SCHEMA, msg)
    PROD.produce("raw_ticks", buf.getvalue())
