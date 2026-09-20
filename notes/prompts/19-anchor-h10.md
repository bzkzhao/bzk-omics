# PROMPT 19 — the anchor under its named test: gate G, check A, and H10

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.

**Base.** Fetch, then fast-forward to `origin/main`. It must be a fast-forward
of `2eb8445` whose only changes are:
- `walk/PREREG-PXD018299-H10.md`, added, with sha256
  `68147bea38fc04f1d2eaf0fa3279d21d7ba643462103fc233b4ed3ce33ec81d8`;
- anything under `notes/prompts/`.

Verify with `git diff --stat 2eb8445..origin/main` and the hash. Otherwise report
and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`. **Never force-push, and never amend or rebase a pushed
commit. Do not write, retype or commit any file under `notes/prompts/`.** This
container has no raw store. **You build and test; bzk runs the instrument.**

**Read `walk/PREREG-PXD018299-H10.md` in full. It is the specification. Its §7
expectations (X1–X8) are not inputs, and nothing in the code may read or
depend on them.** Also read:
- `HYPOTHESIS.md` v8's H10 amendment;
- `bzk/stats/perseus_s0.py` and `tests/test_perseus_s0.py`;
- `bzk/sources/pxd026748_reconstruction.py`, for the shotgun pipeline and the
  gate pattern to reuse;
- `bzk/sources/pxd018299_differential.py`, for the anchor's columns;
- `tests/fixtures/pxd018299_published_cascade.json`, for `deposit_id`.

Where the pre-registration is silent, choose, record the choice in the module
and the report, and never choose by outcome.


## Part A — the two missing scheme variants in `perseus_s0`

Add `random_excluding_trivial` and `exhaustive_excluding_trivial`.
- The **trivial relabellings** are the identity and the mirror, the mirror
  being group A given exactly B's columns. The mirror exists only when
  n_A = n_B, and then it is excluded too.
- `random_excluding_trivial` draws until it has `randomisations` non-trivial
  draws. Draws are with replacement among the non-trivial relabellings.
- Update the docstring to explain why these variants exist. **Under `joint`,
  the mirror reproduces every observed |d| exactly, so keeping it floors every
  q at 1 / (number of relabellings).** At 3 against 3 that is 1/19. This was
  found on a simulated 1,375-row matrix, where `joint` with the mirror called
  none of 200 +4 SD effects at FDR 0.01, against 69 for `per_side` exhaustive.
- Correct the comment in `tests/test_perseus_s0.py` P1 that generalises the
  1/19 floor to *"cannot support an FDR of 0.01"*. The floor comes from the
  mirror, not from the number of relabellings.
- **Tests:**
  - (i) Under `joint` with the mirror excluded, a 3-against-3 matrix with many
    strong effects reaches q ≤ 0.01. Mutation: keep the mirror, which must fail.
  - (ii) The exhaustive-excluding-trivial scheme runs 18 relabellings at 3
    against 3.
  - (iii) Randomly drawn relabellings are never trivial.


## Part B — `bzk/sources/pxd018299_h10.py`

Run as `python -m bzk.sources.pxd018299_h10`, with the same IO/arithmetic split
and injectable paths as turns 16 and 17.

**B1. Gate G, as §4 specifies.** Reuse turn 16's shotgun pipeline functions and
Table 3 reader, with no copies. Grouping is WT against *ISG15*−/− across all 12
shotgun samples.
- For each of the 8 variants, at the default cell over seeds 0–19: compute
  precision and recall of Table 3's `+` among complete-case proteins, using a
  majority-of-seeds call.
- Report the number of complete-case `+` proteins, and set the weakly
  informative flag if it is below 30.

**B2. The anchor matrix, as §§2–3 specify.**
- The population is the site table minus reverse decoys. Contaminants,
  localisation below 0.75 and refused rows are all **kept**.
- **The intensity and normalisation check:** S1 against log2 of the summed
  columns and of the `___1` columns, with and without per-column median
  subtraction, at the 99% criterion over deposit-measured cells. The rule order
  and the fallbacks are as §3 states.
- **The valid-value rule:** the strictest candidate retaining all 798
  published claims' rows. Report each candidate's count.
- **The published-draw estimates:** for S1's cells where the deposit value is
  missing, report per WT column the mean and SD of the published values, and
  the implied downshift and width under both scopes.

S1 is `SUPP_DATA_1` (`bzk/sources/protein_groups.py`), read through its
declaration. Locate its header by content. If its column names differ from what
you expect, stop with the header printed. **Do not guess them.**

**B3. Check A.** For each variant that passed G: does any claim reach
q ≤ 0.01 and d > 0 on the anchor at the default cell, under any seed?

**B4. The primary variant and the family.**
- Take the primary variant by §4's rule. If no variant is admitted, **stop
  after writing G and A**, with `anchor_run: false`.
- Otherwise run the 360 paired members (imputation seed k and permutation seed
  k) under the primary variant, and under each other admitted variant as a
  secondary.

**B5. Readouts A to D, as §6 specifies, plus H10's verdict computed
mechanically.**
- Recurs at ≥ 5%, absent at ≤ 1%, with a 1e-9 slack at the boundaries as in
  turn 17.
- The permutation-fixed and imputation-fixed isolations.
- The 14 named targets, taken from the existing targets fixture's symbol
  mapping.

**B6. The author configuration.** The pre-registration's author-parameter rule
(its opening section and §6 A) is implemented as follows.
- If `walk/PXD018299-author-parameters.json` exists, read it and validate it.
  - **Accepted keys:** `width_sd`, `downshift_sd`, `scope`, `seed`,
    `randomisations` and `scheme`. Any other key refuses by name.
  - **Required keys:** `source` and `date_received`.
  - Any parameter it omits takes the registered default.
- Run that configuration's readout A, and record whether the file was tracked
  in git at the run's commit (`git ls-files --error-unmatch`).
- If it was tracked, the author configuration is readout A's **primary** and
  the default cell is reported beside it. If it was untracked, or absent, the
  default cell is primary.
- **H10's verdict never reads this file.**
- Define the file's schema in the module docstring, and add a short example
  under `notes/` (not `walk/`) with placeholder values. **Do not create
  `walk/PXD018299-author-parameters.json`.**

**Output:** `tests/fixtures/pxd018299_h10.json`.
- It carries the header keys and every source's hash.
- It keeps per-claim support counts per member for the primary variant, or a
  compact equivalent, and says which it stores.
- It holds all of G's and A's figures.

**Performance.** The gate runs 8 variants × 20 seeds × 250 permutations over
2,438 proteins, and the family runs 360 members × 250 permutations over the
anchor matrix. Vectorise the permutation null over rows. Report the measured
runtime of a scaled-down synthetic run, and estimate the real one.


## Tests — `tests/test_pxd018299_h10.py`

Offline, synthetic data. Each test must be seen to fail before it passes, and
the report gives each mutation and its failure message.

- **The normalisation and column check picks per the rule order,** including
  the `undetermined` fallback.
- **The valid-value rule is the strictest one that retains every published
  row.** Mutation: take the loosest.
- **No variant admitted means no anchor run.** Mutation: run anyway.
- **The primary variant is chosen by G's F1, with ties to the earlier
  variant.**
- **The verdict at the boundaries:** 5% and 1% exactly, and a value just inside
  each.
- **The paired seeds:** member k uses imputation seed k and permutation seed k;
  the two isolations hold the other seed at 0.
- **Imputed cells are identified by deposit missingness, not by value.**
  Mutation: identify them by a value cut-off.
- **The author configuration:**
  - a tracked file makes it readout A's primary, and an untracked file does
    not;
  - an unknown key refuses;
  - H10's verdict is identical with and without the file.

  Mutation: let the verdict read the author configuration.


## Registered expectations for this turn

E1. The suite is 805 passed and 14 skipped at base (measured at `2eb8445` in a
    container with no raw store), plus the new tests.
E2. Only `tests/test_perseus_s0.py`'s P1 comment and the classifications in the
    tautology sweep may change among existing tests. Name every change. Do not
    touch the floor.


## Task

1. Verify the base, and read the listed documents.
2. Write Parts A and B and their tests.
3. Run E1–E2 and every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit Part A (`stats:`), then Part B (`sources:`). Push, fast-forward only.
5. Write `notes/reports/19-anchor-h10-build-report.md` and commit it alone.
   Push.


## Out of scope

- Any real-data run.
- Changing the pre-registration.
- The third deposit.
- `ARCHITECTURE.md` §4 and ADR-0015.
- The tautology floor.
- `notes/prompts/`.


## Report

- The base check.
- Every choice made where the pre-registration was silent, with its reason.
- Each test, with its mutation and failure message.
- The output's shape.
- The runtime estimate.
- E1–E2, each held or missed.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- What this turn does NOT cover.
- Commit SHAs and the push range, stating every push was a fast-forward.
