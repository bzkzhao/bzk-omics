# RESULT — H5c and H9p on PXD026748 (`HYPOTHESIS.md` v6 §5)

**Run 2026-09-20 on bzk's machine, after registration.**
- **Registration:** both hypotheses in `HYPOTHESIS.md` v6 at `12f0885`, unchanged
  in v7 at `c48d099`.
- **Instrument:** `python -m bzk.sources.pxd026748_h5c_h9p`, built in turn 17
  (`12ca971`) and run at `fb9f123`.
- **Output:** `tests/fixtures/pxd026748_h5c_h9p.json`. That is the figures'
  machine-readable home; this document is the scoring.

**Provenance.** The fixture records `working_tree_clean: false`, from untracked
files only, as with the reconstruction run. Its fixture-consistency check
recomputed the reconstruction's counts (111 durable, 177 underdetermined,
0 unsupported), and they equal the stored ones.

---

## H5c — corroboration by citation, against durability

| | flagged (also found *in vivo*) | unflagged |
|---|---|---|
| ISG15 claims reaching the test | 126 | 142 |
| durable at P < 0.01 | 62 (**49.2%**) | 43 (**30.3%**) |

- **Difference: +0.189.** The registered threshold was at least +0.10.
- **Verdict: discriminates.**
- **The population:** clusters 1a, 1b and 2, 268 claims. Cluster 3's 20 claims
  are excluded, as registered.
- **The flag:** the column reads 131 `x` against 165 empty across all 296 rows.
  That is 128 among ISG15 claims, of which 126 reach the test.

**The declared confound, descriptive only and never in the verdict.** Missing
values per claim, out of 12:

| missing values | flagged | unflagged |
|---|---|---|
| 0 to 2 | 20 (16%) | 16 (11%) |
| 3 to 5 | 15 (12%) | 30 (21%) |
| 6 to 8 | 53 (42%) | 45 (32%) |
| 9 | 38 (30%) | 51 (36%) |

**Reading (judged).** Flagged claims are somewhat less often at the maximum of 9
missing values, and somewhat more often nearly complete, so part of the
difference could be abundance rather than truth. The distributions overlap
heavily, and a difference of +0.19 is unlikely to be explained by this shift
alone. But a stratified comparison was not registered, and running one now would
be a post-hoc analysis. **What H5c establishes:** the instrument's durability
tracks independent, citation-level corroboration in the expected direction. That
is evidence its defeats are not noise. It is **not** a filled C0, which requires
corroboration measured on both sides.

---

## H9p — D5 at protein grain

| | protein grain (Table 2) | site grain (Table 1) |
|---|---|---|
| exposure | 600 (all joined, all reach the test) | 288 |
| claims with at least one missing value | 185 | 270 |
| underdetermined among those | 128 | 177 |
| **conditional rate** | **U_p = 0.692** | **U_s = 0.656** |

**The registered thresholds:**
- particular to site data at U_p ≤ 0.328;
- general to imputation at U_p ≥ 0.524.

**Verdict: general to imputation.**

**Descriptive, never in the verdict.**
- The unconditional rates are protein 21.3% (128 of 600) and site 61.5% (177 of
  288).
- Complete rows number 415 of 600 proteins, against 18 of 288 sites.

**Reading (judged).** Once a claim's row has a missing value, a protein claim is
as imputation-dependent as a site claim. The large gap between the unconditional
rates comes almost entirely from **exposure**: 94% of the site claims carry
missing values, against 31% of the protein claims. So on this deposit, PTM site
claims are more affected by imputation because they are far more often built on
missing values, and **not** because a site claim with missing values is more
fragile than a protein claim with missing values.

**For the thesis.** H9p's registered wording stands: the imputation effect is
general to the step, not particular to site data. A PTM-specific argument cannot
rest on per-claim fragility. It can rest only on exposure: site claims, and
absence-defined claims in particular, carry missing values far more often. That
exposure difference is descriptive here and was not registered.


---

## Addendum, 2026-09-20 — post-hoc checks and two corrections (UNREGISTERED)

Added after an adversarial review of the findings document. **Nothing here changes
either registered verdict.** The text above is left as written, and this section
supersedes it where they disagree.

**1. The stratified comparison declined above was later run, as a descriptive
check.** The reading above says running one *"would be a post-hoc analysis"*. It
is one, and it is labelled as such. Script:
`notes/scripts/describe_h5c_h9p_strata.py`, which reads only
`tests/fixtures/pxd026748_h5c_h9p.json`.

```
H5c — durable share, flagged minus unflagged, within missingness strata (clusters 1a, 1b, 2)
   0-5 missing: flagged 35, unflagged 46, difference +0.150
   6-8 missing: flagged 53, unflagged 45, difference +0.297
     9 missing: flagged 38, unflagged 51, difference +0.147
  weighted by stratum size: +0.203
H9p — underdetermined share within missingness strata, proteins against sites
   1-2 missing: proteins 30 of 55 (55%) | sites 10 of 24 (42%)
   3-5 missing: proteins 43 of 63 (68%) | sites 29 of 46 (63%)
   6-8 missing: proteins 44 of 55 (80%) | sites 79 of 111 (71%)
    9+ missing: proteins 11 of 12 (92%) | sites 59 of 89 (66%)
```

- **H5c:** the corroboration gap survives the declared missingness confound in
  every stratum. Abundance acting through measured intensity is not tested.
- **H9p:** at equal missingness, protein claims are at least as
  imputation-dependent as site claims. This supports the exposure reading above.

**2. The flag is not independent corroboration.** The reading above calls it
*"independent, citation-level corroboration"*. Zhang et al. 2019 shares an author
with the publication (F. Thery). The publication's GG search strategy was based on
that study's method, and both appear to come from the Ghent group. **The flag is a
within-lab reproducibility signal, in mouse.** H5c therefore shows that durability
tracks reproduction within one lab's practice, not corroboration in general. The
wording *"its defeats are not noise"* becomes *"not only noise"*.

**3. The timing.** H5c and H9p were registered in v6 (11:37 UTC) after the
reconstruction fixture holding every claim's durability had been committed (11:23
UTC), and with the flag column visible in the published table. The join had not
been run. They were **pre-specified, not blind**.

**4. The exposure argument has a design confound.** Site claims carry missing
values more often partly because this experiment creates true absences: the
deconjugase strips the conjugate, and the knockout removes ISG15. So *"a
PTM-specific argument can rest only on exposure"* needs a further condition. It
would have to show high exposure outside deconjugase and knockout designs.
