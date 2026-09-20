# Report — implementing `perseus_s0`

**Run at:** 2026-09-21 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Base:** `69700ea`, a fast-forward of `5a7f699` · **Commits:** `3ae9308`, `7236993`, and this report's own · **Pushed, every push a fast-forward**

**Headline.** §4's default and required entry is written, registered and tested. **No data run, on any deposit.** The statistic, the permutation null, the FDR at a threshold and the q-value are each checked against a second enumeration written in the test file, which shares no line with the module. Both open questions — sidedness and how the relabellings are drawn — are built as named variants and **chosen by nobody here**. Twelve tests, seventeen mutations. E1 held at 793 + 12; **E2 was missed in one place, necessarily, and the place is named below**.

**Two things a reader should know before the gate runs.**
1. **A 19-relabelling null cannot support an FDR of 0.01.** At three against three the smallest attainable q is 1/19 ≈ 0.053, because one null row at or beyond the threshold is the smallest non-zero numerator there is. The anchor's published threshold is 0.01, so its gate will need either more columns or a randomisation count the authors supply — this is a property of permutation FDR, not of this implementation, and it is asserted in P1 so it cannot be discovered late.
2. **The brief states the exhaustive cut two ways**, and they disagree at exactly one point. Resolved, and recorded, below.

---

## The base check

```
git rev-parse origin/main        → 69700ea
git diff --stat 5a7f699..origin/main
  HYPOTHESIS.md | 150 +++++++++++++++++++++++++++++++++++++++++++++++++++++-----
  1 file changed, 139 insertions(+), 11 deletions(-)
git show origin/main:HYPOTHESIS.md | sha256sum
  → 24d732523009098e5224b97d905a0544673ba7543af629e4eeb92c9b7c5709e3
```

The hash is the one the prompt gives and the only changed path is the one it allows. No stop condition fired. `HYPOTHESIS.md` v8 §0 and the H10 amendment, `ARCHITECTURE.md` §4, `ONTOLOGY.md` l.155–175, `ROADMAP.md` l.73 and l.91–98, ADR-0015, ADR-0017 and `bzk/stats/tests.py` were each read before anything was written. Nothing under `notes/prompts/` was read, written or committed.

---

## The algorithm as implemented, with every choice the brief left open

**The statistic.** `d = (mean_A − mean_B) / (s + s0)`, with `s` the pooled (Student) standard error, from `_moments(…, pooled=True)` in `bzk/stats/tests.py`. No second copy of the variance arithmetic exists.

**The null.** Relabellings of the columns preserving both group sizes; `d` is recomputed for every row in each.

**The FDR.** `FDR(t)` = mean over permutations of #{null |d| ≥ t}, over #{observed |d| ≥ t}. A row's q is the smallest FDR over the observed thresholds that would still call it, which is computed as a running minimum over thresholds ordered from least to most extreme — that ordering *is* the monotonicity, rather than a sort applied afterwards.

| # | choice | reason |
|---|---|---|
| 1 | **The exhaustive cut is on `C − 1`, the draws that would actually run, not on `C`.** | The brief says both: *"when the number of distinct relabellings, C(n_A + n_B, n_A), is at most `randomisations`"* and, of the same case, *"uses exactly 19 non-identity relabellings at 3 against 3 when `randomisations ≥ 19`"*. They disagree at exactly one point, `randomisations == C − 1`. Resolved toward the second: `randomisations` is a budget of draws, the identity is never one of them, and refusing an enumeration of 19 because a twentieth relabelling exists that the scheme would not use is a fallback with no cost behind it. **Both sides of the cut are asserted** — 19 enumerates, 18 falls back — so the resolution is visible rather than implied. |
| 2 | **The mirror relabelling is kept; only the identity is dropped.** | Giving group A precisely B's columns is a genuine relabelling that yields `−d`. Dropping it would make the null asymmetric under `per_side` for no stated reason. |
| 3 | **`random` draws with replacement and does not exclude the identity.** | The brief fixes the draws as independent with repeats allowed. A de-duplicating "random" scheme would be a third scheme wearing the name of the second. |
| 4 | **Under `per_side`, a row with `d == 0` is placed on the positive side.** | Strict inequalities on both sides would leave such a row with no q at all. The choice is stated rather than left to a comparison operator. |
| 5 | **q is not capped at 1.** | It is a ratio of counts and can exceed 1 where the labels carry nothing. Clipping would assert a bound the estimator does not have, and significance is `q ≤ alpha`, which an uncapped q above 1 fails exactly as a capped one would. |
| 6 | **A non-finite `d` is excluded from every threshold and count, and comes back `q = NaN`, `significant = False`.** | `welch_t`'s rule one level along: a caller who skipped imputation gets an obviously empty answer for that row rather than a plausible one. NaN propagates; it does not raise. |
| 7 | **`direction` is `sign(mean difference)`: +1, −1, or 0.** | The brief says direction is reported by the sign of the mean difference. 0 where the two group means are exactly equal is a real case in the test matrix, and a two-valued direction would have to invent one of them. |
| 8 | **`sidedness` and `scheme` are required with no defaults, like `s0`, `alpha`, `randomisations` and `seed`.** | *"Do not choose here."* A default would answer an open question silently, which is the failure ADR-0017 names. |
| 9 | **The outcome is a `PerseusOutcome`, not a `TestResult`.** | A permutation q-value is not a p-value. Putting it in a field named `p_value` would be the shape I15 forbids one level down — a number presented as something it is not. The registry's value type widened to admit this rather than the number being renamed to fit. |
| 10 | **The registry entry declares `("s0", "fdr", "randomisations")`.** | `ONTOLOGY.md` l.155 names `s0` and the randomisation count as identifying; `ARCHITECTURE.md` §4 names three — *"`s0`, `fdr`, and the number of randomisations"*. The superset is declared, so neither document is under-recorded. `fdr` is §4's name for the level the brief calls `alpha`; the outcome carries the value, so a caller building `parameters_json` never has to guess. |
| 11 | **`randomisations_used` is recorded beside `randomisations`.** | `exhaustive_when_small` is a request, not a guarantee. What determines the result is the count that ran, and a record carrying only the request would not say which null was used. |
| 12 | **`TESTS` now holds `RegisteredTest` records rather than bare callables.** | The entry and its required parameters are one fact; two dicts keyed by name would be two homes for it, which is the mirror this repository guards everywhere else. `welch_t`'s own function is untouched and still satisfies the narrower `Test` shape. |

