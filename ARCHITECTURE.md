# ARCHITECTURE.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 0.8 |
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

Isoform accessions are cached under their full form (`P09914-2`), never collapsed to canonical. Fetching `rest.uniprot.org/uniprotkb/P09914-2.fasta` returns the isoform sequence; stripping the suffix returns a different protein of different length, and positions resolved against it are wrong without erroring.

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

Two classes of adapter, because the platform sits downstream of both search engines and analysis tools.

**Analysis-output adapters** — ingest results computed elsewhere. `Analysis.kind = 'external'`, `parameters_observed = false` (I19).

| Adapter | Priority | Rationale |
|---|---|---|
| Perseus result table | 1 | The collaborating group's workflow, confirmed by correspondence. The shortest path to holding a real user's real results |

**Search-output adapters** — ingest raw quantification, retaining the matrix (I11) so results are recomputable.

| Adapter | Priority | Rationale |
|---|---|---|
| MaxQuant | 2 | PXD018299 and the archival deposits; the validated regression fixture |
| DIA-NN | 3 | Current instrument-side pipeline; incoming data |
| Spectronaut | 4 | Dominant commercial DIA tool in core facilities |
| FragPipe | 5 | Common alternative |

The Perseus adapter moved to first priority after the collaborator confirmed his workflow. It is also the smallest: a result table is a flat file of proteins, differences and significance values, with no localisation or razor-pick complexity.

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

`SampleMapping` is supplied by SDRF where present and by manual curation where not. Per `ONTOLOGY.md` §5.3, the adapter does not consume a configuration file: it consumes a `SampleMapping` that has already been written to the graph as an `Analysis` node with `kind = 'curation'`, and returns `Sample` nodes bearing `SAMPLE_GENERATED_BY` edges to it.

Practically this means the mapping UI is a write path into the graph, not a form that produces YAML. A corrected mapping creates a new curation node and retracts the old under I6; it never edits in place. The `basis` and `confidence` recorded there propagate to every derived result, which is what invariant I8 enforces at export.

---

## 4. Statistics

### Pluggable by construction

**No statistical test is privileged by the schema.** `DifferentialResult.test` is a recorded string that nothing downstream branches on. Tests register against a common interface and are selected per analysis.

This is not abstraction for its own sake — but the case for it was nearly made on a false premise, which is instructive.

**Correction, 2026-08-06.** An earlier revision inferred from the 2025 TNBC preprint's silence on proteomic statistics that the group had moved away from Perseus, and advised against building the Perseus-compatible test as the primary path. **That inference was wrong.** Confirmed by author correspondence: the group's workflow remains Perseus — log₂ transformation, missing-value filtering, imputation from a normal distribution, and a dedicated two-sample test, with volcano plots built on the difference in log intensities.

Absence of a stated method in a publication is not evidence of a changed method. The registry architecture stands on its own merits; only the choice of default entry was wrong. See ADR-0015, which supersedes ADR-0011.

### Imputation is part of the statistics layer, not the adapter

Measured on PXD018299: `Ratio mod/base` yields 23 testable sites; `Intensity` with Perseus-style imputation yields thousands and recovers 12 of 14 published targets. Imputation is therefore not a convenience — it determines whether the analysis works at all.

It is registered like a test, with recorded parameters (`method`, `downshift_sd`, `width_sd`, `seed`) per I15. Default entry: `downshifted_normal` at 1.8 SD downshift, 0.3 SD width, matching Perseus, so published analyses can be reproduced. A seed is mandatory — without it the same inputs give different answers and I9 fails.

Imputation never happens in the adapter. Adapters emit measured values and nulls; what to do about the nulls is an analysis decision that must be recorded.

### The registry's role changed

With the platform positioned downstream, the statistics registry is no longer the point. Its purposes are now recomputation — running an alternative test over a retained matrix — and comparison, showing where a recomputed result diverges from an externally computed one. That divergence is a finding about analytical sensitivity, not a defect, and reporting it is something no existing tool does.

`perseus_s0` remains default and required, because matching the collaborator's numbers is a precondition for being trusted with the comparison.

### v0.1 registry contents

| Test | Status | Use |
|---|---|---|
| `perseus_s0` | **Default and required** | SAM-style modified *t*-test with fold-change curvature parameter `s0` and permutation-based FDR. The collaborating group's workflow; required to reproduce their published and internal results |
| `moderated_t_ebayes` | Secondary | Empirical Bayes variance shrinkage (Smyth 2004). Better calibrated at *n* = 3 than a plain *t*-test; retained for comparison |
| `welch_t` | Sanity check | Plain two-sample test; useful for detecting when the choice of test is load-bearing |

`perseus_s0` is not the same test as `welch_t` with Benjamini–Hochberg. The `s0` parameter introduces a fold-change dependence into the significance threshold, producing the characteristic curved boundary on a Perseus volcano rather than straight cutoffs on both axes. A reproduction that ignores this will not match the group's numbers even when it recovers the same proteins.

Required parameters, recorded on the `Analysis` per I16: `s0`, `fdr`, and the number of randomisations.

**To confirm with the collaborator:** the exact `s0` and FDR values used, and whether "difference in intensities" denotes the difference of log₂ values (which is the log fold change) or an untransformed difference.

FDR control (BH, permutation) is a separate pluggable step recorded in `fdr_method`. Perseus uses permutation-based FDR, not BH.

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
- `0015` Perseus `s0` test as the default statistical entry; supersedes `0011`
- `0016` Embargoed dataset state for unpublished collaborator data

---

## Open questions

1. Does the UniProt cache need historical sequence versions, or only current? Measured: 1 of 20 sampled PXD018299 sequences was amended after the search, so roughly 5% of sites are at risk of drift. Current-only resolution flags them; historical retrieval would reconcile them. Flagging is cheaper and satisfies I2 — resolve in favour of flagging unless the rate rises.
2. Where does normalisation live — in `quant/` as a storage-time transform, or in `stats/` as an analysis-time one? Storage-time is faster; analysis-time is more auditable and better matches the provenance model.
3. Does the front end query the graph directly through a read-only endpoint, or only through typed API routes? The former is faster to build; the latter keeps invariants enforceable in one place.
4. Where does the curation export live relative to the graph, and what triggers a re-export? I9 requires it to survive a rebuild, so it cannot live only inside `graph.kuzu/`.
