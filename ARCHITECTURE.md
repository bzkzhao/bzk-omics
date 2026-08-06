# ARCHITECTURE.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 0.5 |
| Last reviewed | 2026-08-06 |
| Depends on | `ONTOLOGY.md`, `VISION.md` |
| Authoritative for | Language and library choices, storage layout, module boundaries |

This document is expected to change weekly during v0.1. Decisions recorded here that survive scrutiny should be promoted to numbered ADRs in `decisions/`.

---

## 1. Stack

| Layer | Choice | Rationale |
|---|---|---|
| Language | Python 3.12 | The proteomics ecosystem is Python. `pyteomics`, `pyopenms`, UniProt clients, `polars` all exist and are tested. Reimplementing them elsewhere is a category error. |
| Package management | `uv` | Fast, lockfile-based, single-binary. Supports the one-afternoon install promise. |
| API | FastAPI | Typed, async, generates OpenAPI for the front end for free. |
| Graph store | Kùzu | Embedded, Cypher, columnar, MIT-licensed, no server process. Neo4j requires operational overhead a laptop-local product cannot justify. |
| Columnar store | DuckDB | Embedded, fast aggregation over site × sample matrices, reads Parquet directly. |
| DataFrames | Polars | Lazy evaluation and predictable memory on wide quantitative tables. |
| Statistics | Pluggable registry over NumPy / SciPy | See §4. |
| Front end | SvelteKit + TypeScript, served on localhost | No desktop packaging in v0.1. |
| Charts | Observable Plot or D3 | Volcano, UpSet, site-level heatmaps. |

**Deferred:** Tauri desktop packaging (v0.2), local LLM serving via Ollama or vLLM (v0.3), any cloud component.

---

## 2. Storage layout

The boundary is defined normatively in `ONTOLOGY.md` §2. Concretely:

```
~/.bzk-omics/
  graph.kuzu/            # identity, relationships, provenance
  quant.duckdb           # site × sample and protein × sample matrices
  raw/                   # ingested source files, content-addressed by SHA-256
  cache/uniprot/         # sequence + version cache, keyed by accession#sv
```

`SiteObservation.quant_ref` is the join key into `quant.duckdb`. Nothing per-sample enters the graph.

The UniProt cache is not optional. Site position validation requires the exact sequence for the exact version, and a laptop-local product cannot depend on network availability at query time. Cache entries are immutable — a new sequence version is a new entry, never an overwrite.

---

## 3. Modules

```
bzk/
  ontology/      # schema DDL, node/edge dataclasses, invariant checks
  adapters/      # ingestion; one module per search engine
    maxquant.py
    fragpipe.py
    diann.py
    base.py      # the adapter contract
  resolve/       # UniProt resolution, sequence-version pinning, position validation
  quant/         # DuckDB layer, normalisation
  stats/         # moderated t-test, BH, protein-level adjustment
  provenance/    # PROV-O mapping, content hashing
  api/           # FastAPI routes
web/             # SvelteKit
```

### The adapter contract

**Priority order is DIA-NN first.** The Pinto-Fernández group moved to DIA in 2022 (ABPP-HT*) and its 2025 work uses DIA-NN 2.0 with FASTA-predicted libraries on an Orbitrap Fusion Lumos. MaxQuant is archival — required for PXD018299 and other pre-2022 deposits, not for incoming data.

| Adapter | Priority | Rationale |
|---|---|---|
| DIA-NN | 1 | Current lab pipeline; incoming data |
| MaxQuant | 2 | Archival public datasets (PXD018299) |
| Spectronaut | 3 | Dominant commercial DIA tool in core facilities |
| FragPipe | 4 | Common alternative |

Every adapter maps a search engine's output to `Observation` nodes plus a quantitative frame. Because v0.1 must treat local and PRIDE-downloaded datasets identically, the adapter takes a file and a separate sample-mapping, never a directory convention.

```python
class ObservationAdapter(Protocol):
    name: str                       # 'diann' | 'maxquant' | 'fragpipe' | 'spectronaut'
    def sniff(self, path: Path) -> bool: ...
    def parse(self, path: Path, mapping: SampleMapping) -> ParsedObservations: ...
```

The signature takes a file and a mapping — never a directory convention. Search engines differ more in output layout than in output content, so sniffing the file is stable where assuming a folder shape is not.

`ParsedObservations` satisfies the `Observation` contract (`ONTOLOGY.md` §5.1) and makes no tryptic assumptions (I12): peptides need not end in K or R, may carry several modifications, and may map to more than one protein.

**Adapter responsibilities beyond parsing.** Measured against PXD018299: drop `Reverse` and `Potential contaminant` rows before anything else; normalise sample names (one replicate carries an instrument run ID); convert PRIDE `ftp://` locations to `https://ftp.pride.ebi.ac.uk`; record rather than apply the localisation threshold; emit the full candidate protein set, never the razor pick alone.

**Identifier translation is first-class.** Gene symbol, UniProt accession and protein description are three namespaces for one entity, and search output carries all three inconsistently (`Gene names`, `Proteins`, `Protein names`, all semicolon-separated). Without translation the user cannot ask a question in the vocabulary they think in — a query for "ADAR" must reach a row keyed on `P55265`. Resolution prefers reviewed Swiss-Prot entries over TrEMBL where both appear in a candidate set, recorded as `ProteinAssignment` basis rather than applied silently.

