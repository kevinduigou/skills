# Retrospective calibration protocol

## Objective
Assess whether the forecasting system systematically overestimates revenue, margins, or FCFF, or assigns too-narrow scenario bands. This is not a mechanical backtest of hypothetical stock trading and is not evidence that forecast-error reduction ensures excess returns.

## Required as-of controls
For each historical valuation date T:
1. Freeze the filings, consensus, news and share counts **published by T**, not the current revised history.
2. Archive input assumptions and their sources. Market data must be splits-adjusted consistently and from the proper listing currency.
3. Forecast a pre-specified target fiscal period after T, then record reported actual **and its publication date**.
4. Compare actual against bear/base/bull, record absolute/signed error; when realized >0 calculate percentage error; present WAPE only if sum of actual absolute amounts >0.
5. Attribute surprise to shipments/ASP, taxes, capex, NWC, share dilution, market discount assumptions, etc. Recalibrate **only subsequent** test windows (rolling origin).

## Metrics implemented
`financial_skill.calibration` returns `MAE`, signed forecast bias (base−actual), bear–bull empirical coverage and `WAPE`. For heteroskedastic cyclical markets, inspect horizon-by-horizon error, regime and forecasts' distribution; price outcomes also depend on changing required returns and macro expectations. Avoid optimizing to retrospectively known prices. More advanced proper scoring rules can be added if probabilities are externally justified.

## Point-in-time invariant
Each `ForecastRecord` stores `forecast_asof`, `target_period_end`, and `actual_published_on`. The code rejects any record that puts published actuals before the forecast date. This prevents one simple class of leakage, but does not replace auditing the actual historical dataset.
