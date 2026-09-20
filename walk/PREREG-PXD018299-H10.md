# PRE-REGISTRATION — PXD018299 under its named test (H10, `HYPOTHESIS.md` v8)

**Registered 2026-09-20, before any anchor computation under this test, at the
commit that adds this file.** It is committed **before** the meeting with the
authors, by bzk's decision.

**The author-parameter rule, decided here in advance.** Author-stated
parameters, whenever received, define an **additional configuration** that is
run and reported beside the primary. They may be any of: imputation width,
downshift, scope or seed; the randomisation count; or the permutation scheme.
- **If they are stated before the anchor run is executed,** that configuration
  becomes the primary for **readout A**, the recomputed recovery.
- **H10's verdict (readout B) stays on the registered default cell either
  way.** That is consistent with v8's rule, because readout A is defined by this
  pre-registration and is not one of v8's registered primaries.
- *Received* and *before the run* are established by the record, not by
  memory. Author parameters enter only through a committed file,
  `walk/PXD018299-author-parameters.json`, holding the values, their source
  (who stated them, when, and in what form) and the date received. The run
  records whether that file existed at its commit.
- Using author values after results exist is not a fork. They are external
  information, not an option chosen by how it came out.

Kinds follow the earlier pre-registrations: **MEASURED**, **DERIVED**,
**JUDGED**.

**What this measures.** Two things, in one run.
1. **The anchor recomputed under its own named test.** This replaces the D6
   figure (237 significance losses under our earlier Welch-based test) with a
   figure measured against the paper's criterion.
2. **H10: does draw instability (D7) recur on the anchor?**

---

## 1. The published test (read, PMC7884788)

- **Test:** Perseus 1.6.0.2, a two-sample t-test with **s0 = 0.1** and
  **permutation FDR = 0.01**. The Fig. 2 legend applies these values to all the
  paper's proteomic analyses.
- **Contrast:** KO + IFN against WT + IFN, three replicates each.
- **The claim set:** Data Table S1, 798 GlyGly peptides *"significantly
  enriched"* in KO + IFN (`SUPP_DATA_1`, `sha256:e2680e30…a0db`).
- **Support** for a claim: q ≤ 0.01 **and** d > 0 (higher in KO + IFN).
- **Unstated:** the randomisation count, imputation, the valid-value rule, and
  normalisation.

## 2. Population and exposure

**Population.** Every row of the deposit's site table
(`HAP1_USP18KO_GlyGlyKSites.txt`, `sha256:a4a503e3…2009`) except reverse
decoys, carrying the six `Intensity KO_IFN_1..3` and `Intensity WT_IFN_1..3`
columns.
- Contaminants and rows with localisation below 0.75 are **kept**. The paper's
  own table retains 33 peptides below 0.75 and 3 flagged contaminants, so
  removing them would be D6 again.
- Rows the platform refused at ingestion are **kept**. Refusal is a statement
  about reference identity, and the paper's statistics never saw it.

**Exposure.** All **798** published claims. Each joins exactly one deposit row
by `deposit_id` in `tests/fixtures/pxd018299_published_cascade.json` (MEASURED:
798 rows, 798 distinct ids, none missing). Claims that fail the valid-value rule
(§3) leave the exposure, and are reported.

## 3. The unstated steps, fixed here by rule, never by outcome

**Values.** log2 of the six intensities. A zero or blank intensity is missing.

**Which intensity columns: decided by the same check as normalisation.** Perseus
may have analysed the summed `Intensity KO_IFN_n` columns or the
per-multiplicity `___1` columns of an expanded table. The check below runs
against both. The column family that meets the 99% criterion is used; if both
do, the summed columns are used, since they are the platform's. If neither
does, the summed columns are used and the result is flagged, as for
normalisation.

**Normalisation: decided by a check on the published values.** Data Table S1
carries the paper's six log2 intensities for each of its 798 rows.
- For the cells where the deposit reports a measured intensity: if S1's value
  equals log2 of the deposit value (|Δ| ≤ 1e-6) for at least 99% of those
  cells, **there is no normalisation**.
- Otherwise, the rule tests per-column median subtraction, with medians over
  the population, under the same criterion. If that matches, it is used.
- If neither matches, the run records `normalisation: undetermined` and uses
  none, and every result carries that flag.

**The valid-value rule: the strictest candidate consistent with the published
set.** The candidates, strictest first:
1. at least 3 valid values in at least one group;
2. at least 2 in at least one group;
3. at least 1 in at least one group.

The rule taken is the strictest one under which **every** published claim's row
passes, because the paper's rule must have retained all 798. Every candidate's
count is reported. If none retains all 798, the run takes the one retaining the
most and reports those that fail.

**The published draw: an estimation readout, not a choice.** In S1's cells where
the deposit value is missing, S1 carries the value the paper imputed. For each
WT column, the run reports the mean and SD of these published imputed values
against the column's measured distribution. From those it estimates the implied
downshift and width, under both per-sample and whole-matrix scope.

This answers the circularity objection to the earlier "signature" argument: the
imputed cells are identified by the deposit's missingness, not by a value
cut-off. **It is estimation only.** It locates the published run; it does not
change the family or the primary readout.