**No branching on pipeline metadata** (I13). `acquisition_mode`, `search_engine` and `library_type` are recorded fields. A conditional on their value anywhere outside `adapters/` means the abstraction has leaked and the next pipeline change becomes a rewrite rather than a new module.

`SampleMapping` is supplied by SDRF where present and by manual curation where not. Per `ONTOLOGY.md` §5.2, the adapter does not consume a configuration file: it consumes a `SampleMapping` that has already been written to the graph as an `Analysis` node with `kind = 'curation'`, and returns `Sample` nodes bearing `SAMPLE_GENERATED_BY` edges to it.

Practically this means the mapping UI is a write path into the graph, not a form that produces YAML. A corrected mapping creates a new curation node and retracts the old under I6; it never edits in place. The `basis` and `confidence` recorded there propagate to every derived result, which is what invariant I8 enforces at export.

---

## 4. Statistics

### Pluggable by construction

**No statistical test is privileged by the schema.** `DifferentialResult.test` is a recorded string that nothing downstream branches on. Tests register against a common interface and are selected per analysis.

This is not abstraction for its own sake. The 2020 USP18 study used Perseus with permutation FDR and s0; the 2025 TNBC study reports neither. A platform that hard-codes one test is obsolete within three years — the same failure mode as hard-coding a search engine.

**Superseded:** an earlier revision recommended implementing the Perseus permutation-FDR-with-s0 test to reproduce published cutoffs. That was based on 2020 methods and appears obsolete. Do not build it as the primary path. See ADR-0007 (superseded by ADR-0011).

### Imputation is part of the statistics layer, not the adapter

Measured on PXD018299: `Ratio mod/base` yields 23 testable sites; `Intensity` with Perseus-style imputation yields thousands and recovers 12 of 14 published targets. Imputation is therefore not a convenience — it determines whether the analysis works at all.

It is registered like a test, with recorded parameters (`method`, `downshift_sd`, `width_sd`, `seed`) per I15. Default entry: `downshifted_normal` at 1.8 SD downshift, 0.3 SD width, matching Perseus, so published analyses can be reproduced. A seed is mandatory — without it the same inputs give different answers and I9 fails.

Imputation never happens in the adapter. Adapters emit measured values and nulls; what to do about the nulls is an analysis decision that must be recorded.

### v0.1 registry contents

| Test | Use |
|---|---|
| `moderated_t_ebayes` | Default. Empirical Bayes variance shrinkage (Smyth 2004), ~200 lines, no R dependency |
| `welch_t` | Fallback and sanity check |
| `permutation_s0` | Optional, for reproducing legacy Perseus-analysed results |

FDR control (BH, permutation) is a separate pluggable step recorded in `fdr_method`.

### Protein-level adjustment

Site-level diGly quantification is confounded by parent protein abundance: a site appears regulated when its protein is regulated, independent of modification stoichiometry. Where a matched proteome dataset exists for the same samples, the site log₂FC is corrected against the protein log₂FC, `protein_adjusted` is set true, and an `ADJUSTED_BY` edge records which result was used. Where it does not, the result is labelled *stoichiometry-uncorrected* in every view and export.

PXD018299 carries a matched proteome generated by splitting 20 µg of digest before the GlyGly immunoprecipitation, so the pairing is available by construction. Getting this right matters more than any feature.

## 5. Seed ADRs

To be written as numbered, immutable records in `decisions/`:

- `0001` Two-graph model: reference and evidence disjoint
- `0002` Python over TypeScript for the backend
- `0003` Kùzu over Neo4j for the graph store
- `0004` Split storage: graph identity in Kùzu, quantitative matrices in DuckDB
- `0005` Sequence version as part of the `ModificationSite` primary key
- `0006` Modifier identity as a defeasible assignment, not a site property
- `0007` Local moderated *t*-test over an R dependency
- `0008` Append-only assertions with explicit retraction
- `0009` Sample-to-condition mapping as a curation activity, not configuration
- `0010` `Observation` and `EvidencedInference` as contracts, not tables
- `0011` Statistical tests pluggable; supersedes `0007`
- `0012` Graph is derived, not authoritative; rebuild over migration (I9)
- `0013` Quantitative matrices retained permanently, never only derived statistics (I11)
- `0014` Adapter order under pipeline uncertainty: DIA-NN, MaxQuant, FragPipe

---

## Open questions

1. Does the UniProt cache need historical sequence versions, or only those encountered? Historical retrieval is possible but slow; encountering a superseded version during ingestion of an old public dataset is likely.
2. Where does normalisation live — in `quant/` as a storage-time transform, or in `stats/` as an analysis-time one? Storage-time is faster; analysis-time is more auditable and better matches the provenance model.
3. Does the front end query the graph directly through a read-only endpoint, or only through typed API routes? The former is faster to build; the latter keeps invariants enforceable in one place.
4. Where does the curation export live relative to the graph, and what triggers a re-export? I9 requires it to survive a rebuild, so it cannot live only inside `graph.kuzu/`.
