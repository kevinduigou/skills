"""No-network reproducible report: python -m financial_skill.cli --input FILE --output report.md.
JSON must be point-in-time verified by the analyst; this tool never fetches market data.
"""
import argparse
import json
from dataclasses import replace
from datetime import date
from pathlib import Path

from .domain import (CapitalStructure, Currency, DiscountRate,
                     MarketSnapshot, MoneyMillions, SharesMillions)
from .forecasting import AnnualDrivers, ForecastCase, TerminalEconomics
from .valuation import value_case, sensitivity
from .reverse import implied_constant_revenue_growth, revenue_margin_frontier
from .fragility import (EconomicShock, evaluate_shock, adverse_loss_curvature,
                        dispersion_fragility, liquidity_runway)
from .returns import shareholder_irr
from .historical import cagr, yoy
from .evidence import validate_evidence
from .recommendation import calculate_rating


def parse_input(path: Path):
    data = json.loads(path.read_text(encoding='utf8'))
    cur = Currency(data['currency'])
    m = lambda n: MoneyMillions(float(n), cur)
    cap = data['capital_structure']
    capital = CapitalStructure(m(cap['cash']), m(cap['debt']),
                               m(cap.get('other_nonoperating_assets', 0)),
                               m(cap.get('minority_interest', 0)),
                               m(cap.get('preferred_equity', 0)),
                               SharesMillions(cap['diluted_shares_millions']))
    p = data['price_snapshot']
    market = MarketSnapshot(data['ticker'], p['price'], cur,
                            date.fromisoformat(p['observed_on']), p['source_url'])
    cases = []
    for name, c in data['scenarios'].items():
        cases.append(ForecastCase(name, m(data['starting_revenue_millions']),
                                  tuple(AnnualDrivers(**x) for x in c['drivers']),
                                  DiscountRate(c['discount_rate']),
                                  TerminalEconomics(**c['terminal'])))
    validate_evidence(data, market.observed_on)
    if set(x.name for x in cases) != {'bear', 'base', 'bull'}:
        raise ValueError('Three named scenarios required: bear, base, bull')
    return data, capital, market, {c.name: c for c in cases}


def fmt(v: float | None, digits: int = 1) -> str:
    return 'n.m.' if v is None else f'{v:,.{digits}f}'


def pct(v: float | None, digits: int = 1) -> str:
    return 'n.m.' if v is None else f'{v*100:+.{digits}f}%'


