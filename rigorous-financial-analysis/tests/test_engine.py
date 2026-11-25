import math
import unittest
from dataclasses import replace
from datetime import date

from financial_skill.domain import (CapitalStructure, Currency, DiscountRate,
                                    MarketSnapshot, MoneyMillions, SharesMillions)
from financial_skill.forecasting import (AnnualDrivers, TerminalEconomics,
                                        ForecastCase, make_forecast, terminal_fcff)
from financial_skill.valuation import value_case, sensitivity
from financial_skill.reverse import (implied_constant_revenue_growth,
                                     implied_margin_shift, target_enterprise_value,
                                     bisect_target)
from financial_skill.fragility import (EconomicShock, evaluate_shock, adverse_loss_curvature,
                                      dispersion_fragility, liquidity_runway)
from financial_skill.historical import cagr, yoy
from financial_skill.returns import shareholder_irr
from financial_skill.calibration import ForecastRecord, calibrate


def fixture():
    c = Currency.USD
    m = lambda x: MoneyMillions(x, c)
    cap = CapitalStructure(m(200), m(300), m(0), m(0), m(0), SharesMillions(100))
    drivers = tuple(AnnualDrivers(.07, .2, .25, .05, .08, .05) for _ in range(10))
    case = ForecastCase('base', m(1000), drivers, DiscountRate(.12),
                        TerminalEconomics(.025, .2, .25, .15))
    val = value_case(case, cap)
    market = MarketSnapshot('SYNTH', val.fair_price, c, date(2025,12,31), 'synthetic://fixture')
    return cap, case, val, market


class DomainTests(unittest.TestCase):
    def test_money_currency_mismatch(self):
        with self.assertRaises(ValueError):
            _ = MoneyMillions(1, Currency.USD) + MoneyMillions(2, Currency.EUR)

    def test_share_units_and_bridge(self):
        cap, case, v, _ = fixture()
        self.assertAlmostEqual(v.enterprise_value.amount - 100, v.equity_value.amount)
        self.assertAlmostEqual(v.fair_price * 100, v.equity_value.amount)
        self.assertEqual(cap.ev_from_equity(v.equity_value), v.enterprise_value)

    def test_negative_shares(self):
        with self.assertRaises(ValueError): SharesMillions(0)

    def test_rate_invariant(self):
        with self.assertRaises(ValueError): DiscountRate(0)
        with self.assertRaises(ValueError): DiscountRate(float('nan'))

    def test_terminal_invariant(self):
        with self.assertRaises(ValueError): TerminalEconomics(.20,.2,.25,.15)
        with self.assertRaises(ValueError): ForecastCase('invalid', MoneyMillions(100, Currency.USD),
            (AnnualDrivers(.1,.2,.25,.05,.1,.1),), DiscountRate(.02), TerminalEconomics(.03,.2,.25,.15))

    def test_market_currency(self):
        cap, case, v, market = fixture()
        euro_market = replace(market, currency=Currency.EUR)
        with self.assertRaises(ValueError): target_enterprise_value(euro_market, cap)


class ValuationTests(unittest.TestCase):
    def test_fcff_annual(self):
        cap, case, _, _ = fixture()
        year = make_forecast(case)[0]
        self.assertAlmostEqual(year.revenue.amount, 1070)
        self.assertAlmostEqual(year.ebit.amount, 214)
        self.assertAlmostEqual(year.nopat.amount, 160.5)
        self.assertAlmostEqual(year.capex.amount, 85.6)
        self.assertAlmostEqual(year.delta_nwc.amount, 3.5)
        self.assertAlmostEqual(year.fcff.amount, 124.9)

    def test_gordon_normalized_roic(self):
        cap, case, v, _ = fixture()
        last = v.years[-1]
        f = last.revenue.amount * 1.025 * .20 * .75 * (1-.025/.15)
        self.assertAlmostEqual(v.terminal_fcff_next.amount, f)

    def test_pv_reconciliation(self):
        cap, case, v, _ = fixture()
        expected_explicit = sum(y.fcff.amount/(1+.12)**y.year for y in v.years)
        self.assertAlmostEqual(v.explicit_pv.amount, expected_explicit)
        self.assertAlmostEqual(v.explicit_pv.amount + v.terminal_pv.amount, v.enterprise_value.amount)
        self.assertAlmostEqual(v.terminal_share, v.terminal_pv.amount/v.enterprise_value.amount)

    def test_distressed_equity_is_floored_not_negative_stock_price(self):
        cap, case, _, _ = fixture()
        m = lambda x: MoneyMillions(x, Currency.USD)
        distressed = replace(cap, debt=m(1_000_000))
        valuation = value_case(case, distressed)
        self.assertLess(valuation.equity_residual.amount, 0)
        self.assertEqual(valuation.equity_value.amount, 0)
        self.assertEqual(valuation.fair_price, 0)
        self.assertTrue(valuation.distress_flag)

    def test_discount_sensitivity(self):
        cap, case, _, _ = fixture()
        grid = sensitivity(case, cap)
        self.assertEqual(len(grid),9)
        self.assertGreater(grid[1][2], grid[7][2])

    def test_zero_or_negative_terminal_fcff(self):
        cap, case, _, _ = fixture()
        with self.assertRaises(ValueError):
            value_case(replace(case, terminal=TerminalEconomics(.025,-.1,.25,.15)),cap)


