> **Final deliverable:** build the standalone `.html` research dashboard with the 1–100 investment needle first. For design and rubric see [`html-output-standard.md`](html-output-standard.md). This Markdown outline is the substantive source-of-truth, not a substitute for the required HTML artifact.

# Standard report template

## Investment decision (as-of YYYY-MM-DD)
**Transparent rating (1–100, or Not Rated):** ... | **Classification:** Strong Sell / Sell / Hold / Buy / Strong Buy | **Ticker/exchange/class:** ... | **Price timestamp/source:** ... | **Currency, ADR:** ... | **Conditional stance:** buy/watch/avoid | **Reason:** ... | **Facts missing:** ...

## Verified facts vs assumptions
| Item | Value | Units/period | Publication date | Primary-source link | Type (actual / estimate / assumption) |
|---|---:|---|---|---|---|
| Revenue | | | | | |
| EBIT margin | | | | | |
| CFO, capex, reported FCF | | | | | |
| Cash/debt/minority | | | | | |
| Diluted shares, SBC, buybacks | | | | | |

**Historical diagnostics:** 5-year CAGR + 3-year CAGR + latest YoY for both revenue and FCF, n.m. when endpoints nonpositive; cycle normalization and capex/FCF conversion.

## Explicit three-scenario FCFF DCF
| Driver / Result | Bear | Base | Bull |
|---|---:|---:|---:|
| Starting revenue (reported) | | | |
| Revenue growth years 1–5 / 6–10 | | | |
| EBIT margin path | | | |
| Tax / D&A / capex / ΔNWC | | | |
| Terminal ROIC, growth, WACC | | | |
| PV explicit FCFF | | | |
| PV terminal FCFF | | | |
| **PV terminal / EV** | | | |
| EV → equity bridge | | | |
| **Fair value per diluted share** | | | |
| Upside vs dated quote | | | |

Explain nonlinear shift from final explicit FCFF to normalized terminal FCFF and any changes in reinvestment policy.

## Reverse DCF
Price-implied EV. Revenue CAGR needed under base margins; matrix of revenue growth vs implied terminal/steady EBIT margin. Describe plausible/implausible demand and reinvestment constraints. Show no root rather than extrapolating.

## Sensitivity & fragility
WACC × g fair-value table; sensitivities to ROIC, EBIT margin, capex, cash/debt and dilution. Revenue/price/rate/input shocks with explicit transmission, stressed equity values, normalized adverse C(h), mean-preserving dispersion J(h), liquidity buffer and threshold to financing distress. Specify shocks by unit/horizon; no invented probabilities.

## Expected investor outcome
Explicit purchase price, annual distributions, conditional exit prices and shareholder IRR. Identify where dilutive stock grants, taxes or repurchases modify payoff. Contrast to risk-free alternative, hurdle and other opportunities.

## Conditional verdict and falsification
Acceptable valuation/purchase price, evidence needed to upgrade/downgrade stance, thesis breakers, monitoring triggers, timing of future results and primary links. No guaranteed return or single-score certainty.
