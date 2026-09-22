# Report — H10 attempt 2: the `joint_half` convention, its checks, and D′

**Run at:** 2026-09-22 (the commit date) · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Base:** `8d1bb6e`, a fast-forward of `20e3185` · **Commits:** `36b344a`, `ce70f48`, and this report's own · **Pushed, every push a fast-forward**

**Headline.** Part A adds the `joint_half` sidedness — `joint` with the null count halved, and nothing else — with the fit, the 404 and attempt 1's result written into its docstring. Part B makes attempt 2 a mode of the existing module: four `joint_half` variants, G2a, G2b, check A, readout D′, its own fixture and an `in-sample` label on every result block. **No data run.** Fifteen tests, twenty mutations. E1 held at 833 + 15; E2 held.

**One defect was caught by a test rather than planted.** `anchor_block` gained an `s1_gene_column` key for D′, and that key reached **attempt 1's** `anchor_matrix` block. Attempt 1 has run and its result is committed; a fixture that gains a field is a fixture of something else. The byte-identity test failed, D′ reports the column instead, and the test that caught it was itself rewritten first — see below.

---

## The base check

```
git rev-parse origin/main        → 8d1bb6e
git diff --stat 20e3185..origin/main
  walk/PREREG-PXD018299-H10-attempt2.md | 117 +++++++++++++++++++++++++++++++++
  1 file changed, 117 insertions(+)
git show origin/main:walk/PREREG-PXD018299-H10-attempt2.md | sha256sum
  → 16759b7f2992b629b889f2f6ae5e4191e340f66cf9252deb956a1eb613ff3166
```

The hash is the one the prompt gives and the only changed path is the one it allows. No stop condition fired. Attempt 2's pre-registration, attempt 1's, `walk/RESULT-PXD018299-H10-attempt1.md` and `notes/scripts/diagnose_gate_g.py` were all read in full. **Y1–Y4 appear nowhere in the code**: no constant carries them, no branch consults them, nothing is compared against them. Nothing under `notes/prompts/` was read, written or committed.

---

## Every choice made where the specification was silent

| # | choice | reason |
|---|---|---|
| 1 | **Attempt 1's variant list is pinned to its own two sidedness values**, not read off `perseus_s0.SIDEDNESS`. | That constant just grew to three. Reading attempt 1's eight off it would have made a registered, already-run gate a twelve-variant run, and its committed result a description of something else. |
| 2 | **G2b's majority is applied per direction**: a row counts as higher in WT when a majority of seeds called it *and* put it there. | §3 says *"the number called higher in WT … with the majority-of-seeds call"*, and this is that rule applied to each count. A row called by many seeds in no consistent direction is then in neither count, which is the honest answer for it. `both` is reported rather than assumed away, because ten up and ten down of twenty is arithmetically possible. |
| 3 | **The bands are inclusive at both ends.** | §3 writes them as ranges — [58, 86] and [168, 252] — and a count at an endpoint is inside a range. Asserted at all four endpoints. |
| 4 | **The WT/knockout orientation is asserted by a probe through the same call, and a failure stops the run.** | §3's two bands are asymmetric, so a swapped argument order would exchange them and leave both counts looking plausible — 33 and 145 is a miss either way round. The probe is one synthetic row, higher in every WT column, pushed through `perseus_s0` with the same two arguments in the same order `gate_block` uses. A comment cannot catch a later edit; this does. |
| 5 | **`gate_block` takes `direction` as an opt-in parameter, default off.** | Attempt 2's two counts ride on the same twenty imputations and the same calls the gate already makes, so computing them separately would be a second twenty draws wearing the same seeds' names. Off by default is what keeps attempt 1's block byte-for-byte what it was. |
| 6 | **D′'s "highest-intensity" peptide is the one with the highest mean of its six published log2 values.** | §4 says *"highest-intensity"* and not which summary. The mean over the six uses every column the table publishes; a max or a single column would use one. |
| 7 | **S1's gene-name column is located by content** (`resolve_column`, required fragment `gene`), and its cells are split on `;`. | Its spelling is in no document this repository holds — turn 19's rule for every other S1 column, applied to one more. Splitting on `;` is how MaxQuant and Perseus write multi-symbol cells. |
| 8 | **Matching is exact after splitting, except MAGE.** | §4 declares the one prefix rule, and `prefix_matched_symbols` names it in the output so a reader sees MAGE is the exception rather than that matching is loose. `pxd018299_differential.py`'s recorded reason holds: substring matching lets OAS1 hit OASL — and here, STAT1 hit STAT1B. |
| 9 | **The default cell's per-row support is handed to D′ through the family block and popped before writing.** | D′ needs exactly the support readout A's median produced; recomputing it inside D′ would be a second median over the same draws that could differ from the first. Popping keeps it out of the file. |
| 10 | **`--attempt N` is parsed by hand, defaulting to 1.** | One flag, and the default has to be attempt 1 so `python -m bzk.sources.pxd018299_h10` keeps meaning what it meant when attempt 1 ran. |
| 11 | **`is_tracked` resolves the path relative to the repository root before asking `HEAD`.** | `git cat-file -e HEAD:<path>` takes a repository-relative path; an absolute one names nothing. |
| 12 | **Attempt 2 labels both the top-level block and the readouts block.** | §1 requires the label *"wherever it is reported"*, and a reader looking at the readouts alone should not have to scroll up for it. |
| 13 | **A failed attempt 2 reports `named test not reproduced (attempt 2)`.** | §3's own words, and the suffix keeps it distinguishable from attempt 1's identical sentence in a directory holding both files. |

