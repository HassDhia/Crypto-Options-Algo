"""
Tiny Black‑Scholes helper re‑exporting py_vollib functions
so the rest of the code calls one module.
"""
from py_vollib.black_scholes import black_scholes
from py_vollib.black_scholes.greeks.analytic import delta, gamma, vega

__all__ = ["theo_price", "delta", "gamma", "vega"]


def theo_price(right: str, s: float, k: float, t: float, r: float, sigma: float) -> float:
    """
    right: 'c' for call, 'p' for put
    s: spot
    k: strike
    t: time to maturity (years)
    r: risk‑free (0 for crypto)
    sigma: implied vol
    """
    return black_scholes(right, s, k, t, r, sigma)
