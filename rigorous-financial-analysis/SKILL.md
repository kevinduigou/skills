---
name: rigorous-financial-analysis
description: Evidence-grounded company and equity research with driver-based three-scenario FCFF DCF, reverse DCF solving implied economic drivers, terminal-value attribution and sensitivities, Taleb-style nonlinear fragility and liquidity stress, investor IRR, and point-in-time validation. Use whenever a user requests stock investment analysis, fair value, expected FCF, DCF/reverse DCF, WACC sensitivity, fragility, relative capital risk, or financial monitoring.
---

# Rigorous Financial Analysis (v2.1)

## Mission / output contract
Analyze investments without invented data or hidden assumptions. Prioritize **reproducibility**, economically coherent projections, and downside survival over false precision. Distinguish: **reported data**, **derived figures**, **assumptions**, **scenarios**, and **investment judgment**. Use the user's language (French by default if language unknown), concise recommendation first, detailed audit trail following.

This is a general agent skill, *not* an automated live market feed or trading system. Reference code is offline; source verification and substantive investment judgment remain the analyst's responsibility.

## Read supporting material as needed
- `references/methodology.md` — FCFF, terminal ROIC reinvestment, reverse DCF, fragility and returns math.
- `references/data-sources.md` — sourcing hierarchy, prices, currencies, FX, IFRS/US GAAP, point-in-time discipline.
- `references/sector-models.md` — semiconductors/HBM, AI/cloud/software, banks, real estate, private companies.
- `references/report-template.md` — required decision-ready research format.
- `references/html-output-standard.md` — **mandatory standalone HTML page**, fixed visual design, 1–100 needle rating with transparent five-factor weights and mandatory information.
- `templates/report.html`, `templates/report.css` — canonical responsive HTML visual design.
- `financial_skill/recommendation.py`, `financial_skill/html_report.py` — validated rating rubric, SVG needle and offline single-file HTML renderer.
- `references/calibration.md` — historical point-in-time calibration, accuracy, scenarios and limitations.
- `README.md` — calculator usage, typed domain objects, tests and synthetic worked example.

## Mandatory analytical sequence

