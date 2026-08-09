# ROADMAP.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 1.37 |
| Last reviewed | 2026-08-09 |
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
| **Perseus result-table adapter** | The collaborating group's workflow. A flat table of proteins, differences and significance values — no localisation or razor-pick complexity. **Written and tested against fixtures; not yet run on a real export.** Established 2026-08-09: the two published BJC tables are Perseus exports *of the annotation matrix* and carry no test statistic, so they cannot supply one. The adapter's group handling is no longer the blocker it was — ADR-0022 discharged that — and what it needs is a Perseus table that carries a `Difference` and a p-value |
| **MaxQuant site-table adapter** | PXD018299, the validated regression fixture. Required to keep the published-target recovery verifiable — see the amended exit criterion: the figure is 9 of 14 through this route, and the criterion is that every miss is traced, not that the number is 12 |
| UniProtKB resolution | Sequence-version pinning, isoform-aware, position validation, persistent cache |
| Evidence graph in Kùzu | `Observation` and `EvidencedInference` contracts defined even though few subtypes ship |
| Quantitative matrices in DuckDB | I11 — retained permanently, never only derived statistics |
| `welch_t` | **Implemented first.** The 12-of-14 baseline was measured under Welch + BH; reproducing it exactly is how a pipeline bug is distinguished from a genuine difference between tests |
| `perseus_s0` | Default and required per ADR-0015. Implemented second, and its own recovery number recorded as a separate baseline — it will not necessarily be 12 |
| `ModifierAssignment` | Created as ambiguous on every site; manual assignment with basis |
| `ProteinAssignment` | As a node, per `ONTOLOGY.md` §6.3. Same shape and cardinality as `ModifierAssignment`, so no additional machinery |
| `Imputation` | As a node, per `ONTOLOGY.md` §6.5. **Several per `Analysis`** — `IMPUTATION_FOR` is `MANY_ONE` (§6.5 DDL), so an analysis's imputation state is a *set*. This row read *"One per `Analysis`"* until 2026-08-09 and contradicted the normative DDL; corrected here under `CLAUDE.md` § Conventions rather than worked around in the code that reads it. §8 I15's *substantially imputed* is defined on a `DifferentialResult`, not on an `Analysis`, so the set does not collapse to a flag either |
| Curation and analysis records | I8, I15, I16, I19 — every choice recorded |
| **Output via notebook or minimal Streamlit** | No SvelteKit. Visualisation is not the differentiator and can wait. **Met 2026-08-09** — `bzk/query/` answers five questions and `bzk/ui/app.py` displays three panels over it, with all four `Absence` values rendered as four distinct claims. No volcano and no notebook: the three `colab_*.ipynb` files still read the deposit rather than Kùzu, and there is nothing to plot until a `DifferentialResult` exists |
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
| Gene symbols live in `Gene names`, not `Proteins` or `Protein names` | semicolon-separated | Identifier translation is first-class; §3 must resolve HGNC as well as UniProt. **Measured 2026-08-08: no second authority is needed** — UniProt's own payload carries the HGNC id (`HGNC:7532` for `P20591`), and what is missing is that the entry cache stores the parse rather than the payload (`ONTOLOGY.md` §11 Q12) |
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
| **Rows dropped by a threshold the graph does not record** | **242 of 2,298 (10.5%)** at `Localization prob >= 0.75` | I16's exact case, unfired because the adapter emits no `Analysis` for it to check. See § The platform made an invisible analytical choice |
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
they are the published supplementary data of the paper this whole reproduction is anchored to.

**Narrowed 2026-08-09, and the narrowing is what stopped an ingestion.** *Perseus export* is right
and *the exact artefact in question* was right for the question this survey asked — protein-group
ambiguity, which is answered from the accession columns. It is not right for ingestion: these are
Perseus exports of the **annotation matrix**, and neither carries a `Student's T-test Difference` or
a p-value column, so no `DifferentialResult` can be minted from them. A survey that reads headers
can establish what a column *is* and cannot establish what is *missing* from the set. See
§ *Step 0 stopped the BJC ingestion*. The
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
| ~~`perseus.py` on a real export~~ | Said *"refuses ~72–77% of rows, so it is unusable until the schema can hold a group"*. **Discharged by ADR-0022** — `candidate_proteins` became identifying and `RESOLVES_TO_PROTEIN` `MANY_MANY`, so the group *is* the identity and nothing is refused for being a group. Confirmed against the code 2026-08-09, in the turn that went to ingest these files and was stopped by something else entirely |
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

### Nine of fourteen, and the five misses are traceable, 2026-08-07

Slice 4b ran the differential analysis over the population the graph holds, using `bzk/stats/`
written from `ARCHITECTURE.md` §4 and `ONTOLOGY.md` §6.5 rather than from
`colab_reproducefigure.ipynb` — the distinction being that copied arithmetic agreeing with itself is
guaranteed. `python -m bzk.sources.pxd018299_differential`.

| step | this route | notebook |
|---|---|---|
| rows in file | 2,341 | 2,341 |
| after decoys and contaminants | 2,298 | 2,298 |
| after `Localization prob >= 0.75` | 2,056 | 2,056 |
| **ingested** | **1,967** (89 refused) | not applicable |
| after `>=2 replicates in either group` | **1,321** | **1,375** |
| significant up (adj p < 0.05, log2FC > 1) | **508** | **561** |
| published targets recovered | **9 of 14** | **12 of 14** |

**The populations differ by the refusals and by nothing else.** Of the 89 rows refused at
ingestion, exactly **54** would have passed the presence rule, and **1,321 + 54 = 1,375**. That
identity is what makes the comparison trustworthy: it could have come out otherwise, and had it
not, the difference would have been somewhere unaccounted for. It also confirms in passing that
this route's filtering and presence rule match the notebook's exactly, which nothing was designed
to test.

**All five misses are traceable, and three are not statistical.**

| target | rows | refused | reason | outcome |
|---|---|---|---|---|
| **ADAR** | 7 | 7 | `unresolved_protein` | never tested |
| **OAS2** | 8 | 8 | `residue_mismatch` | never tested |
| **OAS1** | 2 | 2 | `residue_mismatch` | never tested |
| DDX60 | 5 | 0 | — | tested, not significant |
| PSMB9 | 1 | 0 | — | tested, not significant |

The notebook's two misses were ADAR and PSMB9. This route misses the same two, plus OAS1 and OAS2
to sequence drift and DDX60 at the threshold. **ADAR is missed by both routes for different
reasons** — the notebook tested it and it fell short of the thresholds; here it was never tested,
because its razor pick no longer exists in UniProt.

**Every one of the three lost targets has a reviewed Swiss-Prot entry in its own candidate group.**

| gene | razor pick | status of the pick | reviewed alternative in the same group |
|---|---|---|---|
| ADAR | `H0YCK3` | **`Inactive`** — deleted from UniProt | `P55265` Swiss-Prot sv4 |
| OAS1 | `H0YI20` | TrEMBL | `P00973` Swiss-Prot sv4 |
| OAS2 | `A0A087X0V5` | TrEMBL | `P29728` Swiss-Prot sv3 |

That is I17 — *reviewed entries are preferred, and the preference is recorded* — which is specified
in §6.3, classified `CON` in `HANDOFF.md` §8, and implemented nowhere. The earlier measurement that
drift is 2.8× likelier on unreviewed entries, and that every deleted entry was unreviewed, now has
a cost attached: three published targets.

**9 is not a worse number than 12 and not a better one.** It is the answer for a different
population — one that excludes sites whose positions cannot be validated against today's UniProt.
Nothing here was tuned toward agreement, and a figure that had matched would have needed explaining
as much as one that differs.

### Validity-conditional promotion: 12 of 14 — the same count as the notebook, not the same twelve, 2026-08-07

ADR-0024 rule 1 (validity is a precondition of promotion, not a preference within it), implemented
after the ADR and read against the pre-registration below.

| | I17 as first written | + validity precondition |
|---|---|---|
| promotions applied | 526 | **522** (the 4 declined) |
| ingested | 2,025 | **2,029** |
| refused | 31 | **27** |
| after presence rule | 1,358 | **1,362** |
| significant up | 524 | **516** |
| **published targets recovered** | **11 of 14** | **12 of 14** |

**Pre-registered outcome A.** TAP1 returned. The claim is the narrow one written in advance:
*validity must dominate preference* — worth exactly four rows on this deposit. It is **not** evidence
that reviewed-preference is safe; the 522 unaffected promotions carry that and were already counted.
This is I17 **repaired**, not I17 confirmed.

**Outcome D ruled out, by the check the pre-registration demanded.** Four rows were eligible and the
population moved by exactly four (2,025 → 2,029). The identity holds a third time, with a third
split: **1,362 + 13 refused-but-testable = 1,375.**

**`significant_up` fell, 524 → 516, while four more sites were tested.** Not a defect: BH adjusts
against the size of the tested set, so adding four rows re-ranks every p-value. Recorded because a
count moving *down* as the population moves *up* looks like an error and is not.

#### The twelve are not the notebook's twelve

The count matches. **The membership does not**, and the pre-registration said a matching result
would need explaining as much as a differing one.

| | misses |
|---|---|
| notebook (12 of 14) | **ADAR**, PSMB9 |
| this route (12 of 14) | **OAS1**, PSMB9 |

Both miss PSMB9 — it falls short of the thresholds in both, which is a real agreement. Beyond that
the routes **disagree in both directions**: this route recovers ADAR, which the notebook tested and
found below threshold, and loses OAS1, which the notebook recovered.

- **ADAR** is recovered *because* of I17. Its razor pick `H0YCK3` is deleted from UniProt; promotion
  to `P55265` made it testable and it cleared the thresholds. The notebook, keying against the 2019
  FASTA, tested it and got adj p 0.24.
- **OAS1** is lost to ADR-0024 rule 3. Its group holds two distinct canonical reviewed proteins,
  `F8VXY3` and `P00973`, so the platform declines to promote, the razor pick `H0YI20` fails the
  residue check, and the site is refused. The notebook had no residue check and tested it.

So *"12 of 14"* is a coincidence of arithmetic between two populations that differ by 13 sites and
two published targets. **Reporting it as agreement would be the error this section exists to
prevent.** The amended v0.1 exit criterion asks for the population and the traced misses precisely
because the number alone would have read as a reproduction.

### I17 implemented: 11 of 14, three gained and one lost, 2026-08-07

**Read against the pre-registration below, which was committed at `8ed3e90` before any I17 code
existed, and the implementation at `77dd515` before this result was known.**

| | before I17 | after I17 |
|---|---|---|
| ingested | 1,967 | **2,025** |
| refused | 89 (40 drift · 48 unresolvable · 1 no pick) | **31** (19 · 11 · 1) |
| promotions applied | — | **526** |
| after presence rule | 1,321 | **1,358** |
| significant up | 508 | **524** |
| **published targets recovered** | **9 of 14** | **11 of 14** |

**The population identity holds under the new keying**, which the pre-registration required to be
re-checked rather than assumed: **1,358 + 17 refused-but-testable = 1,375**. The split changed (54
→ 17) while the total did not, so promotion moved sites across the refusal boundary without
inventing or losing any.

**Each pre-registered outcome occurred, for a different gene.** That is why they were written per
outcome rather than as one prediction.

| gene | pre-registered outcome | what happened |
|---|---|---|
| **ADAR** | **1** — resolves and is recovered | `H0YCK3` (`Inactive`) → `P55265`. Recovered. |
| **OAS2** | **1** — resolves and is recovered | `A0A087X0V5` (TrEMBL) → `P29728`. Recovered. |
| **PSMB9** | **2** — resolves, not recovered | `A2ACR0` → `P28065`, tested, still below threshold. The notebook missed it too. |
| **OAS1** | **3** — I17 as specified does not reach it | **Not promoted.** Its group holds *two distinct canonical reviewed* proteins, `F8VXY3` and `P00973`. §6.3 says *"the reviewed Swiss-Prot entry"*, singular; the data has two, and choosing between two genuinely different reviewed proteins is the search engine's job. The implementation declines, by a rule stated before the run. |

So the hypothesis — *reviewed-preferred resolution recovers targets a razor pick loses* — **holds for
two of the three targets it was written about**, fails to apply to the third for a reason that is a
gap in the invariant rather than in the data, and picked up DDX60 besides (previously tested and
below threshold; the changed keying moved it above).

**And it lost TAP1 — the fourth possibility, realised.**

TAP1 was recovered at 9-of-14 and is refused at 11-of-14. Its razor pick `A0A140T9T7` is an
unreviewed 808-residue entry with **K at both 449 and 458**. Promotion moved it to `Q03518`, the
reviewed Swiss-Prot entry, which is **748 residues** today and carries **L at 449 and V at 458** —
so the residue check refused both rows. MaxQuant's own `Positions within proteins` gives 449/458 for
*both* accessions, so the 2019 FASTA held a Q03518 of the same length as the TrEMBL form; the
reviewed entry has since been revised by sixty residues and the unreviewed one has not.

**This is the counterexample to a statistic already on record.** § Sequence drift measures drift as
2.8× likelier on unreviewed entries, and every deleted entry was unreviewed. Both remain true and
both are population statistics. TAP1 is the case that runs the other way: **reviewed-preferred is
not uniformly safer, and I17 can cost a validated site.** Nothing in §6.3 anticipates this, and the
adapter is right to refuse — the alternative is keying a published target at a position that is a
leucine.

Net: three gained (ADAR, OAS2, DDX60), one lost (TAP1), 9 → 11. The gain is real and the loss is
not noise; both belong in any statement of the number.

### Pre-registration: what implementing I17 would mean, 2026-08-07

**Written and committed before I17 exists in any form**, because this is the measurement with the
strongest pull toward the answer we want. Three self-confirming measurements have been caught this
session (`HANDOFF.md` §8), and each was found *after* the fact. Recording the interpretation of each
outcome in advance is what stops the third outcome below being reported as the first.

I17 promotes a reviewed Swiss-Prot entry over an unreviewed razor pick and records
`basis = 'reviewed_preferred'` (§6.3). ADAR, OAS1 and OAS2 each have a reviewed entry in their own
candidate group, so the case is reachable. Three outcomes, and what each licenses:

1. **All three resolve to their reviewed entries and are recovered → 12 of 14.** The claim would
   then be: *reviewed-preferred resolution recovers published targets that a razor pick loses.*
   Stated here as the **hypothesis, before testing it** — so that if it holds, it is a prediction
   confirmed and not a result narrated backwards into one.
2. **They resolve but are not recovered.** Then the loss was the *refusal*, not the threshold, and
   I17's value is that these sites become **testable**, not that they become significant. The
   recovery figure would stay at 9 or move to 10–11, and the honest headline would be about
   population rather than about significance. This outcome is worth as much as the first and reads
   as a weaker result only if the hypothesis was never written down.
3. **They do not resolve.** Then I17 *as specified* does not reach this case, and the reason is a
   finding about the invariant rather than about the data — most likely that promotion needs review
   status per candidate, which needs every candidate resolved, which §6.3 does not say and no
   module does. Reporting this as anything other than a gap in I17 would be the failure this
   pre-registration exists to prevent.

A fourth possibility is not an outcome but a defect to watch for: **promotion changes which
`ProteinSequence` a site keys against, so it re-mints `ModificationSite` and `SiteObservation` ids
and can change the tested population well beyond these three genes.** If the population moves, the
1,321 + 54 = 1,375 identity above no longer holds, and any recovery figure must be reported against
the new population with that identity re-checked rather than assumed.

### Pre-registration: what converging the canonicalization divergences would mean, 2026-08-08

**Written and committed before any of C1, C10 or C11 is implemented.** The 2026-08-08 sweep closed
by asserting every fix is free, and this turn is about to test that assertion. The assertion has the
shape the three caught self-confirming measurements had — a number produced by the same reasoning
that predicts it — so the prediction is recorded before the test rather than after.

**The prediction: no existing id moves.** All 11,730 ids a replay currently reproduces are unchanged
after the three fixes land. It rests on three scans of the current graph: 0 of 4,561 `Protein`
accessions carry a lowercase letter; 0 of 14,371 CURIE values inside identifying `STRING[]` fields
have a non-lowercase prefix; `Analysis.parameters_json` is NULL on both `Analysis` nodes.

**How it will be tested, stated in advance:** rebuild from the four I9 inputs into a fresh database
with the new code, extract every node id by label, and diff against `~/.bzk-omics/graph.kuzu`. *Not*
by re-running the three scans — they produced the prediction, and a scan cannot test itself.

