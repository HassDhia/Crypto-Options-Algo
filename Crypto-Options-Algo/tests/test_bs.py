from common.quant.bs import theo_price
import math

def test_theo_basic():
    p = theo_price('c', 100, 100, 1, 0, 0.2)
    assert math.isclose(round(p, 4), 7.9656, rel_tol=1e-4)
