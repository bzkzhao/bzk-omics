# Report — record the supplement's Excel-coerced cells as found

**Run at:** 2026-09-20 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Opened at:** `a33472f`, exactly · **Commits:** `be2fcb6`, and this report's own · **Pushed, every push a fast-forward**

**Headline.** Date-typed cells are recorded as ISO-8601 and flagged; a date in a key column is refused by name rather than absorbed as an ordinary miss. **No symbol is inferred for either cell.** E1 held at 741/14, E2 held. **Two changes beyond the brief, both forced by a test and both reported** — one of them because my own new tests took an unrelated module red, which is under *Tests*.

**The base check.** `git rev-parse origin/main` → `a33472f6d5d6010564b98edaaa3c01ae9b7a051e`, which is `a33472f notes: track prompt 15` exactly — `a33472f..origin/main` is empty and `git diff --stat a33472f..origin/main` is empty. No stop condition fired.

---

## Receipt checks

### R1 — where a published cell reaches the fixture, and where it becomes a key

`bzk/sources/pxd026748_published_cascade.py:92–100`:

```python
PUBLISHED_COLUMNS = (
    "#",
    "Cluster",
    "Uniprot ID",
    "Gene name",
    "Lysine position",
    "Multiplicity",
    "Sequence window",
)
```

`:255–265`:

```python
            by_window[_text(row[window_column])].append(_text(row[column["id"]]))

    records: list[dict[str, Any]] = []
    for cells in published:
        record: dict[str, Any] = {
            "published": {name: cells.get(name) for name in PUBLISHED_COLUMNS},
            "deposit_id": None,
            "lost_at": None,
            "loss_reason": None,
            "has_positive_multiplicity_column": None,
        }
```

**A published cell's raw value reaches the fixture at exactly one place: `:260`.** That dict comprehension copies each of the seven columns straight out of the row, and it is where the `datetime` entered. Nothing else writes a published cell into a record.

**A published cell is turned into a key through `_text` at two places, three calls:**

| line | call | what it keys |
|---|---|---|
| `:268` | `_text(cells.get("Uniprot ID"))`, `_text(cells.get("Lysine position"))` | the join key |
| `:277` | `_text(cells.get("Sequence window"))` | the window diagnostic's lookup |

**And one place downstream reads the record's copy rather than the raw cell**, worth naming because after C1 that copy is an ISO string for a coerced cell: `summary` at `:350`, `_text(r["published"].get("Multiplicity")) == "2"`. `:337`'s `str(r["published"].get("Cluster"))` is the same shape without `_text`.

### R2 — what `_text` returns for a `datetime`

Measured:

| input | `_text` returns |
|---|---|
| `datetime(2021, 9, 9, 0, 0)` | `'2021-09-09 00:00:00'` |
| `date(2021, 9, 7)` | `'2021-09-07'` |
| `time(0, 0)` | `'00:00:00'` |

**Yes — a date in `Uniprot ID` or `Lysine position` would produce a key that looks valid and matches nothing.** `_text`'s only special case is the integral float; everything else falls through to `str(value).strip()`, which for a `datetime` is a non-empty, plausible-looking string. The row would be lost at `join` as an ordinary `no_key_match`, indistinguishable in the fixture from a claim the deposit genuinely does not carry — and the coercion would be invisible in the one place it changed an outcome. **That is what C2 exists for.**

---

## Changes

All in `bzk/sources/pxd026748_published_cascade.py`.

### C1 — coerced cells recorded as found, and flagged

**New constants** beside the existing reasons: `COERCED_TYPES = (datetime, date, time)`, `SERIALISABLE_TYPES`, `KEY_COLUMNS`, `REASON_COERCED_KEY`. The `COERCED_TYPES` comment records the failure that produced them, including that nothing was written.

**New `_coerced_type` and `_published_value`**, beside `_text`. `_published_value` returns `value.isoformat()` for a date or time and the value unchanged otherwise. Its docstring says the ISO string is the cell *as found* and makes no claim about what preceded it: `datetime` is a subclass of `date`, so the recorded `type` is `type(value).__name__` — what `openpyxl` handed back, not what it also is.

**In `build`**, the record's construction becomes:

```python
        raw = {name: cells.get(name) for name in PUBLISHED_COLUMNS}
        coerced = [
            {"column": name, "as_found": _published_value(name, value), "type": kind}
            for name, value in raw.items()
            if (kind := _coerced_type(value)) is not None
        ]
        record: dict[str, Any] = {
            "published": {name: _published_value(name, value) for name, value in raw.items()},
            "coerced_cells": coerced,
            ...
```

`coerced_cells` is present on **every** record, empty on almost all of them: a key that appears only where something went wrong is a key a reader has to know to look for.

**In `summary`**, a `coerced_cells` entry with `by_column` and `rows` (the `#` of each affected row), computed over **every** record rather than only those reaching the test — a coerced cell is a fact about the supplement, and counting it only where it survived would report a property of the cascade as a property of the file. T6c is the mutation that pins that.

