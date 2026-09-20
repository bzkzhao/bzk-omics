# PROMPT 15b — record the supplement's Excel-coerced cells as found

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.

**Base.** Fetch, then fast-forward to `origin/main`. It must be `a33472f`, or a
fast-forward of it whose only additions are under `notes/prompts/`. Otherwise
report and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`. **Never force-push, and never amend or rebase a pushed
commit. Do not write, retype or commit any file under `notes/prompts/`.** This
container has no raw store.


## What happened

bzk ran `python -m bzk.sources.pxd026748_published_cascade` on the real files at
`a33472f`. It computed the records, then failed while serialising:
`TypeError: Object of type datetime is not JSON serializable`, raised at
`main()`'s `write_text`. **Nothing was written, so the no-partial-fixture
property held.**

A read-only diagnostic over the pinned supplement
(`sha256:872371eb…36a870`, sheet `Table 1`, header at sheet row 2) found
**exactly two** date-typed cells. Both are in `Gene name`:

| sheet row | `#` | `Uniprot ID` | cell value, as `openpyxl` returns it |
|---|---|---|---|
| 34 | 32 | Q9UHD8 | `datetime(2021, 9, 9, 0, 0)` |
| 57 | 55 | Q16181 | `datetime(2021, 9, 7, 0, 0)` |

This is the familiar pattern of spreadsheet software converting a gene symbol to
a date. **Which symbol each date replaced is an inference, and it is not made
here.** `PUBLISHED_COLUMNS` copies cells into each record raw
(`bzk/sources/pxd026748_published_cascade.py:260`), and that is where the
`datetime` entered.


## Receipt checks

R1. Quote `pxd026748_published_cascade.py:92–100` and `:255–265`. Name every
    place a published cell's raw value reaches the fixture, and every place a
    published cell is turned into a key through `_text`.
R2. What does `_text` return for a `datetime`? Would a date in `Uniprot ID` or
    `Lysine position` produce a key that looks valid but matches nothing?


## Changes

**C1 — Record coerced cells as found, and flag them.** Every published cell
that `openpyxl` returns as a `datetime`, `date` or `time` is written into the
record as its ISO-8601 string, **unchanged in meaning**. The record also gains
`coerced_cells`, a list of objects `{column, as_found, type}`. `as_found` is the
ISO string, and `type` is the Python type name.

**Do not map a date to a gene symbol, and do not guess one.** That would record
an inference as if it were the source. The summary gains a `coerced_cells`
entry that counts coerced cells by column and lists the `#` of each affected
row.

**C2 — A date must never become a key silently.** If a key column (`Uniprot ID`
or `Lysine position`) holds a coerced cell, the row is lost at `join` with reason
`coerced_key`. It is not sent through `_text` to fail as an ordinary
`no_key_match`. Nothing in the real supplement hits this, since both coerced
cells are in `Gene name`. It exists so the failure would be named if it ever
occurred.

**C3 — Nothing else changes.** Stages, key rule, groups and other outputs stay
as they are. After C1, serialisation must succeed on any value `openpyxl` can
return in these columns.


## Tests — added to `tests/test_pxd026748_published_cascade.py`

Each test must be seen to fail before it passes. Report the mutation and the
failure message for each.

T6. A synthetic workbook with a `datetime` in `Gene name`:
    - `main()` writes a fixture that parses as JSON;
    - the record carries the ISO string and a `coerced_cells` entry naming
      `Gene name`;
    - the summary counts it.

    Mutations: drop the conversion, which must fail on serialisation; drop the
    flag, which must fail on the assertion.
T7. A `datetime` in `Lysine position`: the row is lost at `join` with
    `coerced_key`, not with `no_key_match`.


## Registered expectations

E1. Suite = 738 passed, 14 skipped at base, then plus the new tests.
E2. No existing test changes, and no id pin moves.
E3. **For bzk's rerun on his machine, stated here in advance.** The rerun
    succeeds. The summary's `coerced_cells` reports **2** cells, both in
    `Gene name`, at `#` 32 and 55. No row is lost with `coerced_key`. **Every
    cascade figure is exactly what it would have been without the dates**, since
    neither affects a key.


## Task

1. Verify the base, and run R1–R2.
2. Make C1–C3, and write T6–T7.
3. Run E1–E2 and every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit as one commit (`sources:` prefix), then push, fast-forward only.
5. Write `notes/reports/15b-coerced-cells-report.md` and commit it alone. Push.


## Out of scope

- Any gene-symbol inference.
- Generating the fixture.
- The reconstruction.
- `notes/prompts/`.


## Report

- R1–R2 answered.
- C1–C3, with the file and lines changed.
- T6–T7, each with its mutation and failure message.
- E1–E2, each held or missed.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- What this turn does NOT cover.
- Commit SHAs and the push range, stating every push was a fast-forward.
