# Report — the anchor under its named test: gate G, check A, and H10

**Run at:** 2026-09-20 *(corrected 2026-09-20: first recorded as 2026-09-22, which does not match the commit date)* · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Base:** `0e4dc6b`, a fast-forward of `2eb8445` · **Commits:** `388c757`, `e368326`, and this report's own · **Pushed, every push a fast-forward**

**Headline.** Part A adds the two missing permutation schemes; Part B implements the whole pre-registration — gate G, check A, the two §3 checks, the 360-member paired family and readouts A to D. **No data run, on any deposit.** Twenty-eight tests, thirty-one mutations. E1 held at 805 + 28; **E2 held exactly as written** — `tests/test_perseus_s0.py`'s P1 comment and the sweep classifications, and nothing else.

**One finding worth reading before the gate runs.** Turn 18's report said a 19-relabelling null "cannot support an FDR of 0.01". **That is wrong, and the correction is the reason two of §4's eight variants exist.** The floor is the *mirror*, not the draw count: under `joint`, the mirror relabelling reproduces every observed `|d|` exactly, so q is floored at one over the number of relabellings whatever the data say. Drop the mirror and the same-sized null reaches q = 0. The P1 comment is corrected in place.

---

## The base check

```
git rev-parse origin/main        → 0e4dc6b
git diff --stat 2eb8445..origin/main
  walk/PREREG-PXD018299-H10.md | 213 +++++++++++++++++++++++++++++++++++++++++
  1 file changed, 213 insertions(+)
git show origin/main:walk/PREREG-PXD018299-H10.md | sha256sum
  → 68147bea38fc04f1d2eaf0fa3279d21d7ba643462103fc233b4ed3ce33ec81d8
```

The hash is the one the prompt gives and the only changed path is the one it allows. No stop condition fired. The pre-registration was read in full, along with `HYPOTHESIS.md` v8's H10 amendment, `bzk/stats/perseus_s0.py` and its tests, turn 16's reconstruction module, `bzk/sources/pxd018299_differential.py` and the published-cascade fixture. Nothing under `notes/prompts/` was read, written or committed.

---

## Part A — what the mirror costs, measured

The reviewer's simulation (1,375 rows, 3 against 3, 200 planted +4 SD effects) had `joint` with the mirror call **none** at FDR 0.01 against **69** for `per_side` exhaustive. **Re-run here at seed 0 on the same shape, the mechanism reproduces exactly and the sizes do not:**

| variant | draws | called of 200 | smallest q |
|---|---|---|---|
| `joint` + `exhaustive_when_small` (mirror kept) | 19 | **0** | 0.0526 = 1/19 |
| `joint` + `exhaustive_excluding_trivial` | 18 | 1 | 0.0 |
| `per_side` + `exhaustive_when_small` | 19 | 46 | 0.0 |
| `per_side` + `exhaustive_excluding_trivial` | 18 | 46 | 0.0 |

So the floor is the mirror's and not the enumeration's size, and the reviewer's 69 is that run's figure, not this one's — the docstring says which is whose. A third thing the table shows and the docstring carries: `joint` **without** the mirror still called only 1 of 200, because counting `|d|` doubles the null relative to a one-sided count. The mirror makes `joint` impossible at this design; the two-tailed count makes it weak.

---

## Every choice made where the pre-registration was silent

