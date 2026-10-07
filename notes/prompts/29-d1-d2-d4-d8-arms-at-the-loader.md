# Prompt 29 — Build ADR-0038 D1, D2, D4 and D8: arms declared in curation, I22 at mint, `Contrast`–`Sample` edges, `isotype_control`

**Repository:** `main` at the commit adding this prompt.

**Precondition, check before anything else.** ADR-0039 must be `Accepted`. It decides the guard
amendment this prompt builds in §2.6, and an `Accepted` ADR is what §2.6 cites. At the time this
prompt was written ADR-0039 was `Proposed` at `e356356`. If it is still `Proposed`, **stop and say
so** — ADR-0038's own path was landed-`Proposed`, reviewed, accepted, then built, and this prompt
is the build half of that pattern for ADR-0039.

**Governing:**
- `decisions/0038-contrast-arms-are-declared-and-bound-at-the-loader.md`:
  - D1 (l.80–106), D2 (l.107–156), D4 (l.197–215), D8 (l.459–470);
  - *Implied changes* l.489–544, and its defect at l.504–505 (see ADR-0039);
  - *Measurements* M3 (l.595–596) and M4 (l.597–614).
- `decisions/0039-the-shape-guard-admits-pinned-exceptions.md`, in full.
- `notes/REVIEWER-HANDOFF-2026-10-07.md` §6.3 and its P1.
- `CLAUDE.md` l.95–99, the four-point close.

**Settled ground.** ADR-0038 as accepted, ADR-0039 as accepted, D2/D3 of ADR-0036 built at
`190e696`, and the h10 digest fix at `dfe6640`. This prompt builds D1, D2, D4 and D8. It does
**not** build:
- D5 (producers binding through the adapter) — prompt 30;
- D6-revised (the Perseus proof, the untested count on `Analysis`) — prompt 31;
- D7 (I4 labels, the untested-row display) — prompt 32;
- a D2/D3 invariant-level check (handoff 10-05 §7) — carried, see *Out of scope*.

**This is not an identity change. 0 ids move, in every record and every label.** That is
pre-registered in §3 and it is the claim most easily broken by accident — see §2.2's warning.

**Edits are limited to** `ONTOLOGY.md`, `bzk/`, `tests/` and the three curation records named in
§2.5. No ADR, no `ROADMAP.md`, no `HANDOFF.md`, and nothing under `notes/` other than this prompt.

The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **Repository state.**
   - Run `git log --oneline -3` and `git status --short`. HEAD must be this prompt's commit, the
     tree clean, and ADR-0039 present and `Accepted`.
   - Then the open-of-turn checks: `uv run pytest`, `uv run pytest tests/test_schema.py`,
     `uv run mypy bzk tests`.
   - Expected **in a container**: `908 passed, 14 skipped`; 20 passed; `Success` over 117 files.
   - **The skip count differs on bzk's Mac** — it reports `914 passed, 8 skipped` at `dfe6640`,
     because six tests that skip here run there on local state (the PXD055843 content store). Both
     total 922. Report the numbers you see; a 908/14 here and a 914/8 there are the same suite, and
     neither is a defect.
2. **D1's shape, quoted.**
   - Quote ADR-0038 l.82–83 and l.96–99 verbatim.
   - State the **exact** names of the two new contrast-entry fields, and the full recognised key
     set for a contrast entry.
   - Expected: `numerator_samples` and `denominator_samples`, lists of the record's own `mapping`
     keys verbatim; recognised set `id`, `numerator`, `denominator`, `numerator_samples`,
     `denominator_samples`, `note`.
3. **What a contrast entry's keys are checked against today.**
   - Quote `bzk/curation/loader.py` l.484–490.
   - Say what happens today to an unknown key inside a `contrasts_of_interest` entry, and name the
     measurement that established it.
   - Expected: nothing checks it; the key is dropped and the contrast nodes are identical to the
     unmodified record's (ADR-0038 M3, and V5 of its *Landing verification*).
