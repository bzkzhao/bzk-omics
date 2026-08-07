# HANDOFF.md — starting implementation

| Field | Value |
|---|---|
| Status | Active until week 2 is complete, then delete |
| Version | 1.0 |
| Last reviewed | 2026-08-07 |
| Depends on | All repository documents |
| Authoritative for | Nothing. This is scaffolding, not a source of truth |

The repository documents say *what* and *why*. This says *how to start*, and carries the context that lives in a conversation rather than in a specification. It has a short life — once the resolver and the first adapter exist, it is redundant and should be deleted rather than maintained.

---

## 1. Opening the first Claude Code session

Give it this, verbatim:

> Read CLAUDE.md first, then VISION.md, ONTOLOGY.md, ARCHITECTURE.md, ROADMAP.md and OPERATIONS.md. ONTOLOGY.md is normative — its DDL is a contract, not an example. Do not write any feature code yet. Set up the project skeleton per ARCHITECTURE.md §3 using uv, with pinned dependencies, and show me the structure before creating files.

Two things to resist in the first hour. It will offer to write an adapter — decline, the invariant tests come first. It will offer to simplify the schema — decline, and if something in the DDL genuinely does not work in Kùzu, amend `ONTOLOGY.md` first and then the code, never the reverse.

---

## 2. Environment

```bash
# Python 3.12 and uv already installed
git clone <your repo>
cd bzk-omics
uv init --python 3.12
```

Pin exactly, not with compatible-release specifiers. `OPERATIONS.md` §4 explains why for Kùzu specifically.

```
kuzu           # pin the exact version you install; pre-1.0, minor releases have changed behaviour
duckdb
polars
requests
pytest
pytest-cov
streamlit      # v0.1 interface; no SvelteKit
fastapi        # thin, for later; routes only per ADR-0018
scipy          # perseus_s0 implementation
numpy
```

Record the resolved Kùzu version in `ARCHITECTURE.md` §1 the moment you have it. Right now that row says "exact version pinned" with no number in it.

---

## 3. Build order, with acceptance criteria

Follow `ROADMAP.md` § Milestones. This adds the granularity that document deliberately omits.

### Status, 2026-08-07 — read this first

**Weeks 1–2 are complete.** On disk and committed:

- `bzk/ontology/schema.py` — structured DDL emitter, 56 tables, mirrors `ONTOLOGY.md` §4–6; guarded by `tests/test_schema.py` (parses the normative DDL, asserts agreement, builds on Kùzu 0.11.3).
- `bzk/ontology/invariants.py` — write-time checks I2, I3, I4, I10, I14, I15, I16, I19 plus change-set **structural validation (ADR-0019, incl. multiplicity)**, derived from `schema.py`.
- `bzk/resolve/uniprot.py` — isoform-aware resolver, two-tier immutable cache, 20/20 on PXD018299 offline.
- `bzk/rebuild.py` — drop / create-schema / replay / drift-check. I9 met **vacuously** only (no ingested content yet — see the Weeks 1–2 *Done when* note below).
- `bzk/adapters/base.py` — the `ObservationAdapter` contract, `SampleMapping`, `ParsedObservations`; `tests/test_adapters_base.py` pins it against `tests/fixtures/valid_changeset.json`.

`perseus.py` is **not** written. Do not start it first.

**The next action is documents, in this exact order — three separate turns:**

1. ~~**ONTOLOGY v1.3 — add `RESULT_FOR_PROTEIN`.**~~ **Done 2026-08-07.** `DifferentialResult → ProteinObservation` (`MANY_ONE`) added to §5 DDL and `schema.py` `REL_TABLES`; schema is now 57 tables (was 56); `tests/test_schema.py` and `tests/test_rebuild.py` green. **The next action is item 2.**
2. **ADR-0020 + `ONTOLOGY.md` §3/§9 id amendment** — deterministic, content-derived evidence-node ids (decision (a); §8).
3. **The curation loader** — reads `data/curation/*.json` in the shape those files already have; loader defaults and the `content_hash` / `Contrast` items are in §8.

*Only then* `bzk/adapters/perseus.py` (Weeks 3–4 below). The empty `raw/` (§8) bounds what can be validated end to end until it is populated.

