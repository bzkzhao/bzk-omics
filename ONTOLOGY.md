# ONTOLOGY.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 1.16 |
| Last reviewed | 2026-08-07 |
| Depends on | `VISION.md` |
| Depended on by | `ARCHITECTURE.md`, ingestion adapters, statistics module, UI |
| Authoritative for | Node types, edge types, field semantics, invariants |

This document is the single source of truth for the data model. No other document may define a node type, edge type, or field. Where another document needs one, it references this file.

DDL is given in Kùzu syntax, **validated against 0.11.3** — all statements in §4–§7 execute unchanged, including `STRING[]` columns and `MANY_MANY` multiplicity. Every column is declared in its table's `CREATE`; the document specifies a schema, not the order in which it was designed. It is normative: an implementation that diverges is wrong, or this document is wrong and must be amended before the code is.

---

## 1. The central distinction

The graph is partitioned into two disjoint node sets.

**Reference nodes** describe entities that exist independently of any measurement. A lysine at position 42 of a given protein sequence exists whether or not it was ever observed. Reference nodes are imported from external authorities and are never authored locally.

**Evidence nodes** describe what this laboratory did and found. They are authored locally and carry provenance.

The two sets are joined only through observation nodes. This is the load-bearing constraint of the entire model: it is what allows the system to distinguish *"we measured this"* from *"the literature says this"*, and to answer either question without contaminating the other.

```
REFERENCE                          EVIDENCE
─────────                          ────────
Gene                               Project
Protein ──[HAS_SEQUENCE]──┐        Experiment
ProteinSequence ◄─────────┘        Sample
     ▲ [SITE_ON]
ModificationSite ◄──[MEASURED_AT]── SiteObservation
Modifier ◄────[ASSIGNS]──────────── ModifierAssignment
Pathway                            Dataset
Disease                            Analysis
Drug                               DifferentialResult
Publication                        Person, Software
```

---

## 2. Storage boundary

The graph stores **identity, relationships, and provenance**. It does not store per-sample quantitative matrices.

A diGly experiment produces a site × sample matrix that reaches millions of cells across a handful of datasets. Property graphs handle this badly. Quantitative values live in columnar storage (DuckDB / Parquet), keyed by `SiteObservation.id`, and are joined at query time.

Rule: if a value is one-per-entity, it is a graph property. If it is one-per-entity-per-sample, it is columnar.

---

## 3. Identifiers

All external identifiers are **CURIEs** — `prefix:local_id` — resolved against the prefix map below, which is maintained here and nowhere else (`CLAUDE.md` § Single source of truth).

| Prefix | Authority | Example |
|---|---|---|
| `uniprot` | UniProtKB | `uniprot:P05161` |
| `hgnc` | HGNC | `hgnc:4053` |
| `ensembl` | Ensembl | `ensembl:ENSG00000187608` |
| `unimod` | Unimod | `unimod:121` |
| `mod` | PSI-MOD | `mod:00492` |
| `reactome` | Reactome | `reactome:R-HSA-1169408` |
| `go` | Gene Ontology | `go:GO:0032020` |
| `mondo` | MONDO | `mondo:MONDO_0004992` |
| `chebi` | ChEBI | `chebi:CHEBI:15377` |
| `doi` / `pmid` | Publications | `pmid:21139048` |

Locally generated (evidence) nodes use `bzk:` with a **deterministic, content-derived id**: `bzk:` followed by a truncated SHA-256 over a canonical serialization of the node's identity — its label, its identifying fields, and the ids of the content-addressed nodes it anchors to (reference CURIEs, the `ModificationSite` key, `Dataset.content_hash`). The same input therefore yields the same id on re-ingestion: identical content converges on one node rather than minting a new one, which is what makes replay idempotent under I9. Mutable and provenance-timestamp fields (`asserted_at`, `retracted_at`, `created_at`) are excluded from identity, so retraction and supersession follow I6 without changing an id. This extends I7's key discipline from reference nodes to evidence nodes; see ADR-0020.

**Node identity, per label.** Every id in this graph is content-derived (I7). The two halves of §1 *encode* that differently, and the difference is deliberate:

- **Reference nodes carry human-readable composite keys** — an authority's own identifier, optionally composed with local structure, per the §4 templates.
- **Evidence nodes carry opaque digests** — `bzk:` plus a truncated SHA-256 (ADR-0020).

The identity **model** is identical for both: a node's identity is its label, its identifying fields, the ids of its anchors, and — where it has one — the field values of a **qualifying child**. Only the encoding differs, and it differs because the inputs do. A reference key composes identifiers an authority already minted, few and short enough to read by eye and check in a URL. An evidence identity spans peptide sequences, parameter sets and several anchors at once; no readable concatenation survives that, so it is hashed.

**Why a child's *values* and not its id.** An anchor contributes its **id**; a qualifying child contributes its **field values**, and the distinction is load-bearing rather than stylistic. `Imputation` already anchors *to* its `Analysis`, so `Imputation.id ← Analysis.id`. Adding `Analysis.id ← Imputation.id` would close a cycle and neither id could be computed. Taking the child's *values* instead leaves a DAG: every `Analysis` id is computable from child field values alone, and every `Imputation` id from the `Analysis` id that produces — one pass, no cycle. This is not obvious from the table, which is why it is written here.

**Configuration belongs in identity; products never do.** This is the durable rule, not the single instance that prompted it. A child of an `Analysis` is either **configuration** — it determines what the analysis computed, so two analyses differing only in it are different analyses — or a **product** — the analysis emitted it. `Imputation` is configuration: §6.5 and I15 make the seed mandatory precisely because it materially determines the result, and two runs differing only in seed produce different numbers. `DifferentialResult`, `ModifierAssignment` and `EnzymeAssociation` are products; folding a product into its producer's identity would be circular in meaning as well as in computation. Any future child of an `Analysis` must be classified before it is added.

**Canonical ordering.** `IMPUTATION_FOR` is `MANY_ONE`, so several `Imputation`s may attach to one `Analysis`. The folded set is therefore sorted into a canonical order before hashing, exactly as the order-sensitive list fields are (`filters_applied`, `candidate_modifiers`, `candidate_proteins`). This also **depends on the float canonicalization rule**, which is stated nowhere yet and unimplemented: `downshift_sd` and `width_sd` are `DOUBLE`s, so `1.8` and `1.80` would fold to different `Analysis` ids until that rule exists. Recorded in `HANDOFF.md` §8 as part of the key builder's contract.

**This table, not the key builder, defines identity; the builder mirrors it.** `tests/test_schema.py` checks it against the DDL in four directions: every node table in the DDL has exactly one row; every identifying and excluded name is a real column of that node; **every column is accounted for, listed as identifying or in `Excluded columns`**; and every anchor names a real relationship *whose declared endpoints are this node and that anchor* — not merely a relationship that exists. A column that is neither identifying nor excluded is a silent default to non-identifying, which is the missing-field collision this scheme exists to prevent, and the completeness check turns adding a column into a forced row edit. The exclusions fall in three families — mutable and provenance timestamps (`asserted_at`, `retracted_at`, `created_at`, `started_at`, `ended_at`); `quant_ref` and the quantitative outputs a node reports; and descriptive free text (`label`, `rationale`) — but the per-row `Excluded columns` list is authoritative, since prose categories cannot be checked.

**Reference nodes.** The key is the §4 template; the identifying fields below are what that template composes. Where a row's identifying fields are `—`, the id *is* the authority's identifier and no column composes it.

| Node type | Identifying fields | Anchors (via edge) | Excluded columns |
|---|---|---|---|
| `Gene` | — (authority-assigned) | — | `symbol`, `ensembl_id`, `name` |
| `Protein` | `accession` | — | `name`, `organism_taxid` |
| `ProteinSequence` | `sequence_version` | `Protein` (`HAS_SEQUENCE`) | `sequence` |
| `ModificationSite` | `residue`, `position`, `modification_type` | `ProteinSequence` (`SITE_ON`) | — |
| `Modifier` | — (authority-assigned) | — | `name`, `c_terminal_motif`, `leaves_gg_remnant` |
| `Pathway` | — (authority-assigned) | — | `name`, `source` |
| `Disease` | — (authority-assigned) | — | `label` |
| `Drug` | — (authority-assigned) | — | `label` |
| `Publication` | — (authority-assigned) | — | `title`, `year` |

**Evidence nodes.** The digest is computed over the identity tuple below.

