# Report — H10 attempt 3: the principled primary, and the typical-draw check

**Run at:** 2026-09-22 (the commit date) · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Base:** `e13f06c`, a fast-forward of `9b69bc1` · **Commits:** `107ed6a` and this report's own · **Pushed, every push a fast-forward**

**Headline.** Part B makes attempt 3 a third mode of `bzk/sources/pxd018299_h10.py`: two variants with the primary fixed by §2 rather than chosen by a score, check A strengthened to §3's median over twenty seeds, a rerun-consistency stop against attempt 2's committed fixture, every readout for both variants, the verdict from the primary alone, and two flags on every result block. **No data run.** Thirteen tests — twelve new, one extended — and twenty-three mutations. E1 held at 848 + 12. E2 held.

**Two mutations left a test green and are reported rather than swapped.** One is a wrong-reason failure (`FileNotFoundError` instead of a byte comparison); the other is inert at synthetic scale and is the reason a new non-degeneracy assertion was added. Both are below.

---

## The base check

```
git rev-parse origin/main                                  → e13f06c
git diff --stat 9b69bc1 HEAD -- . ':!notes/prompts'
  tests/fixtures/pxd018299_h10_attempt2.json | 312197 +++++
  walk/PREREG-PXD018299-H10-attempt3.md      |    113 +
  walk/RESULT-PXD018299-H10-attempt2.md      |    170 +
  3 files changed, 312480 insertions(+)
sha256sum walk/PREREG-PXD018299-H10-attempt3.md
  → f83c6d08931ef42467494f007febf137a2360112c699188569627fc07b9ae506
```

The hash is the one the prompt gives, and the only changed paths are the three it allows. `origin/main` and `HEAD` were the same commit. No stop condition fired. Attempt 3's pre-registration, attempt 2's, attempt 1's and both committed RESULT files were read in full. **Z1–Z6 appear nowhere in the code**: no constant carries them, no branch consults them, nothing is compared against them. Nothing under `notes/prompts/` was read, written or committed.

---

## Every choice made where the specification was silent

| # | choice | reason |
|---|---|---|
| 1 | **Check A counts claims, not rows**, and `check_a` (attempts 1 and 2) is left exactly as it was. | §3 says *"the per-seed count of claims with q ≤ 0.01 and d > 0"*. Attempts 1 and 2 asked `.any()` over every row of the matrix, which is a superset of the claims. The two agree on whether anything is reached and disagree on how much, and only attempt 3 needs the amount — so it is a second function, not an edit to the first. |
| 2 | **Every seed runs; there is no short-circuit**, and `reached_under_any_seed` is reported beside the median. | A median needs all twenty counts, so the short-circuit could not be kept. Reporting the old rule beside the new one makes the *difference* legible rather than only its consequence — which is the whole reason a third attempt exists. |
| 3 | **Every seed's count is in the file**, not only the median. | §3's own words. A median of 1 over `[0, 0, 1, 40, …]` and one over `[1, 1, 1, 1, …]` are different facts about a variant. |
| 4 | **Rerun consistency compares six integers per variant** — both numerators, both denominators and the two direction counts — and not the shares or the `passes` flags. | A share is a quotient: 83/83 and 1/1 are both a precision of 1.00. A test plants exactly that pair and would pass if shares were compared. |
| 5 | **A variant absent from attempt 2's fixture is itself a mismatch**, named `reason: "absent"`. | Attempt 2 ran four variants and attempt 3 runs two of them, so this should never fire. It fires if the committed fixture is not the run attempt 3 thinks it is, which is precisely the condition §3's stop exists for. |
| 6 | **The consistency check runs before check A and before anything else is computed.** | §3 calls a difference an instrument fault. Twenty seeds of imputation and permutation computed against an instrument already known to have moved is twenty minutes spent on a number that cannot be reported. |
| 7 | **Both flags ride on the top-level block *and* on each readout block.** | §4 says *"every result"*. A reader looking at the primary's readouts alone should not have to scroll up to learn which matrix produced them. |
| 8 | **Each variant is run as its own primary** — `family_block_for(variants=[variant], primary=variant)` — and the `secondary_variants` key is popped from each block. | §4 requires both *"in full"*. `family_block_for` reports every other admitted variant's readout A under `secondary_variants`, which here would always be empty; an empty map would read as *"no secondary was admitted"*, which is a different statement from *"the two are siblings"*. |
| 9 | **`disclosed` is a parameter of `family_block_for` defaulting to `False`.** | §1's label belongs to attempt 3 alone. A default of `True` changes attempt 1's and attempt 2's fixtures, which the digest test catches — and that is the recorded mutation for it. |
| 10 | **An unadmitted primary still writes the checks that did run**, and returns 1. | §3 says the result is *"H10 not tested (attempt 3)"*. That is a finding, not a blank: the consistency check and all twenty seeds of check A are in the file, and only the family is absent. |
| 11 | **`verdict_read_from: "primary"` is written into the file.** | §4's rule is a property of the result and will be read years after the sentence that set it. |
| 12 | **`primary_variant`, `primary_admitted` and `secondary_variant` are recorded whether or not the primary was admitted**, and `instrument_fault` is written `false` on the normal path too. | A field that appears only on success makes its absence ambiguous — unrun, or run and clean. |
| 13 | **`CHECK_A_MEDIAN_MINIMUM = 1` is a named constant**, compared with `>=` against a float median. | §3's threshold is a registered number and belongs where a reader looks for one. `np.median` returns a float at even counts, so the comparison is float-to-int by construction. |
| 14 | **The stale docstring correction records what it was and why it was wrong.** | *(Comment only; the two digests below are what prove it changed no output.)* |

