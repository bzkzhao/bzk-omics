# Prompt 34 — Build the PXD032267 gate instrument

**Repository:** `main` at the commit adding this prompt.

**What this builds.** The instrument that `walk/PREREG-PXD032267-gate.md` registers:
- a validated Tukey HSD;
- the gate (input check, then five test variants);
- readouts A–D.

All of it is tested on synthetic inputs only. **No deposit bytes exist in the
container, and none are fetched here.** The real run happens later, on bzk's
Mac, under commands the reviewer writes after this turn's report.

**Governing:**
- `walk/PREREG-PXD032267-gate.md`, in full. Every threshold, variant, grid
  value and readout definition comes from it. Where this prompt and the
  pre-registration disagree, **the pre-registration wins**, and the
  disagreement is reported.
- `walk/walk_PXD032267.json` § `deposit_read`, for the published values and
  the facts the pinning check compares against.
- `CLAUDE.md`'s four-point close.

**Settled ground.**
- The pre-registration is committed (`96da102`) and is not edited.
- The R reference is committed before this prompt:
  `tests/fixtures/r_tukey_reference.csv`, produced on bzk's Mac by
  `notes/scripts/tukey_reference.R`. It is the oracle for §2.1. **Do not
  regenerate it, edit it, or produce it another way.** Its independence from
  this session is the point.
- The template for an instrument of this kind is `bzk/sources/pxd018299_h10.py`:
  constants transcribed from a registration, a fixture writer, and a `main` the
  container never runs.

**Edits are limited to:**
- `bzk/stats/tukey.py` (new);
- `bzk/sources/pxd032267_gate.py` (new);
- `bzk/sources/pride.py`: two `DepositFile` declarations, with
  `expected_content_hash=None`;
- `tests/`.

There are no ADR, `ONTOLOGY.md`, curation record, `ROADMAP.md`, `HANDOFF.md`
or `HYPOTHESIS.md` edits, and nothing under `walk/`. No graph, schema or DDL
change: this instrument writes a fixture and nothing else.

The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **Repository state.**
   - Run `git log --oneline -3` and `git status --short`. HEAD should be this
     prompt's commit, with a clean tree.
   - Open-of-turn checks: `uv run pytest`, `uv run pytest tests/test_schema.py`,
     `uv run mypy bzk tests`, and `ruff check bzk tests` /
     `ruff format --check bzk tests`.
   - Expected **in a container:** `1010 passed, 14 skipped`; `Success` over 120
     files; ruff clean. bzk's Mac reports `1016 passed, 8 skipped`. Report what
     you get, and stop if anything is red.
2. **The oracle.**
   - Report `tests/fixtures/r_tukey_reference.csv`'s row count, its distinct
     `case` values, and the `R.version` row.
   - State, from `notes/scripts/tukey_reference.R`'s header, what each of T1–T5
     is computed from, and the df for T1 and T2 in `tg_n3`.
   - Expected: cases `tg_n10`, `tg_n3`, `ptukey_grid`, `environment`; T1 is
     `TukeyHSD` on `supp:dose` with interaction-model error, df = N − 4; T2 is
     `ptukey` on the additive model's error, df = N − 3; in `tg_n3`, df = 8 and
     9.
3. **The registration's gate, in its own words.** Quote §4's *Input check*
   paragraph and its *The rule* bullets, verbatim.
   - State what happens when there are fewer than two gate rows.
   - State what happens when two passing variants are within 1e-4 of each
     other on every gate row.
   - State how the primary is chosen when several variants pass.
   - Expected: *undeterminable*, with nothing downstream; *not separated*, with
     readouts A–C reported under both; the smallest maximum |Δ| wins, and table
     order breaks only exact ties.
4. **What already exists that this must reuse, not re-implement.**
   - Quote the signatures of `bzk.stats.imputation.downshifted_normal`,
     `bzk.stats.anova.two_way`, `bzk.sources.pride.fetch` and
     `bzk.adapters.maxquant.read_table`.
   - Name the `TwoWayResult` fields that give the interaction-model residual
     mean square.
   - Expected: `residual_sum_squares / residual_df`. Say whether `two_way`
     accepts missing values. Expected: it raises, so imputation must come first.
5. **The deposit facts the pinning check compares against.** From
   `walk_PXD032267.json` § `deposit_read.site_table`, report:
   - `data_rows`, `columns` and `population.reverse`;
   - the twelve sample labels.

   Expected: 1,440, 171 and 14. The labels are `KOC1-3`, `KOTCA1-3`, `WtC1-3`
   and `WtTAC1-3`. **`TCA` in the KO labels is the deposit's own spelling and is
   not corrected.**

**Do not start §1 until bzk replies.**

---

## 1. Deposit declarations

In `bzk/sources/pride.py`, declare `PXD032267_SITES` (`GlyGly__K_Sites.txt`) and
`PXD032267_PARAMETERS` (`parameters.txt`): year 2023, month 5, with
`expected_content_hash=None`.
- A comment says the digests are pinned by the first Mac fetch, and that `None`
  is deliberate, not missing.
- **Do not invent a digest.** The existing digest-mirror tests must still pass.
  If one requires a non-`None` digest for every declaration, report it and do
  not weaken it.

## 2. Build

### 2.1 `bzk/stats/tukey.py`

