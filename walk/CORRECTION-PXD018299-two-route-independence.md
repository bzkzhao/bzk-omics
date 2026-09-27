# CORRECTION — the two downshift recoveries are not independent (2026-09-27)

**This corrects two claims published in `walk/CHECKS-two-route-recovery.md` §1 and
carried into `walk/FINDINGS.md` §2.** Neither band moves, and no registered rule,
threshold or verdict changes. The dated check is not rewritten; it carries a
banner, and this document is the record. `walk/FINDINGS.md` is edited directly.

Vocabulary as fixed in `walk/CHECKS-membership-and-corrections.md`: **withdrawn**
= false as stated; **superseded** = correct under a disfavoured choice. Both
claims below are **withdrawn**. Line numbers are as the banner leaves them.

---

## The findings withdrawn

**1. The independence claim.** `CHECKS-two-route-recovery.md:49`:

> **The two bands overlap on Perseus's default of 1.8, and share no inputs.**

and its title at `:1` — *"the downshift recovered twice"* — the heading of §1 at
`:25` — *"The authors' downshift, recovered twice by routes sharing no inputs"* —
and the closing clause at `:52`, *"by two independent routes"*. In
`walk/FINDINGS.md` the same claim stood at the §2 heading, in both rows of the
route table as the entry *"supplement + deposit"*, in the sentence
*"The two bands share no inputs and overlap on Perseus's default of 1.8"*, and in
the `imputation model` row of §5's condition table as an unqualified *"twice"*.

**2. The supersession claim**, which rests on it. `CHECKS-two-route-recovery.md:50–51`:

> This supersedes round 15's framing: the finding is not that an observation
> matched a simulation, but that **the authors' imputation parameter is
> recoverable from their published numbers by two independent routes**.

## Why they were wrong

Route 1 is the *against the deposit's column* readout of Check 2 in
`walk/CHECKS-PXD018299-imputation-effects.md`, computed by
`notes/scripts/diagnose_imputation_effects.py`. Route 2 is block LL of
`notes/scripts/diagnose_round16.py`. Four dependences hold between them.

**1. Route 2's drawn cells are a subset of route 1's drawn inputs.** Both read
their cell values from the same object — Data Table S1, opened at
`diagnose_round16.py:75` and at `diagnose_imputation_effects.py:103`, and indexed
by the same published-cascade fixture. Both classify a cell as drawn by asking
what the deposit reports there, and the two tests are not the same test. Route 2
uses `provided()` at `diagnose_round16.py:67–70`, called at `:93`: a cell is drawn
only if the summed intensity column **and** its three `___1`/`___2`/`___3`
sub-columns are all non-positive. Route 1 uses `cell()` at
`diagnose_imputation_effects.py:51–57`, applied at `:117` through
`math.isnan(matrix[i, j])`: a cell is drawn if the summed column alone is
non-positive or unparseable. Route 2's condition is route 1's plus three further
conjuncts, so route 2's drawn cells are contained in route 1's. Route 2 narrows
the claim set again at `diagnose_round16.py:94`, skipping any claim with no drawn
cell or a wholly drawn arm.

**2. Route 2's measured cells are taken from route 1's reference.** `measured_fc`
at `diagnose_round16.py:96–98` is built from the S1 cells at positions the
deposit **does** provide. By `walk/CORRECTION-PXD018299-S1-provenance.md:25–27` —

> **All 2,437 measured cells agree within 0.01.** Data Table S1 **is** log2 of the
> deposited site table's summed `Intensity KO_IFN_*` and `WT_IFN_*` columns, with
> no normalisation, rounded for publication.

— those cells are rounded copies of exactly the deposit cells that make up route
1's reference population. Route 2's measured half is therefore not a second body
of evidence; it is the reference, rounded.

**3. Both routes reference the same deposit column distribution.** Route 2's
`column_mean` and `column_sd` at `diagnose_round16.py:84–85` are computed at
`:78–83` over every population row whose value in that column is positive. Route
1's reference at `diagnose_imputation_effects.py:126` is the non-NaN entries of
the same column over the rows retained by `keep` at `:64`. A positive value in a
column implies at least one measured value in that column's group, so `keep` is
implied by membership and excludes nothing: the two reference sets are the same
set of cells, column by column.

