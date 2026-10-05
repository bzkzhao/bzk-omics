# Prompt 28 — Build ADR-0036 D2 and D3: `Sample.role` and `bait` (identifying, determined), `antibody`, and `modality = 'ip_ms'`

**Repository:** `main` at the commit adding this prompt, directly on top of `d19a670`.

**Governing:**
- `decisions/0036-ip-ms-as-role-tagged-observations.md`:
  - D2 (l.137–168);
  - D3 (l.170–176);
  - R2 (l.51–65) and R3 (l.67–76);
  - *Implied changes* l.366–376;
  - *Landing verification* V2, V4 and V5 (l.450–453).
- `notes/REVIEWER-HANDOFF-2026-10-04.md` §6 step 5, which carries 2026-10-03 §5 step 2.
- `CLAUDE.md` l.95–99, the four-point close.

**Settled ground.** ADR-0036 as accepted, the `Contrast` build at `767e6e4`, and D8 at `265beac`.
This prompt builds D2 and D3 as accepted. It does not build:
- D5 (I22);
- D7 (I4 widened);
- any IP curation record or ingestion.

**This is an identity change.** Every `Sample` id re-mints exactly once. Nothing else moves. Both
claims are pre-registered below.

**Edits are limited to** `ONTOLOGY.md`, `bzk/` and `tests/`. No ADR, no `ROADMAP.md`, no
`HANDOFF.md`, no curation record, and nothing under `notes/` other than this prompt.

The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **Repository state.**
   - Run `git log --oneline -2` and `git status --short`.
   - HEAD must be this prompt's commit, with `d19a670` beneath it, and the tree must be clean.
   - If either check fails, stop.
   - Then run, as the open-of-turn checks: `uv run mypy bzk tests`, the full `uv run pytest`, and
     `uv run pytest tests/test_schema.py`. Expected:
     - mypy `Success` over 117 files;
     - **897 passed, 14 skipped**;
     - 20 passed.
2. **D2 and D3 as accepted.**
   - Quote ADR-0036 l.137, l.158–163 and l.170–176 verbatim.
   - Then state in one sentence each:
     - what determines `role`'s absence;
     - what determines `bait`'s absence;
     - D3's "if and only if".
3. **How a `determined` absence is enforced today.**
   - Quote `bzk/curation/loader.py` l.246–250.
   - Say whether anything in `bzk/` checks that a `determined` field is null *only* where its
     determiner says it should be. Name the file and line, or state that nothing does.
   - Scope the answer to the existing rows: `Sample.cell_line`, `Sample.timepoint_h` and
     `Imputation.seed`.
   - Expected: the loader treats membership in `schema.ABSENCE` as permission to be null, and
     checks no condition. I15's seed check is the one exception, and it lives in an invariant.
4. **Where `Sample` is minted.**
   - Name every place in `bzk/` that mints a `Sample` id.
   - Name every place that emits a `Sample` node without minting it.
   - Expected: the loader mints, at l.403–406. `bzk/adapters/base.py` `sample_nodes` re-emits loader
     nodes, narrowed to DDL columns (l.51–70).
5. **Mapping-entry keys.**
   - Quote `loader.py` l.371–373.
   - Say what happens today to a key inside a `mapping` entry that is not in `_SAMPLE_FIELDS`.
   - Expected: it is dropped silently. `_check_known_keys` covers top-level keys only.
6. **The pin.**
   - Quote the fixture's `note` key from `tests/fixtures/pxd018299_curation_ids.json` far enough to
     include its "regenerated and the move explained" sentence.
   - List the fixture's top-level keys, with the count of ids under each.
   - Expected: `project`, `experiment`, `dataset`, `analysis`, 12 `samples` and 2 `contrasts` —
     18 ids.
   - Name every test that reads the fixture.

**Do not start §1 until bzk replies.**

---

## 1. What D2 and D3 decide, and the readings this prompt adds

**D2.** `Sample` gains two identifying fields and one non-identifying field:
- **`role`.** A closed enum: `ip` or `no_antibody_control`. Its absence is **determined by
  `Experiment.modality`**: NULL unless `modality = 'ip_ms'` (R2).
