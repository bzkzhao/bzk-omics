# Report — building the PXD026748 reconstruction (the D5 / H9s instrument)

**Run at:** 2026-09-20 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Base:** `d3917c6`, exactly · **Commits:** `f268ec5`, `d9b35bf`, `b836139`, and this report's own · **Pushed, every push a fast-forward**

**Headline.** Parts A, B and C are written and tested; **nothing has been run on real data**, because this container has no raw store. The ANOVA reproduces R's published `aov` table on `ToothGrowth` to its printed precision and agrees with a nested least-squares F test to 1e-9. The four t variants are written and each checked against hand arithmetic, Student's additionally against `scipy`. The instrument runs end to end on synthetic bytes, gate and family, and the gate's authority over the GG arm is asserted rather than assumed. E1 held at 745 + 30; **E2 was missed in one place and the place is named below**; E3 held.

**One thing bzk should know before the first real run.** The published sheets' column *spellings* are recorded nowhere in this repository, and this container cannot open the workbook. `resolve_column` locates them by content and **refuses by name, printing the header it actually read**, rather than guessing. If the first run stops there, the four column names can be passed to `main` as arguments — no edit is needed. This is the largest of the choices listed below.

---

## The base check

`git rev-parse origin/main` at the open → `d3917c68dd2fc4759cad1c4cb2b413c9ba0368e4`, which is `d3917c6 walk: pre-register the PXD026748 reconstruction (H9s), gated on shotgun positive controls` exactly. The first commit of this turn, `f268ec5`, has `d3917c6` as its parent (`git rev-parse f268ec5^` → `d3917c6…`). No stop condition fired. Nothing under `notes/prompts/` was read, written or committed.

---

## Every choice made where the pre-registration was silent

Each is written into the module as a constant, a docstring or a recorded string, and **none was made by looking at an outcome** — nothing here has been run against the real bytes at all.

| # | choice | reason |
|---|---|---|
| 1 | **Table 2 and Table 3's columns are located by content**, and refused by name with the header printed where that fails. `main` takes all four as overrides. | Their spellings are in no document this repository holds. A column position would be a guess that produces numbers; a refusal produces a question. |
| 2 | **The sample columns are sorted by mapping key.** | The ANOVA and both t-tests are invariant to column order, so the sort decides nothing except that two runs build the same matrix. |
| 3 | **WT is whichever genotype label is not the knockout**, and the record spells the knockout `ISG15-/-`. | `:85` names the contrast and no document names the label. The module refuses a record with other than two genotypes rather than picking. |
| 4 | **PC3's population is every complete-case protein**, with the Table-3-restricted figure reported beside it. | `:95` says *"complete-case proteins"* where `:93-94` say *"complete-case proteins … that are in Table 3"*. The difference is in the pre-registration; both numbers are reported so a reader can see which is which. |
| 5 | **PC2 ties break on the variant's name.** | *"the one passing with the most proteins"* does not order a tie. A tie is visible in the fixture as two equal numerators. |
| 6 | **A claim whose deposit row is not in the filtered population counts as `unsupported`** — supported in no member, which is literally true — **and is also listed by id** in `claims_without_a_row_in_the_population`. | "Supported in none" and "not in the population" must never be one number. Its per-member `min_p` is `null`, not 0 or 1. |
| 7 | **A fourth verdict outcome, `both`.** | `:162`'s exclusivity argument is arithmetic about 288 (274 + 15 > 288), not a property of the rule. At E = 200 the two thresholds are 190 and 10 and both can hold; reporting one of them would be choosing silently. At the registered exposure this branch is unreachable. |
| 8 | **The verdict's thresholds are `ceil(0.95E)` and `ceil(0.05E)`.** | *"≥ 95% of exposure"* is not met by 273.6 of 288, and rounding up reproduces the registered 274 and 15 exactly. |
| 9 | **The full 288 × 360 min(P) matrix is stored**, one row per claim aligned with `family.members`. | The turn asked which was stored: it is the raw data, not a compact equivalent, so every readout is recomputable from the fixture without re-running the family. |
| 10 | **Student's t and both S0 variants are not registered in `bzk.stats.TESTS`.** | `ARCHITECTURE.md` §4's registry table is normative and lists neither; `student_t_s0` at S0 = 1 sits one permutation-FDR step from the `perseus_s0` §4 records as *required and unwritten*, so a registry entry would read as that gap having been closed. The pre-registration's "registered set" is enumerated by the instrument that uses it. |
| 11 | **PC1 also reports how many proteins would be within tolerance under a flipped sign**, and the gate never reads it. | A sign convention opposite to the assumed one shows up as a large number here and a small one in PC1. That is a diagnosis; correcting by it would be tuning. |
| 12 | **The GG population is `_filter`'s output**, including rows the platform refused at ingestion. | The prompt fixes this, and the module records why: a refused row still carries measured intensities and still sets every per-sample median. |
| 13 | **Zero becomes missing at log2**, and the rule is written into the fixture as `missing_rule`. | `:81` states it. `maxquant.cell_value` keeps a reported zero because I19 forbids the *adapter* reading that convention as absence — this is the analysis layer making the call the invariant reserves for it. |