---

## Each test, its mutation, and the failure message

Twenty-three mutations over thirteen tests, each confirmed applied **by reading the file back from disk** and reverted; a read-back against the pristine text follows every revert, and the suite is green after them.

| test | mutation | failure |
|---|---|---|
| **attempts 1 and 2 are unchanged by attempt 3** | `family_block_for`'s `disclosed` defaulting `True` | digest `1f2f53ff…` against `512a0a4f…` |
| ” (the **attempt 2** line) | attempt 2's header gaining attempt 3's `matrix` flag | digest `c98fc257…` against `eb593fe7…`, **attempt 1's line still green** |
| both variants get full readouts, verdict from the primary | only the primary in the readout loop | `assert {'primary'} == {'primary', 'secondary'}` |
| ” (the exit-status line) | `_attempt_3`'s closing `return 0` returned 1 | `assert 1 == 0` |
| the verdict reads the primary and not the secondary | `readouts["secondary"]["readout_b"]["verdict"]` | `assert 'absent' == 'recurs'` |
| readout A is labelled disclosed before the run | `disclosed=False` at the call | `KeyError: 'disclosed_before_run'` |
| every result block carries both flags | `**flags` dropped from the readout block | `KeyError: 'validation'` |
| attempt 3 never writes the earlier fixture paths | attempt 3 also writing its block under `FIXTURE_NAME_ATTEMPT_2` | bytes differ at index 99 |
| the primary is fixed and never scored | the primary chosen as `max(…, key=f1)` | `'joint_half+exhaustive_excluding_trivial' == 'joint_half+random_excluding_trivial'` |
| check A uses the median and not any seed | `reached` computed as `any(c > 0 …)` | `assert True is False` |
| ” (the median line) | the median reported as the mean | `assert 0.05 == 0.0` |
| ” (the non-degeneracy line) | every seed's count replaced by the maximum | `assert 1 > 1 … where {1} = set([1, 1, 1, …])` |
| check A reports every seed's count | `counts_by_seed` truncated to `seed_counts[:1]` | `assert 1 == 3` |
| ” (the median-of-the-counts line) | the reported counts one higher than the counts summarised | `assert 4.0 == 5.0` |
| a G2 mismatch stops the run as an instrument fault | `consistent` hard-coded `True` | `assert 0 == 1` |
| the consistency check compares counts, not shares | the six integers replaced by the two shares | only `recall_share` differs; **precision 83/83 against 1/1 invisible** |
| a variant absent from the earlier fixture is a mismatch | the `absent` difference not appended | `assert True is False` |
| an unadmitted primary leaves H10 not tested | that branch writing a verdict and returning 0 | `assert 0 == 1` |
| ” (the `check_a` set line) | the reported `check_a` narrowed to the primary's entry | `Extra items in the right set: 'joint_half+exhaustive_excluding_trivial'` |

