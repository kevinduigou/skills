---
name: setup-autoresearch
description: Define a rigorous, measurable autonomous research loop before implementing or running experiments. Use when the user invokes /setup-autoresearch or asks to configure an autoresearch workflow.
---

# /setup-autoresearch

## Purpose

Turn an initially vague research goal into an explicit, testable experiment specification that an autonomous agent can execute safely.

Do not start modifying code or launching experiments until the goal, metric, measurement infrastructure, experiment boundaries, and validation protocol are sufficiently specified. Ask questions conversationally, in small batches. Reuse information already provided by the user or discovered in the repository; do not ask for it again.

The output is a concise Autoresearch Specification and, when approved, a rendered `program.md`. Render `program.md` from `templates/program.md.j2` using the structured values collected during the interview. 

## Operating principles

- **Clarify before optimizing.** Never assume that a convenient metric represents the user's real goal.
- **Prefer observable outcomes.** Every metric must have a precise definition, data source, unit, direction of improvement, and evaluation command or procedure.
- **Separate objective from constraints.** Use hard constraints for invalid experiments and non-negotiable limits; do not let a weighted score compensate for a violation.
- **Avoid metric gaming.** Identify ways the agent could improve the score without improving the underlying goal.
- **Make experiments attributable.** Prefer one meaningful change per experiment unless the user explicitly wants compound changes.
- **Keep comparisons fair.** Fix or record data versions, splits, seeds, compute budgets, software versions, and baseline commit.
- **Target the leaderboard leader.** For model or strategy improvement with ranked candidates, use the top eligible entry in `leaderboard.md` as the incumbent to beat, unless the user explicitly specifies another objective. An older baseline or convenient weak opponent must not silently replace it. Preserve explicit objectives for other research tasks.
- **Validate beyond the search loop.** Do not treat the best score seen during repeated experimentation as unbiased evidence of generalization.
- **Be honest about missing infrastructure.** If the metric cannot currently be measured reliably, make instrumentation or dataset preparation a prerequisite.
- **Minimize friction.** Ask only questions whose answers materially affect the design. Offer reasonable defaults, clearly labeled as proposals, when the user is unsure.
- **Render from a template.** Keep the reusable instructions in `templates/program.md.j2`; do not hand-compose a separate, inconsistent `program.md` when the template is available.
- **Do not leave unresolved template variables.** Validate the data context and inspect the rendered file for leftover Jinja delimiters or missing required sections before calling it complete.

## Interview workflow

Proceed through the phases below. Ask one focused question at a time when a missing answer blocks progress. If several independent details are essential and easier to answer together, ask a short grouped set. Do not dump the entire questionnaire at once.

### Phase 1 — Goal: what should improve?

Establish:
1. The real-world or scientific outcome the user wants.
2. The object being optimized (model, feature set, strategy, code path, policy, workflow, etc.).
3. The intended user or downstream decision, if relevant.
4. What success looks like in practical terms.
5. Scope and exclusions.
6. For ranked-candidate optimization, the leaderboard path (default `leaderboard.md`) and whether success means beating its first-ranked entry. Reuse an existing leaderboard rather than asking the user to identify a known incumbent.

Ask a question such as:

> What do you ultimately want to improve, and what decision or outcome should become better if the research succeeds?

Then probe for ambiguity only as needed. Distinguish a scientific discovery goal (e.g. find predictive signals) from a deployment goal (e.g. maximize returns after costs).

Write a one-sentence goal statement and ask the user to confirm it before proceeding if its interpretation is consequential.

### Phase 2 — Metric: what observable quantity represents the goal?

Identify a primary metric and any secondary metrics. For each metric, establish:
- Exact definition/formula and unit.
- Whether higher or lower is better.
- Evaluation population and time horizon.
- Aggregation method and relevant weighting.
- Baseline or comparator. For leaderboard-based optimization, read the first-ranked eligible entry and verify its source/version and supporting results. State the primary metric relative to this incumbent, rather than the original baseline.
- Minimum practically meaningful improvement.
- Known limitations or ways the metric can be gamed.

