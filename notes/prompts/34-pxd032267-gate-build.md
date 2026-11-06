# Prompt 34 — Build the PXD032267 gate instrument (revision 3)

**Repository:** `main` at the commit adding this revision.

**Why revision 3.** An independent checker audited revision 1 at `a7da073` and
returned *fix before release*. Revision 2 closed seven of its nine findings;
a re-audit then found the author rule half-stated, an unmarked join key that
could fail on the Mac with no retry allowed, a gate order that hid a finding,
no valid-value fallback under readout D, and two unguarded mirrors. Revision 3
fixes those, and a third pass corrected four more points in it. Revision 1's findings, all taken, were:
1. Table 8's p-values were nowhere in the repository. They are now in
   `walk/PXD032267-published-tables.json`.
2. The hash step contradicted itself.
3. The author-parameter rule was dropped.
4. Readout B's secondaries and the *not separated* branch were given by label
   only.
5. Two rules were cited at one half.
6. The tautology sweep was unmentioned.
7. The Tukey function's contract conflicted with its own validation.
8. Six implementation points were left to guessing.
9. Two wording errors.

Earlier revisions are superseded in place. Revision 1's text is in `a7da073`.

**What this builds.** The instrument `walk/PREREG-PXD032267-gate.md`
registers:
- a validated Tukey HSD;
- the gate (gate-row count, then the input check, then five test variants);
- readouts A–D.

All of it is tested on synthetic inputs only. **No deposit bytes exist in the
container, and none are fetched here.** The real run is on bzk's Mac, under
commands the reviewer writes after this turn's report.

**Governing:**
- `walk/PREREG-PXD032267-gate.md`, in full. Where this prompt and the
  registration disagree, **the registration wins**, and the disagreement is
  reported. Where the registration is silent and this prompt supplies a
  reading, the reading is marked **[reading]**, and the report lists every one.
- `walk/PXD032267-published-tables.json`: the **only home** of Table 7 and
  Table 8, transcribed from the supplement PDF with its sha256.
- `walk/walk_PXD032267.json` § `deposit_read`: the facts the pinning check and
  the join compare against.
- `CLAUDE.md`'s four-point close.

**Settled ground.**
- The registration is committed (`96da102`) and is not edited.
- The R oracle, `tests/fixtures/r_tukey_reference.csv`, was generated on bzk's
  Mac (R 4.5.2) by `notes/scripts/tukey_reference.R` and committed with
  revision 1 at `a7da073`. An independent R 4.3.3 run agrees on all 114 values
  to 1e-14. **Do not regenerate it, edit it, or produce it another way.** Its
  independence from this session is the point.
- The template for this kind of instrument is `bzk/sources/pxd018299_h10.py`.
  Reuse its conventions and point to them; do not re-derive them.

**Edits are limited to:**
- `bzk/stats/tukey.py` (new);
- `bzk/sources/pxd032267_gate.py` (new);
- `bzk/sources/pride.py`: two `DepositFile` declarations;
- `tests/`, including `tests/test_tautology_sweep.py` (see §2.3).

No ADR, `ONTOLOGY.md`, curation record, `ROADMAP.md`, `HANDOFF.md`,
`HYPOTHESIS.md`, `walk/` or `notes/` edits. No graph, schema or DDL change.

The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **Repository state.**
   - Run `git log --oneline -3` and `git status --short`. HEAD should be this
     revision's commit, with a clean tree.
   - Run `uv run pytest`, `uv run pytest tests/test_schema.py`,
     `uv run mypy bzk tests`, `ruff check bzk tests` and
     `ruff format --check bzk tests`.
   - Expected **in a container:** `1010 passed, 14 skipped`; `Success` over 120
     files; ruff clean. bzk's Mac reports `1016 passed, 8 skipped`. Stop if
     anything is red.
