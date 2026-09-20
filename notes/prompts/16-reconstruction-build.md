# PROMPT 16 — build the PXD026748 reconstruction (the D5 / H9s instrument)

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.

**Base.** Fetch, then fast-forward to `origin/main`. It must be `d3917c6`, or a
fast-forward of it whose only additions are under `notes/prompts/`. Otherwise
report and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`. **Never force-push, and never amend or rebase a pushed
commit. Do not write, retype or commit any file under `notes/prompts/`.** This
container has no raw store. As in turns 13 and 15, **you build and test; bzk
runs the instrument on his machine.**

**Read `walk/PREREG-PXD026748-reconstruction.md` in full before writing
anything.** Unlike turn 15's pre-registration, this one is the **specification**:
- the pipeline, in order;
- the positive-control gate;
- the family's grid and seeds;
- the readouts;
- H9s's verdict rule.

**Implement it exactly.** Where it is silent, choose, record the choice in the
module and in the report, and never choose by looking at an outcome. Its
registered expectations (R1–R5, and the JUDGED thresholds of PC1–PC3) are
**not** inputs. Nothing in the code may read or depend on them.


## Part A — `bzk/stats/anova.py`: a balanced two-way ANOVA with interaction

- It is vectorised over rows: a matrix of rows × samples, plus two factor labels
  per sample. For each row it returns SS, df, F and P for factor A, factor B and
  A×B, plus the residual SS and df.
- It is written from the sums of squares for a balanced design, following
  `bzk/stats/tests.py`'s convention of working from the definition. The P value
  comes from `scipy.stats.f.sf`.
- **It refuses** any missing value and any unbalanced design, with a message.
  After imputation every cell of the design is full, and anything else is a bug
  upstream.

**The validation, which the pre-registration requires.**
- **A1, a published worked example.** R's `ToothGrowth` dataset, fetched from
  `https://raw.githubusercontent.com/vincentarelbundock/Rdatasets/master/csv/datasets/ToothGrowth.csv`.
  Its sha256 must be
  `b35e084a98731429169eb9b216c9b904e8b9ea127707b741bb8fc146354c26fe`. Commit it as
  `tests/fixtures/toothgrowth.csv`, with its provenance in a README line or the
  test's docstring. If you cannot fetch it, stop and report.
  - The design is `len ~ supp * factor(dose)`, 2 × 3 with n = 10, balanced.
  - The published answer is R's `aov` table. Assert to its printed precision:

    | term | SS | df | F | P |
    |---|---|---|---|---|
    | supp | 205.35 | 1 | 15.572 | 0.000231 |
    | dose | 2426.43 | 2 | 92.000 | < 2e-16 |
    | supp:dose | 108.32 | 2 | 4.107 | 0.0219 |
    | residuals | 712.11 | 54 | | |
- **A2, an independent computation.** On random balanced 2 × 2 × 3 data, compare
  with an F test from nested least-squares models: full minus reduced residual
  sum of squares via `numpy.linalg.lstsq`. Assert agreement to 1e-9.

Each test must be seen to fail before it passes.


## Part B — `bzk/stats/tests.py`: the t-test variants the gate may choose among

`welch_t` exists. Add a Student (pooled-variance) two-sample t, and an S0
modification in the sense of Tusher et al. (SAM): the statistic divides the
difference in means by (standard error + S0).

That gives the registered set of four:
- {Student, Welch}
- × {P from the unmodified statistic, P from the S0-modified statistic, using
  the same df}

with S0 = 1. Each variant is its own named function. Test each against a
hand-computable case, and test Student's against `scipy.stats.ttest_ind` with
`equal_var=True`.


## Part C — `bzk/sources/pxd026748_reconstruction.py`: the instrument

Run as `python -m bzk.sources.pxd026748_reconstruction`. **Split the IO from the
arithmetic, as turns 13 and 15 did**, with injectable `home`, `fixtures_dir` and
record/supplement paths.

**C1, the shotgun positive controls**, using the pre-registration's shotgun
pipeline:
- the input is the raw `proteinGroups.txt`, `LFQ intensity {label}` for the 12
  labels in `curation_PXD026748_shotgun.json`;
- remove reverse sequences, contaminants and proteins only identified by site;
- log2, per-sample median subtraction, and the valid-value filter.

Then compute:
- **PC0:** the number of proteins passing.
- **The join to Table 3:** Table 3's `Uniprot ID` equals the **first entry** of
  the protein group's `Majority protein IDs`, split with the adapter's existing
  `_split`. Report unmatched and ambiguous rows as counts, and record this rule
  in the module. Table 3's IDs are single and unique (measured by the reviewer).
- **Complete-case proteins:** no missing value among the 12, after the filter.
- **PC1:** the log2(WT/KO) difference of group means. **PC2:** −log10 P, under
  each of the four t variants.
- **PC3:** the two-way ANOVA (Part A) membership at P < 0.01 on any term,
  compared with Table 2's membership. **Read Table 2's IDs from the workbook at
  run time, and never from a constant.** The pre-registration records 600 at
  `:65`; that figure is read from the supplement, not predicted, and the run
  reports the count it actually reads beside it.

**The gate is computed exactly as registered.**
- PC0 must equal 2,438.
- PC1, PC2 and PC3 must meet their thresholds, where PC2 passes if at least one
  of the four variants passes.
