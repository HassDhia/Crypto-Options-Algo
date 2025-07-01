import os
import logging
import redis
from datetime import datetime
from typing import Dict, Optional
from common.quant import bs  # New import


logger = logging.getLogger(__name__)


class OptionFilter:
    """Encapsulates deterministic filtering logic for option candidates."""
    def __init__(
        self,
        delta_min: float = 0.25,
        delta_max: float = 0.75,
        min_edge: float = 0.0,
        max_skew: float = float('inf'),
        avoid_iv_crush: bool = False
    ):
        """
        Initialize filter thresholds.
        :param delta_min: Minimum acceptable delta (0.0-1.0)
        :param delta_max: Maximum acceptable delta (0.0-1.0)
        :param min_edge: Minimum theoretical edge (decimal fraction)
        :param max_skew: Maximum acceptable IV skew ratio
        :param avoid_iv_crush: Filter options near expiration to avoid IV crush
        """
        self.delta_min = delta_min
        self.delta_max = delta_max
        self.min_edge = min_edge
        self.max_skew = max_skew
        self.avoid_iv_crush = avoid_iv_crush

    def _compute_delta(self, instrument: str) -> float:
        """Compute option's delta based on moneyness heuristic"""
        try:
            parts = instrument.split('-')
            underlying_sym = parts[0]
            strike = float(parts[2])
            option_type = parts[3]
        except Exception as e:
            logger.warning(f"Could not parse instrument {instrument}: {e}")
            return 0.5  # ATM default

        # Get underlying price from Redis
        underlying_price = self._get_underlying_price(underlying_sym)
        if underlying_price is None:
            # Fallback to strike price if no market data
            underlying_price = strike

        # Calculate moneyness ratio
        moneyness = underlying_price / strike

        # Delta approximation based on moneyness
        if option_type == 'C':
            # Calls: ITM when underlying > strike
            delta = max(0.0, min(1.0,
                0.5 * (moneyness ** 0.5)
            )
        elif option_type == 'P':
            # Puts: ITM when underlying < strike
            delta = max(0.0, min(1.0,
                0.5 * ((strike / underlying_price) ** 0.5)
            )
        else:
            delta = 0.5

        return delta

    def _get_underlying_price(self, symbol: str) -> Optional[float]:
        """Get underlying price from Redis"""
        try:
            r = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=0
            )
            price = r.get(f"last_price:{symbol}")
            return float(price) if price else None
        except Exception as e:
            logger.error(f"Error getting underlying price: {e}")
            return None

    def _compute_theoretical_edge(
        self, instrument: str, bid: float, ask: float
    ) -> float:
        """Estimate theoretical edge using Black-Scholes when enabled"""
        if os.getenv("SCOUT_USE_BS", "0") == "1":
            try:
                # Parse instrument to extract strike and option type
                parts = instrument.split('-')
                strike = float(parts[2])
                option_type = parts[3].lower()
                right = 'c' if option_type == 'c' else 'p'

                # Get underlying price - using existing method
                underlying_sym = parts[0]
                s = self._get_underlying_price(underlying_sym)
                if s is None:
                    return 0.0

                # Parse expiration time
                expiry_str = parts[1]
                exp_day = int(expiry_str[:2])
                exp_month_str = expiry_str[2:5]
                exp_year = 2000 + int(expiry_str[5:])
                exp_month = datetime.strptime(exp_month_str, "%b").month
                exp_date = datetime(exp_year, exp_month, exp_day)
                t = (exp_date - datetime.utcnow()).days / 365.0

                # Placeholder values - should be replaced with actual market data
                r = 0.01  # Risk-free rate
                sigma = 0.7  # IV

                # Calculate theoretical price
                theo = bs.theo_price(right, s, strike, t, r, sigma)
                mid_px = (bid + ask) / 2.0
                edge_pct = (theo - mid_px) / mid_px
                return edge_pct
            except Exception as e:
                logger.error(f"BS calculation failed: {e}")
                return 0.0
        else:
            # Fallback to existing heuristic
            return 0.0

    def _check_iv_skew(self, instrument: str) -> bool:
        """Check IV skew/crush criteria"""
        if not self.avoid_iv_crush:
            return True

        try:
            # Parse expiration date from instrument code
            parts = instrument.split('-')
            expiry_str = parts[1]

            # Parse expiration date (format: DDMMMYY)
            exp_day = int(expiry_str[:2])
            exp_month_str = expiry_str[2:5]
            exp_year = 2000 + int(expiry_str[5:])
            exp_month = datetime.strptime(exp_month_str, "%b").month
            exp_date = datetime(exp_year, exp_month, exp_day)

            # Check if expiration is within 2 days
            if (exp_date - datetime.utcnow()).days < 2:
                return False
        except Exception as e:
            logger.warning(f"IV crush check failed for {instrument}: {e}")

        return True

    def is_candidate(self, tick: Dict) -> bool:
        """Apply all filters to determine if tick is a trade candidate"""
        instrument = tick.get("instrument")
        bid = tick.get("bid")
        ask = tick.get("ask")

        if None in (instrument, bid, ask):
            return False

        delta = self._compute_delta(instrument)
        edge = self._compute_theoretical_edge(instrument, bid, ask)
        iv_ok = self._check_iv_skew(instrument)

        # Apply filter criteria
        if not (self.delta_min <= delta <= self.delta_max):
            return False
        if edge < self.min_edge:
            return False
        if not iv_ok:
            return False

        return True
