# Methodology: mechanically auditable, economically defensible

## Units and conventions
All `MoneyMillions.amount` values are in **millions of explicitly named currency**. `SharesMillions.count` is **millions of ordinary-equivalent shares**. Their ratio is currency per ordinary-equivalent share. No implicit FX, share conversion, or ADR ratio conversion. All rates are annual decimals (e.g., `0.12` = 12%). Cash flows at year-end, no midyear convention. The reference model assumes nominal discount and nominal terminal growth in the same currency. Inflation, FX, and local currency WACC must be consistent.

## Operating model
For each forecast year t, with previous revenue `R_{t-1}`:

```
R_t       = R_(t-1) * (1 + sales_growth_t)
EBIT_t    = R_t * EBIT_margin_t
NOPAT_t   = EBIT_t - max(EBIT_t, 0) * modeled_cash_tax_rate_t
D&A_t     = R_t * depreciation_pct_t
Capex_t   = R_t * capex_pct_t
DeltaNWC_t= (R_t - R_(t-1)) * incremental_NWC_per_incremental_revenue_t
FCFF_t    = NOPAT_t + D&A_t - Capex_t - DeltaNWC_t
```

Loss-carryforwards, cash interest in bridge, acquisitions, leases, SBC and post-tax operating items must be added separately if material. `NOPAT` assumes the standard operating-tax shield; a negative EBIT carries no immediate tax benefit in this simple engine. This is an explicit simplification, not GAAP tax modeling. Capex must be sustainable relative to installed assets and unit growth. High capacity utilization / ASP shocks require explicit segment forecasts.

## Terminal steady state
For year N+1:

```
Revenue_(N+1) = Revenue_N * (1+terminal_g)
NOPAT_(N+1) = Revenue_(N+1) * normalized_terminal_EBIT_margin * (1 - terminal_cash_tax)
Steady_state_reinvestment = NOPAT_(N+1) * terminal_g / normalized_ROIC
FCFF_(N+1) = NOPAT_(N+1) * (1 - terminal_g/normalized_ROIC)
TV_N = FCFF_(N+1) / (WACC - terminal_g)
```

Require positive ROIC, `ROIC > g`, `WACC > g`, and positive terminal FCFF. Check `FCFF_(N+1) / FCFF_N` against a plausible transition and report unexplained discontinuities. A steady state with market share and returns far above competitive equilibrium requires justification. For negative terminal growth, reinvestment release may be temporary; if unsustainable, do not use a perpetuity.

## Value and equity bridge

```
EV = SUM(FCFF_t / (1+WACC)^t, t=1..N) + TV_N/(1+WACC)^N
EquityValue = EV + cash + nonoperating_assets - debt - minority_interest - preferred_stock
FairSharePrice = max(0, EquityValue) / diluted_shares    # limited-liability floor
TVShare = [TV_N/(1+WACC)^N] / EV
```

The implemented bridge retains the **raw economic equity residual**, floors displayed common equity value at zero to reflect limited liability, and raises a **distress flag** if the residual is nonpositive. Zero is not a complete option/restructuring valuation; seniority, recovery, capital injection and equity optionality require a specialist model. Debt definitions (including lease liabilities) must correspond to FCFF treatment. Cash can be restricted or needed for operations; do not automatically count it all as excess. Interest-bearing leases and pension obligations may require balance-sheet bridge adjustments. A single share count is an implementation simplification; forecast the dilution if material. If using FCFE, discount at cost of equity and **do not apply an EV bridge**.

Terminal share is an attribution ratio, **not a fixed target**. Its denominator can be negative or small when explicit FCFF is deeply negative; discuss such cases rather than clamp the ratio. Increase horizon only if supported by economics; moving terminal years into the explicit window does not extinguish uncertainty.

## Reverse DCF
Given a verified share price P at a dated snapshot:

```
MarketEquity = P * diluted_shares
MarketEV = MarketEquity - cash - nonoperating_assets + debt + minority + preferred
```

Find a driver θ such that `modeled_EV(θ) = MarketEV` with all other parameters fixed. The reference engine solves constant **explicit revenue CAGR** or, for each fixed revenue CAGR, a common **EBIT margin shift** across years and normalized terminal margin. Use a bracketed monotone root; if the target isn't in range or modeled value is nonmonotone, show `no feasible root`. Interpreting implied economics requires considering multiple combinations of margins, capex and business duration.

## Finite-difference fragility
Let `V(s)` be valued equity after a shock s, where larger adverse s means greater damage. Use signed loss `L(s) = V(0)-V(s)` to avoid spurious kinks induced by `max(0,.)`.

```
Adverse curvature C(h) = L(2h) - 2L(h) + L(0)
                       = 2V(h) - V(2h) - V(0)
Normalized C = C / V(0)  [only when V(0) > 0]
Mean-preserving dispersion J(h) = (L(-h)+L(+h))/2 - L(0)
                                = V(0) - [V(-h)+V(+h)]/2
```

Positive C indicates accelerating adverse losses over that interval. Positive J indicates that more symmetric shock dispersion reduces mean modeled value (assuming symmetric shocks around same mean). Both depend on the specific shock grid and exposure, can be zero in linear models, and cannot be casually compared across unlike shocks. **They are not probabilities of ruin.** Model nonlinear margin transmission, capex rigidity and debt/operating costs explicitly; never assume convexity just because a narrative mentions tail risks.

Separate: business FCF declines; equity (residual claim) may lose disproportionately because of senior claims; purchase price relative to fair value may amplify investor loss. Report distance to liquidity/covenant threshold in shock units when such data exist. The reference cash-runway helper uses only the analyst's cash, committed liquidity, operating FCF and debt maturity assumptions; re-check mandatory interest/maintenance capex treatment and minimum cash buffer.

## Investment IRR
An investor paying P and receiving future cash dividends D_t, then selling at price S_N, solves:

```
0 = -P + SUM(D_t/(1+IRR)^t) + S_N/(1+IRR)^N
```

This is a scenario-implied investor return, conditional on exit valuation and distributions; **it is not the DCF discount rate**. Buybacks can change share count and investor ownership without cash dividends; model per-share dilution and share count explicitly where material. Do not claim that buying below computed DCF fair value guarantees an IRR.

## Historical CAGR, cycles and base rates
For positive endpoints over n years, `(end / start)^(1/n)-1`. Zero/negative FCF → report n.m., absolute changes and cycle-normalized FCF instead. Include most recent YoY and comparisons with segment cycles, peer ROIC, plausible long-term capacity, margin ceilings, capex, and industry base rates. Avoid treating a peak as a recurring normal level.
