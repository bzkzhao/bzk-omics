# CHECKS — the gap is what imputation predicts, and a protein-grain comparison

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
