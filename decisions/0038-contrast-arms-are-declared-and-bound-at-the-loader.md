# ADR-0038 — Contrast arms are declared in curation and bound to `Sample`s at the loader; I22 runs at mint; a producer reads only columns its arms bind; background enrichment is admitted

| | |
|---|---|
| Status | Proposed |
| Date | 2026-10-05 |
| Supersedes | — |
| Superseded by | — |

**It supersedes nothing.** It amends ADR-0036's **mechanism**, not its rules: D5's enforcement
site; R1/D4's refusal of a control arm; D2's closed `role` enum; D7's label scope. It also widens
the loader's rule R7 on `antibody`, built at `190e696`. ADR-0036 stays `Accepted` and is not
edited; the `Supersedes` row stays `—` because no decision of it is replaced.

Drafted against `ebc0750`. **Every number below was measured at `ebc0750`, in a scratch clone, by
`notes/scripts/measure_adr0038.py` (landed in the same commit as this file), unless it is marked as
a prediction or cited to another dated home.** The instrument's output is reproduced verbatim under
*Measurements*; this record is the dated home for those figures. Line references are to `ebc0750`.

This record decides representation, invariants and their enforcement sites. **It makes no
`ONTOLOGY.md`, `schema.py`, curation-record or code change.** The amendments are listed under
*Implied changes, described and not made*. Landed by the reviewer's own session, so the round-trip's
independence rests on review, not on the landing.

---

## Context

**ADR-0036 D5 cannot be built as accepted, because no producer binds an arm to `Sample` nodes.**
D5 says I22 runs *"where columns are bound"* — the differential writer and the Perseus adapter — and
that a graph-checkable form *"waits on a `Contrast`–`Sample` linkage"*. Measured against the code:

- **The differential writer no longer takes condition strings.** D5 cites `differential.py`
  l.39–40 and l.119; `767e6e4` (ADR-0029 E) removed both, and `site_change_set` now receives the
  loader's node whole. The citations are stale; the defect they pointed at moved, not closed.
- **The PXD018299 differential picks columns by token.** `CONTRAST = ("KO_IFN", "WT_IFN")`
  (`pxd018299_differential.py` l.111) feeds `_intensity_columns` (l.258, called at l.319–320),
  which builds `Intensity KO_IFN_1..3`. The curated `Sample`s are keyed to `Ratio mod/base …`
  columns. Nothing ties the token to those samples. M7 shows it picks the right six columns, which
  is a coincidence of MaxQuant's naming, not a binding.
- **The Perseus adapter binds a contrast by column suffix and reads only aggregate statistics**
  (`DeclaredContrast`, `perseus.py` l.253; `contrast_ids[declared.column_suffix]`, l.502;
  `_contrast_reader`, l.756). The suffix names no sample.
- **Curation contrasts are condition strings that do not compose from the samples' fields** (M2).
  `'USP18-/- + IFN'` equals no `genotype`, no `treatment` and no `genotype + treatment`. Where a
  string does equal a field it over-selects: `'WT'` matches **6** samples for a 3-sample arm.
- **Substring matching fails in both directions** (M2). `'USP18-/- + IFN'` is a substring of **0**
  mapping keys; PXD055843's `'siUSP24 (+ IFN-B)'` is a substring of **9**, the 3 intended plus the 6
  `NO USP2` / `WITH USP2` columns.
- **`Contrast` has no relationship to `Sample`** (M1): the only two tables touching it are
  `RESULT_IN_CONTRAST` and `CONTRAST_IN_EXPERIMENT`. So `ONTOLOGY.md` l.581's *"the provenance chain
  from `DifferentialResult` through `Contrast` to `Sample` terminates in a recorded curation event"*
  is false of every result in the graph.

**So I22 as accepted would run over an empty set** and pass on every input, which is the shape
`CLAUDE.md`'s point 2 records twice: a check reporting clean because it never ran.

**D7's enforcement already exists; its display does not.**
- `_check_I4` (`invariants.py` l.386) iterates every `DifferentialResult` (l.389) and reads no grain
  edge (M9). It is already wider than `ONTOLOGY.md` l.903's *"on a site"*.
- **No I4 label is implemented anywhere** (M9). `stoichiometry-uncorrected` appears in `bzk/` once,
  in a comment (`differential.py` l.148); `abundance-uncorrected` appears nowhere. The UI shows
  the raw state (`ui/app.py` l.240). Protein-abundance results have no label even in prose.

**The aim this record serves** is general IP-MS ingestion: proven on public data first (PXD018299's
interactome, then PXD055843 S3), then run locally on unpublished data that never enters the
repository. That aim is why background enrichment is admitted here and not deferred again.

---

## Decisions

### D1. Arms are declared in curation, by mapping key, on every contrast.

Each `contrasts_of_interest` entry gains **`numerator_samples`** and **`denominator_samples`**:
non-empty lists of the record's own `mapping` keys, verbatim.

- **A mapping key names a `Sample`, not a column the producer reads.** That is what dissolves the
  Intensity-vs-Ratio case: PXD018299's samples stay keyed by `Ratio mod/base …`, and which column a
  producer reads for a given quantity is D5's business, not the key's.
