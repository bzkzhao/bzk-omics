# ROADMAP.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 1.90 |
| Last reviewed | 2026-08-12 |
| Depends on | `VISION.md`, `ONTOLOGY.md`, `ARCHITECTURE.md` |
| Authoritative for | Scope, milestones, deferrals |

---

## v0.1 — target: 8 weeks part-time, scope cut to match

**Revised 2026-08-06 after external review.** The previous version claimed four weeks for a scope realistically requiring 11–15 weeks at 15–20 hours per week. That was wrong by roughly a factor of three, and the error was more dangerous than an ordinary slip: the only way to hit four weeks with that scope is to downgrade invariants from errors to warnings, which destroys the discipline that makes the design worth having.

**A smaller v0.1 that enforces I1–I19 strictly is worth more than a larger one that violates them to meet a date.**

~~Scope is therefore cut to a single path, and the remainder moved to v0.2.~~ **Corrected 2026-08-11, by the same amendment that struck *one dataset* below.** *A single path* was already superseded when ADR-0017 decided **B, both ingestion paths**, and both are on disk. What this sentence still gets right is the *shape* of the original cut — a smaller v0.1, with the remainder at v0.2 — and that is unchanged; what moved is which axis decides the remainder, and the two axes are set out under § *In scope*.

**The goal is a usable tool for one laboratory.** Not a product for a market, and not merely a proof that the ontology holds — a working end-to-end path that someone in the Pinto-Fernández group can run on their own data and get an answer from.

That is a higher bar than a schema demonstration and a much lower one than a released product. Everything in scope below is there because that group needs it; everything deferred is deferred because they do not, yet.

### In scope

~~One ingestion path, one dataset, one statistical test, no web frontend.~~ **Amended 2026-08-11,
and the contradiction it resolves is this document's own rather than the redraw's.** *One dataset*
is contradicted twice below by the exits this same document sets: § *Weeks 3–4* requires a Perseus
table *"cross-queried against a second dataset"* and calls that **the first genuinely useful
milestone**, and § *Weeks 7–8* requires an answer *"across all my datasets"*, plural. A v0.1 that
holds one dataset cannot reach either. The clause has been false since those exits were written and
neither the plan nor this redraw introduced it.

**Two ingestion paths, more than one dataset, one statistical test, no web frontend.** *Two paths*
because ADR-0017 decided **B, both ingestion paths**, is `Accepted`, and both are built —
`bzk/adapters/perseus.py` and `bzk/adapters/maxquant_sites.py` are on disk; *one path* described a
scope that was already superseded when this table still asserted it.

**What a second dataset actually reaches, stated because the two halves of that exit are not
blocked by the same thing.** *Ingested, resolved, stored* is reached by any second deposit and needs
nobody. *Cross-queried* is **not**, and its blocker is neither this table nor a person: § *Weeks
3–4* records it as separately blocked on `ONTOLOGY.md` §11 Q1, the two-datasets-one-`Contrast`
question, where `Contrast` identity is numerator plus denominator with no anchor and a HAP1 contrast
and an HCT116 contrast receive one id. That is a modelling question inside this repository and it is
**not settled here**. So the amendment removes a false constraint and does not claim the milestone.

#### The dependency axis — what this table now sorts on, 2026-08-11

**The original cut had a different axis and its sentence cannot be borrowed.** *A smaller v0.1 that
enforces I1–I19 strictly is worth more than a larger one that violates them* justified cutting on
**invariant enforcement**. This redraw sorts on **who supplies the input**: a row leaves v0.1 when it
cannot be *completed* without something only Dr Pinto-Fernández can supply. The two axes are
independent and a row may be in scope on one and out on the other, so each move below carries its
own citation.

**Three rules the sort obeys, because each of them changed an outcome.** A row that is merely
**blocked** does not move — being stuck is not the same as being dependent, and the protein-groups
rows below stay in scope for exactly that reason. A dependency that cannot be **cited** is a
dependency that has been asserted, and it stays. And a row does not come forward if there is
anything he could say that would change it; that test is what keeps `moderated_t_ebayes` deferred
below, on its own reasoning rather than on the reasoning that deferred it originally.

| Capability | Note |
|---|---|
| **Perseus result-table adapter — the code** | The collaborating group's workflow. A flat table of proteins, differences and significance values — no localisation or razor-pick complexity. **Written and tested against fixtures**, and ADR-0022 discharged the group-handling blocker. **Stays in v0.1 as code and moves to v0.2 as a milestone — 2026-08-11.** Running it on a real export left this table on the dependency redraw: what it needs is a Perseus table carrying a `Difference` and a p-value, the two published BJC exports were established on 2026-08-09 to carry no test statistic, and the dependency is citable in the exit criterion's own words: § *Weeks 3–4* asks for *"a real user's results, held and connected"*, and the intended first user is the collaborating group — so a stranger's public Perseus export would demonstrate the adapter and would not meet that exit. The module is on disk and does not un-ship |
| **MaxQuant site-table adapter** | PXD018299, the validated regression fixture. Required to keep the published-target recovery verifiable — see the amended exit criterion: the figure is 9 of 14 through this route, and the criterion is that every miss is traced, not that the number is 12 |
| **MaxQuant protein-groups adapter** | **This table had no row for it at all until 2026-08-10, while `maxquant.py` carried the plan in a docstring and `ONTOLOGY.md` §8 I14 quoted a measured protein-grain prevalence — the scope table was the one place the capability was invisible.** Written and tested 2026-08-10; run offline over `HAP1_USP18KO_proteinGroups.txt` it emits 4,797 `ProteinObservation`s over 23,807 `Protein`s with 67,158 cells and 0 refusals. **Not ingested**: the file's fourteen columns are the proteome run and the curation record's twelve `Sample`s are the diGly run, so there is no sample to key a cell to and I8 forbids inventing one. **Kept in v0.1 on the 2026-08-11 dependency redraw. That decision stands; the justification it was given was wrong twice and is replaced here, 2026-08-12.** It is *blocked*, and blocked is not dependent — what it needs is a curation record for the proteome run. **First error: the deposit was said to be unchecked, and this document had already checked it twice.** § *Deposit and supplementary survey* records **SDRF present — No** on 2026-08-06, and § *The protein adapter is written and the ingestion is not* records that *nothing in the deposit says which is the replicate, whether they are technical replicates to be averaged, or whether one is a failed run* — a statement about the deposit, not about filenames. **Second error: the bases named were the wrong ones.** Deposit metadata is `submitter_metadata`, which §5.3 marks `inferred`; the sentence demanded an *authoritative* basis and then pointed at a source that cannot carry one. **Nothing requires authoritative here, and the record already in the graph proves it**: `curation_PXD018299.json` carries `basis = 'publication_methods'`, `confidence = 'inferred'`, and every `SiteObservation` and the 12-of-14 baseline rest on it. Holding the proteome run to a standard the diGly run does not meet would be unjustifiable. **So the row stays on a named and citable ground**: §5.3's `publication_methods` — the associated paper's methods section — is public, is open, and is **unchecked**; it is not walked here. `author_correspondence` remains a second route and is his. The row would move only if the public avenue were walked and found empty. **I8's second clause is what that ground costs, and it is already live rather than newly incurred**: *any result derived from a curation with `confidence = 'inferred'` is labelled as such in every view and export, naming the `basis`*. The shipped record is already `inferred`, so the obligation stands today against `bzk/query/`'s five questions, `bzk/ui/app.py`'s three panels and I18's export boundary — and `invariants.py` still lists I8's labelling half as unenforced. A second `inferred` record for the proteome run adds no new kind of debt, only more of it. Named here and not built |
| UniProtKB resolution | Sequence-version pinning, isoform-aware, position validation, persistent cache |
| Evidence graph in Kùzu | `Observation` and `EvidencedInference` contracts defined even though few subtypes ship |
| Quantitative matrices in DuckDB | I11 — retained permanently, never only derived statistics. **Site grain only, as of 2026-08-10**: 48,696 cells in `site_values`, **0 in `protein_values`**. The protein adapter exists and writes cells; what is missing is a curation record for the proteome run, so the gap is now the deposit's sample mapping rather than the pipeline. **Kept in v0.1**, on the row above and not restated here: the site half is met and needs nobody, and the protein half waits on the same curation record. Its justification was corrected on 2026-08-12 — the deposit *had* been checked, and the open avenue is `publication_methods` rather than an authoritative basis |
| `welch_t` | **Implemented first**, and **its results are in the graph since 2026-08-09** — 1,362 `DifferentialResult`s under one `Analysis`. The 12-of-14 baseline was measured under Welch + BH; reproducing it exactly is how a pipeline bug is distinguished from a genuine difference between tests |
| ~~`perseus_s0`~~ | **Moved to v0.2 on the dependency axis, 2026-08-11.** ADR-0015's Consequences record that *"the `s0` and FDR parameter values are not yet known — to be obtained at the meeting"*, and § *Author correspondence* carries the same gap independently: *"Exact `s0` and FDR values still to obtain"*. A SAM-style modified *t* cannot be implemented against unknown parameters, and no value in this repository can stand in for them — picking one would assert a number the collaborator has not given, which is the failure ADR-0017 names as *being 95% right about `s0` and permutation FDR is worse than useless*. **ADR-0015 is unaffected and unamended**; see the note below the table |
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
| ~~Collaborator's Perseus tables~~ | Real results from the intended first user | Perseus — **moved to v0.2, 2026-08-11**: the supply side of the adapter row above, and the one build target in this table that no public archive can substitute for |
| PXD064305 and the other 2025 deposits | Embargoed pending publication; not yet accessible | DIA-NN (v0.2) — **and the grounds were re-examined on 2026-08-11 rather than inherited.** The DIA-NN ground is an adapter fact and survives untouched, since the dependency axis says nothing about which search engine wrote a file. The embargo is a *second and independent* ground on the new axis: *pending publication* makes accessibility the depositing group's to grant. **Both would have to fall for this row to come forward**, so it is more firmly at v0.2 than before, not less |

**ADR-0015 stands unamended, and that was decided rather than assumed — 2026-08-11.** Moving
`perseus_s0` to v0.2 raised whether it contradicts an `Accepted` record that calls the entry
**default and required**. It does not, and the argument is not that leaving 0015 alone is cheaper.
**`CLAUDE.md`'s single-source table puts scope, milestones and deferrals in this document**, so a
release claim inside an ADR would be a second home for a fact this table owns — the duplication that
table exists to prevent. `ARCHITECTURE.md` §4's registry table already reads it that way: it states
a status *per entry*, and the one entry carrying a release marker ends *"ROADMAP is authoritative for
scope"*, which routes exactly this question here. And ADR-0017's own Consequences give the reason
`perseus_s0` is required — *matching the collaborator's numbers is a precondition for being trusted*
— which is a claim about what the platform must eventually do, not about which release does it.
**So 0015 decides which registry entry is default; this table decides when it ships**, no
superseding record is written, and no ADR number is taken.

**Two deferrals withdrawn, 2026-08-06.** `ProteinAssignment` and `Imputation` were previously deferred to v0.2, to be represented as fields on `SiteObservation` and as JSON on `Analysis` respectively. Both deferrals are withdrawn.

The saving was notional. The full DDL validates unchanged against Kùzu 0.11.3, so the tables are created either way; and `ModifierAssignment` — already in scope — establishes the node-per-inference pattern and its cardinality. Populating two more tables through the same code path costs close to nothing.

The alternative cost was real: two representations of the same fact, one as fields and one as a node, is exactly the duplication `CLAUDE.md` forbids, and it would have made I14 and I15 enforceable in two different ways depending on version.

### Explicitly deferred

| Deferred | Target | Why |
|---|---|---|
| **`perseus_s0`** | v0.2 | **Moved here 2026-08-11 on the dependency axis.** ADR-0015 records the `s0` and FDR values as *"not yet known — to be obtained at the meeting"*, and no substitute exists: a chosen value would assert a parameter the collaborator has not supplied. **Nothing he could say leaves it in v0.1** — supplying the values unblocks it rather than altering it. ADR-0015 is unaffected; see the note under § *In scope* |
| **Perseus adapter run on a real export** | v0.2 | **Moved here 2026-08-11.** The *module* stays in v0.1 and is written and fixture-tested; what moves is the milestone, because the only input that completes it is a Perseus table carrying a `Difference` and a p-value, and the published BJC exports were measured on 2026-08-09 to carry no test statistic. This is § *Weeks 3–4*'s exit, and it is **half** of it — the *cross-queried* half is separately blocked on `ONTOLOGY.md` §11 Q1 and by nobody outside this repository |
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
| **`moderated_t_ebayes`** | v0.2 | Needed for the comparison capability, not for the first pipeline. **Considered for the v0.1 side of the 2026-08-11 redraw and deliberately left here, on a reason that is not the one above.** It needs nobody — the retained matrix is on disk, the registry exists, and § *Measured findings* establishes that under I16 a second test is a second `Analysis` with its own recovery number, so no new machinery — and *needs nobody* was the whole of the case for bringing it forward. It fails the second test: **he could say to match Perseus before adding a test of our own, which is ADR-0015's own reasoning**, and that would make it wasted v0.1 work rather than merely early. A row the meeting could change does not come forward, so this one does not, and the axis therefore moved **nothing** into v0.1 |
| RNA-seq modality | v0.3 | See `ONTOLOGY.md` §11 Q2 |
| Local LLM serving | v0.3 | Follows natural-language querying |

#### Rows examined on the dependency axis and left where they are — 2026-08-11

Recorded because a row that was looked at and kept is not the same as a row nobody read, and only
the first can be audited.

| Row | Decision |
|---|---|
| **MaxQuant site-table adapter** (in scope) | **Stays.** PXD018299 is a public PRIDE deposit, already ingested — 2,029 sites, 27 refused. Nothing about it waits on a person. That it happens to be the collaborating group's own published deposit (Pinto-Fernández *et al.*, *Br J Cancer* 124:817–830) changes nothing on this axis: a published deposit is public to everyone |
| **`welch_t`** (in scope) | **Stays.** Implemented, and its 1,362 results are in the graph. It is also now the **only** test in v0.1, which is a consequence of `perseus_s0` leaving and is stated here rather than left to be noticed: its own row calls it a way to tell a pipeline bug from a genuine difference between tests, and with one test in scope that comparison has nothing to compare against until v0.2 |
| **`ModifierAssignment`** (in scope) | **Stays, and *manual* was established rather than assumed.** The question was whether *manual assignment with basis* means the collaborator asserting. It does not: §6.1's `basis` is a **closed enum of eleven values, none of which is a person's say-so** — every one names an experimental or literature evidence type — and four are marked as drawn from PXD018299's own disambiguation strategy and *directly automatable*. The default is created automatically on ingestion at `inferred_default` / `ambiguous`. What a human does is *select which evidence applies*, which needs evidence and not an opinion. One basis, `isg15_interactome_concordance`, does wait — on `EnrichmentObservation`, deferred to v0.2 on its own grounds, which is a modelling dependency and not a person |
| **`embargo_holder`, `embargo_reference`, `embargo_released_at`** (§5 DDL; ADR-0016) | **Stay as declared, unpopulated.** Populating them needs whoever holds an embargo, but **no v0.1 row holds embargoed data** — the 2025 deposits are at v0.2 — and I18 is an *export-boundary* check whose trigger is the first export path, which is RO-Crate export, also v0.2. So the columns are in v0.1 and the dependency is not: nothing in v0.1 can reach a state where they must be filled |
| **Reference graph beyond Reactome and GO**; **SvelteKit**; **API routes** | **Stay deferred, and not re-argued.** All three are independent of him, so the dependency axis has nothing to say about them either way; each was deferred on its own grounds and this redraw neither strengthens nor weakens those grounds |
| **Volcano axis** (§ *Author correspondence*) | **Dependent, and blocks nothing in v0.1.** *To confirm at the meeting*, and it governs how a displayed number is read — but v0.1's output row is met with three panels and **no volcano**, so there is no v0.1 surface on which the ambiguity can be displayed. It is a live dependency against a v0.2 capability, not against this table |

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


### Cold to cold, identical — the histone explanation's own prediction, met, 2026-08-09

**Run against the pre-registration above. Every prediction held; the outcome is (1), identical.**

| Prediction | Result |
|---|---|
| Per-label id sets identical on all twelve labels, 12,769 ids | **held**, symmetric difference 0 |
| `Gene` 1,039, `ENCODES` 1,054, partition 1,054 / 3,492 / 15 / 0, refusals 27, sites 2,029 | **held** |
| Cache: 2,260 / 3,013 / 2,182 / 7 `AMBIGUOUS`, every shared sequence and pin identical, 0 version movements, snapshots differing in `fetched_at` only | **held**, all of it |
| Fetch count **5,273** | **held**, the same integer twice |
| 391 tests, 0 skipped with the graph, 10 without | **held** |
| Empty content store: exit **1**, `INCOMPLETE:` line, both stores written | **held** |
| Panel two over a DDL-only graph: fourteen `NOT_STORED`, 0 `UNATTRIBUTABLE` | **held**, and over the curation-only graph too |
| Panel two over the full cold graph: 12 of 14, `DDX58`/`OAS1` `UNATTRIBUTABLE` | **held** |
| `.streamlit/config.toml` present in the fresh checkout with both values | **held** |

**Why identical is worth more here than it usually is, and still not worth much.** The first cold
run differed from the warm one and the difference was argued to be internal — a superseded parse
frozen in the entry cache. An argument like that predicts non-recurrence, and this is the run that
could have falsified it: same code, same deposit, empty cache, and the twelfth label came back.
**Nothing internal is unstable.** What it does not touch is the external half: three hours apart,
against an authority that releases roughly monthly, so an unchanged UniProt is the likeliest reason
the two matched and this is no evidence at all about a release boundary. Registered as the weakest
useful outcome before the run, and it is.

**The strongest single number is not the total but the fetch count.** 2,260 entries and 3,013
sequences — **5,273** round trips — twice, exactly. That is a property of the deposit and the
resolver rather than of the network, and it is what lets a reader price a rebuild for their own
deposit. The wall clock moved: **37 m 14 s then 39 m 34 s**, 6.3% apart, so `OPERATIONS.md` §5's
cold figure is now a range and its `~0.40 s per fetch` is 0.40–0.43. **The entry said *n* = 1 and
was honest about it, and that was still not enough** — a single draw stated correctly is not a
usable figure, and this is the fourth time on this project that a point value has had to become an
interval after being contradicted.

**A mid-run rate was measured, with its clock spacing recorded, because the last one was not.** A
15-second poller over a 706-second window gave 1.14 s per accession and 0.50 s per round trip —
above the whole-run 0.43, so the within-run rate is not flat and the whole-run figure is the one to
quote. `ROADMAP.md`'s 12× error came from three spot counts with unrecorded spacing; recording the
spacing is what makes this one a measurement rather than an impression.

**The one finding, and it is in the documentation the *first* rehearsal wrote.** §4.1 was correct
and worked as written; both prerequisites were already present, so **`:144`'s *the second is the one
that surprises* was not tested here** — the honest report is that its precondition did not hold, not
that it was confirmed. The failure is one cross-reference away, in `HANDOFF.md` §3, where every line
of the run block began `python -m …` against §4.1's own `.venv/bin/python`. **It fails
machine-dependently, which is worse than failing.** Run literally: `python` is
`/usr/local/bin/python`, **3.11.15**, with a user-site `requests`, so `bzk.sources.pride` and
`bzk.sources.protein_groups` **succeeded** — right bytes, right digests, wrong interpreter — and the
run died on the third line at `ModuleNotFoundError: No module named 'kuzu'`, which points at a
dependency rather than at the interpreter. Corrected in place — **and the class is not closed**: three more imperative bare-`python` lines survive at `HANDOFF.md:241`, `:316` and `:392`, named there and deliberately not swept, because this was a freeze run and correcting the documented run path was its remit. The many *references* to `python -m …` across the tree — instrument columns, dated records of what a past rebuild reported — are a different thing and are right as they stand. Nothing else in the procedure was wrong.

**`bzk drift` was not run and is named as unrun.** Above 35 minutes at 3,013 sequences on a turn
already carrying a 39-minute rebuild, and §5 records that a run over an archive that has not aged
compares fetches against fetches of the same release — this archive was written hours ago. The
second cold rebuild is the better instrument for the question anyway: it re-fetched all 3,013
sequences into an empty tree and the comparison is over the whole archive rather than a sample.


### Pre-registration: what writing computed differential results would mean, 2026-08-09

**Written and committed before any code.** `query.differential_table` returns `NOT_STORED` because
nothing writes `DifferentialResult` rows: `perseus.py` emits them and has no real input, and
`pxd018299_differential.py` computes them and writes none. This closes the gap for the `welch_t`
run, which § *v0.1 — in scope* records as implemented first for a stated reason.

**The starting state, measured before predicting anything.** `python -m bzk.rebuild`: **1 m 55.2 s**,
2,029 sites, 27 refusals, 12,782 node and 10,283 edge statements, 48,696 cells. Graph: `Gene` 1,039,
`ENCODES` 1,054, `gene_absence` 1,054 / 3,492 / 15 / 0, **12,769 ids over twelve labels** captured
before the rebuild dropped them. All five queries run: `differential_table` `NOT_STORED` on both
analyses, `unprovenanced` `DifferentialResult: (0, 0)`, `refusals` `NOT_RETAINED`,
`imputation_state` `NOT_STORED` on both, `Contrast` / `Imputation` / `DifferentialResult` all **0**.

**Step 0 is answered and needs no work.** `differential_table` **already surfaces the test**:
`DifferentialRow` carries `quantity`, `test` and `fdr_method`, read off the `Analysis` at
`graph.py:326` where I16 puts them. So a caller can tell a `welch_t`/BH row from a
`perseus_s0`/permutation one, and ADR-0015's *will not match their numbers* concern is answerable at
the row. One gap is at the **screen** rather than in the query: `app.py`'s table renders `test` and
not `fdr_method`, so a reader sees half of the pair the concern turns on.

**`moderated_t_ebayes`'s absence changes nothing this turn writes.** Under I16 a second test is a
second `Analysis` with its own recovery number; adding one is not registered here and would put two
recovery figures in the graph on the turn that puts the first one in.

**Structure established by probing before predicting, because a prediction about output cannot catch
a wrong premise about structure.** `store.write_change_set` builds `labels_by_id` from the
change-set's **own** nodes, so an edge to an observation that is not in the batch raises rather than
matching the stored one — ADR-0019's self-containment, enforced. Run against the validator, the
minimal batch that passes is: the `SiteObservation`, **its `ModifierAssignment`** (I3 refuses the
observation alone), the `Analysis`, an `Imputation` (I15 refuses an analysis producing results
without one), the `Contrast`, and the `DifferentialResult`. Both refusals were seen, not reasoned
about. The observation, its assignment and the `Dataset` are taken from the adapter's own parse
output rather than re-keyed, so their ids cannot be wrong and the `MERGE … SET` rewrites identical
values.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| **No existing id moves**: 0 lost on all twelve labels; `Analysis` gains exactly 1 and no other populated label gains any | per-label set diff against the pre-rebuild capture | exact set equality per label |
| `DifferentialResult` = **1,362**, one per tested row — 2,029 ingested, presence rule ≥2 of 3 in either arm, and whole-matrix imputation leaves every admitted row with a computable statistic so `tested == after presence rule` | Cypher count | exact integer; falsified if `tested < 1,362` |
| `Contrast` **1**, `Imputation` **1**, `Analysis` **3** | Cypher count | exact |
| Edges: `WAS_GENERATED_BY` **1,362**, `RESULT_FOR_SITE` **1,362**, `RESULT_IN_CONTRAST` **1,362**, `IMPUTATION_FOR` **1**, `USED` **3** | Cypher count | exact |
| Refusals **27**, sites **2,029**, `gene_absence` **1,054 / 3,492 / 15 / 0** — unchanged, since nothing re-ingests | rebuild report and Cypher | exact |
| `differential_table(new)` → **1,362 rows**, absence **`None`**, every row `test='welch_t'`, `fdr_method='BH'`, `protein_adjusted='not_applied'`, `substantially_imputed=None` | the query | exact |
| `differential_table(curation analysis)` → `[]` with **`NONE_FOUND`**, not `NOT_STORED` — the table is no longer empty, so the same empty list means the other thing | the query | exact enum identity |
| `unprovenanced` → `DifferentialResult (0, 1362)`; `Dataset (0, 1)`; `SiteObservation (0, 2029)` | the query | exact |
| `imputation_state(new)` → methods `('downshifted_normal',)`, seeds `(0,)`, absence `None`, `satisfies_i15` **True**; the two older analyses move `NOT_STORED` → **`NONE_FOUND`** | the query | exact |
| `refusals` → **`NOT_RETAINED`**, unchanged; `gene_symbols` → **12 of 14**, unchanged; `site_keying` → 2,029 with a basis, 522 displaced, unchanged | the queries | exact |

**No prediction about the wall clock**, per this section's rule.

**The recovery figure gets the sharpest fence yet, because this turn puts a number in the graph that
looks exactly like it.** § *Validity-conditional promotion* fixes **12 of 14 as identifiability, not
recovery** — how many published symbols are answerable from stored `Gene.symbol`. What this turn
writes has a **recovery** count, under `welch_t` and BH, against a published comparison of 9 of 14
through this route with every miss traced. **This turn does not compare the two, does not recompute
the comparison, and writes nothing near either that could blur which quantity is which.** The
identification route is not switched: `pxd018299_differential.py` keeps reading `Gene names`, for
the reason recorded in its own docstring, and that decision is not revisited here.

**Decisions to be argued in the records rather than assumed here.** Which `kind` a computed analysis
takes from `'processing' | 'curation' | 'external'` and what `parameters_observed = true` then
obliges under I19; where a module that computes a statistic and emits a change-set lives, given that
`sources/` fetches, `adapters/` parses and `store.py` writes; whether one computed analysis over one
dataset forces §11 Q1's `Contrast` placement. **Nothing new is built beyond the write path** — no
second test, no volcano, no read-layer additions.


### The graph holds computed results: 1,362 rows, and every prediction held, 2026-08-09

**Run against the pre-registration above.** `python -m bzk.sources.pxd018299_differential` now writes
what it computes. Every registered prediction held, including the two that were about meaning rather
than about counts.

| Prediction | Result |
|---|---|
| No existing id moves; `Analysis` gains exactly 1 and no other populated label gains any | **held** — 0 lost on all twelve; `Analysis` +1, `Contrast` +1, `Imputation` +1, `DifferentialResult` +1,362, nothing else moved |
| `DifferentialResult` = **1,362**, derived from the presence rule over 2,029 | **held** — `after presence rule 1,362`, `tested (non-NaN p) 1,362` |
| `Contrast` 1, `Imputation` 1, `Analysis` 3 | **held** |
| `WAS_GENERATED_BY` 1,362, `RESULT_FOR_SITE` 1,362, `RESULT_IN_CONTRAST` 1,362, `IMPUTATION_FOR` 1, `USED` 3 | **held** |
| Refusals 27, sites 2,029, `gene_absence` 1,054 / 3,492 / 15 / 0 unchanged | **held** |
| `differential_table(new)` → 1,362 rows, absence `None`, every row `welch_t`/BH/`not_applied`/`substantially_imputed=None` | **held**, asserted over all 1,362 |
| `differential_table(the other two)` → `[]` with **`NONE_FOUND`**, not `NOT_STORED` | **held** |
| `unprovenanced` → `DifferentialResult (0, 1362)` | **held** |
| `imputation_state(new)` → `('downshifted_normal',)`, `(0,)`, absence `None`, I15 satisfied; the other two `NOT_STORED` → `NONE_FOUND` | **held** |
| `refusals` `NOT_RETAINED`; `gene_symbols` 12 of 14; `site_keying` 2,029 with 522 displaced | **held**, all unchanged |

**The two predictions worth having made are the ones about the same empty list.** `NOT_STORED` →
`NONE_FOUND` on two analyses that did not change is what an absence value buys: their state is
identical and the honest answer about it is different, because the claim was never about them. A
bare `[]` would have moved silently.

**Step 0 needed no work and the answer is why.** `differential_table` already carried `test` and
`fdr_method` off the `Analysis`, where I16 puts them, so a row is legible as `welch_t`/BH rather
than Perseus-comparable. The gap was one layer out: `app.py`'s table rendered `test` and not
`fdr_method`, showing half of the pair ADR-0015's Consequences turn on. One column added; the
`moderated_t_ebayes` question was answered without work, since under I16 a second test is a second
`Analysis` with its own recovery number and adding one is not registered here.

**Three structural premises, two of them established by being refused.** `store.write_change_set`
resolves an edge's endpoints from the change-set's **own** nodes, so a result cannot attach to an
observation the batch does not carry; including the observation then makes I3 demand its
`ModifierAssignment`. Both refusals were produced against the validator before any writer existed.
**The pre-registration got the layer wrong and the test found it**: it said `store` raises, and
ADR-0019's structural validation raises first, naming the edge — the stricter guard is the earlier
one, and reading `store.py` was what produced the wrong attribution.

**A fourth premise was wrong in the other direction and is the better behaviour.** Two results over
one observation in one analysis were expected to converge on one node, since the numbers are
excluded from identity (§3). The batch is **refused** instead: a duplicate id inside one change-set
means the producer contradicted itself rather than repeated itself, and silent convergence would
have kept whichever the loop wrote last. Found by writing the test, not by reading the code.

**Where the writer lives, and why not where the computation is.** `bzk/analysis/` is a fourth layer
beside `sources/`, `adapters/` and `stats/`, argued in `ARCHITECTURE.md` §3: there is no file to
parse and no observation to mint, `stats/` must not learn the schema or I11's retained matrix stops
being swappable, and a dataset script is the wrong home for a contract every future computed
analysis needs. It does no arithmetic, no I/O and no writing, asserted on the module's AST.

**`kind` and `parameters_observed`, decided against I19 rather than against new machinery.**
`'processing'` — §5's enum offers `'processing' | 'curation' | 'external'` and `'external'` is the
value that says the platform did **not** run it; there is no fourth. `parameters_observed = true`,
which I19 makes the standing a platform-produced result has, and the obligation it carries is
concrete: the recorded parameters must be **the values the computation used**, so they are passed
from the same constants rather than transcribed a second time, and the flag is not an argument the
caller can set.

**§11 Q1 is not forced by this run.** `Contrast` is keyed on numerator and denominator with no
dataset anchor, so a second dataset declaring the same contrast would converge on this node — which
is exactly the reuse Q1 describes. One computed analysis over one dataset produces one `Contrast`
and no collision, so nothing here settles or requires settling it; the keying is `perseus.py`'s,
inherited rather than chosen.

**What writing results did not change.** `substantially_imputed` is still `None` on every row. I15's
clause needs a denominator that lives per-sample in `quant.duckdb`, and the location of the
denominator is unaffected by writing rows — the `Imputation` node records method and seed, which is
what makes the mask reconstructible, not what makes the fraction derivable from the graph.

**The recovery fence, stated once and not crossed.** § *Validity-conditional promotion* fixes **12
of 14 as identifiability**. The run written here reports a **recovery** count, under `welch_t` and
BH. They have been the same integer since `Gene` landed and they are not the same quantity. This
entry does not compare them, does not recompute the published 9-of-14 comparison, and the
identification route was not switched — `pxd018299_differential.py` still reads `Gene names`, for
the reason its own docstring records.


### Pre-registration: what retaining refusals would mean, and step 0's answer, 2026-08-09

**Written and committed before any code.** `query.refusals` returns `NOT_RETAINED` because
`adapters.base.Refusal` never leaves the adapter. Step 0 asks whether a refusal is an entity, and
**the answer registered here, before implementing anything, is no** — with the further answer that
no legible form is written this turn either, for reasons that are measurements rather than taste.

**The starting state, measured before predicting anything, and a finding fell out of confirming
it.** Before the rebuild: `Analysis` 3, `Contrast` 1, `Imputation` 1, `DifferentialResult` **1,362**,
`SiteObservation` 2,029, `Gene` 1,039; `differential_table` 1,362 rows for the `welch_t` analysis and
`NONE_FOUND` for the other two; **14,134 ids over fifteen labels** captured. `python -m bzk.rebuild`
then took **1 m 40.9 s** and reported 2,029 sites, 27 refusals, 12,782 node and 10,283 edge
statements, 48,696 cells — and left `DifferentialResult` at **0**, `Contrast` 0, `Imputation` 0,
`Analysis` 2, with `differential_table` back at `NOT_STORED`. **`bzk rebuild` drops the computed
results and does not regenerate them**, because they are produced by a second command it does not
run. Re-running `python -m bzk.sources.pxd018299_differential` (52.3 s, 4,090 node and 5,450 edge
statements — **new measurements, no baseline for them exists in the tree**) restored the graph to
**exactly** the captured state: 14,134 ids, every per-label set identical, edges identical, partition
identical. So I9 holds over the *pair* of commands and `OPERATIONS.md` §5's sentence about what
`bzk rebuild` reconstructs is now false.

**The five populations, all measured, and they are not one kind of thing.**

| Population | Size | Shape |
|---|---|---|
| Site adapter `Refusal` objects | **27** — `residue_mismatch` 15, `unresolved_protein` 11, `no_razor_pick` 1 | per row, the platform's machinery failed on a specific input |
| Resolver per-accession failures (`resolve/nodes.py`) | **7**, all `no sequence_version` | per accession; feeds 11 of the 27 above |
| `perseus.py` | **0** `Refusal` objects; four `PerseusError` raises | file-level: a missing column or no declared contrast |
| Presence rule (`bzk/analysis/`) | 2,029 → 1,362 = **667** | a declared threshold, recorded in `filters_applied` |
| Pre-ingestion filters | decoys and contaminants **43**, localisation **242** | declared thresholds, counted in the report and stored nowhere |

**One premise in the enumeration was wrong and the measurement is what shows it.** The resolver's
failures are **7**, not the 3,492 `unresolved` in `gene_absence`. Those 3,492 are candidate
accessions the adapter never sends to the resolver at all — `ResolvedProteins.candidate_nodes` mints
them with that value — while the resolver's own failures are the seven accessions it tried and could
not key. Two populations, one word.

**Three kinds, not five instances of one.** *Declared-filter drops* (43, 242, 667): the criterion
is stated in advance and recorded in `filters_applied`; nothing about an individual row is
interesting, because the row failed a threshold. *Keying failures* (the 27, and the 7 behind eleven
of them): the platform's own machinery failed against a specific row, and the row is interesting
individually — residue drift is a finding about UniProt, not about data quality. *Unreadable input*
(perseus's four raises): file-level, and an exception is right. **`base.py`'s *deliberately not an
exception* is about rows**, so the two adapters do not conflict; perseus refuses no rows at all.

**Step 0, answered against the structure rather than against preference, with the structure probed
first.**

* **A refusal has no entity, and the probe says what that costs.** `unprovenanced` iterates
  `PROV_ENTITIES` — §7's `prov:Entity` list — so a label outside it is neither provenanced nor
  flagged: `Modifier` has 3 rows and the query does not mention it, confirmed by running. A
  `Refusal` node would sit outside the one invariant the read layer enforces.
* **Its id cannot be minted, and that is not paperwork.** `evidence_id("Refusal", …)` raises
  `'Refusal' has no identity spec in schema.IDENTITY`. Identity is a precondition. Composing one
  over `(dataset, row, reason)` means identifying a thing that does not exist by a file-local
  MaxQuant id; including `detail` would make prose identity-bearing.
* **ADR-0004's own rule assigns it elsewhere.** *One-per-entity is a graph property; one-per-entity-
  per-sample is columnar.* A refusal is neither — it is one per **input row**, finer than either,
  and there is no entity for it to be one of. By that rule it is columnar.
* **§7 opens *provenance is a PROV-O mapping, not a log*.** A node whose only edges are to the
  `Dataset` and the `Analysis` is a log row.

**And the legible form is not written this turn, which is a decision and not an omission.** The
count is one-per-`Analysis` and would be a graph property by the same rule — but a bare total is the
error `gene_absence` exists to refuse: *27 refused* tells a reader the population is incomplete
without telling them that **15 of them are sequence drift**, which is the finding. Storing it by
reason needs either a mini-format inside a `STRING[]` or a column per slug, and storing the
breakdown columnar puts it where `bzk/query/` cannot reach — the state `substantially_imputed = None`
already documents, so it would move the gap rather than close it. **Minting a shape to make one
query return something is what step 0 was told not to do.**

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| **No id moves and no count changes**: 14,134 ids over fifteen labels, every per-label set identical, all edge counts identical | per-label set diff against the capture above | exact set equality |
| Refusal counts as tabulated: 27 (15 / 11 / 1), 7, 0, 667, 43 and 242 | the adapter report and the run's own output | exact integers |
| `query.refusals` → **`NOT_RETAINED`**, `reasons = ()`, unchanged | the query | exact enum identity |
| `differential_table` → 1,362 rows for `welch_t`, `NONE_FOUND` for the other two; `unprovenanced` → `DifferentialResult (0, 1362)`; `imputation_state` → one satisfying I15 and two `NONE_FOUND`; `gene_symbols` → 12 of 14 | the five queries | exact |
| `NOT_RETAINED` **keeps a live case** — it is the only value that fits a fact no query can answer, and nothing stored this turn changes that | `graph.py`'s four `Absence` values against the state | exact |

**No collision sweep is predicted**, because step 0 does not land on a node type and there is nothing
to sweep. **The interface is not touched**: nothing stored changes, so nothing on screen changes, and
`absences_panel` already renders `NOT_RETAINED` with its detail beneath the heading.


### Refusals are not entities, and the enumeration was the finding, 2026-08-09

**Run against the pre-registration above. Every prediction held and nothing was stored.**

| Prediction | Result |
|---|---|
| No id moves and no count changes: 14,134 ids over fifteen labels | **held** — every per-label set, edge count and partition identical |
| Refusal counts: 27 (15 / 11 / 1), 7, 0, 667, 43 and 242 | **held**, all measured rather than quoted |
| `query.refusals` → `NOT_RETAINED`, `reasons = ()` | **held**, unchanged |
| The other four queries unchanged | **held** — 1,362 rows for `welch_t`, `NONE_FOUND` twice, `(0, 1362)` unprovenanced, one analysis satisfying I15, 12 of 14 |
| `NOT_RETAINED` keeps a live case | **held**, and it is now the *only* value of the four whose case is a fact no query can answer |

**No collision sweep was run and none was predicted**, because step 0 did not land on a node type.

**The three structural facts that decided it, each probed rather than argued.** `unprovenanced`
iterates §7's `prov:Entity` list, so a label outside it is neither provenanced nor flagged —
`Modifier` has three rows and the query does not mention it. `evidence_id("Refusal", …)` raises
*`'Refusal'` has no identity spec in `schema.IDENTITY`*, so identity is a precondition and not
paperwork; composing one over `(dataset, row, reason)` would identify a thing that does not exist
by a file-local MaxQuant id, and including `detail` would make prose identity-bearing. And
ADR-0004's own rule — *one-per-entity is a graph property, one-per-entity-per-sample is columnar* —
puts a per-**input-row** fact in neither, because there is no entity for it to be one of.

**Why no legible form was written either, which is a decision and not an omission.** A count is
one-per-`Analysis` and would be a graph property by the same rule. A **bare total** is the error
`gene_absence` exists to refuse: *27 refused* says the population is incomplete without saying that
**15 of them are sequence drift**, which is the finding. By reason needs a mini-format inside a
`STRING[]` or a column per slug; columnar puts the breakdown where `bzk/query/` cannot reach, which
is the state `substantially_imputed = None` already documents, so it would move the gap rather than
close it. **Minting a shape to make one query return something is what step 0 was told not to do.**
The absence is pinned by a test instead, both halves mutation-tested, so adding `Refusal` to the DDL
or an identity row for it fails rather than passing quietly.

**Three kinds, not five instances of one — and the model covered the middle one only.**

| Kind | Members | Why it is its own kind |
|---|---|---|
| Declared-filter drops | decoys and contaminants **43**, localisation **242**, presence rule **667** | the criterion is stated in advance and lives in `Analysis.filters_applied`; the row failed a threshold and nothing about it individually is interesting |
| Keying failures | the **27** — `residue_mismatch` 15, `unresolved_protein` 11, `no_razor_pick` 1 — behind which sit **7** accessions the resolver could not key | the platform's own machinery failed against a specific row; residue drift is a finding about UniProt, not about data quality |
| Unreadable input | `perseus.py`'s four `PerseusError` raises, **0** `Refusal` objects | file-level. `base.py`'s *deliberately not an exception* is about **rows**, and a file with no usable column has no rows to refuse — so the two adapters do not conflict |

**One premise in the enumeration was wrong, and measuring is what showed it.** The resolver's
per-accession failures are **7**, all `no sequence_version` — not the 3,492 `unresolved` in
`gene_absence`. Those 3,492 are candidate accessions the adapter never sends to the resolver;
`ResolvedProteins.candidate_nodes` mints them with that value. Two populations wearing one word,
and the eleven `unresolved_protein` refusals are rows over the seven, not over the 3,492.

**The larger finding came from confirming the state, not from the question.** `python -m
bzk.rebuild` **drops the 1,362 `DifferentialResult`s** along with the `Contrast`, the `Imputation`
and one `Analysis`, and does not regenerate them — they are written by a second command the rebuild
does not run, and `differential_table` goes back to `NOT_STORED`. **I9 is intact**: running the
differential straight afterwards restored the graph to exactly its prior state — 14,134 ids over
fifteen labels, every per-label set, edge count and `gene_absence` figure identical, and **4,090
node and 5,450 edge statements**, which have no earlier baseline in the tree. What was false is
`OPERATIONS.md` §5's opening sentence read as *this command restores the graph*; corrected there,
and `HANDOFF.md` §3's ordering is now load-bearing rather than a convenience.

**The interface was not touched, and that is the disclosure rather than an omission.** Nothing
stored changed, so nothing on screen changed; `absences_panel` already renders `NOT_RETAINED` with
its detail. `ROADMAP.md` § *Weeks 7–8*'s *ambiguity and correction status visible everywhere a
number appears* is not engaged, because this turn put no number anywhere.


### Pre-registration: what a MaxQuant protein adapter would mean, 2026-08-09

**Written and committed before any adapter code.** `ProteinObservation` has 0 nodes and the reason
is upstream of retention: the adapter does not exist. The reader does, guarded, and the file is in
`raw/` with a pinned digest.

**The starting state, measured before predicting anything.** `python -m bzk.rebuild` **1 m 50.3 s**
— 2,029 sites, 27 refusals, 12,782 node and 10,283 edge statements, 48,696 cells — then
`python -m bzk.sources.pxd018299_differential` **52.7 s**, restoring the pair's state exactly:
**15 labels, 14,134 ids**, every per-label set and edge count identical to the capture taken before
the rebuild. `ProteinObservation` **0**, `Gene` 1,039, `ENCODES` 1,054.

**What the adapter inherits, read rather than re-derived.** `maxquant.read_table` drops **six spill
lines** in this exact file — each carrying 147 tabs, so the field count matches the header and every
structural check passes — using the file's own contiguous `id` column rather than a heuristic; and
it reads bytes and decodes explicitly against the CRLF hazard. The adapter inherits both by going
through the reader, which is what `maxquant.py` was written early to provide.

**The identity is settled and is not re-decided.** `ProteinObservation` keys on `candidate_proteins`
anchored on `Dataset` alone (§3, ADR-0022): a `MANY_MANY` `RESOLVES_TO_PROTEIN` cannot be an anchor,
and the observed group replaces the single-`Protein` anchor that forced a razor pick. The adapter
reads **`Protein IDs`** — the group as the search reported it — which is also the first entry of
`perseus.PROTEIN_COLUMNS`, so the two adapters agree without a decision. `Majority protein IDs` is
MaxQuant's own narrowing to the subset carrying half the peptides; §6.3 calls that its razor-rule
inference, and reading it would silently substitute an inference for the observation.

**The storage question is not reopened.** `quant.duckdb`'s `protein_values` exists, the row shape is
identical to `site_values` by ADR-0004's contract, and `value` is nullable because a null cell is a
measurement the search did not report. Nothing about writing protein cells contradicts it.

**Measured on the real file, before the adapter existed, so the predictions below are derived and
not read off a run.** 4,988 physical lines → **4,982** rows after six spill lines → **4,797** after
`Reverse` and `Potential contaminant`. `Protein IDs` is non-empty on **all 4,797**; 4,133 (86.2%)
name more than one accession; the largest group holds 57. Distinct accessions **23,807**, and the
sum of group sizes is **23,807** as well — MaxQuant's groups are disjoint, so those two coincide by
construction rather than by luck. ~~Fourteen quantitative columns per family (`Intensity `,
`LFQ intensity `, `iBAQ `).~~ **Wrong on the third — 14, 14 and 0; see the outcome below.**

**Step 1's decisions.**

**A group with no razor pick is not a case here.** At site grain a pick is unavoidable because the
`ModificationSite` key carries a protein-specific position; at protein grain ADR-0022 made the group
*the identity*, so there is nothing to pick and `no_razor_pick` has no analogue. The three site slugs
do **not** transfer: `no_razor_pick` cannot arise, `unresolved_protein` cannot (no sequence is
needed — a protein-level quantification measures a gene product, not a sequence version, §3), and
`residue_mismatch` cannot (no residue). **One new slug is defined and it is a counted kind and
nothing more**: `empty_protein_group`, for a row whose accession list is empty, because
`candidate_proteins` is identifying and an empty list would key every such row identically.
**Measured 0 instances on this file**, so it is tested against a synthetic row rather than a real one.

**What `Analysis` and `Dataset` this belongs to.** §3 keys `Dataset` on `content_hash`, so the
proteinGroups file is a **second `Dataset`** — a different digest, already pinned in `pride.py`. It
therefore needs its own ingestion `Analysis` with its own `USED` edge, and `unprovenanced` will
compute a status for it as a `prov:Entity`.

**The registered outcome is that the ingestion does not happen, and this is registered before the
adapter is written rather than discovered while writing it.** The proteinGroups file's fourteen
columns are the **proteome** run — `WT_P_2hGradient1`, `KO_INF_P_2hGradient2` and so on — and the
curation record's twelve `Sample`s are the **diGly** run's raw files. The two sets do not overlap in
a single member. Minting samples from the fourteen column names is what I8 forbids in as many words:
*experimental design inferred from filenames is never presented as though it came from the
submitters*. §5.3's `filename_inference` basis exists for exactly this and would sanction a second
curation record — **and the mapping is not deducible even so**: KO/none has **five** columns for
three replicates, three of which name replicate 1
(`KO_P_2hGradient1`, `KO_P_2hGradient1_190305112303`, `KO_P_2hGradient1_2ul`), and `_2ul` is a
different injection volume, which is a different preparation rather than the same sample. Nothing in
the deposit says which is the replicate, whether they are technical replicates to be averaged, or
whether one is a failed run. **Authoring that mapping is a human judgement and this turn does not
make it.**

**So `I11`'s protein half is not met, decided against I11's own wording rather than by analogy.**
*Every observation persists its per-sample quantitative values in the columnar store.* With zero
`ProteinObservation`s the clause is vacuously true and unmet; with observations and no `Sample` to
key a cell to it cannot be met, and writing observations with `quant_ref` set and no cells would
assert retention that did not happen — the DDL calls a null `quant_ref` the violation state, and a
non-null one over an empty table is worse than the state it names.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| **The graph does not change**: 15 labels, 14,134 ids, every per-label set, edge count and `gene_absence` figure identical | per-label set diff against the capture | exact set equality |
| `ProteinObservation` stays **0**; `Dataset` stays **1**; `protein_values` stays **0 cells** | Cypher and DuckDB | exact integers |
| The adapter, run offline against the real file, would emit **4,797** `ProteinObservation`, **23,807** distinct `Protein`, **4,797** `REPORTS_PROTEIN`, **23,807** `RESOLVES_TO_PROTEIN`, **0** refusals, and **67,158** cells were a fourteen-sample mapping supplied | the adapter over the real file, without writing | exact integers |
| The five queries are unchanged — 1,362 rows for `welch_t`, `NONE_FOUND` twice, `(0, 1362)` unprovenanced, one analysis satisfying I15, `NOT_RETAINED`, 12 of 14 | the queries | exact |

**Probed before predicting, and the protein grain differs from the site grain in a way that matters.**
Against the validator: a `Dataset` + `ProteinObservation` + its `Protein`s with both edges validates;
so does the same batch **without `quant_ref`**, **without `REPORTS_PROTEIN`** and **without
`RESOLVES_TO_PROTEIN`**. ~~**No invariant fires at protein grain.**~~ **False, and withdrawn in the
outcome below — one does.** I3 forces a `ModifierAssignment`
onto every `SiteObservation` and there is no counterpart here, so correctness rests entirely on the
adapter and its tests. Self-containment still bites: an accession absent from the batch is refused
by name.

**Out of scope and registered as such**: the comparison against `protein_groups.py`'s survey is made
*available* by an adapter producing the same population by a different route, and is not made here —
it is its own pre-registration. No protein-grain differential results, no `RESULT_FOR_PROTEIN`.


#### Outcome: the MaxQuant protein adapter, 2026-08-10 — every prediction held, and three statements around them did not

| Prediction | Result |
|---|---|
| **The graph does not change** — 15 labels, 14,134 ids, every per-label set and edge count identical | **held.** Nothing was written; the registered stop-short is the reason, not an accident of the run |
| `ProteinObservation` stays **0**; `Dataset` stays **1**; `protein_values` stays **0 cells** | **held** |
| Offline over the real file: **4,797** `ProteinObservation`, **23,807** `Protein`, **4,797** `REPORTS_PROTEIN`, **23,807** `RESOLVES_TO_PROTEIN`, **0** refusals, **67,158** cells | **held, all six exactly.** `parse` takes **0.726 s**, plus 1 `Analysis`, 1 `Dataset`, 14 `Sample`, 14 `PRODUCED`, 1 `USED`. 4,982 rows read, 6 spill lines dropped, 185 decoys and contaminants |
| The five queries are unchanged | **held** — `(0, 1)` / `(0, 2029)` / `(0, 1362)` unprovenanced; 1,362 rows for `welch_t` and `NONE_FOUND` for the other two analyses; one analysis satisfying I15 (`downshifted_normal`, seed 0); `NOT_RETAINED` for refusals; 12 of 14 symbols |

**The confirming pair, run after the adapter was written and before anything was committed.**
`python -m bzk.rebuild` — 2,029 sites, 27 refusals, 12,782 node and 10,283 edge statements, 48,696
cells, `EXIT=0` — then `python -m bzk.sources.pxd018299_differential` in **47.470 s**, writing 1,362
`DifferentialResult`s over 4,090 node and 5,450 edge statements. Against an id set captured **before**
the rebuild dropped it: **15 labels, 14,134 ids, identical id-for-id, every edge count identical.**
`site_values` 48,696 cells, `protein_values` **0**.

**The one thing the pre-registration got wrong is the sentence it was proudest of.** *No invariant
fires at protein grain* was measured, not assumed — and measured with a probe that removed
`quant_ref`, `REPORTS_PROTEIN` and `RESOLVES_TO_PROTEIN` **entirely**. **I14's second half fires
here**, and only on a **strict non-empty subset**: an observation naming three candidates and
reaching all three validates, reaching *none* validates (a node re-staged as a referent carries no
edges, ADR-0019), and reaching *one or two* is refused by name. Removing all the edges is precisely
the shape that hides it. This is the recurring class on this project — *a check reporting clean
because it never ran* — arriving inside the instrument that was supposed to prevent it, and it is
the third time a green probe has been consistent with the guard never firing.

The correction is not only textual: the assertion in the tests that restates I14 was then re-checked
against what it can actually catch. `assert reached == set(observation['candidate_proteins'])` is
made to fail by emptying the edge loop (`protein_ids[:0]`) and **not** by narrowing it
(`protein_ids[:1]`), which raises I14 inside `parse` before the line is reached. So the test covers
exactly the gap the invariant leaves, and the mutation that looks like the obvious one establishes
the invariant instead.

**Two more statements the turn falsified, both by measurement rather than by reading.**

**`iBAQ` has no columns in this file, and the pre-registration said fourteen.** Measured on the
header: 14 `Intensity `, 14 `LFQ intensity `, **0 `iBAQ`** of any spelling — bare or per-sample.
`ibaq` stays in the adapter's quantity→prefix map because it is a MaxQuant output *option*, and a
declaration naming it against this file now raises by name rather than reading a family that is not
there. The earlier figure came from a measurement that counted the family without checking the file
carried it.

**A reported `0` is 39.8% of this matrix, and the adapter's first draft folded it to null.**
`maxquant_sites.py` had already decided the other way and recorded why: MaxQuant writes zero for an
undetected intensity, and reading that convention as absence is an interpretation I19 leaves to the
statistics layer. Measured here: **26,744 of 67,158 `LFQ intensity` cells are `0`** and 11,975 of
the `Intensity` ones. Two MaxQuant adapters over one deposit meaning two things by a zero is not a
difference of grain, so the function moved to `maxquant.cell_value` — one home — and the protein
adapter defers to it. With the draft's reading the same run reports 26,744 nulls and 0 zeros; with
the corrected one, 0 nulls and 26,744 zeros.

**Three defects in the adapter that only the tests found**, each a thing the change-set format does
not police: the ingestion `Analysis` was staged with no `__label__`; the `Sample` descriptors were
passed through unnarrowed, carrying `mapping_key` — not a DDL column — into the change-set; and a
`_deduplicate` post-pass over every node would have silently folded two rows naming one protein
group into one observation. The first two are now caught by structural validation and by a test
copied from the site adapter's, which is the shape of a fact with two homes — so `sample_nodes`
moved to `adapters/base.py`. The third is refused outright: two rows keying to one
`ProteinObservation` contradict ADR-0022's identity, neither row can be chosen, and folding them
would overwrite one row's cells with the other's under `INSERT OR REPLACE`. Measured **0 instances**
— 4,797 rows, 4,797 distinct sorted groups — because MaxQuant's groups are disjoint.

**Six guards, each made to fail, each mutation read back off disk before the run.** Removing the
`staged_proteins` filter → `STRUCTURE — duplicate node id 'uniprot:P09914'`; `protein_ids[:1]` →
I14 by name; `mapping.samples` for `sample_nodes(mapping)` → the narrowing test; folding `0` in
`cell_value` → the protein *and* the site test together, which is the one-home claim demonstrated;
disabling the duplicate-group guard → its test; disabling the quantity-family check → its test. One
assertion was **withdrawn rather than pinned**: `sorted(protein_ids) == sorted(set(protein_ids))`
cannot fail, because `parse` validates before returning and structural validation refuses a
duplicate `(label, id)`, so no `parsed` carrying one reaches an assert.

**The registered stop-short stands and is the turn's result, not its shortfall.** The ingestion did
not run, `protein_values` holds 0 cells, and I11's protein half is unmet — for the reason registered
in advance and re-confirmed against the file: the fourteen quantitative columns are the proteome run
and the curation record's twelve `Sample`s are the diGly run, sharing no member. The fourteen-sample
mapping used for the offline measurement was constructed in memory from the column names, is not a
curation record, and was never written. What changed is *which layer* the gap is in: the adapter was
the blocker on 2026-08-09 and the deposit's sample mapping is the blocker now.


### Pre-registration: I20's checker and the empty-table coverage guard, 2026-08-10

**Written and committed before any code.** Two properties that hold by construction today and are
asserted nowhere. This turn writes no nodes.

**The starting state.** `ruff check bzk tests`, `ruff format --check bzk tests` and `mypy bzk tests`
clean; `pytest tests/test_schema.py` 20 passed. Id set captured before anything: **15 labels, 14,134
ids**, `Gene` 1,039, `ENCODES` 1,054, `ProteinObservation` 0, `protein_values` 0.

#### (1) Q7 — the answer is on record; what is missing is the number and the function

§11 Q7 was answered 2026-08-07 and the deferral it replaced — *once `perseus.py` emits results at
both grains* — is the circular shape ADR-0023 named: the adapter chooses how many result edges to
emit, so counting its output reports its own choice back. The constraint is **at-least-one by
evidence** (the `neither` case occurred here, in the valid fixture, before `aefd4e9`) and
**at-most-one by construction** (no source computes one result at two grains). It is minted as
**I20** — I1–I19 are taken and no reserved number sits between them.

**Probed against the validator before predicting, because last turn's withdrawn assertion was one
that failed via structural validation rather than at its own line.** Over a change-set carrying a
`Dataset`, an `Analysis`, an `Imputation`, a `Contrast` and a `DifferentialResult`: **exactly one
`RESULT_FOR_PROTEIN` validates, exactly one `RESULT_FOR_SITE` validates, `neither` validates, and
`both` validates.** So neither failing case is reachable through ADR-0019's structural validation —
this is a genuinely new check and not a restatement of one, and that is established rather than
assumed.

**Which of the two the code can construct, read exhaustively rather than sampled.** Two modules emit
a result edge: `bzk/analysis/differential.py:156` emits `RESULT_FOR_SITE` and nothing else, and
`bzk/adapters/perseus.py:274` emits `RESULT_FOR_PROTEIN` and nothing else. **Nothing in `bzk/` can
construct `both`** — it is reachable only from a hand-written change-set, which is what the test
will be. `neither` is constructible by any caller that omits the edge, and was.

**`ONTOLOGY.md`:123's *a single site-level `Analysis` emits both* is a different axis and is not in
tension.** That is two `DifferentialResult`s over one observation — corrected and uncorrected —
**both site-grain, both attaching by `RESULT_FOR_SITE`**, so exactly-one holds per result. Read from
Q7's own entry rather than re-derived. The fixture is the demonstration: `bzk:dr1`, `bzk:dr3` and
`bzk:dr4` each carry `RESULT_FOR_SITE` alone and `bzk:dr2` carries `RESULT_FOR_PROTEIN` alone.

**`ONTOLOGY.md` §11 Q7's `ADJUSTED_BY` collision is read and not closed here.** It sits in the same
entry: `ADJUSTED_BY` is absent from §3's anchor list, so two corrected results differing only in
their baseline both mint `bzk:1529fff2e684983da8b8983e266cefb5`. I20 does not touch it and its
reasoning does not depend on it — I20 counts edges out of a result and never keys one — so this
turn neither closes nor disturbs it. Registered here so the disclaimer is on the record rather than
implied by silence. **Closed the next day by ADR-0025**, and this paragraph's line reference was
`:1073` when written and is `:1100` now — corrected here, and the reason it is worth a sentence is
that a line number is the one cross-reference form in this tree that rots without anything moving.

#### (2) The coverage question, measured before being characterised

`bzk/query/__init__.py`'s `__all__` exports **nine** query functions plus `connect` and the types.
Four carry an `Absence`, one returns `SiteKeying | None`, four return plain containers. Measured
against a DDL-only graph, before writing anything:

| Export | Over a DDL-only graph |
|---|---|
| `differential_table` | `([], Absence.NOT_STORED)` |
| `imputation_state` | `absence=NOT_STORED`, `satisfies_i15=False` |
| `refusals` | `absence=NOT_RETAINED` |
| `gene_symbols` | `NOT_STORED` per symbol, `detail` naming the empty `Gene` table |
| `site_keying` | `None` |
| `site_ids` / `analysis_ids` | `[]` |
| `unprovenanced` | `{'Dataset': (0, 0), 'SiteObservation': (0, 0), 'DifferentialResult': (0, 0)}` |
| `gene_absence_census` | `{'unresolved': 0, 'no_cross_reference': 0, 'not_captured': 0, 'encoded': 0}` |

**One premise of this turn is corrected by that table.** `gene_absence_census` was described as
returning *an empty dict over a DDL-only graph with nothing to say why*. It does not: it keys **all
four** §4 states at zero, which is the `test_the_attributed_form_is_available_where_a_protein_is_in_hand`
convention — *an omitted key and a zero read differently* — and an all-zero census says the
`Protein` table is empty without ambiguity. `unprovenanced` is the same shape. So of the four plain
containers, two answer by keying every category at zero and two are enumerations, where an empty
list has no second reading. **No export is silent over an empty graph today.** That is the fact the
guard freezes; it is not a defect being fixed.

**Whether the classification can be made self-checking — the question this turn has to answer, not
assume.** Registered as answerable **yes**, with the two holes named and each closed by a specific
mechanism: an *added* export is caught by set equality between the registry and the exported
callables, and a *changed signature* on a classified export is caught by binding the recorded
arguments through `inspect.signature`. What remains, and is recorded rather than closed, is that a
non-query callable added to `__all__` must be excluded by name — an explicit escape hatch of one
entry (`connect`), which fails loudly by forcing a decision rather than skipping silently.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| **No id moves**: 15 labels, 14,134 ids, every per-label set and every edge count identical | per-label id-set diff against the capture taken before the rebuild | exact set equality |
| I20 refuses `neither` and refuses `both`; exactly-one validates at **both** grains | `invariants.validate` over hand-built change-sets | the error names `I20`; four cases, exact |
| Both refusals arrive **at I20**, not at structural validation | the pre-change probe above already shows all four validating | exact — an `InvariantError` whose first field is `I20` |
| Removing `"I20": _check_I20` from `_CHECKS` fails **exactly** the two refusal tests and nothing else in the suite | mutation in a copy, read back before running | exact test names, exact count |
| Every existing fixture already satisfies I20, so no other test moves | `pytest` | exact — 0 other failures |
| The coverage guard classifies **9** exports; adding a tenth export without classifying it fails, naming it | add a query to `graph.py` and `__all__` in a mutated copy | exact — the failure message contains the new name |
| Changing a classified export's signature fails the guard through `bind` | mutation | exact — `TypeError` from `inspect.signature(...).bind` |
| The nine values in the table above are exactly what the guard asserts | the guard itself, over a DDL-only graph | exact enum identity and exact containers |
| The sweep floor at `test_tautology_sweep.py:778` (**26 / 926**) does **not** fail on the additions and must be re-denominated by hand | run `sweep()` | exact integers |

**What would make this turn a failure rather than a decision.** A coverage guard that passes by
omission — keyed off a list someone maintains beside `__all__` rather than off `__all__` itself —
or an I20 whose two mutations are caught by something other than I20. Both are the class recorded at
`HANDOFF.md`:593 and :954, and both are tested for by mutating the thing the guard names.

#### Outcome, 2026-08-10 — every prediction held, and the classification is self-checking

| Prediction | Result |
|---|---|
| No id moves — 15 labels, 14,134 ids, every per-label set and edge count identical | **held**, id-for-id against the capture taken before the rebuild |
| I20 refuses `neither` and `both`; exactly-one validates at both grains | **held** — the four probe cases invert exactly, each error naming `I20` |
| Both refusals arrive at I20, not at structural validation | **held** — established by the pre-change probe, where all four validated |
| Removing `"I20": _check_I20` fails exactly the two refusal tests and nothing else | **missed, and the miss is better than the prediction** — **four** tests fail, not two |
| Every existing fixture already satisfies I20 | **held** — `bzk:dr1`, `bzk:dr3`, `bzk:dr4` carry `RESULT_FOR_SITE` alone and `bzk:dr2` `RESULT_FOR_PROTEIN` alone; 0 other tests moved |
| The guard classifies 9 exports; a tenth fails, named | **held** — `Extra items in the right set: 'newly_added_query'` |
| A changed signature fails through `bind` | **held** — `TypeError: missing a required keyword-only argument: 'grain'` |
| The nine DDL-only values are what the guard asserts | **held**, unchanged from the pre-registered table |
| The sweep floor does not fail on the additions and must be moved by hand | **held** — 26/926 → 27/942, re-read from `sweep()` |

**The one miss is a prediction that was too narrow about its own guard.** Removing I20 from
`_CHECKS` fails **four** tests: the two refusal cases, `test_I20_accepts_a_result_at_either_grain`
and `test_valid_changeset_passes_every_check` — because `validate(..., only="I20")` raises
`ValueError: unknown or non-write-time invariant` when the id is not registered. So the registry
entry is guarded from both sides, by tests that assert the check *fires* and by tests that assert it
*runs at all*, and the prediction counted only the first kind. Recorded as a miss because it was
stated as an exact count.

**Three mutations on I20, each read back off disk before its run.** Removing the registry entry →
four failures, all naming I20. Relaxing `len(named) == 1` to `<= 1` → **one** failure, the `neither`
case alone, which is the sharpest of the three: it separates the two halves of the invariant so
neither can be carried by the other. Hard-coding `_RESULT_EDGES` to `RESULT_FOR_SITE` → four
failures including the DDL-derivation test, on its own line —
`{'RESULT_FOR_SITE'} == {'RESULT_FOR_PROTEIN', 'RESULT_FOR_SITE'}`.

**Four on the coverage guard, and one of them is the mutation this turn was told to make.** Adding
an export without classifying it fails `test_every_exported_query_is_classified` **by name** — that
is the anti-omission property, and breaking an existing export would not have tested it. Changing a
classified export's signature fails at `bind`. Removing `gene_symbols`' empty-`Gene` check fails the
value assertion and nothing else. Writing `group="absence"` on `site_ids` fails the group check,
which is what makes `group` a claim rather than a label: it is decided from whether an `Absence` is
reachable in the return, not from what the row says.

**What the coverage guard cannot do, recorded rather than closed.** A callable added to `__all__`
that is not a query must be excluded by name in `NOT_A_QUERY`, which holds one entry (`connect`).
That is an escape hatch, and the reason it is acceptable is that it is loud: the export is forced
into the registry or into that set, and both are edits someone has to write. A pattern — *anything
whose first parameter is `conn`* — would have made the exclusion an accident of naming instead.

**Three assertions classified in the sweep, none withdrawn.** The closest call is
`set(_RESULT_EDGES) == declared`, where both sides read `schema.REL_TABLES`: it is not an instance
because they are two different filters over one source and the property asserted is that the source
is shared, demonstrated by the hard-coding mutation failing on that line. What it cannot catch is a
change made to both sides at once, which is why the literal pair on the next line is not redundant.

**§11 Q7 is closed and `ONTOLOGY.md`:1073's `ADJUSTED_BY` collision is not.** I20 counts edges out
of a result and never keys one, so its reasoning does not touch the collision, and nothing here
narrows or widens it.

**One correction on the list had no target, and that is recorded rather than silently skipped.** A
*reflection-driven `Absence` guard* had been carried as a want to be corrected; searching the whole
tree — every `.py` and every `.md` — returns **zero** occurrences of the phrase or of anything
describing it. It was never written down, so there was nothing to correct. The guard this turn
wrote is behavioural rather than reflective and was designed against the rejection recorded in
`graph.py`, not against that item. Noted here because *the correction was already discharged* and
*the correction had no target* are different states, and a list that cannot tell them apart is how
a want survives being satisfied.


### Pre-registration: the three cache trees and a third cold rehearsal, 2026-08-10

**Written and committed before the rehearsal runs.** Nothing is built. Part 1 is a decision over
measurements already taken; Part 2 is the run.

#### Part 1 — the three trees, measured before being named

| | `~/.bzk-omics` | `.cold1` | `.warm` |
|---|---|---|---|
| entries / sequences / pins | 2,260 / 3,013 / 2,182 | 2,260 / 3,013 / 2,182 | 2,261 / 3,014 / 2,183 |
| `AMBIGUOUS` snapshots | **7** | **7** | **0** |
| `raw/` objects | 4 | 4 | **6** |
| graph | 15 labels, 14,134 ids | 12 labels, 12,769 ids | 12 labels, 12,774 ids |
| `Gene` | 1,039 | 1,039 | **1,044** |
| `.drift` receipt | none | none | 2026-08-08, 2,845 sequences |
| on disk | 124 MB | 105 MB | 106 MB |

**`~/.bzk-omics` and `.cold1` are byte-identical where it counts.** Same file sets in all three
cache tiers, symmetric difference **empty**, and the same SHA-256 over the concatenated sequence
files (`cacd8d24…`) and over the pins (`01b0e854…`). `.cold1`'s graph is `~/.bzk-omics`'s minus the
differential results — the state a rebuild alone produces. So `.cold1` holds **nothing the live tree
does not**, and it is a **leftover**.

**`.warm` differs by exactly one accession and two objects, and that is what makes it an
instrument.** Its extra entry, sequence and pin are all `P20591` — MX1, looked up by hand and never
requested by the pipeline — and its sequence tier **minus that one file digests to `cacd8d24…`, the
cold trees' value exactly**. So the immutable tier is not what distinguishes it. What does is the
**entry** tier: 0 of 2,261 snapshots carry `AMBIGUOUS` against 7 of 2,260 in both cold trees, and
its graph carries the five histone `Gene`s (1,044 against 1,039). Those snapshots were written under
the superseded first-cross-reference rule and cannot be regenerated — the fix cannot reach a cache
hit, and a re-fetch produces the cold tree.

**The distinction each tree is identified by is *input*, *leftover*, or *reproducibility
instrument*, and the third is the one the document set had no word for.** `ROADMAP.md` §
*Measured findings* already carries the histone finding's three measurements, so `.warm` is not the
only evidence **of** it — what `.warm` uniquely preserves is the ability to **re-derive** them. A
record can be read; an instrument can be re-run against. Deleting it would leave the finding true
and unfalsifiable, which is the state this project treats as worse than an open question.

**Decision.** `~/.bzk-omics` is the **live tree**, the input every documented command acts on.
`.cold1` is a **leftover** and may be deleted. `.warm` is a **reproducibility instrument**, is
**not deleted**, and is not an input — no documented command reads it, and its two orphan `raw/`
objects and its `P20591` entry are exactly why it must not be mistaken for one. Recorded in
`OPERATIONS.md` §1.

**`HANDOFF.md`:610's trigger does not fire, and the reason is a level difference rather than a
size one.** That row is about **objects inside** a content-addressed store having no reachability
notion, and its trigger is *the first `raw/` large enough that someone wants to delete something*.
Naming trees does not give `raw/` a reachability notion: `.warm`'s two orphan objects are still
indistinguishable from inputs **by the store**, which is the row's actual subject. And nobody wants
to delete anything for size — the largest tree is 124 MB. Identifying the tree does not identify the
object, so the row stands unchanged with its trigger unfired.

#### Part 2 — what the third cold rehearsal is predicted to show

**Five things have landed since the second rehearsal**: the MaxQuant protein adapter, I20 and its
checker, the empty-table coverage guard, the differential writer, and ADRs 0006–0012 and 0014.

**The suite figure has no current home and is reported as a measurement.** `ROADMAP.md`'s cold-clone
entry records **391**; collection today reports **435**. Measured here rather than predicted from
the delta, because three modules and a scatter of cases landed across five turns and no running
total was kept.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| Per-label diff against the **live tree** after the pair: **15 labels, 14,134 ids**, symmetric difference 0, every edge count identical | per-label id-set capture from the live tree, diffed against the clone's | exact set equality |
| `Gene` **1,039**, `ENCODES` **1,054**, refusals **27**, sites **2,029**, `DifferentialResult` **1,362** | the two commands' own reports and Cypher | exact integers |
| Cache reproduced: **2,260** entries, **3,013** sequences, **2,182** pins, **7** `AMBIGUOUS`; sequence and pin digests `cacd8d24…` / `01b0e854…` | file-set diff plus the concatenated digests | exact counts, exact bytes |
| Fetch count **5,273** — 2,260 entry + 3,013 sequence round trips | count the files written into an empty cache | exact integer |
| Suite in the clone: **435** tests, **0** skipped with the graph present; **11** skipped with no `~/.bzk-omics` | `pytest -q -rs` | exact integers |
| The five queries after the pair: `(0,1)`/`(0,2029)`/`(0,1362)` unprovenanced; 1,362 rows for `welch_t` and `NONE_FOUND` twice; one analysis satisfying I15; `NOT_RETAINED`; 12 of 14 | the queries | exact |
| §4.1 installs as written — `uv sync --frozen`, no edit to the procedure | running it | pass/fail |

**No prediction is registered for the cold wall clock.** `OPERATIONS.md` §5 puts this instrument's
resolution at *nothing finer than about two minutes*, the cold range is *n* = 2 at 37 m 14 s –
39 m 34 s, and a third draw inside that band would establish nothing a reader could use. What the
instrument **does** resolve is the fetch count, which reproduced exactly across both prior runs, so
that is where the falsifiable claim sits. If any rate is estimated mid-run the **poll spacing is
recorded with it**: `ROADMAP.md` § *Measured findings* carries a 12× error that came from three spot
counts with no clock. **The requirement is met by an instrument rather than by discipline since
2026-08-10** — `python -m bzk.fetch_progress` puts the interval on every sample line, so a
figure taken with it cannot be reported without its clock.

**Registered outcomes, weakest first.**

* **Identical is the weakest useful outcome and is named as such.** It says the four inputs plus the
  code reproduce the graph on a machine whose caches were empty an hour earlier. It does not say
  UniProt is stable — a run this close to the last one compares fetches against the same release,
  the defect already recorded for both `bzk drift` runs.
* **A changed refusal count with no id movement** is `OPERATIONS.md` §1's named case: content amended
  under an unchanged version number, visible only as a delta that reads like drift. **The delta I
  would accept as that is any refusal count above 27 whose extra rows are all `residue_mismatch`,
  with `sequence_version` unchanged on every affected accession** — a mismatch is what an amended
  sequence under a fixed version produces, and an unchanged version is what makes it invisible to
  the pin. A change in `no_razor_pick` or `unresolved_protein` would be a different cause and is not
  accepted as this one.
* **A different `Gene` or `ENCODES` count** is accepted by `OPERATIONS.md` §1's decision where a
  cross-reference genuinely changed at UniProt, and **not** accepted where the cause is internal —
  which is what the histone finding turned out to be. The discriminator is the `AMBIGUOUS` count: 7
  is the current rule's output, and a run returning 0 would be reading snapshots written under the
  superseded one, which a cold tree cannot do.
* **A moved id is the failure the pin cannot prevent in a cold tree**, because every pin is written
  by the fetch under test. There is no prior copy to compare against inside the run; the only
  reference is the live tree, and that is the whole reason the diff is taken.

#### Part 3 — cut, and the reason recorded

`bzk drift` is **not run**. `OPERATIONS.md` §5 already states that both prior runs reported zero
drift, that neither number means anything about the archive, and that the first meaningful run is
one over an archive aged weeks against UniProt's roughly monthly releases. Every archive on disk is
hours to a day old. A third clean result would not move that sentence, so it would cost ~35 minutes
to restate a paragraph.

**One line was checked instead of run, and it distinguishes the two states correctly.**
`drift.staleness_line` reads the receipt from the tree it is given, and its wording is a claim about
the **archive**, not about the command: over the live tree and `.cold1` it says *sequence archive
holds 3,013 sequence(s) and has NEVER been drift-checked*, which is true — neither tree has a
receipt, and `bzk drift`'s two runs both happened in `.warm`. Over `.warm` it says *last
drift-checked 2 day(s) ago over a DIFFERENT set (2,845 then, 3,014 now)*, which is the archive
digest doing exactly what it was written for. So the line does not conflate *this archive was never
checked* with *the command has never run*, and no fix is proposed.


#### Outcome, 2026-08-10 — every prediction held, and two figures widened

| Prediction | Result |
|---|---|
| Per-label diff against the live tree: 15 labels, 14,134 ids, symmetric difference 0, edge counts identical | **held** — `labels whose id SET differs: none` |
| `Gene` 1,039, `ENCODES` 1,054, refusals 27, sites 2,029, `DifferentialResult` 1,362 | **held**, all five |
| Cache: 2,260 / 3,013 / 2,182, **7** `AMBIGUOUS`, digests `cacd8d24…` and `01b0e854…` | **held** — entry, sequence and pin set diffs all empty, both digests equal |
| Fetch count **5,273** | **held** — the same integer a third time |
| Suite: **435** tests, **0** skipped with the graph; **11** with no `~/.bzk-omics` | **held** — 435 passed in 296.58 s; 424 passed, 11 skipped in 97.85 s |
| The five queries | **held** — `(0,1)`/`(0,2029)`/`(0,1362)`, 1,362 rows and `NONE_FOUND` twice, one analysis at I15, `NOT_RETAINED`, 12 of 14 |
| §4.1 installs as written | **held** — `uv sync --frozen`, exit 0, no edit to the procedure |

**The suite figure is a measurement and it is 435, against the 391 this section recorded** for the
first rehearsal. No running total was kept across the five turns that grew it, which is why it is
reported rather than derived.

**Two figures widened, and neither was predicted, correctly.** The cold rebuild took **2,396.2 s
(39 m 56.2 s)** — **22 s above** the top of the *n* = 2 band it was compared against. No wall-clock
prediction was registered because §5 puts this instrument's resolution at nothing finer than about
two minutes, and 22 s is an order of magnitude inside that; the range moves to **37 m 14 s –
39 m 56 s, *n* = 3**. The install took **9.1 s** against 7.5 s and 6.0 s, so §4.1's figure becomes
**6.0–9.1 s, *n* = 3**. Both are widenings of an interval that a smaller *n* could not have
anticipated, which is the correction this document has now applied to the same two numbers three
times.

**The mid-run rate was polled at 60-second spacing and the spacing is recorded with it**, per the
12× error this section carries: **~129 round trips per minute**, flat from the first sample to the
last, which is 0.47 s per trip. That is the *within-run* rate and it sits between the second run's
706-second window (0.50 s) and the whole-run averages (0.40–0.44 s), so the non-flatness the second
run found is confirmed with a coarser clock rather than contradicted.

**Two failures, in the order they happened.**

**(1) `python -m bzk.sources.protein_groups` died after 63.8 s** with
`requests.exceptions.ChunkedEncodingError: ('Connection broken: IncompleteRead(6895685 bytes read,
9165560 more expected)')` — a truncated download of the 16 MB proteinGroups file, leaving **3 of 4**
`raw/` objects present. Re-running it succeeded in 16.1 s. **This is a transient and not a procedure
defect**, and it is recorded rather than smoothed over because the procedure has no retry and the
next person will meet it: the fetcher is not idempotent-by-resume, it simply refetches, and the
content store's digest addressing is what makes a second attempt safe. All four objects verified
afterwards — every directory name equals the SHA-256 of the file inside it, and all four digests
equal the live tree's.

**(2) The background wrapper exited 144 while the rebuild exited 0.** `pkill -f "cold3/poll.sh"`
matched its own shell's command line, which contains that string, and killed the wrapper. The
rebuild's own `EXIT=0` and its full report were already in the log. Same error as the second
rehearsal; no measurement was affected, and it is named again because it is a property of the
harness rather than of the tree. **This run and the one it names are occurrences 1 and 2 of four —
the two with an artefact behind them. The other two, and why their provenance is weaker, are in
§ *The missing `&`*.**

**The registered outcomes, resolved.** The result is **identical**, the weakest of the four, and it
is weaker still than the second rehearsal's for the reason that section already states — one day is
far inside UniProt's release cadence. What this run adds that the second could not is that **the
code moved and the output did not**: five landings separate this clone from the reference graph, and
I20 now runs at write time over all 1,362 `DifferentialResult`s the second command writes. None of
the other three outcomes arose. No refusal delta (27 exactly, so the amended-sequence case named in
advance did not fire), no `Gene` or `ENCODES` movement, and no id moved.

**`.cold1` was not deleted in this turn.** The decision records that it may be; acting on it is not
a measurement and nothing here needed the space.


### Pre-registration: `ADJUSTED_BY` as an anchor, 2026-08-10

**Written and committed before any code.** Steps 0 and 0b were measured first; both permit the
amendment, so the turn proceeds.

**The starting state.** `ruff check bzk tests`, `ruff format --check bzk tests`, `mypy bzk tests`
clean; `pytest tests/test_schema.py` 20 passed. Id set captured before anything: **15 labels, 14,134
ids**, `DifferentialResult` 1,362.

#### Step 0 — it is no longer free, and the cost is measured rather than characterised

**The collision reproduces exactly against shipped code, before any amendment.** Two corrected
results differing only in their baseline, keyed through `keys.evidence_id`, both mint
**`bzk:1529fff2e684983da8b8983e266cefb5`** — the id §11 Q7's second half recorded on 2026-08-07,
matched digit for digit. The tuple is the seven lines that record shows, and the baseline appears in
none of them.

**§11 Q7 says the amendment *is free today and will not stay free*. That sentence was true on
2026-08-07 and is false now.** The differential writer landed 1,362 `DifferentialResult`s on
2026-08-09. Measured by recomputing every one of them with the anchor added to the spec in memory:
**1,362 of 1,362 ids move.** The `@ProteinObservation= null` line in the recorded tuple is exactly
why — an absent anchor still renders, so adding one changes the tuple for results that will never
carry the edge. **0 of the 1,362 carry an `ADJUSTED_BY` edge and all 1,362 are `not_applied`**, so
every one of them moves for a field none of them uses.

**What that costs, established rather than assumed.** Searched: **nothing outside the graph cites a
live `DifferentialResult` id.** No test asserts one — `tests/test_query_real_graph.py` and
`tests/test_rebuild.py` contain no `bzk:` literal at all; `tests/fixtures/valid_changeset.json` uses
hand-written ids (`bzk:dr1`…`bzk:dr4`) that no builder recomputes; the only complete recorded id in
the document set is the collision demonstration's, which is constructed and not live. `bzk rebuild`
**drops** all 1,362 and `python -m bzk.sources.pxd018299_differential` regenerates them, which is
§5's recorded two-command shape. So *ids move* is cheap here in a way it is not for
`ModificationSite`, whose keys are cited by position in every downstream claim — and the reason is
structural, not a matter of scale: these ids are **derived on demand and referenced by nothing**.

#### Step 0b — the first self-referential anchor, probed rather than reasoned

No `Identity` in `schema.py` anchors on its own label. Five probes against the shipped validator,
because the differential turn's three wrong premises were found on this exact surface:

| Probe | Result |
|---|---|
| Corrected result listed **before** its baseline in the node list | **validates** — and so does the reverse. ADR-0019 constrains *presence*, not order |
| A **two-cycle**, `R1 ADJUSTED_BY R2` and `R2 ADJUSTED_BY R1` | **validates** today |
| A **self-loop**, `R ADJUSTED_BY R` | **validates** today |
| One result naming **two** baselines | **refused** — `STRUCTURE — ADJUSTED_BY is MANY_ONE` |
| `evidence_id` called baseline-first on a DAG | keys both, `bzk:4a317881…` then `bzk:77aaecc7…` |

**Rows 2 and 3 are measurements of 2026-08-10 and stand; what they measured has since changed.**
Both cases still validate where the ids are **hand-written**, which is what the probe used. Where
the ids claim to be digests, **I21 refuses both** as of the same day — the two-cycle at whichever
member is reached first, the self-loop because an id cannot encode itself. The probe is not
falsified; the state it probed is no longer the current one.

**The self-anchor is workable and the ordering dependency is real but confined.** Structural
validation is order-blind, so the change-set carries no ordering obligation; the obligation is on
the **producer**, which must key the baseline before the result that anchors on it — a topological
order, and `ADJUSTED_BY` being `MANY_ONE` means each node has at most one such edge, so the
dependency graph is a forest.

**`ADJUSTED_BY` is already single-valued, so §3:89's anchor rule is satisfied without touching
multiplicity.** `MANY_ONE` from `DifferentialResult` to `DifferentialResult` means each *source*
appears at most once, which the fourth probe confirms the validator enforces. **`schema.py`:588 is
therefore not forced to change**, and the amendment depends on it staying `MANY_ONE` — that
dependency is new and is recorded in the ADR.

**One consequence the amendment introduces, named and not guarded.** A cycle validates today and
will still validate after; what changes is that it becomes **unkeyable** — computing either id needs
the other's. ~~So `evidence_id` cannot *produce* a cycle, which is a strengthening, and a hand-written
one remains constructible exactly as it is now.~~ No acyclicity invariant is added: that is a new
invariant and outside this turn's scope, and the amendment neither creates the hole nor widens it.

**The struck sentence is corrected 2026-08-10 and it was the wrong half that was wrong.**
`evidence_id` *can* produce an id for a member of a cycle — it resolves nothing, and an omitted
anchor is permitted — so what it cannot produce is the **cyclically-determined** id, which is the
producer's impossibility. The gap that phrasing hid is not the cycle at all: the same omission
re-mints ADR-0025's own collision, since two corrections against different baselines both minted
with a null self-anchor are one node again. Closed by **I21**, and the following turn's outcome
entry carries the measurements. *Outside this turn's scope* was the right call on the acyclicity
check specifically — it was subsumed rather than built.

#### Step 1 — the amendment and its record

`ONTOLOGY.md` §3's identity table moves first, `schema.py`'s `IDENTITY` mirrors it, and
`tests/test_schema.py` checks the mirror in four directions. **ADR-0025**, the next free number —
`decisions/README.md`'s Queued table reserves only 0018, whose subject is typed API routes.

**Status: `Proposed`.** Of README's three branches, `Superseded` is false — this record replaces no
earlier decision, it completes one §11 Q7 left open — and `Accepted` would assert a review that has
not happened, which is the branch nine of ten informative records took and the one the 2026-08-09
convention exists to stop repeating.

#### Step 2 — what the guard covers, stated so a pass cannot be misread

The two-`evidence_id` demonstration is run **before** the amendment (it collides, shown above) and
after (it separates), the same shape the I20 probe used. **The collision is unreachable through any
current writer**: `perseus.py`:256 records protein-grain results as uncorrected by construction, the
1,362 are all `not_applied`, and nothing emits `applied` at all. So the guard is exercised **only by
a constructed case**, and a green test is evidence the key builder separates two baselines — not
evidence that anything in this repository produces two. §11 Q7's 82%-multi-mapping argument is about
a faithful future implementation and is not a claim about today's graph.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| **1,362** ids move — every `DifferentialResult` and no other | per-label id-set diff against the capture | exact integer, exact set |
| **0** non-`DifferentialResult` ids move; 15 labels, 14,134 ids, every other per-label set identical | the same diff | exact set equality |
| Every edge count identical, including `RESULT_FOR_SITE` 1,362 and `WAS_GENERATED_BY` 1,362 | `store.count_edges` | exact integers |
| Refusals **27**, sites **2,029**, `Gene` 1,039, `ENCODES` 1,054 | the rebuild's report | exact integers |
| The five queries: `(0,1)`/`(0,2029)`/`(0,1362)`; 1,362 rows for `welch_t` and `NONE_FOUND` twice; one analysis at I15; `NOT_RETAINED`; 12 of 14 | the queries | exact |
| The collision separates after the amendment and collides before | two `evidence_id` calls each side | exact — two distinct digests |
| `tests/test_schema.py` fails on the §3 table before `schema.py` is amended | run it between the two edits | exact — the mirror check names the anchor |

**What would make this turn a failure rather than a decision.** Amending `schema.py` and
`ONTOLOGY.md` together so the mirror check never had the chance to fail, or reporting a green guard
without saying that nothing produces the case it guards.

#### Outcome, 2026-08-10 — every prediction held, and the amendment landed

| Prediction | Result |
|---|---|
| **1,362** ids move — every `DifferentialResult` and no other | **held** — `DifferentialResult: 1362 → 1362, left 1362, arrived 1362, unchanged 0` |
| **0** non-`DifferentialResult` ids move; 15 labels, 14,134 ids | **held** — 14 of 15 labels unmoved, totals identical |
| Every edge count identical | **held** |
| Refusals **27**, sites **2,029** | **held** |
| The five queries | **held** — `(0,1)`/`(0,2029)`/`(0,1362)`; 1,362 rows and `NONE_FOUND` twice; one analysis at I15; `NOT_RETAINED`; 12 of 14 |
| The collision separates after and collides before | **held** — `bzk:1529fff2…` twice before; `bzk:c5ab52d2…` and `bzk:8fdc78a9…` after |
| `tests/test_schema.py` fails between the two edits | **held**, and it failed **twice** — see below |

**The mirror failed in two directions, and the second was the more useful.** With §3 amended and
`schema.py` untouched, `test_schema_identity_matches_ontology_table` named the missing anchor:
`Extra items in the right set: ('DifferentialResult', 'ADJUSTED_BY')`. So did
`test_identity_table_matches_ddl` — but for a different reason, and it caught a mistake in the
amendment rather than the amendment's absence. **The first draft put the explanation inside §3's
anchors cell**, and that cell is parsed for backticked all-caps tokens; the prose contained
`` `MANY_ONE` ``, which the parser read as a relationship, and the guard fired with
*relationship(s) {'MANY_ONE'} cited without a node type*. That guard exists so *a bare edge name
cannot slip past the direction check*, and it worked on the first thing that tried it. The
explanation moved below the table, where §3's other notes live, and the cell carries citations only.

**Five mutations, each read back off disk before its run.** Removing the anchor → four
`test_keys.py` failures plus the mirror. Pointing it at `Analysis` instead → the same five, which is
the right answer: an anchor on the wrong label is not a weaker version of this one. Widening
`ADJUSTED_BY` to `MANY_MANY` → **two** failures, `test_the_self_anchor_depends_on_a_many_one_relationship`
and the DDL mirror, which is the load-bearing dependency made visible. Adding a **second**
self-anchor → **one** failure, the structural claim alone. Omitting a null anchor from the tuple
instead of rendering it → **one** failure, the test that explains why 1,362 ids moved. The last two
are the sharpest: each fires at exactly the assertion that names it.

**One new assertion matched the sweep and it is pinned, not withdrawn.**
`self_anchored == {'DifferentialResult': ['DifferentialResult']}` — a literal display against a value
computed from `schema.IDENTITY`, caught by Pass D because the call is in the binding rather than the
comparison. Made to fail by the second-self-anchor mutation. The other four guards' equalities do
not match the net: `adjusted_by.multiplicity == "MANY_ONE"` and `.pairs == (…)` compare an attribute
against a literal with no call on either side and no bare name, so neither pass reaches them. Floor
re-denominated **942 → 949**, same 27 modules.

**What this turn did not do.** No acyclicity check: a two-cycle and a self-loop validated before the
amendment and validate after, and the amendment makes them unkeyable rather than illegal. `schema.py`'s
`ADJUSTED_BY` multiplicity is untouched, as scoped — the amendment depends on it rather than forcing
it. And the guard is exercised only by a constructed pair, because no writer here emits `applied`.


### Pre-registration: guarding the three enumerations of ADR numbers, 2026-08-10

**Written and committed before any code.** Nothing is built but the guard. This turn touches no
writer, so `bzk rebuild` and the differential are run as a **state check** and nothing is predicted
to change.

#### Step 0 — four surfaces, three of them records

`decisions/README.md` § *Which is the enumeration that can rot* counts **three**, and the asymmetry
is worth stating rather than inferring: `ARCHITECTURE.md` §5's seed list, README's **Written** table
and README's **Queued** table are the three places a number is *recorded*; `decisions/` is the
**referent** those records are about, not a fourth record. A file cannot disagree with itself, so
the guard compares each record against the directory and against the others.

**§5 is narrower than it looks and one tempting relationship is not an invariant.** It holds
`0001`–`0018` and nothing beyond, because `0019`–`0025` were never seeded. So *every Written entry
appears in §5* is **false by construction** — measured: 7 records (`0019`–`0025`) are in the
directory and absent from §5 — and cannot be made an invariant. What §5 does support is its
*unstruck* set and its header's count claim.

**A struck seed line means written, and a struck description means something else.** `0007`'s line
strikes the number **and** its wording, because the seed was wrong and the record establishes which
of two accounts holds. The parser therefore reads the strike on the **number only**; a second strike
inside the prose is a correction mark and carries no membership meaning. Measured: 18 seed lines,
**17 struck**, **1 unstruck** (`0018`).

**Measured at this commit — five relationships hold and one does not.**

| Relationship | At `fdc8ef3` |
|---|---|
| Written numbers == directory numbers, both directions | **holds** — 24 and 24, symmetric difference empty |
| Every Written link resolves to a file | **holds** — 24 of 24 |
| §5's unstruck set == Queued | **holds** — `{0018}` both |
| Queued disjoint from Written | **holds** |
| §5's header *all but one are written* | **holds** — 18 seeds, exactly one (`0018`) absent from the directory |
| `Supersedes` reciprocal with `Superseded by` | **does not hold** — see Step 2 |

**What a zero licenses, stated in advance.** Both tables were reconciled **by hand** on 2026-08-09.
A clean first run is therefore evidence about *that reconciliation*, not about the class: it says the
hand-fix was correct and complete on the day, and says nothing about whether the enumerations stay
in step — which is the whole point of committing the check rather than repeating the audit.

#### Step 1 — where the guard lives, and its non-vacuity half

**A new module, `tests/test_decision_index.py`.** `tests/test_schema.py` is the precedent for a
document-versus-code mirror, and it is the wrong home here: its subject is the DDL, nothing in
`bzk/` reads `decisions/`, and adding a filesystem-and-Markdown check to it would make its own
docstring false. `tests/` is nonetheless the only executable surface this project has, and a check
that lives anywhere else is the procedure that does not re-run.

**The parser must be shown to find what it claims to parse.** A Markdown table drifts and a regex
that matches nothing passes by omission — the failure `tests/test_query_absence_coverage.py` was
built against. **This was hit while preparing the turn**: a first row-regex matched **zero** Written
rows against a table holding 24, and any comparison keyed off it would have been green. So each
parsed set has its **count pinned**, and the mutation set includes **emptying a table**, not only
corrupting a row.

#### Step 2 — the status convention, and the one relationship that does not hold

Measured now: **15 `Accepted`, 6 `Proposed` (`0006`, `0008`, `0009`, `0010`, `0012`, `0025`), 3
`Superseded` (`0007`, `0011`, `0014`)**; ADR-0025 landed `Proposed` last turn, so any earlier figure
is stale by one. Of the four candidate checks:

* **A status is one of the three named values** — writable, holds (0 outside the set).
* **A `Superseded` record names a successor that exists** — writable, holds 3 of 3.
* **`Supersedes` is reciprocal with `Superseded by`** — **writable, and it fails.** `0014` carries
  `Superseded by | ADR-0017`; `0017` carries `Supersedes | —`. One-sided, one instance.
* **The round-trip itself** — **readable here and not writable as a suite assertion**, established
  rather than asserted. Every one of the 24 has a first commit git can read, and the informative
  ones can be classified. But `tests/test_tautology_sweep.py` runs the **whole suite** inside a copy
  that excludes `.git`, and `git log` there returns *fatal: not a git repository* — so a
  git-dependent assertion would turn that module red for a reason unrelated to what it checks. The
  measurement is recorded in prose instead.

**The one-sided pair is not fixed by editing `0017`.** It is `Accepted`, and `decisions/README.md`
records that from 2026-08-07 the convention holds strictly — an Accepted ADR is amended only by a
superseding ADR. So the guard asserts the two directions that hold and pins the asymmetry as a
**named exception with its reason**, the `NOT_A_QUERY` shape: a *second* one-sided pair fails.

**Predictions.**

| Prediction | Instrument | Precision |
|---|---|---|
| **No id moves** — 15 labels, 14,134 ids, every per-label set and edge count identical | per-label id-set diff against a capture taken before the state check | exact set equality |
| `decisions/` holds **24** files; Written **24** rows; Queued **1** row; §5 **18** lines, 17 struck | the guard's own parsers | exact integers |
| Statuses: **15** `Accepted`, **6** `Proposed`, **3** `Superseded` | the guard | exact integers |
| Disagreement count on the five holding relationships: **0** | the guard | exact integer |
| Disagreement count on reciprocity: **1**, the pair `(0017, 0014)` | the guard | exact — the pair named |
| Refusals **27**, sites **2,029**, `DifferentialResult` **1,362** | the state check's own reports | exact integers |
| The five queries unchanged | the queries | exact |

**Mutation discipline, registered in advance.** Adding a file without a row, adding a row without a
file, moving a number between Queued and Written, **emptying** a table, and adding a second
one-sided supersession. The tautology shape is the specific risk — two sets derived from one parse
compare equal whatever the parse did — so every set is compared against a **pinned count** as well
as against its counterpart.

#### Outcome, 2026-08-10 — every prediction held, and the pinned count caught a defect in the guard

| Prediction | Result |
|---|---|
| No id moves — 15 labels, 14,134 ids, every per-label set and edge count identical | **held** |
| `decisions/` **24** files; Written **24**; Queued **1**; §5 **18** lines, **17** struck | **held**, all five |
| Statuses **15** `Accepted`, **6** `Proposed`, **3** `Superseded` | **held** |
| Disagreements on the five holding relationships: **0** | **held** |
| Disagreements on reciprocity: **1**, the pair `(0017, 0014)` | **held** — pinned as the one named exception |
| Refusals **27**, sites **2,029**, `DifferentialResult` **1,362** | **held** |
| The five queries unchanged | **held** |

**The pinned count earned itself before any mutation ran.** The first strike counter read
`sum(1 for _, struck in seeds)` — no condition — and counted all **18** seed lines against a pinned
**17**. It is the *assertion named a field it did not read* shape, in the very line written to
prevent a vacuous comparison, and nothing but the pinned integer would have caught it: the set
comparisons it guards were all green. That is the second time in this module's short life the
non-vacuity half fired on its own author, the first being the row-regex that matched zero rows
against a table of 24.

**Eight mutations, each read back off disk before its run, plus a ninth for the one direction the
eight did not reach.** A planted file with no row → 3 failures; a planted row with no file → 3; `0018`
moved Queued → Written → 3; the Written table emptied → 2; the seed list emptied → 3; a seed
un-struck → 2. Two fire at exactly one test each, which is the sharpest discrimination available
here: a **second one-sided supersession** (`0016` superseded by `0019`, with `0019` silent) and a
**one-character link break** on `0022`. The ninth covers `forward - backward`, which none of the
eight could reach — `0019 Supersedes ADR-0016` with `0016` saying nothing back gives
`{('0019', '0016')} == set()`.

**Thirteen new sweep matches, classified individually, none withdrawn.** Five are computed values
against pinned literals; five compare sets parsed from **different documents or the filesystem**;
one compares the two README tables; one is a computed list against `[]`. Only `forward`/`backward`
are drawn from a single parse, and they read two different header fields — both directions were made
to fail separately, which is what distinguishes them from the tautology shape. Floor re-denominated
**949 → 967**, **27 → 28** modules.

**One disagreement found, and not fixed.** `0014` carries `Superseded by | ADR-0017`; `0017` carries
`Supersedes | —`. The fact is recorded in three other places, so what is missing is the reciprocal
row rather than the decision — but `0017` is `Accepted`, and `decisions/README.md` records that
since 2026-08-07 an Accepted ADR is amended only by a superseding ADR. Editing it to make the guard
green would breach the convention the directory exists to keep, so the guard carries the asymmetry
as a named exception with its reason and fails on a second one. **Fixed nothing; pinned one.**

**Two things measured that the records had wrong, corrected rather than absorbed.** The bulk
*"Add files via upload"* set is **six** records (`0001`, `0002`, `0003`, `0015`, `0016`, `0017`), not
five; and re-measured at 24 records the informative population is **18**, of which **8** first appear
`Accepted`, 7 `Proposed` and 3 `Superseded`, against README's *nine of ten*. ADR-0022 remains the
only completed round-trip. Both figures were measured on 2026-08-09 at a smaller directory and are
replaced by the current measurement rather than diagnosed — what a different rule for *readable*
might have counted then is not recoverable from here.

**Two header shapes exist in `decisions/` and neither is a defect.** `0004` and `0013` carry no
`Superseded by` row at all, and `0013` uses `| Field | Value |` where the others use `| | |`. An
absent row means *not superseded*, which the guard reads correctly; a missing **Status** row would
fail, because that one is asserted present.


### Instruments the documents named that had no home, 2026-08-10

**No pre-registration: this turn writes no nodes and predicts nothing about the graph.** State
confirmed with the five checks only — a rebuild is not needed and none was run.

**The poller. Four recorded figures rested on an instrument that was not in the repository.**
`OPERATIONS.md` §5's 706-second window at 15-second spacing, `ROADMAP.md`'s 12× correction, the
second rehearsal's window and the third's 60-second samples. No `poll.sh`, no `scripts/`, no
`tools/` — each run rebuilt one from memory.

**Where it landed, and the reasoning is the whole of the decision.** Three shapes were weighed. A
root-level `scripts/` would falsify `ARCHITECTURE.md` §3's module tree, which enumerates that level,
and would raise a fourth lint target — a question `CLAUDE.md` point 1 governs with two precedents,
one widening and one permanent exclusion. A documented procedure in `OPERATIONS.md` costs nothing
structurally and guarantees nothing. **Neither was needed, because `bzk/drift.py` is the exact
precedent**: an operational instrument the platform does not import, living in `bzk/`, run as
`python -m bzk.drift`. So `bzk/fetch_progress.py` is a module beside it — already inside `ruff bzk`
and `mypy bzk`, so **no target widens and CLAUDE.md point 1 is not engaged**, and the module tree
gains one line rather than a directory.

**Nowhere was the third option and it was rejected on a cost that is now paid.** An instrument
reconstructed each time is not a defect if what it measures is recorded with its spacing — but the
same `pkill -f` self-match was written twice by the same process, and the fix is not a better
pattern. **`pkill -f` matches the full command line of every process, and the killer's own argv
contains the pattern**, so any pattern sufficient to find the poller is present in the process
searching for it. `--watch-pid` asks the kernel about one pid; there is no pattern to match.

**Unfalsified and incomplete, 2026-08-11 — the paragraph is right about the pattern and silent
about the pid.** `--watch-pid` takes a pid, and this turn's landing left **no document showing where
that pid comes from**: `HANDOFF.md`'s command block carried `--watch-pid $!` with no `&` anywhere
above it, so `$!` expanded from nothing. The complete three-line form existed only in
`bzk/fetch_progress.py`'s own docstring, which is the one place a reader following the command block
is not looking. *No pattern* is the right fix and it is not reachable by someone who cannot obtain
the pid — so the two occurrences on 2026-08-10 were **after** this paragraph, **after** the module,
and **after** `HANDOFF.md`:72 already named `--watch-pid`. That is what makes the missing `&`
load-bearing rather than cosmetic: the class recurred beside its own fix. Corrected in
`HANDOFF.md` §3, and `tests/test_command_blocks.py` now refuses a block that spends a variable it
never earns.

**Establishing what the three pollers measured was required before choosing, and it produced a
finding.** All three counted the same quantity — files arriving in `cache/uniprot/entry/` and
`cache/uniprot/seq/`. **What differs is the unit, and the conversion is stated nowhere beside the
figures**: the first reported *~1.0 s per accession*, the later two *0.50* and *0.47 s per round
trip*. With 2,260 entries and 3,013 sequences a cold run is 2.3332 trips per accession, so
1.0 / 2.3332 = 0.4286 — inside `OPERATIONS.md` §5's whole-run 0.40–0.44 s per fetch. The figures are
one measurement in two units, and a reader comparing them without the factor reads a 2.5×
disagreement that does not exist. The module prints both units on every line for that reason.

**Eight mutations, each read back off disk before its run.** Removing the watched-pid stop, the
backstop, the dead-pid branch, the spacing from the line, the previous-sample rate, the first-sample
guard, the per-accession unit, and summing the two tiers at the point of reading — each fails the
test that names it. **One fails by hanging rather than by going red**: with the backstop removed an
unwatched poller has no termination condition at all, so the call never returns and the suite stops
instead of failing. Measured at 45 s under the harness, and recorded in the test that owns it rather
than softened with an in-process watchdog.

**The commands, and the decision is not the one the framing suggested.** `pyproject.toml` declares
no `[project.scripts]`, so `bzk rebuild` and `bzk drift` are not installed names. The shorthand
appears in **37 places** across the document set, which reframes it: they are used as *names for two
operations*, not as command lines, and rewriting 37 sentences into `python -m bzk.rebuild` would
make the prose worse without making it truer. **Declaring console scripts was rejected** because
`bzk rebuild` with a space is not a script name — it is a `bzk` executable with a subcommand
dispatcher, a CLI this project has never had, that no run on record used, and that would change what
an install produces to make sentences true about something never executed. So §5 declares the
shorthand at its head, states the invocations, and **says what the decision costs**: a reader meeting
one of the 37 without that paragraph can still type a command that does not exist. `:224` and `:279`
carry the invocation inline as well.

**It does not reach the three bare-`python` lines** at `HANDOFF.md`:241, :316 and :392. Those are
about *which interpreter* — `python` against `.venv/bin/python` — and are separately named; this is
about whether the name exists at all. Stated rather than swept in.

**One of the two cited failure modes has no record in the repository, and this turn transcribes it
rather than relocating it.** The `pkill` self-match is in `ROADMAP.md` twice and `HANDOFF.md` once.
The stale-monitor echoes — a completed background run notifying twice through monitors still armed —
appear in no document; they are from the session transcripts. Recorded here as transcription, which
is a weaker provenance than everything around it.

**That sentence counts *homes*, and the quantity amended below is *occurrences* — 2026-08-11.** Three
homes was right and is still right: two passages in this file and one in `HANDOFF.md`. What no home
carried is how many times the failure has happened, and the two numbers were never the same one.
See § *The missing `&`*.

**No sweep matches were added.** The surface grew to 29 modules and 986 asserts and the match set did
not move: every equality in the new module compares against a literal display, which Pass C excludes
by construction. The floor moved 28/967 → 29/986 by hand, and that a growing surface added zero
matches is exactly what the floor exists to keep visible, since the multiset alone would have said
nothing. **File counts in three checks moved**, as expected of a committed module: `ruff` and `mypy`
now cover **75** source files against 73, and the suite is **460** tests against 449.


### Pre-registration: ADR-0025's acyclicity gap, what it actually is, 2026-08-10

**Written and committed before any code.** This turn writes no nodes.

**The state at this session's open, performed here rather than inherited.** Baseline id set captured
before the rebuild dropped it: **15 labels, 14,134 ids**, `DifferentialResult` 1,362, every edge
count recorded. The five checks and the two commands are run in this session; if it compacts
mid-turn the open is re-run and said so, because the last compaction cost exactly that.

#### What is already established and is not re-derived

`keys.evidence_id` takes `anchor_ids` as an argument and resolves nothing, so there is no recursion,
no hang and no write. Driving a cyclic pair at it produces a real id —
`bzk:9b76e0c5b4702a56c1351a4e05bad5a7`, with `@DifferentialResult=␀null` in the tuple — because
`keys.py`:299–300 permits absent anchors outright: *not every anchor applies to every instance*.

**So three documents are imprecise in the same way**, and none of them cites that clause.
`decisions/0025`:57–62, `ROADMAP.md`:2853–2856 and `ONTOLOGY.md`:91 all say `evidence_id` **cannot
produce** a cycle. It can produce an id for a member of one. What it cannot produce is the
**cyclically-determined** id, because the caller cannot supply the anchor — so the impossibility is
the **producer's**, which is exactly where `ONTOLOGY.md`:91 already puts the ordering obligation two
sentences earlier. The correction is to make the three homes say what that sentence says.

#### Step 0 — what the null-anchor path costs, predicted before it is run

The live question is no longer the cycle. It is that **a caller who does not supply the self-anchor
gets a silent id**, indistinguishable at the point of minting from a legitimately absent anchor — a
result that measures a protein and so has no site, or the reverse.

**Predicted, from reading the two checks and before constructing anything:**

| Prediction | Instrument | Precision |
|---|---|---|
| **No id moves** — 15 labels, 14,134 ids, every per-label set and edge count identical | per-label id-set diff against the capture taken before the rebuild | exact set equality |
| The null-anchor case is **not distinguishable** by any existing check | constructed change-sets through `invariants.validate` | pass/fail per case |
| I4 refuses `applied` with **no** `ADJUSTED_BY` edge | `validate(..., only="I4")` | the error names I4 |
| I4 **accepts** `applied` whose id was minted with a null self-anchor, provided the edge is present — because I4 reads the edge and never the id | the same | validates |
| I20 is silent on it: it counts `RESULT_FOR_*` and not `ADJUSTED_BY` | `validate(..., only="I20")` | validates |
| **Two corrected results against different baselines, both minted with a null anchor, collide** — ADR-0025's own collision, reopened by the null path | two `evidence_id` calls | one digest, twice |
| The 2-cycle validates end to end, both members `applied`, each carrying an edge | `invariants.validate` | validates |
| Refusals **27**, sites **2,029**, `DifferentialResult` **1,362** | the two commands' reports | exact integers |

**What a *not distinguishable* answer licenses, stated in advance.** It would mean the identity and
the edges can disagree with nothing noticing: the id says *no baseline*, the edge says *baseline X*.
Nothing in this repository recomputes an id from a stored change-set, so that disagreement is
invisible by construction rather than by omission — and the collision ADR-0025 was written to close
returns through the null door.

#### Step 1 — the decision this turn owes, and it may be *nothing is minted*

Three things bear on it and all three are already on record. No writer emits `applied` —
`analysis/differential.py` fixes `protein_adjusted='not_applied'`, so the path is unreachable today.
`schema.py`'s `MANY_ONE` already refuses two baselines on one result. And I4 may already refuse the
sharpest sub-case. **If the honest answer is that no invariant is warranted, that is the answer and
it is recorded** — but the three documents' wording is corrected either way, because it is a claim
about the code that the code does not support.

**If a guard is warranted, which layer it fires at is established before it is written.** ADR-0019's
structural validation raises before `store`, and a guard was withdrawn here once for failing at the
wrong layer. Any guard would be exercised only by constructed cases, as I20's and ADR-0025's are.

**Out of scope and named:** `ADJUSTED_BY`'s multiplicity, protein-grain results, and a general cycle
check over other edges — if the reasoning raises the last, it is reported and not built.

#### Step 1 pre-registration — a guard is warranted, and it is not the acyclicity check

**Written and committed after step 0's measurements and before any code.** Step 0 answered *not
distinguishable* on every count, so the gate opened; what follows is registered before the checker
exists, because step 1's own shape was only decidable once step 0 had run.

**The guard is an identity check, not a cycle check, and that is the finding.** *An `ADJUSTED_BY`
edge obliges the source's id to encode its target* — recompute the id from the node's identifying
fields and the anchor ids its own change-set names, and require equality. **Acyclicity falls out of
it**: a cycle needs each id to encode the other's, which needs `sha256` to determine its own input,
measured in step 0 to have no fixed point in 12 iterations. So the invariant the record contemplated
is subsumed by a narrower one, and no cycle check is written.

**Two shapes were measured against each other before choosing, because the weaker one is tempting.**
A *weak* form — *the id must not be the one it would have with no baseline* — closes the null door
and nothing else. Measured: a two-cycle assembled from two ids each minted honestly against some
**third** baseline, then cross-linked, **passes the weak form and is refused by the strong form at
both ends** (`bzk:4dab180e…`, `bzk:2e3ceb59…`). The weak form was rejected on that measurement.

**The strong form unscoped refuses the valid fixture, measured rather than discovered later.**
`bzk:dr1` is a hand-written mnemonic and recomputes to `bzk:3f1d92bfc9477eb7adb5e0c6b3df70f8`;
`bzk:dr1` also appears in ten hand-written change-sets in `tests/test_invariants.py`. So the check is
scoped to ids that **claim** to be digests — `bzk:` + `keys.DIGEST_HEX` lowercase hex — and a
hand-written id stays outside it, which is exactly the fixture route ADR-0025 already records as the
one that survives. That scope is a real limit and is stated in §8 rather than left to be found.

| Prediction | Instrument | Precision |
|---|---|---|
| A correction whose id was minted with a **null** self-anchor is refused, naming **I21** | `validate(..., only="I21")` over a constructed change-set | the error's first field is `I21` |
| The same change-set **validates** under another invariant, so the refusal is I21's and not structural validation's | `validate(..., only="I2")` on the identical input | validates |
| A correction whose id **does** name its baseline validates | the same | validates |
| A two-cycle built from ids minted against other baselines is refused at the **first** member reached | the same | the error names `I21` |
| A hand-written id (`bzk:dr1`) carrying an `ADJUSTED_BY` edge is **ignored** | the same | validates |
| A result with **no** `ADJUSTED_BY` edge is ignored — the shape all 1,362 shipped results have | the same | validates |
| Removing `"I21": _check_I21` from `_CHECKS` fails **exactly 6** tests and nothing else | mutation in a copy, read back off disk before the run | exact count, exact names |
| Scoping dropped (every id checked) fails the two tests that depend on the scope | the same | exact count |
| Recomputing with the self-anchor forced to `None` — the bug itself — fails the refusal test **and** the acceptance test | the same | exact count |
| **No id moves**: 15 labels, 14,134 ids, every per-label set and edge count identical | per-label id-set diff against `open_before.json` | exact set equality |
| The five checks stay clean; the suite grows by the new tests only | `pytest`, `ruff`, `mypy` | exact counts |

**What it will not cover, registered now so a pass cannot be misread.** Nothing in this repository
produces the case: no writer emits `protein_adjusted='applied'`, all 1,362 shipped results are
`not_applied` and none carries an `ADJUSTED_BY` edge, so **it is exercised only by constructed
cases**, exactly as I20's and ADR-0025's own guard are. A green suite says the checker separates a
correction from its baseline, not that any correction exists. And the check reads anchor ids from
the change-set's own edges, so it obliges a change-set carrying an `ADJUSTED_BY` edge to carry that
result's other anchor edges too — an obligation ADR-0019's self-containment already implies and I20
already imposes for `RESULT_FOR_*`, stated because it is new for the other three.


### The gap was never the cycle — I21, and four homes corrected, 2026-08-10

**Every step-0 prediction held, and the answer they add up to is that ADR-0025 closed its own
collision only for producers that chose to co-operate.**

| Prediction | Outcome |
|---|---|
| The null-anchor case is **not distinguishable** by any existing check | **held** — I4, I20 and ADR-0019's structural validation all validate it |
| I4 refuses `applied` with **no** `ADJUSTED_BY` edge | **held** — `InvariantError: I4` |
| I4 **accepts** `applied` whose id was minted with a null self-anchor, the edge present | **held** — it reads the edge, never the id |
| I20 is silent on it | **held** — it counts `RESULT_FOR_*` |
| **Two corrections against different baselines, both minted with a null anchor, collide** | **held** — both `bzk:3473130e9cb7f1198196ee40b0e30727`; supply the anchor and they separate |
| The 2-cycle validates end to end | **held** |
| No id moves; refusals 27, sites 2,029, results 1,362 | **held** — 15 labels, 14,134 ids, symmetric difference **0** on every label and every edge count identical to the capture taken before the rebuild dropped it, over `python -m bzk.rebuild` then `python -m bzk.sources.pxd018299_differential` |
| The five checks stay clean; the suite grows by the new tests only | **held** — 468 tests against 460, **75** source files unchanged because no module was added |

**The tuple line is the whole finding in one row.** A null self-anchor renders
`@DifferentialResult=␀null` — character for character what a legitimately absent
`@ProteinObservation` renders — so the disagreement between an id that says *no baseline* and an
edge that says *baseline X* is invisible at every layer, by construction rather than by omission.
Nothing in this repository recomputes an id from a stored change-set. Now one thing does.

**The decision: a guard is warranted, and it is not the acyclicity check the record contemplated.**
I21 — *an `ADJUSTED_BY` edge obliges the source's id to encode its target*. Acyclicity is subsumed:
a cycle needs each id to encode the other's, which needs `sha256` to determine its own input.
Measured rather than argued — the corrected result **recomputes exactly** from its own anchors, and
a cycle has **no fixed point in 12 iterations**. So the suggestion the reasoning raised — a general
acyclicity invariant — is reported here and was **not built**, because a narrower check already
implies it.

**The weak form was measured against the strong one and rejected on the measurement.** *The id must
differ from its no-baseline form* closes the null door and nothing else: two ids minted honestly
against a **third** baseline each, then cross-linked into a two-cycle (`bzk:4dab180e…`,
`bzk:2e3ceb59…`), **pass** it. I21 refuses them at both ends. That case is why I21 recomputes.

**The scope is a real limit and was found by measurement, not by argument.** Unscoped, the strong
form **refuses the valid fixture**: `bzk:dr1` is a hand-written mnemonic and recomputes to
`bzk:3f1d92bfc9477eb7adb5e0c6b3df70f8`. **The step-1 pre-registration said *ten hand-written
change-sets besides* and that figure was not measured when it was written; counted, it is six** —
six change-sets in `tests/test_invariants.py` mint a `DifferentialResult` with that id, and the
fixture carries four `bzk:dr*` results of which one is corrected. The direction of the finding is
unchanged and the number was wrong, which is why it is corrected here rather than quietly. So I21
governs ids that *claim* to be digests — `bzk:` + `keys.DIGEST_HEX` hex, a claim and never a proof —
and a hand-written id stays outside it. That leaves the fixture route exactly as ADR-0025 already
records it, and **no fixture or test change-set was re-keyed**.

**Eight tests, not the six registered, and the two extra are the ones that would have been missed.**
The layer question is asserted rather than assumed: the same change-set that I21 refuses
**validates** under `validate(..., only="I2")`, which runs ADR-0019 first, so the refusal is I21's
own — the check that would have caught the assertion withdrawn on 2026-08-10 for failing at the
wrong layer. The second addition is **reachability**, and it was found by asking what `only="I21"`
cannot establish: all six registered cases target the checker directly, and a checker registered in
`_CHECKS` and never reached would pass every one of them. On a hand-built change-set the full
`validate` raises **I3** first — a `SiteObservation` with no `ModifierAssignment` — so the fixture is
the instrument: re-keyed through the null door it is refused by the full `validate` at I21 and by
nothing else, and re-keyed to the id that *does* name its baseline it validates. The digest is the
difference, not the re-keying.

**Four mutations, each read back off disk before its run, each over the whole suite.**

| Mutation | Result |
|---|---|
| **A** — `"I21": _check_I21` removed from `_CHECKS` | **9 failed, 459 passed.** Seven of the eight I21 tests, `test_valid_changeset_passes_every_check`, and the sweep. Registered as **6**; the miss is the same one I20's turn made — `validate(..., only="I21")` raises `ValueError` on an unknown invariant, so every *accepting* case fails too, not just the refusing ones |
| **B** — the digest scope dropped, every id held to a recomputation | **4 failed.** `test_valid_changeset_passes_every_check`, `test_I21_leaves_a_hand_written_id_alone`, **`test_adapters_base.py::test_parsed_observations_validate_as_a_changeset`**, and the sweep |
| **C** — the recomputation itself omits the self-anchor: the bug the guard exists to catch | **5 failed.** The refusal, layer, acceptance and full-`validate` cases, and the sweep |
| **D** — `is_digest_id` accepts anything beginning `bzk:` | **4 failed**, the identical set to B |

**Three things the mutations established that the tests alone did not.** **B named a third consumer
of the fixture**: `_ReplayAdapter` in `tests/test_adapters_base.py` parses `valid_changeset.json` and
hands it to `validate`, so the fixture's hand-written `bzk:dr1` reaches I21 by a path neither the
fixture test nor the scope test goes through. Dropping the scope reddens all three, which is the
measurement behind *no fixture was re-keyed* rather than an assurance about one file. **C is caught
by the acceptance case, not the refusal case** — with the anchor omitted from the recomputation the
crossed cycle is still refused, for the right outcome by the wrong computation, and only
*accepts-a-correction-whose-id-names-its-baseline* goes red. A guard tested by refusals alone would
have survived it. And **the eighth test correctly does not move under A**: the anchor-direction case
reads `_RESULT_ANCHORS`, not the registry, so a mutation to the registry has nothing to say to it.

**The sweep's `test_every_classified_instance_re_runs_its_recorded_evidence` fails in all four and
is not four catches.** It re-runs the suite over its recorded evidence, so it is red whenever the
suite is red. It is listed because omitting it would make the counts unreproducible.

**One tautology was written and caught in the same turn, by this repository's own sweep.** The
anchor-direction test first asserted `set(_RESULT_ANCHORS) == set(schema.IDENTITY['Differential\
Result'].anchors)`. `_RESULT_ANCHORS` **is** that expression, so the assertion compared a value to
itself, and `tests/test_tautology_sweep.py` matched it on the first run. It was removed rather than
pinned; the count and the direction remain, and they are not tautologies. That is the sweep catching
new code rather than the audit that created it, which had not happened before.

**What this did not cover, stated rather than implied.** It is exercised **only by constructed
cases** — no writer emits `protein_adjusted='applied'`, all 1,362 shipped results are `not_applied`
and none carries the edge — so a green suite says the checker separates a correction from its
baseline, never that any correction exists. And it obliges a change-set carrying an `ADJUSTED_BY`
edge to carry the result's other anchor edges too; ADR-0019's self-containment already implies that
and I20 already imposes it for `RESULT_FOR_*`, but it is new for `WAS_GENERATED_BY` and
`RESULT_IN_CONTRAST`.

**I21 is an instance of a class — *an id must encode its anchors* — and the class is not closed.
Whether it *can* be closed was measured rather than asserted, because a note is not allowed to
stand in for a guard that is writable.** `store.py`:120 is the single funnel every write passes, so
wrapping `invariants.validate` there counts the real population. Over `bzk rebuild` and the
differential, digest-shaped nodes staged **without every anchor edge their id was minted from**:

| Label | staged | short of an anchor edge |
|---|---|---|
| `SiteObservation` | 7,449 | **1,362** — no `Dataset`, no `ModificationSite` in that change-set |
| `ModifierAssignment` | 7,449 | **7,449** |
| `Sample` | 72 | **36** — no `Experiment` |
| `DifferentialResult` | 1,362 | 1,362, but **only of anchors that do not apply** — `ProteinObservation` at site grain, and no baseline |
| `Analysis`, `Experiment`, `Imputation` | 7 / 3 / 1 | 0 |

**So the general check is not writable today, and the reason is structural rather than
effortful.** ADR-0019 permits a node to be **re-staged as a referent** — `_check_I14` says so in
code, *"No edges in this batch is not a violation"* — and the ingestion actually does it, 1,398
times for `SiteObservation` and `Sample` alone. A rule that every digest-shaped id must recompute
would refuse every one of them, so closing this class means changing the change-set contract, not
adding an assertion. **I21 escapes precisely because its trigger is the edge and not the node**: a
change-set that emits `ADJUSTED_BY` is producing the relationship, which is the one moment the
baseline is known to be present. That is the measurement that makes the scope a design decision
rather than an omission, and it is recorded here rather than as a `HANDOFF.md` §8 note, because a
note would imply an assertion someone merely has not written yet.

**Four homes carried the imprecise sentence and none of them cited the clause that makes it false.**
`decisions/0025`:57–62, `ROADMAP.md`:2853–2856, `ONTOLOGY.md`:91 and — found while correcting them —
`ONTOLOGY.md` §11 Q7's own closing note, which repeated it in the very entry that recorded the
collision. All four are corrected in place with the original struck. `keys.identity_tuple`'s *absent
anchors are permitted* now names I21, so the clause and the invariant that depends on it are no
longer one-way. **The ADR edit is an ordinary one, not a supersession**: `decisions/README.md` binds
append-only to `Accepted` and ADR-0025 is `Proposed`. That it is Proposed is the only reason — had
it been Accepted this would have been ADR-0026 to fix a sentence in an unratified record.


### The missing `&` — a fix nobody could reach, and the occurrence count, 2026-08-11

**No pre-registration and no nodes written.** Confirmed with the five checks; a rebuild is not
needed, because nothing here touches the graph, the schema or any key.

**The defect is one character, and it sat between a fix and its reader.** `HANDOFF.md`'s command
block listed `.venv/bin/python -m bzk.rebuild` with no background operator and then, six lines
later, `.venv/bin/python -m bzk.fetch_progress --watch-pid $!`. `$!` expands to the pid of the last
backgrounded job; the block backgrounds nothing, so read as a stranger would, **the pid comes from
nowhere**. The complete three-line form existed — in `bzk/fetch_progress.py`'s own docstring, which
is exactly where a reader following the command block is not looking. Corrected: the poller now
leaves the sequential list, which it never belonged in (it runs *beside* the rebuild, not after the
differential), and appears as the same three lines the module carries.

#### The occurrence count, and it is a different quantity from the one already recorded

**§ *Instruments the documents named* counts homes — three, and that is still right.** What no home
carried is how many times the failure has *happened*. **Four**, and they do not have equal
provenance, so they are listed with it rather than summed:

| # | When | Provenance |
|---|---|---|
| 1 | the second cold rehearsal, 2026-08-09 | on the record — `ROADMAP.md` § *Cold to cold* by back-reference, `HANDOFF.md` §3 |
| 2 | the third cold rehearsal, 2026-08-10 | on the record — `ROADMAP.md`:2775–2779, with the exact `pkill -f "cold3/poll.sh"` |
| 3 | the I21 turn, stopping a mutation run — `pkill -f "mutate21.py"` | **transcription from the session**, no artefact in the tree |
| 4 | the I21 turn, stopping it again — a `ps \| grep \| kill` pipeline, not `pkill` | **transcription from the session**, no artefact in the tree |

Rows 3 and 4 follow the provenance discipline § *Instruments the documents named* already applies to
the stale-monitor echoes: they are from the session transcripts, recorded as transcription, which is
weaker than everything around them. **Row 4 is the more useful of the two**, because it did not use
`pkill` at all: it derived pids from a `ps`/`grep` pipeline and still took the wrapper down with the
same exit 144. Pattern-derived process selection wearing a `kill`-by-pid costume is the same failure,
which is the strongest available support for *the fix is not a better pattern but no pattern*.

**The fact worth recording is not that the class recurred but that it recurred beside its fix.**
Rows 3 and 4 are dated **after** `bzk/fetch_progress.py` landed, **after** § *Instruments the
documents named* argued the pattern point, and **after** `HANDOFF.md`:72 already named
`--watch-pid`. A termination fix that the reader cannot reach is not a fix in force, and the reason
it could not be reached was the missing `&`. That is what makes the character load-bearing rather
than cosmetic.

#### Every command block, and whether it is complete as written

The enumeration was **mechanical first and read by hand after**, because seven turns of short
enumerations is the reason the instruction said *treat this as a minimum*. **27 fenced blocks across
the eleven documents, 7 of them command blocks**; scanning for a shell variable spent and never
earned returned **exactly one** — `HANDOFF.md`'s. Then each was read:

| Block | Status |
|---|---|
| `HANDOFF.md`:64–73, the end-to-end list | **was the defect**; corrected, and the poller moved out of the sequence |
| `HANDOFF.md`:79–83, the poller's three lines | **new here**, and complete — it is the module docstring's form verbatim |
| `HANDOFF.md`:27–32, `git clone <your repo>` + `uv init` | **assumes something the reader supplies, and marks it.** `<your repo>` is an explicit placeholder, and the block is *history* — `uv init` created this repository rather than installing it, which `OPERATIONS.md` §4.1 already says |
| `HANDOFF.md`:36–47, the dependency list | **not a command block.** It is package names; a classifier keying on the first word alone calls `pytest` and `streamlit` commands, which is a false positive the guard's argument-or-path rule exists to prevent |
| `OPERATIONS.md`:184–186, `uv sync --frozen` | **complete** |
| `OPERATIONS.md`:196–198, the two `streamlit` flags | **complete, with one condition stated beside it and not in it** — the relative path means it only works from the repository root, which §4.1's prose says explicitly |
| `OPERATIONS.md`:220–223, the two `python -m` forms | **complete** |

**Three cited sites are not command blocks at all, and that is the finding about them.**
`OPERATIONS.md`:244 and `ROADMAP.md`:2689 both name `python -m bzk.fetch_progress` **in prose, with
no invocation** — they cite the instrument for the figures it produced, which is a citation and not
an instruction, but it means **`OPERATIONS.md` §4.1 does not share `HANDOFF.md`'s gap for the reason
that it has no poller invocation at all**: the document that owns the install and the cold-rebuild
figures never shows the command that produced them. `ARCHITECTURE.md`:94 is a line in the module
map — it names `--watch-pid` accurately and does not purport to be runnable. None of the three is
edited; a module map and a figure's citation are not procedures.

#### The guard, and what defeats a stronger one

**It is writable, so it is written** rather than noted: `tests/test_command_blocks.py`, with
`tests/test_decision_index.py` as the precedent for a test that reads documents. *A block spends a
shell variable nothing in the block earns* is decidable from the text — a use is `$NAME`/`${NAME}`/
`$!`, a producer is an assignment, a `for`, a `read`, or, for `$!` alone, a background operator
earlier in the block. **What defeats a stronger version is stated rather than asserted**: *is this
command runnable* is not textual. A block can name a path that does not exist, a flag since renamed,
or a working directory it never states — `OPERATIONS.md`:196–198 is exactly that case, and its
condition lives in the prose beside it. So the guard asserts the one property that is textual.

**Two of its own defects were found by making it fail rather than by review.** The first draft did
not treat `&` as an assignment separator and reported the **corrected** block as broken — a guard
firing at the wrong thing, caught because a failure was expected not to arrive. The second
classified the dependency listing as commands, because the first word of `pytest` is `pytest`; the
argument-or-path rule fixes it and both negative cases are asserted.

**Five mutations, each read back off disk before its run.**

| Mutation | Result |
|---|---|
| **A** — `HANDOFF.md`'s block reverted to the form committed at `6dcbd97` | **4 failed, 468 passed** over the whole suite: the main assertion, the mirror against the module docstring, the coverage case, and the sweep's evidence re-run |
| **B** — `&&` counted as a background operator | **1 failed** — the non-vacuity case. This is the mutation that matters most, because treating `&&` as a fork would let the original defect pass anywhere a `&&` appeared above it |
| **C** — `&` dropped from the assignment separators | **2 failed** — and this is the first draft's own bug, reproduced deliberately: the *corrected* block reports a gap |
| **D** — the argument-or-path requirement dropped | **1 failed** — the coverage case, on its two negative assertions; `pytest` and `streamlit` in the dependency listing become commands |
| **E** — the classifier recognises nothing | **2 failed** — and **not** the main assertion, which passes over an empty list. That is the measurement behind the sweep classification of `gaps == []`: its non-vacuity is carried by the other two cases and not by itself |

**A's fourth failure is the sweep and it is not a fourth catch** — `test_every_classified_instance_
re_runs_its_recorded_evidence` re-runs the suite, so it is red whenever the suite is red. Listed so
the count reproduces. **Sweep: floor 993 → 1007 asserts and 29 → 30 modules; one new match,
`gaps == []`, classified individually and pinned by hand with E as its evidence.**


### The v0.1 boundary redrawn on dependency, and a stop that left no trace, 2026-08-11

**No prediction is registered and none should be.** This turn produces no measured quantity — it
sorts a table and writes prose — so § *Pre-registration* has nothing to bind, and manufacturing a
prediction to satisfy the form would be the failure that section exists to prevent. Every figure
quoted below is carried from an existing record and named at its source rather than re-measured.

#### The stop that left no trace, and why that was the larger of two failures

**A previous turn was refused a `refs/tags/*` push and wrote nothing to disk.** The 403 is real and
is now recorded — `OPERATIONS.md` §1.2, chosen over three other candidate homes because §1 is
authoritative for what survives and §1.1 is the exact precedent: a durability section discovering it
had no row for *which name*. `HANDOFF.md` §2 and §8 were rejected despite §8's `Blocking?` column
fitting the fact well, because that file's own header says it is authoritative for nothing and
should be deleted once the adapters exist, and a durability fact outliving the file that holds it is
the same defect one level out. §4.1 was rejected as an install procedure, which this is not.

**The second failure was treating the tag as a precondition.** Nothing in this repository made it
one: `grep -rn "demo-verified\|git tag\|annotated tag\|refs/tags" --include=*.md .` returns **zero
hits**, run at `7b9559a`. What a tag adds over a commit hash is a *name*, not persistence — the
commit is reachable from two refs on the remote and outlives any container regardless. A stop that
lives only in a chat transcript is in precisely the position the tag was in: real, and gone with the
container. **The repository's own standard for irreplaceable content is version control**, and a
reason not to proceed is content.

#### What moved, and the three rules that decided it

Two rows left v0.1 — `perseus_s0`, and the Perseus adapter's *real-export* milestone as distinct
from its module — and one build target followed the second. **Nothing came forward.**

That last is the result worth stating. `moderated_t_ebayes` was the one genuine candidate: it needs
nobody, its machinery exists, and I16 makes a second test a second `Analysis`. It stayed deferred
because **he could say to match Perseus first**, which is ADR-0015's own reasoning, and a row the
meeting could change does not come forward. **The axis is asymmetric on purpose** — a wrongly
deferred independent row costs a release that is smaller than it needed to be, while a wrongly
retained dependent row costs a release that cannot ship at all.

**Two rows were blocked and stayed, which is the rule that did the most work.** The protein-groups
ingestion and I11's protein half are stuck on a curation record for the proteome run. It would have
been easy to call that his and move both, and an uncitable dependency leaves a row where it is.

**The rows still stay and the reason given here was wrong — corrected 2026-08-12, in the in-scope
row and not restated here.** This paragraph said nobody had checked the deposit; this document had
checked it twice, once in the survey above and once in the paragraph this one already cited. It
also demanded an *authoritative* basis while pointing at deposit metadata, which §5.3 marks
`inferred` — and the curation record already in the graph is `inferred` itself.

#### The one-dataset clause, confronted rather than worked around

`One ingestion path, one dataset, one statistical test` was contradicted by this document before any
redraw touched it: § *Weeks 3–4* requires a second dataset and calls that the first genuinely useful
milestone, and § *Weeks 7–8* requires an answer across *all my datasets*. It is amended. **The
amendment claims less than the exit it unblocks** — *ingested, resolved, stored* is reached by any
second deposit and needs nobody; *cross-queried* remains blocked on `ONTOLOGY.md` §11 Q1, which is a
modelling question inside this repository and is **not settled here**.

#### ADR-0015, and the handover question

**0015 stands unamended, and not because that is cheaper.** `CLAUDE.md` puts scope in this document,
so a release claim inside an ADR would be a second home for a fact this table owns.
`ARCHITECTURE.md` §4's registry table already routes the question here in the one cell that carried a
release marker — and **that cell was itself the duplication**, so the marker moved out of all three
cells into a cross-reference rather than being copied into two more.

**The handover question does not block the redraw, and the reading that said it did is wrong.** Both
branches were run: under *Perseus results* and under *search-engine output* alike, the Perseus
adapter needs a table only he has. A row dependent under both branches is not made more or less
dependent by the answer. What the question actually bears on — whether the raw matrix is essential
or merely prudent, whether B was over-engineered — is **retrospective**: ADR-0017 is `Accepted`, both
paths are on disk, and an answer arriving now can evaluate that decision but cannot reverse it.


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

### Pre-registration: criteria for a second deposit, 2026-08-12

**Written and committed before any candidate was inspected.** The section below this one is the
2026-08-07 survey of *one* deposit; this registers how a *second* is chosen, and the shortlist that
results lands beneath it as a sibling section, so the two surveys sit together and the criteria are
readable against the findings they were written to test.

**Three indices were measured reachable from this container first, because none of this is possible
otherwise.** `https://ftp.pride.ebi.ac.uk/pride/data/archive/2022/02/PXD018299/` → 200;
`https://www.ebi.ac.uk/pride/ws/archive/v3/search/projects` → 200 with a JSON body;
`https://proteomecentral.proteomexchange.org/api/proxi/v0.1/datasets` → 200. `bzk/sources/pride.py`
itself cannot find a deposit — checked structurally rather than by grepping for *search*: an AST walk
shows exactly **two** `DepositFile` constants, one URL template built wholly from their fields, and
`fetch(deposit)` taking a `DepositFile`. There is no function that accepts a query or returns a list,
so a deposit the module has not been told about has no URL to build.

**One candidate was seen before these criteria were written and it is disclosed rather than
quietly used.** Verifying that the search API's 200 carried a usable body returned the first record
of an `ISG15` query — `PXD071724`, DIA-NN. No criterion below was shaped by it, and it is admitted
to the survey on the same terms as every other candidate; a reader who suspects otherwise can check
that C0(d) excludes DIA-NN and was not written to spare it.

#### The point of the axis: contrast, not resemblance

**A deposit resembling PXD018299 in these respects is the weaker choice, not the stronger one.**
Every figure below was induced from a single deposit inspected on 2026-08-06. A second deposit that
reproduces them adds a second observation of the same thing; one that *differs* tells us which of
them were properties of the model and which were properties of that file. The survey therefore ranks
on **how many of these a candidate could falsify**, and a candidate that would confirm all of them
ranks last.

#### C0 — admissibility, hard gates; any failure excludes and is recorded

| # | Gate | Why |
|---|---|---|
| a | **Public, not embargoed** | ADR-0016's embargo fields exist and no v0.1 row populates them; an embargoed deposit is out and this turn does not change that |
| b | **Reuse terms establishable from the deposit's own metadata** | If they cannot be established, the candidate is excluded *and the exclusion is recorded as unestablished* rather than assumed permissive |
| c | **Carries a site-grain processed table** | The v0.1 path is the MaxQuant site adapter; a protein-only deposit tests nothing at the grain the anchor domain lives at |
| d | **MaxQuant** | The two written adapters are MaxQuant; DIA-NN, FragPipe and Spectronaut are v0.2 by § *Explicitly deferred*. A non-MaxQuant deposit is excluded **for this survey only** and recorded with its engine |
| e | **A proteome UniProt can resolve** | Position validation and I2's sequence pinning both run through UniProt; a species it cannot resolve makes every rate unmeasurable |

**C0(d)'s reading rule, settled — 2026-08-12, committed before any count was recomputed under it.**
The gate above is **unedited and nothing in it is struck**: it names no signal, so it was
underdetermined rather than wrong, and there is nothing in its text to withdraw. What is amended is
the *reading rule*, which was never written down and was adopted in practice by § *Widened draw*
**after** the two signals were seen to disagree on `PXD074126`. The pre-amendment rule, left standing
and struck:

~~**Either signal admits.** A deposit is MaxQuant for C0(d) if the filename route says so **or** the
declared `softwares` list does.~~

**Amended — the filename route decides; the declared list corroborates, and can neither admit nor
veto.** Three clauses, because each answers a different failure:

1. **`engines` decides.** C0(d) asks whether a written adapter can read the deposit's site-grain
   table, and an adapter consumes a file. A project-level `softwares` list does not say which tool
   produced which file, so it cannot answer that question and must not admit on its own.
2. **The declared list is recorded and reported for every row it exists on**, never discarded. It is
   evidence about the deposit and it is the signal that exposed the matcher gap below.
3. **An unstated `softwares` list is *not stated*, not *not MaxQuant*, and never vetoes.** This
   repository already models that distinction — `SITE_PRESENT`/`SITE_CANDIDATE`/`SITE_ABSENT`, and
   C0(b)'s separation of *unstated* from *refused* — and an absence given veto power asserts what the
   data cannot support, facing the other way.

**Reasoning, consequences and the arguments against the four rejected readings are in § *Settling
C0(d)'s reading rule, 2026-08-12*** and are not restated here. **C0(a), (b), (c) and (e) are
unchanged; C1, C2, C3 and C4 are unchanged.**

#### C1 — contrast criteria, each naming the figure it is tested against

A candidate scores one point per criterion on which it is **predicted to differ**. Bands are stated
so *differs* is decided by a rule and not by taste.

| # | Criterion | Tested against | Informative if |
|---|---|---|---|
| 1 | Multi-mapping rate (I14) | **1,896 / 2,298 = 82.5%** | outside **60–95%** |
| 2 | Razor picks that are isoforms (I2) | **6/20 = 30%** | outside **15–45%**, sample ≥ 20 |
| 3 | Razor pick on TrEMBL despite a reviewed entry (I17) | **4 of 8 = 50%** | outside **25–75%**, sample ≥ 8 |
| 4 | `AMBIGUOUS` fold | the state **measured 0 of 198 times**; 7 of 2,260 cold snapshots carry it | any non-zero rate over a comparable accession sample |
| 5 | Declared-quantity enum (I16) | `intensity_multiplicity_summed` | a different multiplicity treatment or intensity family |
| 6 | Localisation distribution | median **1.00**, min **0.35** | a different median, a different column name, or a different scale |
| 7 | Native stoichiometry (I4) | `Ratio mod/base` **present** per sample | **absent** — which would test whether `native` is reachable outside this deposit at all |
| 8 | Sample-name convention | one replicate carrying a run ID (`KO_1_181212063719`) | a different convention in kind, not just in spelling |
| 9 | Unrecorded threshold (I16's unfired case) | **242 of 2,298 = 10.5%** dropped at `Localization prob >= 0.75` | the deposit applying its own filtering before deposit |
| 10 | SDRF present | **No** | **Yes** — `sdrf` is §5.3's authoritative basis and has never once been exercised |
| 11 | Design recoverable from column names | *unambiguous* | **not** recoverable — which tests whether `filename_inference` generalises at all |

**How this list was assembled, since a short enumeration is the recurring failure here.** All 24
data rows of § *Measured findings*' table were walked, not the five named at the outset: rows 6, 7,
10 and 23 supplied criteria 6, 7, 8 and 9, and row 8 supplied criterion 10. §8 was then walked
programmatically for invariants citing a PXD018299 measurement inside their own text, which returns
**I2, I14 and I17** — `I21` also matched and is a **false positive**, the digits `198` occurring
inside the digest `bzk:3473130e9cb7f1198196ee40b0e30727`. Rows describing the *published paper*
rather than the deposit, and rows that are resolver-bug findings, were not made criteria.

#### C2 — ranking, C3 — survey size, C4 — method

**Rank** by C1 points. Ties break on: SDRF present, then site count ≥ 1,000 so the rates are
measurable at all, then smaller download.

~~**At most 12 candidates enter**, drawn from the PRIDE v3 search API over a query set fixed here
before running — `ISG15`, `ubiquitin GlyGly`, `diGly`, `ubiquitinome` — taking the API's own
ordering and not reordering by eye.~~

**C3 was unusable as written and is amended here, with the original left standing — 2026-08-12,
after the first run and before any candidate was judged.** *Taking the API's own ordering* over a
list of queries, read literally, walks query one to exhaustion first — and `ISG15` alone returns 25,
so it took all twelve slots and `diGly` (25 results) and `ubiquitinome` (25) were never queried at
all. The registered query set was not surveyed; one quarter of it was. **Amended to allocate the cap
round-robin across the queries**, which is what *a query set* was for. `ubiquitin GlyGly` returns
**0** and contributes nothing, which is itself recorded rather than quietly dropped.

**C3 also said nothing about archives, and that produced a false zero.** Filename-only reading
records `PXD065158` — *Proteome-wide identification of ISG15 sites in HeLa cells* — as carrying no
processed files and no identifiable engine, because it deposits its entire search as one 405 MB
`Search_GlyGly.zip`. **Amended: a candidate's non-raw archives are listed by reading the zip's
central directory over a byte range**, two requests against 405 MB, retaining nothing. Up to three
archives per candidate; any beyond that, and any that fails to read, is recorded as such — a skipped
archive and an empty one otherwise produce the same blank column, which is the failure this
amendment exists to prevent.

**Classification uses the established method and not a new one.** Perseus versus raw search-engine
output is decided by the type-prefix stamp (`C:`/`N:`/`T:`/`M:`), **never** by the presence of a
statistics column, which § *Deposit and supplementary survey* records as having produced a false
positive on a `Q-value` column that raw MaxQuant also carries. Search engine and grain are read from
the deposit's file listing where the filenames settle it.

**No bytes are retained**, so `raw_store` is not exercised this turn and nothing enters
`data/curation/`. Any figure that reaches a document comes from an instrument on disk, in the shape
`drift.py` and `fetch_progress.py` already set — not imported by the platform, run as `python -m`.

#### Predictions, and where none is made

**No prediction is registered about any rate in C1 (1)–(4), (6) or (9), and the reason is that no
instrument in this container can resolve them this turn.** Each needs the candidate's site table
parsed, and this survey deliberately downloads none — so a predicted multi-mapping rate would be a
number with no instrument behind it, which is the shape this section exists to forbid. What the
survey *can* resolve is metadata: engine, grain, file inventory, SDRF presence, public status. Those
are read, not predicted.

**If the survey finds no admissible candidate, that is the result** and it is recorded with the
criteria that excluded them. No criterion is relaxed to produce a shortlist.

### Pre-registration: re-running the same twelve through the fixed instrument, 2026-08-12

**Committed before the instrument is changed and before anything is run.** Six under-reporting
modes were closed after the survey below, and **nothing has measured what closing them did**. The
same twelve accessions go back through the current instrument — no new candidate, no widened draw,
C3 untouched — so that any later difference is attributable to the field rather than to the fixes.

**Both endpoints were confirmed answering first**, since the whole exercise depends on them:
`https://ftp.pride.ebi.ac.uk/pride/data/archive/2022/02/PXD018299/` → 200, and
`https://www.ebi.ac.uk/pride/ws/archive/v3/projects/PXD018299/files` → 200 with a JSON body.

#### (a) How many of the twelve rows change in any cell — predicted **7**

| Row | Predicted change | Why |
|---|---|---|
| 2, 6, 10, 12 | **Engine** cell | `none identifiable` splits, and each of these has spectra and no table, so each becomes `no_processed_output` |
| 9 | **Engine** *and* **Site table** | `Peptides_UbPTMs.txt` makes it `unclassified` rather than *none identifiable*; `UbPTMs_PTMs_Summary.txt` matches a site hint, so the site cell moves `—` → `candidate` |
| 5 | **Site table** | `abundance_single-site_MS2quant_Norm.tsv` matches a site hint → `candidate`. Engine stays `maxquant`: it is matched by `proteinGroups.txt`, not by the `sites.txt` marker that was removed |
| 7 | **Files** count | `raw_`/`_raw` no longer filter archives out *before* the cap, so a different set of three may be expanded — the count can move in either direction |

**Predicted unchanged: rows 1, 3, 4, 8, 11.** The DIA-NN and Proteome Discoverer markers still match
under the suffix rule, and none of these five has a name that a site hint reaches.

**Instrument** — `python -m bzk.deposit_survey` over the twelve accessions, compared cell by cell
against the table below. **Precision** — exact, per cell; a row counts as changed if any of *Files*,
*Engine*, *Site table*, *SDRF* or the recorded reason differs.

**The number that would be most informative is not 7.** A **0** would say the six modes are inert on
the very sample they were derived from, which would be a finding against the fixes. Row 8's count is
the one I am least able to predict: it has 607 files and its archives are the ones the narrowed hint
set most affects.

#### (b) How many change admissibility — predicted **0**

**Not one, and the reason is structural rather than optimistic.** `SITE_TABLE_HINTS` reports
`candidate` and **never** `present`; the comment at that constant says so, and says the two
filenames the split was built from are the reason `SITE_TABLE_MARKER` was *not* widened. So for rows
5 and 9 the fix changes what is *reported*, not whether C0(c) passes. Row 5 is the only C0(d) pass
in the twelve and it needs C0(c); `candidate` is by construction not that.

**The one way this could be non-zero**, named in advance so a surprise is not retro-fitted: the
narrowed archive-hint set now lists zips it previously skipped, and if one of those holds a file
matching MaxQuant's `…Sites.txt` convention, that row would reach `present` on a genuine basis. I
do not expect it, and I am naming it because it is the only path.

**If any candidate does become admissible, the turn stops at saying so** — no C1 scoring, no
ranking, no admission.


### Pre-registration: re-drawing the sixty through the guarded parser, 2026-08-12

**Committed before the run, in its own commit, so the ordering rests on git rather than on the
account below.** Defect 2 — a server answering a ranged request with **200** — made the old parser
return an empty tuple, indistinguishable from an archive holding nothing. The parser is now guarded.
This measures what the old one got wrong.

**The sample cannot be re-drawn from the repository, and that is the first finding.** `survey`
derives its sixty at run time from `QUERIES` (`bzk/deposit_survey.py` l.53–67, thirteen terms) at
`MAX_CANDIDATES` (l.70), round-robin, in the API's own per-query ordering (l.571). Nothing on disk
names the accessions. Counted at `c167fc5`: the widened-draw section holds **12** distinct `PXD`
accessions — exactly the twelve of § *Widened draw* → *Twelve pass C0 entirely* — and the whole of
`ROADMAP.md` holds **25**.
**Forty-eight of the sixty were classified and never recorded.** So the drawn list is written to this
document as a first-class output of the run, and the comparison below is bounded: a survey-path run
yields *a* sixty, not *the* sixty, and rows present in only one draw are not evidence of change in
either direction.

**Both endpoints confirmed answering first, in this container, before anything was predicted:**
`https://www.ebi.ac.uk/pride/ws/archive/v3/search/projects?keyword=ISG15&pageSize=3` → **200**,
`application/json`, 3 rows, first accession `PXD071724`; and
`https://www.ebi.ac.uk/pride/ws/archive/v3/projects/PXD018299/files?pageSize=500` → **200**,
`application/json`, 39 rows. `self_check` passes: `PXD018299` lists 39 files including
`HAP1_USP18KO_GlyGlyKSites.txt`.

**A third surface was probed, because the guards live on it and not on the two JSON endpoints.**
`ftp.pride.ebi.ac.uk` advertises `Accept-Ranges: bytes` and answered **206** with an exact
`Content-Range` for both of `PXD065158`'s archives — `Search_GlyGly.zip` (405,865,159 B) and
`Search_shotgun.zip` (1,397,829,455 B) — 65,536 bytes asked for and 65,536 returned in each case.
Every prediction about a guard below rests on that measurement of the **host**, not on a reading of
the parser.

**C0(b) is not evaluable from the survey path, established by reading the endpoint rather than the
module.** `search` (l.269–278) never sets `license`, and the search endpoint **has no such field** —
its row keys carry `submissionType`, `organisms`, `softwares` and no licence of any kind. Only
`projects/{accession}` carries `license`, which is why `classify` (l.559) is the only reader of it.
No change to `search` could supply C0(b); the gate needs one project-record read per drawn accession,
exactly the read `classify` makes. That read issues no query and so cannot widen the draw.

#### (a) Rows **shared with the widened draw** changing in any cell — predicted **0**, band 0–1

**Comparable cells are only those the widened draw recorded.** For its twelve, § *Widened draw* →
*Twelve pass C0 entirely* states
CC0, MaxQuant, `site=present`, and a resolvable organism. Per-row *Files* counts were never recorded
for those twelve, so *Files* is **not** a comparable cell here and a differing count is not a change.

Three reasons, each naming what it rests on:

| # | Reason | Rests on |
|---|---|---|
| 1 | All twelve reach `site=present` through `SITE_TABLE_MARKER` matched against the **file-listing** endpoint. Defect 2 can only empty an *archive* read, so the cell carrying C0(c) for these rows never passes through the parser | reading l.212 against l.293–305 at `c167fc5` |
| 2 | Defect 2's precondition — a server ignoring `Range` — is not present today | the two 206s measured above, on the one host every archive URL resolves to |
| 3 | Licence and organism come from the project record, which no guard touches | l.547–559 |

**What would falsify it:** a deposit updated between the widened draw and this run — new files, or a
changed licence. That is the only path I can name, and it is why the band is 0–1 rather than 0.

**Predicted C0 passes among shared rows: 12**, contingent on (d). **If any candidate's C0 verdict
changes in either direction the turn stops at saying so** — no C1 scoring, no ranking, no admission.

#### (b) Guard 2 (ranged request answered 200) — predicted **0 raises**

**Bounded first, because a zero-raise result licenses only what the bound allows.** Guard 2 (l.399)
is `if start > 0 and response.status_code == 200`. `chunk` is called from three places and the bound
differs at each:

| Call | Site | `start` | Guard 2 reachable? |
|---|---|---|---|
| first read | l.406 `chunk(max(0, size - tail))` | `max(0, size - 65536)` | only when `size > 65,536` |
| zip64 header | l.422 | the zip64 locator's offset | yes, for any real archive |
| directory | l.426 `chunk(cd_off, cd_off + cd_size - 1)` | `cd_off` | yes whenever `cd_off > 0` |

So the stated bound — *archives above 64 KiB only* — **holds for the first read and not for the
function.** A sub-64-KiB archive whose server ignores `Range` gets the whole file on the first read,
where `blob` is then the complete archive and the end-of-central-directory parse is correct rather
than wrong; the ignore is caught one call later at l.426, where `cd_off > 0`. The genuinely uncovered
case is therefore narrower than *small archives*: it is an **empty** zip under 64 KiB, where
`cd_off` is 0 and `declared` is 0 and there is nothing to get wrong. This refinement is a claim about
the code and is verified offline before the run, not asserted.

**Predicted: exactly 0 raises**, on the host measurement above. **Drawn candidates sitting inside the
bound** — at least one inspected archive above 64 KiB — predicted **15, band 10–25, low confidence**:
it is inferred from the widened draw's recorded *14 of 60 depend on `archive_entries`*, which counts
reads that **returned entries** and is therefore a lower bound on reads *attempted*. No instrument in
this container resolves it before the draw is made.

#### (c) Guard 4 (length vs `cd_size`) — predicted **0**. Guard 3 (count vs declared) — predicted **0**, band 0–1

**These two are not equally supported and are not predicted with equal confidence.**

Guard 4 (l.429) fires on a short partial-content body. It turns on the **host's** range behaviour,
which is measured: exact `Content-Range`, exact byte counts, twice. Predicted **0**.

Guard 3 (l.441) fires when the parsed entry count disagrees with the declared count. It turns on the
**internal structure of archives I have not sampled**, not on anything measured above. A single
archive with more than 65,535 entries, a spanned directory, or a zip64 end-of-central-directory whose
16-bit `declared` is saturated would flip it to ≥1. Predicted **0** at materially lower confidence,
band 0–1.

**Two further raise routes are reported separately rather than folded into the four**, because both
land in `skipped` as `unreadable (RuntimeError)` and would otherwise be miscounted as guard 3 or 4:
guard 1, the absent zip64 locator (l.418) — predicted **0**; and the **unnumbered** guard at l.409,
no end-of-central-directory in the last 64 KiB, which a zip carrying a trailing comment longer than
64 KiB would trip — predicted **0**, band 0–1.

#### (d) Drawn rows shared with the widened draw — predicted **12 of 12**, band 10–12

The widened draw's recorded members are the twelve of § *Widened draw* → *Twelve pass C0
entirely*. Both runs use thirteen registered
terms, `size=100`, page 0, cap 60, round-robin, on the same calendar date, so they address the same
index hours apart. **What would falsify it:** PRIDE's relevance ordering is not contractually stable,
and a deposit indexed today can shift ranks across the cap boundary. Instrument: set intersection
between the drawn list and the twelve parsed from that paragraph. Precision: exact integer.

#### Where no instrument in this container resolves the quantity, no prediction is made

Two, named so their absence is not read as an oversight: **how many of the drawn sixty are accessions
appearing nowhere in `ROADMAP.md`** — unknowable in that direction, since forty-eight of the widened
sixty were never recorded — and **per-row cell values for any row not shared with the widened draw**,
which have no recorded counterpart to differ from.


### Second-deposit survey: no admissible candidate in twelve, 2026-08-12

**The result is that the shortlist is empty**, recorded with the criteria that excluded each
candidate rather than produced by relaxing one. Run with `python -m bzk.deposit_survey` over the
query set registered above, cap 12, round-robin after C3's amendment.

| # | Accession | Files | Engine | Site table | SDRF | Excluded by |
|---|---|---|---|---|---|---|
| 1 | `PXD071724` | 51 | DIA-NN | — | N | C0(d), C0(c) — *Mapping ISG15 sites on GAPDH and PGK1 by AP-MS* |
| 2 | `PXD078284` | 9 | none identifiable | — | N | C0(c), C0(d) — Arabidopsis XL-MS; no processed output |
| 3 | `PXD077594` | 19 | DIA-NN | — | N | C0(d), C0(c) — *Ubiquitinome Profiling… Data-Independent…* |
| 4 | `PXD071548` | 12 | Proteome Discoverer | — | N | C0(d), C0(c) — *ISGylation of H2AX…* |
| 5 | `PXD076163` | 35 | **MaxQuant** | — | N | **C0(c) only.** The one engine pass in twelve, and it carries `proteinGroups.txt` plus a custom `abundance_single-site_MS2quant_Norm.tsv` — protein grain and a non-MaxQuant single-site table, no `…Sites.txt` |
| 6 | `PXD068808` | 35 | none identifiable | — | N | C0(c), C0(d) — *Global ISGylome… SARS-CoV-2*; `.d`/mzML only |
| 7 | `PXD069668` | 179 | DIA-NN | — | N | C0(d), C0(c); 5 further archives unlisted at the limit |
| 8 | `PXD065158` | 607 | **FragPipe** | — | **Y** | C0(d), C0(c) — *Proteome-wide identification of ISG15 sites in HeLa cells*. **The near miss**, and see below |
| 9 | `PXD075792` | 23 | none identifiable | — | N | C0(c), C0(d) — `Peptides_UbPTMs.txt` / `UbPTMs_PTMs_Summary.txt`, not MaxQuant's form |
| 10 | `PXD069603` | 68 | none identifiable | — | N | C0(c), C0(d) — mzXML and a submission spreadsheet |
| 11 | `PXD058618` | 8 | Proteome Discoverer | — | N | C0(d), C0(c) — *USP18 interactor and PTM mass spectrometry* |
| 12 | `PXD074126` | 3 | none identifiable | — | N | C0(c), C0(d) — Arabidopsis |

**Every one fails C0(c): not one of the twelve deposits a MaxQuant site-grain table.** Eleven also
fail C0(d). No candidate reached C1, so **no contrast criterion was scored and no rate was measured**
— which is why no prediction was registered for any of them.

**`PXD065158` is the near miss and the most informative row.** It is *Proteome-wide identification
of ISG15 sites in HeLa cells* — the anchor domain almost exactly — it carries **607** files after
its archives are listed, and it is the **only deposit in the sample carrying an SDRF**, which is
criterion 10, §5.3's authoritative basis that has never once been exercised here. It fails on
engine: the 405 MB `Search_GlyGly.zip` holds `psm.tsv`, `peptide.tsv`, `protein.tsv`, `pepXML` and
`MSBooster` output — FragPipe, whose adapter is v0.2. **Recorded as excluded and not as absent**,
because it would pass every gate the moment a FragPipe adapter exists.

**An explanation was proposed, measured, and rejected.** PRIDE marks 11 of 12 `PARTIAL`, and across
the registered queries the split is **201 `PARTIAL` to 8 `COMPLETE`** — a `PARTIAL` submission is
not obliged to deposit processed search output, which would neatly explain the zero. **It does not,
because `PXD018299` is itself `PARTIAL`** and deposits all three of its processed tables anyway. The
submission type does not predict whether a site table is present, so the hypothesis is recorded as
falsified rather than carried as a plausible cause.

**What this result is and is not.** It is a statement about **twelve deposits drawn by four
registered queries**, not about PRIDE. The cap was registered before the run and is not raised here
to produce a shortlist.

**The instrument that produced it under-reported in six ways, closed 2026-08-12; this paragraph
named two of them and was therefore incomplete when it was written.** The twelve-row table above and
the empty shortlist stand as recorded — nothing here re-runs anything, and **no claim is made about
what a re-run would return**, which would be a prediction with no instrument behind it.

| Mode | What it did | Closed by |
|---|---|---|
| **1. Site tables outside MaxQuant's convention read as absent** — named in this paragraph | `PXD076163`'s `abundance_single-site_MS2quant_Norm.tsv` is site grain and scored `—` | C0(c)'s test is now **three-state**: `present` for MaxQuant's own convention, `candidate` for a name that suggests site grain without following it, `absent` for neither. Widening the marker was rejected: every name added is a guess, and it would have turned an under-inclusive gate over-inclusive |
| **2. Archives beyond the cap** — named in this paragraph | five unlisted for `PXD069668`, in prose only | every skip now returns as data, per archive, with its reason |
| **3. Archives skipped by name hint** — **not** named, and it left no trace at all | `_RAW_ARCHIVE_HINTS` filtered before the cap and appended nothing, so the unlisted count under-stated what had not been looked at | `raw_` and `_raw` are removed as guesses about naming — `Search_GlyGly.zip` is the standing proof a name can say nothing — and the two container formats that remain record every skip |
| **4. *None identifiable* collapsed two findings** — **not** named, 5 of 12 or 42% of the sample | `PXD078284` has no processed output; `PXD075792` has `Peptides_UbPTMs.txt` this instrument could not classify. One is a fact about the deposit, the other an instrument gap, and the column rendered them identically | `no_processed_output` and `unclassified` are now distinct states |
| **5. One constant answered two questions** — found while closing 1 | `sites.txt` was C0(c)'s marker *and* a MaxQuant engine marker, so a non-MaxQuant site table would have marked a deposit MaxQuant | the engine table no longer carries it |
| **6. Engine markers matched as substrings** — found by the new test on its first run | `summary.txt` classified `PXD075792`'s `UbPTMs_PTMs_Summary.txt` as MaxQuant | markers match as a **suffix of the basename**, which admits a submitter's prefix (`HAP1_USP18KO_proteinGroups.txt`) without admitting the coincidence; one compression wrapper is stripped first so a gzipped table is not a new under-report |

**A seventh was closed that is not an under-report but an over-run.** `_get` raised on any non-200
and the exception reached `main`, so one accession that would not answer could end a survey of
twelve after three — with the remaining nine looking like a field that had been searched. A failed
listing is now recorded against that candidate and the run continues.

**`tests/test_deposit_survey.py` now guards the module**, which had none while both its siblings
did. ~~Every test injects a stub session, so none needs the network — a guard against silent zeroes
that skipped in a sandboxed clone would be absent exactly where it is needed.~~

**That sentence was false when written and is corrected 2026-08-12.** Three of the archive tests did
not inject a session, because `expand_archives` took none and fetched a deposit's URL map as its
first statement — before deciding whether any archive would be opened. In a clone that cannot reach
`www.ebi.ac.uk` they **failed** rather than skipped, so a clean checkout reported a red suite, and
the missing coverage was of the archive-visibility fixes those tests exist for. **They passed in the
container that wrote them only because it has network access**, which is how the claim survived
being checked: a passing count is a property of the container it was measured in, not of the
repository. Both halves are repaired — the seam is threaded and the fetch deferred — and the
absence of a request is now asserted directly, since no networked container can tell a deferred
fetch from an eager one by outcome. One path is still unexercised and says so at the function:
`archive_entries` cannot take a session without a Protocol admitting `head` and a `headers=`
keyword, which is a change to a contract three other modules satisfy.

### C3 amended a third time, and the coverage denominator, 2026-08-12

**Written and committed before the widened run.** The two earlier C3 amendments stand above; so
does this one's pre-amendment text. **C0 is untouched — C0(d), the MaxQuant gate, exactly as
written.** This measures the field the gate sees; it does not adjust the gate.

#### The denominator, which no survey has ever stated

**The v3 search returns a `total_records` HTTP header and caps a page at 100 rows**, and neither
was known when the earlier draws were made. That settles an arithmetic this document could not
explain: § *…no admissible candidate in twelve* records **201 `PARTIAL` to 8 `COMPLETE`** — 209 —
against four queries that at `pageSize=25` return at most 100. **It was a run at `size=100`**, which
`search`'s signature has always allowed since `size` is a default and not a constant, and
`submission_type` is populated only inside `search`, so search results alone could produce it. **And
it was truncated**: `diGly` returned exactly 100 because 100 is the ceiling. Its true total is
**178**, so the 209 was 45 + 0 + 100 + 64 where the honest figure over those four queries is 287.

| Term | `total_records` | Page 0 |
|---|---|---|
| `ISG15` | 45 | 45 |
| `ISGylome` | 8 | 8 |
| `diGly` | **178** | 100 *(ceiling)* |
| `GlyGly` | **248** | 100 *(ceiling)* |
| `K-GG` | 46 | 46 |
| `diglycine` | 69 | 69 |
| `ubiquitinome` | 64 | 64 |
| `ubiquitylome` | 44 | 44 |
| `ubiquitin remnant` | **113** | 100 *(ceiling)* |
| `ubiquitination site` | 96 | 96 |
| `ubiquitylation site` | 28 | 28 |
| `UbiSite` | 9 | 9 |
| `ubiquitin GlyGly` | **0** | 0 |

**Union over page 0 of all thirteen: 450 distinct accessions.** That is the denominator every
coverage claim below rests on. Pagination works (`page=0,1,…`), so the three truncated terms are
reachable at a cost of one further request each; they are **not** paginated in this draw, and that
is a stated limit rather than an oversight.

#### C3, amended

~~**At most 12 candidates enter**, over `ISG15`, `ubiquitin GlyGly`, `diGly`, `ubiquitinome`.~~

**Query set — thirteen terms, and how they were chosen rather than only what they are.** The
starting point was that `ubiquitin GlyGly` returns **0**, recorded above: a two-word query that
matches nothing is evidence the field is not indexed by the phrase a reader would write. So terms
were drawn from what a diGly deposit is actually *titled* — the remnant by its chemistry (`GlyGly`,
`K-GG`, `diglycine`), the sub-proteome by its two spellings (`ubiquitinome`, `ubiquitylome`), the
enrichment by its method (`ubiquitin remnant`, `UbiSite`), the measurement by its object
(`ubiquitination site`, `ubiquitylation site`), and the anchor domain (`ISG15`, `ISGylome`). Each
was **measured before inclusion** and each is kept with its total, including the zero: a term that
matches nothing is a fact about the index and is retained so the next draw does not re-try it.

**Cap — 60**, raised from 12. **Cost, since it is the reason it is not higher**: classification is
2 requests per candidate (project record, file listing), plus 3 per archive opened (one `HEAD`, two
ranged `GET`s) to a limit of three archives — so 2 to 11 requests per candidate, and the ranged
reads are against files of hundreds of megabytes. Measured on the twelve, classification runs at
roughly ten seconds each. 60 is what fits without the draw becoming the turn.

**`size` — 100**, the page ceiling, one page per term, no pagination.

**The twelve already surveyed are re-included.** Excluding them would make the widened result
incomparable with the two records above, and they are 12 of 450 — small enough that their presence
does not distort a distribution and useful enough as a consistency check on the instrument.

**Coverage, stated in two numbers because they are different.** The draw pool is **450 of 450**
distinct accessions the thirteen terms reach on page 0 — but that pool itself misses the tails of
three truncated terms. Full classification covers **60 of 450 = 13.3%**.

**And one measurement covers the whole pool at almost no cost.** `search` populates
`Candidate.software` from PRIDE's declared `softwares`, so an engine census over all **450** needs
**thirteen requests** — the ones already made — and no file listing at all. It is run, because Step
2's question of whether engine distribution is measurable from search alone answers *yes* and the
cost is already paid. It is reported separately from the classified 60 and never merged with it.

#### Step 2's measurement: the two engine signals on the twelve

`Candidate.software` has been populated since the module was written and **read by nothing** —
`grep -rn "\.software" --include=*.py .` finds no consumer in `bzk/` or `tests/`. Measured now:

| Filename route | Declared | Rows |
|---|---|---|
| **agree** | | `PXD071724`, `PXD077594`, `PXD069668` (DIA-NN); `PXD071548`, `PXD058618` (Proteome Discoverer); `PXD065158` (FragPipe) — **6** |
| filename only, nothing declared | — | `PXD076163` (MaxQuant, from `proteinGroups.txt`) — **1** |
| **declared only, filename `unclassified`** | | `PXD075792` → **FragPipe**; `PXD074126` → **MaxQuant** — **2** |
| neither | — | `PXD078284`, `PXD068808`, `PXD069603` — **3** |

**They disagree twice and one of those matters.** `PXD074126` **declares MaxQuant** while the
filename route reads `unclassified` — so the twelve contained **two** MaxQuant deposits and the
survey saw one, and the row excluded on C0(d) may pass the gate it was excluded on. The two signals
are **not merged**; `engine_state` stays a three-state property with its recorded reason. What is
recorded is the comparison.

**A parsing repair was needed to read the field at all.** PRIDE returns CvParams and the module
kept `str(x)`, yielding `"{'@type': 'CvParam', …, 'name': 'MaxQuant'}"`. Same values, legible; not
a widening, and not one of the six modes.

#### Step 4: predicted before the run, with what each outcome licenses

**(a) Candidates in the 60 passing C0 entirely — predicted 3.** *Instrument*: `--classify` over the
draw, C0 evaluated per candidate. *Precision*: exact integer. *Reasoning, from the field rather than
from the diff* — the last prediction missed because it reasoned about changed code paths, and this
one reasons about deposits: MaxQuant should be the largest declared tool across a pool spanning the
2010s and 2020s, but C0(c) needs a deposited `…Sites.txt`, and most PRIDE submissions are `PARTIAL`
and deposit raw files only. Roughly a third MaxQuant, of which perhaps a quarter deposit the
processed site table, over 60 → about 5, discounted to **3** for the naming convention.

**(b) Engine distribution among deposits with site-grain output** — predicted, of those in the 60
showing `present` or `candidate`: **MaxQuant 30%, DIA-NN 25%, FragPipe 15%, Proteome Discoverer
10%, unclassified 20%**. *Instrument*: the filename route and the declared field, reported
separately. *Precision*: ±10 percentage points, which is as fine as 60 candidates can resolve.

**What each outcome licenses, both branches written before either is seen.**

> **C0(d) is the binding constraint** if deposits carrying site-grain output are substantially
> non-MaxQuant — concretely, if **non-MaxQuant site-grain deposits ≥ 2× MaxQuant site-grain
> deposits**. That would say the gate, not the field, is what leaves the shortlist empty, and the
> second-deposit test is limited by which adapter exists rather than by what has been deposited.

> **C0(d) is not the binding constraint** if **MaxQuant site-grain deposits are ≥ half of all
> site-grain deposits**, **or** if **≥ 5 candidates pass C0 entirely**. Either says a MaxQuant field
> exists at a size that makes the gate incidental, and an empty shortlist would then be about the
> draw or the other gates.

**Between those two — non-MaxQuant strictly under 2× and MaxQuant strictly under half, with fewer
than 5 passing — nothing is licensed**, and that is registered as a real outcome rather than a gap
to be argued into one branch afterwards.

**No prediction is made** about the declared-software census over the 450: it covers a pool whose
composition no instrument here has previously sampled, and a number invented for it would have
nothing behind it.

### Widened draw: the MaxQuant field is large, and C0(d) does not bind, 2026-08-12

**Instrument** `python -m bzk.deposit_survey`, thirteen registered terms, `size=100`, one page per
term, cap **60**, run 2026-08-12. **The two records below stand unedited**; this is a third beside
them. **No candidate is scored, ranked or admitted** — twelve pass C0 and the turn stops at saying
so.

#### The declared-software census over the whole pool — 450 accessions, thirteen requests

Measurable from search alone, which is what made it affordable; no file was listed for it.

| Declared tool | Deposits | Share of 450 |
|---|---|---|
| **MaxQuant** | **222** | **49.3%** |
| Proteome Discoverer | 75 | 16.7% |
| Mascot | 54 | 12.0% |
| Sequest | 34 | 7.6% |
| DIA-NN | 33 | 7.3% |
| Spectronaut | 27 | 6.0% |
| Andromeda | 27 | 6.0% |
| FragPipe | 9 | 2.0% |
| *declaring nothing* | 70 | 15.6% |

Submission type across the pool: **417 `PARTIAL`, 33 `COMPLETE`** — and `PXD018299` is itself
`PARTIAL`, so that split still predicts nothing about whether processed files are present.

#### The classified 60

| Site state | Count |
|---|---|
| `present` | **12** |
| `candidate` | 10 |
| `absent` | 38 |

**Site-grain deposits (present or candidate): 22 of 60.** By engine, counting a deposit MaxQuant if
*either* signal says so: **MaxQuant 14, non-MaxQuant 8** — a MaxQuant share of **63.6%** and a
non-MaxQuant-to-MaxQuant ratio of **0.57**.

**Twelve pass C0 entirely** — `PXD079072`, `PXD075538`, `PXD070339`, `PXD074990`, `PXD027328`,
`PXD074949`, `PXD027163`, `PXD032078`, `PXD019152`, `PXD018299`, `PXD070789`, `PXD060435`. Every one
is CC0, MaxQuant, `site=present`, with a resolvable organism. **One of them is `PXD018299` itself**,
which is the instrument finding the anchor deposit and classifying it exactly as this repository
already knows it — a consistency check rather than a candidate, leaving **eleven** that are new.

**C0(b) could not be evaluated when it was predicted, and the instrument was repaired rather than
the gate waived.** `license` is on the project record and nothing read it, so *passes C0 entirely*
was unanswerable at prediction time. It is carried now; all twelve state **CC0**, and an unstated
licence reads as empty, which C0(b) treats as exclusion rather than permission.

#### The decision rule, applied to the numbers it was written for

Both registered *not-binding* conditions fire, and neither *binding* condition does:

- MaxQuant is **63.6%** of site-grain deposits, against a threshold of **≥ 50%**.
- **12** pass C0 entirely, against a threshold of **≥ 5**.
- The binding condition required non-MaxQuant **≥ 2×** MaxQuant; measured, it is **0.57×**.

> **C0(d) is not the binding constraint on the second-deposit test.** The MaxQuant gate is not what
> left the first shortlist empty. A MaxQuant, site-grain, CC0 field exists at a size the earlier
> draw could not see — and what limited that draw was its **query set**, not its gate: the four
> original terms never named the remnant chemistry, and `GlyGly`, `K-GG` and `diglycine` are where
> this field lives.

**This decides nothing about C0(d) and nothing is adjusted.** It measures the field the gate sees.

#### Both predictions missed, and in opposite directions to the last one

**(a) predicted 3, measured 12.** The reasoning was that MaxQuant would be roughly a third of the
pool and that only a quarter of those would deposit a processed site table. The first half was
**too low** — 49.3% — and the second **much too low**. The diagnosis the previous turn recorded was
that predicting from the diff misses what the diff reveals; **this miss is the same error moved one
step out**: I predicted from a field I had only ever seen through four queries that do not name the
remnant, so the sample I was extrapolating from was selected by the very defect this turn fixed.

**(b) predicted MaxQuant 30%, DIA-NN 25%, FragPipe 15%, Proteome Discoverer 10%, unclassified 20%
among site-grain deposits, ±10 points. Measured, by the filename route: MaxQuant 50%, DIA-NN 9%,
FragPipe 4.5%, Proteome Discoverer 0%, unclassified 36%.** Every category missed, four of five
outside the registered band. The shape of the error is one belief: I expected the 2020s DIA
transition to have moved ubiquitomics further than it has. It has not — DIA-NN is 7.3% of the pool
and Spectronaut 6.0%, against MaxQuant's 49.3%.

#### What this rests on, and what it cost

~~**14 of 60 rows (23.3%) depend on `archive_entries`, which still has no injectable seam and no
test** — and **7 of the 12 that pass C0** do, along with 11 of the 22 site-grain rows. Nearly a
quarter of this result therefore carries **weaker provenance** than the rest, and at this cap that
is no longer a footnote about three rows.~~

**The counts stand; the reason for the discount does not — 2026-08-12.** 14 of 60, 7 of the 12 and
11 of the 22 are unchanged, because nothing here re-ran anything. What changed is that
`archive_entries` now takes a session and is tested: `bzk/http.py` declares a third Protocol, and
the parse is checked against archives built by `zipfile` rather than against a hand-made blob.
**Whether those rows would classify identically under the tested parser is a measurement and is not
made here** — the counts above are therefore still the honest description of what that result rests
on, and only the *untested* half of the ground for discounting them is withdrawn.

**One of the four defects closed could have changed what those rows reported, and it is left as an
open question rather than answered.** A server answering a ranged request with **200** — the whole
file's head instead of the part asked for — used to yield an **empty tuple**, because
`raise_for_status` passes on a 200, the body then starts `PK\x03\x04`, and the parse loop never
runs. That is indistinguishable from *this archive holds nothing*, which is precisely the false zero
`archive_entries` was written to fix, and it sat one function away from the `self_check` that exists
to prevent the same shape. **Any of the 14 rows could have been reported on an empty listing for
that reason**, and nothing in the record distinguishes them. The other three defects truncate rather
than empty, so they could have shortened a listing without emptying it.

**The measurement was made, and the reason above expired with it — 2026-08-12, § *Re-draw of the
sixty through the guarded parser*.** Read that section for the result; what belongs here is only that
*nothing here re-ran anything* no longer holds. **There is no single successor to 14**, because the
denominator's definition changed underneath it: 14 counted reads that **returned entries**, and the
guarded parser distinguishes a read that succeeded from one that was attempted and failed, which the
old one could not. The successor is a **pair** — over the re-drawn sixty, **14** rows carried a
successful archive read and **0** had a read attempted and fail; of the twelve rows shared with this
draw, **7** carried a successful read. The three counts above are not edited and are not restated.

**One transient failure is on the record**: the `diGly` search read-timed-out at 60 s on its first
attempt and succeeded on the second. It is retryable and was retried; a run without per-term retry
would have lost 100 rows from the pool and reported a smaller field with no indication.

**Coverage.** 60 of 450 = **13.3%** fully classified; 450 of 450 for the declared census. The pool
itself is page 0 of each term, so the tails of `diGly` (178), `GlyGly` (248) and `ubiquitin remnant`
(113) are unseen — roughly 240 further deposit-hits behind the ceiling.

### Re-run of the same twelve through the fixed instrument, 2026-08-12

**The table above is not edited and must not be.** It records what an instrument measured on
2026-08-12 before six under-reporting modes were closed; overwriting it would erase the evidence
that closing them changed anything, which is the thing this section measures. What follows is the
**same twelve accessions** through the current instrument — `python -m bzk.deposit_survey
--classify`, added for this and issuing no query, so the draw is not widened — read cell by cell
against that table.

| # | Accession | Files | Engine | Site table | SDRF | Changed |
|---|---|---|---|---|---|---|
| 1 | `PXD071724` | 51 | `diann` | **`candidate`** | N | **yes** — site |
| 2 | `PXD078284` | 9 | **`unclassified`** | `absent` | N | **yes** — engine |
| 3 | `PXD077594` | 19 | `diann` | `absent` | N | no |
| 4 | `PXD071548` | 12 | `proteomediscoverer` | `absent` | N | no |
| 5 | `PXD076163` | 35 | `maxquant` | **`candidate`** | N | **yes** — site |
| 6 | `PXD068808` | 35 | **`unclassified`** | `absent` | N | **yes** — engine; 16 archives skipped by format, now recorded |
| 7 | `PXD069668` | 179 | `diann` | **`candidate`** | N | **yes** — site; 5 skipped at the cap |
| 8 | `PXD065158` | 607 | `fragpipe` | **`candidate`** | **Y** | **yes** — site |
| 9 | `PXD075792` | 23 | **`unclassified`** | **`candidate`** | N | **yes** — engine *and* site; 18 skipped |
| 10 | `PXD069603` | 68 | **`unclassified`** | `absent` | N | **yes** — engine |
| 11 | `PXD058618` | 8 | `proteomediscoverer` | `absent` | N | no |
| 12 | `PXD074126` | 3 | **`unclassified`** | `absent` | N | **yes** — engine |

#### The two predictions

**(a) rows changed — predicted 7, measured 9. Missed by two, and the miss is the informative half.**
Not one file count moved: the mechanism I predicted for row 7 — narrowed archive hints changing
which three archives the cap admits — **did not occur at all**, and row 7 changed for an entirely
different reason. And I predicted rows 1 and 8 unchanged; both moved to `candidate`. **What the miss
is evidence of** is that I predicted from the *fixes* rather than from the *deposits*: I reasoned
about which code paths had changed and matched them to rows, and the actual changes came from what
was inside archives nobody had looked in. A prediction derived from a diff will systematically miss
whatever the diff made newly visible.

**Four rows changed to a value I named wrongly.** I predicted rows 2, 6, 10 and 12 would read
`no_processed_output`. **Every one reads `unclassified`, and so does row 9 — not one of the twelve
is `no_processed_output`.** The row-level prediction held and the value was wrong in every instance,
which is worth more than the count: it means the baseline's own prose — *no processed output* for
row 2, *`.d`/mzML only* for row 6, *mzXML and a submission spreadsheet* for row 10 — described **an
instrument gap as a property of the deposit**. All five have table-shaped files this instrument
cannot classify. That is mode 4 earning its place, and it is the clearest single result here.

**(b) admissibility — predicted 0, measured 0. Held, and for the structural reason registered.**
`SITE_TABLE_HINTS` reports `candidate` and never `present`; no row reached `present`; C0(d) is
untouched. **No candidate became admissible, so nothing is scored, ranked or admitted**, and the
named path by which (b) could have been non-zero — a `…Sites.txt` inside a previously hint-skipped
archive — did not materialise.

#### What the re-run found that neither prediction anticipated

**DIA-NN and FragPipe both write site-grain GlyGly tables, and three rows fail on engine rather than
on grain.** Row 1 and row 7 carry `report.UniMod_121_sites_90.tsv` and `report.UniMod_121_sites_99.tsv`
— **UniMod:121 is the GlyGly remnant**, the same modification PXD018299's site table holds — and row
8 carries `combined_site_K_114.0429.tsv`, 114.0429 being that remnant's mass. So for rows 1, 7 and 8
the baseline's recorded reason *C0(d), C0(c)* is now **half wrong**: they have site-grain output and
fail the **MaxQuant** gate alone. The table above is left unedited, so a reader comparing the two
must take the exclusion reasons in the earlier one as superseded on that point.

**Three rows rest on a path with no test, and are marked accordingly.** Rows **1, 7 and 8** reached
`candidate` only through `archive_entries`, which has no injectable seam and is exercised against
the live host and by nothing in `tests/`. Their site state therefore carries **weaker provenance**
than the other nine — the distinction this repository already draws between artefact-sourced and
transcription-sourced figures. Rows 5 and 9 reached `candidate` from top-level filenames and do not
depend on it.

### Re-draw of the sixty through the guarded parser: no guard raised, no verdict moved, 2026-08-12

**Instrument** `python -m bzk.deposit_survey --json`, thirteen registered terms, `size=100`, page 0
per term, cap **60**, run 2026-08-12. **Parser commit `c167fc5`** — the guarded parser. The widened
draw ran at **`c8bd02d`**, its immediate parent, on the unguarded one. Predictions were committed
first, at `037e2a7`, before the run; § *Pre-registration: re-drawing the sixty through the guarded
parser* is that commit. **The baseline, re-run and widened-draw tables all stand unedited**, and
**no candidate is scored, ranked or admitted.**

**Relationship to the widened draw, and why the two samples are not the same object.** `survey`
derives its sixty at run time; nothing on disk named the widened draw's. Counted at `c167fc5`, its
section held **12** distinct accessions — the twelve passing C0 — against **25** in the whole
document, so **48 of that sixty were classified and never recorded** and cannot be recovered. This
run therefore yields *a* sixty, not *the* sixty. The three sets, kept apart:

| Set | Count | Comparable? |
|---|---|---|
| in **both** draws | **12** | yes — every recorded member of the widened draw was drawn again |
| in the **new draw only** | **48** | no — no recorded counterpart to differ from |
| in the **widened draw only** | **0** | knowable only for the twelve that were recorded |

The zero in the third row is **not** a claim that the two draws are identical. It says every
*recorded* member was re-drawn; the 48 unrecorded members of the widened sixty are unknowable in
that direction, and some of this draw's 48 are certainly among them.

#### The drawn sixty, pinned

**Written here because a sample that exists only inside a run is the same defect as a figure whose
instrument was never written.** In draw order — first-seen across the registered terms, round-robin,
in the API's own ordering within each term:

`PXD071724`, `PXD068808`, `PXD078284`, `PXD079072`, `PXD077594`, `PXD076163`, `PXD075792`
`PXD030644`, `PXD071548`, `PXD065158`, `PXD075538`, `PXD075275`, `PXD070339`, `PXD074990`
`PXD061232`, `PXD027328`, `PXD055843`, `PXD074949`, `PXD074673`, `PXD070994`, `PXD069668`
`PXD067153`, `PXD074126`, `PXD060627`, `PXD027330`, `PXD044834`, `PXD074538`, `PXD073869`
`PXD066132`, `PXD069603`, `PXD067220`, `PXD073844`, `PXD060403`, `PXD027163`, `PXD058618`
`PXD032078`, `PXD073775`, `PXD066134`, `PXD068989`, `PXD067225`, `PXD070295`, `PXD059137`
`PXD020389`, `PXD057003`, `PXD025753`, `PXD073734`, `PXD073484`, `PXD073798`, `PXD065838`
`PXD063016`, `PXD065615`, `PXD069676`, `PXD058858`, `PXD019152`, `PXD018299`, `PXD070789`
`PXD073754`, `PXD061601`, `PXD060435`, `PXD069387`

#### The row table for the draw

`Engine` is the **filename route** (`engine_state`) alone; the declared signal is not merged into it.
`C0 gates met` lists which of (a)–(e) pass, so a failure is legible as which gate. `Archive read` is
`yes` where at least one archive was opened and returned entries.

| # | Accession | Files | Engine (filename route) | Site | SDRF | Licence | Skipped | C0 gates met | Archive read | In widened 12 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `PXD071724` | 51 | `diann` | `candidate` | N | CC0 | 0 | abe | yes | — |
| 2 | `PXD068808` | 35 | `unclassified` | `absent` | N | CC0 | 16 | abe | — | — |
| 3 | `PXD078284` | 9 | `unclassified` | `absent` | N | CC0 | 0 | abe | — | — |
| 4 | `PXD079072` | 24 | `unclassified` | `present` | N | CC0 | 0 | abce | — | **yes** |
| 5 | `PXD077594` | 19 | `diann` | `absent` | N | CC0 | 0 | abe | — | — |
| 6 | `PXD076163` | 35 | `maxquant` | `candidate` | N | CC0 | 0 | abde | — | — |
| 7 | `PXD075792` | 23 | `unclassified` | `candidate` | N | CC0 | 18 | abe | — | — |
| 8 | `PXD030644` | 22 | `unclassified` | `absent` | N | CC0 | 0 | abe | — | — |
| 9 | `PXD071548` | 12 | `proteomediscoverer` | `absent` | N | CC0 | 0 | abe | — | — |
| 10 | `PXD065158` | 607 | `fragpipe` | `candidate` | Y | CC0 | 0 | abe | yes | — |
| 11 | `PXD075538` | 130 | `maxquant` | `present` | N | CC0 | 0 | **abcde** | yes | **yes** |
| 12 | `PXD075275` | 53 | `diann` | `absent` | N | CC0 | 0 | abe | — | — |
| 13 | `PXD070339` | 2281 | `maxquant` | `present` | N | CC0 | 8 | **abcde** | yes | **yes** |
| 14 | `PXD074990` | 485 | `maxquant` | `present` | N | CC0 | 0 | **abcde** | yes | **yes** |
| 15 | `PXD061232` | 38 | `diann` | `absent` | N | CC0 | 0 | abe | — | — |
| 16 | `PXD027328` | 100 | `unclassified` | `present` | N | CC0 | 0 | abce | — | **yes** |
| 17 | `PXD055843` | 56 | `unclassified` | `absent` | N | CC0 | 52 | abe | — | — |
| 18 | `PXD074949` | 123 | `maxquant` | `present` | N | CC0 | 0 | **abcde** | yes | **yes** |
| 19 | `PXD074673` | 12 | `diann` | `absent` | N | CC0 | 0 | abe | — | — |
| 20 | `PXD070994` | 75 | `maxquant` | `absent` | N | CC0 | 0 | abde | — | — |
| 21 | `PXD069668` | 179 | `diann` | `candidate` | N | CC0 | 5 | abe | yes | — |
| 22 | `PXD067153` | 21 | `proteomediscoverer` | `absent` | Y | CC0 | 0 | abe | — | — |
| 23 | `PXD074126` | 3 | `unclassified` | `absent` | N | CC0 | 0 | abe | — | — |
| 24 | `PXD060627` | 22 | `unclassified` | `absent` | N | CC0 | 0 | abe | — | — |
| 25 | `PXD027330` | 100 | `maxquant` | `absent` | N | CC0 | 0 | abde | — | — |
| 26 | `PXD044834` | 60 | `no_processed_output` | `absent` | N | CC0 | 0 | abe | — | — |
| 27 | `PXD074538` | 11 | `proteomediscoverer` | `absent` | N | CC0 | 0 | abe | — | — |
| 28 | `PXD073869` | 62 | `diann` | `absent` | N | CC0 | 0 | abe | — | — |
| 29 | `PXD066132` | 21 | `proteomediscoverer` | `absent` | N | CC0 | 0 | abe | — | — |
| 30 | `PXD069603` | 68 | `unclassified` | `absent` | N | CC0 | 0 | abe | — | — |
| 31 | `PXD067220` | 21 | `proteomediscoverer` | `absent` | Y | CC0 | 0 | abe | — | — |
| 32 | `PXD073844` | 5 | `unclassified` | `candidate` | N | CC0 | 0 | abe | — | — |
| 33 | `PXD060403` | 35 | `unclassified` | `absent` | N | CC0 | 0 | abe | — | — |
| 34 | `PXD027163` | 100 | `maxquant` | `present` | N | CC0 | 0 | **abcde** | — | **yes** |
| 35 | `PXD058618` | 8 | `proteomediscoverer` | `absent` | N | CC0 | 0 | abe | — | — |
| 36 | `PXD032078` | 112 | `maxquant` | `present` | N | CC0 | 0 | **abcde** | yes | **yes** |
| 37 | `PXD073775` | 32 | `diann` | `absent` | N | CC0 | 0 | abe | — | — |
| 38 | `PXD066134` | 9 | `proteomediscoverer` | `absent` | N | CC0 | 0 | abe | — | — |
| 39 | `PXD068989` | 394 | `unclassified` | `candidate` | Y | CC0 | 27 | abe | yes | — |
| 40 | `PXD067225` | 62 | `proteomediscoverer` | `absent` | Y | CC0 | 0 | abe | — | — |
| 41 | `PXD070295` | 5 | `unclassified` | `absent` | N | CC0 | 0 | abe | — | — |
| 42 | `PXD059137` | 3684 | `unclassified` | `absent` | N | CC0 | 2 | abe | yes | — |
| 43 | `PXD020389` | 100 | `no_processed_output` | `absent` | N | CC0 | 0 | abe | — | — |
| 44 | `PXD057003` | 15 | `no_processed_output` | `absent` | N | CC0 | 0 | abe | — | — |
| 45 | `PXD025753` | 51 | `unclassified` | `candidate` | N | CC0 | 0 | abe | — | — |
| 46 | `PXD073734` | 67 | `unclassified` | `absent` | N | CC0 | 0 | abe | — | — |
| 47 | `PXD073484` | 5 | `unclassified` | `absent` | N | CC0 | 0 | abe | — | — |
| 48 | `PXD073798` | 63 | `diann` | `absent` | N | CC0 | 0 | abe | — | — |
| 49 | `PXD065838` | 22 | `proteomediscoverer` | `absent` | N | CC0 | 0 | abe | — | — |
| 50 | `PXD063016` | 8 | `unclassified` | `absent` | N | CC0 | 0 | abe | — | — |
| 51 | `PXD065615` | 18 | `unclassified` | `absent` | N | CC0 | 6 | abe | yes | — |
| 52 | `PXD069676` | 15 | `unclassified` | `candidate` | Y | CC0 | 0 | abe | — | — |
| 53 | `PXD058858` | 35 | `unclassified` | `absent` | N | CC0 | 0 | abe | yes | — |
| 54 | `PXD019152` | 10531 | `maxquant` | `present` | N | CC0 | 0 | **abcde** | yes | **yes** |
| 55 | `PXD018299` | 39 | `maxquant` | `present` | N | CC0 | 0 | **abcde** | — | **yes** |
| 56 | `PXD070789` | 10 | `maxquant` | `present` | N | CC0 | 0 | **abcde** | — | **yes** |
| 57 | `PXD073754` | 32 | `diann` | `absent` | N | CC0 | 0 | abe | — | — |
| 58 | `PXD061601` | 100 | `unclassified` | `candidate` | N | CC0 | 0 | abe | — | — |
| 59 | `PXD060435` | 75 | `maxquant` | `present` | N | CC0 | 6 | **abcde** | yes | **yes** |
| 60 | `PXD069387` | 3 | `unclassified` | `absent` | N | CC0 | 0 | abe | — | — |

**Every one of the sixty is CC0 with a resolvable organism, so C0(a), (b) and (e) never bind in this
draw** and the gate is decided entirely by (c) and (d).

#### Guards: none raised, and the bound on what that licenses

**Zero raises, across all four guards and both further raise routes, over 60 rows and 30 archives
opened.** No read failed; no listing failed. The `skipped` column is 140 entries and every one of
them is a *decision not to look*, never a failed look: **104** `instrument format, not listed` and
**36** `beyond the limit of 3`, with **0** `unreadable`.

**What that licenses is bounded by archive size, and the bound is measured rather than assumed.** All
**30** archives opened are **above 64 KiB** — none at or below it. Guard 2 is unreachable on the
first read (l.406) when `size <= 65536`, so a draw containing small archives would have had a blind
spot on that call; this draw contains none, and all **14** rows carrying an archive sit inside the
bound. The zero is therefore informative for every archive this run touched.

**The stated bound is narrower than the function, and this was verified rather than reasoned.** Guard
2 also sits on the directory read at l.426, where `start` is `cd_off`. Offline, against zips built by
`zipfile` and a stub that answers 200 to every ranged request: a **>64 KiB** archive raises on call
**#1**, and a **<64 KiB** archive passes call #1 with `start=0` and raises on call **#2**. The
uncovered case is therefore not *small archives* but an **empty** zip under 64 KiB, where `cd_off` is
0 and `declared` is 0 and there is nothing to get wrong. `tests/test_deposit_survey.py` l.495 already
pins the second call — it uses a two-entry zip, which is under the tail — so the repository's guard-2
test and this run's archives exercise **different call sites**, and neither alone covers both.

#### Two counts, kept apart

**Neither is *the fourteen recomputed*.** The old parser could not distinguish a read that returned
nothing from a read that failed, so the widened draw's 14 counted only reads that **returned
entries**; the guarded parser separates the two and there is no single successor figure.

| | Count | Of the 12 shared rows |
|---|---|---|
| (i) rows whose state came from a **successful** archive read | **14** of 60 | **7** |
| (ii) rows where a read was **attempted and failed** | **0** of 60 | **0** |

A third figure is reported because (i) is the weaker reading of *depends on*: of the 14, **11** would
classify differently with the archive-derived entries removed — for the other three the archive
confirmed a state the file listing already gave. Among the 12 shared rows the two readings coincide
at **7**.

**Those two figures land on the widened draw's 14 of 60 and 7 of the 12 exactly.** That is
corroboration, not confirmation: the widened draw never recorded *which* 14, so the sets cannot be
compared and the agreement could be coincidence over a different fourteen.

**The per-archive comparison Step 3 asked for is not computable, and that is a property of the record
rather than of this run.** *Which archives previously contributed nothing and now yield entries, and
the reverse* requires the widened draw's per-archive outcomes, and it recorded no archive names at
all — not for the 48, and not for the 12. Only the aggregate survives the comparison.

#### C0: no verdict moved, and the pair of counts is a reading difference

**Among the twelve rows shared with the widened draw, the count passing C0 is 12 under the reading
the widened draw used, and 10 under the filename route alone.** Two rows carry the difference:
`PXD079072` and `PXD027328` both read `engine_state` = `unclassified` and so fail C0(d) on the
filename route, while both declare **MaxQuant** on the project record and so pass it under the
either-signal disjunction that § *Widened draw* → *The classified 60* applied to its own engine
tally (*counting a deposit MaxQuant if either signal says so*).

**Neither is a change, and three measurements establish that rather than one argument:**

| # | Measurement | Result |
|---|---|---|
| 1 | `ENGINE_MARKERS` and `SITE_TABLE_MARKER` diffed across `c8bd02d`→`c167fc5` | **byte-identical**; the classification rule did not move |
| 2 | `updatedDate` for both deposits | **2026-05-30** and **2021-07-15** — neither was touched between the two runs |
| 3 | archive dependence of both rows | **zero** archive-derived entries, **zero** skipped reads — defect 2 could not have reached either |

So both rows read `unclassified` on the filename route at the widened draw too, and that section's
*Every one is … MaxQuant* was already resting on the declared signal for these two when it was
written. **The disjunction is not settled here and the signals are not merged** — it is pre-registered
work for the head of the C1-scoring turn (§ *C3 amended a third time* → *They disagree twice and one
of those matters*). What is recorded is that two of the twelve
turn on which signal C0(d) reads, which is why the count is reported as a pair and not as a number.
**Settled 2026-08-12 in favour of the filename route — § *Settling C0(d)'s reading rule* carries the
decision and the recount; the pair above is superseded by the single count there, and this paragraph
is left standing unedited as the state before it.** **And that count is itself superseded by
§ *The MaxQuant matcher*, 2026-08-12, which corrected the matcher the filename route runs on.**

**No candidate's C0 verdict changed in either direction.** No C1 scoring, ranking, shortlist or
admission was performed.

#### An instrument finding the run surfaced: the declared signal is weaker on the survey path

**The two paths read `softwares` from different endpoints and they do not agree.** `search`
(l.269–278) reads the **search** endpoint; `classify` (l.559) reads the **project record**. Measured
over all sixty: **27 of 60** rows carry no declared software on the survey path, and **17 of those 27
declare one on the project record** — always in that direction, never the reverse. `PXD079072` is one
of the seventeen.

**This is recorded and not acted on.** It bears directly on the deferred disjunction, since the
declared half of it is under-populated by 17 rows on the path that draws the sample, and settling
that is not this turn's work. Two further consequences are named without being measured: the
declared-software census at § *The declared-software census over the whole pool* was taken *from
search alone* and may under-count for the same
reason, and this draw's 45% empty rate against that census's 15.6% *declaring nothing* is a gap too
large to be sampling alone — but the draw is a rank-biased round-robin and not a uniform sample of
the 450, so the two rates are not directly comparable and **no re-measurement was made.**

**C0(b) is not evaluable from the survey path at all**, established the same way: the search
endpoint has **no `license` field**, so no change to `search` could supply it. The licences in the
table above come from one project-record read per drawn accession — the same read `classify` makes,
issuing no query and so unable to widen the draw.

#### The pre-registered predictions, against the measurement

| | Predicted | Measured | |
|---|---|---|---|
| (a) shared rows changing in any cell | **0**, band 0–1 | **0** | hit |
| (b) guard 2 raises | **0** | **0** | hit |
| (c) guard 4 raises | **0** | **0** | hit |
| (c) guard 3 raises | **0**, band 0–1 | **0** | hit |
| guard 1, and the unnumbered l.409 | **0**, and 0 band 0–1 | **0**, **0** | hit |
| (d) rows shared with the widened draw | **12**, band 10–12 | **12** | hit, exactly |
| rows inside guard 2's first-read bound | **15**, band 10–25, low confidence | **14** | inside band, off by one |

**Six of seven were predicted from the host and all six hit.** The two 206s with exact
`Content-Range` measured before the run carried (b), (c) and guard 1; the shared identity of the
index across hours carried (d). **The one prediction reasoned from a recorded aggregate rather than
from the host — rows inside the bound, inferred from *14 of 60 depend on `archive_entries`* — is the
one that missed**, by one, in the direction the inference's own weakness predicted: 14 counted reads
that returned entries and was a lower bound on reads attempted, and the attempted count turned out to
equal it because nothing failed.

**One prediction cannot be scored and is not.** *(a)* was predicted over cells the widened draw
recorded, and the two rows that turned out to matter are exactly the ones whose recorded cell —
*MaxQuant* — is ambiguous between the two signals. Under the filename route the pair reads as two
changed cells; under the disjunction as none. Measurements 1–3 above show neither is a movement, so
**0** is entered, but it is entered on the strength of those three and not on the cell comparison.

#### What this run did not cover

**Coverage is unchanged at page 0 per term** — no term added, no cap raised, no `size` changed, and
the tails of `diGly`, `GlyGly` and `ubiquitin remnant` are as unseen as before. **The 48 rows in this
draw only are recorded but not compared**, having no counterpart. **The 48 unrecorded members of the
widened sixty stay unrecoverable** — this run does not reconstruct them and no attempt was made to.
**The guards were exercised offline and by absence, not in anger**: no archive in this draw raised
one, so the run tests that the guarded parser does not raise spuriously and says nothing about how it
behaves against a server that does ignore `Range`. And **`skipped` records the exception type, not
which guard fired** — `expand_archives` l.521 writes `unreadable ({type})` and all four guards raise
`RuntimeError`, so had a guard raised, *which one* would have needed a targeted re-read to recover.
The analysis carried that re-read path and it ran zero times. That gap is left open rather than
closed, because closing it is a change to `bzk/` this run did not require.


### Settling C0(d)'s reading rule, 2026-08-12

**The consequences are written down and committed before the decision, in their own commit.** C0(d)
reads two engine signals — the filename route in `engines`, and PRIDE's project-level `softwares`
list. The widened draw counted a deposit MaxQuant if **either** says so, and it adopted that
disjunction **after** the two signals were seen to disagree on `PXD074126`. That is choosing a rule
from its result, which is the shape this project refuses, so the rule is settled here on its merits.
**This section scores nothing.**

#### C0(d) as pre-registered, quoted before anything is amended

From § *Pre-registration: criteria for a second deposit, 2026-08-12* → *C0 — admissibility, hard
gates; any failure excludes and is recorded*, row **d** (l.3847 at `188d618`):

> | d | **MaxQuant** | The two written adapters are MaxQuant; DIA-NN, FragPipe and Spectronaut are v0.2 by § *Explicitly deferred*. A non-MaxQuant deposit is excluded **for this survey only** and recorded with its engine |

**The gate names no signal.** The reading rule is therefore *underdetermined* by the text rather than
contradicted by it, which is why this is a settlement and not a correction.

#### What the record can and cannot settle, verified rather than assumed

**The record carries one signal per row, not two.** The sixty-row table's header (l.4543) is
`| # | Accession | Files | Engine (filename route) | Site | SDRF | Licence | Skipped | C0 gates met | Archive read | In widened 12 |`
— eleven columns, none of them declared software. The declared signal appears only in prose, and
names exactly two accessions: `PXD079072` and `PXD027328`.

**Two facts computed from the record, not carried forward:** all sixty rows pass C0(a), (b) and (e),
and exactly **12** rows are `site=present` — the same twelve marked *In widened 12*. So C0 over the
sixty is decided entirely by (c) ∧ (d), (c) restricts it to those twelve, and **the recount over the
sixty is the count over these twelve**. Nothing outside them can be admitted by any reading.

#### The permitted re-read, and what it found

`classify()` over the two accessions the record names as disagreeing — no query issued, no candidate
outside the pinned sixty touched. The `--classify` CLI branch invokes exactly this function but
prints neither `software` nor `license` (l.612–622), and the declared list is what the question
needs, so the function was called directly.

| | `PXD079072` | `PXD027328` |
|---|---|---|
| declared (`softwares`, project record) | `MaxQuant` | `Andromeda`, `MaxQuant` |
| `engines` (filename route) | `()` | `()` |
| `ENGINE_MARKERS['maxquant']` suffix hits | **none** | **none** |
| marker *stem* present, suffix rule misses it | none | **`modificationSpecificPeptides_ntermUb.txt`** |
| MaxQuant parameter file | `mqpar.xml` | `mqpar.xml`, `mqpar_DP.xml` |
| MaxQuant-convention site table | `GlyGlySites.txt` | `GlyGly__K_Sites.txt`, `Phospho__STY_Sites.txt` |

**The hypothesised failure mode is not demonstrated on either disputed row.** The case against a
project-level signal is that a deposit can declare MaxQuant for one part of its pipeline while the
site table came from another tool. On these two rows the file-level evidence *corroborates* the
declaration rather than conflicting with it: both carry MaxQuant's own parameter file, both carry
site tables in MaxQuant's `…Sites.txt` convention, and `PXD027328` carries a genuine MaxQuant table
name that the suffix rule misses only because the submitter appended `_ntermUb` before the
extension. **So the disagreement on these two rows is a matcher gap, not a signal conflict.** That is
established by the re-read; it is not established that no row anywhere has a genuine conflict.

#### The consequence table — every reading, by accession, before the choice

The twelve, in the record's draw order. **Admits** means the reading passes C0(d) for that row and
so admits it through C0 entirely.

| Reading | Admits | Count | Drops |
|---|---|---|---|
| **(a)** filename route alone | all but the two below | **10** | `PXD079072`, `PXD027328` |
| **(b)** declared software alone | *not computable* | **—** | *not computable* |
| **(c)** either — union, the current rule | all twelve | **12** | none |
| **(d)** both — intersection | *not computable* | **—** | *not computable* |
| **(e)** filename decides, declared corroborates | all but the two below | **10** | `PXD079072`, `PXD027328` |

The ten that every computable reading admits: `PXD075538`, `PXD070339`, `PXD074990`, `PXD074949`,
`PXD027163`, `PXD032078`, `PXD019152`, `PXD018299`, `PXD070789`, `PXD060435`.

**(b) and (d) are not computable, and the reason is a property of the record.** Both need the
declared signal for all twelve; the record carries it for two. Re-reading the other ten is outside
this turn's bound, which permits `--classify` only over accessions the record names as disagreeing.
What the record *does* support is a bound: **(b) admits between 2 and 12** — at least the two
disputed rows, which declare MaxQuant — and **(d) admits at most 10**, since it is a subset of (a).
Neither bound separates the readings, so **no count backs the decision on (b) or (d)**; they are
decided on argument below and that is stated rather than disguised.

**One thing is known and is not usable, and is recorded as such rather than quietly relied on.** The
turn that produced the re-draw measured the declared signal for all sixty and did not write it into
this document; that measurement is why (b) and (d) are known to *differ* from (c) and (a) rather than
merely possibly differing. A figure that exists only inside a run is exactly what § *Re-draw* was
written to stop being relied on, so it is named here and **entered nowhere**. The decision below does
not rest on it.

#### Predicted, before the recount

The record holds the material for three readings, so these are a check on arithmetic and not a
forecast: **(a) 10**, **(c) 12**, **(e) 10**, each over the sixty and each equal to its count over the
twelve. **No prediction is made for (b) or (d)** — the record does not carry the signal, and a
predicted count with no instrument behind it is the shape § *Predictions, and where none is made*
forbids. No prediction is made about what any C1 scoring would rank; none is performed.

**The consequences above were known, in writing and in a prior commit, when the reading was chosen.**

#### The decision — (e), filename decides and declared corroborates

**Chosen: (e).** The rule as amended is at § *Pre-registration: criteria for a second deposit* →
*C0(d)'s reading rule, settled* and is not restated here. Each of the other four is refused on a
stated ground, and the grounds are the repository's own commitments rather than preferences.

**The gate's own text is textual support for a file-level route, and it is suggestive rather than
decisive.** C0(d)'s justification is *"The two written adapters are MaxQuant"* — a claim about what
the platform can **read**, and an adapter consumes a file, not a project record. But the row names no
signal, and *recorded with its engine* is agnostic about how the engine is determined. **Calling this
suggestive rather than decisive is itself part of the decision**: if the text were decisive, the
union would be a *contradiction* of C0 and this would be a correction rather than a settlement, and
reading suggestive evidence as decisive is the same over-reach that produced the post-hoc disjunction
in the first place.

| Reading | Refused because |
|---|---|
| **(b)** declared alone | A project-level list cannot support *this deposit's site table is MaxQuant output*. Choosing it would make C0(d) a test of submitter metadata discipline rather than of what an adapter can read — the opposite of the gate's stated justification. **No count backs this; it is refused on argument.** |
| **(c)** either (the rule in force) | Same defect, weakened but not removed: the union lets a declaration admit a deposit **by itself**, so a multi-tool pipeline declaring MaxQuant anywhere passes C0(d) with no MaxQuant-shaped file at all. The union has no defence against that case. It is also the rule chosen from its own result. |
| **(d)** both | Lets an **absence** veto. A deposit declaring nothing is *not stated*, not *not MaxQuant*, and this repository models that distinction deliberately. A veto on absence asserts what the data cannot support, facing the other way. **No count backs this; it is refused on argument.** |
| **(a)** filename alone | Right about which signal decides, wrong about what to do with the other. It **discards** the declared list — including on the two rows where the re-read shows the declaration is correct and the matcher is not. Discarding the signal that exposed the gap is *hide* where this project says *flag*. |

**(a) and (e) admit the same rows.** The whole difference is that (e) keeps the declared list recorded
and reported. That is the difference between a gate that is silently under-inclusive and one that is
under-inclusive **in the open**, and it is the reason (e) is chosen over the reading that would have
produced an identical count for less work.

**The choice was not made by which reading admits more, and not by which is fewer lines.** (e) admits
**10**, fewer than the **12** the rule in force admits — the chosen reading is the more restrictive of
the two computable ones. And (e) is strictly more work than (a) for the same count, since it requires
the declared list to be carried and displayed. **The consequences were in writing and in commit
`fd9782c` when the choice was made**, which is the condition this section exists to satisfy.

#### What (e) costs, named rather than discovered later

**(e) drops two deposits a MaxQuant adapter would very likely read.** `PXD079072` and `PXD027328`
both carry `mqpar.xml`, both carry site tables in MaxQuant's own `…Sites.txt` convention, and
`PXD027328` carries `modificationSpecificPeptides_ntermUb.txt` — a MaxQuant table name the suffix
rule misses only because a suffix was appended before the extension. **These are false negatives
produced by `ENGINE_MARKERS`, not by the reading rule.**

**The rule is not bent to cover them.** Widening the matcher to admit them would be choosing the
matcher from the rows it needs to admit, which is the same move as the post-hoc disjunction this
section was written to undo — and `sites.txt` was removed from `ENGINE_MARKERS` deliberately, so
re-admitting it would reopen a closed defect. The gap is recorded here as a finding and **no constant
is changed this turn**. What (e) guarantees is that the declared list stays visible on both rows, so
the gap reads as a gap rather than as an absence of evidence.



#### The recount under (e), predicted beside measured

| Reading | Predicted | Measured |
|---|---|---|
| (a) filename alone | 10 | **10** |
| (b) declared alone | *none made — the record does not carry the signal* | *not computable* |
| (c) either | 12 | **12** |
| (d) both | *none made — the record does not carry the signal* | *not computable* |
| **(e) chosen** | **10** | **10** |

**Under the settled rule, 10 of the sixty pass C0**: `PXD075538`, `PXD070339`, `PXD074990`,
`PXD074949`, `PXD027163`, `PXD032078`, `PXD019152`, `PXD018299`, `PXD070789`, `PXD060435`. `PXD018299`
is the anchor deposit and a consistency check rather than a candidate, so **nine are new**.

**Superseded 2026-08-12 — the matcher this count was computed with was
wrong, and § *The MaxQuant matcher* carries the corrected count.** The reading rule settled
here is unchanged; what changed underneath it is what counts as a MaxQuant filename. This
paragraph stands as the state before that correction.

`PXD079072` and `PXD027328` are excluded, each **on C0(d) alone** — every other gate passes on both —
and each is recorded with its declared list and with the matcher gap that produced the exclusion, per
clause 2 of the settled rule.

**This is a recount, not a scoring.** The count moves off twelve, so the turn ends here: **no C1
scoring, no ranking, no shortlist, no admission, no curation record.**

**No standing table required an edit, and that is a consequence of the reading rather than a
convenience.** The re-draw's sixty-row table computed its `C0 gates met` column on the filename
route, so it already encodes (e) exactly — all ten `abcde` rows are the ten above. Had (c) been
chosen, two cells would have had to change in a table this turn is not permitted to edit, which is
itself a small argument that the record was already written against the reading the gate's text
supports. The baseline, re-run, widened-draw and re-draw tables all stand unedited.


### The MaxQuant matcher, derived from the tool and registered before it was applied, 2026-08-12

**This is instrument implementation, not criteria.** C0(d)'s text is MaxQuant and its settled reading
makes the filename route decide; *what counts as a MaxQuant filename* is the matcher, the same
distinction C0(c) and `SITE_TABLE_MARKER` already carry. **No criterion is amended.** C0(a)–(e)
including (d) and its reading, and C1–C4, are unchanged.

**The danger is the point, so the rule is derived before any deposit is consulted.** Two deposits are
known to be dropped and known to be MaxQuant. A matcher tuned until they pass would be a matcher
chosen by the rows it must admit — the move § *Settling C0(d)'s reading rule* undid. So the marker
list and the match form below come from MaxQuant's documentation, and the consequences are measured
afterwards and accepted whatever they are.

#### Source

| Claim | Source |
|---|---|
| The result tables MaxQuant writes | Cox Labs, *Output Tables* — `https://cox-labs.github.io/coxdocs/output_tables.html` |
| They are written to `combined/txt` | Cox Labs, *First steps with MaxQuant* — *"All result files will appear in the folder `…\combined\txt` as tab-delimited text files."* |
| `mqpar.xml` is MaxQuant's parameter file | Cox Labs, *Download & Installation* — *"pre-configure the `mqpar.xml` file in MaxQuant GUI"*; created by `MaxQuantCmd.dll --create new_mqpar.xml` and consumed by `MaxQuantCmd.dll mqpar.xml` |

**`experimentalDesignTemplate.txt` is named nowhere in the pages read and is therefore not
included**, though it is a name this instrument's author has seen in deposits. That is the rule Step
1 sets and it is applied against interest.

#### Which documented names are markers, and which are refused

| Documented name | Marker? | Why |
|---|---|---|
| `proteinGroups.txt` | **yes** | already; distinctive |
| `evidence.txt` | **yes** | already; kept unchanged |
| `modificationSpecificPeptides.txt` | **yes** | already; distinctive |
| `msms.txt` | **yes** | already |
| `allPeptides.txt` | **yes** | already |
| `msmsScans.txt`, `msScans.txt`, `mzRange.txt`, `aifMsms.txt` | **yes — added** | documented `combined/txt` tables, and distinctive: no other tool writes these names |
| `mqpar.xml` | **yes — added** | see below |
| `peptides.txt` | **no** | generic — the l.84–85 rule that dropped `summary.txt` and `parameters.txt`. Anybody may write `peptides.txt`, so it carries no evidence |
| `summary.txt`, `parameters.txt` | **no** | already refused at l.84–85, unchanged |
| `tables.pdf` | **no** | generic, and not a table |
| `[modification]Sites.txt` | **out of scope** | `sites.txt` was removed from `ENGINE_MARKERS` deliberately and is not re-admitted here under any spelling |

**The four scan tables are added even though they are unlikely to change anything.** Excluding a
documented, distinctive marker *because* it would not move a row would be choosing the matcher by its
consequences, which is the failure this section is written against. They are in because MaxQuant
writes them.

**`mqpar.xml` is a marker — decided explicitly.** It is MaxQuant's parameter file, no other tool
writes that name, and it is **file-level**, so it satisfies the settled reading with no project-level
inference — which is precisely what the declared `softwares` field could not offer. Three things
follow and are stated rather than discovered later:

1. **It evidences C0(d) without touching C0(c).** A parameter file is not a site-grain table. `.xml`
   is not in `_TABLE_EXTENSIONS`, so `mqpar.xml` can never become a `processed_file`, a
   `site_table` or a `site_candidate`. C0(c) is decided by `site_state` alone and is untouched.
2. **It changes what the marker table means**, from *result tables that evidence the engine* to
   *filenames that evidence the engine*. The constant's own docstring already says *filename
   markers*, so the widening is of practice rather than of the stated contract — but it is a real
   change and is named.
3. **A deposit carrying only raw files plus `mqpar.xml` will report `maxquant` rather than
   `no_processed_output`**, because `engine_state` prefers a matched engine over the no-output state.
   That is a reporting consequence with **no C0 consequence**, since C0(c) is decided separately. How
   many of the sixty it touches is measured below, not guessed.

#### The match form, bounded in both directions

**Refused: keep `endswith`.** It is defeated by a token appended before the extension —
`modificationSpecificPeptides_ntermUb.txt` does not end with `modificationSpecificPeptides.txt`.

**Refused: substring.** l.79–82 already records why: `UbPTMs_PTMs_Summary.txt` matched `summary.txt`
as a substring on this instrument's first run.

**Adopted: token-boundary containment on the stem, with the extension required to match.** For a
lowercased basename (compression suffix already stripped by `_basename`) and a marker, both split at
their last `.`: the extensions must be equal, and the marker's stem must occur in the basename's stem
with a **non-alphanumeric character or a string boundary on each side**.

**This is looser on the right and stricter on the left than `endswith`, and both directions are
bounded here rather than left to be discovered:**

| Direction | Effect | Examples |
|---|---|---|
| **newly admits** | a token appended before the extension, or a marker delimited on both sides | `modificationSpecificPeptides_ntermUb.txt`; `proteinGroups_filtered.txt`; `run1_evidence_final.txt` |
| **stops admitting** | a marker run into a preceding alphanumeric with no separator | `endswith` admits `foobarproteingroups.txt`; the token form does not |

~~**What it would falsely admit** is the same class `endswith` already exposes, differently shaped:
any file whose stem carries a marker as a delimited token and whose extension matches —
`my_evidence_table.txt` from a non-MaxQuant pipeline would read `maxquant`. `evidence` is the weakest
marker on that test and is kept only because it is already in force and its removal is not this
turn's question.~~

**Corrected 2026-08-12 — the struck text describes the *registered* form, which was tightened before
it shipped, and its example is false against the code.** The rule as implemented **anchors**: the
marker's stem must *begin or end* the basename's stem, not merely sit between two separators. This
block sat next to the tightening that superseded it and still stated the looser rule, which matters
because *what it would falsely admit* is the row a later reader consults to check the rule's reach.
Measured against the shipped matcher:

| Shape, `evidence` stem | Classifies? |
|---|---|
| `evidence.txt` — exact | **yes** |
| `supporting_evidence.txt`, `HAP1_USP18KO_evidence.txt` — ends the stem, separator before | **yes** |
| `evidence_final.txt`, `evidence_ntermUb.txt` — begins the stem, separator after | **yes** |
| `my_evidence_table.txt`, `a_evidence_b.txt` — **in the middle** | **no** |
| `myevidence.txt`, `evidencetable.txt` — run into an alphanumeric | **no** |
| `evidence.tsv` — wrong extension | **no** |
| `evidence.txt.gz` — one compression wrapper stripped | **yes** |

**So the exposure is end-anchored, not *anywhere between separators*.** A non-MaxQuant
`supporting_evidence.txt` would read `maxquant`; `my_evidence_table.txt` — the example the struck text
gave — would not, because excluding the middle is exactly what the tightening was for. `evidence` is
still the weakest marker on that narrower test, and is kept in force: **whether it should be a marker
at all is not reopened here.**

**What it must not stop admitting is the anchor.** `PXD018299` — already ingested — deposits
`HAP1_USP18KO_proteinGroups.txt`. The marker is preceded by `_`, a non-alphanumeric, so it still
matches. **A form that dropped it would be a worse failure than any false positive**, and it is
pinned by a test that fails if the boundary rule is tightened to exact equality or to prefix-only.

#### The other four engines are out of scope, and the reason is not convenience

`ENGINE_MARKERS`' four non-MaxQuant entries keep `endswith`, unchanged. Three reasons:

1. **C0(d) is the MaxQuant gate.** DIA-NN, FragPipe, Spectronaut and Proteome Discoverer gate
   nothing — they are v0.2 by C0(d)'s own text. Re-matching them would move recorded `engine_state`
   cells with no criterion consequence.
2. **Their markers are structurally different and a token form has no single meaning across them.**
   `.pdresult` and `.msf` are bare extensions with no stem; `_report.xls` is an extension marker
   carrying a leading separator, written for `endswith`; `report.pr_matrix.tsv` carries dots inside
   its stem. One rule across those four shapes would be four rules in a trench coat.
3. **The defect is demonstrated only for MaxQuant.**

**The exposure named against them is real, pre-existing, and left standing rather than fixed:** under
`endswith`, `report.tsv` matches any `*_report.tsv` and `peptide.tsv` any `*peptide.tsv`. Recording it
is not fixing it, and fixing it is not this turn's brief.

#### Predicted, before the rule was applied

| Quantity | Predicted | Reasoning |
|---|---|---|
| rows of the sixty changing **engine state** | **6**, band 3–12 | `mqpar.xml` is the only addition likely to move anything. The two disputed rows carry it; how many of the other 48 non-MaxQuant rows do is not knowable from the record. The four scan tables should move **0**, since a deposit carrying `msmsScans.txt` almost certainly carries `msms.txt` already |
| rows changing **C0 verdict** | **+2, and 0 removals** — 10 → **12** | Only `site=present` rows can pass C0 and there are exactly twelve; ten already pass, so the only possible admissions are `PXD079072` and `PXD027328` |
| direction | **admission** | but a **removal is mechanically possible** and is named in advance: the left-boundary tightening drops any row whose only MaxQuant marker is run into a preceding alphanumeric. `PXD018299`'s is separator-preceded and safe; the other nine are not checked before the run |
| rows moving `no_processed_output` → `maxquant` | **0–1** | three rows are `no_processed_output`; a deposit with no tables but a deposited `mqpar.xml` is uncommon |

**No prediction is made about what any C1 scoring would rank; none is performed.**

#### The registered form was tightened before it was applied, and an existing test is why

**Registered above as *token-boundary containment*; implemented as *anchored* containment.** The
registered form allowed a marker's stem anywhere between two non-alphanumerics, which classifies
`prefix_proteinGroups.txt_suffix.txt` — the exact shape
`test_an_engine_marker_in_the_middle_of_a_name_does_not_classify` was written to forbid. **The rule
was tightened to fit the guard rather than the guard weakened to fit the rule**: the marker's stem
must now *begin or end* the basename's stem, not merely sit inside it. That existing test passes
unedited, which is the strongest available evidence that this matcher was not shaped by the rows it
had to admit.

**One consequence of the tightening, correcting the registration above:** `run1_evidence_final.txt`
was given there as an example of a name the new form would newly admit. Under the anchored form it is
**not** admitted — the marker neither begins nor ends the stem. The registered claim was wrong in the
permissive direction and is corrected here rather than quietly dropped.

#### What changed over the pinned sixty

File listings are the pinned run's own persisted output, so the only thing varying is the matcher and
a change cannot be deposit drift. **All three changed rows were then re-verified live with
`classify`** — no query, no candidate outside the sixty — and all three agree.

| Accession | Engine state | Admitted by | C0 |
|---|---|---|---|
| `PXD079072` | `unclassified` → **`maxquant`** | `mqpar.xml` | `abce` → **`abcde`** — admitted |
| `PXD027328` | `unclassified` → **`maxquant`** | `modificationSpecificPeptides_ntermUb.txt` **and** `mqpar.xml`, `mqpar_DP.xml` | `abce` → **`abcde`** — admitted |
| `PXD058858` | `unclassified` → **`maxquant`** | `DDA_ArgC_mqpar.xml`, `DDA_LysCArgC_mqpar.xml` | `abe` → `abde` — **still excluded** |

**Nothing else moved.** No `site_state` changed, the three `no_processed_output` rows all stayed
`no_processed_output`, and **the left-tightening removed nothing** — every change is a gain.

**`PXD058858` is the admission nobody predicted, and it is recorded because it is evidence.** It
deposits two MaxQuant parameter files under prefixed names and reads `maxquant` for the first time.
It does **not** enter C0: it has no site-grain table, so it fails C0(c) and stays out. A rule reverse-
engineered from the two disputed rows would not have reached a third deposit that helps nobody's
case, and would not have reached one that gains C0(d) and is excluded anyway.

**The two changes are separable and only one of them is load-bearing here:**

| Change | Rows it moves on its own |
|---|---|
| the anchored match form | **1** — `PXD027328`, which `mqpar.xml` independently rescues |
| the marker additions | **3** — all three, and **all three via `mqpar.xml`** |
| the four documented scan tables | **0** |

**So the match-form change alters no C0 verdict on its own within this sixty, and the four scan
tables alter nothing at all.** Both are kept because MaxQuant writes those names and `endswith` is
defeated by an appended token — justified by the tool, not by an effect here. Saying so is the
point: a matcher that only ever earns its keep on the rows that prompted it is the one to distrust.

#### Predicted beside measured

| Quantity | Predicted | Measured | |
|---|---|---|---|
| rows changing engine state | **6**, band 3–12 | **3** | inside the band, at its floor |
| rows changing C0 verdict | **+2, 0 removals** | **+2, 0 removals** | hit |
| C0 count | 10 → **12** | 10 → **12** | hit |
| direction | admission | admission | hit |
| `no_processed_output` → `maxquant` | 0–1 | **0** | hit |

**The engine-state miss is evidence about what `unclassified` means in this pool.** The prediction of
six assumed that a fair share of the `unclassified` rows were mis-matched MaxQuant deposits. Three
were. The rest are `unclassified` because they carry **no recognisable processed output at all** —
a genuine absence of engine evidence rather than a matcher gap — which is the same distinction
`engine_state` was split three ways to preserve, now measured rather than asserted. The prediction
mistook a reporting state for a defect rate.

#### The recount — 12 of the sixty pass C0

`PXD079072`, `PXD075538`, `PXD070339`, `PXD074990`, `PXD027328`, `PXD074949`, `PXD027163`,
`PXD032078`, `PXD019152`, `PXD018299`, `PXD070789`, `PXD060435`. **`PXD018299` is the anchor deposit
and a consistency check rather than a candidate, so eleven are new.**

**This is a recount, not a scoring.** No C1 scoring, no ranking, no shortlist, no admission, no
curation record. The count moved, and the turn ends at saying so.

**The count returns to twelve and that is a coincidence of arithmetic, not a restoration.** The
twelve here are not the widened draw's twelve reinstated: they are the ten the settled reading
admitted plus the two the corrected matcher recovered, and the reason they are in is now a
**file-level** marker on each rather than a project-level declaration. `PXD058858` gained C0(d) in the
same pass and is still out.

#### What this did not cover

**The four deferred engines are unchanged and their exposure stands recorded, not fixed** — under
`endswith`, `report.tsv` matches any `*_report.tsv`, `peptide.tsv` any `*peptide.tsv`, and DIA-NN's
and Spectronaut's markers **overlap on every `*_report.tsv`**, so such a file reads as two engines at
once. That overlap was found by a test assertion of mine that was wrong about the current behaviour,
and it is pinned in `tests/test_deposit_survey.py` rather than repaired.

**`evidence.txt` remains the weakest MaxQuant marker** — a non-MaxQuant `supporting_evidence.txt` or
`evidence_final.txt` would read `maxquant` — and it is left in force because removing it is not this
turn's question. *Corrected 2026-08-12: this sentence gave `my_evidence_table.txt`, which the shipped
matcher does **not** classify. The exposure is end-anchored and is bounded by measurement in* § *The
MaxQuant matcher* *→* What it would falsely admit.

**`experimentalDesignTemplate.txt` is not a marker** because the documentation pages read do not name
it, not because it was judged generic.

**The rule was derived from three documentation pages, not from MaxQuant's source.** A name MaxQuant
writes that those pages omit is not in the table and this turn does not know it is missing.




### C1 scored on what the record supports, 2026-08-12

**A partial score, and deliberately not a ranking.** C1's eleven criteria are scored only where the
record and the listings the survey already holds can settle them. **No deposit's data file is
downloaded or parsed.** No candidate is ranked, shortlisted or preferred, and **C2 is not applied** —
applying a contrast rule to a partial score would express a preference the evidence does not support.
C1's criteria and bands are unchanged.

#### Predicted, before the criteria were investigated

Registered from C1's *Tested against* column alone, before any of the platform's own code was read:

| Quantity | Predicted | Reasoning from the column |
|---|---|---|
| scorable **from the record alone** | **2**, band 1–3 | criterion 10, *SDRF present*, which the survey already carries as `has_sdrf` and the re-draw table already prints; and criterion 8, *sample-name convention*, on the guess that raw filenames in the listing carry the convention |
| unscorable **even with the file** | **3**, band 2–4 | criterion 4, since `AMBIGUOUS` is a state the platform's resolver produces rather than anything a table contains; criterion 3, which needs UniProt's reviewed/unreviewed status; criterion 2, on the guess that deciding *isoform* needs UniProt rather than the accession's own spelling |
| the remainder | scorable only **with the file** | — |

**No prediction is made about how any candidate would score on an unscorable criterion, and none
about a ranking.**

#### Scorability, criterion by criterion from the *Tested against* column

Three questions per criterion, kept apart: does the **record or a listing** settle it; does it need
the deposit's **file**; or is it **unscorable even with the file**, because what it tests is something
the platform *derives* rather than something a deposit *contains*.

| # | Criterion | From the record? | Needs the file | Unscorable even with the file |
|---|---|---|---|---|
| 1 | Multi-mapping rate (I14) | no | site table, protein-group column | no |
| 2 | Razor picks that are isoforms (I2) | no | site table, razor column | **no** — `bzk/resolve/uniprot.py` decides isoform as `"-" in requested`, from the accession's own spelling |
| 3 | Razor pick on TrEMBL despite a reviewed entry (I17) | no | site table | **yes** — `reviewed` comes from the UniProt pin, not from the deposit |
| 4 | `AMBIGUOUS` fold | no | site table | **yes** — set when UniProt returns several HGNC ids; a resolver state, in no deposit |
| 5 | Declared-quantity enum (I16) | no | headers only | **splits — see below** |
| 6 | Localisation distribution | no | site table; column name from headers, median and scale from the values | no |
| 7 | Native stoichiometry (I4) | no | headers only — `Ratio mod/base ` present or absent | no |
| 8 | Sample-name convention | no | headers | no |
| 9 | Unrecorded threshold (I16's unfired case) | no | site table values | no |
| 10 | SDRF present | **yes** | — | no |
| 11 | Design recoverable from column names | **no — decided, see below** | headers | no |

**Criterion 4 is not alone, which is why the other ten were checked rather than assumed.** Two whole
criteria and one half have its shape — testing a state the platform produces rather than one a
deposit carries. **3** joins it: `reviewed` is read from the UniProt pin. **2 does not**, against the
prediction: isoform status is decided from the accession string, so the file alone settles it.

**Criterion 5 splits, and the halves fall on opposite sides.** `QUANTITY_COLUMNS` maps
`intensity_multiplicity_summed` to the column prefix `Intensity `, so *which intensity family a
deposit offers* is readable from the headers. But the **declaration itself is a curation act**: a
deposit's table offers columns, and an `Analysis` declares which were used. No deposit states its own
declared quantity, so that half is unscorable even with the file — it does not exist until someone
curates the deposit.

**Criterion 11 is decided *not* scorable from a listing, and the reason is a deposit already in the
record.** The criterion asks whether the design is recoverable from the **columns of the quantified
table**; a listing enumerates **raw files**. Those two sets can share no member, and `PXD018299` is
the demonstration: `HANDOFF.md` records that its fourteen quantitative columns are the *proteome* run
while the curation's twelve samples are the *diGly* run, **sharing no member**, and that the mapping
"is not deducible even with §5.3's `filename_inference` basis". Scoring 11 off the listing would
answer a different question about a different set — which is the failure mode this whole exercise is
built to avoid.

**A wording discrepancy found while deciding it, recorded and not fixed.** `ONTOLOGY.md` §5.3 defines
`filename_inference` as *"Deduced from raw file naming conventions"*, while C1's criterion 11 is worded
*"Design recoverable from column names"*. In a MaxQuant table these usually coincide, because MaxQuant
names its quantitative columns after the raw runs — but they are not the same set, and `PXD018299` is
a deposit where they diverge. **C1 is not amended**: the criteria and their bands are out of scope.

#### Criterion 10 scored over the twelve — the only one the record settles

Tested against the anchor's **No**; informative if **Yes**.

| Candidate | SDRF | Point |
|---|---|---|
| `PXD079072`, `PXD075538`, `PXD070339`, `PXD074990`, `PXD027328`, `PXD074949`, `PXD027163`, `PXD032078`, `PXD019152`, `PXD018299`, `PXD070789`, `PXD060435` | **N**, all twelve | **0** |

**Zero of twelve are informative on criterion 10.** Every candidate matches the anchor, so the one
criterion the record can settle separates nothing. The criterion's own note says `sdrf` "has never
once been exercised"; after twelve candidates it still has not been, and that is now measured rather
than assumed. **Recomputed from the listings and cross-checked cell-by-cell against the re-draw
table's SDRF column — all sixty agree**, so this is the record's own figure and not a second one.

**Ten criteria are left unscored and are not estimated.** No band is inferred from a title, an
abstract or a declared-software field.

**This is not a ranking.** One criterion scoring zero across twelve candidates orders nothing, and
even a full score would not be applied here: **C2 is not applied, no candidate is shortlisted, and
none is preferred.**

#### What full scoring would cost — registered, not paid

From listings only; no file was downloaded. The criteria that need data concern the **K-GG** site
table, so that subset is registered separately from every site table of any modification.

| | K-GG site tables | All site tables |
|---|---|---|
| tables | 16 | 39 |
| candidates covered | **11 of 12** | 12 |
| distinct objects to retrieve | 16 — **4 direct files, 12 archives** | 22 — 6 direct, 16 archives |
| total bytes | **24.70 GB** | 33.58 GB |
| of which direct files | 84.7 MB | 91.7 MB |
| of which archives | **24.61 GB** | 33.49 GB |

**`PXD070789` has no K-GG site table in its listing.** It passes C0(c) on `Phospho-STY-Sites.txt`,
which is a site-grain table and satisfies the gate as written — but there is no diGly table to
measure criteria 1, 2, 6 or 9 against. That is a scorability finding about the candidate, recorded
here and not acted on.

**Three quarters of the twelve are behind an archive, and one archive is 17 GB.** `PXD019152`'s
`MaxQUANT_HpH.zip` is 16,993,871,159 bytes and holds one of its K-GG tables; `PXD032078`'s
`txt_GlyGlyKsites.zip` is 1.33 GB, `PXD060435`'s two are 0.9 GB together, and `PXD074949` spreads
three searches over 0.67 GB.

**What existing code covers, and what is new work:**

| Step | Existing? |
|---|---|
| resolve a filename to a URL | **yes** — `file_urls` |
| retrieve a **direct** file | **yes** — `bzk/sources/pride.py` `fetch_bytes`, and `fetch` to put it in the content-addressed store |
| parse a MaxQuant site table | **yes** — `bzk/adapters/maxquant.py` `read_table`, `bzk/adapters/maxquant_sites.py` |
| retrieve a table **inside an archive** | **no — new work** |
| map samples to columns | **no** — a curation record, which is a separate decision |

**The archive half is the real cost and it has two shapes.** Either **24.61 GB of whole-archive
downloads** using code that exists, or **new range-extraction code**: `archive_entries` already parses
each entry's central-directory header but **returns only the names and discards the offsets**, so
fetching one member of a 17 GB archive is reachable in principle and unwritten in fact.

**Registering this is the turn; deciding to pay it is not.** Downloading and parsing twelve site
tables is most of an ingestion, and ingestion carries its own invariants, a curation record per
deposit, and I18's export obligations. **No file was fetched, nothing entered `data/curation/`, and
no candidate was admitted.**

#### Predicted beside measured

| Quantity | Predicted | Measured | |
|---|---|---|---|
| scorable from the record alone | **2**, band 1–3 | **1** — criterion 10 | inside the band |
| unscorable even with the file | **3**, band 2–4 | **2 whole (3, 4) + one half (5)** | at the band's floor |

**Both misses came from guessing at a mechanism instead of reading it.** Criterion 8 was predicted
scorable from raw filenames; sample names are **column** names, and the listing's raw-file set can
share no member with the quantified columns. Criterion 2 was predicted to need UniProt; the accession
string settles it. **The one prediction that held did so for a reason I had actually checked** — the
survey already carries `has_sdrf` — and the two that failed were both about code I had not yet read.
The half-criterion in 5 was not predicted at all, because the prediction treated each criterion as
falling whole to one side.



### How the site tables get retrieved — decided, and nothing fetched, 2026-08-12

**This turn decides the mechanism and retrieves nothing.** No file, direct or archived; no range
request against any deposit; no extraction, parse or scoring. No code is written for the chosen
option. The decision and its reasoning are the whole output.

#### The register framed a binary, and it is not one — three corrections before choosing

**(i) A quarter of the objects cost 0.34% of the bytes, and one of the four is the anchor.** The
register carries the count and the byte total but not the per-candidate breakdown. Over the survey's
held listings:

| Candidate | Direct K-GG file | Bytes |
|---|---|---|
| `PXD079072` | `GlyGlySites.txt` | 102,731 |
| `PXD018299` | `HAP1_USP18KO_GlyGlyKSites.txt` | 2,759,052 |
| `PXD027163` | `UbiSite_GlyGly__K_Sites.txt` | 15,802,963 |
| `PXD027328` | `GlyGly__K_Sites.txt` | 65,992,977 |

**`PXD018299` is the anchor and is already ingested**, so *direct files only* reaches **three new
candidates**, not four. The remaining seven — `PXD019152`, `PXD032078`, `PXD060435`, `PXD070339`,
`PXD074949`, `PXD074990`, `PXD075538` — are reachable only through an archive, and `PXD070789` has no
K-GG table under any option.

**(ii) Five criteria need only the file's first line, which no option in the register accounts for.**
Criteria **7** (`Ratio mod/base ` present), **8** (sample-name convention) and **11** (design from
column names) are settled by the **header row** alone, as are **5**'s intensity-family half and
**6**'s column-name half. Only criteria **1**, **2**, **9** and **6**'s distribution half need the
values. A header is kilobytes.

**(iii) The range-extraction increment is larger than the register implied and smaller than "new
code" suggests — read off the parser rather than estimated.** `archive_entries`' loop unpacks
`nlen, elen, clen` from bytes 28–34 and steps past every other field. Confirmed against archives
built by `zipfile`: `compressed_size` sits at bytes **20–24** and the local-header offset at bytes
**42–46**, both already traversed and discarded. **The offset alone does not locate the data**, and
that is measured rather than argued: forcing a Zip64 entry gives a central extra length of **0**
against a local extra length of **20**, so computing the data start from the central directory lands
**20 bytes short**. The local header must be read for its own name and extra lengths. End to end —
retain the two fields, range-read the local header, compute the data start, range-read
`compressed_size` bytes, `zlib.decompress(..., -15)` — **reproduces the member exactly**, verified
offline.

**It is tens of lines, not a component.** The core is fifteen to twenty-five lines over machinery that
exists: `RangedSession`, the `chunk()` pattern in `archive_entries`, and `zlib` from the standard
library. **The honest caveat is where it grows**: Zip64 64-bit sizes in the extra field, stored
(method 0) against deflate (method 8), and refusing encrypted or data-descriptor entries rather than
mis-reading them. `archive_entries` itself grew four guards for exactly that class, so forty to sixty
lines plus tests is the realistic figure — still well short of a component.

#### The options, as six

| | Option | Bytes | Code | K-GG coverage |
|---|---|---|---|---|
| **(a)** | whole-archive download | **24.61 GB** | exists | 11 of 12 |
| **(b)** | range extraction of the member | ~ the table | **new, tens of lines** | 11 of 12 |
| **(c)** | direct files only | **84.7 MB** | exists | 4 of 12 — **3 new** |
| **(d)** | (c) first, then (a) or (b) | staged | exists, then new | staged |
| **(e)** | **header-only reads** — added here | **kilobytes** | exists for direct; (b)'s machinery for archived | criteria 7, 8, 11 and two halves |
| **(f)** | **retrieve nothing** — added here | 0 | none | none |

#### What each option buys, criterion by criterion

**The denominator is 11, not 12, for criteria 1, 2, 6 and 9** — `PXD070789` passes C0(c) on
`Phospho-STY-Sites.txt` and has no diGly table, so those four are unscorable for it under **every**
option including a full download. Criteria **3** and **4** are unscorable even with the file under
every option, so no option moves them. Criterion **10** is already scored at 12 of 12 and 0
informative.

| Option | criteria 7, 8, 11 + halves of 5, 6 | criteria 1, 2, 9 + 6's distribution |
|---|---|---|
| (a) | 11 of 12 | 11 of 12 |
| (b) | 11 of 12 | 11 of 12 |
| (c) | 4 of 12, **3 new** | 4 of 12, **3 new** |
| (e) | 11 of 12 *(4 of 12 if direct-only)* | none |
| (f) | none | none |

#### C2 cannot operate on a partial score, so (c) is weaker than its byte count suggests

C2 ranks **by C1 points**, breaking ties on *SDRF present*, then *site count ≥ 1,000*, then *smaller
download*. Three things follow, and they are not about C2's merits — C2 is unchanged:

1. **A partial score is a lower bound per candidate, and lower bounds do not order totals.** A
   candidate two points behind on the scored criteria can lead by four once the unscored ones are
   read.
2. **Under (c), seven candidates would score zero on every table-derived criterion because nothing
   was read**, not because they do not differ. Rendering an unread criterion as a zero is the shape
   I15 and I16 forbid everywhere else in this project.
3. **The tie-breaks make it worse rather than rescuing it.** *SDRF present* is **N for all twelve** —
   measured, inert. *Site count ≥ 1,000* needs the table. *Smaller download* is the only tie-break
   the record can settle, and it would rank by which deposit was cheapest to fetch. **Ranking a
   partial score would select on retrieval convenience**, which is the failure this chain has already
   undone twice.

**So no ranking happens until the score is complete across the eleven.** (c) and (d) remain usable as
*retrieval plans*; they are not usable as *selection*.

#### What (a) costs beyond bytes, measured in this container

`df` reports **29 GB available** on the filesystem carrying both the working tree and `~/.bzk-omics`.
**24.61 GB is 85% of that**, before a single table is extracted, and the writable allowance is fixed
per session — so the cost is not paid once but on every fresh container. **`PXD019152`'s
`MaxQUANT_HpH.zip` is 16,993,871,159 bytes, 69% of the archive total on its own**, and holds one K-GG
table. The ratio is the argument: (a) moves 24.61 GB to read sixteen tables whose own sizes are tens
of megabytes.

#### What (b) costs beyond the code

**`RangedSession` exists, and nothing in `tests/` exercises the live ranged path** — the parser is
tested through a fake session, and the guards were verified against constructed archives rather than
against PRIDE. **A member extractor inherits exactly that gap**: it would be green offline and
unexercised against the real server until it first runs. That is the same shape as defect 2, where a
parser returned an empty tuple because a server behaviour no test reproduced. It is a real cost and
it is not a reason to prefer (a), which carries no equivalent guarantee either — but it means the
extractor's first live run is a measurement, not a formality.

#### Decided: (b), staged by what each criterion needs, with (e) first. Never (a)

**Chosen: build the range-extraction increment on `archive_entries`, and sequence retrieval by
criterion need rather than by where the file happens to sit.** ~~Header reads first — settling
criteria 7, 8 and 11 and the two halves across all eleven at kilobytes — then the same machinery for
the full tables the value criteria need.~~

**Mispriced, corrected 2026-08-12 before the first live use.** *At kilobytes* was wrong, and the
reason is a guard this document already calls the extractor's purpose: `extract_member` verifies the
inflated bytes against the central directory's **CRC-32**, and a read stopping at the first newline
cannot verify it. So a header costs a **whole member** — ~~tens of megabytes~~ **under 3 MB, for
every archived member** — not kilobytes.

**The resolution is that the saving which matters is archive → member, not member → line.** The
archives are gigabytes and a site table is ~~tens of megabytes~~ **under 3 MB**, so extracting the
whole member and
verifying its CRC is cheap by roughly three orders of magnitude against the archive it sits in. A
partial-inflate path would buy back ~~tens of megabytes~~ **under 3 MB** out of a saving already
measured in gigabytes,
and would pay for it with the one guard that detects a **wrong answer** rather than an absent one.
**No partial path is built.**

**The magnitude was corrected again, 2026-08-12, and this correction had the direction right the
first time and the size wrong.** *Tens of megabytes* was written **before the directory reads
returned member sizes**, so it was an estimate standing in for a measurement. Measured, from the
twelve archived member rows:

| Population | Bytes | |
|---|---|---|
| the **twelve archived member rows** | **10,964,463** | 10.96 MB — the whole population, counting the duplicated artefact twice |
| the **eleven distinct artefacts**, under the shared-artefact rule | **8,291,999** | 8.29 MB — what an extraction of all of them actually transfers |
| the **four direct tables** | 102,731 · 2,759,052 · 15,802,963 · 65,992,977 | a separate population, not this one |

**The three must not be run together, and the largest archived member is 2,672,464 B — under 3 MB.**
**Not one archived member reaches 10 MB**, so *tens of megabytes* was never true of this population at
all; it was true of the **direct** tables, which is where the estimate came from and which are a
different set.

**Corrected against the instruction that asked for the correction**: *tens of megabytes* was said to
fit exactly one direct table. It fits **two** — `PXD027163`'s 15,802,963 B (15.80 MB) and
`PXD027328`'s 65,992,977 B (65.99 MB) — both inside [10 MB, 100 MB). The point survives and is
sharpened: the estimate was borrowed from a population where it holds for half the members, and
applied to one where it holds for none.

**This changes no decision, and that is said rather than left to be inferred.** (b) over (a) was
argued on gigabytes against megabytes; the archived members turn out to be **three times smaller than
the estimate**, so the comparison it rested on becomes stronger, not weaker. The bound two paragraphs
below — *even at 100 MB per member, the sixteen come to ~1.6 GB* — remains true and is now known to be
loose by roughly two orders of magnitude; it is left standing because a deliberately generous bound
does not become wrong by being generous.

**(b) over (a) is unaffected.** That choice rested on 24.61 GB of whole archives against the members
themselves. Even at 100 MB per member — well above the 66 MB of the largest *direct* K-GG table — the
sixteen come to ~1.6 GB, still an order of magnitude under 24.61 GB, so the comparison survives under
any plausible member size rather than needing the exact figures.

**What does not survive is the stage ordering, and it is void rather than wrong.** *Headers first*
was a cost argument — header reads are nearly free — and at the granularity the CRC requires they
cost exactly what the full member costs. **So the two stages are the same operation**: one pass
extracts a member, and every criterion that member can settle is settled from the same bytes. The
ordering dissolves instead of needing to be re-decided, and the corrected plan is simpler than the
one it replaces rather than a different trade.

**(a) is rejected on capacity, not on weight.** 24.61 GB against 29 GB of a per-session allowance,
re-paid every container, to read sixteen tables. **(c) alone is rejected because it cannot select** —
three new candidates chosen by which were cheapest to reach. **(f) is rejected** because criterion 10
scoring 0 of 12 leaves C1 with nothing measured, and the survey's whole purpose is the contrast the
unscored criteria carry. **(d) is superseded by the chosen staging**, which stages on the same axis
the criteria already split along instead of on the accident of archive membership.

**Not chosen by bytes alone, and what the bytes buy is stated:** (e)'s kilobytes buy three whole
criteria and two halves across eleven candidates; (b)'s further reads buy the four value criteria
across the same eleven; (a)'s extra 24.5 GB buy **nothing** that (b) does not.

#### This is recorded here rather than as an ADR, on the project's own convention

`decisions/README.md` says an ADR is a numbered, immutable record of a settled choice with what was
rejected. That much fits. **What does not fit is the subject.** Every record in `decisions/`
constrains the **platform** — storage, keys, contracts, invariants, statistics, identity. This
constrains an **operational instrument**: `bzk/deposit_survey.py`, whose own docstring states it is
not part of the platform and which nothing in `bzk/` imports. An ADR here would be the first about
something outside the platform.

Second, the whole second-deposit chain — C3's amendments, C0(d)'s reading rule, the matcher, the
scores and the cost register — is recorded in `ROADMAP.md`, and CLAUDE.md gives each fact one home.
Splitting this decision into `decisions/` would put half a chain of reasoning in each document.

**If the extractor is later promoted into the platform** — used by ingestion, or living in
`bzk/http.py` beside the Protocols — **that** is an architectural decision and **that** is when an ADR
is warranted, on the contract rather than on the survey's retrieval convenience.

**A hard constraint found while considering it, which is not the reason for the choice.** An ADR
could not have landed green this turn regardless. `tests/test_decision_index.py` pins the directory
against `decisions/README.md`, and a probe file at `decisions/0026-*.md` — written, tested, removed,
tree verified clean — failed **three** assertions: the Written-table/directory agreement in both
directions, `EXPECTED_WRITTEN_ROWS = 24`, and a **pinned status census** that the README does not
mention. Landing an ADR therefore requires editing `decisions/README.md` and
`tests/test_decision_index.py`, both out of scope this turn. **The merits decided the placement; the
probe only confirms nothing was lost by it.** `0026` remains the next free number.


### The member extractor, built and stopped at the tautology sweep, 2026-08-12

**Nothing real was extracted.** No deposit file was fetched, no network call was made to any host,
and every test serves archives built here by `zipfile`. **Nothing was pre-registered**, and the
reason is that this turn produces no number comparable against a recorded one: every new test fails
before the code exists, which is trivial rather than informative, and mutation-firing is an
obligation this project already imposes rather than a quantity to forecast.

#### Where the offsets come from

Verified against archives built by `zipfile`, reading each field and comparing it to what `zipfile`
itself reports for the same entry — not taken from a summary. The central-directory file header:

| Field | Bytes | Read before? |
|---|---|---|
| general-purpose flags — bit 0 encrypted, bit 3 data descriptor, bit 11 UTF-8 name | 8–10 | no |
| compression method — 0 stored, 8 deflate | 10–12 | no |
| CRC-32 | 16–20 | no |
| compressed size | 20–24 | no |
| uncompressed size | 24–28 | no |
| name / extra / comment lengths | 28–34 | **yes — the only fields the parser read** |
| local-header offset | 42–46 | no |

**The local header must be read even so, and that is measured rather than argued.** It carries its
**own** name and extra lengths, and they need not match the central record's: a zip64 entry gives a
central extra length of `0` against a local `20`, so a data start computed from the central directory
lands twenty bytes inside the member. Mutating the extractor to use the central figure fails
`test_the_local_headers_own_extra_length_locates_the_data`.

#### How a member is identified, and why that decided the shape

**`archive_entries` decodes names `"utf-8", "replace"`.** A member whose name is not valid UTF-8 —
the format permits it; bit 11 clear means the bytes are in the writer's own code page — comes back
carrying replacement characters. An extractor selecting by *that string* could fail to match its own
central record, or match the wrong entry where two raw names mangle alike. **That is an
identification failure between the two functions, and worse than a refusal.**

**Measured against real data before deciding**: of **18,124** archive-derived entry names in the
survey's held listings, **0** carry U+FFFD and **0** carry any non-ASCII character at all. So the gap
is **real in the format and unobserved in this sample** — which is evidence about the sample, not a
proof it cannot fire.

**Three shapes were available and a record type was chosen.** `archive_entries` has **one**
production call site — `expand_archives`, which consumes names only — and eight in tests.

| Shape | Rejected because |
|---|---|
| extend `archive_entries`' return type | makes the survey path carry records it has no use for, and changes a contract nine call sites are written against |
| a parallel function returning records | **two parses of the same central directory**, each needing its own copy of the four guards, and two copies drift — the duplication CLAUDE.md's one-home rule exists to stop |
| **a record type, chosen** | one parse; `archive_entries` becomes `tuple(m.name for m in archive_members(...))`; and the extractor takes the **record**, so it never parses a name |

**The choice was not made on call-site count** — the record type happens to touch fewest, but the
reason is one parse and exact identification. **It dissolves the identification guard rather than
adding one**: `ArchiveMember` carries `name_bytes` beside `name`, so nothing selects by the decoded
string, and the local header's name bytes are compared against the central record's to prove the
extractor is at the right member.

#### What refuses and what handles

| | Behaviour |
|---|---|
| **stored (method 0)** | **handled** — a legitimate method; refusing it would fail on a real archive for no reason |
| **deflate (method 8)** | **handled** — `zlib.decompress(..., -15)` |
| any other method | **refused**, naming the method number |
| **encrypted** (flag bit 0) | **refused** |
| **data descriptor** (flag bit 3) | **handled** — it makes the *local* header's sizes and CRC placeholders, and nothing here reads those; they come from the central record, which is authoritative under bit 3. Only the local name and extra *lengths* are read, and bit 3 does not touch them |
| **zip64 sizes** | **handled** — where a 32-bit field reads `0xFFFFFFFF` the value comes from the extra field. `MaxQUANT_HpH.zip` at 16,993,871,159 bytes is past the 32-bit ceiling, so this is certain for it rather than contingent |
| a name that does not round-trip | **not a case** — selection is by record, so the decode never participates |

**Five guards beyond the list, each found by construction rather than by design:**

| Guard | Detects |
|---|---|
| local header signature is not `PK\x03\x04` | the central directory points somewhere that is not a member |
| local name length or bytes differ from the central record's | would return **a different member's bytes under this member's name** — which no CRC check catches, because the CRC would be that member's too |
| **short local header** | found *while writing the body test*: it reached `struct.unpack` and surfaced as `struct.error`, which `expand_archives` records as `unreadable` with no sign the read was truncated |
| short body | a truncated body inflates to a shorter table that reads as a small one |
| declared uncompressed size disagrees with the inflated length | a corrupt central record, distinct from corrupt bytes |

**The CRC check is the one that differs in kind.** The four guards on the directory parse all detect
**absence or truncation**. This one detects a **wrong answer**: bytes that arrived, inflated, and are
not what the archive declares. Guard 2 — the ignored-`Range` check — now has **one home** in
`_ranged`, so the extractor inherits it rather than re-deriving it, and its bound is the same one it
has in the parser: a member whose local header sits at offset **0** cannot trip it, because the first
read starts at zero. That case is not left uncovered — the length check catches it — and both are
asserted rather than only the one that reads better.

#### Twelve guards, twelve tests, each made to fail

Every guard was mutated out in turn, **the mutation read back off disk before the run**, the suite
run, and the file reverted. All twelve fail exactly one test each and nothing else. **Two were not
covered on the first pass and both were real gaps**, not bookkeeping:

- **the declared uncompressed size** — subsumed by the CRC check in every case then constructed, so
  removing it left the suite green. Closed by an archive whose declared size is wrong while its CRC
  is left correct, which isolates the two.
- **the zip64 sentinel resolution** — the unit test covered `_zip64_values` but not the assignment
  back into the record, so removing that line changed nothing observable. Closed by building a real
  zip64 central entry: the sentinel written into the fixed record, the true value into the extra
  field, and the directory size patched to match.

#### What this does not establish

**The extractor has never read a PRIDE archive, and nothing here exercises it against a live host.**
Every test serves bytes from a `zipfile`-built archive through an injected session; `_ForbiddenRanged`
asserts that no read escapes that seam. **This is the same provenance gap `archive_entries` carried,
and that one took three turns to surface** — a parser green offline while a server behaviour no test
reproduced returned an empty tuple in the field.

**So: the first live use will be the first evidence this works against a real server, and it is not
verified against PRIDE.** Recorded here rather than assumed away, because the gap is acceptable for a
build turn only when it is written down.

#### Stopped: the tautology sweep reports eleven unclassified expressions

**`tests/test_tautology_sweep.py::test_the_pinned_multiset_has_not_changed_unreviewed` fails**, and
it is the only failing test — 531 pass, 11 skip. It names **11** matching expressions or occurrence
counts introduced by the new tests, among them
`extract_member(...) == zf.read('combined/txt/GlyGly (K)Sites.txt')`,
`member.crc32 == info.CRC == zlib.crc32(content) & 4294967295` and `got == content`.

**The sweep is doing its job and the resolution it names is out of scope.** Its failure message
directs each entry to be classified into `INSTANCES` or `PINNED` **inside
`tests/test_tautology_sweep.py`**, which this turn may not edit. The alternative — rewriting the
assertions to compare against literal displays, the convention this file already follows for the
parser test — would preserve some of them and lose others: comparing the extractor's output against
`zipfile`'s own read of the same archive **is** the reference check the tests exist for, and turning
it into a literal would discard the second implementation that makes it evidence.

**So the turn stops here rather than choosing between editing a guard it was told not to touch and
weakening the tests to get past it.** Nothing was reverted: the extractor, its twelve guards and its
tests are on the working branch, `ruff check`, `ruff format --check` and `mypy` are clean, and the
suite is green but for that one test. **It is not fast-forwarded onto `main`**, because a red suite
on `main` is exactly what the sweep exists to prevent.


### Classifying the extractor's eleven sweep matches, 2026-08-12

**The extractor turn stopped rather than weakening the assertions the sweep flagged. This turn
classifies them.** No assertion in `tests/test_deposit_survey.py` is rewritten: comparing the
extractor's output against `zipfile`'s own read **is** the reference check those tests exist for, and
replacing it with a literal display would discard the second implementation that makes it evidence.

#### Predicted, before any expression was classified

**11 to `PINNED`, 0 to `INSTANCES`.** The reasoning is the instance property itself: an `INSTANCES`
row claims the assertion *stays green* under a mutation of the code it purports to test. Every one of
the eleven compares the extractor's or the parser's output against either `zipfile`'s independent
read of the same archive or a value computed without touching the code under test, so mutating that
code should break them rather than leave them green. **If any one of the eleven is genuinely an
instance, that is a defect in a test the previous turn was asked for, and it will be said plainly.**

#### The surface, measured rather than taken

`sweep()` reports **31 modules, 1123 asserts**, and **11 new expressions over 13 occurrences** — two
appearing twice (`… == content` and `… session=_RangedSession(blob)) == expected`), the other nine
once each. **Thirteen, not fourteen, and two doubled rather than three**: the count was measured from
`sweep()` and cross-checked against `grep` over the file, because `PINNED` is a multiset and a count
entered wrongly is a hole in the guard rather than a cosmetic slip.

#### Classified: eleven to `PINNED`, none to `INSTANCES`

**The dispositions are not interchangeable.** `PINNED` (l.203) is *reviewed, and not a tautology* —
a multiset of `(module, normalized source, occurrences)`, keyed that way because *a set cannot see a
pinned expression duplicated and a count cannot see one swapped for another* (l.198–200). `INSTANCES`
(l.798) claims the assertion **is** one: it *stays green* under a stated mutation, and the mutation
plus its `green_scope` are re-run by `test_every_classified_instance_re_runs_its_recorded_evidence`.
Pass C (l.113) is what admitted most of these — *one side of an `==` contains a call and another side
is not a literal display*.

**All eleven went red under a mutation, so none is an instance** — and the check applied was stricter
than the test reddening: for every one, the failure message names **that assertion** rather than
merely its test, because a test can redden at an earlier line. Three mutations carry them, each aimed
at what the assertion actually compares: `extract_member` returning `raw[:-1] + b"X"` (length
preserved, content changed, applied after every guard so nothing refuses); `raw[:-1]` (length
changed); and field-level mutations of the directory parse — the zip64 write-back removed, the CRC
read from bytes 12–16, the uncompressed size from 20–24. Each expression's own reason and its
mutation are recorded beside it in `tests/test_tautology_sweep.py`, one per expression rather than in
bulk.

**Two separations were measured rather than asserted.** `got == content` and `len(got) == len(content)`
sit in the same test, and the length-preserving mutation reddens the first and **not** the second —
which is what shows they are two assertions rather than one and a weaker copy. And the two chained
comparisons are **one expression each, not several**: a chain is a single `ast.Compare`, so `sides` is
all three terms and `ast.unparse` records the whole chain. In both chains one conjunct compares the
parse against `zipfile`'s and the other recomputes independently; **neither conjunct is trivial, but
only the first exercises our code** — the second checks the reference implementation, which is why it
is kept rather than dropped.

**Classified by hand first, regenerated second.** The eleven rows were written out with reasons and
counts, and only then was l.201–202's command run — as a **check**, not a source: the regenerated set
equals `PINNED` exactly, with nothing unclassified and nothing stale. Regenerating first would have
pinned all eleven wholesale and produced a green suite with nothing reviewed.

**No `INSTANCES` row was added, so no `green_scope` was written**, and the whole-suite scopes at
l.786 and l.794 were not added to. `INSTANCES` is unchanged at four rows and re-runs green.

#### Predicted beside measured

| | Predicted | Measured |
|---|---|---|
| `PINNED` | **11** | **11** (13 occurrences) |
| `INSTANCES` | **0** | **0** |

**Hit exactly, and the prediction rested on the instance property rather than on inspection.** No
expression among the eleven is a tautology, so there is no defect in the tests the extractor turn was
asked for.

#### The floor

`assert modules >= 31 and asserts >= 1039` → **`asserts >= 1123`**; **modules unchanged at 31**,
since the extractor's tests went into a module the sweep already counted. Read off `sweep()` rather
than incremented, and moved for those tests alone.

#### A finding about the sweep, recorded and not fixed

**Pass D's second conjunct cannot be false, so Pass D matches a shape Pass C is written to exclude.**
Pass C requires a call on one side *and a non-literal on another*. Pass D fires when no side contains
a call, on `any(side is a Name bound from a call) and bool(non_literal)` — but `_is_literalish`
returns `False` for **any** `ast.Name`, so whenever the first conjunct holds, the bare name is itself
in `non_literal` and the second conjunct is satisfied by construction. It can never fail.

The visible consequence is `got == b'body of GlyGly (K)Sites.txt'`: a computed value against a
**literal display**, which Pass C would have excluded and Pass D admits. That is an over-match
relative to Pass C's stated principle, not a wrong verdict — the expression is correctly `PINNED`
either way. **Left alone**: the passes and the matching logic are out of scope here, and a guard that
over-matches costs a classification while one that under-matches costs a defect.

### Pre-registration: the extractor's first live use, 2026-08-12

**Committed before any live call, in its own commit.** The extractor is offline-tested and has never
read a PRIDE archive. This turn is deliberately minimal — **read central directories, then extract
exactly one member** — because every first live contact on this project has produced a finding, and
doing twelve at once would mix first-contact failures with data.

**A precision about what is and is not first contact.** `archive_members` is the parse that
`archive_entries` now projects, and *that* parse has already read PRIDE archives live: 18,124 entry
names came off them during the survey runs. What has never been read live is the set of fields this
record added — method, flags, CRC-32, both sizes, the local-header offset — and `extract_member`
entirely. So Step 3 is first contact for the **new fields**, not for the walk.

**The archive host was confirmed answering first**:
`https://ftp.pride.ebi.ac.uk/pride/data/archive/2022/02/PXD018299/` → `HEAD 200`,
`Accept-Ranges: bytes`, and a ranged `GET` → **206** with an exact `Content-Range` over a
2,085,098,293-byte file.

#### The size threshold

**100,000,000 bytes uncompressed** is the largest member this turn will extract. Set from the direct
K-GG tables already priced: the largest is 66 MB, so 100 MB covers a typical site table with margin,
and it bounds the turn without being generous enough to matter against ~29 GB of free disk. **If the
smallest available K-GG member exceeds it, nothing is extracted** — the threshold is recorded, the
size is recorded, and the turn stops rather than raising the number to fit what it found.

#### What counts as success for the single extraction

Four things, all of them checks the code already makes or that this turn adds around it:

1. **The CRC-32 verifies.** `extract_member` raises otherwise, so a returned value *is* a verified one.
2. **The inflated length equals the declared uncompressed size** — a separate guard from the CRC.
3. **The first line parses as a tab-separated header with more than one column**, which is what makes
   the bytes a readable table rather than merely correct.
4. **Nothing persists.** No file under `raw/`, none under `data/curation/`, nothing in the
   content-addressed store: the member is held in memory and dropped.

#### What counts as a finding rather than a failure

**A guard raising is evidence about the format or the server, not necessarily a defect.** Each of the
guards points somewhere different, and the distinction is registered now so it is not decided after
seeing which fired:

| Raise | Evidence about |
|---|---|
| ranged request answered 200 | the **server** — it ignored `Range` |
| no end-of-central-directory in the tail | the **archive** — a trailing comment longer than 64 KiB |
| zip64 declared with no locator | the **archive** — a malformed end record |
| parsed count ≠ declared, or short directory | **truncation**, server or transfer |
| local header not at the offset, or naming another member | the **archive** — a central directory that does not agree with itself |
| unsupported method, encrypted, directory entry | the **member** — outside what the extractor supports, by design |
| CRC-32 mismatch | **bytes that are wrong**, which is the only one that would indicate the extractor itself is broken |

**Only the last is a defect in this code on its face.** The rest are findings about what PRIDE
actually serves, and each is recorded with the accession, the archive, the guard and the bytes.

#### Predictions, from the host and the format rather than from the test suite

The offline suite establishes the code is right about `zipfile`; that is not the same as being right
about PRIDE, so none of these rests on it.

| Quantity | Predicted | Rests on |
|---|---|---|
| of the **12 archives**, directories reading with **no guard raising** | **12** | the same walk has already read PRIDE archives live at scale during the survey; the host answers 206 with exact ranges, measured minutes ago |
| archives showing **Zip64 sentinels** | **exactly 1** | only `MaxQUANT_HpH.zip` at 16,993,871,159 bytes exceeds the 32-bit ceiling; the other eleven are ≤ 2.28 GB, and none is likely to carry >65,535 entries |
| the **smallest** K-GG member, uncompressed | **~10^7 bytes**, band 10^6–10^8 | the direct K-GG tables measure 0.10, 2.76, 15.8 and 66 MB, so a few megabytes is the shape of the small end |
| compression method of the K-GG members | **8 (deflate)** throughout | text tables, and deflate is what every archiver defaults to |

**No prediction is made about what any column header will contain**, and no C1 criterion is scored
this turn.

### The extractor's first live use: twelve directories, one member, 2026-08-12

**No guard raised.** Twelve central directories read live and one member extracted and CRC-verified.
Nothing was retained — no file under `raw/`, none under `data/curation/`, nothing in the
content-addressed store; the member was held in memory and dropped.

#### Twelve directories, live

| Accession | Archive | Archive bytes | Entries | Guard | K-GG member, uncompressed | Method |
|---|---|---|---|---|---|---|
| `PXD019152` | `MaxQUANT_HpH.zip` | 16,993,871,159 | 9,210 | **none** | 393,147 | 8 |
| `PXD074990` | `PTMH1299_search_results.zip` | 2,283,114,958 | 482 | **none** | 1,115,157 | 8 |
| `PXD019152` | `MaxQUANT_PRM.zip` | 1,765,625,472 | 1,297 | **none** | 42,042 | 8 |
| `PXD032078` | `txt_GlyGlyKsites.zip` | 1,330,037,043 | 19 | **none** | 2,551,526 | 8 |
| `PXD075538` | `search_1023_1032.zip` | 476,843,006 | 22 | **none** | 124,642 | 8 |
| `PXD075538` | `search_0995_R01R18.zip` | 319,100,824 | 21 | **none** | 533,887 | 8 |
| `PXD074949` | `search_1066_R01R18.zip` | 278,912,137 | 22 | **none** | 70,631 | 8 |
| `PXD060435` | `txt.zip` | 275,252,853 | 17 | **none** | 2,672,464 | 8 |
| `PXD070339` | `txt.zip` | 275,252,853 | 17 | **none** | 2,672,464 | 8 |
| `PXD075538` | `search_0995_R19R34.zip` | 219,652,728 | 22 | **none** | 105,317 | 8 |
| `PXD074949` | `search_1233_R01R18.zip` | 202,629,531 | 21 | **none** | 354,273 | 8 |
| `PXD074949` | `search_1066_R47R64.zip` | 191,509,376 | 22 | **none** | 328,913 | 8 |

**Zip64 fired live, and this is the finding of the step.** `MaxQUANT_HpH.zip` at 16,993,871,159 bytes
is past the 32-bit ceiling, and **6,057 of its 9,210 entries carry a local-header offset above
`0xFFFFFFFF`** — so the sentinel path the offline tests exercised through a hand-built fixture
resolved six thousand real offsets on a real archive. No entry in any of the twelve carries a
compressed or uncompressed size above the ceiling, and **exactly one archive of twelve shows Zip64 at
all**, which is what the archive sizes predicted.

**Every K-GG member is deflate (method 8), and every archive read on the first or second attempt.**
Entry counts span 17 to 9,210; directory reads took 0.5–1.3 s each.

#### One transport failure, and it is not a guard

**`PXD075538` / `search_0995_R01R18.zip` raised `ChunkedEncodingError` —
*Connection broken: IncompleteRead(0 bytes read, 65536 more expected)* — on its first attempt, and
read cleanly on retry.** It is not one of the four guards and not evidence about the format: it is a
transport failure on the tail read, of the same kind as the `diGly` search that read-timed-out once
and succeeded on the second attempt. Retried once, recorded, and it recurred **zero** times across
the remaining reads and the re-reads for the Zip64 measurement.

**It also demonstrates a deferred item live, with a non-guard exception.** `expand_archives` catches
`requests.RequestException` alongside the guards and writes `unreadable ({type})`, so in a survey run
this would have been recorded as `unreadable (ChunkedEncodingError)` — **indistinguishable from a
guard raise, and indistinguishable from a permanent failure**. The gap was recorded as *which guard
fired is not recoverable*; what this shows is that it is wider than that, because the trace cannot
separate a guard from a retryable transient either. Recorded, not fixed.

#### One member, extracted and verified

| | |
|---|---|
| accession / archive | `PXD019152` / `MaxQUANT_PRM.zip` (1,765,625,472 B) |
| member | `MaxQUANT_PRM/combined/txt/GlyGly (K)Sites.txt` |
| method / flags | 8 (deflate) / `0x0000` — no encryption, no data descriptor |
| local-header offset | 1,758,362,673 — **below** the 32-bit ceiling |
| compressed / uncompressed | 10,464 B / 42,042 B |
| ranged reads | **2** — 75 B of local header and name, then 10,464 B of body |
| bytes transferred | **10,539** |
| elapsed | 1.08 s |
| CRC-32 | `0x45f29d3f` — verified by the function, recomputed independently here: **True** |
| declared length | matches the inflated length: **True** |

**10,539 bytes moved to lift a 42,042-byte table out of a
1,765,625,472-byte archive — a ratio of about 167,533:1.**
That is the retrieval decision's premise, measured rather than argued, on one member.

#### The first line, as evidence the bytes are a readable table

**69 tab-separated columns**, 1,133 bytes. It is a MaxQuant `GlyGly (K)Sites.txt`
header on its face: `Proteins`, `Localization prob`, `Number of GlyGly (K)`, `Sequence window`, `GlyGly (K) Probabilities`, `Intensity`, `Intensity___1`, `Ratio mod/base`, `Reverse`, `id`, `Best localization raw file`, `Best PEP scan number
`. The `___1`/`___2`/`___3` suffixes are MaxQuant's multiplicity columns
and `Ratio mod/base` is I4's stoichiometry column.

**No C1 criterion is scored against these headers.** They are evidence that the extraction produced a
readable table, not a measurement — and several of them are exactly what criteria 5, 6, 7 and 11 will
be read from, which is why scoring them here would pre-empt a turn that has to register its
predictions first.

#### What this establishes, and what it does not

**The *never read a PRIDE archive* limit is now partly discharged, and only partly.**

| Claim | Status after this turn |
|---|---|
| `archive_members`' walk reads PRIDE archives | already true before this turn — 18,124 entry names during the survey |
| its **new fields** — method, flags, CRC, sizes, offsets — read live | **established, on 12 archives** |
| its **Zip64 sentinel resolution** runs live | **established**, 6,057 offsets on `MaxQUANT_HpH.zip` |
| `extract_member` works against a real server | **established for one member of one archive** |
| the other eleven members will extract | **not established** |
| `extract_member` handles a Zip64 **offset** | **not established** — and almost certainly not exercised: Step 4 takes the *smallest* member, whose offset is 1,758,362,673, below the ceiling, while the Zip64 archive holds the *largest* |
| stored (method 0), encrypted, or data-descriptor members | **not exercised** — every K-GG member here is plain deflate |

**So one success does not read as general.** The parse is now live-exercised broadly; the extractor is
live-exercised once, on the easiest member of the twelve, through the paths a small deflate entry
takes and no others.

#### Predicted beside measured

| Quantity | Predicted | Measured | |
|---|---|---|---|
| directories reading with no guard raising | **12** | **12** | hit |
| archives showing Zip64 | **exactly 1** | **1** | hit |
| compression method of the K-GG members | **8 throughout** | **8 throughout** | hit |
| smallest K-GG member, uncompressed | **~10^7 B**, band 10^6–10^8 | **42,042 B** ≈ 4×10^4 | **missed, two orders low, outside the band** |

**The miss is evidence that I predicted from the wrong population.** The band came from the *direct*
K-GG tables — 0.10, 2.76, 15.8 and 66 MB — which are all global diGly experiments. The smallest
archived member is from `MaxQUANT_PRM.zip`, a **parallel-reaction-monitoring** run: targeted at a
handful of peptides, so its site table has almost no rows. The archived twelve differ from the direct
four in experimental **design**, not only in size, and a size extrapolated across that difference was
extrapolated across the thing that determines it.

#### No code change was required

No guard raised, and the one failure was a transport transient that did not recur, so nothing in
`bzk/deposit_survey.py` changed and no test was added. **Two defects in this turn's own probes were
found and corrected**, neither in the module: a Zip64 check written as `resolved == 0xFFFFFFFF`, which
cannot ever hold because the parse replaces a sentinel with the real value — it reported *no Zip64
anywhere*, including on the 17 GB archive, until it was rewritten as `resolved > 0xFFFFFFFF`; and a
`head -60` on the extraction script's output, which broke its pipe before it wrote its record, so the
**same** member was extracted a second time for that mechanical reason. One member, twice; no second
member.

### Experimental design across the twelve, from held evidence only, 2026-08-12

**No network call was made this turn.** Every figure below is parsed out of this document.

**Why it is being asked at all.** The last prediction missed by two orders because it extrapolated a
member size from the four *direct* K-GG tables, all global diGly experiments, onto an archived member
from a parallel-reaction-monitoring run. The recorded diagnosis was that the archived set differs in
experimental **design**, not only in size — and that bears on more than a prediction. C1's rates are
measured against `PXD018299`, and a targeted assay over a handful of peptides can differ from it on
every one of them for reasons that say nothing about whether the ontology generalises. **No registered
criterion asks what produced a deposit's site table**: C0(c) asks only that one exists. **This turn
measures; it changes no criterion.**

#### Predicted, before classifying

**0 of the twelve classifiable as targeted**, band 0–1, with most **undetermined** and a small number
**discovery**. What that rests on, stated so the basis can be checked rather than the number:

1. **The held names contain exactly one targeted marker** — `MaxQUANT_PRM` — and it sits on
   `PXD019152`, which also carries `MaxQUANT_HpH`. A deposit that ran both makes that marker evidence
   about an **archive**, not about the deposit.
2. **Nothing else in the held names says targeted.** `search_*`, `txt*`, `PTMH1299_search_results`,
   `GlyGlySites.txt`, `UbiSite_*`, `HAP1_USP18KO_*` carry no design marker either way.
3. **Domain**: K-GG remnant profiling is a discovery technique — enrich the remnant, then acquire over
   the proteome. Targeted PRM on ubiquitination sites exists but is unusual, and would not normally
   reach a deposit as a `GlyGly (K)Sites.txt` from a global search.

**The prediction deliberately does not use size or entry count**, and naming that is the point: those
are the tempting deciders, and letting them decide would repeat the exact error being diagnosed. Size
is a **consequence** of design, not evidence of it — a small global experiment and a large targeted
one both exist.

#### The evidentiary limit: no title is held for any of the twelve

**Verified rather than assumed.** The sixty-row table has **no title column** — its header is
`| # | Accession | Files | Engine (filename route) | Site | SDRF | Licence | Skipped | C0 gates met | Archive read | In widened 12 |`
— and every occurrence of these accessions elsewhere in this document is a token in a list, a table
row, or prose about the accession. None carries a deposit title.

**The record does hold titles, and that sharpens the limit rather than softening it.** Six of the
*baseline* twelve are recorded with theirs — *Proteome-wide identification of ISG15 sites in HeLa
cells*, *Global ISGylome… SARS-CoV-2*, *Ubiquitinome Profiling… Data-Independent…*, and three more.
Those six are **disjoint from the twelve here**. So the field was carried when the baseline was
written and dropped when the sixty were classified.

**`Candidate.title` exists in the module and the CLI prints it**, so this is a field the record
declined rather than one the instrument lacks. **Recorded as a finding; not fixed, and no title is
fetched.** The classification below therefore proceeds on circumstantial signals only, and is weaker
evidence than a title would have been — which is stated here rather than left to be inferred from how
confidently the table reads.

#### The reconciliation, checked

**4 direct + 7 archived = 11 covered, with no overlap, and `PXD070789` uncovered — twelve in total.**
Verified by parsing both tables: the four with a direct K-GG table are `PXD018299`, `PXD027163`,
`PXD027328`, `PXD079072`; the seven with an archived one are `PXD019152`, `PXD032078`, `PXD060435`,
`PXD070339`, `PXD074949`, `PXD074990`, `PXD075538`. The intersection is empty. So *16 objects*,
*11 of 12 candidates* and *7 candidates with archives* are three different counts of three different
things, and they agree.

#### The signals the record actually holds

Beyond the three named — archive and member names, uncompressed size, entry count — the record holds
three more, and they are enumerated because leaving them out would overstate the scarcity:

| Signal | Where | Use |
|---|---|---|
| **`Files` count** per candidate | the sixty-row table | 10 to 10,531; a held quantity, and subject to the same warning as size |
| **number of archives** per candidate | the twelve-archive table | 1 to 3; `PXD074949` and `PXD075538` carry three each |
| **run-range markers inside archive names** | `R01R18`, `R19R34`, `R47R64`, `1023_1032` | reads as run or fraction ranges — **a guess about a naming convention**, the class of error that got `raw_`/`_raw` removed from the archive hints |
| **site tables for more than one modification** | the matcher re-read table | structural, and **not** a size signal |

**Size and entry count decide nothing on their own here.** That is the discipline the last miss
bought: size is a consequence of design, not evidence of it.

#### Classified: 2 discovery, 0 targeted, 10 undetermined

| Candidate | Verdict | Deciding signal |
|---|---|---|
| `PXD018299` | **discovery** | **prior ingestion by this repository** — 2,341 sites → 2,298 after decoys and contaminants → 2,056 after localisation → 1,375 tested. A 2,298-site K-GG dataset is a discovery experiment. The only verdict here resting on a measurement rather than a filename |
| `PXD027328` | **discovery** | **site tables for two distinct modifications** from one search — `GlyGly__K_Sites.txt` and `Phospho__STY_Sites.txt`, with `modificationSpecificPeptides_ntermUb.txt` — which is a global multi-PTM search. Structural, not size |
| `PXD019152` | **undetermined — the conflict case** | carries `MaxQUANT_HpH.zip` (high-pH reversed-phase fractionation, a discovery marker) **and** `MaxQUANT_PRM.zip` (parallel reaction monitoring, a targeted marker). **Not resolved by the stronger name.** A deposit that ran both makes each marker evidence about an *archive*, so reading PRM as this deposit's character is as wrong as reading HpH as it |
| `PXD027163` | **undetermined** | `UbiSite_GlyGly__K_Sites.txt` is suggestive of a proteome-wide enrichment method, but the meaning is supplied from outside the record **and** `UbiSite` is one of the thirteen registered query terms, so the name may reflect the query rather than the method. Two independent weaknesses; it does not settle |
| `PXD074949` | **undetermined** | three archives named `search_1066_R01R18`, `search_1066_R47R64`, `search_1233_R01R18`. The run-range reading is suggestive of discovery-scale batching and is explicitly **not** decisive |
| `PXD075538` | **undetermined** | same shape — `search_0995_R01R18`, `search_0995_R19R34`, `search_1023_1032`; same objection |
| `PXD070339` | **undetermined** | `txt.zip` names the content, not the design. **See the identity finding below** |
| `PXD060435` | **undetermined** | `txt.zip`, likewise. **See the identity finding below** |
| `PXD074990` | **undetermined** | `PTMH1299_search_results.zip` — an internal identifier and *PTM*, which C0(c) already establishes |
| `PXD032078` | **undetermined** | `txt_GlyGlyKsites.zip` names the modification, not the design |
| `PXD079072` | **undetermined** | one site table and `mqpar.xml`; five `.raw` files with `-40`/`-60`/`-80` variants. Nothing structural either way |
| `PXD070789` | **undetermined** | 10 files, and separately **no K-GG table at all** — its only site table is phospho. For this candidate the binding limit is the **modification**, not the design |

#### `PXD070339` and `PXD060435` deposit the same archive

**Identical on every held field**: archive size 275,252,853 B, 17 entries, member `txt/GlyGly (K)Sites.txt`,
compressed 535,252 B, uncompressed 2,672,464 B, **CRC-32 `0xb6226139`**, and **local-header offset
127,107,162**. A matching CRC on the member together with a matching offset inside the archive is
decisive for the member and near-decisive for the archive: these are the same bytes under two
accessions.

**So two of the twelve are not independent candidates**, and that matters beyond design: a contrast
scored on both would be scored twice against one dataset. Recorded; nothing is admitted, ranked or
excluded on it.

#### What this means for C1 — recorded, not acted on

**The anchor's figures were measured on a discovery run, and the record says so**: C1's *Tested
against* column for criterion 1 is **1,896 / 2,298 = 82.5%** and for criterion 9 is **242 / 2,298 =
10.5%**, both from `PXD018299`'s 2,298 filtered K-GG sites. A denominator of 2,298 is a global
experiment by construction.

All eleven checked, not only the four value criteria:

| # | Criterion | On a targeted run |
|---|---|---|
| 1 | Multi-mapping rate (I14) | **misleading** — over a handful of peptides the rate is dominated by which were chosen, and the 60–95% band is met or missed by accident |
| 2 | Razor picks that are isoforms (I2) | **self-protected** — its `sample ≥ 20` floor is not met, so it becomes *unscorable* rather than wrong |
| 3 | Razor pick on TrEMBL despite reviewed (I17) | **self-protected** — same, on `sample ≥ 8` |
| 4 | `AMBIGUOUS` fold | **self-protected in wording** — it asks for *any non-zero rate over a **comparable** accession sample*, and a targeted accession set is not comparable. The only criterion whose text already carries the guard |
| 5 | Declared-quantity enum (I16) | **misleading** — a targeted acquisition reports differently by design, so it differs for acquisition reasons rather than ontology ones |
| 6 | Localisation distribution | **misleading** — in a targeted assay the sites are chosen, so probabilities cluster and the median differs by design |
| 7 | Native stoichiometry (I4) | **survives** — presence or absence of a `Ratio mod/base` column is a MaxQuant configuration fact, independent of design |
| 8 | Sample-name convention | **survives** — a convention in kind is independent of design |
| 9 | Unrecorded threshold | **misleading for the rate**, survives as a yes/no: *did the deposit pre-filter* is answerable; *what fraction it dropped* depends on a score distribution that depends on design |
| 10 | SDRF present | **survives** — a metadata fact, already measured N for all twelve |
| 11 | Design recoverable from column names | **survives**, and asks a different question: whether design is *recoverable*, not which design it is |

**Five misleading (1, 5, 6, 9), three self-protected (2, 3, 4), four surviving (7, 8, 10, 11)** — and
criterion 9 sits in both columns, misleading as a rate and sound as a yes/no.

**The gap is real but narrower than it first looks**, and that is the finding rather than a call for a
gate. Two of C1's four value criteria refuse themselves on a small sample through floors already
written into their bands, and a third refuses itself through the word *comparable*. What is exposed is
criteria **1, 5, 6** and the rate half of **9** — four measurements out of eleven — and only on a
deposit that is actually targeted, of which **this turn found none**.

**No criterion is amended.** Whether design should be a gate is a criteria decision with its own
consequences to write down first, and settling it inside the turn that found the gap is the shape this
project has undone twice.

#### Predicted beside measured

| Quantity | Predicted | Measured | |
|---|---|---|---|
| classifiable as **targeted** | **0**, band 0–1 | **0** | hit |
| shape | most undetermined, a small number discovery | **10 undetermined, 2 discovery** | hit |

**The prediction held, and it held for the reason it was registered on**: the one targeted marker in
the held names sits on the one deposit that also carries a discovery marker, so it never became a
verdict. **The trap the last miss opened was not walked into** — size and entry count decided nothing,
and the two discovery verdicts rest on a prior ingestion and on a structural multi-modification fact,
neither of which is a size.

### Pre-registration: the title rule and the duplicate branches, 2026-08-12

**Committed before the twelve project records are read, in its own commit.** Two open questions share
one input: the design classification left ten of twelve **undetermined** for want of titles, and the
`PXD060435`/`PXD070339` duplicate cannot be resolved from held bytes, which settle identity and say
nothing about provenance.

**One title has already been seen and it is disclosed rather than pretended away.** Confirming the
endpoint answered required reading a record, and `PXD018299`'s was used because its design is already
established from this repository's own ingestion — so it leaks nothing about the ten that are open.
Its title begins *"Deep analysis of the USP18-dependent ISGylome and proteome…"*.

#### Rule (a) — design from a title, stated from the designs and not from these deposits

The two designs differ on **whether the analyte set is an input or an output**. A targeted assay
monitors a pre-specified list of precursors: the analytes are chosen before acquisition. A discovery
run acquires across the sample without such a list: the analytes are a result. So the rule turns on
whether a title names something that **entails an inclusion list**, or names a scope or depth strategy
that **entails there is none**.

**Targeted** — the title names at least one of:

| Class | Terms |
|---|---|
| targeted acquisition mode | `PRM`, `SRM`, `MRM`, *parallel reaction monitoring*, *selected reaction monitoring*, *multiple reaction monitoring* |
| an enumerated analyte set | *a panel of…*, *monitoring of X and Y*, *targeted analysis of <named proteins>* |
| absolute quantification against spiked standards | `AQUA`, *SIL peptide*, *isotope-labelled standard* |

**Discovery** — the title names at least one of:

| Class | Terms |
|---|---|
| acquisition or scope entailing no inclusion list | *shotgun*, *global*, *comprehensive*, *proteome-wide*, *system-wide*, *unbiased*, *deep* |
| the measured layer named as a whole | *proteome*, *phosphoproteome*, *acetylome*, *transcriptome* |
| a depth-increasing fractionation strategy | *high-pH*, `HpH`, `SCX`, *off-gel*, *fractionation*, *fractionated* |

**Undetermined** — neither class appears; **or both appear**; or the only design-bearing word's sense
here is ambiguous.

#### How the rule avoids confirming itself on a selected sample

**Every one of the twelve matched at least one of the thirteen registered query terms**, so their
titles are a selected sample and any rule built on that vocabulary would confirm itself. The rule
therefore carries an explicit exclusion:

> **No word or phrase that is, or contains, one of the thirteen registered query terms may serve as a
> design signal.** That removes `ISG15`, `ISGylome`, `diGly`, `GlyGly`, `K-GG`, `diglycine`,
> `ubiquitinome`, `ubiquitylome`, *ubiquitin remnant*, *ubiquitination site*, *ubiquitylation site*,
> `UbiSite` and *ubiquitin GlyGly* from both lists above.

**The clause is symmetric in statement and asymmetric in effect, and that asymmetry is the useful
part.** It bites the discovery side, because three query terms — `ISGylome`, `ubiquitinome`,
`ubiquitylome` — are exactly the *-ome* scope words the discovery list would otherwise credit, and a
fourth, `UbiSite`, is the method name the last turn already rejected on this ground. It bites the
targeted side not at all, because **no registered query term is a targeted-acquisition word**. So:

- a **targeted** verdict under this rule cannot be an artefact of how the sample was selected;
- a **discovery** verdict is trustworthy only where it rests on vocabulary the query set does not
  contain — *proteome*, *deep*, *global*, *shotgun*, fractionation terms — which is why those are
  listed and the *-ome* words of the anchor domain are not.

`PXD018299`'s title illustrates it: *ISGylome* is excluded, and what would carry the verdict is *Deep*
and *proteome*.

#### Rule (b) — what each duplicate outcome licenses, written before the evidence

| If the two records… | What follows | What does **not** follow |
|---|---|---|
| **share a submitter, publication, or lab** | the leading reading is supported: one derived artefact, one group. They are **not independent** for contrast — scoring both would score one dataset twice | that either should be **excluded** (out of scope), or that one is *the original*; shared provenance is equally consistent with a deliberate paired deposit, two conditions submitted separately off one search |
| **share none of the three** | the identity needs another explanation — a public re-analysis, a pipeline output attached to the wrong accession, or PRIDE serving one file under two accessions. It becomes a finding about **the archive or the repository**, not about the candidates | that the deposits are the same experiment; unrelated groups can deposit an identical derived file only by one taking the other's |

**What would make them independent candidates despite an identical member — written now, because the
case against the leading reading should not be composed after the evidence arrives.** The member is
one file of 17 in the archive, and the archive is one object among each deposit's **75**
(`PXD060435`) and **2,281** (`PXD070339`) files. **Identical derived output does not entail an
identical experiment.** If the rest of each deposit differs — different raw files, different counts,
different organisms — then these are two experiments sharing one derived artefact, and the held file
counts **already disagree by a factor of thirty**, which is *prima facie* evidence against them being
one deposit twice.

#### Predicted

| Quantity | Predicted | Reasoning |
|---|---|---|
| of the **10 undetermined**, moved off *undetermined* by rule (a) | **5**, band 3–8 | titles in this field commonly carry non-query depth vocabulary — *deep*, *global*, *quantitative*, *proteome* — but roughly as often are plain descriptive phrases naming a biology rather than a method |
| of those, moved to **targeted** | **0** | K-GG remnant profiling is a discovery technique; the exclusion clause guarantees a targeted verdict would have to come from a genuine acquisition word |
| `PXD019152`, the conflict case | stays **undetermined** or resolves **discovery** — not targeted | a title describes a study, and `MaxQUANT_PRM` was an *archive* name; a deposit that ran both is unlikely to name only the targeted half in its title |
| the duplicate branch | **shares a submitter and/or lab** | identical bytes with identical CRC and identical local-header offset is overwhelmingly a same-group artefact; cross-group byte identity requires one group depositing another's exact archive |

#### What PRIDE supplies, and what it does not

Read directly from `{API}/projects/{accession}`, twelve records, **not** through `classify` — that
calls `file_names` and `expand_archives`, so a `classify` per candidate would have meant twelve
accessions of archive work for a metadata read, and would have broken this turn's own
no-archive-read line.

| Field | Key present | Non-empty |
|---|---|---|
| `title` | 12/12 | **12/12** |
| `submitters` | 12/12 | **12/12** |
| `labPIs` | 12/12 | **12/12** |
| `submissionDate` | 12/12 | **12/12** |
| `publicationDate` | 12/12 | **12/12** |
| `references` | 12/12 | **6/12** |
| `doi` | 12/12 | **0/12** |

**So PRIDE supplies four of the five fields wanted and `doi` for none of the twelve.** Publication is
carried by `references` where it is carried at all — a free-text `referenceLine` plus a `pubmedID` —
and for half the sample it is absent. `Candidate` carries none of `submitters`, `labPIs`, `doi`,
`references`, `submissionDate` or `publicationDate`, and `classify` reads six fields off the project
record without them; verified at `b531a32`.

**This was a throwaway read and the module was not extended, deliberately.** The turn scores nothing,
and three of the four fields it needed exist for rule (b) alone — adding them to `Candidate` would put
a contract change in a turn whose only consumer is a record. **The values live in the three tables
below**, which is said explicitly so they are not dropped a third time.

#### The twelve titles

| Accession | Title, as PRIDE returns it |
|---|---|
| `PXD079072` | A dual-anchoring mechanism for the hemimethylated CG-guided  histone ubiquitylation |
| `PXD075538` | Deciphering NAC53, NAC78 interactome in response to Pst infection; NAC53, NAC78, MDP25 subcellular interactomes and identifying ubiquitination sites of NAC53 and NAC78 upon HRD1 E3 ligase mediated ubiquitination. |
| `PXD070339` | Enhanced STEAP4 Ubiquitination in Obesity: Insights from Combined Proteome and Ubiquitylome Analysis of Visceral Adipose Tissue |
| `PXD074990` | Ubiquitin substrates were identified in SILAC-labeled H1299 wild-type and MPND KO cells using LC-MS/MS. |
| `PXD027328` | Deubiquitinating enzymes and the proteasome regulate unique sets of ubiquitin substrates. |
| `PXD074949` | Identification of P-body components by proximity labeling and IP-MSMS |
| `PXD027163` | The inflammation repressor TNIP1 is degraded by selective autophagy in a LIR-dependent manner upon TLR3 activation |
| `PXD032078` | Proteomics-based identification of ISG15 modification sites in vivo upon Coxsackie virus infection |
| `PXD019152` | DDI2 is a ubiquitin-directed endoprotease, responsible for cleavage of transcription factor NRF1 |
| `PXD018299` | Deep analysis of the USP18-dependent ISGylome and proteome unveils important roles for USP18 in tumour cell antigenicity and radiosensitivity |
| `PXD070789` | DUSP26 protects against acute kidney injury by dephosphorylating p53 at serine 312 |
| `PXD060435` | Enhanced STEAP4 ubiquitination in Obesity: Insights from Integrated Proteome and Ubiquitylome Analysis of Visceral Adipose Tissue |

#### Re-classified under rule (a)

| Accession | Previous | Under rule (a) | Deciding words | Why |
|---|---|---|---|---|
| `PXD079072` | undetermined | undetermined | — | no term from either list |
| `PXD075538` | undetermined | undetermined | — | *interactome* is the measured layer as a whole but is **not a listed term**, and *identifying … of NAC53 and NAC78* is not *monitoring of* / *targeted analysis of* |
| `PXD070339` | undetermined | **discovery** | **Proteome** | the one listed discovery term present |
| `PXD074990` | undetermined | undetermined | — | *SILAC* is **not** the targeted list's *SIL peptide* — see the rule defect below |
| `PXD027328` | discovery | discovery | — | the title adds nothing; the verdict stands on the **structural** signal, two site tables for distinct modifications |
| `PXD074949` | undetermined | undetermined | — | *proximity labeling*, *IP-MSMS* are enrichment, not depth |
| `PXD027163` | undetermined | undetermined | — | names a biology, no method term |
| `PXD032078` | undetermined | undetermined | — | *Proteomics-based* names a discipline, not a scope; `ISG15` excluded as a query term |
| `PXD019152` | undetermined | undetermined | — | **the conflict case stays open** — the title names no acquisition at all, so `PRM` remains an *archive* name and never becomes a deposit verdict |
| `PXD018299` | discovery | discovery | **Deep**, **proteome** | already discovery from ingestion; the title now **independently corroborates** it |
| `PXD070789` | undetermined | undetermined | — | *dephosphorylating p53 at serine 312* is the finding, not an inclusion list |
| `PXD060435` | undetermined | **discovery** | **Proteome** | the one listed discovery term present |

**Two verdicts changed, both to discovery, both on the same word — and both belong to the one study.**
`PXD070339` and `PXD060435` are the duplicate pair, so rule (a) resolved **one study**, not two
candidates. **Eight of twelve remain undetermined**; discovery stands at four, targeted at **zero**.

#### Two defects in the pre-registered rule, found by applying it

1. **`SILAC` near-collides with the targeted list's `SIL peptide`.** SILAC is whole-proteome metabolic
   labelling — a discovery technique — while a spiked SIL peptide is a targeted one. A careless
   application of the rule as written would have classified `PXD074990` **targeted** on a string
   match. The rule should have said *spiked synthetic standard*; it said *SIL peptide*.
2. **The term lists are not exhaustive of the classes they illustrate**, and applying the rule forced
   a choice the rule did not state: does the **list** govern, or the **class**? *interactome* is a
   measured layer named as a whole and is not listed; *Proteomics-based* names a discipline, not a
   scope. **Resolved as list-governs**, to keep the rule reproducible by another reader, at the cost
   of leaving `PXD075538` and `PXD032078` undetermined. *Proteomics* against *proteome* is the closest
   near-miss, and a substring rule would have caught it — which is exactly the rule the matcher turn
   rejected, so the strictness here is consistent rather than arbitrary.

#### The duplicate, resolved: branch one

**Same submitter, same lab, same study.** `PXD060435` and `PXD070339` both carry submitter **Yuhao
Li**, identifier `3563926`, one email and one institution — Army Medical University (Third Military
Medical University), Chongqing. The `labPIs` entry names the same person under **two different
identifiers**, `3101129` and `3315110`, with differing affiliation strings, so PRIDE holds two PI
records for one person.

**The titles differ in one word.** *Enhanced STEAP4 ubiquitination in Obesity: Insights from
**Integrated** Proteome and Ubiquitylome Analysis of Visceral Adipose Tissue* against *…from
**Combined** Proteome and Ubiquitylome Analysis…*.

**So branch one holds: they are not independent for contrast purposes** — the identical `txt.zip` is
the diGly search output that criteria 1, 2, 6 and 9 would be measured on, and scoring both would score
one dataset twice.

**What the pre-registered rule said would not follow, and does not.** Neither is excluded — that is
out of scope and criteria-adjacent. And **neither is named the original**, though the asymmetries are
recorded as facts: `PXD060435` was submitted earlier (2025-02-03 against 2025-11-05) and carries the
publication, while `PXD070339` carries none — and the publication attached to `PXD060435` uses
`PXD070339`'s wording, *Combined*, in its own reference line. Those are facts; *therefore one is the
original* is the inference rule (b) pre-registered as not licensed.

**The case against the leading reading survives as a fact and is now explained rather than refuted.**
The file counts still differ by a factor of thirty — 75 against 2,281 — so these are two deposits of
different extent from one study sharing one derived artefact, not one deposit twice.

#### A second shared submitter, which was not being looked for

**`PXD075538` and `PXD074949` share submitter identifier `111980178`** — found by checking the twelve
records already read, at no further cost. Their titles are **different studies** (*Deciphering NAC53,
NAC78 interactome…* against *Identification of P-body components by proximity labeling and IP-MSMS*)
and their archives differ.

**That pair is the control the first one needed**: shared submitter **alone** does not imply shared
data. Two of the twelve share an archive and a study; two more share only a person. **Four of twelve
sit in a same-submitter pair**, and only one pair is a data duplicate. Recorded; nothing excluded.

#### Dates, and C0(a) left open on purpose

| Accession | Submitted | Published | References |
|---|---|---|---|
| `PXD079072` | 2026-05-30 | 2026-05-30 | 0 |
| `PXD075538` | 2026-03-12 | 2026-03-23 | 0 |
| `PXD070339` | 2025-11-05 | 2025-11-26 | 0 |
| `PXD074990` | 2026-02-27 | 2026-05-15 | 0 |
| `PXD027328` | 2021-07-15 | 2022-05-23 | 1 |
| `PXD074949` | 2026-02-26 | 2026-03-17 | 0 |
| `PXD027163` | 2021-07-07 | 2022-08-07 | 0 |
| `PXD032078` | 2022-03-05 | 2024-05-23 | 1 |
| `PXD019152` | 2020-05-13 | 2020-06-24 | 1 |
| `PXD018299` | 2020-03-31 | 2022-02-15 | 1 |
| `PXD070789` | 2025-11-16 | 2026-02-15 | 1 |
| `PXD060435` | 2025-02-03 | 2026-01-23 | 1 |

**All twelve carry a submission and a publication date, all in the past.** So the records **do** make
C0(a) answerable — and it is **not** answered here. The deferral asks that it not be settled as a side
effect of reading dates for another purpose, and evaluating *public, not embargoed* against ADR-0016's
embargo fields is a different check from observing that PRIDE reports a publication date. The dates
are recorded; the gate stays open.

#### Predicted beside measured

| Quantity | Predicted | Measured | |
|---|---|---|---|
| of the 10 undetermined, moved off *undetermined* | **5**, band 3–8 | **2** | **missed, below the band** |
| of those, moved to **targeted** | **0** | **0** | hit |
| `PXD019152`, the conflict case | not targeted | **undetermined** | hit |
| duplicate branch | shares submitter and/or lab | **shares both** | hit |

**The miss is evidence about what a PRIDE title in this domain is for.** The prediction assumed method
vocabulary would be present independently of the query terms. It largely is not: these titles name
**biology** — a mechanism, a protein, a disease, a tissue — and the only design-suggestive words most
of them carry are `Ubiquitylome`, `ISGylome`, `ISG15` and *ubiquitination sites*, every one of which
the exclusion clause removes. **So the selection effect the clause was written against was real and
larger than expected**: strip the query vocabulary and almost no method vocabulary remains. The clause
did its job, and the cost of it doing its job is eight undetermined.

### The shared-artefact rule: consequences registered before the choice, 2026-08-12

**No network call was made this turn.** The duplicate blocks: extracting both spends bytes for
identical numbers, and scoring both gives one study two entries in any ranking. **This turn decides
the rule; it extracts nothing and scores nothing.**

#### Is it the only one, and what is the check worth

**Verified over both sets, from the record alone.** Among the twelve archived K-GG members, **11 of 12
sizes are distinct** and the single repeated value is **2,672,464** — `PXD060435` and `PXD070339`. The
four direct K-GG tables are **4 distinct of 4** (102,731 / 2,759,052 / 15,802,963 / 65,992,977) and
**none equals any archived member size**. Over all sixteen objects: **15 distinct of 16, one repeat.**

**What the check is worth: little on its own.** Equal uncompressed size is a weak fingerprint beside
the CRC-32 and local-header offset that settled this pair, and the directory rows carry **no CRC
column** — so size equality can only *flag* a pair for a byte-identity check, never establish one. Two
different tables of the same length are entirely possible.

**Its reach is structural, not measurable.** The sixty-row table's columns are `#`, `Accession`,
`Files`, `Engine (filename route)`, `Site`, `SDRF`, `Licence`, `Skipped`, `C0 gates met`,
`Archive read`, `In widened 12` — **no member size**. Member sizes exist only for the sixteen objects
of the C0 passers, so **the check cannot run over the 48 non-passers at all**: the instrument never
recorded the fingerprint for them. That is the answer to *is this the only one* — not *no others
exist*, but *no others are findable from what was recorded*, and no directory is read this turn to
change it.

#### What each disposition keeps and drops

The consequences are known, so they are on the table rather than deferred. Twelve pass C0, of which
`PXD018299` is the anchor and a consistency check rather than a candidate.

| | Disposition | Keeps | Drops | Enters C1 measurement |
|---|---|---|---|---|
| **(a)** | keep both, flagged | 12 | 0 | 12 — needs something downstream to prevent double-counting |
| **(b)** | collapse to one entry | 11 entries over 12 accessions | 0 accessions, 1 entry | 11 |
| **(c)** | drop one, on a tie-break | 11 | 1 — `PXD060435` or `PXD070339` | 11 |
| **(d)** | drop both | 10 | 2 — both | 10 |

#### (b) and (d) against what the record already says

l.6312–6314: *"The case against the leading reading survives as a fact and is now explained rather than
refuted. The file counts still differ by a factor of thirty — 75 against 2,281 — so these are two
deposits of different extent from one study sharing one derived artefact, not one deposit twice."*

**(b) does not survive as written, and is struck rather than repaired in place.** It says *the two
accessions recorded as one candidate*, which asserts they **are** one candidate. The sentence above
says they are two deposits — and the larger holds **2,206 files the smaller does not**. Collapsing to
one entry would have to choose which extent the entry has or blur it, and either way loses what the
larger deposit holds beyond the shared artefact. Its coherent successor collapses the **artefact**, not
the candidates, and that is a different proposition, so it is listed below as its own option rather
than folded back into (b).

**(d) is struck: its stated ground is false here.** The ground offered was *a deposit whose diGly
output is not its own*. The output **is** the study's own — one submitter, one lab, one study, deposited
twice. There is no borrowed data to object to. And what (d) would cost if it were re-grounded on
something else is worth recording: it removes two candidates that may be perfectly good ubiquitomics
**on a property of the deposit record rather than of the data**.

#### Enumerated beyond the four

| | Disposition | Keeps | Enters C1 measurement |
|---|---|---|---|
| **(e)** | measure the artefact once; **both** candidates carry the same C1 result, sharing recorded | 12 | 1 measurement, 2 carriers |
| **(f)** | **one of the sharing set enters C1 measurement**; the others are recorded as sharing that artefact and are not re-measured | 12, none removed | 11 |
| **(g)** | do nothing — extract both, let the identical numbers stand | 12 | 12 |

**(g) is the status quo and is named so it is weighed rather than defaulted into**: its cost is exactly
the two harms that made this block — bytes spent for identical numbers, and one study occupying two
slots in any ranking.

#### Predicted, before deciding — about my own reasoning

**I expect to choose (f)**, and to reach it by three eliminations rather than by preference:

1. **(a) and (e) require C2 to know that two candidates share a score.** C2 ranks by C1 points with
   tie-breaks on SDRF, site count and download size; it has no notion of a shared artefact. Both
   would need a C2 amendment, and C2 is out of scope — so I expect to find them **unavailable rather
   than merely less good**.
2. **(b) and (d) are struck above**, on the record's own characterisation.
3. **(c) and (f) differ in what they say happens to the second accession** — dropped, against recorded
   as sharing. I expect **(f)** because nothing is removed from the candidate set, which is both what
   the scope requires and the more honest description: the deposit still passes C0 and is still a real
   deposit; what it does not get is a second measurement of the same bytes.

**And I expect the tie-break to be extent, selecting the larger deposit.** The reasoning I expect to
use is that **C1 cannot distinguish them by construction** — every criterion is measured on the
identical artefact — so the choice cannot be made on C1 grounds at all, and must be made on what the
deposit offers beyond C1. That is extent.

**If I end elsewhere I will say what moved me.** No prediction is made about what either deposit would
score.

#### Decided: (f) — one measurement per artefact, nothing removed

**The rule, stated without naming any accession.** If it needed them it would not be a rule.

> **Shared-artefact deduplication.** Where two or more candidates in the drawn set carry a
> **byte-identical derived artefact** — identical member name, compressed size, uncompressed size and
> **CRC-32** — exactly **one** enters C1 measurement. It is the candidate of **greatest extent by file
> count**; ties break on the earlier submission date, and then on the lexically first accession, so the
> choice is total. The others are **recorded as sharing that artefact** and are not re-measured.
> **Identity is established on the artefact — never on the submitter, the lab, the title or the
> publication.**
>
> **Size equality is a screen, not the trigger.** Equal uncompressed size flags a pair for the
> byte-identity check; the check itself needs the CRC-32, which the directory read already yields. A
> pair that survives the screen and fails the CRC comparison is **not** a shared artefact.

#### Why (a) and (e) are unavailable rather than merely worse

Both keep two candidates carrying one measurement, so both need the **ranking** to know that two
entries are one study. C2 is *Rank by C1 points*, with tie-breaks on SDRF present, then site count
≥ 1,000, then smaller download. It has no notion of a shared artefact, and on this pair its tie-breaks
would not even separate them usefully: **SDRF is N for both**, and **site count comes from the identical
table**, so the first two are inert and the third — smaller download — would order one study's two
accessions adjacently at whatever rank the score earned. **Expressing (a) or (e) therefore requires
amending C2, which is out of scope.** They are ruled out by availability, not by taste.

#### Why (f) over (c)

They differ only in what happens to the second accession — *dropped*, against *recorded as sharing*.
**(f) is substantively better, not gentler.** Under (c) the accession leaves the candidate set and a
later reader sees eleven with no trace of the twelfth or of why; under (f) twelve remain and the
sharing is recoverable from the record. That is this project's standing discipline — **flag rather than
hide** — applied to a candidate set rather than to a result. It also keeps the deposit's own C0 verdict
intact, which is true of it: it passes C0, and what it does not get is a second measurement of the same
bytes.

#### The tie-break, and why it cannot be a C1 ground

**C1 cannot distinguish the two by construction.** Every criterion that needs data is measured on the
artefact, and the artefact is identical, so **any C1-based tie-break is a coin toss dressed as a
reason**. The choice therefore has to be made on what the deposit offers *beyond* C1 — and that is
**extent**: the larger holds 2,206 files the smaller does not, and if the shared part is measured once
either way, preferring extent maximises what remains testable when the deposit is eventually ingested.

**On this pair the rule selects the 2,281-file deposit — and three other plausible tie-breaks all
select the other one.** Submission date favours the 75-file deposit (2025-02-03 against 2025-11-05);
publication attachment favours it; and **C2's own third tie-break, smaller download, favours it too.**
The rule going against all three is the strongest available evidence that it was not chosen for whom it
favours. It also avoids two grounds the record has already declined: *therefore one is the original*,
which the earlier record withheld, and the publication attachment, which is unreliable here because the
reference line on one deposit uses **the other's** title wording.

#### The generalisation test, run explicitly

| Pair | Shared submitter? | Common member size | Rule fires? | Correct? |
|---|---|---|---|---|
| the data duplicate | yes, `3563926` | **2,672,464** | **yes** | yes — one artefact, one measurement |
| the control pair | yes, `111980178` | **none** — `105,317`/`124,642`/`533,887` against `70,631`/`328,913`/`354,273` | **no** | yes — different studies, different archives, both measured |

**A submitter-keyed rule would fire on both pairs and be wrong about the second.** That is why the rule
keys on the artefact and names the submitter only as something it must *not* use. The control pair is
what makes that testable rather than asserted.

#### Where the rule lives: the survey's method, not a criterion

**It is not a criterion, and the reason is what criteria do here.** C0 decides **admissibility** — both
deposits still pass every gate, and neither verdict changes. C1 is the **contrast criteria and their
bands** — untouched; what changes is how many times they are evaluated, not what they measure or where
their bands sit. C2 **ranks what it is given** — unamended, and it receives one entry per artefact
rather than being taught about duplicates. C3 is **survey size** — the draw, the cap and the twelve
passers all stand.

**C4 is labelled *method*, and this is still not a C4 amendment.** Read at `3974cc0`, C4's content is
narrow: classification is decided by the type-prefix stamp and **never** by the presence of a
statistics column; engine and grain are read from the file listing; and **no bytes are retained**. A
deduplication step is neither a classification method nor a retention policy, so it sits beside C4
rather than inside it.

**So it is recorded here as a step in the survey's method**: a rule about what the survey *does* with
its own output between passing C0 and measuring C1. **Nothing is removed from any earlier table** — the
candidate set as recorded stands, and what changes is only what a later turn measures.

#### Predicted beside chosen

| | Predicted | Chosen |
|---|---|---|
| disposition | **(f)** | **(f)** |
| route | by elimination: (a)/(e) unavailable on C2, (b)/(d) struck | **as predicted** |
| tie-break | **extent**, on the ground that C1 cannot distinguish them | **as predicted** |

**Nothing moved me, and that is worth one sentence of scepticism rather than satisfaction**: the
prediction and the decision were written by the same reasoning in the same turn, so their agreement
tests only that the reasoning was stable, not that it was right. What carries weight instead is that
the rule fires on the duplicate and not on the control, and that its tie-break selects against the
three readings that had priority, publication and C2's own tie-break behind them.

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

**This exit moved to v0.2 on 2026-08-11's dependency redraw, and only as a milestone.** The adapter stays in v0.1; what waits is *a real user's results*, which this exit asks for by name and which only the collaborating group can supply. The second, §11 Q1 half is unaffected by that move — it waits on a modelling decision inside this repository and on nobody outside it, and it is not settled here.

### Weeks 5–6 — raw path and statistics
MaxQuant site-table adapter. DuckDB quantitative layer. **`welch_t` with BH first**, reproducing 12 of 14 exactly; then `perseus_s0` with permutation FDR, its recovery number recorded as a separate baseline. `ModifierAssignment`, `ProteinAssignment` and `Imputation` including supersession and retraction.

*Exit, amended 2026-08-07 — the old wording asserted a number the two routes cannot share.* It read *"12 of 14 recovered through the real pipeline rather than a notebook"*, which assumes the pipeline sees the same sites the notebook did. **It does not, and it should not:** ingestion refuses 89 rows for reasons the notebook could not detect — residue drift against today's UniProt, deleted entries, a razor pick MaxQuant withheld — and 54 of those would have been tested. Measured, this route recovers 9 of 14 (§ Nine of fourteen). Holding "12" as the exit criterion would make passing it a matter of *reducing the refusals*, which is the opposite of the point: the criterion would be satisfied by ingesting sites the platform cannot validate.

*Exit:* PXD018299 ingested end to end and analysed through the platform's own statistics layer rather than a notebook, with

- **the population reported at every step**, and any divergence from the notebook's 1,375 accounted for exactly rather than approximately — today `1,321 + 54 refused-but-testable = 1,375`;
- **every unrecovered published target traced** to refusal or to threshold, so a miss is explained rather than counted;
- **the recovery figure recorded with its population**, whatever it is. A number is not the criterion; an unexplained number is the failure.

A site moves from ambiguous to `basis = uba7_knockout, confidence = confirmed`, and the superseded assignment remains inspectable.

Two things the old wording also assumed and that are **not yet true**, both blocking a literal reading of "through the real pipeline": gene symbols never enter the graph (`Gene` has no nodes, `Protein.name` is null on all **4,561** — corrected 2026-08-08 from 4,441, which the repository contradicts in five places), so target identification still reads the deposit's `Gene names`. **Decided 2026-08-08 and no longer open as a modelling question**: the symbol's home is `Gene.symbol`, not `Protein.name` — routing it onto `Protein` would make `Gene.symbol` redundant (ONTOLOGY.md §4). The blocker is now named and measured: `Gene.id` is an `hgnc:` CURIE, `Resolution.gene` is a *symbol*, and UniProt's payload does carry the id (`HGNC:7532` for `P20591`, measured) while the entry cache stores the parse rather than the payload — so nothing on disk has it. ONTOLOGY.md §11 Q12 holds the open part, which is what the cache should store — and as of 2026-08-09 Q12 is itself **blocked on a layer below it**: every answer re-writes `cache/uniprot/entry/{canonical}.json`, a tier whose key carries no version and which `ONTOLOGY.md` §8 and `OPERATIONS.md` §3 both wrongly called immutable until that date. **Both were settled on 2026-08-09**: the tier was split (`OPERATIONS.md` §3.1), Q12 was answered, and `Gene` was minted — **1,039 nodes, 1,054 `ENCODES` edges**, with `gene_absence` naming why the other 3,507 proteins have none (1,044 / 1,059 / 3,502 until the cold-clone rebuild the same day corrected them — ONTOLOGY.md §4). Target identification is answerable from stored content: 12 of 14 by exact symbol, 13 counting the `DDX58`→`RIGI` rename. The projected reach of ~3,231 was wrong by a factor of three because it counted cached entries rather than resolved accessions.; and I11 is met at **site grain only** since 2026-08-08: `quant_ref` is `site_values` on all 2,029 `SiteObservation`s and `quant.duckdb` holds 48,696 cells, so the site matrix is retained rather than re-read (ADR-0004, ADR-0013) — while `ProteinObservation` retains nothing. **The trailing clause read *"no adapter writing its cells"* and is false as of 2026-08-10**: `bzk/adapters/maxquant_protein_groups.py` writes them, and measured offline over `HAP1_USP18KO_proteinGroups.txt` would write 67,158. The half stays unmet because the *deposit* cannot supply a `Sample` for those fourteen columns — see § *Outcome: the MaxQuant protein adapter* — which is a different blocker in a different layer, and worth distinguishing precisely because the old wording would have gone on reading true. Gene symbols and the protein grain both remain on that reading.

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

**The ADR clause is met, 2026-08-09.** *"ADRs 0004–0014 written"* names eleven records; 0004, 0005
and 0013 already existed and the remaining eight — 0006–0012 and 0014 — were written that day, so
the range is complete. Three of the eight land as `Superseded` rather than `Proposed` because they
record decisions already replaced (0007 by 0011, 0011 by 0015, 0014 by 0017), and none lands
`Accepted`: `decisions/README.md` requires a review round-trip and records why eight of them landing
`Accepted` in one commit would have asserted one that had not happened. **0018 is the only reserved
number still unwritten**, and it is outside this range.

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

   **Tested against the 2026-08-11 dependency redraw and found not to block it — and it had been read the other way first.** The reading that stopped a redraw was that *which adapter is the v0.1 path* depends on this answer, so the axis could not be drawn until he supplied one. **That is wrong, and the test is to run both branches.** If the answer is *Perseus results*, the Perseus adapter needs a real Perseus table carrying a `Difference` and a p-value — from him. If the answer is *search-engine output*, the MaxQuant path is primary, is already ingested from a public deposit, and the Perseus adapter **still** needs that same table before its exit is met. The row is dependent under **both** branches, so the answer moves nothing across the axis: it changes which path he would reach for first, not what he must supply. Every other row on the redraw is likewise unmoved by it — `perseus_s0` waits on parameter values under either answer, and the protein-groups mapping is untouched by it entirely.

   **What it does bear on is retrospective, which is why it cannot gate a plan.** Its two recorded consequences are whether retaining the raw matrix is *essential or merely prudent* (this entry) and whether *A may prove sufficient and B over-engineered* (ADR-0017 § Open). ADR-0017 is `Accepted`, its Decision is **B, both ingestion paths**, and both are on disk — `bzk/adapters/perseus.py` and `bzk/adapters/maxquant_sites.py`. An answer arriving now cannot un-build them; it can only tell us whether building both was worth it. **Evaluating a decision already executed is not the same as blocking one not yet taken**, and conflating the two is what turned an open question into a stop.
5. When do the recorded assumptions get revisited? Suggested trigger: first real dataset from the collaborating project, whenever that arrives.
