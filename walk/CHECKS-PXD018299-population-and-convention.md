# CHECKS — population, convention, and the seven claims (DESCRIPTIVE, UNREGISTERED)

**Run 2026-09-22 on bzk's machine.** Script: `notes/scripts/diagnose_round4.py`.
**Not an independent path:** the same instruments the registered run used
(`anchor_population`, `downshifted_normal`, `perseus_s0`), re-aggregated by a
separate script. **Attempt 3 stands unchanged**; nothing here is registered.

---

## D — the twelve-sample population

The deposit holds four groups of three: `KO`, `KO_IFN`, `WT`, `WT_IFN`. Which
valid-value rule across all twelve retains the published set:

| rule | rows retained | published claims retained |
|---|---|---|
| at least 3 in one of the four groups | 985 | 683 of 798 |
| **at least 2 in one of the four groups** | **1,558** | **798 of 798** |
| at least 1 in one of the four groups | 2,225 | 798 of 798 |

The strictest rule that keeps every published claim is **at least 2**. Rerunning
the IFN contrast on that population, at the default cell over 20 paired draws:

| | `joint_half` | `joint` (unhalved) |
|---|---|---|
| claims supported, median draw | 750 of 798 | 688 of 798 |
| unstable among claims with an imputed value | **163 of 758 (21.5%)** | **209 of 758 (27.6%)** |
| the seven wholly drawn claims | **0 of 7 supported** | 0 of 7 |

By imputed count, under `joint_half`: 0 imputed 40/40 supported, 0 unstable;
1 → 15/15, 0; 2 → 26/26, 1; 3 → 596/598, 43; 4 → 73/112, **112 unstable**;
6 → 0/7, 7.

**Readings (judged).**
- **The population deviation is not verdict-relevant.** 21.5% against the
  registered 21.2%. The concern that a larger matrix would loosen the threshold
  enough to matter is **measured and small**. The reviewer's mechanism is real
  but its magnitude is not.
- **H10's verdict is robust to the FDR convention.** `recurs` at 21.5% halved
  and 27.6% unhalved, against a 5% threshold. The convention moves the level,
  not the verdict.
- **The class-conditional shape is unchanged:** every 4-imputed claim is
  unstable under both conventions; the 3-imputed class stays far from the
  threshold.
- **The population does not explain the seven.** They remain unsupported.

## E — which convention returns the published count, on the authors' own values

Data Table S1 carries the authors' own post-imputation values. Placing all 798
rows and filling the rest of the matrix with our draws:

| convention | calls over the whole matrix (median of 20 draws) | published claims called |
|---|---|---|
| `joint` (Perseus's documented q-value) | **918** (888–937) | 798 of 798 |
| `per_side` | 985 (966–1,006) | 798 of 798 |
| `joint_half` (fitted on `PXD026748`) | 998 (981–1,014) | 798 of 798 |

The paper called **798**.

**Readings (judged).**
- **The seven are significant under the authors' own draw, and only under it.**
  With S1's values in place, every published claim is called, the seven
  included. Re-drawn at the same parameters, the same seven are supported in 1
  to 8 draws out of 20 (round 3, part C; D above). **Their publication is the
  realisation, not the filter and not the threshold.** This is the project's
  clearest single measurement of draw dependence.
- **The halving looks specific to the other deposit.** Unhalved `joint` comes
  closest to the published count (918 against 798); `joint_half` overshoots most
  (998). This is the first anchor-side evidence on the convention, and it points
  the way the review suspected: the factor of 2 may be an artefact of Munnur's
  run, perhaps its preserved treatment grouping, rather than a universal Perseus
  behaviour.
- **It is hybrid evidence, not decisive.** Only the 798 published rows carry the
  authors' values; the other ~760 rows carry ours, and they shape the null. All
  three conventions overshoot 798, which is what a partly-our-draw null would
  do.

## What follows

- **Attempt 3's verdict stands, and is now known to be robust** to both the
  population and the convention. Its *level* (21.5% against 27.6%) depends on
  the convention; its *direction* does not.
- **The transferred convention should be reported as probably wrong for this
  deposit**, with the unhalved figure given beside it.
- **A registered attempt 4 is not warranted by these checks.** The two
  deviations that motivated one are now measured: the population moves the rate
  by 0.3 points, and the convention moves it from 21.5% to 27.6% without
  changing the verdict.
- **Still untested:** whether preserving the treatment grouping reproduces
  Munnur's Table 3 without any halving. That would explain the factor of 2 at
  its source.