Three outcomes, and what each licenses:

1. **No id moves.** The scans were right, the divergences were a window that had not yet been walked
   through, and the fixes cost nothing. This is the expected outcome and the weakest of the three:
   it confirms a prediction rather than discovering anything, and it must be reported that way.
2. **An id moves.** Then the scans were wrong and the graph already contains two spellings of one
   fact — a live fragmentation, not a closing window. That is a larger finding than the sweep's,
   because it means some fraction of the 2,029 sites are duplicated or keyed against the wrong
   protein, and the fix is a re-mint with a migration rather than a free change. The headline would
   be the fragmentation, not the fix.
3. **The rebuild refuses.** Distinct from (2) and **not excluded by any scan**, because C10 and C11
   converge by refusing rather than normalizing, and every scan above measured the *graph* — which
   by construction holds only values that already got through. A value in `raw/` or the curation
   export that the new checks reject would never have reached a node to be counted. The finding
   would then be about the input, the refusal count is the measurement, and the correct response is
   to read what was refused before deciding whether the check or the input is wrong.

Outcome 3 is the one to watch, for the same reason outcome D was on I17: it is the one the
preparatory work cannot see.

**Result, 2026-08-08 — outcome 1, and it is the weakest of the three.** The three fixes landed, then
a full rebuild from the four I9 inputs into a separate database (57 s) produced **11,730 node ids
and 9,217 edges, 0 differing from the graph on disk** — per label: 4,561 `Protein`, 2,029
`ModificationSite`, 2,029 `SiteObservation`, 2,029 `ModifierAssignment`, 1,062 `ProteinSequence`, 12
`Sample`, 3 `Modifier`, 2 `Analysis`, and one each of `Project`, `Experiment`, `Dataset`. Refusals
stayed at 27, the count already recorded, so outcome 3 did not occur either.

What that licenses and what it does not. It confirms a prediction; it discovers nothing. The
divergences were a window that had not been walked through, and the fixes cost nothing **today** —
which is a fact about a graph produced by one adapter reading one UniProt-sourced deposit, and every
value in it is canonical because that adapter emits canonical values. A second search engine, a
Perseus run carrying a declared `s0`, or a curator-typed accession each closes the window
independently, and the guards are what make that closing cheap rather than the clean scan.

The re-derivation is a different check from the three scans that produced the prediction, which is
the point of specifying it in advance: the scans read the graph's stored values, while this ran the
whole adapter over the raw deposit through the changed builder. A scan cannot see a value the old
code refused, reshaped, or never reached.

### Pre-registration: what widening the tautology sweep would mean, 2026-08-08

**Written and committed before the widened passes are written or run.** The 2026-08-08 sweep
reported 46 Pass A matches, 32 Pass B matches and *"one other instance"*, and closed on Pass B's
zero as evidence the surface was covered. An audit then produced three instances by hand, two of
which no pass could have matched, so the previous count was a property of the criterion rather than
of `tests/`. A widened criterion is about to produce four new numbers to set against 46, 32, 78 and
one, and every one of them will be produced by a criterion I chose — the same shape as a scan
testing itself.

**The criterion, fixed in advance.** Pass C: every `assert` containing an `==` where one side
contains a call expression and the other side is neither a literal nor a display of literals.
Matches are then read by hand and classified as instances or not, where an instance is an assertion
whose call is the expression the producing code used to compute the value on the other side.

**The prediction, in three parts.** Pass C matches strictly more than Pass A's 46. It matches all
three hand-found instances — `test_drift.py:108`, `test_drift.py:110`, `test_perseus.py:228`. And
the classified instance count is **greater than three**, because three came from an unaided read of
a 627-assert surface and an unaided read is not exhaustive.

**How it will be tested, stated in advance:** each classified instance is confirmed by mutating the
function its call names and showing the assertion's own module stays green. *Not* by re-reading the
match list — the list is what produced the classification, and a classification cannot test itself.
Instances are counted twice over: those whose mutation the whole suite survives, and those another
test catches independently, since the second kind is a tautology whose defect is covered elsewhere
and the distinction changes what the count means.

Four outcomes, and what each licenses:

1. **Pass C matches all three and finds no fourth.** The audit's list was complete and the boundary
   is three. Weakest outcome: it confirms someone else's count, and the criterion was built knowing
   the three it had to catch.
2. **Pass C matches all three and finds more.** The expected outcome, and the one that says the
   previous "one" was a criterion artefact rather than a miscount. The number itself is then only
   as good as the hand classification, which must be reported as such.
3. **Pass C misses one of the three.** Then the finding is about the criterion, not the count, and
   no number from that run may be reported — including a reassuring one.
4. **Pass C's match count is so large the classification is not readable by hand.** Then the
   criterion is a net rather than a detector, and what gets committed is the net with its
   classification pinned, not a claim that the class is enumerated.

Outcome 3 is the one to watch, because a criterion built to catch three known instances will catch
them by construction — so the run that matters is the one over instances nobody has named yet, and
that run cannot report a miss it does not know about.

### Pre-registration: what repairing the sweep's own surface would mean, 2026-08-08

**Written and committed before the widened net is written.** `tests/test_tautology_sweep.py`
declares that it examines every matching assertion in `tests/`, and examines the first comparison of
each assert and no other, while counting one assert twice. It is the third artefact in a row to land
inside the class it was built to close, and the numbers about to move are the ones it reports about
itself — a net measuring its own reach.

**One number in this prediction was handed to me and is not mine.** An audit removed the `break`
alone and reported 82 matches, an identical set, 0 added and 0 gone. I will re-run it, but I am
recording that I knew the answer before predicting it; a prediction made after the fact is worth
naming as such rather than presenting as foresight. The widening below is broader than that change,
so the run is not the same run.

**The prediction.** Matches stay at **82**. Asserts fall from 633 to **632**, the single duplicate
being `test_rebuild.py:250` inside `_resolve` nested in `_resolver_for`. Modules stay at **19**. The
three edges the net does not reach today — an `AsyncFunctionDef`, an assert outside any function, a
`.py` file in `tests/` that is not `test_*.py` — are each measured at zero, so covering them moves
nothing now and is done for what the declaration says rather than for what the tree contains.

**How it will be tested, stated in advance:** the net's own reach is tested by *planting*, at each
granularity at which the surface can shrink, and observing the module go red — not by re-reading the
match set, which is the artefact under suspicion. The counts are read off the repaired net; the
reach is not.

Four outcomes, and what each licenses:

1. **Matches unchanged at 82.** The expected outcome, and the one with the most ways to be
   misread. It licenses exactly this: *today*, no second-or-later comparison in `tests/` matches
   Pass C or D. It does **not** license "the gap was empty" as a statement about the gap, and it
   does not license "the net is now complete". **Corrected 2026-08-08: the licensing argument here
   originally rested on a plant that established nothing.** The planted second conjunct unparsed to
   a string already in `PINNED`, so a set-keyed record could not register it under the broken net or
   the repaired one, and the sentence that read "a planted instance went undetected, so the gap
   demonstrably admitted one" was drawing a conclusion its plant could not support. The gap did
   admit one — shown afterwards by a *novel* expression in the same position, green under the
   restored `break` and red without it — so the conclusion survives and the evidence for it does
   not. The five second comparisons that exist are four comprehension filters neither
   pass matches by construction and one attribute-against-attribute compare Pass D excludes on form;
   that is a fact about the criteria meeting today's tree, and the two zeros this module has already
   over-read are recorded in `HANDOFF.md` and in the section above.
2. **Matches grow.** Then the gap was hiding matches, the reported 82 was wrong as a description of
   `tests/`, and every classification resting on it is reopened.
3. **Matches shrink.** Then the widening broke a criterion. That is a finding about the net, not
   about `tests/`, and no count from that run may be reported.
4. **Asserts do not fall to exactly 632.** Then the double-count is not the single site measured,
   and the counter's defect is larger than one nested function.

Outcome 1 is the one to watch, and not because it is unlikely. It is the outcome under which every
number in the report is identical to the numbers the defective net produced, so nothing in the
output distinguishes a repaired net from the broken one — only the planting does, which is why the
mutations at each granularity are part of this change and not a follow-up to it.

### Pre-registration: what building the quantitative layer would mean, 2026-08-08

**Written and committed before `bzk/quant/` exists as anything but a docstring.** I11 has been the
unmet invariant blocking the most since Slice 4b, and closing it touches every `SiteObservation` in
the graph. The temptation this pre-registration exists against is the one every previous round hit:
reporting the ids as unchanged when nothing was ever capable of changing them, and calling that a
confirmation.

**The prediction rests on a premise that is verifiable rather than assumed, and the premise is
stated first.** `quant_ref` is in the *Excluded columns* cell for both observation types in §3's
identity table (`ONTOLOGY.md` §3, the `SiteObservation` and `ProteinObservation` rows), and
`tests/test_schema.py` asserts that identifying ∪ excluded partitions every node's columns. So
populating it *cannot* enter an identity tuple — checked directly:
`schema.IDENTITY['SiteObservation'].fields` is `('candidate_proteins',)` and holds no `quant_ref`.
A prediction of no movement is therefore a prediction about the code doing what the guarded
partition says, not a hope.

**The prediction.** After the layer lands and a full rebuild runs:

* symmetric difference **0** over **11,730** node ids and **9,217** edges, across all 24 labels and
  33 relationships;
* refusals unchanged at **27**;
* **2,029** `SiteObservation` and **4,561** `Protein`;
* wall clock within ~10% of **69.0 s**, which is the baseline **measured on the unchanged tree today**
  rather than the 119.9 s recorded in §8 from a different container — quoting the stale figure would
  make any comparison a statement about hardware.

**How it will be tested, stated in advance:** a full rebuild into a separate database, then a
per-label id diff against `~/.bzk-omics/graph.kuzu`. *Not* by re-reading §3's partition or
`schema.IDENTITY`, which is what produced the premise; a partition cannot test the code that is
supposed to respect it.

**Added 2026-08-08, after the fact and marked as such:** that method covers the id diff and **not
the wall clock**, which is the only prediction here whose test was never registered. A band was
stated, a single run was taken against it, and nothing said how many runs or what spread would
count. The consequence is in the result below.

Four outcomes, and what each licenses:

1. **Nothing moves.** The expected outcome and the weakest. It licenses "the layer is additive at
   the graph", nothing more — in particular it says nothing about whether the matrix is *correct*,
   which is a separate claim tested by reading values back rather than by ids not moving.
2. **An id moves.** Then `quant_ref` reached an identity tuple despite the partition, which would
   make the §3 guard itself unsound, and that is the finding — larger than the layer.
3. **The rebuild refuses, or the refusal count moves off 27.** Then writing the matrix changed what
   the adapter admits, which means the matrix write is not additive to ingestion and the two are
   entangled where the scope assumed they are not.
4. **Wall clock moves by much more than 10%.** Then the columnar write is not the cheap part the
   design assumes, and the "re-read from the deposit every run" cost this replaces was mis-stated.

Outcome 1 is the one to watch, and the reason is specific rather than generic: **the ids could not
have moved.** The partition guarantees it, so a report of "0 differing" carries almost no
information about this turn's work, and every temptation is to present it as though it did. The
claim that carries information is the one about values read back out of DuckDB, and it must not be
allowed to borrow the id diff's authority.

**Result, 2026-08-08 — outcome 1 on the graph, and outcome 4 on the clock.**

Everything predicted about the graph held: **11,730 node ids, symmetric difference 0** across all 24
labels; **9,217 edges, none differing** across 33 relationships; refusals **27**; **2,029**
`SiteObservation`; **4,561** `Protein`. As pre-registered, this licenses "the layer is additive at
the graph" and nothing more — the partition guaranteed it, so the number is a check that the code
respected a guard, not a finding.

**The wall clock is the finding, and it is outcome 4.** The first implementation took the rebuild
from **69.0 s to 235.2 s**, far outside the ±10% band. Attributed rather than guessed: the adapter's
`parse` is **3.45 s** and the columnar write was **165.2 s for 48,696 cells — 3.4 ms each**, which
is the *same* per-row cost `HANDOFF.md` §8 measured for the graph's per-statement write. The write
used `executemany` and its docstring cited that very measurement as the reason to batch; it was one
round trip per row against the primary key's index all the same. Replaced with a single
`INSERT OR REPLACE … SELECT` over a registered frame: **1.43 s**. So the design's assumption that
the columnar write is cheap is true of the bulk path and was false of the code that claimed to take
it. Those two figures are attributed and stand.

**The rebuild wall clock is withdrawn as a result, 2026-08-08.** This paragraph said the rebuild
*"returns to 62.2 s"*, which asserted restoration for a number **below** its 69.0 s reference, and
62.2 s sits **0.1 s inside** the band's lower edge — converting the declared outcome 4 into
prediction-met on a margin the instrument cannot resolve. Re-measured, three rebuilds per tree:

| tree | runs (s) | median | spread |
|---|---|---|---|
| pre-layer (`a9d03e1`, no cells, no DuckDB file) | 68.1, 64.7, 58.4 | 64.7 | **9.6 s** |
| current (`d7862e8`, 48,696 cells) | 74.5, 59.0, 57.6 | 59.0 | **17.0 s** |

**A 0.1 s margin is not resolvable by this instrument, and neither is the band.** The band is 13.8 s
wide (62.1–75.9) and the within-tree spread is 9.6–17.0 s, so a single run cannot place a tree
inside or outside it: two of the three current-tree runs fall *below* the band and one falls inside.
The honest record is that **the clock prediction was not established either way** — not that it was
met, and not that it failed.

**The 6.8 s is not attributed to the change, and the reason is that there is nothing to attribute.**
69.0 s was a single draw, and the pre-layer tree's own range is 58.4–68.1 s, so 69.0 sits at or above
its top. The two distributions overlap almost entirely, and the tree that does *more* work has the
**lower** median — 59.0 against 64.7 — which is itself the proof that the difference is run-to-run
variation rather than an effect. n = 3 per tree; the conclusion rests on the spread exceeding the
margin by two orders of magnitude, not on the medians.

**The claim that carries information, kept separate from the id diff as pre-registered.** All 24
cells of one real observation were read back out of DuckDB and each was found in its own column of
the deposit — **24 of 24**, 12 of them null where MaxQuant wrote `NaN`. `quant_ref` is `site_values`
on all 2,029 observations and **NULL on none**, which is I11's violation state absent.

**Regenerability, established by running rather than inherited from `OPERATIONS.md` §1: value-for-
value, not byte-for-byte.** Two rebuilds produce different file digests and identical row digests;
deleting `quant.duckdb` and rebuilding reproduces the content exactly. The distinction matters
because a DuckDB file carries metadata and free-space layout that byte equality would compare too,
so byte-for-byte is the wrong question to ask of this store — `OPERATIONS.md` §1 is amended to say
which one it means.

### Pre-registration: what deciding where a gene symbol lives would mean, 2026-08-08

**Written and committed before any code changes.** Gene symbols are the last thing `ROADMAP.md`
§ *Weeks 5–6* names as blocking a literal reading of *"through the real pipeline"*, and the
temptation here is the opposite of the previous rounds': not to over-read a green number, but to
route the symbol to whichever column is reachable and call target identification solved.

**A new requirement, introduced here and not previously recorded anywhere in this repository:
every prediction states how it will be measured and at what precision.** A prediction whose
instrument cannot resolve its own margin is not a prediction. That is what the 62.2 s figure cost —
recorded below as an instance and, until now, not generalised into the format that produced it.
Where no instrument can resolve a quantity, the honest move is to make no prediction about it, and
this section makes none about wall clock for that reason.

**The starting state, measured before predicting anything** — 4,561 `Protein` nodes, **0** with a
non-null `name`, **0** `Gene` nodes; 2,261 cached UniProt entry files, **2,128** carrying a non-null
`gene`; and of the graph's 4,561 accessions, **3,254** would get a symbol from cached bytes alone.
The **1,307 shortfall** breaks down as 1,180 accessions with no cached entry file at all and 127
whose cached entry carries no `gene`.

**The premise the id prediction rests on, verified rather than assumed.** `Protein.name` is in the
*Excluded columns* cell of §3's identity table, `schema.IDENTITY['Protein'].fields` is
`('accession',)`, and `tests/test_schema.py::test_identity_table_matches_ddl` asserts that
identifying ∪ excluded partitions every node's columns — so §3's row is authoritative rather than
decorative, and no value written to `name` can reach an identity tuple.

