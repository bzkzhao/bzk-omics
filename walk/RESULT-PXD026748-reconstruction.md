# RESULT — PXD026748 reconstruction (H9s, the D5 measurement)

**Run 2026-09-20 on bzk's machine, after registration.**
- **Registration:** `walk/PREREG-PXD026748-reconstruction.md` at `d3917c6`.
- **Instrument:** `python -m bzk.sources.pxd026748_reconstruction`, built in turn 16
  (`b836139`) and run once at `9e8dbe1`, in 9.2 s.
- **Output:** `tests/fixtures/pxd026748_reconstruction.json`, committed at
  `0d24eda`. It is the figures' machine-readable home. This document is the
  transcript and the scoring.

**Provenance.** The fixture records `working_tree_clean: false`. `git status
--short` at the time showed **only untracked files**: `data/frame/200`,
`data/frame/probe.py`, `probe_v2.json` and `probe_v3.json`, `notes/reports/last.md`
and `run.md`, and the fixture itself. No tracked file was modified.

---

## Console output, verbatim

```
[gate] PC0 2,438 of 2,438 registered
[gate] PC1 1,512/1,512 (1.0000)
[gate] PC3 1,512/1,512 (1.0000)
[gate] PC2 student_t      1,512/1,512
[gate] PC2 student_t_s0   77/1,512
[gate] PC2 welch_t        1,054/1,512
[gate] PC2 welch_t_s0     77/1,512
[family] 360/360 {'width_sd': 0.4, 'downshift_sd': 2.0, 'scope': 'whole_matrix', 'seed': 19}
[family] exposure 288 claim(s) over 360 member(s)
[family] primary durable 111, underdetermined 177, unsupported 0
[family] verdict extends_d5_to_imputation_alone (needs 274 / 15 of 288)
[family] wrote /Users/bzk/bzk-omics/tests/fixtures/pxd026748_reconstruction.json
```

---

## The gate: passed

| control | registered | measured | |
|---|---|---|---|
| PC0, proteins passing the shotgun filters | 2,438 | **2,438** | held, exact |
| PC1, log2 fold change within 0.01 on complete cases | ≥ 99% | **1,512 / 1,512** | held |
| PC2, −log P within 0.05 (best variant) | ≥ 99% | **1,512 / 1,512**, Student's t | held |
| PC3, ANOVA membership vs Table 2 | ≥ 98% | **1,512 / 1,512** | held |

**PC2's other variants:** Welch 1,054, and both S0-modified variants 77. Measured,
therefore: **the publication's shotgun t-test was Student's, with P not modified
by S0.** As registered, that choice was made on imputation-free proteins only.

**The join to Table 3:** 2,438 matched, 0 unmatched, 0 ambiguous. Table 2 read 600
IDs.

**PC1's sign check:** only 21 proteins would pass under a flipped sign, all near
zero fold change. So the WT/KO orientation is confirmed.

**What the gate establishes.** Wherever imputation cannot enter, the
reconstruction reproduces the publication's own published statistics, to the
protein.

---

## Scoring

| # | registered | measured | |
|---|---|---|---|
| R1, durable, P < 0.01 | 220 to 285, point ~260 | **111** (38.5%) | **missed, below** |
| R2, underdetermined, P < 0.01 | 3 to 60, point ~20 | **177** (61.5%) | **missed, above** |
| R3, unsupported in all 360, P < 0.01 | 0 to 30, point ~8 | **0** | held |
| R4, whole table supported in the default cell | 240 to 360, point ~300 | **283** | held |
| R5, threshold-consistency count | not predicted | **106** | reported |

**H9s's verdict, computed mechanically as registered (`HYPOTHESIS.md` v5).**
- Durable 111 is below the 274 needed to *weaken* D5.
- Underdetermined 177 is at least the 15 needed to *extend* it.
- **The verdict is: extends D5 to imputation alone.**

The reviewer's registered expectation was *"extends, narrowly"*. The direction
held. The size was wrong by an order of magnitude, and in the direction of
greater dependence on the imputation. **No rule, threshold or grid value was
moved.**

**By cluster, at the primary threshold:**

