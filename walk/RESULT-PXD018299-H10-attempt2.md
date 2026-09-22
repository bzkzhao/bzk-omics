# RESULT — PXD018299 under its named test, attempt 2 (H10)

> **Correction (2026-09-22).** This document's finding that Data Table S1 was not
> produced from the deposited site table is **withdrawn**: it came from comparing a
> rounded published table at a tolerance of 1e-6. S1 **is** log2 of the deposit's
> summed intensities. See `walk/CORRECTION-PXD018299-S1-provenance.md`. The registered
> verdicts below are unaffected; the `matrix: deposit, not the published S1` flag is
> withdrawn with the finding.

**Run on bzk's machine after registration**
(`walk/PREREG-PXD018299-H10-attempt2.md`, committed at `8d1bb6e`), at `9b69bc1`,
in 18.8 s. No author-parameter file existed. Output:
`tests/fixtures/pxd018299_h10_attempt2.json`. **Every figure here is validated
in-sample, with independent confirmation pending,** because the `joint_half`
convention was fitted on Table 3.

**Context, not evidence.** A postdoc in the lab, **not an author of the
publication**, stated on 2026-09-22 that the lab's practice is Perseus's default
imputation settings. No number here depends on that statement. It matches the
registered default cell (0.3, 1.8, `per_sample`).

---

## 1. The checks the fit did not use: passed

**G2a, the full gate: passed by all four variants.**
- Precision 83 / 83 = 1.00, recall 83 / 86 = 0.965, F1 0.982.
- Attempt 1's unhalved joint count reached recall 0.50.

**G2b, the direction split: passed by all four.**
- Higher in WT: 64 (the band was [58, 86]; Perseus called 72).
- Higher in *ISG15*−/−: 211 or 212 (the band was [168, 252]; Perseus called
  210).
- The fit never used direction.

**Check A:**

| variant | reached q ≤ 0.01 and d > 0 |
|---|---|
| `random` | yes, **at seed 4 only** |
| `random_excluding_trivial` | yes, at seed 0 |
| `exhaustive_when_small` | **no** (the mirror kept, a floor of 1/38) |
| `exhaustive_excluding_trivial` | yes, at seed 0 |

**Reading (judged).** The halved convention reproduces Perseus's calls on data it
was not fitted to, in direction and across seeds. The fit came from one number,
so this is strong in-sample support. The convention is still unverified against
Perseus's code.

## 2. The registered primary is degenerate

- **Admitted variants:** `random`, `random_excluding_trivial` and
  `exhaustive_excluding_trivial`.
- **They tie on G2a's F1,** so §3's tie rule chose the first in §2's list:
  **`random`**. That misses Y4, which expected `random_excluding_trivial`.
- **Draws with replacement include the identity and mirror relabellings,** which
  floor q at 3 against 3 near 0.018 in a typical draw. Check A's *any seed*
  criterion admitted this variant on one favourable seed.

**Primary readouts, as registered:**
- **Readout A:** 0 of 791 supported in the default cell (by the median over
  draws). X6 expected 650 to 798: **missed**.
- **Readout B:** 1 of 751 claims with an imputed value changes support across
  draws (0.13%), so the **verdict is `absent`**.
  - Family categories: 0 durable, 6 underdetermined, 785 unsupported.
  - Whole table supported in the default cell: 0.
- **Readouts D and D′:** no target supported at either grain, in any tier.

**Reading (judged).** These are properties of the variant, not of the anchor.
The primary supports almost nothing, and a claim set with nothing in it is
trivially stable. So **H10's registered verdict, `absent`, stands as recorded,
but H10 was not tested in substance.**

**The registration defect** lies in two places:
- check A tested attainability under *any* seed, not the typical one;
- ties went to list order, which placed the with-replacement scheme first.

Both belong to the reviewer, not the code.

## 3. The registered secondary variants

§4 of attempt 1 requires every admitted non-primary variant to be reported:

| variant | readout A: supported of 791 (default cell, median) |
|---|---|
| `random_excluding_trivial` | **725 (91.7%)** |
| `exhaustive_excluding_trivial` | **724 (91.5%)** |

