# Mandatory HTML research deliverable — v2.1

## Output contract (every completed company study)

Deliver **one standalone, responsive HTML page** as the final study artifact, in addition to any requested Markdown, figures or source tables. The page must be consistent across companies, and the gauge must appear **before** financial charts and detailed tables.

Packaged canonical design sources:
- `templates/report.html` — accessible semantic page structure and slots.
- `templates/report.css` — colors, spacing, page layout, charts, mobile and print styles.
- `financial_skill/html_report.py` — escapes untrusted inputs, computes display data, embeds CSS and renders a single self-contained HTML file; no external CDN, javascript, remote images or network connectivity.

Run the generator with verified attributed financial input:

```bash
PYTHONPATH=. python -m financial_skill.cli \
  --input company_study.json \
  --output company_study.md \
  --html-output company_study.html
```

If `--html-output` is omitted, the generator always writes the sibling `.html` alongside the `.md` file. Finish the chat response with a link to the HTML page and label its valuation as-of date; show a minimal verdict in prose, but keep full report content in HTML.

If a research request lacks financial data sufficient to populate the engine, **never invent figures or recommendation grades**. Research and verify first; if unavailable, provide an HTML research brief documenting missing inputs with an unrated gauge, not a fabricated score. If the user requests text only, honor their preference.

## Required design layout and information order

1. Header: issuer/company, exact share/ticker (including exchange/ADR when relevant), price-as-of date, currency and synthetic/data verification status.
2. **Large semi-circular five-band needle gauge:** 1–20 **Strong Sell**, 21–40 **Sell**, 41–60 **Hold**, 61–80 **Buy**, 81–100 **Strong Buy**. Show numeric score **1–100**, category and concise conditional investment thesis. If evidence insufficient, use `Not rated`, no needle/score. Do **not** show invented middle/neutral scores.
3. Quick read: dated market price, central fair value, upside/downside, terminal contribution, prominent data-quality warning.
4. Historical facts: 3y, 5y CAGR and latest YoY for revenue and FCF, capital structure.
5. Driver-based Bear/Base/Bull valuations with normalized terminal ROIC, growth, WACC, terminal-value contribution and distress warnings; charts for base revenue and FCFF.
6. Reverse DCF market-implied growth and margin assumptions with feasibility caveat.
7. WACC × terminal-g price sensitivity table; range should reflect inputs, not manufactured confidence intervals.
8. Taleb-style finite-difference stress/fragility, liquidity breach/financing gap, conditional shareholder IRR where available. Distinguish local curvature from tail risk.
9. Auditable annual FCFF model, source links and source publication dates, thesis catalysts/invalidation and transparent scoring breakdown.
10. Footer with model limits, data provenance, non-personalized investment research disclaimer, print styling.

The layout must be self-contained (HTML+embedded CSS), mobile-responsive, accessible SVG gauge with a text equivalent, and printable. Do not link to unverified resources or rely on a live browser API. Escape user inputs rather than trusting raw HTML in financial descriptions or links.

## Recommendation scoring rubric

Score is an **analyst-justified composite judgment**, not a modeled probability, expected price appreciation or predicted return. Do not represent it as statistically calibrated. All five dimension scores require a nonempty evidence-based rationale, preferably citing the relevant fundamental tables and scenarios.

| Dimension | Weight | What it must consider |
|---|---:|---|
| Valuation & margin of safety | 30% | Base fair value vs quote, Bear downside, value ranges and alternatives |
| Conditional shareholder return | 20% | Modeled investor IRR vs hurdle and opportunity cost, payout/dilution assumptions |
| Business quality & durability | 20% | ROIC economics, competitive durability, management/capital allocation, cyclicality |
| Balance sheet & downside resilience | 20% | Cash runway, refinancing gaps, concentration, nonlinear shock loss, risk of ruin |
| Evidence quality & uncertainty | 10% | Filing provenance, confidence in model drivers, cyclicality, data gaps, calibration |

For **each dimension**, interpret points as follows; interpolate where justified:
- **0**: severely unfavorable, or demonstrably poor; be explicit about why.
- **25**: unfavorable / substantial adverse assumptions or uncertainty.
- **50**: neutral, fairly valued / marginally meets the relevant hurdle.
- **75**: favorable, meaningful evidence-supported advantage / risk-adjusted attractiveness.
- **100**: exceptional under the identified economics; not a guarantee.

**Important:** Missing evidence is not automatically a 0 or 50. For meaningful uncertainty that can be analyzed, lower the evidence dimension and explain why. If vital inputs or the analyst's dimensions are absent, withhold the rating entirely rather than creating false precision.

Weighted score `round_half_up(sum(weight_i × dimension_i)/100)`, clamped to integer `[1,100]`. All weights fixed above. Analyst must keep qualitative thesis consistent with computed category; if not, revise underlying assumptions or disclose disagreement, never manually override the derived score. No 30% target for terminal value. A 1-point variation is not meaningful precision; display the number because requested, with full component rationale and dominant sensitivities.

### Example `investment_assessment` field

```json
{
  "investment_assessment": {
    "thesis": "Conditional watch: fair value approximately equals the quote; expected return does not clearly beat the hurdle.",
    "components": {
      "valuation": {"score": 50, "rationale": "Base FCFF DCF is close to current dated price; deep Bear downside remains."},
      "return": {"score": 45, "rationale": "Conditional five-year IRR trails the analyst's required return."},
      "quality": {"score": 65, "rationale": "Above-cost-of-capital ROIC; competitive endurance not yet demonstrated."},
      "resilience": {"score": 40, "rationale": "Stress funding gap and cyclicality limit resilience."},
      "evidence": {"score": 70, "rationale": "Five audited historical periods; estimate uncertainty remains."}
    },
    "catalysts": ["Evidence supporting improved unit economics"],
    "invalidation_triggers": ["Unexpected sustained cash burn"]
  }
}
```

For real reports these grades must be derived from the actual research. This fragment illustrates schema, not a recommendation. If this input is omitted, the HTML report will explicitly show **Not rated**.

## Quality checklist before sharing

- [ ] Date, ticker, currency, price and source are displayed and reconcile.
- [ ] Gauge needle, number and verbal category agree with documented component scores.
- [ ] No numerical rating appears when dimensions are missing.
- [ ] Revenue/FCFF charts and every fair-value card match the deterministic output.
- [ ] The terminal value share is displayed and not interpreted against an arbitrary 30% cap.
- [ ] All scenarios, sensitivity tables, distress warnings and data limitations are retained.
- [ ] Underlying source values are cited where real data exist; synthetic figures visibly flagged.
- [ ] HTML renders offline, on mobile and in print, with no active content or external dependency.
