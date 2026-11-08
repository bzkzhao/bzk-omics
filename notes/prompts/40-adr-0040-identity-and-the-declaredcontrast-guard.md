# Prompt 40 — ADR-0040: arms belong to a contrast by identity, and `DeclaredContrast` enforces it (revision 4)

**Repository:** `main` at the commit adding this prompt. Every line reference below was measured at
`c57aeb9` and is wrong by however far later commits moved the file; §0 re-measures them.

**Why.** `DeclaredContrast` (`bzk/adapters/perseus.py` l.310–312) takes a `Contrast` node and a
`ContrastArms` as independently chosen arguments. l.643 anchors every result on
`str(declared.contrast["id"])` while `_prove` binds and recomputes over `declared.arms` (l.979), so
a mismatched pair attributes results to contrast A while proving the binding over B's arms. This is
the shape `site_change_set` had before `f61f6fd`, which closed it there (`bzk/analysis/differential.py`
l.164) using the `contrast_id` the loader fills. **The same question was never asked for this second
producer**, and `f61f6fd` answered it one way for one producer without an ADR. Decision recorded
2026-11-08: **identity**, in a new ADR, with the guard landing alongside it.

**Why revision 4.** A third independent audit found **no blocker** and three smaller defects, all in
text revision 3 added — including the *supporting* clause of revision 3's corrected justification,
which was itself false. That is the third consecutive revision in which a fix carried its own
defect, and the second in which a correction of a reason was wrong rather than merely incomplete.
All three are fixed below. That audit built the whole thing on a scratch copy, reproduced every row
of the measured table, both branches of the sixth-file conditional, the six-raw-store-gated-skip
enumeration and all three mutation outcomes.

**Why revision 3.** A second independent audit found **no blocker** and five smaller defects, two of
them inside sentences revision 2 had rewritten — including a repair instruction whose *action* was
right and whose stated *reason* was false. All five are fixed below. That audit built the whole thing
on a scratch copy and reproduced every row of the measured table, the six-file list, the pin set and
all three mutation outcomes.

**Why revision 2.** An independent checker found **one blocker** and nine smaller defects.
The blocker was mine and of a shape this project keeps recording: I measured the suite with the
guard and the two repairs, then registered that figure as the **post-build** expectation — forgetting
the test §1.6 itself orders the build to commit. A compliant agent would have had to report a
spurious off-by-one against a figure this prompt called measured, or delete the mandated test to
hit it. Re-measured below, with the guard's message conforming to §1.2.

**The hazard is not hypothetical here.** Two committed tests pair a contrast with arms minted for a
different one, and both pass today with nothing flagging them: `tests/test_perseus.py` l.1387 inside
`test_the_count_is_per_contrast` (l.1383), and l.472 inside
`test_refuses_when_a_declared_contrast_has_no_columns` (l.466).

**Measured in the reviewer's clone at `c57aeb9`**, on a container with no raw store, in two stages
because they answer different questions:

| state | suite |
|---|---|
| baseline, untouched | 1230 passed, 14 skipped |
| **+ guard + both repairs, nothing else** | **1230 passed, 14 skipped** — so the repair scope is exactly two tests, not an estimate |
| **+ §1.6.1's mandated test** | **1231 passed, 14 skipped** — the post-build figure §1.5 registers |

The second row is what proves no third test needed touching. The third is what the build must
reproduce.

**What this builds.** One decision record, one `__post_init__` check, two test repairs, one new
test, and the pins that move. **Six files:**
`decisions/0040-arms-belong-to-a-contrast-by-identity.md` (new), `decisions/README.md`,
`tests/test_decision_index.py`, `bzk/adapters/perseus.py`, `tests/test_perseus.py`, and
`tests/test_tautology_sweep.py` — **conditionally**: its floor (l.2329, holding `60` and `2639`)
moves only if §1.6.1's test carries `assert` statements, and `PINNED` (342 entries) moves only if one
of them is a matching equality. A test written as `pytest.raises(..., match=...)` with no `assert`
moves neither, and then this sixth file drops out of the diff. Read both off `sweep()` — §1.6 says
predict neither, and that applies to this sentence too.

**Do not size the check from a line count.** `pyproject.toml` sets `line-length = 100`, and a
message naming both ids as §1.2 requires does not fit in three lines.

**A new ADR is a critical node** (`CLAUDE.md` l.95), so the four-point close applies to this turn.