| # | choice | reason |
|---|---|---|
| 1 | **`exhaustive_excluding_trivial` falls back to `random_excluding_trivial` above the cut**, and the cut is on the draws that would run (`C − trivial`). | §4 names the scheme and not its behaviour at 12 samples, where C(12,6) = 924. The symmetry with `exhaustive_when_small` is the only reading under which the four schemes are two pairs; the alternative enumerates 184,756 relabellings at 10 against 10. Reported as `scheme_used`, never silent. |
| 2 | **`random_excluding_trivial` keeps drawing until it has `randomisations` non-trivial draws.** | The count reported is then the count that ran. Filtering after drawing would report a number larger than the null actually used. |
| 3 | **The mirror is dropped only where it exists.** At unequal group sizes the two exhaustive schemes coincide, and the count says `C − 1` rather than `C − 2`. | There is no relabelling that hands A exactly B's columns when the counts differ; dropping "the mirror" there would drop a real relabelling. |
| 4 | **G's majority is computed as a majority of the seeds that ran**, not as the literal 10. | §4 fixes *"at least 10 of the 20 seeds"*, and at twenty seeds the two readings are the same number — asserted. The choice is for the tests: ten of three cannot be met, and a threshold nothing can reach is not a smaller version of §4's rule. |
| 5 | **The eight variants are ordered sidedness-outermost, scheme-inner**, as §4's bullets list them. | §4's tie-break is *"the earlier variant in the list above"*, so the order is load-bearing and is the one the section prints. The tie-break is positional, never alphabetical. |
| 6 | **A variant whose F1 is undefined cannot be primary.** | A variant that called nothing has no precision. Scoring it zero would rank it against variants whose F1 exists. |
| 7 | **§3's check evaluates all four family × normalisation combinations, then picks by rule**: any meeting the criterion; summed over `___1`; no normalisation over median-subtracted; else summed, unnormalised, flagged `undetermined`. | §3 gives the preferences (*"if both do, the summed columns are used"*) and the fallback but not the traversal. Measuring all four and reporting every fraction makes the pick auditable rather than a first match through an unstated order. |
| 8 | **`undetermined` is recorded as its own value, not as `none`.** | The run used no normalisation either way; what differs is whether that was *established*. A fixture reading `none` would assert a finding the check did not make. |
| 9 | **The medians for the normalised candidate are taken over the population**, not over the 798. | §3 says *"with medians over the population"*; a median over the claim set would be a median of the rows the paper selected rather than of the matrix it normalised. |
| 10 | **Readout A's "median over its 20 draws" includes exactly 10 of 20.** | The median of twenty booleans at 10 is 0.5, and the rule includes it — the same majority §4 states for the gate, so the two readouts do not disagree about what a median of twenty booleans means. |
| 11 | **The verdict's boundaries carry a 1e-9 slack**, as turn 17 established. | These shares are rationals over claim counts; a registered direction decided by binary floating point at its own boundary is not the registered direction. |
| 12 | **The 14 targets come from the committed targets fixture's `gene` list, and match claims by `gene_names` split on `;`, exact.** | §6 D names the targets and not the mapping. `pxd018299_differential.py` already carries the same fourteen; reading the fixture avoids a third copy, and exact matching is that module's own recorded rule — substring matching lets OAS1 hit OASL. |
| 13 | **The fixture stores every claim's support for every member as 0/1**, not a summary. | The prompt allows a compact equivalent; the raw matrix is 798 × 360 and makes each readout recomputable without re-running. Which is stored is said in the file. |
| 14 | **`is_tracked` returns `False` where git cannot answer.** | §6 A turns on *committed*. A run outside a work tree cannot establish that, and treating an unanswerable question as a yes would make readout A's primary depend on a file nobody else can see. |
| 15 | **The author file's `scheme` is validated against `perseus_s0`'s four**, and every parameter it omits takes the registered default. | The pre-registration lists the admissible parameters and says omitted ones default; it does not say what an unreadable value does. Refusing by name is the same rule the unknown-key check applies. |

**§7's expectations are not inputs.** X1 to X8 appear nowhere in either module: no constant carries them, no branch consults them, nothing is compared against them.

---

## Each test, its mutation, and the failure message

**Part A — `tests/test_perseus_s0.py`, three new tests, six mutations.**

| test | mutation | failure |
|---|---|---|
| `joint` reaches 0.01 only once the mirror is excluded | the mirror kept (`mirror = None`) | `0.0526… == 0.0 ± 1e-12` |
| ” (for the with-mirror line) | the mirror dropped from the scheme that keeps it | `0.0 == 0.0526…` |
| the exhaustive-excluding scheme runs 18 at 3 against 3 | the exhaustive branch skipping only the identity | `assert 19 == 18` |
| ” (for the unequal-size line) | the mirror misread as the **last** `n_a` columns | `assert 54 == 55` |
| `random_excluding_trivial` never draws a trivial relabelling | the filter applied after drawing rather than during | `frozenset({0, 1, 2}) not in [...]` is false |
| ” (for the label and count lines) | the branch labelled `"random"`; one draw fewer | `'random' == 'random_excluding_trivial'`; `399 == 400` |

**Part B — `tests/test_pxd018299_h10.py`, twenty-five tests, twenty-five mutations.**

