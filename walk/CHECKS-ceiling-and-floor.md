# CHECKS — the ceiling, the misses, and what the instability figure supports

**Run 2026-09-22 on bzk's machine.** Script: `notes/scripts/diagnose_round9.py`.
Not an independent path: the same instruments the registered runs use.
**Attempt 3's registered verdict stands.** One further claim of this project's
own is withdrawn below.

Vocabulary, as fixed in `walk/CHECKS-membership-and-corrections.md`:
**withdrawn** = false as stated; **superseded** = correct under a disfavoured
choice.

---

## 1. No thresholding of this statistic reproduces the published list

F1 against the anchor's published 798, scored continuously over the factor
scaling the null count (1.0 is Perseus's documented rule, 0.5 the halved one):

| scale | calls | precision | recall | F1 |
|---|---|---|---|---|
| 0.25 | 1,102 | 0.711 | 0.990 | 0.827 |
| 0.40 | 924 | 0.814 | 0.951 | 0.877 |
| **0.50 (halved)** | 822 | 0.882 | 0.917 | 0.899 |
| 0.60 | 763 | 0.927 | 0.894 | **0.910** |
| 0.75 | 717 | 0.957 | 0.867 | 0.910 |
| **1.00 (documented)** | 689 | 0.977 | 0.851 | 0.909 |
| 1.50 | 672 | 0.987 | 0.838 | 0.906 |
| 2.00 | 651 | 0.995 | 0.819 | 0.899 |

**The ceiling is F1 0.910, and the family is flat near it.** The three rules in
contention differ by 0.001. So **the mismatch with the published list is not
about the FDR rule**: it sits upstream, in the population, the statistic's
inputs, or a filter the paper applied and did not state.

**Precision is dropped from the case for the documented rule.** The halved rule
is the documented rule with the threshold scaled, so its calls are a superset:
within that nested family the stricter member always wins precision and loses
recall. Citing 0.977 against 0.882 argued from the chosen threshold. What
remains, and is enough: the documented rule is what Perseus documents, and it
needs no transfer from another deposit.

## 2. The misses are the phenomenon, not the instrument

Of the 118 published claims the documented rule does not call:

| | claims |
|---|---|
| supported in **1 to 9** of 20 draws | **112** |
| supported in 0 draws | 6 |
| in the 4-imputed class | **110 of 118** (that class holds 112 claims) |

Measured knockout intensity: 22.71 among the missed, 23.90 among the recovered.

**Reading (judged).** The shortfall is overwhelmingly **draw dependence**, which
is the phenomenon under study, rather than misspecification. Nearly every missed
claim is one whose support the draw decides, and nearly all of them sit in the
single class where a drawn value competes with two measured ones. Reporting
"misses 14% of the published list" as an instrument failure, as this project did
last round, was the wrong reading of it.

## 3. Withdrawn: "the gradient survives both rules"

Unstable share by imputed class, 95% Wilson intervals:

| imputed of 6 | claims | documented | halved |
|---|---|---|---|
| 0 | 40 | 2.5% [0–13%] | 0.0% [0–9%] |
| 1 | 15 | 20.0% [7–45%] | 6.7% [1–30%] |
| 2 | 26 | **30.8% [17–50%]** | 0.0% [0–13%] |
| 3 | 598 | **14.9% [12–18%]** | 7.7% [6–10%] |
| 4 | 112 | 97.3% [92–99%] | 100.0% [97–100%] |

**The gradient is not monotone.** Under the documented rule the 2-imputed class
exceeds the 3-imputed class, and under the halved rule the ordering flips. The
small classes carry wide intervals, so the middle is best described as **not
ordered**.

**What survives both rules,** at the level the data support:
- claims with no imputed value are stable (0 to 2.5%);
- claims with a whole arm drawn **and** one value missing from the other arm are
  almost always unstable (97 to 100%);
- the middle is unordered.

## 4. The rule-invariant floor

| measure | claims with an imputed value (751) |
|---|---|
| unstable, documented rule | 209 (27.8%) |
| unstable, halved rule | 159 (21.2%) |
| **unstable under BOTH** | **156 (20.8%)** |

**20.8% is a floor no choice of convention removes.** It should be quoted beside
the documented rule's 27.8%.

**One measure is not usable as computed.** The log10 q spread across draws came
out at a median of 9.24, which is an artefact of the clipping floor meeting
q values of exactly zero in some draws. It is **not reported**; rank movement is
the right threshold-free instrument and has not been run.

## 5. What the instability figure is evidence for

Four conditions must hold for it to speak about the paper's own claims:

| condition | met? | why |
|---|---|---|
| imputation model | **yes** | the authors' downshift and width are measured from their own published matrix (1.76–1.78, 0.29) against the default cell's 1.8 and 0.3 |
| statistic | **yes** | the ordering matched Perseus's exactly on the other deposit's published output |
| threshold | **no** | theirs is unknown; the candidates differ by 133 calls |
| population | **no** | the rule was chosen to retain the published set |

**So the claim the evidence supports is:** *a Perseus-shaped selection, run on
this deposit at the authors' own imputation parameters, has about a quarter of
its threshold-region membership decided by the draw* — 27.8% under the
documented rule, with a floor of 20.8%.

**It is not** evidence that 28% of the paper's 798 claims would flip if the
authors reran. That needs their threshold and their population, and neither is
known.

**The claim whose evidence is complete** remains the seven: called under the
authors' own published values, supported in 1 to 8 of 20 re-draws at measured
parameters, and unsupported under every rule tried. It needs no threshold
transfer and no population argument.

## 6. A pattern in this project's own errors

Three times a sound measurement has been paired with a mechanism narrated one
level past the data:
- the **grouping explanation** (the nulls were indistinguishable);
- **π0** as a reading of the other deposit's factor of two (a data-dependent
  constant cannot be what the software implements);
- the **class-location claim**, and then its replacement, the gradient.

Each time the measurement held and the story did not. That is the failure this
project attributes to published claims, occurring in its own write-ups, and it
belongs in the limitations: **the number is durable, the reading around it is
not.**
