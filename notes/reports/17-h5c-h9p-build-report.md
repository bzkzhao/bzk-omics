# Report — building the H5c and H9p instrument

**Run at:** 2026-09-21 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Base:** `c48d099`, a fast-forward of `12f0885` · **Commits:** `12ca971`, and this report's own · **Pushed, every push a fast-forward**

**Headline.** `bzk/sources/pxd026748_h5c_h9p.py` measures both hypotheses in one run, reusing turn 16's ten functions with no second copies. **Nothing has been run on real data** — this container has no raw store — but the whole path from bytes to verdict is exercised offline, `main` included. Eighteen tests, twenty-one mutations, every one confirmed applied by reading the file back and reverted. E1 held at 775 + 18; E2 held, with the three sweep classifications named. **One defect was found by a test rather than by reasoning**: H9p's registered factor comparison was decided by binary floating point at its own boundary.

---

## The base check

```
git rev-parse origin/main        → c48d099
git diff --stat 12f0885..origin/main
  HYPOTHESIS.md                         | 131 ++++++++++++++++++++++++++++++++--
  notes/reports/REVIEW-seed-lability.md | 125 ++++++++++++++++++++++++++++++++
  2 files changed, 251 insertions(+), 5 deletions(-)
git show origin/main:HYPOTHESIS.md | sha256sum
  → 1969ec294d632c16283cc5ba3255c07101034e8ea58c3492263b9e20ae8c486e
```

The hash is the one the prompt gives, and the only two changed paths are the two it allows. No stop condition fired. `HYPOTHESIS.md` v7 was read in full, and §5's H5c and H9p entries are quoted where this module implements them. Nothing under `notes/prompts/` was read, written or committed.

**The committed reconstruction fixture is present and self-consistent.** `tests/fixtures/pxd026748_reconstruction.json`, 3.5 MB, `gg_run: true`, 288 claims over 360 members, stored primary counts **111 durable / 177 underdetermined / 0 unsupported**. Recomputing the categories from its own per-claim `min_p` reproduces those counts exactly, which is the guard the module runs before it reads anything.

---

## Every choice made where v6 was silent

Each is a constant, a docstring or a recorded string in the module, and none was made by looking at an outcome — nothing here has been run against the real bytes.

| # | choice | reason |
|---|---|---|
| 1 | **A flag cell is `x` after stripping whitespace and folding case**, and every distinct value the column held is reported as `flag_values_as_found`. | §5 states the value and states no normalisation. The allowance is small, and reporting the raw values makes it auditable — if the column turns out to hold only `x` and blanks, the allowance changed nothing and the fixture says so. Nothing is read as flagged for being merely non-empty. |
| 2 | **`#` is matched literally, and its absence is a named refusal.** Every other column here is located by content; `#` cannot be, because `resolve_column`'s normaliser reduces it to the empty string. | A column that cannot be matched by content must be matched by name, and a missing one must stop rather than silently key the join on `None`. |
| 3 | **Both sides of the join are compared as integers.** | `openpyxl` returns `1.0` for a number typed in Excel and `'1'` for text; the fixture stores `1`. They are the same published row, and a string comparison would join none of them. |
| 4 | **The registered thresholds are compared with a 1e-9 tolerance** — H5c's ±0.10 and H9p's ×0.5 and ×0.8 alike. | The figures are rationals in binary floating point: `0.5 - 0.4` is `0.09999999999999998` and `0.8 * 0.8` is `0.6400000000000001`. A registered direction decided by the representation rather than by the data is not the registered direction. The slack is four orders of magnitude below the smallest gap between two genuinely different results at these group sizes (≥ 1/(288·288) ≈ 1.2e-5), so it can merge nothing real. **This was found by the boundary test failing, not by reasoning ahead** — see below. |
| 5 | **A duplicated `#` in Table 1 stops the run**, as an unjoined claim does. | The join is on that column; keeping one of two rows would decide silently which published row a claim's group came from. |
| 6 | **H5c reports `undefined` if either group is empty.** | v6 registers three differences and no empty-group case. A difference of two proportions where one does not exist is not zero, and `does_not_discriminate` over an empty group would be a finding about nothing. |
| 7 | **H9p's family runs over the whole filtered shotgun matrix, and the exposure is read off it.** | `whole_matrix` scope draws from the population's own mean and standard deviation, so imputing the exposure alone would impute from a different distribution than the reconstruction did. |
| 8 | **A Table 2 id leading more than one protein group is counted `ambiguous` and used by nothing.** | Turn 16's recorded join rule, applied unchanged; it is reported beside `unmatched` and `not_reaching_the_test` so the three losses stay distinguishable. |
| 9 | **A claim with no row in the filtered population has `missing_values: null`, never 0.** | Absent is not zero — the same rule `pxd026748_ingest_figures` applies to an absent MaxQuant column. Its min(P) is null too, and a null clears no threshold, so it is `unsupported` rather than dropped. |
| 10 | **Each claim is written with its support count and category, not with its 360 `min_p` values**, and the source matrix is pinned instead by `reconstruction_fixture_hash`. | Copying them would duplicate the reconstruction fixture's whole matrix inside this one. Every figure here is recomputable from the counts kept. |
| 11 | **U_s is taken over all 288 site claims, cluster 3 included.** | §5's H9p says *"the 288 site claims"*; the cluster-3 exclusion is H5c's, and H5c's reason for it — the flag concerns ISG15 targets — does not apply to a comparison about imputation. |
| 12 | **Support is recomputed from the fixture's per-claim `min_p`, not read from its stored `support` field.** | The fixture carries both; recomputing and then checking the totals against the stored counts uses the numbers rather than the conclusions, and turns the stored counts into a guard instead of a source. |
| 13 | **A fixture recording `gg_run: false` stops the run.** | Its gate failed, so it carries no family, and both hypotheses' site-grain halves come from that family. |

