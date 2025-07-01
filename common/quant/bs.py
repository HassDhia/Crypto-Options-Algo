def theo_price(right, s, k, t, r, sigma):
    """
    Calculate theoretical option price using Black-Scholes
    :param right: 'c' for call, 'p' for put
    :param s: underlying price
    :param k: strike price
    :param t: time to expiration in years
    :param r: risk-free rate (decimal)
    :param sigma: volatility (decimal)
    :return: theoretical price
    """
    from py_vollib.black_scholes import black_scholes
    return black_scholes(right, s, k, t, r, sigma)