- **The loader resolves each key to the `Sample` id it already minted, and refuses:**
  - a key absent from `mapping` (exact membership, no normalisation);
  - an empty arm, or a key repeated within an arm;
  - a sample in both arms;
  - two entries in one record with the same (`numerator`, `denominator`) pair (D3);
  - an entry whose `numerator` equals its `denominator` (D3);
  - **an unknown key in a contrast entry.** Measured (M3): today the loader accepts
    `numerator_sampels` and drops it, minting contrast nodes identical to the unmodified record's.
    Without this refusal a misspelled arm field loads clean and D8 is defeated silently. The
    recognised set is `id`, `numerator`, `denominator`, `numerator_samples`,
    `denominator_samples`, `note` (all five live entries carry `note`).
- **`LoadedCuration` carries the resolved arms beside each `Contrast` node** (sample ids per arm and
  the derived kind, D2). Producers take the arms from there, as they already take the node
  (ADR-0029 E), and never from a caller.

Measured (M4): all 5 existing contrasts declare cleanly, 3 against 3, no overlap. Every arm carries
one value for every `Sample` identifying field but `replicate`. The declarations imply **30**
`Contrast`–`Sample` edges.

### D2. I22 is enforced by the loader, at contrast mint. Background enrichment is admitted.

**I22 — a contrast's arms are role-consistent.** Kind is derived from the anchor's `modality` and
the arms' roles, and never stored (ADR-0036 D4's rule, kept):

| Experiment | Numerator arm | Denominator arm | Kind | Permitted |
|---|---|---|---|---|
| not `ip_ms` | every `role` NULL | every `role` NULL | `condition` | yes — all 5 existing contrasts |
| `ip_ms` | all `ip`, one `bait` | all `ip`, the same `bait` | `differential_association` | yes |
| `ip_ms` | all `ip`, one `bait` | all one control role | `background_enrichment` | **yes — lifted here** |
| `ip_ms` | any control | any | — | no: a control is never the numerator |
| `ip_ms` | mixed roles in one arm, or two control roles in one arm | | — | no |

The first row's NULLs are already guaranteed by the loader's rules R1–R7 in `_check_sample_roles`
(l.315; built at `190e696`, handoff 10-05 §2). I22 adds the pairing.

**Why the loader and not the producers.** D5's sites see columns, not samples. The loader is the
only `Sample` minter and the only `Contrast` minter (ADR-0029 E), so it is the one place both arms'
samples and the experiment's `modality` are in hand. One site cannot disagree with itself.

**The lift of ADR-0036 R1's refusal is deliberate.** R1 refused any arm containing a
`no_antibody_control` sample *"until a record adds roles to `Contrast` identity"*. That condition
named a mechanism because, without declared arms, identity was the only place a contrast could say
what it compares. D1 and D4 now say it, and I22 fixes orientation, so R1's purpose is met without
its mechanism (D3 measures why the mechanism itself is rejected). The grounds for admitting the
design at all:

- **It is the standard IP-MS design.** Affinity purification is scored against negative controls —
  an isotype IgG or a beads-only pull-down — in the field's standard scoring practice (SAINT, Choi
  et al. 2011; the CRAPome, Mellacheruvu et al. 2013). A platform that ingests IP-MS generally and
  refuses the control comparison refuses the common case.
- **PXD055843 S3 carries it.** Columns 1–4 are one antibody-free bead control per condition,
  columns 5–16 three IP sets per condition (`walk/SURVEY-public-IP-tables.md` §7, l.383–396). The
  methods name the beads as the negative control; no reported analysis uses them (ADR-0036,
  Context).
- **What a deposit with one bead per condition supports is a statistics question, not a
  representation one.** A 1-sample arm carries no variance; whether a test runs on it is the
  statistics registry's and I15's business, and ADR-0036 D8's whole-arm flag already applies.
  Representing the contrast honestly is not the same as licensing a test on it.

**`role` gains `isotype_control`.** ADR-0036 D2 closed the enum at `ip` and
`no_antibody_control` and said adding a value *"later is a visible commit"*; this is that commit.
- `bait` stays NULL for it (determined by `role ≠ 'ip'`, unchanged).
- **The loader's R7 widens:** `antibody` is NULL unless `role ∈ {'ip', 'isotype_control'}`,
  because an isotype control has a reagent and its catalogue number is the same kind of fact.
- No sample carries the value, so no id moves. `input` stays out: no deposit in view has one.

**Not part of I22: whether an arm must be one condition.** All 10 existing arms are (M4). A pooled
bead arm spanning conditions is a standard choice and would fail such a rule. Opened as Q16.

### D3. An IP-vs-control contrast whose arms share a condition string is separated by distinct curator labels, guarded mechanically.

**The case.** PXD055843 S3's per-condition background comparison has two arms whose condition is
the same string. As (`X`, `X`) its id carries neither direction nor what is compared, and its reverse
mints the same id.

**Decided: option (c).** The curator writes distinct `numerator` and `denominator` strings
(*"siUSP24 (+ IFN-B), ISG15 IP"* / *"siUSP24 (+ IFN-B), beads"*, say). D1's loader refuses equal
strings and a repeated pair. **What the contrast means is not carried by the strings**: membership
is D1's arms, orientation is I22's control-never-numerator rule, kind is derived (D2). The strings
are a label whose only obligation is to differ.

**Re-mint cost, measured over the 5 contrasts (M5):**

