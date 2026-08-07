# ROADMAP.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 1.9 |
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
| Sequences amended since the ~2019 search | 1 of 20 (5%) — `H7BZW7`, updated June 2026 | ~114 of 2,298 sites at risk of silent drift. Amendment is ongoing, not historical, so flagging beats one-time reconciliation. Resolves `ARCHITECTURE.md` open question 1. **Superseded by measurement 2026-08-07: the realised cost is 40 of 2,056 sites (1.9%), not ~114 — see § Sequence drift below. The 5% figure counts sequences amended, which bounds sites broken rather than estimating it** |
| **Sites whose residue no longer matches today's UniProt** | **40 of 2,056 (1.9%)**, over 16 proteins | Measured, not projected. Refused at ingestion and counted; drift is 2.8× likelier on unreviewed entries |
| **Razor picks whose UniProt entry has since been deleted** | **25 accessions, 48 sites**, all `Inactive`, all unreviewed | The site cannot be keyed at all (I2). Strengthens I17: the TrEMBL pick is the one that disappears |
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

### Independent re-derivation, 2026-08-07

**The finding is the reproduction, not the values.** Every number below was already recorded above or in `data/curation/analysis_PXD018299_KOIFN_vs_WTIFN.json`; none is new, and none is added as a table row. What was never true until now is that they come back from `raw/` on demand. The baseline had been measured once, in a Colab session, and nobody had repeated it — so "12 of 14" rested on a notebook run that no longer existed anywhere, against a file nobody still had. Re-fetched from PRIDE into the content-addressed store and re-derived end to end, it reproduces.

Fetched with `python -m bzk.sources.pride` (2,759,052 bytes, digest as cited by the three `data/curation/` records) and re-derived from those verified bytes. Confirmed, against the rows above: 2,341 sites → **2,298** after decoys and contaminants → **2,056** after localisation ≥ 0.75 → **1,375** tested; **4,038 of 8,250** values imputed (48.9%); **ADAR** adj p **0.24** and **PSMB9** log2FC **+0.89** the two misses; **3 of 14** recovered targets unambiguous (DDX60, IFIH1, PSMB10). The three counts are checked against the curation record, which owns them.

The per-site rows now exist on disk for the first time — `tests/fixtures/pxd018299_welch_baseline.json`, regenerable with `bzk/sources/pxd018299_baseline.py`. This closes the gap the survey below records for `res`, for the fourteen targets only: three integers cannot distinguish "12 of 14" from "12 of 14, a different twelve", and the fixture pins which twelve, at which site, on which razor pick. ADAR and PSMB9 are pinned as *not* recovered, so a change that raises the count must also be explained.

**Caveat, and the reason the fixture exists.** The re-derivation transcribes `colab_reproducefigure.ipynb` in **pandas** — now pinned at `3.0.5` in the dev dependency group, having until this date been an unpinned transitive arrival via streamlit. So the reproduction is controlled as of today and was not before. Whether the same pipeline yields the same rows under **polars and numpy**, which is what `ARCHITECTURE.md` §4 specifies for the platform's own quantitative layer, is **untested**. That difference is precisely what the fixture is for, and it stays open until the statistics layer lands.

### Protein-group ambiguity at protein grain, 2026-08-07

**§6.3's 82% has a protein-grain counterpart, and it is the same order of magnitude.** The site
figure — 1,896 of 2,298 filtered GlyGly sites map to more than one protein — is what settled
`SITE_ON` and produced `ProteinAssignment`. The protein grain had no such number, so
`bzk/adapters/perseus.py` refusing a multi-accession row was a decision taken against an unmeasured
frequency. Measured over three real artefacts, regenerable with
`python -m bzk.sources.protein_groups`, pinned in `tests/fixtures/pxd018299_protein_groups.json`.

| Artefact | Rows | `Majority protein IDs` multi | median / max | isoform-only | distinct-gene |
|---|---|---|---|---|---|
| BJC **Supplementary Data 2** — Perseus export | 25 | **18 (72.0%)** | 2 / 6 | 9 | 9 |
| BJC **Supplementary Data 3** — Perseus export | 323 | **250 (77.4%)** | 2 / 18 | 84 | **166 (51.4% of rows)** |
| `HAP1_USP18KO_proteinGroups.txt` — MaxQuant | 4,797 | **3,698 (77.1%)** | 3 / 33 | 991 | **2,707 (56.4% of rows)** |

