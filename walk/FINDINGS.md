# How much of a published PTM claim set is fixed by its methods?

**Two deposits, reconstructed from their raw data: PXD018299 (Pinto-Fernández
et al., *Br J Cancer* 2021) and PXD026748 (Munnur et al., *Nat Immunol* 2021).**

Neither paper states how it imputed its missing values. On both, a substantial
minority of published claims sit close enough to the significance line that the
imputation's random draw decides them. On the first — the only one that
published its post-imputation matrix — something stronger can be measured: what
the published numbers themselves are made of.

**What goes in this document:** a result appears here if it survives without our
reconstruction of the paper's pipeline, or if it is needed to defend a result
that does. Everything else — fifteen rounds of convention, population and
threshold work, and every claim withdrawn along the way — is in the repository
at `bzkzhao/bzk-omics`, under `walk/` and `notes/`.

---

## 1. Ninety-five per cent of the published effect sizes contain a value the authors drew

Data Table S1 of the first paper has no gaps. Its values are log2 of the
deposited site table, unnormalised and rounded, which means **every cell the
deposit does not provide is an imputed value**. Counting across the whole
published table:

| | claims |
|---|---|
| no drawn cell | 40 |
| some drawn, both arms still measured somewhere | 43 |
| **an entire arm drawn, no measured counterpart** | **715** |
| **published fold change contains a drawn value** | **758 of 798 (95%)** |

Among the 43 where a measured-only fold change can still be computed, the
published figure **exceeds** it in 41 cases, by a median of **1.055 log2 units**
— about a doubling.

**This needs nothing reconstructed.** It compares the published table against
the deposit, and it would hold whatever method produced the missing values,
including by hand. That independence is why it stands while everything about the
paper's selection remains contested.

**It is not a claim that the sites are absent or the effects unreal.** A drawn
value is the analysis's estimate of an unmeasured quantity. The finding is the
rate at which published magnitudes rest on such estimates.

## 2. The imputation setting is recoverable from the published numbers, twice

| route | evidence | recovered downshift |
|---|---|---|
| the drawn cell values, against the deposit's column statistics | supplement + deposit | 1.76 – 1.78 |
| the published fold changes, through their gap against the measured-only part | supplement + deposit | 1.70 – 1.90 |

The second is informative because the prediction moves sharply with the
parameter: a median gap of +0.29 at a downshift of 1.0 and +1.73 at 2.5, against
an observed +1.055 with a bootstrap standard error of 0.077. **The two bands
share no inputs and overlap on Perseus's default of 1.8.**

This identifies a setting near 1.8 column standard deviations. It does not
identify the particular draw, and the seed is not recorded anywhere.

## 3. Seven published claims have no measurement in the contrast they were tested in

Their intensities sit only in the untreated samples, so all six values entering
the tested comparison are imputed. The sites are real — each is measured without
interferon, with ordinary localisation and identification scores. What is
generated is the quantity the claim was tested on.

**Under the authors' own published values, every one is called. Re-drawn at the
recovered parameters, they are supported in 1 to 8 draws out of 20.** Their
publication is the realisation, not the filter and not the threshold.

## 4. The same experiment's protein claims are a third as likely to rest on a drawn arm

The same samples, lab and software, without PTM enrichment: 25 published protein
claims, joined to the deposit under a mapping confirmed by 122 of 122 comparable
cells.

| | site claims (798) | protein claims (25) |
|---|---|---|
| contain a drawn cell | 95% | 44% |
| rest on a wholly drawn arm | 90% | **32%** |

The contrast is real and its intervals do not come close to touching. But 32% is
a large figure for a table nobody would describe as imputation-dependent, and it
points at the general reading: **this is a property of label-free quantification
with imputation, which PTM enrichment intensifies rather than creates.**

Three caveats: the denominator is 25; the grains differ in quantification
(summed intensity against LFQ) as well as in enrichment; and a second published
protein table could not be used, because its values match no reading of any
deposited column (§8).

## 5. Selection instability, with its conditions stated

Recomputed under Perseus's documented FDR rule, at the recovered imputation
parameters, over 20 paired draws:

| | |
|---|---|
| published claims whose support changes across draws | **210 of 791 (26.5%)** |
| the same at 100 draws | 38.3% |
| floor across the whole FDR rule family, at 20 draws | 13.7% |

**Four conditions must hold for this to speak about the paper's own claims. Two
are met and two are not:**

| condition | met | why |
|---|---|---|
| imputation model | **yes** | recovered from the authors' published values, twice |
| statistic | **yes** | its ordering matched the other paper's published Perseus calls exactly — established on that deposit's Supplementary Table 3, the only published table either paper provides that carries per-row test statistics |
| threshold | **no** | theirs is unknown; candidate rules differ by 133 calls |
| population | **no** | our filter was chosen to retain the published claim set |

So the claim is: **a Perseus-shaped selection, run on this deposit at the
authors' own imputation parameters, has about a quarter of its threshold-region
membership decided by the draw.** It is not a claim that a quarter of the
paper's list would flip if the authors reran.

**The reconstruction agrees with the published list to within the draw.** Of 16
claims we call that the paper did not, 3 are supported in every draw; of 118 the
paper called that we do not, 6 are supported in none. Structural disagreement is
**9 claims of 791 at 20 draws, 4 at 100 draws** — and it falls as draws rise
while instability rises, so neither figure means anything without its draw count.

