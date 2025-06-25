import asyncio, json, aiohttp
from typing import AsyncGenerator

URL = "wss://www.deribit.com/ws/api/v2"
PING = {"jsonrpc": "2.0", "id": 42, "method": "public/test"}

async def stream() -> AsyncGenerator[dict, None]:
    async with aiohttp.ClientSession() as sess, sess.ws_connect(URL) as ws:
        await ws.send_json(PING)
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                yield json.loads(msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break
