# ROADMAP.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 1.4 |
| Last reviewed | 2026-08-07 |
| Depends on | `VISION.md`, `ONTOLOGY.md`, `ARCHITECTURE.md` |
| Authoritative for | Scope, milestones, deferrals |

---

## v0.1 — target: 8 weeks part-time, scope cut to match

**Revised 2026-08-06 after external review.** The previous version claimed four weeks for a scope realistically requiring 11–15 weeks at 15–20 hours per week. That was wrong by roughly a factor of three, and the error was more dangerous than an ordinary slip: the only way to hit four weeks with that scope is to downgrade invariants from errors to warnings, which destroys the discipline that makes the design worth having.

**A smaller v0.1 that enforces I1–I19 strictly is worth more than a larger one that violates them to meet a date.**

Scope is therefore cut to a single path, and the remainder moved to v0.2.

**The goal is a usable tool for one laboratory.** Not a product for a market, and not merely a proof that the ontology holds — a working end-to-end path that someone in the Pinto-Fernández group can run on their own data and get an answer from.

That is a higher bar than a schema demonstration and a much lower one than a released product. Everything in scope below is there because that group needs it; everything deferred is deferred because they do not, yet.

### In scope

One ingestion path, one dataset, one statistical test, no web frontend.

| Capability | Note |
|---|---|
| **Perseus result-table adapter** | The collaborating group's workflow. A flat table of proteins, differences and significance values — no localisation or razor-pick complexity |
| **MaxQuant site-table adapter** | PXD018299, the validated regression fixture. Required to keep 12-of-14 verifiable |
| UniProtKB resolution | Sequence-version pinning, isoform-aware, position validation, persistent cache |
| Evidence graph in Kùzu | `Observation` and `EvidencedInference` contracts defined even though few subtypes ship |
| Quantitative matrices in DuckDB | I11 — retained permanently, never only derived statistics |
| `welch_t` | **Implemented first.** The 12-of-14 baseline was measured under Welch + BH; reproducing it exactly is how a pipeline bug is distinguished from a genuine difference between tests |
| `perseus_s0` | Default and required per ADR-0015. Implemented second, and its own recovery number recorded as a separate baseline — it will not necessarily be 12 |
| `ModifierAssignment` | Created as ambiguous on every site; manual assignment with basis |
| `ProteinAssignment` | As a node, per `ONTOLOGY.md` §6.3. Same shape and cardinality as `ModifierAssignment`, so no additional machinery |
| `Imputation` | As a node, per `ONTOLOGY.md` §6.5. One per `Analysis` |
| Curation and analysis records | I8, I15, I16, I19 — every choice recorded |
| **Output via notebook or minimal Streamlit** | No SvelteKit. Visualisation is not the differentiator and can wait |
| Rebuild script | Written in week 1, run weekly. I9 is only true if tested |
| `tests/` from week 1 | Invariant violations, adapter fixtures, resolution edge cases |

**Build targets**

| Accession | Content | Adapter |
|---|---|---|
| PXD018299 | USP18-dependent ISGylome — the validated fixture | MaxQuant |
| Collaborator's Perseus tables | Real results from the intended first user | Perseus |
| PXD064305 and the other 2025 deposits | Embargoed pending publication; not yet accessible | DIA-NN (v0.2) |

**Two deferrals withdrawn, 2026-08-06.** `ProteinAssignment` and `Imputation` were previously deferred to v0.2, to be represented as fields on `SiteObservation` and as JSON on `Analysis` respectively. Both deferrals are withdrawn.

The saving was notional. The full DDL validates unchanged against Kùzu 0.11.3, so the tables are created either way; and `ModifierAssignment` — already in scope — establishes the node-per-inference pattern and its cardinality. Populating two more tables through the same code path costs close to nothing.

The alternative cost was real: two representations of the same fact, one as fields and one as a node, is exactly the duplication `CLAUDE.md` forbids, and it would have made I14 and I15 enforceable in two different ways depending on version.

### Explicitly deferred