| Prediction | Instrument | Precision |
|---|---|---|
| No node id moves: symmetric difference **0** over 11,730 ids, 24 labels | rebuild into a separate database, per-label id diff against `~/.bzk-omics/graph.kuzu` | exact set equality — discrete, no margin |
| Refusals **27** | the rebuild's own refusal list | exact integer |
| **2,029** `SiteObservation`, **4,561** `Protein` | `count_nodes` on the rebuilt graph | exact integer |
| `Protein.name` non-null: **0** | Cypher count on the rebuilt graph | exact integer |
| The 14 targets are **not** identifiable from stored content | query the graph for any stored symbol — `Gene` count, `Protein.name` — and attempt the match without the deposit | discrete: either a symbol is stored or it is not |

The fourth is a prediction of **zero by decision, not by failure**, and it is the one this section
exists to keep honest. If the symbol's home turns out to be `Gene.symbol`, then the only fact
available offline — the symbol, on 2,128 cached entries — has nowhere to go, and `Protein.name` gets
nothing this turn. Predicting 0 in advance is what stops that outcome being presented afterwards as
a deliberate scoping choice if it was in fact a decision made to avoid a refetch.

Four outcomes, and what each licenses:

1. **All five hold.** The decisions are additive at the graph and change no stored value. It
   licenses "where the symbol belongs is now decided and recorded"; it licenses nothing about
   target identification, which the fifth prediction explicitly says stays where it is.
2. **`Protein.name` becomes non-null.** Then the symbol was routed onto `Protein`, and the reasoning
   for that has to survive the objection that `Gene.symbol` already exists — two homes for one fact
   is what `CLAUDE.md` calls a defect.
3. **An id moves.** Then §3's Excluded-columns row is not what the guard enforces, which makes the
   guard unsound and is a larger finding than this turn.
4. **Refusals or counts move.** Then a documentation-and-decision turn changed ingestion, which
   means the resolver path is entangled with the adapter's refusals in a way nothing records.

Outcome 1 is the one to watch, and for a reason specific to it: **it is indistinguishable at the
graph from having done nothing.** Every number is the number the unchanged tree produces, so nothing
in the output can show that the turn's work happened, and the only evidence for it is the reasoning
and the withdrawn artefacts. That is the correct shape for this turn and it is also the shape a turn
takes when it quietly failed to do anything, so the two must be told apart by what was decided and
recorded rather than by what was measured.

### Pre-registration: what minting `Gene` would mean, 2026-08-09

**A protocol breach, disclosed first, because a pre-registration that hides one is worse than
none.** *"Pre-registration, before any code runs"* was not honoured in full. Three classes of
measurement were taken before this section was written: the mandated opening rebuild (which the
turn orders first, so that one is in order), the offline graph-and-cache counts the turn asks for
as *"what is measurable without new fetches"*, and — the actual breach — **the three HGNC
authority lookups that settle step 0's first contradiction.** Step 0's verdict depends on those,
which makes them exactly the class a pre-registration exists to stop being adjusted around. They
are therefore recorded below as **measurements already taken**, not as predictions, and nothing in
this section claims foresight about them. Everything after this paragraph was genuinely unmeasured
when it was written.

**Already measured, before this section (no foresight claimed).**

| Measured | Instrument | Result |
|---|---|---|
| Starting state | `python -m bzk.rebuild` | 2,029 sites, 27 refused, 57 tables — unmoved |
| The four figures at `HANDOFF.md` §*What is left of ROADMAP's v0.1 exit* | Cypher over `~/.bzk-omics/graph.kuzu` | 4,561 `Protein`, 0 named, 0 `Gene`, 0 `ENCODES` — all four unmoved |
| Reach from cached bytes | cached `entry/*.json` against the graph's accessions | 3,254 of 4,561; 1,180 no cached file, 127 cached with no `gene` — unmoved |
| `HGNC:5699` | `rest.genenames.org/fetch/hgnc_id/HGNC:5699` | `IGHVIII-38-1`, an immunoglobulin heavy variable pseudogene — **not MX1** |
| `HGNC:4053` | `rest.genenames.org/fetch/hgnc_id/HGNC:4053` | `ISG15`, `uniprot_ids: ['P05161']` |
| MX1 | `rest.genenames.org/fetch/symbol/MX1` | `hgnc_id: 'HGNC:7532'`, `uniprot_ids: ['P20591']` |
| Cached entries by `entry_type` | the 2,261 tier-1 files | Swiss-Prot **1,125**, TrEMBL **1,058**, Inactive **78** |
| Whether any cache file already holds a cross-reference | key-set difference against `_Entry`'s eight fields | **0 of 2,261** |
| When the entry tier was last written | `fetched_at` in every tier-1 file | 1,054 on 2026-08-07, 1,207 on 2026-08-08 — the ingestion dates; nothing has refreshed it |

**The step-0 spelling decision, registered before it is implemented.** HGNC's own identifier is
rendered `HGNC:7532` — that is literally the string its REST API returns in `hgnc_id`, measured
above. §4's rule is *"the local part keeps its authority's casing"*, with `chebi:CHEBI:15377` and
`go:GO:0032020` given as correct. Nine of §3's ten rows already carry the authority's rendering
verbatim; `hgnc:4053` is the only row that strips it. So the decision registered here is
**`hgnc:HGNC:7532`, and §3 and §4's bare examples are the losing side** — not because doubling
reads well, but because the alternative requires declaring one authority exempt from a rule three
others already follow, with no reason available to state. The decision is registered rather than
described because it is falsifiable by the code: if it costs anything structural, that shows up as
a failing test rather than as an argument.

| Prediction | Instrument | Precision |
|---|---|---|
| P1 — `check_curie_case('hgnc:HGNC:7532')` is **accepted today** | call it; outcome is a return or a `KeyError_` | exact, binary |
| P2 — `check_curie_case('hgnc:7532')` is **also accepted today**, so the builder currently mints two ids for one gene | same | exact, binary |
| P3 — widening `_Entry` with a **defaulted** field triggers **no refetch**: a real cached file loads with the new field `None` | a scratch subclass and a session that raises on any call, against a copy of one real cache file | exact, binary — a fetch either happens or it does not |
| P4 — HGNC cross-reference coverage (frame, *n* and selection below) | live `GET rest.uniprot.org/uniprotkb/{acc}.json`, in memory, never written to the cache | 95% Wilson interval per stratum; see below |
| P5 — at most **one** HGNC cross-reference per entry across the sample | same fetches, counting `database == 'HGNC'` elements | exact integer over 120 |
| P6 — the new `hgnc` local-part guard **fires**: `hgnc:7532` raises, `hgnc:HGNC:7532` returns | the guard, then a mutation that removes the branch, with the mutated file read back before the run | exact, binary |
| P7 — suite green above 325; sweep floor holds (≥ 20 modules, ≥ 655 asserts), 0 gone | `pytest`; `tests/test_tautology_sweep.py` | exact integers |

**P4's frame, stated before it is drawn.** Frame: the **2,261** canonical accessions that have a
tier-1 entry file today — not the graph's 3,315 canonical accessions, because the 1,054 that were
never resolved are the adapter's resolution-policy shortfall and a re-capture would fetch them
fresh either way. Stratified on the cached `entry_type`, because coverage plausibly differs by
kind and the strata are the units the decision turns on: Swiss-Prot *N* = 1,125, TrEMBL
*N* = 1,058, Inactive *N* = 78. ***n* = 40 per stratum, 120 fetches total.** Selection is
systematic and deterministic — each stratum's accessions sorted ascending, every ⌊*N*/40⌋-th taken
from index 0 — so the draw is reproducible without a seed. A hit is a `uniProtKBCrossReferences`
element whose `database` is `HGNC` and whose `id` matches `^HGNC:[0-9]+$`.

**P4's precision, and what it is not asked to resolve.** At *n* = 40 the 95% Wilson interval is at
its widest ±15.5 pp (*p* = 0.5), and a clean 40/40 gives a lower bound of 91.2%. The sample is
asked only to separate *essentially all* (≥ 90%) from *about half* from *essentially none*, per
stratum — gaps far larger than the margin. **It will not be used to resolve any difference below
about 9 pp**, and no figure from it will be quoted without its interval. Registered predictions:
**Swiss-Prot ≥ 90%; Inactive = 0%** (an inactive entry is a deletion stub). **For TrEMBL, no
prediction is registered** — I have no basis for one, and a guess written in the prediction column
is precisely the defect this format exists to catch.

**The turn's outcome, registered as a prediction because it could go either way.** **`Gene` is
predicted *not* to be minted this turn.** The chain: no I9 input carries an HGNC id (0 of 2,261,
measured); obtaining one means re-capturing the entry tier, which changes what an I9 input contains
and is an ADR rather than a side effect; and a builder written against a field that is `None` on
every cached entry emits **0** `Gene` nodes, which is the partial table this turn forbids
producing. **Falsifier, stated so the prediction is not self-sealing:** if P3 or P4 exposes a route
that mints `Gene` from an input that already exists, the prediction is wrong and the builder is
written in this turn rather than deferred. The prediction is registered *because* the comfortable
outcome and the correct outcome coincide here, which is when a stated falsifier is worth most.

**What would make this turn a failure rather than a deferral.** Deciding the spelling and *not*
guarding it — the class this repository has now been caught in three times, where a machine-
checkable rule is recorded as prose and the record then reads as though it were enforced. The
spelling decision reaches an authority that is about to occupy an identifying position, so it is
enforceable now, and a `HANDOFF.md` note would not close it.

#### Outcome, 2026-08-09 — every prediction held, and one instrument degenerated

| Prediction | Result |
|---|---|
| P1 `hgnc:HGNC:7532` accepted today | **held** — returned unchanged |
| P2 `hgnc:7532` also accepted | **held**, and understated: `hgnc:hgnc:7532` was accepted too, so it was **three** spellings of one gene, not two |
| P3 defaulted widening triggers no refetch | **held** — loaded `P20591` with `gene='MX1'`, `hgnc_id=None`, no call; the required-field variant refetched, as the contrast predicted |
| P4 Swiss-Prot ≥ 90% | **held** — 40/40, 95% CI [0.912, 1.000] |
| P4 Inactive = 0% | **held**, and then censused: 0 of 78, exact |
| P4 TrEMBL — no prediction registered | 37/40, 95% CI [0.801, 0.974]. Recorded as the reason the abstention was right: a guess would have been low |
| P5 at most one HGNC cross-reference per entry | **held** — 0 or 1 across all 198 entries fetched; never 2 |
| P6 the new guard fires | **held** — two mutations, each read back off disk before running, each failing the new tests and only those; reverted and green |
| P7 suite and sweep | see the four-point report on the commit |
| **`Gene` is not minted** | **held.** The falsifier did not fire: no existing input carries an HGNC id, tier-2 stores bare sequence with no FASTA header, and `raw/` carries symbols |

**The instrument that degenerated, reported rather than quietly repaired.** P4's registered
selection was *"every ⌊N/40⌋-th from index 0"*. For the inactive stratum *N* = 78, so the step is 1
and the rule returns **the alphabetically first 40** — a clustered draw, not a spread one. The
procedure was followed exactly as registered and the registered procedure was wrong for any stratum
with *N* < 2*n*. The fix taken was not a redraw but a **census**: 78 fetches, 0 hits, no interval
needed. Worth recording because the defect was in the pre-registration itself, which is the one
place the format cannot catch its own error — and because the result would have looked identical
either way, so nothing in the output would have surfaced it.

**What this outcome table does not cover.** It says every prediction held; it does not say the
predictions covered the turn. The spelling decision, the two document corrections and the
entry-tier finding were all *unpredicted* — three of the four things this turn produced. A
pre-registration bounds the ways a turn can fool itself about numbers it went looking for; it says
nothing about what it finds on the way.

### Pre-registration: what settling the entry tier's key would mean, 2026-08-09

**Written and committed before any code changes.** The state is not re-established here; it is
recorded at `ONTOLOGY.md` §8 I9, `OPERATIONS.md` §3 and `HANDOFF.md` §8. What is open is the
decision, and the temptation specific to it is to pick the shape that costs least to write rather
than the one the archive supports — the entry tier has never been refreshed, so every option looks
safe from where the repository currently sits.

**Confirmed before predicting: 2,029 sites, 27 refusals, 4,561 `Protein`, 0 named, 0 `Gene`, 3,254
reachable — all unmoved.**

**Measured before deciding, because the three shapes are not equally available and the archive
says which.** No foresight is claimed for these; they are the inputs to the decision, not tests of
it.

| Measured | Result |
|---|---|
| `sv` files per accession in the sequence tier | **{1: 2845}** — every accession has exactly one version archived; none has two |
| `entry.sequence` against `seq/{acc}#sv{n}.txt` | **2,014 identical, 0 differing** — the entry tier's copy is a duplicate of an immutable file |
| `sequence_version` recoverable from the immutable tier by glob | **2,183 agree, 0 disagree, 0 unrecoverable**; the remaining **78** carry no version at all and are exactly the `Inactive` entries |
| `data/curation/resolution_PXD018299.json` | a **642-byte summary** — `n_sampled: 20`, `sequence_versions: [1,2,3,4]`. **Not** a per-accession pin |
| Readers of `fetched_at` in `bzk/` or `tests/` | **none** |
| A defaulted new field, pre- vs post-widening | **distinguishable on disk** (key absent vs `"hgnc_id": null`), **not through `_load_entry`**, which fills both from the default |

**The decision registered, before it is implemented: shape 3 — split by identity-bearing-ness.**
The entry tier keeps its non-versioned key and is **declared** a mutable snapshot; everything
identity-bearing moves to the immutable tier as a write-once pin at `seq/{canonical}#sv{n}.meta.json`
carrying `entry_type`, `reviewed` and the sequence, with the version in the key. Reasons, each
resting on a row above rather than on preference:

- **Shape 1 is rejected on a measurement, not on cost.** Versioning the entry key converts a silent
  overwrite into an ambiguous read: with two captures present, nothing says which one a rebuild
  must use. `raw/` escapes that because the curation record cites a `content_hash`; the sequence
  tier escapes it because the site key already names the version. The entry tier is read *before*
  any id exists, and the one record that could name a capture is a summary. So versioning needs a
  new per-accession manifest — a new I9 input — to be a fix at all. Separately, every candidate
  version component fails: `sequence_version` is circular (the fetch is what reveals it), a content
  digest changes on every re-fetch because `fetched_at` is inside the payload, and `fetched_at`
  itself is settled below rather than promoted into a key.
- **Shape 2's requirement is met by shape 3's mechanism, which is why they converge.** §11 Q6 says
  a re-resolve refuses sites keyed against amended sequences and the only signal is a changed
  refusal count reading as data drift. That mechanism runs entirely through `sequence` and
  `sequence_version` — and both are already pinned immutably, measured identical on all 2,014
  comparable entries. Reading them from the pin rather than from the snapshot does not restate Q6's
  paragraph, it removes the path the paragraph describes. What it does **not** remove is `reviewed`,
  which steers I17's promotion and therefore which `ModificationSite` is keyed, and which nothing
  immutable records. That is the field the pin exists for.
- **`fetched_at` is settled as a *fetch* clock, and stays out of the key.** It is written only in
  `_fetch_entry` and never on a cache hit, so as a record of *when this file was written* it is
  exactly correct — `OPERATIONS.md` §3's 90-day *access* rule is what is wrong, being unimplementable
  against a clock that no reader reads. Shape 3 needs no version component in the entry key, so the
  question of using a compromised field as one does not arise.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| No node id moves: symmetric difference **0** over 11,730 ids, 24 labels | rebuild into a separate database, per-label id diff against `~/.bzk-omics/graph.kuzu` | exact set equality, no margin |
| Refusals **27**; **2,029** sites; **4,561** `Protein` | the rebuild's own report and `count_nodes` | exact integers |
| The backfill writes **2,183** pins and rewrites **0** of the 2,261 entry files | count `seq/*.meta.json` after; compare every entry file's `fetched_at` before and after | exact integers |
| The `hgnc_id` widening makes the next rebuild rewrite **2,261** entry files | count entry files whose `fetched_at` date is 2026-08-09 after the run | exact integer. A **smaller** number falsifies the premise that the resolver asks for every cached canonical, and would mean some cached entries were written by a path other than rebuild |
| `Gene` stays **0** | Cypher count | exact integer |

