"""Reverse DCF: solve observable economic drivers, not arbitrary FCF CAGR."""
from dataclasses import dataclass

from .domain import CapitalStructure, MarketSnapshot
from .forecasting import ForecastCase, replace_growth, shift_margins
from .valuation import value_case


@dataclass(frozen=True)
class ReverseResult:
    parameter: str
    implied_value: float | None
    lower: float
    upper: float
    reason: str | None


def target_enterprise_value(market: MarketSnapshot, capital: CapitalStructure) -> float:
    if market.currency != capital.currency:
        raise ValueError('Market currency mismatch; convert FX and ADR ratios explicitly')
    return capital.ev_from_equity(market.market_equity(capital.diluted_shares)).amount


def bisect_target(f, target: float, lower: float, upper: float,
                  *, tolerance: float = 1e-8) -> float | None:
    """Bracketed continuous monotone root only; no extrapolation on failure."""
    if lower >= upper:
        raise ValueError("Lower root bound must be below upper bound")
    fl = f(lower) - target
    fu = f(upper) - target
    if abs(fl) <= tolerance:
        return lower
    if abs(fu) <= tolerance:
        return upper
    if fl * fu > 0:
        return None
    # Detect clear nonmonotonicity before interpreting a root as an implied economic expectation.
    checkpoints = [f(lower + (upper-lower)*i/16) for i in range(17)]
    changes = [checkpoints[i+1] - checkpoints[i] for i in range(16)]
    if not (all(v >= -1e-8 for v in changes) or all(v <= 1e-8 for v in changes)):
        return None
    for _ in range(180):
        mid = (lower + upper) / 2
        fm = f(mid) - target
        if abs(fm) <= tolerance or (upper - lower) < 1e-12:
            return mid
        if fm * fl > 0:
            lower, fl = mid, fm
        else:
            upper, fu = mid, fm
    return (lower + upper) / 2


def implied_constant_revenue_growth(case: ForecastCase, capital: CapitalStructure,
                                    market: MarketSnapshot,
                                    lower: float = -0.5, upper: float = 0.8) -> ReverseResult:
    target = target_enterprise_value(market, capital)
    def ev(x: float) -> float:
        return value_case(replace_growth(case, x), capital).enterprise_value.amount
    result = bisect_target(ev, target, lower, upper)
    return ReverseResult('annual revenue growth', result, lower, upper,
                         None if result is not None else 'No bracketed root; price requires assumptions outside search bounds or alternative margins')


def implied_margin_shift(case: ForecastCase, capital: CapitalStructure,
                         market: MarketSnapshot, fixed_revenue_growth: float,
                         lower: float = -0.2, upper: float = 0.2) -> ReverseResult:
    target = target_enterprise_value(market, capital)
    fixed = replace_growth(case, fixed_revenue_growth)
    # The inverse problem must stay inside valid terminal perpetuity economics.
    # A user-supplied lower margin bound may imply nonpositive terminal FCFF;
    # clip the search domain rather than discarding a perfectly valid interior root.
    valid_lower = max(lower, -fixed.terminal.ebit_margin + 1e-9,
                      -1 - min(d.ebit_margin for d in fixed.drivers))
    valid_upper = min(upper, 1 - fixed.terminal.ebit_margin,
                      1 - max(d.ebit_margin for d in fixed.drivers))
    if valid_lower >= valid_upper:
        return ReverseResult('EBIT margin shift', None, valid_lower, valid_upper,
                             'No economically valid EBIT margin interval')
    def ev(x: float) -> float:
        return value_case(shift_margins(fixed, x), capital).enterprise_value.amount
    try:
        result = bisect_target(ev, target, valid_lower, valid_upper)
        return ReverseResult('EBIT margin shift', result, valid_lower, valid_upper,
                             None if result is not None else 'No bracketed solution within valid margin bounds')
    except ValueError as e:
        return ReverseResult('EBIT margin shift', None, valid_lower, valid_upper, f'Invalid assumptions: {e}')


def revenue_margin_frontier(case: ForecastCase, capital: CapitalStructure,
                             market: MarketSnapshot, growth_options: tuple[float, ...],
                             margin_bounds: tuple[float, float] = (-0.2, 0.2)) -> tuple[tuple[float, ReverseResult], ...]:
    return tuple((g, implied_margin_shift(case, capital, market, g, *margin_bounds))
                 for g in growth_options)
