# Primary-source and point-in-time policy

## Priority
1. Regulatory filings / official reports (10-K, 10-Q, 20-F, annual statements, AMF disclosures, DART, exchange filings) and cash-flow notes.
2. Issuer investor relations and earnings presentations for management guidance; do not substitute non-GAAP guidance for reported history.
3. Independent financial market data provider for **dated** quotation, currency, effective shares, listing class, corporate actions and ADR ratio. Check several sources when possible.
4. Industry sources for energy/fab capacity and unit economics, marked as estimates; third-party consensus must carry provider/date and distinguish estimate vs realized.

No unsupported current prices. Record **price date and timezone** separately from **period end** and **publication date** of filings. For LTM, show which quarters used and whether cumulative cash flow has been de-accumulated; avoid double counting. If annual report is not yet public at valuation date, it cannot appear in a backtest.

## Data ledger required for nonsynthetic CLI use
Input JSON includes an `evidence` array with one record per core reported number:

```json
{"fact_key":"starting_revenue_millions","source_kind":"filing","source_url":"https://example.com/real-document","published_on":"2026-02-10","period_end":"2025-12-31"}
```

Required keys include `starting_revenue_millions`, `capital_structure.cash`, `.debt`, `.diluted_shares_millions`, `price_snapshot.price`, and historical revenue/FCF period entries if present. Validation rejects missing keys, future-published evidence and non-HTTPS attribution. **URL syntax checks do not verify the links or that the documents actually support the numbers**; the analyst must check them. Source and observation dates must be contemporaneously plausible.

## Cash-flow definitions
- Simple reported FCF often CFO − capex. That is **not generally identical to unlevered FCFF**, because CFO includes cash interest and other financing-related tax effects. The engine forecasts **FCFF from after-tax EBIT, depreciation, capex and NWC** and values EV at WACC. Record and reconcile discrepancies.
- Distinguish maintenance vs growth capex and lease principal vs lease operating charges. Investment in intangibles may belong in economic capex.
- SBC: state whether it is treated as full economic compensation (in NOPAT/FCFF), or the model assumes eventual share issuance; never blindly subtract the expense and also penalize shares for the same grant. Present dilution/buyback sensitivity if material.
- Debt, cash, preferred, minority, pension, finance leases, contingent liabilities: reconcile consistently between enterprise and equity values. Exclude operational minimum cash from excess cash when relevant.
- Non-operating securities/associates and minority claim values need explicit balance-sheet/market assumptions, not blindly book values.
- For IFRS vs US GAAP, especially capitalized R&D, leases, interest and operating cash flow definitions, adapt economically rather than importing fields without reconciliation.

## Required reasonableness cross-checks
- Market cap ≈ price × *correct security-equivalent* diluted shares; ADR ratio, splits and currency conversions documented.
- Currency: match FCF and WACC and terminal growth; date and method of FX translation; do not mix USD per ADR with KRW ordinary shares.
- FCFF year forecasts vs operating income margins, taxes, reinvestment and industry returns.
- Terminal reinvestment vs g/ROIC; terminal NOPAT vs last-year NOPAT.
- Sensitivity if market has a quote, and at least one comparator or market opportunity-cost benchmark.
- If any fact is unavailable, show missingness explicitly rather than imputing certainty.
