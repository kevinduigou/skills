---
name: branch-review
description: Opinionated code review of the current git branch against master, focused on functional programming, immutability, hexagonal architecture, illegal-states-unrepresentable, and naming clarity. Use when the user asks to "review the branch", "review this branch", "code review the branch", or any phrasing that asks for a review of branch-level changes. Diffs the branch against an up-to-date origin/master and writes findings grouped by severity to Review.md at the repo root. For Meson repos, also reviews any changed entries under subprojects/ (vendored or submodules) and merges their findings into the same Review.md.
---

# Branch Review

Opinionated code review of the current branch versus `master`. Output goes to `Review.md` at the repo root — do NOT dump the full review into the chat.

## Workflow

1. **Refresh master**

   ```bash
   git fetch origin master
   ```

2. **Get the diff**

   ```bash
   git diff origin/master...HEAD
   ```

   Use `...` (three dots) so the diff is against the merge-base, not the current tip of master. If `origin/master` is missing, fall back to `git diff master...HEAD` after confirming the local master is current.

3. **List changed files** (helps prioritize what to read in full):

   ```bash
   git diff --name-status origin/master...HEAD
   ```

4. **Detect Meson subprojects and review changed ones.** If the repo is a Meson project (a `meson.build` at the root and a `subprojects/` directory), each entry under `subprojects/` is a separate codebase that must be reviewed independently when it has changes.

   - Check whether the project is a Meson repo:

     ```bash
     test -f meson.build && test -d subprojects && echo meson
     ```

   - If yes, list the subprojects that changed on this branch (each subproject may be a regular subdirectory or a git submodule):

     ```bash
     git diff --name-only origin/master...HEAD -- subprojects/ \
       | awk -F/ 'NF>=2 && $1=="subprojects" {print $2}' | sort -u
     ```

     Also include any submodules under `subprojects/` whose pointer moved:

     ```bash
     git diff --submodule=short origin/master...HEAD -- subprojects/
     ```

   - For every changed subproject, run a separate review pass:
     - If it is a submodule, `cd` into it and diff against the pointer recorded on `origin/master` (resolve with `git ls-tree origin/master -- subprojects/<name>` to get the old commit, then `git diff <old>...HEAD` inside the submodule).
     - If it is a vendored subdirectory, scope the diff with `git diff origin/master...HEAD -- subprojects/<name>/`.
     - Apply the same principles below to each subproject's diff.

   - The findings from each subproject are written into the **same** `Review.md` at the root repo, under a dedicated subproject section (see "Output format" — "Subproject reviews"). Do NOT write a separate `Review.md` inside each subproject.

5. **Read full files when context matters.** The diff alone is not enough to judge architecture or naming coherence — open changed files (and their neighbours) to verify dependency direction, ports/adapters placement, and naming consistency. Apply this to root-repo files and to each changed subproject.

6. **Apply the principles below** to flag findings. Be opinionated but precise — every finding cites a file:line and the principle it violates. For subproject findings, prefix the path with `subprojects/<name>/...` so it is unambiguous in the merged report.

7. **Write `Review.md`** at the repo root in the exact format under "Output format" below.

8. **Reply briefly** in chat: 1–2 sentences pointing the user to `Review.md` and naming the top blocker (if any), plus the list of subprojects reviewed (if any). Do not paste the full review.

## Review principles

Apply in this priority order. Higher-priority categories produce harder findings (Blocker / Major); lower-priority ones produce Minor / Nit findings unless they compound.

### Core (highest priority)

- **Functional Programming style** — prefer pure functions, expressions over statements, transformations over mutation.
- **Immutability first** — mutability only at the edge (I/O boundaries). Frozen dataclasses, `@final`, `__slots__` for domain objects.
- **Make illegal states unrepresentable** — factory methods (e.g. `try_create()`), validation before instantiation, no public constructors for constrained types, sum types over flag combinations.
- **Clear, PO-readable names** — a Product Owner should be able to read identifiers and understand intent. No abbreviations, no jargon. Domain terms match the ubiquitous language used in tickets.
- **Hexagonal Architecture coherence** — Domain → Application → Infrastructure → Interface. Dependency direction is sacred (domain never imports infrastructure). Ports live in application; adapters in infrastructure.
- **File size / readability** — split files that have grown too large to scan in one screen of focus.

### Logic & Design

- Single Responsibility — if the function name needs "and", split it.
- No boolean parameters — replace with an enum or two named functions.
- Exhaustive pattern matching — `match` / `switch` must cover every variant; never silently fall through.
- Parse, don't validate — transform unstructured input into typed domain objects at the boundary; do not re-validate inside the core.
- No primitive obsession — `UserId`, `Email`, `Amount` beat raw `str` / `int`.

### Correctness & Safety

- Null/None only at the edge — use `Option` / `Maybe` types internally.
- Errors are values — `Result` / `Either` over exceptions for expected failures. `try`/`except` only in the infrastructure layer.
- No silent failures — every error path handled explicitly, never swallowed.
- Totality — every function returns a value for every possible input.

