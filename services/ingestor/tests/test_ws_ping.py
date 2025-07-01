import asyncio
import os
import sys

# Setup path before other imports
parent_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.insert(0, parent_dir)

# Local imports after path setup - must be after sys.path modification
import pytest  # noqa: E402
from ingest import deribit_ws as ws  # noqa: E402

@pytest.mark.asyncio
async def test_ping():
    gen = ws.stream()
    msg = await asyncio.wait_for(gen.__anext__(), timeout=10)
    assert msg["id"] == 42
