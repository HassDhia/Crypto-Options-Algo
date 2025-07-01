import os
import sys
import pytest
import json

# Setup path before other imports
parent_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.insert(0, parent_dir)

# Local imports after path setup
from freezegun import freeze_time  # noqa: E402
from unittest.mock import AsyncMock, patch  # noqa: E402
from ingest.deribit_ws import stream, emit_snapshots  # noqa: E402


@pytest.mark.asyncio
@freeze_time("2025-01-01 00:00:00")
async def test_throttling_emits_once_per_interval():
    """Test that snapshots are emitted exactly once per 5-minute interval"""
    mock_redis = AsyncMock()
    mock_metrics = AsyncMock()
    mock_ws = AsyncMock()
    mock_ws.__aenter__.return_value = mock_ws

    # Mock websocket messages
    mock_ws.receive.side_effect = [
        AsyncMock(type=1, data=json.dumps({
            "params": {
                "channel": "ticker.BTC-OPTION.raw",
                "data": {
                    "instrument_name": "BTC-31DEC25-40000-C",
                    "mark_iv": 0.5,
                    "delta": 0.25
                }
            }
        })),
        # This will make the test run forever unless we limit it
        RuntimeError("Test complete")
    ]

    with patch('aiohttp.ClientSession') as mock_session, \
         patch('aioredis.Redis') as mock_redis_cls:
        mock_session.return_value.__aenter__.return_value = mock_ws
        mock_redis_cls.return_value = mock_redis

        # Run with frozen time
        with pytest.raises(RuntimeError):
            async for _ in stream():
                pass

    # Verify snapshot was emitted once
    mock_redis.scan_iter.assert_called_once()
    mock_metrics.incr.assert_called()


@pytest.mark.asyncio
async def test_emit_snapshots_with_complete_data():
    """Test snapshot emission with complete instrument data"""
    mock_redis = AsyncMock()
    mock_metrics = AsyncMock()

    # Mock Redis response
    mock_redis.hgetall.return_value = {
        "bids": json.dumps([40000, 1]),
        "asks": json.dumps([41000, 1]),
        "mark_iv": "0.5",
        "delta": "0.25"
    }
    mock_redis.scan_iter.return_value.__aiter__.return_value = [
        b"book:BTC-31DEC25-40000-C"
    ]

    await emit_snapshots(mock_redis, mock_metrics)

    # Verify metrics were updated
    mock_metrics.incr.assert_called_with(
        "ingestor_ticks_emitted_total", 1
    )


@pytest.mark.asyncio
async def test_emit_snapshots_with_incomplete_data():
    """Test snapshot emission with incomplete instrument data"""
    mock_redis = AsyncMock()
    mock_metrics = AsyncMock()

    # Mock Redis response missing required fields
    mock_redis.hgetall.return_value = {
        "bids": json.dumps([40000, 1]),
        "asks": json.dumps([41000, 1])
    }
    mock_redis.scan_iter.return_value.__aiter__.return_value = [
        b"book:BTC-31DEC25-40000-C"
    ]

    await emit_snapshots(mock_redis, mock_metrics)

    # Verify incomplete metric was updated
    mock_metrics.incr.assert_called_with(
        "ingestor_snapshot_incomplete_total", 1
    )