### Weeks 1–2

**`tests/test_invariants.py` first, and failing.** One case per invariant that can be checked at write time — I2, I3, I4, I10, I14, I15, I16, I19. Each constructs a violating node and asserts the write is rejected. Write these before the schema exists; they will fail to import, which is correct.

**`bzk/ontology/schema.py`** — generate the Kùzu DDL from `ONTOLOGY.md` §4–6 rather than hand-writing it. A dict of node and edge definitions that emits Cypher. This is what makes a field rename a regeneration instead of a search across the codebase.

**`bzk/resolve/uniprot.py`** — port from `colab_identityresolution.ipynb` Steps 4 and 5 (the isoform-aware version, validated 20/20). **Not a verbatim port**, and the module docstring says so: two deliberate changes beyond adding the cache. (1) The `sequence_source` guard moves into the module — an isoform whose sequence cannot be fetched returns *no* sequence rather than the canonical one, so a caller cannot accidentally validate an isoform position against the canonical sequence (the notebook was safe only because Step 5 checked `sequence_source` first). (2) The persistent cache under `~/.bzk-omics/cache/uniprot/` is two-tier: entry metadata keyed on the base accession, sequence keyed on `accession#isoform#sv` and immutable — the immutable key needs the sequence version, which is only known after the entry fetch. Retention policy in `OPERATIONS.md` §3.

**`bzk/rebuild.py`** — drops and reconstructs from `raw/` plus the curation export. Written now, not later. I9 is an assumption until this runs.

*Done when:* twenty accessions resolve and validate; a mismatched position fails loudly; the graph drops and recreates its schema. "Rebuilds without loss" is met only **vacuously** so far — there are no observations in the graph to lose, since no adapter has ingested any. I9 therefore stays an assumption until the first adapter has put content in the graph and a rebuild reproduces it; §8 records this as partial, and it is not discharged by `rebuild.py` alone.

### Weeks 3–4

**`bzk/adapters/base.py`** then **`perseus.py`**. Signature is `(file, SampleMapping) -> ParsedObservations`, never a directory convention. `Analysis.kind = 'external'`, `parameters_observed = false`.

**Curation ingestion** — `data/curation/curation_PXD018299.json` is the fixture and the format. It was written by hand; the loader should accept exactly that shape.

*Done when:* a Perseus table is ingested, resolved, stored, and cross-queried against a second dataset.

### Weeks 5–6

**`bzk/adapters/maxquant.py`** — port the filtering logic from `colab_seethedata.ipynb` Step 7 and `colab_reproducefigure.ipynb` Steps 2–4.

**`bzk/quant/`** — DuckDB layer, I11.

**`bzk/stats/perseus_s0.py`** — see §5 below, which contains a warning.

---

## 4. Code that already exists

| Notebook | Cells | Becomes | Fidelity |
|---|---|---|---|
| `colab_identityresolution.ipynb` | 4–5 | `bzk/resolve/uniprot.py` | Ported, not verbatim: `sequence_source` guard moved into the module, two-tier cache added. Validated 20/20 |
| `colab_seethedata.ipynb` | 7 | `bzk/adapters/maxquant.py` filtering | Decoy and contaminant removal, semicolon splitting |
| `colab_seethedata.ipynb` | 2 | `bzk/adapters/pride.py` | The `ftp://` → `https://` conversion is permanent behaviour, not a workaround |
| `colab_reproducefigure.ipynb` | 4 | `bzk/stats/imputation.py` | Downshifted normal; seed mandatory per I15 |
| `colab_reproducefigure.ipynb` | 5 | `bzk/stats/` BH correction | Straightforward |
| `data/curation/curation_PXD018299.json` | — | Fixture and format spec | The shape the loader must accept |

---

## 5. The regression baseline — read before implementing statistics

**The 12-of-14 result was measured under Welch's *t*-test with Benjamini–Hochberg**, not under `perseus_s0`. Exact parameters:

```
quantity              Intensity columns
localization_prob     >= 0.75
filters               Reverse, Potential contaminant removed
presence rule         >= 2 replicates in either group
imputation            downshifted normal, 1.8 SD down, 0.3 SD width, seed 0
test                  Welch t, unequal variance
fdr                   Benjamini-Hochberg
significance          adj_p < 0.05 and log2FC > 1
result                12 of 14; ADAR (adj p 0.24) and PSMB9 (log2FC +0.89) missed
```