- **`bait`.** A protein CURIE, for example `uniprot:P05161`. Its absence is **determined by
  `role`**: NULL unless `role = 'ip'`.
- **`antibody`.** Non-identifying.

**D3.**
- `Experiment.modality` gains the value `'ip_ms'`.
- `role` is non-null, and one of its two values, **if and only if** `modality = 'ip_ms'`.

The reviewer found four things while writing this prompt. §0 asks you to verify each.

**F-a. `antibody` gets no §3 row.**
- ADR-0036 l.370 says *"classify its absence per §3"*.
- But §3 classifies identifying fields only. `tests/test_schema.py` l.331–334 refuses any other
  row, which is the same finding as prompt 27's F-a.
- So `antibody` is a nullable non-identifying column. Its rule lives in the DDL comment and in
  §2.3's check, not in §3.

**F-b. No `determined` row has its condition enforced today (§0.3).**
- D3's "if and only if" is a rule the record states outright, so this build enforces it, together
  with `bait`'s rule, at the only place a `Sample` is minted: the loader (§2.3).
- This is the first determiner condition the loader checks.
- **The existing rows (`cell_line`, `model_system`, `timepoint_h`) stay unenforced.** That gap is
  older than this prompt and gets its own prompt.

**F-c. Two readings beyond D2's text.** Both are refusals, so they can only narrow what loads.
- **`bait` must begin with `uniprot:`.** D2 names a CURIE and gives `uniprot:P05161`. Every
  protein CURIE the platform mints is `uniprot:`, so any other form is refused rather than
  carried.
- **`antibody` is NULL unless `role = 'ip'`.** A `no_antibody_control` has none by definition
  (D2's table), and a lysate sample has no IP.
- If bzk rejects either reading, it comes out before §1 starts.

**F-d. Mapping-entry keys are not checked for unknowns (§0.5).**
- After this build, a misspelt `role` or `bait` in an `ip_ms` record is still caught, because
  §2.3 then finds the required field missing.
- A misspelt `antibody` is dropped silently.
- The general fix is out of scope.

## 2. The build

### 2.1 `ONTOLOGY.md` and `bzk/ontology/schema.py` — both homes together

- **Identity table, `Sample` row (ONTOLOGY l.115).**
  - Append `role` and `bait` to the identifying fields, **after `organism_taxid`, in that order**.
  - Add `antibody` to the non-identifying list.
- **`schema.IDENTITY["Sample"].fields` (`schema.py` l.247–257).** Append `"role"` and `"bait"`
  after `"organism_taxid"`, in that order. **The order is identifying.** §3's predicted ids
  assume it.
- **§3 absence table.** Insert two rows directly after `Sample.timepoint_h` (ONTOLOGY l.146):
  - `Sample` | `role` | determined | `Experiment.modality`: NULL unless `modality = 'ip_ms'`
    (ADR-0036 D2, D3);
  - `Sample` | `bait` | determined | `role`: NULL unless `role = 'ip'` (ADR-0036 D2).
- **`schema.ABSENCE`.** Add the same two rows after `("Sample", "timepoint_h")`.
- **ONTOLOGY l.380.** The `modality` comment gains `'ip_ms'`.
- **`Sample` DDL** (ONTOLOGY l.384–398, `schema.py` l.414–428). After `replicate_type`, add:
  - `role STRING`, commented with `'ip' | 'no_antibody_control'`, NULL unless the experiment's
    modality is `'ip_ms'`, and the §3 reference;
  - `bait STRING`, commented as the targeted protein's `uniprot:` CURIE, NULL unless
    `role = 'ip'`;
  - `antibody STRING`, commented as non-identifying, the clone or catalogue number, NULL unless
    `role = 'ip'`, and that it may be NULL even then (D2: it is conditionally reported).
- **Version.** Bump ONTOLOGY 1.44 → 1.45. Leave *Last reviewed* as it is.

`tests/test_schema.py` must pass with both homes moved together, and must not be edited. The
reviewer's rehearsal of exactly these table edits gave 20 passed.

### 2.2 `bzk/curation/loader.py` — reading the fields

- `_SAMPLE_FIELDS` (l.129–139) gains `"role"`, `"bait"` and `"antibody"`.
- Nothing else changes about how fields are read.

### 2.3 `bzk/curation/loader.py` — the D2/D3 check (the guard)

**The function.** Add
`_check_sample_roles(modality: Any, samples: Mapping[str, Mapping[str, Any]]) -> None`. It raises
`CurationInvalid` naming **every** offending `mapping[...]` path in one message, not only the first.

**Where it runs.** Call it in `load` after `samples` is built (l.367–373) and before
`_pending_owed` (l.379). That places it with the vocabulary checks, ahead of completeness, as
`load`'s docstring orders them.

**What it refuses.** For each sample:

| # | Refusal | Ground |
|---|---|---|
| R1 | `role` not in `{None, "ip", "no_antibody_control"}` | D2: closed enum |
| R2 | `role` is not None while `modality != "ip_ms"` | D3 / R2 |
| R3 | `role` is None while `modality == "ip_ms"` | D3 |
| R4 | `bait` is not None while `role != "ip"` | D2 |
| R5 | `bait` is None while `role == "ip"` | D2: identifying, and no absence classified for `role = 'ip'` |
| R6 | `bait` is not a `str` beginning `uniprot:` | F-c |
| R7 | `antibody` is not None while `role != "ip"` | F-c |

**What the message carries.**
- the path, in the form `mapping['…'].role`;
- the value found;
- the rule broken, citing ADR-0036 D2/D3 and ONTOLOGY §3.

**Tests**, in `tests/test_curation_loader.py`:
- **Build a valid `ip_ms` record in the test.** Start from `curation_PXD018299.json` read as JSON.
  Set `experiment.modality = "ip_ms"`. Give every mapping entry
  `role = "ip"`, `bait = "uniprot:P05161"` and an `antibody`, except one entry, which gets
  `role = "no_antibody_control"` and no `bait`. Assert the record loads.
- **R1–R7.** One case each, made from that record or from the real record, each refused with its
  own message.
- **One multi-error case.** Show the message names two paths at once.
- **D2's purpose, in one test.** Two samples identical in every field except `role` (`ip` against
  `no_antibody_control`, with `bait` set accordingly) mint **different** ids.
