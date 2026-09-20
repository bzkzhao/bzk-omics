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