## 4. The test implementation: a gate, then an attainability check

**Variants.** `perseus_s0` (turn 18) gives four variants. The build turn adds
the two missing trivial-relabelling treatments, making **eight**:

- **Sidedness:** `joint` or `per_side`.
- **Scheme:**
  - `random` (with replacement);
  - `random_excluding_trivial` (identity and mirror excluded);
  - `exhaustive_when_small` (identity excluded, mirror kept);
  - `exhaustive_excluding_trivial` (identity and mirror excluded).

**Randomisations: 250.** This is the reviewer's understanding of Perseus's
default, **not verified** and not stated by the paper. It is recorded as a
choice.

**Gate G (on published Perseus output).**
- *The data:* `PXD026748`'s shotgun arm, through the pipeline the earlier gate
  validated (PC0 to PC3). The test is WT against *ISG15*−/−, 6 against 6, at
  s0 = 1 and FDR 0.05, at the default imputation cell (0.3, 1.8, per sample),
  seeds 0 to 19.
- *The target:* Supplementary Table 3's `+` calls.
- *The metric,* over the complete-case proteins (1,512 in the earlier gate): a
  protein counts as called if it is called in at least 10 of the 20 seeds.
  Compute the **precision** and the **recall** of these calls against Table 3's
  `+` among complete-case proteins.
- *A variant passes G* if its precision and recall are both **≥ 0.95**.
- *G passes* if at least one variant passes.
- *Also reported:* the number of complete-case `+` proteins. If it is below 30,
  G is flagged *weakly informative* but not failed.

**Check A (attainability on the anchor).** A variant survives only if it produces
at least one claim with q ≤ 0.01 on the anchor's matrix, under at least one
seed at the default cell. The publication reports 798 calls at FDR 0.01 from a
3-against-3 design, so a variant that cannot reach 0.01 there is **refuted by
the paper**.

**Admitted variants** are those passing both G and A.
- If none is admitted, the anchor readouts below **do not run**. The result is
  reported as *named test not reproduced*.
- The **primary variant** is the admitted one with the highest G F1, where F1
  is the harmonic mean of precision and recall. Ties go to the earlier variant
  in the list above.
- Every other admitted variant is reported as secondary.

## 5. The family

The same axes as H9s:
- width 0.2, **0.3**, 0.4;
- downshift 1.6, **1.8**, 2.0;
- scope **`per_sample`** or `whole_matrix`;
- 20 paired draws per cell. Draw k uses imputation seed k **and** permutation
  seed k.

The **default cell** is (0.3, 1.8, `per_sample`).

The whole-matrix scope of our earlier anchor path is a cell of this grid, not
the default.

## 6. Readouts

**A. The recomputed recovery, which replaces the D6 figure.** The number of the
798 supported in the default cell, by the median over its 20 draws. It is
reported next to 512 (the earlier Welch-based recovery) and the 237 significance
losses.
- If `walk/PXD018299-author-parameters.json` is committed before the run, the
  same count under the author configuration is readout A's **primary**, and
  the default cell's count is reported beside it.
- Otherwise the default cell is primary, and the author configuration, whenever
  it arrives, is an added readout.

**B. H10's primary, as registered in v7 and v8.** At the default cell, the share
of claims whose support differs across the 20 paired draws, **over claims whose
row carries at least one imputed value**.
- **Recurs:** at least 5%.
- **Absent:** at most 1%.
- **Indeterminate:** between the two.

**Reported, never the headline:**
- the same share over all claims;
- the share with the permutation seed held at 0, which isolates the imputation;
- the share with the imputation seed held at 0, which isolates the
  permutations;
- the full-family durable, underdetermined and unsupported counts;
- the whole-table count of supported sites.

**C. The published-draw estimates** (§3).

**D. The 14 named targets:** each one's support in the default cell, as the
median over draws, under the paper's test.

## 7. Registered expectations (JUDGED)

| # | quantity | registered | basis |
|---|---|---|---|
| X1 | valid-value rule taken | **≥ 3 in at least one group** | published claims are measured in KO + IFN; a Perseus-typical rule |
| X2 | normalisation check | **none** (S1 equals log2 of the deposit) | S1 is a Perseus export of the matrix it tested |
| X3 | S1 cells at deposit-missing positions | **filled** (S1 has zero missing values) | MEASURED earlier: zero missing across 798 × 6 |
| X4 | variants failing A | both `joint` variants that keep the mirror or draw with replacement | simulation on turn 18's code, 3 against 3 |
| X5 | G passes | yes, with at least one `per_side` or trivial-excluding variant admitted | the test statistic already matched Table 3 exactly |
| X6 | readout A | **650 to 798**, point ~740 | the paper's own draw called all 798 |
| X7 | readout B | **recurs**, point ~20% | 668 of 798 claims have all three WT cells below 21, heavily imputed like cluster 1a |
| X8 | the 14 targets supported under the named test | **≥ 12 of 14** | the paper's table carries all 14 |

**No rule, threshold, grid value or variant list is changed after the run.**
Misses are reported as misses.
