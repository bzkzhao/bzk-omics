# Prompt 32 — Build ADR-0038 D7's display half and D6-revised (c)'s: I4 per grain and kind, and the untested-row label

**Repository:** `main` at the commit adding this prompt.

**Governing:**
- `decisions/0038-contrast-arms-are-declared-and-bound-at-the-loader.md`:
  - **D7 (l.421–458)** in full — its table at l.426–432, its *Where each refusal sits* at
    l.444–457;
  - **D6-revised (c)** (l.394–407), the display half only; its minting half is built;
  - **M9 (l.632–635) and M10 (l.636–641)**, the measurements that say what exists today.
- `notes/REVIEWER-HANDOFF-2026-10-09.md` §6, which records what prompts 30 and 31 changed about
  this scope.
- `ONTOLOGY.md` I4 (l.916) and §8.
- `CLAUDE.md` l.95–99, the four-point close.

**Settled ground.** ADR-0038 and ADR-0039 accepted. D1, D2, D4, D5, D8, D6-revised and D7's
**producer** half are built. `ONTOLOGY.md` v1.47. **This prompt is the last of the four** and
finishes ADR-0038. It does not build:
- the protein-grain IP writer or the protein-groups binding (M8) — order item 3;
- anything that would let a protein-grain `applied` result exist — D7 refuses it for now, and
  opening it is its own record.

**This is not a schema change and not an identity change.** No DDL column is added, no id moves,
`tables_created` stays **60**, and `ONTOLOGY.md` goes v1.47 → **v1.48** for I4's widening alone.

**Edits are limited to** `ONTOLOGY.md`, `bzk/ontology/invariants.py`, `bzk/query/graph.py`,
`bzk/ui/app.py` and `tests/`. No ADR, no curation record, no fixture under `tests/fixtures/`
unless a refusal needs one, no `ROADMAP.md`, no `HANDOFF.md`, and nothing under `notes/` other
than this prompt.

The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **Repository state.**
   - `git log --oneline -3`, `git status --short`. HEAD is this prompt's commit, tree clean.
   - Open-of-turn: `uv run pytest`, `uv run pytest tests/test_schema.py`, `uv run mypy bzk tests`,
     both `ruff` targets.
   - Expected **in a container**: `963 passed, 14 skipped`; 20 passed; `Success` over 117 files;
     clean / 117. **On bzk's Mac the same suite is `969 passed, 8 skipped`** — six tests skip in a
     container and run there, both totalling 977 (handoff 10-09 §1). Report what you see.
2. **D7's table, quoted whole.**
   - Quote ADR-0038 l.426–432 verbatim — the header, the separator and all five rows.
   - State how many (grain, kind, state) cells carry a label and how many are refused.
   - **Say what a cell that is neither means**, in the record's own words.
   - Expected: *a cell with no label is a cell no result may occupy* — there is no fallback, and a
     result landing in one is an error, not an unlabelled row.
3. **What `_check_I4` checks today, and what D7 adds.**
   - Quote `bzk/ontology/invariants.py`'s `_check_I4` in full.
   - State its two existing clauses, and the third D7 adds.
   - Expected: the tri-state enum, and `applied` requires an `ADJUSTED_BY` edge; D7 adds **a
     result with a `RESULT_FOR_PROTEIN` edge must be `not_applied`**.
   - Name the measurement saying this refuses nothing that exists, and what it found.
   - Expected: M10 — every committed `applied`/`native` fixture result is site grain.
4. **Where kind comes from, and the one rule about it.**
   - Name the function that derives a contrast's kind and the module it lives in.
   - Expected: `bzk.ontology.invariants.contrast_kind` (l.874), from the anchor's `modality` and
     the arms' sample roles.
   - State whether the query layer may re-derive kind itself. Expected: **no** — kind is derived,
     never stored, and one derivation means one function. The query layer calls it.
   - Say what the query layer must read from the graph to call it.
5. **The display's two halves, and what each already has.**
   - For D7's label: name the field `bzk/query/graph.py` already returns for a result's state, and
     the line the UI prints it at.
   - Expected: `DifferentialRow.protein_adjusted` (l.122, selected at l.389); `bzk/ui/app.py`
     l.240.
   - For D6-revised (c): name the `Analysis` field prompt 31 built and what it holds.
   - Expected: `rows_untested_json`, non-identifying, per `Contrast` id, NULL on a `processing` or
     `curation` analysis.
6. **The projection rule this prompt must not break.**
   - Run `grep -c "properties(" bzk/query/graph.py` and `grep -c "RETURN \*" bzk/query/graph.py`.
   - Expected: **0** and **0**. Say why that matters.
   - Expected: every `Analysis` property is selected by name, so a store one column behind the
     schema returns the same rows (checked for prompt 30, handoff 10-09 §6). **A generic
     projection added here breaks that**, and nothing would catch it.