**On the `fetched_at` instrument, and what it cannot resolve.** `ONTOLOGY.md` §8 I9 records the
distribution across all 2,261 as 1,054 on 2026-08-07 and 1,207 on 2026-08-08, and this section uses
it for exactly one claim: **whether a file has been rewritten since ingestion.** For that it is
sound — it is written on fetch and only on fetch, so an unchanged value is proof of an unrewritten
file. It cannot resolve *when an entry was last read*, which is the use `OPERATIONS.md` §3 makes of
it, and it cannot distinguish two fetches within the same second. Neither limit bears on any
prediction above.

**The one selection rule, with its behaviour at the sizes it will actually meet.** Version recovery
globs `seq/{canonical}#sv*.meta.json`. **0 matches** → no pin; fall through to the snapshot and the
network, which is today's path unchanged. **1 match** → use it. **≥2 matches** → refuse, because the
archive holds two captures and nothing names which is authoritative; guessing the newest is the
overwrite this decision exists to remove. On the current archive the histogram is **{1: 2845}**, so
the ≥2 branch is **unreachable from the corpus** and must be tested synthetically or it will be
asserted and never run — which is what `ROADMAP.md` § *Outcome, 2026-08-09* records happening to a
selection rule whose boundary was not stated in advance.

**Q12, registered as conditional on the above.** If shape 3 holds, `hgnc_id` is non-identity-bearing
and belongs in the snapshot tier, where a re-capture cannot move an id — so widening becomes
permissible for the first time, and the defaulted-field trap is closed by the on-disk distinction
measured above: **key absent means *not captured* and refetches; explicit `null` means *captured,
no HGNC id* and does not.** `Gene` is still **not minted**: the refetch that would populate
`hgnc_id` produces cache state, not committed state, and a builder run before it would emit a
partial table.

**What would make this turn a failure rather than a decision.** Declaring the snapshot safe while
leaving an identity-bearing field reading from it. `reviewed` is the one that would be missed,
because unlike `sequence_version` it does not appear in any key and its effect on identity is one
step removed, through I17's choice of which protein a site is keyed against.

#### Outcome, 2026-08-09 — one prediction missed by one, and its falsifier named the reason

| Prediction | Result |
|---|---|
| Backfill writes **2,183** pins | **held** — 2,183, with 78 snapshots carrying no `sequence_version` (the `Inactive` entries) and 0 unreadable |
| Backfill rewrites **0** of the 2,261 entry files | **held** — every `fetched_at` unchanged across the run |
| Refusals **27**; **2,029** sites; **4,561** `Protein` | **held** — and 1,062 `ProteinSequence`, 11,743 node and 9,229 edge statements, 48,696 cells, every figure identical to the pre-change run |
| The widening makes the rebuild rewrite **2,261** entry files | **missed: 2,260.** The registered falsifier was *"a smaller number would mean some cached entries were written by a path other than rebuild"*, and that is exactly what it is — see below |
| `Gene` stays **0** | **held** |
| No node id moves | **not measured as registered** — see below |

**The one that missed is `P20591`, and it is worth more than the prediction was.** It appears **0
times** in the deposit and has no `Protein` node, so the rebuild has never had reason to ask for it;
its cache entry was written on 2026-08-07 by an exploratory lookup, not by the pipeline. The
premise the prediction rested on — that every cached canonical is one the resolver asks for — is
false by exactly one, and the one is MX1: the accession this repository's worked example and its
entire `Gene` thread are written around, cached because it was looked up by hand.

**The id prediction was lost by a procedural error, and no substitute is offered as though it were
the measurement.** The instrument was *"rebuild into a separate database and diff per-label against
`~/.bzk-omics/graph.kuzu`"*, and that needed the pre-change id set captured **before** the rebuild
dropped it. It was not. What exists instead is weaker in one way and stronger in another, and both
halves are stated: every count is identical, which an id could move without disturbing; and
**across all 2,183 pinned accessions, the pin and the re-fetched snapshot agree on all three
identity-bearing fields — 0 disagreements** in `sequence_version`, `entry_type` and `reviewed`.

**That zero is the honest result and it cuts against the demonstration.** Nothing moved at UniProt
between ingestion and the re-fetch, so the pin was never called upon, and **the corpus cannot show
that the split works** — a run with the pin and a run without it would have produced the same
graph. Only the synthetic cases in `tests/test_pins.py` exercise the protection, which is why they
are written against a snapshot deliberately made to disagree. A green rebuild here is consistent
with the pin doing nothing, and saying otherwise would be the self-confirming shape this file
records three times already.

**Unpredicted, and a change to an I9 input rather than a detail.** The sequence archive grew from
**2,845** files to **3,014**. The 169 are canonical sequences for accessions the pipeline had only
ever reached as isoforms: `resolve` now archives the canonical sequence whenever it writes a pin, so
a pinned accession always has its bytes on disk rather than falling back to the mutable snapshot.
That completes the pin's guarantee and it was a deliberate line, but no prediction was registered
for it and it should have been — it is the sort of consequence that shows up later as an unexplained
count. `bzk drift`'s receipt now correctly reports a **changed archive set** rather than staleness.

**The live sample from earlier the same day, now censused.** It projected ~2,104 of 2,261 entries
carrying an HGNC cross-reference. The full re-fetch gives **2,102 with an id and 158 with an
explicit null** — inside the interval and two off the point estimate. Recorded because the sample
was drawn to decide whether the capture was worth its cost, and this is the only chance to find out
whether it was any good.

### Pre-registration: what minting `Gene` and `ENCODES` would mean, 2026-08-09

**Written and committed before any code changes.** The blockers are cleared, which is the hazard:
the previous three turns each ended by naming a reason not to build, and a turn that finally builds
is the one most likely to accept its own projection as a result.

**Confirmed first — and the baseline id set captured before the rebuild dropped it**, which is the
instrument this file records losing on the last turn. `11,730` ids across 11 non-empty labels of 24
node tables, held outside the tree: `Analysis` 2, `Dataset` 1, `Experiment` 1, `ModificationSite`
2,029, `Modifier` 3, `ModifierAssignment` 2,029, `Project` 1, `Protein` 4,561, `ProteinSequence`
1,062, `Sample` 12, `SiteObservation` 2,029. The rebuild then reported **2,029 sites, 27 refusals,
11,743 node and 9,229 edge statements, 48,696 cells**, and the graph **4,561 `Protein`, 0 named,
0 `Gene`, 0 `ENCODES`** — all unmoved. Wall clock **96.1 s**, one draw.

**The residual of 1 is `P20591`, and it was reported in conversation and written down nowhere.**
The `hgnc_id` census over the 2,261 snapshots is **2,102 with an id, 158 with an explicit null, 1
with the key absent**, and the last is MX1: `fetched_at` 2026-08-07T15:39, `gene` MX1, `sv` 4,
Swiss-Prot. It appears **0 times** in the deposit and has no `Protein` node, so the rebuild has
never had reason to ask for it and the widening never reached it. It is in the cache because it was
looked up by hand — the accession this repository's worked example is written around.

**Step 0's decision, registered before implementation: `Gene.id` may be derived from a snapshot
field, and the guarantee sentence was a description of its contents rather than a principle.**

*Option 1 — move `hgnc_id` to the pin — is rejected as **wrong**, not as harder.* The pin's whole
property is that it is written once. A pin created before the field existed carries no `hgnc_id`
key, and there are 2,183 of them; filling one means **rewriting a write-once record**, which is not
a cost but the negation of the thing. It does **not** reopen the backfill window, and the reason is
worth separating from the refusal: that window was about preserving the *original* capture, and
`hgnc_id` was never captured at ingestion, so there is no earlier value to lose. What breaks is
write-once itself, not the window. Independently, the pin is keyed `{canonical}#sv{n}` — an HGNC id
has no relation to a sequence version, so a version bump would mint a second pin whose `hgnc_id` is
a fresh capture presented with the standing of a pinned one.

*Option 2 — adopted, and it argues against I7 and §4 rather than against a docstring's phrasing.*
The line the pin actually draws is not *"no id depends on the snapshot"* but **a snapshot field may
not reach the composition of a composed key, directly or by selection**. That is §4's own division
of reference nodes into composed and authority-assigned, and it sorts every field correctly:
`sequence_version` is a *component* of `uniprot:{acc}#sv{n}` and of every `ModificationSite` built
on it; `reviewed` selects which protein a site is keyed against, so it reaches composition
indirectly; `gene` and `last_seq_update` reach neither. `hgnc_id` reaches neither either —
**`Gene.id` is not composed**, and §3's identity table says so in the document rather than by
inference: `Gene`'s identifying fields are `—`, its anchors are `—`, and §4's authority-assigned
shape is *"the id **is** the external identifier, CURIE-prefixed; nothing local composes it"*, which
makes CURIE-prefixing explicitly not composition. Against I7 (:825), *reference node ids are derived
from their content* — `hgnc:HGNC:7532` **is** HGNC's content, and two graphs that both saw that
cross-reference converge on one node, which is the clause's stated purpose.

*What option 2 costs, stated rather than discovered.* If UniProt's cross-reference for an accession
changes, a rebuild produces a **different `Gene` node and a different `ENCODES` edge**. That is a
real difference between rebuilds and it is accepted, because it is a different failure from the one
the pin exists for: a pinned field moving **re-keys an existing node and every evidence digest
anchored on it**, silently and without changing a count. A `Gene` change moves no id, cascades into
no digest — `Gene` appears in no `IDENTITY` spec's anchors, already asserted in `tests/test_keys.py`
— and changes a node count, which is visible.

*Option 3 is not reached*, since option 2 is established rather than merely cheaper.

**Step 1's multiplicity choice: 198 is taken as the evidence, and arrival is made a refusal.** The
census is not ordered and its cost is stated so the refusal is a decision rather than an evasion:
re-reading every payload means re-fetching all 2,261 snapshots, **measured at 29m55s** on
2026-08-09. It is not paid because it **cannot change the decision** — a second HGNC cross-reference
is refused whenever it appears, so the rate at which it appears has no bearing. What the census
would buy is confidence in a rate the guard makes irrelevant. Today `uniprot.py` takes the first
match, which is a *silent* decision; that becomes a refusal. **The residual is stated and bounded:**
the 2,102 ids already captured were captured under first-match, so if any had two the first was
taken silently and the guard is prospective only. The blast radius of one such case is one
`Protein`'s `ENCODES` edge — `Gene.id` is authority-assigned and anchors nothing, so it cannot
propagate.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| **No existing node id moves**: symmetric difference **0** over all 11,730 baseline ids, per label | the captured baseline, diffed per label against the post-build graph | exact set equality, no margin |
| Refusals **27**; **2,029** sites; **4,561** `Protein` | the rebuild's own report | exact integers |
| **`Gene` = 1,104**; **`ENCODES` = 3,230** | Cypher counts | exact integers. Derived from the cache→graph projection, so a mismatch means the builder's wiring differs from what the cache supports, not that the projection was optimistic |
| Absence partitions exactly: **1,180** no cached entry + **151** explicit null + **0** `NOT_CAPTURED` + 3,230 = 4,561 | Cypher plus the snapshot census | exact integers |
| Target identifiability: **12** of the 14 by exact symbol, **13** allowing one rename, **1** genuinely absent | match the 14 in `pxd018299_baseline.py` against stored `Gene.symbol` | exact integers over a set of 14 |
| `bzk rebuild` wall clock | **at least three timed runs, reported as a spread** | ±10 s at best — `OPERATIONS.md` §5 is not corrected from one draw against one draw |

**Each identifiability outcome's meaning, fixed in advance.** *13 of 14* means the two shortfalls
have different causes and only one is a gap: `DDX58` is stored as **`RIGI`** — HGNC renamed it, and
`hgnc:HGNC:19102` is the same node under either name — while `OAS1`'s only `Protein` in the graph is
`H0YI20`, a TrEMBL fragment with no gene and no cross-reference. *If it comes out 14*, something
supplied a symbol the cache does not have and the source must be found before it is believed. *If
it comes out below 12*, the builder is dropping symbols the projection says are there. **And if the
count is anything other than 14, that is not a failure**: `ROADMAP.md` § *What v0.1 must contain*
holds that the number is not the criterion, and identifiability is a different quantity from
recovery — this section makes **no** claim about recovery and the differential is not run.

**The rename is the finding this prediction exists to surface.** Matching a 2020 deposit's
`Gene names` against stored symbols would miss `DDX58` while the gene is present, which is the case
for keying on `hgnc:HGNC:19102` rather than on a symbol string, made concrete rather than argued.

**What would make this turn a failure rather than a build.** Emitting `Gene` for 3,230 `Protein`s
and leaving the other 1,331 with an absent `ENCODES` edge that means three different things. The
three are not equally likely and that is the trap: 1,180 is the adapter's razor-pick policy and 151
is UniProt reporting no cross-reference, so a reader who assumes the common case reads a policy
artefact as a biological statement.

#### Outcome, 2026-08-09 — the projection was wrong by a factor of three, and it took the build to show it

| Prediction | Result |
|---|---|
| No existing node id moves: symmetric difference **0** over the 11,730 baseline ids | **held** — per label, 0 lost and 0 gained on all eleven. The twelfth label is `Gene`, (0 lost, 1,044 gained), which is the new table |
| Refusals **27**; **2,029** sites; **4,561** `Protein` | **held**, with 12,787 node and 10,288 edge statements against 11,743 and 9,229 |
| `Gene` = **1,104**; `ENCODES` = **3,230** | **missed: 1,044 and 1,059** |
| Absence partitions exactly, 1,180 + 151 + 0 + 3,230 = 4,561 | **partition held, every count wrong**: 3,492 `unresolved` + 10 `no_cross_reference` + 0 `not_captured` + 1,059 with an edge = 4,561 |
| Targets: **12** by exact symbol, **13** allowing one rename, **1** genuinely absent | **held exactly** — `DDX58` is stored as `RIGI` at `hgnc:HGNC:19102`; `OAS1`'s only `Protein` is `H0YI20`, a TrEMBL fragment |
| Wall clock from a spread, not one draw | **84.7 s / 100.6 s / 83.9 s**, n = 3 |

**Why the count prediction missed, and it is not a scoping matter.** The projection asked *how many
of the graph's 4,561 accessions have a cached entry carrying an `hgnc_id`* and got 3,230. The
builder asks a different question — *how many accessions does the resolver see* — and the answer is
about **1,069**, because the site adapter resolves only the razor picks and mints an accession-only
`Protein` for every other candidate in a protein group. The projection was a fact about the cache
presented as a fact about the graph. **The instrument was wrong, not imprecise**, so no interval
would have caught it; what catches it is asking which code path produces the number.

**The build was wrong before it was right, and the suite could not tell.** The first `Gene` build
put **3,492** proteins in the graph with a NULL `gene_absence` and no `ENCODES` edge — the exact
collapse §4's column exists to prevent, on the first run, with **344 tests green**. The partition
guard that should have caught it lives on `ResolvedProteins.__post_init__`, and those proteins never
pass through a `ResolvedProteins`: they are minted beside it, in two adapters. A guard on the object
one producer returns cannot cover a second producer. The fix is at the change-set — where both
producers pass — as `invariants._check_gene_absence`, and restoring the old adapter line now fails
four tests. **This is what the count prediction bought**: 1,059 edges against 3,230 predicted is
what made the graph worth querying at all, and the NULLs were only visible because the numbers were
checked one at a time rather than as a total.

**`OPERATIONS.md` §5's 119.9 s is corrected by this turn's own first measurement**, which is what
the opening rebuild was for. Three timed runs of the finished tree give **83.9–100.6 s**, spread
16.7 s, and the opening run on the unchanged tree gave 96.1 s. All four are below 119.9, which was
itself one draw. Recorded as a range with *n* stated, because a single draw replacing a single draw
is what `ROADMAP.md` § *the 62.2 s figure* records costing a false conclusion.

**What this outcome does not claim.** Identifiability is **not** recovery. 12 of 14 here means
twelve published symbols are answerable from stored `Gene.symbol`; it is not a recovery figure, no
differential was run, and no comparison to 12-of-14 or 9-of-14 is made or implied. `ROADMAP.md`
§ *What v0.1 must contain* holds that the number is not the criterion, which is why the meaning of
each outcome was fixed before the run rather than after.

### Pre-registration: what a read path over the graph would mean, 2026-08-09

**Written and committed before any code changes.** Everything built so far writes; nothing reads,
and the hazard specific to a first read path is that its output *looks* like an answer. A number
that leaves this layer without the status `ONTOLOGY.md` requires to travel with it is worse than no
read path, because it is quotable.

