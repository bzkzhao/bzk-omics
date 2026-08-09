# ARCHITECTURE.md

| Field | Value |
|---|---|
| Status | Draft |
| Version | 1.16 |
| Last reviewed | 2026-08-09 |
| Depends on | `ONTOLOGY.md`, `VISION.md` |
| See also | `OPERATIONS.md` — backup, cache policy, pinning, testing |
| Authoritative for | Language and library choices, storage layout, module boundaries |

This document is expected to change weekly during v0.1. Decisions recorded here that survive scrutiny should be promoted to numbered ADRs in `decisions/`.

---

## 1. Stack

| Layer | Choice | Rationale |
|---|---|---|
| Language | Python 3.12 | The proteomics ecosystem is Python. `pyteomics`, `pyopenms`, UniProt clients, `polars` all exist and are tested. Reimplementing them elsewhere is a category error. |
| Package management | `uv` | Fast, lockfile-based, single-binary. Supports the one-afternoon install promise. |
| API | FastAPI | Typed, async, generates OpenAPI for the front end for free. |
| Graph store | Kùzu, **pinned `==0.11.3`** | Embedded, Cypher, columnar, MIT-licensed, no server process. Pre-1.0, so the pin is not optional — see `OPERATIONS.md` §4. |
| Columnar store | DuckDB | Embedded, fast aggregation over site × sample matrices, reads Parquet directly. |
| DataFrames | Polars | Lazy evaluation and predictable memory on wide quantitative tables. |
| Statistics | Pluggable registry over NumPy / SciPy | See §4. |
| Front end | **Streamlit or notebook in v0.1**; SvelteKit + TypeScript deferred to v0.2 | Visualisation is not the differentiator. A minimal interface is enough for the anchor laboratory to use the pipeline. |
| Charts | Observable Plot or D3 | Volcano, UpSet, site-level heatmaps. |

**Deferred:** SvelteKit frontend (v0.2), Tauri desktop packaging (v0.2), local LLM serving via Ollama or vLLM (v0.3), any cloud component.

---

## 2. Storage layout

The boundary is defined normatively in `ONTOLOGY.md` §2. Concretely:

```
~/.bzk-omics/            # per-machine runtime state — rebuildable, not committed
  graph.kuzu/            # identity, relationships, provenance
  quant.duckdb           # site × sample and protein × sample matrices
  raw/                   # ingested source files, content-addressed by SHA-256
  cache/uniprot/         # entry/  by accession — MUTABLE snapshot, overwritten on re-fetch
                         # seq/    by accession#sv — the archive, written once:
                         #           .txt        the sequence
                         #           .meta.json  the pin: entry_type, reviewed

<repo>/
  data/curation/         # curation, analysis and resolution records (JSON) — the non-derivable
                         # human-authored inputs, version-controlled (OPERATIONS.md §2, §1)
```

**The observation id is the join key into `quant.duckdb`** — `SiteObservation.id = site_values.observation_id`, `ProteinObservation.id = protein_values.observation_id` — exactly as `ONTOLOGY.md` §2 says. **Corrected 2026-08-08 (ADR-0004):** this line read *"`SiteObservation.quant_ref` is the join key"*, which contradicted §2 and named only one of the two grains. Both cannot be the join key; if the store is keyed by the id then `quant_ref` duplicates it. `quant_ref` instead names the **table** an observation's values are in, and `NULL` means none are retained — the I11 violation state, readable at the node without opening DuckDB. Nothing per-sample enters the graph: `quant_ref` is one-per-entity, which is the side of §2's own rule that belongs on the node.

The split is deliberate: everything under `~/.bzk-omics/` is derived and rebuildable (I9), so it is per-machine and gitignored; `data/curation/` holds the one class of content that cannot be recomputed — human judgement — so it lives in the repository and survives a disk failure independently (OPERATIONS.md §1). `rebuild.py` reads the curation export from here.

Isoform accessions are cached under their full form (`P09914-2`), never collapsed to canonical. Fetching `rest.uniprot.org/uniprotkb/P09914-2.fasta` returns the isoform sequence; stripping the suffix returns a different protein of different length, and positions resolved against it are wrong without erroring.

The UniProt cache is not optional. Site position validation requires the exact sequence for the exact version, and a laptop-local product cannot depend on network availability at query time.

