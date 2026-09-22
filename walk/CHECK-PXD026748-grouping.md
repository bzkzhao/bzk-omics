# CHECK — does preserving the treatment grouping explain the halving? (DESCRIPTIVE, UNREGISTERED)

**Run 2026-09-22 on bzk's machine.** Script:
`notes/scripts/diagnose_grouping_v2.py`. Not an independent path: it scores a
restricted null with the same `_statistic` and `_q_values` the registered runs
use. **No registered verdict, pre-registration or committed fixture is touched.**

## The question

Attempt 2 fitted a halved null count (`joint_half`) to reproduce `PXD026748`'s
published Perseus calls, and attempt 3 transferred it to the anchor. Perseus's
documentation defines its q-value with no halving. An adversarial review
proposed a mechanism: Munnur's shotgun run compares WT against *ISG15*−/− across
twelve samples with PLpro treatment nested inside genotype, so if that run used
**"preserve grouping in randomizations"**, permutations would exchange labels
only within a treatment. That would explain the factor of two there, and it
would not transfer to the anchor's unnested 3-against-3 design.

## The result: it does not explain it

The strata read as expected: three WT and three *ISG15*−/− per treatment, with
399 non-identity within-treatment relabellings available, of which 250 were
drawn. Scored against Table 3 on complete-case proteins, 20 seeds, majority
call:

| null | calls | precision | recall | F1 |
|---|---|---|---|---|
| `joint`, unrestricted (Perseus's documented q) | 159 | 1.000 | 0.500 | 0.667 |
| **`joint_half`, unrestricted (the fitted convention)** | **276** | **1.000** | **0.965** | **0.982** |
| `joint`, within-treatment null | 150 | 1.000 | 0.465 | 0.635 |

Table 3 calls 282.

**Restricting the null makes it stricter, not looser.** Within-treatment
relabellings keep each treatment balanced across the two pseudo-groups, so the
treatment effect never enters the null's group means, the null statistics come
out larger, and the FDR rises. Calls fall from 159 to 150. The hypothesis needed
the opposite.

## Where the convention stands, on both deposits

| | halved | unrestricted `joint` |
|---|---|---|
| `PXD026748`, against Table 3's 282 calls | 276 (recall 0.965) | 159 (recall 0.500) |
| `PXD018299`, against the paper's 798 calls, on the authors' own values | 998 | 918 |

**Readings (judged).**
- **The halving is an empirical fit to one deposit's output with no mechanism
  behind it.** Grouping is now ruled out, and version, s0, FDR level and design
  were already different between the deposits without explaining it.
- **The two deposits pull in opposite directions.** Munnur needs a looser rule
  than Perseus documents; the anchor, if anything, a stricter one.
- **Perseus's documented q-value is the unrestricted `joint`.** The deposit
  requiring the adjustment is the anomalous one, and the adjustment should not
  be carried across deposits as though it were Perseus's behaviour.

## What follows for reporting

The anchor's figures should be given under **both** rules, with the unhalved one
at no less standing than the halved:

| | halved (registered) | unrestricted `joint` |
|---|---|---|
| claims unstable, among those with an imputed value | 21.2% registered; 21.5% on the twelve-sample population | 27.6% |
| claims supported, median draw | 725 of 791; 750 of 798 | 688 of 798 |

**H10's verdict, `recurs`, holds under both** (the threshold is 5%). What the
convention moves is the level, not the direction. The registered figure keeps
its standing as the pre-specified one; it no longer keeps it alone.

**Still open:** why Munnur's output needs the halving. Perseus's source is not
public, its documentation describes no such rule, and grouping is now excluded.
The remaining routes are the authors, the software's own randomisation count, or
another published Perseus output to test against.
