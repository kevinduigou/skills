"""Finite-difference fragility and explicit cash-runway / ruin thresholds.
No risk probabilities are inferred from three stress scenarios.
"""
from dataclasses import dataclass, replace

from .domain import CapitalStructure, DiscountRate, finite
from .forecasting import ForecastCase
from .valuation import value_case


@dataclass(frozen=True)
class EconomicShock:
    """First forecast year's revenue multiplier plus persistent margin/capex shifts.
    revenue_change=-0.2 = 20% lower year-one revenue, propagated to later years.
    Reinvested NWC responds to actual year-one revenue change.
    """
    revenue_change: float = 0.0
    ebit_margin_delta: float = 0.0
    capex_to_revenue_delta: float = 0.0
    discount_rate_delta: float = 0.0

    def __post_init__(self) -> None:
        if finite(self.revenue_change, 'shock revenue change') <= -1:
            raise ValueError('shock revenue change must be greater than -100%')
        for name in ['ebit_margin_delta', 'capex_to_revenue_delta', 'discount_rate_delta']:
            finite(getattr(self, name), name)


def shock_case(case: ForecastCase, shock: EconomicShock) -> ForecastCase:
    drivers = list(case.drivers)
    first = drivers[0]
    drivers[0] = replace(first, revenue_growth=(1 + first.revenue_growth) * (1 + shock.revenue_change) - 1)
    drivers = [replace(d, ebit_margin=d.ebit_margin + shock.ebit_margin_delta,
                       capex_to_revenue=d.capex_to_revenue + shock.capex_to_revenue_delta) for d in drivers]
    return replace(case, drivers=tuple(drivers),
                   discount_rate=DiscountRate(case.discount_rate.annual + shock.discount_rate_delta),
                   terminal=replace(case.terminal, ebit_margin=case.terminal.ebit_margin + shock.ebit_margin_delta))


@dataclass(frozen=True)
class ShockResult:
    base_equity: float
    shocked_equity: float
    signed_loss: float
    downside_loss: float
    percent_loss: float | None


def evaluate_shock(case: ForecastCase, capital: CapitalStructure, shock: EconomicShock) -> ShockResult:
    base = value_case(case, capital).equity_value.amount
    stressed = value_case(shock_case(case, shock), capital).equity_value.amount
    signed_loss = base - stressed
    return ShockResult(base, stressed, signed_loss, max(0, signed_loss),
                       signed_loss / base if base > 0 else None)


@dataclass(frozen=True)
class Curvature:
    signed_difference: float
    normalized: float | None
    description: str


def adverse_loss_curvature(v0: float, vh: float, v2h: float) -> Curvature:
    """C = L(2h)-2L(h)+L(0) using SIGNED losses; no max(0,..) kink."""
    for v in (v0, vh, v2h):
        finite(v, 'valuation')
    value = 2 * vh - v2h - v0
    return Curvature(value, value / v0 if v0 > 0 else None,
                     'Positive values: adverse losses accelerate over these equally spaced shock increments')


def dispersion_fragility(v_minus_h: float, v0: float, v_plus_h: float) -> Curvature:
    """J=[L(-h)+L(h)]/2-L(0) = V(0) - [V(-h)+V(h)]/2.
    Positive means same-mean dispersion lowers average modeled equity value.
    """
    for v in (v_minus_h, v0, v_plus_h):
        finite(v, 'valuation')
    value = v0 - (v_minus_h + v_plus_h) / 2
    return Curvature(value, value / v0 if v0 > 0 else None,
                     'Positive values: wider symmetric shock dispersion reduces average valuation')


@dataclass(frozen=True)
class LiquidityYear:
    year: int
    ending_cash: float
    shortfall_below_buffer: float


@dataclass(frozen=True)
class LiquidityResult:
    path: tuple[LiquidityYear, ...]
    first_breach_year: int | None
    peak_funding_gap: float


def liquidity_runway(initial_cash: float, operating_fcf: tuple[float, ...],
                     debt_maturities: tuple[float, ...], minimum_cash: float = 0,
                     committed_liquidity: float = 0) -> LiquidityResult:
    """Simplified liquidity bridge, same millions and currency for all amounts.
    operating_fcf must include mandatory cash interest and maintenance capex.
    committed_liquidity represents reliably drawable funding, not uncommitted credit.
    """
    cash = finite(initial_cash, 'cash') + finite(committed_liquidity, 'committed liquidity')
    if cash < 0 or minimum_cash < 0 or committed_liquidity < 0:
        raise ValueError('Cash, funding and cash buffer must be nonnegative')
    if not operating_fcf or len(operating_fcf) != len(debt_maturities):
        raise ValueError('Equal nonempty annual arrays required')
    path = []
    first = None
    for y, (fcf, maturity) in enumerate(zip(operating_fcf, debt_maturities), 1):
        if finite(maturity, 'maturity') < 0:
            raise ValueError('Debt maturity cannot be negative')
        cash += finite(fcf, 'FCF') - maturity
        gap = max(0., minimum_cash - cash)
        if gap > 0 and first is None:
            first = y
        path.append(LiquidityYear(y, cash, gap))
    return LiquidityResult(tuple(path), first, max(x.shortfall_below_buffer for x in path))
