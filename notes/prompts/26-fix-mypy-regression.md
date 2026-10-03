# Prompt 26 — Fix the `mypy bzk tests` regression from `856c3d1` and `819fe7d`

**Repository:** `main` at the commit adding this prompt, directly on top of `9cf9892`.
**Governing:** `CLAUDE.md` l.96, which names the five checks and their targets.

This is a **type-only fix**. It makes no behaviour change and adds or removes no test. It touches
exactly three files:

- `bzk/ontology/invariants.py`;
- `tests/test_invariants.py`;
- `tests/test_anchor_recompute_dryrun.py`.

Nothing under `walk/`, `ONTOLOGY.md`, `decisions/`, `notes/` (other than this prompt) or
`pyproject.toml` changes. The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **Repository state.**
   - Run `git log --oneline -2` and `git status --short`.
   - HEAD must be this prompt's commit, with `9cf9892` beneath it.
   - The only untracked path allowed is `notes/prompts/22-walk-two-route-independence.md`.
   - If either check fails, stop.
2. **The errors.**
   - Run `uv run mypy bzk tests`.
   - Give its summary line, and every error as `file:line [code]`.
   - Expected: `Found 14 errors in 3 files (checked 117 source files)`, made up of:
     - 12 in `tests/test_anchor_recompute_dryrun.py`;
     - 1 at `bzk/ontology/invariants.py:648 [index]`;
     - 1 at `tests/test_invariants.py:510 [arg-type]`.
   - If the set differs, stop.
3. **Quotations.** Quote these verbatim, each with its line numbers:
   - `bzk/ontology/invariants.py` l.645–648, l.658 and l.688;
   - `tests/test_invariants.py` l.507–510;
   - `tests/test_anchor_recompute_dryrun.py` l.19–40;
   - `tests/test_survey_ip_tables.py` l.17–23.
4. **Where it arrived.**
   - For each of `a74cf18`, `856c3d1` and `819fe7d`, run:
     `git worktree add --detach /tmp/w-<hash> <hash>`
     then, from inside that worktree, `<repo>/.venv/bin/mypy --cache-dir=/dev/null bzk tests`
     then `git worktree remove --force /tmp/w-<hash>`.
   - Give each summary line. Expected:
     - `a74cf18`: `Success: no issues found in 116 source files`;
     - `856c3d1`: `Found 12 errors in 1 file`;
     - `819fe7d`: `Found 14 errors in 3 files`.
   - Confirm `git worktree list` shows only the main tree afterwards.

**Do not start §1 until bzk replies.**

---

## 1. The defect (reviewer audit of `9cf9892`)

`mypy bzk tests` was clean at `a74cf18`. Two commits broke it, and no report since has named mypy:

- **`856c3d1`** added `tests/test_anchor_recompute_dryrun.py`, which produces 12 errors:
  - the fixture, the helper and the four tests are unannotated;
  - `module_from_spec` receives `ModuleSpec | None`;
  - `dry.CHANGE_SETS = 0` assigns an attribute that `ModuleType` does not declare.
- **`819fe7d`** added two errors:
  - `invariants.py:648` indexes `by_rel: dict[str, …]` with `edge.get("type")`, which is
    `Any | None` because `Edge = dict[str, Any]`;
  - `test_invariants.py:510` passes `analysis["id"]`, typed `object` because
    `_curation_change_set` returns `dict[str, object]`, where `e()` wants `str`.

The `2026-10-03` handoff's §1 Suite row reports pytest and ruff, gives no target for ruff, and omits
mypy. That is the omission `CLAUDE.md` l.96 forbids. That handoff is a dated record, so it is
**not** edited here. The report below is where the correction lives.

## 2. The fix — exactly these changes

**Constraints.** No new `# type: ignore` and no `cast`. No change to mypy or ruff configuration. No
runtime behaviour change. If any error cannot be cleared within these constraints, stop and report
it. Do not widen the fix to get round it.

**F1 — `bzk/ontology/invariants.py` l.646.**
- Change `by_rel: dict[str, list[Edge]]` to `by_rel: dict[str | None, list[Edge]]`.
- This is exact. An edge with no `type` is grouped under `None` today, and the reads at l.658 and
  l.688 pass a `str`, so they never reach that group.
- Do **not** change l.648 to `edge["type"]`. That would raise `KeyError` where today the edge is
  grouped and ignored, which is a behaviour change.

