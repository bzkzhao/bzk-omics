# CHECKS — the draw count, the nine read, and a shared-threshold mechanism

**Run 2026-09-22 on bzk's machine.** Scripts:
`notes/scripts/diagnose_round11.py` and `diagnose_round12.py`. Not an
independent path: the same instruments the registered runs use. **Attempt 3's
registered verdict stands.**

Vocabulary as fixed in `walk/CHECKS-membership-and-corrections.md`: **withdrawn**
= false as stated; **superseded** = correct under a disfavoured choice.

---

## 1. Both headline numbers move with the draw count, in opposite directions

| draws | unstable, of claims with an imputed value | structural misses | structural extras |
|---|---|---|---|
| 20 | 27.8% | 6 | 3 |
| 50 | 34.1% | 5 | 3 |
| 100 | **38.3%** | **2** | **2** |

**Neither number may be quoted without its draw count.** Instability rises with
draws because more draws find more claims that ever move; "structural", defined
by unanimity across draws, falls for the same reason. At 20 draws the pair
flatters the reconstruction twice over: the lowest instability and the largest
apparent agreement are read off the same run.

**The counts are observations, not properties.** Six claims with no support in
20 draws is consistent with a per-claim support probability up to **16.8%**;
three supported in all 20, with one down to **86.1%**. "Supported in no draw"
is the correct phrasing; "structurally absent" is not.

## 2. The nine, read rather than counted

| | id | imputed of 6 | localisation | note |
|---|---|---|---|---|
| published, never supported | 889 | **0** | 1.00 | fully measured — see §3 |
| | 952 | 4 | 0.97 | draw territory |
| | 997 | 4 | 1.00 | draw territory |
| | 1100 | 4 | 0.53 | draw territory |
| | 1726 | 2 | 0.98 | |
| | 1733 | 3 | 0.65 | |
| called in every draw, not published | 225 | 3 | 1.00 | |
| | 1151 | 3 | 1.00 | |
| | 1811 | 3 | 1.00 | |

Eight of the nine sit at 2 to 4 imputed values, which is draw territory even
when unanimous over 20 draws. **Only one is fully measured.**

## 3. New: a claim's fate can depend on other claims' imputations

`id 889` (ATP1A1 K605) is measured in all six columns, localisation 1, score 89,
published, and called in **no** draw.

| | across 20 draws |
|---|---|
| its statistic | +2.664 to +2.664 (frozen, as a fully measured row must be) |
| its q | **0.0144 to 0.0177** (threshold 0.01) |
| its positive-direction rank | 839 to 880 of 2,101 |

Its own values never change. **The imputations drawn for other rows move the
null, and so move this row's q.** A fully measured published claim is therefore
excluded by draws made for other claims.

**Readings (judged).**
- This is a mechanism the project had not named: **draw dependence propagating
  through a shared FDR threshold into rows with no imputed values at all**.
  Every previous measurement treated instability as a property of imputed rows.
- It weakens the "structural discordance" framing: at least one of the nine is
  **threshold proximity**, not a different pipeline. The q range (0.014 to 0.018
  against a 0.01 cut) is close enough that a modest difference in the paper's
  threshold would call it.
- Its protein field carries twelve candidates (`P05023-4;P05023;…;P13637-3`,
  genes ATP1A1/ATP1A2/ATP1A3), the razor-ambiguity class this project has
  measured elsewhere. Not implicated in the exclusion, but recorded.

## 4. Two structural candidates eliminated

**The unit.** The per-multiplicity `___1` columns give 691 calls at precision
0.975 and recall 0.858, against 689 at 0.977 and 0.851 for the summed columns.
**Indistinguishable.** The most promising structural candidate is gone.

**The population, searched rather than fitted,** under the documented rule:

| population rule | rows | calls | precision | recall |
|---|---|---|---|---|
| at least 1 in a group (the one used) | 2,101 | 689 | 0.977 | 0.851 |
| at least 2 in a group | 1,465 | 755 | 0.927 | 0.885 |
| **at least 3 in a group** | 914 | 717 | 0.944 | **1.000** |
| **at least 3 in the knockout arm** | 799 | 719 | 0.942 | **1.000** |
| at least 1 in both groups | 336 | 21 | 1.000 | 0.253 |

**No population lands on the paper's 798 calls**, so the population is not the
explanation either. But **where claims have three real measurements, the
reconstruction reproduces the published selection exactly** (recall 1.000). The
disagreement lives entirely among sparse rows.

## 5. The crossing share is cut-dependent, and is not rule-free

| cut at rank | share of claims whose rank range crosses it |
|---|---|
| 200 | 62.3% |
| 400 | 68.7% |
| 600 | 43.8% |
| **781 (the documented rule's calling rate)** | **27.6%** |
| 1,000 | 20.1% |
| 1,400 | 11.1% |

Round 10's 32.9% inherited the rule through its reference point and used a
ranking over both directions while the cut counted only one. **Superseded.** The
rule-free figure is the rank-spread distribution itself: quartiles **408 / 491 /
606** of 2,101 rows, for claims with an imputed value. The crossing share may be
quoted only as "at the documented rule's calling rate".

## 6. The two unopened supplements do not carry what is needed

| file | sheet | rows | content |
|---|---|---|---|
| MOESM4 (16 kB) | "Proteins significantly UP in US" | 26 | protein-level, LFQ intensity columns, KO listed first |
| MOESM5 (74 kB) | "Proteins significantly UP in US" | 324 | protein-level; **values are log2 ratios, not intensities**, despite the header; WT listed first, with `WT_IFN-1` hyphenated |

Neither holds a parameters sheet, a Perseus session, or a site-level matrix.
**The threshold and the population remain unrecoverable from the published
record.** Two incidental observations: MOESM5's header disagrees with its
content, and the two tables differ in column order and in naming convention
(`WT_IFN_1` against `WT_IFN-1`) — in a deposit where column naming has already
caused difficulty.

## 7. What remains

- **Running Perseus** on the deposited matrix at the published settings. It is a
  Windows application; this work ran on Linux without a virtual machine.
- **The authors**, for the threshold, the randomisation count and the
  population.

Everything else testable from the published record has now been tested: the FDR
rule family, the s0 axis, the imputation grid, the permutation scheme, the
estimator, the unit, the population, and the supplements.
