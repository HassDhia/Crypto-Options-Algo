import json
import logging
import os
from confluent_kafka import Consumer, KafkaException, Producer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Kafka configuration
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "redpanda:9092")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://redpanda:8081")
OPTION_SNAPS_TOPIC = "option_snaps"
SCOUTED_OPTIONS_TOPIC = "ticks.scouted"

# Connect to schema registry
schema_registry_conf = {'url': SCHEMA_REGISTRY_URL}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Avro deserializer for option snaps
option_snap_schema_str = json.dumps({
    "namespace": "ingestor.avro",
    "type": "record",
    "name": "OptionSnap",
    "fields": [
        {"name": "instrument", "type": "string"},
        {"name": "timestamp", "type": "long"},
        {"name": "best_bid_price", "type": "double"},
        {"name": "best_ask_price", "type": "double"},
        {"name": "mark_iv", "type": "double"},
        {"name": "delta", "type": "double"},
        {"name": "underlying_price", "type": "double"},
        {"name": "last_price", "type": "double"},
        {"name": "bid_iv", "type": "double"},
        {"name": "ask_iv", "type": "double"},
        {
            "name": "stats",
            "type": {
                "type": "map",
                "values": ["double", "string", "null"]
            }
        }
    ]
})
avro_deserializer = AvroDeserializer(schema_registry_client, option_snap_schema_str)

# Kafka consumer configuration
conf = {
    'bootstrap.servers': KAFKA_BOOTSTRAP,
    'group.id': 'option-scout-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
}

# Create consumer
consumer = Consumer(conf)

def calculate_option_score(snap):
    """
    Calculate a score for an option based on market conditions and Greeks.
    Higher scores indicate more favorable trading opportunities.
    """
    # Extract key metrics
    bid_ask_spread = snap['best_ask_price'] - snap['best_bid_price']
    # Positive when market expects upward movement
    iv_skew = snap['ask_iv'] - snap['bid_iv']

    # Calculate liquidity score (lower spread is better)
    spread_score = 1 / (bid_ask_spread + 0.001)  # Avoid division by zero

    # Calculate IV rank score (higher IV rank is better for selling options)
    # Placeholder for actual IV rank calculation
    iv_rank = (snap['mark_iv'] - 0.3) / 0.5
    iv_score = max(0, min(1, iv_rank))  # Normalize between 0-1

    # Calculate risk-adjusted return potential
    # Placeholder for actual calculation - would incorporate historical volatility
    risk_adjusted_return = 0.5

    # Combine factors into a composite score
    score = (
        0.4 * spread_score +
        0.3 * iv_score +
        0.2 * risk_adjusted_return +
        0.1 * iv_skew
    )
    return score


def process_option_snap(msg):
    """Process an option snapshot message and calculate its score"""
    try:
        # Deserialize the Avro message
        snap = avro_deserializer(
            msg.value(),
            SerializationContext(msg.topic(), MessageField.VALUE)
        )
        # Calculate option score
        score = calculate_option_score(snap)

        # Create enriched payload with score
        # Create payload matching ScoutedTick schema
        enriched = {
            "timestamp": snap['timestamp'],
            "instrument": snap['instrument'],
            "bid": snap['best_bid_price'],
            "ask": snap['best_ask_price'],
            "edge_pct": round(score, 4),
            "delta": snap['delta'],
            "vega": 0.0,   # Placeholder value for now
            "theo_price": (snap['best_bid_price'] + snap['best_ask_price']) / 2
        }
        logger.info(f"Scored option {snap['instrument']}: {score}")
        return enriched
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return None


# Create Kafka producer for scouted options
producer_conf = {'bootstrap.servers': KAFKA_BOOTSTRAP}
producer = Producer(producer_conf)

def main():
    logger.info("Starting option scout agent...")
    consumer.subscribe([OPTION_SNAPS_TOPIC])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            # Process the message
            enriched = process_option_snap(msg)

            # Produce to scouted_options topic
            if enriched:
                # Serialize and produce to Kafka
                # In production, we'd use Avro serialization
                # For now, use JSON for simplicity
                producer.produce(
                    SCOUTED_OPTIONS_TOPIC,
                    json.dumps(enriched).encode('utf-8')
                )
                producer.flush()
                instrument = enriched['instrument']
                logger.info(f"Published scouted option: {instrument}")

            # Commit message offset
            consumer.commit(asynchronous=False)

    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
