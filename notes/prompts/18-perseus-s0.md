# PROMPT 18 — implement `perseus_s0` (the SAM-style test with permutation FDR)

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.

**Base.** Fetch, then fast-forward to `origin/main`. It must be a fast-forward of
`5a7f699` whose only changes are:
- `HYPOTHESIS.md`, now v8, with sha256
  `24d732523009098e5224b97d905a0544673ba7543af629e4eeb92c9b7c5709e3`;
- anything under `notes/prompts/`.

Verify with `git diff --stat 5a7f699..origin/main` and the hash. Otherwise report
and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`. **Never force-push, and never amend or rebase a pushed
commit. Do not write, retype or commit any file under `notes/prompts/`.** **No
data run this turn**, on any deposit.


## Why this turn exists

`ARCHITECTURE.md` §4 names `perseus_s0` the registry's **default and required**
test, and `bzk/stats/tests.py` records it as unwritten. `ROADMAP.md` moved it to
v0.2 on 2026-08-11 because *"the `s0` and FDR parameter values are not yet
known"*.

For `PXD018299` they are now known from the publication itself:
- the paper's Methods (PMC7884788, *Data analysis*) name *Perseus (v1.6.0.2) ...
  a t-test with permutation FDR = 0.01 ... and s0 = 0.1*;
- the Fig. 2 legend applies these values to all the paper's proteomic analyses.

`HYPOTHESIS.md` v8 amends H10 to use exactly this test. **The randomisation count
is still unstated.** `ONTOLOGY.md` l.155 makes it mandatory beside `s0`, so it
stays a required, declared parameter, and nothing here may default it silently.

Read these first:
- `HYPOTHESIS.md` v8 §0 and the H10 v8 amendment;
- `ARCHITECTURE.md` §4;
- `ONTOLOGY.md` l.155–175;
- `ROADMAP.md` l.73 and l.91–98;
- ADR-0015 and ADR-0017;
- `bzk/stats/tests.py`.


## Part A — `perseus_s0` in `bzk/stats/`

**The statistic** (Tusher et al.'s SAM form, as §4 describes it). For each row,
`d = (mean_A − mean_B) / (s + s0)`, where `s` is the pooled (Student)
standard error. Reuse `_moments`; do not write a second copy of the variance
arithmetic.

**The null.** Permutations of the column labels that preserve both group sizes.
In each permutation, `d` is computed for every row.

**The FDR.**
- At a threshold `t`, FDR(t) is the mean over permutations of #{null |d| ≥ t},
  divided by #{observed |d| ≥ t}.
- Each row's q-value is the smallest FDR over the thresholds that would still
  call it: `t ≤ |d_i|`, restricted to the observed `|d|` values. This makes q
  monotone.
- A row is significant at level α if `q ≤ α`.
- Direction is reported by the sign of the mean difference.

**Required parameters, with no defaults:** `s0`, `alpha`, `randomisations` and
`seed`. The permutation generator is `numpy.random.default_rng(seed)`.

**Two implementation questions the methods do not settle.** Implement both
answers to each, as named variants. That gives four combinations; H10's gate
will choose among them on published output, exactly as PC2 chose a t-test
variant. **Do not choose here.**
- **Sidedness.**
  - `joint`: one FDR over |d|, both directions together.
  - `per_side`: separate FDRs for positive and negative `d`, using one-sided
    counts.
- **The permutation scheme.**
  - `random`: `randomisations` independent draws, where repeats are allowed.
  - `exhaustive_when_small`: when the number of distinct relabellings,
    C(n_A + n_B, n_A), is at most `randomisations`, use all of them once,
    excluding the identity. Otherwise fall back to `random`.

  Record which scheme actually ran. **Name the fact the scheme exists for in the
  docstring:** at 3 against 3 there are only 20 relabellings.

**The output** is per row: `d`, the mean difference, `q`, whether it is
significant, and the direction. It also reports the variant, the scheme that
ran, the randomisation count used, and the seed.

**Registration.** Add `perseus_s0` to the registry `TESTS` **only if** §4's
table describes what you built. It does (a SAM-style modified t with `s0`
curvature and permutation FDR), so register it. Record `s0` and the
randomisation count in the parameters the registry passes on, as `ONTOLOGY.md`
l.155 requires. If anything you build differs from §4, stop and report instead
of registering.

**Scope record.** Add one dated note to `ROADMAP.md` at l.73's entry. It should
say that the dependency's `s0` and FDR values are published for `PXD018299`, that
the randomisation count remains unstated and is declared per analysis, and that
the entry is implemented in this turn. **Do not rewrite the entry's history.**
bzk may revise the note.


## Tests — `tests/test_perseus_s0.py`

Each test must be seen to fail before it passes. Report each mutation and its
failure message.

P1. **A hand-computed case.** On a tiny matrix (for example 6 rows, 3 against
    3, with all 20 relabellings enumerable), compute the `d` values, the null
    counts, FDR(t) and the q-values by hand in the test, and assert the module's
    values exactly.
P2. **s0 bites.** A row with a small mean difference and a tiny standard error
    is significant at `s0 = 0` and not at `s0 = 1`. Mutation: ignore `s0`.
P3. **q is monotone** in |d| under `joint`. Mutation: return the raw FDR(|d|).
P4. **The seed is honoured.** The same seed gives identical q-values; a
    different seed under `random` gives a different null.
P5. **The exhaustive scheme** uses exactly 19 non-identity relabellings at 3
    against 3 when `randomisations ≥ 19`, and falls back to `random` at 6
    against 6 with `randomisations = 250` (C(12,6) = 924 > 250). Mutation:
    include the identity.
P6. **`per_side` differs from `joint`** on a constructed asymmetric case.
P7. **No silent defaults.** Calling without `randomisations` or `seed` fails
    loudly.
P8. **The registry entry** carries `s0` and the randomisation count in its
    parameters, and `welch_t` is unchanged.


## Registered expectations

E1. Suite = 793 passed and 14 skipped at base (measured at `5a7f699` in a
    container with no raw store; v8 changes no code), plus the new tests.
E2. No existing test changes, beyond classifications in the tautology sweep,
    which must be named. Do not touch the sweep's floor.


## Task

1. Verify the base, and read the listed documents.
2. Write Part A, then P1–P8.
3. Run E1–E2 and every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit the code and tests (`stats:`), then the `ROADMAP.md` note as its own
   commit (`docs:`). Push, fast-forward only.
5. Write `notes/reports/18-perseus-s0-report.md` and commit it alone. Push.


## Out of scope

- Any data run.
- The H10 pre-registration and its gate thresholds.
- The anchor pipeline.
- Amending `ARCHITECTURE.md` §4 or ADR-0015.
- The tautology floor.
- `notes/prompts/`.


## Report

- The base check.
- The algorithm as implemented, with every choice the brief left open.
- P1–P8, each with its mutation and failure message.
- E1–E2, each held or missed.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- What this turn does NOT cover.
- Commit SHAs and the push range, stating every push was a fast-forward.
