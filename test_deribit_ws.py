import asyncio
from services.ingestor.ingest.deribit_ws import stream, get_live_data

async def test_stream():
    """Test the Deribit WebSocket stream and data access"""
    print("Starting test...")

    # Start the stream in background
    stream_task = asyncio.create_task(stream())

    try:
        # Wait a bit for data to accumulate
        await asyncio.sleep(10)

        # Test get_live_data()
        print("\nTesting get_live_data():")
        data = get_live_data()
        print(f"Got {len(data)} instruments in snapshot")
        if data:
            print("Sample instrument:", data[0])

    finally:
        # Clean up
        stream_task.cancel()
        try:
            await stream_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(test_stream())