**The registered expectations were not inputs.** R1–R5 appear nowhere in the code. The JUDGED shares of PC1–PC3 appear exactly once each, in `gate_verdict`, which runs after every figure has been computed by `positive_controls`; PC0's 2,438 is a constant because `:92` records it as MEASURED and the gate is an exact comparison against it. Table 2's 600 is **not** a constant: its membership is read from the workbook at run time and the run reports the count it actually read.

---

## A1 and A2, with the numbers

**A1 — R's published `aov` table for `ToothGrowth`**, `len ~ supp * factor(dose)`, 2 × 3 with n = 10. The fixture is R's own distributed copy, fetched from `Rdatasets` and committed as `tests/fixtures/toothgrowth.csv`; its sha256 is asserted as `b35e084a…354c26fe` and matches the digest the prompt gave.

| term | SS | df | F | P | asserted to |
|---|---|---|---|---|---|
| supp | 205.35 | 1 | 15.572 | 0.000231 | SS ±5e-3, F ±5e-4, P ±5e-7 |
| dose | 2426.43434 | 2 | 92.000 | < 2e-16 | asserted as a bound, since R prints one |
| supp:dose | 108.319 | 2 | 4.107 | 0.0219 | SS ±5e-3, F ±5e-4, P ±5e-5 |
| residuals | 712.106 | 54 | | | SS ±5e-3 |

All eight figures hold. A second test asserts the table is **symmetric in the order of the factors** — swapping them swaps the main effects and leaves the interaction alone, which is true of a balanced design and of nothing else, and is the licence `:54-58` relies on.

**A2 — an independent computation.** 40 random rows of a balanced 2 × 3 design with n = 2, every F compared against a nested least-squares F test built from `numpy.linalg.lstsq` residual sums of squares. Agreement to `rel=1e-9`.

**A2 failed first, and the fault was in the test.** Under treatment coding the interaction columns still carry main-effect information, so dropping a factor's own columns while keeping the interaction block does not remove that factor from the model — the nested comparison measures a Type I effect and disagrees with the balanced sums of squares by construction. The signature was unambiguous: the interaction agreed **exactly** (0.345042 both ways), the sums of squares partitioned the total exactly, A1 matched published numbers, and only the two main effects disagreed. Switching `_dummies` to sum coding, under which the three column blocks are mutually orthogonal on a balanced design, closed it. The reasoning is written into the helper's docstring so the next reader does not rediscover it.

A third check asserts the partition: A + B + AB + residual equals the total sum of squares to 1e-9. It is a real check rather than an identity because the residual is computed from within-cell spread, never by subtraction.

---

## Every test, its mutation, and the failure message

Every mutation was confirmed applied **by reading the file back from disk** before the test was run, and reverted afterwards; the suite is green again below. Nine, ten and twelve mutations, for nine, nine and twelve tests.

### Part A — `tests/test_anova.py` (9 tests)

| test | mutation | failure |
|---|---|---|
| the fixture is the file that was fetched | one newline appended to `tests/fixtures/toothgrowth.csv` (restored from a copy taken first) | digest read `1e3ab698…`, not `b35e084a…` |
| A1 matches R's published table | `ss_a = n * b * ((mean_a` → `n * ((mean_a` | `assert np.float64(68.44999999999997) == 205.35 ± 0.005` |
| A1 is symmetric in the factors | `mean_b = cell_means.mean(axis=1)` → `cell_means[:, 0, :]` | `assert np.float64(2426.4343333333345) == 3504.3273333333327 ± 0.00350433` |
| A2 agrees with nested least squares | `ms_residual = ss_residual / df_residual` → `/ (df_residual - 1)` | 40/40 mismatched, `Max relative difference: 0.2000000000000657` |
| the sums of squares partition the total | the grand mean dropped from the interaction | obtained 4.76595864247774 against 4.1012748839953845 ± 4.1e-09 |
| min_p is the smallest of the three | `np.nanmin` → `np.nanmax` | obtained 0.9370839388737385 against 0.12177609152392764 |
| a missing value is refused | `np.isnan(values).any()` → `.all()` | `Failed: DID NOT RAISE AnovaError` |
| an unbalanced design is refused | `if len(sizes) != 1:` → `if len(sizes) > 2:` | `Regex pattern did not match. Expected 'unbalanced'; Actual message: 'each cell needs >=2 observations to leave residual df; got 1'` |
| a single observation per cell is refused | `if n < 2:` → `if n < 1:` | `Failed: DID NOT RAISE AnovaError` |