Write it from the definition, in `anova.py`'s style. scipy supplies only
`studentized_range.sf` and `t.sf`.
- **One function** gives, for a rows × 12 matrix with no missing values and
  balanced 2 × 2 cell labels, the p-value of one named pair under **T1–T5**
  exactly as the registration's §4 table and the R script define them.
- It refuses missing values and unbalanced designs, as `two_way` does.
- **Validation:** `tests/test_tukey.py` reproduces every `T1_p`–`T5_p`, `diff`,
  `mse_*` and `ptukey_grid` value in the R fixture to |Δ| ≤ 1e-6.
  - Map R's pair names (`VC:0.5-OJ:0.5`) by parsing them. Do not hard-code
    them.
  - **Prove the test bites.** Mutate the T1 df to N − 3, show the test fails,
    revert, and show it passes. Read the mutated file back, per `CLAUDE.md`'s
    point 2.

### 2.2 `bzk/sources/pxd032267_gate.py`

**Constants transcribed from the registration**, each with its section cited:
- the tolerances (1e-5 input, 1e-4 p-value);
- the gate's minimum of two rows;
- the five variants, in table order;
- the imputation grid and the default cell;
- 20 draws;
- the valid-value candidates (3, 2, 1);
- the support rule (p < 0.05, Difference > 0.585 up and < −0.585 down);
- readout A's verdict rule (min–max range; ±25%);
- the recurs/absent thresholds (5%, 1%).

**Published values, with provenance:**
- Table 8's ten rows: protein name, position, `p_value` and `Difference`, with
  the supplement's citation.
- Table 7's six counts.
- **Mirror guard:** a test asserts that the ten `Difference` values equal
  `walk_PXD032267.json`'s `join_to_published_claims.rows[*].published_difference`.
- A test reads every registered number listed above from
  `walk/PREREG-PXD032267-gate.md` and asserts each module constant equals it.
  This follows the pattern of `graph.I4_LABELS`' guard. If a number cannot be
  parsed unambiguously, report it; do not hard-code around it.

**The pipeline, each step a function, run in the registration's order:**
1. **Pinning check (§2).** Verify both files by hash and require 1,440 data
   rows, 171 columns and 14 reverse rows. A mismatch raises.
2. **Population.** Remove reverse rows only.
3. **Values.** log2 of the twelve `Intensity <sample>` columns; zero is
   missing.
4. **Join Table 8.** Join by protein name contained in `Protein names` and the
   position in `Positions within proteins`. Require exactly one row per claim,
   or raise.
5. **Valid-value rule (§3).** The strictest candidate that retains all ten
   claims, with each candidate's count recorded.
6. **Gate rows.** Table 8 rows measured in all twelve samples.
7. **Input check, then Gate G (§4).** Report every variant's |Δ| per gate row,
   the passing set, the primary, every pairwise gap among passing variants,
   and the status: one of `passed`, `not_separated`, `undeterminable`,
   `input_not_reproduced` or `not_reproduced`.
8. **Readouts A–D (§5)**, only if G passed. Imputation runs on the full
   twelve-column matrix, through `downshifted_normal`, over the grid, with draw
   k using seed k. Report:
   - readout A's six counts and verdicts;
   - readout B's exposure, share, verdict and the `n ≤ 10` flag;
   - its secondaries;
   - readout C's count out of 20;
   - readout D. Cells whose `Identification type <sample>` is `By matching` are
     set to missing before imputation, and A and B are recomputed.

**Output.** `tests/fixtures/pxd032267_gate.json`, written by `main()` only.
- `main()` is `# pragma: no cover` and is **not run in this turn**.
- `generated_under` follows `pxd018299_published_cascade.py`'s convention:
  `generated_at`, `commit`, `working_tree_clean`, and the versions used.

### 2.3 Tests, synthetic only

Every refusal and branch is tested against a synthetic twin, never against
real data being in a particular state (`HANDOFF.md` §8). At minimum:
- the pinning check fails on a wrong row count;
- the join raises on zero matches and on two;
- the valid-value rule picks the strictest candidate retaining all claims;
- the input check fails on a 2e-5 Difference error;
- fewer than two gate rows gives `undeterminable`;
- two variants within 1e-4 give `not_separated`;
- the closest fit wins over table order;
- readout A's three verdicts are each reachable;
- readout B's thresholds sit at exactly 5% and 1%.

Mutation-prove two of them, as in §2.1.

## 3. Out of scope — do not do these, and report if tempted

1. Fetching anything from PRIDE, or running `main()`.
2. Inventing or pinning a content hash.
3. Editing the registration, the walk record, `HYPOTHESIS.md` or the R
   fixture.
4. Adding a test variant, a grid value or a threshold the registration does not
   name.
5. Ingesting PXD032267 into the graph, or writing a curation record. This is an
   instrument, like `pxd018299_h10.py`, not an adapter.
6. Mapping protein names to UniProt accessions. Keying stays name plus position
   for this instrument; the walk record's `keyability_note` already says
   accession recovery is a later step.
7. Any change to `bzk/adapters/` or the resolver for *Mus musculus*.

## 4. Report

Close with `CLAUDE.md`'s four points, checks named with their targets. Then
add:
- each §2.2 constant beside the registration line it was parsed from;
- the mutation evidence;
- **anything in the registration you found ambiguous to implement, quoted, with
  the reading you took.** This is the most useful part of the report: the
  registration was written before any code existed, and the build is where its
  gaps show.
