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

**Platform-run producers read raw columns through the binding** (review R1, 2026-10-05).
`site_change_set` and the coming protein-grain IP writer receive the loader's arms and read the
arm columns from the file through the binding. ~~Reading the retained matrix (`quant_store` cells
keyed by `Sample` id) is the same binding executed at ingestion, and is permitted; whichever is used,
the input is keyed by `Sample` id.~~ **The retained-matrix route is deferred** until a build
pre-registers that it reads the same values as the raw route, cell for cell.

**R1's first ground was refuted when checked, and is recorded as refuted.** It was that two rows
might key to one observation, so a route keyed by observation would test fewer units. The
existing data says they do not:
- **PXD018299: 2,029 ingested rows, 2,029 `SiteObservation`s.** The real-graph test pinned 2,029
  sites when PXD018299 was the only site deposit (`tests/test_query_real_graph.py` l.64). The
  differential's population line reads `2,341 → 2,298 → 2,056 → 2,029 → 1,362` (handoff 10-04
  §3.1, M1), whose 2,029 is consistent with the ingested count; which printed line it is was not
  re-derived here.
- **The two-deposit graph: 4,195 = 2,029 + 2,166**, the second being PXD026748's `sites_emitted`
  (M11, from its committed fixture; 4,195 from handoff 10-05 §3.3). The `Dataset` anchor keeps the
  deposits apart, so any convergence would have shown as a shortfall. There is none.
- **Tested rows are one-to-one with results:** 1,362 tested (the same population line), and 1,362
  `DifferentialResult`s in the graph (handoff 10-05 §3.3, MA). Two tested rows sharing an
  observation would mint one result id.

**R1 stands on two other grounds.**
- **The retained matrix cannot detect convergence if it ever happens.** Measured (M11):
  `write_cells` accepts a batch carrying one key twice, retains one cell and reports
  `cells_staged 2`. A future deposit whose rows did converge would lose a value silently, and the
  count would not show it. The raw route maps each row to its observation through the adapter's
  report, which is the record the population counts above were read from.
- **The two routes apply different value conventions, unmeasured against each other.** The raw
  route reads `float(cell or 0.0)` and folds `0` to `NaN`. The store keeps a reported `0` as `0`
  (`maxquant.cell_value`), and a reader would have to fold it again. Probably equivalent, but not
  measured.

**Cost:** none in this record's build. The raw route is what `pxd018299_differential.py` already
reads; D5 changes how it names columns, not where it reads them.

### D6. An aggregate-only producer proves its binding arithmetically.

**Refuted by PV on 2026-10-05 (*Results*, below): not built as decided.** Revised as
*D6-revised*, after D6, which is pre-registered on a different export (*PV-S3*) and not built until
that has run and the record is accepted.

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

### D6-revised. Untested rows are recognised from the statistics columns; every tested row proves the binding.

**Proposed 2026-10-05, after PV refuted D6 as registered. For review. Not built until its own
pre-registration (*PV-S3*, below) has run on a different export and the record is accepted.**
D6 above stays as written, refuted; this replaces it if it survives.

**(a) An untested row is recognised from the statistics columns alone.** A row is *untested* when
its Difference is `0`, its −log p is `0` (p = 1), and its test statistic is `0` where the file
carries that column.
- **It reads no arm column**, so the binding under test cannot influence which rows it excludes.
  That is what keeps the proof failing closed: a wrong binding still has to agree on every row the
  file tested.
- **Where the rule came from, stated so S1 is not counted as evidence for it.** S1's 27 refused
  rows each carry Difference `0`, statistic `0`, −log p `0` and q `1`, and no agreeing row has
  Difference `0` (*Results*, E2–E4). So the rule picks out exactly those 27 on S1, by
  construction. **S1 shaped the rule and cannot confirm it.** PV-S3 is the test.
- q is recorded beside the rule, not in it: q is computed across rows, so it is not a property of
  one row's test.
- **Can a tested row carry all three zeros? Yes, in exactly one case.** Equal group means give a
  Difference of 0, a statistic of 0 and p = 1, a genuine null. Other degenerate cases come out
  differently: zero variance with unequal means gives an infinite statistic, and zero variance with
  equal means gives an undefined one, not 0. On continuous log2 intensities exactly equal means
  are very unlikely, though not impossible once values are rounded. **None occurred in S1:** no
  tested row has Difference exactly `0` (*Results*, E2). The cost is in *Limits* below.

