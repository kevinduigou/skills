"""Offline, standard-library-only reference financial valuation engine."""
from .domain import Currency, MoneyMillions, SharesMillions, DiscountRate, CapitalStructure, MarketSnapshot
from .forecasting import AnnualDrivers, TerminalEconomics, ForecastCase, make_forecast
from .valuation import value_case, sensitivity
from .reverse import implied_constant_revenue_growth, revenue_margin_frontier
from .fragility import EconomicShock, evaluate_shock, adverse_loss_curvature, dispersion_fragility, liquidity_runway
from .returns import shareholder_irr
from .calibration import ForecastRecord, calibrate
