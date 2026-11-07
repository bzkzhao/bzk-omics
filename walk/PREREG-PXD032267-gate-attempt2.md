# PRE-REGISTRATION — PXD032267 under its named test, attempt 2 — final

**Registered 2026-11-07, before attempt 2 runs, at the commit that adds this
file.**

**What governs attempt 2.** `walk/PREREG-PXD032267-gate.md` (attempt 1) governs
it in full, except where this file replaces it. Every variant, grid value,
threshold, readout definition and registered expectation not named below is
carried over unchanged.

**What stands.** Attempt 1 stands and is reported beside this one
(`walk/RESULT-PXD032267-gate-attempt1.md`). Its outcome, *input not
reproduced*, is not revised.

**Why a second attempt, against attempt 1's §7.** §7 allowed a second attempt
only on new independent information or an instrument fault. Neither occurred.
This attempt is made instead on the ground H10 attempt 3 used: **a defect in the
registration, corrected exactly and nothing else.** The defect was the input
check's tolerance. Its basis was the reviewer's, it was too weak, and the
attempt-1 result records it. The override is bzk's decision. It is made once, and
§5 below closes every further route.

---

## 1. What is already known, disclosed

Seen since attempt 1 was registered, all from the attempt-1 run and its
exploratory diagnosis (`notes/scripts/explore_pxd032267_gate_only.py`):
- the three gate rows, their published and deposit-computed Differences, and the
  input-check deltas;
- the valid-value rule taken, and the rows it retains;
- the join;
- **every variant's p on the three gate rows, with the input check suspended.**
  T1 reproduced the published p-values to 6.5e-6, and every other variant
  missed by more than 1e-2;
- **the rounding test:** log2 values rounded to four decimals reproduce all
  three published Differences to 3.3e-7.

**Therefore Gate G is not a fresh test in attempt 2.** Its outcome is disclosed.
It is run, reported and checked for consistency, but not scored as a
prediction.

**Unseen, and so the tests attempt 2 can still make:**
- readout A, the six count verdicts;
- readout B, D7's verdict, with its secondaries and family categories;
- readout C;
- readout D.

No count, support, draw or readout of any kind has been computed on this
deposit.

## 2. The correction — exactly two changes

**Change 1: the values are the authors' matrix.** Every measured cell's log2
intensity is rounded to **four decimals**, half to even (numpy's `round`), before
anything that uses it: the input check, the gate, the valid-value rule,
imputation and every readout. Imputed draws are not rounded: the deposit gives
no evidence about how the authors' drawn values were stored, and rounding them
would add an assumption.
- **Basis (DERIVED, disclosed in §1):** the fingerprint in the attempt-1
  result. A four-decimal input puts every difference on a grid of steps of
  1e-4 / 3, and all three gate rows sit 3.3e-7 from the published value.

**Change 2: the input-check tolerance is 5e-7 + 1e-9.**
- **Basis:** with change 1, the only remaining source of disagreement is the
  publication's rounding to six decimals, which is at most 5e-7. The 1e-9 is
  floating-point slack, the same role as H10's `THRESHOLD_TOLERANCE`.
- This tolerance is **derived from a model of the export, not fitted to the
  deltas.** The model was found after seeing them, which is why the gate is
  disclosed and not scored. The model is the registered thing.

**Nothing else changes.** In particular, these are all as in attempt 1:
- the population, the join, the gate rows' definition and the p tolerance
  (1e-4);
- the variant table and the primary rule;
- the imputation grid and the default cell;
- seeds 0–19, the support rule, and readout A's verdict rule;
- readout B's exposure and thresholds, and readouts C and D.

## 3. Consistency checks, before any readout

These are run and reported. A failure stops the run as an instrument fault.
1. Attempt 1's pinning, join and valid-value results are reproduced exactly:
   the same digests, ids, rule taken and rows retained. Rounding to four
   decimals cannot change which cells are measured.
2. The input check passes on all three gate rows at the change-2 tolerance.
3. Gate G passes, with **T1 the only passing variant**. Each variant's max |Δp|
   is reported beside the exploratory diagnosis's value, but **not tested
   against it**: rounding moves inputs by up to 3e-5, and T4 and T5 can be
   steep in p, so a fixed bound there could fail for no reason. T1's sole pass
   is robust: the next-closest variant missed by 1.4e-2, a hundred times the p
   tolerance.

Checks 2 and 3 reproduce what §1 disclosed. If either fails, the build, not the
data, is suspect.

**A failure in §3 is an instrument fault, not an attempt.** No readout has
been computed when §3 runs: the run checks first and computes readouts only
after all three pass. So a §3 failure is fixed in the build and the run
repeated, and nothing is spent. The run's output records every §3 failure and
fix. Once a readout has been computed, §5 applies without exception.

## 4. Readouts and expectations

**Readouts A–D are as attempt 1 registered them, under the primary,** with the
§2 values.

**Expectations Y4 to Y8 are attempt 1's, carried over verbatim and not
revised.** They were registered before anything in §1 was known, and nothing in
§1 bears on a readout. Restating them now could only add hindsight.

| # | carried from attempt 1 | status |
|---|---|---|
| Y2 | input check passes; G passes; primary T1 | **disclosed, not scored** |
| Y3 | valid-value rule ≥ 3 in at least one cell | already scored (hit), in attempt 1 |
| Y4 | readout A, WT TAC vs control up: reproduced or near; median 4 to 40, point ~12 | **scored here** |
| Y5 | readout A, the other five cells: reported, not predicted | reported |
| Y6 | readout B: recurs | **scored here** |
| Y6b | Ttn K12993: 20 of 20, durable | **scored here** |
| Y7 | readout C: reported, not predicted | reported |
| Y8 | readout D: reported, not predicted | reported |

**Every attempt-2 readout carries the label** *second attempt, after a
registration defect; test identified exploratorily* wherever it is reported.
That includes FINDINGS and HYPOTHESIS. A D7 verdict from this attempt is
weaker than a clean first-attempt confirmation, and the label says so.

## 5. Stopping rule — final, with no exception

**Attempt 2 is the last registered attempt on PXD032267, under any
circumstance.** Specifically:
- **No defect found in this registration permits a third attempt** once any
  readout has been computed. A defect found then is reported, not corrected.
  The only repeat allowed is §3's: an instrument fault caught before any
  readout exists.
- **Author or provider parameters, if they ever arrive,** enter only as an added
  configuration under the carried-over author rule. They are reported beside
  this attempt and never re-run as an attempt.
- **The third-deposit gate** in `HYPOTHESIS.md` §9 is then satisfied or not by
  this attempt alone. Whether to take another deposit is a new decision, and its
  rule is registered before any candidate is examined.

**No rule, threshold, grid value or variant is changed after the run.** Misses
are reported as misses, beside attempt 1.

## 6. Build requirement

The instrument needs **one parameter**, the number of decimals measured values
are rounded to. It is `None` for attempt 1, so attempt 1's run reproduces
unchanged, and `4` for attempt 2. It also needs a second tolerance constant,
parsed from this file.
- Attempt 2 writes `tests/fixtures/pxd032267_gate_attempt2.json`, and never
  overwrites attempt 1's fixture.
- §3's consistency checks are part of the run, not a separate script, and run
  **before any readout is computed**. The code must make that order
  structural, not incidental: a readout function that runs before §3 has
  passed is a defect.