On the wider `Protein IDs` column the same three read 88.0%, 91.0% and 86.2%.

**The two BJC tables are the exact artefact in question** — real Perseus protein-level exports,
identifiable by the `C:` / `N:` / `T:` column-type prefixes Perseus writes into an Excel export, and
they are the published supplementary data of the paper this whole reproduction is anchored to. The
MaxQuant table gives *n* = 4,797 upstream of Perseus and shows that Perseus' selection does not
change the picture: 77.4% and 77.1% agree to within a third of a point.

**The number that decides the modelling is not the headline but the split.** An isoform-only group
names one gene whose isoform is unresolved, and "resolve to the gene" is at least available. A
distinct-gene group names different proteins and has no fallback at all — and distinct-gene groups
are the majority of the multi-accession rows in every artefact, **51.4% and 56.4% of all rows** in
the two larger ones. So the cheap answer is unavailable for roughly half of every protein-level
table this group produces.

| Consequence | |
|---|---|
| `perseus.py` on a real export | refuses ~72–77% of rows, so it is unusable until the schema can hold a group |
| The site/protein asymmetry | not a Perseus quirk: the protein grain was modelled less completely than the site grain, and 77% is not an edge case |
| §6.3's open question | *"either the key gains a way to name several parents, or the relationship narrows"* — posed for sites, unresolved, and now posed identically one grain up |

**Two findings from the measurement itself, both of the ran-cleanly-and-was-wrong class.**

**Six lines of `HAP1_USP18KO_proteinGroups.txt` are not protein groups.** MaxQuant writes long
semicolon-separated numeric lists in its `*_IDs` columns and six spill onto their own physical
lines, each carrying exactly 147 tabs — so the field count matches the header, every structural
check passes, and `pandas` reads them as data with numbers like `6215;8153;8154` in the accession
column. Excluding them moves the headline by 0.1 of a point and the largest apparent group from
**5,090 members to 33**. The file states its own row count (`id` is a contiguous 0-based sequence,
0..4,981 for 4,988 physical lines), so a line without one is not a row; that is the test used,
rather than anything heuristic. Any future MaxQuant adapter must apply it.

**Supplementary Data 3 contains 12 rows flagged `C: Potential contaminant`.** A published table of
significantly-changed proteins carries contaminants the reader is expected to filter. Not a defect
in the paper — the column is right there — but it settles a design question: an analysis-output
adapter cannot assume an export has been filtered, and `Analysis.filters_applied` describing what
the *user says* they applied is exactly the `parameters_observed = false` distinction doing its job.

### The ingested population is 1,967, 2026-08-07

The graph now holds the deposit's sites (`python -m bzk.rebuild`), and the population that reached
it is **not** the file's row count and **not** the notebook's 1,375. Stated here because every
comparison against `colab_reproducefigure.ipynb` from now on is between two different populations,
and a difference in a downstream count will otherwise be read as a pipeline discrepancy.

| | rows | |
|---|---|---|
| `HAP1_USP18KO_GlyGlyKSites.txt` | 2,341 | |
| − decoys and contaminants | −43 | 2,298 |
| − `Localization prob < 0.75` | −242 | 2,056 considered |
| − refused at ingestion | −89 | 40 residue drift · 48 unresolvable protein · 1 no razor pick |
| **= `SiteObservation`s in the graph** | **1,967** | |

The notebook's 1,375 is a different filter again — it is the testable subset after its own
quantitative filtering, not the ingestible subset — so 1,967 and 1,375 are not two answers to one
question. Reconciling them is Slice 4b's business.

### Sequence drift costs 40 of 2,056 sites, 2026-08-07

The first measurement of what it costs to key 2019 site positions against 2026 UniProt, produced by
running `bzk/adapters/maxquant_sites.py` over the deposit's GlyGly table
(`python -m bzk.sources.pxd018299_sites`). The adapter validates every site's reported residue
against the sequence version it pins and **refuses** the ones that disagree, so the count is the
measurement rather than a by-product of it.

