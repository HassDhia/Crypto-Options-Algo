import os
from kafka import KafkaConsumer, KafkaProducer
import json


def create_consumer(topic, group_id=None):
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    return KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset='earliest',
        group_id=group_id,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )


def create_producer():
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )
