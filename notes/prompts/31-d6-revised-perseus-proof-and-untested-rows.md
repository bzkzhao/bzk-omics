# Prompt 31 — Build ADR-0038 D6-revised: the Perseus binding proves itself, and untested rows mint no result

**Repository:** `main` at the commit adding this prompt.

**Governing:**
- `decisions/0038-contrast-arms-are-declared-and-bound-at-the-loader.md`:
  - **D6-revised (l.342–419)** in full, including its *Limits*;
  - *Results* E1–E4 (l.759–768), the S1 measurements rule (a) was built from;
  - *Results — PV-S3 and ORIGIN* (l.877–938), the out-of-sample test that supports it;
  - **D6 (l.279–341) stays in the record, refuted.** Read it to know what was refuted; do not
    build it.
- `notes/REVIEWER-HANDOFF-2026-10-08.md` §6, for P2, P3 and what 29 made available.
- `CLAUDE.md` l.95–99, the four-point close.

**Settled ground.** ADR-0038 and ADR-0039 accepted. D1, D2, D4, D8 built at `ce9e83e`; D5 and
D7's producer refusal at `402fce8`, with its Mac run confirmed on 2026-10-09 (`[4b]` unchanged,
`Analysis.label` overwritten in place, no id moved). `ONTOLOGY.md` v1.46. This prompt builds
**D6-revised (a), (b) and (c)'s minting half**, and **P3**. It does not build:
- D6-revised (c)'s **display** half — the view that says *not tested by the source analysis* —
  which is prompt 32, together with D7's `_check_I4` and the query layer;
- the protein-groups binding (ADR-0038 M8) — order item 3.

**This is a schema change, but not an identity change.** `Analysis` gains one **non-identifying**
field (P3). No id moves anywhere. `tables_created` stays at **60**: the field is a column on an
existing node table, not a table. Both are pre-registered in §3.

**Edits are limited to** `ONTOLOGY.md`, `bzk/ontology/schema.py`, `bzk/adapters/perseus.py`,
`bzk/sources/pxd055843_perseus.py`, `data/curation/curation_PXD055843.json` (§2.5 and §2.6 only),
the six `tests/fixtures/perseus_synthetic_*.txt`, and `tests/`. No ADR, no `ROADMAP.md`, no
`HANDOFF.md`, and nothing under `notes/` other than this prompt.

The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **Repository state.**
   - `git log --oneline -3`, `git status --short`. HEAD is this prompt's commit, tree clean.
   - Open-of-turn: `uv run pytest`, `uv run pytest tests/test_schema.py`, `uv run mypy bzk tests`,
     and both `ruff` targets.
   - Expected **in a container**: `945 passed, 14 skipped`; 20 passed; `Success` over 117 files;
     clean / 117. The skip count is environment-dependent (handoff 10-08 §4.4) — report what you
     see.
2. **Rule (a), quoted, and what it must not read.**
   - Quote ADR-0038 l.350–353 verbatim.
   - State the three conditions for *untested*, and say **why the rule reads no arm column**.
   - Expected: Difference `0`, −log p `0` (p = 1), and test statistic `0` **where the file carries
     that column**; reading no arm column is what keeps the proof failing closed, because a wrong
     binding must still agree on every row the file tested.
3. **Why S1 cannot confirm the rule, in one sentence.**
   - Quote the sentence in D6-revised (a) that says so.
   - Expected: S1's 27 refused rows have exactly that signature and no agreeing row has Difference
     `0`, so the rule picks out those 27 **by construction** — S1 shaped it; PV-S3 is the test.
   - Say what §3's S1 parse therefore does and does not establish.
4. **What the adapter reads today.**
   - Name the four module-level column templates in `bzk/adapters/perseus.py` (l.138–141) and say
     which three `_contrast_reader` resolves.
   - Say whether any test-statistic column is read today. Expected: **no** — `Difference`,
     `q-value`, and one of `p-value` / `-Log p-value`; the statistic column is not read at all, so
     rule (a) needs a fourth template.
   - Name the exact statistic column ADR-0038 E1 observed in S1.
   - Expected: `Student's T-test Test statistic siUSP24_IFN_siCTRL_IFN`.