4. **How a `Contrast` id is minted, and what must not change.**
   - Quote `loader.py` l.496–497.
   - State which record fields enter `props`, and therefore what would happen to all five
     `Contrast` ids if the arms were folded into `props`.
   - Expected: `props` is `{numerator, denominator}` only; adding arms to it re-mints every
     `Contrast`, which would also break `tests/fixtures/pxd018299_curation_ids.json`.
5. **The mirror that is currently unguarded.**
   - Quote `loader.py` l.309–312 and `ONTOLOGY.md` l.400–406.
   - Say what, if anything, checks that the two agree.
   - Expected: nothing does. This is handoff 10-05 §7's *unguarded mirror*, and §2.4 closes it.
6. **The shape guard and its exception.**
   - Quote `tests/test_schema.py` l.81–98, and `tests/test_decision_index.py` **l.75–84** —
     the reason at l.75–83 and the `ONE_SIDED_SUPERSESSION` pin itself at l.84.
   - **The range moved by one** when ADR-0039 was accepted: its acceptance commit added a
     line to the `EXPECTED_STATUSES` transition log above it. ADR-0039 l.96 still cites
     l.73–82 and is `Accepted`, so it is not edited; read it as l.75–84 and say so.
   - State what ADR-0039 decides the guard must now do, and what the pin keys on.
   - Expected: refuse a same-shape pair unless pinned with the record that decided the two names
     are distinct facts; the pin keys on the **pair, its endpoints and its multiplicity**, so a
     third `Contrast → Sample, MANY_MANY` edge still fails.

**Do not start §1 until bzk replies.**

---

## 1. What this prompt builds, and the readings it adds

- **D1** — every contrast declares its arms by mapping key; the loader resolves them and refuses
  as D1 lists, including an unknown contrast-entry key.
- **D2** — I22, the role-consistency table, enforced at contrast mint; `isotype_control` added to
  the `role` enum; R7 widened.
- **D4** — `NUMERATOR_SAMPLE` and `DENOMINATOR_SAMPLE`, both `Contrast → Sample, MANY_MANY`,
  **non-identifying**, written only by the loader.
- **D8** — every contrast, required; no optional form.

**Two readings this prompt adds, neither in the record:**

- **Kind is derived, never stored.** `LoadedCuration` carries the derived kind beside the arms.
  Nothing writes it to a node property, and no DDL column holds it (ADR-0036 D4's rule, kept by
  D2).
- **I22's vacuity is bounded and must be stated.** §2.3 puts `_check_I22` in
  `invariants._CHECKS`, which runs at all five `validate` sites. It runs non-vacuously at the
  loader's own call and at the store write that replays it. Every adapter stages a `Contrast`
  without arm edges, so it passes vacuously there. **That is sound only while the loader is the
  only `Contrast` minter** (ADR-0029 E), and the prompt's report must say so in those words.

---

## 2. The build

### 2.1 `ONTOLOGY.md` and `bzk/ontology/schema.py` — both homes together

- **§5 DDL, immediately after l.521** (`CONTRAST_IN_EXPERIMENT`):
  ```
  CREATE REL TABLE NUMERATOR_SAMPLE(FROM Contrast TO Sample, MANY_MANY);
  CREATE REL TABLE DENOMINATOR_SAMPLE(FROM Contrast TO Sample, MANY_MANY);
  ```
- `schema.REL_TABLES` gains the same two, beside `CONTRAST_IN_EXPERIMENT`. **Nothing in
  `IDENTITY`.** Identity is an allow-list — `schema.Identity` has `fields`, `anchors`,
  `child_fields`, `authority` and no excluded set — so non-identifying means *absent from
  `fields`*, not *listed somewhere else*.
- l.119 `Contrast` row: arms are declared in curation and materialised as D4's edges; identity
  unchanged.
