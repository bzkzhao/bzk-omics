# PRE-REGISTRATION — PXD018299 under its named test, attempt 3 (H10)

**Registered 2026-09-22, before attempt 3 runs, at the commit that adds this
file.**

**What governs attempt 3.** `walk/PREREG-PXD018299-H10.md` (attempt 1) and
`walk/PREREG-PXD018299-H10-attempt2.md` still govern it, except where this file
replaces them.

**What stands.** Attempts 1 and 2 stand and are reported beside this one
(`walk/RESULT-PXD018299-H10-attempt1.md`, `walk/RESULT-PXD018299-H10-attempt2.md`).

**Why a third attempt.** Attempt 2's registered primary was degenerate. Check A's
*any seed* rule admitted `joint_half+random` on one favourable seed, and the
tie rule then chose it by list order. In a typical draw it supports nothing. So
**H10 was not tested in substance.** The defect was in the registration, and
this attempt corrects exactly that defect and nothing else.

---

## 1. What is already known, disclosed

Attempt 2 computed these for the two variants attempt 3 uses:

| figure | `random_excluding_trivial` | `exhaustive_excluding_trivial` |
|---|---|---|
| G2a | precision 1.00, recall 0.965 | same |
| G2b | WT 64, KO 212 | same |
| check A (any seed) | reached | reached |
| **readout A** (default cell, median) | **725 of 791** | **724 of 791** |

**Readout A is therefore not a fresh test in attempt 3.** It is reported for
completeness and is not scored as a prediction.

**Unseen for these variants, and so the tests attempt 3 can still make:**
- readout B (H10's verdict and its isolations);
- the family categories;
- the whole-table count;
- readouts D and D′.

## 2. The variants, and the primary, fixed by principle rather than by tie

| role | variant | why |
|---|---|---|
| **primary** | `joint_half` + `random_excluding_trivial`, 250 randomisations | It keeps **both** of v8's random steps, imputation and permutation, paired by seed, as H10's v8 amendment requires. It is also closest to Perseus's documented practice of drawing a fixed number of randomisations. |
| secondary | `joint_half` + `exhaustive_excluding_trivial` | The exact enumeration of the same 18-relabelling null. It has no permutation randomness, so its readout B isolates the imputation alone. |

The primary is chosen by these reasons, **not** by G2a's F1, and not by any
readout.

## 3. Check A, strengthened to the typical draw

A variant is admitted only if, at the default cell, **the median over seeds 0–19
of the number of claims with q ≤ 0.01 and d > 0 is at least 1**. This replaces
attempt 2's *any seed* rule. Both variants are expected to pass, given readout A
in §1.

**Rerun consistency.** G2a and G2b are recomputed and must equal attempt 2's
values exactly, since they are deterministic given the seeds. A difference stops
the run and is reported as an instrument fault.

If the primary is not admitted, **no readout is reported as primary**, and the
result is *H10 not tested (attempt 3)*.

## 4. Readouts

All of attempt 1's §6 readouts and attempt 2's D′ are computed **for both
variants in full**:
- A, as disclosed and not scored;
- B: H10's verdict, the share over all claims, both isolations, and the family
  categories;
- the whole-table count;
- C, as attempt 2, unchanged;
- D and D′.

**H10's verdict is read from the primary only,** with the v7 thresholds:
- **recurs:** at least 5%;
- **absent:** at most 1%;
- **indeterminate:** between the two.

These shares are taken over claims whose row carries at least one imputed
value.

**Every result carries two flags:**
- `validation: in-sample; independent confirmation pending`;
- `matrix: deposit, not the published S1`. Attempt 2 §4 found S1 was not
  quantified from the deposited site table: about 2% of cells match, and 7
  published claims have no deposit values.

## 5. The stopping rule

**Attempt 3 is the final registered attempt at H10 on this deposit** under
information available now. A fourth requires **new independent information**:
- the authors' stated settings;
- Perseus's code or documentation of its FDR convention;
- an independent published Perseus output;
- or the quantification behind S1.

No further attempt may be made to change an outcome of this one.

## 6. Registered expectations (JUDGED)

| # | quantity | registered | basis |
|---|---|---|---|
| Z1 | check A (typical draw) | both variants pass | readout A is 725 / 724 (disclosed) |
| Z2 | H10 verdict (primary) | **recurs**, point ~12%, range 5–30% | 751 of 791 claims carry imputed values; about 8% of claims sit outside the 92% recovered, so many are near the line |
| Z3 | readout B, secondary (imputation only) | at least 5%, below the primary's | removing permutation randomness removes one source |
| Z4 | readout B, permutation-fixed isolation (primary) | at least 5% | imputation is the larger source on the second deposit |
| Z5 | readout D, primary | 12 or more of 14 at any-site grain | X8, carried over |
| Z6 | readout D′, Results-not-curated (DDX3X, DHX9) | both supported at any-site grain | both carry significant S1 sites |

**No rule, threshold or variant is changed after the run.** Misses are reported
beside attempts 1 and 2.
