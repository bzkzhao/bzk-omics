# ROADMAP.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 0.7 |
| Last reviewed | 2026-08-06 |
| Depends on | `VISION.md`, `ONTOLOGY.md`, `ARCHITECTURE.md` |
| Authoritative for | Scope, milestones, deferrals |

---

## v0.1 — target: four weeks, part-time

The goal is not a usable product for other people. It is a working end-to-end path from a real diGly file to a cited, provenanced, honestly-labelled result, proving the ontology survives contact with real data.

### In scope

**Build targets.** Real datasets, named, from the collaborating group:

| Accession | Content | Adapter |
|---|---|---|
| PXD018299 | USP18-dependent ISGylome — HAP1 WT vs USP18 KO ± IFN; GlyGly peptidome, matched proteome, ISG15 interactome | MaxQuant (archival) |
| PXD064305, PXD064246, PXD064445, PXD064479, PXD064517 | USP18 inhibition in TNBC — MDA-MB-231 and 4T1, cell and tumour tissue, human and mouse | DIA-NN 2.0 |
| PXD043553 | USP16 ISG15 cross-reactive DUB | to confirm |

The 2025 deposits are whole-proteome and simpler to ingest; start there and prove the pipeline before attempting site-level data.

**Capabilities**

- Ingestion via the adapter contract, treating local and PRIDE datasets identically. Order: **DIA-NN** (near-certain for proteome under A1; unblocks PXD064305 immediately), **MaxQuant** (required for PXD018299 regardless of what the lab chooses — the only confirmed matched-proteome diGly fixture), **FragPipe** (hedges A2). Spectronaut on demand only. This order is correct under every plausible answer to A1 and A2, which is the point.
- UniProtKB resolution with sequence-version pinning and site-position validation.
- Evidence graph in Kùzu; quantitative matrices in DuckDB. `Observation` and `EvidencedInference` contracts defined in week 1 even though only two subtypes ship.
- Whole-proteome differential analysis across cell-line and tumour-tissue samples, human and mouse — this is what currently flows through the lab.
- Statistical test registry with moderated *t* as default; protein-level adjustment where a matched proteome exists; explicit labelling where it does not.
- `ModifierAssignment` created by default as ambiguous on every ingested site; manual assignment with basis and rationale.
- Minimal reference-graph import: **Reactome and GO only**, pulled forward from v0.2. Pathway context is what makes site data interpretable rather than a list.
- Cross-dataset comparison and faceted retrieval.
- Provenance on every value; curation export satisfying I9.

### Explicitly deferred

| Deferred | Target | Why |
|---|---|---|
| Natural-language querying | v0.3 | Requires a stable schema first; a query interface over a moving ontology is wasted work |
| Reference graph beyond Reactome and GO (Open Targets, DepMap) | v0.2 | Ongoing maintenance liability |
| `EnrichmentObservation` (IP-MS, ABPP) and cross-modality concordance | v0.2 | Needs a stable site layer first; the highest-value deferred item |
| `EnzymeAssociation` | v0.2 | Contract defined in v0.1; population needs perturbation datasets |
| RO-Crate export | v0.2 | Valuable at publication, not during development |
| Workflow capture (CWL/WDL/Nextflow) | v0.2 | Provenance is recorded manually in v0.1 |
| Actions beyond manual annotation | v0.2 | Retraction propagation needs the graph to have downstream consumers first |
| Multi-user, permissions | v0.4 | Single-researcher tool by design until it isn't |
| Tauri desktop packaging | v0.2 | `uv run` plus localhost is adequate |
| RNA-seq modality | v0.3 | See `ONTOLOGY.md` §11 Q2 |
| Local LLM serving | v0.3 | Follows natural-language querying |

---

## Measured findings

From PXD018299 (`HAP1_USP18KO_GlyGlyKSites.txt`, MaxQuant site table, 2.8 MB), inspected 2026-08-06. These are measurements, not assumptions.