5. **Where a result is minted, and what rule (c) must skip.**
   - Quote `perseus.py`'s result loop, **l.547–575**, far enough to show the `DifferentialResult`
     mint and its three edges.
   - State precisely what rule (c) keeps and what it drops for an untested row.
   - Expected: the `ProteinObservation`, its `REPORTS_PROTEIN` and `RESOLVES_TO_PROTEIN` edges and
     its **cells** are emitted as usual; only the `DifferentialResult` node and its
     `WAS_GENERATED_BY` / `RESULT_FOR_PROTEIN` / `RESULT_IN_CONTRAST` edges are not.
6. **P3's field, and the precedent that is not one.**
   - Quote `ONTOLOGY.md`'s `Analysis` DDL opening (**l.479–480**).
   - State what P3's field holds, and whether `parameters_json` is a precedent for its **identity**
     status.
   - Expected: a per-`Contrast` untested count, **non-identifying**; `parameters_json` is the
     precedent for representation only — a canonicalized JSON object in a `STRING` — and is itself
     **identifying** (l.120, l.175), which this field must not be.

**Do not start §1 until bzk replies.**

---

## 1. What this prompt builds, and the readings it adds

- **(a)** Untested rows recognised from the statistics columns alone.
- **(b)** Every tested row recomputes the Difference from its arm values and agrees within
  **1e-3**; at least one row must be tested; a file carrying statistics but no sample columns is
  refused.
- **(c), minting half.** An untested row mints no `DifferentialResult`. The external `Analysis`
  carries the per-contrast untested count (P3), and `PerseusIngestReport` reports the same count.

**Three readings this prompt adds, none in the record:**

- **The proof is the adapter's, not a test's.** (b) is a property the adapter enforces on every
  parse, for every file, not an assertion in `tests/`. A fixture proves the enforcement works; it
  is not itself the proof.
- **(a) and (b) must be ordered, and the order is load-bearing.** A row is classified by (a)
  **first**; only rows (a) calls tested are put to (b). Reversed, an untested row's `0` Difference
  would be compared against a recomputed value, fail (b), and refuse the whole file — which is the
  carried finding reappearing as a crash instead of as a false null.
- **The count is per contrast, and `PerseusAdapter` takes a list of contrasts** (`perseus.py`
  l.346). One number for the file would be wrong the moment a second contrast is declared, which
  is the hazard P3 chose (i) to avoid. Both committed analysis records declare one `contrast`, so
  on present data the map has one entry — build for the list anyway.

---

## 2. The build

### 2.1 `bzk/adapters/perseus.py` — rule (a), recognising an untested row

- A fourth module-level template beside l.138–141, for
  `Student's T-test Test statistic {suffix}`.
- `_contrast_reader` resolves it **where present** and records whether it was. Its absence is not
  an error — D6-revised *Limits* says a file without it recognises untested rows on Difference and
  p alone, and that this is weaker. Say so in the docstring.
- A row is untested when Difference is `0`, −log p is `0` (p = 1), **and** the statistic is `0`
  where the column exists. q is **not** part of the rule: q is computed across rows, so it is not
  a property of one row's test. Record that beside the rule.

### 2.2 `bzk/adapters/perseus.py` — rule (b), the proof

- For every **tested** row, recompute the Difference from the arms' sample values in the file and
  require agreement within **1e-3**. The tolerance is R2's, fixed before PV ran; do not change it,
  and do not make it a parameter.
- `DeclaredContrast` gains the arms. They come from `LoadedCuration.contrast_arms`, as prompt 30's
  producer takes them — **the adapter derives nothing and re-resolves no mapping key**.
- Refuse, each with its own message and its own test:
  - **no tested row in the file** — a file where (a) excludes everything proves nothing;
  - **a tested row disagreeing by more than 1e-3**, naming the row and the deviation;
  - **a file carrying the statistics columns but no sample columns**, which cannot be proved at
    all.
- The refusal messages must distinguish these three. A single "proof failed" is the compound
  clause this series keeps paying for.

### 2.3 `bzk/adapters/perseus.py` — rule (c) and the count

- An untested row mints no `DifferentialResult` and none of its three edges. Its
  `ProteinObservation`, that observation's edges, and its cells are unchanged.
