import math
import pytest
from common.quant import bs

def test_theo_price_call():
    price = bs.theo_price('c', 100, 100, 0.5, 0.01, 0.2)
    assert price > 0
    assert price > 4.0  # Rough estimate for ATM call


def test_theo_price_put():
    price = bs.theo_price('p', 100, 100, 0.5, 0.01, 0.2)
    assert price > 0
    assert price > 3.5  # Rough estimate for ATM put


def test_delta_magnitude():
    call_price = bs.theo_price('c', 100, 100, 0.5, 0.01, 0.2)
    put_price = bs.theo_price('p', 100, 100, 0.5, 0.01, 0.2)
    assert call_price > put_price  # Calls should be more valuable in normal conditions


def test_edge_calculation():
    theo = 10.0
    mid = 9.5
    edge = (theo - mid) / mid
    assert edge == pytest.approx(0.05263, abs=0.01)


def test_call_theo_price_precision():
    # Known Black-Scholes call price for S=100,K=100,r=0,t=1,σ=0.20
    theo = bs.theo_price('c', 100, 100, 1.0, 0.0, 0.20)
    assert math.isclose(theo, 7.9656, rel_tol=1e-4)
