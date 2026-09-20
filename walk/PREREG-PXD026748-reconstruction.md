# PRE-REGISTRATION — PXD026748 reconstruction (H9s, the D5 measurement)

**Registered 2026-09-20, before the reconstruction exists or runs, at the commit
that adds this file.** It measures `HYPOTHESIS.md` v5's H9s on the second
deposit. Kinds follow the earlier pre-registrations: **MEASURED**, **DERIVED**,
**JUDGED**.

## Exposure (MEASURED)

**288** published claims reach the test, according to
`tests/fixtures/pxd026748_published_cascade.json`, committed immediately before
this file, and scored against `walk/PREREG-PXD026748-cascade.md`. By cluster:

| cluster | claims |
|---|---|
| 1a | 117 |
| 1b | 39 |
| 2 | 112 |
| 3 | 20 |

All 288 are P-selected, so all 288 are D5's exposure. Cluster 1a is the
publication's "PLpro targets" (D1). It is reported as a subset under the same
test, never as a separate exposure.

## The pipeline: fixed by the publication, and held constant across the family

This is the methods' GG pipeline (`notes/reports/REVIEW-ADR-0035.md`,
addendum), in the paper's order:

1. **Population.** The GG site table's rows after reverse, contaminant and
   localisation < 0.75 are removed: the adapter's `_filter`, **2,187** rows. This
   is every row the paper's pipeline saw. Rows the platform later refused at
   ingestion stay in the population, because they were in the paper's matrix;
   claims on them are already outside the exposure.
2. **Input.** The summed `Intensity {label}` for the 12 mapped samples. Route A
   was admitted by rule in `walk/RESULT-PXD026748-multiplicity.md`, and the
   divergence is declared.
3. **log2.** Zero and blank values become missing.
4. **Per-sample median subtraction,** over that sample's non-missing values.
5. **Valid-value filter.** Keep rows with at least 3 non-missing values in at
   least one of the four (genotype, treatment) groups. This is the reading
   recorded in the review addendum.
6. **Imputation.** Missing values are drawn from a down-shifted normal
   distribution, using `bzk/stats/imputation.py`'s `downshifted_normal`. This is
   **the only step the family varies.**
7. **A two-way ANOVA** of genotype × PLpro treatment, with interaction. After
   imputation every cell holds 3 values, so the design is balanced and the Type
   I, II and III sums of squares coincide. It gives three P values per row: for
   genotype, for treatment, and for the interaction.
8. **Support.** A row is supported if its smallest P value is below the
   threshold. No correction for multiple testing is applied, as the publication
   applied none.

**The ANOVA must be validated before any real data passes through it,** against
a worked example with published answers. That is a requirement on the build
turn, and without it this pre-registration is not run. The
positive controls below then test it again, on this study's own published
shotgun outputs.

## Positive controls from the same study (a gate)

**Read on 2026-09-20.** Supplementary Tables 2 and 3 of the same supplement
(`sha256:872371eb…36a870`, sheets `Table 2` and `Table 3`) publish the
**shotgun arm's** statistical outputs:
- **Table 2** lists 600 proteins from the two-way ANOVA: 209 upregulated and 391
  downregulated.
- **Table 3** gives a log2 fold change and a −log P for each of **2,438**
  quantified proteins. 282 of them are marked significant: 72 up and 210 down.
  That matches the paper's text and its Supplementary Fig. 7.

The shotgun arm ran through the same Perseus version, the same filters, the
same normalisation and the same two-way ANOVA design as the GG arm. For proteins
with **no missing values**, imputation cannot affect the result. **Those
proteins test the reconstruction's own machinery against published numbers,
before the GG arm is run.**

The shotgun pipeline, as stated in the methods:
1. Reverse sequences, contaminants and proteins only identified by site are
   removed.
2. LFQ intensities are log2-transformed.
3. Per-sample median subtraction.
4. The valid-value filter: at least 3 in at least one of the four groups.
5. Imputation.
6. The same two-way ANOVA, with P < 0.01 on any term, gives Table 2.
7. A WT vs *ISG15*−/− t-test across the six-and-six samples gives Table 3.

The input is `tests/fixtures/pxd026748_shotgun_ingest.json`'s ingested LFQ cells
for `proteinGroups.txt` (`sha256:b74a1797…f884`).

| # | control | registered | kind |
|---|---|---|---|
| PC0 | proteins passing the shotgun filters | **2,438** | MEASURED from the publication, since Table 3 lists 2,438. A miss means the protein pipeline is not the paper's, and the gate fails |
| PC1 | complete-case proteins (no missing LFQ value in the 12 samples) that are in Table 3: reconstructed log2(WT/KO) within 0.01 of the published value | **≥ 99%** | JUDGED |
| PC2 | the same proteins: reconstructed −log P within 0.05 of the published value | **≥ 99%** | JUDGED |
| PC3 | complete-case proteins: agreement between reconstructed membership of the ANOVA's P < 0.01-on-any-term set and membership of Table 2 | **≥ 98%** | JUDGED |