**Do not start §1 until bzk replies.**

---

## 1. What this prompt builds, and the readings it adds

- **D7's write-time refusal**: `_check_I4` gains the protein-grain clause.
- **D7's display**: the query layer derives kind, maps (grain, kind, state) to the table, and the
  UI shows the label.
- **D6-revised (c)'s display**: for each contrast an external `Analysis` carries, the view derives
  the observations with no result there and checks that count against `rows_untested_json`.

**Four readings this prompt adds, none in the record:**

- **The label table has one home and a guarded copy.** ADR-0038 says the table's home is
  `ONTOLOGY.md` I4 and the code copy is guarded by a test, *as every other mirror here is*. Follow
  the house pattern (`schema.py` ↔ §4–§7, `ABSENCE` ↔ §3, `CURATION_BASIS` ↔ §5.3,
  `_SAMPLE_ROLES` ↔ the `Sample` DDL comment, added in prompt 29).
- **No fallback is a refusal, not a blank.** A (grain, kind, state) triple with no cell must raise,
  naming the triple. A `—` or an empty string there is the *runs-cleanly-and-is-wrong* shape this
  repository exists to refuse, and it is what the absence machinery in `graph.py` was built to
  prevent at the row level.
- **The untested display must not infer from absence alone.** D6-revised (c) is explicit: the
  derived count and the recorded count must be **equal**, and where they are not the view shows a
  **mismatch error**, never the label. "No result here" cannot distinguish *untested* from *absent
  from the file* from *dropped by a fault*; only the agreement of two independently-obtained
  numbers can.
- **Two absences, two answers.** `graph.py`'s `Absence` enum exists because an empty list means
  several different things. The untested display adds another: a result that is absent **and**
  accounted for by the count. Decide where that sits relative to `Absence`, and say why in the
  code.

---

## 2. The build

### 2.1 `bzk/ontology/invariants.py` — `_check_I4`'s third clause

- A `DifferentialResult` carrying a `RESULT_FOR_PROTEIN` edge must be `not_applied`. The message
  names the result, the state it carried and the grain, and cites ADR-0038 D7.
- Grain is visible in every change-set (I20), so this is a write-time check and belongs here.
- **It must not need kind.** Kind is not visible at write time — producers stage the `Contrast` as
  a bare referent — which is exactly why D7 puts the kind-dependent refusal at the producer, built
  in prompt 30 as `site_change_set`'s `condition` check. Do not duplicate that here.

### 2.2 `ONTOLOGY.md` — I4 widened, and the table's home

- I4 is at **l.916** at this commit (ADR-0038 l.457 cites it as l.903, which was true when the
  record was written; the file has grown since). It currently reads *"Every `DifferentialResult` **on a site**…"*. Widen it to every
  grain, add D7's protein-grain `not_applied` rule, and give the label table its home in §8 beside
  I4.
- The table is as ADR-0038 l.426–432 prints it: five rows, three state columns, refusals named.
- Version 1.47 → **1.48**; last reviewed to the build date.
- **Nothing else in `ONTOLOGY.md` moves.** No DDL, no §3, no identity.

### 2.3 `bzk/query/graph.py` — kind, and the label

- Derive kind by calling `invariants.contrast_kind`, never by re-implementing D2's table. Read
  from the graph what that call needs: the result's `Contrast`, that contrast's
  `CONTRAST_IN_EXPERIMENT` anchor's `modality`, and the arms' `Sample` nodes through
  `NUMERATOR_SAMPLE` / `DENOMINATOR_SAMPLE` (built in prompt 29).
- Map (grain, kind, `protein_adjusted`) to the label, **no fallback**. A triple with no cell
  raises, naming the triple.
- Grain comes from the result's `RESULT_FOR_SITE` / `RESULT_FOR_PROTEIN` edge, as `_check_I4` reads
  it.
- **Select every property by name.** No `properties(…)`, no `RETURN *` (§0.6).

### 2.4 `bzk/query/graph.py` and `bzk/ui/app.py` — the untested-row display

- For each contrast an external `Analysis` carries, derive the `ProteinObservation`s with no
  `DifferentialResult` in that contrast for that analysis, and compare the count against
  `rows_untested_json`'s entry for that contrast id.
- **Equal:** those observations display *not tested by the source analysis*.
- **Unequal:** a mismatch error naming both numbers, **never the label**.
- `rows_untested_json` is NULL on a `processing` or `curation` analysis. Decide what the view does
  then and say why — an internal run has no source analysis whose placeholders it must recognise.
- The UI prints the label where it prints `protein_adjusted` today (`app.py` l.240).

### 2.5 `tests/` — the mirror guard and the refusals

- **Guard the label table against `ONTOLOGY.md` §8**, parsed from the document, as the other
  mirrors are.
