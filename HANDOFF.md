# HANDOFF.md — starting implementation

| Field | Value |
|---|---|
| Status | Active until week 2 is complete, then delete |
| Version | 1.32 |
| Last reviewed | 2026-08-10 |
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

Pin exactly, not with compatible-release specifiers. `OPERATIONS.md` §4.2 explains why for Kùzu specifically.

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

### Status, 2026-08-09 — read this first

**A fresh session should read this block, then `ROADMAP.md` § Measured findings, then start at
"The next action" below.** Everything above the line in this section is history; this is state.

**What runs today, end to end:**

```
uv sync --frozen                                        # build .venv (OPERATIONS.md 4.1)
.venv/bin/python -m bzk.sources.pride                   # fetch the deposit into the content store
.venv/bin/python -m bzk.sources.protein_groups          # fetch proteinGroups + the two BJC tables
.venv/bin/python -m bzk.rebuild                         # graph from the four I9 inputs
#   ^ drops the computed results; the differential below must follow it (OPERATIONS.md 5)
.venv/bin/python -m bzk.drift                           # validate the sequence archive, weekly
.venv/bin/python -m bzk.sources.pxd018299_differential  # the differential run and its populations
streamlit run bzk/ui/app.py                             # three panels over bzk/query/
```

**Corrected 2026-08-09 by rehearsing it from a cold clone.** Three of these lines were missing —
the install (nothing in the tree said `uv sync`), the `protein_groups` fetch, and the app — and the
rebuild's `~120 s` was a **warm-cache** figure carrying no such label: from an empty cache the same
command takes **37 m 14 s – 39 m 34 s** (`OPERATIONS.md` §5, where the timings live).

**Corrected again the same day, by the second rehearsal, and this one is the more instructive
failure.** Every line above began `python -m …`, which contradicts `OPERATIONS.md` §4.1's own
instruction — *`.venv/bin/python -m bzk.rebuild`, or `uv run python -m bzk.rebuild`* — one
cross-reference away, and nothing here said to activate the venv. **The way it fails is worse than
being plainly wrong: it is machine-dependent.** Run literally on this container, `python` resolves
to `/usr/local/bin/python`, **3.11.15**, with a user-site `requests` — so the first two lines
*succeeded*, wrote the right bytes to `~/.bzk-omics/raw/` under the wrong interpreter, and the run
failed three lines later at `ModuleNotFoundError: No module named 'kuzu'`. A reader following this
block gets two silent successes and then an error that points at a dependency rather than at the
interpreter. The flags on the last line are gone because `.streamlit/config.toml` now carries both
values (§4.1); the bare command is the documented one.

**The block is corrected and the class is not closed, which this says rather than leaves to be
inferred.** Three more imperative uses of a bare `python -m …` survive in this document — `:241`
(*run `python -m bzk.rebuild` and confirm it reports 2,029 sites*), `:316` (*run it with
`python -m bzk.sources.pxd018299_sites`*) and `:392` (*must run `python -m bzk.sources.pride`
first*) — and each fails the same way on a machine whose `python` is not the venv's. They are
**not** fixed here: the run that found this was a freeze rehearsal, and correcting the documented
run path was its remit while sweeping the document was not. The mentions that are *references*
rather than instructions — `README.md`'s Status row, `ROADMAP.md`'s instrument columns, this
document's dated records of what a past rebuild reported — are a different thing and are correct as
they stand.

**The graph** (rebuilt 2026-08-07, post-ADR-0024): 2,029 `SiteObservation`s each with a
`ModifierAssignment`, 2,029 `ModificationSite`s, 4,561 `Protein`s, 1,062 `ProteinSequence`s, 3
`Modifier`s, 12 `Sample`s, 2 `Analysis` (curation + ingestion), **0 `ProteinAssignment`** — see
§6.3, deliberately empty. 27 rows refused. Two independent replays reproduce **11,730 ids
identically** — the figure predates `Gene`, and a **third replay on 2026-08-09 from a clone with no
cache at all** reproduced **12,774** across twelve labels with symmetric difference **0** on eleven
of them. The twelfth is `Gene`, where five nodes did not come back; `ONTOLOGY.md` §4 records why,
and it is not UniProt.

**The sequence archive is drift-checked but the receipt no longer covers it** (2026-08-08 05:03 UTC,
2,845 sequences, 0 drifts, 34m30s — against **3,014** now). The archive grew on 2026-08-09 when
`resolve` began archiving the canonical sequence for accessions previously reached only as
isoforms, and `rebuild` correctly reports a changed set rather than staleness. Re-running `bzk
drift` is the weekly cadence's business (`OPERATIONS.md` §5), not a repair. And see §8: a
clean result over an archive whose oldest member is thirteen hours old is not evidence the
sequences are stable, and re-running it today would not make it one. The receipt lives at
`~/.bzk-omics/cache/uniprot/.drift`, outside the repository, so a session on a fresh machine starts
with no receipt at all and `rebuild` will correctly say the archive has *never* been checked.

**Slice 4b's result: 12 of 14 published targets, which is *not* the notebook's twelve.** Both routes
miss PSMB9; this one recovers ADAR (the notebook found it below threshold) and loses OAS1 (two
canonical reviewed candidates, so ADR-0024 rule 3 declines to promote and the razor pick fails the
residue check). Populations differ by 13 sites. `ROADMAP.md` § Validity-conditional promotion is
authoritative; **do not quote 12 of 14 as a reproduction.**

**Schema is 57 tables** (24 node + 33 rel) since ADR-0023 dropped two duplicates.

**`Gene` and `ENCODES` are minted — 1,039 genes, 1,054 edges, 2026-08-09.** Every `Protein`
without one carries `gene_absence` saying which of three absences it is (§4): **3,492 unresolved**
— the site adapter resolves only razor picks — **10 no_cross_reference**, 0 `not_captured`. That
partition is enforced at the change-set by `invariants._check_gene_absence`, written because the
first build put 3,492 proteins in the graph with a NULL column and a green suite. Target symbols
are now answerable from stored content: **12 of 14** by exact match, **13** counting `DDX58`, which
HGNC renamed and the graph holds as `RIGI` at `hgnc:HGNC:19102`. `OAS1` is genuinely absent — its
only `Protein` here is `H0YI20`, a TrEMBL fragment. **This is identifiability, not recovery**, and
no differential was run.

#### What is left of ROADMAP's v0.1 exit

The criterion was amended 2026-08-07 — it is no longer a number, it is *population reported at every
step, divergence accounted for exactly, every miss traced*. That part is met. Three things are not:

1. **`perseus_s0` is unwritten.** `ARCHITECTURE.md` §4 makes it **default and required**; only
   `welch_t` (the sanity check) exists, and §4 is explicit the two are not interchangeable — the
   `s0` curvature changes which sites pass. Needs permutation FDR too, which is also unwritten.
   Its recovery number is a **separate baseline** and will not necessarily be 12.
2. ~~**Gene symbols never enter the graph.**~~ **Closed 2026-08-09.** `Gene` holds 1,039 nodes and
   the 14 targets are answerable from stored content. `Protein.name` is still null on all 4,561 and
   stays so by decision (§4) — the symbol's home is `Gene.symbol`. What remains on the differential
   side is that `bzk/sources/pxd018299_differential.py` still reads the deposit's `Gene names`
   column: the graph can now answer it, and switching the module over is a change to the
   differential, which this turn did not run and does not touch.

   **Decided 2026-08-08 and no longer open as a modelling question**: the symbol's home is `Gene.symbol`, not `Protein.name` — routing it onto `Protein` would make `Gene.symbol` redundant (ONTOLOGY.md §4).

   **Minted 2026-08-09 (§11 Q12, closed).** 1,039 `Gene`, 1,054 `ENCODES`. The pre-registered projection was 1,104 and 3,230 and was wrong in an instructive way: it assumed every graph `Protein` passes through the resolver, and only the ~1,069 razor picks do. So `Gene` answers *which of the 14 targets* from stored content — 12 by exact symbol, 13 once `DDX58`/`RIGI` is allowed for — while 3,492 proteins carry `gene_absence = 'unresolved'`, which is the adapter's resolution policy and not a fact about them.
3. ~~**I11 is unmet.**~~ **met 2026-08-08 for `SiteObservation` **only**** — `bzk/quant/`, ADR-0004 and ADR-0013; `ProteinObservation` retains nothing, see below. `quant.duckdb` is created by `rebuild`, `quant_ref` is `site_values` on all 2,029 `SiteObservation`s, and **48,696 measured-or-null cells** are retained (2,029 sites × 12 samples × 2 quantities). The matrix is no longer
   re-read from the deposit each run, and the statistics layer is pluggable in fact rather than in
   principle: an alternative test is recomputable from stored values. Values are **measured and
   null, pre-imputation** (ADR-0013), so the imputation mask stays reconstructible from a seeded
   `Imputation` rather than lost to `n_imputed`'s count.