Ask:

> What observable quantity would convince you that the goal is improving? Is there an existing metric you trust, or should we define one?

Examples by domain:
- Language model: held-out log loss, bits per byte, task accuracy, exact-match/F1, latency, memory, cost per request.
- Classification/ranking: PR-AUC, ROC-AUC, precision/recall at a fixed threshold, NDCG, calibration.
- Forecasting: MAE/RMSE, log loss, directional accuracy, calibration, performance against a naive forecast.
- Quantitative finance: net-of-cost out-of-sample Sharpe, excess return, drawdown, turnover, capacity, benchmark-relative results.
- Systems: throughput, p95/p99 latency, error rate, memory, CPU/GPU use, cost per job.
- Scientific experiments: pre-registered primary endpoint, effect size, uncertainty interval, replication rate.

Do not recommend a single metric solely because it is easy to calculate. If objectives conflict, ask the user to prioritize them or define constraints/Pareto trade-offs.

### Phase 3 — Measurement and observability infrastructure

Determine whether the metric can actually be computed and audited.

Ask only relevant questions:
- What data, labels, logs, benchmark, or simulator are available?
- Where do they live, and how are they accessed?
- Is there an existing evaluation command, API, test suite, or backtesting engine?
- Can the evaluation be run repeatedly with deterministic or recorded conditions?
- Are timestamps, data versions, labels, and ground truth trustworthy?
- What is the runtime and compute cost per evaluation?
- What failures or missing data should invalidate a run?
- What is the required result file (path/name), and what format does it use (for example, `results.tsv`)?
- Does the result file capture every attempted trial, including rejected, invalid, and crashed runs—not only successful experiments?
- Can each result record include enough metadata to reproduce the trial?
- Can the evaluator compare directly against the leaderboard leader, or otherwise measure the agreed improvement relative to that leader under comparable conditions? If not, specify and authorize the required evaluator adaptation before freezing it for the campaign.

If necessary, ask a direct infrastructure question:

> Can we already compute this metric from a repeatable command or dataset? If yes, what command and output should the agent use? If not, we should build that measurement path before optimizing.

Classify the state as:
- **Ready:** reliable automated measurement exists.
- **Needs instrumentation:** metric is clear but measurement is not automated or auditable.
- **Needs data:** required data/labels/simulator are missing or inadequate.
- **Not yet measurable:** goal needs refinement before a metric can be defined.

Do not let the agent optimize against hand-entered, inconsistent, or unverifiable scores. Treat the result file as mandatory, not optional: define its path/name and schema before rendering `program.md`. If the file does not exist, specify how to create and initialize it before the first experiment.

### Leaderboard contract for ranked-candidate optimization

Use `leaderboard.md` to identify the current incumbent; the result file remains the source of truth for measured outcomes. The leaderboard should name the leader's ID, artifact path and immutable version (commit or source hash), ranking method, evaluation conditions, and references to supporting result records. Include uncertainty and scope limitations where ranking evidence is weak.

If an existing leaderboard is valid, use its rank 1 without rerunning selection each campaign. If absent or inconsistent, specify a bounded initialization or repair based on comparable logged evidence, or a selection protocol fixed before new measurements. Do not rank candidates solely from incomparable historical scores. Research candidates need not be deployed to be eligible if their evidence meets the declared ranking rule.

Freeze the leader's version and record the leaderboard snapshot/hash for each candidate's full validation chain. A screen result never changes rank 1. Only after all acceptance conditions pass, including required integration checks, promote the candidate and update the leader's version, previous incumbent and validation evidence. Preserve previous rankings and their original evaluation conditions; a direct-duel promotion score is not a tournament-average score. Rejected candidates may be logged separately without displacing the leader. Never rewrite immutable result records for promotion.

For tasks where ranking candidates is inapplicable, keep the user's actual objective and explicitly disable leaderboard mode with a reason; do not invent a model competition.

### Phase 4 — Experiment: what may the agent change?

