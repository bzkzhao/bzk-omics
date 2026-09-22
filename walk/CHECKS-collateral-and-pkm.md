# CHECKS — the collateral channel measured, PKM resolved, and 2,341 ruled out

**Run 2026-09-22 on bzk's machine.** Script: `notes/scripts/diagnose_round13.py`,
output `notes/logs/round13.txt`. Not an independent path: the same instruments
the registered runs use. **Attempt 3's registered verdict stands.** From this
round each script's stdout is committed beside it.

Vocabulary as fixed in `walk/CHECKS-membership-and-corrections.md`: **withdrawn**
= false as stated; **superseded** = correct under a disfavoured choice.

---

## 1. The denominator was wrong, and the collateral channel is narrow

Round 12 found that a fully measured claim's q moves with other rows' draws, so
the 40 fully measured claims are exposed too and should not have been excluded
from the denominator.

| | |
|---|---|
| fully measured published claims | 40 |
| of those, q range spans the 0.01 cut | **1** |
| their q range across draws | median 0.0015, max 0.0033 |
| instability over claims with an imputed value | 209 of 751 = 27.8% |
| **instability over all published claims** | **210 of 791 = 26.5%** |

**`id 889` is singular, not typical.** The collateral channel exists and is
measurable, but it moves one claim of forty, and the q ranges it produces are
small. **26.5% is the figure with the right denominator**; 27.8% is superseded
as the headline and kept as the conditional rate.

This also explains an anomaly left open in round 9: 1 of 40 zero-imputed claims
appeared unstable, with no mechanism at the time. That claim is `id 889`, and
the mechanism is the shared threshold.

## 2. PKM: the anomaly is the authors' own draw, and an older statistic is wrong

A review check found that of 39 published claims with all three wild-type cells
"measured", 38 agreed with the platform's fold change to within 0.001, and
`id 1107` (PKM K270) differed by 0.29. Read at row level:

| | KO_IFN 1–3 | WT_IFN 1–3 |
|---|---|---|
| S1 (published) | 26.150, 26.346, 26.282 | 22.505, **21.094**, 22.518 |
| deposit, summed | 26.150, 26.346, 26.282 | 22.505, **absent**, 22.518 |
| deposit, every `___n` | same | `WT_IFN_2` carries no value at any multiplicity |

**S1's 21.094 is the authors' imputed value**, about 1.4 below their other
wild-type values, consistent with the downshift recovered in earlier rounds. The
published fold change is +4.220 against the deposit's +3.748, and the difference
is entirely that one drawn cell.

**Withdrawn: "38 of 39 measured-WT rows agree".** That set was defined by S1's
completeness, and S1 has no missing values anywhere, so it cannot identify
measured rows. The comparison included at least one imputed cell. The
corrected statement: **of published claims whose wild-type arm is measured in
the deposit, the platform's fold change agrees with the published one to within
rounding**, and `id 1107` is not an exception to it but an illustration of the
draw entering a published number.

**The unit axis is now cleared at row level too.** Round 11 eliminated it on
aggregate agreement (691 calls against 689); this row confirms the summed and
per-multiplicity readings are identical where both exist.

## 3. The paper's 2,341 cannot be reconstructed, because it is a different unit

| reading of the site table | rows |
|---|---|
| rows in the table | 2,318 |
| minus reverse and contaminants | 2,298 |
| localisation ≥ 0.75 | 2,073 |
| any IFN intensity | 2,101 |
| any intensity in any of the twelve samples | 2,225 |
| expanded rows carrying intensity, twelve samples | 2,233 |
| expanded rows carrying intensity, IFN only | 2,106 |

**None is 2,341.** The paper counts GlyGly **peptides**; this table is
site-keyed, and a site carries several peptide forms, so the count is not
recoverable from it at any filter or expansion. It would need
`modificationSpecificPeptides.txt`, which the raw store does not hold.

**Reading (judged).** This is a clean negative: the constraint is real, and it
lives at a unit we do not have. It also bounds the same-kind success on the
other deposit, where expanded rows reproduced its stated 2,143 exactly — that
worked because the count there was quoted at site-and-multiplicity grain.

## 4. The conditional claim, restated from the partition

The dense population (at least three valid values in a group):

| | |
|---|---|
| rows | 914 |
| published claims inside it | **677 of 798 (85%)** |
| calls | 717 |
| hits | 677 |
| extra calls | **40** |
| recall inside it | 1.000 |
| precision inside it | 0.944 |

**Recall 1.000 is close to tautological** and is superseded as evidence: the 121
excluded published claims are exactly the sparse rows that were being missed,
and restricting the matrix also changes every row's q, so this is a different
test rather than the same test restricted. Its precision shows the cost: 40
extra calls against 16 on the full population.

**The conditional claim, stated from the partition instead and needing no
rerun:** disagreement with the published selection is concentrated among claims
where an arm is largely drawn (110 of 118 misses sit in the 4-imputed class),
and among claims resting on three real measurements per arm there is
essentially none.

## 5. What remains of the published record

- **Figure 2f**, the published volcano, is the last route to the threshold that
  needs neither Perseus nor the authors. Its curve and its coloured-point count
  would bound the cut-off in (difference, p) space. Not attempted here.
- **Running Perseus** on the deposited matrix at the published settings.
- **The authors**, for the threshold, the randomisation count and the population.

Tested and exhausted: the FDR rule family, the s0 axis, the imputation grid, the
permutation scheme, the estimator, the unit (aggregate and row level), the
population (searched, not fitted), the supplements, and the paper's own
peptide-count constraint.