| Finding | Value | Consequence |
|---|---|---|
| Sites before filtering | 2,341 — matches the published figure | Dataset is a validation fixture; platform output is checkable against BJC 2021 |
| After removing decoys and contaminants | 2,298 | `Reverse` / `Potential contaminant` filtering is mandatory in the adapter |
| **Sites mapping to >1 protein** | **1,896 / 2,298 (82%)** | `SITE_ON` changed `MANY_ONE` → `MANY_MANY`; `ProteinAssignment` added (§6.3, I14) |
| Localisation probability | median 1.00, min 0.35 | Threshold recorded on the `Analysis`, never hard-coded (§6.4) |
| Native stoichiometry | `Ratio mod/base` present per sample | `protein_adjusted` became tri-state; `native` added (I4) |
| SDRF present | No | A2 confirmed; `basis = publication_methods` |
| Design encoded in column names | `WT/KO × ±IFN × 3 reps`, unambiguous | Curation is `inferred` but at the strong end |
| Sample-name inconsistency | one replicate carries a run ID (`KO_1_181212063719`) | Adapter must normalise sample names, not assume they are clean |
| PRIDE download links | returned as `ftp://` | Adapter converts to `https://ftp.pride.ebi.ac.uk` |
| Gene symbols live in `Gene names`, not `Proteins` or `Protein names` | semicolon-separated | Identifier translation is first-class; §3 must resolve HGNC as well as UniProt |
| Razor pick can be a TrEMBL accession over a reviewed Swiss-Prot one | e.g. `A0A024R4E5` chosen over `Q00341` | Resolution should prefer reviewed entries, recorded as `ProteinAssignment` basis |
| **`Ratio mod/base` testable sites** | **23 of 2,056** | Stoichiometrically correct quantity is unusable for low-stoichiometry PTMs |
| **`Intensity` + Perseus-style imputation** | thousands testable; **12 of 14 published targets recovered** | Imputation is load-bearing, not optional; `Imputation` node added (§6.5, I15) |
| Published targets with unambiguous protein assignment | **3 of 14** | I14 applies to the paper's headline findings — ADAR has 6 candidates |
| ADAR, PSMB9 | fall just outside thresholds (adj p 0.24; log2FC +0.89) | Pipeline is stricter than the original, not contradictory |
| Position validation, isoform-aware resolver | **20/20 (100%)** | I2 is cheap insurance; resolution can proceed optimistically |
| **Razor picks that are isoforms** | **6/20 (30%)** | Under the old key template ~30% of sites would key against a sequence they do not follow — most validating as K and silently wrong |
| Position validation, isoform-stripping resolver | 18/20 | Both failures were resolver bugs, not data errors; they exposed the key defect |
| **Razor pick lands on TrEMBL despite a reviewed entry in the set** | **4 of 8 sampled** | I17 added: reviewed preferred, recorded as `ProteinAssignment` basis |
| Sequences amended since the ~2019 search | 1 of 20 (5%) — `H7BZW7`, updated June 2026 | ~114 of 2,298 sites at risk of silent drift. Amendment is ongoing, not historical, so flagging beats one-time reconciliation. Resolves `ARCHITECTURE.md` open question 1 |
| Reviewed entries in sample; sequence versions | 15/20 reviewed; versions 1–4 | Amendment is ongoing across the set, not historical |

Two findings dominate.

**82% multi-mapping** was expected to be a minority case, is the majority case, and invalidated a cardinality in the DDL on first contact with real data.

**Three analysis choices — quantity, missingness handling, and localisation threshold — each individually defensible, changed the outcome from 1 recovered target to 12.** None of the three is reconstructable from the published methods section. That is the reproducibility gap this platform exists to close, now demonstrated rather than asserted. It also validates I11 concretely: because the matrix was retained, the alternative was recomputable without re-ingestion.

**A schema defect was found by a resolver bug.** `P09914-2` position 376 returns threonine against the canonical IFIT1 sequence and lysine against isoform 2. The key template treated isoform as a property rather than part of the identifier, which would have silently merged isoform sites with canonical ones and placed modifications on the wrong residues. Corrected in `ONTOLOGY.md` §4.

**Reproduction status: 12 of 14 published ISGylation targets recovered from PXD018299.** This is now a regression test — any future change to the ingestion or statistics layer must not reduce that number without explanation.

---

## Recorded assumptions

The collaborating project has not started, so its pipeline is not yet chosen. These are assumptions, not findings. Each is recorded with what would falsify it, so being wrong is detectable rather than silent.

| # | Assumption | Confidence | Falsified by |
|---|---|---|---|
| A1 | Proteome acquisition is DIA on DIA-NN 2.x | ~90% | Anything else appearing in a methods section |
| A2 | diGly acquisition stays DDA, FragPipe/MSFragger or MaxQuant | ~60% | Site-level work starting directly on DIA-NN |
| A3 | Statistics run from search-engine output into R; moderated *t* + BH | ~60% | Perseus retained for continuity with prior publications |
| A4 | Immunopeptidomics is outside the v0.1 horizon | ~80% | A group member starting HLA elution work |

A2 is the weakest. Site-level DIA remains harder than proteome DIA — modified-peptide library generation is awkward and localisation confidence in DIA is still contested — so a project starting now would plausibly split acquisition: proteome on DIA, diGly on DDA.

### The hedging rule

