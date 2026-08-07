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
2. ~~**ADR-0020 + `ONTOLOGY.md` §3/§9 id amendment.**~~ **Done 2026-08-07.** ADR-0020 written; §3 id scheme and the §5.1 contract row amended, §9 worked example restubbed to content-derived digests (ONTOLOGY v1.4). Direction unchanged (decision (a)); form chosen is an opaque `bzk:`+truncated-SHA-256 digest over a canonical identity tuple. The key **builder** itself is code and lands with item 3 / the adapters (I7 CON). Follow-ups 2026-08-07: §3 now carries a **per-label identity table** (identifying fields + anchors per evidence node type — the builder mirrors it, not the reverse), and OPERATIONS §2 a **retraction-record format** (retracted id, `retracted_at`, reason) so retraction survives rebuild under I6. Correction 2026-08-07: the §3 identity table surfaced a pre-existing DDL/ARCHITECTURE contradiction — `test` / `fdr_method` were on `DifferentialResult` but ARCHITECTURE §4 records them on `Analysis`; both columns moved to `Analysis` (ONTOLOGY v1.6, ARCHITECTURE v1.1), `s0` stays in `parameters_json` (canonicalized before hashing), and `tests/test_schema.py` now guards the §3 table — extended 2026-08-07 to cover **reference** nodes too (every DDL node table has exactly one row), to check anchor **edge direction** against the DDL rather than the name alone, to parse the §4 **key templates**, and to check reference ids on disk against §4's canonicalization (Unimod-only modification keys, unpadded `sv`, uppercase residue, lowercase CURIE prefix). Follow-on 2026-08-07: the converse (completeness) check found `Analysis` omitting `basis`/`confidence` from identity — the I8 curation-collision — now added; §3 gained an `Excluded columns` column so the guard enforces a full partition of every evidence node's columns (identifying ∪ excluded == columns), ONTOLOGY v1.7. **The next action is item 3.**
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
| ~~**Deterministic evidence-node ids — decision (a)**~~ — ADR-0020 written; §3/§5.1/§9 amended (ONTOLOGY v1.4). Opaque `bzk:`+truncated-SHA-256 digest over a canonical identity tuple; the key builder is code, lands with the loader/adapters (I7 CON) | `ONTOLOGY.md` §3, ADR-0020 | Resolved 2026-08-07 |
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

### The curation loader is blocked on two gaps in the committed records (2026-08-07)

The key builder now exists (`bzk/ontology/keys.py`), so the loader has ids to mint with. But
**neither committed curation record can yet produce a validating change-set**, and both reasons are
the schema working rather than failing — under ADR-0021 a node cannot be minted without its
identifying values, so the loader must refuse rather than invent.

1. **No `content_hash`, so no `Dataset`.** `Dataset` identity *is* `content_hash` (§3), and its
   absence is classified neither `determined` nor `curated`, so it must be present. Both records
   identify their input by bare filename (`HAP1_USP18KO_GlyGlyKSites.txt`). This is the gap
   `OPERATIONS.md` §2 already records; it now blocks rather than merely worries. It cascades: with
   no `Dataset` there is no `USED` anchor for an `Analysis` and no `REPORTED_BY` for an observation.
   **Fix:** back-fill the SHA-256 when the input file is next in hand — which is the same moment
   `raw/` gets populated, so the two unblock together.