| Deferred | Target | Why |
|---|---|---|
| Natural-language querying | v0.3 | Requires a stable schema first; a query interface over a moving ontology is wasted work |
| Reference graph beyond Reactome and GO (Open Targets, DepMap) | v0.2 | Ongoing maintenance liability |
| `EnrichmentObservation` (IP-MS, ABPP) and cross-modality concordance | v0.2 | Needs a stable site layer first; the highest-value deferred item |
| `EnzymeAssociation` | v0.2 | Tables created in v0.1 but unpopulated; population needs perturbation datasets |
| RO-Crate export | v0.2 | Valuable at publication, not during development |
| Workflow capture (CWL/WDL/Nextflow) | v0.2 | Provenance is recorded manually in v0.1 |
| Actions beyond manual annotation | v0.2 | Retraction propagation needs the graph to have downstream consumers first |
| Multi-user, permissions | v0.4 | Single-researcher tool by design until it isn't |
| Tauri desktop packaging | v0.2 | `uv run` plus localhost is adequate |
| **SvelteKit frontend** | v0.2 | Notebook or Streamlit output suffices to prove the pipeline. Faceted search, volcano and UpSet plots are polish, not proof |
| **DIA-NN, FragPipe, Spectronaut adapters** | v0.2 | One search-engine adapter is enough to validate the contract |
| **`moderated_t_ebayes`** | v0.2 | Needed for the comparison capability, not for the first pipeline |
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

### From author correspondence, 2026-08-06

`basis: author_correspondence` — the highest-confidence entry in the curation enum, and the first time it has been used.

| Finding | Value | Consequence |
|---|---|---|
| **Statistical workflow** | **Perseus, unchanged** — log₂ transformation, missing-value filtering, imputation from a normal distribution, dedicated two-sample test | Resolves A3. `perseus_s0` becomes the **default and required** registry entry, not an optional legacy one. ADR-0015 supersedes ADR-0011 |
| Quantity used | Intensity columns | Independently confirms the measured finding above |
| Volcano axis | Difference in intensities rather than fold change | Almost certainly the difference of log₂ values, which *is* log fold change — to confirm at the meeting |
| Perseus test identity | SAM-style modified *t* with `s0` and permutation FDR | Not equivalent to Welch + BH. Produces a curved significance boundary. Exact `s0` and FDR values still to obtain |
| **Convergence** | The Week B pipeline independently arrived at the same workflow | Arrived at by discovering `Ratio mod/base` gives 23 usable sites, not by copying the method. Evidence the reproduction was not accidental |
| Newer USP18 GlyGly dataset | Exists, unpublished, substantially improved coverage | Offered for analysis. Requires the `embargoed` dataset state (`ONTOLOGY.md` §5.2, I18). Search engine unknown — A2 remains open |

**Correction to a prior inference.** An earlier revision read the 2025 TNBC preprint's silence on proteomic statistics as evidence that the group had moved away from Perseus, and advised against building the Perseus-compatible test. That was wrong. Absence of a stated method in a publication is not evidence of a changed method — it is absence of a stated method. Recorded here because the error is more instructive than the correction: it is exactly the kind of inference this platform exists to prevent being made silently.

Two findings dominate.

**82% multi-mapping** was expected to be a minority case, is the majority case, and invalidated a cardinality in the DDL on first contact with real data.

**Three analysis choices — quantity, missingness handling, and localisation threshold — each individually defensible, changed the outcome from 1 recovered target to 12.** None of the three is reconstructable from the published methods section. That is the reproducibility gap this platform exists to close, now demonstrated rather than asserted. It also validates I11 concretely: because the matrix was retained, the alternative was recomputable without re-ingestion.

**A schema defect was found by a resolver bug.** `P09914-2` position 376 returns threonine against the canonical IFIT1 sequence and lysine against isoform 2. The key template treated isoform as a property rather than part of the identifier, which would have silently merged isoform sites with canonical ones and placed modifications on the wrong residues. Corrected in `ONTOLOGY.md` §4.

**Reproduction status: 12 of 14 published ISGylation targets recovered from PXD018299.** This is now a regression test — any future change to the ingestion or statistics layer must not reduce that number without explanation.

### Deposit and supplementary survey, 2026-08-07

Method: read the column headers of every processed file in the PXD018299 PRIDE deposit and every supplementary table of Pinto-Fernández et al., *Br J Cancer* 124:817–830 (2021), and classified each as a Perseus export or raw search-engine output by column markers — Perseus stamps a type prefix on every column name (`C:` categorical, `N:` numerical, `T:` text, `M:` multi-numerical); MaxQuant does not. Also read `colab_reproducefigure.ipynb` end to end to establish what it persists. These are measurements of files on disk and in the publication, not inferences from a methods section.