**The registered thresholds are read once each.** H5c's ±0.10 lives in `h5c_verdict`; H9p's 0.5 and 0.8 live in `h9p_verdict`. Every proportion above them is computed without reference to them. The declared confound — each claim's missing-value count out of twelve — is computed, reported by group, and read by neither verdict; a test holds that.

---

## Every test, its mutation, and the failure message

Eighteen tests, twenty-one mutations. Every mutation was confirmed applied **by reading the file back from disk** before the test ran, and reverted afterwards; the suite is green after the reverts.

| test | mutation | failure |
|---|---|---|
| H5c excludes cluster 3 | `ISG15_CLUSTERS` gains `"Cluster 3"` | `assert 30 == 20` |
| H5c counts every ISG15 cluster | `ISG15_CLUSTERS` cut to `("Cluster 1a",)` | `{'Cluster 1a': 1}` against all three |
| a claim joining no published row stops the run | the guard replaced by `flags.flagged.get(number, False)` | `Failed: DID NOT RAISE HypothesisError` |
| H5c's verdict at the boundaries | `>= H5C_THRESHOLD - tolerance` → `> H5C_THRESHOLD` | `'does_not_discriminate' == 'discriminates'` |
| **H5c never runs a family member** | a `run_member(...)` call inserted at the top of `h5c_block` | `assert [(array(…), SampleAxes(…), Member(…))] == []` |
| the confound never enters the verdict | the mean missing count subtracted from the difference | `0.09999999999999998 == 0.05499999999999998` |
| the flag is `x`, and every value is reported | any non-empty cell read as flagged | `{…, 4: True}` against `{…, 4: False}` |
| a repeated `#` stops the run | the guard neutered | `Failed: DID NOT RAISE HypothesisError` |
| a fixture disagreeing with its own counts stops the run | `recounted != dict(stored)` → `recounted != recounted` | `Failed: DID NOT RAISE HypothesisError` |
| a short `min_p` list is refused | the length check dropped | `Failed: DID NOT RAISE HypothesisError` |
| **H9p is conditional, not unconditional** | the missingness condition dropped from `_conditional` | U_p reads `share 0.15` against `0.75`, and the verdict inverts |
| H9p's verdict at the registered factors | `<= particular + tolerance` → `< particular` | `'indeterminate' == 'particular_to_site_data'` |
| H9p is `undefined`, not a division | `or` → `and` in the zero-denominator guard | `TypeError: unsupported operand type(s) for *: 'float' and 'NoneType'` — the division the test's name forbids |
| the verdict reads the conditional pair and nothing else | `u_p` computed unconditionally | the two populations' verdicts differ |
| the recomputed categories are the registered definition | durable widened to `support >= member_count - 1` | `At index 3 diff: 'durable' != 'underdetermined'` |
| a claim with no row is unsupported, its missingness absent | a null min(P) counted as support | `{'support': 4} != {'support': 0}` |
| ” (second, for the `counts == [0, None]` line) | `missing_counts` returning `0` rather than `None` | `assert [0, 0] == [0, None]` |
| both blocks serialise | `"claims": joined[:1]` | `assert 1 == 20` |
| ” (second, for the key-set line) | the claim entry rebuilt with `**dict(claim)` | extra key `'min_p'` |
| **`main` runs both hypotheses end to end** | Table 2 read from sheet `Table 1` | `assert 5 == 10` |
| ” (second) | `main` returning 1 | `assert 1 == 0` |
| ” (third) | `"sites": sites[:2]` | `assert 2 == 5` |