ADR-0015 makes `perseus_s0` the default. **The number under `s0` will not necessarily be 12** — the curved significance boundary admits and excludes different sites than straight cutoffs.

So: implement `welch_t` first, reproduce 12 of 14 exactly, and only then implement `perseus_s0` and record whatever it gives as a second baseline. Reversing that order means you cannot tell whether a wrong number is a bug in the pipeline or a real difference between tests. Both numbers belong in `ROADMAP.md` § Measured findings.

This is a genuine subtlety and easy to trip over.

---

## 6. Failure modes already encountered

All three cost time during exploration. All three are the same class: code that ran, printed cleanly, and was wrong.

**Index misalignment.** Filtering a pandas frame keeps the original row numbers. Building a new frame with fresh numbering and then looking up rows by the old numbering fails — loudly if the indices do not overlap, *silently* if they partly do. Use `.values` when constructing derived frames, or carry identifiers explicitly.

**Wrong column, no error.** A gene lookup used `Protein names` (descriptions like "Vigilin") instead of `Gene names` (symbols). It returned "not found" fourteen times, which reads exactly like a real negative result. This is the strongest argument for the 12-of-14 regression test: without a known-correct answer, a silent failure is indistinguishable from a finding.

**Isoform stripping.** `P09914-2` reduced to `P09914` fetches a different protein of different length, and positions resolve to the wrong residue without erroring. Fetch isoforms from the FASTA endpoint at their full accession. 30% of razor picks in the sample were isoforms.

---

## 7. What not to do in the first month

- **No SvelteKit.** Streamlit or a notebook. `ARCHITECTURE.md` §1.
- **No Reactome or GO import.** It will feel productive and consume a week.
- **No DIA-NN, FragPipe or Spectronaut.** One search-engine adapter validates the contract.
- **No downgrading an invariant to a warning** to make a dataset load. If a real file cannot satisfy an invariant, that is a finding about the invariant — amend `ONTOLOGY.md` and record why.
- **No new documents.** Seven is enough. Adding an eighth feels like progress and is not.

---

## 8. Open items carried into implementation