2. **The oracle.**
   - Report the fixture's data-row count, its distinct `case` values with their
     row counts, and the `R.version` row.
   - Expected: 115 rows: `tg_n10` 39, `tg_n3` 39, `ptukey_grid` 36,
     `environment` 1, whose `value` is empty.
   - Report the sample counts: `tg_n10` has n = 40 (10 per cell), and `tg_n3`
     has n = 12.
   - Give T1's and T2's df in each case. Expected: 36/37 and 8/9.
3. **The published tables.**
   - From `walk/PXD032267-published-tables.json`, report the source sha256, the
     ten Table 8 rows (protein name, position, `glygly_probabilities`,
     `p_value`, `difference`) and the six Table 7 counts.
   - Confirm each Table 8 `difference` equals the corresponding
     `walk_PXD032267.json` `join_to_published_claims.rows[*].published_difference`.
4. **The registration's gate, in its own words.**
   - Quote §4's *Input check* paragraph and *The rule* bullets verbatim, and
     §5's readout A verdict bullets and readout B threshold bullets verbatim.
   - State the *undeterminable* and *not separated* outcomes, and how the
     primary is chosen.
5. **What exists to reuse.**
   - Quote the signatures of these, with file:line:
     - `downshifted_normal`;
     - `anova.two_way`;
     - `pride.fetch`;
     - `maxquant.read_table`;
     - `pxd018299_h10.read_author_parameters`;
     - `pxd026748_reconstruction.log2_zero_as_missing`.
   - Also give `pxd026748_reconstruction.SEEDS`, and the lines of
     `pxd018299_h10.py` where the valid-value filter is applied **before**
     imputation, and where the durable/underdetermined/unsupported categories
     are computed.
6. **The deposit facts.** From `deposit_read`, report:
   - `data_rows`, `columns` and `population.reverse`. Expected: 1,440, 171
     and 14.
   - The twelve sample labels: `KOC1-3`, `KOTCA1-3`, `WtC1-3`, `WtTAC1-3`.
     `TCA` is the deposit's own spelling and is not corrected.
   - The ten joined deposit `id`s, in Table 8 order. Expected: 57, 151, 281,
     405, 553, 901, 1252, 1270, 1276, 1282.

**Do not start §1 until bzk replies.**

---

## 1. Deposit declarations

In `bzk/sources/pride.py`, declare `PXD032267_SITES` (`GlyGly__K_Sites.txt`) and
`PXD032267_PARAMETERS` (`parameters.txt`): year 2023, month 5,
`expected_content_hash=None`.
- **Do not invent a digest.** A comment says `None` is deliberate, and that the
  first Mac fetch records the digest.
- **Registration gap, reported, not fixed here.** Registration §2 says the
  sha256 *"is recorded in the build turn's report"*. The build turn has no
  bytes, so the digest is recorded by the Mac run's report instead. List this
  under the report's registration disagreements.

## 2. Build

### 2.1 `bzk/stats/tukey.py`

Write it from the definition, in `anova.py`'s style.
- **The contract: a balanced 2 × 2 design, n ≥ 2 per cell, any n.** Input is a
  rows × samples matrix with no missing values, plus two factor arrays. It
  refuses missing values and imbalance, as `two_way` does.
- **For every pair of the four cells, it returns:**
  - `diff`: first-named cell minus second;
  - `mse_interaction` and `mse_additive`;
  - p under **T1–T5**, exactly as registration §4's table and the R script
    define them.
- **The additive MSE** is (residual SS + interaction SS) / (residual df + 1),
  computed from `two_way`'s result or directly.
- **scipy supplies** `studentized_range.sf`, and **`t.sf` [reading]**. The
  registration names only the former, but T3–T5 need the latter. Report this
  as an addition.
- **Validation.** `tests/test_tukey.py` reproduces every numeric value in the R
  fixture to |Δ| ≤ 1e-6, in both cases and the `ptukey` grid.
  - R's pair names (`VC:0.5-OJ:0.5`) are parsed, not hard-coded.
  - The `environment` row is skipped because its value is empty.
  - **Prove the test bites:** mutate the T1 df to N − 3, show the failure,
    revert, and show it passes. Read the mutated file back (`CLAUDE.md` point 2).