**Where untested rows come from: a hypothesis, not established.** S1's methods filter for
*"identification in all three replicates of at least one group"*, over all six groups. A protein
can pass that filter on a group outside the test (the −IFN or USP2 groups) while having **no valid
value in either tested group**. Perseus then has nothing to test, and writes the placeholder.
- **What fits:** every refused row sits among the low-valued rows (D4), which is where an imputed
  draw lands.
- **What does not fit:** the usual Perseus workflow imputes *before* testing. The record quotes the
  methods' filter and imputation, but not where the test sits relative to them. Under that order,
  every row had values at test time and none should be untested. Either the order was different
  here, or the cause is something else.
- **What the file can show is a profile, not the cause.** *ORIGIN*, pre-registered below, checks
  whether the 27 rows look as the hypothesis predicts. Settling it needs the Perseus session or the
  pre-imputation matrix, so it joins the imputation question already with the PI.

**(b) Every tested row must agree within 1e-3, and at least one row must be tested.** The tolerance
is R2's, unchanged.
- **R2's support, as far as it goes.** The tolerance was fixed before PV, on single-precision
  storage measured in the bracketing builds. On S1, all 7,583 tested rows agree within it, and
  those are exactly the rows rule (a) keeps (E2). The median is 1.5e-5 and p99 6e-5, about 17 times
  inside 1e-3. Reversed, only 9 rows fall within it.
- **What is not established:** the largest deviation among S1's tested rows lies somewhere between
  6e-5 and 1e-3, and was not printed. So the margin at the top is unknown, and **all of this is
  in-sample.** T1 prints the maximum over S3's tested rows, out of sample.

**(c) An untested row mints no `DifferentialResult`.** Its `ProteinObservation` and its cells are
ingested as usual, and the adapter's report counts it as `rows_untested`.
- **This is the carried finding's fix, not only D6's.** Without it, S1 would put 27 results with
  log2FC 0, p 1 and q 1 into the graph that no test produced, indistinguishable from a measured
  null.
- **It is a statement about what the Perseus adapter reads**, so ADR-0032 (Proposed) should take it
  into its review.
- **Untested rows are shown, not hidden** (`CLAUDE.md`: *flag rather than hide*). Minting no result
  removes a false measurement; it must not make the row disappear.
  - The ingestion report counts them per contrast, and the source module prints the count.
  - A view of such an observation says *not tested by the source analysis* instead of showing
    nothing. "No result" in a view otherwise cannot distinguish *untested* from *absent from the
    file* or *dropped by a fault*.
  - **The view must not infer "untested" from absence alone.** Two ways for the build prompt to
    choose between: a non-identifying per-contrast count on the external `Analysis`, which the
    view's derived count must equal; or an explicit marker per untested row. Either way the count
    is the check.

**Limits, stated so a pass is not misread.**
- **A real test with exactly equal group means looks the same as a placeholder,** so it is dropped
  too. Its arithmetic would have passed; rule (a) never reads it.
- **A file with no test-statistic column recognises untested rows on Difference and p alone.**
  That is weaker. S1 and S3 both carry the column.
- **The rule covers the placeholder Perseus wrote in these two files.** Another tool, or another
  Perseus version, may mark untested rows differently. An unrecognised placeholder would then fail
  (b), loudly, rather than pass.

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
- **Perseus placeholder statistics** (*Results*, exploratory). S1 carries 27 rows whose Difference,
  test statistic and −log p are `0` and q is `1`, inconsistent with their own arm values. The
  adapter would ingest them as measured nulls. ADR-0032 or its own prompt; blocks PXD055843.
- `quant_store.write_cells` accepts a repeated key within one batch, retains one cell and reports
  the batch's length as `cells_staged` (M11). No current deposit triggers it (D5). It is the
  over-reporting shape `base.py` warns about, recorded for its own prompt.
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
M11 retained-matrix writes under a repeated key
  one batch, key repeated: accepted; cells_staged 2, cells retained 1
  PXD026748 sites_emitted (tests/fixtures/pxd026748_digly_ingest.json): 2166