**Confirmed first, and one figure moved.** 2,029 sites, 27 refusals, 4,561 `Protein`, 1,044 `Gene`,
1,059 `ENCODES`, `gene_absence` at 1,059 / 3,492 / 10 — all unmoved. Wall clock **149.7 s**, and
that is **outside the 83.9–100.6 s range this file recorded yesterday from three runs**. The
correction is recorded below rather than in this section, but the fact belongs here: the instrument
that was tightened yesterday was contradicted by the next measurement taken with it.

**Measured before deciding, because two of the five questions turn out to have no data behind
them.** No foresight claimed; these are the inputs.

| Measured | Result |
|---|---|
| Empty node tables | `DifferentialResult`, `Imputation`, `Contrast`, `ProteinAssignment`, `ProteinObservation`, `Person`, `Software`, and the four out-of-scope reference types |
| `keying_basis` | `razor` 1,507, `reviewed_preferred` 522; `displaced_protein` non-null on exactly the 522 |
| `Analysis` | 2 — one `curation`, one `processing` (`quantity = intensity_multiplicity_summed`, `test` NULL) |
| Refusals in the graph | **no node table exists**; `Refusal` is a dataclass in `bzk/adapters/base.py` and lives only in an adapter's report |
| §7 `prov:Entity` reachability | all 2,029 `SiteObservation` reach an `Analysis` via `USED`→`Dataset`→`REPORTS_SITE` |
| Does one Kùzu query return an inference's basis? | **Yes** — `MATCH (o:SiteObservation)<-[:ASSIGNMENT_FOR]-(ma:ModifierAssignment) RETURN o.id, o.keying_basis, ma.basis, ma.confidence, ma.candidate_modifiers` returns all five in one row. `OPTIONAL MATCH` is supported and yields `None` for the missing side; a bare node returns as a `dict` of its properties; list parameters and `get_column_names()` work |

**Decision 1 — the read path is `bzk/query/`, a sibling of `quant/` and `stats/`.** Argued against
`ARCHITECTURE.md` §3's own boundary reasoning rather than by analogy: `curation/` is separate from
`adapters/` because a curation record is *not an engine's output*, carries no measurements, and runs
first to produce what an adapter consumes — the test is what a module produces and who consumes it.
A read path produces nothing that enters the graph and consumes what every writer has already put
there, so it is at the far end of that same axis and cannot be folded into any producer. It is
**not** `ontology/store.py`, and the reason is that module's own declared property: *"the only
module that writes"*, and *"`invariants.py` is deliberately storage-free"*. `ontology/` is schema,
invariants and the key builder, with exactly one storage-aware exception; a read layer is a second
storage-aware module, so it goes outside rather than widening the exception. `api/` — already in
the tree, unbuilt — is the consumer, which is what keeps this turn's stopping point real.

**Decision 2 — a query returns records carrying their status, never bare rows, and this layer *is*
I5's enforcement point.** `HANDOFF.md` §8 classifies **I5** and **I8**'s reachability half as
*WG — whole-graph / query-time, not written*, and names I5's mechanism as a per-entity
`unprovenanced` flag. That is this decision in concrete form, so answering *"is this the enforcement
point"* with *no* would leave the invariant homeless in the layer its own classification points at.
It is implemented, scoped to what §7 calls a `prov:Entity` — `Dataset`, `SiteObservation`,
`DifferentialResult`, `Figure` — because I5 says *entity node* and §7 is where that word is defined;
reference nodes are not entities and are not flagged. `ONTOLOGY.md` §8 I14's display half and
`ROADMAP.md` § *Weeks 7–8*'s *"ambiguity and correction status visible everywhere a number appears"*
settle the rest: **a bare number may not leave this layer.** A site's row carries its
`candidate_proteins` and the confidence of the assignment that named it; a differential row carries
its `Analysis`'s declared quantity and test; every entity row carries its provenance status.

**Decision 3 — an absent answer is a value, never an empty container.** The precedent is
`quant_ref = NULL` (§5.1): the node carries the reason its neighbour is missing. Applied here,
every query that can come back empty returns *why*, from a closed set. Two of the five are the hard
cases and both were measured above:

- **The differential table returns 0 rows because there are no `DifferentialResult` nodes**, not
  because no site was significant. Those are opposite meanings and an empty list is the same object
  for both.
- **The refusals query cannot be answered from stored content at all.** 27 refusals were reported at
  ingestion and the graph retains none of them: there is no node table, and `Refusal` never leaves
  the adapter. The query is written anyway and reports *not retained*, because that is the finding —
  the population report is not reconstructible from the graph — and a function that returned `[]`
  would bury it.

**A third case the scope statement assumes and the graph cannot support.** Question 5 asks, for each
absent symbol, *which of the three `gene_absence` states applies*. Those states are per-`Protein`,
and the route from a symbol to a protein runs through the `Gene` node that is missing by hypothesis;
`Protein.name` is null by decision (§4), so nothing else carries a symbol. So for a bare symbol the
attribution is **not available**, and the honest return is a fifth state saying so rather than a
guess. Registered here because it is a claim about the schema that the run can falsify: if any
absent symbol comes back attributed, there is a route I did not find.

**Decision 4 — tested against a fixture written through the real write path, plus one skipping
test against the real graph.** The fixture is not a convenience: **the real graph cannot exercise
two of the five queries at all**, having no `DifferentialResult` and no `Imputation`. It is built by
handing change-sets to `ontology.store.write_change_set`, which runs `invariants.validate` first, so
it cannot contain a shape an adapter could not produce — that is the closure for the risk that a
query is tested against data no producer makes. What it costs is stated: a fixture cannot catch a
query that is wrong about the *real* population, which is why the recorded figures get their own
test, and that one skips without `raw/`, making it the fourth such. Adding five would have made
coverage a function of who runs it; adding one keeps the numbers checkable without doing that.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| **No id moves and no count changes** — this turn writes nothing | rebuild, then per-label id diff against the current graph | exact set equality |
| Q1, differential table for the `processing` `Analysis`: **0 rows**, reported as *no results stored*, not as *none significant* | the query | exact integer plus a discrete state |
| Q2, one `ModificationSite`: `keying_basis` present on **all 2,029**; `displaced_protein` non-null on exactly the **522** `reviewed_preferred` | the query over every site | exact integers |
| Q3, imputation state for the `processing` `Analysis`: **empty set**, 0 `Imputation` — and a *set*, not a value | the query | exact integer |
| Q4, refusals: **0 recoverable** against **27** reported at ingestion, returned as *not retained* | the query | exact integers |
| Q5, of the 14 published symbols: **12 present, 2 absent**, and **both absent ones unattributable** | the query | exact integers over a set of 14 |
| I5: **0 unprovenanced** entities — 2,029 of 2,029 `SiteObservation` and 1 of 1 `Dataset` reach an `Analysis` | the provenance status on every returned row | exact integers |

**What Q5's 12 does not mean.** It is the same identifiability figure this file fixed on 2026-08-09,
and the fixing holds: **twelve published symbols are answerable from stored `Gene.symbol`; it is not
a recovery figure.** The differential is not run, `differential.py` is not switched off `Gene names`,
and no comparison to 12-of-14 or 9-of-14 is made or implied. A query that returns 12 must not be
readable as recovery, which is why the record it returns names what it counted.

**One boundary noted and not crossed.** `HANDOFF.md` §8's **EX** class puts I18's embargo check at
the first export, report or figure-writing path. A function returning records is not one — it writes
no file — so I18 is not landed here and is not weakened by anything here. The interface turn is the
one that trips that trigger.

**What would make this turn a failure rather than a read path.** Returning the empty differential
table as an empty list. Everything else in the design is downstream of that one distinction, and it
is the case where the wrong answer is indistinguishable from the right one at the call site.

#### Outcome, 2026-08-09 — every prediction held, and the fixture caught three wrong premises

| Prediction | Result |
|---|---|
| No id moves, no counts change | **held** — the turn writes nothing; the graph is unchanged and the closing rebuild reports the same figures |
| Q1: **0 rows**, reported as *not stored* | **held** — `Absence.NOT_STORED` |
| Q2: `keying_basis` on all **2,029**, `displaced_protein` on exactly **522** | **held**, and the 522 is *the same set* as the `reviewed_preferred` sites, which is the half I17 fails silently in |
| Q3: **empty set**, and a set rather than a value | **held** — `Absence.NOT_STORED` on both analyses |
| Q4: **0** recoverable against **27** reported | **held** — `Absence.NOT_RETAINED` |
| Q5: **12** present, **2** absent, both **unattributable** | **held** — `DDX58` and `OAS1`; `RIGI` present at `hgnc:HGNC:19102` |
| I5: **0** unprovenanced | **held** — `{'Dataset': (0, 1), 'SiteObservation': (0, 2029), 'DifferentialResult': (0, 0)}` |

**Every prediction held and the code was still wrong three times, which is the finding.** The
queries were written against premises about the DDL that nobody had checked, and the fixture — built
by handing change-sets to `store.write_change_set`, which validates — refused every one of them
before a single row came back. `RESULT_FOR_SITE` runs to a **`SiteObservation`**, not to a
`ModificationSite`; `RESULT_FOR_PROTEIN` runs to a **`ProteinObservation`**, not to a `Protein`; and
a `ProteinAssignment` reaches an observation by `PROTEIN_ASSIGNMENT_FOR`, not by `ASSIGNS_PROTEIN`.
**Predictions about output cannot catch a wrong premise about structure** — all three would have
returned plausible empty columns against the real graph, which has no results to disagree with them.
That is the argument for the fixture stated as a result rather than as an intention.

**A fourth premise was wrong and is a gap rather than a typo.** §8 I15 says a result *"whose
underlying values are more than half imputed"* is flagged **substantially imputed** in every view
and export. There is no such column on `DifferentialResult`, and the graph holds the numerator
(`SiteObservation.n_imputed`) without the denominator, which is per-sample in `quant.duckdb`. So the
flag is **not derivable from the graph alone**: `DifferentialRow.substantially_imputed` is always
`None` and carries `n_imputed` beside it, because a `False` would assert the clause satisfied.

**One guard was unreachable from every caller.** `_provenance`'s fall-through — the branch that
fails safe to *unprovenanced* for an entity type with no declared provenance path — is reached by
nothing today: `Figure` is in §7's list, has no table, and `unprovenanced` skips labels absent from
the DDL. Flipping it to `provenanced=True` left the whole module green. Kept rather than deleted,
because *flagged* is the direction I5 has to fail in, and tested directly with the callers
enumerated rather than guessed.

**`OPERATIONS.md` §5's wall clock is widened again, by this turn's own opening rebuild.** Yesterday
it went from one draw (119.9 s) to a three-run range (83.9–100.6 s). Today's first rebuild returned
**149.7 s**, outside it, followed by 148.5 s and 101.7 s. Six runs across two sessions give
**83.9–149.7 s**, a spread of ~66 s rather than 17. Three consecutive runs in one session measure
the machine's mood, not the command, and the correction is recorded as that lesson rather than as a
third number.


### Step 0 stopped the BJC ingestion: the tables carry no statistic, 2026-08-09

**Nothing was ingested and nothing was built.** The turn set out to run BJC Supplementary Data 2 and
3 through `bzk/adapters/perseus.py` so that `differential_table` would return rows instead of
`Absence.NOT_STORED`. Establishing the input first — which is what Step 0 is for — showed that it
cannot: **neither file contains a test statistic.** The finding is recorded here rather than worked
around, and no pre-registration table appears below because the run it would predict did not happen.
What the predictions *would* have been, and why they are withdrawn, is stated at the end.

**Confirmed before establishing anything.** 2,029 sites, 27 refusals, 4,561 `Protein`, 1,044 `Gene`,
1,059 `ENCODES`, `gene_absence` 1,059 / 3,492 / 10, and `differential_table` returning
`Absence.NOT_STORED` — all unmoved. Rebuild wall clock **122.1 s**, inside the 83.9–149.7 s range
this file records and nearer its middle than either endpoint.

**The input is sound, which is why the finding is about content and not access.** Both files already
have a fetcher — `bzk/sources/protein_groups.py`, added for the ambiguity survey — pointing at
Springer's stable ESM path for doi:10.1038/s41416-020-01167-y. They already enter `raw/` through
`provenance/raw_store.store`, the same content-addressing every other input gets, and both verify:

| File | Springer name | Digest | Size |
|---|---|---|---|
| Supplementary Data 2 | `41416_2020_1167_MOESM4_ESM.xlsx` | `sha256:da870551116f00b4ea5a89ae930156e503283d2ee7a4eebe5c03acfb54651509` | 16,127 bytes |
| Supplementary Data 3 | `41416_2020_1167_MOESM5_ESM.xlsx` | `sha256:9c9d9dfbd69078053caed1158752a14c31bdc5e4364e25d3401f3c691b3b9fca` | 74,388 bytes |

**They do not belong in `sources/pride.py` and already do not live there** — the module says why:
*"the path scheme is Springer's, not PRIDE's, and giving it its own type keeps `sources/pride.py`
about PRIDE."* **I9's input list does not change**: `raw/` is already its first input and these are
already in it. So the question Step 0 was asked to answer has the answer *already correct*, and the
work of this turn was to find out what is inside them.

**What is inside them, measured against what `perseus.py` requires.** The adapter needs
`Student's T-test Difference {suffix}` and one of `Student's T-test p-value {suffix}` /
`-Log Student's T-test p-value {suffix}`. **Zero columns in either file match any of the three.**

| | Supplementary Data 2 | Supplementary Data 3 |
|---|---|---|
| Sheets | 1, visible | 1, visible |
| Dimensions | `A1:X27` — 24 columns, 25 data rows | `A1:AB325` — 28 columns, 323 data rows |
| Columns matching `Difference` or `T-test` | **0** | **0** |
| Only statistic-like column | `N: Q-value`, 3 distinct values including 0 — MaxQuant's **identification** FDR, not a differential *q* | same |
| Quantitative columns | 6 × `LFQ intensity`, range **20.79 – 33.61** | 6 × `LFQ intensity`, range **−6.331 – 10.73** |

**These are Perseus *exports*, and that was never in doubt — the `C:` / `N:` / `T:` prefixes are
Perseus's own column-type marks. What they are exports *of* is the annotation matrix, not a t-test
result.** A Perseus t-test writes its `Difference` and p-value back as new `N:` columns; there are
none. So the tables give the **membership** of the significant set and the values behind it, and
withhold the statistic that made it significant. That is a perfectly ordinary thing for a paper's
supplementary data to be, and it is not what a `DifferentialResult` requires: `log2fc`, `p_value`
and `adj_p_value` would all have to be invented.

**Three further findings from the same measurement, each of the ran-cleanly-and-was-wrong class.**

1. **The two files' quantitative columns are not the same quantity.** Data 2's LFQ values run
   20.79–33.61 — log2 intensities. Data 3's run **−6.331 to 10.73**, and a negative intensity is not
   an intensity. Ingesting both under one `Analysis.quantity` would put two different measurements
   in one closed-enum slot (§5, I16), and the enum has no value that is honestly both.
2. **Eleven of Data 3's 323 rows have their gene-name list split across headerless columns.**
   `T: Gene names` holds only the first symbol and the remainder sit in four unnamed trailing
   columns — row 4 carries `SRGAP2` in the column with `SRGAP2C`, `SRGAP2B`, `SRGAP1` beside it,
   outside the header. Sixteen stray cells in total. A reader taking `T: Gene names` at face value
   silently loses one to four symbols per affected row, and a positional reader trusting the header
   width reads a gene symbol as data. Same shape as the six MaxQuant spill lines recorded above,
   found the same way, and it would not have surfaced from a header read.
3. **The replicate columns disagree between the files in name and order.** Data 2 writes
   `KO_IFN_1` and lists KO first; Data 3 writes `WT_IFN-1` — hyphen, not underscore — and lists WT
   first. A curation record mapping samples to conditions cannot be shared between them.

**What was *not* found, because two artefacts said it would be and both are stale.** This file's
consequence table said `perseus.py` *"refuses ~72–77% of rows, so it is unusable until the schema
can hold a group"*, and `bzk/sources/protein_groups.py`'s docstring said the adapter *"refuses a
multi-accession row"*. **Both were true when written and neither is true now** — ADR-0022 made
`candidate_proteins` identifying and `RESOLVES_TO_PROTEIN` `MANY_MANY`, and `perseus.py`'s own
docstring records the change: *"This adapter refused every one of them until ADR-0022 … Since
ADR-0022 the group **is** the identity."* So the blocker this survey predicted is discharged, and
the blocker that actually stopped the turn is one neither artefact anticipated. Both are corrected
in place.