### 2.2 `bzk/sources/pxd032267_gate.py`

**Constants transcribed from the registration**, each citing its section, with
full rules and not half-rules:
- input tolerance |Δ Difference| ≤ 1e-5;
- p tolerance |Δp| ≤ 1e-4;
- at least two gate rows;
- the variants T1–T5 in table order;
- the grid: width {0.2, 0.3, 0.4}, downshift {1.6, 1.8, 2.0}, scope
  {`per_sample`, `whole_matrix`}, and the default cell (0.3, 1.8,
  `per_sample`);
- 20 draws, **seeds 0–19**, matching `SEEDS = tuple(range(20))` in
  `pxd026748_reconstruction.py`;
- the valid-value candidates (3, 2, 1);
- support: up when p < 0.05 **and** Difference > 0.585; down when p < 0.05
  **and** Difference < −0.585;
- readout A's verdicts:
  - *reproduced*: the published count lies within the minimum to maximum of
    the 20 draws' counts;
  - *near*: outside that range but within ±25% **of the median of the 20
    draws' counts**;
  - *not reproduced*: otherwise;
- readout B: *recurs* at **at least** 5%; *absent* at **at most** 1%;
  *indeterminate* between the two.

**Published values** are read from `walk/PXD032267-published-tables.json` at
run time, never copied into the module.

**Guards, in tests:**
- each registered number above is parsed from `walk/PREREG-PXD032267-gate.md`
  and compared to the module constant, in the pattern of `graph.I4_LABELS`'
  guard. A number that cannot be parsed unambiguously is reported, not
  hard-coded around;
- the published-tables `difference` values equal `walk_PXD032267.json`'s
  `published_difference` values;
- the joined deposit ids equal `walk_PXD032267.json`'s `id`s, which is checked
  at run time by step 4 below;
- Table 7's six counts in the published-tables file equal the table in
  registration §5;
- the two p-values the registration quotes in §6 Y6 (Ackr3 0.0499, Adprhl1
  0.039) agree with the published-tables file to the registration's rounding.

**Author parameters.** Registration lines 21–25 adopt H10's rule *unchanged*
(`PREREG-PXD018299-H10.md` l.11–12 and l.173–174). Implement both halves:
- read `walk/PXD032267-author-parameters.json` if it exists, and record whether
  it is **tracked in git at the run's commit**, as H10 records `author.tracked`
  (`pxd018299_h10.py` l.1372–1376);
- **only if it is tracked at the run's commit** does the author configuration
  become readout A's primary, with the default cell reported beside it. An
  untracked file is reported and ignored, because registration lines 22–23
  require a *committed* file;
- **readout B always stays on the default cell**; the author configuration is
  an added readout B line, never the verdict;
- **accepted keys for this instrument:** `width_sd`, `downshift_sd`, `scope`
  and `seed`, plus the required `source` and `date_received`. Any other key is
  refused by name, including H10's `randomisations` and `scheme`, which have no
  meaning for a parametric test. Do not reuse H10's key set as is.

**The pipeline, each step a function, in this order:**
1. **Pinning check (registration §2).**
   - Hash both files and **record** the digests. While the declaration's digest
     is `None`, there is nothing to compare against: say so in the output
     rather than imply a comparison.
   - Require these facts, as counted by `maxquant.read_table`: 1,440 data rows,
     171 columns, 14 rows with `Reverse` = `+`.
   - Also record the file's raw newline count **[reading]**: `deposit_read`
     counted non-empty lines in a browser, which `read_table` might count
     differently.
   - A mismatch raises.
2. **Population.** All rows except reverse decoys.
3. **Values.** The twelve `Intensity <sample>` columns through
   `log2_zero_as_missing`. Zero is missing.