---

## 0. Receipt check — answer, then stop and wait

Execute these against the repository. Do not answer from this prompt.

1. **Line references.** Report the line of each, as measured now: `class DeclaredContrast`; its three
   fields; **both** lines that read `declared.contrast["id"]` — l.643, the result anchor every row is
   attributed through, and l.588, which keys the proof dict; the `_prove` line that binds
   `declared.arms`; `site_change_set`'s `contrast_id` check; `ContrastArms`' `contrast_id` field in
   the loader; and in `tests/test_perseus.py`, `ARMS`, `CONTRAST`, `_anchored_contrast`, and both
   tests with their mismatched construction sites. This prompt says `perseus.py` 294, 310–312, 643,
   979; `differential.py` 164; and `test_perseus.py` 58, 80, 86, 466, 472, 1383, 1387. Report any
   difference with its size. A grep for that expression returns two hits, and both are expected.
2. **The construction sites, counted.** List every `DeclaredContrast(` call site under `bzk/` and
   `tests/`, and for each say whether its `arms` were minted for the `contrast` it is paired with.
   This prompt says **eight** sites and **two** mismatched. Report any third mismatch, and whether
   the production site (`bzk/sources/pxd055843_perseus.py` l.129) takes both from one loader object.
   A ninth site exists under `notes/scripts/`, which §2 puts out of scope; report it if you find it
   rather than treating it as a discrepancy.
3. **`__post_init__` and the index pins.** Confirm `bzk/adapters/perseus.py` contains no
   `__post_init__` today, and report the current values of `EXPECTED_FILES`,
   `EXPECTED_WRITTEN_ROWS`, `EXPECTED_QUEUED_ROWS`, `EXPECTED_SEED_LINES`, `EXPECTED_SEED_STRUCK`
   and `EXPECTED_STATUSES` in `tests/test_decision_index.py`, beside the values the directory
   actually yields. This prompt says 38, 38, 1, 18, 17 and
   `{"Accepted": 26, "Proposed": 9, "Superseded": 3}`, all currently true of the directory.
4. **The real records agree already.** For every `data/curation/curation_*.json`, report each
   contrast's `contrast_arms[...].contrast_id` beside `str(contrast(...)["id"])` and whether they
   match. This prompt says **five pairs, zero mismatches**. **If any real record mismatches, stop:**
   the guard would refuse committed data and this prompt's premise is wrong.
5. **Extension's cost, established not assumed.** `ADR-0038` D4 puts arm membership in
   `NUMERATOR_SAMPLE` and `DENOMINATOR_SAMPLE` edges. Report whether anything reachable from
   `DeclaredContrast` carries those edges or the `Sample` ids needed to check extension at the
   adapter, and what a producer would have to be given to check it. Report; this prompt does not
   ask you to build extension.

Then stop and wait.

## 1. Build

### 1.1 The ADR

`decisions/0040-arms-belong-to-a-contrast-by-identity.md`, following the template in
`decisions/README.md`'s template (l.112–126), which is the four-row shape this record needs:
`Status`, `Date`, `Supersedes`, `Superseded by`. ADR-0038 carries a `Reviewed` row as its **third**
of five; a record landing unreviewed has none — **though `Proposed` does not forbid one**: ADR-0030
is `Proposed` and acquired a `Reviewed` row when it was reviewed and held.
**Status `Proposed`** — it becomes `Accepted` only after the review round trip
(`decisions/README.md` l.5). **It supersedes nothing**, and says so: it decides a question
`f61f6fd` answered for one producer without asking, and extends that answer to the second. Keep it
short, as the README asks: context, decision, consequences, alternatives rejected.

What it must record, each from §0's measurements rather than from this prompt:

- **The decision.** *Belong* means the arms object was minted for this contrast, compared by the
  minted node's id. Not *these samples are this contrast's arms*.
- **Why identity and not extension.** Identity is checkable at the adapter boundary today, because
  `ContrastArms.contrast_id` already exists for exactly this purpose and `site_change_set` already
  enforces it. Extension needs ADR-0038 D4's edges plumbed to the producer (§0.5), and no test or
  production site asks for it.
- **What identity does not give up.** Two contrasts may still share arm *samples*; each simply
  carries arms minted for it. The two readings diverge only where arms minted for A are handed to B
  with identical samples.
