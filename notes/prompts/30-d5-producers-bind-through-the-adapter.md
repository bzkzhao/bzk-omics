# Prompt 30 — Build ADR-0038 D5 and D7's producer refusal: a producer reads only columns its arms bind

**Repository:** `main` at the commit adding this prompt.

**Precondition — the Mac graph must be current, and this is a build-time check, not a Mac one.**
Prompt 29's cold rebuild (its §5) had not run when this prompt was written: the Mac graph was last
built at `190e696`, and `ce9e83e` changed the loader and added two rel tables. **§5's differential
run here is meaningless against a store built before `ce9e83e`** — it would compare figures from a
graph whose `Contrast` carries no arm edges. The container work (§0–§4) does not depend on it and
may proceed either way. Before §5 runs, confirm prompt 29's rebuild landed and its figures held
(58 → 60 tables; replay 18/52, 18/52, 16/38, 23/63; edge statements 31,379). If it has not, do
§0–§4, report, and leave §5 for bzk.

**The rebuild's figures, in full** — prompt 29 §5 pre-registered seven lines, and §5 below rests on
three of them that a count-only check would not catch:
- all **16 labels 0 gone / 0 new**;
- 58 → **60** tables;
- replay 18/40, 18/40, 16/38, 23/57 → **18/52, 18/52, 16/38, 23/63**;
- edge statements 31,349 → **31,379**;
- node statements 32,793, observations 4,195 / 4,768, 48 refusals and `INCOMPLETE` **unchanged**;
- **30 arm edges** in the graph;
- **M1 `[4b]` unchanged**.

§5's own predictions — `DifferentialResult` ids 0 moved, 1,362 results, `[4b]` unchanged — are
only meaningful if the last three held. Confirm all seven, not the counts alone.