4. **Join Table 8 [reading]: two keys computed independently.**
   - Key P (peptide): the deposit's `GlyGly (K) Probabilities` cell equals the
     published `glygly_probabilities` string, and the published position is
     present in `Positions within proteins`.
   - Key N (name), the walk record's rule: the published protein name is
     contained in `Protein names`, and the position is present as for key P.
   - For each claim, record which keys matched and on which rows.
   - **The join takes a row R when every key that matched finds R, and at
     least one of them finds only R. Otherwise it raises.** So one key alone
     finding exactly one row is enough. Key N is substring containment and may
     over-match; then key P decides.
   - The joined `id`s must equal the walk record's ten ids, in order, or
     raise. That is the guard either key passes through.
   - Why both: an exact-string key can fail on formatting, and a raise here
     ends the registered attempt. Registration §7 allows a second attempt only
     for faults caught by §2 or §4.
5. **Valid-value rule (registration §3).** The strictest candidate retaining
   all ten claims, applied over the four cells, with each candidate's retained
   count recorded.
   - **If no candidate retains all ten [reading]:** take the candidate retaining
     the most, and name the claims lost. This follows
     `pxd018299_h10.valid_value_choice` (l.649–650). Registration §2 says
     claims that fail leave the exposure and are reported. The case can arise
     under readout D's masking.
6. **Imputation input [reading, following the H10 convention].** The filtered
   rows only. `pxd018299_h10.py` applies the valid-value filter before
   imputing, so `per_sample` statistics are over the filtered matrix. Cite the
   lines.
7. **Gate G, in this order [reading on the order].**
   1. Count gate rows: Table 8 rows measured in all twelve samples. Fewer than
      two gives status `undeterminable`, and the variants are not scored.
      **The input check still runs on whatever gate rows exist, and its result
      is recorded beside the status.** If the authors' matrix is not the
      deposit's, that matters more than the row count, and a new registration
      written without knowing it would be wasted.
   2. Input check: Difference to 1e-5 on every gate row, where **Difference
      for "X vs Y" is mean(X) − mean(Y)**. Table 8's positive values fix the
      sign for WT TAC vs WT control. Applying the same convention to the two
      KO comparisons is a **[reading]**. A failure gives status
      `input_not_reproduced`.
   3. The variants: per variant and gate row, record |Δp|. Record the passing
      set; the primary (smallest maximum |Δp|, with table order breaking exact
      ties only); and every pairwise maximum gap among passing variants.
      Status is `passed`, `not_separated` or `not_reproduced`.
      **The trigger is the registration's:** status is `not_separated` when
      **any** two passing variants are within 1e-4 of each other on every gate
      row, whether or not the primary is one of them.
      **The set the readouts run under [reading]** is the primary plus every
      variant that belongs to any such close pair. So the readouts always run
      under more than one variant when the status is `not_separated`, as the
      registration's *under both* requires.
8. **Readouts.** These run when status is `passed` or `not_separated`.
   - Under `not_separated`, readouts A–C are computed under **every** variant
     in the not-separated set. **[reading]** The registration says *both*,
     which is silent on three or more.
   - Readout D is computed under the primary only **[reading]**. The
     registration's *A–C under both* could be read as passing on to D, since D
     is *A and B recomputed*. The report says which reading was taken.
   - Draws: for each member of the grid, seed k for k in 0–19 **[reading]**
     (the registration says *draw k uses seed k* and gives no range; 0–19 is
     the house convention), imputing pipeline step 6's matrix with
     `downshifted_normal`. The test is then applied per row for
     the three comparisons:
     - WT TAC vs WT control;
     - *Isg15*−/− TAC vs *Isg15*−/− control;
     - *Isg15*−/− TAC vs WT TAC.

   **Readout A.** For each of the six comparison × direction cells at the
   default cell, record:
   - the count per draw;
   - the median, minimum and maximum over the 20 draws;
   - the published count, and the verdict.

   The headline is WT TAC vs WT control, up.

   **Readout B.** At the default cell:
   - **Exposure:** the Table 8 claims retained by §5, whose row carries at
     least one imputed value **in any of the twelve samples**.
   - **Share:** the exposure claims whose WT TAC vs WT control *up* support
     differs across the 20 draws.
   - The verdict, and the `n ≤ 10` flag.

   **Readout B secondaries,** all reported and never the headline:
   1. **Whole population:** the share of retained rows carrying an imputed
      value whose support differs across the 20 draws, **computed separately
      for each of the six cells [reading]**. The registration's *across all six
      cells* is ambiguous between per-cell shares and any-cell instability.
      Report the any-cell figure beside them.
   2. **Family categories** for the ten claims, over all 360 grid members, with
      `pxd018299_h10.py`'s definitions (cite the lines):
      - *durable*: supported in every member;
      - *unsupported*: supported in none;
      - *underdetermined*: otherwise.
   3. Each claim's support count out of 20 at the default cell.

   **Readout C.** Filamin-C K2590's *down* support in *Isg15*−/− TAC vs WT TAC,
   out of 20 at the default cell.

   **Readout D [reading on the masking point].** Cells whose
   `Identification type <sample>` is `By matching` are set to missing
   **before** pipeline steps 5 and 6. The registration says only *before
   imputation*. Masking before step 5 lets the valid-value rule be chosen
   again, with step 5's fallback. Then the valid-value rule,
   imputation, readout A and readout B are recomputed. Report whether the
   valid-value rule taken changes.

