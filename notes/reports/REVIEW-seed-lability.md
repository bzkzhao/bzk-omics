# Review — seed lability as a distinct finding

2026-09-20. Reviews the descriptive breakdown in `PXD026748 — what the second
deposit measured`, §"What underdetermined mostly means", against `HYPOTHESIS.md`.

**Position:** this is the strongest result the project has produced, it is not
D5, and it should be separated from D5 before anything is drafted.

---

## 1. What was measured

Home: `walk/RESULT-PXD026748-reconstruction.md` and the committed fixture. All
figures below belong there and are named, not restated elsewhere.

- Under the publication's own default imputation settings, a substantial share
  of its testable claims pass with some random draws and fail with others.
- Every claim classified underdetermined across the 360-member family has at
  least one parameter setting at which seeds disagree.
- No underdetermined claim fails on parameter choice alone.
- Support falls with imputation width; downshift matters less; scope almost not
  at all.

## 2. What it establishes

That a **fully specified** analysis does not determine the claim set. Nothing
was left unstated at the point where the instability arises: the test is
specified, reproduced exactly at the gate, and the settings are the software's
documented defaults. Re-running the stated pipeline produces a different set of
published claims.

This is categorically different from analytical underdetermination (D5), which
says the published record fails to determine the analysis. Here the record
determines the analysis and the analysis still fails to determine the claims.
Registered in `HYPOTHESIS.md` v7 as **D7, stochastic non-determination**.

Four properties make it stronger than D5:

1. **It cannot be a family-size artefact.** The primary figure is measured at
   the publication's own settings, not across a grid the reviewer chose. The
   standing objection to the 360-member conjunctive criterion does not reach it.
2. **It is not a reporting criticism.** No author failed to state anything. That
   removes the adversarial reading, which matters when both deposits are
   co-authored inside the group.
3. **It generalises without a second deposit.** Any downshifted-normal
   imputation feeding a hard P threshold has this property; the mechanism is
   arithmetic, not biological.
4. **It carries a one-line fix.** Record the seed, or report support as a
   fraction across draws rather than a binary set. Findings with an actionable
   remedy and a number behind them get adopted.

## 3. What it does not establish

- **Not that any claim is false.** Nothing in the set is unsupported in every
  variant, and the median underdetermined claim holds in most of them. The
  finding is about what the publication pins down, not about the biology. Any
  sentence that blurs this is a misreport.
- **Not a rate for the literature.** One deposit, and see §5.
- **Not that PTM data are special.** Imputation is grain-agnostic. The route to
  domain specificity runs through absence-defined claims (§6), and H9p tests it.
- **Not that the published run was unlucky.** Which draw the authors got is
  unknown until the seed is supplied. Until then the realised run's position in
  the distribution is unmeasured.

## 4. Novelty

The phenomenon is field folklore. It surfaces in tool-comparison work noting
that results differ between imputation variants, and in support-forum threads
where someone finds their differential-expression list changed between runs and
is told the imputation has a random component. What I can find no instance of is
a **measured rate of claim-set instability across seeds, at a publication's own
settings, against that publication's own claim set.**

That is the position the thesis has been looking for since v1: documented enough
that this measures a known problem rather than announcing one, unmeasured enough
that the number is new. It is a better position than D5 holds — parameter
variation changing the significant list is published — and better than the diGly
ambiguity, which is not only documented but quantified by others.

**Positioning sentence to use, once:** existing work asks which imputation
method is best; this asks what a published claim set is worth when the method is
fixed and only the draw varies.

## 5. Limitations that must be stated before anyone else states them

1. **The two deposits are not independent.** Both publications are co-authored
   inside the group. Shared people, plausibly shared conventions, possibly a
   shared analyst. Convergence between them has an alternative explanation, and
   the side-by-side comparison currently reads as two samples of the literature.
   The third deposit must be unaffiliated. This is now the project's most
   valuable open gate.
2. **The denominator is wrong by one level.** A claim whose row carries no
   missing value cannot be seed-labile. The rate belongs over claims with at
   least one imputed value, not over all testable claims. Both should be
   reported; the conditional one is the finding.
3. **Three defensible counts exist, and choosing after seeing them is the error
   this project studies.** The primary readout is registered by rule in
   `HYPOTHESIS.md` v7 §5 before drafting, with the other two reported as
   sensitivity. Committing the forking-paths error at the reporting layer would
   be the most quotable flaw in the paper.

## 6. What it opens

- **The anchor decomposition.** The anchor used the same imputation family. Its
  223 can be split into test choice and seed. If seed lability appears there
  too, the class has two instances from one measurement already in hand.
  Registered as H10.
- **The absence-defined route to domain specificity.** The exposed cluster is
  the one defined by absence, and PTM site claims are disproportionately
  absence-defined. Two measurable steps, neither requiring D3.
- **The realised draw.** With the seed from Ghent, the published run can be
  located in the distribution rather than assumed typical.

## 7. Recommended order

1. Register D7 and the primary readout rule. *(done, v7)*
2. Compute the conditional denominator.
3. Register H4 on the attribution exposure set now available at claim grain.
4. Anchor decomposition (H10).
5. Third deposit, unaffiliated.
6. H5c and H9p, which were next and are now fifth and sixth.

The reordering is the point of this review. H5c and H9p were registered when D5
was the headline; D7 is a larger finding, cheaper to extend, and it does not
depend on either.