```

M11 was added with review R1, run at `923ba7b`, where `bzk/` and `tests/` differ from `ebc0750`
only in `tests/test_decision_index.py`'s pins. M1–M10 come out byte-identical ahead of it.

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
  **Held** (*Results*).
- PV above — **run; see *Results*.**

---

## Results — run on bzk's Mac at `4d6a23f`, 2026-10-05

Both runs were made after every edit to D5 and D6 was public (`4d6a23f`, tree `e92166f…`). The
outputs below are as bzk pasted them. The PV block was pasted in two parts: the four PV lines first,
then the two lines above them, from `--s1 | head -2`.

### Results per contrast

```
bzk:8f9a06344675831a26dd59b2bf8c4393 1362
```

**Held, exactly.** All 1,362 results sit in `KO_IFN_vs_WT_IFN`. D3's re-mint cost is now measured
on the graph: options (a) and (b) would move all 1,362 results, option (c) none.

### PV — pre-registered

```
PV rows 7610; arms 3/3; substring numerator 9
PV0 rows carrying a finite Difference: 7610
PV1 declared order, values as stored: max |dev| 1.09 over 7610 rows
PV2 reversed order, values as stored: max |dev| 7.54 over 7610 rows
PV3 substring numerator, as stored: max |dev| 5.64 over 7610 rows
PV4 declared order, log2 of stored: max |dev| 3.33 over 7610 rows
```

| # | Prediction | Measured | Verdict |
|---|---|---|---|
| PV1 (D6's rule) | max \|dev\| ≤ 1e-3 | 1.09 | **refuted** |
| PV1b | 1e-6 < max \|dev\| ≤ 2e-5 | 1.09 | **refuted** — and see D3 below: even among agreeing rows, p99 is 6e-5, three times the bound |
| PV2 | > 0.5 | 7.54 | held |
| PV3 | > 1e-3 | 5.64 | held |
| PV4 | > 1e-3 | 3.33 | held |
| PV5 | PV1's rows = `PV0` | 7,610 = 7,610 | held |

**By the outcome table registered before the run, both PV1's and PV4's lines exceed 1e-3, so D6 is
not built as decided, this record is revised, and the tolerance is not loosened.** Nothing below
changes that verdict.

### Exploratory — not pre-registered

Two read-only diagnostics were run after PV, to find what the revision must say. They cannot
rescue D6 at the registered tolerance and are not offered as doing so. Both are committed with this
section, byte-identical to what ran: `notes/scripts/adr0038_pv_diag1.py` (sha256
`96da1617…b6f2c5`) and `notes/scripts/adr0038_pv_diag2.py` (`8271e47d…96dba`). Each reads the
instrument by relative path, so it runs from the repository root. Column headers in the first
diagnostic's D1–D2 lines are shortened here to their `Set | condition` part; the full headers are
in `curation_PXD055843.json`'s `mapping`.

```
D1 numerator columns: Set 1/2/3 | siUSP24 (+ IFN-B) (TP04, TP08, TP12)
D1 denominator columns: Set 1/2/3 | siC (+IFN-B) (TP03, TP07, TP11)
D2 other quantitative-looking columns: the 6 -IFN-B columns and the 6 USP2 columns (TP01, TP02, TP05, TP06, TP09, TP10, TP13–TP18)
D3 declared order: n 7610; <=2e-5 4813; <=1e-3 7583; <=0.1 7586; median 1.5e-05; p90 3.77e-05; p99 6e-05; max 1.09
D3 reversed order: n 7610; <=2e-5 0; <=1e-3 9; <=0.1 660; median 0.591; p90 1.66; p99 3.56; max 7.54
D4 rows with any arm value in its column's lowest 10%: 1426, agreeing within 1e-3: 1399
D4 rows with no arm value in its column's lowest 10%: 6184, agreeing within 1e-3: 6184
D5 signed deviation: mean -0.000907, median -8.6e-16
D6 worst: dev 1.09; Difference 0; arm values [9.412, 10.154, 9.761, 7.964, 9.393, 8.707]
D6 worst: dev 1.09; Difference 0; arm values [9.74, 10.308, 8.979, 7.383, 8.688, 9.7]
D6 worst: dev 0.996; Difference 0; arm values [9.056, 8.63, 7.726, 9.68, 9.659, 9.061]
E1 statistics columns present: ["-Log Student's T-test p-value siUSP24_IFN_siCTRL_IFN", "Student's T-test q-value siUSP24_IFN_siCTRL_IFN"] | other columns carrying the suffix: ["Student's T-test Significant siUSP24_IFN_siCTRL_IFN", "Student's T-test Test statistic siUSP24_IFN_siCTRL_IFN"]
E2 rows: 7610; Difference exactly 0: 27; refused at 1e-3: 27; refused with Difference exactly 0: 27
E3 raw Difference cells among refused rows: [('0', 27)]
E4 "-Log Student's T-test p-value siUSP24_IFN_siCTRL_IFN" among refused rows: [('0', 27)]
   among the 7583 agreeing rows, blank cells: 0