| Item | Where | Blocking? |
|---|---|---|
| ~~Kùzu version number not recorded~~ — recorded `==0.11.3` | `ARCHITECTURE.md` §1 | Resolved |
| `Contrast` reference-vs-evidence ambiguity | `ONTOLOGY.md` §11 Q1 | No — settle before v0.2 |
| ~~**`RESULT_FOR_PROTEIN` edge missing**~~ — added `DifferentialResult → ProteinObservation` (`MANY_ONE`) to ONTOLOGY §5 DDL (v1.3) and `schema.py` `REL_TABLES`; consistency test green | `ONTOLOGY.md` §5 | Resolved 2026-08-07 |
| **Deterministic evidence-node ids — decision (a), pending ADR-0020** | `ONTOLOGY.md` §3/§9 | Direction settled 2026-08-07, ADR not yet written. Evidence nodes (`SiteObservation`, `DifferentialResult`, `Analysis`, …) get **deterministic, content-derived ids** — decision (a) — not ULIDs. This makes re-ingestion idempotent: replaying the same input under I9 produces the same node ids rather than duplicates, which is what lets `rebuild.py` verify reproduction. It resolves the I7 / §3 / I9 tension noted during the resolver work in favour of I7's key discipline. The change is ADR-0020 plus a §3/§9 id-scheme amendment; sequence it **after** ONTOLOGY v1.3 (`RESULT_FOR_PROTEIN`) and **before** the curation loader |
| **Curation record carries no `content_hash`** | `data/curation/*.json`, `OPERATIONS.md` §2 | Every record under `data/curation/` identifies its input by bare filename, no checksum, so I9 replay cannot confirm it is running against the bytes the curation was written for. Format gap now recorded in `OPERATIONS.md` §2 (add SHA-256 `content_hash`); existing records back-filled when their input is next in hand. No — not blocking, but it lands with the curation loader |
| **`colab_reproducefigure.ipynb` cell 16 is a second test → a second `Analysis` (I16)** | statistics layer, weeks 5–6 | Cell 16 adds an `adj_p_moderated` column: a *second* significance test (moderated *t*) computed on the same matrix as the primary welch_t. Under I16 each declared quantity/test is its own `Analysis`, so `res` carries the outputs of **two** analyses, not one — the per-site table does not end at `n_candidate_proteins` as an earlier note implied. The adapter (or the notebook reconstruction) must emit two `Analysis` nodes and route each result column to its own. No — surfaces when that table is ingested |
| **Statistics-registry default vs on-disk baseline — ordering question** | `HANDOFF.md` §5, statistics layer | ADR-0015 makes `perseus_s0` the **default and required** registry entry (from author correspondence). But the 12-of-14 regression on disk was measured under `welch_t` + BH, and the only per-site result the group has produced (`colab_reproducefigure.ipynb`) is also welch_t. So the *validated-on-disk* method and the *default* method differ. §5 already fixes the build order (welch_t first, reproduce 12-of-14, then `perseus_s0` as a second baseline); the open question is which becomes the registry default the first adapter writes, and whether the two baselines are recorded side by side before that is decided. Keep measured (welch_t, on disk) and reasoned (perseus_s0, from correspondence) distinct — ADR-0015's own discipline. No — settle when the statistics layer lands |
| Multi-modified peptides | `ONTOLOGY.md` §11 Q3 | Possibly — will surface on first MaxQuant ingestion |
| **I17 `reviewed_preferred` promotion — owned by the search-output adapters** (decided 2026-08-07) | `ProteinAssignment` construction in `adapters/` | No — the Perseus (analysis-output) adapter has no candidate sets or razor picks (`ARCHITECTURE.md` §3), so I17 does not apply there. The promotion of a reviewed Swiss-Prot entry over a TrEMBL razor pick belongs to the **search-output adapters** (MaxQuant first), in **`ProteinAssignment` construction** (`ONTOLOGY.md` §6.3, I17), recorded as `basis = 'reviewed_preferred'`; it lands with the MaxQuant adapter (weeks 5-6). The resolver only reports review status |
| **Curation-loader default: curation `Analysis` (`kind = 'curation'`) → `parameters_observed = true`** | curation loader, weeks 3–4 | A curation `Analysis` records a sample-to-condition mapping or a manual assertion. The curation act is performed *for* the platform and its JSON record **is** the artifact — there is nothing executed elsewhere that the record merely reports. So `parameters_observed = true`: the platform observes the whole of what this `Analysis` consists of. This is the only case that defaults true. No — a loader default, applied when the loader is written |
| **Curation-loader default: `data/curation/analysis_*.json` → `parameters_observed = FALSE`** | curation loader, weeks 3–4 | These records describe a **Colab notebook run** (e.g. `colab_reproducefigure.ipynb`). I19: `false` means the analysis was run outside the platform, with parameters *as stated* rather than *as executed* — which is exactly a hand-authored JSON transcribing a notebook. The platform did not witness the execution; the same person having written both the curation and the notebook does not make it a witness, and "the parameters were executed, not reported" is the argument I19 exists to refuse. Consequence beyond the field: setting `true` would give the 12-of-14 baseline the same provenance standing as a platform-computed result — the exact promotion I19 forbids. Note the class boundary: the **analysis-output** class defaults `false` whether the external tool is Perseus (ADR-0017) *or* the group's own notebook — the split is **platform-executed vs not**, not who ran it. I16 is orthogonal to both: quantity and filters are required and recordable regardless, so declaring them never settles the I19 flag. No — a loader default, applied when the loader is written |
| **`Contrast` deferred to the adapter** | `ONTOLOGY.md` §11 Q1, curation loader | The curation records name their contrasts (`contrasts_of_interest`) but the `Contrast` node's reference-vs-evidence placement is unsettled (§11 Q1, v0.2). Default: the loader does not materialise `Contrast` nodes yet; the adapter constructs the contrast inline when it emits `DifferentialResult`s. Revisit with §11 Q1 before v0.2. No |
| **`raw/` is empty — blocks end-to-end ingestion** | `raw/`, `ROADMAP.md` § Deposit survey | No source tables are on disk. The first Perseus adapter fixture, the first `DifferentialResult` ingestion, and any non-vacuous I9 rebuild all depend on either re-downloading PXD018299 / the BJC supplementary from PRIDE and nature.com, or reconstructing `colab_reproducefigure.ipynb`'s `res` (which is never persisted — see the survey). Until `raw/` has content, the adapter can be *written* against the shared valid change-set but not *validated* against real input. **Yes** — for the first adapter's end-to-end test, not for writing the adapter |
| ADRs 0004–0014 unwritten | `decisions/` | No — write during weeks 7–8 |
| Search engine for the new USP18 dataset | Assumption A2 | Yes for that dataset only |
| Where in his pipeline the handover belongs | `ROADMAP.md` § Open questions | No — ask at the meeting |