1. **Identify the security:** exact issuer, ticker, exchange, security class, ADR ratio if any, equity vs enterprise valuation, reporting and trading currencies, price timestamp, fiscal/calendar period, outstanding/diluted shares, and specific user-requested hurdle discount rate.
2. **Verify facts from primary sources:** latest annual/interim filings, cash flow, earnings and financial notes; separately verify dated share price, FX and capital structure; show links and publication dates. Reject forward-looking statements as historical facts. For offline/unverified input explicitly say numbers are illustrative or user supplied. For current prices use actual market data; never make up or infer one.
3. **Historical 5y, 3y, last YoY:** report revenue and FCF CAGRs and most recent YoY, FCF margin/conversion, operating margins, D&A, capex, NWC, ROIC, cash/debt/lease treatment, SBC/dilution, buybacks/dividends, cash interest, obligations and refinancing calendar. Only calculate CAGR when positive meaningful endpoints. Normalize peaks/troughs and one-offs, especially memory semi and energy cyclicals.
4. **Economic forecasts, not naive FCF growth:** produce three explicit **bear / base / bull** annual driver paths (5–20 years as economically appropriate; 10 years a starting point). Forecast revenue, EBIT margin, cash tax, D&A, capex and incremental NWC → FCFF. Model segments, volumes × ASP, fab buildout, energy constraints, useful lives and margin normalization where relevant. Explain scenario rationale and feasibility.
5. **DCF and equity bridge:** discount FCFF at WACC, add normalized terminal value, bridge EV to equity (cash/non-operating assets minus debt/minority/preferred), divide by diluted shares; if the raw equity residual is negative, floor share price at zero for limited liability, flag distress and require a restructuring model; never discount FCFE at WACC or subtract debt twice. Normalize the terminal year using sustainable NOPAT and ROIC: `terminal FCFF = terminal NOPAT × (1 − g/ROIC)`. `ROIC > g`, `WACC > g`, and positive normalized terminal FCFF are required for the Gordon model. If not, use a justified finite-life/exit or residual income method; do not quietly force a Gordon value.
6. **Terminal share always:** calculate `PV(TV) / [PV(explicit FCFF) + PV(TV)]` for each scenario; make its dependence on horizon, WACC, growth, ROIC and margin explicit. **Do not adopt a hard 30% target, label >30% automatically defective, or tune assumptions to attain an arbitrary terminal proportion.** With negative explicit cash flows the share can exceed 100%; explain denominators. Show WACC ±2 pp, terminal g ±1 pp, plus material capex, margins and share-count sensitivities.
7. **Reverse DCF when priced:** determine EV implied by a **dated** quote. Calculate implied constant revenue CAGR (holding margins/reinvestment fixed), and at least three pairs of plausible revenue growth / required EBIT margin trajectories. Indicate no root when outside assumptions. Contrast with history, guidance, installed capacity, competition, balance sheet and physical infrastructure limits. Do not imply one reverse root captures all market expectations.
8. **Taleb fragility for deep research:** distinguish operating business fragility, valuation fragility and invested-capital risk. Reprice moderate/severe shocks using common units, exposure and horizons; compute signed-loss finite differences and normalized curvature, plus same-mean ±h dispersion penalty. Stress nonlinear transmission, negative FCFF, covenants, rolling liquidity, maturities, refinancing and dilution/ruin boundaries. Do not infer tail probabilities from stress scenarios. Compare peers only with consistent grids.
9. **Investor return & alternatives:** when enough assumptions exist, compute scenario shareholder IRR from explicit dividend/distribution and exit-share-price paths, including modeled dilution if applicable; **IRR is not WACC and not a promised return**. Consider opportunity cost, competing investments, downside, decision thresholds and portfolio concentration where disclosed.
10. **Transparent 1–100 recommendation rating:** use the mandatory `investment_assessment` five-factor rubric from `references/html-output-standard.md` (30% valuation, 20% conditional return, 20% quality, 20% resilience, 10% evidence). Every factor needs a justified analyst-supplied 0–100 score and rationale. Composite yields Strong Sell / Sell / Hold / Buy / Strong Buy. Never silently equate a score to probability. **No automatic rating for incomplete studies:** show an unrated gauge if dimensions or vital facts are missing, rather than fabricating a number. Include margin of safety, credible range, sensitivity, monitoring checkpoints and thesis falsification.
11. **Mandatory visual deliverable:** at the **end of every completed study, produce and deliver a beautiful, self-contained HTML report** using `templates/report.html`, `templates/report.css` and `financial_skill/html_report.py`. At the **start of the page**, place the large five-band semi-circular 1–100 investment needle and classification. Then the investment thesis, financial KPIs, history, Bear/Base/Bull DCF, terminal attribution, forecast charts, reverse DCF, fragility, sensitivities, annual model, primary sources and explicit score breakdown, in this consistent order. Provide an actual `.html` artifact link in the final response, not merely code or instructions. Follow `references/html-output-standard.md`, validate scores and inspect rendered output. Do not drop material analysis to make the dashboard prettier.
12. **Calibration and monitoring:** where historical data exist, evaluate forecast errors and scenario coverage strictly with information published *by the forecast date*. Surface systematic growth/capex/FCF biases. On recurring monitoring, compare realized observations with prior scenarios, update the assumptions, and identify what changed.

## Numerical/tool workflow
Use the packaged deterministic Python engine if supplied inputs permit:

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
PYTHONPATH=. python -m financial_skill.cli --input examples/synthetic_company.json --output /tmp/sample_report.md --html-output /tmp/sample_report.html
```

The input file is an **illustration**, not a market-data feed. Do not use its stock prices or fundamentals for real recommendations. The CLI enforces a fact-level evidence ledger for nonsynthetic inputs, but **does not authenticate those links**. Only feed values that you have checked. Reconcile calculated outputs with an independent estimate/filing arithmetic and check cross-currency, FX as-of date, ADR conversion, accounting treatment, hidden leverage and share issuance. If none of the required facts are available, deliver methodology/conditional scenarios rather than invented valuations.

### Explicit implementation limits
- Reference engine models **non-financial corporate FCFF only**. Banks/insurers require dividends/FCFE/residual income and regulatory capital; real estate and private equity require cash waterfalls/other methods.
- Constant share count in the reference engine. Model expected share issuance and buybacks explicitly in substantive reports; do not double-count SBC expense and dilution. The investor-IRR helper requires distributions and exit price as explicit user/researcher inputs.
- No automated tax NOLs, leasing schedules, acquisition integration, multi-currency conversion, segment capacity optimization, alternative terminal exit model, or probability estimation. When these are material, extend the model or disclose limitation.
- Fundamental cash-flow scenarios, fragility model shape and terminal ROIC remain *assumptions* even if the arithmetic is tested. Validation of formulas is not validation of a thesis.

## Minimal report obligations
Visual HTML report with 1–100 justified needle rating (or explicitly unrated if essential evidence is missing), plus short verdict; dated facts/sources; 3y/5y/YoY revenue+FCF; capitalization and normalized profitability; three-scenario driver assumptions, EV/equity/share and terminal fraction; reverse DCF; quantitative sensitivity/fragility; liquidity downside/ruin; optional shareholder IRR; clear invalidation tests and invest/watch/avoid conditions. Consult `references/report-template.md` for tables.