Of the three, **(3) blocks the most**: recomputation and the comparison capability
(`ARCHITECTURE.md` §4's stated purpose for the registry) both need a retained matrix, and (1) is
worth little without it since the point of a second test is running it over the same values.

#### The next action

~~**Write the DuckDB quantitative layer (I11).**~~ **Done 2026-08-08.** `bzk/quant/store.py`,
`quant_ref` populated by the adapter, `quant.duckdb` created by `rebuild`.

**This block was two revisions stale on gene symbols and is corrected 2026-08-09, independently of
the read path.** It said gene symbols had a settled *modelling* half with *"only the cache question
(§11 Q12) open"*. Q12 was answered on 2026-08-09 and `Gene` was minted the same day — 1,039 nodes,
1,054 `ENCODES` edges, three named absence states. **One of the three remains: `perseus_s0` over the
retained matrix**, which waits on the meeting.

~~**Nothing reads the graph.**~~ ~~**The query half landed; the interface is unbuilt.**~~
**Both landed 2026-08-09.** `bzk/query/` answers five questions over Kùzu and `bzk/ui/app.py` is
the minimal Streamlit interface over it: three panels, `streamlit run bzk/ui/app.py`. The notebooks
are untouched and still read the deposit rather than Kùzu.

**The demo was rehearsed from a cold clone on 2026-08-09 and the tree did not survive it intact.**
Nothing was built; six things were found, and the order matters because the first three are the ones
that would have run out the clock in front of a real audience. **(1)** No install procedure existed
anywhere — `OPERATIONS.md` §4.1 now has one. **(2)** `bzk rebuild` from an empty cache takes **37
minutes**, not the two the tree implied. **(3)** With no `raw/` it exits **0** over an empty graph.
**(4)** The graph reproduced id-for-id except five `Gene` nodes that no committed code can produce
(`ONTOLOGY.md` §4). **(5)** The app is served on every interface by default and reports usage
statistics, both contradicting claims made two commits earlier. **(6)** Over an empty graph the gene
panel says *"Present but unattributable"* — an assertion about content that is not there. Four
of the six are documentation and are corrected; **(3)** and **(6)** are code and are in §8. A **seventh** came from the closing checks rather than the clone and is fixed here: `test_tautology_sweep.py`'s mutation harness copied `__pycache__` into its temporary tree and so could run **stale bytecode instead of the source it had just mutated** — the classifier for every assertion in the sweep, able to report a result it had not computed. `ROADMAP.md` § *Measured findings* has the demonstration.

**Rehearsed a second time on 2026-08-09, as a freeze run, and it found one thing.** The graph and
the whole UniProt cache reproduced from nothing **exactly** — 12,769 ids over twelve labels,
symmetric difference 0, every sequence byte-identical, every pin identical, 7 `AMBIGUOUS` both
times, `fetched_at` the only field that moved. That is the evidence the histone explanation
predicted and could not supply on its own (`ONTOLOGY.md` §8 I9). The one finding is in this
section: **every line of the block above began `python -m …`**, which contradicts `OPERATIONS.md`
§4.1, and on a container with a system `python` and a user-site `requests` the first two lines
succeed under **3.11.15** before the third fails on `kuzu`. Corrected above. The cold wall clock
became a range — 37 m 14 s – 39 m 34 s, *n* = 2 — with the fetch count reproducing exactly at
5,273; §5 carries both.

**The eight queued ADRs are written, 2026-08-09.** 0006–0012 and 0014, completing `ROADMAP.md`
§ *Weeks 7–8*'s *"ADRs 0004–0014 written"*; **0018 is the only reserved number left**. Five land
`Proposed` and three `Superseded` — none `Accepted`, for the reason `decisions/README.md` now
records. Two things surfaced while writing them and neither is fixed here. **`ARCHITECTURE.md` §5's
seed for 0007 was wrong** — it read *local moderated t-test over an R dependency*, which ADR-0015's
account contradicts and which makes the 0007→0011 supersession incoherent; the seed is marked wrong
in place and the evidence is in the record. **Both enumerations of reserved numbers were stale** —
`decisions/README.md` listed 0004 and 0013 as queued after they were written, and omitted 0018,
which the seed list reserves. Reconciled. Nothing checks the three enumerations against each other,
which is the standing item this does not close.

**The graph holds computed results, 2026-08-09.** `python -m bzk.sources.pxd018299_differential`
writes what it computes: **1,362** `DifferentialResult`s under one `Analysis`
(`kind = 'processing'`, `parameters_observed = true`, `welch_t` with BH), one `Contrast`, one
`Imputation`. `query.differential_table` returns rows instead of `NOT_STORED`, and the two analyses
that produced nothing moved `NOT_STORED` → `NONE_FOUND` without their own state changing — the
transition an absence value exists for. No id moved. **`bzk/analysis/` is a fourth layer**, argued
in `ARCHITECTURE.md` §3 rather than filed under the layer nearest to hand. Three things this did
not change and one it did not touch: `substantially_imputed` is still `None` because I15's
denominator is per-sample in `quant.duckdb`; refusals are still `NOT_RETAINED`; `gene_symbols` is
still 12 of 14; and §11 Q1's `Contrast` placement is not forced by one analysis over one dataset.
`perseus_s0` still waits on the meeting, so the second baseline and its own recovery number do not
exist yet.

**Refusals: asked, answered no, and nothing stored — 2026-08-09.** A refusal is **not an entity**.
It has no id by construction; `evidence_id` refuses a label §3 does not carry; `unprovenanced`
iterates §7's `prov:Entity` list, so a `Refusal` node would sit outside the only invariant the read
layer enforces; and §7 opens *provenance is a mapping, not a log*. ADR-0004's rule puts a
per-input-row fact in the columnar store, which `bzk/query/` does not reach — so storing it there
moves the gap rather than closing it. `query.refusals` still answers `NOT_RETAINED`, which is now
**the only live case that value has**, and `tests/test_adapters_base.py` pins the absence so the
next person re-opens the argument instead of discovering a hole.

**The MaxQuant protein adapter is written and the ingestion is not — 2026-08-10.**
`bzk/adapters/maxquant_protein_groups.py`, 27 tests, six guards each made to fail. Run offline over
`HAP1_USP18KO_proteinGroups.txt` it emits **4,797** `ProteinObservation` over **23,807** `Protein`,
0 refusals, **67,158** cells, in 0.726 s — every pre-registered figure exact. **Nothing was
written**, and that was registered before the code existed: the file's fourteen quantitative columns
are the *proteome* run (`WT_P_2hGradient1`, `KO_INF_P_2hGradient2`, …) and the curation record's
twelve `Sample`s are the *diGly* run, sharing no member, so there is no `Sample` to key a cell to.
Minting fourteen from the column names is what I8 forbids, and the mapping is not deducible even
with §5.3's `filename_inference` basis — KO/none has five columns for three replicates, three of
them naming replicate 1, one at a different injection volume. **So I11's protein half is still
unmet, and the blocker moved from the pipeline to the deposit's sample mapping.**

Three things the turn found rather than built. **I14's second half does fire at protein grain**,
which the pre-registration's own probe had measured as *no invariant fires here* — it removed the
edges entirely, and I14 only fires on a strict non-empty subset. **`iBAQ` has no columns in this
file**, contradicting a measurement recorded the day before. And **a reported `0` is 39.8% of this
matrix**; the first draft folded it to null, which `maxquant_sites.py` had already refused to do, so
the value reader moved to `maxquant.cell_value` and `sample_nodes` to `adapters/base.py` — two
conventions that had been one home short. `ROADMAP.md` § *Outcome: the MaxQuant protein adapter*
carries all of it.

**The enumeration is the more useful half, and it found three kinds where the model had one.**
Declared-filter drops (43 decoys and contaminants, 242 localisation, 667 presence rule) are a
threshold's effect and belong to `filters_applied`; keying failures are the 27, behind which sit 7
accessions the resolver could not key; unreadable input is `perseus.py`'s four `PerseusError`
raises, which produce no `Refusal` at all and do not contradict `base.py` — *deliberately not an
exception* is about rows. **One premise corrected on the way**: the resolver's failures are **7**,
not `gene_absence`'s 3,492, which are candidates the adapter never sends to it.

**And confirming the state found something bigger than the question.** `bzk rebuild` **drops the
1,362 `DifferentialResult`s and does not regenerate them** — they come from a second command. The
pair reproduces the graph exactly (14,134 ids, every per-label set identical), so I9 holds; what was
false is `OPERATIONS.md` §5's sentence about what one command reconstructs, corrected there, and the
order in §3's block above is now load-bearing rather than a convenience.

**Two things the interface established rather than assumed.** Kùzu takes a single writer lock, so
the app **cannot read the graph while `bzk rebuild` holds it** — `query.connect` raises
`IO exception: Could not set lock on file`, verified 25 s into a running rebuild, and the app
renders that state rather than a traceback or a silent retry. And **I18's EX trigger did not fire**:
§8 I18 says *"queries and views within the local instance are unrestricted"*, a screen is such a
view, and there is no download button — one would fire it, and a test asserts its absence. That
reading holds only while the app is served locally, which the entry does not say and this does.

**Corrected 2026-08-09: it is not served locally by default, so the condition the reading rests on
was unmet from the day it was written.** Bare `streamlit run` binds **`0.0.0.0`** and prints a
Network URL and an External URL — observed in the server's own log, `Uvicorn server started on
0.0.0.0:8599`. The condition was stated and never checked, in the same block that congratulated
itself on stating it. `OPERATIONS.md` §4.1 now carries the two flags that make it true, and the
same run found the second default: Streamlit reports *"Collecting usage statistics"* unless told
not to, in a project whose first word is local-first. Neither is fixed in the repository — a
`.streamlit/config.toml` is the right fix and is §8's.

**One read-layer gap reported and deliberately not closed.** A caller cannot ask whether an absent
symbol's locus is present under another name: `DDX58` returns `UNATTRIBUTABLE` while `RIGI` is
present at `hgnc:HGNC:19102`, and nothing joins them. The UI shows both and links neither, because
making the comparison for the reader would assert a synonymy the graph does not hold. **Whether the
read layer should offer that comparison is open**; the renderer is the wrong place to decide it.

**One gap found and closed, and the way it was found is the point.** `bzk/ui/` may import
`bzk.query` and nothing else from `bzk/`. The first panel written against that rule needed a list
of site ids for a selector, which the read layer did not expose, and the first draft reached for a
`MATCH` in the renderer — exactly the leak the rule exists to catch. `query.site_ids` and
`query.analysis_ids` were added to the read layer instead. A test parses every import in
`bzk/ui/*.py` and fails on `kuzu` or on any `bzk` import outside `bzk.query` / `bzk.ui`.

**Corrected 2026-08-09: this block implied that what remains waits on the meeting, and one item does
not.** `perseus_s0` does. **Running the Perseus adapter on a real export does not**, and it was
attempted the same day. It is blocked on the artefact rather than on a decision: the two published
BJC supplementary tables are Perseus exports *of the annotation matrix* and carry **no
`Student's T-test Difference` and no p-value column**, so they cannot mint a `DifferentialResult`
however they are ingested. Established by measurement, not by reading headers — which is what the
2026-08-07 survey did, and why it recorded these as *the exact artefact in question*. The adapter's
protein-group handling, which that survey named as the blocker, was discharged by ADR-0022 and is
no longer one. `ROADMAP.md` § *Step 0 stopped the BJC ingestion* holds the digests, the column
inventory and three further findings about the files.

**Also corrected: `bzk/adapters/perseus.py` is still fixture-only**, so `differential_table`
returns `Absence.NOT_STORED` with nothing behind it, and the four measured-state claims in
`bzk/query/` — 0 `DifferentialResult`, 0 `Imputation`, and the `unprovenanced` dict — **all still
hold**, re-measured 2026-08-09 after the attempt. They were expected to move and did not.

Before starting, run `python -m bzk.rebuild` and confirm it reports 2,029 sites; if it does not, the
deposit or the archive has moved and that is the finding, not a setup problem.

**Two habits this project runs on, both learned the hard way and both cheap to lose:**

- **Before quoting any number, ask what would have had to be different for it to come out
  otherwise.** Three self-confirming measurements were caught here (§8); the fourth will not
  announce itself.
- **Pre-register anything that could move a headline figure.** Write down what each outcome would
  mean *before* running it. `ROADMAP.md` § Pre-registration is the worked example, and it is what
  stopped 12-of-14 being reported as a reproduction.

---

**The next action is documents, in this exact order — three separate turns:**

1. ~~**ONTOLOGY v1.3 — add `RESULT_FOR_PROTEIN`.**~~ **Done 2026-08-07.** `DifferentialResult → ProteinObservation` (`MANY_ONE`) added to §5 DDL and `schema.py` `REL_TABLES`; schema is now 57 tables (was 56); `tests/test_schema.py` and `tests/test_rebuild.py` green. **The next action is item 2.**
2. ~~**ADR-0020 + `ONTOLOGY.md` §3/§9 id amendment.**~~ **Done 2026-08-07.** ADR-0020 written; §3 id scheme and the §5.1 contract row amended, §9 worked example restubbed to content-derived digests (ONTOLOGY v1.4). Direction unchanged (decision (a)); form chosen is an opaque `bzk:`+truncated-SHA-256 digest over a canonical identity tuple. The key **builder** itself is code and lands with item 3 / the adapters (I7 CON). Follow-ups 2026-08-07: §3 now carries a **per-label identity table** (identifying fields + anchors per evidence node type — the builder mirrors it, not the reverse), and OPERATIONS §2 a **retraction-record format** (retracted id, `retracted_at`, reason) so retraction survives rebuild under I6. Correction 2026-08-07: the §3 identity table surfaced a pre-existing DDL/ARCHITECTURE contradiction — `test` / `fdr_method` were on `DifferentialResult` but ARCHITECTURE §4 records them on `Analysis`; both columns moved to `Analysis` (ONTOLOGY v1.6, ARCHITECTURE v1.1), `s0` stays in `parameters_json` (canonicalized before hashing), and `tests/test_schema.py` now guards the §3 table — extended 2026-08-07 to cover **reference** nodes too (every DDL node table has exactly one row), to check anchor **edge direction** against the DDL rather than the name alone, to parse the §4 **key templates**, and to check reference ids on disk against §4's canonicalization (Unimod-only modification keys, unpadded `sv`, uppercase residue, lowercase CURIE prefix). Follow-on 2026-08-07: the converse (completeness) check found `Analysis` omitting `basis`/`confidence` from identity — the I8 curation-collision — now added; §3 gained an `Excluded columns` column so the guard enforces a full partition of every evidence node's columns (identifying ∪ excluded == columns), ONTOLOGY v1.7. **Item 3 followed and is done; the next action is `bzk/adapters/perseus.py`.**
3. ~~**The curation loader**~~ **Written 2026-08-07** — `bzk/curation/loader.py`, reading `data/curation/*.json` in the shape those files already have. Emits `Project → Experiment → Sample` plus the `Dataset` and the §5.3 curation `Analysis`, keyed through `bzk/ontology/keys.py`, validated against `invariants.validate` before it returns, and handed to an adapter as a `SampleMapping`. Both §8 loader defaults are applied (`parameters_observed = true`; no `Contrast` materialised). `bzk/adapters/perseus.py` is now the next action (Weeks 3–4 below).

   **`data/curation/curation_PXD018299.json` loads. 2026-08-07 — every blocker below is closed.** The loader refused it with eight named items on the day it was written: the two titles, plus `Sample.timepoint_h` on the six unstimulated samples. The six cleared later that day by defining what the column measures (ONTOLOGY v1.17, blocker 3), and the curator supplied the titles. What comes out:

   | | |
   |---|---|
   | Nodes | **16** — 1 `Project`, 1 `Experiment`, 1 `Dataset`, 1 `Analysis` (`kind = 'curation'`), 12 `Sample` |
   | Edges | **38** — 1 `CONTAINS`, 12 `PERFORMED_ON`, 12 `PRODUCED`, 12 `SAMPLE_GENERATED_BY`, 1 `USED` |
   | `Project` | `bzk:7db0223c881d950dfc3589acbdc80347` |
   | `Experiment` | `bzk:222c1d19e977939d440f321823de5b94` |
   | `Dataset` | `bzk:6508668c392a6a03b509922209e73508` |
   | `Analysis` | `bzk:bc90e3eb515d6edd1351ce25ecd33209` |
   | `Sample` (WT_1) | `bzk:9924d6d24941af0f1b64171e0b550e76` |
   | `Sample` (WT_2) | `bzk:7b2ed3b2751c3364da982151935c9845` |
   | `invariants.validate` | accepts |

   All twelve `Sample` ids distinct. The six `treatment = 'none'` samples key with a null `timepoint_h`, which is the §3 determined absence working rather than being tolerated. No `Contrast`, `Publication` or `Person` node — the first is deferred to the adapter (§11 Q1), the second because the record cites its DOI only in prose, the third because `curated_by` is null and a nameless `Person` cannot be keyed.

   **The refusal path moved off this record when it stopped refusing.** Five tests asserted the refusal and failed the moment the titles arrived — correctly, but a guard resting on real data being *incomplete* stops guarding once the curator completes it. `tests/fixtures/curation_synthetic_pending.json` is now the loadable fixture's incomplete twin, and `tests/test_schema.py`'s pending-marker guard scans `tests/fixtures/` as well, since the last real marker in the repository disappeared with the titles.

4. ~~**`bzk/adapters/perseus.py`**~~ **Written 2026-08-07.** The first adapter, and the first code to satisfy `ObservationAdapter`. Protein grain, per ARCHITECTURE §3's *"a flat file of proteins, differences and significance values"* — so `ProteinObservation` → `Protein`, no `ModificationSite`, no `ProteinSequence`, no sequence version and therefore **no network call in the ingestion path**. Emits `Dataset` (keyed on the result table's own digest), an `Analysis` with `kind = 'external'` / `parameters_observed = false`, its `Imputation`, one `Contrast` per declared contrast, and a `Protein` / `ProteinObservation` / `DifferentialResult` per row; re-stages the `SampleMapping`'s `Sample` nodes so the batch is self-contained (ADR-0019) and validates before returning. Declared parameters are constructor arguments so `parse(file, mapping)` keeps the protocol signature — see ARCHITECTURE §3.

   **Unvalidated against real input, and that is the whole of what is left.** No Perseus export from the group exists; every fixture is synthetic. Three hazards are handled and each is mutation-tested: Perseus' default `-Log Student's T-test p-value` column (read raw, 4.51 means "not significant" where 3.09e-05 is meant — `HANDOFF.md` §6's wrong-column class exactly); CRLF; and protein groups, which the adapter **refuses** rather than razor-picking (see §8). The next action is `bzk/adapters/maxquant.py` and the DuckDB quantitative layer (Weeks 5–6 below).

5. **The next action: get the first real `Observation` into the graph.** Everything upstream of it
   now exists — the loader, the store, a non-vacuous rebuild, an adapter that no longer refuses the
   common row, and ADR-0022's identity change that unblocked it. Nothing has ever stored an
   `Observation` of either kind.

   **Route, and why this one.** Not `perseus.py`: it is ready, but no Perseus export from the group
   exists and the two BJC supplementary tables are published *results* rather than this
   laboratory's own file — ingesting them would put someone else's summary in the graph as though
   it were the anchor laboratory's data. The route is the **site grain**, through
   `HAP1_USP18KO_GlyGlyKSites.txt`, which is on disk, content-addressed, and already re-derived
   end to end by `bzk/sources/pxd018299_baseline.py`. ADR-0022's site half is what makes it
   possible: `SiteObservation.candidate_proteins` means a site keyed from an 82%-multi-mapping
   table no longer needs a razor pick to have an id.

   **Slices 0 and 1 are done (2026-08-07).**

   *Slice 0* — `SiteObservation.peptide_sequence` is no longer identifying (ONTOLOGY v1.19, §3).
   The deposit has **no peptide-level file** — 36 `.raw`, 3 `.txt`, 1 `.xlsx`, and the GlyGly table's
   only sequence column is `Sequence window`, a 31-mer of the *protein* — so the value had no source
   and its absence would have been contingent under ADR-0021. It is not needed: a site table is one
   row per site, and `Dataset` + `ModificationSite` + `candidate_proteins` separates every row the
   source can produce. Peptidoform discrimination stays §11 Q4's.

   *Slice 1* — `bzk/resolve/nodes.py`. Accessions to `Protein` + `ProteinSequence` + `HAS_SEQUENCE`
   (ADR-0005), injected on the adapter's constructor so `parse(file, mapping)` keeps its signature,
   de-duplicated (4,815 distinct accessions across the filtered table, 1,335 of them isoforms), and
   entirely offline-testable. Unresolved accessions are reported, not raised — the adapter decides
   whether a dead accession sinks a site. `residue_at` is the hook Slice 2's measurement needs.

   **Slice 2 is done (2026-08-07)** — `bzk/adapters/maxquant_sites.py`, the first search-output
   adapter, with `resolve_to_nodes` injected on its constructor. `Proteins` and `Positions within
   proteins` are index-aligned on all 2,056 rows, and `Position` agrees with the aligned entry on
   2,055 of 2,055 where the razor pick is in the list, so the pairs are read rather than inferred.
   Run it with `python -m bzk.sources.pxd018299_sites` (needs `python -m bzk.sources.pride` first;
   ~1,050 UniProt lookups on a cold cache, minutes, then cached).

   **The measurement the slice existed for: 40 of 2,056 sites (1.9%) fail the residue check** and
   are refused — full breakdown in `ROADMAP.md` § Sequence drift. Two things worth carrying
   forward. First, the prior ~114-of-2,298 estimate was **3× high and measuring a different
   quantity**: it counted *sequences amended*, which bounds *sites broken* rather than estimating
   it, since a sequence can be amended without moving any particular lysine. Second, drift is
   **2.8× likelier on unreviewed entries** (2.5% vs 0.9%), and all 25 accessions whose UniProt
   entry has been deleted outright are unreviewed — so I17's *reviewed preferred* is not only about
   naming a better identifier, it is about picking the one that still resolves in five years.

   Refusals are returned rather than logged: `ParsedObservations.refusals`, defaulting to empty so
   `perseus.py` is unaffected. That channel *is* how the measurement exists — a `logging.warning`
   would have left it uncountable.

   **Slice 3 is done (2026-08-07).** `bzk/ontology/seed.py` turns `schema.GG_REMNANT_MODIFIERS`
   into the three `Modifier` nodes — the set's one home now also carries `c_terminal_motif`, the
   mature C-terminus, so the column and the membership argument do not drift apart. Every
   `SiteObservation` gets a `ModifierAssignment` with `basis = 'inferred_default'`,
   `confidence = 'ambiguous'` and the three-member candidate set, and **no `ASSIGNS` edge**: I3
   forbids an ambiguous assignment naming a modifier, and that refusal is the product. On the real
   file: 1,967 sites, 1,967 assignments, 3 modifiers, 0 `ASSIGNS`.

   **§6.1's every-observation-has-an-assignment rule is now enforced, not conventional.** It is the
   under-claiming half of I3, written before the adapter emitted anything and failing on all ten
   adapter tests until it did. A site with no assignment is not a *cautious* site — nothing
   downstream can tell "not assigned yet" from "assigned, ambiguous", and the first reads as an
   omission inviting someone to assume ubiquitin. Scoped to the change-set, which means a producer
   re-staging a `SiteObservation` must re-stage its assignment; that is stricter than I2's residue
   clause, which skips, and the checker's docstring says why the two differ.

   **Slice 4a is done (2026-08-07)** — the adapter is wired into `replay_ingestion` beside the
   loader. Each curation record names its deposit by `content_hash`; where those bytes are in the
   content store, the record's `SampleMapping` and the file go through the adapter that sniffs it.
   The curation record is written **first**, and that ordering is load-bearing: both key `Dataset`
   on `content_hash` — the loader from the record, the adapter by hashing the bytes — so their ids
   converge (I7) and every site hangs off the dataset the curation describes. Asserted, not assumed.

   **The graph, as of the 2026-08-07 rebuild after ADR-0024 (`python -m bzk.rebuild`):** 2,029
   `SiteObservation`s, 27 refused, **11,730 nodes and 9,217 edges in the graph** — corrected
   2026-08-08 from 11,743 and 9,229, which are the *statements issued* (`nodes_staged`), 13 nodes
   and 12 edges higher because the adapter re-stages the `Dataset`, the 12 `Sample`s and their
   `PRODUCED` edges as ADR-0019 requires — and **no `ProteinAssignment` at
   all** — ADR-0024 removed `reviewed_preferred` from that basis enum, so the 522 promotions are
   recorded as `keying_basis` / `displaced_protein` on the observations instead. Two independent
   replays reproduce **11,730 ids identically**, re-run against the post-I17 keying rather than
   carried over. The paragraph below describes the superseded pre-ADR-0024 state.

   **Superseded — the graph after I17 and before ADR-0024:** 2,025
   `SiteObservation`s with 2,025 `ModifierAssignment`s and 2,025 `ModificationSite`s, 522
   `ProteinAssignment`s (the I17 promotions that survived to a site — 526 were computed, and the
   four whose promoted entry failed the residue check produced no site), 4,558 `Protein`s, 1,063
   `ProteinSequence`s, 3 `Modifier`s, 12 `Sample`s, **2** `Analysis` (curation and ingestion), and
   one each of `Project` / `Experiment` / `Dataset`. Before I17 it held 1,967 sites and 11,389 ids
   reproduced across two independent replays; the reproducibility check has not been re-run against
   the new keying.

   The rebuild also exercised the drift receipt's archive digest against real data for the first
   time: I17's extra resolutions grew the archive from 1,029 to 2,845 sequences, and the staleness
   line correctly reported *"last drift-checked 0 day(s) ago over a DIFFERENT set (1,029 then,
   2,845 now)"* rather than the flattering "0 days ago". That is the guard doing exactly what it
   was written for — a fresh timestamp over a stale scope. **Cleared 2026-08-08** by a full check
   over all 2,845 (34m30s, 0 drifts); the line now reads *"drift-checked 0 day(s) ago over 2,845
   sequence(s), 0 drift(s)"*.

   **The ingested population is 1,967, and it is not the notebook's 1,375 nor the file's 2,341.**
   2,341 rows → 43 decoys and contaminants → 242 below the localisation threshold → 2,056
   considered → 89 refused (40 residue drift, 48 unresolvable proteins, 1 no razor pick) → 1,967.
   Any comparison against the notebook is between two different populations and must say so.

   **Slice 4b** — the statistics path and the 12-of-14 re-derivation through the graph. Not started;
   ROADMAP's v0.1 exit criterion.

*Only then* the Weeks 5–6 work below.

**`raw/` does not persist across containers.** It lives under `~/.bzk-omics/` and is gitignored (`ARCHITECTURE.md` §2), so any session that needs the PXD018299 site table must run `python -m bzk.sources.pride` first — the fetch is idempotent and rewrites nothing if the bytes are already there. The durable link is the `content_hash` the three `data/curation/` records cite (`sha256:a4a503e3…`), not the file: it is what lets a session confirm it is working against the same bytes the curation was written for. A session that skips the fetch discovers this by failing. Re-fetched on a second, empty container 2026-08-07 and the digest reproduced byte-for-byte (2,759,052 bytes) — the deposit is stable at that URL, so a hash mismatch should be read as a revised deposit or a truncated download, not as normal drift.

### Weeks 1–2

**`tests/test_invariants.py` first, and failing.** One case per invariant that can be checked at write time — I2, I3, I4, I10, I14, I15, I16, I19. Each constructs a violating node and asserts the write is rejected. Write these before the schema exists; they will fail to import, which is correct.

**`bzk/ontology/schema.py`** — generate the Kùzu DDL from `ONTOLOGY.md` §4–6 rather than hand-writing it. A dict of node and edge definitions that emits Cypher. This is what makes a field rename a regeneration instead of a search across the codebase.

**`bzk/resolve/uniprot.py`** — port from `colab_identityresolution.ipynb` Steps 4 and 5 (the isoform-aware version, validated 20/20). **Not a verbatim port**, and the module docstring says so: two deliberate changes beyond adding the cache. (1) The `sequence_source` guard moves into the module — an isoform whose sequence cannot be fetched returns *no* sequence rather than the canonical one, so a caller cannot accidentally validate an isoform position against the canonical sequence (the notebook was safe only because Step 5 checked `sequence_source` first). (2) The persistent cache under `~/.bzk-omics/cache/uniprot/` is two-tier: entry metadata keyed on the base accession, sequence keyed on `accession#isoform#sv` and immutable — the immutable key needs the sequence version, which is only known after the entry fetch. Retention policy in `OPERATIONS.md` §3.

**`bzk/rebuild.py`** — drops and reconstructs from `raw/` plus the curation export. Written now, not later. I9 was an assumption until this ran *with content*, which it first did on 2026-08-07.

*Done when:* twenty accessions resolve and validate; a mismatched position fails loudly; the graph drops and recreates its schema. **All met, and "rebuilds without loss" stopped being vacuous on 2026-08-07** — for a whole week it was true only because the graph was empty. The curation loader, not an adapter, is what discharged it: `replay_ingestion` loads `data/curation/`, `bzk/ontology/store.py` writes it, and `tests/test_rebuild.py` rebuilds twice and compares ids. **It is discharged for curation content only.** No `Observation` has ever been stored, so "no observations in the graph to lose" is still literally true — what changed is that there is now something to lose and losing it fails a test.

### Weeks 3–4

**`bzk/adapters/base.py`** then **`perseus.py`**. Signature is `(file, SampleMapping) -> ParsedObservations`, never a directory convention. `Analysis.kind = 'external'`, `parameters_observed = false`.

**Curation ingestion** — `data/curation/curation_PXD018299.json` is the fixture and the format. It was written by hand; the loader should accept exactly that shape.

*Done when:* a Perseus table is ingested, resolved, stored, and cross-queried against a second dataset.

### Weeks 5–6

**`bzk/adapters/maxquant.py`** — port the filtering logic from `colab_seethedata.ipynb` Step 7 and `colab_reproducefigure.ipynb` Steps 2–4.

**`bzk/quant/`** — DuckDB layer, I11. Written 2026-08-08 (ADR-0004, ADR-0013): `store.py` holds the two matrices, keyed `(observation_id, sample_id, quantity)`.

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
| ~~**Curation record carries no `content_hash`**~~ **Resolved 2026-08-07** (f4c0865) | `data/curation/*.json`, `OPERATIONS.md` §2 | Every record under `data/curation/` identified its input by bare filename with no checksum, so I9 replay could not confirm it was running against the bytes the curation was written for — *"two deposits, or a re-download after a deposit is revised, can share a name and differ in content"* (`OPERATIONS.md` §2). All three records now carry `sha256:a4a503e3…`, back-filled once `bzk/sources/pride.py` had the input in hand, and `tests/test_curation_content_hash.py` guards them against `bzk.sources.pride.PXD018299_SITES` as the single home rather than against each other — so a partial back-fill fails rather than ties. The guard discovers citers from disk across `data/curation/` and `tests/fixtures/`, so a fifth record cannot go unchecked. Resolved || **`colab_reproducefigure.ipynb` cell 16 is a second test → a second `Analysis` (I16)** | statistics layer, weeks 5–6 | Cell 16 adds an `adj_p_moderated` column: a *second* significance test (moderated *t*) computed on the same matrix as the primary welch_t. Under I16 each declared quantity/test is its own `Analysis`, so `res` carries the outputs of **two** analyses, not one — the per-site table does not end at `n_candidate_proteins` as an earlier note implied. The adapter (or the notebook reconstruction) must emit two `Analysis` nodes and route each result column to its own. No — surfaces when that table is ingested |
| **Statistics-registry default vs on-disk baseline — ordering question** | `HANDOFF.md` §5, statistics layer | ADR-0015 makes `perseus_s0` the **default and required** registry entry (from author correspondence). But the 12-of-14 regression on disk was measured under `welch_t` + BH, and the only per-site result the group has produced (`colab_reproducefigure.ipynb`) is also welch_t. So the *validated-on-disk* method and the *default* method differ. §5 already fixes the build order (welch_t first, reproduce 12-of-14, then `perseus_s0` as a second baseline); the open question is which becomes the registry default the first adapter writes, and whether the two baselines are recorded side by side before that is decided. Keep measured (welch_t, on disk) and reasoned (perseus_s0, from correspondence) distinct — ADR-0015's own discipline. No — settle when the statistics layer lands |
| Multi-modified peptides | `ONTOLOGY.md` §11 Q3 | Possibly — will surface on first MaxQuant ingestion |
| **I17 `reviewed_preferred` promotion — scope corrected 2026-08-07** | `ProteinAssignment` construction in `adapters/` | **Correction, same day, to a decision made earlier the same day.** The row read: *"the Perseus (analysis-output) adapter has no candidate sets or razor picks (ARCHITECTURE §3), so I17 does not apply there"*. The reasoning was sound and the premise was false — `Majority protein IDs` **is** a candidate set, it is MaxQuant's own pick, and 72–77% of rows carry one (ROADMAP § Protein-group ambiguity). ARCHITECTURE §3's *"no localisation or razor-pick complexity"* was the same premise and is right about localisation only. **I17 does reach the analysis-output adapter.** What it cannot yet do there is act: promoting a reviewed entry over a TrEMBL one needs review status per member, which is a resolver run, and recording the promotion needs the subset-narrowing shape the row above says is missing. The promotion of a reviewed Swiss-Prot entry over a TrEMBL razor pick belongs to the **search-output adapters** (MaxQuant first), in **`ProteinAssignment` construction** (`ONTOLOGY.md` §6.3, I17), recorded as `basis = 'reviewed_preferred'`; it lands with the MaxQuant adapter (weeks 5-6). The resolver only reports review status |
| **Curation-loader default: curation `Analysis` (`kind = 'curation'`) → `parameters_observed = true`** | curation loader, weeks 3–4 | A curation `Analysis` records a sample-to-condition mapping or a manual assertion. The curation act is performed *for* the platform and its JSON record **is** the artifact — there is nothing executed elsewhere that the record merely reports. So `parameters_observed = true`: the platform observes the whole of what this `Analysis` consists of. This is the only case that defaults true. No — a loader default, applied when the loader is written |
| **Curation-loader default: `data/curation/analysis_*.json` → `parameters_observed = FALSE`** | curation loader, weeks 3–4 | These records describe a **Colab notebook run** (e.g. `colab_reproducefigure.ipynb`). I19: `false` means the analysis was run outside the platform, with parameters *as stated* rather than *as executed* — which is exactly a hand-authored JSON transcribing a notebook. The platform did not witness the execution; the same person having written both the curation and the notebook does not make it a witness, and "the parameters were executed, not reported" is the argument I19 exists to refuse. Consequence beyond the field: setting `true` would give the 12-of-14 baseline the same provenance standing as a platform-computed result — the exact promotion I19 forbids. Note the class boundary: the **analysis-output** class defaults `false` whether the external tool is Perseus (ADR-0017) *or* the group's own notebook — the split is **platform-executed vs not**, not who ran it. I16 is orthogonal to both: quantity and filters are required and recordable regardless, so declaring them never settles the I19 flag. No — a loader default, applied when the loader is written |
| **`Contrast` deferred to the adapter** | `ONTOLOGY.md` §11 Q1, curation loader | The curation records name their contrasts (`contrasts_of_interest`) but the `Contrast` node's reference-vs-evidence placement is unsettled (§11 Q1, v0.2). Default: the loader does not materialise `Contrast` nodes yet; the adapter constructs the contrast inline when it emits `DifferentialResult`s. Revisit with §11 Q1 before v0.2. No |
| **`raw/` is empty — blocks end-to-end ingestion** | `raw/`, `ROADMAP.md` § Deposit survey | No source tables are on disk. The first Perseus adapter fixture, the first `DifferentialResult` ingestion, and any non-vacuous I9 rebuild all depend on either re-downloading PXD018299 / the BJC supplementary from PRIDE and nature.com, or reconstructing `colab_reproducefigure.ipynb`'s `res` (which is never persisted — see the survey). Until `raw/` has content, the adapter can be *written* against the shared valid change-set but not *validated* against real input. **Yes** — for the first adapter's end-to-end test, not for writing the adapter. **Narrowed 2026-08-07:** `res` is now reconstructable on demand rather than lost — `bzk/sources/pxd018299_baseline.py` re-derives it from the fetched deposit, and its fourteen target rows are committed at `tests/fixtures/pxd018299_welch_baseline.json` (ROADMAP § Independent re-derivation). The full 1,375-row table is still not on disk and the item stands; what is gone is the risk that the baseline could not be reproduced at all |
| ~~**Change-set nodes cannot carry a `label` column**~~ **Fixed 2026-08-07** — discriminator renamed to `__label__` | `bzk/ontology/invariants.py`, ADR-0019 | `label` was both the change-set's node-type key and a real DDL column on `Sample`, `Dataset`, `Analysis`, `Contrast`, `Disease` and `Drug`, so those six columns were unwritable through the documented ingestion path. Renamed rather than worked around, and done now because with no adapters and no graph content it was a mechanical pass over two modules, one fixture and three test files — after `perseus.py` it would have been a migration. Read from `invariants.NODE_TYPE_KEY`, never as a literal. Ids did not move: `label` is excluded from identity (§3) on all six, checked directly. The identity tuple in `keys.py` keeps its own `label=` prefix — hash input, and no collision there. ADR-0019 amended. Resolved |
| ~~**A protein group cannot be ingested at protein grain**~~ **Resolved 2026-08-07 — ADR-0022** | `bzk/adapters/perseus.py`, `ONTOLOGY.md` §3/§5/§6.3 | `ProteinObservation` was keyed on a single `Protein` anchor, so its id *was* the razor pick and a group could not be minted at all; and `PROTEIN_ASSIGNMENT_FOR` reached only `SiteObservation`, so there was nowhere to record the ambiguity either. Measured before amending: **72–77% of rows** name a group (ROADMAP § Protein-group ambiguity), so this was the common path. `candidate_proteins` is now identifying on both observation types, `RESOLVES_TO_PROTEIN` is `MANY_MANY`, `PROTEIN_ASSIGNMENT_FOR` is a two-pair relationship, and I14 gained a second check so an observation cannot name a group while resolving to one member. `perseus.py` ingests groups. Resolved |
| **MaxQuant's narrowing to `Majority protein IDs` has no representation** | `ONTOLOGY.md` §6.3, `bzk/adapters/perseus.py` | ADR-0022 splits the observed candidate set (on the observation) from the inferential one (on the assignment), and the two differ on **52–72% of rows** — MaxQuant narrows `Protein IDs` to `Majority protein IDs`, which §6.3 calls *"its own razor-rule inference"* and says is *"recorded as such"*. It is not recorded: §6.3's shape is a candidate set plus a **concluded protein** (`ASSIGNS_PROTEIN`), and a narrowing to a smaller **subset** is neither — there is no edge for "weighed six, kept three, concluded none". So the adapter reads the wider column and emits no `ProteinAssignment` at all, which loses the narrowing rather than misrecording it. Two ways out, both modelling decisions: let `ASSIGNS_PROTEIN` be absent while the assignment's `candidate_proteins` carries the narrowed subset (making the field mean *kept* rather than *weighed*), or add a subset-narrowing basis with its own edge. **Trigger: the first adapter that has both columns and wants to keep the narrowing** — the MaxQuant adapter, weeks 5–6. No |
| **`perseus.py` is unvalidated against real input** | `bzk/adapters/perseus.py`, `raw/` | **Narrowed 2026-08-07:** it no longer refuses 72–77% of rows (ADR-0022), so the blocker is now only the absence of a file. The adapter is written, tested and mutation-tested, entirely against synthetic fixtures — no Perseus export from the group exists. Three hazards are handled on the strength of the documented format rather than a real file: the `-Log Student's T-test p-value` column name, the `#!{...}` annotation rows, and `Majority protein IDs` as the accession column. All three are conventions, and a real export may spell any of them differently — the adapter refuses loudly on each (naming the columns it looked for) rather than guessing, so a mismatch is a clear error and not a silent empty result. **Trigger: the first real export.** Yes for end-to-end validation, no for the adapter existing |
| **A test whose fixture is live project data stops guarding when the data changes — and goes GREEN, not red** | `tests/`, every adapter's error paths | **The rule: a refusal or error path is tested against a synthetic twin, never against real data being in a particular state.** Found 2026-08-07 when the curator supplied the two titles: five loader tests and one schema guard stopped guarding in the same commit. The five were *designed* to fail on that event and did, which is the benign half. The dangerous half is the other one — `test_pending_markers_point_at_values_that_are_actually_pending` scanned `data/curation/` for `pending` blocks, the last one in the repository left with the titles, and the guard would have passed forever over an empty loop. It caught itself only because it carried an explicit `assert checked` non-vacuity line; without that there would have been no signal at all. Note the asymmetry: a test asserting real data is BROKEN fails loudly when it is fixed, but a test asserting a property OF broken data quietly stops having anything to assert. The second is the one to design against, and 'the suite is green' does not distinguish them. Fix applied: `tests/fixtures/curation_synthetic_pending.json` is the loadable fixture's incomplete twin, differing only in what is owed, and the schema guard now scans `tests/fixtures/` too. **This will recur at every adapter**: a malformed-input test written against whichever real file happens to be malformed today stops testing the day that file is corrected or replaced. Synthetic twin, always — and every guard that can be vacuous carries a non-vacuity assertion, which is what made this one detectable. No — but it applies to `perseus.py` and every adapter after it |
| ~~**Reserved-namespace collisions between other paired key spaces are unswept**~~ **Swept and asserted 2026-08-07** | `bzk/curation/loader.py`, `data/curation/*.json`, `tests/test_curation_loader.py`, ADR-0019 § reserved namespace | ADR-0019's rule was guarded for the one pair it was written from — the change-set format against the DDL — and this row deferred the curation record's key space to *"the second record format"*. That was a trigger for something already checkable: the record's structural keys (`pending`, `unresolved`, `corrections`, `mapping`, `contrasts_of_interest`) either collide with a DDL column name or they do not, and nothing about a second format is needed to find out. **Run: zero collisions against all 86 column names.** So the row was correct — and being correct is exactly why it should have been an assertion rather than a note, since prose that is true today is indistinguishable from prose that stopped being true. Now `loader.STRUCTURAL_KEYS` — declared where the loader owns the contract — plus `test_structural_keys_do_not_collide_with_ddl_columns` against `schema.NODE_TABLES`, and `test_declared_structural_keys_are_all_really_used` so the list cannot rot into fiction. **What it does not catch:** a *new* structural key added to the record without being declared, since the loader reads keys as literals rather than through one accessor. Narrower than the trigger it replaces, and stated rather than implied. Resolved |
| **Edge keys `type` / `from` / `to` carry the same latent collision — guarded, not renamed** | `bzk/ontology/invariants.py`, ADR-0019 § reserved namespace | An edge dict is `{"type", "from", "to", **properties}`, so a relationship property named `type`, `from` or `to` would collide exactly as `label` did on nodes. **None exists** — the DDL declares two rel properties in total, `source` and `evidence_code` — so this was left un-renamed. What changed 2026-08-07 is that it is now a **test**, not this note: ADR-0019's reserved-namespace rule is guarded in `tests/test_invariants.py`, passes today with nothing to catch, and fails the day a rel table gains such a property. The trigger below is therefore automatic; it does not depend on anyone reading this row. **Trigger: the guard going red.** The fix is then the same dunder move, and it is cheap only while the graph is empty. No || ~~**`tests/` has never been type-checked — 34 mypy errors**~~ **Resolved 2026-08-07** — `mypy bzk tests` is clean; `CLAUDE.md` point 1 now names that target | `tests/`, `CLAUDE.md` point 1 | `mypy bzk` is clean and is what point 1 names; `mypy bzk tests` finds **34 errors in 6 files**. So the suite every four-point report cites as its evidence is the one part of the tree the type checker has never seen. Two distinct classes, and only the first is cosmetic. **(a) 25 `[arg-type]`, all the injected-stub pattern**: `_FakeSession` / `_FixtureSession` / `_StubSession` passed where the signature says `requests.Session \| None`. The injection is deliberate (`rebuild.py`, `sources/pride.py`), so the fix is a `Protocol` for the session surface, not a cast — a small design decision, not a cleanup. **(b) a real signature/behaviour mismatch already hiding there**: `tests/test_keys.py:196` calls `protein_sequence_key("uniprot:P20591", "04")` — a `str` where the signature declares `int`. It passes because the body does `int(sequence_version)`, so the accepted domain is genuinely wider than the declared type and a test depends on that. Either the signature is wrong or the test is; type-checking `tests/` is what surfaces the question. That one error is the argument for the item: the gap hides real things, not only noise. **Trigger: before the loader's tests are written** — that is when `tests/` starts carrying ingestion logic rather than fixtures and assertions, and untyped ingestion logic is the case the checker earns its keep on. Not blocking until then. **Fired and discharged 2026-08-07, with the loader.** (a) the 24 injected-session errors are gone via `bzk/http.py` — **two** protocols, `BytesSession` and `RestSession`, not one: the deposit fetch reads `content` and `raise_for_status`, the resolver reads `status_code`/`text`/`json`, and a single protocol carrying all five would have forced every stub to grow members it never calls, which is worse than the untyped state. `requests.Session` satisfies both structurally, so no call site changed. (b) the real mismatch was real, and the *signature* was wrong: `protein_sequence_key` declared `int` while its body has always done `int(sequence_version)`, which is what performs §4's unpadding — so `'04'` and `4` both key `#sv4` and a test depended on it. Widened to `int | str | None`; the `None` arm is declared because the I2 guard exists to reject it, and the `# type: ignore` that a test needed to *reach* that guard was the tell. The remaining ten were ordinary: three `json.loads` returning `Any`, one missing list annotation, two missing generator return types, and three kuzu union-narrowings now asserted rather than cast |
| ~~**The K-GG remnant set was stated as four in two places**~~ **Closed by a guard 2026-08-07** | `ONTOLOGY.md` §6.1 and §9, `bzk/ontology/schema.py` | The prose claim *"ubiquitin, NEDD8, ISG15 and FAT10 all leave a K-GG remnant"* was wrong, and the correction is the interesting part of this row: verifying it against UniProt **canonical** sequences first gave the wrong answer for every modifier, because those are precursors — the C-terminus that matters is the **mature chain**, after the propeptide is cleaved. On mature chains the criterion is not "ends in GG" but "has K or R at −3", since trypsin cuts C-terminal to K/R and the remnant is everything after the last one. Three qualify: ubiquitin `P0CG48` (LRLR**GG**), NEDD8 `Q15843` (LALR**GG**), ISG15 `P05161` (LRLR**GG**), all 114.0429 Da. FAT10 `O15205` ends in GG but carries isoleucine at −3, leaving `GNLLFLACYCIGG` at 1,324.63 Da. **The correction was applied to §6.1 and the enum, and §9's worked example kept the four-item set for another hour** — a guard scoped to the section being fixed would have reported clean over it. `test_gg_remnant_modifiers_match_ontology_6_1` now scans the **whole document**: no accession outside `schema.GG_REMNANT_MODIFIERS` may appear on a `leaves_gg_remnant true` line, and no worked `candidate_modifiers` list may name one. Both halves mutation-tested. The guard cannot check the biology — that reasoning lives in §6.1 and beside the enum, because three accessions do not explain themselves. Resolved |
| ~~**`SITE_ON` is `MANY_MANY` against a key composing one parent**~~ **Closed 2026-08-07 — ADR-0023 narrows it to `MANY_ONE`** | `ONTOLOGY.md` §4, §6.3, ADR-0023 | §6.3 deferred this to *"the first search-output adapter"*. The adapter arrived and **could not settle it** — it emits one `SITE_ON` per site unconditionally, so the *1,967 of 1,967* offered here as evidence was the adapter reporting its own design choice back. The row is kept rather than rewritten because that failure generalises: **deferring a modelling question to an implementation only works when the implementation is free to come out either way**, and where it is not, the deferral must name the measurement instead. What settled it was in the file all along — the same peptide sits at a different absolute position in each protein it maps to, 75.1% of multi-protein rows — plus the key composing exactly one `ProteinSequence`, and `P20591:48 = K` against `P09914-2:48 = E` showing a shared position *number* is not a shared position. A second parent is now a write-time structural error, with its red case in `tests/test_invariants.py`. Resolved |
| ~~**Two pairs of relationships model one fact each**~~ **Closed 2026-08-07 — ADR-0023** | `ONTOLOGY.md` §3/§4/§5/§6.1/§6.3, `bzk/ontology/schema.py`, ADR-0023 | `RESOLVES_TO_SITE` and `MEASURED_AT` were the same endpoints at the same multiplicity; `REPORTS_SITE` and `REPORTED_BY` were one fact in both directions. §1's diagram drew one of each and §3's identity table anchored the other, so two readers of the same document would have written queries traversing different edges over one graph. **`MEASURED_AT` and `REPORTS_SITE` survive; the other two are dropped, not aliased** — an unpopulated relationship that means the same as a populated one answers with zero rows where a removed one errors. Renaming cost nothing in ids (`identity_tuple` discards the relationship name; verified by performing the swap, not by reading it). Schema 59 → **57** tables. **The class is closed by two assertions, not by this turn having looked**: no two relationships may share endpoints and multiplicity, and none may be another's exact reverse — both unwritable until the DDL stopped declaring the violations, both mutation-tested. Resolved |
| **The resolver reports `status='ok'` for a deleted UniProt entry** | `bzk/resolve/uniprot.py`, `bzk/resolve/nodes.py` | Found by the first real adapter run: 25 of the site table's razor picks return `entryType: 'Inactive'` — UniProt entries deleted or demerged since the 2019 search — and `resolve` reports them `status='ok'` with `sequence_version=None` and no sequence, because the fetch succeeded and it only inspects `reviewed`/`sequence`/`entryAudit`. Nothing is *wrong* downstream: `resolve_to_nodes` refuses them for having no sequence version, and `maxquant_sites.py` refuses the 48 sites keyed on them, so no bad data is admitted. What is lost is the *reason*. The refusal reads *"no sequence_version, so no ProteinSequence can be keyed"*, which sounds like a metadata gap in a live entry; the truth is that the protein the search named no longer exists as a distinct entry, which is a different finding for a curator and a different fix (re-map to the merge target, not wait for UniProt to fill a field). **`entry_type` is already captured on `Resolution` and already carries `'Inactive'`** — nothing needs fetching, only a status the caller can branch on, so this is small. It is deferred here rather than done inline because it widens `Resolution.status`'s closed set, which `tests/test_resolve.py` and the recorded-response fixtures both pin. **Trigger: the next change to `resolve/uniprot.py`.** No |
| ~~**A change-set could not hold `Protein` and `Modifier` for one accession**~~ **Fixed 2026-08-07 — ADR-0019 corrected** | `bzk/ontology/invariants.py`, `bzk/ontology/store.py`, ADR-0019 | Found by the first real run that seeded `Modifier` nodes: §3 keys **both `Protein` and `Modifier` on bare `uniprot:`**, so ISG15 is `uniprot:P05161` under both — the protein a diGly search reports as a razor pick, and the modifier its K-GG remnant might have come from. That is this project's anchor domain, not an edge case. ADR-0019 said node ids are unique within a change-set and the code read that as unique *globally*; Kùzu stores the two in separate tables and was never troubled. Corrected to **(label, id)** in three places, and the second and third are the dangerous ones: `store.py` resolved an edge's endpoint labels through `{id: node}`, so a collision would have picked the wrong label, `MATCH`ed the wrong table and **written nothing** — the silent failure its own comment already warned about; and `_index` was global, so I2's `HAS_SEQUENCE` clause would have read `.get('accession')` off a `Modifier`, got `None`, and **skipped the check** rather than raising. Both are the shape this repository keeps meeting: a check reporting clean because it never ran. Edges still name endpoints by bare id, which is unambiguous only because no relationship admits both labels in one role — now asserted by `test_no_relationship_role_admits_two_labels_that_can_share_an_id`, mutation-tested, so the day that stops being true is a red test rather than a wrong answer. Resolved |
| **ADR-0019 has become the change-set format specification, not a decision record** | `decisions/0019-changeset-structural-validation.md`, `ARCHITECTURE.md` §3 | It now carries **five dated amendments** — the fifth hole (multiplicity), the sixth (node type declared at all), the `__label__` rename, the reserved-namespace rule, and the (label, id) correction — and between them they *are* the format: what a node is, what an edge is, which keys are structural, how endpoints resolve. `decisions/README.md` says a record is *"never edited; a changed decision gets a new record"*, and the dated-section style is the compromise that keeps the trail readable, which is the rule's purpose. But a living specification is not a decision, and the two want different homes: a decision is read once to learn why, a specification is read repeatedly to learn what. **Eventually the format moves to `ARCHITECTURE.md` §3 and ADR-0019 keeps only its original decision** — change-sets are self-contained, structural validation precedes invariants — with the amendments becoming the specification's history rather than the ADR's. **Trigger: the next amendment.** A sixth is the point at which the trail stops being a trail. Not done now: moving it while it is still accumulating would mean moving it twice. No |
| **`store.py` writes one statement per node and per edge — measured at scale 2026-08-07** | `bzk/ontology/store.py` | Flagged as fine at 16 nodes and untested beyond that. Now measured on the real deposit: **90.3 s to write 20,294 statements** (11,386 node statements + 8,908 edge statements — corrected 2026-08-08; the parenthetical said *nodes* and *edges*, decomposing a total of statements with the two words the rename removed, in the row cited as the reason to rename), **4.45 ms each, 225 statements/second**. For context in the same run, the adapter's `parse` — reading 2.8 MB, resolving 1,054 accessions off a warm cache, validating the whole change-set — takes **0.75 s**. So the write is **120× the cost of producing what it writes**, and it is the whole of the replay's wall clock. Not optimised here, deliberately: `MERGE` per statement is what makes replay idempotent (I7/I9), and batching changes the write path's semantics, not just its speed. The obvious move is one parameterised `UNWIND` per label and per relationship, which preserves `MERGE` and should collapse 20,294 round trips into ~21. **That would bring the write "under 10 s" — and that figure is an extrapolation from 225 statements/second, not a benchmark.** It is flagged here because, as of 2026-08-07, **it is the only unmeasured number left in the document set**: the drift check's ~980 s became 973.7 s measured, the rebuild's cost became 119.9 s measured, the archive's size became 8.3 MB measured, and the sequence-drift exposure became 40 of 2,056 measured. An estimate that is the last of its kind is one nobody re-examines, because there is no longer a habit of re-examining estimates — so it is named as the last one rather than left to become quietly permanent. **It stays an extrapolation until someone benchmarks the `UNWIND` form**, and no decision should rest on the 10 s. **Trigger: the second dataset, or any interactive path that rebuilds.** At one dataset, 90 s is tolerable; at ten it is 15 minutes and nobody re-runs it. No |
| ~~**`query.gene_symbols` claims `UNATTRIBUTABLE` over an empty `Gene` table**~~ **Closed 2026-08-09** | `bzk/query/graph.py`, `tests/test_query.py`, `tests/test_ui.py` | Found by the cold-clone rehearsal, driving the app over a graph built with no `raw/`: all fourteen symbols rendered as *"Present but unattributable — the graph holds what would answer this"* over a graph holding nothing. It was one function and not a class — `differential_table`, `imputation_state` and `refusals` all consult the DDL first, and this was the only one of five that did not, and the only one whose absence value asserts *presence*. `gene_symbols` now returns `NOT_STORED`, which §5.1's enum defines for exactly this. **The interesting half is the guard, not the fix.** Both existing fixtures were populated, so the branch was unreachable from the suite; the new one carries a `Protein` and no `Gene`, so a check written as *is the graph empty* fails it — confirmed by mutating the check to count `Protein` instead of `Gene`. And over that graph the page renders `NOT_STORED` **sixteen** times, fourteen from panel two and two from panel three, so a substring assertion would have passed a broken panel: demonstrated by reverting the fix and watching `RENDERING[NOT_STORED].headline in text` stay `True` with fourteen `UNATTRIBUTABLE` notices on screen. The UI assertion is by element position and count instead. Resolved |
| ~~**`bzk rebuild` exits 0 when there is no deposit to ingest**~~ **Closed 2026-08-09** | `bzk/rebuild.py`, `OPERATIONS.md` §5 | `main` now exits **1** where a curation record named a deposit that was not ingested — absent from the content store, or present and recognised by no adapter. **`OPERATIONS.md` §5's two halves are not in tension and that is the decision:** *never refuses on staleness, it is the disaster-recovery path* and *a different result is a regression, stop* act at different moments, because refusing stands in front of the work and an exit status is emitted after it. So `rebuild()` is untouched, the stores are written identically, and only what the process tells a script changes. Staleness keeps its exit 0, deliberately: §5 calls the receipt a report and not a control. **One branch was written and removed rather than kept**: a predicate distinguishing *names no deposit* from *deposit missing* had an unreachable arm, because `Dataset.content_hash` is identifying (§3) and the loader refuses a record without one — pinned now by `test_a_record_naming_no_deposit_cannot_reach_the_replay_at_all` rather than reasoned about. Both counter branches carry a test and both were mutation-tested; the no-adapter one had none when it was written. Resolved |
| ~~**Streamlit's two defaults contradict the project: binds `0.0.0.0`, reports usage statistics**~~ **Closed 2026-08-09** | `.streamlit/config.toml`, `bzk/ui/app.py`, `OPERATIONS.md` §4.1 | A committed `.streamlit/config.toml` sets `server.address = "localhost"` and `browser.gatherUsageStats = false`, and a test reads both values so the guarantee survives someone forgetting a flag. Verified by running the bare command from the repository root: `Uvicorn server started on localhost:8603`, one `URL:` line rather than three, and no *Collecting usage statistics*. **It restores the *served locally* condition for the documented invocation, and the reason is stronger than usually:** `streamlit run bzk/ui/app.py` names a relative path, so it can only run from the repository root — which is the directory the config is read from. An absolute-path invocation from elsewhere escapes it; that limit is stated in §4.1 rather than papered over. `app.py`'s docstring asserted the I18 reading with no condition and now carries one and cites where it is met. **`CLAUDE.md`'s normativity rule names `ONTOLOGY.md` and does not reach a reading that lives in §3 here**, so what settles that pair is the single-source rule instead: the condition has one home and a module docstring is not it. Resolved |
| **`AMBIGUOUS` folds into `no_cross_reference` — the code half closed 2026-08-09, the modelling question open** | `bzk/resolve/nodes.py`, `ONTOLOGY.md` §4 | `schema.GENE_ABSENCE`'s description said *"UniProt reports no HGNC cross-reference"* where §4's table says *no **usable** cross-reference — none at all (10), or several (5)*. §4 had been corrected around the code and the code was the half left diverging; under `CLAUDE.md`'s normativity rule the code is what moves, and it has. **The modelling question is deliberately not settled and the trigger is sharpened rather than left as fired.** *Fired — the state is populated* was the wrong trigger: it fired on the day it was written and does not say what would make the change worth its cost. The cost is a normative DDL change moving a partition recorded in six places; the benefit is a distinction **no reader currently sees** — `gene_absence` reaches no panel, no export and no report, and `gene_absence_census` is called from `tests/` and nowhere else, searched rather than assumed. §4's *three absences that must not read as one* is about a reader, so: **Trigger: the first reader that puts `gene_absence` in front of a person** — a panel, an export, or a curator-facing report — or the ambiguous share growing beyond the third of `no_cross_reference` it is today. No |
| **The content store keeps objects nothing references, and nothing can tell them apart from inputs** | `bzk/provenance/raw_store.py`, `~/.bzk-omics/raw/` | The warm tree holds **6** objects; a cold clone running every documented fetcher produces **4**. The extra two are BJC supplementary files pulled by hand during the 2026-08-09 investigation, cited by no curation record, no fetcher and no document — searched for by digest and by filename, zero hits. They are harmless: I9 replay reads what the curation records cite, so an orphan is ignored rather than ingested. What is missing is any way to *know* that — a content-addressed store with no reachability notion cannot distinguish an input from a leftover, so `raw/` grows and nobody can safely prune it. Note the direction: the cold tree is the correct one and the warm tree accumulated. **Trigger: the first `raw/` large enough that someone wants to delete something.** No |
| ~~**The rebuild's drift check now refetches every cached sequence**~~ **Split out 2026-08-07 — `bzk drift`** | `bzk/drift.py`, `bzk/rebuild.py`, `OPERATIONS.md` §1/§5 | The drift check was never a rebuild step: rebuild reconstructs derived state from the I9 inputs, this validates one of those inputs against the outside world, and the graph is byte-identical either way — shown rather than argued, since two replays that skipped it reproduced the same 11,389 ids as one that did not. Welded, it cost ~980 s of a 1,057 s rebuild; split and both measured end to end, **`rebuild` is 119.9 s and `bzk drift` is 973.7 s** over 1,029 sequences. That run reported zero drift, which says only that the check runs — the archive was hours old (see the self-guaranteeing-measurement row below). Nothing about the check is weakened — it still refetches every archived sequence with `refresh=True`, because §11 Q5's failure is invisible to anything that trusts the version number. **What answers *"what stops someone rebuilding for a year without ever drift-checking"* is the receipt**, not the split: `bzk drift` writes `~/.bzk-omics/cache/uniprot/.drift` (timestamp, count, digest of the set checked, outcome), and `rebuild` reports staleness from it every run. It never *refuses* — rebuild is the disaster-recovery path (`OPERATIONS.md` §1) and a network check in front of recovery is worse than a stale check. The digest is load-bearing: a check that covered 20 sequences yesterday says nothing about the 1,028 ingested this morning, and "checked 1 day ago" would be true and misleading. Resolved |
| **The site adapter applies a localisation threshold and records it nowhere (I16)** | `bzk/adapters/maxquant_sites.py`, `ONTOLOGY.md` §5.4/§8 I16 | New with Slice 4a, and created by it: 242 of 2,298 rows are dropped at `Localization prob >= 0.75`, and the graph holds **one `Analysis`, of kind `curation`** — nothing records the threshold, the quantity, or that a filter was applied at all. I16 says *"every `Analysis` records which quantity it consumed and the filters applied, including the localisation threshold"*, and it is not violated only because the adapter emits no `Analysis` to violate it: the check iterates over nodes that do not exist. That is the invisible-choice defect I16 exists to prevent, arriving through the gap rather than through the field. The fix is a search-output `Analysis` — `kind = 'external'`, `external_tool = 'maxquant'`, `parameters_observed = false` (I19), `quantity = 'intensity_multiplicity_summed'`, `localization_threshold`, `filters_applied` — which the observations attach to. Deliberately not added in Slice 4a, which was scoped to wiring: it touches I15's `Imputation` requirement and I19's flag, both decisions rather than plumbing. Now also `ROADMAP.md` § The platform made an invisible analytical choice, because 10.5% of a dataset removed by an unrecorded number is a measured finding about this platform, not only a task. **Trigger: before any result is derived from these observations**, i.e. the first thing Slice 4b does. **Yes** — for Slice 4b, no for the ingestion standing as it is |
| **I18 obligation: an export must state its sequence-archive staleness** | export boundary, `bzk/drift.py`, `ONTOLOGY.md` §8 I18 | **A named obligation on unbuilt work, recorded rather than assumed.** The drift split makes staleness *visible* (a line in `rebuild`'s output) but not *consequential* — a console line is ignorable by construction. What makes it consequential is the export boundary, where this project already refuses embargoed datasets (I18) and flags `unprovenanced` results: **an export, figure or report derived from `ModificationSite` positions whose archive was last drift-checked more than N days ago must state so, in the same channel and by the same rule.** N is `OPERATIONS.md`'s to set; `drift.STALE_AFTER_DAYS` is 7 today and is a *reporting* threshold only, enforced nowhere. This is written down because the strongest half of an accepted proposal depended on it, and a dependency on unbuilt work that is not named is a dependency that quietly does not happen. **Trigger: the first export, report or figure-writing path** — the same trigger I18 itself already carries, so the two land together or neither does. No — but the drift split is materially weaker until it does |
| **Sampling the drift check needs per-sequence staleness first** | `bzk/drift.py` | The obvious next economy: check N sequences per run rather than all 2,845, turning ~35 minutes occasionally into ~1 minute always — and note that the cost of not doing it grew 2.8× in a day, because I17's extra resolutions grew the archive, not because anything about the check changed. Deferred, and the precondition is the reason — **it is only sound if staleness is recorded per sequence rather than globally.** With one receipt for the whole archive, "checked recently" becomes an average over a set whose oldest member may never have been checked at all, and the number that gets reported is the flattering one. That is the same shape as the count that would have hidden the newly-ingested sequences, which the receipt's archive digest already guards against — so the machinery half exists and the per-sequence half does not. **Trigger: whenever the full check stops being run because of its cost** — which the receipt now makes observable rather than a matter of anyone's memory. No |
| **Measurements guaranteed by their own setup — three instances this session, and the diagnostic** | everywhere a number is reported | Each of these was offered as evidence and was instead a restatement of the arrangement that produced it. **(1) `SITE_ON`: 1,967 of 1,967 sites carry exactly one parent** — the adapter emits one unconditionally, so the count is arithmetic on a constant (ADR-0023 records it). **(2) The 12-of-14 re-derivation** reproduced the notebook's numbers using the notebook's own transcribed arithmetic, including its hand-written BH and its best-site rule; that establishes the transcription is faithful, which is worth having, but it is not independent confirmation of the pipeline and must not be cited as one. **(3) Zero drift over 1,029 sequences**, on an archive written at 15:39 and checked at 17:28 the same afternoon — a fetch compared against a fetch under two hours older. All three are green, all three are true, and none is evidence of what it was offered for. **Re-run 2026-08-08 over the grown archive: 0 drifts across 2,845 sequences, and the caveat is unchanged rather than diluted** — 1,816 of those files were written the same day and the oldest was thirteen hours old, so a bigger clean number was bought with more fetches against the same UniProt release. Two clean runs are not corroboration when both share the defect; that is worth stating because a repeated measurement *feels* like independent confirmation and this one is closer to the same measurement taken twice.

**The diagnostic is one question, and it is not "did the check pass":** *what would have had to be different for this number to come out otherwise?* If the answer is "nothing reachable" — because the producer chose it, because the comparison is against its own source, or because no time has passed — the measurement is describing the setup. It belongs in the record as *what ran*, never as *what is true*. This is the same failure as a vacuously-passing test and the same as ADR-0023's circular deferral, one level out: there the implementation could not come out either way, here the measurement could not. **Trigger: every number reported to the curator** — which is why this row is a habit rather than a task, and why it is written down after the third instance rather than the first. No |
| **I17 as specified does not cover two cases the data contains** | `ONTOLOGY.md` §6.3, `bzk/adapters/maxquant_sites.py` | Both found by implementing it, both stated before the run. **(a) "The reviewed Swiss-Prot entry" is singular and the data has several.** ADAR's group holds five reviewed accessions (`P55265` plus four of its isoforms) and OAS1's holds two distinct *canonical* reviewed proteins (`F8VXY3`, `P00973`). The adapter prefers a canonical over an isoform and **declines to promote** where more than one canonical reviewed protein remains, because choosing between two genuinely different reviewed proteins is the search engine's job. That rule is the adapter's, not §6.3's, and OAS1 stays unrecovered because of it. **(b) `reviewed_preferred` cannot carry `ASSIGNS_PROTEIN`.** §6.3 permits it only at confidence `probable`; I14 requires `confirmed` before an assignment may reach `ASSIGNS_PROTEIN` from a multi-candidate set — which promotion always is. So the two rules together permit *recording* the promotion and forbid *asserting* its conclusion. The adapter emits the assignment without the edge, which is the honest shape but leaves §6.3's candidate-set-plus-concluded-protein pattern unsatisfied — the same gap already recorded for `Majority protein IDs` narrowing, reached from the other side. **Trigger: the next §6.3 amendment**, which should settle both together. No |
| **Reviewed-preferred is not uniformly safer — TAP1 is the counterexample** | `ONTOLOGY.md` §6.3 I17, `ROADMAP.md` § I17 implemented | § Sequence drift records drift as 2.8× likelier on unreviewed entries and every deleted entry unreviewed. Both are true and both are *population* statistics. TAP1 runs the other way: its unreviewed razor pick `A0A140T9T7` (808 aa) has K at 449 and 458, and the reviewed `Q03518` it was promoted to is 748 aa today with L and V there — so I17 turned a recovered published target into two refused rows. MaxQuant's own positions are identical for both accessions, so the 2019 FASTA held an 808-residue Q03518 and the **reviewed** entry is the one that has since been revised. The adapter is right to refuse; the point is that I17 has a cost as well as a benefit and §6.3 states only the benefit. **Trigger: before I17's promotion is described anywhere as a safety measure** — it is a trade, measured here at three targets gained and one lost. No |
| ADRs 0004–0014 unwritten | `decisions/` | No — write during weeks 7–8 |
| Search engine for the new USP18 dataset | Assumption A2 | Yes for that dataset only |
| Where in his pipeline the handover belongs | `ROADMAP.md` § Open questions | No — ask at the meeting |

### The curation loader — one blocker left (2026-08-07)

The key builder exists (`bzk/ontology/keys.py`) and the checksum gap is closed, so only the
project/experiment titles remain. Both blockers were the schema working rather than failing — under
ADR-0021 a node cannot be minted without its identifying values, so the loader must refuse rather
than invent.

1. ~~**No `content_hash`, so no `Dataset`.**~~ **Resolved 2026-08-07.** `bzk/sources/pride.py`
   fetched `HAP1_USP18KO_GlyGlyKSites.txt` into the content-addressed store, and all three
   PXD018299 records now cite
   `sha256:a4a503e39581334c3553d3631456ad8aca22e193ba928810f6d46fde15622009` (2,759,052 bytes).
   `Dataset` is constructible.
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

   ~~**The loader waits on the two titles.**~~ **Supplied 2026-08-07** — `project.title` is `"USP18-dependent ISGylation"` and `experiment.title` is `"HAP1 USP18 knockout diGly proteomics, ±IFN-α2b"`, with both `pending` markers removed. The scoping the curator chose, recorded because it governs every future record: **`Project`** is the research *question*, not the laboratory, the platform or the deposit — a second unrelated line of work is a second `Project`. It is broad enough that the higher-coverage USP18 dataset expected in September sits under it as a new `Experiment`, and specific enough not to be reused by accident, `title` being `Project`'s only identifying field and deliberate reuse its one collision case. **`Experiment`** carries every discriminator that will matter once a second exists: cell background, genetic perturbation, modality, treatment axis. Deliberately **excluded**: the accession, because `PXD018299` identifies the `Dataset` and the September data will be a different deposit of arguably the same experiment; and any year, because `Experiment` has no temporal identity and dating it would make a re-run of one design look like two.

3. ~~**`Sample.timepoint_h` is null on the six unstimulated samples, and §3 classifies no such
   absence**~~ **Resolved 2026-08-07 — ONTOLOGY v1.17.** The gap was never the classification; it
   was that `timepoint_h` was the only column in the §5 `Sample` block with no DDL comment, so what
   it measures was unstated and "unknown" could not be told from "inapplicable". It is now defined
   as **hours since treatment**, and §3 classifies the absence `determined` by `treatment`. The six
   samples key as they stand. What follows is the reasoning, kept because the *shape* of the
   mistake recurs — a classification argued from the refusal it would clear rather than from what
   the field means.

   **The evidence.** For hours-since-treatment: the record carries `timepoint_h: 48` on exactly the
   six samples whose `treatment` is not `none`, and null on exactly the six where it is — a perfect
   partition; the 48 comes from the methods as the record quotes them, *"treated with human
   IFN-alpha2b at 1000 U/mL, with the GlyGly peptidome comparison performed at 48 h"*, which anchors
   it to the treatment and not to culture start; and the column sits directly after `treatment` in
   the DDL. The deposit is **silent** — its sample names encode genotype × IFN × replicate only,
   there is no time column and no experimental-design file — so it neither supports nor contradicts.
   Against: the record's own `unresolved` reads the null as a value that exists and was not reported
   (*"not stated separately in the methods … rather than assumed to be 48 h"*), which under this
   definition would be a category error. That phrasing is the symptom of the undefined column rather
   than evidence about its meaning: the curator could not tell which reading applied and correctly
   declined to write anything. A dated `corrections` entry records this in the record itself; the
   `unresolved` prose is left unedited, as the quantity correction before it was.

   **What the first pass got wrong, kept because the error is the instructive part.** It read the
   null as contingent, on the strength of the `unresolved` prose, and offered two ways out: supply
   the timepoint, or classify the absence as determined by `treatment`. Both were framed as the
   curator's call between two defensible options — and that framing was the mistake. They are not
   alternatives. Which one is correct is *decided* by what the column measures, and that question
   had an answer nobody had written down. Defining the field first turns a judgement call into a
   lookup. Asking "what does this column mean?" before "is this null legal?" is the general form.

Neither of the first two is a defect in the loader design; both are the record format meeting a rule
that did not exist when the records were hand-written. `source_type` was a smaller instance of the
same, now resolved: `Sample` requires it and the mapping entries implied it (`cell_line` present ⇒
`cell_line`) without stating it. The third was a different shape again — not a field the format
forgot, but a field the *schema* had never defined — and it is closed.

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
3. ~~**Unformatted floats** (4 fields): `Sample.timepoint_h`, `Analysis.localization_threshold`,
   `Imputation.downshift_sd`, `width_sd`. `1.8` and `1.80` fork an id.~~ **Closed, and this item was
   stale rather than open — corrected 2026-08-08.** The rule shipped with the key builder
   (`keys.py`'s `DOUBLE` branch) and carries three tests, including one for the fold. What was
   actually missing was a *home*: `ONTOLOGY.md` §3 said the rule was "stated nowhere yet and
   unimplemented", and this item repeated it, so both documents asserted a gap that code had closed.
   §3 now states the rule normatively. **A false claim of a gap has no mechanical detector** — code
   contradicts a false claim about what code does, but nothing contradicts a claim about what code
   *does not* do, and no test fails when the gap closes. That is why this survived eight revisions
   of the surrounding paragraph. **The `Analysis` qualifying-child fold (§3) depends on this rule**,
   since it folds two of these floats.

**Fallback keys are now forbidden outright (ADR-0021)**, so the builder never has to reconcile one:
an identifying field may be absent only when its absence is *determined by the data*, never when it
is *contingent on what was known at ingest*. §3 classifies every nullable identifying field, and
`tests/test_schema.py` rejects any marked `contingent` and any absence found in committed data but
left unclassified. `Software` now keys on `name` + `version` (the digest is non-identifying) and
`Person` identity comes from the curation export rather than an ingest-time inference — so the
builder can treat every identifying field as either present or determinedly null, with no
provisional state and no merge step.

Also from the same audit, both now closed: `parameters_json`'s canonicalization was documented in §3
and ADR-0020 and **implemented nowhere**; and reference-key components have their own canonical
forms fixed in `ONTOLOGY.md` §4 (Unimod-only modification keys, unpadded `sv`, uppercase residue,
uppercase accession, lowercase CURIE prefix), which were checked against committed data but not at
construction. See the convergence below.

#### Normalize or refuse — the key builder's fourth family, decided 2026-08-08

A sweep of every canonicalization clause in `ONTOLOGY.md` §3 and §4 against `keys.py` found three
clauses of one class: **an identifying value has a canonical form asserted in the normative
document, and the builder neither normalizes to that form nor refuses a departure from it, so two
spellings of one fact mint two ids.** Converging can mean either, and the mode was decided per
clause rather than by which was easier to write.

| Clause | Mode | Why |
|---|---|---|
| §3 l.171 `parameters_json` *"normalized numeric forms"* | **Normalize** | `250` and `250.0` are the same JSON number — JSON has one number type — so there is no departure to refuse and refusing would reject valid input. `json.loads` preserves the written form and `json.dumps` writes it back, which is how the int/float boundary survived into the hash while float *spelling* already converged through the parse. **Every** integral float collapses to `int`; bools are left alone because `isinstance(True, int)` is true in Python and JSON's `true` is not the number 1, and non-integral floats never reach the collapse. **This clause both normalizes and refuses, and the boundary is stated 2026-08-08:** numeric *forms* normalize, while malformed JSON **and non-finite numbers** are refused — see the row below, and the raise in `canonical_parameters_json` |
| §4 l.265 accession uppercase | **Refuse** | A lowercase accession is not another spelling of a UniProt accession, it is a malformed one, and repairing it asserts more than the input supports (I19's discipline). Two concrete costs of normalizing: `resolve/nodes.py` writes `accession` into the node from the same raw string, so an uppercased id would sit on a node whose own column contradicted it; and a curator's typo becomes permanently invisible, because the repaired id is well-formed and resolves |
| §4 l.266 **first** clause — CURIE prefix lowercase | **Refuse** | The values are node ids. `store.py` writes them as edge endpoints and as `candidate_proteins` elements from the raw change-set, so normalizing the hashed copy alone would leave the id correct and the content it identifies wrong — a worse state than the fork. The builder also cannot tell a CURIE from free text generically, so a blanket normalize is unavailable; the check fires only when a prefix case-folds onto a §3-map prefix, and once detection is that precise, refusal is precise too |
| §4 l.266 **second** clause — the local part renders the authority's identifier verbatim | **Refuse; `uniprot` and `hgnc`** | Added 2026-08-08 as a correction, not a new clause: see the row below. Scoped to the authorities in an identifying position — `uniprot:` fills `candidate_proteins` on four node types, and `hgnc:` *is* `Gene`'s identity. UniProt's half is §4 l.265's accession clause reaching the second position l.266 names. Scoped to the segment before the first `#` for UniProt, because a composed key continues past it in lowercase; not for HGNC, which anchors no composed key |
| — the same clause, `hgnc` `chebi` `go` `mondo` | **Refuse, added 2026-08-09** | The clause read *"keeps its authority's casing"*, which is silent about a *missing* prefix, and §3's map was the one row that stripped one: `hgnc:4053` where HGNC issues `HGNC:4053`. So `hgnc:7532`, `hgnc:HGNC:7532` and `hgnc:hgnc:7532` were all accepted — three spellings, one gene, in a field that is the whole of that gene's identity. §4 is sharpened from *casing* to *the authority's rendering*, which is what its own `chebi:CHEBI:15377` and `go:GO:0032020` examples always demonstrated — so the other three prefixed authorities are determined by the same sentence and are guarded in the same change, not deferred to their node types. **This row is the class's third instance and the first caught before data existed**, rather than after |

The general rule the split follows: **normalize when both spellings are legal renderings of one
value; refuse when one spelling is simply wrong.** Refusal is also this module's existing answer to
a key-authority clause — `modification_site_key` raises on a PSI-MOD accession rather than
translating it — and `perseus.py`'s answer to an unrecognised column.

**The accession clause covers the cache path, not only the id.** `resolve/uniprot.py` builds
`cache/uniprot/entry/{canonical}.json` and `cache/uniprot/seq/{accession}#sv{n}.txt` from the
accession verbatim, where canonical means isoform-stripped and *not* case-folded. So a casing
departure forks the sequence archive — an I9 input — and the drift receipt's digest, and forks them
**differently by platform**: on a case-insensitive volume the two spellings share one cache file
while the graph still mints two ids. `resolve` therefore runs the same check before it builds any
path, and `tests/test_keys.py` asserts that a refused accession leaves the cache directory empty.

Each of the three has a two-spellings-one-id guard in `tests/test_keys.py`, and
`test_reference_ids_on_disk_are_canonical` was extended to assert the accession segment of every
committed reference id, which it skipped while checking the prefix. **That on-disk guard is a weak
net and must not be described as covering the class:** it sees 8 reference ids in total, because it
scans committed JSON rather than the graph. The per-clause guards are the enforcement.

**Corrected 2026-08-08 — §4 l.266 is two clauses and only one was closed, but the record said
three of three.** `check_curie_case` implemented *"CURIE prefixes are lowercase"* and nothing
implemented *"The local part keeps its authority's casing"*, so at 3ca5868
`canonical_value(['uniprot:p05161'], 'STRING[]')` was accepted and the two spellings minted two
`ModifierAssignment` ids. The position is the one that matters: `candidate_proteins` is identifying
on four node types, `protein_key` refuses a mis-cased accession but sits **outside** the hashing
path, and the argument for this whole class is that the builder must not depend on producers
happening to emit canonical values. The UniProt half is now enforced inside the digest path and the
row above records it. **This is the same shape as the two defects it corrects:** a stated reason
more confident than the thing it justifies — here, "closed" asserted of a sentence whose second half
nothing read.

**The class shrank rather than gaining a trigger, 2026-08-09.** It was one open clause: *the local
part of the other ten authorities, unenforced because §4 fixes nothing to enforce.* Sharpening §4
from *casing* to *the authority's rendering* split it, and the determined half was closed in the
same change rather than recorded with a trigger.

- **Closed: `hgnc`, `chebi`, `go`, `mondo`** — the four whose identifiers carry their own prefix,
  in `keys._LOCAL_PART_PREFIX`, each with a §3-example-passes / stripped-form-refused pair in
  `tests/test_keys.py`. **`chebi`, `go` and `mondo` were written with `hgnc` and not deferred**,
  and the reason is the whole lesson of this entry: the argument for deferring them — no nodes,
  the node types out of scope, nothing can fork — is verbatim the argument that was available for
  `hgnc` right up until `Gene` came into scope with three live spellings. Once the rule determines
  the form, what is left is a check, and a determined-but-unguarded rule held as prose is exactly
  what `CLAUDE.md`'s verification point 3 refuses. Cheap now; a re-mint after population.
- **Still open, genuinely undetermined: `ensembl`, `unimod`, `mod`, `reactome`, `doi`, `pmid`.**
  §4 fixes nothing for them and guessing would be inventing a fact with no home (`CLAUDE.md`
  § Working style). **Trigger: the first of them to enter an identifying field or an anchor.** At
  that point §4 states the rendering before the builder enforces it, in that order. The open set
  is asserted in `tests/test_keys.py` as the complement of the enforced one, so it cannot drift
  out of step with `CURIE_PREFIXES` without failing.

`tests/test_keys.py::test_the_local_part_check_is_scoped_to_the_authorities_section_4_fixes`
records the boundary as an assertion rather than as prose. **`hgnc:4053` was in that test's list,
cited as an authority with a numeric local part** — the citation was wrong, and a test asserting
the acceptability of a wrong example is how the third spelling survived a sweep written to find
exactly this.

**Closed 2026-08-09 by `OPERATIONS.md` §3.1 — and the trigger fired the same day it was written.**
The item below was recorded as *"trigger: before answering `ONTOLOGY.md` §11 Q12"*, and Q12 was the
next question asked. The decision is **not** the one this entry predicted: **versioning the entry
key was rejected**, because it exchanges a silent overwrite for an ambiguous read and nothing on
disk names which capture a rebuild must use — the record that could have, `resolution_PXD018299.json`,
is a 642-byte summary. What was done instead is a split by whether a field bears on identity:
`sequence_version`, `entry_type` and `reviewed` move to a write-once pin at
`seq/{canonical}#sv{n}.meta.json`, and the entry file is *declared* the mutable snapshot it always
was. `reviewed` is the field that made the pin necessary and the one a split done by eye would have
left behind — it appears in no key, and reaches identity only through I17's choice of which protein
a site is keyed against. Guarded in `tests/test_pins.py`, every test written against a snapshot that
disagrees with its pin. **One sentence turned out to have four homes** — §8 I9, §11 Q6,
`OPERATIONS.md` §1 and `ARCHITECTURE.md` §2 — all asserting of the whole cache what was true of its
sequence tier; the first two were corrected on 2026-08-09 and the other two only when this decision
made someone read them. The original entry follows, unedited.

**Open item, with a trigger: the UniProt entry cache is overwritten in place (2026-08-09).**
`ONTOLOGY.md` §8 I9 and `OPERATIONS.md` §3 both said the cache is *"keyed so that a new version is
a new entry rather than an overwrite"*; both were describing the **sequence** tier and asserting it
of the whole. `entry/{canonical}.json` carries no version, and `bzk/resolve/uniprot.py`'s docstring
has always called it *"a mutable snapshot"* — so the code was right and two documents were wrong,
in the sentence that names the cache an I9 input. Both are corrected. **It is material**: the entry
tier supplies `sequence_version`, which is embedded in every `ModificationSite` key, so a refresh
re-keys the graph against today's UniProt. Measured 2026-08-09, the exposure is latent — all 2,261
entry files carry their original ingestion `fetched_at`, and `bzk drift` fetches into a throwaway
directory rather than through the live cache. That is a property of no caller passing
`refresh=True` with the default cache directory, not of the design. **Trigger: before answering
`ONTOLOGY.md` §11 Q12**, since every answer to Q12 re-writes that path and would settle the cache's
contract as a side effect of a gene build. Owned by `OPERATIONS.md` §3.

**Corrected 2026-08-08 — the `2**53` cutoff in `_canonical_json_numbers` had a false reason.** Both
this section and the code said collapsing integral floats above `2**53` "would merge values rather
than spellings". It cannot: `int()` on an integral float is exact at any magnitude, since Python
ints are arbitrary precision, and therefore injective — measured across `2**53`, `2**60`, `1e22` and
`1e308`, with no two distinct floats collapsing together. Any precision loss happened at
`json.loads`, before the function is reached. What the cutoff actually did was leave the int/float
fork standing above the bound: `{"n": 1e16}` and `{"n": 10000000000000000}` hashed differently,
which is C1's defect unfixed in a range. The cutoff is removed.

**The wrong reason was the worse half of that defect,** and it is why this is recorded rather than
quietly fixed. `s0` and a randomisation count will never approach `2**53`, so the unreachable fork
cost nothing; a justification that reads as principled is what gets copied into the next boundary
decision. Both instances corrected here shared that shape.

**Decided 2026-08-08 — `canonical_parameters_json` refuses non-finite numbers.** It refused input
that was not JSON and emitted output that was not JSON: Python's parser accepts `Infinity` and `NaN`
as an extension, `json.dumps` writes them back, and `{"n": 1e400}` overflows to `inf` with no
literal involved. Measured before deciding: **no fork resulted** — the parse is symmetric,
`Infinity` and `1e400` converge on one string, and distinct non-finite values stay distinct. The
defect was that a function whose contract is a canonical *JSON* re-serialization produced a string
no JSON parser accepts, and that a test pinned the lax output as expected while nothing recorded it
as a choice.

Refused rather than accepted, and the reasons are not symmetry alone. **`NaN` is an absence wearing
a value's clothes (ADR-0021):** it is identifying, it means *not a number*, and two analyses whose
parameter failed to compute would converge on one id — asserting they are the same analysis when the
data says only that both are broken. Family 4's rule then applies: refuse when one spelling is
simply wrong. The mechanism is `allow_nan=False` at the exit rather than `parse_constant` at the
entrance, because the latter sees literals only and would let `1e400` through.

**Reachability is nil today, and the guard is weaker than its name for that reason.** Nothing in the
repository puts a value into `parameters_json`: `maxquant_sites.py` writes `None`, the curation
loader never touches it, and `perseus.py` passes through a caller-supplied `DeclaredAnalysis` whose
only constructors are in `tests/`. So both the refusal and the test it replaces pin behaviour on an
input no path produces. The decision is recorded for the producer that arrives next — and
`json.dumps` defaults to `allow_nan=True`, so a producer serialising a params dict holding a
computed `nan` emits `{"s0": NaN}` without noticing. Note also that the earlier bound on this
field's value space was too narrow: §5's DDL says *"test-specific parameters, **e.g.** s0,
n_randomisations"*, so it is whatever a test declares.

#### `nodes_written` / `edges_written` renamed to `nodes_staged` / `edges_staged`, 2026-08-08

**The names asserted a property the code does not have.** `store.WriteReport` builds both from the
length of the staged collection in one expression, and both write paths are `MERGE`, so anything
staged a second time issues a statement and creates nothing. ADR-0019 requires a change-set to be
self-contained, which makes re-staging **mandatory rather than incidental**: on PXD018299 the site
adapter re-stages the `Dataset` and all 12 `Sample`s the curation record already wrote, plus the 12
`PRODUCED` edges over them, so the divergence is systematic and its size is exactly 13 and 12.

The full surface was three declarations (`store.WriteReport`, `rebuild.ReplayReport`,
`rebuild.RebuildReport`), one construction, four log strings — one of which closes
`replay_ingestion` rather than `rebuild`, so a caller invoking replay directly ends on a different
line — and three committed tests.

**Renamed rather than re-meant, and not on cost.** What the graph holds already has a home in
`store.count_nodes`, which is where §3's composition list comes from, so re-meaning these would put
one fact in two places — a defect rather than redundancy. Statements issued has no other home and is
load-bearing: the `store.py` performance row above is denominated in it (*"20,294 statements … 225
statements/second"*). **The claim that followed is withdrawn, 2026-08-08.** It read *"and that row
already used the correct word one line below the sentence that did not"*, and the row did not: its
total said *statements* while its own parenthetical decomposed that total as "11,386 nodes + 8,908
edges", on the same line. The exhaustive figure search of 2026-08-08 returned that line — the search
was not what failed; reading it as already correct was — so the row cited as the reason to rename
was carrying the defect the rename exists to remove. Corrected above, and the same withdrawal is in
`store.WriteReport`'s docstring, which made the identical claim.

**The detector is written, and was widened 2026-08-08 after admitting the re-meaning it was
offered against.** Its first version wrote one change-set twice and asserted the reported count
diverged from the graph *delta* — the one alternative it was built around, so nothing could have
made it survive. Re-meaning **both** fields to `sum(count_nodes(conn).values())` — the very design
`store.WriteReport`'s docstring rejects — passed the entire suite, both detectors included, because
each evaluated `1 != 0` exactly as under the correct code.

The widened tests arrange a scenario in which every candidate quantity takes a **different value**,
and exclude each by name: `len(staged)` = 3, graph delta = 1, total after = 5, total before = 4,
transposed field = 0, and no constant satisfies both tests at once. Each of those six re-meanings
was written into `store.py` and run, with a live probe confirming the mutant changed what the report
returns before any red or green was read; all six now fail. Two candidates stay unexcluded and are
named in the test rather than left implicit — distinct staged `(label, id)`, which no *validated*
write can separate from `len(staged)` because ADR-0019 refuses duplicates inside a change-set, and
rows-actually-changed, which Kùzu does not expose. Both fields are covered, since `WriteReport`
builds them in one expression and the surviving re-meaning mutated both together.

**Corrected figures.** The sentence in §3 recording the post-ADR-0024 rebuild said *"11,743 nodes
and 9,229 edges"*. Both are correct numbers about statements issued and wrong about the graph, which
holds **11,730 nodes and 9,217 edges** — measured per label, and the difference is exactly the 13
re-staged nodes and 12 re-staged edges above. Both figures entered in one commit (`12ea998`), four
lines from a sentence in the same paragraph giving 11,730 for the ids, so this was one paragraph
asserting both rather than two sessions disagreeing.

#### A committed assertion that could not fail, and the sweep for its shape

`tests/test_perseus.py` asserted `report.nodes_written == len(parsed.nodes)`, which is the
expression `store.WriteReport` is built from — a tautology that could not fail under any change to
the code it appeared to test. **The same class as the two above:** the code was correct and the
artefact describing it was false, here a test's presence in a green suite asserting that a property
is guarded when it is not. It is the ADR-0019 vacuous-check family, not a new one.

**The replacement over-claimed in turn, and is corrected 2026-08-08.** It read
`report.nodes_staged == sum(count_nodes(conn).values()) == 18`, offered as catching a silent write
failure the per-label dicts below it do not. It does not: those dicts are literals summing to 18 and
24, so `sum(...) == 18` is entailed by them and no state fails the sum while the dict passes — the
silent-skip mutation that "confirmed" the reach fails the dict too, and the dict additionally names
the missing label. The `sum(...)` terms are deleted. What survives is the one conjunct the dicts do
not entail, the *staged* count against a literal, whose reach is this adapter's change-set size and
nothing further.

**Swept twice, and the first sweep's numbers were a property of its criterion.** Pass A took every
equality with `len()` on one side (46 matches) and Pass B every `<obj>.<attr>` against an expression
rooted in the same name (32 matches, **0 hits**), and that zero was read as coverage. It was not: an
audit then produced by hand three instances, two of which **neither pass could have matched** —
`test_drift.py:110` has no `len()` for A and no shared root for B, and `test_perseus.py:228` the
same. The zero was the result that should have prompted the look.

**Widened and re-run 2026-08-08, pre-registered first** (`ROADMAP.md` § Pre-registration: what
widening the tautology sweep would mean). Pass C — one side of an `==` contains a call, another side
is not a literal display — matched all three hand-found instances, so the pre-registration's
outcome 3 did not occur. Pass D covers what C cannot see: no call anywhere in the comparison, but a
side bound earlier from one. Over 19 modules and **632** asserts the two passes match **82**
assertions, against 46 / 32 / 78 before.

**Four instances, not one, and they are not all the same strength.** Each was confirmed by mutating
the producing code, with the behavioural edit read back before any result was trusted — one mutation
in this round reported "applied" on a marker while its real edit silently missed, and produced a
green run indistinguishable from a guard that does not fire.

| Instance | Producing code | Mutation | Own module | Whole suite |
|---|---|---|---|---|
| `test_drift.py:108` | `drift.run` ← `archived_sequences` | `found[:-1]` | green | **green** |
| `test_drift.py:110` | `drift.run` ← `archive_digest(archived_sequences(…))` | `found[:-1]` | green | **green** |
| `test_perseus.py:228` | `perseus.py:180` ← `content_hash` | `hash(data + b"X")` | green (21 passed) | red elsewhere |
| `test_curation_loader.py:412` | `sample_mapping` ← `sample_ids` | `Sample` id + `"X"` | its own test green | red via a sibling |

The last two are tautologies whose defect another test catches, which is a different thing from the
first two and is counted separately rather than folded in. **Trigger, and it now covers all four
rather than `:108` alone:** any change that would make one of these fields stop equalling the
expression it is compared against — for the two `test_drift.py` rows that is the per-sequence
sampling deferred above; for the other two it is any change to how the field is derived. All four
are listed in `tests/test_tautology_sweep.py::INSTANCES`, each with an `Evidence` the suite
**re-runs** — see the correction below, because when that sentence was written the evidence was
prose and "enforced rather than remembered" was not true of it.

Five candidates were excluded **by running**, not by reading: `test_drift.py:111` (a corrupted
receipt round-trip reddens it), `test_maxquant_sites.py:215` (dropping a modifier from
`seed.modifier_nodes` reddens it), `test_curation_loader.py:312` (a constant `label` reddens the
module), `test_schema.py:684` (a round-trip through a live Kùzu database), and
`test_protein_groups.py:71` (internal consistency of a pinned record, where no producing code is in
the loop). `test_raw_store.py:52`/`:53`/`:116`/`:161` fail under the `content_hash` mutation and are
the same strength as `:108`, not weaker.

**The sweep is committed and re-runs** (`tests/test_tautology_sweep.py`), which the previous report
said it would not. It pins a **multiset** — module, normalized source and occurrence count, not
line numbers. **Re-keyed from a set 2026-08-08**, and the argument that justified the set is the
reason: it said a count is satisfied by deleting one substantive assertion and adding one
tautological assertion in the same module, which is true, and left unsaid that a *set* is satisfied
by duplicating any pinned assertion, which is equally true. The two arguments each covered the
other's hole; one of them was stated as though it settled the question. Confirmed by planting before
the re-key: a second copy of `test_drift.py`'s confirmed instance, as its own standalone assert,
left the module green at 633 asserts, 82 matches, 0 new. A new match, a new occurrence of one, a
lost occurrence and a lost match all fail now — one mutation each, all four caught.

**Three things it cannot do**, which was two until this finding made it three:

1. It cannot decide whether a call *is* the producing expression — that needs the producer's body,
   which is why the classification is pinned data rather than a verdict the test computes.
2. It excludes itself from its own surface, since its assertions compare a computed match set
   against a pinned constant and a module that swept itself would pin its own pin.
3. **The key is scope-blind.** It records how many times an expression text occurs in a module,
   never where. Established rather than inferred, by running the net over synthetic source: the same
   matching assert in `f` and in `g` produces an identical multiset either way, and two assertions
   reading `x == h(y)` where `h` is bound to a different callable in each scope are one entry with a
   count of two and therefore one classification for both.

Writing it surfaced two of its own matches — the widened `test_store.py` guards asserted
`report.nodes_staged == len(staged) == 3`, whose first conjunct is the expression `WriteReport` is
built from. Deleted; the literal carries the claim and the exclusions carry the rest.

#### The sweep's own surface was narrower than the surface it declared — corrected 2026-08-08

Third artefact in a row landing inside the class it was built to close, and the first two rounds of
mutation could not have found it: **every mutation offered as confirmation acted at whole-assert or
whole-module granularity, and both defects live below an assert and inside the counter.**

**The loop.** An unconditional `break` sat outside the `if hit:` block, so only the first `Compare`
in each assert was examined. **The plant that was recorded here established nothing and is replaced,
2026-08-08:** it used a confirmed instance's *exact* expression as a second conjunct, which unparses
to a string already in `PINNED` for that module, so a set-keyed record was blind to it under the
broken net and the repaired one alike — confirmed against both. The discriminating plant is a
**novel** expression in the same position, `receipt.checked_at == drift.latest_stamp(home)`: green
under the restored `break`, red without it, naming the new match. The repair holds; the evidence
first offered for it did not.

**The counter.** `for func in ast.walk(tree)` yields nested `FunctionDef`s, and the enclosing
function's own walk has already reached their asserts — so one assert was counted and examined
twice. Measured: 633 walked against 632 distinct, the duplicate `test_rebuild.py:250` in `_resolve`
nested inside `_resolver_for`. Both are one decision about what "the surface" means and are
converged together; the floor was denominated in the inflated number, so it moves in the same edit.

**The floor.** `asserts >= 600` against 633 tolerated deleting a twentieth of the suite's
assertions — the case its own failure message names. Re-denominated at the exact current surface, 19
modules and 632 asserts, with the same discipline `PINNED` already carries: a legitimate reduction
lowers the number in the change that makes it, and additions never trip it.

**Three edges were covered although all three measure zero today** — an `AsyncFunctionDef`, an
assert outside any function, a `.py` file in `tests/` that is not `test_*.py`. Covered because the
declaration says *every assertion in `tests/`*, and a surface that silently excludes a shape belongs
to this class whether or not the shape is currently present.

**The counts did not move, and that was pre-registered as the outcome hardest to read** (`ROADMAP.md`
§ Pre-registration: what repairing the sweep's own surface would mean). Matches stayed at **82**,
identical set, 0 added and 0 gone; asserts fell to 632 exactly as predicted; modules stayed at 19.
Under that outcome every number is the same one the defective net produced, so nothing in the output
distinguishes a repaired net from a broken one — **only planting does**, which is why the net was
split so it can be run over synthetic source. `PLANTED` carries a second-comparison instance, a
nested-function assert, an async assert, a module-level assert, a call on the left-hand side, and a
Pass D shape; `test_the_net_reaches_every_granularity_it_declares` asserts what the net must find in
it, and that expectation caught two of my own errors before the net did — a miscount of the planted
asserts, and a case written as two matching comparisons that were `call == literal` and match
neither pass.

**Nine granularities at which the examined surface can shrink, one mutation each, all nine caught:**
module dropped; a function's asserts skipped; every fifth assert skipped; only the first comparison
examined; only the left side allowed to carry the call; nested asserts counted twice via the old
walk-every-function structure; `AsyncFunctionDef` bodies skipped; module-level asserts skipped; the
glob narrowed back to `test_*.py`.

#### `INSTANCES`' evidence was prose nothing re-ran — corrected 2026-08-08

`test_every_classified_instance_is_still_present` bound the third element to `_evidence` and never
read it, so *"archived_sequences → found[:-1]: whole suite green"* was asserted by the record and
checked by nothing. Changing `drift.run` to derive `sequences_checked` from a source the mutation
does not shorten would have left the sentence intact, the module green, and the record holding a
mutation result that no longer held.

**Whether it is re-runnable was established by building it, not decided by judgement, and the cost
is measured rather than estimated.** Copying the repository without `.venv`, `.git` and the caches
costs **0.08 s** with `__pycache__` carried (1.22 s cold); one whole-suite run inside the copy,
self-deselected to avoid re-entry, **12.4 s**; one module **1.3 s**; one test **0.3 s**. The five
runs the four instances require total **~15 s**, taking the suite from ~9 s to **26.0 s measured**.
That cost is paid: the record is now true rather than asserted.

One reduction was taken and is named rather than absorbed — `content_hash`'s *"suite red elsewhere"*
is checked against `tests/test_raw_store.py` rather than the whole suite. That saves ~12 s and makes
the claim **more** precise, since it names where the mutation is caught instead of asserting that
somewhere does. Both directions of the mechanism were mutation-tested: deriving `sequences_checked`
independently makes the evidence test fail with the row named, and an `old` text that no longer
occurs exactly once fails before any run, because evidence pointing at code that has moved describes
a mutation nobody can apply.

**Corrected 2026-08-08 — "with the row named" was true by accident.** The two `test_drift.py` rows
shared one `Evidence`, and the consumer sorted by `(module, source)` and skipped an `Evidence`
already seen; `archive_digest` sorts before `sequences_checked`, so a change bearing on the
*`sequences_checked`* row failed naming the *`archive_digest`* row, with an instruction that was
wrong for the row it named. **Separability was established by running rather than argued:**
`archive_digest` is called by the second assertion and not the first, and mutating its truncation
leaves the whole suite green — so each row now carries a mutation of the code its own value depends
on, the de-duplication is gone, and the same change now names `sequences_checked`. The cost of a
fourth distinct mutation is one more whole-suite run in a copy, measured at **30.2 s for the
module** against 26.0 s before, and the whole suite at **36.7 s** against 24.5 s.

#### The columnar write cost the same per row as the graph write it cited — 2026-08-08

`bzk/quant/store.py`'s first `write_cells` used `executemany` and its docstring named §8's
per-statement graph measurement (4.45 ms) as the reason to batch. It then cost the same thing:
**165.2 s for 48,696 cells, 3.4 ms each**, taking the rebuild from **69.0 s to 235.2 s** — the
pre-registered outcome 4. `executemany` is one round trip per row against the primary key's index;
it is a loop with a shorter spelling, not a bulk path.

Replaced with a single `INSERT OR REPLACE … SELECT` over a registered polars frame: **1.43 s** for
the same 48,696 cells. The semantics are unchanged — the upsert is still per key — so this is not
speed traded for the convergence I9 needs.

**The rebuild figure that followed is withdrawn, 2026-08-08.** This said the rebuild *"returns to
62.2 s"* — a word asserting restoration for a number below its 69.0 s reference, and a number 0.1 s
inside a band 13.8 s wide. Three rebuilds per tree: pre-layer 68.1 / 64.7 / 58.4, current
74.5 / 59.0 / 57.6. **The within-tree spread is 9.6 s and 17.0 s**, so the instrument cannot resolve
a 0.1 s margin or place a single run in the band at all, and the tree doing more work has the lower
median. The 165.2 s and 1.43 s attributions are unaffected — they differ by two orders of magnitude
and by a mechanism that was isolated — but the end-to-end rebuild clock says nothing either way.

Two things worth carrying. **The attribution was measured, not guessed**: adapter `parse` is 3.45 s
and the write was the other 165 s, so there was never a question of which half to look at. And
**citing a measurement is not the same as heeding it** — the docstring quoted the right number and
the code did the wrong thing, which is why the number is now in the docstring beside what it cost.

#### I11 is met for one of the two live subtypes, not both — corrected 2026-08-08

**This paragraph opened with *"Met for the two live observation subtypes"*, which is the unqualified
claim in its strongest form sitting directly above four lines that contradict it.** A reader taking
the first sentence — which is what a first sentence is for — got the opposite of what the paragraph
went on to say. Corrected by moving the line to the paragraph rather than the paragraph to the line.

**Met for `SiteObservation`. Not met for `ProteinObservation`,** which has its table,
`protein_values`, and its `quant_ref` path, and **no adapter that writes either** — `perseus.py` emits `ProteinObservation`
nodes and no cells, so `quant_ref` is null there. That is the violation state the column exists to
show, and it is visible rather than hidden. `PeptideObservation` and `EnrichmentObservation` are
deferred subtypes with no table at all, so I11 does not reach them.

**Re-checked 2026-08-10 and the verdict is unchanged, with one clause of it now false.** *No
adapter that writes either* is out of date: `bzk/adapters/maxquant_protein_groups.py` exists, is
tested, and run offline over `HAP1_USP18KO_proteinGroups.txt` emits 4,797 `ProteinObservation`s with
`quant_ref = 'protein_values'` and **67,158 cells**. The rest stands, and for a reason upstream of
the adapter: **the ingestion did not run and I11's protein half is still unmet.** That file's
fourteen quantitative columns are the *proteome* run and the curation record's twelve `Sample`s are
the *diGly* run, sharing no member, so there is no `Sample` to key a cell to — and authoring the
mapping from column names is what I8 forbids being presented as the submitters' design. `ROADMAP.md`
§ *Outcome: the MaxQuant protein adapter* has the measurement and the reasoning. Until a curation
record for the proteome run exists, `protein_values` holds **0 cells** and `ProteinObservation` has
**0 nodes** — the same state as before, now with the adapter no longer the reason.

#### Two measurements whose records were larger than what they established — 2026-08-08

**A line-ending count taken through a text read.** A 2026-08-08 measurement reported the PXD018299
deposit as LF and contradicted `ARCHITECTURE.md` §3's *"CRLF throughout, zero bare LF"*; the
contradiction was filed as incidental and left. Re-measured properly — digest-confirmed through
`raw_store.verify`, then `read_bytes` — the deposit is **2,759,052 bytes, 2,342 CRLF, 0 bare LF, 0
bare CR**. §3 was right and the new count was the artefact: it used `Path.read_text()`, which opens
in text mode with universal newlines and translates CRLF to LF *before* anything can count it. The
same bytes report 0 CRLF through that path. Eight artefacts rest on §3's claim and **none needed
correcting**; the one thing that needed correcting was the measurement. Recorded beside §3 as well,
because that is the line the next reader will doubt and the wrong way to doubt it is one function
call away. No guard: this is a measurement, not a class.

**A wall clock closed against a band it cannot resolve.** The rebuild was recorded at 62.2 s against
a 69.0 s ± 10% band — 0.1 s inside the lower edge, converting a declared outcome 4 into
prediction-met — and described as *"returns to"* a figure it sits below. Three rebuilds per tree:
pre-layer 68.1 / 64.7 / 58.4, current 74.5 / 59.0 / 57.6. **Within-tree spread is 9.6 s and 17.0 s
against a 13.8 s band and a 0.1 s margin**, and the tree that does more work has the *lower* median.
The clock prediction is withdrawn as **not established either way**, and the 6.8 s "improvement" is
run-to-run variation with nothing to attribute. The pre-registration stated a test method for the id
diff and none for the clock, which is how a single draw came to close a prediction.


#### Where a gene symbol lives — decided 2026-08-08, and what stopped it landing

**Four questions; three were already answered by documents and only one was open.**

*What carries the symbol.* `Gene.symbol`, not `Protein.name`. §4 gives `Gene` a `symbol` column
reading *"HGNC approved symbol"*, so routing UniProt's `geneName.value` onto `Protein.name` would
make that column redundant — two homes for one fact. `Protein.name` was uncommented in the DDL and
is now stated: UniProt's recommended **protein** name. **What it forecloses, said rather than
discovered:** target identification cannot be answered from `Protein` alone, so it stays on the
deposit's `Gene names` until `Gene` is minted — and swapping in `Protein.name` would be reading a
description where a symbol is meant, the exact error §6 records costing fourteen silent misses.

*Property or inference.* A plain property. It is an authority's own field copied at resolution time,
as `sequence` and `sequence_version` are, and the platform chooses nothing in copying it. ADR-0024 is
the precedent and it runs this way: it **rejected** *"the promotion is an inference and is recorded
as one"*, at the cost of a spurious `ProteinAssignment` basis row and a conflict with I14. One
asymmetry named rather than left: the pinned-cache-plus-drift protection keys on `sequence_version`
and **nothing keys on a name**, so a renamed protein is invisible to `bzk drift` — a limit of the
protection, not an argument for the inference machinery, which records who asserted a thing and not
when it changed.

*Which component owns it.* Already answered — `ARCHITECTURE.md` §2 declares `resolve/nodes.py` as
*accession → `Protein` + `ProteinSequence`*, and a fact UniProt asserts about an accession arrives on
the `Resolution` that module consumes. Checked rather than treated as open, and it was not open.

*`Gene` and `ENCODES`.* Reported, not built (`ONTOLOGY.md` §11 Q12). **The prompt's premise for this
one was half wrong and the correction matters:** the cached entry files cannot be read for an HGNC
cross-reference, because `_load_entry` writes `asdict(_Entry)` — eight fields — and never stores the
payload. So the question was answered by one live fetch instead: UniProt **does** carry it
(`{"database": "HGNC", "id": "HGNC:7532", …}` for `P20591`), 238 cross-references across 81
databases. **No new authority and no second network dependency.** What is missing is on this side.

**Measured starting state, and a shortfall worth its own line.** 4,561 `Protein` nodes, 0 named, 0
`Gene`; 2,261 cached entry files, 2,128 carrying a `gene`. Of the graph's 4,561 accessions only
**3,254** would get a symbol from cached bytes — **1,307 short**, of which 1,180 have no cached entry
at all. That is not cache decay: the site adapter mints a `Protein` for every candidate accession
while resolving only the razor picks, so a third of the graph's proteins were never resolved. Any
future `Gene` minting inherits that shortfall, and it is a property of the adapter's resolution
policy rather than of the cache.

**One stale code comment withdrawn.** `resolve/nodes.py` said *"the resolver reports neither, and
filling them from `gene` or an assumption would be inventing"*. Half false: `Resolution.gene` exists
and is populated on every `ok` path. The conclusion for `name` survives — for a reason the comment
did not give — and `organism_taxid` genuinely is unreported. It now reads as a routing decision
rather than an absence.

#### Minting `Gene` — attempted 2026-08-09, and stopped with a reason rather than a partial table

**Two contradictions settled in the key before anything was built.**

*The worked example named the wrong gene.* `ONTOLOGY.md` §9 read `Gene hgnc:5699 (MX1)`, and
`HGNC:5699` is `IGHVIII-38-1`, an immunoglobulin heavy variable pseudogene. MX1 is `HGNC:7532`,
whose `uniprot_ids` is `['P20591']` and so agrees with the `Protein` line beside it. Both measured
against `rest.genenames.org`. **The unmeasured one was `hgnc:5699`**, and its provenance is
visible in the document: §4's per-node example table copies §3's example verbatim in all six rows
except `Gene`, so the stray value had two homes and §9 inherited it from one of them. The failure
mode is one level in from the rule that was supposed to prevent it — *"reference identifiers are
real"* was **true**, and the claim made with the real identifier was false.

*The spelling was underdetermined, and the rule was too narrow to determine it.* §4 said the local
part *"keeps its authority's casing"*, which says nothing about a prefix that is missing rather
than mis-cased; §3's map wrote bare `hgnc:4053` while HGNC issues `HGNC:4053`. Settled as
**`hgnc:HGNC:7532`** and sharpened at the rule: the local part is the authority's identifier
**rendered verbatim**, which is what §4's own `chebi:CHEBI:15377` and `go:GO:0032020` examples
always showed. Nine of §3's ten rows already complied; `hgnc` was the one that did not, and the
alternative reading needed one authority declared exempt with no reason available to state. Guarded
in `keys.check_curie_case`, not recorded as prose — three spellings were accepted before it
(`hgnc:7532`, `hgnc:HGNC:7532`, `hgnc:hgnc:7532`), in the field that *is* a gene's identity, and the
guard is free only while the table is empty. **`chebi`, `go` and `mondo` were guarded in the same
change**, because the sharpened rule determines them too and the case for deferring them — no
nodes, node types out of scope — is word for word the case that left `hgnc` open until it was not.

**Why `Gene` was not minted, established rather than preferred.** The prediction registered in
`ROADMAP.md` before any of this ran was that it would not be, with a falsifier — *if any route
mints `Gene` from an input that already exists, the builder is written*. No such route exists:
tier-1 entry files hold the eight-field parse and **0 of 2,261** hold a cross-reference; tier-2
holds bare sequence with no FASTA header; `raw/` and the curation export hold symbols, not ids. The
identifiers themselves are not the problem — sampled coverage is 40/40 Swiss-Prot, 37/40 TrEMBL,
0 of 78 inactive. Capturing one means re-writing `entry/{canonical}.json`, and **that path's key is
itself an open item** (§8, above): answering Q12 by re-fetching 2,261 entries would replace the
snapshot every current `sequence_version` came from, as a side effect of a gene build.

**Q12's recorded cost was wrong, in the direction that mattered.** It said widening `_Entry`
*"re-fetches every cached accession"*. Measured against a copy of a real cache file with a session
that raises on any call: a **defaulted** field loads `P20591` clean with `hgnc_id=None` and **no
fetch**; only a **required** field invalidates the cache and refetches. So the cheap-looking option
is the dangerous one — it produces a column reading *this gene has no HGNC id* on 2,261 entries
where it means *this was never captured*, which §3 classifies as a `contingent` absence and
ADR-0021 forbids in an identifying position.

**What a `Protein` with no `Gene` would have to mean** is recorded in Q12 rather than deferred to
the builder: on the current graph the absence has **four** distinguishable causes — 1,180 never
resolved, 72 resolved to an inactive entry, 127 with no `gene`, ~78 with a gene but no
cross-reference — and a missing node records none of them.

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
  ~~**Unenforced**~~ **All three enforced 2026-08-07**, with `maxquant_sites.py` — the trigger
  fired as written. `_check_I2` now runs in four clauses, and each has its red case in
  `tests/test_invariants.py` plus a mutation. One thing the note above got right and is worth
  keeping: the residue clause **skips a change-set that carries no `sequence`**, because re-staging
  a site against a `ProteinSequence` already in the graph is legal and carrying the sequence again
  is not required. That skip is itself asserted, so tightening it later is a decision rather than
  an accident. What this does *not* close: the check runs over a change-set, so a site whose
  `SITE_ON` target is already in the graph and *not* re-staged is unchecked by it — the adapter's
  own residue check is the first line, and this is the backstop the note called it.
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
- **data layer, partial.** **I11 met 2026-08-08 for `SiteObservation` only.** The obligation is
  *every observation keeps its per-sample matrix in DuckDB*, and `ProteinObservation` does not:
  it has a table and a `quant_ref` path and no adapter that writes either. Restating the
  obligation and then declaring it met was the overclaim — the words *every observation* are the
  ones the state falsifies.
- **OP — operational, partial.** **I9** (reproducible rebuild — exercised by `rebuild.py` for schema
  recreation; full regeneration pending adapters).

---

## 9. Delete this file

Once the resolver and the Perseus adapter exist and the rebuild runs, everything here is either obsolete or has migrated into a document that owns it. A handoff note kept past its usefulness becomes a second, stale source of truth — which is the one thing `CLAUDE.md` forbids.
