"""FCFF enterprise DCF and equity bridge. Does not mix FCFE with WACC."""
from dataclasses import dataclass

from .domain import CapitalStructure, MoneyMillions
from .forecasting import ForecastCase, ForecastYear, make_forecast, terminal_fcff


@dataclass(frozen=True)
class Valuation:
    case: ForecastCase
    years: tuple[ForecastYear, ...]
    explicit_pv: MoneyMillions
    terminal_fcff_next: MoneyMillions
    terminal_pv: MoneyMillions
    enterprise_value: MoneyMillions
    equity_residual: MoneyMillions   # may be negative, a financial distress signal
    equity_value: MoneyMillions      # limited-liability floor, not option valuation
    distress_flag: bool
    fair_price: float
    terminal_share: float


def value_case(case: ForecastCase, capital: CapitalStructure) -> Valuation:
    if case.starting_revenue.currency != capital.currency:
        raise ValueError('Forecast/capital currency mismatch')
    years = make_forecast(case)
    r = case.discount_rate.annual
    g = case.terminal.growth
    pv_explicit = sum(y.fcff.amount / (1 + r)**y.year for y in years)
    normalized = terminal_fcff(case, years[-1])
    tv_now = (normalized.amount / (r - g)) / (1 + r)**len(years)
    ev = MoneyMillions(pv_explicit + tv_now, capital.currency)
    residual = capital.equity_from_ev(ev)
    equity = MoneyMillions(max(0.0, residual.amount), capital.currency)
    if ev.amount == 0:
        raise ValueError('Terminal share undefined for zero EV')
    return Valuation(case, years, MoneyMillions(pv_explicit, capital.currency),
                     normalized, MoneyMillions(tv_now, capital.currency), ev, residual, equity,
                     residual.amount <= 0, equity.amount / capital.diluted_shares.count, tv_now / ev.amount)


def sensitivity(case: ForecastCase, capital: CapitalStructure,
                discount_shifts: tuple[float, ...]=(-.02, 0, .02),
                growth_shifts: tuple[float, ...]=(-.01, 0, .01)) -> tuple[tuple[float, float, float | None], ...]:
    from dataclasses import replace
    from .domain import DiscountRate
    results = []
    for dr in discount_shifts:
        for dg in growth_shifts:
            new_r, new_g = case.discount_rate.annual + dr, case.terminal.growth + dg
            if new_r <= max(0, new_g):
                results.append((new_r, new_g, None))
                continue
            try:
                adjusted = replace(case, discount_rate=DiscountRate(new_r),
                                   terminal=replace(case.terminal, growth=new_g))
                results.append((new_r, new_g, value_case(adjusted, capital).fair_price))
            except ValueError:
                results.append((new_r, new_g, None))
    return tuple(results)