**Union where it is a field, most-likely where it is a module.** `acquisition_mode` as a string costs nothing and covers every case. Four adapters cost three weeks and cover cases that may never arrive.

Five structural hedges, in descending value. All are cheap now and expensive to retrofit:

1. **Retain the quantitative matrix** (I11). Converts A3 from a decision into a non-decision — any test is recomputable from stored values.
2. **Content-address raw files** (I9). Any adapter fix becomes re-ingestion, not migration.
3. **Adapter signature is `(file, SampleMapping)`**, never a directory convention. Search engines differ in output layout more than in output content.
4. **No tryptic assumptions in core** (I12). Protects A4 at zero cost.
5. **Pipeline metadata is data, not branches** (I13). Protects A1 and A2.

Under this rule, A2 being wrong costs one adapter — days, not weeks — and A3 being wrong costs a registry entry.

---

## Milestones

### Week 1 — schema and resolution
Kùzu DDL implemented from `ONTOLOGY.md`, generated rather than hand-written so a field rename is a regeneration. Invariants I2, I3, I4, I10 enforced at write time. UniProt resolution with sequence-version pinning and position validation. DIA-NN adapter.

*Exit:* a DIA-NN report produces validated `Protein` and `ProteinObservation` nodes; a site whose position does not match the pinned sequence fails ingestion loudly; the `Observation` contract has two implementations and no consumer branches on subtype.

### Week 2 — public data and remaining adapters
DuckDB quantitative layer. MaxQuant, Spectronaut and FragPipe adapters. Two or three public interferon-stimulated diGly datasets ingested end-to-end. Sample-to-condition mapping UI, writing curation `Analysis` nodes per `ONTOLOGY.md` §5.2 — not a configuration file. SDRF parsing where present, falling back to manual curation with an explicit `basis`.

*Exit:* a public PXD dataset and a hypothetical local dataset coexist in one graph and are queryable together, and a result derived from a filename-inferred design is visibly labelled as such.

### Week 3 — statistics and inference
Statistical test registry; moderated *t* with empirical Bayes shrinkage and BH as the default entry. Protein-level adjustment path with `ADJUSTED_BY`. `ModifierAssignment` complete including supersession; `EvidencedInference` contract defined and `EnzymeAssociation` tables created even though unpopulated.

*Exit:* a site can move from ambiguous to `basis = uba7_knockout, confidence = confirmed`, the superseded assignment remains inspectable, and swapping the default test requires no change outside the registry.

### Week 4 — interface
Faceted site search. Volcano plots. UpSet plot for cross-dataset site overlap. Provenance panel on every value. Ambiguity and stoichiometry-correction status visible everywhere a number appears.

*Exit:* the query *"which sites are lost on ISG15 knockdown across all my datasets"* returns a cited, provenanced answer.

---

## Risks

**Week 2 is the schedule risk.** Public diGly submissions have inconsistent metadata and few carry SDRF-Proteomics. Mapping raw files to conditions on a dataset you did not generate is often manual and occasionally guesswork. Mitigated by `ONTOLOGY.md` §5.2: sample mapping is a curated activity with its own provenance rather than a script, so wrong mappings are visible, correctable, and never silently promoted to fact. The residual risk is time, not correctness — budget a full day per public dataset for design reconstruction, and treat that as normal rather than as slippage.

**Scope creep into the reference graph.** Importing Reactome will feel productive and will consume a week. It is deferred for a reason.

**Statistics done fast rather than correctly.** The protein-level adjustment is the differentiator. If week 3 compresses, cut the UI polish in week 4, not the adjustment.

**Rebuild discipline (I9).** The cheap-schema-change property holds only if the graph is genuinely regenerable. The moment something exists only inside `graph.kuzu/` and nowhere else, migrations become mandatory. Test the rebuild path in week 2, not week 4.

**Documentation drift.** Six documents and one developer under time pressure. The invariant that protects this is in `CLAUDE.md`: amend the document before the code, never after.

---

## Beyond v0.1

Rough ordering, not commitments: reference-graph import and RO-Crate export (v0.2); RNA-seq modality and natural-language querying over a stabilised schema (v0.3); multi-user and the full Action set (v0.4). Public release once a researcher other than the author has ingested their own data unaided.

---

## Open questions

1. Does v0.1 ship publicly, or is it a private proof that the ontology holds?
2. Licence — Apache 2.0 or AGPL? Bears on whether a commercial fork is acceptable.
3. Does a paper come out of this, and if so is the target the tool or the ISGylation biology it enables?
4. When do the recorded assumptions get revisited? Suggested trigger: first real dataset from the collaborating project, whenever that arrives.
