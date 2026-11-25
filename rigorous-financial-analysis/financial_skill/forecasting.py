"""Revenue -> EBIT -> NOPAT -> FCFF using physically inspectable assumptions."""
from dataclasses import dataclass, replace
from typing import Sequence

from .domain import Currency, DiscountRate, MoneyMillions, finite


def in_range(v: float, label: str, low: float, high: float) -> float:
    v = finite(v, label)
    if not low <= v <= high:
        raise ValueError(f'{label} must be in [{low},{high}]: {v}')
    return v


@dataclass(frozen=True)
class AnnualDrivers:
    revenue_growth: float             # percent in decimals (0.10 = +10%)
    ebit_margin: float                 # EBIT/revenue
    effective_cash_tax: float         # cash tax on positive EBIT; loss carryforwards need separate modeling
    depreciation_to_revenue: float    # D&A/revenue
    capex_to_revenue: float           # capex/revenue
    incremental_nwc_to_revenue: float # change in NWC / change in revenue

    def __post_init__(self) -> None:
        g = finite(self.revenue_growth, 'revenue growth')
        if g <= -1:
            raise ValueError('revenue growth must be > -100%')
        object.__setattr__(self, 'revenue_growth', g)
        for attr, lo, hi in (
            ('ebit_margin', -1, 1), ('effective_cash_tax', 0, 1),
            ('depreciation_to_revenue', 0, 1), ('capex_to_revenue', 0, 2),
            ('incremental_nwc_to_revenue', -2, 2),
        ):
            object.__setattr__(self, attr, in_range(getattr(self, attr), attr, lo, hi))



@dataclass(frozen=True)
class TerminalEconomics:
    """ROIC-based normalized perpetual FCFF. Explicit growth must be reinvested.
    NOPAT(1 - g/ROIC), where g >= 0. Negative g models capital release but
    should be used with special care. No extrapolation of peak final-year FCFF.
    """
    growth: float
    ebit_margin: float
    cash_tax_rate: float
    roic: float

    def __post_init__(self) -> None:
        g = finite(self.growth, 'terminal growth')
        if g <= -1:
            raise ValueError('terminal growth must be > -100%')
        object.__setattr__(self, 'growth', g)
        for attr, lo, hi in (('ebit_margin',-1,1),('cash_tax_rate',0,1)):
            object.__setattr__(self, attr, in_range(getattr(self,attr), attr, lo, hi))
        roic = finite(self.roic, 'terminal ROIC')
        if roic <= 0 or roic <= g:
            raise ValueError('terminal ROIC must be > max(growth,0)')
        object.__setattr__(self, 'roic', roic)



@dataclass(frozen=True)
class ForecastCase:
    name: str
    starting_revenue: MoneyMillions
    drivers: tuple[AnnualDrivers, ...]
    discount_rate: DiscountRate
    terminal: TerminalEconomics

    def __post_init__(self) -> None:
        if not self.name or not self.drivers or len(self.drivers) > 20:
            raise ValueError('case requires a name and between 1 and 20 forecast years')
        if self.starting_revenue.amount <= 0:
            raise ValueError('starting revenue must be positive')
        if self.discount_rate.annual <= self.terminal.growth:
            raise ValueError('WACC must exceed terminal growth')


@dataclass(frozen=True)
class ForecastYear:
    year: int
    revenue: MoneyMillions
    ebit: MoneyMillions
    nopat: MoneyMillions
    depreciation: MoneyMillions
    capex: MoneyMillions
    delta_nwc: MoneyMillions
    fcff: MoneyMillions


def make_forecast(case: ForecastCase) -> tuple[ForecastYear, ...]:
    previous = case.starting_revenue.amount
    currency = case.starting_revenue.currency
    result: list[ForecastYear] = []
    for year, a in enumerate(case.drivers, 1):
        revenue = previous * (1 + a.revenue_growth)
        ebit = revenue * a.ebit_margin
        # Simplification: cash tax only on operating profit >0, no NOL modeling
        nopat = ebit - max(0.0, ebit) * a.effective_cash_tax
        depreciation = revenue * a.depreciation_to_revenue
        capex = revenue * a.capex_to_revenue
        delta_nwc = (revenue - previous) * a.incremental_nwc_to_revenue
        fcff = nopat + depreciation - capex - delta_nwc
        m = lambda x: MoneyMillions(x, currency)
        result.append(ForecastYear(year, m(revenue), m(ebit), m(nopat),
                                   m(depreciation), m(capex), m(delta_nwc), m(fcff)))
        previous = revenue
    return tuple(result)


def terminal_fcff(case: ForecastCase, last_year: ForecastYear) -> MoneyMillions:
    t = case.terminal
    revenue_next = last_year.revenue.amount * (1 + t.growth)
    ebit_next = revenue_next * t.ebit_margin
    nopat_next = ebit_next - max(0.0, ebit_next) * t.cash_tax_rate
    fcff_next = nopat_next * (1 - t.growth / t.roic)
    if fcff_next <= 0:
        raise ValueError('Nonpositive normalized terminal FCFF: Gordon model invalid; model a finite-life/exit alternative')
    return MoneyMillions(fcff_next, last_year.revenue.currency)


def replace_growth(case: ForecastCase, annual_growth: float) -> ForecastCase:
    if not -0.999 < annual_growth < 10:
        raise ValueError('candidate growth outside explicit solver domain')
    return replace(case, drivers=tuple(replace(d, revenue_growth=annual_growth) for d in case.drivers))


def shift_margins(case: ForecastCase, shift: float) -> ForecastCase:
    """Shift each explicit EBIT margin and normalized terminal margin equally."""
    return replace(case, drivers=tuple(replace(d, ebit_margin=d.ebit_margin + shift)
                                       for d in case.drivers),
                   terminal=replace(case.terminal, ebit_margin=case.terminal.ebit_margin + shift))