- **The existing records.** All four committed records still load, and every `Sample` in them has
  `role`, `bait` and `antibody` all `None`.

**Mutation evidence** for R1–R7 and for the call site, per `CLAUDE.md` l.97:
- Run with bytecode disabled from the start: `-B`, `PYTHONDONTWRITEBYTECODE=1`, and a cleared
  `__pycache__`. This was prompt 27's lesson, recorded at 2026-10-04 §5.
- For each mutation, give it, read it back, show it red, then show a byte-identical restore and
  green.

### 2.4 The pin — regenerate `samples` only

- Regenerate `tests/fixtures/pxd018299_curation_ids.json` `samples` from the loader, using the
  recipe in the fixture's own note.
- **Leave unchanged:**
  - `project`, `experiment`, `dataset`, `analysis`;
  - `contrasts`, which the note's recipe does not print;
  - the `note` itself.
- §3 predicts every value. If the regenerated `samples` differ from §3's twelve ids, **stop**.
- The explanation the note demands goes in the commit message (§4).

## 3. Pre-registration — this container

**Rehearsal disclosure.** The reviewer applied §2.1, §2.2 and §2.4's identity edits in a scratch
clone of `d19a670` and measured what follows. **§2.3 was not rehearsed.** These predictions test
whether the prompt reproduces that run.

**I1 — every `Sample` moves, nothing else does.**
- Run the block below at this prompt's commit (via `git worktree add --detach`), and again on the
  built tree.
- Compare the two outputs per record and per label.
- Predicted:
  - `Sample` moves **12, 12, 12 and 18 = 54**, for PXD018299, PXD026748, PXD026748 shotgun and
    PXD055843;
  - `Project`, `Experiment`, `Dataset`, `Analysis` and `Contrast` move **0** in every record.

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

**I2 — the regenerated `samples` are exactly these.**

