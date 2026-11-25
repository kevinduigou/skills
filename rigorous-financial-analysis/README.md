# Rigorous Financial Analysis — reusable Agent Skill v2.1

An installable `SKILL.md` plus **Python 3.10+ standard-library-only** reference engine. Combines point-in-time evidence provenance, annual economic driver forecasts, 3-scenario FCFF DCF, normalized ROIC-based terminal cash flow, reverse implied revenue growth/margin grid, downside convexity/dispersion analysis, liquidity stress, investor IRR and calibration primitives. Includes **mandatory fully offline HTML reporting with an SVG investment gauge, responsive charts, and a fixed research layout.**

## Install
Put the `rigorous-financial-analysis` folder in the Skills directory supported by your agent (for example, an Agent Skills-compatible `skills/` folder). Your host's discovery/install steps may differ. Ask the agent to follow the `SKILL.md` workflow for stock/DCF/fragility requests.

## Verify without internet
Run from this folder:

```bash
PYTHONPATH=. python -m unittest discover -s tests -v
PYTHONPATH=. python -m financial_skill.cli --input examples/synthetic_company.json --output /tmp/synthetic_report.md --html-output /tmp/synthetic_report.html
```

Open `examples/synthetic_report.html` in any web browser for the full dashboard and `examples/synthetic_report.md` for the text version. **HTML is generated automatically by default**, using the same `--output` basename if `--html-output` is omitted. **All sample prices and fundamentals are invented solely for demonstration** and must never be cited as real market observations.

## Input schema
The sample JSON enumerates all required economic drivers. Amounts `starting_revenue_millions` and balance-sheet entries are **millions of the declared currency**; `diluted_shares_millions` is million ordinary-equivalent shares, so `price` is currency per share. Each of `bear`, `base`, `bull` must specify an array of 1–20 annual driver sets, WACC, terminal g, ROIC and normalized terminal EBIT margin/tax. Example has 10 years.

For nonsynthetic inputs, set `synthetic: false` and provide the `evidence` array described in `references/data-sources.md`. Source URLs and dates are validated structurally but **not verified through network requests**. Any real stock investment analysis must manually confirm the filings and price as of the valuation date.

`revenue_shock_step` controls the symmetric revenue level shock step. `downside_quadratic_margin_drag` is an **explicit analyst assumption** defining adverse margin transmission as `-coefficient × max(-shock,0)^2`; zero if absent. It is not estimated by the model. Optional `liquidity_stress` is a separate cash bridge with annual debt maturities, optional minimum buffer and committed funding. Optional `shareholder_return_assumptions` are dividends and a hypothetical exit price, not a forecast.

## Canonical report and needle rating

The full presentation standard is in `references/html-output-standard.md`. `templates/report.html` and `templates/report.css` define the consistent layout. The renderer embeds its styles into one portable HTML file without CDN or scripts.

For a numerical recommendation, add `investment_assessment` with five analyst-explained scores (valuation 30%, conditional shareholder return 20%, business quality 20%, downside resilience 20%, evidence/uncertainty 10%). The computed score is an integer 1–100; categories are **Strong Sell (1–20), Sell (21–40), Hold (41–60), Buy (61–80), Strong Buy (81–100)**. A rating is withheld when components are absent. A rating is an analyst opinion, **not** a success probability or mechanically generated trading signal. The synthetic fixture shows a fictional score for display testing.

## Core library

- `domain.py` — currency-safe `MoneyMillions`, `SharesMillions`, validated `DiscountRate` and `CapitalStructure`; no implicit FX/ADR conversion.
- `forecasting.py` — driver-based FCFF, normalized terminal NOPAT and reinvestment `g/ROIC`.
- `valuation.py` — WACC FCFF to EV/equity, per-share value, terminal fraction and 3×3 sensitivity; zero floor / distress flag for negative residual equity.
- `reverse.py` — root-bracketed implied constant revenue CAGR and margin shift frontier; failure when unbracketed/nonmonotone.
- `fragility.py` — explicitly transmitted stress, signed-loss second differences, mean-preserving shock dispersion, liquidity runway.
- `returns.py` — dividend plus terminal sale price IRR for held shares.
- `historical.py` — positive-endpoint-only CAGR and YoY.
- `calibration.py` — out-of-sample fact-availability guard and historical error metrics.
- `evidence.py` — fact-level source records with publication as-of date checks.
- `recommendation.py` — fixed five-component weighting, documented rationale and 1–100 score validation.
- `html_report.py` — HTML escaping, accessible SVG needle, responsive scenario visuals, forecasts, stress, sources and print styles.
- `cli.py` — Markdown **plus mandatory standalone HTML report** from JSON inputs. Data feed deliberately excluded.

## Boundaries and backlog
This is a deterministic **reference implementation**, not a professional securities terminal: no live data ingestion, automatic evidence verification, segment/fab operating optimizer, FX, ADR conversion, diluted share path, tax loss carryforwards, exit multiples, leases schedule, or bank/real-estate waterfall engine. Those must be implemented separately when material. A type-safe and well-tested DCF calculator can still produce a badly wrong valuation if its assumptions are implausible. Do not add arbitrary terminal-value percentages or pseudo-probabilities to mask economic uncertainty.
