"""Offline, single-file, print-friendly HTML financial study renderer.

Templates are bundled source assets. All external data is HTML-escaped, with no
network dependencies, external scripts, or user-supplied HTML interpreted.
"""
from __future__ import annotations

from datetime import date
from html import escape
from math import cos, sin, radians, isfinite
from pathlib import Path
from string import Template
from urllib.parse import urlparse

from .recommendation import InvestmentRating, calculate_rating
from .valuation import value_case, sensitivity
from .reverse import implied_constant_revenue_growth, revenue_margin_frontier
from .fragility import (EconomicShock, evaluate_shock, adverse_loss_curvature,
                        dispersion_fragility, liquidity_runway)
from .historical import cagr, yoy
from .returns import shareholder_irr
from .evidence import validate_evidence

TEMPLATES = Path(__file__).resolve().parents[1] / 'templates'
COLORS = ('#c05a62', '#d68a68', '#d9b966', '#70af91', '#2b9d91')


def h(v: object) -> str:
    return escape(str(v), quote=True)


def num(v: float | None, decimals: int = 1) -> str:
    return 'n.m.' if v is None or not isfinite(v) else f'{v:,.{decimals}f}'


def percent(v: float | None, decimals: int = 1) -> str:
    return 'n.m.' if v is None or not isfinite(v) else f'{100*v:+.{decimals}f}%'


def rate(v: float | None) -> str:
    return 'n.m.' if v is None else f'{100*v:.1f}%'


def tr(cells, head=False, classes=None):
    tag = 'th' if head else 'td'
    return '<tr>' + ''.join(f'<{tag}{(" class=" + chr(34) + h(classes[i]) + chr(34)) if classes and i < len(classes) and classes[i] else ""}>{c}</{tag}>' for i,c in enumerate(cells)) + '</tr>'


def table(headers, rows, classes=None):
    return '<div class="table-scroll"><table>' + '<thead>' + tr([h(c) for c in headers], True, classes) + '</thead><tbody>' + ''.join(tr(row, classes=classes) for row in rows) + '</tbody></table></div>'


def gauge(rating: InvestmentRating | None) -> str:
    cx, cy, radius = 240, 197, 159
    def xy(degrees, rr=radius):
        return (cx + rr*cos(radians(degrees)), cy - rr*sin(radians(degrees)))
    arcs = []
    for j in range(5):
        x1,y1=xy(180-36*j)
        x2,y2=xy(180-36*(j+1))
        arcs.append(f'<path d="M {x1:.2f} {y1:.2f} A {radius} {radius} 0 0 1 {x2:.2f} {y2:.2f}" fill="none" stroke="{COLORS[j]}" stroke-width="26"/>')
    if rating:
        angle=180-180*((rating.score-1)/99)
        ex,ey=xy(angle,120)
        needle=f'<line x1="{cx}" y1="{cy}" x2="{ex:.2f}" y2="{ey:.2f}" stroke="#193248" stroke-width="6" stroke-linecap="round"/><circle cx="{cx}" cy="{cy}" r="12" fill="#193248"/><circle cx="{cx}" cy="{cy}" r="4" fill="#ffffff"/>'
        score_line=f'<div class="rating-number">{rating.score}<span> / 100</span></div>'
        label=h(rating.category)
        aria=f'Investment recommendation {rating.category}, score {rating.score} out of 100'
    else:
        needle=f'<circle cx="{cx}" cy="{cy}" r="10" fill="#a4b1bc"/>'
        score_line='<div class="rating-number">—<span> / 100</span></div>'
        label='Not rated'
        aria='Investment recommendation not rated because required inputs are unavailable'
    # SVG markup is static; numeric coordinates come from validated arithmetic.
    return ('<div class="gauge-title">INVESTMENT CONVICTION SCORE</div>'
            f'<svg class="gauge-svg" viewBox="0 0 480 243" role="img" aria-label="{h(aria)}">'
            + ''.join(arcs) + needle + '</svg>' +
            f'<div class="rating-label">{label}</div>{score_line}'
            '<div class="rating-ends"><span>1 · STRONG SELL</span><span>100 · STRONG BUY</span></div>')


