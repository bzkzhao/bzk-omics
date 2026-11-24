# CHECKS — the gap is what imputation predicts, and a protein-grain comparison

> **Correction (2026-11-24).** Three corrections: §3 on the paper's 2,341, §1's
> *Readings* on selection, and §2 on MOESM5's values.
>
> **2,341.**
> The paper's 2,341 equals the deposited site table's row count before any
> filter, reverse decoys and contaminants included. §3's heading clause *"the
> published record is exhausted on this axis"*, and the claim from *"No filter in
> this region reproduces the paper's stated identification count"* through *"is
> now evidenced rather than assumed."*, are **withdrawn** on **the axis
> inference**: a scan of distinct modified-peptide ids was taken to show that no
> reading of the file is the paper's figure, which is a row count. The scan's
> figures, and its insensitivity to score through *"missing axis."*, stand as
> counts and properties of distinct modified-peptide ids, and its sentences read
> on that axis are true on it. See `walk/CORRECTION-PXD018299-2341.md`.
>
> **W6.**
> Two sentences of §1's *Readings* are withdrawn, and one is qualified.
> - *"Selection adds almost nothing"*, and *"The concern that the 43 are a
>   selected class was correct to raise and turns out not to bite"*, are
>   **withdrawn**: false as stated, because the reasoning was defective. They
>   report as found what was not tested. The simulation conditioned on clearing
>   the weakest published fold change; the published claims were selected by
>   being called, on q, which was not simulated.
> - What remains true on the axis simulated: under the conditioning that was run,
>   a fold-change floor, the shift from +1.007 to +1.047 log2 is small, and that
>   measurement stands. What does not follow is the unqualified claim about
>   selection, or that the gap is downshift arithmetic rather than a selection
>   artefact.
> - Successor: under selection on a fold-change floor, selection moves the
>   simulated median gap from +1.007 to +1.047 log2; selection on q was not
>   simulated.
> - *"Observation and prediction agree to about 0.01 log2 units"* is
>   **qualified**, not unaffected. It compares the observed +1.055 with the
>   fold-change-conditioned +1.047, a conditioning that 8,296 of 8,600 simulated
>   draws cleared (round 15's log, line 9). Against the unconditional +1.007 the
>   difference is 0.048. It stands as a comparison with that simulation only.
>
> **W7.**
> §2's claim that MOESM5's *"values are log2 ratios despite an "LFQ intensity"
> header"* is **withdrawn**: false as stated, because the reasoning was
> defective. No ratio reading has been disproved; the sentence states as found
> what the same paragraph calls unknown. Successor: unknown. What was measured:
> MOESM5's values lie a median 26.6 below log2 of the deposited `proteinGroups`
> LFQ intensities, over 1,556 cells (round 15c's log), so they are not the
> deposit's log2 LFQ intensities; and the two ratio-shaped readings tested, minus
> the row mean and minus the column median, put only 0.3% and 0.1% of cells
> within 0.01. A ratio to a reference the raw store does not hold remains
> untested. The 17 unmatched claims and §2's protein census figures are
> unaffected.
>
> *Other homes, not edited.* For W6: round 16's downshift band
> (`walk/CHECKS-two-route-recovery.md` §1, and through it `walk/FINDINGS.md` §2's
> second route) compares the same selected observation with unconditional
> simulations; round 16's script, lines 107-124, applies no conditioning. It is
> recorded here as the same unexamined limitation and is not re-examined: no
> figure of that document or of `walk/FINDINGS.md` §2 moves. For W7: the MOESM5
> row of the supplements table in `walk/CHECKS-draws-and-threshold.md`, which
> carries its own banner; and round 15c's script, line 8, which reads "log2
> RATIOS". For 2,341: the execution records — round 11's script, line 18; round
> 13's script, lines 22-26, 157, 164 and 184; round 13's log, lines 24-25; round
> 14's script, lines 22-25, 165 and 174; round 14's log, line 21; round 15's
> script, lines 21-24, 181, 199, 202 and 210; round 15's log, lines 20, 30 and
> 31-32; the S1 provenance script, line 7 — and `walk/FINDINGS.md` §8, which is
> edited.

**Run 2026-09-22 on bzk's machine.** Scripts:
`notes/scripts/diagnose_round15.py`, `diagnose_round15b.py`,
`diagnose_round15c.py`; logs `notes/logs/round15.txt`, `round15b.txt`,
`round15c.txt`. Not an independent path: the same instruments the registered
runs use. **Attempt 3's registered verdict stands.**

Vocabulary as fixed in `walk/CHECKS-membership-and-corrections.md`: **withdrawn**
= false as stated; **superseded** = correct under a disfavoured choice.

---

## 1. The gap is directional, and it is what the authors' own model predicts

Round 14 reported |published − measured-only| fold change over the 43 partially
drawn claims, median 1.055 log2. The absolute value hid the direction, and the
class is selected: a claim is in the published table because it was called, and
a drawn cell helps it get called when it lands low in the wild-type arm.

| | median (log2) |
|---|---|
| **observed, signed** | **+1.055** (quartiles +0.691, +1.524) |
| simulated at the recovered parameters, unconditional | +1.007 |
| simulated, conditioned on clearing the weakest published fold change | +1.047 |

**Published exceeds measured-only in 41 of 43 claims.**

**Readings (judged).**
- **Observation and prediction agree to about 0.01 log2 units.** Imputation at
  the parameters recovered from the authors' own published values inflates a
  partially drawn fold change by about one log2 unit, and the published table
  shows exactly that.
- **Selection adds almost nothing** (+1.007 unconditional against +1.047
  conditional), so the gap is the downshift arithmetic rather than a selection
  artefact. The concern that the 43 are a selected class was correct to raise
  and turns out not to bite.
- The signed form is the one to report: *published magnitudes exceed their
  measured part by about one log2 unit* says more than an absolute deviation.

## 2. The protein-grain comparison, inside the same experiment

Same samples, same lab, same software, no PTM enrichment. MOESM4's published
protein claims carry LFQ intensities, so the census rule applies to them.

**The column mapping was tested before use.** The deposited `proteinGroups`
names samples `KO_INF_P_2hGradient1` where the supplement says `KO_IFN_1`, and
no curated record maps them. Under the inferred mapping, **122 of 122
comparable cells match log2 of the deposited value to within 0.01, correlation
1.0000**, so the mapping is confirmed by the published numbers themselves. An
earlier attempt (round 15, JJ) used a naive mapping, matched nothing, and
reported every cell as drawn; that result is **withdrawn**.

| | site claims (798) | protein claims (25) |
|---|---|---|
| contain at least one drawn cell | **95%** | **44%** (11) |
| whole arm drawn | 90% (715) | 32% (8) |
| drawn cells | — | 18.7% (28 of 150) |

**Readings (judged).**
- In the one comparison where everything else is held fixed, **PTM site claims
  are about twice as likely to contain a drawn value, and nearly three times as
  likely to rest on a wholly drawn arm.**
- This sits beside H9p's registered result rather than against it: H9p found
  that *per claim carrying missing values*, protein and site claims are equally
  imputation-dependent. Together they say the difference is **exposure, not
  fragility**.
- **The denominator is 25**, and MOESM4 is the "significantly up" table only, so
  this is suggestive rather than settled. The interval on 11 of 25 runs roughly
  24% to 65%.

**The extension to MOESM5's 323 claims was attempted and refused.** Its values
are log2 ratios despite an "LFQ intensity" header; three readings were tested
against the deposit (raw log2, minus the row mean, minus the column median) and
none matched: 0.0%, 0.3% and 0.1% of cells within 0.01. **What MOESM5's numbers
are remains unknown.** Also recorded: **17 of its 323 claims match no deposited
protein group at all**, a keying gap at protein level.

## 3. The 2,341: the published record is exhausted on this axis

A bounded scan for an exact match on distinct modified-peptide ids, over nine
localisation cuts × six score cuts, with reverse and contaminant rows removed:

| | |
|---|---|
| cells scanned | 54 |
| exact hits on 2,341 | **0** |
| range covered | 1,171 to 2,359 |

The counts are also **insensitive to score below 40**, so score is not the
missing axis. **No filter in this region reproduces the paper's stated
identification count**, and the declaration that the published record is
exhausted on this axis is now evidenced rather than assumed.

## 4. Bookkeeping: two class splits are in the record

The census rule (round 14 onward) treats a cell as provided if the deposit has
it **in the summed column or at any multiplicity**. The earlier class tables
(round 9 onward) used the summed column only. That moves two claims between
classes:

| | multiplicity-aware (census) | summed only (class tables) |
|---|---|---|
| partially drawn | 43 | 41 |
| whole arm drawn | 715 | 710 |

The total carrying a drawn cell (758, or 751 in-matrix) is unaffected, so
nothing downstream changes. **Each table should state which rule it used**, and
from here the multiplicity-aware rule is the default.
