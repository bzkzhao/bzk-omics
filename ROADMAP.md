# ROADMAP.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 1.20 |
| Last reviewed | 2026-08-08 |
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
| **MaxQuant site-table adapter** | PXD018299, the validated regression fixture. Required to keep the published-target recovery verifiable — see the amended exit criterion: the figure is 9 of 14 through this route, and the criterion is that every miss is traced, not that the number is 12 |
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
`INSERT OR REPLACE … SELECT` over a registered frame: **1.43 s**, and the rebuild returns to
**62.2 s**. So the design's assumption that the columnar write is cheap is true of the bulk path and
was false of the code that claimed to take it.

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

### Weeks 5–6 — raw path and statistics
MaxQuant site-table adapter. DuckDB quantitative layer. **`welch_t` with BH first**, reproducing 12 of 14 exactly; then `perseus_s0` with permutation FDR, its recovery number recorded as a separate baseline. `ModifierAssignment`, `ProteinAssignment` and `Imputation` including supersession and retraction.

*Exit, amended 2026-08-07 — the old wording asserted a number the two routes cannot share.* It read *"12 of 14 recovered through the real pipeline rather than a notebook"*, which assumes the pipeline sees the same sites the notebook did. **It does not, and it should not:** ingestion refuses 89 rows for reasons the notebook could not detect — residue drift against today's UniProt, deleted entries, a razor pick MaxQuant withheld — and 54 of those would have been tested. Measured, this route recovers 9 of 14 (§ Nine of fourteen). Holding "12" as the exit criterion would make passing it a matter of *reducing the refusals*, which is the opposite of the point: the criterion would be satisfied by ingesting sites the platform cannot validate.

*Exit:* PXD018299 ingested end to end and analysed through the platform's own statistics layer rather than a notebook, with

- **the population reported at every step**, and any divergence from the notebook's 1,375 accounted for exactly rather than approximately — today `1,321 + 54 refused-but-testable = 1,375`;
- **every unrecovered published target traced** to refusal or to threshold, so a miss is explained rather than counted;
- **the recovery figure recorded with its population**, whatever it is. A number is not the criterion; an unexplained number is the failure.

A site moves from ambiguous to `basis = uba7_knockout, confidence = confirmed`, and the superseded assignment remains inspectable.

Two things the old wording also assumed and that are **not yet true**, both blocking a literal reading of "through the real pipeline": gene symbols never enter the graph (`Gene` has no nodes, `Protein.name` is null on all 4,441), so target identification still reads the deposit's `Gene names`; and — until 2026-08-08 — I11 was unmet, which it no longer is: `quant_ref` is `site_values` on all 2,029 observations, `quant.duckdb` holds 48,696 cells, and the matrix is retained rather than re-read (ADR-0004, ADR-0013). Gene symbols remain the blocker on that reading.

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