def chart_svg(values: list[float], units: str, accent: str) -> str:
    if not values:
        return '<p class="hint">Not available.</p>'
    width, height = 550, 223
    left,right,top,bottom = 69,24,22,42
    lo,hi=min(values),max(values)
    if hi==lo:
        hi=lo+1
    margin=(hi-lo)*.12
    lo-=margin; hi+=margin
    pw=width-left-right; ph=height-top-bottom
    coords=[(left+(pw*i/max(1,len(values)-1)), top + ph*(hi-y)/(hi-lo)) for i,y in enumerate(values)]
    baseline = top + ph*(hi-0)/(hi-lo)
    grids=[]
    for i in range(4):
        y=top+ph*i/3
        val=hi-(hi-lo)*i/3
        grids.append(f'<line x1="{left}" x2="{width-right}" y1="{y:.1f}" y2="{y:.1f}" stroke="#e8eef1"/><text x="{left-11}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="#93a2ad">{h(num(val,0))}</text>')
    pts=' '.join(f'{x:.1f},{y:.1f}' for x,y in coords)
    circles=''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{accent}" stroke="white" stroke-width="1.5"/>' for x,y in coords)
    labels=''.join(f'<text x="{x:.1f}" y="{height-18}" text-anchor="middle" font-size="10" fill="#8696a3">{i+1}</text>' for i,(x,_) in enumerate(coords) if i==0 or i==len(coords)-1 or (len(coords)<7 and i%2==0))
    zero = (f'<line x1="{left}" x2="{width-right}" y1="{baseline:.1f}" y2="{baseline:.1f}" stroke="#a8b6c0" stroke-dasharray="5 5"/>' if top <= baseline <= top+ph else '')
    return (f'<svg class="chart-svg" viewBox="0 0 {width} {height}" role="img" aria-label="{h(units)} over {len(values)} projected years">'
            + ''.join(grids) + zero + f'<polyline points="{pts}" fill="none" stroke="{accent}" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/>' + circles + labels + '</svg>' +
            f'<p class="hint">{h(units)} · years 1–{len(values)} · deterministic base-case forecast</p>')


def score_details(rating: InvestmentRating | None) -> str:
    if rating is None:
        return '<div class="provenance-empty">No numerical rating: five documented scoring dimensions are missing. Do not fabricate a 1–100 investment score.</div>'
    rows = []
    for d in rating.dimensions:
        rows.append(f'<div class="score-row"><div class="score-name">{h(d.label)}<small>Weight {d.weight}%</small></div>'
                    f'<div class="bar"><i style="width:{d.score:.1f}%"></i></div><div class="score-value">{num(d.score,0)}</div>'
                    f'<div class="rationale">{h(d.rationale)}</div></div>')
    return ''.join(rows) + (f'<p class="hint">Weighted score = Σ (dimension × weight / 100) = <b>{rating.score}/100</b>. '
                            'Bands: 1–20 Strong Sell · 21–40 Sell · 41–60 Hold · 61–80 Buy · 81–100 Strong Buy. '
                            'Analyst-supplied judgment, not a probability, statistical estimate, or automatic trade trigger.</p>')


def source_link(url: str) -> str:
    parsed=urlparse(url)
    if parsed.scheme in ('https','http') and parsed.netloc:
        return f'<a href="{h(url)}" rel="noopener noreferrer" target="_blank">Source ↗</a>'
    return '<span class="hint">Unlinked fixture</span>'


