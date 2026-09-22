# CHECKS — the FDR convention, resolved (DESCRIPTIVE, UNREGISTERED)

**Run 2026-09-22 on bzk's machine.** Scripts:
`notes/scripts/diagnose_round6.py` and `notes/scripts/diagnose_round7.py`. Not an
independent path: the same instruments the registered runs use. **Attempt 3's
registered verdict stands; this supersedes the *level* it was computed at, and
nothing else.**

---

## 1. The documented rule reproduces the anchor's own published count

Perseus documents its q-value as the mean false-positive count over
randomisations, over the observed count — our unrestricted `joint`. Scored
against each paper's own published call count, at the default cell, median over
20 seeds:

| | π₀ | mean (documented) | median (SAM) | × π₀ | × 0.5 (the fitted halving) | the paper called |
|---|---|---|---|---|---|---|
| `PXD026748` shotgun | 0.493 | 158 | 241 | **278** | 276 | 282 |
| `PXD018299` anchor | 0.205 | **781** | 783 | 1,150 | 916 | 798 |

**Readings (judged).**
- **On the anchor, the documented rule lands within 2% of the published count,
  with nothing fitted.** That is a validation on the deposit under test, which
  gate G never gave.
- **No single rule fits both deposits.** π₀-scaling fits Munnur and breaks the
  anchor; the documented rule fits the anchor and misses Munnur by nearly half.
- **So the factor of two is a property of Munnur's analysis, not of Perseus,**
  and there was never a convention to transfer. The anchor needs none.
- **Munnur's π₀ of 0.493 is the best available reading of why its output behaves
  as though the null were halved**, an ISG15 knockout moving much of the
  interferon-responsive proteome. It is a reading, not a mechanism: scaling by
  π₀ is not documented Perseus behaviour either.
- **The anchor's π₀ of 0.205** says about 80% of its rows move, which is what a
  USP18 knockout should do to an ISGylome.

## 2. The levels, like for like

On the **registered** population (2,101 rows, 791 claims), default cell, 20
paired draws:

| rule | claims supported | unstable among claims with an imputed value |
|---|---|---|
| **mean (documented)** | **673 of 791** | **209 of 751 = 27.8%** |
| × 0.5 (pre-specified in attempt 2) | 725 of 791 | 159 of 751 = 21.2% |

On the twelve-sample population the documented rule gives 27.6%, so the
population choice moves the headline by 0.2 points.

**H10's verdict, `recurs`, holds under every rule tried** (the threshold is 5%).

## 3. What supersedes what

- **The 21.2% is superseded, not withdrawn.** It is a correct computation under
  a stated convention which the anchor's own published output does not support.
  It keeps its standing as the pre-specified figure, and the audit trail is
  intact.
- **The figure to lead with is 27.8%,** computed under Perseus's documented rule
  on the registered population.
- **`walk/CHECK-PXD026748-grouping.md`'s explanatory paragraph is withdrawn.** It
  claimed the within-treatment null is stricter because the treatment effect
  stays in the spread. Measured, the two nulls are indistinguishable (99th
  percentile 0.784 against 0.811) and the call counts differ by less than seed
  noise (`joint` ranges 138 to 178 per seed). The reason is simpler: **there is
  no treatment effect to move.** PLpro was applied to lysates for 30 minutes,
  and its contrast on the shotgun matrix is flat (median |d| 0.114 against 0.258
  for genotype). The refutation of the grouping hypothesis stands; its
  explanation does not.

## 4. Ruled out along the way

- **Imputation settings.** All 18 registered settings under the documented rule
  give 144 to 169 calls on Munnur against 282. The halving is not a disguised
  imputation difference.
- **Preserved grouping** (§3 above).
- **The median estimator** fits neither deposit's published count better than the
  documented mean once both are scored: 241 against 282, and 783 against 798.

**Still open:** why Munnur's own run behaved as it did. π₀ is the best reading,
not a demonstration. Perseus's source is not public, its documentation describes
neither halving nor π₀ scaling, and a third deposit with a published call count
remains the durable test.
