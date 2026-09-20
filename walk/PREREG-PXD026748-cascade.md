# PRE-REGISTRATION — PXD026748 published-claim cascade (H9s exposure)

**Registered 2026-09-20, before the generator exists or runs, at the commit that
adds this file.** Kinds follow the earlier pre-registrations: **MEASURED**
(already counted elsewhere), **DERIVED**, **JUDGED**.

**What the cascade measures.** Each of the 296 rows of Supplementary Table 1
(`41590_2021_1035_MOESM3_ESM.xlsx`,
`sha256:872371eb9877c6aa1f85e82429e8354993cd4d10c643592ff8ee14012e36a870`, pinned
in the raw store on 2026-09-20) is placed at exactly one stage:
1. join;
2. decoy/contaminant;
3. localisation;
4. ingestion;
5. presence (the paper's valid-value rule on summed intensities).

Rows that pass all five **reach the test**, and they are H9s's exposure
(`HYPOTHESIS.md` v5, §6). The significance stage is not run here, because
significance *is* the reconstruction.

**The join rule, fixed here.** The published (`Uniprot ID`, `Lysine position`)
must equal a deposit row's (`Protein`, `Position`), the razor pick. That is the
key turn 09 used before the six mismatched rows were known.
- A row matching no deposit row is lost at join.
- A row matching more than one is also lost at join, with that reason stated.

Rows lost at join are **reported with any deposit row whose `Sequence window`
equals the published window, but not recovered.** Choosing a fallback key after
seeing which rows it rescues is a selection made with the answer in hand.

---

## Registered figures

| # | quantity | registered | kind | basis |
|---|---|---|---|---|
| C1 | published rows | **296** | MEASURED | report 09, by shape against the walk record |
| C2 | rows with `Multiplicity` 1 | **296** | MEASURED | report 09 |
| C3 | lost at join | **6** | MEASURED | report 09, on the same key rule |
| C3w | join losses with exactly one window-matched deposit row | **6 of 6** | MEASURED | report 09's diagnosis table |
| C4 | lost at decoy/contaminant; at localisation | **0; 0** | JUDGED | the paper applied both filters, at the same 0.75 cut. A loss here would be a divergence the anchor showed (its D6) and this deposit should not |
| C5 | lost at ingestion | **2** | MEASURED | report 09: #122 Q9NVI7 K549 and #136 Q8NI36 K159, both refused for residue mismatch |
| C6 | lost at presence | **0** | JUDGED | every published claim was tested, so it passed the paper's rule. Summed and `___1` presence agree over all 2,187 sites (`walk/RESULT-PXD026748-multiplicity.md`, Q5) |
| C7 | **reach the test: H9s's exposure** | **288** | DERIVED | C1 − C3 − C4 − C5 − C6 |
| C8 | `Cluster` 3 rows; clusters 1a + 1b + 2 | **20; 276** | MEASURED from the publication | the paper reports 20 ubiquitin sites (cluster 3) and 276 ISG15 sites (clusters 1 and 2) |
| C8a | `Cluster` 1a rows | **118 to 135** | JUDGED | the paper's "118 sites as PLpro targets" may be cluster 1a less the 17 sites on genotype-regulated proteins. The basis is thin |
| C9 | exposure rows whose deposit row carries positive `___2`/`___3` intensity | **0 to 27**, point ~3 | JUDGED | 27 of 2,187 filtered sites (1.2%) carry any. The point estimate assumes claims are no more multiply-modified than sites in general |

---

## What a miss would mean

**C3, C5 or C3w missing.** The generator keys differently from turn 09. Find the
difference before trusting either instrument.

**C4 above 0.** A published claim sits on a deposit row that is a decoy, a
contaminant, or below 0.75. The paper states both filters, so that is a
divergence between the paper's statement and its own output, which is the
anchor's D6 appearing on a deposit where it should not.

**C6 above 0.** The summed-intensity presence rule removes a claim the paper
tested. That contradicts route A's admission on this population and must be
reported against `walk/RESULT-PXD026748-multiplicity.md`.

**C7 is the number H9s is measured against.** Whatever it measures, it becomes
the exposure, and the reconstruction's pre-registration uses the measured value,
not 288.

**No rule is adjusted to move a figure into its interval.**