| cluster | durable | underdetermined | unsupported |
|---|---|---|---|
| 1a (the publication's PLpro targets) | 36 | **81 (69%)** | 0 |
| 1b | 11 | 28 (72%) | 0 |
| 2 | 58 | 54 (48%) | 0 |
| 3 (ubiquitin sites) | 6 | 14 (70%) | 0 |

**At the secondary threshold, P ≤ 0.001:** 38 durable, 220 underdetermined, and
**30 unsupported in every member**.

**In the default cell (0.3, 1.8, `per_sample`), by the median over 20 seeds:**
256 of 288 are supported at P < 0.01, and 150 at P ≤ 0.001.

**The one claim on a multiplicity-2 row,** Q14527 K158 (#126, cluster 1b), is
durable, supported in 360 of 360.

---

## Readings (judged)

**1. The caption's threshold is inconsistent with the published set, and the
methods' threshold is consistent with it.** In the default cell, 106 published
claims have a median P between 0.001 and 0.01, and 30 never reach P ≤ 0.001 under
any member. Had the set been selected at the caption's p ≤ 0.001, neither group
should be in it. This resolves one of the publication's internal contradictions
from its own data. It remains a reading, because the published run's draw is
unknown.

**2. The claim set the paper puts first is the least determined by its own
methods.** Cluster 1a is defined by absence: those sites are absent in the WT
PLpro and knockout samples. So the groups that make them significant consist
largely of imputed values, and the imputation's settings set their P values.
Cluster 2, the sites PLpro leaves untargeted, is the least dependent at 48%.

---

## Descriptive breakdown — UNREGISTERED

This section answers a question the registered readouts could not: **do the
underdetermined claims fail in extreme corners of the grid, or flip with the
seed?** It was computed after the run, from the committed fixture, by
`notes/scripts/describe_reconstruction.py`. **It cannot change anything above.**

```
recomputed categories: {'underdetermined': 177, 'durable': 111}
underdetermined claims supported in >= 342/360 members: 54
underdetermined claims supported in >= 324/360 members: 72
underdetermined claims supported in >= 288/360 members: 107
underdetermined claims supported in >= 180/360 members: 145
underdetermined support, min / 25% / median / 75% / max: [8, 236, 309, 351, 359]
underdetermined claims with at least one cell where the seed decides: 177 | failing only by whole cells: 0
default cell (0.3, 1.8, per_sample): supported in all 20 seeds: 173 | in some seeds only: 114 | in none: 1
support share by width_sd, all claims: {'0.2': 0.9102, '0.3': 0.8624, '0.4': 0.8025}
support share by downshift_sd, all claims: {'1.6': 0.8249, '1.8': 0.8643, '2.0': 0.8858}
support share by scope, all claims: {'per_sample': 0.8591, 'whole_matrix': 0.8576}
```

**What it shows.**
- **Most underdetermined claims are usually supported.** The median claim is
  supported in 309 of 360 members. 54 are supported in at least 95% of members,
  and 107 in at least 80%. "Underdetermined" here mostly means *"fails
  sometimes"*, not *"fails usually"*. The strict *all-360* definition was
  registered, and it is what the verdict uses.
- **The seed decides for every one of the 177.** Each has at least one grid cell
  where some seeds support it and others don't. None fails only because of which
  cell was chosen. Imputation's randomness is not a corner case here.
- **The most concrete form of the finding.** Under Perseus's own defaults, **114
  of the 288 published claims (40%) are supported under some of the 20 seeds and
  not others.** Re-running the published pipeline with its defaults and a
  different random draw would give a different set of significant sites.
- **Width matters most:** support share falls from 0.910 at width 0.2 to 0.803 at
  0.4. Downshift matters less, from 0.825 at 1.6 to 0.886 at 2.0. **Scope matters
  almost not at all:** 0.859 against 0.858.

---

## Carried

- **The published run's seed and parameters remain unknown.** No member is
  claimed to be the publication's run, and matching one would not show that it
  was.
- **The imputation-calibration analysis** that the pre-registration excluded
  (using the shotgun proteins that have missing values) remains unregistered. It
  could narrow the grid. It cannot alter this verdict.
- **The declared divergences stand:** summed rather than `___1` intensities; the
  22 cells failing the multiplicity sanity check; and the imputation difference
  between summed and expanded columns, judged negligible and not measured.
