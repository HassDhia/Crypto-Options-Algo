import math
from common.quant.bs import theo_price  # re‑use existing math

WEIGHTS = dict(delta=0.4, gamma=0.3, vega=0.3)

def calculate_greeks(opt):
    s, k, t, sigma, r, right = (
        opt["underlying"],
        opt["strike"],
        opt["ttm"],
        opt["iv"],
        0.0,
        "c" if opt["type"] == "call" else "p",
    )
    # You already have delta + vega helpers in bs.py
    from py_vollib.black_scholes.greeks.analytic import delta, gamma, vega
    return {
        "delta": delta(right, s, k, t, r, sigma),
        "gamma": gamma(right, s, k, t, r, sigma),
        "vega":  vega(right,  s, k, t, r, sigma),
    }

def score_profitability(g):
    return sum(WEIGHTS[k] * g[k] for k in WEIGHTS)

def rank_options(raw_opts):
    enriched = []
    for o in raw_opts:
        greeks = calculate_greeks(o)
        score = score_profitability(greeks)
        enriched.append({**o, **greeks, "score": score})
    return sorted(enriched, key=lambda x: x["score"], reverse=True)[:5]