- Mutation evidence for: the protein-grain clause; the no-fallback refusal; the mismatch error;
  and the mirror guard.
- **Bytecode disabled from the start. `python -I` does not disable it** — it implies `-E`, which
  ignores `PYTHONDONTWRITEBYTECODE` (handoff 10-08 §5). Use the environment variable with a plain
  interpreter.

---

## 3. Pre-registration — this container

**Not rehearsed.** Every figure is read from the record or the code.

**D1 — the protein-grain clause refuses nothing that exists.** ADR-0038 M10: every committed
`applied`/`native` fixture result is site grain. The suite must stay green on the unmutated tree
with the clause in place, and **M10 is the reason**, not luck. State the fixture results you
checked.

**D2 — every triple a result can occupy has a label.** Enumerate the (grain, kind, state) triples
reachable from the committed fixtures and the real graph's shape, and show each maps. The
unreachable ones raise.

**D3 — the no-fallback refusal fires.** A constructed result in a refused cell — a site-grain
result in an IP kind, say — raises, naming the triple.

**D4 — the mismatch error fires.** A constructed `Analysis` whose `rows_untested_json` disagrees
with the derived count shows the error and not the label.

**D5 — `tables_created` stays 60 and no id moves.** This prompt adds no DDL column and no node.

**D6 — `tests/fixtures/` is unchanged**, unless a refusal needs a new fixture; if one does, name
it and say which refusal.

**The checks:**

| Check (target) | Before (container) | After, predicted |
|---|---|---|
| `uv run pytest` (full) | 963 passed, 14 skipped | all pass; state the counts |
| `uv run pytest tests/test_schema.py` | 20 passed | state the number, and whether the mirror guard landed there or in its own module |
| `uv run mypy bzk tests` | Success, 117 files | Success; state the count and whether a new module moved it |
| `uv run ruff check bzk tests` / `ruff format --check bzk tests` | clean / 117 | clean; state the count |

**If any prediction fails, stop and report. Do not adjust code, fixtures or pins to match.**

---

## 4. Commit and report

**One commit**, fast-forwarded onto `main`, single subject line in the series' form, naming: D7's
display half and D6-revised (c)'s built; `_check_I4` refusing a protein-grain result that is not
`not_applied`; the label table homed in `ONTOLOGY.md` §8 and mirrored under guard; kind derived by
`contrast_kind` and never re-implemented; the untested display checking a derived count against
`rows_untested_json`; ONTOLOGY v1.47 → v1.48; 0 ids move.

**Files expected:** `ONTOLOGY.md`, `bzk/ontology/invariants.py`, `bzk/query/graph.py`,
`bzk/ui/app.py`, `tests/`. Any other file needs a reason in the report.

**Report:** the commit hash; §0's answers; D1–D6 as measured; §3's table with "After" measured;
every new refusal's message on the unmutated tree; the mutation evidence; the full `ONTOLOGY.md`
diff; `git diff --stat`; the four-point close. **State whether ADR-0038 is now fully built**, and
if anything of it is not, name it.

Then stop.

---

## 5. For bzk's Mac — a read-only query, no write

- **All 1,362 `DifferentialResult`s map to *stoichiometry-uncorrected*** — site grain,
  `condition` kind, `not_applied`.
- **The untested display is container-only.** No Perseus result is in the graph and none can be
  until PXD055843 unblocks on the PI and I15, so the Mac cannot exercise it. Say so rather than
  reporting it as passing.
- `git status --short` shows only the deferred prompt 22.
- Nothing is written, so no Step A snapshot is needed. (If a later prompt wants a graph-level id
  sweep, `rebuild` drops the stores first, so Step A must run **before** the pull — handoff 10-09
  §4.3.)

---

## Out of scope, and carried

Each of these is machine-checkable and open; none is this prompt's.

- **The one-composition-site rule is enforced by nothing** (`maxquant_sites.py`). `_site` broke it
  unnoticed until prompt 30.
- **`site_change_set` does not check that its `arms` belong to its `contrast`.**
- **A blank or non-numeric statistics cell raises a bare `ValueError`** naming neither row nor
  column (`perseus.py`).
- **`bzk/sources/pxd055843_perseus.py`'s module docstring** does not say untested rows mint no
  result. Stale since `4724046`.
- **ADR-0032 (Proposed) should take D6-revised (c) into its review** (ADR-0038 l.399). Still not
  done.
- **I22 holds only while the loader is the only `Contrast` minter**; nothing guards that.
- `_literal_reads`' blindness to `json.loads(...)["contrast"]`; the protein-groups binding (M8);
  `write_cells` over-reporting; the drift checker; the stale tautology floor; F-d; F-b
  generalised; R6's prefix-only check; a D2/D3 invariant-level check; a background-enrichment
  concordance basis value.
- **Eighteen `claude/*` branches on the remote.** A sweep, not a build item.