E4 "Student's T-test q-value siUSP24_IFN_siCTRL_IFN" among refused rows: [('1', 27)]
   among the 7583 agreeing rows, blank cells: 0
E4 "Student's T-test Significant siUSP24_IFN_siCTRL_IFN" among refused rows: [('', 27)]
   among the 7583 agreeing rows, blank cells: 7169
E4 "Student's T-test Test statistic siUSP24_IFN_siCTRL_IFN" among refused rows: [('0', 27)]
   among the 7583 agreeing rows, blank cells: 0
E5 refused deviations, sorted: [1.088, 1.085, 0.996, 0.82, 0.76, 0.737, 0.732, 0.685, 0.637, 0.548, 0.537, 0.488, 0.454, 0.393, 0.337, 0.265, 0.265, 0.258, 0.254, 0.241, 0.214, 0.146, 0.115, 0.104, 0.095, 0.075, 0.062]
```

**What they establish.**
- **The declared binding agrees on every row the file actually tested.** 7,583 of 7,610 rows agree
  within 1e-3, at rounding level (median 1.5e-5, p99 6e-5). Reversed, only 9 do. The arithmetic
  discriminates as D6 intended.
- **The 27 refused rows are exactly the 27 rows with Difference `0`, and each carries one
  quadruple:** Difference `0`, test statistic `0`, −log p `0` (p = 1), q `1`, Significant blank.
  Their arm means differ by 0.062 to 1.088. **A test statistic of 0 is impossible for a two-sample
  test whose group means differ**, so these cells are not the result of testing the stored values.
  They are a placeholder written into the statistics columns. The set partitions cleanly: no
  agreeing row has Difference exactly `0`.
- **The mechanism is not established.** The rows sit among those with low values (D4), which fits
  rows Perseus did not test, for example ones failing a valid-value requirement. That is a
  hypothesis, and the file cannot settle it.
- **PV1b's precision model was wrong in kind as well as size.** The bound counted rounding only;
  even the agreeing rows' p99 is three times it.

**A finding that outlives D6.** `PerseusAdapter` keeps a reported `0` as `0` (`_cell_value`), so
ingesting S1 today would mint **27 `DifferentialResult`s with log2FC 0, p 1 and q 1 that no test
produced**, indistinguishable from a measured null. That is a generated value displayed as a
measurement, which I15/I19's discipline and `CLAUDE.md`'s *flag rather than hide* both refuse.
Carried below; it belongs to ADR-0032 (what the Perseus adapter reads) or to its own prompt, and
blocks PXD055843's ingestion until settled, alongside the imputation question.

### What the revision must not do, and must do

- **Not:** exclude these rows from the check on S1 and call D6 confirmed. That fits the rule to the
  file that broke it.
- **Must:** define any exclusion from the file's statistics columns alone, independent of the
  binding under test, so it cannot hide a wrong binding. Then re-register it, and test it on a
  different export before D6 is built. PXD055843 S3 is the candidate: it is on bzk's Mac and
  carries one IP-vs-IP test.
- The revision is drafted separately, for review. This section records results only.

## Pre-registration — ORIGIN, on bzk's Mac (exploratory hypothesis; not a gate)

Command: `uv run python notes/scripts/measure_adr0038.py --s1-origin`. It reads S1 by digest,
prints counts per row class only, and writes nothing. S1's values have been seen (PV and the two
diagnostics), but **these profiles have not**.

**What it measures.** A column's lowest 10% stands in for where a downshifted-normal draw lands. It
is a proxy, not an imputation mask, because the file has none. For each row it counts how many of
the six tested-arm values fall in their columns' lowest 10%, and how many groups outside the test
have all three values above it.

| # | Prediction, if the hypothesis holds | Kind |
|---|---|---|
| O1 | Untested rows: median ≥ 4 of 6 tested-arm values in the lowest 10%. Tested rows: median ≤ 1 | reasoned, low |
| O2 | ≥ 24 of 27 untested rows have at least one other group wholly above the lowest 10% | reasoned, low |

**Outcomes.**
- **Both hold:** the hypothesis is supported, not proven. It goes to the PI as a question, with
  this evidence.
- **Either fails:** the record says the origin is unknown, and drops the hypothesis.
- **Neither outcome touches D6-revised.** Rule (a) reads the statistics columns, not the cause.

## Pre-registration — PV-S3, for D6-revised, on bzk's Mac

Committed with D6-revised and before any of S3's values are read. S3's composed headers were read
on bzk's Mac on 2026-10-05, headers only (no cell values), and are the source of the arms below.
S3 is in the content store under the survey's digest
(`sha256:2ea450f3…f52e9`, `Supplementary_Data_S3_ISG15_IP.xlsx`, stored that day; `already_present`).

Command: `uv run python notes/scripts/measure_adr0038.py --s3`. It reads S3 by digest and writes
nothing. It refuses before printing if any column it reads is absent.

**Arms, declared here by exact composed header,** because no curation record covers S3 (it waits on
the PI and ADR-0032). This is the pre-registration's own curator statement, not a curation record.

| Arm | Columns (title rows, run) |
|---|---|
| IP numerator | `Set 1/2/3 \| siUSP24 (+IFN)`: ISG08, ISG12, ISG16 |
| IP denominator | `Set 1/2/3 \| sic (+IFN)`: ISG07, ISG11, ISG15 |
| Beads, numerator side | `only beads _ no Ab \| siUSP24 (+IFN)`: ISG04 |
| Beads, denominator side | `only beads _ no Ab \| sic (+IFN)`: ISG03 |

Full headers are `S3_IP_NUM`, `S3_IP_DEN`, `S3_BEADS_NUM` and `S3_BEADS_DEN` in the instrument. The test's suffix, `siUSP24 (+IFN)_sic (+IFN)`, is
read off the header. **The bead columns carry the same condition labels as the IP columns.** So if
Perseus grouped by condition, the paper's test was 4 against 4 with the beads included, and T1/T2
decide which.

| # | Line | Kind | Prediction |
|---|---|---|---|
| T0 | untested by rule; q among them | reasoned, high — **not blind**: the survey dated "Difference and test statistic … =0: 2" (§7) | **2** untested rows, q = 1 on both. What is unseen is whether both carry the full signature (−log p 0 as well) |
| T0b | rows with a finite Difference | identity | 4,410 |
| **T1** | IP 3 v 3, declared order, tested rows | reasoned, moderate | **max \|dev\| ≤ 1e-3 — D6-revised's gate.** Ground: the paper reports IP against IP across conditions, and the survey found one IP-vs-IP test |
| T2 | IP + beads, 4 v 4 | reasoned, moderate | max \|dev\| > 1e-3. **Exactly one of T1's and T2's lines comes in ≤ 1e-3** |
| T3 | IP 3 v 3, reversed | reasoned, high | max \|dev\| > 1e-3, with few rows within 1e-3 |
| T4 | untested rows, IP 3 v 3 | reasoned, moderate | max \|dev\| > 1e-3: their arm means differ, as S1's did. If it is 0, both are genuine exact nulls and (a)'s limit is what dropped them |
| T5 | T1's median, for precision | reasoned, low; not a gate | ≤ 1e-4 (S1's agreeing rows: 1.5e-5) |

**What each outcome does.**
- **T1 ≤ 1e-3 and T0 holds:** D6-revised is supported on an export that did not shape it. It may
  be built once bzk accepts the record.
- **T1 > 1e-3 and T2 ≤ 1e-3:** the paper's test included the beads. **The mechanism still worked**,
  because it identified the true binding, so D6-revised stands. But the declared 3 v 3 was wrong,
  and **I22 (D2) would refuse the arms that reproduce the paper's own test**, since an arm mixing
  `ip` and `no_antibody_control` is refused. That conflict is resolved in this record before any S3
  curation, though not before D6-revised's build.
- **T1 and T2 both > 1e-3:** D6-revised is refuted. The arithmetic proof is dropped. The Perseus
  binding is revised to a declared-only standing, labelled as such, and the tolerance is not
  loosened.
- **T0 or T4 off prediction** (count not 2, signature incomplete, or untested rows' means equal):
  rule (a) is revised and re-registered before any build.

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