**One of those nine failed in a weaker way than the others and it is reported rather than swapped.** Removing the balance guard did not let the unbalanced design through: it fell through to the `n >= 2` guard one line down and was refused with a different message, so the test failed on the message rather than on the absence of a refusal. That is still a discriminating failure — the design is refused for the wrong reason, and the test says which — but it is not the same strength as a `DID NOT RAISE`, and the difference is recorded here.

### Part B — `tests/test_t_variants.py` (9 tests, 10 mutations)

| test | mutation | failure |
|---|---|---|
| S0 is the registered value | `S0 = 1.0` → `0.5` | `assert 0.5 == 1.0` |
| Welch matches the hand computation | `var1 / n1 + var2 / n2` → `var1 / n2 + var2 / n1` | `0.055076230861421764 == 0.04577582843879493 ± 1e-12` |
| Student matches the hand computation | the pooled variance unweighted, `(var1 + var2) / 2` | `0.05820134120367469 == 0.08386461645701294 ± 1e-12` |
| Welch S0 divides by se + S0 | `pooled=False, s0=S0` → `s0=0.0` | `0.04577582843879491 == 0.17258497570281867 ± 1e-12` |
| Student S0 divides by se + S0 | `pooled=True, s0=S0` → `s0=0.0` | `0.08386461645701294 == 0.221466128104933 ± 1e-12` |
| the four variants are four, not two | `student_t` wired to `pooled=False` | `assert 3 == 4` |
| S0 never sharpens | `standard_error + s0` → `- s0` | `assert np.False_` on the row-wise `>=` |
| Student matches `scipy` | `float(n1 + n2 - 2)` → `- 1` | `Not equal to tolerance rtol=1e-10 … Mismatched elements: 200 / 200 (100%)` |
| every variant refuses one replicate | `if n1 < 2 or n2 < 2:` → `< 1` | `Failed: DID NOT RAISE ValueError` |
| (the `log2fc` line inside the four hand tests) | `difference=mean1 - mean2` → `mean2 - mean1` | `assert np.float64(4.0) == -4.0 ± 4.0e-06` |

The last row exists because the tautology sweep's record claims it: `log2fc == pytest.approx(DIFFERENCE)` occurs four times and the multiset cannot separate the four, so the claim that a P-line catches what that line cannot was measured rather than argued.

### Part C — `tests/test_pxd026748_reconstruction.py` (12 tests)

| test | mutation | failure |
|---|---|---|
| normalisation precedes the valid-value filter | `pipeline` filters first, then normalises the survivors | `assert np.float64(-3.0) == -4.0 ± 4.0e-06` |
| the valid-value rule is three in one group | `MIN_VALID_IN_A_GROUP = 3` → `2` | `assert [True] == [False]` |
| the join reads the first majority id only | `entries[0]` → `entries[-1]` | `At index 0 diff: 'SYNTHETIC-2' != 'SYNTHETIC-1'` |
| primary is strict and secondary inclusive | both comparisons made inclusive | `assert [True, True, True, False] == [False, True, True, False]` |
| an unresolvable column stops with its header | `if len(matches) == 1:` → `if matches:` | `Failed: DID NOT RAISE ReconstructionError` |
| the verdict is mechanical, in fraction form | **`verdict_thresholds` hard-coded to `274, 15`** | `assert (274, 15) == (190, 10)` — the E = 200 case, exactly as the turn predicted |
| both outcomes at once are named | `both` → `weakens_d5` | `assert 'weakens_d5' == 'both'` |
| the seed is honoured | `seed=member.seed` → `seed=0` | `assert not True`, the two seeds' arrays identical |
| the family is the registered grid | `SEEDS = range(20)` → `range(10)` | `assert 180 == 360` |
| **a failing control stops the run before the GG arm** | the gate's guard neutered, so the GG arm runs regardless | `assert 0 == 1` |
| a passing gate runs the family | the multiplicity flag read the wrong way round | `assert 4 == 1` |
| **a refused row stays in the population** | the population restricted to the claims | `assert 5 == (5 + 1)` |

