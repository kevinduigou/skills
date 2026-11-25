# Financial analysis — EXAMPLE-NOT-LISTED

**Research recommendation:** Sell — 34/100 (documented analyst scoring; not a return probability)

**Warning:** Synthetic educational example; NOT real company financials or market quotes.
**Market snapshot:** 34.50 USD/share on 2026-01-01 · synthetic://educational-fixture-no-market-data
**Units:** all monetary aggregates are millions of USD, diluted shares are millions, prices are USD/share.
**Valuation type:** FCFF discounted at WACC → EV → equity bridge. No FCFE/WACC mixing.

## Scenarios
| Case | WACC | Terminal g | Terminal ROIC | EV (m) | Equity (m) | Fair/share | Upside | PV terminal / EV | Distress flag |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| bear | +13.0% | +1.5% | +12.0% | 4,852.6 | 2,852.6 | 3.17 | -90.8% | +41.6% | no |
| base | +11.0% | +2.5% | +18.0% | 28,150.5 | 26,150.5 | 29.06 | -15.8% | +51.4% | no |
| bull | +10.0% | +3.0% | +23.0% | 64,167.6 | 62,167.6 | 69.08 | +100.2% | +60.1% | no |

The equity bridge is floored at zero for limited liability; a negative raw residual flags possible distress and requires a separate restructuring/equity-option analysis.
Terminal share is descriptive, not a pass/fail cutoff. It can exceed 100% when negative interim FCFF offsets terminal PV.
No fixed 30% target is used. Stress discount rate, terminal g, ROIC and normalization instead.

## Base case FCFF forecast
| Year | Revenue (m) | EBIT (m) | NOPAT (m) | D&A (m) | Capex (m) | ΔNWC (m) | FCFF (m) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 13,020.0 | 2,994.6 | 2,335.8 | 846.3 | 1,302.0 | 71.4 | 1,808.7 |
| 2 | 14,076.1 | 3,221.9 | 2,513.0 | 914.9 | 1,407.6 | 73.9 | 1,946.5 |
| 3 | 15,163.0 | 3,453.8 | 2,694.0 | 985.6 | 1,516.3 | 76.1 | 2,087.2 |
| 4 | 16,275.0 | 3,689.0 | 2,877.4 | 1,057.9 | 1,627.5 | 77.8 | 2,230.0 |
| 5 | 17,405.2 | 3,925.8 | 3,062.2 | 1,131.3 | 1,740.5 | 79.1 | 2,373.9 |
| 6 | 18,546.2 | 4,162.6 | 3,246.8 | 1,205.5 | 1,854.6 | 79.9 | 2,517.8 |
| 7 | 19,689.9 | 4,397.4 | 3,430.0 | 1,279.8 | 1,969.0 | 80.1 | 2,660.8 |
| 8 | 20,827.5 | 4,628.3 | 3,610.1 | 1,353.8 | 2,082.8 | 79.6 | 2,801.5 |
| 9 | 21,949.9 | 4,853.4 | 3,785.6 | 1,426.7 | 2,195.0 | 78.6 | 2,938.8 |
| 10 | 23,047.4 | 5,070.4 | 3,954.9 | 1,498.1 | 2,304.7 | 76.8 | 3,071.5 |

- Present value of explicit FCFF: **13,687.0m**.
- Normalized year N+1 FCFF: **3,490.8m**.
- Present value of terminal value: **14,463.5m**.
- Cash: 2,300.0m; debt: 4,400.0m; diluted shares: 900.0m.

## Reverse DCF
- Market-implied enterprise value: **33,050.0m**.
- Constant annual revenue growth needed at base margins/reinvestment: **+9.2%**

| Constant revenue CAGR | Required EBIT margin shift (all projected years + terminal) |
|---:|---:|
| -5.0% | No feasible root |
| +0.0% | No feasible root |
| +5.0% | +6.7% |
| +10.0% | -1.0% |
| +15.0% | -6.6% |
| +20.0% | -10.5% |

These inverse solutions are **conditional** on the fixed assumptions; they do not identify the market's actual beliefs.

## Sensitivity: base fair value per share
| WACC | Terminal g | Fair/share |
|---:|---:|---:|
| +9.0% | +1.5% | 37.52 |
| +9.0% | +2.5% | 39.70 |
| +9.0% | +3.5% | 42.63 |
| +11.0% | +1.5% | 28.14 |
| +11.0% | +2.5% | 29.06 |
| +11.0% | +3.5% | 30.19 |
| +13.0% | +1.5% | 22.15 |
| +13.0% | +2.5% | 22.55 |
| +13.0% | +3.5% | 23.03 |

## Fragility: same-economics revenue-level shock
- Assumed nonlinear transmission: EBIT margin drag = -0.80 × max(-revenue shock, 0)^2 (zero if not provided). This is a scenario assumption, NOT calibrated evidence.
- Baseline equity value: 26,150.5m; -10% revenue shock: 22,373.8m; -20%: 16,983.4m; +10%: 28,889.9m.
- Adverse-loss second difference: **1,613.6m** / base equity: **+6.2%**.
- Same-mean symmetric dispersion penalty J: **518.7m** / base equity: **+2.0%**.
- Finite differences depend on shock size, baseline, horizon and model specification. Not tail probabilities.
- Business resilience, modeled equity value and investor loss are distinct; add contractual/covenant cash cliffs where applicable.
- Liquidity stress: first minimum-cash breach year: **2**; peak financing gap: **900.0m**.

## Investor return, separate from intrinsic value
- Assumed annual dividends [0.5, 0.55, 0.6, 0.65, 0.7]; assumed exit price 50.
- Conditional investor IRR: **+9.2%**. NOT a forecast or a discount rate.

## Historical diagnostics
| Metric | 3y CAGR | 5y CAGR | Latest YoY |
|---|---:|---:|---:|
| revenue_millions | +10.1% | +8.4% | +9.1% |
| fcf_millions | +28.6% | n.m. | +21.4% |
CAGRs are n.m. for nonpositive start/end values; inspect cycle-normalized FCF.

## Decision and falsification checklist
- **No mechanically inferred trading signal.** Any displayed rating is an analyst-justified five-factor composite, not a promise or probability. Compare implied economics, competitive position, leverage and alternatives.
- State explicit valuation date, confidence range, margin of safety, required return and thesis-breakers.
- Confirm dilution, SBC treatment, foreign listing/ADR conversion, leases, NOLs, tax and reporting currency.
- Reconcile and cite each original filing, share count and price; replace this example with primary-source observations.
