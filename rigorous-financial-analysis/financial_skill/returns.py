"""Investor cash-flow IRR. Distributions and exit valuation are EXPLICIT assumptions."""
from math import isfinite

from .domain import finite


def shareholder_irr(purchase_price: float, dividends_per_share: tuple[float, ...],
                    exit_price: float) -> float:
    purchase = finite(purchase_price, 'purchase price')
    exit_value = finite(exit_price, 'exit price')
    if purchase <= 0 or exit_value < 0 or not dividends_per_share:
        raise ValueError('Positive price, nonnegative exit and >=1 annual dividends required')
    if any(not isfinite(d) or d < 0 for d in dividends_per_share):
        raise ValueError('Dividends must be finite and nonnegative')
    def npv(r: float) -> float:
        return -purchase + sum(d / (1 + r)**(i+1) for i, d in enumerate(dividends_per_share)) + exit_value / (1 + r)**len(dividends_per_share)
    lo, hi = -0.999999, 10.0
    if npv(lo) * npv(hi) > 0:
        raise ValueError('IRR root outside [-99.9999%, 1000%] or undefined')
    for _ in range(160):
        mid = (lo + hi)/2
        if npv(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi)/2