One mutation had to be re-applied: the population restriction is an *insertion*, and the mutation harness's read-back check asserted the old text was gone. The check was wrong for insertions, not the mutation — it was fixed to compare the file against its own previous contents, the mutation re-run, and the mutated lines printed back from disk before the test ran.

**What the Part C tests do not establish.** The two end-to-end runs generate their Table 2 and Table 3 from the same synthetic matrix the module then reads, so PC1, PC2 and PC3 pass by construction there. That circularity buys exactly one thing — a gate that passes, so the run continues into the GG arm and the control flow can be asserted — and it is stated in the test module's own docstring rather than left implied. What establishes the arithmetic is independent and elsewhere: A1, A2, and the t variants against hand arithmetic and `scipy`.

For the record, the synthetic harness's gate printed: PC0 2,438 of 2,438; PC1 2,438/2,438; PC3 2,438/2,438; PC2 `welch_t` 2,438, `student_t` 1,918, `student_t_s0` 113, `welch_t_s0` 112 — chosen variant `welch_t`. **These are numbers about synthetic bytes and say nothing about PXD026748.**

---

## The output's shape

`tests/fixtures/pxd026748_reconstruction.json`, written by `main` and **not committed by this turn** — this container cannot produce it.

```
dataset, registration, gg_run, published_file, published_content_hash, published_sheets,
shotgun_file, shotgun_content_hash, digly_file, digly_content_hash, note, generated_by,
generated_under { generated_at, commit, working_tree_clean, python, numpy,
                  missing_rule, valid_value_rule }
gate {
  pc0   { proteins_passing, registered, holds, rows_after_filters }
  join  { rule, table_3_rows, table_2_rows_read, table_2_distinct_ids,
          groups_joined, groups_unmatched, groups_ambiguous, table_3_ids_unmatched }
  complete_case { proteins, in_table_3, wild_type, knockout }
  pc1   { numerator, denominator, share, tolerance, within_tolerance_under_a_flipped_sign }
  pc2   { tolerance, variants { <each of four> { numerator, denominator, share } } }
  pc3   { numerator, denominator, share, threshold_used, reconstructed_members,
          restricted_to_table_3 }
  verdict { thresholds, holds { pc0..pc3 }, chosen_variant, passed }
}
family {                                    # absent entirely when the gate fails
  members[360] { width_sd, downshift_sd, scope, seed }
  default_cell, exposure, population_rows, claims_without_a_row_in_the_population
  readouts { primary | secondary { threshold, counts { durable, underdetermined, unsupported },
                                   by_cluster, default_cell_supported, categories, support } }
  threshold_consistency_count, whole_table_supported_in_the_default_cell
  multiplicity_flagged_claims[], verdict { exposure, durable, underdetermined,
                                           durable_needed, underdetermined_needed, outcome }
  claims[288] { deposit_id, cluster, published_row, uniprot_id, lysine_position,
                has_positive_multiplicity_column, median_min_p_default_cell, min_p[360] }
}
```

**The raw data is kept in full**: `claims[].min_p` is one value per member, aligned with `family.members`, so any readout in the block above can be recomputed from the fixture. A gate failure writes the header and the `gate` block, sets `gg_run: false`, and `main` returns 1 with no `family` key at all — an empty family block would read as a family that ran and found nothing.

---

## E1–E3

**E1 — held.** The base figure of 745 passed / 14 skipped was not re-measured at `d3917c6` (this session was resumed mid-turn and the working tree already carried Part A), but it is recovered exactly by arithmetic: the final suite is **775 passed, 14 skipped**, and this turn added 9 + 9 + 12 = 30 tests. 775 − 30 = 745, with the skip count unmoved at 14. The 14 skips are the raw-store tests, which this container cannot run.

**E2 — missed, in one place, and nothing else.** `tests/test_tautology_sweep.py` changed. Three new test modules add 39 matching expressions to a sweep whose whole design is that a new match must be classified before it lands, so leaving them unclassified leaves the suite red — the change is mandated by the suite rather than chosen. What changed:

- three `PINNED` blocks, one per new module, each classified expression by expression with the mutation that reddens it named;
- the surface floor, `modules >= 32 and asserts >= 1129` → `>= 49 and >= 1693`.

