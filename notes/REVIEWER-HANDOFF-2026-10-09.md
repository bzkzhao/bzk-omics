# REVIEWER HANDOFF — 2026-10-09

**Public version.** This file supersedes `notes/REVIEWER-HANDOFF-2026-10-08.md` as the starting
point. That file stays as the record of the day before.

**What is not restated here.** Items the earlier handoffs carry, which this session did not touch,
are not repeated. Read this file's §6 and §7 alongside:
- 2026-10-08 §6.7 and §7 (this file's §7 says what changed);
- 2026-10-07 §6.4–§6.6, for the scope prompts 30–32 inherit;
- 2026-10-05 §7, 2026-10-04 §7, 2026-10-03 §6–§8.

**Line references** are to `main` at `2d1fc83` (`ONTOLOGY.md` v1.47). `bzk/adapters/perseus.py`
grew by 238 lines and `bzk/adapters/maxquant_sites.py` by 78, so **every line reference into those
two files taken from a handoff dated 10-08 or earlier is stale**. This file's own references were
read at `2d1fc83`. The repository now has two modules named `store.py`; only
`bzk/ontology/store.py` is on the write path.

**Dating.** The session ran 2026-10-08 evening to 2026-10-09.

**ADR-0038 remains the dated home for the figures it produced.** This file adds one measurement it
did not have — §4.1 — and names where it was taken.

---

## 1. Where things stand

| Item | State at `2d1fc83` |
|---|---|
| `main` | `2d1fc83`, pushed. Six commits since `a4bdd8c` (§2) |
| `ONTOLOGY.md` | **v1.47**, last reviewed 2026-10-09 |
| Checks | `pytest` **969 passed, 8 skipped** on bzk's Mac; **963 passed, 14 skipped** in the reviewer's container. Both total 977 — the six-test environment split of 10-08 §4.4, unchanged. `pytest tests/test_schema.py` 20 passed; `mypy bzk tests` clean over 117 files; both `ruff` targets clean |
| ADRs | 38 files: 26 Accepted, 9 Proposed, 3 Superseded |
| **ADR-0038** | **D1, D2, D4, D5, D8, D6-revised and D7's producer half are built.** Only **D7's display half** remains — prompt 32 |
| ADR-0039 | Accepted and built |
| Graph on bzk's Mac | Current. Cold-rebuilt 2026-10-08 at `ce9e83e`, differential re-run 2026-10-09 at `402fce8` |
| PXD055843 ingestion | Still blocked on the PI's imputation answer and I15's seed (`analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` `unresolved[1]`). **The adapter is now built and its proof runs**, §4.1 |

## 2. What this session did

Six commits. Four were landed by bzk with `git am`; **`402fce8` and `4724046` were committed and
pushed by the build sessions themselves** (`author=Claude, committer=Claude`), the fourth
authorship class 10-08 §5 named.

| Commit | What |
|---|---|
| `7e53ff3` | Prompt 30 committed |
| `402fce8` | **D5 and D7's producer refusal built** |
| `9a4fa80` | Prompt 30 §5 corrected: the Mac rebuild recorded as satisfied, and the id check fixed (§4.3) |
| `ba7e5b4` | Prompt 31 committed |
| `4724046` | **D6-revised and P3 built**; ONTOLOGY v1.46 → v1.47 |
| `2d1fc83` | **P2**: `curation_PXD055843.json` `unresolved[4]` cites §4.1's run; §4.1's measurement recorded |

**What `402fce8` builds (D5, D7's producer half):**
- `maxquant_sites.bind_column(mapping, sample_id, quantity, header)` — the one route from a
  `Sample` to a column, asked for **one** family and refusing when that family's header is absent
  even where another family's is present.
- `_compose` is the single composition-and-membership routine, with **three** callers:
  `_sample_columns` (any family), `bind_column` (the one asked for) and `_site` (each in turn).
- `pxd018299_differential.py`: `CONTRAST` and `_intensity_columns` deleted; the contrast id read
  once from the analysis record, with no module constant; arms from `contrast_arms`.
- `site_change_set` takes `arms: ContrastArms` and **refuses any kind but `condition`**.

**What `4724046` builds (D6-revised, P3):**
- **(a)** a fourth template, `STATISTIC`, bound where the file carries it; a row is untested when
  Difference, −log p and (where present) the statistic are all `0`. q is not in the rule.
- **(b)** every tested row recomputes its Difference from the arms within `PROOF_TOLERANCE = 1e-3`,
  with **four** distinct refusals (§4.2).
- **(c)** an untested row mints no `DifferentialResult` and none of its three edges; its
  observation, that observation's edges and its cells are unchanged.
- **P3**: `Analysis.rows_untested_json`, **non-identifying**, absent from `IDENTITY`, NULL on a
  `processing` or `curation` analysis. One classification — `untested_lines`, a `frozenset` —
  feeds both `PerseusIngestReport.rows_untested` and the node field, so the two agree by
  construction.

## 3. Dated home — the runs behind these two builds

**Prompt 30, container.** B1: `bind_column` returns ADR-0038 M7's six headers in arm order against
`ROADMAP.md` l.7073's 159 columns — **re-measured independently in the reviewer's clone** at
`402fce8`. B2, B3, B4 held. Six mutations.

**Prompt 30, Mac, 2026-10-09.** `[4b]` **identical to the pre-30 baseline** — 2,341 → 2,298 →
2,056 → 2,029 → 1,362; 3,997 of 8,172; 516; 12 of 14; 4,090 / 5,450. `git status` clean but for the
deferred prompt 22, so `pxd018299_platform_targets.json` came back byte-identical and all 39 pinned
observation ids survived. The `Analysis` node `bzk:2e2f0ade51447fd0bcc208edeace1598` kept its id and
its `label` changed in place to `welch_t KO_IFN_vs_WT_IFN (BH)` — `MERGE … SET` confirmed on real
data.

**Prompt 31, container.** C1–C6 held. **Seventeen mutations**, every one read back, fired and
reverted. The reviewer re-measured independently at `4724046`: `rows_untested_json` absent from
`IDENTITY["Analysis"].fields`; both curation `Analysis` ids byte-identical to `ba7e5b4`; only the
three statistics-bearing fixtures moved; `pxd018299_curation_ids.json` untouched; `tables_created`
still 60.

**Prompt 31, Mac, 2026-10-09 — §4.1.**

## 4. Corrections and new measurements

### 4.1 ADR-0038's open margin on S1, now measured

ADR-0038 l.390–392 records, of rule (b)'s tolerance: *"the largest deviation among S1's tested rows
lies somewhere between 6e-5 and 1e-3, and was not printed. So the margin at the top is unknown."*

The S1 parse at `4724046` prints it:

> `contrast bzk:180e18ad99631bba5da4a6e6734cd6a9: binding accepted — 7,583 tested row(s) within
> 0.001 (max deviation 7.73e-05); 27 untested row(s), no result minted for them`

- **7.73e-05**, about 13× inside the tolerance and just above the recorded p99 of 6e-5 — the tail
  is short, not long.
- Beside **PV-S3's T1 of 7.27e-5** over S3's 4,408 tested rows, the two files' worst cases agree to
  within 6%. That is a stronger consistency than either number alone, and PV-S3 remains the
  out-of-sample support.
- **S1 is in-sample.** It shaped rule (a), so this shows the code reproduces the diagnostics, not
  that the rule is right.
- ADR-0038 is `Accepted` and is **not** edited. The measurement lives in
  `curation_PXD055843.json` `unresolved[4]` (P2, `2d1fc83`) and in that commit's message.

**I15 then refused the change-set, by design**, and PXD055843 remains un-ingested. The refusal
arrives as an **uncaught traceback**, not a stated refusal — correct behaviour, but a reader who
does not know the convention cannot tell it from a crash. The proof line printing *before* it is
what makes the run readable, and that only works because the build moved the proof ahead of
emission (§5).

### 4.2 To prompt 31 §2.2 — three gaps the build found and closed

The prompt named one refusal where three were needed, and the build stopped and asked. All three
of its proposals were right, and the first would otherwise have been a silent vacuous pass.

1. **Rule (b) binds from `_sample_columns`' `placed`, never from `samples`.** `perseus.py` has
   `samples = [] if withheld else placed`, and `_withheld_because` returns a reason whenever the
   declared imputation method is not `"none"` — which PXD055843 always declares. **A proof sourced
   from `samples` would have found no arm values, checked nothing and passed, on the one real file
   it exists for.** Withholding is an I11 question about *retaining values*; the binding is a D5
   question about *naming columns*. The code now says so.
2. **A partially-placed arm is refused under the same refusal as no sample columns**, naming the
   unplaced arm samples. A mean over a subset is a different Difference —
   `_withheld_because` already reasons this way.
3. **A tested row with a blank or non-finite arm value is refused, not skipped.** PV's instrument
   skipped such rows (`notes/scripts/measure_adr0038.py` l.345–348), which was right for reporting
   a maximum and wrong for a rule claiming *every* tested row. **This diverges from PV
   deliberately**; S1 and S3 have no blanks, so it decides nothing on present data.

### 4.3 To prompt 30 §5 — an id check that was never checkable

§5 asked for *"`DifferentialResult` ids 0 moved"* from a before/after of the graph. The
2026-10-08 cold rebuild had emptied the results, so no prior state existed. Corrected in
`9a4fa80`: `tests/fixtures/pxd018299_platform_targets.json` byte-identity is the id check — it
pins `population.tested = 1362` and 39 observation ids across 14 targets.

**The general rule, now recorded twice:** `rebuild` drops the stores (`bzk/rebuild.py` l.154), so a
graph-level id sweep needs its Step A run **before** the pull. Prompt 28 managed it; prompt 29
inherited the wording without the ordering.

### 4.4 To prompt 30 §0.4 and §3 — two scope defects in the prompt

- **A `grep` scoped to one file is not a scope check.** §0.4 asked for
  `grep -n CONTRAST bzk/sources/pxd018299_differential.py`. A **repo-wide** grep finds
  `bzk/sources/pxd018299_published_cascade.py` building `KO_COLUMNS`/`WT_COLUMNS` from
  `differential.CONTRAST` — deleting the constant broke that module at import. (Those two names are
  at l.93–94 at `2d1fc83`, now literals; they were at l.89–90 before `402fce8`.) **Before deleting a
  module-level name, grep the repository for it, not the file.**
  - Resolved by spelling S1's six column names out as literals, identical strings, beside
    `S1_AS_DEPOSIT` which already spells its siblings. **D5 does not govern that file**: S1 is the
    published spreadsheet, with no `Sample` binding, so the derivation was a string convenience.
- **A file count is not a check result.** §3 pre-registered *"Success, 117 files"* for `mypy`,
  which encoded an assumption that no module would be added. The binding tests went into the
  existing `tests/test_maxquant_sites.py` — the house pattern, one test module per adapter module
  — so the count held, but the figure should have said what it assumed.

### 4.5 To prompt 31 §2.7 — six fixtures, three with statistics

The prompt said the six `perseus_synthetic_*.txt` fixtures gain sample columns. Only
`groups`, `plain_pvalue` and `proteins` carry a Difference column; the other three are refused
before rule (b) runs, so there is nothing for them to be consistent with. The prompt counted files,
not files-with-statistics.

## 5. How this session ran

**A prompt's `§0` stopped two builds, both times correctly, and both times for something outside
the prompt's own content.** Prompt 30's build found the prompt had never been committed, so HEAD
was not "this prompt's commit". Prompt 31's build found three unanswerable gaps in §2.2 before
writing a line. **Both cost a turn and both were avoidable from the reviewer's side:** a prompt now
ships as a patch at the same time as the draft, and bzk lands it before the build is released.

**The failure path, read before the happy path.** PXD055843's parse is *always* refused by I15
inside `validate`, which runs **before** `report` is set. A print placed after `build` would never
execute on the one real file, and §4.1's figures would have been unreadable. The build moved the
proof ahead of emission, printed it in a `finally`, and wrote a test that it survives the refusal;
mutation M13 confirms it fires. **A prompt that only describes the success path can specify an
output that cannot exist.**

**One classification, written twice.** Rule (c)'s skip and `rows_untested` are the same
`frozenset`, so the report and the `Analysis` field cannot disagree. That is the shape to prefer
over two computations that happen to match.

**Mutation testing keeps finding holes in the work that produced it.** Prompt 29 found I22's
`_CHECKS` gap; prompt 30 found `_site` had been breaking the one-composition-site rule unnoticed;
prompt 31 recorded M8′ firing as a `KeyError` rather than its intended refusal, which is an honest
report of a mutation that went red for the wrong reason.

**The common cause, still being paid.** Of this session's five corrections, three are a scope or a
count asserted rather than measured (§4.3, §4.4 twice) and two are a clause that needed splitting
(§4.2, §4.5). The two standing rules now have a third:
- *measure the thing you add, not only the thing you were told about* (10-07);
- *a line reference is a measurement with a shelf life* (10-08);
- **a scope is a measurement too — grep the repository, not the file, and say what a pre-registered
  figure assumes.**

## 6. Next — prompt 32, the last of the four

**Scope:** `ONTOLOGY.md` I4, `bzk/ontology/invariants.py`, `bzk/query/graph.py`, `bzk/ui/app.py`,
`tests/`. The 2026-10-07 handoff §6.6 has the inherited detail; this section records what the two
builds changed about it.

- **`_check_I4` widens.** Today (`bzk/ontology/invariants.py` l.386) it checks the tri-state and
  that `applied` carries an `ADJUSTED_BY` edge. D7 adds: **a result with a `RESULT_FOR_PROTEIN`
  edge must be `not_applied`**. ADR-0038 M10 measured every committed `applied`/`native` fixture
  result as site grain, so this refuses nothing that exists.
- **The query layer derives kind and maps (grain, kind, state) to D7's table** (ADR-0038 l.426–432,
  the table rows at l.428–432),
  with **no fallback** — a cell with no label is a cell no result may occupy. `invariants.contrast_kind`
  (l.874) already exists and is the one derivation; the query layer must call it, not re-derive.
- **ONTOLOGY I4 widens from *"on a site"* to every grain**, and the code copy of the label table is
  guarded against §8 as every other mirror here is.
- **The untested-row display** — D6-revised (c)'s display half — now has a real field to check
  against: `Analysis.rows_untested_json`, per `Contrast` id. For each contrast an external
  `Analysis` carries, the view derives the observations with no result there and compares.
  **Equal: *not tested by the source analysis*. Unequal: a mismatch error, never the label.**
- **`bzk/query/graph.py` has no generic projection** — zero occurrences of `properties(` — so a
  store one column behind the schema returns the same rows. That was checked for prompt 30 §6.5 and
  still holds; a prompt 32 that adds one breaks it.

**Mac run:** read-only query. All 1,362 `DifferentialResult`s should map to
*stoichiometry-uncorrected*. **The untested display is container-only**: no Perseus result is in
the graph and none can be until PXD055843 unblocks.

## 7. Open items — what changed since 2026-10-08 §7

**New, each machine-checkable and each needing its own prompt:**
- **The one-composition-site rule is enforced by nothing.** `_site` broke it unnoticed until
  prompt 30; a fourth site could appear the same way. The guard would be an AST check that only
  `_compose` builds a family-prefixed header in `maxquant_sites.py`.
- **`site_change_set` does not check that its `arms` belong to its `contrast`.** `ContrastArms`
  carries no contrast id, so a caller can pass a mismatched pair.
- **A blank or non-numeric statistics cell raises a bare `ValueError`** naming neither row nor
  column. Pre-existing on Difference, p and q; now inherited by the statistic column rule (a)
  reads.
- **`bzk/sources/pxd055843_perseus.py`'s module docstring** says the graph gets "the
  `ProteinObservation`s and their `DifferentialResult`s", without noting that untested rows get
  none. Stale since `4724046`.
- **Eighteen `claude/*` branches on the remote.** `CLAUDE.md` says development lands directly on
  `main`. A sweep, not a build item.

**Changed:**
- **The 2026-10-08 §7 items on `_literal_reads`** and the Perseus "arms are identifying" sentence:
  the second is **closed** (`402fce8` fixed the sentence *and* its docstring twin; the phrase is
  gone from `bzk/sources/pxd055843_perseus.py` at `2d1fc83`, so the old l.109 / l.97–98 references
  resolve to nothing);
  `_literal_reads`' blindness to a key read off `json.loads(...)` stays open.
- **`curation_PXD055843.json`'s stale `rationale`** is **closed** (`4724046`).

**Closed:**
- 2026-10-07 §6.4 (prompt 30) and §6.5 (prompt 31), including P2 and P3.
- ADR-0038's unmeasured S1 margin (§4.1).

**Unchanged and still open:** the drift checker reporting failed fetches as drift; F-b generalised;
F-d; R6's prefix-only check; the stale tautology floor; `write_cells` over-reporting (M11); the
protein-groups adapter's silently dropped family (M8); **ADR-0032 taking D6-revised (c) into its
review** (ADR-0038 l.399, still not done); a background-enrichment concordance basis value; the
D2/D3 invariant-level check; I22's dependence on the loader being the only `Contrast` minter.

**Questions for the PI, collected** (none blocks prompt 32; the first blocks PXD055843 ingestion).
Each names the file it is recorded in, because both PXD055843 records carry an `unresolved` list:
1. Did imputation run on S1 (I15's seed)? *(open since September.)*
   `analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` `unresolved[1]` states the block;
   `curation_PXD055843.json` `unresolved[2]` states the I15 requirement only.
2. Where the untested rows come from — **now 27, confirmed by the accepted rule** (§4.1). Recorded
   in no `unresolved` entry; new from ORIGIN.
3. s0 for S1's test. `analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` `unresolved[0]` and
   `curation_PXD055843.json` `unresolved[1]`.