- **The limit, stated so a pass is not misread.** `contrast_id` is a claim, not a proof: a
  hand-built `ContrastArms` can state any id, and the loader is the only production site that fills
  it. So the check catches accidents, not intent.
- **The `dataset` gap, unchanged.** Neither this check nor `site_change_set`'s relates `arms` or
  `contrast` to `dataset`, so a `dataset` from another record stays representable. By design, and
  recorded as such.
- **The cost, measured.** Two committed tests pair mismatched arms, and no third did; repairing
  them leaves the suite at 1230 / 14, unchanged from baseline, with the mandated guard test taking
  it to 1231 / 14. Put a figure in the ADR only if you re-measure it in this turn; otherwise cite
  §0 and this prompt's table as the reviewer's measurement.

### 1.2 The guard

A `__post_init__` on `DeclaredContrast` refusing a pair whose `arms.contrast_id` differs from
`str(self.contrast["id"])`, raising `PerseusError` and naming both ids. `DeclaredContrast` is a
frozen dataclass with no `__post_init__` today (§0.3), so this is a new method, not a changed line.
The message says what is wrong and which record to look at; follow `site_change_set`'s refusal
(`bzk/analysis/differential.py` **l.164–170**) in wording and in what it names. The half that
satisfies *"which record to look at"* is **l.169**, which names
`LoadedCuration.contrast_arms` under the same handle as `LoadedCuration.contrast`; a message built
from l.164–168 alone stops mid-sentence and omits exactly that.

Nothing else about `DeclaredContrast` changes: no field, no default, no frozen-ness.

### 1.3 The two repairs

Each contrast gets arms minted for it, keeping the same samples, so each test's subject is untouched:

- `test_perseus.py` l.1387: `other` takes `replace(ARMS, contrast_id=str(other_node["id"]))`.
- `test_perseus.py` l.472: the same intent, but **not the same edit**. That node is minted inline as
  an argument, so there is no name to read `["id"]` from: give it one first — a local or a walrus —
  rather than calling `_anchored_contrast` twice. **Not because a second call would mint a different
  node:** it is deterministic — `evidence_id` over the same props and anchor — so two calls return
  the same id and the comparison would in fact be against the right one. The reason is that a second
  call **restates the mint instead of reading the node that was passed**, so the test stops showing
  where the id came from. **The fragility is on the other side, not in the helper:** the
  `Experiment` anchor is a literal inside `_anchored_contrast` (l.63, and the only occurrence in the
  file), so changing it moves both calls identically and nothing diverges. What a restated mint is
  fragile under is an edit to **l.473** — change that contrast's arguments or its helper and the
  duplicated call keeps comparing against the old one, silently. Expect a few lines here, not one.

`replace` is **already imported** at `tests/test_perseus.py` l.33 and used at l.945; nothing to add.
**Neither test's subject is the pairing** — l.1383's is a count
per contrast, l.466's is a contrast with no columns — so neither docstring needs changing. If either
does need changing to stay true, report it rather than rewriting the test's purpose.

### 1.4 The index pins

A new ADR moves them, as ADR-0038's own V8 row records for its landing. Read each off the
directory; do not predict it:

- `EXPECTED_FILES` and `EXPECTED_WRITTEN_ROWS`: 38 → 39.
- `EXPECTED_STATUSES["Proposed"]`: 9 → 10, since 0040 lands `Proposed`.
- `EXPECTED_QUEUED_ROWS`, `EXPECTED_SEED_LINES`, `EXPECTED_SEED_STRUCK`: unchanged — 0040 is not in
  `ARCHITECTURE.md` §5's seed list, which holds 0001–0018 only.
- `decisions/README.md`'s **Written** table gains a row after 0039 (l.92).

`tests/test_decision_index.py` asserts every pinned count before comparing any set (its module
docstring says why), so a wrong pin fails there rather than binding nothing.

### 1.5 Expected outcome — registered before the run

| check | expected |
|---|---|
| `pytest`, after the build | **1231 passed, 14 skipped**, no raw store — baseline plus §1.6.1's test |
| the same with **the PXD018299 deposit** present | 1234 / 11, on this prompt's arithmetic — the three skips that flip are `tests/test_pxd018299_baseline.py` l.275 and l.290 and `tests/test_pxd018299_refusals.py` l.230, all gated on `sha256:a4a503e3…` |
| `tests/test_perseus.py` alone | **64 → 65** |
| the guard, made to fail | a `PerseusError` naming both ids |
| `data/curation` loads | unchanged; all five pairs still match |

