# PROMPT 21 — H10 attempt 3: the principled primary, and the typical-draw check

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.

**Base.** Fetch, then fast-forward to `origin/main`. It must be a fast-forward
of `9b69bc1` whose only changes are:
- `walk/RESULT-PXD018299-H10-attempt2.md` and
  `tests/fixtures/pxd018299_h10_attempt2.json`, both added;
- `walk/PREREG-PXD018299-H10-attempt3.md`, added, with sha256 `f83c6d08931ef42467494f007febf137a2360112c699188569627fc07b9ae506`;
- anything under `notes/prompts/`.

Verify with `git diff --stat 9b69bc1..origin/main` and the hash. Otherwise report
and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`. **Never force-push, and never amend or rebase a pushed
commit. Do not write, retype or commit any file under `notes/prompts/`.** This
container has no raw store. **You build and test; bzk runs it.**

**Read these in full before writing anything:**
- `walk/PREREG-PXD018299-H10-attempt3.md`, which is the specification;
- the attempt-1 and attempt-2 pre-registrations, which still govern everything
  attempt 3 does not replace;
- `walk/RESULT-PXD018299-H10-attempt2.md`, for why attempt 3 exists.

**The expectations Z1–Z6 are not inputs.** Where the specification is silent,
choose, record the choice in the module and the report, and never choose by
outcome.


## Part B only: attempt 3 mode in `bzk/sources/pxd018299_h10.py`

Add `attempt = 3` and the flag `--attempt 3`. **Attempts 1 and 2 must stay
byte-reproducible.** Extend the worktree-digest test that turn 20 built so that
it pins attempt 2's canonical fixture as well as attempt 1's.

**Under attempt 3:**
- **The variants** are `joint_half` + `random_excluding_trivial`, which is the
  **primary, fixed by the specification**, and `joint_half` +
  `exhaustive_excluding_trivial`, the secondary. **No tie rule applies,** and
  the primary is never chosen by F1 or by any readout.
- **G2a and G2b are recomputed** and compared with the values in the committed
  attempt-2 fixture, `tests/fixtures/pxd018299_h10_attempt2.json`. Compare the
  precision and recall numerators and denominators, and the direction counts,
  for both variants. **Any difference stops the run** with
  `instrument_fault: true` and nothing else computed.
- **Check A, typical draw:** at the default cell, the median over seeds 0–19 of
  the per-seed count of claims with q ≤ 0.01 and d > 0 must be ≥ 1. Report every
  seed's count.
- **If the primary is not admitted,** write `h10: "not tested (attempt 3)"` and
  report no primary readout.
- **Every readout for both variants:**
  - A, labelled `disclosed_before_run: true`;
  - B, with the verdict, the share over all claims, both isolations and the
    family categories;
  - the whole-table count;
  - C;
  - D and D′.

  **H10's verdict is read from the primary only.**
- **The flags:** every result block carries
  `validation: "in-sample; independent confirmation pending"` and
  `matrix: "deposit, not the published S1"`.
- **Output:** `tests/fixtures/pxd018299_h10_attempt3.json`. **Never write the
  attempt-1 or attempt-2 fixture paths.**

**The stale docstring.** The module docstring at about l.51 still describes the
old `git ls-files` check. Correct it to `git cat-file -e HEAD:<path>`,
consistent with the function. This is a comment-only change and must not alter
either earlier fixture.


## Tests — added to `tests/test_pxd018299_h10.py`

Each test must be seen to fail before it passes. The report gives each mutation
and its failure message.

- **Attempts 1 and 2 are byte-identical** to their pinned canonical digests.
- **The primary is fixed.** With synthetic readouts where the secondary would
  win on any metric, the primary is still `random_excluding_trivial`.
  Mutation: choose by F1.
- **Check A uses the median, not any seed.** A case where one seed reaches
  q ≤ 0.01 and the median does not is **not** admitted. Mutation: revert to
  any seed.
- **The G2 rerun consistency check.** A synthetic mismatch against the committed
  attempt-2 values stops the run with `instrument_fault: true`.
- **Both variants get full readouts,** and the verdict reads the primary alone.
  Mutation: read the verdict from the secondary.
- **Readout A carries `disclosed_before_run: true`.**
- **Attempt 3 never writes the earlier fixture paths.**


## Registered expectations for this turn

E1. The suite is 848 passed and 14 skipped at base, plus the new tests.
E2. No existing test changes, beyond classifications in the tautology sweep
    (named) and the worktree-digest test's extension. The floor is untouched.


## Task

1. Verify the base, and read the documents.
2. Write the attempt-3 mode, the docstring fix, and the tests.
3. Run E1–E2 and every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit (`sources:`), then push, fast-forward only.
5. Write `notes/reports/21-h10-attempt3-build-report.md`, with the run date
   taken from the commit date, and commit it alone. Push.


## Out of scope

- Any real-data run.
- Changes to `perseus_s0` or to any pre-registration.
- Any variant beyond the two named.
- The S1 quantification question.
- The tautology floor.
- `notes/prompts/`.


## Report

- The base check.
- Every choice made where the specification was silent, with its reason.
- Each test, with its mutation and failure message.
- E1–E2, each held or missed.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- What this turn does NOT cover.
- Commit SHAs and the push range, stating every push was a fast-forward.
