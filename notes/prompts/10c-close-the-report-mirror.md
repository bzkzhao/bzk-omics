# PROMPT 10c — close the report-mirror class, and forbid force-pushes

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.
Base: `6703249`. Verify HEAD before anything else; if it differs, report the
commits between and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`.

This is a correction turn from the audit of 10b. It adds no capability.

**Never force-push, and never amend or rebase a commit that has been pushed.**
A correction discovered after a push is a new commit, with a line in the report
saying why. That holds even when it makes this turn's commit count differ from
what the Task section says: the history outranks the count. 10b amended a
pushed commit and force-pushed `main`. This turn writes the rule down (C3).

**Do not write, retype or commit any file under `notes/prompts/`.** bzk commits
prompt files from his own copy.


## Receipt checks

R1. `bzk/rebuild.py:95–124` (`ReplayReport`) and `:126–144`
    (`RebuildReport`). List each class's field names in order. Name the fields
    that are in one class and not the other, and say which class each belongs
    to.

R2. `bzk/rebuild.py:453–464`. Quote it. How many lines restate a
    `ReplayReport` field by hand? What happens today, and at which stage, if a
    field is added to `ReplayReport` and not to this call?
    - Is it a failure or a silence?
    - If a failure, is it at import, in a test, or at runtime?

R3. `CLAUDE.md:94`. Quote the sentence about fast-forwarding onto `main`.
    Does any line of `CLAUDE.md` forbid a force-push or the amendment of a
    pushed commit? Answer from a `grep` you report, not from reading.

R4. `tests/test_agent_config_references.py`. Say in one sentence what it checks
    in `CLAUDE.md`. Say whether an added sentence with no file path, line
    reference or backticked identifier can trip it.


## Changes

**C1 — Remove the hand-written mirror.** Replace the field-by-field call at
`:453–464` with a construction that carries every `ReplayReport` field by
iterating `dataclasses.fields(ReplayReport)`, plus `tables_created`.

After this, a field added to `ReplayReport` without a matching
`RebuildReport` field raises `TypeError` on every rebuild. That turns a silent
omission into a loud one. Keep `RebuildReport` as a declared dataclass: its
fields are the public surface and stay spelled out. Do not derive it
dynamically.

**C2 — Guard the declaration.** Add one test with two assertions:
- the fields of `ReplayReport` are a subset of those of `RebuildReport`, less
  an explicit, named exclusion set, which today is empty;
- each shared field has the same type annotation in both classes.

Also assert that `RebuildReport`'s fields beyond `ReplayReport`'s are exactly
`{"tables_created"}`, so that a field added to `RebuildReport` alone is
noticed too.

This test is where the class is closed. C1 makes a violation loud at runtime,
and C2 makes it fail before any rebuild runs.

**C3 — The rule, in `CLAUDE.md`.** Add one sentence to the `:94` bullet, after
its fast-forward sentence, and change nothing else in the file: never
force-push, and never amend or rebase a pushed commit; a correction after a push
is a new commit. Name 10b's force-push as the instance, by its prompt number and
without a SHA. The amended SHA no longer exists and cannot be cited.


## Tests — each seen to fail before it passes

For each test, report the mutation, confirmed applied by read-back and then
reverted, and the failing assertion's message.

- **C2, subset half:** add a dummy `int` field to `ReplayReport` in a copy.
- **C2, type half:** change one shared field's annotation in `RebuildReport`
  in a copy.
- **C2, extra-field half:** add a dummy field to `RebuildReport` alone.
- **C1:** with C2's test disabled, add a dummy field to `ReplayReport` alone.
  Show that an existing rebuild test now fails with `TypeError`. Name the test.
  This is the evidence that C1 turned the silence into a failure.

A mutation that turns out to be unreachable is reported as such and replaced,
as 10b did.


## Registered expectations

E1. Suite = 708 passed + the new tests, 14 skipped. Report the split.
E2. `test_rebuilt_ids_match_the_committed_pin` passes unmodified.
E3. No figure changes. `RebuildReport`'s repr has the same fields in the same
    order as at `6703249`. Show a repr from a synthetic rebuild before and
    after C1.


## Task

1. Run R1–R4.
2. Make C1–C3 and write the tests.
3. Run E1–E3 and every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit C1 and C2 as one commit (`rebuild:` prefix). Commit C3 alone
   (`docs:` prefix). Push. Fast-forward only.
5. Write `notes/reports/10c-close-the-report-mirror-report.md` and commit it
   alone. Push.


## Out of scope

- Everything 10b's out-of-scope list named.
- Any other field or wording in either report class.
- Any other line of `CLAUDE.md`.
- `notes/prompts/`.


## Report

- R1–R4 answered, with R3's `grep` shown.
- C1–C3, each with the file and lines changed.
- Each mutation and its failure message.
- E1–E3, each held or missed.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- Whether the class *a `ReplayReport` field not carried into `RebuildReport`*
  is now closed, and by what.
- What this turn does NOT cover.
- Commit SHAs and the push range, stating that every push was a fast-forward.