**"The store present" means that one deposit, not a full store.** Six of the 14 skips are
raw-store-gated, not three: those three, plus `tests/test_protein_groups.py` l.130 (`SUPP_DATA_2`,
`SUPP_DATA_3`, `PXD018299_PROTEIN_GROUPS`, fetchable by a documented command) and
`tests/test_pxd055843_depletion_ranking.py` l.365 and l.380 (`Supplementary_Data_S1_TP.xlsx`,
hand-stored). The other eight want `~/.bzk-omics/graph.kuzu`. A fully stocked store would give
1237 / 8. Report what your machine actually holds rather than mapping onto either figure.

**A difference is reported at its size and not adjusted.** Do not edit the expected column.

### 1.6 Mutation proof

Per `CLAUDE.md` l.97 including its cache rule — delete every `__pycache__`, then run with
`PYTHONDONTWRITEBYTECODE=1`, in that order — mutate by content, confirm each applied by reading the
file back, revert each, and confirm green. Each list is a floor: report what actually failed.

1. **Remove the `__post_init__`.** A new test must fail: add one that builds a `DeclaredContrast`
   pairing `CONTRAST_NODE` with arms minted for another contrast and expects `PerseusError`. Without
   that test the guard is unverified, since the two repairs only prove it *can* be satisfied.
2. **Invert the comparison** (`==` for `!=`). `tests/test_perseus.py` builds `CONTRAST` at module
   level (l.86), so this **aborts collection of that module and interrupts the session** — plain
   `pytest` reports one collection error and runs nothing, so there is no swathe to name until you
   re-run with `--continue-on-collection-errors`. Report the collection error first, then the
   swathe under that flag.
3. **Compare the record handle instead of the minted id**, if the loader exposes one — or report
   that nothing on the node carries a handle to compare, which is what `ContrastArms`' docstring
   claims.

Then the sweep: `tests/test_tautology_sweep.py` pins every **matching** equality under `tests/` —
`PINNED` holds 342 against 2,639 asserts, so most equalities are not in it. Classify
whatever the new test adds, regenerate `PINNED` with the command in the comment at l.201–202 —
strip the `#: ` prefixes, the leading *"Regenerate with"* and its opening backtick, the closing
backtick, and the trailing *"**after** classifying whatever is"*, then rejoin — and report `PINNED`'s
size and the floor before and after. Read both off `sweep()`; predict neither.

## 2. Out of scope

- **FINDINGS §2 route 2 and stage 4's note: prompt 41**, renumbered from 40 by this prompt's
  landing. The disagreement `notes/prompts/38-...md` §2 records about route 2's producing script is
  unchanged and still unsettled.
- **FINDINGS §5 and §6** (stages 6 and 7). Their source attributions remain unverified, and after
  stage 3's note proved wrong and stage 4's is disputed, treat them as unmeasured rather than likely.
- **Extension.** Not built, not plumbed. §0.5 reports its cost; the ADR records why it was rejected.
- **The `dataset` gap** and **`contrast_id` as a claim rather than a proof.** Both are recorded in
  the ADR as standing limits, neither is closed here.
- **`site_change_set`'s own check.** Untouched; this prompt extends its rule to a second producer
  rather than changing it.
- **The eight unguarded source-readers** — functions that parse module source with no synthetic
  cases fed to them. Prompt 39 §2 defers them and cites its own §0.2; **neither section enumerates
  them**, and its §3 point 3 orders the list produced in that build's report rather than containing
  one. Still open, and still unlisted in the repository.
- Anything under `walk/` or `notes/`, and any fixture.

## 3. Report

Close with the four points of `CLAUDE.md` l.96–99 (l.95 is their parent bullet):

1. Each check by name at its actual result and target: `pytest` (full suite), `pytest
   tests/test_schema.py`, `ruff check bzk tests`, `ruff format --check bzk tests`, `mypy bzk tests`.
   A check not run is reported as not run. State which machine and whether the raw store held
   anything.
2. The §1.6 mutations, each with its confirmed application and what failed; and §1.5's table,
   expected beside observed.
3. What this did not cover, including at least: that `contrast_id` is a claim and the check catches
   accidents rather than intent; the `dataset` gap; that extension is unbuilt and its cost only
   reported; and that the ADR is `Proposed`, so the decision is not yet reviewed.
4. Any instruction from this prompt dropped or partly done.
