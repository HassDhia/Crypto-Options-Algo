import pytest
import time
from common.kafka import create_consumer, create_producer
from uuid import uuid4

def test_reject_large_notional():
    # Setup Kafka consumers and producers
    sizing_consumer = create_consumer("size.ack", "size.reject")
    risk_producer = create_producer()
    sizing_producer = create_producer()

    # Generate a unique signal ID
    signal_id = str(uuid4())

    # Create a large notional size proposal
    proposal = {
        "signal_id": signal_id,
        "instrument": "BTC-30JUN25-60000-C",
        "proposed_size": 1000000,  # 1 million BTC notional
        "timestamp": int(time.time() * 1000)
    }

    # Send the proposal
    sizing_producer.send("size.proposal", key=signal_id, value=proposal)
    sizing_producer.flush()

    # Wait for response (timeout after 10 seconds)
    start_time = time.time()
    while time.time() - start_time < 10:
        msg = sizing_consumer.poll(timeout_ms=1000)
        if msg is None:
            continue

        if msg.topic() == "size.reject" and msg.key() == signal_id:
            reject = msg.value()
            assert reject["reason"] == "Notional limit exceeded"
            return

    pytest.fail("Did not receive rejection within timeout period")

def test_ack_small_notional():
    # Setup Kafka consumers and producers
    sizing_consumer = create_consumer("size.ack", "size.reject")
    risk_producer = create_producer()
    sizing_producer = create_producer()

    # Generate a unique signal ID
    signal_id = str(uuid4())

    # Create a small notional size proposal
    proposal = {
        "signal_id": signal_id,
        "instrument": "BTC-30JUN25-60000-C",
        "proposed_size": 1,  # Small position
        "timestamp": int(time.time() * 1000)
    }

    # Send the proposal
    sizing_producer.send("size.proposal", key=signal_id, value=proposal)
    sizing_producer.flush()

    # Wait for response (timeout after 10 seconds)
    start_time = time.time()
    while time.time() - start_time < 10:
        msg = sizing_consumer.poll(timeout_ms=1000)
        if msg is None:
            continue

        if msg.topic() == "size.ack" and msg.key() == signal_id:
            ack = msg.value()
            assert ack["approved_size"] == 1
            return

    pytest.fail("Did not receive acknowledgment within timeout period")