**What PC2 fixes, and what it does not.** PC2 settles implementation details the
methods leave open: Student's or Welch's t-test, and whether the reported P is
modified by S0. It settles them on **imputation-free proteins only**. It decides
nothing about the imputation grid, and it may choose only among a registered set
of implementations: {Student, Welch} × {S0 applied to P, S0 not applied}. The
choice is reported.

**The gate.** The GG reconstruction runs only if PC0 holds exactly and PC1, PC2
and PC3 each meet their threshold. If one fails, the failure is reported and the
GG arm does not run until it is understood. No threshold is moved.

**Not in this registration.** The shotgun proteins that *have* missing values
could be used to estimate which imputation widths and downshifts are consistent
with the published P values. That is a separate analysis, to be registered
separately if it is pursued. It cannot alter this registration's family, its
readouts or its verdict.

## The family (H9s's axes, with values fixed here)

| axis | values | basis |
|---|---|---|
| width (× observed SD) | 0.2, **0.3**, 0.4 | Perseus's default is 0.3, plus one step either side |
| downshift (× observed SD) | 1.6, **1.8**, 2.0 | Perseus's default is 1.8, plus one step either side |
| scope | **`per_sample`**, `whole_matrix` | Perseus's default is per column, plus the alternative `bzk/stats/imputation.py` supports |
| seeds | 0 to 19, `numpy.random.default_rng(seed)` | 20 per cell of the grid |

That gives **18 grid cells × 20 seeds = 360 members.** The **default cell** is
(0.3, 1.8, `per_sample`), in bold above. It is the one a reader assuming
"Perseus defaults" would pick. It is reported, but it is **not** evidence of
what the publication ran, because the publication's seed is unrecorded.

**No value in this grid is changed after the run.**

## Readouts

For each of the 288 claims, at the primary threshold:
- the share of the 360 members that support it;
- **durable** = supported in all 360;
- **underdetermined** = supported in some members but not all;
- **unsupported** = supported in none.

Each readout is also given by cluster, for the default cell alone, and at the
secondary threshold.

**Thresholds.**
- **Primary: P < 0.01**, from the methods.
- **Secondary: P ≤ 0.001**, from the supplement's caption.

**The threshold-consistency count.** In the default cell, how many claims have a
median P over seeds in (0.001, 0.01]? If the published set had been selected at
0.001, none should fall there. This count is reported and bears on which
statement selected the set.

**The whole-table count.** How many of the 2,187 rows are supported in the
default cell, as a median over seeds? The publication reports 296 sites. That
figure is reported next to this one, and it is not the exposure.

## H9s's rule, as registered in v5

- **Weakens D5:** durable ≥ 95% of exposure, which is **≥ 274 of 288**.
- **Extends D5 to imputation alone:** underdetermined ≥ 5% of exposure, which
  is **≥ 15 of 288**.
- **Neither:** some other composition of the 288. It is reported as found, and
  it decides nothing.

The first two outcomes cannot both hold, because 274 + 15 > 288.

## Registered expectations (JUDGED, with thin basis)

| # | quantity | registered | basis |
|---|---|---|---|
| R1 | durable, primary threshold | **220 to 285**, point ~260 (90%) | only imputation varies; imputed values mostly land in the groups where a site is absent, which is where these claims' effects live |
| R2 | underdetermined, primary threshold | **3 to 60**, point ~20 (7%) | claims near P = 0.01 flip with the draw |
| R3 | unsupported in all 360, primary threshold | **0 to 30**, point ~8 | effects the paper's own draw may have favoured |
| R4 | whole-table supported rows, default cell | **240 to 360**, point ~300 | the publication's 296, with the platform's population differences |
| R5 | threshold-consistency count | **reported, not predicted** | it measures which of the paper's two thresholds the set is consistent with, and the reviewer has no basis for a number |

**Which H9s outcome the reviewer expects:** the point estimates put the durable
fraction near 90% and the underdetermined fraction near 7%. That would be
*"extends D5 to imputation alone"*, **narrowly**. The expectation is uncertain,
and it is registered so that it can be wrong.

## Declared divergences and carried items

- **A fourth statement of the search database.** The Reporting Summary (MOESM2)
  says *"release 2020_06 including isoforms and unreviewed sequences"*. The
  methods say January 2021, with 20,621 sequences. The deposit's FASTA path sits
  under `01_2021`. The deposit governs, as before, and this does not bear on the
  reconstruction.

- **Summed intensities, not `___1`.** They diverge for 27 of the 2,187 rows. One
  claim among the exposure sits on such a row (the cascade fixture's
  `reaches_test_with_positive_multiplicity_column` = 1), and it is reported
  individually.
- **22 cells fail the multiplicity sanity check.** They are unexplained and
  carried.
- **The imputation difference between summed and expanded columns** was judged
  negligible and not measured.
- **The published run's own seed and parameters are unknown.** No member of the
  family is claimed to be the publication's run.

**No rule, threshold or grid value is adjusted after the run.**
