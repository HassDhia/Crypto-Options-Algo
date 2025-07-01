"""
Simplest REST puller – avoids websockets for MVP speed.
Fetches book summaries once per call.
"""
import httpx, logging, time

logger = logging.getLogger(__name__)
BASE = "https://www.deribit.com/api/v2/public"

_latest_snapshot: list[dict] = []  # populated by fetch()

def fetch_snapshot(currency: str = "BTC") -> list[dict]:
    url = f"{BASE}/get_book_summary_by_currency?currency={currency}&kind=option"
    try:
        data = httpx.get(url, timeout=10).json()["result"]
        # add time-to-maturity (ttm) and mark_iv convenience keys
        now = time.time()
        for opt in data:
            exp = opt["expiration_timestamp"] / 1000
            opt["ttm"] = max((exp - now) / (365 * 24 * 3600), 1e-6)
            opt["mark_iv"] = opt["mark_iv"] / 100  # convert pct→dec
        global _latest_snapshot
        _latest_snapshot = data
        return data
    except Exception as e:
        logger.warning("Deribit fetch failed: %s", e)
        return _latest_snapshot  # fallback