The fixture's `note` gains a sentence saying the cells are recorded as found and that no symbol is inferred.

### C2 — a date never becomes a key silently

A branch before the join, so `_text` never sees a coerced key:

```python
        if any(entry["column"] in KEY_COLUMNS for entry in coerced):
            record["lost_at"] = cascade.STAGE_JOIN
            record["loss_reason"] = REASON_COERCED_KEY
            record["window_matches"] = window_lead
            continue
```

The window lead is recorded for this loss as for any other join loss — the key is unusable, the window is still a lead.

**One incidental change the branch forced.** The window lookup was inline in the `no_key_match` branch; with two join branches needing it, extracting it as a closure over `cells` tripped `B023` (a function defined in a loop reading the loop's variable — the late-binding trap). It is now an eager local, `window_lead`, computed once per row with a comment saying why. One dict lookup.

### C3 — nothing else changes

Stages, the key rule, the groups, the presence rule and every other output are as they were. The existing fourteen tests pass unmodified.

---

## Tests — each seen to fail before it passes

Three added to `tests/test_pxd026748_published_cascade.py`, all offline. T6 and T7 run `main()` **end to end** against a synthetic deposit, record and supplement, all built in `tmp_path` and stored in a temporary `home`; the supplement is declared with the digest the store returned, which is what lets `verify` find it without a hash anyone typed. The deposit is a site table with a header and **no data rows**, so `parse` resolves nothing and the run is offline and instant.

| # | mutation | test | failing assertion's message |
|---|---|---|---|
| **T6a** | the ISO conversion dropped, returning the raw value | `test_a_date_in_gene_name_is_recorded_as_found_and_flagged` | `TypeError: Object of type datetime is not JSON serializable` — **the original failure, reproduced exactly** |
| **T6b** | the flag condition inverted | same | `assert [{'column': '#', 'as_found': 1, 'type': None}, …] == [{'column': 'Gene name', …, 'type': 'datetime'}]` |
| **T6b′** | `coerced_cells` emptied outright | same | `assert [] == [{'column': 'Gene name', 'as_found': '2021-09-09T00:00:00', 'type': 'datetime'}]` |
| **T6c** | the summary counting only rows that reached the test | same | `assert {'by_column': {}, 'rows': [1]} == {'by_column': {'Gene name': 1}, 'rows': [1]}` |
| **T7** | the coerced-key branch removed | `test_a_date_in_a_key_column_is_refused_by_name` | `assert 'no_key_match' == 'coerced_key'` — **exactly the absorption C2 prevents** |
| **GUARD** | the unknown-type refusal removed | `test_a_type_json_cannot_hold_stops_by_name` | `Failed: DID NOT RAISE CascadeSourceError` |

**T6 asserts all three halves as one claim**: the fixture is read back off disk and parsed as JSON — the defect was a *serialisation* failure, so reading the file is the only assertion that would have caught it — then the ISO string, the `coerced_cells` entry, that an uncoerced row carries the key empty, and the summary.

**T7 asserts both rows**, so `coerced_key` and `no_key_match` are visibly distinguishable in one fixture: `{"coerced_key": 1, "no_key_match": 1}`.

### My new tests took an unrelated module red, and that is how the second extra change was found

The full suite came back **`1 failed, 740 passed`**, and the failure was `tests/test_tautology_sweep.py::test_every_classified_instance_re_runs_its_recorded_evidence` — a module this turn does not touch, reporting that `test_drift.py`'s recorded evidence no longer reproduces.

**I did not assume it was pre-existing.** Stashing the change and running that test on `a33472f` gave `1 passed in 55.96s`, so it was mine. Reproducing it directly — copying the repository without `.git` and running the new module's tests there — gave:

```
subprocess.CalledProcessError: Command '['git', 'rev-parse', 'HEAD']' returned non-zero exit status 128.
```

The sweep re-runs a recorded mutation **in a copy of the repository made without `.git`**, and the moment a test here called `main()` end to end, `_commit()` shelled out to git inside that copy and took the evidence run red. A module unrelated to this one failing because provenance was mandatory.

`_commit()` now returns `null`s where git cannot answer, with the reason in its docstring. **`null` rather than a placeholder**: a fixture whose `commit` reads `"unknown"` asserts a commit by that name, and one whose `working_tree_clean` reads `false` asserts a dirty tree nobody looked at. Verified by re-running the new tests in a `.git`-less copy — **17 passed** — and then by the full suite.

**One lint suppression, with its reason.** `DTZ001` wants a `tzinfo` on every `datetime(...)`. The test helper `_excel_date` carries `# noqa: DTZ001` because Excel stores no zone and `openpyxl` invents none: a tz-aware fixture would be testing a value the supplement cannot contain.

---

## Registered expectations

### E1 — **held**

| | at `a33472f` | after |
|---|---|---|
| passed | 738 | **741** |
| skipped | 14 | **14** |

741 = 738 + 3 new tests.

### E2 — **held**

**No existing test changed.** `git status` before the commit showed two modified files, both of which this turn owns; nothing else under `tests/` was touched, and the fourteen tests from turn 15 pass unmodified.

**No id pin moved.** `test_rebuilt_ids_match_the_committed_pin` → **1 passed**, unmodified. Nothing here writes to the graph.

The tautology sweep needed no new entry; its failure was the `.git` one above, and it is green.

### E3 — registered for bzk's rerun, not run here

Stated in the brief and repeated so the report carries it: the rerun succeeds; the summary's `coerced_cells` reports **2** cells, both in `Gene name`, at `#` 32 and 55; no row is lost with `coerced_key`; and **every cascade figure is exactly what it would have been without the dates**, since neither affects a key. **Nothing in this container can check any of that** — the supplement is not here — and the code's shape is the only argument for the last clause: `Gene name` is read at `:260` and at no key site.

---

## `CLAUDE.md` point 1 — every check, at its actual result, with its target

Environment built with `uv sync` from the committed `uv.lock`. Every command under `.venv/bin/python`.

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **741 passed, 14 skipped** |
| `pytest tests/test_schema.py` | `tests/test_schema.py` | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed!** |
| `ruff format --check` | `bzk tests` | **104 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 104 source files** |

`ruff check .` — which additionally covers the three notebooks, permanently out of scope — **was not run and is reported as not run.**

---

## `CLAUDE.md` point 2 — the change did what it claimed

- **The original failure is reproduced by T6a**, byte for byte: `TypeError: Object of type datetime is not JSON serializable`. That is the strongest available evidence that the defect was real and is closed.
- **`_text`'s behaviour on a date was measured**, not reasoned, before C2 was written on it.
- **The fixture is read back off disk** in both T6 and T7, because the defect was serialisation and an in-memory assertion would have passed throughout.
- **The suite failure was traced rather than assumed pre-existing**: stashed, re-run on the base, then reproduced in a `.git`-less copy.

---

## `CLAUDE.md` point 3 — what this turn does not cover

- **No gene symbol is inferred, for either cell**, and none may be. The fixture records `2021-09-09T00:00:00` and `2021-09-07T00:00:00` and says which column they were in. Whoever recovers `SEPT9` and `MARCH7` — or whatever they were — does it with the paper, and records it somewhere that is allowed to carry an inference. **This module's output is not that place.**
- **E3 is unverifiable here.** The supplement is not in this container; the two cells, their `#` values and the claim that no figure moves are the brief's measurements, repeated, not re-derived.
- **The residual type is named and unhandled by design.** `openpyxl` can return `timedelta`; `_published_value` refuses it with the column and the type rather than choosing a representation. That is a stop, not a conversion, and the next such cell will halt a run.
- **Coercion in a non-published column is out of reach.** Only the seven `PUBLISHED_COLUMNS` pass through `_published_value`; a date elsewhere in the sheet is never read.
- **Nothing detects a cell Excel coerced to a *number* or a *string***. `40795` in `Gene name` is a date that lost its formatting, and it is indistinguishable here from a value that was always a number. Only the typed cases are caught, because only they are decidable from what `openpyxl` returns.
- **`_commit()`'s tolerance is this module's only.** `bzk/sources/pxd018299_published_cascade.py` has the same `check=True` shape and would fail the same way if a test ever called its `main()`. Not changed — it is the anchor's, out of scope here, and named rather than left to be discovered.
- **Out of scope and untouched:** any gene-symbol inference, generating the fixture, the reconstruction, `notes/prompts/`.
- **The tautology sweep's floor** is still stale and untouched.

---

## `CLAUDE.md` point 4 — instructions dropped, partially done, or exceeded

**Nothing dropped. Two changes beyond the brief, both forced and both reported:**

1. **`_published_value` refuses a type JSON cannot hold.** C3 says *"serialisation must succeed on any value `openpyxl` can return in these columns"*, and `timedelta` is such a value with no `isoformat`. Stringifying it would invent a representation nobody chose; refusing it by name turns the next occurrence into a build-time failure that says which column and which type, instead of the opaque `write_text` `TypeError` this turn exists to fix.
2. **`_commit()` tolerates not being in a work tree.** Forced by the sweep's evidence run, as above. Without it this turn's own tests break a module it does not touch.

**One incidental refactor**, named under C2: the window lookup became an eager local because two branches now need it and a closure over the loop variable is the late-binding trap `B023` names.

**No commit was amended and no ref was force-pushed.**

---

## Commits and push range

| commit | contents |
|---|---|
| `be2fcb6` | `sources: record the supplement's Excel-coerced cells as found, and never key on one` — C1, C2, C3 and the three new tests |
| this report's own | `notes/reports/15b-coerced-cells-report.md`, alone |

**Push range:** `a33472f..be2fcb6` for the change, then one commit on top carrying this report.

**Every push in this turn was a fast-forward.** `git push` reported `d7834a0..be2fcb6` on the branch and `a33472f..be2fcb6` on `main` — the `..` form, never the `+` prefix git prints for a forced update. No `--force`, no `--force-with-lease`, no amend, no rebase.