def generate_report(data, capital, market, cases) -> str:
    valuations = {name: value_case(case, capital) for name, case in cases.items()}
    base = valuations['base']
    rating = calculate_rating(data)
    headline = 'Synthetic educational example; NOT real company financials or market quotes.' if data.get('synthetic', False) else 'Source figures are user-supplied; verify links, publication dates and corporate actions independently.'
    rows = [f'# Financial analysis — {data["ticker"]}', '',
            f'**Research recommendation:** {rating.category} — {rating.score}/100 (documented analyst scoring; not a return probability)' if rating else '**Research recommendation:** Not rated — missing documented score inputs',
            '', f'**Warning:** {headline}',
            f'**Market snapshot:** {market.price:,.2f} {market.currency.value}/share on {market.observed_on.isoformat()} · {market.source_url}',
            f'**Units:** all monetary aggregates are millions of {market.currency.value}, diluted shares are millions, prices are {market.currency.value}/share.',
            f'**Valuation type:** FCFF discounted at WACC → EV → equity bridge. No FCFE/WACC mixing.',
            '', '## Scenarios',
            '| Case | WACC | Terminal g | Terminal ROIC | EV (m) | Equity (m) | Fair/share | Upside | PV terminal / EV | Distress flag |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for name in ('bear', 'base', 'bull'):
        v = valuations[name]
        rows.append(f'| {name} | {pct(v.case.discount_rate.annual)} | {pct(v.case.terminal.growth)} | '
                    f'{pct(v.case.terminal.roic)} | {fmt(v.enterprise_value.amount)} | {fmt(v.equity_value.amount)} | '
                    f'{fmt(v.fair_price, 2)} | {pct(v.fair_price/market.price-1)} | {pct(v.terminal_share)} | {'YES' if v.distress_flag else 'no'} |')
    rows.extend(['', 'The equity bridge is floored at zero for limited liability; a negative raw residual flags possible distress and requires a separate restructuring/equity-option analysis.',
                 'Terminal share is descriptive, not a pass/fail cutoff. It can exceed 100% when negative interim FCFF offsets terminal PV.',
                 'No fixed 30% target is used. Stress discount rate, terminal g, ROIC and normalization instead.',
                 '', '## Base case FCFF forecast',
                 '| Year | Revenue (m) | EBIT (m) | NOPAT (m) | D&A (m) | Capex (m) | ΔNWC (m) | FCFF (m) |',
                 '|---:|---:|---:|---:|---:|---:|---:|---:|'])
    for y in base.years:
        rows.append(f'| {y.year} | {fmt(y.revenue.amount)} | {fmt(y.ebit.amount)} | {fmt(y.nopat.amount)} | '
                    f'{fmt(y.depreciation.amount)} | {fmt(y.capex.amount)} | {fmt(y.delta_nwc.amount)} | {fmt(y.fcff.amount)} |')
    rows.extend(['', f'- Present value of explicit FCFF: **{fmt(base.explicit_pv.amount)}m**.',
                 f'- Normalized year N+1 FCFF: **{fmt(base.terminal_fcff_next.amount)}m**.',
                 f'- Present value of terminal value: **{fmt(base.terminal_pv.amount)}m**.',
                 f'- Cash: {fmt(capital.cash.amount)}m; debt: {fmt(capital.debt.amount)}m; diluted shares: {fmt(capital.diluted_shares.count)}m.',
                 '', '## Reverse DCF',
                 f'- Market-implied enterprise value: **{fmt(capital.ev_from_equity(market.market_equity(capital.diluted_shares)).amount)}m**.',
                 ])
    implied = implied_constant_revenue_growth(cases['base'], capital, market)
    rows.append(f'- Constant annual revenue growth needed at base margins/reinvestment: **{pct(implied.implied_value)}**'
                if implied.implied_value is not None else f'- Growth solver: **no bracketed solution** ({implied.reason}).')
    rows.extend(['', '| Constant revenue CAGR | Required EBIT margin shift (all projected years + terminal) |', '|---:|---:|'])
    for growth, result in revenue_margin_frontier(cases['base'], capital, market,
                                                  tuple(data.get('reverse_growth_grid', [0.03, 0.08, 0.13, 0.18])) ,
                                                  tuple(data.get('reverse_margin_bounds', [-0.15, 0.15]))):
        rows.append(f'| {pct(growth)} | {pct(result.implied_value) if result.implied_value is not None else "No feasible root"} |')
    rows.extend(['', 'These inverse solutions are **conditional** on the fixed assumptions; they do not identify the market\'s actual beliefs.',
                 '', '## Sensitivity: base fair value per share',
                 '| WACC | Terminal g | Fair/share |', '|---:|---:|---:|'])
    for r, g, price in sensitivity(cases['base'], capital):
        rows.append(f'| {pct(r)} | {pct(g)} | {fmt(price,2)} |')
    h = float(data.get('revenue_shock_step', .1))
    v0 = base.equity_value.amount
    # An optional EXPLICIT nonlinear shock-transmission assumption; never infer from 3 observations.
    drag = float(data.get('downside_quadratic_margin_drag', 0))
    if drag < 0:
        raise ValueError('downside_quadratic_margin_drag must be nonnegative')
    def modeled_shock(change):
        margin_change = -drag * max(-change,0)**2
        return EconomicShock(revenue_change=change, ebit_margin_delta=margin_change)
    vm = evaluate_shock(cases['base'], capital, modeled_shock(-h)).shocked_equity
    vmm = evaluate_shock(cases['base'], capital, modeled_shock(-2*h)).shocked_equity
    vp = evaluate_shock(cases['base'], capital, modeled_shock(h)).shocked_equity
    curvature = adverse_loss_curvature(v0, vm, vmm)
    disp = dispersion_fragility(vm, v0, vp)
    rows.extend(['', '## Fragility: same-economics revenue-level shock',
                 f'- Assumed nonlinear transmission: EBIT margin drag = -{drag:.2f} × max(-revenue shock, 0)^2 (zero if not provided). This is a scenario assumption, NOT calibrated evidence.',
                 f'- Baseline equity value: {fmt(v0)}m; -{h:.0%} revenue shock: {fmt(vm)}m; -{2*h:.0%}: {fmt(vmm)}m; +{h:.0%}: {fmt(vp)}m.',
                 f'- Adverse-loss second difference: **{fmt(curvature.signed_difference)}m** / base equity: **{pct(curvature.normalized)}**.',
                 f'- Same-mean symmetric dispersion penalty J: **{fmt(disp.signed_difference)}m** / base equity: **{pct(disp.normalized)}**.',
                 '- Finite differences depend on shock size, baseline, horizon and model specification. Not tail probabilities.',
                 '- Business resilience, modeled equity value and investor loss are distinct; add contractual/covenant cash cliffs where applicable.'])
    if 'liquidity_stress' in data:
        q = data['liquidity_stress']
        liq = liquidity_runway(q['initial_cash'], tuple(q['operating_fcf_millions']),
                               tuple(q['debt_maturities_millions']),
                               q.get('minimum_cash',0), q.get('committed_liquidity',0))
        rows.append(f'- Liquidity stress: first minimum-cash breach year: **{liq.first_breach_year or "none"}**; peak financing gap: **{fmt(liq.peak_funding_gap)}m**.')
    if 'shareholder_return_assumptions' in data:
        ret = data['shareholder_return_assumptions']
        irr = shareholder_irr(market.price, tuple(ret['annual_dividends_per_share']), ret['assumed_exit_price'])
        rows.extend(['', '## Investor return, separate from intrinsic value',
                     f'- Assumed annual dividends {ret["annual_dividends_per_share"]}; assumed exit price {ret["assumed_exit_price"]}.',
                     f'- Conditional investor IRR: **{pct(irr)}**. NOT a forecast or a discount rate.'])
    hist = data.get('historical',{})
    if hist:
        rows.extend(['', '## Historical diagnostics', '| Metric | 3y CAGR | 5y CAGR | Latest YoY |', '|---|---:|---:|---:|'])
        for k in ('revenue_millions','fcf_millions'):
            hdata = hist.get(k,{})
            if not hdata: continue
            c3 = cagr(hdata['three_years_ago'],hdata['latest'],3)
            c5 = cagr(hdata['five_years_ago'],hdata['latest'],5)
            y = yoy(hdata['last_year'],hdata['latest'])
            rows.append(f'| {k} | {pct(c3)} | {pct(c5)} | {pct(y)} |')
        rows.append('CAGRs are n.m. for nonpositive start/end values; inspect cycle-normalized FCF.')
    if not data.get('synthetic',False):
        rows.extend(['', '## Point-in-time source ledger', '| Fact key | Published | Period end | Type | Source |', '|---|---|---|---|---|'])
        for e in validate_evidence(data, market.observed_on):
            rows.append(f'| {e.fact_key} | {e.published_on} | {e.period_end} | {e.source_kind} | [Primary document]({e.source_url}) |')
    rows.extend(['', '## Decision and falsification checklist',
                 '- **No mechanically inferred trading signal.** Any displayed rating is an analyst-justified five-factor composite, not a promise or probability. Compare implied economics, competitive position, leverage and alternatives.',
                 '- State explicit valuation date, confidence range, margin of safety, required return and thesis-breakers.',
                 '- Confirm dilution, SBC treatment, foreign listing/ADR conversion, leases, NOLs, tax and reporting currency.',
                 '- Reconcile and cite each original filing, share count and price; replace this example with primary-source observations.', ''])
    return '\n'.join(rows)


def main() -> None:
    p = argparse.ArgumentParser(description='Offline DCF / reverse DCF / fragility report from attributed user inputs')
    p.add_argument('--input', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path, help='Markdown research report')
    p.add_argument('--html-output', type=Path, help='Optional HTML path; defaults to Markdown output with .html extension')
    a = p.parse_args()
    data, cap, market, cases = parse_input(a.input)
    report = generate_report(data, cap, market, cases)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(report, encoding='utf8')
    from .html_report import render_html_report
    html_output = a.html_output or a.output.with_suffix('.html')
    html_output.parent.mkdir(parents=True, exist_ok=True)
    html_output.write_text(render_html_report(data, cap, market, cases), encoding='utf8')
    print(f'Wrote {a.output} and {html_output}')


if __name__ == '__main__':
    main()
