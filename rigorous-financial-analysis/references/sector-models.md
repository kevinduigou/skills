# Sector routing and drivers

## Semiconductors and memory (SK hynix, Micron, Samsung, SanDisk)
- Separate DRAM/NAND/HBM and foundry/logic where applicable: **bit shipments × ASP**, margins and yield, supply capacity, fab generations, utilization, inventory and cycle age.
- HBM capacity and packaging/TSV yields, supply agreements, customer concentration, DRAM wafer allocation, ramp costs, product mix and competitor supply.
- Model capex committed in weak demand, depreciation with a lag, inventory build/clear, margin trough and multi-year recovery. Peak FCF alone is not a normalized base.
- Stress ASP -20/-40/-60%, volume, yield or customer shift with comparable fixed-capex rules. Check financing/lending and cash buffers through downturns.

## AI infrastructure and semiconductors (NVIDIA, accelerators)
- Distinguish silicon unit ASP/shipments, networking, recurring/service sales; hyperscaler cash ROI, customer cash generation and replacement cycle.
- Energy/transformers/datacenter construction and interconnect, GPU utilization, export rules, competition, supply chain concentration, depreciation and pricing power.
- Stress customer capex contraction, pricing pressure and lower return on installed AI compute; do not assume all booked AI capex is sustainable demand.

## Software, cloud and platforms (Alphabet, Meta, software platforms)
- Separate advertising/cloud/consumer/hardware and AI inference/training; paid seats/users × ARPU, margins, incremental serving cost, customer acquisition and retention.
- Advertising cyclicality, privacy/regulatory exposure, data center depreciation useful life, energy, incremental capex, SBC net dilution and antitrust remedies.
- Model infra capex and depreciation with different timing; do not treat capital expenditure as perpetually depressed or one-time automatically.

## Energy and commodities (e.g., XOM)
- Commodity prices × production, decline rates, depletion reserve replacement, project breakevens, operating leverage, fiscal regimes and environmental/liability obligations.
- Reserve lives and future capex alter terminal interpretation. For a depleting resource, use a finite-life resource model rather than arbitrary perpetual FCF.
- Oil price stress, fuel/input costs, hedges, tax windfalls and rate sensitivity must pass through production/FCF mechanics, not only WACC.

## Financial firms (banks, insurance)
**Do NOT use industrial FCFF EV/WACC engine.** Debt is operating raw material, working capital and CFO are not comparable. Use dividend discount, excess return/residual income and FCFE based on regulatory distributable capital. Consider CET1/RWA, cost of risk, NIM, funding costs, liquidity and insurance reserve adequacy. Specialized calculation implementation is *not included* here.

## Property and housing investments
Owner-occupied or rental IRR must include purchase costs, closing fees, taxes, maintenance, insurance, debt schedule, amortization and equity proceeds net of selling costs/taxes. For rent-vs-buy, include imputed rent saved, rent inflation, investing the downpayment and cash differences, and consistent opportunity cost. Do not classify mortgage principal as expense or ignore equity buildup. Specialized amortization implementation is *not included* here.

## Private business / startup equity
- Discount future owner cash flows under funding/dilution and exit constraints, liquidation preferences, options and shareholder waterfall.
- Separate enterprise value from investor security's equity payoff, given preferred claim structure.
- No invented public quote; extreme uncertainty implies ranges, not precise target prices.

## Comparative work
Use same valuation date, FX, WACC/currency assumptions when appropriate, shock normalization, terminal ROIC policy, and economic cycle. Ranking by one DCF upside number without base-rate/fragility considerations is not a defensible cross-sector decision.