**The withdrawn predictions, and the premise that falsified them.** They were to be derived from the
survey's 18 and 250 mapped rows: `DifferentialResult` at 25 + 323 = 348 minus refusals,
`ProteinObservation` at the same count, `Dataset` at 3, `Imputation` at 2, and `differential_table`
returning rows with `unprovenanced` moving `DifferentialResult` off `(0, 0)` and `Dataset` off
`(0, 1)`. Every one of them assumed the files carry a statistic. **They are withdrawn rather than
answered, because a prediction about a run that does not happen is not a prediction** — and
recording the number they would have taken is worth more than the number itself: 348 rows of
`DifferentialResult` would have been minted from `log2fc` and `adj_p_value` values that do not
exist in the source.

**The one thing this establishes about the four measured-state claims in `bzk/query/`.** They record
0 `DifferentialResult`, 0 `Imputation`, and `{'Dataset': (0, 1), 'SiteObservation': (0, 2029),
'DifferentialResult': (0, 0)}`. All four were expected to be falsified by this turn and **none of
them is**: nothing was ingested, so every figure still holds, re-measured through the read layer
after the confirming rebuild. They are left exactly as they are.

### Pre-registration: what a minimal interface would mean, 2026-08-09

**Written and committed before any code changes.** Three panels over `bzk/query/` and nothing else.
The hazard specific to a first interface is that it is the first thing anyone *looks* at, so a
rendering decision made for layout reasons becomes the platform's claim: four distinct absences
drawn as one blank grid would undo the read layer's central decision without a line of it changing.

**Confirmed first.** 2,029 sites, 27 refusals, 4,561 `Protein`, 1,044 `Gene`, 1,059 `ENCODES`,
`gene_absence` 1,059 / 3,492 / 10, `differential_table` at `Absence.NOT_STORED`, `unprovenanced`
`{'Dataset': (0, 1), 'SiteObservation': (0, 2029), 'DifferentialResult': (0, 0)}` — all unmoved.
Rebuild wall clock **120.8 s**, inside the 83.9–149.7 s range and nearer its middle than either end.

**Established before deciding.**

| Question | Result |
|---|---|
| Does `streamlit==1.61.1` run here? | **Yes** — imports and reports `1.61.1` |
| Can it read the graph **while a rebuild holds it**? | **No.** `RuntimeError: IO exception: Could not set lock on file : /root/.bzk-omics/graph.kuzu`, raised from `query.connect` 25 s into a rebuild. Kùzu takes a single writer lock |
| Can the UI be tested headlessly? | **Yes** — `streamlit.testing.v1.AppTest` runs a script and exposes `.title`, `.markdown`, `.info`, `.dataframe`, `.exception`. Verified against a probe script |

**Decision 1 — `bzk/ui/app.py`, and it is a sibling of `query/` rather than part of it.** §3's
boundary test is *what a module produces and who consumes it*. `query/` produces records consumed by
`api/` and now by this; a Streamlit app produces **a screen consumed by a person**, and nothing in
`bzk/` consumes it. It is the terminal end of the same axis, one step past `query/`. Not `web/`,
which is reserved for SvelteKit at v0.2 and a different stack; not `api/`, because FastAPI routes
are consumed by a front end and this *is* one. Inside `bzk/` rather than beside it so that `ruff`
and `mypy` cover it on their existing targets. **It imports `bzk.query` and nothing else from
`bzk/`** — no `kuzu`, no Cypher — and anything a panel needs beyond that is reported as a read-layer
gap rather than reached around.

**Decision 2 — the UI derives nothing.** Every value on screen is a field of a record `bzk/query/`
returned. Three consequences, each fixed here rather than left to layout:

- **`substantially_imputed is None` renders as *unknown*, with the reason.** `graph.py` argues a
  `False` would assert I15's clause satisfied; a blank cell says the same thing more quietly, and a
  reader supplies the missing word themselves. It shows *not derivable — the denominator is in
  `quant.duckdb`, which the read layer does not reach.*
- **The UI does not resolve the rename.** `DDX58` renders `present=False, UNATTRIBUTABLE`; `RIGI`
  renders present at `hgnc:HGNC:19102`. Both appear; **neither is joined to the other.** Whether a
  caller should be able to see that `RIGI` carries `DDX58`'s locus is a read-layer question and is
  reported below as a gap, not closed here.
- **I14's display half attaches for the first time.** Wherever a number appears with a candidate
  set behind it, the set appears beside it.

**Decision 3 — it is tested, and on what it renders rather than on whether it imports.** The module
holds no derivation, but it does hold one real decision — the mapping from each `Absence` to what
appears on screen — and that mapping is the whole point of the third panel. A test that only
imported the module would be the shape this project has been caught by twice: *a guard that cannot
see the objects it governs*. So `AppTest` runs the app against a fixture graph and asserts the text.
**What it costs:** `AppTest` executes the script in-process, so a Streamlit version bump can break
the tests without breaking the app and vice versa; and the assertions are on substrings of rendered
markdown, which is a weaker contract than a return value. Both accepted — the alternative is
asserting nothing about the only decision the module makes.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| **No id moves, no count changes** — this turn writes no nodes | the baseline id set captured before the confirming rebuild (12,774 ids, 12 labels), diffed per label after | exact set equality, no margin |
| Panel 1: `keying_basis` on **2,029 of 2,029**, `displaced_protein` on exactly **522**, and the 522 are exactly the `reviewed_preferred` sites | `site_keying` over every site, as § *the read path* already asserts | exact integers |
| Panel 2: **12 present, 2 absent**, both `UNATTRIBUTABLE`; `RIGI` present at `hgnc:HGNC:19102`; `DDX58` and `RIGI` shown **unjoined** | the rendered panel, read back through `AppTest` | exact integers, and a discrete presence/absence of a join |
| Panel 3: **three** distinct absence renderings on the real graph — `NOT_STORED` twice with different subjects, `NOT_RETAINED` once — and **all four** `Absence` values distinguishable | an exhaustiveness assertion over `Absence`, plus `AppTest` text | exact: 4 of 4 mapped, no two strings equal |
| Suite: skip count stays **10**, because the UI tests build their own fixture graph and do not gate on `~/.bzk-omics` | `pytest -q -rs` under a fake `HOME` | exact integer |
| Suite wall clock **150–200 s** | `time pytest -q` | **±20 s at best.** Two prior observations 1.5 s apart would suggest better, but this machine showed a 66 s spread on a two-minute rebuild, so a tighter claim is not available and none is made |

**No prediction is registered for the worked site's candidate-set size.** No such figure is recorded
in the tree, and a number quoted from a terminal is not a baseline — which is how the last one got
in.

**What Panel 2's 12 is, fixed before it is displayed.** Identifiability, not recovery: twelve
published symbols are answerable from stored `Gene.symbol`. § *the outcome of minting `Gene`* fixes
that reading and the panel must not blur it, so the panel names what it counted rather than showing
a bare 12. No differential is run and no comparison to any recovery figure is made.

**The I18 boundary, tested rather than assumed.** The reading offered was *a screen is not an export
and a download button is*. **I18's own text settles it**: §8 — *"Queries and views within the local
instance are unrestricted."* A Streamlit screen is a view within the local instance, so the EX
trigger does not fire; a download button writes a file, which is what `HANDOFF.md` §8 names as the
risk, so it would. **None of the three panels needs one and none is added.** One condition the
entry does not state and this section will: *within the local instance* is a property of how the app
is served, so binding it to a non-loopback address would make it a shared artifact and fire the
trigger. Nothing here binds anything; the app is run by hand.

**What would make this turn a failure rather than an interface.** A panel that renders an absence
as blank. The read layer distinguishes four; a screen that shows one is the layer's central decision
discarded at the last step, and it is the step where a reader actually forms a belief.

#### Outcome, 2026-08-09 — every panel prediction held; the wall-clock one missed and its precision claim was the worse half

| Prediction | Result |
|---|---|
| No id moves, no count changes | **held** — 12,774 ids, 0 lost and 0 gained on every one of the 12 labels |
| Panel 1: basis on 2,029/2,029, `displaced_protein` on exactly 522, the same set | **held** (asserted in `test_query_real_graph.py`); the panel renders both cases — default site `A0A024R571#sv1#K138` shows `razor` / *not promoted*, and `Q00341#sv3#K90` shows `reviewed_preferred` with `displaced_protein: uniprot:A0A024R4E5` |
| Panel 2: 12 present, 2 `UNATTRIBUTABLE`, `RIGI` at `hgnc:HGNC:19102`, unjoined | **held** — *"12 of 14 requested symbols are present"*; `DDX58` and `OAS1` each render `present=False`, `absence=unattributable`, and no element names both a symbol and its rename |
| Panel 3: three distinct absence renderings; all four `Absence` values distinguishable | **held** — `NOT_STORED` (differential), `NOT_RETAINED` (refusals), `NOT_STORED` ×2 (one per `Analysis`), all on screen at once with different text. `NONE_FOUND` does not occur on this graph, which is why the exhaustiveness assertion exists rather than the screen being the only check |
| Skip count stays **10** | **held** — 10 of 383, unchanged; the UI tests build their own fixture and do not gate |
| Suite **150–200 s, ±20 s at best** | **missed: 233 / 238 / 302 s** |

**The wall-clock miss, and why the precision claim was the worse half.** The new tests add **5.1 s**
— `test_ui.py` runs in five seconds — so the suite did not get slower because of this turn. It was
168.7 s and 170.2 s in one session and is 233–302 s in the next, which is the machine, and it is the
same shape as `bzk rebuild`'s wall clock two entries above: **three consecutive runs measure a
session, not a command.** The prediction was drawn from last session's two observations 1.5 s apart,
and the ±20 s was a hedge against exactly the wrong thing — the interval should have been wide
enough to survive a different session, not tight enough to reflect one. Both figures in
`test_query_real_graph.py` are corrected to ranges with their *n*.

**The import rule found a read-layer gap on its first use, which is the rule working.** `bzk/ui/`
may import `bzk.query` and nothing else from `bzk/`. The first panel needed a list of site ids for
a selector, the read layer did not expose one, and **the first draft wrote a `MATCH` in the
renderer** — the exact leak. `query.site_ids` and `query.analysis_ids` were added to the read layer
instead, and a test now parses every import in `bzk/ui/*.py`. Reported rather than absorbed because
it is the difference between a constraint and a habit: the rule cost something on day one and was
paid rather than relaxed.

**One assertion passed for the wrong reason and was caught by mutation.** Panel one's test asserted
`IFIT1_2 in text`; replacing the displaced accession with the word *(promoted)* left it green,
because the same accession appears in the candidate list two lines below. It now asserts the
composed line, `` `displaced_protein`: **uniprot:P09914-2** ``. Fourth time this suite has been
caught by an assertion satisfied by a different element than the one it names.

**The I18 boundary was tested and did not fire.** §8 I18's own sentence — *"queries and views within
the local instance are unrestricted"* — settles it: a screen is such a view. No download button was
added, and a test asserts that no module in `bzk/ui/` contains `download_button`, `write_text(`,
`open(`, `to_csv` or `savefig`.

**One read-layer gap reported and not closed.** A caller cannot ask whether an absent symbol's locus
is present under another name. `DDX58` returns `UNATTRIBUTABLE`; `RIGI` is present at
`hgnc:HGNC:19102`; nothing joins them and the UI shows both without linking them. Whether the read
layer should offer that comparison is a read-layer question and the renderer is the wrong place to
answer it.

**The four measured-empty claims in `bzk/query/` still hold** — 0 `DifferentialResult`, 0
`Imputation`, the `unprovenanced` dict, and refusals not being retained. Nothing was ingested this
turn either; they were checked and left.

### Pre-registration: what a cold-clone rehearsal would mean, 2026-08-09

**Written and committed before the clone.** Every rebuild on record has run against a populated
`~/.bzk-omics`. I9 names four inputs and a cold clone has one of them — `raw/` is fetchable and the
curation export and the DDL are in the repository, but **the UniProt cache is not**, and it is the
input the graph's keys come from. `OPERATIONS.md` §5 says the claim behind I9 is true only while it
is verified; it has never been verified from nothing.

**What makes this different from a warm rebuild, and it is the reason to run it.** `OPERATIONS.md`
§3.1 records that the pin's backfill is sound *only because the snapshots were still the original
capture*, and that the window closes the first time anything re-fetches. **A cold clone is outside
that window by construction**: there are no snapshots to backfill from, so every pin is written by
the fetch under test. The cold rebuild is not protected by the pin — it is the act the warm tree's
pins were created by. A difference here therefore means something a difference in a warm rebuild
would not: it is UniProt moving against the *original* capture, with nothing in between.

**The warm baseline, captured before `~/.bzk-omics` is moved aside.** 12,774 ids over 12 non-empty
labels — `Analysis` 2, `Dataset` 1, `Experiment` 1, `Gene` 1,044, `ModificationSite` 2,029,
`Modifier` 3, `ModifierAssignment` 2,029, `Project` 1, `Protein` 4,561, `ProteinSequence` 1,062,
`Sample` 12, `SiteObservation` 2,029. Edges: `ASSIGNMENT_FOR` 2,029, `CONTAINS` 1, `ENCODES` 1,059,
`HAS_SEQUENCE` 1,062, `MEASURED_AT` 2,029, `PERFORMED_ON` 12, `PRODUCED` 12, `REPORTS_SITE` 2,029,
`SAMPLE_GENERATED_BY` 12, `SITE_ON` 2,029, `USED` 2. `gene_absence` 1,059 / 3,492 / 10. Cache:
2,261 snapshots, 3,014 archived sequences, 2,183 pins.

**Step 5's four outcomes, registered before the run.**

1. **Identical.** I9 holds under the conditions it names — and this is the **weakest useful
   outcome**, which the registration says now rather than the report saying it afterwards. UniProt
   releases roughly monthly (§5) and the warm capture is two days old, so an unchanged UniProt is
   the most likely explanation of an identical result and is not evidence that the guarantee would
   survive a release boundary. **This is the outcome the documents make most likely and it is
   registered as the expected one.**
2. **A changed refusal count with no id movement.** `OPERATIONS.md` §1 says this is what actually
   happens when content is amended under an unchanged version: no key moves, the graph regenerates
   smaller, and the signal reads like drift. §11 Q5's isoform limitation — versions taken from the
   parent entry — is one mechanism. **Delta accepted as this rather than as a defect: any size, if
   and only if every extra refusal carries a sequence-content reason *and* the accession's freshly
   fetched sequence differs from the one preserved in the moved-aside archive.** That archive is
   the discriminator and it is why `~/.bzk-omics` is moved rather than deleted: a refusal whose
   accession's bytes are unchanged is not drift, it is a defect. Expected size **0**, since two
   days is inside a release.
3. **A different `Gene` or `ENCODES` count.** **Accepted by decision, not a finding**
   (`OPERATIONS.md` §3.1): a changed cross-reference moves no id, cascades into no digest — `Gene`
   is in no `schema.IDENTITY` anchor list — and changes a visible count. Registered as accepted so
   the report cannot present it as a discovery and stop.
4. **A moved id.** `sequence_version`, `reviewed`, or anything else that re-keys an existing node
   and every evidence digest anchored on it. **This is the failure the pin exists to prevent and
   the one a cold tree has no pin against.** What matters is its size and location: which labels,
   how many ids, and whether the movement reaches `ModificationSite` and the `bzk:` digests
   anchored on it. **If it happens, report and stop** rather than chasing the cause.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| Per-label id sets **identical** to the warm baseline, all 12 labels, symmetric difference 0 | per-label set diff against the captured JSON | exact set equality |
| Node and edge counts identical; refusals **27**; `gene_absence` **1,059 / 3,492 / 10**; `Gene` **1,044**; `ENCODES` **1,059** | the rebuild's report and Cypher | exact integers |
| Digests of both BJC files and the deposit match what `sources/` records | `provenance/raw_store.verify` | exact |
| Suite: **10 skip** before the fetch, **0 skip** after the graph exists; wall clock inside **233–302 s** | `pytest -q -rs` | exact integer; ±70 s, which is the recorded spread and no finer |
| Panels: 12 of 14 present, `DDX58`/`OAS1` `UNATTRIBUTABLE`, three distinct absence notices | `AppTest` against the cold graph | exact |

**No prediction is registered for the cold wall clock.** `ROADMAP.md`'s own standard says that
where no instrument can resolve a quantity the honest move is to make none, and `OPERATIONS.md` §5
already records that a regression smaller than its own spread cannot be seen. A cold rebuild is
dominated by network round trips whose per-fetch cost was measured varying by 3× *within one run*
last session. What **is** registered is the shape, which an instrument can resolve: **the cold run
is dominated by fetches rather than by the write path**, checked by comparing `cold − warm` against
the number of accessions fetched, and the fetch count will be reported so the figure is
decomposable rather than a single opaque number.