class ReverseTests(unittest.TestCase):
    def test_market_ev_reconcile(self):
        cap, case, v, market = fixture()
        self.assertAlmostEqual(target_enterprise_value(market, cap),v.enterprise_value.amount)

    def test_implied_growth_recovers_known_case(self):
        cap, case, v, market = fixture()
        result = implied_constant_revenue_growth(case,cap,market)
        self.assertIsNone(result.reason)
        self.assertAlmostEqual(result.implied_value,.07,places=8)

    def test_implied_margin_shift_recovers_zero(self):
        cap, case, v, market = fixture()
        result = implied_margin_shift(case,cap,market,.07,lower=-.1,upper=.1)
        self.assertAlmostEqual(result.implied_value,0,places=7)

    def test_margin_solver_restricts_invalid_terminal_bounds(self):
        cap, case, _, market = fixture()
        result = implied_margin_shift(case,cap,market,.07,lower=-.5,upper=.1)
        self.assertAlmostEqual(result.implied_value, 0, places=7)
        self.assertGreater(result.lower, -.2)

    def test_root_outside_bracket(self):
        result = bisect_target(lambda x:x**2,100,0,3)
        self.assertIsNone(result)


class FragilityTests(unittest.TestCase):
    def test_zero_shock_identity(self):
        cap, case, v, _ = fixture()
        a = evaluate_shock(case,cap,EconomicShock())
        self.assertAlmostEqual(a.base_equity,a.shocked_equity)
        self.assertAlmostEqual(a.signed_loss,0)

    def test_adverse_curvature(self):
        c = adverse_loss_curvature(100, 90, 70)
        self.assertAlmostEqual(c.signed_difference,10)
        self.assertAlmostEqual(c.normalized,.1)

    def test_dispersion(self):
        c = dispersion_fragility(90,100,105)
        self.assertAlmostEqual(c.signed_difference,2.5)

    def test_liquidity_breach(self):
        r = liquidity_runway(300,(-100,-150,200), (0,200,0), minimum_cash=100)
        self.assertEqual(r.first_breach_year,2)
        self.assertEqual(r.peak_funding_gap,250)

    def test_reject_missing_maturity(self):
        with self.assertRaises(ValueError): liquidity_runway(100,(100,),())


class DiagnosticsTests(unittest.TestCase):
    def test_cagr_and_yoy(self):
        self.assertAlmostEqual(cagr(100,121,2),.1)
        self.assertIsNone(cagr(-2,100,3))
        self.assertIsNone(yoy(-2,100))

    def test_irr(self):
        self.assertAlmostEqual(shareholder_irr(100, (0,0,0,0,0), 100), 0, places=8)
        self.assertAlmostEqual(shareholder_irr(100, (0,0), 121), .1, places=7)

    def test_calibration_and_no_lookahead(self):
        record = ForecastRecord(date(2020,1,1),date(2021,12,31),date(2022,2,1),90,100,110,105)
        metrics = calibrate((record,))
        self.assertEqual(metrics.samples,1)
        self.assertEqual(metrics.mae,5)
        self.assertEqual(metrics.signed_bias,-5)
        self.assertEqual(metrics.scenario_coverage,1)
        with self.assertRaises(ValueError):
            ForecastRecord(date(2022,3,1),date(2021,12,31),date(2022,2,1),90,100,110,105)


if __name__ == '__main__':
    unittest.main()