### Two mutations did not fail for the reason the test claims, and are recorded

1. **`name = FIXTURE_NAME_ATTEMPT_2` in place of `fixture_name_for(3)`** — the obvious mutation for *"never writes the earlier fixture paths"* — reddens the test with `FileNotFoundError` on attempt 3's own output, from inside the test's own helper, **before the byte comparison is reached**. It proves a path changed; it does not exercise the claim. The recorded mutation writes attempt 3's block to attempt 2's path *in addition* to its own, which leaves the run intact and reddens the byte comparison itself.
2. **Reporting the mean in place of the median leaves `test_check_a_reports_every_seeds_count` green.** At synthetic scale every seed returns the same count, and on a constant list the mean, the median and the maximum are one number. This is the third time this suite has hit that shape — pooled against Welch at equal group sizes (turn 16), and the harmonic against the arithmetic mean at precision == recall (turn 18). **It is machine-checked now rather than noted:** `test_check_a_uses_the_median_over_seeds_and_not_any_seed` asserts `len(set(counts_by_seed)) > 1` before it asserts anything about the median, so a stub that flattened its own counts fails on that line — which a mutation confirms. The mean mutation does redden that test (`assert 0.05 == 0.0`), so the median is guarded; it is guarded **there** and not in the seeds-count test, and the comment in each says so.

### The two failing tests that were a monkeypatch-scope defect, not a code defect

`test_the_verdict_reads_the_primary_and_not_the_secondary` and `test_the_attempt_3_primary_is_fixed_and_never_scored` both failed with `StopIteration` inside **attempt 1's** `main`. Their stubs were installed before the helper ran attempts 1 and 2, so the `primary_variant` spy returned an attempt-3 variant name into attempt 1's eight-variant list. `_run_attempt_3` now takes a `patch` hook called after the two earlier runs and before attempt 3, and the reason is in its docstring: the earlier attempts are the unstubbed instrument attempt 3 is measured against.

---

## E1 and E2

**E1 — held.** The base suite was 848 passed and 14 skipped at `e13f06c`. The final suite is **860 passed, 14 skipped**. This turn adds twelve tests and replaces one with an extended version of itself: 848 + 12 = 860, skips unmoved at 14.

**E2 — held.** Two existing test files changed, and they are the two E2 names:

- `tests/test_pxd018299_h10.py` — only `test_attempt_1s_fixture_is_unchanged_by_attempt_2`, which becomes `test_attempts_1_and_2_are_unchanged_by_attempt_3` and pins attempt 2's canonical fixture beside attempt 1's. `ATTEMPT_2_DIGEST` was measured at `e13f06c` in a `git worktree` with `PYTHONPATH` pointed at that tree, the same way `ATTEMPT_1_DIGEST` was, and with G2b's bands widened exactly as the test widens them — a digest of a run that stopped at the gate would pin the gate and nothing after it. `ATTEMPT_1_DIGEST` was re-measured unchanged at the same commit. No other assertion in that file changed.
- `tests/test_tautology_sweep.py` — **eight classifications**, all `PINNED`, each with the mutation that reddens it, plus two counts moved (`code == 0` 1 → 4, `code == 1` 1 → 3) and one expression removed because attempt 3 replaced it. **The `gone` half of that assertion caught an over-removal in the same turn**: `attempt_1_path.read_bytes() == before` was deleted with it and had to be restored, because attempt 2's own single-fixture test still carries that line. The note records that rather than hiding it.

**The sweep's floor was not touched**, as the out-of-scope list requires: it still reads `modules >= 49 and asserts >= 1693` and passes unchanged. **`perseus_s0` was not touched. No pre-registration was touched. No variant beyond §2's two exists in the code.**