- l.400–406 `Sample` DDL comment: `role` gains `'isotype_control'`; `antibody` is NULL unless
  `role ∈ {'ip', 'isotype_control'}`.
- l.581: cite ADR-0038 D4 in the provenance-chain sentence.
- §8: mint **I22**, as D2's table, enforced at the loader, with its graph form over D4's edges.
- §11: **Q16** — must an arm be one condition, and are pooled control arms exempt?
- Version 1.45 → **1.46**.

**Not in this prompt:** l.903 / I4 (prompt 32).

### 2.2 `bzk/curation/loader.py` — D1's arms

- Each contrast entry gains `numerator_samples` and `denominator_samples`, resolved against
  `sample_ids` by **exact membership, no normalisation**.
- Refuse, each with its own message and its own test:
  - a key absent from `mapping`;
  - an empty arm;
  - a key repeated within an arm;
  - a sample in both arms;
  - two entries in one record with the same (`numerator`, `denominator`) pair;
  - an entry whose `numerator` equals its `denominator`;
  - an unknown key in a contrast entry, against the recognised set in §0.2.
- Emit the two edge types. `LoadedCuration` carries the resolved arms and the derived kind.
- **The warning.** `contrast_id = evidence_id("Contrast", props, {"Experiment": experiment_id})`
  with `props = {"numerator": …, "denominator": …}`. The arms go on the **entry** and into
  `LoadedCuration`; they must not reach `props`, the node's properties, or `IDENTITY`. The moment
  they do, all five `Contrast` ids move and I3 fails with them.
- Multi-error reporting as the existing refusals do it.

### 2.3 `bzk/ontology/invariants.py` — I22 (handoff P1)

- `_check_I22` as an entry in `_CHECKS`, not a loader-only function.
- It implements D2's table over the change-set's arm edges and the anchor's `modality`.
- The vacuity statement from §1 goes in the function's docstring **and** in the report.

### 2.4 `bzk/curation/loader.py` — the enum, R7, and the mirror guard

- `_SAMPLE_ROLES` (l.311) gains `isotype_control`.
- The R7 check (l.356) widens: `antibody` is NULL unless `role ∈ {'ip', 'isotype_control'}`.
- **Add the mirror guard** — `_SAMPLE_ROLES` and `_IP_MODALITY` against the `Sample` DDL comment,
  parsed from `ONTOLOGY.md`. This closes handoff 10-05 §7's *unguarded mirror*, and it is in scope
  here because this prompt is the change that would otherwise break it silently. Follow the house
  pattern: `schema.py` ↔ §4–§7, `ABSENCE` ↔ §3, `CURATION_BASIS` ↔ §5.3.
- No sample carries `isotype_control`, so no `Sample` id moves.

### 2.5 The three curation records

`curation_PXD018299.json`, `curation_PXD026748.json` and `curation_PXD055843.json` gain
`numerator_samples` / `denominator_samples` on every entry, **exactly as ADR-0038 M4 prints them**
(l.597–614): five entries, 30 keys, 3 against 3, no overlap.

- `curation_PXD026748_shotgun.json` declares no contrast and is **not** edited.
- **`curation_PXD055843.json`'s `unresolved` list is not touched.** It carries eleven entries,
  zero-indexed, among them `[1]` s0, `[2]` the imputation seed, `[4]` arm order and `[6]` which
  DIA-NN quantity the columns hold. None is edited, resolved or renumbered here. `[4]` is P2 and
  belongs to prompt 31; `[2]` and `[1]` bear on PI questions that are still open, and the record
  that states the ingestion block is the *analysis* record's `unresolved[1]`, not this one's.

### 2.6 `tests/test_schema.py` — ADR-0039's guard amendment

- The shape guard gains a pinned-exception table, one entry:
  `NUMERATOR_SAMPLE` / `DENOMINATOR_SAMPLE`, citing ADR-0038 D4, keyed on the pair **and** its
  endpoints **and** its multiplicity.