2. **No `Project` or `Experiment`, so no `Sample`** — **format decided 2026-08-07: the record grows
   the block.** Minting an `Experiment` from the accession was rejected: it would invent a title,
   which `CLAUDE.md` forbids, and the title is the curator's to supply. `Sample` anchors on
   `Experiment` (`PERFORMED_ON`) and `Experiment` on `Project` (`CONTAINS`), so the whole chain must
   be constructible before any `Sample` id exists. The block is **exactly the identifying fields of
   those two nodes and nothing more**:

   ```jsonc
   "project":    { "title": null },                       // REQUIRED — Project's only identifying field
   "experiment": { "title": null,                         // REQUIRED — identifying
                   "modality": "digly_proteomics",        // REQUIRED — identifying; moved from top level
                   "organism_taxid": 9606 }               // REQUIRED — identifying since ONTOLOGY v1.13
   ```

   `modality` **moved** out of the top level into the block rather than being duplicated: it is an
   `Experiment` field, and two homes for one fact is the defect this repository keeps repairing.
   `Project.created_at` is not in the block — it is non-identifying, so the loader does not need it.

   A third, smaller instance sits in `mapping`: every entry now carries `source_type` (null,
   awaiting the curator). It is identifying on `Sample` and is **not** a determined absence, so a
   `Sample` cannot be keyed without it — whereas `model_system` may stay absent for a cell line,
   because *that* absence is determined by `source_type` (§3).

   Consequence worth stating: `organism_taxid` is asserted at experiment level rather than derived
   from the samples, so **one `Experiment` is one organism**, and cross-species work is two
   experiments rather than one with mixed samples.

   **`source_type` resolved 2026-08-07** — `cell_line` on all twelve entries (HAP1 is a near-haploid
   human cell line derived from KBM-7). The two titles remain the curator's to supply.

   **Pending values carry a structured marker.** A record's top-level `pending` object maps the
   dotted field path to a note: the keys are machine-detectable, so **the loader refuses by field
   name rather than failing late on a null**, and the notes state the consequence at the point
   someone will be editing — both titles are *identifying*, so supplying or changing one re-mints
   the `Experiment` id and every `Sample` id beneath it. Cheap while the graph is empty (I9
   regenerates it); not cosmetic afterwards. The `unresolved` prose is kept alongside because it
   carries the reasoning a marker cannot — in particular *why the loader must not derive a title* —
   which is what stops a later session quietly filling it in. Marker for detection, prose for
   reasoning. `tests/test_schema.py` checks every marked path resolves to a null, so a filled value
   cannot leave a stale marker behind and make the loader refuse a record that is ready.

   **The loader waits on the two titles.**

Neither is a defect in the loader design; both are the record format meeting a rule that did not
exist when the records were hand-written. `source_type` is a third, smaller instance: `Sample`
requires it and the mapping entries imply it (`cell_line` present ⇒ `cell_line`) without stating it.

### The key builder's contract (audit 2026-08-07) — write this before the builder, not after

The 2026-08-07 identity audit measured the value space of every identifying field in `ONTOLOGY.md`
§3. **Two of roughly forty-five are guarded**: `Analysis.quantity` (`QUANTITY_VALUES`, now checked at
write time by `_check_I16` and on disk by `tests/test_schema.py`) and
`DifferentialResult.protein_adjusted` (`PROTEIN_ADJUSTED`, checked by `_check_I4`). Everything else
relies on adapters happening to emit canonical values, which is precisely the assumption ADR-0020's
idempotent replay cannot make: two spellings of one fact mint two ids for one thing.

**Do not patch this field by field.** `quantity` was closed one turn, `parameters_json` given a
canonicalization rule another, and the audit found the remaining ~43 unguarded — the pattern is the
defect. The fix is **one canonicalization discipline implemented once in the key builder**, covering
three families:

1. **Prose-closed, unguarded enums** (~15 fields): `Experiment.modality`; `Sample.source_type`,
   `replicate_type`; `Analysis.kind`, `basis`, `test`, `fdr_method`, `external_tool`;
   `Imputation.method`, `scope`; `DifferentialResult.adjustment_method`; and the `basis` of all three
   `EvidencedInference` subtypes. Each is closed in a document and open in code. `Analysis.kind` is
   the worst: `_check_I16` branches on `kind == 'curation'`, so a misspelling both forks the id *and*
   silently escapes the quantity and filter checks.
   **`Analysis.confidence` is the one still fully unguarded.** `confidence` on the three
   `EvidencedInference` subtypes is now wired to `schema.CONFIDENCE` (`ambiguous` | `probable` |
   `confirmed`) via `_check_I3` / `_check_I10` / `_check_I14`, but `Analysis.confidence` is
   curation's **separate** vocabulary — `authoritative` | `inferred` (§5.3) — which no frozenset
   models and no check reads. Reusing `CONFIDENCE` for it would be wrong, not merely loose: the two
   sets share no values. It needs its own closed enum in `schema.py` and a checker, and it is
   identifying, so a misspelling forks an `Analysis` id.
2. **Order-sensitive lists** (3 fields): `Analysis.filters_applied`,
   `ModifierAssignment.candidate_modifiers`, `ProteinAssignment.candidate_proteins`. Element order
   alone changes the id, and a search engine's candidate ordering is not canonical — at I14's
   measured 82% multi-mapping this is the common path, not an edge case. Sort before hashing.
