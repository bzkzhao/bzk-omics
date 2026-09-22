# RESULT — PXD018299 under its named test, attempt 3 (H10) — final registered attempt

**Run on bzk's machine after registration**
(`walk/PREREG-PXD018299-H10-attempt3.md`, committed at `e13f06c`), at `49cf3fc`,
in 17.9 s. No author-parameter file existed. Output:
`tests/fixtures/pxd018299_h10_attempt3.json`.

**Every figure carries two flags:**
- **validated in-sample; independent confirmation pending,** because
  `joint_half` was fitted on Table 3;
- **matrix: the deposit, not the published S1.** Attempt 2 §4 found S1 was not
  quantified from the deposited site table.

**Under the pre-registration's §5 stopping rule, this is the last registered
attempt at H10 on this deposit.**

---

## 1. The consistency check, and check A on the typical draw

**Rerun consistency: consistent.** All 12 compared integers (6 per variant: the
precision and recall numerators and denominators, and the two direction counts)
equal attempt 2's. There was no instrument fault.

**Check A, median over seeds 0–19, at the default cell:**

| variant | per-seed claim counts | median | admitted |
|---|---|---|---|
| `random_excluding_trivial` (**primary**, fixed by §2) | 711 to 731 | 722.5 | yes |
| `exhaustive_excluding_trivial` (secondary) | 713 to 731 | 722.5 | yes |

## 2. H10 — the registered verdict: **recurs**

It is read from the primary only, at the default cell, over the claims whose
row carries at least one imputed value.

| quantity | primary | secondary (imputation only) |
|---|---|---|
| **claims whose support changes across the 20 draws** | **159 of 751 (21.2%)** | 159 of 751 (21.2%) |
| over all claims | 159 of 791 (20.1%) | 159 of 791 (20.1%) |
| isolation: permutation seed fixed, so imputation varies | 159 of 751 (21.2%) | 159 of 751 (21.2%) |
| isolation: imputation seed fixed, so permutations vary | **1 of 751 (0.13%)** | 0 of 751 |
| family categories (360 members) | 312 durable, 479 underdetermined, 0 unsupported | same |
| whole table supported, default cell | 822 | 820 |

The verdict is **recurs**: 21.2% against the registered threshold of at least
5%.

## 3. Readouts D and D′ — the named targets

**D (the curated 14), at any-site grain: 14 of 14 supported.** At largest-site
grain the count is 13 of 14: ADAR's highest-intensity site is not supported,
though its other site is. OAS2 has 5 of its 6 sites supported.

**D′, every tier, at any-site grain:**
- **Results, not curated:** DDX3X and DHX9 are both supported.
- **Discussion:** TAP1, GBP1, STAT1, IFIT1, PSMB10, PSMB9, GBP2 and MAGE are all
  supported. **PARP14 is absent from S1,** which is reported as absent and not
  as a miss.

## 4. Readout A, and a defect found while scoring

**The fixture's readout A (676 of 791 for both variants) is mislabelled.**
`pxd018299_h10.py` (l.1343 at `a5aeb00`) passes the whole family's support, all
360 members, to `_readout_a` under the key `default_cell`. The rest is
correctly scoped:
- readouts B, D and D′ use the default cell's 20 members;
- attempt 2's secondary readout A (l.1413) used them too.

**Recomputed from the fixture** by `notes/scripts/recompute_readout_a.py`, with
no re-run. The output, verbatim:

```
primary (joint_half+random_excluding_trivial): default cell (20 members) 725 of 791; as the fixture computed it (360 members) 676; fixture's stored value 676
secondary (joint_half+exhaustive_excluding_trivial): default cell (20 members) 724 of 791; as the fixture computed it (360 members) 676; fixture's stored value 676
```

**The correct default-cell readout A is 725 of 791 (primary) and 724
(secondary),** exactly as §1 of the pre-registration disclosed from attempt 2,
and consistent with check A's per-seed median of 722.5. The figure 676 is
retained as what it actually is: **the claims supported by the median over the
whole 360-member family.**

**Scope of the defect.** It affects only readout A, in every attempt since turn
19. It changes **no scored result.** Readout A was disclosed and unscored in
attempt 3. Attempt 2's degenerate primary gave 0 of 791, and a default-scoped
count would also be near 0, since that variant floors q near 0.018. The code
fix is deferred to a build turn. The committed fixtures are **not** edited, and
this document is the record of the correction.

## 5. Registered expectations, scored

| # | registered | measured | |
|---|---|---|---|
| Z1 | check A passes for both | median 722.5 for both | held |
| Z2 | H10 **recurs**, point ~12%, range 5–30% | **recurs, 21.2%** | held (above the point estimate) |
| Z3 | secondary at least 5% **and below** the primary | 21.2%, **equal** | partly missed: "below" missed |
| Z4 | permutation-fixed isolation at least 5% | 21.2% | held |
| Z5 | 12 or more of 14 targets at any-site grain | 14 of 14 | held |
| Z6 | DDX3X and DHX9 both supported | both | held |

**Why Z3 missed (judged).** The reviewer expected permutation randomness to add
some instability. The isolations show it adds almost none: 1 of 751. So removing
it leaves the rate unchanged.

## 6. Readings (judged)

- **Draw instability recurs on the anchor.** A fifth of the claims whose row
  carries an imputed value change support when Perseus's default imputation is
  re-drawn. That is the same class of finding as `PXD026748`'s, where 114 of
  288 claims (40%) were seed-labile at the defaults. The two deposits share
  authors, so this is recurrence **within one group's practice, not across the
  literature.**
- **The source is the imputation, not the permutations.** Holding the
  imputation fixed leaves one claim unstable, while holding the permutations
  fixed leaves 159. With 250 randomisations over 18 non-trivial relabellings,
  the permutation null is effectively stable.
- **Under the paper's own test, the anchor largely reproduces.**
  - About 92% of published claims are recovered in the median draw at the
    defaults: 725 of 791.
  - 312 claims are durable across the whole family, and none is unsupported.
  - Every named target is recovered at any-site grain.

  This replaces the Welch-based story of 237 significance losses, which were a
  departure from the paper's test (D6).
- **All of this is on the deposit, not the published matrix.** S1's
  quantification remains unidentified. Every figure is in-sample, because
  `joint_half` was fitted on Table 3.
