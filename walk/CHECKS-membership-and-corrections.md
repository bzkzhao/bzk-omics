# CHECKS — membership, the class table, and what the documented rule does not do

**Run 2026-09-22 on bzk's machine.** Script: `notes/scripts/diagnose_round8.py`.
Not an independent path: the same instruments the registered runs use.
**Attempt 3's registered verdict stands.** Two of this project's own claims do
not, and are corrected below.

**Vocabulary, fixed here and applied throughout.** Only two words, on one axis:
- **Withdrawn** — the claim was false as stated, because the instrument or the
  reasoning was defective. A successor is noted where one exists; the word does
  not change.
- **Superseded** — the claim was a correct computation under a stated choice
  that later evidence disfavours.

"Retired" and "partial withdrawal" are not used.

---

## 1. Withdrawn: "instability lives in the 4-imputed class"

That table was computed under the halved rule. The documented rule is stricter,
so its threshold sits lower, and the boundary moves into the 3-imputed class.
Recomputed on the registered population, default cell, 20 draws:

| imputed of 6 | claims | supported, documented | unstable, documented | unstable, halved |
|---|---|---|---|---|
| 0 | 40 | 39 | 1 | 0 |
| 1 | 15 | 14 | 3 | 1 |
| 2 | 26 | 23 | 8 | 0 |
| 3 | 598 | 595 | **89** | 46 |
| 4 | 112 | **2** | 109 | 112 |

**The claim is withdrawn,** and so is the stronger claim built on it — that these
class-conditional rates are population-invariant and should be led with. Under
the documented rule the 4-imputed class supports almost nothing (2 of 112) and
the instability has moved into the canonical class. **The shape was
rule-dependent, and this project asserted it as structural.**

What survives: instability concentrates where a drawn value competes with
measured ones, and the direction of the gradient (more imputed, more fragile)
is unchanged. The *location* of the boundary is a property of the rule.

## 2. Withdrawn: "validated on the deposit under test, with nothing fitted"

Membership against the anchor's published list of 798, rather than its count:

| rule | calls | precision | recall | F1 |
|---|---|---|---|---|
| documented (mean) | 689 | 0.977 | 0.851 | 0.909 |
| halved | 822 | 0.882 | 0.917 | 0.899 |

**Neither rule reproduces the published list.** The documented rule misses 119
published claims; the halved one adds 97 the paper did not call. They are within
a point of each other on F1.

**Two further corrections to how that claim was stated.**
- **The "781 against 798" was not like for like.** 781 was the median per-seed
  call count; 689 is the number called in a majority of 20 seeds. The comparable
  figure is 689, a 14% shortfall.
- **"With nothing fitted" overstated it.** The population rule in use ("at least
  1 valid value in a group of six", or "at least 2 of twelve") was chosen
  because it retains all 798 published claims, so it is still fitted to the set
  under test. The accurate form: **no fitted FDR convention, measured imputation
  parameters, on a population still chosen to retain the published set.**

**What still holds.** The documented rule is better supported than the halving:
it is what Perseus documents, it needs no transfer between deposits, and it is
more precise (0.977 against 0.882). H10's level is **27.8%** under it, and the
verdict `recurs` holds under both.

## 3. π0 is a coincidence, not a reading

Previously filed as "the best available reading" of the other deposit's factor
of two. **Withdrawn.**
- Perseus is the same program in both runs, so any rule it implements applies to
  both. π0-scaling gives 278 against 282 on `PXD026748` and 1,150 against 798 on
  the anchor. A factor that appears only where the data make it 0.5 is not
  something the software can be doing.
- On the deposit where it fits, it is indistinguishable from the constant it
  replaces: 278 against 276 for a flat halving. It adds no explanatory power,
  only the appearance of a mechanism.
- **The estimator matters and was not stated:** Storey's 2 × mean(p > 0.5) on
  Student t p-values. With most rows moving, π0 estimates are unstable and
  estimator-dependent. The figures 0.493 and 0.205 should not be quoted bare.

## 4. Reconstructing the other deposit's inputs does not dissolve it either

Five valid-value filters × two normalisations, scored on membership against
Table 3's list under the documented rule:

| filter | normalisation | rows | calls | precision | recall |
|---|---|---|---|---|---|
| at least 1 / 2 / 3 in a group | none | 2,438 | 159 | 1.000 | 0.564 |
| at least 1 / 2 / 3 in a group | median-subtracted | 2,438 | 169 | 1.000 | 0.599 |
| at least 3 in both | none | 2,169 | 98 | 1.000 | 0.541 |
| at least 3 in both | median-subtracted | 2,169 | 102 | 1.000 | 0.564 |
| complete rows only | none | 1,512 | 140 | 0.614 | 1.000 |
| complete rows only | median-subtracted | 1,512 | 218 | 0.394 | 1.000 |

No cell reaches the published list. The filters barely bite, because nearly
every row passes them.

**Untested input:** whether Table 3 was computed from `LFQ intensity` or plain
`Intensity` columns. That is one grid axis and should be run before this line of
inquiry is closed.

## 5. The direct test is not available here

**Perseus 1.6 is a Windows desktop application; this environment is Linux with
no virtual machine.** The deposited matrix is in hand and the settings are
published, so the question — what does Perseus call on this matrix at S0 = 1 and
FDR 0.05? — is answerable in an afternoon by anyone with a Windows machine.
Every inference in rounds 5 to 8 concerns a program that could simply be run.
This is recorded so that a reader does not have to wonder why the obvious test
is missing.

## 6. Where this leaves the convention

- **Unexplained.** Grouping, the imputation settings, the median estimator, π0
  and the input grid are all excluded or insufficient.
- **The documented rule is preferred** on documentation, on precision, and
  because it requires no transfer. It is not validated: it misses 14% of the
  anchor's published list.
- **Two separable needs, previously conflated.** A **calibration** deposit needs
  only deposited data, stated Perseus settings and a published call list; shared
  authors are irrelevant. The **thesis** needs a deposit with no shared authors.
  The first is cheaper and should not wait behind the second.
