"""Historical diagnostics with explicit 'not meaningful' for negative baselines."""
from math import isfinite


def cagr(start: float, end: float, years: int) -> float | None:
    if years <= 0 or not all(isfinite(x) for x in (start, end)):
        raise ValueError('Invalid period or values')
    if start <= 0 or end <= 0:
        return None
    return (end/start)**(1/years)-1


def yoy(prior: float, latest: float) -> float | None:
    if not all(isfinite(x) for x in (prior, latest)):
        raise ValueError('Nonfinite values')
    if prior <= 0:
        return None
    return latest/prior - 1