| Stage | Rows | |
|---|---|---|
| `HAP1_USP18KO_GlyGlyKSites.txt` | 2,341 | |
| − decoys and contaminants | −43 | 2,298, matching the figure already on record |
| − `Localization prob < 0.75` | −242 | **2,056 considered** |
| − no razor pick | −1 | `Protein` empty; MaxQuant declined to pick (row 1319) |
| − protein unresolvable | −48 | 25 accessions, **all UniProt `Inactive`** — see below |
| − **residue mismatch** | **−40** | **16 proteins. 1.9% of sites considered** |
| = emitted | **1,967** | |

**The prior estimate was ~114 of 2,298 and it was measuring something else.** That figure came from
*1 of 20 sampled sequences amended since the search* (5%), extrapolated. The extrapolation is not
wrong so much as answering a different question: a sequence can be amended without moving any
particular lysine, so *sequences amended* is an upper bound on *sites broken*, not an estimate of
it. Measured, the consequence is **1.9%**, about a third of the projection. The correction is worth
keeping in both directions — the exposure is real and it is smaller than feared, and neither of
those was knowable before an adapter existed to count it.

**Drift concentrates in unreviewed entries, which is I17's argument made quantitative.** Of the
1,053 distinct razor picks, 656 are reviewed Swiss-Prot and 397 are unreviewed TrEMBL. Of the 16
proteins carrying a mismatch, 6 are reviewed and 10 are unreviewed — **0.9% of reviewed proteins
against 2.5% of unreviewed**, a factor of 2.8. And every one of the 25 unresolvable accessions is
unreviewed. So the razor picks that land on TrEMBL despite a reviewed entry in the set (already on
record at 4 of 8 sampled) are the same picks most likely to be unkeyable or stale later. I17's
*reviewed preferred* is not only about naming the better identifier; it is about picking the one
that will still mean the same thing in five years.

**The 48 unresolvable sites are deletions, not missing metadata.** All 25 accessions return UniProt
`entryType: 'Inactive'` — entries deleted or demerged since the 2019 search, carrying no sequence
and no version. The refusal reports them as *"no sequence_version, so no ProteinSequence can be
keyed (I2)"*, which is true but understates it: the protein the search named no longer exists as a
distinct entry. `bzk/resolve/uniprot.py` returns `status='ok'` for these, which is what makes the
refusal message read as a metadata gap rather than a deletion; recorded in `HANDOFF.md` §8.

### The K-GG remnant set is three, not four, 2026-08-07

`ONTOLOGY.md` §6.1 stated that *"Ubiquitin, NEDD8, ISG15 and FAT10 all terminate in a diglycine
motif"* and that tryptic digestion *"leaves an identical K-ε-GG remnant (+114.0429 Da) ... in every
case"*. Verified against UniProt **mature chains** — the canonical sequences are precursors, and
checking those first gave the wrong answer for every modifier, which is why this is recorded as a
measurement rather than a reading.

Terminating in GG is not the criterion. Trypsin cuts C-terminal to K/R, so the remnant is everything
after the modifier's **last K or R**, and a diglycine remnant requires K or R at position −3.

| Modifier | Mature C-term | −3 | Tryptic remnant | Mass |
|---|---|---|---|---|
| ubiquitin `P0CG48` | LRLR**GG** | R | `GG` | **114.04 Da** |
| NEDD8 `Q15843` | LALR**GG** | R | `GG` | **114.04 Da** |
| ISG15 `P05161` | LRLR**GG** | R | `GG` | **114.04 Da** |
| FAT10 `O15205` | CYCI**GG** | I | `GNLLFLACYCIGG` | 1,324.63 Da |
| SUMO1 `P63165` | QEQT**GG** | T | `ELGMEEEDVIEVYQEQTGG` | 2,135.92 Da |
| UFM1 `P61960` | PRDR**VG** | R | `VG` | — (no GG) |

**Consequence.** `candidate_modifiers` on the default `ModifierAssignment` is the three, not four —
FAT10 ends in GG but is excluded by the same argument that excludes SUMO, and would not be
co-isolated by anti-K-GG enrichment. §6.1's DDL example always said three and its prose said four;
the prose was corrected. The set is now `schema.GG_REMNANT_MODIFIERS`, one home, guarded against
§6.1, and a closed enum rather than a query over `Modifier` nodes — which would have made an
identifying field depend on graph state (ADR-0021).

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