```
"Ratio mod/base WT_1":               "bzk:a7397c31a33ec3fd123688e28c5b1f77"
"Ratio mod/base WT_2":               "bzk:ae46521ad93eb8f631d6bd3cf8d788bd"
"Ratio mod/base WT_3":               "bzk:b8ed424bcc7974e3eb6e8ec354406c80"
"Ratio mod/base WT_IFN_1":           "bzk:160466ee6ccbc0abd5668347e6d2cfc2"
"Ratio mod/base WT_IFN_2":           "bzk:af00d698a4c1d4756d18be60ac97c8a9"
"Ratio mod/base WT_IFN_3":           "bzk:6411e062628cbb86cbe1ac3030454005"
"Ratio mod/base KO_1_181212063719":  "bzk:1b87dadd0711177f9ee7616df1a236f3"
"Ratio mod/base KO_2":               "bzk:1a858f54fbb68f50d130ad9ba863ad8c"
"Ratio mod/base KO_3":               "bzk:9ce216ff87e7ff506b8934471a030e11"
"Ratio mod/base KO_IFN_1":           "bzk:ad6f2630025334e7d133986b8006dd48"
"Ratio mod/base KO_IFN_2":           "bzk:bf85e95f15356faf27de03f68199ce8a"
"Ratio mod/base KO_IFN_3":           "bzk:224e0032a0baefb70f4839167a0c1080"
```

`git diff d19a670 -- tests/fixtures/pxd018299_curation_ids.json` touches exactly these twelve
value lines.

**The checks:**

| Check (target) | Before (`d19a670`) | After, predicted |
|---|---|---|
| `uv run mypy bzk tests` | Success, 117 files | Success, 117 files |
| `uv run pytest` (full) | 897 passed, 14 skipped | all pass; **14 skipped**; state the count |
| `uv run pytest tests/test_schema.py` | 20 passed | 20 passed, file unedited |
| `uv run ruff check bzk tests` / `ruff format --check bzk tests` | clean / 117 | clean / 117 |
| Rehearsal, after §2.1, §2.2 and §2.4 but **before** regenerating the pin | — | exactly 3 failures: `test_the_minted_ids_have_not_moved`, `test_rebuilt_ids_match_the_committed_pin`, and the sweep's `test_every_classified_instance_re_runs_its_recorded_evidence` (it runs the whole suite as its green scope, so it fails while the pin does). Report what you see at that point |
| `git diff d19a670 -- tests/fixtures/pxd018299_platform_targets.json` | — | empty |

**If any prediction fails, stop and report.** Do not adjust code or fixtures to match.

## 4. Commit and report

**One commit**, fast-forwarded onto `main`, with this message:

`ADR-0036 D2+D3 built: Sample.role/bait identifying (absence determined by Experiment.modality / role), antibody non-identifying, modality 'ip_ms', D2/D3 enforced in the loader (R1-R7); ONTOLOGY v1.45. Re-mint, explained per the pin's note: role and bait join Sample identity, and an absent identifying field still renders into the tuple, so all 54 Sample ids move once (12/12/12/18); no other id moves; pxd018299_curation_ids.json samples regenerated, other keys untouched`

**Files expected:**
- `ONTOLOGY.md`;
- `bzk/ontology/schema.py`, `bzk/curation/loader.py`;
- `tests/fixtures/pxd018299_curation_ids.json`, `tests/test_curation_loader.py`;
- `tests/test_tautology_sweep.py` only if the sweep requires classification of new comparisons.

Any other file needs a reason in the report.

**Report:**
- the commit hash;
- §0's answers;
- I1's per-record, per-label table;
- I2 as a diff;
- §3's table with "After" measured;
- the R1–R7 messages on the unmutated tree;
- the mutation evidence;
- the full `ONTOLOGY.md` diff;
- `git diff --stat d19a670`;
- the four-point close.

Then stop.

## 5. For bzk's Mac — pre-registered now, run later

The graph on bzk's Mac was written at `265beac` and has not changed since: everything run since
was read-only. **Step A must run before the build commit is pulled.** It photographs the current
ids.

**Step A — right after this prompt lands, before the build is pulled.**

```
git pull --ff-only
uv run python -c "import pathlib;t=pathlib.Path('notes/prompts/28-d2-d3-sample-role-bait-ip-ms.md').read_text();m=\"<<'BEFORE'\n\";s=t.index(m)+len(m);exec(compile(t[s:t.index('\nBEFORE\n',s)],'before','exec'))"
```