### Unenforced invariants (audit 2026-08-07), by class

The write-time change-set checks (I2, I3, I4, I10, I14, I15, I16, I19) and change-set structural
validation (ADR-0019) are enforced in `bzk/ontology/invariants.py`. The rest are not yet enforced;
grouped by *how* they must be enforced, so a source-tree lint is not mistaken for a data check.

- **CS — write-time change-set check, not written.** **I1** (disjointness: reject locally-authored
  reference–reference edges; ref–ref edges carry `source`). **I8** (also WG: every `Sample` reaches a
  curation `Analysis` via `SAMPLE_GENERATED_BY`). **Residue agreement across `SITE_ON`** (completes
  I2, candidate new invariant): I2 pins the sequence version but never verifies the residue at the
  site's position matches the parent `Protein`'s sequence — the write-time mirror of the resolver's
  `validate_position`. It belongs in the write-time set: it would catch a site keyed at one
  residue attached by `SITE_ON` to a protein where that position is a different residue (the
  isoform-bug arithmetic, and exactly the malformed second `SITE_ON` the valid fixture now avoids).
  It needs the `Protein.sequence` present in the change-set, which the label check does not yet
  require, and it overlaps the resolver, so it is a graph-ingestion backstop rather than the first
  line. Build with the first adapter, not before.
- **WG — whole-graph / query-time, not written.** **I5** (provenance reachability; entities with no
  path to an `Analysis` flagged `unprovenanced` at query time, §7). **I8** (the reachability half).
- **EX — export boundary, not written.** **I18** (embargo). *Trigger: I18 must land with the first
  export, report or figure-writing path, before that path merges.* The risk is not the embargoed
  dataset arriving — local queries over it are unrestricted (§8) — it is the first code that can
  write a file. Streamlit output is on the v0.1 list, so this is an ordering constraint on that work,
  not a reminder.
- **LINT — source-tree lint, not a data check, not written.** **I12** (no tryptic assumptions in
  core: no assumption peptides end in K/R, carry one modification, or map to one protein). **I13**
  (no branching on `search_engine` / `acquisition_mode` / `library_type` / `test` outside
  `adapters/` and the stats registry). Both need a test that greps/parses the source, not a
  change-set.
- **CON — enforced by construction, pending the code that constructs.** **I7** (deterministic
  content-derived reference keys; holds once a single key builder exists). **I17** (reviewed
  preferred — decided 2026-08-07: owned by the search-output adapters (MaxQuant first) in
  `ProteinAssignment` construction; the Perseus analysis-output adapter has no candidate sets, so
  it does not apply there. Lands weeks 5-6. See the table row above).
- **write-path, not written.** **I6** (append-only assertions: reject in-place edits of
  `ModifierAssignment` / `DifferentialResult`; supersession creates a new node; retraction
  propagation is a v0.2 action-layer concern).
- **data layer, pending.** **I11** (quantitative retention: every observation keeps its per-sample
  matrix in DuckDB — needs the `quant/` layer).
- **OP — operational, partial.** **I9** (reproducible rebuild — exercised by `rebuild.py` for schema
  recreation; full regeneration pending adapters).

---

## 9. Delete this file

Once the resolver and the Perseus adapter exist and the rebuild runs, everything here is either obsolete or has migrated into a document that owns it. A handoff note kept past its usefulness becomes a second, stale source of truth — which is the one thing `CLAUDE.md` forbids.
