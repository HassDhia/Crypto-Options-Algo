# backend/app/deribit_api.py
import httpx, time

BASE_URL = "https://www.deribit.com/api/v2/public"

def fetch_options_snapshot(currency: str = "BTC") -> list[dict]:
    """
    Fetch live options data for the given currency from Deribit.
    Returns a list of option data dicts.
    """
    url = f"{BASE_URL}/get_book_summary_by_currency?currency={currency}&kind=option"
    resp = httpx.get(url, timeout=10)
    data = resp.json().get("result", [])
    # Enrich data with time-to-maturity (ttm in years) and decimal implied vol
    now = time.time()
    for opt in data:
        # Deribit provides expiration_timestamp in ms
        exp_ts = opt["expiration_timestamp"] / 1000.0
        opt["ttm"] = max((exp_ts - now) / (365 * 24 * 3600), 1e-6)  # years until expiry
        opt["mark_iv"] = opt["mark_iv"] / 100.0  # convert IV from % to fraction
    return data