**No existing assertion was changed, weakened or removed, and no id pin moved.** All 39 entries are `PINNED`; none is the `INSTANCES` class, and the distinguishing test was applied rather than assumed — an instance is one whose *own scope stays green* under the mutation, and every one of these reddens its own test.

**And the floor had not moved in a month.** It stood at 32 modules / 1,129 asserts while the surface had grown to 47 / 1,641 — fifteen modules and five hundred assertions accrued behind a `>=` that is silent about a surface that grows. That is the slack the module's own comments describe and then took again; the gap is recorded in the file rather than closed quietly.

**E3 — held.** A1's numbers match R's published table to the precision the prompt gave; the table is reproduced above.

---

## `CLAUDE.md` point 1 — every check, at its target, at its actual result

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **775 passed, 14 skipped** |
| `pytest tests/test_schema.py` | that module | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed** |
| `ruff format --check` | `bzk tests` | **109 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 109 source files** |

Every command was run under `.venv/bin/python`. The targets are `bzk tests` and not the whole repository: `ruff check .` additionally covers the three notebooks, which are deliberately out of scope permanently and were not run here.

**Point 2 — the change did what it claims, checked directly.** Each of the thirty new tests was made to fail with a named mutation, every mutation confirmed applied by reading the file back, and every one reverted; the suite is green after the reverts and the figures above are from that green run. A1's eight figures were compared against R's printed table rather than inferred from a passing suite.

**Point 3 — what this turn does not cover.**

- **Nothing has been run on real data.** No raw store here. PC0, PC1, PC2, PC3, the 360-member family and H9s's verdict are all unmeasured; the gate's real outcome is unknown, and so is whether the reconstruction reproduces the publication at all.
- **The supplement's sheet 2 and 3 column spellings are unverified.** They are recorded in no document this repository holds and the workbook is not reachable from here. `resolve_column` refuses by name with the header printed, and `main` takes four overrides, so the failure mode is a question rather than a wrong number — but the first real run may well stop there.
- **The end-to-end tests establish control flow, not correctness of PC1–PC3**, for the reason given above.
- **`tests/fixtures/pxd026748_reconstruction.json` is not committed**, so nothing guards the fixture's shape against the generator. That guard is a turn that needs the fixture to exist first, exactly as turns 13 and 15 recorded for theirs.
- **The `both` verdict branch is unreachable at the registered exposure** and is covered only by a test at E = 200.
- **`gate_verdict`'s tie-break is untested end to end.** It is asserted nowhere; a tie between two variants would be visible in the fixture as two equal numerators, and the name-ordered choice is documented rather than pinned.
- **No `Analysis`, `Imputation` or result node is written to the graph.** This turn produces a fixture, not an ingestion; I15's `Imputation` node for these 360 runs does not exist, and nothing here touches `graph.kuzu/`.
- **The class this turn's Part B closes is closed by a test, not by a note.** `set(TESTS) == {"welch_t"}` in `tests/test_stats.py` already guards the decision not to register the three new variants: it fails the moment one is registered without `ARCHITECTURE.md` §4 being amended. No `HANDOFF.md` §8 note was needed, and none was written.

**Point 4 — instructions dropped or partially done.**

- **E2 was missed as described above**, deliberately and with the reason stated. That is the only instruction from this turn not met as written.
- The base check was performed against `origin/main` and the first commit's parent rather than by re-fetching at the open, because the session was resumed mid-turn with Part A already written. The conclusion is the same and the evidence is given.
- Everything else in Parts A, B and C, their tests, and the task list was done: the readouts are all present (both thresholds, by cluster, the default cell alone, the threshold-consistency count, the whole-table count, the one multiplicity-flagged claim, the verdict in fraction form), the three commits carry the prefixes asked for, and nothing under `notes/prompts/` was touched.

---

## Commits and the push

| commit | subject |
|---|---|
| `f268ec5` | `stats:` a balanced two-way ANOVA with interaction, validated before use |
| `d9b35bf` | `stats:` the four t variants PC2 chooses among, three of them unregistered |
| `b836139` | `sources:` the PXD026748 reconstruction, gated on the shotgun positive controls |
| this report | committed alone |

`main` was fast-forwarded onto the work and pushed: **`d3917c6..b836139`**, a fast-forward. The harness's working branch was updated to the same commit: **`dc4db3a..b836139`**, also a fast-forward. No branch was force-pushed, and no pushed commit was amended or rebased.