**Two mutations are recorded as having been replaced or strengthened, rather than quietly swapped.**

- The join guard's first mutation simply deleted the `raise`. The test failed — but with `KeyError: 77` from the dict lookup one line below, a crash rather than a named refusal, so the guard's value was partly carried by the line after it. It was replaced with the plausible wrong implementation (`.get(number, False)`, an unjoined claim read as unflagged), which fails as `DID NOT RAISE`.
- `counts == [0, None]` and the claim key-set assertion each needed a **second, line-specific** mutation, because the obvious one reddens an earlier assertion in the same test and this one never runs. That is the stricter standard `tests/test_tautology_sweep.py` records for its own entries, applied here.

### The defect a test found

`test_h9p_verdict_at_the_registered_factors` failed on first run: `U_p = 0.64` against `0.8 × U_s` with `U_s = 0.8` gave `indeterminate`, because `0.8 * 0.8` is `0.6400000000000001` in binary floating point. A case sitting exactly on a registered threshold was being pushed off it by the representation — in a hypothesis whose thresholds are *"judgement, fixed here, and not moved after measurement"*. The same shape was already handled on H5c's side (`0.5 - 0.4` is `0.09999999999999998`); the fix extends the same 1e-9 slack to H9p's two factors, with the bound on what it can merge computed rather than asserted. **The test was written before the code was believed correct, and it was not.**

---

## The output's shape

`tests/fixtures/pxd026748_h5c_h9p.json`, written by `main` and **not committed by this turn** — this container cannot produce it.

```
dataset, registration, published_file, published_content_hash, published_sheets,
digly_file, digly_content_hash, shotgun_file, shotgun_content_hash,
reconstruction_fixture, reconstruction_fixture_hash, note, generated_by,
generated_under { generated_at, commit, working_tree_clean, python, numpy,
                  primary_threshold, gg_population_rows,
                  fixture_consistency { members, claims, recomputed_counts,
                                        stored_counts, agrees } }
h5c {
  population { clusters, excluded_cluster, claims, excluded_claims, by_cluster }
  flag { rule, column, join_rule, values_as_found }
  group_sizes { flagged, unflagged }
  durable_proportion { flagged | unflagged { numerator, denominator, share } }
  difference, verdict, undefined_reason
  confound_missing_values { note, by_group { flagged | unflagged { <count>: n } } }
  claims[288] { deposit_id, published_row, cluster, uniprot_id, lysine_position,
                support, category, flagged, missing_values }
}
h9p {
  join { table_2_ids_read, exposure, unmatched, ambiguous, not_reaching_the_test,
         unmatched_ids, ambiguous_ids, not_reaching_ids, members,
         rows_after_filters, rows_reaching_the_test }
  exposure, site_claims
  conditional { u_p | u_s { numerator, denominator, share } }
  verdict { outcome, reason, particular_at_or_below, general_at_or_above }
  descriptive { unconditional_underdetermined { protein | site }, complete_rows { protein | site } }
  proteins[] { accession, support, category, missing_values }
  sites[288]  { deposit_id, cluster, support, category, missing_values }
}
```

Every figure is recomputable from what is kept: each claim and each exposure protein carries the support count and the missing-value count the proportions were formed from. The 360 per-member `min_p` values are **not** copied — they stay in the reconstruction fixture, whose sha256 this file pins.

---

## E1 and E2

**E1 — held.** The base suite was measured here at `c48d099` before anything was written: **775 passed, 14 skipped**, exactly the reviewer's figure. The final suite is **793 passed, 14 skipped**, and this turn adds 18 tests: 775 + 18 = 793, with the skips unmoved at 14. The 14 skips are the raw-store tests this container cannot run.

