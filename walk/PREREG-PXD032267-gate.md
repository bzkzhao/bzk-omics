# PRE-REGISTRATION — PXD032267 under its named test (third deposit)

**Registered 2026-11-06, before any reconstruction of this deposit, at the
commit that adds this file.** It is the gate and measurement that
`HYPOTHESIS.md` §9's top gate needs. The deposit was selected under the v8 rule
(`walk/SELECTION-third-deposit.md`) and has been read at G4
(`walk/walk_PXD032267.json`, `deposit_read`).

**What this measures, in order. Each step runs only if the one before it
passes.**
1. **Gate G:** is the paper's test identified? This is a deterministic check
   against published p-values.
2. **Readout A:** do the paper's stated pipeline and selection rule reproduce
   its published call counts?
3. **Readout B:** does draw instability (D7) recur on a deposit with no shared
   authors? This is H10's definition, carried to this deposit unchanged.

Kinds follow the earlier pre-registrations: **MEASURED**, **DERIVED**,
**JUDGED**.

**Author-parameter rule: as `PREREG-PXD018299-H10.md`, unchanged.** Values
stated by the authors or by their contract provider (Creative Proteomics) enter
only through a committed `walk/PXD032267-author-parameters.json`. They define an
additional configuration and never replace the registered default cell for
readout B.

---

## 0. Disclosed before registration

Everything in `walk/walk_PXD032267.json` § `deposit_read` was seen before this
file was written:
- the parameter comparison;
- the population counts;
- the missingness per sample;
- the identification types;
- the join of all ten Table 8 claims;
- each claim's WT-arm measured pattern and its measured-only difference.

That means:
- **The Difference construction is known**: the mean of log2 raw `Intensity`
  per arm, unnormalised. Three complete rows matched to three decimals. It is
  not scored here.
- **Which Table 8 claims carry imputed WT cells is known:** seven of ten.
- **Not seen:** any KO-arm value of any Table 8 claim, any p-value computed by
  this project, and any count under any test.

## 1. The published test (read, *J Clin Invest* 133:e161453)

- **Pipeline:**
  - log2 intensities;
  - missing values (intensity 0) replaced by random draws from a normal with a
    smaller mean;
  - a two-way ANOVA with post hoc Tukey's HSD "to identify significant pairs".
- **Design:** genotype (WT, *Isg15*−/−) × surgery (control, TAC), n = 3 per cell.
- **Selection:** upregulation at Difference > 0.585 and downregulation at
  Difference < −0.585, with P < 0.05 from the general Statistics section.
  Reading that section as applying here is an inference, flagged in the record.
- **Published outputs:**
  - Supplemental Table 7: call counts for six comparison × direction cells;
  - Supplemental Table 8: ten upregulated sites in WT TAC vs WT control, each
    with `p_value` and `Difference`;
  - main text: filamin-C K2590 is also significantly *down* in *Isg15*−/− TAC vs
    WT TAC.
- **Unstated:** the imputation downshift, width, scope and seed; any
  valid-value or localisation filter; normalisation; whether the Table 8
  `p_value` is Tukey-adjusted.

## 2. Population

**Every row of `GlyGly__K_Sites.txt` except reverse decoys.** Contaminants and
rows below 0.75 localisation are **kept**. The paper's reported 1,426 sites are
exactly the non-reverse rows (MEASURED, disclosed in §0), so filtering further
would be D6 again.

**Pinning.** Before the run, `GlyGly__K_Sites.txt` and `parameters.txt` enter the
content store, and their sha256 is recorded in the build turn's report.
`deposit_read` held no bytes, so the run must establish that its file matches
the one read: 1,440 data rows, 171 columns and 14 reverse rows. A mismatch stops
the run.

**Exposure for readout B:** the ten Table 8 claims. Claims that fail the
valid-value rule (§3) leave the exposure and are reported.

## 3. The unstated steps, fixed here by rule

- **Values:** log2 of the twelve `Intensity <sample>` columns (the summed
  family, which the §0 Difference check established). Zero is missing.
- **Normalisation:** none, as established in §0. Not re-decided.
- **Valid-value rule: the strictest candidate that retains all ten Table 8
  claims.** The candidates, strictest first:
  1. at least 3 valid values in at least one of the four cells;
  2. at least 2 in at least one;
  3. at least 1 in at least one.

  Every candidate's retained count is reported.