---

## `CLAUDE.md` point 1 — every check, at its target, at its actual result

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **860 passed, 14 skipped** |
| `pytest tests/test_schema.py` | that module | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed!** |
| `ruff format --check` | `bzk tests` | **115 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 115 source files** |

Every command was run under `.venv/bin/python`. The targets are `bzk tests` and not the whole repository: `ruff check .` additionally covers the three notebooks, which are deliberately out of scope permanently and were **not** run here.

**Point 2 — the change did what it claims, checked directly.** Every one of the thirteen tests was made to fail with a named mutation; every mutation was confirmed applied by reading the file back from disk, and every one was reverted with a read-back against the pristine text. Two mutations that did not fail for the test's reason are reported above rather than swapped out, and one of them produced a new assertion. Beyond the suite, the attempt-3 path was run end to end over synthetic bytes and its output inspected: `consistency: true` and `instrument_fault: false`, check A reporting a count for every seed with both variants admitted, both readout blocks carrying `readout_a` (with `disclosed_before_run: true`), `readout_b`, `readout_c`, `readout_d` and `readout_d_prime`, `h10` equal to the primary's verdict, and `verdict_read_from: "primary"`.

**Point 3 — what this turn does not cover.**

- **No data run.** Whether either variant clears the median, what the primary's verdict is, the isolations, the family categories, the whole-table count, D and D′ — none of it is known. The instrument exists; what it says does not.
- **Readout A is not a test for these variants.** §1 discloses 725 and 724 of 791, so Z1 and readout A are reported and not scored. The tests attempt 3 can still make are B, the family categories, the whole-table count, and D and D′.
- **`joint_half` is still unvalidated.** It was fitted on one number at one seed, from the table G2a scores against; the Perseus plugin source returned 404 on 2026-09-22. `validation: "in-sample; independent confirmation pending"` is on every block and nothing here changes that.
- **The rerun-consistency check is exercised against a *synthetic* attempt-2 fixture.** In the real run it reads the committed 5.1 MB file; in the suite it reads whatever the synthetic attempt-2 run just wrote. What is tested is that a one-count difference stops the run, not that the committed file's numbers are what attempt 3 will recompute.
- **The two digests pin synthetic runs.** They establish that attempt 3 changed nothing in attempts 1 and 2's *code paths*; they say nothing about the committed real fixtures, which this container cannot regenerate.
- **The constant-counts class is closed for the median and no wider.** The non-degeneracy assertion covers `check_a_typical`'s summary. The general rule — *a test of a summary statistic over data where every summary coincides is a test of nothing* — is not machine-checkable as stated, and is recorded in the two test docstrings that carry an instance of it rather than as a fourth note nobody will read.
- **Nothing tests the `--attempt 3` flag's parsing beyond the tests calling `main` with it.** The hand-rolled parser is turn 20's and is unchanged.
- **The stopping rule is prose.** §5 says attempt 3 is the last attempt on this deposit without new independent information. No code enforces that, and none was asked for.

**Point 4 — instructions dropped or partially done.** None. Part B, the two variants, the recomputed G2a/G2b with its stop, check A as the median, every readout for both variants, the verdict from the primary, both flags, the attempt-3 fixture path, the docstring fix, the seven required tests (all thirteen, each seen to fail first), E1, E2, the five checks, the commit, the push and this report were all done. Two things were added that the brief did not name: the `patch` hook in `_run_attempt_3`, which the monkeypatch-scope defect required, and the non-degeneracy assertion, which point 3's own standard required once the inert mutation had been found.

---

## Commits and the push

| commit | subject |
|---|---|
| `107ed6a` | `sources:` H10 attempt 3 — the principled primary, check A on the typical draw, and the rerun-consistency stop |
| this report | committed alone |

`main` was pushed fast-forward: **`e13f06c..107ed6a`**, and the harness branch `claude/eloquent-fermat-or15bq` was fast-forwarded to the same commit. No branch was force-pushed, and no pushed commit was amended or rebased.
