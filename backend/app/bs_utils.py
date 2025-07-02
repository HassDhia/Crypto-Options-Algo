# backend/app/bs_utils.py
import math

def norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function."""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def norm_pdf(x: float) -> float:
    """Standard normal probability density function."""
    return (1.0 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * x * x)

def black_scholes_greeks(flag: str, S: float, K: float, T: float, sigma: float):
    """Compute Black-Scholes delta, gamma, vega for a given option."""
    if T <= 0 or S <= 0 or sigma <= 0:
        # Handle edge cases – return zeros
        return {"delta": 0.0, "gamma": 0.0, "vega": 0.0}
    # Black-Scholes d1 and d2
    d1 = (math.log(S/K) + 0.5 * sigma**2 * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    # Delta: N(d1) for calls, N(d1)-1 for puts
    delta = norm_cdf(d1) if flag == 'c' else norm_cdf(d1) - 1.0
    # Gamma: probability density * factor
    gamma = norm_pdf(d1) / (S * sigma * math.sqrt(T))
    # Vega: option vega (per 1.0 vol change, scaled by 100 if needed per 1% vol)
    vega = S * norm_pdf(d1) * math.sqrt(T)
    return {"delta": delta, "gamma": gamma, "vega": vega}