- **Imputation family: the H10 grid, unchanged.**
  - width 0.2, **0.3**, 0.4;
  - downshift 1.6, **1.8**, 2.0;
  - scope **`per_sample`** or `whole_matrix`;
  - 20 draws per cell, with draw k using seed k.

  The **default cell** is (0.3, 1.8, `per_sample`). The test is parametric, so
  imputation is the only random step.

## 4. Gate G: identifying the test

**Variants.** Each gives a p-value for the WT TAC vs WT control pair:

| id | variant |
|---|---|
| **T1** | Tukey HSD over the four cell means, with MSE and df = 8 from the two-way ANOVA with interaction (equivalently one-way over four cells) |
| T2 | Tukey HSD over the four cell means, with MSE and df = 9 from the additive two-way model |
| T3 | unadjusted pairwise t on the T1 MSE, df = 8 (Fisher's LSD) |
| T4 | Student's t on the two cells alone, df = 4 |
| T5 | Welch's t on the two cells alone |

**Gate rows.** Table 8 claims whose row has all **twelve** intensities measured
(non-zero), so no draw enters the p-value. Their number is not known at
registration: no KO-arm value has been seen.

**Input check, before any variant is scored.** On every gate row, the
published `Difference` must equal the mean-of-log2 difference computed from the
pinned file to |Δ| ≤ 1e-5. The published values carry six decimals, so rounding
alone is at most 5e-7. If a gate row fails, G is reported as **input not
reproduced** and nothing downstream runs. That is a different finding from *test
not identified*: it says the authors' matrix is not the deposit's, which would
make every p comparison meaningless.

**The rule.**
- A variant **passes** if, on every gate row, |p − published `p_value`| ≤ 1e-4.
- **Why 1e-4 (DERIVED, `notes/scripts/sim_tukey_variant_separation.py`).** In
  simulated 2 × 2, n = 3 designs with p in Table 8's range, the median smallest
  gap between any two variants is about 2e-3. 7.4% of designs have some pair
  within 1e-4, mostly T4 against T5 when the two arms' variances are close. So
  one row cannot always separate the variants, and two rows almost always can,
  which is why §4 needs at least two gate rows. The margin is about 200 times
  the publication's rounding, which covers implementations of the
  studentised-range distribution.
- **G passes** if at least one variant passes.
- **If several pass,** the **primary** is the one with the smallest maximum |Δ|
  over gate rows, with table order breaking an exact tie. Each pair of passing
  variants is reported with its largest gap on the gate rows. If two passing
  variants are within 1e-4 of each other on every gate row, G is flagged **not
  separated**, and readouts A–C are reported under both.
- **Why not table order alone.** H10 attempt 2's tie rule picked a degenerate
  variant by list position. Here the gate is an identification, so the closest
  fit is the identified test; order only breaks exact ties.
- **Too few gate rows:** if there are fewer than two, G is **undeterminable**.
  Nothing downstream runs, and the result is reported as *gate rows
  insufficient*. The next step is then a new registration, not a relaxed one.
- **G fails** if no variant passes. Nothing downstream runs, and the result is
  *named test not reproduced*.

**Instrument validation, before any real data.** Tukey HSD is written from the
definition, following `bzk/stats/anova.py`'s convention, with scipy supplying
only `studentized_range.sf`. It is validated against R's `TukeyHSD(aov(...))` on
`ToothGrowth` (supp × dose), to |Δp| ≤ 1e-6. The R output is committed as the
fixture. A failure stops the build, not the gate.

## 5. Readouts

**A. Count reproduction (Table 7).** For each of the six cells, the median count
over the default cell's 20 draws under the primary variant:

| comparison | published up | published down |
|---|---|---|
| WT TAC vs WT control | 10 | 48 |
| *Isg15*−/− TAC vs *Isg15*−/− control | 74 | 18 |
| *Isg15*−/− TAC vs WT TAC | 31 | 5 |

These are reported with the population and the valid-value rule taken. Readout A
is the closest analogue of the anchor's documented-rule call count. It measures
whether the stated pipeline determines the published counts, not whether the
reconstruction is right.

**Per cell, a verdict fixed now:**
- **reproduced:** the published count lies within the minimum to maximum of the
  20 draws' counts;
- **near:** the count is outside that range but within ±25% of the median;
- **not reproduced:** otherwise.

The headline is the verdict for WT TAC vs WT control, up: it is the cell whose
members are published, and so the only one that bears on readout B. The other
five are reported. A *not reproduced* headline does not stop readout B, but it is
reported beside it, because B's support rule would then not be the paper's.

**B. D7 on this deposit (H10's definition, unchanged).** At the default cell, the
share of the ten Table 8 claims whose support differs across the 20 draws, taken
over claims whose row carries at least one imputed value **in any of the twelve
samples**. Support means p < 0.05 and Difference > 0.585 under the primary
variant.
- **Recurs:** at least 5%.
- **Absent:** at most 1%.
- **Indeterminate:** between the two.

**The power flag, stated now.** The exposure is at most ten claims. One
changing claim is at least 10% and so reads *recurs*; zero reads *absent*. The
verdict is therefore close to binary, and it is flagged `n ≤ 10` wherever it is
reported. It does not carry the weight of the anchor's verdict, which was over
751 claims.

**Reported, never the headline:**
- the same share over the whole population, across all six cells;
- the full-family durable, underdetermined and unsupported counts for the ten
  claims;
- each claim's support count out of 20 at the default cell.

**C. The named target.** Filamin-C K2590's support for *down* in *Isg15*−/− TAC
vs WT TAC (p < 0.05, Difference < −0.585), as a count out of 20 at the default
cell.

**D. Match-between-runs sensitivity, reported and not scored.** Readouts A and B
recomputed with every cell whose `Identification type` is `By matching` set to
missing before imputation. The paper does not state that MBR was used, so this
measures how far the published set depends on it.

## 6. Registered expectations (JUDGED)

| # | quantity | registered | basis |
|---|---|---|---|
| Y1 | gate rows | **reported, not predicted** | no KO-arm value seen |
| Y2 | G, if determinable | input check passes; G passes; primary **T1** | the paper names Tukey HSD after a two-way ANOVA, and T1 is that test. The input check is expected to pass because three rows already match to three decimals (§0) |
| Y3 | valid-value rule taken | **≥ 3 in at least one cell** | every Table 8 claim has a complete WT TAC or WT control arm (§0) |
| Y4 | readout A, WT TAC vs control, up | verdict **reproduced or near**; median **4 to 40**, point ~12 | Wide on purpose: the valid-value rule and imputation parameters are unknown, and with n = 3 under Tukey adjustment the count is sensitive to both. The anchor's documented rule came within 2% of its count, but its pipeline was more fully stated |
| Y5 | readout A, other five cells | **reported, not predicted** | no basis for numbers |
| Y6 | readout B | **recurs** | Two published p-values sit close to 0.05: Ackr3 K362 (0.0499) and Adprhl1 K335 (0.039). Under T1 their p uses an error pooled over all four cells, so any imputed KO cell in the row moves it with the draw. Their KO cells are unseen, so this rests on a mechanism, not a count |
| Y6b | Ttn K12993, support at the default cell | **20 of 20, durable** | Its control arm is wholly drawn and sits about 1.8 SD below the column mean with width 0.3 SD, so the difference stays near 5 in every draw. *Durable* here means stable under re-drawing, not grounded in measurement. That is the distinction FINDINGS §1 rests on, and this claim is its cleanest instance |
| Y7 | readout C (filamin-C down) | **reported, not predicted** | KO-arm values not seen |
| Y8 | readout D, WT TAC vs control up | **reported, not predicted** | Removing matched cells raises missingness in both arms: in the joined claims, matched cells sit in control and TAC samples alike. A drawn control lowers the control mean and a drawn TAC cell lowers the TAC mean, so the direction is not determined |

## 7. Stopping rule

**This is the single registered attempt on this deposit.** A second needs
new independent information: author or provider parameters, the provider's
pipeline documentation, or `mqpar.xml`. An instrument fault caught by §2's
pinning check or §4's validation also permits one, after it is fixed.
**No rule, threshold, grid value or variant is changed after the run.** Misses
are reported as misses.