- `PerseusIngestReport` gains `rows_untested`, **per contrast**, keyed by the contrast's id.
- The same per-contrast count goes on the external `Analysis` node as P3's field (§2.4).
- The two must be the same number by construction, not by coincidence: compute once, use twice.

### 2.4 P3 — the field on `Analysis`

- **`ONTOLOGY.md`:** one new column on the `Analysis` node table, with its comment; `§3`'s
  identity table **unchanged**; the `Analysis` row in l.120's table notes the field is
  non-identifying. Version 1.46 → **1.47**.
- **`bzk/ontology/schema.py`:** the mirror. **Nothing in `IDENTITY`** — identity is an allow-list
  (`schema.Identity`), so non-identifying means absent from `fields`.
- **Representation:** a canonicalized JSON object in a `STRING`, mapping each `Contrast` id to its
  untested count. `parameters_json` is the precedent **for representation only**; unlike it, this
  field is not identifying and is not canonicalized into any id.
- An internal `Analysis` — one the platform ran — carries no such count. State what the field
  holds in that case and why, in the DDL comment.

### 2.5 `bzk/sources/pxd055843_perseus.py` — the source module

- Takes the arms from `LoadedCuration.contrast_arms` and passes them in `DeclaredContrast`.
- Prints the per-contrast untested count.
- **PXD055843 stays blocked** on the PI's imputation answer and I15's seed
  (`data/curation/analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` `unresolved[1]`). This module
  must still build a change-set `invariants.validate` refuses, by design. Do not "fix" that.
- **One stale sentence, in scope.** That record's `rationale` says `contrasts_of_interest` is
  *"carried verbatim onto `LoadedCuration.contrasts` and read by nothing"*. False since `ce9e83e`:
  the loader resolves the arms and emits six edges from them. Correct that clause in
  `data/curation/curation_PXD055843.json` and change nothing else in it except §2.6.

### 2.6 P2 — `curation_PXD055843.json` → `unresolved[4]`

**After §5's Mac run, not before.** The entry is *"Which arm of the contrast is the numerator"*,
`unresolved[4]` of `data/curation/curation_PXD055843.json`, zero-indexed. The other ten entries
and all four in the analysis record are untouched.

- Its ground today is the record's own: the statistics columns carry the Perseus suffix
  `siUSP24_IFN_siCTRL_IFN`, marked **MEASURED HERE**, and Perseus writes numerator first. **That
  stays primary.**
- **Not PV1**, which was refuted (ADR-0038 *Results*). The exploratory diagnostic at `a458628`
  corroborates and is named nowhere in the entry.
- The edit adds §5's run as a third support, **still noting it is in-sample**, and does not
  displace the suffix. 0 ids move.
- If §5 has not run when the rest is ready, **leave the entry alone**, commit without it, and say
  so. It then rides in whichever commit records §5's results.

### 2.7 The fixtures and the call sites

- The six `tests/fixtures/perseus_synthetic_*.txt` gain sample columns consistent with their
  Difference values, plus untested rows. A fixture whose Difference no longer matches its samples
  is a fixture that would refuse under (b).
- 22 `PerseusAdapter(` call sites in `tests/`. Count them before and after.
- Constructed fixtures for **every** refusal in §2.2 and for the untested signature.

---

## 3. Pre-registration — this container

**Not rehearsed.** No part of this was built in a scratch clone first. Every figure is read from
the record or the code, and §3's job is to be falsifiable.

**C1 — the rule picks out S1's 27 rows.** On a constructed fixture carrying ADR-0038 E2–E4's
signature — Difference `0`, −log p `0`, statistic `0` — the row is untested; a row with any of the
three non-zero is tested. **In-sample by construction** (§0.3): this shows the code implements the
rule, not that the rule is right.

**C2 — (a) runs before (b).** A fixture whose untested row carries arm values that would *fail*
(b) must parse cleanly. If (b) ran first, the file would be refused. This is the ordering test and
it is the one most easily lost.

**C3 — the three refusals are distinguishable.** Three constructed fixtures, three different
messages: no tested row; a tested row off by more than 1e-3; statistics columns with no sample
columns.

**C4 — the count appears in two places and agrees.** `PerseusIngestReport.rows_untested` and the
`Analysis` field carry the same per-contrast number on the same parse.

