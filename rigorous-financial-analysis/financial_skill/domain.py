"""Validated financial domain types. Monetary values are in *millions* of currency.
Shares are in millions, so MoneyMillions / SharesMillions = currency/share.
No implicit FX, ADR, or unit conversions are performed.
"""
from dataclasses import dataclass
from datetime import date
from enum import Enum
from math import isfinite


class Currency(str, Enum):
    USD = 'USD'
    EUR = 'EUR'
    KRW = 'KRW'
    JPY = 'JPY'
    GBP = 'GBP'
    CNY = 'CNY'
    CHF = 'CHF'


def finite(value: float, label: str) -> float:
    value = float(value)
    if not isfinite(value):
        raise ValueError(f'{label} must be finite')
    return value


@dataclass(frozen=True)
class MoneyMillions:
    amount: float
    currency: Currency

    def __post_init__(self) -> None:
        object.__setattr__(self, 'amount', finite(self.amount, 'money'))
        if not isinstance(self.currency, Currency):
            raise TypeError('currency must be Currency enum; explicit FX conversion required')

    def __add__(self, other: 'MoneyMillions') -> 'MoneyMillions':
        self._check(other)
        return MoneyMillions(self.amount + other.amount, self.currency)

    def __sub__(self, other: 'MoneyMillions') -> 'MoneyMillions':
        self._check(other)
        return MoneyMillions(self.amount - other.amount, self.currency)

    def _check(self, other: 'MoneyMillions') -> None:
        if not isinstance(other, MoneyMillions) or self.currency != other.currency:
            raise ValueError('Currency mismatch or invalid money type; no implicit FX conversion')


@dataclass(frozen=True)
class SharesMillions:
    count: float

    def __post_init__(self) -> None:
        n = finite(self.count, 'diluted shares')
        if n <= 0:
            raise ValueError('diluted shares must be positive')
        object.__setattr__(self, 'count', n)


@dataclass(frozen=True)
class DiscountRate:
    annual: float

    def __post_init__(self) -> None:
        r = finite(self.annual, 'discount rate')
        if r <= 0:
            raise ValueError('discount rate must be > 0')
        object.__setattr__(self, 'annual', r)


@dataclass(frozen=True)
class CapitalStructure:
    """Balances as of valuation date; DO NOT double count leases or restricted cash."""
    cash: MoneyMillions
    debt: MoneyMillions
    other_nonoperating_assets: MoneyMillions
    minority_interest: MoneyMillions
    preferred_equity: MoneyMillions
    diluted_shares: SharesMillions

    def __post_init__(self) -> None:
        cur = self.cash.currency
        balances = [self.cash, self.debt, self.other_nonoperating_assets,
                    self.minority_interest, self.preferred_equity]
        if any(x.currency != cur for x in balances):
            raise ValueError('Capital structure currency mismatch')
        if any(x.amount < 0 for x in balances):
            raise ValueError('Capital structure balance must be nonnegative')

    @property
    def currency(self) -> Currency:
        return self.cash.currency

    def equity_from_ev(self, ev: MoneyMillions) -> MoneyMillions:
        if ev.currency != self.currency:
            raise ValueError('EV currency mismatch')
        return (ev + self.cash + self.other_nonoperating_assets - self.debt
                - self.minority_interest - self.preferred_equity)

    def ev_from_equity(self, equity: MoneyMillions) -> MoneyMillions:
        if equity.currency != self.currency:
            raise ValueError('Equity currency mismatch')
        return (equity - self.cash - self.other_nonoperating_assets + self.debt
                + self.minority_interest + self.preferred_equity)


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    price: float                 # Currency per ordinary (or equivalent) share
    currency: Currency
    observed_on: date
    source_url: str

    def __post_init__(self) -> None:
        p = finite(self.price, 'share price')
        if not isinstance(self.currency, Currency) or not isinstance(self.observed_on, date):
            raise TypeError('Market currency must be Currency and observed_on must be date')
        if p <= 0:
            raise ValueError('share price must be positive')
        object.__setattr__(self, 'price', p)
        if not self.symbol or not self.source_url:
            raise ValueError('price ticker and source provenance are required')

    def market_equity(self, shares: SharesMillions) -> MoneyMillions:
        return MoneyMillions(self.price * shares.count, self.currency)
