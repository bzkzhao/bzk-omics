# REVIEWER HANDOFF — 2026-10-07

**Public version.** This file supersedes `notes/REVIEWER-HANDOFF-2026-10-05.md` as the starting
point. That file stays as the record of the days before.

**What is not restated here.** Items the earlier handoffs carry, which this session did not touch,
are not repeated. Read this file's §6 and §7 alongside:
- 2026-10-05 §7, open items (this file's §7 says what changed);
- 2026-10-04 §7, open items;
- 2026-10-03 §6–§8, roadmap tensions, open items and caveats.

**Line references** are to `main` at `a83a3f7` (`ONTOLOGY.md` v1.45). `bzk/`, `ONTOLOGY.md` and
`data/` are byte-identical to `ebc0750`, and `tests/` differs only in `test_decision_index.py`'s
pins. Re-verify before citing. Module names are given with their package path throughout, because
two modules are named `store.py` (`bzk/ontology/store.py` and `bzk/quant/store.py`) and only the
first is on the write path.

**Dating.** The session ran from 2026-10-05 to 2026-10-07. Runs are dated by their position in the
commit chain.

**ADR-0038 is the dated home for every number this session produced** — its *Measurements*, its
*Results* (S1, at `4d6a23f`) and its *Results — PV-S3 and ORIGIN* (at `05f9f3e`). This file
produces no new figures. Where it states one, it names that home.

---

## 1. Where things stand

| Item | State at `a83a3f7` |
|---|---|
| `main` | `a83a3f7`, pushed. Eight commits since `ebc0750` (§2) |
| `ONTOLOGY.md` | v1.45, unchanged this session |
| Checks | Run at `a83a3f7`, targets per `CLAUDE.md` l.96: `pytest` **908 passed, 14 skipped**; `pytest tests/test_schema.py` 20 passed; `mypy bzk tests` clean over 117 files; `ruff check bzk tests` and `ruff format --check bzk tests` clean |
| Untracked | On bzk's Mac: `notes/prompts/22-walk-two-route-independence.md`, still deferred by decision (10-05 §4 item 4) |
| ADRs | 37 files: **25 Accepted**, 9 Proposed, 3 Superseded |
| ADR-0038 | **Accepted**, as it stood at `59bb0d2`, in `a83a3f7`. D6 refuted by PV and kept in the text; **D6-revised accepted in its place**. **Nothing built** |
| ADR-0036 | D5's enforcement site and D7's scope are amended by ADR-0038; D2, D3 and D8 built (10-05 §1) |
| Graph on bzk's Mac | Built at `190e696`; current, since no `bzk/` change has landed since. 1,362 results, all in one contrast (ADR-0038 *Results*) |
| Content store | PXD055843 S1 and S3 both present under their recorded digests (S3 confirmed `already_present` on 2026-10-07) |
| PXD055843 ingestion | Still blocked: the PI's imputation answer and I15's seed, recorded as `data/curation/analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` `unresolved[1]`, which states the block. The placeholder rows (§7) are handled once prompt 31 builds |

## 2. What this session did

All eight commits were landed by bzk from his Mac with `git am`, each checked against a tree hash
computed in the reviewer's clone before pushing.

| Commit | What |
|---|---|
| `8ed075a` | ADR-0038 landed `Proposed`, with its instrument `notes/scripts/measure_adr0038.py` (M1–M10) |
| `27b8dbc` | PV instrument: refuses an absent column, prints `PV0`. As landed, a missing column would have printed a vacuous pass |
| `923ba7b` | Review R2: the Perseus tolerance fixed at **1e-3 before PV ran**, on single-precision storage read from two public builds of Perseus' plugin API |
| `4d6a23f` | Review R1: platform producers read raw columns. R1's first ground (row convergence) was refuted and recorded; R1 stands on M11 and unmeasured value conventions |
| `a458628` | Mac results: results per contrast held; **PV refuted D6**; the 27 placeholder rows found by two exploratory diagnostics, committed byte-identical |
| `05f9f3e` | D6-revised (with bzk's review folded in), and its PV-S3 and ORIGIN pre-registrations, public before either ran |
| `59bb0d2` | Mac results: **PV-S3 held on every line**; ORIGIN held, with its weak discriminating power recorded |
| `a83a3f7` | Accepted by bzk; status pins 24/10/3 → 25/9/3 |

**What ADR-0038 decides,** in one line each (the record is authoritative):
- **D1.** Each contrast declares its arms by mapping key; the loader refuses bad arms and unknown
  contrast-entry keys.
- **D2.** I22 at the loader, at mint. Background enrichment (IP vs control) admitted;
  `isotype_control` added; a control is never the numerator.
- **D3.** Same-string IP-vs-control contrasts separated by distinct labels: 0 ids move, against
  every result for the identity options.
- **D4.** `NUMERATOR_SAMPLE` / `DENOMINATOR_SAMPLE` edges, non-identifying. **Conflicts with
  ADR-0023's guard (§4, §6.2).**
- **D5.** Producers read columns only through each format's binding, raw columns only.
- **D6-revised.** Perseus proves its binding by recomputing the Difference on every tested row;
  untested rows are recognised from the statistics columns and mint no result.
- **D7.** I4 labels per grain, kind and state; protein-grain results must be `not_applied`.
- **D8.** Every contrast, required.

## 3. Dated home

None here. ADR-0038 holds every figure this session produced (header). The Mac commands and their
verbatim outputs are in the same record.

## 4. Corrections

**To ADR-0038 (Accepted, so corrected by the next record, ADR-0039).**
- *Implied changes* (l.504–505) says `tests/test_schema.py` "moves with §5". It does not: D4's two
  edges share endpoints and multiplicity, and ADR-0023's guard refuses that. Measured in a scratch
  clone: 2 failed, 18 passed. The landing verification never ran the DDL. §6.2 sets out the
  decided fix.

**To the 2026-10-05 handoff.**
1. **§6 step 2** planned prompt 29 as ADR-0036 D5/D7 enforced at `bzk/analysis/differential.py` and
   `bzk/adapters/perseus.py`. Superseded: at those sites I22 would have run over an empty set, because no
   producer binds an arm to a `Sample` (ADR-0038 *Context*). Prompt 29 is now §6.3.
2. **§7's "unguarded mirror"** moves into prompt 29.
3. ADR-0036 D5 cites `bzk/analysis/differential.py` l.39–40 and l.119, removed by `767e6e4`. Recorded in
   ADR-0038 *Context*; ADR-0036 is not edited.

**To this session's own working papers.** The plan's revisions 1–3, the checker and bzk's review
cited ADR-0038 at l.497 and l.389. Those were the lines in the drafting clone; at `a83a3f7` they are
l.504–505 and l.399, and this file uses the current numbers.

## 5. How this session ran

**Pre-registration did its job twice.**
- **PV refuted D6 as registered, and the verdict stood.** The tolerance was not loosened. The
  diagnostics that explained the failure were run afterwards, labelled exploratory, and committed
  byte-identical. They shaped D6-revised; they were not counted as evidence for it.
- **D6-revised was then tested on a file that did not shape it** (S3), with both candidate
  bindings — 3 v 3 IP and 4 v 4 with beads — registered and exactly one predicted to agree.

**Defects in the reviewer's own pre-registrations, caught before the runs:** a vacuous-pass path
in the PV instrument (`27b8dbc`); the PV outcome paragraph had the PV4 case backwards, and PV4's
"exactly one holds" was false of the expected case (both fixed in `923ba7b`).

**The build plan went through three audits** (§6 is revision 3, with a fourth pass folded in).
- Revision 1 → 2, the checker: ten findings, all verified. Four would have broken a prompt: D4
  against ADR-0023's guard; M0 and `tests/test_rebuild.py` moving; a second use of `CONTRAST`; and P2
  citing refuted PV1. The four-point close had been narrowed to point 2.
- Revision 2 → 3, bzk: P0–P3 decided, P3 against the reviewer's recommendation; three
  corrections, all verified.
- Revision 3 → this file, the reviewer's clone at `a83a3f7`: six findings. Two material — half of
  bzk's own `tables_created` correction had been dropped in transmission, and prompt 31 carried no
  id pre-registration while its stated reason covered only results that are never written. Four
  smaller: P2's ground narrowed past the record's own, a false universal on authorship, a lost
  countable, and bare module names where two `store.py` exist. All six are applied below.
- A further pass on those six fixes found four more, each in a clause written to fix an earlier
  one: a named structure that does not exist (`Analysis` has no "excluded columns" — identity is an
  allow-list), an unmeasured trailer claim, and two misattributions between PXD055843's two
  `unresolved` lists. Applied below.
- **The common cause, named: three of revision 1's ten findings share it** — a clause cited by its
  label ("M0 unchanged", "PV1/PV2", "moves with §5") without re-reading what it now says. The
  checker counts this the fourth compound-clause narrowing in the series. The later passes add a
  second form of the same fault: **a correction extended past what was measured for it.** The rule
  taken from it, for every pass after this one: *measure the thing you add, not only the thing you
  were told about.*

**Mechanics.**
- **Landing by tree hash.** Every patch was checked by applying it to a fresh clone of the pushed
  parent and comparing trees. Commit hashes differ between clones; trees do not.
- **The reviewer's container reset twice.** Nothing was lost, because nothing was left unpushed.
- **A stop hook flagged a throwaway commit** made in the verify clone by a dummy committer. It was
  deleted; verification now uses `git apply --index` and `git write-tree`, which make no commit.
- **The reviewer does not push; bzk commits every change.** Authorship is not uniform across the
  series, and the three classes are measured rather than assumed:
  - the eight build commits `8ed075a`→`a83a3f7` are `author=Claude, committer=Zhekai Zhao`. Of
    these, **two carry a `Co-Authored-By` trailer — `59bb0d2` and `a83a3f7` — and six do not**;
    the trailer begins at the seventh commit of the series and does not mark the class;
  - the prior reviewer handoffs `ebc0750` and `d19a670` are `author=Zhekai Zhao,
    committer=Zhekai Zhao`, no trailer;
  - `190e696`, the run §1 cites for the Mac graph, is `author=Claude, committer=Claude`.
  So "each landing commit is bzk's" is true of the committer for everything this session landed,
  and false of the author throughout, and false of the committer at `190e696`.

## 6. Next — the build plan for ADR-0038, revision 3

**Decided by bzk on 2026-10-07:** P0 (a), P1 invariant, P2 after 31, P3 (i). Measured figures are
cited to their homes; figures below are predictions a prompt will pre-register.

### 6.1 Shape

| Step | Builds | Depends on | Ids that may move | Mac run |
|---|---|---|---|---|
| **ADR-0039** | P0 (a): ADR-0023's guard gains one pinned exception | — | — | none |
| **29** | D1, D2, D4, D8 — arms, I22 at mint, arm edges, `isotype_control` | ADR-0039 | **none** | cold rebuild + differential |
| **30** | D5 — producers bind through the adapter; D7's producer refusal | 29 | **none** | differential only |
| **31** | D6-revised — Perseus proof; untested rows counted on `Analysis` | 29 | **none** — the P3 field is non-identifying (§6.5), so the `Analysis` nodes already in the graph do not re-mint; no Perseus result is written | read-only parse of S1 |
| **32** | D7 — I4 labels; the untested-row display | 29, 31 | none | read-only query |

- 30 and 31 depend only on 29. 32 now depends on 31 too, because it carries D6-revised (c)'s
  display half (§6.6).
- **Every prompt closes with `CLAUDE.md` l.95–99's four-point report**: every check by name with
  its target; the change did what it claimed, with mutation evidence for every new guard; what it
  did not cover; any dropped instruction. 29 and 32 amend `ONTOLOGY.md` and 30 and 31 change
  adapters, so all four are critical nodes.
- This handoff lands first, as its own commit.

---

### 6.2 P0 — D4 against ADR-0023's guard. **Decided: (a).**

**The conflict, measured.** `tests/test_schema.py::test_no_two_relationships_share_endpoints_and_multiplicity`
(l.81–98) refuses two relationships with the same endpoints and multiplicity. D4's two edges are
both `Contrast → Sample, MANY_MANY`. With exactly those two DDL lines added after l.521 in a
scratch clone: **2 failed, 18 passed** — the shape guard, and the mirror test (expected, since
`bzk/ontology/schema.py` was not edited).

**Why it is real, not a test bug.** ADR-0023 wrote the guard as a proxy: same shape is taken to
mean *one fact under two names*. D4's two edges are two facts with one shape. ADR-0038 D4 cited
ADR-0023 for "two facts, two types", without checking the guard that ADR wrote. Both ADRs are
`Accepted`, and README's convention is that an Accepted ADR is amended only by a new record. So the
build cannot resolve this, and neither can a test edit on its own.

**Why (a) changes no decision** (bzk, verified at `a83a3f7`): ADR-0023's *Decision* section has
three numbered items — `SITE_ON` narrows, `MEASURED_AT` survives, `REPORTS_SITE` survives. The
shape guard sits under *Consequences*, as the assertion closing that class. Narrowing its scope is
therefore consistent with `Supersedes —` and README l.7.

**Option (a) — decided. ADR-0039 amends ADR-0023's guard; D4 stands.**
- The guard refuses a same-shape pair unless it is pinned as an exception, with the ADR that
  decided they are distinct facts. `NUMERATOR_SAMPLE` / `DENOMINATOR_SAMPLE` is the one entry,
  citing ADR-0038 D4. **The pin keys on the exact pair, its endpoints and its multiplicity**, so any
  other same-shape pair — a third `Contrast → Sample, MANY_MANY` edge included — still fails.
- The reverse-relationship guard (`tests/test_schema.py` l.101–125) is untouched.
- The precedent is `ONE_SIDED_SUPERSESSION` in `tests/test_decision_index.py` (l.73–82): pinned,
  so a **second** same-shape pair still fails loudly.
- Supersedes `—`, as ADR-0038 did for ADR-0036: it amends a guard's scope, not a decision.

**Option (b), not chosen.** ADR-0039 would amend ADR-0038 D4 to one edge, `ARM_SAMPLE`, with a
`side` property.
- The guard is untouched.
- But it reverses a decision accepted today, and D4's stated reason against it stands: every reader
  must filter on `side`, and forgetting the filter silently merges both arms.

ADR-0039 records ADR-0038's drafting defect (l.504–505) so a reader of ADR-0038 finds the
correction.

**ADR-0039's own landing**: `tests/test_decision_index.py` moves — files
37 → 38, Written rows 37 → 38, and the status count gains one wherever it lands (`Proposed` 9 → 10
if it lands for review, as ADR-0038 did). The guard's edit itself lands in prompt 29, together with
the DDL it permits; ADR-0039 only decides it.

---

### 6.3 Prompt 29 — arms, I22, edges (D1, D2, D4, D8)

**Scope:** `ONTOLOGY.md`, `bzk/ontology/schema.py`, `bzk/ontology/invariants.py`,
`bzk/curation/loader.py`, three curation records, `tests/` — **including `tests/test_schema.py`
under P0 (a), and `tests/test_rebuild.py`'s two pins** (below).

**ONTOLOGY and schema, both homes together:**
- §5 DDL after l.521: the arm edges as P0 decides. `schema.REL_TABLES` the same. Nothing in
  `IDENTITY`.
- l.119 `Contrast` row; `Sample` DDL comment (`isotype_control`; `antibody` NULL unless
  `role ∈ {'ip','isotype_control'}`); l.581 cites ADR-0038 D4; §8 mints **I22**; §11 **Q16**.
  Version 1.45 → 1.46.

**Loader:** D1's resolution and every refusal, including unknown keys in a contrast entry;
`LoadedCuration` carries arms and derived kind; the arm edges; `_SAMPLE_ROLES` gains
`isotype_control`; the R7 check widens; **the mirror guard** for `_SAMPLE_ROLES` / `_IP_MODALITY`
(`bzk/curation/loader.py` l.311–312) against the DDL comment (handoff 10-05 §7).

**Curation records:** PXD018299, PXD026748, PXD055843 gain arms in `contrasts_of_interest` as
ADR-0038 M4 prints them.
- `data/curation/curation_PXD055843.json` carries **eleven** `unresolved` entries, and **none is
  edited, resolved or renumbered by this prompt** — among them `[1]` s0, `[2]` the imputation seed,
  `[4]` arm order (P2, §6.5) and `[6]` which DIA-NN quantity the eighteen columns hold. Indices are
  zero-based, as the file stores them.
- The second `unresolved` list, in `data/curation/analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json`
  (four entries, none on arm order), is out of scope entirely. **Its `[1]` is the entry that states
  the ingestion block** — "this record cannot be ingested until one exists" — not the curation
  record's `[2]`, which states the I15 requirement and stops there. Both files carry a seed entry
  and an s0 entry, so neither is ever cited without its filename.
- §7's three PI questions map onto these entries with a gap, not one-to-one: **Q1** (imputation on
  S1 / I15's seed) bears on the analysis record's `[1]` and the curation record's `[2]`; **Q3** (s0)
  on the analysis record's `[0]` and the curation record's `[1]`; **Q2** (where the untested rows
  come from) bears on no `unresolved` entry in either file — it is new from ORIGIN. `[6]` is not a
  PI question. A resolution arriving from this prompt rather than from the PI would be a silent
  answer to a question that is still open.

**Tests:** each D1 refusal; each row of D2's table by a constructed `ip_ms` record (none exists on
disk, said so); the multi-error message; all four records load; mutation evidence for every new
refusal and for I22, bytecode disabled from the start.

**Pre-registration (rehearsed in a scratch clone before the prompt is issued):**
- **I1:** loader node ids, every record, every label — **0 moved**.
- **I2:** loader edges per record: PXD018299 40 → **52**, PXD026748 40 → **52**, shotgun **38**
  unchanged, PXD055843 57 → **63**. Nodes unchanged (18, 18, 16, 23). Computed at `a83a3f7`
  from the loader's current output plus 6 edges per contrast.
- **I3:** `tests/fixtures/pxd018299_curation_ids.json` unchanged (it pins node ids only).
- **`tests/test_rebuild.py` l.134 and l.138 move:** `tables_created` 58 → **60**; PXD018299's
  `(18, 40)` → **`(18, 52)`**.
- **Mac, Step A / Step B** as prompt 28 ran them; cold rebuild, because `rebuild` drops and
  recreates the stores (`bzk/rebuild.py` l.154, `drop_stores`):
  - ids: all 16 labels 0 gone / 0 new;
  - **M0 moves, by design**, from handoff 10-05 §3.3: 58 → **60 tables**; replay 18/40, 18/40,
    16/38, 23/57 → **18/52, 18/52, 16/38, 23/63**; edge statements 31,349 → **31,379**; node
    statements 32,793, observations 4,195 / 4,768, 48 refusals and `INCOMPLETE` unchanged.
  - graph: 30 arm edges; M1 `[4b]` unchanged.

#### P1 — where I22's check lives. **Decided: an invariant, `_check_I22` in `_CHECKS`.**
- **`_check_I22` does not exist at `a83a3f7`** — `I22` appears nowhere in `bzk/` or `tests/`. What
  follows states where it will run once this prompt builds it. It is a forward claim about the
  mechanism, not a property a reader can verify before the build.
- An entry in `invariants._CHECKS` runs at **every** `validate` call, not only the loader's.
  `invariants.validate` is defined at `bzk/ontology/invariants.py` l.882 and called at exactly five
  sites: `bzk/curation/loader.py` l.518, `bzk/ontology/store.py` l.120 (every graph write), and the
  three adapters — `bzk/adapters/maxquant_sites.py` l.408,
  `bzk/adapters/maxquant_protein_groups.py` l.442, `bzk/adapters/perseus.py` l.580.
  `bzk/adapters/base.py` l.121 names it in a docstring and is not a sixth. `bzk/quant/store.py`
  l.120 is unrelated prose about `executemany` cell writes.
- It runs non-vacuously wherever the arm edges are in the change-set: the loader's own, and the
  store write that replays it. Every adapter change-set stages `Contrast` without arm edges, so it
  passes vacuously there. That is sound while the loader is the only `Contrast` minter, and the
  prompt must say so.
- Handoff 10-05 §7 flags the same gap for D2/D3 ("enforced only in the loader … consider an
  invariant-level check before any IP adapter exists"); an invariant for I22 is that direction.
  The D2/D3 invariant itself stays out of scope.
- *Alternative:* a loader-only function, like `_check_sample_roles` — the shape handoff 10-05 §7 flags.

---

### 6.4 Prompt 30 — producers bind through the adapter (D5; D7's producer refusal)

**Scope:** `bzk/adapters/maxquant_sites.py`, `bzk/analysis/differential.py`,
`bzk/sources/pxd018299_differential.py`, `tests/`.

- `maxquant_sites` exposes (`Sample` id, quantity) → exact composed header or refusal, built on
  `QUANTITY_COLUMNS` (l.122). `_sample_columns` (l.128) accepts a sample if *any* family's header
  exists (l.147); the new function checks the family asked for.
- `pxd018299_differential.py`: delete `CONTRAST` (l.111) and `_intensity_columns` (l.258); arms
  from `LoadedCuration`, `Intensity` columns through the binding; raw columns only (R1).
- `site_change_set` takes arms and kind; refuses any kind but `condition`.
- **`CONTRAST` has two text uses, both changed**:
  - the `[4b]` header (l.382) prints the contrast's record id;
  - `DeclaredRun(label=…)` (l.510) becomes `Analysis.label`. `label` is not in `Analysis`
    identity (`bzk/ontology/schema.py` l.285–299), so no id moves, but the store writes
    `MERGE … SET` (`bzk/ontology/store.py` l.137–139), so **the Mac run overwrites `label` on the
    existing `Analysis`**. Pre-registered: the old and new label strings, and that this is the only
    property that changes.

**Pre-registration:**
- Container: for PXD018299's real header (`ROADMAP.md`'s 159-column line), the binding returns
  exactly ADR-0038 M7's six headers.
- **Mac:** pull, differential, `git status`:
  - `tests/fixtures/` byte-identical (the targets fixture carries no contrast string);
  - `[4b]` figures as handoff 10-05 §3.3 M1;
  - `DifferentialResult` ids 0 moved, 1,362 in `KO_IFN_vs_WT_IFN`;
  - the `Analysis` node's `label` changes as pre-registered, and nothing else on it.

---

### 6.5 Prompt 31 — the Perseus proof; untested rows counted (D6-revised)

**Scope:** `ONTOLOGY.md` and `bzk/ontology/schema.py` (the new `Analysis` field, P3),
`bzk/adapters/perseus.py`, `bzk/sources/pxd055843_perseus.py`, the six
`tests/fixtures/perseus_synthetic_*.txt`, `tests/`.

- **Nothing in `IDENTITY`.** The field is not added to `IDENTITY["Analysis"].fields`. Identity here
  is an allow-list — `schema.Identity` (l.211–223) has `fields`, `anchors`, `child_fields` and
  `authority`, and no excluded set — so a non-identifying column is non-identifying by absence. The
  field lands as a DDL column on the `Analysis` node table, in its `bzk/ontology/schema.py` mirror,
  and nowhere in `IDENTITY`.
- **PXD055843's curation and analysis records are out of scope for this prompt** except as P2
  below directs, and P2 edits exactly one entry:
  `data/curation/curation_PXD055843.json` → `unresolved[4]`. The other ten entries in that file,
  and all four in `data/curation/analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json`, are untouched.
- `DeclaredContrast` gains the arms; rule (a) on every row; rule (b), 1e-3, on every tested row;
  at least one tested row; reads the statistic column where present; a file with statistics and
  no sample columns is refused.
- Rule (c): untested rows mint no `DifferentialResult`. The external `Analysis` carries the
  per-contrast untested count (P3), and `PerseusIngestReport` reports the same count.
- Fixtures gain sample columns consistent with their Difference values, plus untested rows; 22
  `PerseusAdapter(` call sites in `tests/`.

**Pre-registration:**
- **`Analysis` ids: 0 moved.** The new field is non-identifying, so neither the differential
  `Analysis` nor either committed analysis record re-mints.
- **`tables_created`: unchanged at 60.** The field is a column on an existing node table, not a
  table. The figure is asserted in `tests/test_rebuild.py` — at l.134 at `a83a3f7`, which prompt 29
  edits, so cite the assertion rather than the line.
- **Query path: no rebuild required.** `bzk/query/graph.py` selects `Analysis` properties by name
  only — `a.id` (l.276, l.281, l.287, l.349) and `a.quantity, a.test, a.fdr_method` (l.373) — with
  no `properties(a)`, no `RETURN *` and no generic projection anywhere in the module. A Mac store one
  column behind the schema returns the same rows, so §6.6's container-only display holds on the code
  as it stands rather than by assumption. State in the prompt that this is checked, so that adding a
  generic projection later is recognised as breaking it.
- Container: constructed fixtures for every refusal and for the untested signature.
- **Mac, read-only parse of S1, no graph write** (PXD055843 stays blocked on the PI and I15):
  results that would be emitted 7,583, untested 27, binding accepted. **In-sample**: S1 shaped rule
  (a), so this shows the code reproduces the diagnostics, not that the rule is right.

#### P2 — PXD055843's `unresolved` entry on arm order. **Decided: edit it after 31's Mac run.**
The entry is `data/curation/curation_PXD055843.json` → `unresolved[4]`, "Which arm of the contrast
is the numerator". It is not in the analysis record, which has no arm-order entry.
- **What supports the declared order is the record's own ground, not the diagnostic.** `[4]` states
  it: the statistics columns carry the Perseus suffix `siUSP24_IFN_siCTRL_IFN`, marked **MEASURED
  HERE**, and Perseus writes numerator first.
- **Not PV1:** PV1 was refuted (ADR-0038 *Results*). The exploratory diagnostic in the same section
  (`a458628`, 7,583 of 7,610 rows agreeing in declared order, 9 reversed) corroborates the entry and
  is named nowhere in it. Both are kept; the measured suffix is primary.
- After 31, the **accepted** rule — not an exploratory script — will have confirmed the declared
  order on S1. The edit then cites that run as a third support, still noting it is in-sample, and
  does not displace the suffix. It is a curation-record edit with 0 ids moved (rehearsed), so it
  rides in whichever commit records 31's Mac results.

#### P3 — how untested rows are recorded. **Decided: (i), a per-contrast count on `Analysis`.**
- **(i) A count per contrast on the external `Analysis`.** The view finds untested rows by absence
  and must match the count. No new table. But the count must be keyed by contrast, and `Analysis`
  has no per-contrast field today, so this still needs a schema decision on its shape.
- **(ii) A marker per row:** a non-identifying edge `ProteinObservation → Contrast` carrying the
  `Analysis` id. "Which proteins were not tested in contrast X" becomes a direct traversal; the
  edge count is the check. One rel table, one ONTOLOGY row, and `tables_created` moves again.
- **bzk chose (i), for three reasons, each verified at `a83a3f7`:**
  1. **(ii) as drafted brings back D4's hazard.** The edge carries the `Analysis` id as a property
     every reader must filter on whenever two external analyses cover one contrast. That case is
     possible: an external `Analysis` anchors on `Dataset`, and `PerseusAdapter` takes a list of
     contrasts (`bzk/adapters/perseus.py` l.346). Forgetting the filter would merge two analyses'
     untested sets silently — the failure D4 rejected `side` for.
  2. **The record's rule is met either way** (D6-revised (c)).
  3. **There is nothing to traverse yet**, and both options are non-identifying: (i) → (ii) later
     is additive, (ii) → (i) drops a table.
- **What (i) means:** one non-identifying field on `Analysis`, mapping each `Contrast` id to its
  untested count. The view's derived count per contrast must equal it; where it does not, the view
  shows a mismatch error, never *not tested by the source analysis*. Both committed analysis
  records declare one `contrast`, so on present data the map has one entry.
- **For 31's rehearsal to settle, not a decision:** the field's representation. No column in the
  schema is a map type today. `Analysis.parameters_json` is the precedent **for representation
  only** — a JSON object canonicalized into a `STRING` (`ONTOLOGY.md` l.175). It is **identifying**:
  l.120 lists it in `Analysis`'s identifying fields and l.175 says so outright. The canonicalization
  precedent transfers; the identity status does not.

---

### 6.6 Prompt 32 — I4 labels; the untested-row display (D7; D6-revised (c)'s display half)

**Scope:** `ONTOLOGY.md` I4, `bzk/ontology/invariants.py`, `bzk/query/graph.py`, `bzk/ui/app.py`,
`tests/`.

- `_check_I4` (`bzk/ontology/invariants.py` l.386): a result with a `RESULT_FOR_PROTEIN` edge must
  be `not_applied`.
- Query layer derives kind and maps (grain, kind, state) to D7's table, no fallback; UI shows the
  label in the results-row mapping (`bzk/ui/app.py` l.240 is its neighbourhood). ONTOLOGY I4
  (l.903) widened; the code copy guarded against §8.
- **Untested-row display**: for each contrast an external
  `Analysis` carries, the view derives the observations with no result there and checks that count
  against the `Analysis` field (P3). Equal: they show *not tested by the source analysis*. Unequal:
  a mismatch error, never the label.

**Pre-registration:**
- Container: every committed `applied`/`native` fixture result is site grain (ADR-0038 M10).
- **Mac, read-only query:** all 1,362 results map to *stoichiometry-uncorrected*. Untested display
  is tested in the container only: no Perseus result is in the graph, and §6.5's query-path note is
  why the missing column is never read there.

---


### 6.7 After the build

- **Order item 3:** PXD018299's `ISG15_interactome` `.xlsx`, the first real IP ingestion —
  platform-run, IP vs IP. Needs a protein-grain internal differential writer and the protein-groups
  binding function (§7).
- **Order item 4:** PXD055843 S3, with its four bead controls. Blocked on the PI and ADR-0032 — a
  blocker set that differs from the deposit's own (§1: the PI's imputation answer and I15's seed).
  The paper's test excluded the beads (ADR-0038 *Results — PV-S3*), so the beads are free for a
  separate background-enrichment contrast.
- **Order item 5:** the laboratory's unpublished IP-MS data, run locally. **Nothing about that
  dataset enters the repository.**
- **Not scheduled:** the K425 hypothesis (10-05 §6 item 4) and prompt 22 (deferred).

## 7. Open items — what changed since 2026-10-05 §7

**New:**
- **Perseus placeholder statistics** (ADR-0038 *Results*, both sections). S1 carries 27 rows and
  S3 2 whose Difference, test statistic and −log p are `0` and q `1`. Today's adapter would
  ingest them as measured nulls. Prompt 31 builds the fix (D6-revised (c)).
- **Where untested rows come from: a question for the PI**, beside the imputation question. Did
  the S1 and S3 Perseus sessions run the test before imputation, or on a different valid-value
  filter from the methods'? ORIGIN supports the hypothesis only weakly (ADR-0038 *Results*). This
  one bears on no existing `unresolved` entry in either PXD055843 record.
- **ADR-0032 (Proposed) should take D6-revised (c) into its review** (ADR-0038 l.399).
- **`write_cells` over-reports a repeated key** (ADR-0038 M11): keeps one cell, reports the batch
  length. No current deposit triggers it. Its own prompt.
- **The protein-groups adapter drops a family it cannot reach from the mapping keys, silently**
  (ADR-0038 M8: the interactome's `Intensity n-m`). An I11 question for order item 3.
- **Q16** (to be minted in prompt 29): must an arm be one condition; are pooled control arms
  exempt?
- **A background-enrichment concordance basis value** is not minted; nothing consumes one yet.

**Changed:**
- **The unguarded mirror** (`_SAMPLE_ROLES`, `_IP_MODALITY`, `bzk/curation/loader.py` l.311–312) is
  now in prompt 29's scope.
- **D2/D3 enforced only in the loader:** P1 puts I22 in `_CHECKS`, which is the direction §7
  pointed; the D2/D3 invariant itself stays open.

**Closed:**
- 2026-10-05 §6 step 2, replaced by ADR-0038 and §6 here.

**Unchanged and still open:** the drift checker reporting failed fetches as drift; F-b
generalised; F-d; R6's prefix-only check; the stale tautology floor.

**Questions for the PI, collected** (none blocks the build; the first blocks PXD055843 ingestion).
Each names the file it is recorded in, because both PXD055843 records carry an `unresolved` list:
1. Did imputation run on S1 (I15's seed)? *(open since September.)* Recorded at
   `analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` `unresolved[1]`, which states the ingestion
   block, and at `curation_PXD055843.json` `unresolved[2]`, which states the I15 requirement only.
2. Where the untested rows come from (above). Recorded in no `unresolved` entry; new from ORIGIN.
3. s0 for S1's test. Recorded at `analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` `unresolved[0]`
   and `curation_PXD055843.json` `unresolved[1]`.
