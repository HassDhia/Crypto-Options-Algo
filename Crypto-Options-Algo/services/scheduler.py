import asyncio, logging, os
from services.ingestor.deribit_ws import fetch_snapshot
from services.calculator import top_n
from services.api.app import push_top_options  # runtime import

log = logging.getLogger(__name__)
INTERVAL = int(os.getenv("REFRESH_SECS", 300))  # 5 min default

async def run():
    while True:
        snap = fetch_snapshot("BTC")
        leaders = top_n(snap)
        push_top_options(leaders)
        log.info("Top5: %s", [o["instrument_name"] for o in leaders])
        await asyncio.sleep(INTERVAL)

if __name__ == "__main__":
    import uvloop; uvloop.install()
    asyncio.run(run())