**E2 — held.** One existing test module changed, `tests/test_tautology_sweep.py`, and only in the way E2 allows: **three `PINNED` classifications**, named here.

| entry | classification |
|---|---|
| `counts == [0, None]` | `counts` is bound from `missing_counts(...)`; the right side is a literal the test wrote. Evidence is the line-specific mutation above. |
| `code == 0` | `main`'s exit status against a literal. Evidence: `main` returning 1. |
| `len(written['h9p']['sites']) == len(CLAIM_IDS)` | a length of what was written against the length of the claim list the test supplied. Evidence: `"sites": sites[:2]`. |

None is the `INSTANCES` class, and the distinguishing test was applied rather than assumed: an instance is one whose own scope stays **green** under the mutation, and each of these reddens its own test.

**The sweep's floor was not touched**, as this turn's out-of-scope list requires. It reads `modules >= 49 and asserts >= 1693`; the surface is now 50 modules and 1,749 asserts, so both figures sit above it and the guard passes unchanged. **That gap is slack of exactly the kind the module's own comments describe**, and it is left as found because moving it is out of scope this turn. It is named here so the next turn to touch that file does not have to rediscover it.

**No id pin moved.** No existing assertion was changed, weakened or removed.

---

## `CLAUDE.md` point 1 — every check, at its target, at its actual result

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **793 passed, 14 skipped** |
| `pytest tests/test_schema.py` | that module | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed** |
| `ruff format --check` | `bzk tests` | **111 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 111 source files** |

Every command was run under `.venv/bin/python`. The targets are `bzk tests` and not the whole repository: `ruff check .` additionally covers the three notebooks, which are deliberately out of scope permanently and were not run here.

**Point 2 — the change did what it claims, checked directly.** Each of the eighteen tests was made to fail with a named mutation, every mutation confirmed applied by reading the file back, and every one reverted; the figures above come from the green run after the reverts. The one end-to-end test executes `main`, `gg_matrix` and `shotgun_family` over synthetic bytes, so the IO seam is exercised rather than inferred from the pure tests passing.

**Point 3 — what this turn does not cover.**

- **Neither hypothesis has been measured.** No raw store here. H5c's two proportions and its difference, H9p's U_p and U_s, and both verdicts are unknown. The module produces them; this turn produces only the module.
- **The published sheets' header spellings are still unverified.** Table 2's id column and Table 1's flag column are located by content and refused by name with the header printed; `main` takes both as overrides. Turn 16 recorded the same gap, and the real run has since resolved Table 2's and Table 3's — Table 1's flag column is the one that has not been read by any run yet.
- **`tests/fixtures/pxd026748_h5c_h9p.json` is not committed**, so nothing guards the fixture's shape against the generator. That is a turn that needs the fixture to exist first, as turns 13, 15 and 16 each recorded for theirs.
- **The end-to-end test establishes the seam, not the figures.** Its synthetic Table 1 and Table 2 are written by the test, so the verdicts it produces are about synthetic bytes. The arithmetic is established by the seventeen pure tests, which compare against values written by hand.
- **H9p's site-grain missingness is read from the GG deposit, not from the reconstruction fixture**, because the fixture does not record it. The two must agree by construction — the same `_filter` population through the same `pipeline` — and that agreement is enforced by reuse rather than by an assertion, since there is no second number to compare against.
- **The tautology sweep's floor is stale and was left so**, per the out-of-scope list.
- **Nothing is written to the graph.** No `Analysis`, no `Imputation`, no result node; this turn produces a fixture.
- **D7, H10, the anchor decomposition, D3 and attribution are untouched**, and nothing here reads H5c or H9p in D7's terms.

**Point 4 — instructions dropped or partially done.** None. Every item of the prompt's module spec, test list and task list was done: the ten reused functions are imported rather than copied, the IO is injectable, H5c never runs the family, the confound is descriptive, H9p is conditional with an `undefined` case, the seven required tests are present with their mutations, and the sweep classifications are named above. The one deviation from what I expected to write is the 1e-9 threshold tolerance, which is a choice recorded in the module, in the table above and in its own section.

---

## Commits and the push

| commit | subject |
|---|---|
| `12ca971` | `sources:` measure H5c and H9p, with durability read from the committed reconstruction |
| this report | committed alone |

`main` was pushed fast-forward: **`c48d099..12ca971`**. No branch was force-pushed, and no pushed commit was amended or rebased.