---

## Each test, its mutation, and the failure message

Twenty mutations over fifteen tests, each confirmed applied **by reading the file back from disk** and reverted; the suite is green after the reverts.

**Part A — `tests/test_perseus_s0.py`, three tests, six mutations.**

| test | mutation | failure |
|---|---|---|
| `joint_half` is `joint` with the null count halved | the **observed** count halved instead of the null | `Not equal to tolerance rtol=1e-12 … Mismatched elements: 6 / 6` |
| `joint_half` halves the mirror floor | the halving dropped (`null_scale=1.0`) | `0.0526… == 0.0263… ± 1e-12` |
| ” (the `joint` line) | `joint` quietly routed through the halving | `0.0263… == 0.0526…` |
| `joint` and `per_side` unchanged | `joint` routed through the halving | `[0.0263…, 0.5, …] == approx([0.0526…, 1.0, …])` |
| ” (the `per_side` line) | `d >= 0` narrowed to `d > 0` on the positive side | `[0.0, nan, …] == approx([0.0, 0.5789…, …])` |

**Part B — `tests/test_pxd018299_h10.py`, twelve tests, fourteen mutations.**

| test | mutation | failure |
|---|---|---|
| attempt 1's variant list and fixture name are untouched | `ATTEMPT_1_SIDEDNESS` gaining `joint_half` | `Left contains 4 more items, first extra item: 'joint_half+random'` |
| ” (the `variants_for` lines) | the two attempts' lists swapped | `Variant(sidedness='joint_half'…) != Variant(sidedness='joint'…)` |
| **attempt 1's fixture is unchanged by attempt 2** | attempt 1's run given the direction split too | digest `d8d19fad…` against `512a0a4f…` |
| ” | **S1's gene column reaching attempt 1's `anchor_matrix`** | digest `d25007f9…` against `512a0a4f…` |
| G2b's bands are inclusive | the WT band's lower end raised by one | `AssertionError: (58, 168)` |
| G2b counts each direction by its own majority | the majority applied to significance rather than to direction | `assert 4 == 2` |
| the direction orientation puts WT above zero | the probe read the wrong way round | `assert False` |
| ” (the whole-protein line) | the gate's up and down counts swapped | `assert 0 >= 1` |
| attempt 2 admits only G2a ∧ G2b ∧ A | **G2b skipped** | `'joint_half+random' not in [...]` |
| ” (attempt 1's rule) | G2b made unconditional | `'joint_half+random_excluding_trivial' != 'joint_half+random'` |
| D′ reports the three tiers separately | the tiers flattened into one | `{'results_curated'} == {'discussion', …}` |
| D′ matches MAGE by prefix and nothing else | every symbol matched by prefix | `assert False is True` — STAT1 hit STAT1B |
| D′ reports an absent symbol as absent | an absent symbol reported as unrecovered | `{'absent_from_s1': False, …} == {'absent_from_s1': True, 'sites': 0}` |
| D′ takes the largest site by intensity | the largest site taken as the weakest | `assert True is False` |
| a staged file does not count as committed | back to `git ls-files --error-unmatch` | `assert True is False` |
| attempt 2 writes its own fixture | `fixture_name_for(2)` returning attempt 1's name | attempt 1's bytes changed at index 1407 |
| ” (the variant-set line) | `registered` pinned to `VARIANTS` | `{'joint+exhaustive_when_small', …} == {'joint_half+…'}` |

### Two tests were rewritten because a mutation showed they proved nothing

1. **The byte-identity test compared the live code against itself.** It ran the synthetic end-to-end twice and diffed the two, which establishes determinism and nothing else — and it **passed** under a mutation that turned the direction split on for everyone, because both runs carried it. It now hashes the canonical fixture and compares against a digest measured in a `git worktree` of `36b344a`, with `PYTHONPATH` pointed at that tree so the worktree's `bzk` was the one imported rather than the editable install's. Rewritten, it immediately caught the real `s1_gene_column` leak.
   - Four fields are excluded from the digest and each is named in the test: `generated_at`, `commit`, `working_tree_clean` and `runtime_seconds` are a run's own identity, and the two synthetic supplements' content hashes move between runs because `openpyxl` stamps a creation time into every `.xlsx` it writes — a property of the test's fixture generator, not of the module.
2. **The attempt-2 end-to-end test could not reach the anchor.** G2b's bands are absolute counts calibrated to 2,438 rows, and a synthetic matrix small enough to run in a test cannot reach 58 of anything, so no variant was ever admitted and D′, the `validation` labels and the whole anchor path went untested. The bands are widened **for that one run**, with the reason in the test, and what the bands themselves do is asserted at their own four endpoints by a separate test.

**One further mutation was discarded as inert and is reported rather than quietly replaced.** Flipping `gate_block`'s `direction` *default* changes nothing, because `main` always passes the value explicitly; the mutation that reaches attempt 1's output is `direction=True` at the call site, and that is the one recorded above.

---

## E1 and E2

**E1 — held.** The base suite was measured here at `8d1bb6e` before anything was written: **833 passed, 14 skipped**. The final suite is **848 passed, 14 skipped**, and this turn adds 15 tests (3 in Part A, 12 in Part B): 833 + 15 = 848, with the skips unmoved at 14.

**E2 — held.** One existing test file changed, and it is the one E2 names: `tests/test_tautology_sweep.py`, with **fourteen classifications** — six from Part A's tests and eight from Part B's — each carrying the mutation that reddens it. Two of Part A's six are recorded as **documentary rather than guarded**, with the reason: `_fdr_at(...) == 1/19` is computed entirely inside the test from its own enumeration and states a property of the hand case, which no mutation to the module reaches; and `half.q_value[argmax] == 1/38` restates one element of the `assert_allclose` two lines above it.

**No assertion in any other existing test changed. No id pin moved. The sweep's floor was not touched**, as the out-of-scope list requires: it reads `modules >= 49 and asserts >= 1693` against a surface of 52 modules and 1,954 asserts, so it passes unchanged.

---

## `CLAUDE.md` point 1 — every check, at its target, at its actual result

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **848 passed, 14 skipped** |
| `pytest tests/test_schema.py` | that module | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed** |
| `ruff format --check` | `bzk tests` | **115 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 115 source files** |

Every command was run under `.venv/bin/python`. The targets are `bzk tests` and not the whole repository: `ruff check .` additionally covers the three notebooks, which are deliberately out of scope permanently and were not run here.

**Point 2 — the change did what it claims, checked directly.** Each of the fifteen tests was made to fail with a named mutation, every mutation confirmed applied by reading the file back, and every one reverted. Two tests were rewritten because a mutation showed them vacuous, and one mutation was discarded as inert and reported. The attempt-2 path was run end to end over synthetic bytes and its output inspected — four `joint_half` variants scored, the direction split present on each, `attempt: 2` and the `in-sample` label on both blocks, D′'s three tiers filled, and `MAGE` correctly reported `absent_from_s1` on a matrix that carries no MAGE symbol.

**Point 3 — what this turn does not cover.**

- **No data run.** G2a's four figures, G2b's two counts, which variants survive check A, the primary variant, readouts A to D and D′ are all unknown. The instrument exists; what it says does not.
- **The convention is unverified, and every attempt-2 result says so.** `joint_half` was fitted on one number at one seed, from the same table G2a scores against. The Perseus plugin source returned 404 on 2026-09-22. `validation: "in-sample; independent confirmation pending"` is on every result block, and nothing in this turn changes that status.
- **G2b and check A are the only unfitted constraints**, and neither is independent of the deposit: both are computed on the same two files the fit came from. What would make attempt 2 independent — a second published Perseus output with its parameters stated, the code, or the authors — none of it is in hand.
- **`tests/fixtures/pxd018299_h10_attempt2.json` is not committed**, so nothing guards its shape against the generator. That is a turn which needs the fixture to exist first.
- **The end-to-end test establishes the seam, not the figures.** Its Table 3 is generated from one variant's own majority calls so the gate passes, and G2b's bands are widened for it. Neither is a claim about the real run.
- **D′'s tiers are the pre-registration's lists, typed in.** The two `results, not curated` symbols and the nine `discussion` ones are §4's; only the curated fourteen are read from a committed fixture. If §4's lists are wrong, this reproduces them.
- **Attempt 1's committed fixture and result are untouched**, and nothing here re-runs or re-scores them.
- **The third deposit, both pre-registrations and the tautology floor are untouched**, as the out-of-scope list requires.

**Point 4 — instructions dropped or partially done.** None. Parts A and B, their tests, the `--attempt` flag, the staged-file fix and the task list were all done. The one addition the brief did not ask for is `ATTEMPT_1_SIDEDNESS`: widening `perseus_s0.SIDEDNESS` silently widened attempt 1's variant list, and pinning it is what makes *"leave `joint` and `per_side` untouched"* true of the caller as well as of the test.

---

## Commits and the push

| commit | subject |
|---|---|
| `36b344a` | `stats:` the `joint_half` sidedness, fitted and declared as fitted |
| `ce70f48` | `sources:` H10 attempt 2 — the four `joint_half` variants, G2b, D′, and the staged-file fix |
| this report | committed alone |

`main` was pushed fast-forward: **`8d1bb6e..ce70f48`**. No branch was force-pushed, and no pushed commit was amended or rebased.