**The install is expected to have gaps and they are the output.** §4 is a pinning *policy* and
contains no install procedure. Nothing in steps 2–4 is fixed by hand: a documented procedure that
does not work is a defect in the procedure, and the fix goes in `OPERATIONS.md`.

**Three demo failure modes, none with a claim in the tree.** A **stale holder** — the recorded
advice is *wait and reload*, which is exactly what cannot work if the holder is dead, so the
question is whether anything short of finding the process recovers. The app **without `raw/`** — it
reads the graph, not the deposit, so it should run, and if `graph.kuzu` alone suffices that is a
much smaller thing to carry into a room. The app **without the network** — no claim either way. The
live-lock case is already established and implemented and is not re-established.

**Nothing is built.** No features, no panels, no read-layer additions. A panel needing something the
read layer does not expose is reported.

### The cold clone: I9 held on 12,774 ids and lost five, and the cause was our own code, 2026-08-09

**Run against the pre-registration two entries above.** A clone of `7f50216` from GitHub into an
empty directory, `~/.bzk-omics` moved aside rather than deleted, install from the pins, `raw/`
fetched by the documented path, `python -m bzk.rebuild` from nothing. Nothing was built.

| Prediction | Instrument | Result |
|---|---|---|
| Per-label id sets identical, all 12 labels, symmetric difference 0 | per-label set diff | **missed on one label.** 11 of 12 exact; `Gene` lost 5 and gained 0. No id *moved* anywhere |
| Counts identical; refusals **27**; `gene_absence` **1,059 / 3,492 / 10**; `Gene` **1,044**; `ENCODES` **1,059** | rebuild report and Cypher | **refusals 27 held**, every node and edge count held except `Gene` **1,039** and `ENCODES` **1,054**; partition **1,054 / 3,492 / 15 / 0** |
| Digests of both BJC files and the deposit match `sources/` | `raw_store.verify` | **held**, 4 of 4 |
| Suite: **10 skip** with no `~/.bzk-omics`, **0 skip** with the graph; **233–302 s** | `pytest -q -rs` | **10 and 0 held.** Wall clock **89.1 s** without a graph and **107.2 s** with one — both **below** the registered range, which was measured on a busier machine |
| Panels: 12 of 14, `DDX58`/`OAS1` unattributable, three distinct absence notices | `AppTest` | **held**, exactly |

**Outcome 3 by its shape and not by its cause, which is why the report does not stop there.** The
registration accepted a changed `Gene` count in advance, on the reasoning that a changed
cross-reference moves no id and cascades into no digest. No id moved and nothing cascaded — but
**UniProt did not change.** The immutable tier came back byte-identical, 3,013 of 3,013 sequences
and 2,182 of 2,182 pins, zero version movement. What changed is that `_fetch_entry` took the
**first** HGNC cross-reference until 07:58 UTC on 2026-08-09, and the seven affected snapshots were
written between 06:30 and 06:50 — under the superseded rule, an hour before the fix. `_load_entry`
treats only `NOT_CAPTURED` as a miss, so a snapshot holding a stale-but-present value is a cache hit
forever and the fix could not reach them. Three measurements settle it rather than suggest it:
**0 of 2,261** warm snapshots carry `AMBIGUOUS` against **7 of 2,260** cold ones — under the current
rule a probability-zero result if those entries had ever been read by it; the five lost genes are
all histones (`P62805`, `P62807`, `P68431`, `P84243`, `Q6FI13`), the textbook one-protein-many-loci
case; and `P62805` carries **14** HGNC cross-references at UniProt today, of which the warm snapshot
holds exactly the first. So the warm graph asserted `H4C1 encodes P62805` and four more like it —
one locus named as *the* gene of a protein UniProt attributes to fourteen.

**The generalisation, which is worth more than the five nodes.** A derived-store guarantee needs its
inputs to be **re-derivable by the code that reads them**, and *unmodified* is a strictly weaker
property that looks identical from outside. `raw/` and the sequence tier store bytes and have it.
The entry tier stores a **parse** and does not: a change to the parser silently invalidates every
file, leaves every mtime and every `fetched_at` untouched, and no check in the tree looks. That is
the same split `OPERATIONS.md` §3.1 drew for identity-bearing fields, arrived at from the other
direction — and §3.1's *"correct only because they are still the original capture"* is the sentence
this falsifies, since they **are** the original capture and that turned out to be compatible with
being wrong.

**Wall clock: 37 m 14.5 s, and the decomposition is the usable part.** 194 s of CPU (8.7%); 2,260
entries and 3,013 sequences fetched, 5,273 round trips at ~0.40 s each. The write path that
dominates a warm rebuild is ~4% of this. The registered shape — *dominated by fetches rather than by
the write path* — **held**, and no figure was registered for the total, correctly. **A wrong reading
was taken and corrected mid-run and it belongs here:** an early estimate of ~12 s per accession was
computed from three spot counts whose spacing had not been recorded, i.e. a rate with no clock. A
15-second poller then measured **~1.0 s per accession** flat from the first sample to the last. The
error was 12× and the instrument was the problem, not the network.

**Three demo failure modes, all three answered.** **A stale holder:** the recorded advice — *wait for
the rebuild to finish and reload* — is complete, because there is no state to be stranded in. Kùzu's
lock is an OS file lock released by the kernel, so a holder killed with `SIGKILL` leaves nothing on
disk and the next read succeeds immediately; verified both ways, and the live case incidentally
re-verified against the real rebuild at 25 minutes in rather than the 25 seconds recorded before.
**Without the network:** all three panels render inside a network namespace with only loopback. The
app is genuinely offline-capable, which nothing in the tree had claimed either way. **Without
`raw/`:** the app runs — `graph.kuzu` alone is enough to carry into a room — but the two findings
around it are worse than the mode itself. `bzk rebuild` over an empty content store **exits 0** and
reports `done` (`OPERATIONS.md` §5), and the app then renders that empty graph with the gene panel
claiming *"Present but unattributable"* for all fourteen symbols — an assertion about content that is
not there, from the one read-layer entry point of five that does not check whether its table is
empty (`HANDOFF.md` §8).

**What the install rehearsal cost, before any of that.** No install procedure existed in the tree at
all: `ARCHITECTURE.md` named `uv` and credited it with *"the one-afternoon install promise"*,
`HANDOFF.md`'s history block assumed `uv` and Python 3.12 were already present, and `README.md` said
*"Working software: None yet"* under a Status table last touched three days and six milestones
earlier. The machine's `python3` was **3.11.15**, which cannot run this project. `uv sync --frozen`
is now `OPERATIONS.md` §4.1, with the figures. Two more defaults were found by running rather than
reading: `streamlit run` binds `0.0.0.0` — falsifying the *served locally* condition the I18 reading
was published under two commits earlier — and reports usage statistics.

**A seventh, found by the turn's own closing checks rather than by the clone.** Correcting the
census figure turned `test_tautology_sweep.py` red on an unrelated row, and the row was innocent:
`_run_in_a_mutated_copy` copies the repository with `shutil.copytree` and did not exclude
`__pycache__`, so the copy loaded **the working tree's last compiled bytecode** in preference to the
source beside it. Demonstrated with a planted value rather than argued: a test file was edited to
assert `9999`, run once to compile, restored to `1054`, and the copy then failed asserting **9999** —
a number present in no file in that copy — while the same copy taken without `__pycache__` passed.
Python's default invalidation compares source **size and mtime-in-seconds**, and `9999` and `1054`
are the same size, so an edit-and-restore inside one second is invisible to it; the working tree
itself was serving the stale value for several minutes before this was noticed. **The instrument
that classifies every assertion in the sweep could therefore report a result it had not computed,
in either direction**, since the mutation it applied to a source file need never have been executed.
Excluded now, and the class is closed by an assertion rather than by the exclusion: `test_no_repository_copy_carries_compiled_bytecode` parses every `.py` under `tests/` and `bzk/`, resolves each `copytree`'s `ignore=` to the `ignore_patterns(...)` it was bound to, and requires `__pycache__` among them — with a non-vacuity line, since one instance today is exactly the count at which prose stops being distinguishable from prose that has rotted. Both halves mutation-tested. The demonstration is in the helper's docstring. This is the same shape as ADR-0019's
`_index` and the four vacuous invariant checks — a check reporting clean because it never ran — and
it is the third time it has appeared in a mutation harness rather than in the code under test.

**The scoreboard, since four of the six findings were documentation.** Predictions about output were
five and four held. Every one of the six findings came from somewhere else: from executing a
procedure that had never been executed, from comparing two trees, and from reading a server's own
log. The registration said the install was expected to have gaps and that the gaps were the output;
that was the only part of it that anticipated what the run would actually produce.


### Pre-registration: what closing the rehearsal's four findings would mean, 2026-08-09

**Written and committed before any code.** The four are `HANDOFF.md` §8's rows at :493–:496, left
open by a turn instructed to build nothing. Two of them can put a false claim in front of a reader,
which is what makes them a schedule item and not a backlog item.

**The starting state, measured before predicting anything, and it has not moved.** `python -m
bzk.rebuild` against `~/.bzk-omics`: **1 m 46.6 s**, 2,029 sites, 27 refused, 1 deposit, 12,782 node
and 10,283 edge statements, 48,696 cells, 57 tables. Graph: `Gene` **1,039**, `ENCODES` **1,054**,
`Protein` 4,561, `gene_absence` **1,054 / 3,492 / 15 / 0**, nothing unprovenanced. **12,769 ids over
twelve labels**, captured to compare against. The wall clock sits inside `OPERATIONS.md` §5's warm
range and nowhere near the 37 m 14 s cold figure, which is the expected reading now that the cache
is populated and is not evidence about either range.

**The correction list checked before editing, since the last one was stated unconditionally and
two of its items were already discharged.** `ONTOLOGY.md` §4's enum table — **already correct**,
:295 reads *no usable HGNC cross-reference — none at all (10), or several (5)* against a count of
15, and it is not edited again. `schema.py:125`'s cached partition — **already correct**, and it
moves only if (4) changes the enum. `OPERATIONS.md` §5 — **half discharged**: it records that a
rebuild with no deposit exits 0, and says nothing about what an exit code means, which is what (2)
changes. `schema.py:131` and `bzk/ui/app.py:28–29` — **not discharged**, both diverge from a
document corrected around them.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| No id moves: symmetric difference **0** on all twelve labels, **12,769** ids | per-label set diff against the pre-change capture | exact set equality |
| `gene_absence` still **1,054 / 3,492 / 15 / 0**, summing to 4,561 | `query.gene_absence_census` | exact integers |
| Refusals **27**, sites **2,029** | the rebuild's report | exact integers |
| (1) over a graph with an empty `Gene` table: all fourteen `present=False`, `absence is NOT_STORED`, `gene_id is None`, `protein_ids == ()` | `gene_symbols` return values against an empty-`Gene` fixture | exact enum identity |
| (1) on screen over that graph: the `NOT_STORED` headline appears in **panel two**, located between the *"0 of 14"* line and panel three's heading; the `UNATTRIBUTABLE` headline appears **0 times** on the page | `AppTest` element list, by index rather than by substring | exact position, exact count |
| (1) on the populated graph is unchanged: 12 of 14, `DDX58`/`OAS1` still `UNATTRIBUTABLE` | `test_query_real_graph.py`, `AppTest` | exact |
| (2) `python -m bzk.rebuild` exits **1** where a curation record names a deposit the content store lacks, **0** against `~/.bzk-omics`, and writes `graph.kuzu` and `quant.duckdb` in both cases | shell exit status, then `ls` | exact integer, file present |
| (3) with the committed config and no flags, the server logs `localhost` and no usage-statistics line | the server's own stdout | exact strings |

**The position-not-substring row is the one carrying weight.** Over an empty graph the app renders
`NOT_STORED` **twice** — once for the gene panel and once for imputation in panel three — so
`"Nothing is stored" in text` would pass while panel two still said the wrong thing. That is the
same shape as the `test_perseus` tautology and as last turn's panel-one assertion, which a candidate
list two lines below the field it named would have satisfied. Registered here so the fix cannot read
as adequate for having changed something.

**Two things no prediction is made about.** Wall clock, for §5's reason. And whether several HGNC
cross-references should read as `no_cross_reference` at all — a modelling judgement, and no
instrument resolves it. What *is* registered about (4) is the falsifiable half: **the partition does
not move**, because bringing `schema.py:131` into line with the table changes a description string
and no branch.

**Where (2) is predicted to land, before the code decides it.** `OPERATIONS.md` §5 holds both
halves — *rebuild never refuses on staleness, it is the disaster-recovery path* and *a rebuild that
produces a different result is a regression, stop and find out why*. The registered reading is that
these are not in tension because they act at different moments: refusing stands **in front of** the
work and an exit status is emitted **after** it. So the prediction is that the stores are written
identically either way and only `main()`'s status differs — falsified if any file, count or id
differs between an exit-0 and an exit-1 run of the same tree.


### The four rehearsal findings closed, and two guards that could not have failed, 2026-08-09

**Run against the pre-registration above.** Every registered prediction held.

| Prediction | Result |
|---|---|
| No id moves: symmetric difference 0 on twelve labels, 12,769 ids | **held**, exact |
| `gene_absence` still 1,054 / 3,492 / 15 / 0 | **held** |
| Refusals 27, sites 2,029 | **held** |
| (1) over an empty `Gene` table: fourteen `NOT_STORED`, no `UNATTRIBUTABLE` | **held** |
| (1) on screen: `NOT_STORED` in panel two by position, `UNATTRIBUTABLE` zero times | **held**, and see below |
| (1) on the populated graph unchanged: 12 of 14, `DDX58`/`OAS1` `UNATTRIBUTABLE` | **held** |
| (2) exit **1** where a deposit was named and not ingested, **0** otherwise, stores written both times | **held** |
| (3) bare `streamlit run` logs `localhost` and no usage-statistics line | **held** |

**The position-not-substring row earned its registration, demonstrated rather than argued.** With
the fix reverted, over the empty-`Gene` graph, `RENDERING[NOT_STORED].headline in text` evaluates
**`True`** while fourteen `UNATTRIBUTABLE` notices sit on the page — because panel three renders
`NOT_STORED` twice for its own reasons. A substring assertion would have passed a panel that still
said the wrong thing. The committed assertion is on the **first fourteen warnings** being panel
two's, the **last three** being panel three's exactly, `UNATTRIBUTABLE` appearing **zero** times, and
the `NOT_STORED` total being **16** — a number panel three alone cannot produce.

**The fixture had to be chosen as carefully as the assertion.** It carries a `Protein` and no
`Gene`, so a check written as *is the graph empty* passes it and is still wrong; confirmed by
mutating the check to count `Protein` instead of `Gene`, which the fixture rejects. Both existing
read-layer fixtures were populated — one gene and 1,039 — which is why the branch had never been
reachable from the suite and was found by driving the app instead.

**Two guards were written this turn that could not have failed, and both were removed rather than
kept.** A predicate separating *a record that names no deposit* from *one whose deposit is missing*
had an unreachable arm: `Dataset.content_hash` is identifying (§3), so the loader refuses a record
without one before the replay sees it. Deleted, and the premise pinned by a test instead, because
the reasoning is what makes the unconditional count correct and prose cannot carry it. And the
second increment of that counter — the *no adapter recognises* branch — had no test when it was
written, on a path only reachable through a deposit whose bytes sniff rejects; it has one now, and
without it `bzk rebuild` would have exited 0 over a graph missing every site because a file layout
changed.

**Where an empty ingestion sits, which was the question (2) actually posed.** `OPERATIONS.md` §5's
two halves — *never refuses on staleness, it is the disaster-recovery path* and *a different result
is a regression, stop* — are not in tension, because refusing stands **in front of** the work and an
exit status is emitted **after** it. `rebuild()` is unchanged and the stores are written identically;
only what the process tells a script changes. Staleness keeps exit 0 deliberately: §5 calls the
receipt a report and not a control, and a fresh install has never drift-checked anything.