**4. Route 2 consumes route 1's output.** `WIDTH` at `diagnose_round16.py:49` sets
the standard deviation of every simulated draw, at `:114–116`. Its value is the
width route 1 recovered for the wild-type columns, reported at
`walk/CHECKS-PXD018299-imputation-effects.md:64–66` and read at `:71–72`. Route 2
does not re-derive that width; it fixes it and scans the downshift alone.

## The restated finding

Two statistics agree near Perseus's default of 1.8. The second's drawn cells are
a subset of the first's. Its measured cells come from the reference both use. It
takes the first's recovered width as fixed.

## Erratum on the route-1 label

The route named **readout C** in the table at `CHECKS-two-route-recovery.md:46` is
not readout C. Readout C is defined in `walk/RESULT-PXD018299-H10-attempt2.md` §5
and references S1's significant rows; the band in that row is Check 2's
deposit-reference readout, in
`walk/CHECKS-PXD018299-imputation-effects.md:59–66`. Readout C itself is
superseded there, at `:75–77`, precisely because its reference biased the
wild-type estimate. The same mislabel is at `notes/scripts/diagnose_round16.py:127`
and in the run log at `notes/logs/round16.txt:18`; neither is edited.

## What does not change

- **Both recovered bands.** `walk/CHECKS-two-route-recovery.md:46–47`.
- **The band scan's sensitivity table.** `walk/CHECKS-two-route-recovery.md:30–40`.
- **The bootstrap standard error on the observed median.**
  `walk/CHECKS-two-route-recovery.md:42`.
- **Route 1's column-by-column table.**
  `walk/CHECKS-PXD018299-imputation-effects.md:59–66`.
- **Attempt 3's registered verdict.** `walk/RESULT-PXD018299-H10-attempt3.md:39`
  and `:53`.

Every figure in this project's downshift recovery lives in
`walk/CHECKS-two-route-recovery.md` and
`walk/CHECKS-PXD018299-imputation-effects.md`. None is restated here.

## Every home of the withdrawn claims, and how each was handled

| home | wording | handled |
|---|---|---|
| `CHECKS-two-route-recovery.md:1` | title, *"the downshift recovered twice"* | banner; body not edited |
| `CHECKS-two-route-recovery.md:25` | §1 heading, *"recovered twice by routes sharing no inputs"* | banner; body not edited |
| `CHECKS-two-route-recovery.md:46–47` | the route table, whose *evidence used* column shows no overlap | banner over §1; body not edited |
| `CHECKS-two-route-recovery.md:49` | *"and share no inputs"* | banner; body not edited |
| `CHECKS-two-route-recovery.md:50–51` | the supersession of round 15's framing | banner; body not edited |
| `CHECKS-two-route-recovery.md:52` | *"by two independent routes"* | banner; body not edited |
| `FINDINGS.md` §2 heading | *"recoverable from the published numbers, twice"* | edited: *"by two overlapping statistics"* |
| `FINDINGS.md` §2 route table | *"supplement + deposit"* on both rows | edited: each route's inputs in words, including the fixed width |
| `FINDINGS.md` §2 body | *"The two bands share no inputs and overlap…"* | edited: the overlap half kept, the four dependences named |
| `FINDINGS.md` §5 condition table | *"recovered from the authors' published values, twice"* | edited: pointer to §2 |
| `notes/scripts/diagnose_round16.py:14–15` | *"a SECOND, independent recovery of the parameter"* | listed, not edited: the instrument of a dated run |
| `notes/scripts/diagnose_round16.py:127–128` | the second recovery as separate evidence, with the readout-C mislabel | listed, not edited |
| `notes/logs/round16.txt:18–19` | the same sentence, as run output | listed, not edited: logs are never edited |

No home outside `walk/` and `notes/` asserts the independence of these two
recoveries. `HYPOTHESIS.md:57–61` reports route 1 alone and is unaffected.
