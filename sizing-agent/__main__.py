import os
import math
import logging
import redis
from common.kafka import create_consumer, create_producer
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KellySizer:
    """
    Calculates position size using a Bayesian-Kelly criterion approach.
    """
    def __init__(self, capital: float, max_fraction: float = 1.0):
        """
        :param capital: Total capital (or bankroll) to allocate from
        :param max_fraction: Max fraction of capital to use on one trade
        """
        self.capital = capital
        self.max_fraction = max_fraction

    def compute_size(
        self,
        edge: float,
        volatility: float,
        price: float
    ) -> int:
        """
        Compute position size (number of contracts) based on edge and volatility.
        :param edge: Expected edge (fractional expected return of the trade)
        :param volatility: Standard deviation or risk factor for the trade
        :param price: Current option price
        :return: Recommended number of contracts to trade
        """
        if edge <= 0 or volatility <= 0:
            # No positive expected return or no volatility info => no trade
            return 0

        # Kelly fraction: edge / variance
        # (approximation for normally-distributed returns)
        kelly_fraction = edge / (volatility ** 2)

        # Cap the fraction to avoid over-betting
        kelly_fraction = max(0.0, min(kelly_fraction, self.max_fraction))

        # Allocate this fraction of capital to the trade
        allocated_capital = kelly_fraction * self.capital
        if allocated_capital <= 0:
            return 0

        # Number of contracts = allocated capital / price per contract
        num_contracts = allocated_capital / price

        # Since contracts must be whole numbers, take floor
        size = math.floor(num_contracts)

        # Ensure at least 1 contract if we have any positive allocation
        if size == 0 and kelly_fraction > 0:
            size = 1

        return int(size)

# Configuration: capital base for sizing (could come from portfolio or config)
capital_base = float(os.getenv("TRADING_CAPITAL", "100000"))  # e.g. $100k play-money
sizer = KellySizer(capital=capital_base, max_fraction=0.2)  # don't bet more than 20% on any single trade

# Connect to Redis (for market data or risk parameters if needed)
redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'),
                           port=int(os.getenv('REDIS_PORT', 6379)), db=0)
consumer = create_consumer("ticks.scouted")
producer = create_producer()
logger.info("Sizing agent started with capital base $%.2f", capital_base)

for message in consumer:
    try:
        tick = message.value  # a scouted tick (already filtered and risk-checked candidate)
        instrument = tick.get("instrument")
        bid = tick.get("bid")
        ask = tick.get("ask")
        if instrument is None or bid is None or ask is None:
            continue

        # Determine current price to use for sizing (use ask if we plan to buy, bid if we plan to sell)
        # Assuming strategy is to buy undervalued options (long positions) as an example
        price = ask

        # Estimate edge and volatility for this instrument
        edge = 0.0
        vol = 0.0
        try:
            # Fetch pre-computed analytics from Redis
            edge_val = redis_client.hget("analytics:edges", instrument)
            vol_val = redis_client.hget("analytics:vols", instrument)
            if edge_val:
                edge = float(edge_val)
            if vol_val:
                vol = float(vol_val)
        except Exception as e:
            logger.warning(f"Could not fetch analytics for sizing {instrument}: {e}")

        # Fallback to basic assumptions if data missing
        if edge == 0.0:
            try:
                # Use filter threshold as baseline edge
                params = redis_client.hgetall("filter_params")
                if params and b'min_edge' in params:
                    edge = float(params[b'min_edge'])
                else:
                    edge = 0.01  # default 1% edge
            except Exception:
                edge = 0.01
        if vol == 0.0:
            vol = 0.5  # default 50% volatility

        # Ensure reasonable values
        edge = max(0.0, min(edge, 1.0))
        vol = max(1e-6, min(vol, 3.0))  # avoid zero and cap at 300%

        # Compute position size using Kelly sizing
        contracts = sizer.compute_size(edge=edge, volatility=vol, price=price)

        # Risk adjustment: cap position size at 10 contracts (temporary safeguard)
        MAX_POSITION = 10
        if contracts > MAX_POSITION:
            logger.info(f"Capping position size for {instrument} from {contracts} to {MAX_POSITION}")
            contracts = MAX_POSITION

        # Publish sizing decision
        size_signal = {
            "instrument": instrument,
            "size": float(contracts),
            "timestamp": int(datetime.utcnow().timestamp() * 1000)
        }
        producer.send("size.signals", value=size_signal)

        # Log the size signal with formatted percentages
        edge_pct = edge * 100
        vol_pct = vol * 100
        log_msg = (
            f"Size signal for {instrument}: {contracts} contracts "
            f"(edge={edge_pct:.2f}%, vol={vol_pct:.2f}%)"
        )
        logger.info(log_msg)
    except Exception as e:
        logger.error(f"Error in Sizing agent for {message}: {e}")
