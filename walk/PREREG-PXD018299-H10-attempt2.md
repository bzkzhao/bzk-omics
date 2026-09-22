# PRE-REGISTRATION — PXD018299 under its named test, attempt 2 (H10)

**Registered 2026-09-22, before attempt 2 runs, at the commit that adds this
file.**

**What it supersedes.** It replaces only what it names in §1–§3 of
`walk/PREREG-PXD018299-H10.md` (attempt 1, `0e4dc6b`). Everything else there
still governs attempt 2 unchanged:
- the population and exposure (§2);
- the unstated steps (§3);
- the family (§5);
- readouts A to D (§6);
- expectations X1–X3 and X6–X8 (§7);
- the author-parameter rule.

**Attempt 1 is not replaced.** Its result stands, and this attempt is reported
beside it (`walk/RESULT-PXD018299-H10-attempt1.md`).

---

## 1. The fit, declared

Attempt 1's gate failed with precision 1.0 and recall 0.50 (joint) on Perseus's
86 complete-case calls. A descriptive diagnosis
(`notes/scripts/diagnose_gate_g.py`, seed 0, default cell) found two things:
- **The statistic ranks exactly as Perseus's does.** Its top 86 are the 86
  published calls.
- **At Perseus's 282nd call, our joint q is 0.098.** Half of that, 0.049, sits
  just under Perseus's 0.05.

**The convention adopted here was fitted to that one number, at one seed, on
Table 3.** It is:

> **`joint_half`:** as `joint`, except the null count at each threshold is
> halved. FDR(t) = ½ × mean over permutations of #{null |d| ≥ t}, divided by
> #{observed |d| ≥ t}. q-values stay monotone as before.

This is the leading reading of a counting convention: null exceedances counted
in one tail against observed exceedances in both. It is **not verified**. The
Perseus plugin source (`github.com/JurgenCox/perseus-plugins`) returned 404 on
2026-09-22.

**Consequence: any result of attempt 2 is validated in-sample only.** It is
labelled *"validated in-sample; independent confirmation pending"* wherever it
is reported.

## 2. The variants

`joint_half` × the four schemes of attempt 1:
1. `random`;
2. `random_excluding_trivial`;
3. `exhaustive_when_small`;
4. `exhaustive_excluding_trivial`.

That is four variants, in that order. **No other convention is admitted.** It
is not per-side, which attempt 1 showed calls 8 up against Perseus's 72, and it
is not the unhalved joint count.

## 3. The checks: what the fit did not use

All three must pass for any variant to be admitted to the anchor run. The fit
used a single figure: the q at the 282nd rank, at seed 0. None of these
reuses it.

**G2a — the full gate.** Attempt 1's gate G, unchanged (seeds 0–19, majority
call, the default cell, s0 = 1, FDR 0.05). Precision **and** recall of Table 3's
`+` among complete-case proteins must both be **≥ 0.95**.

**G2b — the direction split.** Over all 2,438 rows, with the majority-of-seeds
call, the number called *higher in WT* must fall in **[58, 86]**, and the number
called *higher in ISG15−/−* in **[168, 252]**. Perseus called 72 and 210; the
bands are ±20%. Attempt 1's unhalved joint run gave 33 and 145, outside both.
The fit never looked at direction.

**A — attainability on the anchor,** unchanged: at least one claim reaches
q ≤ 0.01 with d > 0, at the default cell, under at least one seed.

**Admission and the primary variant.**
- A variant is admitted only if it passes G2a, G2b and A.
- The primary is the admitted variant with the highest G2a F1, with ties going
  to the earlier variant in §2. At 6 against 6 the four schemes are expected to
  tie, so check A is what separates them.
- If no variant is admitted, the anchor readouts do not run, and the result is
  **named test not reproduced (attempt 2)**.

## 4. One added readout, D′ (descriptive, registered before the run)

Readout D covers the 14 curated targets. **D′ covers the publication's own named
targets**, matched by gene symbol against Data Table S1's gene-name column. It
has three tiers:
- **Results, curated (14):** as readout D.
- **Results, not curated (2):** DDX3X, DHX9.
- **Discussion:** TAP1, GBP1, STAT1, IFIT1, PSMB10, PSMB9, GBP2, PARP14, and
  MAGE. MAGE is matched as any symbol beginning `MAGE`, and that rule is
  declared as such.

For each target, D′ reports two grains:
- **any site:** at least one of its S1 peptides is supported, as the median over
  the default cell's draws;
- **largest site:** its highest-intensity S1 peptide is supported.

A symbol that matches nothing in S1 is reported as *absent from S1*, never as
*not recovered*. **D′ has no registered expectation and decides nothing.**

## 5. Registered expectations (JUDGED)

| # | quantity | registered |
|---|---|---|
| Y1 | G2a passes | yes, all four schemes tied |
| Y2 | G2b passes | yes, up and down both inside their bands |
| Y3 | check A | `random` and `exhaustive_when_small` **fail** (trivial relabellings in the null; with halving the mirror floor is 1/38 ≈ 0.026); both trivial-excluding schemes **pass** |
| Y4 | primary variant | `random_excluding_trivial` (it ties on F1 and comes first in §2) |

X1–X3 and X6–X8 of attempt 1 carry over unchanged.

**No rule, band, threshold or variant is changed after the run.** Misses are
reported as misses, beside attempt 1's.
