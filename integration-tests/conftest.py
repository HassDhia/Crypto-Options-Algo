import pytest
from redis import Redis
from common.kafka import create_consumer


@pytest.fixture
def redis_client():
    """Fixture providing a Redis client connected to test Redis instance"""
    return Redis(host='redis', port=6379)


@pytest.fixture
def redpanda_consumer():
    """Fixture providing a Kafka consumer for test topics"""
    return create_consumer(
        topic='ticks.raw',
        group_id='test-group'
    )


@pytest.fixture(autouse=True)
def clear_redis(redis_client):
    """Auto-used fixture to clear Redis before each test"""
    redis_client.flushall()
    yield
    redis_client.flushall()
