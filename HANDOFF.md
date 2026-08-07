# HANDOFF.md — starting implementation

| Field | Value |
|---|---|
| Status | Active until week 2 is complete, then delete |
| Version | 1.0 |
| Last reviewed | 2026-08-06 |
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

### Weeks 1–2

**`tests/test_invariants.py` first, and failing.** One case per invariant that can be checked at write time — I2, I3, I4, I10, I14, I15, I16, I19. Each constructs a violating node and asserts the write is rejected. Write these before the schema exists; they will fail to import, which is correct.

**`bzk/ontology/schema.py`** — generate the Kùzu DDL from `ONTOLOGY.md` §4–6 rather than hand-writing it. A dict of node and edge definitions that emits Cypher. This is what makes a field rename a regeneration instead of a search across the codebase.

**`bzk/resolve/uniprot.py`** — port from `colab_identityresolution.ipynb` Steps 4 and 5 (the isoform-aware version, validated 20/20). **Not a verbatim port**, and the module docstring says so: two deliberate changes beyond adding the cache. (1) The `sequence_source` guard moves into the module — an isoform whose sequence cannot be fetched returns *no* sequence rather than the canonical one, so a caller cannot accidentally validate an isoform position against the canonical sequence (the notebook was safe only because Step 5 checked `sequence_source` first). (2) The persistent cache under `~/.bzk-omics/cache/uniprot/` is two-tier: entry metadata keyed on the base accession, sequence keyed on `accession#isoform#sv` and immutable — the immutable key needs the sequence version, which is only known after the entry fetch. Retention policy in `OPERATIONS.md` §3.

**`bzk/rebuild.py`** — drops and reconstructs from `raw/` plus the curation export. Written now, not later. I9 is an assumption until this runs.

*Done when:* twenty accessions resolve and validate; a mismatched position fails loudly; the graph rebuilds without loss.

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
| Multi-modified peptides | `ONTOLOGY.md` §11 Q3 | Possibly — will surface on first MaxQuant ingestion |
| **I17 `reviewed_preferred` promotion is unowned** | resolver surfaces `reviewed`; nothing consumes it | No — decide with the first adapter. The promotion of a reviewed Swiss-Prot entry over a TrEMBL razor pick belongs to the **adapter** (which assembles the candidate set) or to **`ProteinAssignment` construction** (`ONTOLOGY.md` §6.3, I17), recorded as `basis = 'reviewed_preferred'` — never to the resolver, which only reports review status |
| ADRs 0004–0014 unwritten | `decisions/` | No — write during weeks 7–8 |
| Search engine for the new USP18 dataset | Assumption A2 | Yes for that dataset only |
| Where in his pipeline the handover belongs | `ROADMAP.md` § Open questions | No — ask at the meeting |

### Unenforced invariants (audit 2026-08-07), by class

The write-time change-set checks (I2, I3, I4, I10, I14, I15, I16, I19) and change-set structural
validation (ADR-0019) are enforced in `bzk/ontology/invariants.py`. The rest are not yet enforced;
grouped by *how* they must be enforced, so a source-tree lint is not mistaken for a data check.

- **CS — write-time change-set check, not written.** **I1** (disjointness: reject locally-authored
  reference–reference edges; ref–ref edges carry `source`). **I8** (also WG: every `Sample` reaches a
  curation `Analysis` via `SAMPLE_GENERATED_BY`).
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
  preferred — see the table row above; recorded by the adapter or `ProteinAssignment` construction).
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