```
uv run python - <<'BEFORE'
import json
import pathlib

import kuzu

from bzk.ontology.schema import NODE_TABLES

home = pathlib.Path.home() / ".bzk-omics"
conn = kuzu.Connection(kuzu.Database(str(home / "graph.kuzu"), read_only=True))
snap = {}
for t in NODE_TABLES:
    res = conn.execute(f"MATCH (n:{t.name}) RETURN n.id")
    ids = []
    while res.has_next():
        ids.append(res.get_next()[0])
    snap[t.name] = sorted(ids)
out = home / "ids-before-adr0036-d2.json"
out.write_text(json.dumps(snap))
print("BEFORE", {k: len(v) for k, v in snap.items() if v})
print("BEFORE wrote", out)
BEFORE
```

**Step B — after the build commit lands.**

```
git pull --ff-only
uv run python -m bzk.rebuild
uv run python -m bzk.sources.pxd018299_differential
git status --short
uv run python -c "import pathlib;t=pathlib.Path('notes/prompts/28-d2-d3-sample-role-bait-ip-ms.md').read_text();m=\"<<'AFTER'\n\";s=t.index(m)+len(m);exec(compile(t[s:t.index('\nAFTER\n',s)],'after','exec'))"
```

```
uv run python - <<'AFTER'
import json
import pathlib

import kuzu

from bzk.ontology.schema import NODE_TABLES

home = pathlib.Path.home() / ".bzk-omics"
conn = kuzu.Connection(kuzu.Database(str(home / "graph.kuzu"), read_only=True))
snap = {}
for t in NODE_TABLES:
    res = conn.execute(f"MATCH (n:{t.name}) RETURN n.id")
    ids = []
    while res.has_next():
        ids.append(res.get_next()[0])
    snap[t.name] = sorted(ids)
before = json.loads((home / "ids-before-adr0036-d2.json").read_text())
for label in sorted(set(before) | set(snap)):
    b, a = set(before.get(label, ())), set(snap.get(label, ()))
    if b or a:
        print("AFTER", label, "| before", len(b), "| after", len(a), "| gone", len(b - a), "| new", len(a - b))
pinned = json.loads(pathlib.Path("tests/fixtures/pxd018299_curation_ids.json").read_text())
print("AFTER pinned Sample ids in the graph", len(set(pinned["samples"].values()) & set(snap["Sample"])), "of", len(pinned["samples"]))
AFTER
```

**Predictions:**

| # | Prediction | Kind |
|---|---|---|
| MA | `BEFORE` reports `Sample` **54**, `Contrast` **5** and `DifferentialResult` **1,362** among its counts | identity: 12 + 12 + 12 + 18 samples; contrasts 2 + 2 + 0 + 1; §3.1 of 2026-10-04 |
| M0 | The rebuild's figures are unchanged from 2026-10-04 §3.1 M0 | identity: fields and columns change, no table and no statement does |
| M1 | Every `[4b]` line is unchanged from 2026-10-04 §3.1 M1 | identity: no `Contrast`, `Analysis` or observation id moves |
| MS | `git status --short` shows **only** `?? notes/prompts/22-walk-two-route-independence.md` | identity. This corrects 2026-10-04 §3.1 M1's wording defect |
| MB | `AFTER Sample`: before 54, after 54, **gone 54, new 54**. **Every other label: gone 0, new 0.** Pinned: **12 of 12** | identity: I1 at graph scale. No node anchors on `Sample` (V2) |

**Reading the result.** Any miss here stops everything. These are all identity predictions, so a
miss is a defect in §2 or in the instrument, not a finding.

## Out of scope

- **Enforcing the existing `determined` rows** (F-b), and a general mechanism for determiner
  conditions.
- **Unknown-key checking inside `mapping` entries** (F-d).
- **A closed vocabulary for `Experiment.modality`.** It stays a commented string. D3 adds a value
  to the comment.
- **ADR-0036 D5 (I22), D6 and D7**, and any IP curation record or ingestion.
- **The drift checker's failed-fetch-as-drift defect** (2026-10-04, after §3.3; next handoff).
- **Everything in 2026-10-04 §7**, and prompt 22.
