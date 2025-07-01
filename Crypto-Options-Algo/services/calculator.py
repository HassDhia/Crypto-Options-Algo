import logging
from common.quant import bs

WEIGHTS = dict(delta=0.4, gamma=0.3, vega=0.3)
log = logging.getLogger(__name__)

def greeks(opt: dict) -> dict:
    """Compute Δ, Γ, Vega via py_vollib helpers."""
    s = opt["underlying_price"]
    k = opt["strike"]
    t = opt["ttm"]
    sigma = opt["mark_iv"]
    r = 0.0
    right = "c" if opt["option_type"] == "call" else "p"
    return dict(
        delta=bs.delta(right, s, k, t, r, sigma),
        gamma=bs.gamma(right, s, k, t, r, sigma),
        vega=bs.vega(right,  s, k, t, r, sigma),
    )

def score(opt: dict) -> float:
    g = greeks(opt)
    return sum(WEIGHTS[k] * g[k] for k in WEIGHTS)

def top_n(snapshot: list[dict], n: int = 5) -> list[dict]:
    enriched = []
    for o in snapshot:
        if o["bid_price"] == 0:          # ignore 0‑bid
            continue
        g = greeks(o)
        enriched.append({**o, **g, "score": score(o)})
    enriched.sort(key=lambda x: x["score"], reverse=True)
    return enriched[:n]