Define the search space and operational boundaries:
- Allowed files, modules, parameters, features, architectures, algorithms, or configurations.
- Forbidden files and protected interfaces.
- Whether dependency changes, network access, data collection, or schema changes are allowed.
- Compute/time budget per trial and total budget.
- Experiment granularity: one hypothesis/change per trial or grouped changes.
- How the agent starts each trial: baseline commit or best-known commit.
- How changes are versioned, logged, retained, or reverted.
- Stop conditions and when human approval is required.

Ask:

> Which parts of the system should the agent be allowed to change, and which must remain fixed to keep experiments comparable?

Use a narrow search space initially. Expand it after the evaluation harness has demonstrated reliability.

### Phase 5 — Validation: is the improvement real?

Design a validation protocol appropriate to the domain. Establish:
- A baseline and a comparison method.
- Separate development/search data from validation and final test data.
- Leakage, contamination, survivorship, selection, and data-quality risks.
- Repeated runs or seeds where randomness matters.
- Uncertainty estimates or statistical tests when appropriate.
- Robustness checks across time periods, segments, regimes, distributions, hardware, or realistic operating conditions.
- Practical constraints such as latency, memory, cost, risk, interpretability, and maintainability.
- A confirmation budget for promising candidates.
- Criteria for accepting, rejecting, or escalating a result.

Ask:

> What evidence would be sufficient to believe an improvement is real and generalizes beyond the experiments used to discover it?

Avoid using the same holdout repeatedly to select candidates. For time-dependent problems, preserve temporal ordering. For finance, explicitly check point-in-time data, universe membership, execution assumptions, transaction costs, and survivorship/look-ahead bias. For ML, check leakage, split integrity, distribution shift, and task-relevant metrics.

If the user has no protocol, propose a minimal one and label assumptions explicitly.

### Phase 6 — Synthesize and confirm

Produce an **Autoresearch Specification** containing:

1. **Goal** — one sentence.
2. **Primary metric** — definition, unit, direction, baseline, and minimum meaningful improvement.
3. **Guardrails** — hard constraints and secondary metrics.
4. **Measurement** — data sources, evaluation command, outputs, and observability status.
5. **Experiment space** — allowed changes, protected components, and trial budget.
6. **Validation protocol** — split strategy, leakage controls, repeatability, robustness, and final confirmation.
7. **Acceptance/rejection rule** — explicit conditions for keeping or reverting a candidate.
8. **Required result file** — exact path/name, format, schema, initialization behavior, and append/update rules. This is the mandatory log of record for every experiment.
9. **Logging and reproducibility** — metadata to record for every run.
10. **Known risks and unresolved questions**.
11. **Leaderboard contract** — enabled or not (with reason), path, rank-1 selection and evidence, initialization, frozen incumbent/version, comparison method, and promotion rule. For ranked-candidate optimization, the goal must explicitly require beating rank 1.
12. **Next actions** — ordered implementation tasks.

Ask the user to approve the specification before rendering `program.md` or running experiments, especially when assumptions affect the objective, data integrity, cost, or safety.

## Minimum run-record schema

Recommend one machine-readable record per trial with, at minimum:

- `experiment_id`
- `timestamp`
- `parent_commit`
- `candidate_commit`
- comparator ID and immutable code/artifact version; leaderboard snapshot/version when leaderboard mode is enabled
- `hypothesis`
- `changed_files`
- `data_version`
- `split_or_evaluation_period`
- `seed`
- `command`
- `status`
- `primary_metric`
- `secondary_metrics`
- `runtime_seconds`
- `compute_or_cost`
- `constraint_violations`
- `decision` (`keep`, `revert`, `invalid`, or `needs_review`)
- `decision_reason`

Adapt the schema to the chosen file format, but do not silently omit required fields. Missing measurements should be represented explicitly, not treated as zero or silently omitted. For a tabular format, encode nested values consistently (for example, JSON strings in a TSV/CSV column) or use a structured format such as JSONL if appropriate.