Readouts B, D and D′ were not computed for the secondary variants. **Reading
(judged):** under the paper's own test, with trivial relabellings excluded,
about 92% of the published claims are recovered, against 512 of 798 under our
earlier Welch-based test. This is secondary and in-sample, and it rests on a
matrix that does not match S1 (§4).

## 4. What S1 shows about the published matrix

**Normalisation: undetermined.** The share of measured cells where S1 equals the
candidate transform of the deposit, within 1e-6:

| column family | none | median-subtracted |
|---|---|---|
| summed | 50 / 2,437 (2.1%) | 0 |
| `___1` | 46 / 2,425 (1.9%) | 0 |

**Valid-value rule:** no candidate retains all 798.

| rule | rows retained | claims retained |
|---|---|---|
| at least 3 in a group | 914 | 677 |
| at least 2 in a group | 1,465 | 791 |
| at least 1 in a group | 2,101 | 791 |

The rule taken was *at least 1*. The 7 claims lost (deposit ids 124, 434, 562,
1070, 1140, 1233 and 1903) have **no measured value in any of the six deposit
columns**, yet carry six values in S1. X1 expected *at least 3* and X2 expected
*no normalisation*: **both missed.**

**Reading (judged).** Data Table S1 was not produced from log2 of the deposited
site table, with or without median subtraction. At least 7 of its rows have
values the deposit does not. The likeliest explanation is a different
quantification behind the published table (another search or processing run),
not a normalisation of this one. **The reconstruction therefore tests the
deposit, not the published matrix, and every anchor readout carries that
flag.**

## 5. Readout C — the published imputation, re-derived from S1

Imputed cells are those the deposit reports no value for. The implied
parameters, **per sample**:

| column | n imputed | downshift | width |
|---|---|---|---|
| KO_IFN_1 | 38 | 1.77 | 0.24 |
| KO_IFN_2 | 49 | 1.70 | 0.23 |
| KO_IFN_3 | 49 | 1.79 | 0.28 |
| WT_IFN_1 | 738 | 2.44 | 0.49 |
| WT_IFN_2 | 735 | 2.17 | 0.46 |
| WT_IFN_3 | 742 | 2.58 | 0.51 |

Treated as one **whole matrix**: downshift 2.46, width 0.41.

**Reading (judged).** The KO columns sit close to Perseus's defaults (1.8 and
0.3). The WT columns do not. Two limits apply:
- the "observed" reference distribution is S1's 798 significant rows, not the
  full matrix Perseus imputed from, which biases the WT estimate;
- §4 shows S1 was not quantified from this deposit.

This is an estimate, not a confirmation of the defaults.

## 6. Registered expectations, scored

| # | registered | measured | |
|---|---|---|---|
| X1 | valid-value rule at least 3 | at least 1 (none retains all 798) | missed |
| X2 | no normalisation | undetermined (about 2% match) | missed |
| X3 | S1 filled at deposit-missing cells | filled | held |
| X6 | readout A 650–798 | 0 (primary); 725 / 724 (secondaries) | missed (primary) |
| X7 | readout B recurs | `absent`, degenerate | missed; not tested in substance |
| X8 | 12 or more of 14 targets | 0 (primary) | missed (primary) |
| Y1 | G2a passes | passed, all four | held |
| Y2 | G2b passes | passed, all four | held |
| Y3 | `random` and `exhaustive_when_small` fail A | `exhaustive_when_small` failed; `random` passed at one seed | partly missed |
| Y4 | primary `random_excluding_trivial` | `random` | missed |

## 7. What follows

- **Attempts 1 and 2 stand together.** Attempt 1 left the named test
  unreproduced. Attempt 2 reproduced it in-sample, but its registered primary
  was degenerate.
- **H10 remains untested in substance.** A third attempt would have to make a
  trivial-excluding variant primary, and strengthen check A to the typical draw.
  Its readout A is already known (725 / 724), so readout A would **not** be a
  fresh test there. Readouts B, D and D′ are unseen for these variants, so H10
  **could** still be tested.
- **The anchor's published matrix is not this deposit's.** Any claim about the
  paper's own run needs the quantification behind S1, which neither the deposit
  nor the paper identifies.