def render_html_report(data, capital, market, cases) -> str:
    """Return a fully embedded standalone HTML document from validated CLI inputs."""
    rating=calculate_rating(data)
    vals={key:value_case(cases[key],capital) for key in ('bear','base','bull')}
    base=vals['base']
    currency=market.currency.value
    upside=base.fair_price/market.price-1
    synthetic=bool(data.get('synthetic',False))
    warning=('SYNTHETIC EXAMPLE — every figure, price and recommendation is fictional. Do not use for investment decisions.'
             if synthetic else 'Source records contain analyst supplied values; links are structurally validated but are not independently authenticated by this offline tool.')
    revenue=chart_svg([y.revenue.amount for y in base.years],f'Revenue, millions of {currency}','#0d9992')
    fcf=chart_svg([y.fcff.amount for y in base.years],f'FCFF, millions of {currency}','#d79851')
    kpis=[]
    for title,value,foot,css in (
        ('Market quotation',f'{num(market.price,2)} {currency}',f'Observed {market.observed_on.isoformat()}',''),
        ('Base fair value',f'{num(base.fair_price,2)} {currency}','FCFF DCF per diluted share',''),
        ('Base upside / downside',percent(upside),'Versus dated quotation','upside' if upside>=0 else 'downside'),
        ('Terminal share',percent(base.terminal_share),'PV of terminal / enterprise value','')):
        kpis.append(f'<div class="kpi"><div class="k-label">{h(title)}</div><div class="k-value {css}">{h(value)}</div><div class="k-foot">{h(foot)}</div></div>')
    if rating:
        thesis=rating.thesis
        rating_caution='Rating uses a weighted 5-dimension analyst rubric; it is not the probability of an investment succeeding.'
    else:
        thesis='Insufficient documented judgment inputs to assign a 1–100 rating. Review the underlying valuation and complete the five scoring dimensions before issuing a recommendation.'
        rating_caution='The needle is withheld intentionally when a defensible score cannot be calculated.'
    historical=data.get('historical',{})
    hist_rows=[]
    for key,label in (('revenue_millions','Revenue'),('fcf_millions','Free cash flow')):
        item=historical.get(key)
        if item:
            hist_rows.append([h(label),h(percent(cagr(item['three_years_ago'],item['latest'],3))),
                              h(percent(cagr(item['five_years_ago'],item['latest'],5))),
                              h(percent(yoy(item['last_year'],item['latest'])))])
    hist_table=table(['Metric','3y CAGR','5y CAGR','Latest YoY'],hist_rows,['','num','num','num']) if hist_rows else '<div class="provenance-empty">No dated historical series supplied.</div>'
    cap_rows=[]
    for label,value in [('Cash',capital.cash.amount),('Debt',capital.debt.amount),('Other non-operating assets',capital.other_nonoperating_assets.amount),('Minority interests',capital.minority_interest.amount),('Preferred equity',capital.preferred_equity.amount),('Diluted shares (millions)',capital.diluted_shares.count)]:
        cap_rows.append([h(label),h(num(value,1))])
    capital_table=table([f'Millions of {currency} (unless shares)','Value'],cap_rows,['','num'])
    cards=[]
    price_max=max(v.fair_price for v in vals.values())
    for case_name in ('bear','base','bull'):
        v=vals[case_name]
        change=v.fair_price/market.price-1
        attr=' downside' if change<0 else ' upside'
        cards.append(f'<article class="scenario {case_name}"><div class="s-top"><h3>{h(case_name.title())} case</h3><span>{"FOCUS" if case_name=="base" else "SCENARIO"}</span></div>'
                     f'<div class="s-fair">{num(v.fair_price,2)} <small style="font-size:12px">{h(currency)}</small></div>'
                     f'<div class="s-upside{attr}">{h(percent(change))} vs market</div><div class="s-meter"><i style="width:{max(0,min(100,100*v.fair_price/max(.01,price_max))):.1f}%"></i></div>'
                     f'<div class="s-detail"><span>WACC</span><b>{rate(v.case.discount_rate.annual)}</b></div>'
                     f'<div class="s-detail"><span>Terminal growth</span><b>{rate(v.case.terminal.growth)}</b></div>'
                     f'<div class="s-detail"><span>Terminal ROIC</span><b>{rate(v.case.terminal.roic)}</b></div>'
                     f'<div class="s-detail"><span>PV(TV) / EV</span><b>{percent(v.terminal_share)}</b></div>'
                     f'<div class="s-detail"><span>Enterprise value (m)</span><b>{num(v.enterprise_value.amount,0)}</b></div>'
                     f'<div class="s-detail"><span>Distress residual</span><b>{"YES — model needed" if v.distress_flag else "No"}</b></div></article>')
    cards_html='<div class="scenario-grid">'+''.join(cards)+'</div><p class="s-foot">Values are conditional on explicitly modeled economic assumptions. Shares are assumed constant in the reference implementation; dilution requires a separate model. A negative raw equity bridge is floored for display and is not a restructuring valuation.</p>'
    terminal_analysis=('<div class="terminal-grid">'
                       f'<div class="terminal-item"><small>Explicit FCFF, PV (m)</small><strong>{num(base.explicit_pv.amount,0)}</strong></div>'
                       f'<div class="terminal-item"><small>Terminal value, PV (m)</small><strong>{num(base.terminal_pv.amount,0)}</strong></div>'
                       f'<div class="terminal-item"><small>Normalized year N+1 FCFF (m)</small><strong>{num(base.terminal_fcff_next.amount,0)}</strong></div>'
                       '</div><p class="hint">Terminal cash flow = normalized NOPAT × (1 − perpetual g / terminal ROIC). Terminal share is diagnostic; no arbitrary 30% threshold or target is applied.</p>')
    implied=implied_constant_revenue_growth(cases['base'],capital,market)
    implied_html=('<div class="panel-title">Required constant revenue CAGR</div>'
                  f'<div class="big-metric">{percent(implied.implied_value)}</div>'
                  '<p>At base-case profit margins, cash reinvestment and terminal assumptions, this is the constant explicit revenue growth that would reconcile the modeled valuation to the observed quote.</p>'
                  '<p>Conditional root only; not the market’s unique belief. '+h(implied.reason or '')+'</p>')
    frontier=revenue_margin_frontier(cases['base'],capital,market,
                                    tuple(data.get('reverse_growth_grid',[.03,.08,.13,.18])),
                                    tuple(data.get('reverse_margin_bounds',[-.15,.15])))
    reverse_table=table(['Fixed revenue CAGR','Implied margin shift'],
                        [[h(percent(g)),h(percent(root.implied_value) if root.implied_value is not None else 'No feasible root')]
                         for g,root in frontier],['num','num'])
    sens=sensitivity(cases['base'],capital)
    g_list=sorted(set(r[1] for r in sens)); r_list=sorted(set(r[0] for r in sens))
    sens_map={(r,g):p for r,g,p in sens}
    vals_avail=[p for _,_,p in sens if p is not None]
    smin,smax=(min(vals_avail),max(vals_avail)) if vals_avail else (0,1)
    sen_rows=[]
    for r in r_list:
        cells=[h(rate(r))]
        for g in g_list:
            pv=sens_map[(r,g)]
            if pv is None:
                cells.append('<span title="Invalid parameter combination">n.m.</span>')
            else:
                q=(pv-smin)/(smax-smin) if smax>smin else 0.5
                # No probabilities: just a continuous visual scale from relative-low to relative-high valuation.
                back=f'rgba(38,151,133,{0.07+q*.29:.3f})' if pv>=base.fair_price else f'rgba(204,102,95,{.05+(1-q)*.20:.3f})'
                cells.append(f'<span style="display:block;padding:9px 3px;background:{back};border-radius:6px">{num(pv,2)}</span>')
        sen_rows.append(cells)
    sen_table='<div class="table-scroll"><table class="heatmap"><thead>'+tr(['WACC / g']+[h(rate(g)) for g in g_list],True)+'</thead><tbody>'+''.join(tr(c) for c in sen_rows)+'</tbody></table></div>'
    step=float(data.get('revenue_shock_step',.1))
    drag=float(data.get('downside_quadratic_margin_drag',0))
    if not 0<step<.5 or drag<0 or not isfinite(step) or not isfinite(drag):
        raise ValueError('Shock step must be 0–50% exclusive and nonlinear drag finite nonnegative')
    def shock(change):
        return EconomicShock(revenue_change=change, ebit_margin_delta=-drag*max(-change,0)**2)
    vm=evaluate_shock(cases['base'],capital,shock(-step)).shocked_equity
    vmm=evaluate_shock(cases['base'],capital,shock(-2*step)).shocked_equity
    vp=evaluate_shock(cases['base'],capital,shock(step)).shocked_equity
    v0=base.equity_value.amount
    curv=adverse_loss_curvature(v0,vm,vmm)
    disp=dispersion_fragility(vm,v0,vp)
    stress=[('Baseline equity value',v0), (f'−{step*100:.0f}% revenue',vm),
            (f'−{2*step*100:.0f}% revenue',vmm), (f'+{step*100:.0f}% revenue',vp)]
    fr='<div class="stress-grid">'+''.join(f'<div class="stress"><small>{h(title)}</small><strong>{num(v,0)}</strong></div>' for title,v in stress)+'</div>'
    fr+=f'<div class="risk-note">Adverse loss curvature: <b>{percent(curv.normalized)}</b> of base equity · symmetric dispersion penalty J: <b>{percent(disp.normalized)}</b> · assumed nonlinear margin drag coefficient: {num(drag,2)}. These are model-dependent finite differences, not calibrated loss probabilities.</div>'
    if 'liquidity_stress' in data:
        li=data['liquidity_stress']
        run=liquidity_runway(li['initial_cash'],tuple(li['operating_fcf_millions']),
                            tuple(li['debt_maturities_millions']),
                            li.get('minimum_cash',0),li.get('committed_liquidity',0))
        fr+=f'<p class="hint">Liquidity stress: first minimum-cash breach in year <b>{run.first_breach_year if run.first_breach_year is not None else "none"}</b>; peak modeled funding gap <b>{num(run.peak_funding_gap,1)}m {h(currency)}</b>. This simplified bridge does not model covenants or financing remedies.</p>'
    if 'shareholder_return_assumptions' in data:
        ret=data['shareholder_return_assumptions']
        irr=shareholder_irr(market.price, tuple(ret['annual_dividends_per_share']),ret['assumed_exit_price'])
        fr+=f'<p class="hint">Separate conditional shareholder IRR: <b>{percent(irr)}</b> assuming an exit share price of {num(ret["assumed_exit_price"],2)} {h(currency)} and the specified distributions. IRR is not WACC and not a promised return.</p>'
    forecast=table(['Year','Revenue','EBIT','NOPAT','D&A','Capex','ΔNWC','FCFF'],
                   [[h(y.year)]+[h(num(getattr(y,k).amount,1)) for k in ('revenue','ebit','nopat','depreciation','capex','delta_nwc','fcff')]
                    for y in base.years],['num']*8)
    if synthetic:
        source='<div class="provenance-empty">The entire example is synthetic. There are no external filings or verified market observations. The scoring is for interface demonstration only.</div>'
    else:
        ledger=validate_evidence(data,market.observed_on)
        source=table(['Evidence fact','Published','Period','Type','Link'],
                     [[h(x.fact_key),h(x.published_on),h(x.period_end),h(x.source_kind),source_link(x.source_url)]
                      for x in ledger])
        source+='<p class="hint">Links are included for audit, but the generator does not authenticate them or fetch financial data.</p>'
    items=lambda lines: ('<ul class="bullet-list">'+''.join(f'<li>{h(text)}</li>' for text in lines)+'</ul>') if lines else '<p class="hint">No entries supplied; report remains conditional.</p>'
    tests=(f'<b class="section-index">POTENTIAL CATALYSTS</b>{items(rating.catalysts if rating else [])}'
           f'<p class="section-index" style="margin-top:18px">THESIS INVALIDATION</p>{items(rating.invalidators if rating else [])}')
    variables={
      'page_title':h(f'Investment study | {data.get("company_name", data["ticker"])}'),
      'stylesheet':(TEMPLATES/'report.css').read_text(encoding='utf-8'),
      'report_date':h(f'PRICE DATE · {market.observed_on.isoformat()}'),
      'asof_label':h(market.observed_on.isoformat()),
      'company_name':h(data.get('company_name',data['ticker'])),
      'ticker':h(data['ticker']), 'currency':h(currency),
      'report_type':'SYNTHETIC STUDY' if synthetic else 'CONDITIONAL VALUATION',
      'data_status':'SYNTHETIC DATA' if synthetic else 'ATTRIBUTED INPUTS',
      'gauge_html':gauge(rating), 'thesis':h(thesis),
      'basis':h(f'Base-case estimated fair value {num(base.fair_price,2)} {currency}; reference quote {num(market.price,2)} {currency}; upside {percent(upside)}. Scenario assumptions must be checked against capacity, competition and financing.'),
      'rating_caution':h(rating_caution),
      'warning':h(warning), 'kpis':''.join(kpis),
      'history_table':hist_table, 'capital_table':capital_table,
      'scenario_cards':cards_html, 'revenue_chart':revenue,'fcf_chart':fcf,
      'terminal_analysis':terminal_analysis,
      'implied_growth':implied_html,'reverse_table':reverse_table,
      'sensitivity_table':sen_table,'fragility_html':fr,
      'forecast_table':forecast, 'source_html':source,
      'decision_tests':tests, 'score_breakdown':score_details(rating),
      'footer_notice':'SYNTHETIC / NOT INVESTABLE' if synthetic else 'RESEARCH SUMMARY / POINT-IN-TIME'
    }
    return Template((TEMPLATES/'report.html').read_text(encoding='utf-8')).substitute(variables)
