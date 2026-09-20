# PROMPT 15c — the window diagnostic reads multi-window cells

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.

**Base.** Fetch, then fast-forward to `origin/main`. It must be `b0b220e`, or a
fast-forward of it whose only additions are under `notes/prompts/`. Otherwise
report and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`. **Never force-push, and never amend or rebase a pushed
commit. Do not write, retype or commit any file under `notes/prompts/`.** This
container has no raw store.


## What happened

bzk ran the generator on the real files. **Ten of the pre-registration's eleven
figures held, including exposure = 288.** One missed:
- **Registered, C3w:** 6 of 6 join losses have exactly one window-matched
  deposit row.
- **Measured:** 1 of 6.

The pre-registration says a C3w miss means *"the generator keys differently
from turn 09. Find the difference before trusting either."*

**The difference is found (measured on bzk's machine, read-only).**
- 85 of the deposit's 2,653 rows carry a `Sequence window` cell holding
  **several windows separated by `;`**, one per candidate protein.
- The generator matches the whole cell for equality
  (`pxd026748_published_cascade.py:306–308` and `:334–336`), so it finds only
  single-window cells.
- Splitting on `;` finds **exactly one** row for each of the six:

| `#` | published | whole-cell | split on `;` → row, protein owning that window |
|---|---|---|---|
| 106 | P21333 K16 | — | 200, O75369 |
| 141 | P60842 K60 | — | 1065, P38919 |
| 148 | P08238 K112 | 456 | 456, *(Proteins and windows differ in count)* |
| 169 | Q9BXB5 K395 | — | 2320, Q9BXB4 |
| 176 | P08238 K283 | — | 459, *(Proteins and windows differ in count)* |
| 215 | Q92973 K56 | — | 84, O14787 |

So under turn 09's instrument C3w holds at 6 of 6. As things stand, the fixture
would record `window_matches: []` for five rows, and that would assert that no
deposit row shares their window. **That assertion is false, so the fixture has
not been committed.**


## Receipt checks

R1. Quote `:300–310` and `:330–340`. State the matching rule as it stands, and
    what `[]` asserts to a reader of the fixture.
R2. `bzk/adapters/maxquant_sites.py`. Does the adapter already split any
    `;`-separated site-table column, such as `Proteins`? Quote it. If it does,
    reuse its splitting rule and don't write a second one.


## Changes

**C1 — Split multi-window cells in the diagnostic.** Index each deposit row
under **every** window its `Sequence window` cell carries. For each window match,
record `{row, protein}`:
- `protein` is the `Proteins` entry at the same position as the matched window,
  **only when** `Proteins` and `Sequence window` split to the same count;
- otherwise `protein` is `null`, with `protein_unattributed_reason` saying the
  counts differ and giving both counts.

**Never guess the alignment.**

**C2 — The diagnostic stays a diagnostic.** No key, no stage and no count other
than the window matches changes. A row lost at `join` stays lost. `[]` must now
mean *"no deposit row carries this window among its windows"*. State that
meaning in the module where `window_matches` is built, and in the fixture's
`note`.


## Tests

Each test must be seen to fail before it passes. Report each mutation and its
failure message.

T8. A deposit row whose `Sequence window` holds two windows, with a
    two-candidate `Proteins`. A published row missing on key but carrying the
    **second** window gets `{row, protein: <second candidate>}`. Mutation: revert
    to whole-cell equality.
T9. Counts differ: three windows but two proteins. The match is recorded with
    `protein: null` and the reason. Mutation: align by position regardless.
T10. The row stays lost at `join`, and the summary's counts are unchanged from
     the same input under the old rule. Mutation: let a window match recover
     the row.


## Registered expectations

E1. Suite = 741 passed, 14 skipped at base, then plus the new tests.
E2. No existing test changes, apart from any that pin the old whole-cell
    behaviour. Name each one and say why.
E3. **For bzk's rerun, stated in advance.** The summary is **identical**:
    - exposure 288, with the same stage counts, clusters and coerced cells;
    - the six join losses carry exactly the row/protein pairs in the table above;
    - #148 and #176 carry `protein: null` with the count-mismatch reason.


## Task

1. Verify the base, and run R1–R2.
2. Make C1–C2, and write T8–T10.
3. Run E1–E2 and every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit as one commit (`sources:` prefix), then push, fast-forward only.
5. Write `notes/reports/15c-window-diagnostic-report.md` and commit it alone.
   Push.


## Out of scope

- Any change to the join key or to any stage.
- Recovering any row.
- Interpreting the protein pairs, which is the reviewer's job.
- The anchor's cascade module.
- `notes/prompts/`.


## Report

- R1–R2 answered.
- C1–C2, with the file and lines changed.
- T8–T10, each with its mutation and failure message.
- E1–E2, each held or missed.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- What this turn does NOT cover.
- Commit SHAs and the push range, stating every push was a fast-forward.