3. **Unformatted floats** (4 fields): `Sample.timepoint_h`, `Analysis.localization_threshold`,
   `Imputation.downshift_sd`, `width_sd`. `1.8` and `1.80` fork an id. **The `Analysis` qualifying-
   child fold (§3) depends on this rule**, since it folds two of these floats.

**Fallback keys are now forbidden outright (ADR-0021)**, so the builder never has to reconcile one:
an identifying field may be absent only when its absence is *determined by the data*, never when it
is *contingent on what was known at ingest*. §3 classifies every nullable identifying field, and
`tests/test_schema.py` rejects any marked `contingent` and any absence found in committed data but
left unclassified. `Software` now keys on `name` + `version` (the digest is non-identifying) and
`Person` identity comes from the curation export rather than an ingest-time inference — so the
builder can treat every identifying field as either present or determinedly null, with no
provisional state and no merge step.

Also outstanding from the same audit: `parameters_json`'s canonicalization is documented in §3 and
ADR-0020 but **implemented nowhere**, so today it behaves as open free text; and reference-key
components have their own canonical forms now fixed in `ONTOLOGY.md` §4 (Unimod-only modification
keys, unpadded `sv`, uppercase residue, lowercase CURIE prefix), checked against committed data but
not against an ingested change-set.

### Unenforced invariants (audit 2026-08-07), by class

The write-time change-set checks (I2, I3, I4, I10, I14, I15, I16, I19) and change-set structural
validation (ADR-0019) are enforced in `bzk/ontology/invariants.py`. The rest are not yet enforced;
grouped by *how* they must be enforced, so a source-tree lint is not mistaken for a data check.

- **CS — write-time change-set check, not written.** **I1** (disjointness: reject locally-authored
  reference–reference edges; ref–ref edges carry `source`). **I8** (also WG: every `Sample` reaches a
  curation `Analysis` via `SAMPLE_GENERATED_BY`). **The `EvidencedInference` contract itself
  (§6), unenforced in every clause.** §6 requires each subtype to carry `basis`, `confidence`,
  `rationale`, `asserted_at` / `retracted_at`, *and* an evidence edge to an `Analysis` or a
  `Publication`. Nothing checks any of it. `_check_confidence` (added 2026-08-07) validates the
  **value** of `confidence` when one is present and deliberately skips `None`, because presence is
  the contract's business and not that checker's — so an assignment with no `confidence` at all
  passes today. The same holds for the other required fields and for the evidence edge; the valid
  fixture's `bzk:ma1` has neither `ASSIGNMENT_SUPPORTED_BY` nor `ASSIGNMENT_CITES` and is accepted.
  A single contract check over the three subtypes would close all of it, and it is a pure
  change-set function, so it belongs here rather than at query time. See also §11 Q9, which asks
  whether the contract's evidence-edge clause is right in the first place — settle that before
  writing the check, or the check will enforce a clause the schema contradicts. **Residue agreement across `SITE_ON`** (completes
  I2, candidate new invariant): I2 pins the sequence version but never verifies the residue at the
  site's position matches its `SITE_ON` target's sequence — the write-time mirror of the resolver's
  `validate_position`. It belongs in the write-time set: it would catch a site keyed at one
  residue attached by `SITE_ON` to a sequence where that position is a different residue (the
  isoform-bug arithmetic, and exactly the malformed second `SITE_ON` the valid fixture now avoids).
  It needs the `ProteinSequence.sequence` present in the change-set, which the label check does not
  yet require, and it overlaps the resolver, so it is a graph-ingestion backstop rather than the
  first line. Build with the first adapter, not before. **Two further I2 clauses, both unenforced,
  both from ADR-0005:** (i) a site key's `sv` segment must equal its `SITE_ON` target's
  `sequence_version`; (ii) a `ProteinSequence`'s id must agree with its own `sequence_version` and
  with the accession of the `Protein` reached by `HAS_SEQUENCE`. Both are cheap string comparisons
  over the change-set — no sequence content needed — and sit in the same scope as the
  residue-agreement check above. **All three land together with the first adapter.** The valid
  fixture supplies the positive case for all three; the violating cases belong in
  `tests/test_invariants.py` as red cases, per the one-violation-per-invariant pattern.
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
  content-derived keys; ADR-0020 extends this from reference nodes to evidence nodes, so one key
  builder now serves both — I7 holds once that builder exists, which lands with the loader/adapters).
  **I17** (reviewed
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
