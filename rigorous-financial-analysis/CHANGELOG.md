# v2.1 — Mandatory visual report and investment needle (2026-11-24)

- Added a self-contained, responsive HTML report template with fixed section order, accessible semi-circular investment needle and printed output.
- Added transparent five-dimension investment scoring, fixed weighting, reasoned analyst inputs, 1–100 composite and five recommendation bands; no rating with missing inputs.
- HTML report contains financial KPIs, 3-scenario DCF, revenue/FCFF charts, reverse DCF, sensitivity heatmap, Taleb fragility stress, liquidity, annual forecast, source ledger and score breakdown.
- CLI now always generates `.html` alongside Markdown; optional `--html-output` overrides destination.
- Included a fictional HTML report and scoring example; no external data dependencies, no JavaScript or CDN.
- New security and consistency tests for HTML escaping, rating bounds, band mapping and page generation.

# Changelog

## 2.0.0 — Driver-based, auditable reference implementation

**Replaces** the original single-file `scripts/dcf.py` with typed package `financial_skill`.

- Implements revenue → EBIT → NOPAT → FCFF forecasting for annual bear/base/bull scenarios.
- Implements normalized terminal value from `NOPAT × (1 - g/ROIC)` and strict `WACC > g`, `ROIC > g` checks.
- Always reports PV terminal contribution; **removes the outdated 30% maximum / target as a quality standard**.
- Adds EV → equity reconciliation, limited-liability equity floor and distress flag.
- Adds dated-price reverse DCF solving revenue CAGR and an EBIT-margin frontier.
- Adds explicit WACC × terminal-growth sensitivity and shock re-pricing.
- Adds signed adverse-loss second difference, mean-preserving ±shock dispersion measure and cash-runway breach modeling.
- Adds conditional shareholder IRR, positive-endpoint-only historical CAGR/YoY and point-in-time forecast calibration primitives.
- Validates money currencies and share units; requires source-date provenance ledger for nonsynthetic CLI input.
- Includes a visibly synthetic JSON example and rendered research report; no live market feed.
- Adds 32 unit/integration tests, standard-library-only engine, and optional Python package metadata.

**Still out of scope:** live data fetching/verification, accounting adjustments requiring source notes, actual 5y historical backtest without a point-in-time dataset, diluted share issuance path, debt schedule interest/tax modeling, insurance/bank FCFE and real estate/equity waterfalls. Do not interpret implementation coverage as validation of the investment scenarios.
