import os
import json
import pytest

from common.kafka import create_producer


@pytest.fixture(scope="module")
def seed_sample_ticks():
    # Create Kafka producer
    producer = create_producer()

    # Get the path to sample_ticks.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sample_path = os.path.join(current_dir, 'sample_ticks.json')

    # Read sample ticks
    with open(sample_path) as f:
        ticks = json.load(f)

    # Produce each tick to the topic
    for tick in ticks:
        producer.send("ticks.raw", value=tick)

    # Flush to ensure all messages are sent
    producer.flush()


def test_tick_flow(redis_client, redpanda_consumer, seed_sample_ticks):
    # Wait for messages to be processed
    redpanda_consumer.poll(timeout_ms=5000)

    # Check that messages were consumed
    partitions = redpanda_consumer.assignment()
    total_offset = sum(redpanda_consumer.position(p) for p in partitions)
    assert total_offset > 0

    # Check that Redis has the expected keys
    for tick in [
        {"instrument": "BTC-25JUN25-60000-C", "bid": 0.05},
        {"instrument": "ETH-25JUN25-3500-C", "bid": 0.02}
    ]:
        key = f"last_bid:{tick['instrument']}"
        assert redis_client.get(key) is not None
        assert float(redis_client.get(key)) == tick['bid']