**Registration was checked against §4 before it was done, not assumed.** §4's table describes *"SAM-style modified t-test with fold-change curvature parameter `s0` and permutation-based FDR"*, and that is what was built: the `s0` curvature is in the denominator, the FDR is a permutation FDR and not BH, and §4's *"required parameters, recorded on the `Analysis` per I16"* are declared on the entry. Nothing diverges, so it is registered.

---

## P1–P8, each with its mutation and failure message

Twelve tests, seventeen mutations. Every mutation was confirmed applied **by reading the file back from disk** before the test ran, and reverted afterwards; the suite is green after the reverts.

| test | mutation | failure |
|---|---|---|
| **P1** the statistic matches closed-form arithmetic | `s0` dropped from the denominator | `12.247448713915619 < 0.02` is false — the row whose spread is tiny |
| ” (second, for the two rows whose group means are equal) | a numerator "guard", `np.where(difference == 0, 1.0, difference)` | `assert 1.0911115445599888 == 0.0 ± 1e-12` |
| **P1** the null counts, FDR and q match an independent enumeration | `FDR = (null/draws) / called` → `/ called.max()` | `Not equal to tolerance rtol=1e-12 … Mismatched elements: 3 / 6 (50%)` |
| **P1b** the standard error is pooled, not Welch's | `pooled=True` → `pooled=False` | `assert -2.457719193661888 == -1.9683261229993825 ± 2e-12` |
| **P2** `s0` bites | `d = difference / standard_error` | `assert 12.247448713915619 < 0.02` |
| **P3** q is monotone in `|d|` | `cummin = np.minimum.accumulate(fdr)` → `cummin = fdr` | `assert np.False_` on `np.diff(ordered_q) <= 1e-12` |
| **P4** the seed is honoured | `default_rng(seed)` → `default_rng(0)` | `assert not True` — the two seeds' q-values identical |
| **P5** the exhaustive scheme and its fallback | the cut moved back to `C` | `'random' == 'exhaustive'` at `randomisations = 19` |
| **P5b** the identity is not in the null | `if group != identity` → `if group != ()` | `assert 20 == 19` |
| ” (second, for the `used` line) | the exhaustive branch labelled `"random"` | `'random' == 'exhaustive'` |
| **P6** `per_side` differs from `joint` | `if sidedness == "joint"` → `if sidedness in SIDEDNESS` | `assert not True` — `np.allclose(joint.q_value, per_side.q_value)` |
| **P7** no silent defaults | `randomisations`, `seed`, `sidedness` and `scheme` given defaults | `Failed: DID NOT RAISE TypeError` |
| **P8** the registry entry | `REQUIRED_PARAMETERS` cut to `("fdr",)` | `assert 's0' in ('fdr',)` |
| ” (second, for the `welch_t` log2fc line) | `welch_t`'s difference negated in `bzk/stats/tests.py` | `assert -3.0 == 3.0 ± 3e-06` |
| ” (third, for the `welch_t` p-value line) | Welch–Satterthwaite's df off by one | `assert 0.0227…== 0.021311641128756713 ± 1e-12` |
| the outcome carries every declared parameter | `return draws, "exhaustive", len(draws)` → `randomisations + 1` | `assert 20 == 19` |

### P1b exists because a mutation found a hole

The first mutation run against P1 was the obvious one — swap the pooled standard error for Welch's — and **P1 stayed green**. The reason is arithmetic: at `n_A == n_B`, `pooled_var · (1/n + 1/n)` is `(v_A + v_B)/n`, which is Welch's `v_A/n + v_B/n` *exactly*, for any variances. P1 is three against three, because that is what makes the 20 relabellings enumerable, so it cannot distinguish the two standard errors at all. **P1b was added for that alone**: three against five, with the pooled value written out by hand (`−4 / (sqrt(56/15) + 0.1)`) and the Welch value asserted to differ. The same trap was recorded in turn 16's t-variant tests and was walked into again here; the mutation is what caught it, not the reading.