- The chosen variant is the one passing with the most proteins within
  tolerance. Report every variant's figure.

**If the gate fails, write the control results and stop.** The GG arm must not
run. `main()` exits non-zero, and the fixture records the gate's figures and
`gg_run: false`.

**C2, the GG family, which runs only if the gate passes.**
- **Population:** the GG site table after the adapter's `_filter`, 2,187 rows.
  This is the paper's matrix, and **it includes rows the platform refused at
  ingestion**.
- **Input:** summed `Intensity {label}` for the 12 labels in
  `curation_PXD026748.json`.
- **Pipeline:** log2 (zero or blank becomes missing), per-sample median
  subtraction, the valid-value filter, then imputation with
  `bzk/stats/imputation.py`'s `downshifted_normal`.
- **For each of the 360 members** (width_sd ∈ {0.2, 0.3, 0.4}, downshift_sd ∈
  {1.6, 1.8, 2.0}, scope ∈ {`per_sample`, `whole_matrix`}, seeds 0–19), impute
  and run Part A's ANOVA (genotype × treatment). Record min(P) per row.
- **Claims:** the 288 rows reaching the test in
  `tests/fixtures/pxd026748_published_cascade.json`, keyed by their
  `deposit_id`. For each claim, record:
  - the count of the 360 members supporting it, at both P < 0.01 and P ≤ 0.001;
  - its median min(P) in the default cell (0.3, 1.8, `per_sample`).
- **The three categories, exactly as the pre-registration defines them
  (`:134–136`).** They partition each claim by its support count over all 360
  members, and they are not thresholds on a majority:
  - **durable** = supported in **all 360**;
  - **underdetermined** = supported in some members, but not all;
  - **unsupported** = supported in **none**.
- **Readouts, all exactly as registered:**
  - durable, underdetermined and unsupported counts, at both thresholds;
  - the same, by cluster;
  - the default cell alone;
  - the threshold-consistency count;
  - the whole-table supported count in the default cell;
  - the one multiplicity-flagged claim, reported individually;
  - **H9s's verdict, computed mechanically, in the registered fraction form
    (`:156–160`).** Let E be the exposure the code measures from the cascade
    fixture.
    - **Weakens D5:** durable ≥ 95% of E.
    - **Extends D5 to imputation alone:** underdetermined ≥ 5% of E.
    - **Neither:** any other composition. It is reported as found, and it
      decides nothing.

    Compute the thresholds from E, never from constants. At E = 288 they are
    274 and 15, which is the registered instance, so report E beside the
    verdict.

**Output:** `tests/fixtures/pxd026748_reconstruction.json`, with the header keys
earlier fixtures use (`generated_by`, and `generated_under` with commit, clean
tree and date), both sources' hashes, the gate block, and the family block. Keep
the raw per-claim data: 288 × 360 min(P) values, or a compact equivalent, so the
reviewer can recompute any readout. Say which you stored.


## Tests for Part C — `tests/test_pxd026748_reconstruction.py`

Offline, on synthetic data. Each test must be seen to fail before it passes.
Report each mutation and its failure message.

- **The gate blocks the GG arm.** A failing positive control means no GG
  computation and no family block. Mutation: run GG regardless.
- **The pipeline order matters and is followed.** Build a case where normalising
  after filtering gives a different result from normalising before it, and
  assert the registered order.
- **Refused rows stay in the population.** A row absent from the emitted
  observations still contributes to the per-sample medians.
- **The verdict is mechanical, and in the fraction form.**
  - At E = 288, synthetic counts at durable 274 / underdetermined 14 give
    *weakens D5*, and at 273 / 15 give *extends D5 to imputation alone*.
  - At a different E, for example 200, the thresholds move to 190 and 10.
  - Mutation: hard-code 274 and 15. The different-E case must then fail.
- **The seed is honoured.** Two runs with the same member are identical, and a
  different seed differs.


## Registered expectations for this turn

E1. Suite = 745 passed and 14 skipped, plus the new tests. That base figure was
    measured by the reviewer at `d3917c6` in a container like this one, with no
    raw store, and the raw-store tests account for the skips. Report the split,
    and if your base differs, say why before adding anything.
E2. No existing test changes, and no id pin moves.
E3. A1's numbers match R's published table to the precision given above.


## Task

1. Verify the base, and read the pre-registration.
2. Write Parts A–C and their tests.
3. Run E1–E3 and every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit in three commits, pushing fast-forward only: Part A (`stats:`), Part B
   (`stats:`), then Part C (`sources:`).
5. Write `notes/reports/16-reconstruction-build-report.md` and commit it alone.
   Push.


## Out of scope

- Running anything on real data.
- The optional imputation-calibration analysis the pre-registration excludes.
- Any change to the pre-registration.
- The B-store defect, the `_split` home, and the anchor's `_commit()`.
- `notes/prompts/`.


## Report

- The base check.
- Every choice made where the pre-registration was silent, with its reason.
- A1 and A2, with the numbers.
- Each test, with its mutation and failure message.
- The output's shape.
- E1–E3, each held or missed.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- What this turn does NOT cover.
- Commit SHAs and the push range, stating every push was a fast-forward.
