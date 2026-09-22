# CHECKS — imputation effects on PXD018299 (DESCRIPTIVE, UNREGISTERED)

**Run 2026-09-22 on bzk's machine**, at the request of an adversarial review of
the same date. Script: `notes/scripts/diagnose_imputation_effects.py`, which
reads the deposit, Data Table S1 and the committed cascade fixture, and writes
nothing.

**Neither check touches a registered verdict, a pre-registration, or a committed
fixture.** Both reproduce the registered figures from an independent path, and
then explain them.

---

## Check 1 — imputation decides the test, and instability has one home

Support and instability by how many of a claim's six values are imputed, at the
default cell over 20 paired draws, under attempt 3's primary variant:

| imputed of 6 | claims | supported | unstable | median q |
|---|---|---|---|---|
| 0 | 40 | 40 | 0 | 4.7e-04 |
| 1 | 15 | 15 | 1 | 1.9e-03 |
| 2 | 26 | 26 | 0 | 2.1e-03 |
| 3 | 598 | 596 | **46** | 4.9e-04 |
| 4 | 112 | 48 | **112** | 1.1e-02 |
| **total** | **791** | **725** | **159** | |

**It reconciles exactly with the registered readouts:** 725 supported (readout A)
and 159 unstable (readout B), reached without touching the attempt-3 fixture.

**Readings (judged).**
- **The canonical claim is far from the threshold, not near it.** 598 claims have
  the whole wild-type arm drawn against a fully measured knockout arm. Their
  median q is 4.9e-04, about twenty times below the 0.01 cut, and only 46 are
  unstable. Drawn-against-measured is a large, stable difference, because the
  draw sits about 1.8 column SDs below the measured mean by construction.
- **Instability has one home: the 4-imputed class.** All 112 claims with the
  wild-type arm drawn **and one knockout value missing** are unstable, with a
  median q of 0.011, straddling the threshold. Two measured knockout values are
  compared against three drawn wild-type values and one drawn knockout value,
  and the drawn knockout value decides. These 112, plus 46 of the 3-imputed
  class, are the whole of H10's 21%.
- **This is why the rate is 21% and not higher.** The review predicted it, and
  the figures bear it out.
- **The seven wholly-imputed published claims cannot be evaluated here.** The
  reconstruction's valid-value rule removes them, which is why exposure is 791
  rather than 798. By extrapolation they would be **stable and comfortably
  significant**, since with both arms drawn the comparison reduces to the two
  columns' imputation centres. That is a prediction, not a measurement.

## Check 2 — the authors' realised draw is Perseus's defaults

Data Table S1 is log2 of the deposit's site table
(`walk/CORRECTION-PXD018299-S1-provenance.md`), so S1's values at deposit-missing
cells **are the authors' own imputed draw**. Readout C compared them against
S1's 798 significant rows; the right reference is the deposit's own column
distribution, which is what Perseus imputes from.

| column | drawn values | against the deposit's column | against S1's significant rows (readout C) |
|---|---|---|---|
| KO_IFN_1 | 38 | down 1.49, width 0.22 (n 1,329) | down 1.77, width 0.24 (n 760) |
| KO_IFN_2 | 49 | down 1.39, width 0.20 (n 1,297) | down 1.70, width 0.23 (n 749) |
| KO_IFN_3 | 49 | down 1.51, width 0.26 (n 1,299) | down 1.79, width 0.28 (n 749) |
| **WT_IFN_1** | **738** | **down 1.76, width 0.29** (n 407) | down 2.44, width 0.49 (n 60) |
| **WT_IFN_2** | **735** | **down 1.77, width 0.29** (n 412) | down 2.17, width 0.46 (n 63) |
| **WT_IFN_3** | **742** | **down 1.78, width 0.29** (n 377) | down 2.58, width 0.51 (n 56) |

Perseus's defaults are **downshift 1.8, width 0.3**, applied per column.

**Readings (judged).**
- **The wild-type columns give the defaults, on 738 drawn values each:** 1.76 to
  1.78 and 0.29. This is the authors' realised draw, measured from published
  values rather than assumed. It independently confirms what a lab postdoc (not
  an author) stated about the lab's practice.
- **Readout C's wild-type deviation was the bias, not a finding.** Using S1's
  significant rows as the reference put it at 2.17 to 2.58; the proper reference
  removes it. Readout C should be read as superseded by this table.
- **The knockout columns are noisy and are not read into.** Each rests on 38 to
  49 drawn values against a reference of about 1,300, and they sit below the
  defaults at 1.39 to 1.51.
- **What this still does not give:** the seed. The parameters are recovered; the
  realisation is not reproducible from them.

## What follows

- The published run's imputation parameters are now **recovered, not assumed**,
  for this deposit. Any further reconstruction of it should use them, and they
  are the registered default cell already.
- The imputation's effect on the claim set is **mechanically understood**: it
  moves claims across the threshold only where a drawn value competes with two
  measured ones.
- **Neither check bears on the transferred FDR convention.** That remains
  untested.
