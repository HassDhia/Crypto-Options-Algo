# backend/app/calculator.py
from . import bs_utils

# Example weightings for the score (can adjust as needed)
W_DELTA = 1.0
W_GAMMA = 0.5
W_VEGA  = 0.1

def score_option(opt: dict) -> float:
    """Calculate a simple profitability score for an option based on Greeks."""
    # Determine if option is call or put from instrument name or field
    flag = 'c' if opt.get("option_type", "").lower() == "call" \
             or opt["instrument_name"].endswith("-C") else 'p'
    S = opt["underlying_price"]    # current underlying (e.g. BTC) price
    K = opt.get("strike_price") or float(opt["instrument_name"].split("-")[2])
    T = opt["ttm"]                # time-to-maturity in years (computed on fetch)
    sigma = opt["mark_iv"]        # implied vol (decimal form)
    greeks = bs_utils.black_scholes_greeks(flag, S, K, T, sigma)
    # Weighted sum of selected Greeks
    score = (W_DELTA * greeks["delta"] 
             + W_GAMMA * greeks["gamma"] 
             + W_VEGA  * greeks["vega"])
    return score

def rank_options(options: list, top_n: int = 5) -> list:
    """Return the top N options from the list, ranked by our score."""
    for opt in options:
        opt_score = score_option(opt)
        opt["score"] = opt_score
    # Sort options in descending order of score
    options.sort(key=lambda o: o["score"], reverse=True)
    return options[:top_n]