| Option | `Contrast` ids moved | Consequence |
|---|---|---|
| (a) `numerator_role`, `denominator_role` in identity | **5 of 5** | An absent identifying field still renders, so every contrast moves |
| (b1) arm members' `Sample` ids in identity | **5 of 5** | — and `190e696`'s `Sample` re-mint would have moved all 5 again (M6) |
| (b2) arm members' `Sample` values folded in as qualifying children | **5 of 5** | Same coupling, through values |
| **(c) distinct labels** | **0 of 5** | — |

- A `DifferentialResult` id follows its contrast (M5, one representative re-keyed). Only
  `KO_IFN_vs_WT_IFN` carries results today: the two result-writing modules are
  `pxd018299_differential.py`, which writes that contrast, and `pxd055843_perseus.py`, which has
  never run (PXD055843 is blocked). So (a) and (b) each move **every result in the graph — 1,362**
  (count's home: `notes/REVIEWER-HANDOFF-2026-10-05.md` §3.3, MA). That per-contrast split is
  derived from the code, not counted from a graph; *Not measurable here* registers the count.
- **(a) is rejected** because it stores in identity what D1 and D2 already fix — a second home for
  orientation and kind — and pays the whole graph for it.
- **(b) is rejected** because it makes `Contrast` identity a function of `Sample` identity. Nothing
  anchors on `Sample` today (M1), which is why `190e696` moved 54 ids and no other (ADR-0036 V2,
  confirmed at graph scale in handoff §3.3). Under (b) every future `Sample` identity change
  re-mints every contrast and every result.

**What (c) does not catch, stated so a pass is not misread.** Two records sharing one `Experiment`
could declare the same pair with different arms; the per-record guard cannot see across records.
Today no two records share an `Experiment`: the four records mint 4 distinct `Experiment` ids
(M1; agrees with handoff §3.3 Step A's `Experiment` 4). D4's edges make the collision visible in the graph as a contrast whose arms come from two curation
activities, but nothing refuses it.

### D4. The binding becomes `Contrast`–`Sample` edges.

Two relationships, both `Contrast → Sample`, `MANY_MANY`, **non-identifying**, written only by the
loader from D1's arms:

- `NUMERATOR_SAMPLE`
- `DENOMINATOR_SAMPLE`

Two types rather than one with a `side` property, because they are two facts and ADR-0023's rule is
one relationship per fact; a property every reader must filter on is the conflation that rule
exists to prevent.

- **No id moves** (not anchors; M5 (c) is the measurement for the identity half).
- **I22 becomes graph-checkable,** which D5 named and did not build.
- **l.581 becomes true** for every result whose contrast is declared, and D8 makes that all of them.
- Producers stage the `Contrast` as a referent without these edges, as they stage it without
  `CONTRAST_IN_EXPERIMENT` (ADR-0029 E); ADR-0019 self-containment is satisfied by the loader's
  change-set, which carries both endpoints.

### D5. A producer reads only columns its arms bind, through one binding per file format.

**The rule.** A column is bound to a `Sample` in exactly one place per format — the adapter's
`_sample_columns` — by composing the header from the sample's mapping key through the adapter's
closed family table and requiring exact membership in the file's header. **A producer never names
a column.** It asks the binding for (`Sample` id, quantity) and receives a header or a refusal.
The arms' sample ids come from D1.

This is not new machinery. It is the rule both MaxQuant adapters already follow at ingestion —
`maxquant_sites._sample_columns` (l.128–152, family table l.122) and the protein-groups adapter's
*"By exact name, built from the label — never a prefix scan"* (l.419) — made the only route by which
a producer reaches a column.

**The Intensity-vs-Ratio case, measured on PXD018299's real 159-column header** (`ROADMAP.md`
l.7073; M7): the binding takes the arms keyed `Ratio mod/base KO_IFN_1..3` / `WT_IFN_1..3` to
`Intensity KO_IFN_1..3` / `Intensity WT_IFN_1..3`, all present, **identical to what the token
picks**. So deleting `CONTRAST` predicts identical figures. A `startswith('Intensity KO_IFN_1')`
scan would catch **4** columns (the `___1..3` multiplicity columns).

**Where the binding refuses, it refuses on purpose** (M8). In PXD018299's interactome, **0 of 12**
`Intensity n-m` columns are reachable from an `LFQ intensity` label, while all **12** LFQ keys bind.
The file does not say which experiment number is which condition (survey §2), so the platform does
not either. Step 3 reads the LFQ family; binding the other needs a curator statement, which the
survey's blindness rule currently forbids deriving from per-row values. *The protein-groups adapter
today drops an unreachable family without a word* — an I11 finding, carried below, not decided
here.

**Platform-run producers.** `site_change_set` and the coming protein-grain IP writer receive the
loader's arms and read the arm columns through the binding. Reading the retained matrix
(`quant_store` cells keyed by `Sample` id) is the same binding executed at ingestion, and is
permitted; whichever is used, the input is keyed by `Sample` id.

### D6. An aggregate-only producer proves its binding arithmetically.

The Perseus adapter reads statistics, not samples. **It proves its contrast columns belong to the
declared arms by recomputing the Difference column from them.**

- For every row whose Difference and every arm value are finite, `Difference` must equal
  `mean(numerator columns) − mean(denominator columns)` within **1e-3, absolute**. At least one
  row must be checkable. **The tolerance is fixed here, before PV runs** (review R2, 2026-10-05):
  a threshold chosen after seeing PV's numbers would be fitted to them.
- **Any disagreement refuses the contrast.** The rule fails closed: a wrong arm, a wrong order or
  a near-duplicate column set (the 9-key substring arm, M2) changes the means.
- **It proves direction as well as membership.** The reversed order differs by twice the
  Difference. That settles the PXD055843 record's `unresolved` entry on arm order (read from the
  suffix under Perseus' numerator-first convention) from the file's own numbers.
- **A file with statistics and no sample columns cannot be bound and is refused.** No public case
  needs otherwise: PXD055843 S1 carries 18 sample columns (curation record rationale) and S3 16
  (survey §7). Admitting a declared-only binding is a later, visible commit.
- The values are read in memory for the check and not retained; retention stays governed by the
  adapter's existing `withheld_because`.
- The suffix (`DeclaredContrast.column_suffix`) stays as the locator of the statistics columns. It
  no longer carries the binding.

**Why 1e-3, and not 1e-6 as first drafted.** The tolerance has to clear the rounding a correct
binding carries and stay far below the error a wrong one makes.

- **Perseus stores its main matrix in single precision**, checked on 2026-10-05 against the two
  builds of its plugin API that are still public. `JurgenCox/perseus-plugins` returned 404 on that
  date, so the mirrors were used.
  - `jdrudolph/perseus-plugins` `master` (`PerseusApi` 1.4.0.0; bundled DLLs dated 2016-05-30):
    the source declares `public abstract float Get(int i, int j)` on `MatrixIndexer`, and the
    bundled `BaseLibS.dll` agrees (`get_Item` returns `float32`).
  - `cox-labs/PluginInterop` `master` (bundled DLLs dated 2020-11-05): `MatrixIndexer.Get` now
    returns `float64`, but `PerseusApi.dll`'s `PerseusFactory` references `FloatMatrixIndexer` and
    not `DoubleMatrixIndexer`, and `FloatMatrixIndexer` stores `float32[,]` blocks.
  - **PXD055843's Perseus, v1.6.2.3, falls between those two builds and was not itself
    inspected.** The finding is a bracket, not a reading of that version.
  - Reproduce: fetch both archives from `codeload.github.com`, then read `MatrixIndexer`'s source
    and the DLLs' method and field signatures with `dnfile` (`pip install dnfile`). Element type
    `0x0c` is `float32`, `0x0d` `float64`.
- **What that costs a correct binding.** A `float32` near log2 intensities of 10–30 carries about
  7 significant digits. **I believe, and have not verified here,** that .NET Framework's default
  `float` formatting writes 7 significant digits, which puts the export's quantum at 1e-5. Each
  value then carries up to ±5e-6, so each arm mean does too, and the difference of two means up to
  1e-5. Allowing the Difference column its own rounding, the worst case is about **2e-5**. That is
  twenty times 1e-6, so **1e-6 could refuse a correct binding on rounding alone.**
- **What a wrong binding costs.** A reversed order misses by twice the Difference on every row. A
  swapped or extra column moves an arm mean by a third of a between-sample difference, typically
  ≥0.05 log2. 1e-3 sits 50 times above the correct-binding worst case and 50 times below that.
- **1e-3 is also the threshold PV3 and PV4 were already registered at**, so the rule and those
  predictions use one number.

**Cost, measured:** all six `tests/fixtures/perseus_synthetic_*.txt` carry no sample columns, and
22 test call sites construct a `PerseusAdapter` (20 in `test_perseus.py`, 1 each in
`test_adapter_dispatch.py` and `test_pxd055843_perseus.py`). The fixtures gain sample columns
consistent with their Difference values in the build.

**This decision rests on a prediction not yet tested on real data** — PV, below. If PV refutes it,
D6 is not built and this record is revised before acceptance.

### D7. I4's display labels, per grain and kind.

**One label per (grain, kind, state) cell; a cell with no label is a cell no result may occupy.**
Grain is the result's `RESULT_FOR_*` edge; kind is D2's.

| Grain | Kind | `not_applied` | `native` | `applied` |
|---|---|---|---|---|
| site | `condition` | *stoichiometry-uncorrected* | *stoichiometry-native (ratiometric source)* | *stoichiometry-corrected* |
| protein | `condition` | *abundance — no adjustment defined* | refused | refused |
| protein | `differential_association` | *abundance-uncorrected* | refused | refused |
| protein | `background_enrichment` | *abundance-uncorrected* | refused | refused |
| site | either IP kind | refused | refused | refused |

- **The protein-abundance row gets a label that says what it is.** `not_applied` there does not
  mean *a correction was possible and skipped*; there is no protein above a protein. Labelling it
  *uncorrected* would assert an omission that did not happen.
- **Background enrichment is labelled *abundance-uncorrected* too.** Where IP and control arms come
  from one lysate, parent abundance is the same in both arms. A pooled control arm spans
  conditions (Q16), and the label must be true of both.
- **Protein-grain `applied` is refused for now, including ADR-0036 D7's IP abundance correction.**
  No writer emits it. Opening it is a visible commit that defines what an IP result is corrected
  against.

**Where each refusal sits:**
- **Write time, `_check_I4`: a protein-grain result is `not_applied`.** Grain is visible in every
  change-set (I20). Measured (M10): every committed `applied`/`native` result is site grain, so
  this refuses nothing that exists.
- **Kind is not visible at write time**, because producers stage the `Contrast` as a bare referent.
  So the site-grain-in-IP refusal sits at the producer: `site_change_set` refuses arms whose kind is
  not `condition`.
- **Display:** the query layer derives kind from the graph (`CONTRAST_IN_EXPERIMENT` →
  `modality`; D4's edges → roles) and maps the cell to its label, with no fallback. Kind is derived,
  never stored.
- The table has one home, `ONTOLOGY.md` I4; the code copy is guarded by a test, as every other
  mirror here is.
- `ONTOLOGY.md` l.903's *"on a site"* is widened to every grain, matching what `_check_I4` already
  does.

### D8. Scope: every contrast, required.

**Every contrast declares its arms; there is no optional form.**
- **"Recommended" is rejected.** An optional declaration makes I22 pass vacuously wherever it is
  omitted, which is the Context's failure in a new place.
- **"IP only" is rejected.** The token selection this record removes is in a non-IP producer, and
  l.581 stays false for every existing result. It would also give I22 two rules, one per
  `modality`, where D2's table is one.
- **Cost:** three committed records edited (PXD018299, PXD026748, PXD055843), five entries, 30 keys
  (M4); **0 ids move** (M5 (c); D4's edges are non-identifying). The PXD026748 shotgun record
  declares no contrast and is unaffected.

---

## Consequences

- **I22 runs over every contrast**, at the one minting site, and is checkable in the graph.
- **The PXD018299 differential loses `CONTRAST`.** Its figures are predicted identical (M7); its
  build pre-registers 0 ids moved and the `[4b]` line unchanged.
- **The provenance chain l.581 describes exists.**
- **Background enrichment is representable** for public data (S3) and for local data with
  replicated controls, without a re-mint.
- **The Perseus adapter needs sample columns** in every file it binds (D6), and its fixtures change.
- **I4 has a label for every result kind**, and a protein-abundance result stops being displayed as
  though it were missing a correction.
- **Two refusals sit outside the invariant suite** (site-grain IP at the producer; Perseus's
  arithmetic in the adapter). Both are stated where they sit.

---

## Implied changes, described and not made

Line numbers are at `ebc0750`.

**`ONTOLOGY.md`**
- l.119 — `Contrast` row: note that arms are declared in curation and materialised as D4's edges;
  identity unchanged.
- l.400–406 — `Sample` DDL comment: `role` gains `'isotype_control'`; `antibody`'s comment per D2.
- §5 DDL after l.521 — `NUMERATOR_SAMPLE`, `DENOMINATOR_SAMPLE` (`FROM Contrast TO Sample,
  MANY_MANY`).
- l.581 — the provenance-chain sentence: cite D4.
- l.903 — I4 widened to every grain; D7's table; the protein-grain `not_applied` rule.
- §8 — mint **I22** (D2's table), enforced at the loader; graph form over D4's edges.
- §11 — **Q16**: must an arm be one condition, and are pooled control arms exempt?

**`bzk/ontology/schema.py`** — the two rel tables; nothing in `IDENTITY`; `tests/test_schema.py`
moves with §5.

**`bzk/curation/loader.py`**
- Contrast entries: resolve D1's arms, refuse as D1 lists, refuse unknown keys; I22 at mint (l.484–503).
- Emit D4's edges; carry arms and kind on `LoadedCuration`.
- `_SAMPLE_ROLES` (l.311) gains `isotype_control`; the R7 check (l.356) widened. **Guard the
  mirror** against the DDL comment — the unguarded-mirror item of handoff 10-05 §7 — in the same build.

**`bzk/analysis/differential.py`, `bzk/sources/pxd018299_differential.py`** — take the arms from the
loader; read columns through the binding; delete `CONTRAST` (l.111) and `_intensity_columns`
(l.258); refuse non-`condition` kinds at site grain.

**`bzk/adapters/perseus.py`** — D6's arithmetic proof; fixtures under `tests/fixtures/` gain sample
columns.

**`bzk/ontology/invariants.py`** — `_check_I4` reads grain and refuses protein-grain `applied` /
`native`.

**`bzk/query/graph.py`, `bzk/ui/app.py`** — D7's labels from derived kind; the label table's code
copy guarded against §8.

**Curation records** — `curation_PXD018299.json`, `curation_PXD026748.json`,
`curation_PXD055843.json`: arms as M4 prints them.

**Carried, not decided here**
- The protein-groups adapter drops a family it cannot reach from the mapping keys without reporting
  it (M8). An I11 question for step 3.
- F-d (unknown keys in `mapping` entries) is not touched: D1 refuses unknown keys in *contrast*
  entries only.
- A basis value for background-enrichment concordance (ADR-0036 D6's last paragraph) is not minted:
  nothing consumes one yet.

---

## Alternatives considered

- **Roles in `Contrast` identity (D3 a).** Rejected: 5 of 5 contrasts and every result move, to
  store what arms and I22 already fix.
- **Arm membership in identity (D3 b1, b2).** Rejected: couples `Contrast` to `Sample` identity;
  `190e696` alone would have moved all 5 contrasts.
- **Arms as condition strings matched to sample fields.** Rejected on M2: field equality selects
  0 or 6 where 3 are meant.
- **Arms as substrings of mapping keys.** Rejected on M2: 0 for PXD018299, 9 for PXD055843.
- **I22 at the producers (ADR-0036 D5 as accepted).** Rejected: producers bind columns, not samples,
  so the check had nothing to run over.
- **Per-sample `columns` blocks in every mapping entry.** Rejected for now: edits all 54 entries to
  restate what the adapters' family tables already compose, and creates a second home for the
  binding. Reconsider if a format's families do not share run labels and a curator can state the
  correspondence (the interactome's `Intensity n-m`).
- **Trusting the Perseus suffix (status quo).** Rejected: a suffix names no sample, and PXD055843's
  arm order already rests on a convention rather than a measurement.
- **Storing kind on `Contrast`.** Rejected: a derived value with a second home; derived at display
  instead, at the cost of the producer-side refusal in D7.

---

## Measurements — verbatim output at `ebc0750`

Command: `uv run python notes/scripts/measure_adr0038.py`, in a scratch clone at `ebc0750` with
this record's instrument added. Read-only.

```
M1 anchors and relationships
  anchors on Contrast: [('DifferentialResult', 'RESULT_IN_CONTRAST')]
  anchors on Sample: []
  rel tables touching Contrast: [('RESULT_IN_CONTRAST', 'DifferentialResult', 'Contrast'), ('CONTRAST_IN_EXPERIMENT', 'Contrast', 'Experiment')]
  curation_PXD018299.json KO_IFN_vs_WT_IFN: 'USP18-/- + IFN' / 'WT + IFN' -> bzk:8f9a06344675831a26dd59b2bf8c4393
  curation_PXD018299.json KO_vs_WT_unstimulated: 'USP18-/-' / 'WT' -> bzk:d78903eeb3746b372e2100d3b6e52906
  curation_PXD026748.json PLproWT_vs_PLproMut_in_WT: 'WT + IFN-alpha, lysate + PLpro WT' / 'WT + IFN-alpha, lysate + PLpro mutant' -> bzk:45df0bf3df1878e9723fdde9e6490b01
  curation_PXD026748.json PLproWT_vs_PLproMut_in_ISG15KO: 'ISG15-/- + IFN-alpha, lysate + PLpro WT' / 'ISG15-/- + IFN-alpha, lysate + PLpro mutant' -> bzk:e308f9b86b6cda2f46da23e62583c4cd
  curation_PXD055843.json siUSP24_IFN_vs_siC_IFN: 'siUSP24 (+ IFN-B)' / 'siC (+IFN-B)' -> bzk:180e18ad99631bba5da4a6e6734cd6a9
  contrasts minted by the loader: 5
  records 4, distinct Experiment ids 4
M2 do arm strings compose from samples, or substring-match mapping keys?
  KO_IFN_vs_WT_IFN numerator 'USP18-/- + IFN': field-equal 0, key-substring 0
  KO_IFN_vs_WT_IFN denominator 'WT + IFN': field-equal 0, key-substring 0
  KO_vs_WT_unstimulated numerator 'USP18-/-': field-equal 6, key-substring 0
  KO_vs_WT_unstimulated denominator 'WT': field-equal 6, key-substring 6
  PLproWT_vs_PLproMut_in_WT numerator 'WT + IFN-alpha, lysate + PLpro WT': field-equal 0, key-substring 0
  PLproWT_vs_PLproMut_in_WT denominator 'WT + IFN-alpha, lysate + PLpro mutant': field-equal 0, key-substring 0
  PLproWT_vs_PLproMut_in_ISG15KO numerator 'ISG15-/- + IFN-alpha, lysate + PLpro WT': field-equal 0, key-substring 0
  PLproWT_vs_PLproMut_in_ISG15KO denominator 'ISG15-/- + IFN-alpha, lysate + PLpro mutant': field-equal 0, key-substring 0
  siUSP24_IFN_vs_siC_IFN numerator 'siUSP24 (+ IFN-B)': field-equal 0, key-substring 9
  siUSP24_IFN_vs_siC_IFN denominator 'siC (+IFN-B)': field-equal 0, key-substring 3
M3 an unknown key inside a contrasts_of_interest entry
  loaded, not refused; contrast nodes identical to the unmodified record: True
M4 declared arms (mapping keys)
  KO_IFN_vs_WT_IFN: n 3/3, overlap 0, one value per identifying field but replicate: True
    numerator ['Ratio mod/base KO_IFN_1', 'Ratio mod/base KO_IFN_2', 'Ratio mod/base KO_IFN_3']
    denominator ['Ratio mod/base WT_IFN_1', 'Ratio mod/base WT_IFN_2', 'Ratio mod/base WT_IFN_3']
  KO_vs_WT_unstimulated: n 3/3, overlap 0, one value per identifying field but replicate: True
    numerator ['Ratio mod/base KO_1_181212063719', 'Ratio mod/base KO_2', 'Ratio mod/base KO_3']
    denominator ['Ratio mod/base WT_1', 'Ratio mod/base WT_2', 'Ratio mod/base WT_3']
  PLproWT_vs_PLproMut_in_WT: n 3/3, overlap 0, one value per identifying field but replicate: True
    numerator ['Intensity 05_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_Gly-Gly-WT_rep1', 'Intensity 15_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_Gly-Gly-WT_rep2', 'Intensity 21_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_Gly-Gly-WT_rep3']
    denominator ['Intensity 07_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_Gly-Gly-WT_mut_rep1', 'Intensity 11_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_Gly-Gly-WT_mut_rep2', 'Intensity 17_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_Gly-Gly-WT_mut_rep3']
  PLproWT_vs_PLproMut_in_ISG15KO: n 3/3, overlap 0, one value per identifying field but replicate: True
    numerator ['Intensity 01_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_Gly-Gly-KO_rep1', 'Intensity 13_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_Gly-Gly-KO_rep2', 'Intensity 19_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_Gly-Gly-KO_rep3']
    denominator ['Intensity 03_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_Gly-Gly-KO_mut_rep1', 'Intensity 09_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_Gly-Gly-KO_mut_rep2', 'Intensity 23_Ap_WNE14_trap5_CMB-812_FRIMP_denzel_Gly-Gly-KO_mut_rep3']
  siUSP24_IFN_vs_siC_IFN: n 3/3, overlap 0, one value per identifying field but replicate: True
    numerator ['Set 1 | siUSP24 (+ IFN-B) | E:\\Proteomics-SCP00004\\SCP0004_MSQ2531_20221219_Rishov-AdanPinto_TP04_S1-D5_463.d', 'Set 2 | siUSP24 (+ IFN-B) | E:\\Proteomics-SCP00004\\SCP0004_MSQ2531_20221219_Rishov-AdanPinto_TP08_S1-H5_467.d', 'Set 3 | siUSP24 (+ IFN-B) | E:\\Proteomics-SCP00004\\SCP0004_MSQ2531_20221219_Rishov-AdanPinto_TP12_S1-D6_471.d']
    denominator ['Set 1 | siC (+IFN-B) | E:\\Proteomics-SCP00004\\SCP0004_MSQ2531_20221219_Rishov-AdanPinto_TP03_S1-C5_462.d', 'Set 2 | siC (+IFN-B) | E:\\Proteomics-SCP00004\\SCP0004_MSQ2531_20221219_Rishov-AdanPinto_TP07_S1-G5_466.d', 'Set 3 | siC (+IFN-B) | E:\\Proteomics-SCP00004\\SCP0004_MSQ2531_20221219_Rishov-AdanPinto_TP11_S1-C6_470.d']
  Contrast-Sample edges implied: 30
M5 re-mint cost of each identity option
  a_roles: Contrast ids moved 5 of 5
  b1_member_ids: Contrast ids moved 5 of 5
  b2_member_values: Contrast ids moved 5 of 5
  c_labels: Contrast ids moved 0 of 5
  a representative DifferentialResult id follows its Contrast: True
  result-writing source modules: ['bzk/sources/pxd018299_differential.py', 'bzk/sources/pxd055843_perseus.py']
M6 option b's coupling: would 190e696's Sample re-mint have moved a Contrast?
  b1 Contrast ids moved by the Sample re-mint: 5
  c  Contrast ids moved by the Sample re-mint: 0 by construction (no Sample input)
M7 the Intensity-vs-Ratio binding on PXD018299's real sites header
  header read from ROADMAP.md l.7073: 159 columns
  numerator: bound ['Intensity KO_IFN_1', 'Intensity KO_IFN_2', 'Intensity KO_IFN_3']; present True; equals the token's pick True
  denominator: bound ['Intensity WT_IFN_1', 'Intensity WT_IFN_2', 'Intensity WT_IFN_3']; present True; equals the token's pick True
  a startswith('Intensity KO_IFN_1') scan would catch 4 columns
  a startswith('Intensity KO_1') scan would catch 4 columns
M8 the interactome's two families (walk/SURVEY-public-IP-tables.md §6)
  LFQ columns 12, Intensity columns 12; Intensity columns reachable from an LFQ label 0; LFQ keys the protein-groups binding places 12
M9 I4's display labels and grain scope in code
  'stoichiometry-uncorrected' in bzk/: 1 line(s) ['bzk/analysis/differential.py:148:        # ingested. `not_applied` is labelled *stoichiometry-uncorrected* in every view and export;']
  'abundance-uncorrected' in bzk/: 0 line(s) []
  _check_I4 reads a grain edge: False
M10 grain of every applied/native result in the committed fixtures
  valid_changeset bzk:dr1: RESULT_FOR_SITE applied
  valid_changeset bzk:dr2: RESULT_FOR_PROTEIN not_applied
  valid_changeset bzk:dr3: RESULT_FOR_SITE not_applied
  valid_changeset bzk:dr4: RESULT_FOR_SITE not_applied
```

**One measurement was run and discarded as vacuous.** Declaring arms in a record copy and reloading
it changed no node id — but M3 shows the loader drops the new keys, so the result says nothing about
D1. It is not in the instrument. The identity half is measured by M5 (c) instead.

---

## Pre-registration — PV, on bzk's Mac, before D6 is built

Committed with this record and before any run. Command:
`uv run python notes/scripts/measure_adr0038.py --s1` — reads PXD055843 S1 from the content store
by the analysis record's digest; writes nothing.

| # | Line | Kind | Prediction |
|---|---|---|---|
| PV1 | declared order, values as stored | reasoned, moderate | **max \|dev\| ≤ 1e-3, D6's rule.** ~~≤ 1e-6~~ — revised before any run (review R2): see *Why 1e-3* under D6. Ground: the record measured the matrix dense (136,980 cells), which the methods explain as post-imputation, and Perseus' Difference is the difference of group means on the matrix it tested |
| PV1b | PV1's value, read for precision | reasoned, low | 1e-6 < max \|dev\| ≤ 2e-5: `float32` values written at 7 significant digits. **Not a gate.** Below 1e-6 means the export carried full precision and my formatting belief is wrong; above 2e-5 but within 1e-3 means rounding I have not accounted for. D6 holds either way |
| PV2 | reversed order | reasoned, high | max \|dev\| > 0.5 (twice the largest Difference) |
| PV3 | 9-column substring numerator | reasoned, high | max \|dev\| > 1e-3 |
| PV4 | declared order, log2 of stored | reasoned, moderate | max \|dev\| > 1e-3: the stored values are already log2. **Exactly one of PV1's and PV4's lines comes in ≤ 1e-3** *(reworded with R2: "exactly one of PV1 and PV4 holds" was false of the expected case, where both predictions hold)* |
| PV5 | rows checked | identity | PV1's row count equals `PV0`, the number of rows carrying a finite Difference; no figure registered, none measured here |

**Instrument corrected before any run (`8ed075a` → `27b8dbc`).** As landed, `--s1` printed no
denominator for PV5, and a Difference or arm column absent under its composed name made every row
skip, so PV1 would have read `max |dev| 0 over 0 rows` — a pass that never ran. It now refuses
before printing if any column it reads is absent, and prints `PV0`. Predictions PV1–PV5 are
unchanged; M1–M10's output is byte-identical.

**What each outcome does, read off the printed values against 1e-3.** *(Rewritten with R2. The
first draft said "if PV1 and PV4 both fail", which got the PV4 case backwards: PV4's line agreeing
would prove the binding, on log2 of the stored values.)*

- **PV1's line ≤ 1e-3** (expected): the binding is proven on the values as stored.
- **PV1's line > 1e-3 and PV4's ≤ 1e-3:** the stored values are linear and the test ran on their
  log2. The binding is proven, and D6 is revised to declare the transform before it is built.
- **Both lines > 1e-3:** the export's values are not those the test ran on. D6 is not built and
  this record is revised. **The tolerance is not loosened to meet the data.**
- **PV2's line ≤ 1e-3 instead of PV1's:** the record's arm order is reversed. That `Contrast`
  re-mints (order is identifying), with 0 results attached.

## Not measurable here

- **Results per contrast in the graph.** Command for bzk's Mac, read-only:
  `uv run python -c "import kuzu,pathlib; c=kuzu.Connection(kuzu.Database(str(pathlib.Path.home()/'.bzk-omics/graph.kuzu'), read_only=True)); r=c.execute('MATCH (r:DifferentialResult)-[:RESULT_IN_CONTRAST]->(c:Contrast) RETURN c.id, count(r)'); [print(*r.get_next()) for _ in iter(r.has_next, False)]"`.
  Predicted (identity, from the code): one line, `bzk:8f9a06344675831a26dd59b2bf8c4393 1362`.
- PV above.

---

## Landing verification

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| V1 | Every line reference in this record | holds | Re-read at `ebc0750` by `grep -n` on each cited string; `ebc0750` touches only `notes/` since `190e696`, so the handoff's references and these agree |
| V2 | The suite is green before and after; the four checks run | holds | `pytest` at `ebc0750`: 908 passed, 14 skipped. With this landing applied: `pytest` 908 passed, 14 skipped (same count: the change moves pins in an existing test and adds none); `pytest tests/test_schema.py` 20 passed; `ruff check bzk tests` and `ruff format --check bzk tests` clean; `mypy bzk tests` clean over 117 files. The instrument sits outside those targets and is clean under `ruff check` and `ruff format --check` on its own path |
| V3 | No node anchors on `Sample`; only `DifferentialResult` anchors on `Contrast`; nothing relates `Contrast` to `Sample` | holds | M1 |
| V4 | Re-mint cost per D3 option | holds | M5, M6 |
| V5 | The loader drops unknown contrast-entry keys today | holds | M3 |
| V6 | The binding equals the token's pick on PXD018299; the interactome's `Intensity` family is unreachable | holds | M7, M8 |
| V7 | No I4 label exists in `bzk/`; `_check_I4` reads no grain; every `applied`/`native` fixture is site grain | holds | M9, M10; `git grep -n protein_adjusted -- tests` lists `applied` and `native` only on site-grain results (`test_invariants.py` l.207, `test_query.py` l.95, `valid_changeset.json` `bzk:dr1`) |
| V8 | Index pins move with the landing | holds | `tests/test_decision_index.py`: files 36 → 37, Written rows 36 → 37, `Proposed` 9 → 10; README's Written table gains this row. **The reciprocity guard caught a drafting defect:** the first draft wrote the amendment note inside the `Supersedes` cell, and `test_supersession_is_reciprocal_except_where_recorded` read `0036` there as a supersession. Moved to the opening paragraph; the row is `—` |