**F2 — `tests/test_invariants.py` l.510.**
- Change it to `edges.append(e("USED", str(analysis["id"]), second))`.
- Leave `_curation_change_set`'s return type alone. Other callers depend on it.

**F3 — `tests/test_anchor_recompute_dryrun.py`.**
1. Replace l.20–24 (the module-level `SPEC` and the `type: ignore[union-attr]`) with a
   `_load() -> ModuleType`.
   - Follow `tests/test_survey_ip_tables.py` l.17–23 line for line, **except** the
     `sys.modules[spec.name] = module` line.
   - Leave that line out. The current code does not register the module, so adding it would change
     global state.
   - Then add `dry = _load()`.
   - This removes one existing `type: ignore`.
2. Annotate:
   - `_fresh() -> None`;
   - `_record() -> tuple[list[Node], list[Edge]]`, importing both from `bzk.ontology.invariants`;
   - each of the four tests `-> None`.
3. Replace `dry.CHANGE_SETS = 0` with `vars(dry)["CHANGE_SETS"] = 0`.
   - The reviewer measured that the plain assignment still fails `[attr-defined]` once `dry` is
     typed as `ModuleType`.
   - `vars(dry)` is the module's globals. These are what `classify`'s `global CHANGE_SETS` reads
     (`walk/anchor_recompute_dryrun.py` l.68, l.79–80), so the reset behaves exactly as before.

Imports go where ruff's isort places them. Do not reorder anything else.

## 3. Pre-registration

**These predictions are not independent.** The reviewer applied F1–F3 in a scratch clone of
`9cf9892` and ran every check below. Read them as a test of whether this prompt reproduces that
run, not as a prediction from first principles.

| Check (target as stated) | Before (at `9cf9892`) | After, predicted |
|---|---|---|
| `uv run mypy bzk tests` | 14 errors in 3 files | `Success: no issues found in 117 source files` |
| `uv run pytest` (full suite) | 881 passed, 14 skipped | **881 passed, 14 skipped**: no test added or removed |
| `uv run pytest tests/test_schema.py` | 20 passed | 20 passed |
| `uv run ruff check bzk tests` | All checks passed | All checks passed |
| `uv run ruff format --check bzk tests` | 117 files already formatted | 117 files already formatted |
| `grep -rn "type: ignore" bzk tests --include=*.py \| wc -l` | 8 | **7** (F3.1 removes one) |
| `tests/test_tautology_sweep.py` `sweep()`: modules, asserts | 54, 2,044 | **54, 2,045**: `_load`'s `assert` is counted |
| `git diff --stat` against `9cf9892`'s tree, prompt excluded | — | exactly the three files named above |

To read the sweep figure, run:
`uv run python -c "import sys; sys.path.insert(0, 'tests'); import test_tautology_sweep as m; _, mo, a = m.sweep(); print(mo, a)"`

The +1 is expected. The stale floor at l.1916 is a carried defect and stays untouched.

**If any "After" figure differs, stop and report the difference.** Do not adjust the code until it
matches.

## 4. Record, commit, report

- **Commit.** One commit containing the three files, with this message:
  `TYPES: clear the mypy regression from 856c3d1/819fe7d (prompt 26): by_rel keyed str | None, dry-run test typed and loaded via _load, one type: ignore removed; mypy bzk tests clean; 881 passed`
  Fast-forward `main`, as in prompt 24.
- **Checks.** Run every check in §3's table, each with its target and its actual result.
- **Report:**
  - the commit hash;
  - the receipt answers already given;
  - §3's table with the "After" column filled in from your own run;
  - the full `git diff 9cf9892 -- bzk tests`.

Then stop.

## Out of scope

- Any machine guard that mypy was run, such as a test or a hook. This is worth deciding, because
  this regression survived two commits under report-by-prose. Decide it separately, not here.
- Editing `notes/REVIEWER-HANDOFF-2026-10-03.md`.
- `walk/anchor_recompute_dryrun.py`, and anything outside `bzk tests` that `ruff check .` flags.
  The notebooks are permanently out of scope (`CLAUDE.md` l.96).
- The carried defects:
  - `tests/test_tautology_sweep.py:1916`'s stale floor;
  - `bzk/sources/protein_groups.py:117`'s SD3 label.
- §11 Q7's unstruck heading.
- ADR-0036's D8 and everything after it in the handoff's §5.
- Prompt 22.