The skill must establish the result file's exact path/name and format before rendering `program.md`. If unresolved, ask the user; do not silently assume a filename. `program.md` must name the result file and require the agent to append one record for every attempted experiment, including hypothesis, changed code/commit, metrics (or explicit missing values), runtime/cost, status, and keep/revert decision with rationale. Failed, invalid, and crashed attempts must also be recorded. The agent must not start another experiment until the prior attempt's result record has been written, including a failure record if the process crashes and a recovery mechanism is available. If the result file is absent, `program.md` must explain how to initialize it before the first trial.

## Rendering `program.md` from Jinja2

Use `templates/program.md.j2` as the canonical template.

1. Build a structured context from the approved Autoresearch Specification. Keep values as data; do not splice untrusted user content into executable shell commands.
2. Validate that all required values are present. At minimum, require the goal, primary metric and direction, evaluation procedure, allowed/protected change surface, trial budget or explicit budget policy, validation protocol, acceptance/rejection rule, result-file path/name/format/schema, and `leaderboard.enabled`. If enabled, require `leaderboard.path`, `leaderboard.ranking_rule`, `leaderboard.initialization`, `leaderboard.comparison_method`, and `leaderboard.promotion_rule`; if disabled, require `leaderboard.disabled_reason`. Check that the goal, primary metric, evaluator, baseline comparison, starting point and acceptance rules consistently target the leaderboard's leader. Do not hardcode a current model name as the permanent opponent.
3. Render the template with a Jinja2 environment configured with `StrictUndefined` so missing variables fail rather than silently render as empty strings. Autoescaping may be disabled for Markdown output, but values must be escaped or quoted appropriately when used in shell commands or structured data.
4. Write the rendered artifact to the requested `program.md` destination. Do not overwrite an existing user-authored file without explicit approval.
5. Inspect the rendered file. Confirm that it contains the required result-file logging contract, has no unresolved `{{ ... }}` or `{% ... %}` delimiters, and includes all required sections.
6. If a required field is unresolved, return to the interview instead of inventing a value or producing an execution-ready `program.md`.
7. Show the user the rendered `program.md` and identify any explicitly approved assumptions.

The template is a rendering aid, not a substitute for validation. Do not generate or run experiments solely because the template can be rendered.

## Decision rules

- If the goal is ambiguous, continue Phase 1; do not jump to metric selection.
- If ranked-candidate improvement is requested, set the target to rank 1 of the declared leaderboard and require full validation before promotion; use another comparator only when the user explicitly chooses it.
- If the goal is clear but the metric is weak, propose alternatives with trade-offs and ask the user to choose.
- If a metric is selected but not observable, make instrumentation/data access the next task.
- If the agent could exploit the metric, add constraints or change the evaluation protocol before proceeding.
- If validation is too weak to support the intended claim, distinguish exploratory results from confirmed results.
- If the required result file's path/name or format is unknown, resolve it before rendering `program.md`; never render `program.md` without explicit result-file logging instructions.
- If the user asks to start immediately, still establish the minimum viable goal, metric, measurement command/data, allowed change surface, and validation split before running experiments.
- Never claim that a strategy or model generalizes merely because it wins on the optimization metric.
- Never modify production systems, spend money, or access sensitive data without appropriate authorization.

## Interaction style

Be precise and concise. Ask one direct question at a time unless a compact grouped question clearly reduces friction. Explain why a question matters when it may not be obvious. Challenge objectives that are easy to game, statistically weak, or disconnected from the user's real goal. Offer concrete defaults, but keep the final choice with the user.

## Completion criterion

The setup is complete only when a competent coding agent could determine:
- what it is trying to improve,
- how to calculate the score,
- what it may change,
- how much each experiment may cost,
- what invalidates a run,
- how to compare a candidate to the incumbent (rank 1 of the leaderboard when enabled),
- how to verify, freeze and eventually replace that incumbent with auditable evidence,
- where every experiment result must be recorded,
- and what evidence is required before calling an improvement real.

If any of these remain unresolved, report the gap and do not represent the specification as ready for autonomous execution.