**Output.** `tests/fixtures/pxd032267_gate.json`, written by `main()` only.
- `main()` is `# pragma: no cover` and is **not run in this turn**.
- `generated_under` follows `pxd018299_published_cascade.py`: `generated_at`,
  `commit`, `working_tree_clean`, and the versions used.
- It also records both digests and whether the author file existed.

### 2.3 Tests, synthetic only

Every refusal and branch is tested against a synthetic twin (`HANDOFF.md` §8).
At minimum:
- the pinning check fails on a wrong row count and on a wrong reverse count;
- the join raises on zero matches, on two, and on an id mismatch;
- the valid-value rule picks the strictest candidate retaining all claims;
- one gate row gives `undeterminable`, **and** a failing input check on that
  row is recorded beside it;
- the join raises when keys P and N disagree, and succeeds when only one of
  them matches;
- under readout D's masking, a claim losing every value takes step 5's fallback
  and is named;
- the input check fails on a 2e-5 Difference error;
- two variants within 1e-4 give `not_separated`, and readouts run under both;
- a close pair that excludes the primary still gives `not_separated`, and the
  readout set is the primary plus that pair;
- the closest fit beats table order;
- readout A's three verdicts are each reachable, including *near* measured
  against the median;
- readout B sits on its boundaries at exactly 5% and 1%;
- an unknown author-parameter key is refused, including `randomisations`;
- a **tracked** author file becomes readout A's primary and leaves readout B's
  verdict on the default cell; an **untracked** one is reported and ignored;
- key N over-matching beside a unique key P joins on key P without raising.

Mutation-prove two of them, as in §2.1.

**The tautology sweep is expected work.** `tests/test_tautology_sweep.py`
requires every new matching assertion in `tests/` to be classified in `PINNED`,
and the floor to be re-denominated. Do it by the sweep's own procedure, and
report every classification.

## 3. Out of scope — do not do these, and report if tempted

1. Fetching anything from PRIDE or the journal, or running `main()`.
2. Inventing or pinning a content hash.
3. Editing the registration, the walk records, the published-tables file,
   `HYPOTHESIS.md` or the R fixture.
4. Adding a variant, grid value or threshold the registration does not name.
5. Ingesting PXD032267 into the graph, or writing a curation record.
6. Mapping protein names to UniProt accessions.
7. Changing `bzk/adapters/` or the resolver for *Mus musculus*.

## 4. Report

Close with `CLAUDE.md`'s four points, with checks named with their targets.
Then add:
- each §2.2 constant beside the registration line it was parsed from;
- the mutation evidence and the tautology-sweep classifications;
- **every [reading] in this prompt, with any further reading you had to take,
  each quoted against the registration text it interprets;**
- the registration disagreements, starting with §1's digest gap.
