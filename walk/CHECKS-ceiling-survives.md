# CHECKS — the ceiling survives, and the reconstruction agrees to within the draw

**Run 2026-09-22 on bzk's machine.** Script: `notes/scripts/diagnose_round10.py`.
Not an independent path: the same instruments the registered runs use.
**Attempt 3's registered verdict stands.**

Vocabulary as fixed in `walk/CHECKS-membership-and-corrections.md`: **withdrawn**
= false as stated; **superseded** = correct under a disfavoured choice.

---

## 1. The F1 ceiling is not an artefact of the aggregation

The published list is one realisation; round 9 scored a majority over 20 draws
against it. The objection: for claims whose support the draw decides, a majority
cannot include what a single realisation can, so the ceiling might be
manufactured. Measured, per single draw:

| rule | per-seed F1, mean (range) | majority over 20 |
|---|---|---|
| documented | **0.876** (0.865–0.891) | 0.909 |
| halved | 0.846 (0.826–0.864) | 0.899 |

**The objection is refuted, and in the opposite direction:** a single draw does
*worse*, so averaging helps rather than hides. The ceiling stands.

## 2. The s0 axis buys 0.002

s0 rotates the ranking rather than sliding the cut (confirmed: moving s0 from
0.1 to 1.0 correlates the rankings at 0.988 with individual claims moving up to
347 places), so other s0 values give selections nested in nothing round 9
scanned. Per-seed mean F1 over the plane:

| s0 \ scale | 0.25 | 0.5 | 1.0 | 1.5 | 2.0 |
|---|---|---|---|---|---|
| 0.0 | 0.799 | 0.851 | 0.872 | 0.870 | 0.855 |
| **0.1 (stated)** | 0.797 | 0.846 | **0.876** | 0.878 | 0.868 |
| 0.2 | 0.800 | 0.844 | 0.871 | **0.878** | 0.872 |
| 1.0 | 0.819 | 0.835 | 0.840 | 0.838 | 0.834 |

**Ceiling over the plane: 0.878**, against 0.876 at the paper's stated s0 and the
documented scale. **No thresholding of this statistic reproduces the published
list**, and the mismatch is upstream of both the FDR rule and s0.

## 3. The disagreement is 1.1% structural, and the rest is the draw

Both sides of the membership comparison, partitioned by how many draws support
each claim:

| | claims | structural | the phenomenon under study |
|---|---|---|---|
| called but not published | 16 | **3** (supported in all 20 draws) | 13 (10–19 draws) |
| published but not called | 118 | **6** (supported in no draw) | 112 (1–9 draws) |

**Structural discordance: 9 of 791 claims, 1.1%.**

**Reading (judged).** The reconstruction **agrees with the published list to
within draw dependence, apart from about 1%**, on a population chosen to retain
that list. This supersedes round 8's blanket statement that the reconstruction
"does not reproduce the published list": that was true of the calls as
aggregated, and misleading about the agreement underneath. It is **not** a
validation claim: the population is still fitted, and the threshold is still
unknown.

## 4. Three numbers, three jobs

| measure | value | what it is |
|---|---|---|
| structural discordance | **1.1%** (9 of 791) | how far the reconstruction differs from the published selection for reasons other than the draw |
| floor across the rule family | **13.7%** (103 of 751) | unstable at every scaling from 0.25 to 2.0; no choice within the family removes it |
| documented rule | **27.8%** (209 of 751) | H10's level as reported |
| rank crossing | **32.9%** (247 of 751) | share whose rank range across draws crosses the median call boundary; needs no rule, no s0, no population argument |

**The floor is 13.7%, not the 20.8% reported in round 9.** That figure was an
intersection over two points of the family rather than the whole of it, and is
**superseded**. The two-sense caveat stands: a floor with respect to the FDR
rule, and an **underestimate** with respect to the draw count, since instability
is monotone in the number of draws and 20 is few.

Rank movement is the measure that survives every unresolved question about the
convention, and it is the largest of the three.

## 5. The limitation, restated

Round 9 recorded that three times a sound measurement came paired with a
mechanism narrated past the data. Round 9's own J then **partly reinstated** the
content of the withdrawn class-location claim: 110 of the 118 misses sit in that
class, measured rather than asserted.

So the lesson is not "do not narrate mechanisms", which no one can follow. It is
that those readings were **stated at a confidence the measurement had not yet
reached**. The mechanism was often right; the certainty was borrowed from the
number beside it. That is the sharper form of the limitation, and the useful one
for the thesis: a published claim's durable part is its measurement, and the
reading around it needs its own evidence and its own hedge.