| Node type | Identifying fields | Anchors (via edge) | Excluded columns |
|---|---|---|---|
| `Project` | `title` | — | `created_at` |
| `Experiment` | `title`, `modality`, `organism_taxid` | `Project` (`CONTAINS`) | — |
| `Sample` | `cell_line` / `model_system`, `source_type`, `genotype`, `treatment`, `timepoint_h`, `replicate`, `replicate_type`, `organism_taxid` | `Experiment` (`PERFORMED_ON`) | `label` |
| `Dataset` | `content_hash` | — (the SHA-256 of the raw file is itself the anchor) | `label`, `source`, `external_accession`, `acquisition_mode`, `instrument`, `search_engine`, `search_engine_version`, `library_type`, `library_prediction_model`, `fasta_release`, `embargo_holder`, `embargo_reference`, `embargo_released_at` |
| `SiteObservation` | `peptide_sequence` | `Dataset` (`REPORTED_BY`), `ModificationSite` (`RESOLVES_TO_SITE`) | `localization_prob`, `score`, `is_decoy`, `n_imputed`, `quant_ref` |
| `ProteinObservation` | — | `Dataset` (`REPORTS_PROTEIN`), `Protein` (`RESOLVES_TO_PROTEIN`) | `quant_ref`, `n_peptides` |
| `Contrast` | `numerator`, `denominator` | — (placement unsettled — §11 Q1) | `label` |
| `Analysis` | `kind`, `basis`, `confidence`, `quantity`, `localization_threshold`, `filters_applied`, `test`, `fdr_method`, `external_tool`, `external_version`, `parameters_observed`, `parameters_json` | `Dataset` (`USED`) — one or more; for a curation analysis the asserted content stands in for it | `label`, `rationale`, `started_at`, `ended_at`, `workflow_id`, `workflow_revision` |
| `Imputation` | `method`, `downshift_sd`, `width_sd`, `seed`, `scope` | `Analysis` (`IMPUTATION_FOR`) | `n_values_imputed`, `n_values_total`, `asserted_at`, `retracted_at` |
| `ModifierAssignment` | `basis`, `candidate_modifiers`, `confidence` | `Modifier` (`ASSIGNS`), `SiteObservation` (`ASSIGNMENT_FOR`), `Analysis` (`ASSIGNMENT_SUPPORTED_BY`) / `Publication` (`ASSIGNMENT_CITES`) | `rationale`, `asserted_at`, `retracted_at` |
| `EnzymeAssociation` | `direction`, `basis`, `confidence` | `SiteObservation` (`ASSOCIATION_FOR`), `Protein` (`ASSOCIATION_ENZYME`), `Analysis` (`ASSOCIATION_SUPPORTED_BY`) / `Publication` (`ASSOCIATION_CITES`) | `effect_size`, `adj_p_value`, `rationale`, `asserted_at`, `retracted_at` |
| `ProteinAssignment` | `basis`, `candidate_proteins`, `confidence` | `SiteObservation` (`PROTEIN_ASSIGNMENT_FOR`), `Protein` (`ASSIGNS_PROTEIN`) | `rationale`, `asserted_at`, `retracted_at` |
| `DifferentialResult` | `protein_adjusted`, `adjustment_method` (I4's required declaration of result *kind*. A single site-level `Analysis` emits **both** where a matched proteome exists — the uncorrected result (not_applied) and the corrected one (applied, carrying `ADJUSTED_BY` to the protein result it used) — so they share `WAS_GENERATED_BY`, observation and contrast and are separated *only* by these fields; the correction is a within-analysis step, not a separate `Analysis`. Holding both is what lets a user see what the correction did — `ARCHITECTURE.md` §4) | `Analysis` (`WAS_GENERATED_BY`), `SiteObservation` (`RESULT_FOR_SITE`) / `ProteinObservation` (`RESULT_FOR_PROTEIN`), `Contrast` (`RESULT_IN_CONTRAST`) | `log2fc`, `p_value`, `adj_p_value` |

| `Person` | `orcid`, `name` | — | — |
| `Software` | `name`, `version` | — | `container_digest` |

The last two rows are the exception to the digest rule: provenance agents key on their natural external identifiers, and **ADR-0021 settles how** — this line previously described a fallback key, which was the defect. `Software` keys on `name` + `version`; `container_digest` is a non-identifying attribute, because without a digest there is no evidence that two builds differ, and claiming to distinguish them asserts more than the data supports (I19's discipline). `Person` identity comes from the **curation export and never from an ingest-time inference** — where no ORCID exists the curator supplies a discriminator.

`Person` keys on a **composite of `orcid` and `name`, not a fallback**: both always enter the tuple and `orcid` may be null, so there is no conditional *use one else the other* — the structure ADR-0021 forbids and the structure this line previously described. Be precise about what that fixes. Adding an ORCID to a curation record **still changes that person's id**. What changed is where the dependency lives: the defect was never that an id can change, but that it depended on something *outside* I9's input set — what a particular ingest happened to know. The curation export is inside that set, versioned and diffable, so replay from a given curation state is deterministic and a correction is a visible edit rather than an accident of ingest order. This is why `Person.orcid`'s absence is classified **curated** rather than **determined**: a curator's judgement is not the data forcing a null, and the classification says so instead of letting the weaker guarantee hide inside the stronger word.

**Absence must be determined or curated, never contingent.** An identifying field may be null — but only when something outside the moment of ingest fixes that null. The kinds are indistinguishable in storage and must therefore be declared:

- **Determined.** Another recorded field, or a stated structural fact, forces the null. A protein-grain `Analysis` has no `localization_threshold` because a protein-grain quantity has no residue positions to localise. Replay produces the same null every time.
- **Curated.** A versioned human judgement fixes it — not the data. `Person.orcid` is the only instance: a curator recorded that no ORCID exists. Legitimate **only** where the node's identity is curation-sourced (ADR-0021), because the curation export is inside I9's input set, so replay from a given curation state is still deterministic. Weaker than `determined`, and named separately so it cannot hide inside it.
- **Contingent.** The knowledge had simply not arrived — an ORCID not to hand, a digest not yet recorded. The null describes the moment, not the entity, so the id becomes a function of *when you looked*, which ADR-0020 forbids.

**A `determined` classification is an assertion nothing can verify, so it must name *what* determines the absence** — another field, or a stated data fact. A row whose reason names neither is suspect and should be re-examined rather than trusted. The guard requires a non-empty reason and rejects any `contingent` row outright, forcing a redesign instead of licensing the state; it cannot check that a reason is *true*. It also requires that an identifying field found absent in committed data be declared here, so an unclassified absence cannot pass unnoticed. See ADR-0021.

| Node type | Field | Absence | Determined by |
|---|---|---|---|
| `Sample` | `cell_line` | determined | `source_type` — NULL for tissue |
| `Sample` | `model_system` | determined | `source_type` — NULL in vitro; exactly one of this and `cell_line` is present |
| `Analysis` | `basis` | determined | `kind` — curation only (§5.3) |
| `Analysis` | `confidence` | determined | `kind` — curation only (§5.3) |
| `Analysis` | `quantity` | determined | `kind` — a curation analysis consumes none (I16) |
| `Analysis` | `localization_threshold` | determined | `quantity` — a protein-grain quantity has no residue positions to localise (§6.4) |
| `Analysis` | `test` | determined | produces no `DifferentialResult` — an analysis that runs no test generates none; I15 keys on the same predicate |
| `Analysis` | `fdr_method` | determined | as `test` — the FDR step exists only where a test does |
| `Analysis` | `external_tool` | determined | `kind` — external runs only (§5.4) |
| `Analysis` | `external_version` | determined | `kind` — as `external_tool` |
| `Analysis` | `parameters_json` | determined | `test` — NULL when the test takes no further parameters; `perseus_s0` requires `s0` and the randomisation count, which ARCHITECTURE §4 makes mandatory |
| `Imputation` | `downshift_sd` | determined | `method` — NULL unless downshifted normal |
| `Imputation` | `width_sd` | determined | `method` — as `downshift_sd` |
| `Imputation` | `seed` | determined | `method` — stochastic methods only (I15) |
| `Imputation` | `scope` | determined | `method` — NULL when nothing is imputed |
| `DifferentialResult` | `adjustment_method` | determined | `protein_adjusted` — NULL if `not_applied` (I4) |
| `Person` | `orcid` | curated | the curation record states that none exists — a curator's judgement, not a data fact; see the provenance-agent note above |

`workflow_id` and `workflow_revision` were classified `determined` here and are **no longer identifying at all**. Nothing recorded forces their null — they are the only `Analysis` columns the DDL does not annotate — so "no workflow engine was used" and "the workflow id has not been recorded" are indistinguishable, which is precisely the contingent shape. They move to `Excluded columns` on the same reasoning ADR-0021 applies to `Software.container_digest`: absent a recorded revision there is no evidence two runs differ. Should a workflow engine later make them reliably present, they can return to identity with their absence determined by a recorded field.

**Qualifying child fields.** The third identity component. One instance today; the config-vs-product rule above governs any future one.

| Node type | Child (via edge) | Field values folded in |
|---|---|---|
| `Analysis` | `Imputation` (`IMPUTATION_FOR`) | `method`, `seed`, `downshift_sd`, `width_sd`, `scope` |

`ModifierAssignment` anchors on `ASSIGNS` because the concluded modifier **is** the assertion. `candidate_modifiers` is the surviving candidate *set*, which diverges from the conclusion whenever more than one candidate remains: two assignments over one site, from one publication, with the same basis, candidate set and confidence, concluding ubiquitin and ISG15 respectively, are two distinct claims and must not share an id. That is the Ub-vs-ISG15 distinction the platform exists to make (`VISION.md`), and `ProteinAssignment` already anchors its pick the same way.

**`parameters_json` is canonicalized before hashing.** It is an identifying field of `Analysis` and, under the test scheme (§5.4, I16), carries `s0` and the randomisation count. Canonicalizing the identity *tuple* treats each field as a value and does not reach inside a string, so `parameters_json` is itself parsed and canonically re-serialized — sorted keys, normalized numeric forms — before it enters the tuple, never hashed as raw text. Otherwise two ingesters emitting the same parameters with different key order, spacing, or float formatting would produce different `Analysis` ids, defeating the idempotent replay this scheme exists to guarantee (ADR-0020).

**Queryability tradeoff, accepted.** Holding `s0` inside `parameters_json` rather than as a column means analyses cannot be filtered by `s0` without string matching, and ADR-0015 makes `perseus_s0` default and required, so that value *will* be queried. This is accepted deliberately: a column per test parameter does not generalize across tests — permutation counts, shrinkage priors and the rest all differ — and the recomputation and comparison the registry exists for read parameters per analysis, not by a cross-analysis `s0` filter. If an `s0` index is ever needed it is added then, not pre-emptively.

> **To verify, no longer blocking:** the PSI-MOD accession for the GlyGly remnant is unconfirmed and must be checked against the current PSI-MOD release before it is displayed anywhere. It is not urgent: §4 pins Unimod as the sole key authority, so PSI-MOD is a cross-reference only and an unconfirmed value can no longer fragment a `ModificationSite` id.

---

## 4. Reference nodes

```cypher
CREATE NODE TABLE Gene(
  id STRING,                    -- CURIE, hgnc:
  symbol STRING,                -- HGNC approved symbol
  ensembl_id STRING,
  name STRING,
  PRIMARY KEY (id));

CREATE NODE TABLE Protein(
  id STRING,                    -- CURIE, uniprot:ACCESSION. An isoform carries its
                                -- suffix in the accession (uniprot:P09914-2); there is
                                -- no separate isoform column. Stable identity: no
                                -- sequence, no version. See ADR-0005.
  accession STRING,
  name STRING,
  organism_taxid INT64,
  PRIMARY KEY (id));

CREATE NODE TABLE ProteinSequence(
  id STRING,                    -- deterministic; uniprot:ACCESSION#sv{n}. See key template.
  sequence_version INT64,       -- REQUIRED. See invariant I2.
  sequence STRING,
  PRIMARY KEY (id));

CREATE NODE TABLE ModificationSite(
  id STRING,                    -- deterministic; see key template below
  residue STRING,               -- single-letter, e.g. 'K'
  position INT64,               -- 1-based, against ProteinSequence.sequence_version
  modification_type STRING,     -- CURIE, unimod:
  PRIMARY KEY (id));

CREATE NODE TABLE Modifier(
  id STRING,                    -- CURIE, uniprot: of the modifier protein
  name STRING,                  -- 'ubiquitin' | 'NEDD8' | 'ISG15' | 'FAT10'
  c_terminal_motif STRING,      -- 'LRGG' etc.
  leaves_gg_remnant BOOLEAN,    -- tryptic K-ε-GG remnant. See §6.
  PRIMARY KEY (id));

CREATE NODE TABLE Pathway(id STRING, name STRING, source STRING, PRIMARY KEY (id));
CREATE NODE TABLE Disease(id STRING, label STRING, PRIMARY KEY (id));
CREATE NODE TABLE Drug(id STRING, label STRING, PRIMARY KEY (id));
CREATE NODE TABLE Publication(id STRING, title STRING, year INT64, PRIMARY KEY (id));

CREATE REL TABLE ENCODES(FROM Gene TO Protein, ONE_MANY);
CREATE REL TABLE HAS_SEQUENCE(FROM Protein TO ProteinSequence, ONE_MANY);
CREATE REL TABLE SITE_ON(FROM ModificationSite TO ProteinSequence, MANY_MANY);  -- see §6.3
CREATE REL TABLE ANNOTATED_IN(FROM Protein TO Pathway, source STRING, evidence_code STRING);
```

**Key templates.** Every reference key is content-derived (I7) and readable. Two shapes.

*Authority-assigned* — the id **is** the external identifier, CURIE-prefixed per the §3 map. Nothing local composes it.

| Node | Prefix | Example |
|---|---|---|
| `Gene` | `hgnc:` | `hgnc:5699` |
| `Modifier` | `uniprot:` | `uniprot:P05161` |
| `Pathway` | `reactome:` | `reactome:R-HSA-1169408` |
| `Disease` | `mondo:` | `mondo:MONDO_0004992` |
| `Drug` | `chebi:` | `chebi:CHEBI:15377` |
| `Publication` | `pmid:` | `pmid:21139048` |

*Composed* — local structure over an authority identifier. Each composes **its anchor's id** (§3) with **its own identifying fields**, which is the same rule the evidence digests follow; only the encoding differs.

```
Protein           uniprot:{accession}
ProteinSequence   {Protein.id}#sv{sequence_version}
ModificationSite  {ProteinSequence.id}#{residue}{position}#{modification_type}

  uniprot:P05161      /  uniprot:P05161#sv1      /  uniprot:P05161#sv1#K42#unimod:121
  uniprot:P09914-2    /  uniprot:P09914-2#sv2    /  uniprot:P09914-2#sv2#K376#unimod:121
```

`{accession}` is the full UniProt accession **including any isoform suffix** — `P09914-2` *is* an accession, not a canonical accession plus a property. There is no separate isoform field to compose.

A `ModificationSite` key composes **exactly one** `ProteinSequence`. `SITE_ON` is declared `MANY_MANY`, which permits more than the key can express; in practice a site carries one `SITE_ON`, to the sequence it is keyed against, and multi-mapping is carried by `ProteinAssignment.candidate_proteins` (§6.3). The declaration is wider than the key — recorded, not resolved.

**Key canonicalization.** A key that can be written two ways is two ids for one fact — ADR-0020's fragmentation, mirrored into the reference half, and it sits under every observation in the graph. Fixed forms:

- **`modification_type` is keyed on Unimod, always.** §3's prefix map lists both `unimod` and `mod` (PSI-MOD); a site keyed `unimod:121` and the same site keyed `mod:00492` would fragment into two nodes, defeating I7 in the very words it is written in — *identical entities from different sources converge on one node*. Unimod is primary because it is what MaxQuant and FragPipe emit. **A PSI-MOD accession is a cross-reference only and never a key component.**
- **`sequence_version`** renders as a bare decimal integer, unpadded: `#sv4`, never `#sv04`.
- **`residue`** is a single uppercase letter: `K`, never `k`.
- **`accession`** keeps UniProt's own casing, uppercase, with any `-N` suffix: `P09914-2`.
- **CURIE prefixes** are lowercase and spelled exactly as in the §3 map. The *local part* keeps its authority's casing, so `chebi:CHEBI:15377` and `go:GO:0032020` are correct as written.

`ModificationSite.id` is deterministic and content-derived, so the same site ingested from two datasets resolves to one node.

**Both the sequence version and the isoform are part of the key**, and for the same reason: position numbering is only meaningful relative to a specific sequence. `P05161#sv1#K42` and `P05161#sv2#K42` may be different lysines because the sequence was amended; `P09914#K376` and `P09914-2#K376` are different lysines because the isoforms differ in length and numbering.

**`Protein` and `ProteinSequence` are separate nodes** because the same argument applies one level up, and applies differently to different edges. A protein's identity outlives any one version of its sequence: `uniprot:Q9UMW8` is USP18 whatever UniProt does to the sequence record. But a *position* is meaningless without a specific sequence, so the thing a site attaches to must be version-specific. Hence `SITE_ON` targets a `ProteinSequence`, while everything whose meaning is version-independent — `ENCODES`, `ANNOTATED_IN`, `ASSOCIATION_ENZYME` (§6.2), `ASSIGNS_PROTEIN` (§6.3), `RESOLVES_TO_PROTEIN` (§5.1) — targets the stable `Protein`. A protein-level quantification measures a gene product, not a sequence version, and carries no residue positions; its `Dataset` anchor already records which search produced it.

A single `Protein` node could not do both jobs: it cannot carry two `sequence_version`s at once, yet sites legitimately pinned at two different versions can attach to the same protein. See ADR-0005.

Measured on PXD018299: resolving `P09914-2` position 376 against the *canonical* IFIT1 sequence returns threonine, and `P62195-2` position 47 returns alanine. Both validate correctly against their own isoform sequences. A schema that treated isoform as a property rather than part of the key would silently merge these with their canonical counterparts and place modifications on the wrong residues.

**Resolution must therefore fetch isoform sequences directly** (`rest.uniprot.org/uniprotkb/P09914-2.fasta`), never strip the suffix to the canonical accession.

**An isoform's `sequence_version` is taken from its parent entry's `entryAudit.sequenceVersion`.** UniProt versions the canonical entry; the isoform FASTA carries no independent version. The `sv` in a key such as `P09914-2#sv2#K376` is therefore the canonical entry's sequence version at resolution time. This is correct in the common case but has a known limitation — see §11 Q5.

---

## 5. Evidence nodes

```cypher
CREATE NODE TABLE Project(id STRING, title STRING, created_at TIMESTAMP, PRIMARY KEY (id));

CREATE NODE TABLE Experiment(
  id STRING, title STRING,
  modality STRING,              -- 'digly_proteomics' | 'proteomics' | 'rnaseq'
  organism_taxid INT64,
  PRIMARY KEY (id));

CREATE NODE TABLE Sample(
  id STRING, label STRING,
  source_type STRING,           -- 'cell_line' | 'tumour_tissue' | 'primary_cell'
  cell_line STRING,             -- NULL for tissue
  organism_taxid INT64,         -- REQUIRED. Mouse and human coexist in one graph.
  model_system STRING,          -- e.g. '4T1 BALB/c subcutaneous'; NULL in vitro
  genotype STRING,              -- e.g. 'USP18-/-', 'USP18 C64R/C65R'
  treatment STRING,             -- e.g. 'IFN-alpha2b 10 U/mL'
  timepoint_h DOUBLE,
  replicate INT64,
  replicate_type STRING,        -- 'biological' | 'technical'
  PRIMARY KEY (id));

CREATE NODE TABLE Dataset(
  id STRING, label STRING,
  source STRING,                -- 'local' | 'pride' | 'embargoed'
                                -- 'embargoed' = unpublished, shared under
                                -- collaboration. See §5.2 and I18.
  external_accession STRING,    -- e.g. 'PXD018299'; NULL if local
  acquisition_mode STRING,      -- 'dda' | 'dia' | 'prm' | 'srm'
  instrument STRING,            -- e.g. 'Orbitrap Fusion Lumos'
  search_engine STRING,         -- 'diann' | 'maxquant' | 'fragpipe' | 'spectronaut'
  search_engine_version STRING,
  library_type STRING,          -- 'predicted' | 'experimental' | 'hybrid' | NULL for DDA
  library_prediction_model STRING,  -- REQUIRED if library_type = 'predicted'
  fasta_release STRING,         -- UniProt release used for the search
  content_hash STRING,          -- SHA-256 of the ingested source file
  embargo_holder STRING,        -- §5.2; who controls release
  embargo_reference STRING,     -- §5.2; manuscript or agreement
  embargo_released_at TIMESTAMP,-- §5.2; NULL while embargoed
  PRIMARY KEY (id));

CREATE NODE TABLE SiteObservation(
  id STRING,
  peptide_sequence STRING,
  localization_prob DOUBLE,     -- 0–1
  score DOUBLE,
  is_decoy BOOLEAN,
  n_imputed INT64,              -- values generated rather than measured; see §6.5
  quant_ref STRING,             -- key into columnar store; see §2
  PRIMARY KEY (id));

CREATE NODE TABLE ProteinObservation(
  id STRING, quant_ref STRING, n_peptides INT64, PRIMARY KEY (id));


CREATE NODE TABLE Contrast(
  id STRING, label STRING,      -- e.g. 'IFNb_8h vs mock'
  numerator STRING, denominator STRING,
  PRIMARY KEY (id));

CREATE NODE TABLE DifferentialResult(
  id STRING,
  log2fc DOUBLE,
  p_value DOUBLE,
  adj_p_value DOUBLE,
  protein_adjusted STRING,      -- REQUIRED. 'applied' | 'not_applied' | 'native'
                                -- 'native' = source already ratiometric. See I4.
  adjustment_method STRING,     -- NULL if 'not_applied'
                                -- 'residual_vs_protein_lfc' | 'maxquant_mod_base_ratio'
  PRIMARY KEY (id));

CREATE NODE TABLE Analysis(
  id STRING, label STRING,
  kind STRING,                  -- 'processing' | 'curation' | 'external'
                                -- 'external' = run outside the platform;
                                -- parameters recorded, not observed. §5.4
  basis STRING,                 -- curation only; enum in §5.3
  confidence STRING,            -- curation only; 'authoritative' | 'inferred'
  rationale STRING,
  quantity STRING,              -- CLOSED enum (mirror: schema.py QUANTITY_VALUES): 'intensity' |
                                -- 'intensity_multiplicity_summed' | 'ratio_mod_base' | 'lfq' | 'ibaq'.
                                -- 'intensity' is a plain intensity with NO multiplicity axis
                                -- (protein- or precursor-level: proteinGroups, DIA-NN) — the only
                                -- place bare 'intensity' is legal. A MaxQuant modification-site
                                -- source HAS a multiplicity axis and MUST use
                                -- 'intensity_multiplicity_summed' (the summed Intensity column);
                                -- bare 'intensity' is invalid there. Per-multiplicity consumption
                                -- (the ___n split) is deferred — extend the enum when a
                                -- per-multiplicity analysis is actually run. See I16.
  localization_threshold DOUBLE,-- recorded, never hard-coded; see §6.4
  filters_applied STRING[],     -- e.g. ['reverse','potential_contaminant']
  test STRING,                  -- 'perseus_s0' | 'moderated_t_ebayes' | 'welch_t'; per analysis (§5.4, I16)
  fdr_method STRING,            -- 'permutation' | 'BH'; the FDR control step
  workflow_id STRING, workflow_revision STRING,
  parameters_json STRING,       -- test-specific parameters, e.g. s0, n_randomisations (§5.4).
                                -- Identity-bearing: parsed and canonically re-serialized before
                                -- hashing, never hashed as raw text (§3).
  started_at TIMESTAMP, ended_at TIMESTAMP,
  external_tool STRING,         -- §5.4; 'perseus' | 'r' | 'graphpad'
  external_version STRING,      -- §5.4
  parameters_observed BOOLEAN,  -- §5.4; REQUIRED. See I19.
  PRIMARY KEY (id));

CREATE NODE TABLE Person(id STRING, name STRING, orcid STRING, PRIMARY KEY (id));
CREATE NODE TABLE Software(id STRING, name STRING, version STRING, container_digest STRING, PRIMARY KEY (id));

CREATE REL TABLE CONTAINS(FROM Project TO Experiment, ONE_MANY);
CREATE REL TABLE PERFORMED_ON(FROM Experiment TO Sample, ONE_MANY);
CREATE REL TABLE PRODUCED(FROM Sample TO Dataset);
CREATE REL TABLE REPORTS_SITE(FROM Dataset TO SiteObservation, ONE_MANY);
CREATE REL TABLE REPORTS_PROTEIN(FROM Dataset TO ProteinObservation, ONE_MANY);
CREATE REL TABLE RESULT_FOR_SITE(FROM DifferentialResult TO SiteObservation, MANY_ONE);
CREATE REL TABLE RESULT_FOR_PROTEIN(FROM DifferentialResult TO ProteinObservation, MANY_ONE);
CREATE REL TABLE RESULT_IN_CONTRAST(FROM DifferentialResult TO Contrast, MANY_ONE);
CREATE REL TABLE ADJUSTED_BY(FROM DifferentialResult TO DifferentialResult, MANY_ONE);
CREATE REL TABLE SAMPLE_GENERATED_BY(FROM Sample TO Analysis, MANY_ONE);
CREATE REL TABLE CURATION_CITES(FROM Analysis TO Publication);
```

### 5.1 The `Observation` supertype

Kùzu has no inheritance, so the supertype is a **contract**, not a table. Every observation type MUST provide:

| Field / edge | Meaning |
|---|---|
| `id` | `bzk:` + deterministic content-derived digest (§3, ADR-0020) |
| `quant_ref` | Key into the columnar store (§2) |
| `REPORTED_BY → Dataset` | Which dataset reported it |
| `RESOLVES_TO → <reference node>` | The external entity it measures |
| `WAS_DERIVED_FROM` reachability | Provenance path to an `Analysis` (I5) |

Any code operating on these five things works for every modality without modification. Domain logic lives in the subtype, never in code that consumes the contract.

**Built:**

| Subtype | Resolves to |
|---|---|
| `SiteObservation` | `ModificationSite` |
| `ProteinObservation` | `Protein` |

**Design headroom — not commitments.** The contract above was specified so these remain cheap to add if the anchor laboratory needs them. They are not roadmap items, and nothing in the product should be described as supporting them.

| Candidate | Would resolve to | Trigger |
|---|---|---|
| `EnrichmentObservation` | `Protein` | The group's anti-ISG15 IP-MS and ISG15-ABPP data. Concordance between an enrichment hit and a diGly site is a `ModifierAssignment` basis (§6.1), so this is the first candidate and the only one with a named use |
| `PeptideObservation` | `Protein` + `HlaAllele` | Only if immunopeptidomics starts in the group. Non-tryptic, allele-specific, no modification site |
| `AnalyteObservation` | `Analyte` (LIPID MAPS, ChEBI) | Only if lipidomics enters scope. No UniProt identity, so it needs a separate resolver |

The distinction matters: a contract that *permits* extension costs nothing, whereas a roadmap that *promises* extension is a claim about work not started.

```cypher
CREATE REL TABLE REPORTED_BY(FROM SiteObservation TO Dataset, MANY_ONE);
CREATE REL TABLE RESOLVES_TO_SITE(FROM SiteObservation TO ModificationSite, MANY_ONE);
CREATE REL TABLE RESOLVES_TO_PROTEIN(FROM ProteinObservation TO Protein, MANY_ONE);
```

---

### 5.2 Embargoed datasets

Unpublished data shared by a collaborator is neither `local` nor `pride`. It must be ingestible, queryable and analysable, but must not leave the machine in any export, report or figure until released.

The supporting columns — `embargo_holder`, `embargo_reference`, `embargo_released_at` — are declared on `Dataset` in §5.

Release is an event, not an edit: setting `embargo_released_at` and changing `source` to `pride` records that the data became public, and the prior state remains visible in the graph's history.

This state exists because the platform's first real user is expected to supply unpublished data, and a system that cannot hold it safely cannot be used at all. It is also the point at which local-first stops being a design preference and becomes a condition of the collaboration.

### 5.3 Curation as an activity

To compute anything from a dataset, the platform must know which raw files correspond to which experimental conditions — the **sample-to-condition mapping**. Where SDRF-Proteomics accompanies a submission this is machine-readable. Most PRIDE submissions do not include it, so the mapping is inferred from filenames, submission metadata, or the methods section of the associated paper.

That inference is an assertion about an experiment this laboratory did not perform, and it is frequently wrong. Treated as configuration, an error is invisible in the graph and its correction is destructive: the file is edited, results are recomputed, and nothing records that the design was ever inferred or ever different. Treated as an activity, the provenance chain from `DifferentialResult` through `Contrast` to `Sample` terminates in a recorded curation event with an author, a basis, and a supersession path.

Invariant I5 already requires it. `Sample` is an entity node; a `Sample` conjured from a configuration file reaches no `prov:Activity` and is therefore permanently and correctly flagged `unprovenanced`. Configuration is not an available option.

This is structurally the same problem as modifier ambiguity (§6): an inference the primary measurement does not support, which the field habitually reports as fact. Both receive the same treatment.

**Model.** No separate node type. `Analysis` carries `kind = 'curation'` and gains PROV-O provenance for free.

`basis` is a closed enum:

| Value | Meaning | Confidence |
|---|---|---|
| `sdrf` | SDRF-Proteomics accompanying the submission | `authoritative` |
| `author_correspondence` | Design confirmed directly by the submitters | `authoritative` |
| `submitter_metadata` | Locally generated data, or structured PRIDE metadata | `inferred` |
| `publication_methods` | Read from the methods section of the associated paper | `inferred` |
| `filename_inference` | Deduced from raw file naming conventions | `inferred` |

For locally generated data the curation node is created automatically at ingestion with `basis = 'submitter_metadata'`, so the mechanism costs nothing where the design is already known.

Curation nodes are immutable under I6. A corrected mapping supersedes rather than overwrites, and the retraction propagates to every derived result and figure.

`RESULT_FOR_SITE` and `RESULT_FOR_PROTEIN` attach a `DifferentialResult` to the evidence node it measures — a `SiteObservation`, or at protein grain a `ProteinObservation`, mirroring `RESULT_FOR_SITE`'s target. A protein-level result therefore has a target of its own rather than dangling, and it is what `ADJUSTED_BY`'s target must be reachable from: a site-level result corrected against the matched proteome can be traced to the protein that correction came from.

`ADJUSTED_BY` points a site-level result at the protein-level result used to correct it. Its presence is what makes `protein_adjusted = 'applied'` auditable rather than asserted.

---

### 5.4 External analyses

Perseus has been the standard downstream tool in this field for over a decade and is the collaborating group's workflow. Researchers will not stop using it, and there is no reason they should.

The platform therefore ingests **analysis outputs as well as search-engine outputs**, and an `Analysis` may describe work performed elsewhere.

The supporting columns — `external_tool`, `external_version`, `parameters_observed` — are declared on `Analysis` in §5.

**The distinction `parameters_observed` records is the important one.** When the platform computes a result, it knows the test, the seed, the thresholds and the filtered rows because it performed them. When a result arrives from Perseus, those are *stated by the user* — accurate or not, complete or not. Both are usable; conflating them is not.

`parameters_observed = false` therefore propagates: any `DifferentialResult` generated by an external analysis is labelled as carrying reported rather than observed provenance, wherever it appears.

**Both paths are kept.** Where the underlying quantitative matrix has also been ingested (I11), an externally computed result can be recomputed under a different test and the two compared. Divergence between a Perseus result and a recomputed one is a finding about analytical sensitivity, not a defect — and reporting it is something no existing tool does.

Where only the analysis output exists, the result stands with reported provenance. That is worth less than observed provenance and much more than nothing.

---

## 6. Evidenced inference

Three distinct questions about a modification site share one structure: none is measured directly, each is inferred from perturbation or concordance, and the field routinely reports all three as fact.

| Inference | Question | Evidence |
|---|---|---|
| `ModifierAssignment` | Which UBL produced this remnant? | Knockout, mutant, pulldown, concordance |
| `EnzymeAssociation` | Which enzyme wrote or erased it? | Perturbation of the enzyme |
| `ProteinAssignment` | Which protein does this peptide come from? | Unique peptides, isoform-specific evidence |
| `ImputedValue` | What was the abundance where nothing was detected? | A distributional assumption, nothing more |
| Pathway annotation | What process is the protein in? | Curated external annotation |

**`EvidencedInference` is an abstract supertype.** Kùzu has no inheritance, so it is a contract every subtype MUST satisfy: `basis` (closed enum), `confidence` (`ambiguous` | `probable` | `confirmed`), `rationale`, `asserted_at` / `retracted_at` (immutable, superseded per I6), and an evidence edge to `Analysis` or `Publication`.

Absence of a live non-ambiguous inference is a first-class state, never a default assumption. Adding a fourth layer — site-to-domain, site-to-phenotype, site-to-drug-response — means defining a `basis` enum and a target node. Nothing else changes.

### 6.1 Modifier ambiguity

Ubiquitin, NEDD8, ISG15 and FAT10 all terminate in a diglycine motif. Tryptic digestion leaves an identical K-ε-GG remnant (+114.0429 Da) on the acceptor lysine in every case. Neither the precursor mass nor the MS² fragmentation distinguishes them.

The field's default assumption — that a K-GG site is ubiquitin — holds at baseline because ubiquitin conjugation dominates. Under type I interferon stimulation it does not: *ISG15* and *UBA7* are among the most strongly induced genes, and the ISGylated share of the K-GG population rises substantially. This is the exact condition the platform exists to analyse.

A `SiteObservation` is modifier-agnostic. It records a diGly remnant. The identity of the modifier is a **separate, defeasible inference** carrying its own evidence.

```cypher
CREATE NODE TABLE ModifierAssignment(
  id STRING,
  candidate_modifiers STRING[],   -- e.g. ['uniprot:P0CG48','uniprot:Q15843','uniprot:P05161']
  basis STRING,                   -- enum, below
  confidence STRING,              -- 'ambiguous' | 'probable' | 'confirmed'
  rationale STRING,
  asserted_at TIMESTAMP,
  retracted_at TIMESTAMP,         -- NULL if live; see invariant I6
  PRIMARY KEY (id));

CREATE REL TABLE MEASURED_AT(FROM SiteObservation TO ModificationSite, MANY_ONE);
CREATE REL TABLE ASSIGNMENT_FOR(FROM ModifierAssignment TO SiteObservation, MANY_ONE);
CREATE REL TABLE ASSIGNS(FROM ModifierAssignment TO Modifier, MANY_ONE);
CREATE REL TABLE ASSIGNMENT_SUPPORTED_BY(FROM ModifierAssignment TO Analysis);
CREATE REL TABLE ASSIGNMENT_CITES(FROM ModifierAssignment TO Publication);
```

`basis` is a closed enum. Values marked † are drawn from the disambiguation strategy used in the USP18-dependent ISGylome study (PXD018299), and are directly automatable.

| Value | Meaning | Permitted confidence |
|---|---|---|
| `inferred_default` | No orthogonal evidence; abundance prior only | `ambiguous` |
| `usp18_ko_ifn_enrichment` † | Site enriched in deISGylase-KO cells under IFN | `probable` |
| `isg15_interactome_concordance` † | Parent protein also enriched in anti-ISG15 IP-MS | `probable` |
| `isg15_sirna` † | Site or modified species lost on *ISG15* knockdown | `probable`, `confirmed` |
| `ub_nedd8_negative_control` † | Ub and NEDD8 conjugation shown unchanged | `probable` |
| `uba7_knockout` | Site lost on *UBA7*/*UBE1L* knockout | `probable`, `confirmed` |
| `gg_aa_mutant` | Site lost with ISG15 C-terminal GG→AA | `confirmed` |
| `tagged_pulldown` | Recovered by tagged-modifier affinity purification | `confirmed` |
| `nedd8_inhibitor` | NEDD8 excluded pharmacologically (pevonedistat) | `probable` |
| `orthogonal_ms` | Intact/middle-down or modifier-specific enrichment | `confirmed` |
| `literature` | Reported elsewhere; not measured here | `probable` |

**Every `SiteObservation` has at least one `ModifierAssignment`.** On ingestion the default is created automatically with `basis = 'inferred_default'`, `confidence = 'ambiguous'`, and `candidate_modifiers` populated from all `Modifier` nodes where `leaves_gg_remnant = true`. Assignments are never edited; a new one supersedes and the old is retracted (I6).

`isg15_interactome_concordance` requires an `EnrichmentObservation` (§5.1), which is deferred to v0.2. **Until that subtype exists, no interface may offer this basis** — selecting it would create an assignment whose supporting evidence cannot be represented, which is a dangling inference and worse than an ambiguous one. It is the differentiating capability: computed continuously across every dataset rather than by hand, once, per publication.

This is what permits the query the platform exists for: *which sites across all datasets are lost on ISG15 knockdown, and which are not?*

### 6.2 Enzyme attribution

Mass spectrometry cannot identify which enzyme wrote or erased a mark. The human ISGylation cascade runs through UBA7, UBE2L6, and E3 ligases including HERC5, TRIM25 and ARIH1; removal runs through USP18 and cross-reactive DUBs including USP5, USP14, USP16, USP24 and USP36. No spectrum distinguishes their products.

Attribution requires perturbation. A "USP18-dependent ISGylome" is, structurally, a catalogue of site-to-eraser associations established by knockout — which is exactly the output this laboratory generates, and which the schema must therefore represent.

```cypher
CREATE NODE TABLE EnzymeAssociation(
  id STRING,
  direction STRING,        -- 'conjugates' | 'deconjugates'
  basis STRING,            -- enum below
  effect_size DOUBLE,      -- site log2FC on perturbation
  adj_p_value DOUBLE,
  confidence STRING,
  rationale STRING,
  asserted_at TIMESTAMP, retracted_at TIMESTAMP,
  PRIMARY KEY (id));

CREATE REL TABLE ASSOCIATION_FOR(FROM EnzymeAssociation TO SiteObservation, MANY_ONE);
CREATE REL TABLE ASSOCIATION_ENZYME(FROM EnzymeAssociation TO Protein, MANY_ONE);
CREATE REL TABLE ASSOCIATION_SUPPORTED_BY(FROM EnzymeAssociation TO Analysis);
CREATE REL TABLE ASSOCIATION_CITES(FROM EnzymeAssociation TO Publication);
```

`basis`: `knockout` · `knockdown` · `catalytic_mutant` · `inhibitor` · `in_vitro_reconstitution` · `literature`.

A site with no association is **unattributed**. It is never assumed to belong to the canonical enzyme for its modifier.

### 6.3 Protein assignment

**Measured, not assumed:** in PXD018299, 1,896 of 2,298 filtered GlyGly sites (82%) map to more than one protein.

Tryptic peptides are frequently shared between isoforms, paralogues and family members, and the search engine reports every protein a peptide could have come from. So "K48 of P20591" often means "K48 of whichever of these proteins this peptide actually came from". This is a third ambiguity sitting beneath modifier identity and enzyme attribution, and at 82% prevalence it is the common case rather than an edge case.

`SITE_ON` is therefore `MANY_MANY`. MaxQuant's `Leading proteins` and `Protein` columns are its own razor-rule inference, not ground truth, and are recorded as such.

```cypher
CREATE NODE TABLE ProteinAssignment(
  id STRING,
  candidate_proteins STRING[],   -- every accession the peptide could derive from
  basis STRING,                  -- enum below
  confidence STRING,
  rationale STRING,
  asserted_at TIMESTAMP, retracted_at TIMESTAMP,
  PRIMARY KEY (id));

CREATE REL TABLE PROTEIN_ASSIGNMENT_FOR(FROM ProteinAssignment TO SiteObservation, MANY_ONE);
CREATE REL TABLE ASSIGNS_PROTEIN(FROM ProteinAssignment TO Protein, MANY_ONE);
```

| `basis` | Meaning | Confidence |
|---|---|---|
| `unambiguous` | Peptide maps to exactly one protein | `confirmed` |
| `unique_peptide` | Distinguishing peptide observed elsewhere in the dataset | `confirmed` |
| `leading` | Search engine's leading-protein subset | `probable` |
| `razor` | Search engine's razor-rule pick | `ambiguous` |
| `reviewed_preferred` | Reviewed Swiss-Prot entry chosen over TrEMBL in the same candidate set | `probable` |
| `orthogonal_evidence` | Isoform-specific knockdown, transcript evidence | `confirmed` |

**Reviewed entries are preferred, and the preference is recorded.** Measured on PXD018299: in 4 of 8 sampled sites the search engine's razor pick was an unreviewed TrEMBL accession while a reviewed Swiss-Prot entry sat in the same candidate set — `A0A087WXQ8` over `P49720`, `H0YKK0` over `P09661`, `J3KTA4` over `P17844`, `F8VNX8` over `O14545`. Half of protein assignments therefore land on entries with no curator annotation when a well-annotated alternative exists. Resolution promotes the reviewed entry and records `basis = 'reviewed_preferred'`; it never does so silently.

**The `SITE_ON` declaration is wider than the key can express.** `SITE_ON` is `MANY_MANY`, so the DDL permits a `ModificationSite` to attach to several `ProteinSequence`s — but its key composes **exactly one** (§4), so a second attachment would have no representation in the id. In practice a site carries one `SITE_ON`, to the sequence it is keyed against, and the multi-mapping is carried by `candidate_proteins` above; that division is what keeps a razor pick from becoming a silent second parent. Recorded rather than resolved: either the key gains a way to name several parents, or the relationship narrows to `MANY_ONE` and multi-mapping stays entirely within `ProteinAssignment`. Settle when the first search-output adapter constructs both (weeks 5–6).

**Consequence for the headline query.** *Which sites are lost on ISG15 knockdown* is answerable per-protein only where assignment is `confirmed`. Elsewhere the honest answer names a candidate set. Existing tools silently adopt the razor pick; reporting the set instead is a differentiator, not a limitation.

### 6.4 Site localisation

`localization_prob` is retained on every `SiteObservation` and is not a modelling problem — but it is a filtering decision that must be recorded rather than silently inherited. Field convention treats ≥ 0.75 as class I. In PXD018299 the median is 1.00 and the minimum 0.35, so a threshold materially changes the set. The threshold applied is recorded on the `Analysis`, never hard-coded.

### 6.5 Imputation

**Measured, not assumed.** In PXD018299, using `Intensity` columns for the KO+IFN vs WT+IFN contrast, a large fraction of the matrix has no detected value. Absence in mass spectrometry is ambiguous: the analyte may be genuinely absent, or present below the detection limit, and the instrument cannot distinguish these.

Field practice — Perseus' default, and therefore the basis of the published figure this dataset supports — replaces missing values with draws from a normal distribution downshifted below the observed mean. That is a **generated number, not a measurement**, and it materially determines the result.

The two quantities available in this dataset diverge by two orders of magnitude in usability:

| Quantity | Testable sites (≥2 replicates both groups) | Notes |
|---|---|---|
| `Ratio mod/base` | 23 of 2,056 | Stoichiometrically correct; requires modified and unmodified peptide co-quantified |
| `Intensity` + imputation | thousands | Confounded by protein abundance; recovers 12 of 14 published targets |

The stoichiometrically correct quantity is unusable for low-stoichiometry modifications. `protein_adjusted = 'native'` remains right where the ratio exists, but must never be the default path.

```cypher
CREATE NODE TABLE Imputation(
  id STRING,
  method STRING,              -- 'downshifted_normal' | 'knn' | 'min_per_sample' | 'none'
  downshift_sd DOUBLE,        -- Perseus default 1.8
  width_sd DOUBLE,            -- Perseus default 0.3
  seed INT64,                 -- REQUIRED where the method is stochastic
  scope STRING,               -- 'whole_matrix' | 'per_sample'
  n_values_imputed INT64,
  n_values_total INT64,
  asserted_at TIMESTAMP, retracted_at TIMESTAMP,
  PRIMARY KEY (id));

CREATE REL TABLE IMPUTATION_FOR(FROM Imputation TO Analysis, MANY_ONE);
```

`SiteObservation` gains `n_imputed INT64` — how many of that site's values were generated rather than measured.

**Known limitation.** `Imputation` attaches to an `Analysis`, so the model assumes one imputation configuration per analysis. Perseus permits different settings for different matrices — a diGly peptidome and its matched proteome may legitimately be imputed differently within what a researcher considers one analysis. The current model forces either two `Analysis` nodes or a single over-generalised parameter set. Acceptable for v0.1, since two `Analysis` nodes is a correct if verbose representation, but it should be revisited if it proves awkward in practice.

A `DifferentialResult` whose underlying values are more than half imputed is flagged **substantially imputed** in every view and export. A seed is mandatory for stochastic methods: without it, the analysis is not reproducible even from the same inputs, which defeats I9.

---

## 7. Provenance

Provenance is a PROV-O mapping, not a log.

| bzk type | PROV-O class |
|---|---|
| `Analysis` | `prov:Activity` |
| `Dataset`, `SiteObservation`, `DifferentialResult`, `Figure` | `prov:Entity` |
| `Person`, `Software` | `prov:Agent` |

```cypher
CREATE REL TABLE WAS_GENERATED_BY(FROM DifferentialResult TO Analysis, MANY_ONE);
CREATE REL TABLE USED(FROM Analysis TO Dataset);
CREATE REL TABLE WAS_ASSOCIATED_WITH(FROM Analysis TO Person, MANY_ONE);
CREATE REL TABLE WAS_EXECUTED_BY(FROM Analysis TO Software, MANY_ONE);
CREATE REL TABLE WAS_DERIVED_FROM(FROM DifferentialResult TO SiteObservation);
```

An entity with no path to a `prov:Activity` is flagged `unprovenanced` at query time. It is never hidden and never silently trusted.

---

## 8. Invariants

Normative. Violations are ingestion errors, not warnings.

- **I1 — Disjointness.** No edge may connect two reference nodes with locally-authored semantics. Reference-to-reference edges carry a `source` field naming the external authority.
- **I2 — Sequence pinning.** Every `ProteinSequence` carries the `sequence_version` it names and the `sequence` itself; a `Protein` carries neither, because a protein's identity outlives any one version of its sequence. Every `ModificationSite` key embeds that version, and an isoform is keyed against its own accession (`P09914-2`), never the canonical one. A site's `SITE_ON` target is a `ProteinSequence`, not a `Protein`: a site whose target lacks a sequence version cannot be created, and the version embedded in the site key must equal that target's `sequence_version` — otherwise the position asserts against one sequence while attaching to another. A `ProteinSequence`'s own id must likewise agree with what it declares: the `sv` segment of `uniprot:{accession}#sv{n}` must equal its `sequence_version`, and the accession segment must equal the `Protein` it is reached from by `HAS_SEQUENCE`. Guarding the site key against its target while the target's id and column may disagree leaves the same duplication one level down — a key and a field are two homes for one fact. Residue numbering without a fully specified sequence is meaningless: measured on PXD018299, isoform positions resolved against canonical sequences return the wrong residue, and 5% of sequences were amended after the original search.
- **I3 — No bare modifier claims.** No `SiteObservation` may assert a modifier except through a `ModifierAssignment`. No UI or export may render a K-GG site as "ubiquitination" unless a live assignment has `confidence != 'ambiguous'`.
- **I4 — Declared adjustment.** Every `DifferentialResult` on a site sets `protein_adjusted` to one of three states. `applied` requires an `ADJUSTED_BY` edge. `native` means the source quantity is already ratiometric — MaxQuant `Ratio mod/base` divides modified-peptide intensity by unmodified protein signal, so stoichiometry is measured rather than inferred; `adjustment_method` records which. `not_applied` is labelled *stoichiometry-uncorrected* in every view and export. Most DIA outputs, including DIA-NN, provide no native ratio.
- **I5 — Provenance reachability.** Every entity node reaches at least one `Analysis`, or is flagged `unprovenanced`.
- **I6 — Append-only assertions.** `ModifierAssignment` and `DifferentialResult` nodes are immutable. Revision creates a new node and sets `retracted_at` on the old. Retraction propagates to every downstream figure and report.
- **I7 — Deterministic reference keys.** Reference node IDs are derived from their content, so identical entities from different sources converge on one node without a merge step.
- **I8 — Curated design.** Every `Sample` reaches an `Analysis` with `kind = 'curation'` via `SAMPLE_GENERATED_BY`. Any result derived from a curation with `confidence = 'inferred'` is labelled as such in every view and export, naming the `basis`. Experimental design inferred from filenames is never presented as though it came from the submitters.
- **I9 — Reproducible rebuild.** The graph is a derived artifact, never authoritative. Given `raw/` (content-addressed), the curation export, and this DDL, the entire graph must be regenerable from scratch. Curation records and manual inferences are the only non-derivable content; they serialise to a plain JSON export alongside the graph and are versioned independently. This is what converts schema change from a migration problem into a compute-time problem — see §10.
- **I10 — Unattributed enzymes.** No `SiteObservation` may be presented as the product of a named enzyme except through a live `EnzymeAssociation`. A site whose modifier is assigned but whose enzyme is not is displayed as *unattributed*, never as the canonical writer or eraser for that modifier.
- **I11 — Quantitative retention.** Every observation persists its per-sample quantitative values in the columnar store, not merely the statistics derived from them. No pipeline stage may discard the matrix after computing a `DifferentialResult`. This is what makes the statistical layer genuinely pluggable: any test — moderated *t*, permutation with s0, or something not yet written — is recomputable from stored values without re-ingestion. A platform retaining only log₂FC and adjusted *p* is married to whichever test produced them.
- **I12 — No tryptic assumptions.** Core code makes no assumption that peptides terminate in K or R, that a peptide carries at most one modification, or that a peptide maps to exactly one protein. Immunopeptidomics violates the first, multi-modified peptides the second, shared peptides the third. These are free to accommodate now and expensive to retrofit.
- **I13 — Pipeline metadata is data.** `acquisition_mode`, `search_engine`, `library_type` and `test` are recorded fields, never branch conditions. Any conditional on their value outside `adapters/` or the statistics registry is a defect — it is how the abstraction leaks and how the next pipeline change becomes a rewrite.
- **I14 — No false singletons.** A `SiteObservation` whose peptide maps to several proteins is never rendered against one protein without a `ProteinAssignment` of confidence `confirmed`. Where assignment is `razor` or `leading`, views and exports name the candidate set. Measured prevalence in PXD018299 is 82%, so this is the default path, not an exception.
- **I15 — Imputation is declared.** Every `Analysis` producing differential results links to an `Imputation`, including `method = 'none'`. Stochastic methods record a seed; without one the analysis is irreproducible from its own inputs and I9 fails. Results whose underlying values are more than half generated are labelled *substantially imputed* wherever they appear.
- **I17 — Reviewed preferred, never silently.** Where a candidate protein set contains both reviewed (Swiss-Prot) and unreviewed (TrEMBL) entries, resolution promotes the reviewed entry and records `ProteinAssignment.basis = 'reviewed_preferred'`. Measured on PXD018299, the search engine's razor pick was unreviewed in 4 of 8 sampled sites despite a reviewed alternative being present. The promotion is an inference and is recorded as one.
- **I18 — Embargo is enforced at the boundary.** No `Dataset` with `source = 'embargoed'` and `embargo_released_at IS NULL` may contribute to any export, report, figure file or shared artifact. Queries and views within the local instance are unrestricted. The check sits at the export boundary, not at query time, so the data remains fully usable to its holder while being incapable of leaking.
- **I19 — Observed and reported provenance are distinguished.** Every `Analysis` sets `parameters_observed`. Where `false`, the analysis was run outside the platform and its parameters are as stated by the user rather than as executed; every derived `DifferentialResult` is labelled accordingly in views and exports. An externally computed result is never presented with the same provenance standing as one the platform produced.
- **I16 — Quantity and test are declared.** Every `Analysis` records which quantity it consumed and the filters applied, including the localisation threshold, and — where it runs one — the statistical `test` and its `fdr_method`, with test-specific parameters (`s0`, randomisation count) in `parameters_json`. These live on the `Analysis`, not the `DifferentialResult`: every result of an analysis shares them, and `ARCHITECTURE.md` §4 already records the test's parameters there per this invariant. (The DDL previously placed `test` / `fdr_method` on `DifferentialResult`, contradicting §4; the §3 identity table surfaced the pre-existing discrepancy, resolved here — ONTOLOGY v1.6, ADR-0020.) Two defensible quantities on the same dataset differed by a factor of ~90 in usable sites; neither choice is recoverable from a published methods section, and that gap is what this platform exists to close. The declared quantity is drawn from the **closed enum in §5** and must name the *specific* quantity, not just its family: a MaxQuant modification-site source uses `intensity_multiplicity_summed`, and bare `intensity` — legal only where there is no multiplicity axis (protein- or precursor-level) — is invalid there. A value that hid the multiplicity treatment would be the same invisible-choice defect as `intensity` vs `ratio_mod_base`. Because quantity is an identifying field (§3, ADR-0020), two spellings of one quantity would mint two `Analysis` ids for one fact; the closed enum forecloses that. The 12-of-14 baseline was computed on multiplicity-summed intensity (ROADMAP § Deposit and supplementary survey).

---

## 9. Worked example

*Reference identifiers are real; the `bzk:` evidence ids are illustrative stubs standing in for the content-derived digests defined in §3; quantitative values and the site position are illustrative, not measured.*

```
Reference
  Gene           hgnc:5699  (MX1)
  Protein        uniprot:P20591                      (stable; no sequence)
  ProteinSequence uniprot:P20591#sv3, sequence_version 3
                              <-[HAS_SEQUENCE]- uniprot:P20591
  ModificationSite  uniprot:P20591#sv3#K48#unimod:121
                              -[SITE_ON]-> uniprot:P20591#sv3
  Modifier       uniprot:P0CG48 (ubiquitin,  leaves_gg_remnant true)
                 uniprot:Q15843 (NEDD8,      leaves_gg_remnant true)
                 uniprot:P05161 (ISG15,      leaves_gg_remnant true)
                 uniprot:O15205 (FAT10,      leaves_gg_remnant true)

Evidence
  Project        bzk:3a5f0e…  "ISGylation in colorectal carcinoma"
  Experiment     bzk:b1c2d3…  modality digly_proteomics
  Sample         bzk:c4e7a9…  HCT116, IFN-β 1000 U/mL, 8 h, biological rep 1
  Dataset        bzk:d8021f…  source local, search_engine fragpipe 21.1,
                              fasta_release 2026_02, content_hash sha256:9f3c…
  SiteObservation bzk:e6b44c… peptide LLQFIDK(gg)ELVR, localization_prob 0.98
                              -[MEASURED_AT]-> uniprot:P20591#sv3#K48#unimod:121

  ModifierAssignment bzk:f019a7…
      candidate_modifiers [P0CG48, Q15843, P05161, O15205]
      basis inferred_default   confidence ambiguous
      asserted_at 2026-08-01   retracted_at NULL

  ── after the UBA7 knockout arm is ingested ──

  ModifierAssignment bzk:f019a7…  retracted_at 2026-08-14
  ModifierAssignment bzk:a72d10…
      candidate_modifiers [P05161]
      basis uba7_knockout      confidence confirmed
      rationale "site absent in UBA7-/- across 3/3 replicates, adj.p 2.1e-4"
      -[ASSIGNS]-> uniprot:P05161
      -[ASSIGNMENT_SUPPORTED_BY]-> Analysis bzk:39c8bb…

  DifferentialResult bzk:2100ae…
      log2fc 3.4, p 1.2e-5, adj_p 8.0e-4
      protein_adjusted "applied", adjustment_method "residual_vs_protein_lfc"
      -[ADJUSTED_BY]-> DifferentialResult bzk:7cf3d2…  (MX1 protein level)
      -[WAS_GENERATED_BY]-> Analysis bzk:1e90fa…  (test moderated_t_ebayes, fdr_method BH)
```

Before the knockout arm exists, the platform reports a diGly site with an ambiguous modifier. It does not report an ISGylation site. That distinction is the product.

---

## 10. Extension pattern

### What is domain-neutral

The reference/evidence split, PROV-O provenance, immutable append-only assertions, deterministic content-derived keys, curation-as-activity, the `Observation` and `EvidencedInference` contracts, and I9. None of this mentions biology. It is a general pattern for evidence with contested interpretation, from instruments the user does not control, that must survive method change.

### What is domain-specific

Three things, and they are the reason the schema is good enough to generalise rather than accidents of it:

1. `ModificationSite` keyed on sequence version — only meaningful for sequence-indexed PTMs.
2. `ModifierAssignment` — exists because four UBLs leave an indistinguishable tryptic remnant.
3. Protein-level stoichiometry adjustment — specific to PTM-versus-abundance confounding.

### Cost of extension

| Change | Cost |
|---|---|
| New search engine, new statistical test | Hours — adapter or registry entry |
| New `basis` value, new CURIE prefix | Minutes |
| New `Observation` subtype (e.g. `EnrichmentObservation`) | Days — purely additive |
| New `EvidencedInference` subtype | Days — enum plus target node |
| New reference authority (LIPID MAPS, Ensembl) | ~2 weeks — new resolver module |
| Change to a primary key composition | Afternoon **if I9 holds**; weeks otherwise |
| Abandoning the two-graph split or immutability | Months — these are the architectural bets |

Phosphoproteomics is nearly free: same `ModificationSite`, different Unimod term, and the localisation-ambiguity problem is structurally identical to modifier ambiguity. Single-cell and spatial are not — they add dimensions (cell, coordinate) the schema does not have, and need real design work rather than a plugin.

### The rule

Domain logic lives in subtypes, never in code that consumes a contract. Any function operating on the five `Observation` contract fields must work for every modality without modification. A `if isinstance(obs, SiteObservation)` branch outside the subtype module is a defect.

---

## 11. Open questions

1. **`Contrast` sits awkwardly across the reference/evidence boundary.** It is currently an evidence node, since it encodes a local design decision. But it is reused: if two datasets both define *IFN-β 8h vs mock*, they share one `Contrast` node. That makes it reference-like in behaviour while evidence-like in origin, which is the one thing §1 says should not happen.

   Concretely, if the curation for one dataset's sample mapping is retracted, every `DifferentialResult` linked through `RESULT_IN_CONTRAST` is correctly retracted — but the `Contrast` node survives, now partly orphaned. This works, and it is a design smell.

   Two candidate resolutions: make `Contrast` strictly per-dataset and accept duplication, which restores the disjointness at the cost of losing cross-dataset contrast matching; or promote it to a reference node with a deterministic key derived from its condition terms, which requires those terms to resolve to an external vocabulary they currently do not. Neither is obviously right. To settle before v0.2.

   **Now a demonstrated collision, not only a smell (2026-08-07 audit).** `Contrast` identity is `numerator` + `denominator` with **no anchor at all**, so any experimental context not spelled into those two strings is invisible to the id. The curation records show the real string forms — `'USP18-/- + IFN'` vs `'WT + IFN'` — which encode genotype and treatment but **not cell line or organism**. A HAP1 contrast and an HCT116 contrast therefore receive one id, and `RESULT_IN_CONTRAST` can no longer separate the two experiments' `DifferentialResult`s. Unlike a duplicated `Project.title`, this fires on *correct* usage: condition shorthand naturally repeats across cell lines in this laboratory, and cross-dataset reuse is the intended behaviour. Both candidate resolutions above would fix it; the collision raises the priority, not the difficulty.
2. Are transcript-level nodes needed in v0.1, or does RNA-seq enter at v0.2 with `TranscriptObservation` mirroring `ProteinObservation`?
3. Should historical UniProt sequence retrieval be supported, or only current? Measured: 1 of 20 sampled sequences was amended after the original search, implying roughly 5% of sites are at risk of silent position drift. Current-only resolution flags these; historical retrieval would let them be reconciled.
4. Multi-modified peptides: a peptide bearing two K-GG sites currently yields two `SiteObservation` nodes sharing a `peptide_sequence`. Is a `PeptidoformObservation` parent needed to preserve co-occurrence? **Same question from the identity side (§3):** `SiteObservation` identity is `peptide_sequence` + `Dataset` + `ModificationSite`, with no peptidoform state, so two observations of the same site differing in a *second* modification elsewhere would collide. The MaxQuant GlyGly **site** table cannot produce that pair — it has no `Modifications` / `Modified sequence` column and aggregates across other-modification peptidoforms; its only modification axis is same-type GlyGly multiplicity (`Intensity___1/2/3`, verified against the PXD018299 header). The collision becomes reachable only from a **peptidoform-grain adapter** — MaxQuant `evidence.txt`, or DIA-NN modified precursors (assumptions A1/A2). Resolve both together — a peptidoform key in `SiteObservation` identity and the `PeptidoformObservation` parent — when the first such adapter lands; do not amend the identity before then, since a permanently-null field is dead weight.
5. **Does an isoform's `sequence_version`, inherited from the parent entry's `entryAudit` (§4), track edits confined to the isoform?** An isoform is the canonical sequence with its splice-variant (VSP / `VAR_SEQ`) features applied. If UniProt amends only those isoform-defining features — changing the isoform's spliced sequence while leaving the canonical sequence untouched — it is unconfirmed whether `entryAudit.sequenceVersion` bumps. If it does not, an isoform key such as `P09914-2#sv2` could silently denote two different sequences over time: drift specific to isoforms, invisible to the version number. **Mitigation:** `rebuild.py` refetches each resolved sequence and compares it to the stored `ProteinSequence.sequence`, so drift is caught by content, independent of the version number. To confirm: UniProt's versioning behaviour for isoform-only edits, and whether the rebuild comparison suffices or historical isoform retrieval (cf. Q3) becomes necessary.
6. **Is the UniProt cache an I9 input, and if so what makes it reconstructible?** I9 states the graph is regenerable from `raw/` (content-addressed), the curation export, and this DDL. `ProteinSequence.sequence` is derivable from none of the three: sequences come from UniProt, which is mutable, and a superseded `sv` may not be refetchable at all once amended — so a rebuild that reaches the network cannot be relied on to reproduce the sequence a site was pinned to. In practice `rebuild.py` already treats `~/.bzk-omics/cache/uniprot/` as an **input** — it is explicitly not dropped — and `OPERATIONS.md` §3 retains every entry referenced by a live `ModificationSite` for exactly this reason. But I9's own list does not name the cache, so the arrangement works while being unstated. Either I9 gains a fourth input and the cache acquires a reconstruction story (it is today a local directory: not content-addressed like `raw/`, not version-controlled like the curation export, and named in `OPERATIONS.md` §1 as *regenerable, low backup priority* — which is the opposite of what an I9 input must be), or sequence content must come from somewhere already in the list. Recorded 2026-08-07 alongside ADR-0005, which does not resolve it: the split makes the pinned sequence *addressable*, not *reconstructible*.
7. **Should every `DifferentialResult` be required to attach to exactly one of `RESULT_FOR_SITE` or `RESULT_FOR_PROTEIN`?** A result measures either a site or a protein — never both, never neither — so an exactly-one (XOR) structural check would express that, and it is the check that would have caught the protein-level `bzk:dr2` in the valid fixture attaching to nothing it measures. Not minted as an invariant: the grain a `DifferentialResult` carries is only fixed once `perseus.py` emits results at both grains (site and protein), so the cardinality should be decided when the adapter lands rather than pre-committed here. Surfaced 2026-08-07 with `RESULT_FOR_PROTEIN` (v1.3).

   **A second cardinality question sits with it: `ADJUSTED_BY` is not an anchor.** For an `applied` result it names the protein-level result used as the correction baseline, but it is absent from §3's anchor list, so two corrected results differing *only* in which baseline they used share an id. This is reachable under a faithful implementation rather than a contrived one: at I14's measured 82% multi-mapping, an honest correction of an ambiguous site is computed against *each* candidate parent, and `ADJUSTED_BY` is `MANY_ONE`, so each such correction needs its own `DifferentialResult`. Decide with the XOR question above, when `perseus.py` emits protein-adjusted results.
8. **Two identity verdicts left `uncertain` by the 2026-08-07 audit, both pending the adapter that would settle them.** `ProteinObservation` identity is `Dataset` + `Protein` with no identifying field at all; it collides if a `proteinGroups` adapter ever emits two group-level quantifications in one dataset that resolve to the same `Protein` — a shared protein appearing in two groups, or two groups collapsing onto one accession because grouping is not isoform-aware while `Protein` identity is. There is no `ProteinAssignment` fallback at protein grain to separate them. `Imputation` identity is its config plus its `Analysis` anchor; two matrices imputed with identical settings under **one** `Analysis` (a diGly peptidome and its matched proteome) would collide, since `scope` names granularity and not which matrix. §6.5 prescribes two `Analysis` nodes for that case, which avoids it — so the verdict is safe-by-convention, not safe-by-construction. Both settle with the adapters (weeks 3–6).

9. **Is §6's evidence-edge clause right, or does `ProteinAssignment` need an edge?** The `EvidencedInference` contract (§6) states every subtype MUST carry an evidence edge to an `Analysis` or a `Publication`. `ModifierAssignment` has `ASSIGNMENT_SUPPORTED_BY` / `ASSIGNMENT_CITES` and `EnzymeAssociation` has `ASSOCIATION_SUPPORTED_BY` / `ASSOCIATION_CITES`; **`ProteinAssignment` has neither** — its only edges are `PROTEIN_ASSIGNMENT_FOR` and `ASSIGNS_PROTEIN`. So the DDL contradicts its own stated supertype contract, and nothing catches it because the contract is unenforced (`HANDOFF.md` §8, CS class). Two readings, and the documents do not choose. Either the clause is too strong — a protein assignment's bases (`unambiguous`, `unique_peptide`, `leading`, `razor`, `reviewed_preferred`) are **intrinsic to the search output** rather than cited from a separate analysis, so requiring a citation would force a hollow one — or the assignment genuinely has provenance worth naming and the schema is missing the edge, which would leave every razor pick unattributable to the run that made it. Note the first reading does not cover `orthogonal_evidence`, whose whole point is external support. Settle before writing the contract check, and before the MaxQuant adapter constructs `ProteinAssignment`s at scale (weeks 5–6). Surfaced by the 2026-08-07 audit.

10. **Does a preprint and its published version share one `Publication`, or two?** `Publication` is authority-assigned (§4), so a work cited by preprint DOI and later by its published DOI or PMID receives **two ids**, and citations fragment across that boundary — a `ModifierAssignment` citing the preprint and another citing the paper would not converge, and `ASSIGNMENT_CITES` could not show they rest on the same evidence. This is the same late-arriving-identifier shape ADR-0021 settled for `Person` and `Software`, but it does **not** resolve the same way: there, one entity had two possible keys; here it is genuinely arguable that a preprint and a peer-reviewed paper are *different artifacts* with different content and different standing, in which case two nodes are correct and the fragmentation is the model working. The judgement turns on what a citation is for — if it anchors an assertion's evidence, the version matters; if it names a work, it does not. Worth deciding explicitly rather than by default, and cheap while `Publication` carries almost no data. Recorded 2026-08-07 with ADR-0021, which deliberately left it open.

**Resolved**

- ~~Q4: How are PRIDE datasets without SDRF handled?~~ Settled 2026-08-06 in favour of curation-as-activity. See §5.3 and invariant I8. Rationale: the configuration alternative violates I5. To be recorded as ADR-0009.