| Finding | Value | Consequence |
|---|---|---|
| PXD018299 processed tables | 3, all raw MaxQuant — `GlyGly (K)Sites` (site grain, 159 columns), `proteinGroups` (protein grain, 148 columns), `ISG15_interactome` (`.xlsx`, protein grain, 134 columns) | No Perseus export is deposited. The published differential result is not in the deposit; it must be recomputed from the raw tables |
| BJC supplementary Tables 1–3 | Perseus exports — Table 1 site grain, Tables 2–3 protein grain, all carrying `C:`/`N:`/`T:`/`M:` prefixes | The published differential result *does* exist as a Perseus table, at both grains. This is a real analysis-output (Perseus) adapter input |
| BJC supplementary Table 4 | hand-curated — no type prefixes, no per-sample columns | Not an adapter input |
| Column-marker reliability | the type-prefix stamp is decisive; a bare statistics-column search gave a false positive (a `Q-value` column occurs in raw MaxQuant output too) | Classify Perseus by the prefix stamp, never by the presence of a statistics column |
| Supplementary table contents | significant-UP subsets — raw intensities plus MaxQuant annotations, no per-row test statistic | They fix the column and naming conventions an adapter must accept, but carry no p-value or fold change, so they cannot validate `DifferentialResult` ingestion end to end |
| `colab_reproducefigure.ipynb` per-site table (`res`) | 1,375 rows built in memory, never persisted — Step 9 writes only the analysis JSON (counts). Drops peptide sequence and residue; carries no per-site `n_imputed` | The only per-site differential result the group has produced is not on disk. Ingesting it means re-running the notebook or reconstructing the table; recorded as an open item (`HANDOFF.md` §8) |
| Imputation fraction of that analysis | 48.9% — 4,038 of 8,250 values imputed, whole-matrix | Just under the I15 *substantially imputed* threshold (more than half). Load-bearing enough that the imputed status must travel with every point (I15, I16) |
| **Baseline quantity is multiplicity-aggregated** | The GlyGly site table's only modification axis is GlyGly multiplicity: `Intensity___1/2/3` (header cols 74–76) and per-sample `Intensity <sample>___1/2/3` (102–137). `colab_reproducefigure.ipynb` builds `Intensity KO_IFN_{1,2,3}` / `Intensity WT_IFN_{1,2,3}` — the plain per-sample columns (81–89), i.e. the multiplicity-**summed** total; it never touches the `___n` split | The 12-of-14 baseline is computed on multiplicity-summed intensity, yet `analysis_PXD018299_KOIFN_vs_WTIFN.json` recorded only `quantity: "Intensity"` — an analytically consequential choice invisible in the record, the same class as Intensity vs Ratio mod/base. Now recorded as `intensity_multiplicity_summed`; I16 requires quantity to name the multiplicity treatment (`ONTOLOGY.md` §5, I16) |

---

## Recorded assumptions

The collaborating project has not started, so its pipeline is not yet chosen. These are assumptions, not findings. Each is recorded with what would falsify it, so being wrong is detectable rather than silent.

| # | Assumption | Confidence | Falsified by |
|---|---|---|---|
| A1 | Proteome acquisition is DIA on DIA-NN 2.x | ~90% | Anything else appearing in a methods section |
| A2 | diGly acquisition stays DDA, FragPipe/MSFragger or MaxQuant | ~60% | Site-level work starting directly on DIA-NN |
| ~~A3~~ | ~~Statistics run from search-engine output into R; moderated *t* + BH~~ | — | **Resolved 2026-08-06 — see Measured findings. The assumption was wrong.** |
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

**A3 was wrong, and the hedge held.** The cost of the error was changing which registry entry is the default. Had the statistical test been hard-coded, it would have been a rewrite. This is the first empirical test of the hedging rule and it passed.

---

## Milestones

Eight weeks at 15–20 hours per week. Each phase ends with something demonstrable rather than something merely started.

### Weeks 1–2 — foundation
Kùzu DDL generated from `ONTOLOGY.md`. Invariant checks I2, I3, I4, I10, I14 enforced at write time, with `tests/` written first and failing. Isoform-aware UniProt resolution with a persistent cache, ported from the Week C notebook. Rebuild script written and run.

