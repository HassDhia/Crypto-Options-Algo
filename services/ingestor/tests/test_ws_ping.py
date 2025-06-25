import asyncio, pytest, ingest.deribit_ws as ws

@pytest.mark.asyncio
async def test_ping():
    gen = ws.stream()
    msg = await asyncio.wait_for(gen.__anext__(), timeout=10)
    assert msg["id"] == 42