**Corrected 2026-08-09 — this said *"cache entries are immutable, a new sequence version is a new entry, never an overwrite"*, and that is true of one of two tiers.** It is the fourth place one sentence was written from one belief, alongside `ONTOLOGY.md` §8 I9, §11 Q6 and `OPERATIONS.md` §1. What is immutable is `seq/` — the sequence and its pin, keyed by `{accession}#sv{n}` and written once. `entry/` is keyed on the bare accession and is overwritten by every re-fetch. `OPERATIONS.md` §3.1 owns the arrangement and the reason it is safe: nothing identity-bearing is read from the mutable tier.

---

## 3. Modules

```
bzk/
  ontology/      # schema DDL, node/edge dataclasses, invariant checks, the key builder
    store.py     # the change-set write path: the only module that knows both it and Kùzu
    seed.py      # Modifier nodes from GG_REMNANT_MODIFIERS — reference data from version control
  curation/      # data/curation/*.json -> change-set; the one non-derivable input (§2)
    loader.py
  adapters/      # ingestion; one module per search engine or analysis tool
    perseus.py   # analysis-output (ADR-0017); protein grain, no network in the parse path
    maxquant.py  # the guarded table reader every MaxQuant module goes through
    maxquant_sites.py  # search-output; site grain, resolver injected, refusals counted
    fragpipe.py
    diann.py
    base.py      # the adapter contract
  sources/       # retrieval of public deposits (PRIDE); not a search-engine adapter
    pride.py
  resolve/       # UniProt resolution, sequence-version pinning, position validation
    nodes.py     # accession -> Protein + ProteinSequence (ADR-0005); injected, offline-testable
  quant/         # DuckDB layer, normalisation
  stats/         # moderated t-test, BH, protein-level adjustment
  provenance/    # PROV-O mapping, content hashing; raw_store.py is the content-addressed raw/
  drift.py       # `bzk drift` — validates the sequence archive against UniProt; writes a receipt
  http.py        # the injected-HTTP protocols the three network-touching modules share
  api/           # FastAPI routes
web/             # SvelteKit
```

**`curation/` is separate from `adapters/` for the same reason `sources/` is.** An adapter is one
module per search engine, reading a quantitative output file under the `ObservationAdapter`
contract. A curation record is not an engine's output and carries no measurements: it is the human
judgement about which raw file corresponds to which condition, which §5.3 models as an *activity*.
It also runs first and produces the `SampleMapping` an adapter then consumes, so making it an
adapter would make the contract circular.

**The resolver reaches an adapter by injection, never by import.** `bzk/resolve/nodes.py` projects
an accession onto the two nodes ADR-0005 splits it into — `Protein` for stable identity,
`ProteinSequence` for the version a residue position is meaningless without — and an adapter takes
it as a constructor argument, so `parse(file, mapping)` keeps the signature this section fixes.
Two alternatives were rejected: threading a session through `parse` breaks the protocol and makes
every adapter test need a network stub; resolving *after* the adapter leaves it unable to key a
`ModificationSite`, which needs `ProteinSequence.id`, so it could not emit a valid change-set at
all. Unresolved accessions are **reported, not raised** — at the site table's 4,815 distinct
accessions a dead one is expected, and whether it sinks a site is the adapter's call, not the
resolver's.

**An adapter reports what it refused.** `ParsedObservations.refusals` carries one entry per input
row that did not become a node, with a stable reason slug and a human-readable detail; it defaults
to empty so an adapter with nothing to refuse says nothing. A change-set is a claim about what a
file contained, and an adapter that filters silently makes that claim false — `CLAUDE.md` § Flag
rather than hide. This is not bookkeeping: `maxquant_sites.py`'s residue check produces the
sequence-drift measurement on record in `ROADMAP.md` § Measured findings entirely through this
channel, and a `logging.warning` would have left it unmeasurable.

