# REVIEWER HANDOFF — 2026-10-02

**Public version.** Part of this session's work used unpublished data. That work is recorded
locally and is not described here. Line references are to `main` at `3a165a4` (ONTOLOGY.md v1.41,
last reviewed 2026-08-31).
**Re-verify them against the current commit before citing.**

---

## 1. Where things stand

| Item | State |
|---|---|
| `main` | `b960c9a` at handoff; this file is the only addition from this session. Line references were verified at `3a165a4`. ONTOLOGY.md is unchanged between the two (`b960c9a` touches only `walk/`) |
| Untracked | `notes/prompts/22-walk-two-route-independence.md`. Belongs to the walk line (`b960c9a`), which is still moving. Outside this work's scope |
| PXD055843 ingestion | Still **blocked** on the PI's answer about imputation on S1_TP (unchanged) |

## 2. Decisions taken this session

1. **IP-MS enters as option B.** No `EnrichmentObservation` type. IP-MS data are `ProteinObservation`s
   from samples carrying a role (IP / control / input) and a bait. "Enriched" is a
   `DifferentialResult` on an IP-vs-control `Contrast`. The `isg15_interactome_concordance` basis
   points at that result. Rationale: enrichment needs a control by definition, so it is a
   comparison, not a measurement. Whether a protein counts as enriched depended on which analysis
   ran, which is a property of a result. **Cost accepted:** the separation of IP values from
   abundance values is an invariant, not a type, so it needs a machine-checkable guard.
   **Not yet recorded as an ADR.**
2. **Design against public data first.** Unpublished data stays local. Nothing from it enters the
   public repository.
3. **Within a deposit before across deposits.** PXD018299's ISG15 interactome and diGly sites come
   from the same HAP1 USP18-KO cells: the clean concordance case. PXD055843 (HeLa, siUSP24) gives
   a cross-deposit comparison, a separately labelled, weaker claim. The voided R1 join failed
   exactly this way.
4. **Demo choice.** PXD055843 for familiarity: DIA-NN → Perseus 1.6.2.3, permutation FDR, n = 3,
   the same pipeline as the group's current work. PXD018299 for the concordance logic.

## 3. Test 1 — `perseus_s0` against Perseus (method findings only)

The registered verdict and its correction are in a local record. Method findings: `perseus_s0`
reproduced the calls of a Perseus 1.6.2.3 session file (`.sps`, not public) under the
**documented** FDR rule (`joint`), not the halved one. Perseus behaves as if it excludes the
identity and mirror relabellings. "`joint`, trivial excluded" and "`per_side`, mirror kept" both
fit, and this test cannot separate them. **The halving belongs to PXD026748 (Munnur), not
PXD018299.** The reviewer misattributed it in the local record. A committed correction governs;
its audit is open.

**Still open:** why Munnur's own analysis needed the halving (existing reading: π₀ = 0.493).
**Instrument defect:** the Test 1 checker saved called rows for a pre-chosen variant
(`joint + random`) that called nothing. Any rerun should save rows for every passing variant.

## 4. Ontology gaps found (verified at `3a165a4`)

**G1. I15's "substantially imputed" rule misses whole-arm imputation** (l.962). The threshold is
*more than half* of a result's values. A 2-vs-2 result with one arm entirely imputed is exactly
half (2 of 4), so it is not flagged. Yet it compares measured values with generated ones. Position
matters, not only count. **Placement undecided:** its own ADR first, or folded into the enrichment
design (step 2 below). It already applies to data in the graph.

**G2. Imputation is counted on the observation, but imputation belongs to the analysis.**
`SiteObservation.n_imputed` (l.428, l.849), while `Imputation` attaches to `Analysis` (§6.5).
One observation imputed differently by two analyses cannot be represented. `ProteinObservation`
has no imputed count at all, which is the grain IP-MS lives at.

**G3. No vocabulary for enrichment designs.** `Sample` (l.384) has no role or bait.
`Experiment.modality` (l.380) has no IP-MS value. Today an IP's intensities would be
indistinguishable from whole-cell abundance in `protein_values`.

**Consequent edits for the design step:** the headroom row (l.539) and the deferral sentence
(l.684) both name `EnrichmentObservation`. Under option B both are superseded, and l.684's block on
offering the concordance basis lifts only when the B machinery exists.

## 5. Concordance — the design constraint settled in principle

Comparing an IP with diGly sites gives **four** outcomes, not two:

| Pattern | Reading |
|---|---|
| IP-enriched **and** a site that rises in KO + IFN | agreement → `isg15_interactome_concordance`, `probable` |
| IP-enriched, no site | not a contradiction (non-covalent binder, or site missed) |
| Site rises, not IP-enriched | weak at most (Ub/NEDD8 site, or IP missed it) |
| Measured well in both, IP points the other way | the only real contradiction |

**Absence counts against nothing unless it was measured.** "Measured well" must be defined
**before** anyone sees which proteins fall where: it is a pre-registration item, not a design
choice made after the data.

## 6. Caveats for the public-data work

1. **Both deposits are the PI's lab's.** Surprising per-protein results (e.g. a published target
   failing concordance within its own deposit) go to the PI first, before any demo.
2. **Supplementary tables may be hits-only.** PXD018299's BJC tables were significant-UP subsets
   with no per-row statistics. If PXD055843 S3 is the same, it cannot support the "measured well"
   condition, and PXD018299's raw `ISG15_interactome.xlsx` becomes the only complete IP table.
3. **PXD055843's imputation block may extend to S3.** Check S3 for the same question, so it does
   not stall in the same way.
4. **Environment.** PRIDE is not reachable from the reviewer chat's container. The survey must run
   in Claude Code's container or on bzk's Mac.

## 7. Next actions, in order

1. **Survey — measurement only, no schema change.** Prompt in the usual form: receipt check →
   measure → report, nothing bundled. For each public IP table (PXD018299 `ISG15_interactome.xlsx`;
   PXD055843 Supplementary Data S3), record:
   - Perseus export or raw search output (decide by type-prefix stamp, never by a statistics
     column)
   - columns, samples, the control, replicates per group
   - **full table or hits only**
   - missingness, and **any sign that imputation ran**
   - for PXD018299, whether a Perseus counterpart exists among the BJC supplementary tables
   Findings go to dated homes.
2. **Design.** One ADR for option B, superseding the headroom row. ONTOLOGY amendments *before*
   code: sample role + bait, an IP-MS modality, the no-mixing-of-roles invariant, G2, and G1 if
   folded in.
3. **Pre-register the concordance measurement** on PXD018299: the four categories, the "measured
   well" rule, and predictions.
4. **Code.**

## 8. Carried, not this work's scope

- The two unseparated Perseus mechanisms (§3). Separating them needs ≥ 3 replicates per group.
  PXD018299's earlier runs are the candidate.
- Open questions on the unpublished data, recorded locally.