**Governing:**
- `decisions/0038-contrast-arms-are-declared-and-bound-at-the-loader.md`:
  - D5 (l.216–258), including R1's refuted first ground and the deferred retained-matrix route;
  - D7 (l.421–458), and its *Where each refusal sits* list (l.444–457), for the producer half
    only;
  - M7 (the binding on PXD018299's real header) and M8 (the unreachable family).
- `notes/REVIEWER-HANDOFF-2026-10-08.md` §6, and 2026-10-07 §6.4 for the scope this inherits.
- `CLAUDE.md` l.95–99, the four-point close.

**Settled ground.** ADR-0038 and ADR-0039 accepted; D1, D2, D4 and D8 built at `ce9e83e`;
`ONTOLOGY.md` v1.46. This prompt builds **D5** and **D7's producer refusal only**. It does not
build:
- D6-revised (the Perseus proof, the untested count) — prompt 31;
- D7's `_check_I4` widening, the query layer or the display — prompt 32;
- the protein-grain IP writer or the protein-groups binding — order item 3.

**This is not an identity change.** No `Sample`, `Contrast`, `SiteObservation` or
`DifferentialResult` id moves. **One property changes on one existing node**: the `Analysis`'s
`label` (§2.3). Both are pre-registered in §3.

**Edits are limited to** `bzk/adapters/maxquant_sites.py`, `bzk/analysis/differential.py`,
`bzk/sources/pxd018299_differential.py`, `bzk/sources/pxd055843_perseus.py` (one sentence, §2.5)
and `tests/`. No `ONTOLOGY.md`, no ADR, no curation record, no `HANDOFF.md`, and nothing under
`notes/` other than this prompt.

The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **Repository state.**
   - `git log --oneline -3`, `git status --short`. HEAD is this prompt's commit, tree clean.
   - Open-of-turn checks: `uv run pytest`, `uv run pytest tests/test_schema.py`,
     `uv run mypy bzk tests`.
   - Expected **in a container**: `937 passed, 14 skipped`; 20 passed; `Success` over 117 files.
     The skip count is environment-dependent (handoff 10-08 §4.4) — report what you see.
   - Say whether prompt 29's Mac rebuild has landed, and from what you are reading that.
2. **What D5 forbids, quoted.**
   - Quote ADR-0038 l.218–222 (*The rule*, the five lines from "**The rule.**") verbatim.
   - State in one sentence what "a producer never names a column" forbids, and name every place in
     `bzk/sources/pxd018299_differential.py` that breaks it today.
   - Expected: `_intensity_columns` composes `f"Intensity {arm}_{i}"` itself; `CONTRAST` supplies
     the arm strings.
3. **The binding that exists, and what the new one must do differently.**
   - Quote `bzk/adapters/maxquant_sites.py` l.128–152 and l.122–126.
   - State what `_sample_columns` returns, and what it checks at l.147.
   - Expected: it returns `(Sample.id, run label)` per mapped sample, and at l.147 it accepts a
     sample if **any** family's composed header is in the file. The new function is asked for one
     quantity and must check **that family only**; a sample bound for `ratio_mod_base` whose
     `Intensity` column is missing must refuse rather than pass on the other family's presence.
4. **Every mention of `CONTRAST`, not only its uses.**
   - Run `grep -n CONTRAST bzk/sources/pxd018299_differential.py` and list every line, with a
     count.
   - Expected **six lines**: l.111 the definition; l.319 and l.320 the column pick; l.382 the
     `[4b]` header; l.510 the `DeclaredRun(label=…)`; and **l.89, a comment that cites `CONTRAST`
     by name** inside the explanation of why `ANALYSIS_RECORD` is read. That comment dangles once
     the constant is gone and must be rewritten, not deleted — the reasoning it carries outlives
     the constant.
   - Say which mention changes a **stored value** rather than a printed one.
   - Expected: l.510 only — it becomes `Analysis.label`.
5. **Why `label` moves but no id does.**
   - Name the identifying fields of `Analysis` from `bzk/ontology/schema.py`, and say whether
     `label` is among them.
   - Quote the write statement in `bzk/ontology/store.py` that makes an existing node's property
     change on replay.
   - Expected: `label` is not in `IDENTITY["Analysis"].fields`; `store.py` writes
     `MERGE (n:{label} {{{primary_key}: $pk}})` followed by `SET`, so the Mac replay overwrites
     `label` in place on the same id.
6. **Where the arms come from now.**
   - Name the field on `LoadedCuration` that carries the resolved arms, and what each entry holds.
   - Expected: `contrast_arms`, a `dict` of record contrast id → `ContrastArms`, carrying the
     numerator and denominator `Sample` ids **in declaration order** and the derived `kind` from
     `invariants.contrast_kind`. The producer takes them from there and derives nothing.

**Do not start §1 until bzk replies.**

---

## 1. What this prompt builds, and the readings it adds

- **D5** — one binding per file format is the only route from a `Sample` to a column. The producer
  asks for (`Sample` id, quantity) and receives an exact header or a refusal.
- **D7's producer half** — `site_change_set` refuses arms whose derived kind is not `condition`.
  Kind is not visible at write time, because producers stage the `Contrast` as a bare referent, so
  this refusal cannot live in an invariant.

**Three readings this prompt adds, none in the record:**

- **Arm order is part of the binding's contract.** `contrast_arms` carries sample ids in
  declaration order, which is replicate order. The columns the producer reads must come back in
  that order, because the matrix's columns are the arm's replicates and a reordering would change
  every per-row statistic silently. Pre-registered in §3 as an ordered list, not a set.
- **The refusal is per family, and that is the whole change.** `_sample_columns` l.147 accepts on
  *any* family. A producer asking for `intensity_multiplicity_summed` must be refused when only
  the `ratio_mod_base` column exists, even though the sample is bindable. §2.1's test covers it.
- **Raw columns only (R1).** The retained-matrix route is deferred by ADR-0038 D5 until a build
  pre-registers that it reads the same values cell for cell. This prompt does not open it, and a
  build that reads `quant_store` instead of the file has gone outside the record.

---

## 2. The build

### 2.1 `bzk/adapters/maxquant_sites.py` — the binding

- A new public function taking the sample mapping, a `Sample` id, a quantity from
  `QUANTITY_COLUMNS`' keys, and the file's header; returning the **exact composed header** or
  raising `MaxQuantSiteError`.
- Built on `QUANTITY_COLUMNS` (l.122). It recovers the run label from the mapping key exactly as
  `_sample_columns` does — one rule for stripping the prefix, not two.
- It refuses, each with its own message and its own test:
  - a `Sample` id the mapping does not carry;
  - a quantity outside `QUANTITY_COLUMNS`;
  - a mapping key carrying no recognised prefix (as l.141–145 refuses today);
  - **the asked-for family's header absent from the file**, even where another family's is
    present. This is the l.147 difference and the reason the function exists.
- **One composition site per format, which is what D5 l.218–219 requires.** The record names
  `_sample_columns` as the single place a column is bound. Adding a second function that composes
  `f"{prefix}{label}"` and tests membership would make two, so the composition-and-membership step
  moves into one private routine and **both** `_sample_columns` and the new function call it,
  differing only in which families they will accept — any, versus the one asked for.
- `_sample_columns`' observable behaviour at ingestion does not change, and its tests must pass
  untouched. Report the shared routine's name and both call sites.

### 2.2 `bzk/sources/pxd018299_differential.py` — the producer

- **Delete `CONTRAST` (l.111) and `_intensity_columns` (l.258).**
- **The record contrast id is read from its home, and gains no second one.** The module already
  reads it at l.516 — `json.loads(ANALYSIS_RECORD.read_text())["contrast"]` — and l.86–88 says why
  that read is legitimate where transcribing the run's parameters would not be. Read it **once**,
  early in `main()`, bind it to a local, and use that local for the arms lookup, the `[4b]` header
  and the `Analysis.label`. **Do not introduce a module constant holding `"KO_IFN_vs_WT_IFN"`**:
  that is a second home for a fact whose home is the analysis record, against `CLAUDE.md` l.40.
- Arms come from `curation.contrast_arms[<that local>]`.
- Each arm's columns come from §2.1's binding, one call per `Sample` id, **in arm order**, asking
  for the quantity the run declares.
- `[4b]`'s header (l.382) prints the contrast's **record id**.
- Raw columns only. The `0.0 → NaN` step and everything downstream of the matrix are untouched.

### 2.3 `Analysis.label` — the one stored value that changes

`DeclaredRun(label=…)` at l.510 is built from `CONTRAST`. It becomes the record contrast id.

- **Old:** `welch_t KO_IFN vs WT_IFN (BH)`
- **New:** `welch_t KO_IFN_vs_WT_IFN (BH)`

`label` is not in `IDENTITY["Analysis"].fields`, so **no id moves**; but `bzk/ontology/store.py`
writes `MERGE … SET`, so the Mac replay **overwrites `label` on the existing `Analysis` node**.
That is the only property that changes, on the only node that changes, and §3 pre-registers it.

*If a build prefers the `Contrast` node's `label` property (`'USP18-/- + IFN vs WT + IFN'`) over
the record id, that is a defensible choice — but it is a different pre-registration. Take the
record id, as above, so the string the `[4b]` header prints and the string stored on the
`Analysis` are the same one.*

### 2.4 `bzk/analysis/differential.py` — D7's producer refusal

- `site_change_set` takes the arms and the derived kind, and **refuses any kind but `condition`**,
  naming the kind it got.
- The refusal's message says why it sits here and not in an invariant: kind is not visible at
  write time, because producers stage the `Contrast` as a bare referent (ADR-0038 D7).
- No other signature change. `dataset`, `attached_nodes` and `attached_edges` still arrive whole,
  as the adapter minted them (l.80–87).

### 2.5 One stale sentence, in scope because this prompt is the producer prompt

`bzk/sources/pxd055843_perseus.py` l.109 says *"The arms are identifying on `Contrast`
(ONTOLOGY.md §3)"*. False since ADR-0038 D4: the arms are **non-identifying edges**. Correct the
sentence; change no behaviour in that file. (Handoff 10-08 §6 routes this here.)

### 2.6 `tests/test_analysis_record.py` — two reason strings this prompt falsifies

Deleting `CONTRAST` makes two recorded reasons false. The guard checks **keys, not reasons**, so
the suite stays green either way; that is why they are named here rather than left to be caught.

- `UNREAD["contrast"]` (l.115): *"read off the other record only; transcribed as CONTRAST in
  pxd018299_differential"*. After §2.2 there is no transcription.
- `MENTIONS` (l.90): *"transcribes, and says why"* for `pxd018299_differential.py`.

Reword both to what is then true. **Do not widen the fix beyond these two strings**, and in
particular do not change `_literal_reads` — see the next paragraph.

**A pre-existing defect this surfaces, which this prompt does not fix.** The comment at l.112–114
says *"Nothing that opens this one looks at them"*, and `"contrast"` sits in `UNREAD`. Both are
already false: l.516 reads `"contrast"` off this very record. `_literal_reads` does not see it
because the receiver is `json.loads(...)`, a call, not a name in `receivers` (l.150–160). Record
this in point 3 of the close as an open item for its own prompt; changing the AST walk is a change
to the guard's reach and belongs nowhere near this build.

---

## 3. Pre-registration — this container

**Not rehearsed.** Unlike prompt 29, no part of this was built in a scratch clone first. Every
figure below is read from the record or from the code as it stands, and §3's job is to be
falsifiable, not to be confirmed.

**B1 — the binding on PXD018299's real header.** For the six arm samples of
`KO_IFN_vs_WT_IFN`, asking for `intensity_multiplicity_summed` against `ROADMAP.md`'s 159-column
line returns exactly ADR-0038 M7's six headers, **in this order**:

```
numerator   ['Intensity KO_IFN_1', 'Intensity KO_IFN_2', 'Intensity KO_IFN_3']
denominator ['Intensity WT_IFN_1', 'Intensity WT_IFN_2', 'Intensity WT_IFN_3']
```

These are the same columns `_intensity_columns` picks today (M7: *"equals the token's pick
True"*), which is why §5's figures must not move.

**B2 — the per-family refusal fires.** A constructed header carrying `Ratio mod/base WT_1` but not
`Intensity WT_1` binds for `ratio_mod_base` and **refuses** for
`intensity_multiplicity_summed`. Today's `_sample_columns` accepts that sample; the new function
must not.

**B3 — D7's refusal fires.** `site_change_set` given a kind other than `condition` refuses. Build
the case from a constructed `ip_ms` curation, as prompt 29's loader tests do; no such record
exists on disk.

**B4 — no fixture moves.** `git diff -- tests/fixtures/` is empty. *(Stated narrowly this time:
the claim is about `tests/fixtures/`, and it is made because this prompt edits no record and no
fixture. If it turns out false, that is a finding — stop and report, as prompt 29 correctly did.)*

**The checks:**

| Check (target) | Before | After, predicted |
|---|---|---|
| `uv run pytest` (full) | 937 passed, 14 skipped | all pass; state the counts |
| `uv run pytest tests/test_schema.py` | 20 passed | 20 passed, file unedited |
| `uv run mypy bzk tests` | Success, 117 files | Success, 117 files |
| `uv run ruff check bzk tests` / `ruff format --check bzk tests` | clean / 117 | clean / 117 |

**Mutation evidence is required** for every new refusal in §2.1 and for §2.4's kind refusal:
each made to fail, the mutation read back, each reverted, bytecode disabled from the start.
**`python -I` does not disable bytecode** — it implies `-E`, which ignores
`PYTHONDONTWRITEBYTECODE` (handoff 10-08 §5). Use the environment variable with a plain
interpreter.

**If any prediction fails, stop and report. Do not adjust code, fixtures or pins to match.**

---

## 4. Commit and report

**One commit**, fast-forwarded onto `main`, single subject line in the series' form, naming: D5
built; the producer reads columns only through the adapter's binding, per family; `CONTRAST` and
`_intensity_columns` deleted; D7's producer refusal in `site_change_set`; `Analysis.label` changes
on replay and no id moves.

**Files expected:** `bzk/adapters/maxquant_sites.py`, `bzk/analysis/differential.py`,
`bzk/sources/pxd018299_differential.py`, `bzk/sources/pxd055843_perseus.py`, and `tests/`
(including `tests/test_analysis_record.py` for §2.6's two strings). Any
other file needs a reason in the report.

**Report:** the commit hash; §0's answers; B1–B4 as measured; §3's table with "After" measured;
every new refusal's message on the unmutated tree; the mutation evidence; `git diff --stat`; and
the four-point close. State explicitly whether §5 ran or was left for bzk.

Then stop.

---

## 5. For bzk's Mac — only after prompt 29's rebuild has landed

Pull, run the differential, `git status`. Pre-registered:

- `tests/fixtures/` byte-identical — the targets fixture carries no contrast string.
- `[4b]`'s figures as handoff 10-05 §3.3 M1, unchanged. The binding returns the same columns the
  token picked (B1), so every downstream number is the same.
- `DifferentialResult` ids **0 moved**; **1,362** in `KO_IFN_vs_WT_IFN`.
- The `Analysis` node: `label` changes from `welch_t KO_IFN vs WT_IFN (BH)` to
  `welch_t KO_IFN_vs_WT_IFN (BH)`, **and nothing else on it changes**. Report the node's
  properties before and after, not just the label.

---

## Out of scope

- D6-revised and the untested count (prompt 31); D7's `_check_I4`, query layer and display
  (prompt 32).
- The protein-groups binding function and its silently dropped unreachable family (ADR-0038 M8) —
  order item 3.
- The retained-matrix route, deferred by D5 until a build pre-registers it cell for cell.
- `curation_PXD055843.json`'s stale `rationale` sentence — prompt 31, which already edits that
  record for P2.
- **`_literal_reads`' blindness to a key read off `json.loads(...)`** (§2.6). Its own prompt.
- F-d; `write_cells` over-reporting; the drift checker; the stale tautology floor; a D2/D3
  invariant-level check.