| test | mutation | failure |
|---|---|---|
| the check takes no normalisation where S1 equals log2 | the criterion made unreachable | `'undetermined' == 'none'` |
| the check takes median subtraction where that matches | the median candidate never formed | `'undetermined' == 'median_subtracted'` |
| the check prefers summed where both meet it | the families preferred in the other order | `'multiplicity_1' == 'summed'` |
| the check takes `___1` where only it matches | only the summed family considered | `'summed' == 'multiplicity_1'` |
| the check falls back to `undetermined` | the fallback reported as an established `none` | `'none' == 'undetermined'` |
| the criterion is 99% of the deposit-measured cells | the criterion lowered to 98% | `'none' == 'undetermined'` |
| the valid-value rule is the strictest retaining every row | **the loosest candidate taken** | `assert 1 == 2` |
| the fallback takes the most and says so | the fallback taking the fewest | `assert 3 == 1` |
| the primary is the highest G F1 | the lowest F1 taken | `'joint+random' == 'joint+random_excluding_trivial'` |
| a tie goes to the earlier variant | the tie broken alphabetically | `'joint+exhaustive_…' == 'joint+random_excluding_trivial'` |
| an undefined F1 cannot be primary | an undefined F1 scored as zero | `'joint+random' is None` is false |
| admission needs both G and A | admission ignoring check A | `'joint+random' != 'joint+random_excluding_trivial'` |
| the gate majority is ten of twenty | the majority floored rather than rounded up | `assert 1 == 2` at three seeds |
| gate metrics are precision, recall and their harmonic mean | F1 as the arithmetic mean | `0.41666… == 0.4 ± 4e-07` |
| the verdict at the registered boundaries | the recurs boundary made exclusive | `'indeterminate' == 'recurs'` |
| instability is support that differs across draws | instability as "supported at all" | `[True, False, True] == [False, False, True]` |
| a member uses its own seed for both random steps | the permutation seed pinned at 0 | `('permutation', 0) != ('permutation', 7)` |
| support is `q ≤ 0.01` **and** `d > 0` | support dropping the direction | `not np.True_` — the up-in-WT rows called |
| **`main` runs the gate, the check and the readouts** | contaminants dropped with the decoys | `assert 6 == 7` |
| **no variant admitted means no anchor run** | the anchor run going ahead with none admitted | `assert 0 == 1` |
| an unknown key refuses by name | the unknown-key refusal removed | `Failed: DID NOT RAISE H10Error` |
| the author file needs its provenance | `date_received` dropped from the required keys | `Regex pattern did not match … Actual: "… is missing ['source']"` |
| an absent file is `None`, an untracked one is not primary | every file reported as tracked | `assert True is False` |
| ” (for the defaulting line) | an omitted `scope` not defaulting | `Member(…'whole_matrix'…) == Member(…'per_sample'…)` |
| the author configuration moves readout A only when tracked | made primary whether tracked or not | `'author_configuration' == 'default_cell'` |
| the verdict is identical with and without the file | readout B's share deferring to the author file | `plain['readout_b'] == authored['readout_b']` is false |

### Three tests exist only because a mutation found a hole

1. **F1's asymmetric case.** The arithmetic-mean mutation left the metrics test green: the case had precision and recall both at 2/3, and at `precision == recall` the harmonic and arithmetic means are the same number. A second case at 1/2 and 1/3 was added, where they are 0.4 and 0.4167.
2. **The gate's majority.** The first end-to-end run failed with *0 of 8 variants pass* — because `GATE_MAJORITY` was the literal 10 and the test runs three seeds. §4's *"at least 10 of the 20"* is a majority; computing it as one makes a reduced-seed run mean the same thing, and the identity at twenty seeds is asserted so the generalisation cannot quietly loosen.
3. **Readout B's stub.** The verdict-identity test was vacuous: a synthetic matrix small enough to run in a test is perfectly stable, so readout B's share was 0 either way and "identical" was true of two zeroes. The support pattern is now stubbed so one of two imputed claims flips, the share is 0.5 and the verdict is `recurs` — and only then does the comparison mean anything. What computes support is covered separately against the real arithmetic.

**Two further notes on mutation quality.** The end-to-end test's first mutation (the reverse-decoy filter inverted) failed with the claim-join refusal rather than a clean assertion, so it was replaced with *contaminants dropped with the decoys* — and a contaminant row was added to the synthetic deposit, so §2's "contaminants are kept" rule is now exercised rather than assumed. The no-anchor-run test's first mutation was inert (admission ignoring the gate changes nothing when attainability was never computed) and was replaced with *the primary falling back to the first variant*, which is what "run anyway" actually looks like here.

---

## The output's shape