- **Mutation evidence is required and is the point of the pin:** show that a third
  `Contrast → Sample, MANY_MANY` relationship still fails, and that the pinned pair fails if its
  endpoints or multiplicity change. Follow `ONE_SIDED_SUPERSESSION`'s precedent.
- The reverse-relationship guard (l.101–125) is untouched.

### 2.7 `tests/test_rebuild.py` — **three** pins, not two

The plan and the handoff both say "two pins". The rehearsal found a third, in a different test.

| Pin | Location | Before | After |
|---|---|---|---|
| `tables_created` | l.134 | 58 | **60** |
| `(nodes_staged, edges_staged)` | l.138 | `(18, 40)` | **`(18, 52)`** |
| `EXPECTED_EDGES` | defined l.54, asserted l.173, reused l.293 | no arm keys | gains **`"NUMERATOR_SAMPLE": 6`** and **`"DENOMINATOR_SAMPLE": 6`** |

`EXPECTED_NODES` does not move.

---

## 3. Pre-registration — this container

**Rehearsal disclosure.** The reviewer built §2.1, §2.5 and the edge-emission half of §2.2 in a
scratch worktree of `dfe6640` and measured what follows. Three things were **not** rehearsed and
are predictions only: D1's refusals, §2.3's `_check_I22`, and §2.4's enum, R7 and mirror guard.
One difference to be aware of: the rehearsal carried the arms as a nested `arms` object rather
than D1's `numerator_samples` / `denominator_samples`. The resolution, the ids and every count
below are unaffected by that — the same 30 keys resolve to the same 30 edges — but **this prompt
builds D1's shape, not the rehearsal's.**

**I1 — 0 ids move, every record, every label.** Run the block below at this prompt's commit (via
`git worktree add --detach`) and again on the built tree; compare per record and per label.

```
uv run python - <<'IDS'
import glob
import json
from pathlib import Path

from bzk.curation.loader import load_path

out = {}
for f in sorted(glob.glob("data/curation/curation_*.json")):
    r = load_path(Path(f))
    out[f] = {n["id"]: n["__label__"] for n in r.nodes}
print(json.dumps(out))
IDS
```

Predicted: `Project`, `Experiment`, `Dataset`, `Analysis`, `Sample` and `Contrast` all **0 gone /
0 new**, in all four records. Measured in the rehearsal.

**I2 — loader edges per record.** Measured in the rehearsal, not computed:

| record | nodes | edges | arm edges |
|---|---|---|---|
| `curation_PXD018299.json` | 18 → 18 | 40 → **52** | +12 |
| `curation_PXD026748.json` | 18 → 18 | 40 → **52** | +12 |
| `curation_PXD026748_shotgun.json` | 16 → 16 | 38 → **38** | +0 |
| `curation_PXD055843.json` | 23 → 23 | 57 → **63** | +6 |

30 arm edges in total, agreeing with M4's *Contrast-Sample edges implied: 30*. All 30 mapping keys
resolve; six distinct `Sample` ids per contrast.

**I3 — `tests/fixtures/pxd018299_curation_ids.json` is unchanged**, `contrasts` block included.
`git diff -- tests/fixtures/` is empty.

**The checks:**

| Check (target) | Before | After, predicted |
|---|---|---|
| `uv run pytest` (full) | 908 passed, 14 skipped | all pass; state the counts |
| `uv run pytest tests/test_schema.py` | 20 passed | 20 passed, with §2.6's guard amended |
| `uv run mypy bzk tests` | Success, 117 files | Success, 117 files |
| `uv run ruff check bzk tests` / `ruff format --check bzk tests` | clean / 117 | clean / 117 |

**The intermediate state, measured.** With §2.1, §2.2's edges and §2.5 applied but **before** §2.6
and §2.7, the full suite gives **exactly four failures** and no others:

1. `tests/test_rebuild.py::test_rebuild_creates_schema_and_leaves_the_archive_alone` — `tables_created` 60 vs 58;
2. `tests/test_rebuild.py::test_rebuild_puts_the_curation_record_in_the_graph` — `EXPECTED_EDGES` short by the two arm keys;
3. `tests/test_schema.py::test_no_two_relationships_share_endpoints_and_multiplicity` — P0, cleared by §2.6;
4. `tests/test_tautology_sweep.py::test_every_classified_instance_re_runs_its_recorded_evidence`.

**Number 4 is a consequence, not a defect, and must not be "fixed".** `_ARCHIVE_DIGEST_EVIDENCE`
carries `green_scope=("-q",)`, so its mutated copy runs the whole suite; while any of 1–3 is red,
it is red. It clears when they do. `tests/test_tautology_sweep.py` is **not** edited by this
prompt unless the sweep requires classification of new comparisons, and then only for that.

**One correction to the record.** ADR-0038, ADR-0039 and the handoff all state the shape-guard
conflict as **2 failed, 18 passed**. That measurement added the DDL *without* the `schema.py`
mirror, and said so. This prompt edits both together, so the figure here is **1 failed, 19
passed** — the mirror test passes. Do not pre-register 2/18.

**If any prediction fails, stop and report. Do not adjust code, fixtures or pins to match.**

---

## 4. Commit and report

**One commit**, fast-forwarded onto `main`, with a single-subject-line message in the series' form,
naming: D1/D2/D4/D8 built; arms declared by mapping key and resolved at the loader; I22 in
`_CHECKS`; `NUMERATOR_SAMPLE`/`DENOMINATOR_SAMPLE` non-identifying; `isotype_control` added and R7
widened; the mirror guarded; ADR-0039's pinned exception; ONTOLOGY v1.45 → v1.46; **0 ids move**;
`test_rebuild.py`'s three pins moved.

**Files expected:** `ONTOLOGY.md`; `bzk/ontology/schema.py`, `bzk/ontology/invariants.py`,
`bzk/curation/loader.py`; the three curation records; `tests/test_schema.py`,
`tests/test_rebuild.py`, `tests/test_curation_loader.py`. Any other file needs a reason in the
report.

**Report:** the commit hash; §0's answers; I1's per-record, per-label table; I2 as measured;
§3's table with "After" measured; the four intermediate failures as actually seen; every new
refusal's message on the unmutated tree; **mutation evidence for every new refusal, for I22, and
for §2.6's pin** (bytecode disabled from the start, each mutation read back, each reverted); the
full `ONTOLOGY.md` diff; `git diff --stat`; and the four-point close.

Then stop.

---

## 5. For bzk's Mac — pre-registered now, run later

Nothing below runs in the container. Cold rebuild, because `rebuild` drops and recreates the stores
(`bzk/rebuild.py` l.154, `drop_stores`).

- **ids:** all 16 labels, 0 gone / 0 new.
- **M0 moves, by design** (handoff 10-05 §3.3): 58 → **60** tables; replay 18/40, 18/40, 16/38,
  23/57 → **18/52, 18/52, 16/38, 23/63**; edge statements 31,349 → **31,379**; node statements
  32,793, observations 4,195 / 4,768, 48 refusals and `INCOMPLETE` all unchanged.
- **graph:** 30 arm edges; M1 `[4b]` unchanged.
- Step A / Step B as prompt 28 ran them.

---

## Out of scope

- D5, D6-revised, D7 — prompts 30, 31, 32.
- A D2/D3 invariant-level check. §2.3 puts I22 in `_CHECKS`, which is the direction handoff 10-05
  §7 pointed, but the D2/D3 invariant itself stays open.
- F-d, unknown keys inside `mapping` entries. D1 refuses unknown keys in **contrast** entries only.
- `write_cells` over-reporting a repeated key; the drift checker's failed-fetch reporting; the
  stale tautology floor; the protein-groups binding function.
- PXD055843's `unresolved[4]` (P2, prompt 31) and the PI questions.
