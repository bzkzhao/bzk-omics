# CORRECTION — PXD018299's Data Table S1 is the deposit's table (2026-09-22)

**This corrects a finding published in `walk/RESULT-PXD018299-H10-attempt2.md`
§4 and carried into `-attempt3.md` and the findings document.** Attempts 1 to 3
themselves stand: no registered rule, threshold or verdict changes. The
committed fixtures are not edited; this document is the record.

**The finding withdrawn.** Attempt 2 reported that *"Data Table S1 was not
produced from log2 of the deposited site table"*, on the basis that about 2% of
measured cells matched within 1e-6.

**Why it was wrong.** The 1e-6 criterion tested a rounded spreadsheet against
full-precision values. Re-measured with tolerances, by
`notes/scripts/diagnose_s1_provenance.py`:

```
measured cells compared: 2437
  |S1 - log2(site)| <= 1e-06: 50 (2.1%)
  |S1 - log2(site)| <= 0.01: 2437 (100.0%)
  quantiles of S1 - log2(site), 1/5/25/50/75/95/99%: [-0.0, -0.0, -0.0, 0.0, 0.0, 0.0, 0.0]
  correlation of S1 with log2(site): 1.0000
  per-column median offsets: +0.000 on all six
```

**All 2,437 measured cells agree within 0.01.** Data Table S1 **is** log2 of the
deposited site table's summed `Intensity KO_IFN_*` and `WT_IFN_*` columns, with
no normalisation, rounded for publication.

**What follows.**
- **The reconstruction was rebuilding the right table.** The flag *"matrix: the
  deposit, not the published S1"* is withdrawn from every H10 figure.
- **Attempt 2's X2 held after all:** no normalisation, on the summed columns.
  The fixtures' `normalisation: undetermined` is an artefact of the same
  criterion, and the criterion is a **code defect** (`match_fractions` compares
  at 1e-6 and should use a rounding-tolerant comparison).
- **Readout C is legitimate again.** The deposit's missing cells do mark S1's
  imputed values, so the imputation estimate stands, with its reference-
  distribution bias unchanged: the wild-type columns have only about 60 measured
  cells against about 738 imputed.
- An adversarial review (2026-09-22) proposed that S1 might be peptide-level,
  from `modificationSpecificPeptides.txt`. That is **not** the explanation, and
  no peptide-level table was needed.

---

## What survives, sharper: seven claims with no measurement in the tested contrast

`notes/scripts/diagnose_seven_rows.py` looked at the 7 published claims whose
six IFN intensities are all absent from the deposit (ids 124, 434, 562, 1070,
1140, 1233, 1903). **They are not an artefact of column choice.** Their
non-zero intensities all sit in the **untreated** samples:

| deposit id | non-zero deposit intensities | S1's six IFN values |
|---|---|---|
| 124 | KO_1, KO_2, WT_2, WT_3 (untreated) | all six present |
| 434 | WT_1, WT_3 | all six present |
| 562 | KO_1, KO_2, WT_2 | all six present |
| 1070 | WT_1, WT_2 | all six present |
| 1140 | KO_1, KO_2, KO_3, WT_1, WT_2 | all six present |
| 1233 | WT_1, WT_2, WT_3 | all six present |
| 1903 | WT_1, WT_2, WT_3 | all six present |

All seven pass the localisation cut (0.93 to 1.00) and carry ordinary scores, so
identification is not in question. **In the contrast the paper tested, KO + IFN
against WT + IFN, every one of their twelve values is imputed, and all seven
were published as significantly enriched.** That is the strongest single
instance in this project of a published claim resting entirely on generated
values.

## A consequence for the reconstruction's population

The deposit carries **twelve** samples: `KO`, `KO_IFN`, `WT` and `WT_IFN`, three
each. Our reconstruction builds its matrix from the six IFN columns, which suits
the contrast. **The paper's valid-value filter was probably applied across all
twelve**, which would explain how these seven rows survived it: each has two or
three values in an untreated group.

If so, the filtered population, and with it the permutation null and the FDR
threshold, differs from ours. **This is recorded, not acted on.** Attempt 3's
pre-registration §5 closes registered attempts on this deposit, and a population
change is exactly what that rule exists to prevent after the fact. It joins the
list of things a further attempt would need new information to justify.