`tests/fixtures/pxd018299_h10.json`, written by `main` and **not committed by this turn** — this container cannot produce it.

```
dataset, registration, anchor_run,
anchor_file / anchor_content_hash, anchor_published_file / …_content_hash,
gate_file / gate_content_hash, gate_published_file / …_content_hash,
author_parameters_present, author_parameters_tracked, note, generated_by,
generated_under { generated_at, commit, working_tree_clean, python, numpy,
                  anchor_s0, anchor_fdr, randomisations }
gate_g {
  parameters { s0, fdr, randomisations, seeds, majority_of_seeds, cell }
  complete_case_proteins, complete_case_published_calls, table_3_call_values,
  weakly_informative, thresholds,
  variants { <each of 8> { precision, recall, f1, called_complete_case, passes } },
  passes
}
check_a { <each of 8> { reached, seed } }
admitted_variants[], primary_variant
anchor_matrix {
  population_rows, rows_reaching_the_test, published_rows, exposure,
  claims_lost_to_the_valid_value_rule[],
  column_family, column_names, normalisation, normalisation_undetermined,
  match_fractions { "<family>+<normalisation>": {numerator, denominator, share} },
  valid_value_rule { candidates { "3"|"2"|"1" }, taken, retains_every_claim },
  published_draw { rule, per_sample { <column> {n, mean, sd, observed_*, downshift, width} },
                   whole_matrix }
}
readouts {                                   # absent where no variant is admitted
  primary_variant, members, default_cell_members,
  readout_a { default_cell {supported, of}, primary, compared_with,
              author_configuration? {parameters, source, date_received,
                                     tracked_in_git, supported, of} }
  readout_b { conditional_on_imputation, verdict, over_all_claims,
              isolations { permutation_fixed, imputation_fixed },
              family_categories { durable, underdetermined, unsupported },
              whole_table_supported_default_cell }
  readout_c  = anchor_matrix.published_draw
  readout_d { <each of the 14 symbols> { claims, supported } }
  secondary_variants { <name> { supported, of } }
  per_claim_support { note, members[], rows[] { deposit_id, published_row, gene_names,
                                                row_carries_an_imputed_cell, support[] } }
}
runtime_seconds
```

A gate that admits nothing writes everything above `readouts`, sets `anchor_run: false` and `result: "named test not reproduced"`, and `main` returns 1.

---

## The runtime

**Measured here, at real dimensions, on synthetic matrices:**

| operation | size | measured |
|---|---|---|
| one `perseus_s0` call, gate scale | 2,438 × 12, 250 permutations, 6 v 6 | **0.06–0.07 s** |
| one imputation, gate scale | 2,438 × 12 | 0.001 s |
| one `perseus_s0` call, anchor scale, `random` | 2,300 × 6, 250 permutations, 3 v 3 | **0.05 s** |
| one `perseus_s0` call, anchor scale, exhaustive | 2,300 × 6, **18** permutations | **< 0.01 s** |
| the whole synthetic end-to-end `main` | 24 proteins, 8 rows, 8 variants × 3 seeds | **0.18 s** |

**The estimate for the real run**, from those:

- **Gate G:** 8 variants × 20 seeds × 0.065 s ≈ **11 s**, plus 20 imputations (0.02 s).
- **Check A:** at most 8 × 20 × 0.05 s ≈ **8 s**, and less in practice — a variant stops being tested once it has reached.
- **The family, per variant:** 360 members × 0.05 s ≈ **18 s** if the primary is a `random` scheme, or ≈ **1.5 s** if it is an exhaustive one, since at 3 against 3 those run 18 or 19 draws rather than 250. Plus the two isolations (20 members each) and each secondary variant's default cell (20 members each).
- **Total: well under a minute**, and at worst two or three if all eight variants are admitted and the primary draws 250.

The permutation null is vectorised over rows already — `_statistic` computes every row's `d` for a relabelling in one pass, and the FDR accumulates tail counts by `searchsorted` rather than by a per-row loop. That is why 250 permutations over 2,438 rows is 60 ms.

---

## E1 and E2

**E1 — held.** The base suite was measured here at `0e4dc6b` before anything was written: **805 passed, 14 skipped**, exactly the reviewer's figure. The final suite is **833 passed, 14 skipped**, and this turn adds 28 tests (3 in Part A, 25 in Part B): 805 + 28 = 833, with the skips unmoved at 14.

**E2 — held, exactly as written.** Two existing test files changed, and both are the ones E2 names:

1. **`tests/test_perseus_s0.py`'s P1 comment**, corrected as the prompt instructs. It generalised the 1/19 floor to *"a 19-permutation null cannot support an FDR of 0.01"*; the floor is the mirror's, and 18 draws without it reach q = 0. **No assertion in that file changed.**
2. **`tests/test_tautology_sweep.py`**, with **twenty-three classifications** — six from Part A's tests, seventeen from Part B's — each with the mutation that reddens it named, and **one existing count moved 1 → 2**: `used == 'exhaustive'` now occurs twice, because the new exhaustive-excluding test asserts the same expression about a different scheme. That is the case the multiset exists for, and the module's own docstring calls the inseparability of the two its declared limit.

**No id pin moved. The sweep's floor was not touched**, as the out-of-scope list requires: it reads `modules >= 49 and asserts >= 1693` against a surface of 52 modules and 1,892 asserts, so it passes unchanged.

---

## `CLAUDE.md` point 1 — every check, at its target, at its actual result

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **833 passed, 14 skipped** |
| `pytest tests/test_schema.py` | that module | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed** |
| `ruff format --check` | `bzk tests` | **115 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 115 source files** |

Every command was run under `.venv/bin/python`. The targets are `bzk tests` and not the whole repository: `ruff check .` additionally covers the three notebooks, which are deliberately out of scope permanently and were not run here.

**Point 2 — the change did what it claims, checked directly.** Each of the twenty-eight tests was made to fail with a named mutation, every mutation confirmed applied by reading the file back, and every one reverted; the figures above are from the green run after the reverts. Part A's claim about the mirror was re-run rather than transcribed, and the numbers that did not reproduce are named as not reproducing. One test executes `main` end to end over synthetic bytes, so the IO seam — two deposits, two workbooks, the header found by content, both §3 checks, the family and the serialisation — is exercised rather than inferred.

**Point 3 — what this turn does not cover.**

- **No data run.** No raw store here. Gate G's eight precision/recall pairs, check A's verdicts, which variant is primary, §3's two decisions, readouts A to D and H10's verdict are all unknown. The instrument exists; what it says does not.
- **S1's six intensity columns have never been read.** They are located by content and refuse by name with the whole header printed. The first real run may stop there, which is the stop §3 asks for rather than a wrong join.
- **The end-to-end test establishes the seam, not the figures.** Its Table 3 is generated from one variant's own majority calls so the gate passes and the flow continues — deliberate, bounded, and stated in the test module. It establishes nothing about whether precision and recall are computed correctly; the hand-written metrics test does that.
- **`tests/fixtures/pxd018299_h10.json` is not committed**, so nothing guards the fixture's shape against the generator. That is a turn which needs the fixture to exist first, as turns 13, 15, 16 and 17 each recorded for theirs.
- **`walk/PXD018299-author-parameters.json` does not exist and was not created.** Its presence would be a claim that the authors stated those parameters, and nobody has. The schema and a placeholder example are under `notes/`.
- **Readout B's instability has never been observed on real or realistic data.** Every synthetic matrix small enough to test on is perfectly stable, which is why that test stubs the support pattern. Whether the anchor shows instability at all is the measurement this instrument exists to make.
- **The runtime estimate is arithmetic over measured unit costs**, not a measured whole run. The real matrices' missingness and row counts differ from the synthetic ones.
- **Turn 18's committed report still carries the 1/19 claim** in its uncorrected form. Reports are the record of what a turn found, and this one records the correction rather than editing that one.
- **D3, the third deposit, `ARCHITECTURE.md` §4 and ADR-0015 are untouched**, as the out-of-scope list requires.

**Point 4 — instructions dropped or partially done.** None. Parts A and B, their tests, the example author file under `notes/`, the P1 correction, the runtime report and the task list were all done. Two deviations from what the brief literally says are recorded above and in the code: `exhaustive_excluding_trivial`'s fallback above the cut, which §4 does not describe, and the gate majority computed as a majority rather than as the literal 10.

---

## Commits and the push

| commit | subject |
|---|---|
| `388c757` | `stats:` the two trivial-relabelling schemes, and what the mirror costs |
| `e368326` | `sources:` the anchor under its named test — gate G, check A, and H10 |
| this report | committed alone |

`main` was pushed fast-forward twice: **`0e4dc6b..388c757`** and **`388c757..e368326`**. No branch was force-pushed, and no pushed commit was amended or rebased.