**C5 — no id moves, and `tables_created` stays 60.** The field is non-identifying and is a column
on an existing table. Check the `Analysis` ids of both committed analysis records before and
after, and `tests/test_rebuild.py`'s `tables_created` assertion.

**C6 — `tests/fixtures/pxd018299_curation_ids.json` is unchanged.** *(Stated narrowly: this prompt
edits `tests/fixtures/perseus_synthetic_*.txt` by design, so `git diff -- tests/fixtures/` is
**not** empty and must not be pre-registered as such — that was prompt 30's §3 defect carried
forward from the plan, and it is not repeated here.)*

**The checks:**

| Check (target) | Before | After, predicted |
|---|---|---|
| `uv run pytest` (full) | 945 passed, 14 skipped | all pass; state the counts |
| `uv run pytest tests/test_schema.py` | 20 passed | 20 passed **+ any new DDL mirror assertions**; state the number |
| `uv run mypy bzk tests` | Success, 117 files | Success; state the file count, and say so if a new test module moved it |
| `uv run ruff check bzk tests` / `ruff format --check bzk tests` | clean / 117 | clean; state the count |

**Mutation evidence is required** for every new refusal in §2.2, for rule (a)'s three conditions,
for rule (c)'s skip, and for C2's ordering. Each made to fail, read back, reverted; bytecode
disabled from the start. **`python -I` does not disable bytecode** — it implies `-E`, which ignores
`PYTHONDONTWRITEBYTECODE` (handoff 10-08 §5). Use the environment variable with a plain
interpreter.

**If any prediction fails, stop and report. Do not adjust code, fixtures or pins to match.**

---

## 4. Commit and report

**One commit**, fast-forwarded onto `main`, single subject line in the series' form, naming:
D6-revised built; untested rows recognised from the statistics columns and minting no result;
every tested row proving the binding within 1e-3; the per-contrast count on `Analysis` and in the
report; ONTOLOGY v1.46 → v1.47; 0 ids move and `tables_created` stays 60.

**Files expected:** `ONTOLOGY.md`, `bzk/ontology/schema.py`, `bzk/adapters/perseus.py`,
`bzk/sources/pxd055843_perseus.py`, `data/curation/curation_PXD055843.json`, the six
`tests/fixtures/perseus_synthetic_*.txt`, and `tests/`. Any other file needs a reason in the
report.

**Report:** the commit hash; §0's answers; C1–C6 as measured; §3's table with "After" measured;
every new refusal's message on the unmutated tree; the mutation evidence; the full `ONTOLOGY.md`
diff; `git diff --stat`; and the four-point close. State explicitly whether §5 ran and whether
§2.6's edit is in this commit or owed.

Then stop.

---

## 5. For bzk's Mac — a read-only parse, no graph write

PXD055843 stays blocked on the PI and I15, so this parses S1 and writes nothing to the graph.

- **Results that would be emitted: 7,583. Untested: 27. Binding accepted.**
- **In-sample.** S1 shaped rule (a) (§0.3), so this shows the code reproduces the diagnostics, not
  that the rule is right. PV-S3 at `59bb0d2` is the out-of-sample support, and it is already in the
  record.
- `git status --short` shows only the deferred prompt 22.
- **No `Step A` id snapshot is needed** — nothing is written. If a later prompt wants a graph-level
  id sweep, note that `rebuild` drops the stores first, so Step A must run **before** the pull
  (handoff 10-08, and prompt 30's §5).

---

## Out of scope

- D6-revised (c)'s **display** half, D7's `_check_I4`, the query layer and the UI — prompt 32.
- **The one-composition-site guard.** Prompt 30 found `_site` had been breaking that rule
  unnoticed and routed it through `_compose`, but nothing enforces it; a fourth site could appear
  the same way. Its own prompt.
- **`site_change_set` does not check that its `arms` belong to its `contrast`.** `ContrastArms`
  carries no contrast id, so a caller can pass a mismatched pair. Its own prompt.
- `_literal_reads`' blindness to a key read off `json.loads(...)`; the protein-groups binding (M8);
  `write_cells` over-reporting; the drift checker; the stale tautology floor; F-d; a D2/D3
  invariant-level check.
- **ADR-0032 (Proposed) should take D6-revised (c) into its review** (ADR-0038 l.399). Not this
  prompt's to do, and not to be forgotten.
