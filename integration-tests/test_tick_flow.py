def test_tick_flow(redis_client, redpanda_consumer):
    assert redpanda_consumer.group_offsets("ticks.raw") > 0
    assert redis_client.get("last_bid") is not None
