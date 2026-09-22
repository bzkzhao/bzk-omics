# CHECKS — the downshift recovered twice, and MOESM5 matches nothing deposited

**Run 2026-09-22 on bzk's machine.** Script: `notes/scripts/diagnose_round16.py`,
log `notes/logs/round16.txt`. Not an independent path: the same instruments the
registered runs use. **Attempt 3's registered verdict stands.**

Vocabulary as fixed in `walk/CHECKS-membership-and-corrections.md`: **withdrawn**
= false as stated; **superseded** = correct under a disfavoured choice.

---

## 1. The authors' downshift, recovered twice by routes sharing no inputs

The agreement reported in round 15 (+1.055 observed against +1.047 predicted) is
informative only if the prediction moves with the parameter. It does:

| downshift | predicted median gap (log2) | consistent with +1.055? |
|---|---|---|
| 1.0 | +0.291 | no |
| 1.4 | +0.656 | no |
| 1.6 | +0.848 | no |
| **1.7** | +0.935 | **yes** |
| **1.77** | +1.000 | **yes** |
| **1.8** | +1.027 | **yes** |
| **1.9** | +1.129 | **yes** |
| 2.0 | +1.223 | no |
| 2.5 | +1.728 | no |

Bootstrap standard error on the observed median: 0.077. Column SDs 1.61 to 1.92.

| route | evidence used | recovered downshift |
|---|---|---|
| readout C | the drawn **cell values** in S1, referenced to the deposit's column statistics | 1.76 – 1.78 |
| this check | the published **fold changes**, through the gap against their measured-only part | 1.70 – 1.90 |

**The two bands overlap on Perseus's default of 1.8, and share no inputs.** This
supersedes round 15's framing: the finding is not that an observation matched a
simulation, but that **the authors' imputation parameter is recoverable from
their published numbers by two independent routes**.

**What it does not identify:** the realisation, or any distribution with the same
first moment. The claim is *consistent with a downshift near 1.8 column SDs*, not
*this draw produced this table*.

## 2. MOESM5's values match nothing deposited

Round 15c compared MOESM5 against the six IFN columns only. The deposit also
holds untreated samples (`KO_P_*`, `WT_P_*`), and a correlation of 0.707 is the
shape of a comparison between different conditions in the same cell lines, so
each published column was correlated against **all fourteen** deposited LFQ
columns and the mapping read off the argmax:

| published column | best match | r | second | r |
|---|---|---|---|---|
| WT_IFN-1 | KO_P_2hGradient1 | 0.747 | WT_INF_P_2hGradient1 | 0.742 |
| WT_IFN-2 | KO_P_2hGradient1 | 0.737 | WT_INF_P_2hGradient1 | 0.727 |
| WT_IFN-3 | KO_P_2hGradient1 | 0.738 | WT_INF_P_2hGradient1 | 0.736 |
| KO_IFN-1 | KO_INF_P_2hGradient1 | 0.719 | KO_INF_P_2hGradient2 | 0.716 |
| KO_IFN-2 | KO_INF_P_2hGradient1 | 0.718 | KO_INF_P_2hGradient2 | 0.716 |
| KO_IFN-3 | KO_INF_P_2hGradient1 | 0.721 | KO_INF_P_2hGradient2 | 0.719 |

**The argmax is flat and incoherent.** Every correlation lies between 0.716 and
0.747, with best and second separated by 0.003 to 0.010; all three WT columns
point at a KO sample, and all three KO replicates point at the same single
column. That is a spurious argmax over columns that all correlate at about 0.72
with anything protein-abundance-shaped.

**So the untreated-columns hypothesis is tested and fails**, and the narrow
statement stands: **the values under a header reading "LFQ intensity" match no
reading of any deposited column**, and 17 of the table's 323 claims name protein
groups the deposit does not contain. Our copy is content-hashed and reproduced
Data Table S1 and MOESM4 exactly, so this is a property of the published record,
not of the copy.

## 3. Three corrections carried from review

**The census does not depend on the imputation method.** It rests on which cells
the deposit lacks, so 95% would hold if the authors had imputed by any method,
or by hand. **That independence is why the headline survives every unresolved
question about Perseus** — it should be stated wherever the census is reported.

**The protein comparison points at the general claim, not the PTM-specific one.**
Reported earlier as "the cleanest support for the PTM-specific line". Corrected:
**8 of 25 published protein claims (32%) rest on a wholly drawn arm**, which is
large for a table nobody would describe as imputation-dependent. The site/protein
contrast (95% against 44%) is real and decisive at this denominator, but the
protein arm's own figure strengthens the general reading — that this is a
property of label-free quantification with imputation — over the PTM-specific
one.

**The comparison carries a quantification confound.** Site grain uses summed
intensity, protein grain uses LFQ. The two differ in grain, in enrichment **and**
in quantification, and only the first two are the intended contrast.

## 4. A defeater class this project has not named

Joining a published table to its own deposit required a hand-built sample-name
mapping: the deposit names samples `KO_INF_P_2hGradient1`, the supplement
`KO_IFN_1`. A naive join produced a **100% false census** — all 150 protein
cells reported as drawn — caught only by validating the corrected mapping
against the published values (122 of 122 within 0.01).

**No machine consumer would get that join right**, and no existing class covers
it: it is not selection, not reference identity, not analytical state, not
modifier attribution. It is the same guard that established S1's provenance,
applied a second time and again decisive. **Candidate for the taxonomy.**