## 6. A claim can lose support because of draws made for other claims

One published claim (ATP1A1 K605) is measured in all six columns, so its
statistic is frozen across draws at +2.664. Its q nonetheless moves between
0.0144 and 0.0177 and never reaches the 0.01 cut: **the draws made for other
rows move the shared threshold underneath it.**

Across all 40 fully measured claims, one is moved across the cut and the q
ranges are small (median 0.0015). The rate is design-specific — it scales with
how much of the matrix is drawn and how crowded the threshold region is — and
here it is 1 in 40, with an interval of roughly 0.1% to 13%.

**The mechanism matters more than the rate.** It means "this claim is fragile"
is never a well-formed statement: fragility is a property of a claim *in a
matrix*. No existing defeater class covers support lost through data about other
claims, and the mechanism reaches any analysis using a shared FDR threshold, not
only PTM work.

## 7. Unstated is not the same as undetermined

The first paper states neither its imputation nor its valid-value filter. But it
published its post-imputation matrix, so its imputation parameters are
recoverable (§2) and its drawn cells are identifiable (§1). The second paper
publishes no per-replicate values, so the same step is not recoverable there at
all.

**What makes an analytical step undetermined is not that the methods omit it,
but that no published artefact pins it down.** That distinction is actionable:
an author who deposits or publishes the matrix their statistics ran on makes
their unstated steps recoverable, whatever their methods section says.

**It is also a precondition for this work.** The census of §1 needs three
things: a published post-imputation matrix, a deposit at the same grain, and a
join that validates on measured cells. Most published PTM analyses supply the
second and not the first.

## 8. Two negatives that cost real tests

**A supplementary table headed "LFQ intensity" whose values match nothing
deposited.** Correlating each of its six columns against all fourteen deposited
LFQ columns gives a flat, incoherent argmax (every r between 0.716 and 0.747;
all three wild-type columns pointing at a knockout sample). 17 of its 323 claims
name protein groups the deposit does not contain. Our copy is content-hashed and
reproduced the other supplements exactly.

**The paper's stated count of 2,341 identified peptides cannot be reproduced.**
Fifty-four filter combinations over localisation and score give 1,171 to 2,359
distinct modified peptides, and none is 2,341. On this axis the published record
is exhausted, which is now evidenced rather than assumed.

## 9. A defeater class that bites machine consumers directly

Joining the published protein table to its own deposit required a hand-built
sample-name mapping: the deposit names samples `KO_INF_P_2hGradient1`, the
supplement `KO_IFN_1`. **A naive join reported every one of 150 cells as drawn —
a 100% false census — caught only by validating the corrected mapping against
the published values.**

An automated join on column names gets it wrong, and no existing class covers
it. It is the same guard that established the supplement's provenance, applied a
second time and again decisive.

## 10. The second deposit

Reconstructed under its own named test (a two-way ANOVA at P < 0.01), 288 of its
296 published site claims reach the test. **114 of 288 (40%) change support when
the imputation is re-drawn at default settings**, and the effect is present in
every one of 18 parameter settings tried.

Two registered tests on it:
- claims the paper flags as also found in an earlier *in vivo* study are more
  often durable (49% against 30%), and the gap survives stratification by
  missing-value count (+0.15, +0.30 and +0.15 across strata), so the
  instrument's defeats are not only noise. That study shares an author and a
  method with this one, so it is within-lab reproduction, not independent
  corroboration;
- **site claims are not more fragile per claim.** At equal missingness the
  protein rates run at or above the site rates (55% against 42% at one to two
  missing values; 80% against 71% at six to eight), so the difference between
  grains is exposure rather than fragility.

**The census cannot be run here**, for the reason in §7: no per-replicate values
are published.

## 11. Limitations

- **The two deposits share authors.** Everything here is recurrence within one
  group's practice. A third deposit with no shared authors is the outstanding
  requirement.
- **The FDR convention that reproduces the second deposit's published output
  remains unexplained.** Preserved grouping, all 18 imputation settings, the
  median estimator, a null-proportion scaling and a grid over that deposit's own
  filters were each tested and each failed. The documented rule is used here, and
  the verdict holds under every rule tried. Perseus itself was not run: it is a
  Windows application and this work ran on Linux.
- **The protein comparison rests on 25 claims.**
- **This project made the error it studies.** Several times a sound measurement
  was paired with a mechanism narrated one level past the data, and the
  measurement held while the reading did not. One example: a comparison of the
  published table against the deposit at a tolerance of 1e-6, against a
  spreadsheet rounded to five digits, produced a confident and false conclusion
  that the two came from different processing. Every withdrawal is recorded in
  the repository. **The durable part of a published claim is its measurement;
  the reading around it needs its own evidence and its own hedge.**

## 12. Reproducibility

Every figure has one home in `bzkzhao/bzk-omics`. Each registered analysis was
pre-registered in a committed file before it ran (`walk/PREREG-*`), is scored
against that registration (`walk/RESULT-*`), and carries a committed fixture with
replay tests. Every descriptive check carries its script (`notes/scripts/`);
those from round 13 onward also carry their committed output (`notes/logs/`),
and the earlier ones are reproducible by rerunning the script against the
content-hashed raw store. Corrections and withdrawals are in
`walk/CORRECTION-*` and in the check documents, not silently amended.