### Testability

- Pure core, impure shell — business logic testable without mocks, I/O, or DB.
- No test logic in production code — no `if isTest`, no test-only branches.
- Tests document intent — names read like specifications, not like implementation steps.

### Structure & Architecture

- Dependency direction is sacred — domain importing infrastructure is a hard Blocker.
- No anemic domain models — logic lives with the data, not in `*Service` / `*Manager`.
- Ports are interfaces, adapters are implementations — never blur the two.
- Configuration at the edge — env vars injected at startup, not scattered through the code.

### Naming & Readability

- Name what it IS, not what it DOES (`userWithVerifiedEmail` > `processAndFilterUser`).
- Avoid negated booleans (`isActive` > `isNotDisabled`).
- Consistent ubiquitous language — the word in the ticket is the word in the code.
- No abbreviations (`doc` → `document`, `mgr` → rename the concept).

### Code smells to flag hard

- Any `Any` / untyped escape hatch.
- Mutation inside a pipeline or loop.
- Functions longer than ~20 lines.
- More than 2–3 levels of nesting.
- Comments that explain WHAT (only WHY is acceptable).

## Severity guide

- **Blocker** — violates a core principle in a way that breaks the architecture or correctness contract (e.g. domain importing infrastructure, illegal state representable, silent error swallow, mutable shared state). Must fix before merge.
- **Major** — clear violation that will hurt maintainability or clarity (boolean param, anemic model, primitive obsession on a domain concept, function 60 lines deep). Should fix before merge.
- **Minor** — readability or naming issues, small SRP violations, comments-explaining-what.
- **Nit** — style and cosmetic preferences.

When unsure, downgrade severity rather than overstate it. Only flag a Blocker if you can name the principle and point to the line.

## Output format

Write `Review.md` to the repo root with this exact structure:

```markdown
# Branch Review

**Branch:** `<current-branch>`
**Base:** `origin/master` (merge-base)
**Files changed:** <N> (<lines added>+/<lines removed>-)
**Subprojects reviewed:** <comma-separated list, or "none">

## Root repository

### Blockers

- **`path/to/file.py:42`** — *<principle violated>*
  - **Problem:** <one-sentence description>
  - **Fix:** <concrete suggestion>

### Major

- **`path/to/file.py:120`** — *<principle violated>*
  - **Problem:** ...
  - **Fix:** ...

### Minor

- **`path/to/file.py:88`** — *<principle violated>*
  - **Problem:** ...
  - **Fix:** ...

### Nits

- **`path/to/file.py:12`** — *<principle violated>* — <one-line note>

## Subproject reviews

> One section per changed subproject. Omit this whole section if no subprojects changed.

### `subprojects/<name>`

**Type:** <submodule | vendored>
**Diff range:** `<old-rev>...HEAD` (or `origin/master...HEAD -- subprojects/<name>/`)
**Files changed:** <N>

#### Blockers

- **`subprojects/<name>/path/to/file.py:42`** — *<principle violated>*
  - **Problem:** ...
  - **Fix:** ...

#### Major

- ...

#### Minor

- ...

#### Nits

- ...

## Summary

**What was good:**
- <bullet — keep this honest across root + subprojects; if nothing stands out, write "Nothing notable.">
- ...

**Top 3 things to fix (across root + subprojects):**
1. <highest-leverage fix — prefix subproject paths with `subprojects/<name>/`>
2. ...
3. ...
```

Rules for the output:

- Empty severity sections: write `_None._` rather than deleting the heading — the structure stays consistent across reviews.
- One finding per bullet; do not bundle multiple violations in one item.
- Cite `file:line` for every finding (use the line in HEAD, not in the diff hunk).
- Quote a short snippet (≤3 lines) only when needed to make the violation unambiguous.
- Suggested fixes are concrete (name a type, name a function split, name the layer to move to) — never "consider refactoring".

## Notes

- The current project's `CLAUDE.md` may already prescribe immutability rules, Result/Either usage, and layering. Read it if present and align findings with it — its rules are authoritative for this repo.
- Do not run linters / type-checkers / tests as part of this skill. The review is about design and naming; build-time checks are a separate concern.
- If the branch has no diff against `origin/master`, write a one-line `Review.md` saying so and stop.

## Project-specific exclusions

These patterns look like violations of the generic principles above but are part of the established workflow — do NOT flag them as findings.

- **Meson `.wrap` files with `revision = <branch-name>`.** In this project's release process, feature branches (e.g. `IRMADEV-XXXX`) intentionally point every changed `subprojects/*.wrap` at the matching feature branch on the vendored repo. The wraps are re-pinned to immutable SHAs by the release process at merge time, not by the branch author. Treat `revision = <ticket-name>` in a `.wrap` file as expected, not a Blocker.
- **`service_idocdb.wrap` with a `dvpt/` KB tarball URL.** Same reason — the `dvpt/` bucket is the intended location during feature-branch work; the URL is repointed to a stable location at release time.