**(3) restores the condition it was measured against, and the reason is narrower than it looks.**
`.streamlit/config.toml` is read from the **working directory**, and the documented command names a
relative path — `streamlit run bzk/ui/app.py` — so it can only be run from the repository root,
which is where the config is read. Every invocation the documented command can express is covered;
an absolute path from elsewhere is not, and that is stated rather than papered over. `app.py`'s
docstring had asserted the I18 reading with no condition at all and now carries one and cites where
it is met — settled by the single-source rule and not by normativity, since `CLAUDE.md` names
`ONTOLOGY.md` and does not reach a reading that lives in `HANDOFF.md` §3.

**(4) is half closed on purpose.** `schema.GENE_ABSENCE`'s description said *no HGNC
cross-reference* where §4's table says *no **usable** cross-reference — none at all (10), or several
(5)*; the document was already correct and the code was the half diverging, so the code moved. The
modelling question — whether several should read as `no_cross_reference` at all — is **not** settled,
and the trigger is sharpened rather than left as *fired*. *Fired* was useless: it fired the day it
was written and says nothing about when the change is worth its cost. The cost is a normative DDL
change moving a partition recorded in six places; the benefit is a distinction **no reader sees** —
`gene_absence` reaches no panel, no export and no report, and `gene_absence_census` is called from
`tests/` and nowhere else, searched rather than assumed. §4's *three absences that must not read as
one* is a claim about a reader, so the trigger is now the first reader that puts `gene_absence` in
front of a person.

**The correction list was checked before editing and two items needed nothing.** `ONTOLOGY.md` §4's
enum table and `schema.py:125`'s cached partition were both already correct and are untouched — the
partition did not move, as registered. `OPERATIONS.md` §5 was half discharged and gained what an
exit code means. `schema.py:131` and `app.py:28–29` were the two that had diverged. Recording which
items were already discharged is the practice this list adopted after the previous one was stated
unconditionally when it was not.


### Pre-registration: what a second cold rehearsal would mean, 2026-08-09

**Written and committed before the clone.** The first cold rebuild differed from the warm one and
the difference was explained: the entry cache served a parse the code had stopped producing. That
explanation makes a prediction it did not make when it was written — **a second cold run should
reproduce the first cold graph exactly**, because the first-match rule is gone from the code that
writes the cache. If it does not, the explanation is incomplete and whatever else moves is the
finding. Four things changed under it since — `graph.py:545–548`, `rebuild.py:383`,
`.streamlit/config.toml`, `schema.py:131` — and none of them writes to the graph.

**The first cold tree, measured before predicting anything.** `Analysis` 2, `Dataset` 1,
`Experiment` 1, `Gene` 1,039, `ModificationSite` 2,029, `Modifier` 3, `ModifierAssignment` 2,029,
`Project` 1, `Protein` 4,561, `ProteinSequence` 1,062, `Sample` 12, `SiteObservation` 2,029 —
**12,769 ids over twelve labels**. Edges: `ASSIGNMENT_FOR` 2,029, `CONTAINS` 1, `ENCODES` 1,054,
`HAS_SEQUENCE` 1,062, `MEASURED_AT` 2,029, `PERFORMED_ON` 12, `PRODUCED` 12, `REPORTS_SITE` 2,029,
`SAMPLE_GENERATED_BY` 12, `SITE_ON` 2,029, `USED` 2. `gene_absence` 1,054 / 3,492 / 15 / 0. Cache:
**2,260** entry snapshots, **3,013** sequences, **2,182** pins, **7** carrying `AMBIGUOUS`. Four
objects in `raw/`. `ONTOLOGY.md` §8 and `HANDOFF.md` §3 record **12,774** and are correct about the
warm tree; the five-id gap is exactly the five `Gene` nodes the histone finding accounts for, and
neither numeral is edited by this run unless this run moves one of them.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| Step 5: per-label id sets identical on **all twelve** labels, **12,769** ids, symmetric difference 0 | per-label set diff against the capture above | exact set equality |
| `Gene` **1,039**, `ENCODES` **1,054**, partition **1,054 / 3,492 / 15 / 0**, refusals **27**, sites **2,029** | the rebuild's report and Cypher | exact integers |
| Cache: **2,260** entries, **3,013** sequences, **2,182** pins, **7** `AMBIGUOUS`; every shared sequence byte-identical and every shared pin identical, **0** version movements; entry snapshots differing in `fetched_at` **only** | file-set diff plus byte comparison, field-wise JSON diff on the snapshots | exact counts, exact bytes |
| Fetch count **5,273** — 2,260 entry + 3,013 sequence round trips | count the files the run writes into an empty cache | exact integer |
| Suite in the cold clone: **391** tests, **0** skipped with the graph present, **10** skipped with no `~/.bzk-omics` | `pytest -q -rs` | exact integers |
| `bzk rebuild` against an empty content store: exit **1**, an `INCOMPLETE:` line, `graph.kuzu` and `quant.duckdb` both written | shell exit status, then `ls` | exact |
| Panel two over a **DDL-only** graph: fourteen `NOT_STORED`, **0** `UNATTRIBUTABLE` | `gene_symbols` return values | exact enum identity |
| Panel two over the **full** cold graph: **12 of 14** present, `DDX58` and `OAS1` `UNATTRIBUTABLE` | `AppTest` | exact |
| `.streamlit/config.toml` is **present in the fresh checkout** at the repository root with `server.address = "localhost"` and `gatherUsageStats = false` | read the file in the clone before anything runs | exact strings |

**No prediction about the wall clock**, per this section's own rule and because `OPERATIONS.md` §5
records that a regression smaller than the spread cannot be seen at all. The falsifiable half is the
**fetch count** above, which an instrument does resolve, and the shape: fetch-dominated, CPU in the
single-digit percent.

**About step 2, which is the part of the procedure that has never been executed as written.** §4.1
was written *from* the first rehearsal, so this is the first run that tests the text rather than
producing it. Predicted: both prerequisites are already present here — `uv` 0.8.17 and
`/usr/bin/python3.12` — so **:144's surprise does not surprise on this container**, and the honest
report is that the sentence was not tested rather than that it was confirmed. Predicted gap: `uv`'s
cache is warm at 1.1 GB, so following the text exactly measures the warm figure and the cold-cache
number at :150 is not re-measurable without deliberately emptying `UV_CACHE_DIR`, which the text
does not tell anyone to do.

**The four outcomes.**

1. **Identical.** The histone explanation holds and cold-to-cold reproducibility has its first
   evidence. **This is the weakest useful outcome and the registration says so before the run:** the
   two cold runs are hours apart, UniProt releases roughly monthly (§5), so an unchanged UniProt is
   the most likely explanation of an identical result and it establishes nothing about a release
   boundary. What it *would* establish is narrower and still worth having — that nothing internal is
   unstable, which is exactly what the first rehearsal could not separate from an external cause.
2. **A changed refusal count with no id movement.** `OPERATIONS.md` §1 (`:45`): content amended under
   an unchanged version number moves no key and shows only as a refusal delta that reads like drift.
   **Accepted as that, at any size, if and only if every extra refusal carries a sequence-content
   reason *and* the accession's freshly fetched bytes differ from the copy preserved in the first
   cold tree's archive.** That archive is the discriminator and it is why `~/.bzk-omics` is moved
   rather than deleted. A refusal whose accession's bytes are unchanged is not drift; it is a defect.
   **Expected delta 0** — hours, not weeks.
3. **A different `Gene` or `ENCODES` count.** `OPERATIONS.md` §3.1 (`:103–106`) classifies this as
   accepted by decision: it moves no id, cascades into no digest, and changes a visible count.
   **That clause covers a cross-reference genuinely changing at UniProt, and this registration adds a
   distinction it does not carry** — a count moving for an *internal* reason is what the histone
   finding was, and it is **not** accepted. The discriminator is the payload: if the freshly fetched
   HGNC cross-reference list for the affected accession differs from the first cold tree's snapshot,
   it is §3.1's accepted case; if the payload is the same and the count moved, the cause is inside
   this repository and the outcome is a defect — report and stop. Recorded here as an addition to
   `:103–106` rather than as a reading of it.
4. **A moved id.** The failure the pin exists to prevent and which a cold tree has no pin against:
   every pin here is written by the fetch under test, which is `:120`'s window sentence applied to a
   tree that has no earlier capture at all. **Report size and location and stop** — which labels, how
   many ids, and whether the movement reaches `ModificationSite` and the `bzk:` digests anchored on
   it.

**`bzk drift` is not run, named here rather than left unmentioned.** §5 measures 2,069.8 s for 2,845
sequences and says the cost scales with the archive; at 3,013 that is above 35 minutes on a turn
already carrying a 37-minute rebuild. The decision is not only about cost: §5 also records that a
drift run over an archive that has not aged compares fetches against fetches of the same UniProt
release, and this archive was written hours ago, so a third clean result would move no sentence.
**The second cold rebuild is a stronger instrument for this turn's question than `bzk drift` is** —
it re-fetches every sequence into an empty tree and the byte comparison in step 5 is over the whole
archive rather than a sample.

**Nothing is built.** No features, no panels, no read-layer additions, no new guards. A figure
falsified by a measurement here is corrected and the files that reached are enumerated.


### The platform made an invisible analytical choice, 2026-08-07

**The clearest finding of the project, because it is the project's own failure mode.** `VISION.md`
exists because a defensible analytical choice, made once and never recorded, is unrecoverable from
a published methods section. `bzk/adapters/maxquant_sites.py` made one and recorded it nowhere.

The site adapter drops every row below `Localization prob >= 0.75`. On PXD018299 that is **242 of
2,298 rows — 10.5% of the dataset, discarded by a number that appears in no node in the graph.**
After Slice 4a the graph holds one `Analysis`, of kind `curation`; `localization_threshold` is null
on it, and there is no other `Analysis` at all.

I16 is the invariant written for exactly this: *"every `Analysis` records which quantity it consumed
and the filters applied, **including the localisation threshold**"*. It did not fire. Not because
the field was wrong — because the adapter emits no `Analysis`, so the check iterates over nothing.
**An invariant that cannot fire on an empty set is not enforcement, and a filter applied by a node
that does not exist is the invisible choice arriving through the gap rather than through the field.**

Three things make this worth a finding rather than a bug report:

1. **The magnitude is the same class the platform was built for.** § Measured findings already
   records two defensible quantities differing by ~90× in usable sites. 10.5% is smaller and the
   same kind of thing: a reader given the 1,967 sites cannot recover that 242 were removed, or why,
   or that 0.75 rather than 0.5 was the reason.
2. **It was introduced by the turn that made the pipeline real.** Before Slice 4a nothing reached
   the graph, so nothing was unrecorded. Wiring ingestion created the gap in the same commit that
   made the platform work — which is precisely when this class of defect is invented.
3. **It was found by asking what the invariant covered, not by a failing test.** Every check was
   green. `CLAUDE.md` point 3 is the reason it surfaced at all.

The fix is a search-output `Analysis` — `kind = 'external'`, `external_tool = 'maxquant'`,
`parameters_observed = false` (I19), `quantity = 'intensity_multiplicity_summed'`,
`localization_threshold`, `filters_applied` — that every `SiteObservation` attaches to. It is
Slice 4b's first task and blocks any result derived from these observations, because a
`DifferentialResult` computed over a silently filtered population inherits the silence.

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

**Unmet, and 2026-08-09 narrowed why.** The adapter exists and its group handling is no longer a
blocker (ADR-0022). What is missing is a **table that carries a statistic**: the two published BJC
supplementary exports were established to hold LFQ intensities, identifiers and MaxQuant QC columns
and no `Difference` or p-value, so they cannot meet this exit however they are ingested. The
*cross-queried against a second dataset* half is untouched and separately blocked on §11 Q1, the
two-datasets-one-`Contrast` question. See § *Step 0 stopped the BJC ingestion*.

### Weeks 5–6 — raw path and statistics
MaxQuant site-table adapter. DuckDB quantitative layer. **`welch_t` with BH first**, reproducing 12 of 14 exactly; then `perseus_s0` with permutation FDR, its recovery number recorded as a separate baseline. `ModifierAssignment`, `ProteinAssignment` and `Imputation` including supersession and retraction.

*Exit, amended 2026-08-07 — the old wording asserted a number the two routes cannot share.* It read *"12 of 14 recovered through the real pipeline rather than a notebook"*, which assumes the pipeline sees the same sites the notebook did. **It does not, and it should not:** ingestion refuses 89 rows for reasons the notebook could not detect — residue drift against today's UniProt, deleted entries, a razor pick MaxQuant withheld — and 54 of those would have been tested. Measured, this route recovers 9 of 14 (§ Nine of fourteen). Holding "12" as the exit criterion would make passing it a matter of *reducing the refusals*, which is the opposite of the point: the criterion would be satisfied by ingesting sites the platform cannot validate.

*Exit:* PXD018299 ingested end to end and analysed through the platform's own statistics layer rather than a notebook, with

- **the population reported at every step**, and any divergence from the notebook's 1,375 accounted for exactly rather than approximately — today `1,321 + 54 refused-but-testable = 1,375`;
- **every unrecovered published target traced** to refusal or to threshold, so a miss is explained rather than counted;
- **the recovery figure recorded with its population**, whatever it is. A number is not the criterion; an unexplained number is the failure.

A site moves from ambiguous to `basis = uba7_knockout, confidence = confirmed`, and the superseded assignment remains inspectable.

Two things the old wording also assumed and that are **not yet true**, both blocking a literal reading of "through the real pipeline": gene symbols never enter the graph (`Gene` has no nodes, `Protein.name` is null on all **4,561** — corrected 2026-08-08 from 4,441, which the repository contradicts in five places), so target identification still reads the deposit's `Gene names`. **Decided 2026-08-08 and no longer open as a modelling question**: the symbol's home is `Gene.symbol`, not `Protein.name` — routing it onto `Protein` would make `Gene.symbol` redundant (ONTOLOGY.md §4). The blocker is now named and measured: `Gene.id` is an `hgnc:` CURIE, `Resolution.gene` is a *symbol*, and UniProt's payload does carry the id (`HGNC:7532` for `P20591`, measured) while the entry cache stores the parse rather than the payload — so nothing on disk has it. ONTOLOGY.md §11 Q12 holds the open part, which is what the cache should store — and as of 2026-08-09 Q12 is itself **blocked on a layer below it**: every answer re-writes `cache/uniprot/entry/{canonical}.json`, a tier whose key carries no version and which `ONTOLOGY.md` §8 and `OPERATIONS.md` §3 both wrongly called immutable until that date. **Both were settled on 2026-08-09**: the tier was split (`OPERATIONS.md` §3.1), Q12 was answered, and `Gene` was minted — **1,039 nodes, 1,054 `ENCODES` edges**, with `gene_absence` naming why the other 3,507 proteins have none (1,044 / 1,059 / 3,502 until the cold-clone rebuild the same day corrected them — ONTOLOGY.md §4). Target identification is answerable from stored content: 12 of 14 by exact symbol, 13 counting the `DDX58`→`RIGI` rename. The projected reach of ~3,231 was wrong by a factor of three because it counted cached entries rather than resolved accessions.; and I11 is met at **site grain only** since 2026-08-08: `quant_ref` is `site_values` on all 2,029 `SiteObservation`s and `quant.duckdb` holds 48,696 cells, so the site matrix is retained rather than re-read (ADR-0004, ADR-0013) — while `ProteinObservation` retains nothing, no adapter writing its cells. Gene symbols and the protein grain both remain on that reading.

### Weeks 7–8 — output and consolidation
Minimal Streamlit or notebook interface: query, volcano, provenance panel. Ambiguity and correction status visible everywhere a number appears. ADRs 0004–0014 written. Rebuild tested against the full dataset.

**The *query* half landed 2026-08-09, and the interface followed the same day.** `bzk/query/`
answers the five questions and enforces *"ambiguity and correction status visible everywhere a
number appears"* rather than deferring it to the renderer: no bare number leaves the layer, every
`prov:Entity` row carries its I5 provenance status, and an absent answer is a value from a closed
set rather than an empty list. `bzk/ui/app.py` is the minimal Streamlit interface over it — three
panels, no chart, no export — and it carries that requirement one step further: the four `Absence`
values render as **four distinct claims**, each naming the sibling a blank grid would collapse it
onto, and the empty panels stay on screen rather than being hidden until they have rows.

**What is untouched.** The volcano — there is nothing to plot, `DifferentialResult` being empty —
and anything that writes a file, which is where I18's embargo check has to land (`HANDOFF.md` §8,
EX). That trigger did **not** fire here: §8 I18's own sentence is *"queries and views within the
local instance are unrestricted"*, a screen is such a view, and no download button was added. The
*provenance panel* named in this block is partly met: I5's status is on every site row, but as a
line of text rather than a panel of its own.

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