*Exit:* twenty accessions resolve and validate; a site whose position does not match its pinned sequence fails ingestion loudly; the graph drops and rebuilds from raw files without loss.

### Weeks 3–4 — first ingestion path
Perseus result-table adapter. Curation record ingestion. `Analysis.kind = 'external'` with `parameters_observed = false`.

*Exit:* a Perseus table is ingested, resolved, stored, and cross-queried against a second dataset. **This is the first genuinely useful milestone** — a real user's results, held and connected.

### Weeks 5–6 — raw path and statistics
MaxQuant site-table adapter. DuckDB quantitative layer. **`welch_t` with BH first**, reproducing 12 of 14 exactly; then `perseus_s0` with permutation FDR, its recovery number recorded as a separate baseline. `ModifierAssignment`, `ProteinAssignment` and `Imputation` including supersession and retraction.

*Exit:* PXD018299 ingested end to end, 12 of 14 recovered through the real pipeline rather than a notebook. A site moves from ambiguous to `basis = uba7_knockout, confidence = confirmed`, and the superseded assignment remains inspectable.

### Weeks 7–8 — output and consolidation
Minimal Streamlit or notebook interface: query, volcano, provenance panel. Ambiguity and correction status visible everywhere a number appears. ADRs 0004–0014 written. Rebuild tested against the full dataset.

*Exit:* *"which sites are lost on ISG15 knockdown across all my datasets"* returns a cited, provenanced answer, and every displayed number carries its inference status.

### Not in these eight weeks
SvelteKit. DIA-NN, FragPipe, Spectronaut. Reactome and GO. `EnzymeAssociation` population. Cross-modality concordance. Multi-user.

## Risks

**Week 2 is the schedule risk.** Public diGly submissions have inconsistent metadata and few carry SDRF-Proteomics. Mapping raw files to conditions on a dataset you did not generate is often manual and occasionally guesswork. Mitigated by `ONTOLOGY.md` §5.3: sample mapping is a curated activity with its own provenance rather than a script, so wrong mappings are visible, correctable, and never silently promoted to fact. The residual risk is time, not correctness — budget a full day per public dataset for design reconstruction, and treat that as normal rather than as slippage.

**Scope creep into the reference graph.** Importing Reactome will feel productive and will consume a week. It is deferred for a reason.

**Statistics done fast rather than correctly.** The protein-level adjustment is the differentiator. If week 3 compresses, cut the UI polish in week 4, not the adjustment.

**Rebuild discipline (I9).** The cheap-schema-change property holds only if the graph is genuinely regenerable. The moment something exists only inside `graph.kuzu/` and nowhere else, migrations become mandatory. The rebuild script is written in week 1 and run weekly, not deferred.

**Kùzu is pre-1.0.** Cypher coverage is incomplete and the Python API is still moving. Pin an exact version; do not float. I9 mitigates the risk only if the rebuild path is exercised continuously, which is why it moved to week 1.

**Scope creep back into the cut list.** The deferred items are deferred because they are pleasant to build, not because they are hard. SvelteKit in particular will feel like progress and is not. If weeks 7–8 run short, write ADRs.

**Documentation drift.** Six documents and one developer under time pressure. The invariant that protects this is in `CLAUDE.md`: amend the document before the code, never after.

---

## Beyond v0.1

Rough ordering, not commitments: reference-graph import and RO-Crate export (v0.2); RNA-seq modality and natural-language querying over a stabilised schema (v0.3); multi-user and the full Action set (v0.4). Public release once a researcher other than the author has ingested their own data unaided.

---

## Open questions

1. Does v0.1 ship publicly, or is it a private proof that the ontology holds?
2. Licence — Apache 2.0 or AGPL? Bears on whether a commercial fork is acceptable.
3. Does a paper come out of this, and if so is the target the tool or the ISGylation biology it enables?
4. **At which point in his pipeline would the collaborator rather hand something over — search-engine output or Perseus results?** The answer determines whether retaining the raw matrix is essential or merely prudent. Ask at the meeting.
5. When do the recorded assumptions get revisited? Suggested trigger: first real dataset from the collaborating project, whenever that arrives.