**`ontology/store.py` is the only module that writes.** `invariants.py` is deliberately
storage-free — a change-set is plain data, which is what lets every invariant be a pure function
testable without a graph (ADR-0019's rejected alternative (b)) — so the knowledge of how a
change-set becomes rows lives in exactly one place, out of the validator and out of every producer.
It `MERGE`s rather than `CREATE`s: ids are content-derived (I7, ADR-0020) and ADR-0019 requires
producers to re-stage the referents they name, so the same `Protein` legitimately arrives in many
change-sets and must converge rather than collide. That is the write-path half of the guarantee the
digest scheme makes on the read side, and it is what makes I9's replay idempotent.

**`http.py` holds protocols, not a client.** Three modules take an injectable `session` so their
logic is exercisable offline (`resolve/uniprot.py`, `sources/pride.py`, and `rebuild.py`, which
passes one through). Each declared it `requests.Session`, which is stricter than the code needs;
the requirement is structural, and two small `Protocol`s say so — one for a byte fetch, one for the
REST surface. `requests` stays the only HTTP library and nothing wraps it.

### The adapter contract

**Priority order is Perseus first, then MaxQuant; DIA-NN is deferred to v0.2** (`ROADMAP.md` § Explicitly deferred). An earlier revision of this section read *"DIA-NN first"*, reasoning that the Pinto-Fernández group moved to DIA in 2022 (ABPP-HT*) and that its 2025 work uses DIA-NN 2.0 with FASTA-predicted libraries on an Orbitrap Fusion Lumos, so MaxQuant was archival. ADR-0017 reversed that: with the platform positioned downstream, the shortest path to holding a real user's real results is the analysis-output adapter, and the collaborator confirmed Perseus is his workflow. The tables below carry the current order.

**`sources/` is separate from `adapters/` deliberately.** This section defines an adapter as one module per search engine, and the contract is `ObservationAdapter` — `sniff` / `parse` over a file already in hand. Fetching a deposit is neither; it *produces* the file an adapter then reads. It is also separate from `provenance/`, which owns the content-addressed store and stays offline so it can be tested without a network. (`HANDOFF.md` §4 originally pencilled this as `adapters/pride.py`; module boundaries are this document's to settle, and `sources/pride.py` is where it landed.)

Two classes of adapter, because the platform sits downstream of both search engines and analysis tools.

**Analysis-output adapters** — ingest results computed elsewhere. `Analysis.kind = 'external'`, `parameters_observed = false` (I19).

| Adapter | Priority | Rationale |
|---|---|---|
| Perseus result table | 1 | The collaborating group's workflow, confirmed by correspondence. The shortest path to holding a real user's real results |

**Declared parameters are constructor arguments, not `parse` arguments.** An analysis-output adapter must set `Analysis.quantity`, `test`, `fdr_method` and `external_version`, and a result table states none of them — that is what `parameters_observed = false` means (§5.4, I19). They therefore arrive in a `DeclaredAnalysis` passed when the adapter is constructed, leaving `parse(file, mapping)` exactly as the `ObservationAdapter` protocol declares it. The alternative, widening `parse`, would have made the contract different for the two adapter classes; the alternative of defaulting them would make a reported parameter indistinguishable from an observed one, which is the promotion I19 exists to refuse. Contrasts arrive the same way, since Perseus builds its column suffixes from its own group names and those are not the platform's condition labels.

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

**The PXD018299 deposit is CRLF throughout** (2,342 CRLF line endings, zero bare LF; measured 2026-08-07 on the fetched bytes). **Re-measured 2026-08-08 and it stands exactly**: digest-confirmed through `raw_store.verify`, then `read_bytes` — 2,759,052 bytes, **2,342 CRLF, 0 bare LF, 0 bare CR**, ending `b'94\r\n'`. The re-measurement happened because a 2026-08-08 count contradicted this line and reported the deposit as LF; **that count was the artefact, not this one.** It read the file with `Path.read_text()`, which opens in text mode with universal newlines and translates CRLF to LF before anything can count it — through that path the same bytes report 0 CRLF and 2,342 LF. Recorded here rather than only in a handoff note because this line is what the next reader will doubt, and the way to doubt it wrongly is one function call away: **a line-ending measurement taken through any text read is a measurement of Python's newline handling.** `pandas.read_csv` handles it, but any manual `split('\n')` leaves a trailing `\r` on the last field of every row — so the 159th column parses as `'Best PEP scan number\r'` rather than `'Best PEP scan number'`. That is the ran-cleanly-and-was-wrong class `HANDOFF.md` §6 catalogues: a lookup on the last column simply returns nothing.

**Six lines of `HAP1_USP18KO_proteinGroups.txt` are not rows** (measured 2026-08-07). MaxQuant writes long semicolon-separated numeric lists in its `*_IDs` columns and some spill onto their own physical lines, each carrying exactly the header's field count — so the field count matches, every structural check passes, and `pandas` reads them as data whose accession column holds numbers like `6215;8153;8154`. Same class as the CRLF note above, same file, same reader: it runs cleanly and is wrong. The effect on that file was to inflate the largest apparent protein group from **33 members to 5,090** while moving the headline multi-mapping percentage by 0.1 — so no summary statistic would have caught it. The test is the file's own bookkeeping rather than a heuristic: `id` is a contiguous 0-based row number, so a line without one is not a row. Implemented once in `bzk/adapters/maxquant.py`, which every MaxQuant reader goes through, rather than in whichever module met it first.

**An analysis output may not be filtered, and cannot be assumed to be.** BJC Supplementary Data 3 — a published table of significantly-changed proteins, and a real Perseus export — carries **12 rows flagged `C: Potential contaminant`**. Not a defect in the paper, since the column is right there; but it settles a design question for the analysis-output adapter, which could easily have assumed a result table had been through the filters its `Analysis` records. It has not. `filters_applied` describing what the *user says* they applied, rather than what the file demonstrates, is `parameters_observed = false` doing exactly its job (§5.4, I19).

**Adapter responsibilities beyond parsing.** Measured against PXD018299: drop `Reverse` and `Potential contaminant` rows before anything else; normalise sample names (one replicate carries an instrument run ID); convert PRIDE `ftp://` locations to `https://ftp.pride.ebi.ac.uk`; record rather than apply the localisation threshold; emit the full candidate protein set, never the razor pick alone.

**Identifier translation is first-class.** Gene symbol, UniProt accession and protein description are three namespaces for one entity, and search output carries all three inconsistently (`Gene names`, `Proteins`, `Protein names`, all semicolon-separated). Without translation the user cannot ask a question in the vocabulary they think in — a query for "ADAR" must reach a row keyed on `P55265`. **Where each namespace lives was settled 2026-08-08** (`ONTOLOGY.md` §4): the symbol on `Gene.symbol`, the accession on `Protein.accession`, the protein description on `Protein.name`. Three namespaces, three columns — which is why routing the symbol onto `Protein.name` was rejected: it would collapse two of the three into one column and leave the third homeless. Resolution prefers reviewed Swiss-Prot entries over TrEMBL where both appear in a candidate set, recorded as `ProteinAssignment` basis rather than applied silently.

**No branching on pipeline metadata** (I13). `acquisition_mode`, `search_engine` and `library_type` are recorded fields. A conditional on their value anywhere outside `adapters/` means the abstraction has leaked and the next pipeline change becomes a rewrite rather than a new module.

`SampleMapping` is supplied by SDRF where present and by manual curation where not. Per `ONTOLOGY.md` §5.3, the adapter does not consume a configuration file: it consumes a `SampleMapping` that has already been written to the graph as an `Analysis` node with `kind = 'curation'`, and returns `Sample` nodes bearing `SAMPLE_GENERATED_BY` edges to it.

Practically this means the mapping UI is a write path into the graph, not a form that produces YAML. A corrected mapping creates a new curation node and retracts the old under I6; it never edits in place. The `basis` and `confidence` recorded there propagate to every derived result, which is what invariant I8 enforces at export.

---

## 4. Statistics

### Pluggable by construction

**No statistical test is privileged by the schema.** `Analysis.test` is a recorded string that nothing downstream branches on. Tests register against a common interface and are selected per analysis — the test and its `fdr_method` are properties of the `Analysis`, not of each `DifferentialResult` (ONTOLOGY §5, I16, ADR-0020).

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
| `moderated_t_ebayes` | **v0.2, not v0.1** | Empirical Bayes variance shrinkage (Smyth 2004). Better calibrated at *n* = 3 than a plain *t*-test; retained for comparison. `ROADMAP.md` defers it — it serves the comparison capability, not the first pipeline, and ROADMAP is authoritative for scope |
| `welch_t` | Sanity check | Plain two-sample test; useful for detecting when the choice of test is load-bearing |

`perseus_s0` is not the same test as `welch_t` with Benjamini–Hochberg. The `s0` parameter introduces a fold-change dependence into the significance threshold, producing the characteristic curved boundary on a Perseus volcano rather than straight cutoffs on both axes. A reproduction that ignores this will not match the group's numbers even when it recovers the same proteins.

Required parameters, recorded on the `Analysis` per I16: `s0`, `fdr`, and the number of randomisations.

**To confirm with the collaborator:** the exact `s0` and FDR values used, and whether "difference in intensities" denotes the difference of log₂ values (which is the log fold change) or an untransformed difference.

FDR control (BH, permutation) is a separate pluggable step recorded in `fdr_method`. Perseus uses permutation-based FDR, not BH.

### Protein-level adjustment

Site-level diGly quantification is confounded by parent protein abundance: a site appears regulated when its protein is regulated, independent of modification stoichiometry. Where a matched proteome dataset exists for the same samples, the site log₂FC is corrected against the protein log₂FC.

`protein_adjusted` is a **tri-state string, not a boolean** — `applied` | `not_applied` | `native` (`ONTOLOGY.md` §5, I4). `applied` requires an `ADJUSTED_BY` edge naming the protein-level result used; `native` means the source quantity was already ratiometric; `not_applied` is labelled *stoichiometry-uncorrected* in every view and export.

**Both results are stored, not one.** A single site-level `Analysis` emits the uncorrected result *and* the corrected one, sharing their analysis, observation and contrast and separated only by `protein_adjusted` / `adjustment_method` (`ONTOLOGY.md` §3). Holding both is the point: the user can see what the correction did rather than being handed a corrected number alone.

PXD018299 carries a matched proteome generated by splitting 20 µg of digest before the GlyGly immunoprecipitation, so the pairing is available by construction. Getting this right matters more than any feature.

## 4a. Testing

Tests are written before the code they exercise, and the invariant suite comes before any adapter. Full strategy and fixture design in `OPERATIONS.md` §6.

The short version: one failing test per invariant, adapter contract tests against a committed PXD018299 subset, resolution edge cases covering isoforms and amended sequences, and the 12-of-14 regression running through the real pipeline rather than a notebook.

This ordering exists because the invariants are the product. Adapters that ingest data while quietly violating I3 or I14 are worse than no adapters, and under deadline pressure a warning is something a person clicks past.

---

## 5. Seed ADRs

To be written as numbered, immutable records in `decisions/`:

- `0001` Two-graph model: reference and evidence disjoint
- `0002` Python over TypeScript for the backend
- `0003` Kùzu over Neo4j for the graph store
- `0004` Split storage: graph identity in Kùzu, quantitative matrices in DuckDB
- ~~`0005`~~ Sequence version **and isoform** as part of the `ModificationSite` **and `Protein`** keys — **written 2026-08-07**, see [`decisions/0005`](decisions/0005-modificationsite-and-protein-keys.md)
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
- ~~`0017`~~ Downstream positioning, with both ingestion paths — **written**, see [`decisions/0017`](decisions/0017-downstream-positioning.md)
- `0018` Typed API routes only; the front end never queries the graph directly

---

## Open questions

1. Does the UniProt cache need historical sequence versions, or only current? Measured: 1 of 20 sampled PXD018299 sequences was amended after the search, so roughly 5% of sites are at risk of drift. Current-only resolution flags them; historical retrieval would reconcile them. Flagging is cheaper and satisfies I2 — resolve in favour of flagging unless the rate rises.
2. Where does normalisation live — in `quant/` as a storage-time transform, or in `stats/` as an analysis-time one? Storage-time is faster; analysis-time is more auditable and better matches the provenance model.
3. ~~Does the front end query the graph directly, or only through typed API routes?~~ **Resolved 2026-08-06: typed API routes only.** The front end never touches Kùzu. Direct access would place invariant enforcement — I3, I14, I15, I18, I19 — in two places, and I18 in particular must sit at a single export boundary or it is not enforceable at all. The cost is one indirection; the benefit is that honesty guarantees have exactly one implementation.
4. ~~Where does the curation export live relative to the graph~~, and what triggers a re-export? **Location resolved 2026-08-06: `data/curation/` in the repository, version-controlled** — see §2 and `OPERATIONS.md` §2. I9 requires it to survive a rebuild, so it cannot live only inside `graph.kuzu/`; the human-authored records are the one non-derivable input and are committed. **The re-export trigger remains open** — a daemon is heavier than this product should be; a check on startup and shutdown may suffice. This is also `OPERATIONS.md` open Q1.
