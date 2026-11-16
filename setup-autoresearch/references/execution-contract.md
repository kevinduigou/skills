# Execution contract

Defines the structured render context for `templates/program.md.j2`, the result-ledger requirements, and the leaderboard rules. Every field below is required unless marked optional or conditional. Strings must be nonempty; unknown decision-critical values block rendering and must not be hidden in prerequisites.

## 1. Render context

### approval

| Field | Type | Notes |
|---|---|---|
| `spec_version` | string | Version of the approved Autoresearch Specification. |
| `spec_hash` | string | Hash of the approved specification text or context. |
| `evidence` | string | Where and how the user approved (message, timestamp, reviewer). |
| `assumptions` | list[string] | Approved assumptions. May be empty. |

### readiness

| Field | Type | Notes |
|---|---|---|
| `state` | enum | `approved_blocked` or `ready_for_authorization`. `incomplete` specifications are never rendered. |
| `measurement_status` | enum | `ready`, `needs_instrumentation`, `needs_data`, `not_yet_measurable`. |
| `execution_authorization` | string | Who authorizes execution and whether it has been granted. Rendering never grants it. |
| `prerequisites` | list[string] | Must be nonempty when `state` is `approved_blocked`. |

Consistency: `ready_for_authorization` requires `measurement_status: ready`. Any other measurement status implies `approved_blocked`.

### goal

String: objective, scope, exclusions, and intended claim.

### leaderboard

| Field | Type | Notes |
|---|---|---|
| `enabled` | bool | |
| `path` | string | Conditional: required when enabled (default `leaderboard.md`). |
| `ranking_rule` | string | Conditional: ranking and eligibility rules. |
| `incumbent_evidence` | string | Conditional: frozen leader identity, artifact path, immutable version, supporting result records. |
| `initialization` | string | Conditional: how the leaderboard is initialized or repaired before freezing. |
| `comparison_method` | string | Conditional: how candidates are compared with the frozen leader. |
| `promotion_rule` | string | Conditional: what evidence promotes a candidate. |
| `disabled_reason` | string | Conditional: required when disabled. |

### primary_metric

`name`, `definition`, `unit`, `direction` (`maximize` or `minimize`), `population_aggregation` (population, period, aggregation, missing-value treatment), `comparator`, `minimum_improvement` (state absolute or relative), `uncertainty_rule`, `gaming_controls`. All strings.

### secondary_metrics

List of objects with `name`, `definition`, `unit`, `direction`, `role` (`diagnostic` or `constraint`; diagnostic metrics never determine acceptance alone), `procedure`. May be empty.

### constraints

list[string]: hard constraints and invalidation conditions. Must be nonempty.

### evaluation

`data_source`, `data_versioning`, `procedure` (evaluator command or entry point), `outputs_parser`, `split`, `environment`, `comparator_procedure`, `invalidation`, `preflight` (authorized preflight or `none`), `frozen_components`. All strings.

### experiment

| Field | Type |
|---|---|
| `allowed_changes` | list[string], nonempty |
| `protected_changes` | list[string], nonempty |
| `starting_point` | string: artifact plus immutable version |
| `granularity` | string |
| `versioning_rollback` | string |
| `network_dependency_data_policy` | string |
| `per_trial_budget` | string |
| `maximum_attempts` | integer or string |
| `total_budget` | string |
| `confirmation_reserve` | string |
| `budget_accounting` | string: must cover failed, invalid, retried, preflight, and confirmation attempts |
| `concurrency` | string |
| `stop_escalation` | string |

### result_file

`path` (exact path), `format`, `schema_description` (typed fields and nullability, see section 2), `initialization`, `durable_write_policy`, `start_manifest_recovery`, `adjudication_policy`. All strings.

### validation

`stages` (search, confirmation, final evaluation, and progression between them), `leakage_controls`, `repeatability`, `uncertainty_selection`, `robustness_integration`, `holdout_access`, `final_confirmation`. All strings.

### decision_rules, reporting

Strings. `decision_rules` must define `advance`, `keep`, `accept`, `reject`, `invalid`, and `needs_review`.

### next_actions

list[string], ordered. May be empty only when `state` is `ready_for_authorization`.

## 2. Result ledger

The result file is the authoritative outcome ledger. Dashboards and leaderboards are derived views.

Every record must have at least:

- `experiment_id` (unique), `retry_of` (nullable), `candidate_id`, `chain_id`
- `started_at`, `finished_at` (nullable)
- `hypothesis`, `changed_files`, `parent_version`, `candidate_version`
- `comparator_id`, `comparator_version`
- `data_version`, `split`, `seeds`, `procedure`, `environment`, `evaluator_version`
- `metrics` (nullable values; never zero-filled), `uncertainty`
- `evidence_refs`, `runtime`, `cost`
- `constraint_violations`, `errors`
- `stage` (`search`, `confirmation`, `final`)
- `outcome`, one of `advance`, `keep`, `accept`, `reject`, `invalid`, `failed`, `timeout`, `crashed`, `unknown`, `needs_review`
- `rationale`
- When the leaderboard is enabled: `incumbent_path`, `incumbent_version`, `leaderboard_snapshot_hash`

Rules:

1. **Start manifest first.** Durably write a start record before evaluation begins.
2. **One terminal record per attempt.** Every attempted trial gets exactly one terminal outcome, including failures.
3. **Atomic, append-only writes.** Write to a temp file, then fsync and rename, or use an append under a lock. Never truncate or rewrite historical records. Later adjudication or promotion is a new linked record.
4. **Deduplicate** by `experiment_id`. Retries get new IDs linked through `retry_of`.
5. **Crash recovery.** Before new work, reconcile every start manifest that has no terminal record. Recover from durable evidence, or record null metrics with `unknown` or `needs_review`.
6. **Stop if safe logging is unavailable.**

## 3. Leaderboard

- Freeze the rank-1 eligible entry (identity, artifact, immutable version) and the leaderboard snapshot hash before the campaign.
- Only results produced under a comparable protocol (same evaluator, data, split, and conditions) are eligible for ranking.
- Screens and search results never change rank 1. Promote only after full acceptance and durable logging.
- Recheck the snapshot hash immediately before an atomic, locked update. Stop on a concurrent change.
- Preserve previous leaders, their validation IDs, and their original ranking conditions.

## 4. Validation before writing program.md

- Render with Jinja2 `StrictUndefined`. Values are data and are never recursively evaluated.
- Check for missing headings, leftover `{{` or `{%`, contradictory readiness states, and mismatched result or leaderboard paths.
- Record the template hash and the context or specification hash.
- Do not overwrite an existing user-authored file without authorization.