---

## E1 and E2

**E1 — held.** The base suite was measured here at `69700ea` before anything was written: **793 passed, 14 skipped**, exactly the reviewer's figure. The final suite is **805 passed, 14 skipped**, and this turn adds 12 tests: 793 + 12 = 805, with the skips unmoved at 14. The 14 skips are the raw-store tests this container cannot run.

**E2 — missed, in one place, and the miss is forced by the instruction.** `tests/test_stats.py::test_the_registry_holds_what_architecture_4_says_v0_1_holds` asserted `set(TESTS) == {"welch_t"}` with a docstring calling `perseus_s0` *"default and required but unwritten"*. Registering the entry — which this turn was told to do, and which §4 licenses — makes both false. The assertion now reads `{"welch_t", "perseus_s0"}` and the docstring records what changed and why, keeping the half that still does work: `moderated_t_ebayes` is still absent, and the assertion still makes that gap visible. **No other existing test changed**, no id pin moved, and no assertion was weakened or removed.

The other existing-test change is the one E2 allows: **ten `PINNED` classifications** in `tests/test_tautology_sweep.py`, all from `tests/test_perseus_s0.py`, each with the mutation that reddens it named in the block. Nine were measured line by line. **The tenth is recorded as documentary rather than claimed as guarded**: `result.q_value[2] == pytest.approx(1.0 / 19.0)` restates in closed form one element of the `assert_allclose` on the line above, and any mutation to the q arithmetic reddens that line first, so it cannot be reached on its own. What it adds is the reading — 1/19 is the smallest FDR a 19-draw null can produce — and the classification says so rather than inventing evidence for it.

**The sweep's floor was not touched**, as the out-of-scope list requires. It reads `modules >= 49 and asserts >= 1693`; the surface is now 51 modules and 1,793 asserts, so both sit above it and the guard passes unchanged.

---

## `CLAUDE.md` point 1 — every check, at its target, at its actual result

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **805 passed, 14 skipped** |
| `pytest tests/test_schema.py` | that module | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed** |
| `ruff format --check` | `bzk tests` | **113 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 113 source files** |

Every command was run under `.venv/bin/python`. The targets are `bzk tests` and not the whole repository: `ruff check .` additionally covers the three notebooks, which are deliberately out of scope permanently and were not run here.

**Point 2 — the change did what it claims, checked directly.** Each of the twelve tests was made to fail with a named mutation, every mutation confirmed applied by reading the file back, and every one reverted. P1's q-values were checked against a second enumeration written in the test file — `itertools.combinations` over the relabellings, a loop over thresholds, and the statistic written from the definition — which shares no line with the module, so agreement to 1e-12 is a real check rather than one implementation agreeing with itself.

**Point 3 — what this turn does not cover.**

- **No data run, on any deposit.** Nothing here has been run against `PXD018299`, `PXD026748`, or any real matrix. The entry exists; what it produces on real data is unknown.
- **The two open questions are not answered.** Sidedness and the permutation scheme are four named variants, and H10's gate will choose among them on published Perseus output. This turn deliberately does not choose, and no variant is marked preferred anywhere in the code.
- **The gate itself is not built**, and neither is the H10 pre-registration it belongs to.
- **Nothing was checked against a real Perseus run.** The arithmetic is checked against its own definition and against an independent enumeration; whether Perseus 1.6.0.2 computes its permutation FDR this way is exactly what the gate is for, and nothing here anticipates its answer.
- **`Analysis` is not written.** No node, no `parameters_json`, no `fdr_method`. The registry declares what such a record must carry; building one is a different turn.
- **`ARCHITECTURE.md` §4 and ADR-0015 are untouched**, as the out-of-scope list requires, and nothing in the entry diverges from §4's description — that was checked before registering rather than after.
- **The randomisation count is still unstated by the publication.** It stays a required parameter with no default, and a run at 3-against-3 cannot reach the anchor's published FDR of 0.01 whatever it is set to (see the headline).
- **`moderated_t_ebayes` is still unwritten**, and the registry assertion still says so.

**Point 4 — instructions dropped or partially done.** None. Part A, the registration, the `ROADMAP.md` note, P1–P8 and the task list were all done. The two deviations from what the brief literally says are recorded above and in the code: the exhaustive cut resolves a conflict in the brief's own text, and P1b is a test the brief did not ask for, added because a mutation showed P1 could not do the job alone.

---

## Commits and the push

| commit | subject |
|---|---|
| `3ae9308` | `stats:` implement `perseus_s0`, §4's default and required entry |
| `7236993` | `docs:` record that `perseus_s0`'s dependency is discharged |
| this report | committed alone |

`main` was pushed fast-forward: **`69700ea..7236993`**. No branch was force-pushed, and no pushed commit was amended or rebased.
