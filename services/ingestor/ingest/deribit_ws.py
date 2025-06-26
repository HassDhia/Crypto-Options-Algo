import json
import datetime as dt
from typing import AsyncGenerator

import aiohttp


URL = "wss://www.deribit.com/ws/api/v2"
TOPIC = "book.24h.BTC-PERPETUAL.raw"


async def stream() -> AsyncGenerator[dict, None]:
    async with aiohttp.ClientSession() as sess, sess.ws_connect(URL) as ws:
        await ws.send_json({
            "method": "public/subscribe",
            "params": {"channels": [TOPIC]},
            "id": 42
        })
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                ts = dt.datetime.utcnow().isoformat()
                print(f"{ts}  {msg.data[:120]}")
                yield data
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break
