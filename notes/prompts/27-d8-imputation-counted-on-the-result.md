# Prompt 27 — Build ADR-0036 D8: imputation counted on the result, per arm, with the whole-arm flag

**Repository:** `main` at the commit adding this prompt, directly on top of `f1a13fc`.

**Governing:**
- `decisions/0036-ip-ms-as-role-tagged-observations.md` D8 (l.290–326), R3 (l.67–76), V6 (l.454),
  and its *Implied changes* (l.362–411).
- `notes/REVIEWER-HANDOFF-2026-10-03.md` §5 step 1 (l.124–142). Its §3 (l.61–88) is the baseline.
- `CLAUDE.md` l.95–99, the four-point close.

**Settled ground** (handoff l.121–122). ADR-0036 as accepted at `2aecd01`, and the `Contrast` build
at `767e6e4`. This prompt builds D8 as accepted. It does not reopen D8, D2–D7, or ADR-0034.

**This is a code and `ONTOLOGY.md` step.**
- No identity changes, so no id moves.
- No ADR is edited: ADR-0036 is `Accepted` and its *Implied changes* stay as written.
- `ROADMAP.md`, `HANDOFF.md` and `notes/` are not edited, apart from this prompt. §5 says what
  happens to their stale lines instead.
- Rebuild-dependent measurement is bzk's, on his Mac, after landing (§6). It is pre-registered here,
  in this committed file, which closes the gap handoff l.65–67 names.

The prompt ends at the report.

---

## 0. Receipt check — answer all of these, then stop and wait

1. **Repository state.**
   - Run `git log --oneline -2` and `git status --short`.
   - HEAD must be this prompt's commit, with `f1a13fc` beneath it.
   - The only untracked path allowed is `notes/prompts/22-walk-two-route-independence.md`.
   - If either check fails, stop.
   - Then run `uv run mypy bzk tests` and the full `uv run pytest`. Expected: mypy `Success` over
     117 files; pytest **881 passed, 14 skipped**. These are the open-of-turn checks (`CLAUDE.md`
     l.102).
2. **D8 as accepted.** Quote ADR-0036 l.296–311 and l.313–316 verbatim. Then state in one sentence
   each:
   - what determines the counts' absence;
   - what the record says about how the flag is shown when the counts are NULL.
3. **Where the absence rule can live.**
   - Quote `tests/test_schema.py` l.331–334 verbatim.
   - Say whether §3's absence table (ONTOLOGY l.142–161) can hold a row for a non-identifying
     field. ADR-0036 l.374 reads *"Absence row as D8"*, so answer this before §2 places it.
4. **The consumers.**
   - Give `git grep -nw n_imputed -- bzk tests` in full. ADR-0036 V6 (l.454) records 1, 5, 2, 1, 1
     and 2 across six files.
   - For each hit, say whether it is a **writer**, a **reader**, or **prose**.
   - Expected: no writer anywhere. `SiteObservation.n_imputed` has been declared and read but never
     written. Confirm or refute that from the producers: `bzk/adapters/`, `bzk/analysis/`,
     `bzk/sources/`.
5. **What else stages results.**
   - List every change-set in `tests/` and `tests/fixtures/` that stages a `DifferentialResult`
     whose `WAS_GENERATED_BY` `Analysis` has `parameters_observed = True`. Give file and line.
   - These are what §2's guard reaches.
   - Include `tests/fixtures/valid_changeset.json`, F3's "valid change-set every check accepts".
     Expected: `dr1`–`dr4`, all under processing analyses.
6. **The real-graph module.**
   - Quote `tests/test_query_real_graph.py` l.60–63 and l.92–94.
   - ADR-0037 l.187 records **4,195** `SiteObservation`s in the current replay, and the gate at
     l.62 requires 2,029. Say what this module does on bzk's Mac today.
   - **Reason from the code only.** Do not run it: the graph is not here.

**Do not start §1 until bzk replies.**

---

## 1. What D8 decides, and the three facts this prompt adds

**D8** (ADR-0036 l.290–326):
- `DifferentialResult` gains four non-identifying `INT64` fields:
  - `n_values_numerator`;
  - `n_values_denominator`;
  - `n_imputed_numerator`;
  - `n_imputed_denominator`.
- Their absence is **determined by the generating `Analysis`'s `parameters_observed`**.
- *Substantially imputed* is flagged when (a) more than half of the result's values are generated,
  **or** (b) either arm is entirely generated.
- Where the counts are NULL, the flag is **undeterminable, and shown as such, never `false`**.
- `SiteObservation.n_imputed` is retired.

The reviewer found three things while writing this prompt. §0 asks you to verify each.

**F-a. §3's absence table cannot hold D8's row.**
- `test_absent_identifying_fields_are_determined_not_contingent` refuses any row whose field is not
  identifying (`tests/test_schema.py` l.331–334). The four counts are non-identifying by D8's own
  words.
- So ADR-0036 l.374's *"Absence row as D8"* has no legal home in §3's table.
- **The rule is recorded instead in:**
  - §6.5;
  - the DDL comment;
  - I15;
  - a write-time guard (§2.2).
- It is **not** added to `schema.ABSENCE` or to §3's table.
- This places the rule; it does not change it. R3's argument (l.67–76) applies unchanged.

**F-b. D8's mask clause names no recorded field.**
- l.303–304 read *"NULL where `false` and the export carries no mask"*.
- Nothing in the graph records whether an export carries a mask, and no producer reads one today.
  The Perseus adapter is the only `false` producer, and it reads none.
- §3's own rule (ONTOLOGY l.140) is that a `determined` absence must name *what* determines it.
- **So the guard enforces `parameters_observed = false` ⇒ all four NULL, with no exception.**
- A future producer that reads a mask must name a recorded field for it, and amend the guard in the
  same change. Do not build that exception here.

**F-c. The real-graph module has been skipping on bzk's Mac since `624d10e` (2026-09-19).**
- Its gate requires 2,029 `SiteObservation`s. The replay holds 4,195.
- So l.94's `substantially_imputed is None` assertion has been asserting nothing on any machine.
- §2.6 updates l.92–94 to D8's state anyway, because leaving it would be a false statement in the
  tree. **The gate itself is out of scope**: it governs seven tests written for a one-dataset graph.
- The Mac verification in §6 therefore does not rely on this module.

## 2. The build

### 2.1 `bzk/ontology/schema.py` and `ONTOLOGY.md` — the declarations, both homes together

**DDL.** Do both in `schema.NODE_TABLES` and ONTOLOGY's DDL:
- Add the four `INT64` columns to `DifferentialResult`, after `adjustment_method`. That is ONTOLOGY
  l.455–464.
- Remove `n_imputed` from `SiteObservation`: ONTOLOGY l.428, `schema.py` l.456.

**DDL comment** on the four columns. It must state:
- they count values entering the test, per arm, and of those how many were generated;
- all four are NULL iff the generating `Analysis` has `parameters_observed = false` (§6.5,
  ADR-0036 D8).

**ONTOLOGY l.117.** Drop `n_imputed` from `SiteObservation`'s non-identifying list.

**ONTOLOGY l.125.** Add the four counts to `DifferentialResult`'s non-identifying list.

**ONTOLOGY l.850.** Replace the sentence with §6.5's statement of D8, covering:
1. The four counts, with the reason they belong to the result and not the observation: imputation
   belongs to the `Analysis`, so one observation imputed by two analyses has two counts.
2. The absence rule as F-b reads it.
3. A dated line saying `SiteObservation.n_imputed` was retired here, and that it had never been
   written.

**ONTOLOGY l.854.** The flag paragraph becomes (a) **or** (b), with ADR-0036's three (b)-only cases
(l.320–323). It also says that NULL counts make the flag undeterminable, shown as such and never as
`false`. Keep the paragraph's second sentence, about the seed, unchanged.

**ONTOLOGY l.963 (I15).** Replace only the last sentence, with exactly this:

> Results are labelled *substantially imputed* wherever they appear when more than half of their
> values are generated **or** either arm's values are all generated (ADR-0036 D8); where the
> generating analysis's `parameters_observed` is `false` the per-arm counts are absent and the label
> is shown as undeterminable, never as false.

**Version.** Bump ONTOLOGY 1.43 → 1.44. Leave *Last reviewed* as it is, as `767e6e4` did.

**`tests/test_schema.py` must pass with both homes moved together.** Do not edit it to make that
true. If a parse test refuses the new DDL text, fix the text.

### 2.2 `bzk/ontology/invariants.py` — I15 gains the counts' rule (the guard)

Extend `_check_I15` (l.463–481). For every `WAS_GENERATED_BY` edge from a staged
`DifferentialResult` to its `Analysis`:

**Where `parameters_observed` is `True`**, all four counts must be present and must satisfy:
- every count is an `int` and not a `bool`;
- `n_values_numerator >= 1` and `n_values_denominator >= 1`;
- `0 <= n_imputed_numerator <= n_values_numerator`;
- `0 <= n_imputed_denominator <= n_values_denominator`.

**Where it is `False`**, all four must be NULL (F-b).

Each refusal names:
- the result id;
- the field, or fields, at fault;
- ONTOLOGY §6.5 and ADR-0036 D8.

Do not add a new invariant number. This is I15's display half acquiring its precondition.

**Tests** go in `tests/test_invariants.py`, one case each, each made to fail per `CLAUDE.md` l.97:
1. processing result missing a count → refused;
2. external result carrying a count → refused;
3. `n_imputed_numerator > n_values_numerator` → refused;
4. `n_values_denominator = 0` → refused;
5. a `bool` where an `int` is required → refused;
6. a valid processing result and a valid external result → both accepted.

For each case, report:
- the mutation that disables its branch;
- proof the mutation applied: read back the file, or quote the failure message;
- the red result under the mutation;
- the green result after restoring it.

**Fixture updates the guard forces.**
- Add counts to `tests/fixtures/valid_changeset.json` `dr1`–`dr4`. Values: `dr1` 3/3/0/3,
  `dr2` 3/3/1/1, `dr3` 3/3/0/0, `dr4` 3/3/2/2, in the order `n_values_numerator`,
  `n_values_denominator`, `n_imputed_numerator`, `n_imputed_denominator`.
- Update every change-set §0.5 listed, the minimum needed to satisfy the guard.
- Remove `n_imputed=4` from `tests/test_invariants.py` l.690. The column no longer exists, so
  structural validation would refuse it.

### 2.3 Producers

**`bzk/analysis/differential.py`.**
- `SiteResult` (l.44–51) gains the four counts as **required** `int` fields.
- `site_change_set` writes them into `row` (l.138–144). That function fixes
  `parameters_observed = True` (l.23–31), so the counts are never optional here.
- Add a sentence to `site_change_set`'s docstring naming D8.

**`bzk/sources/pxd018299_differential.py`.**
- Compute the per-row arm counts from `imputed.imputed_mask` (l.325), split at `numerator.shape[1]`
  exactly as l.326–327 split the values.
- `n_values_*` are the arm widths, `numerator.shape[1]` and `denominator.shape[1]`.
- Pass all four to each `SiteResult` (l.408).
- Before the graph write, refuse with `SystemExit` unless both of these hold:
  - Σ(imputed counts) == `imputed.n_values_imputed`;
  - Σ(value counts) == `imputed.n_values_total`.
  This guard is made to fail too.
- **No new printed line, and no change to the targets fixture writer.** §6's prediction that the
  `[4b]` output and `tests/fixtures/pxd018299_platform_targets.json` come out byte-identical depends
  on both.

**`bzk/adapters/perseus.py` l.552–553.**
- Beside `adjustment_method = None`, set the four counts explicitly to `None`.
- Add a comment citing D8 and F-b: external analysis, no mask read.

**`tests/test_keys.py`.** Add one test showing that a `DifferentialResult` id is unchanged by the
four counts: the same anchors and identifying fields, with and without counts, give equal ids. This
is §3's pre-registered "no id moves" made machine-checkable. Assert both computed ids against one
literal id, not only against each other, so the tautology sweep does not count it as `x == x`.

**`tests/test_analysis_differential.py`.** Assert the counts land on each result node as passed.

### 2.4 `bzk/query/graph.py` — the flag gets its denominator

Add a pure, module-level function with exactly this name and signature. §6's instrument imports it:

```python
def substantially_imputed(
    n_values_numerator: int | None,
    n_values_denominator: int | None,
    n_imputed_numerator: int | None,
    n_imputed_denominator: int | None,
) -> bool | None:
```

- Return `None` if any argument is `None`.
- Otherwise return (a) `2 * (n_imputed_numerator + n_imputed_denominator) > n_values_numerator +
  n_values_denominator`, **or** (b) either arm's imputed count equals its value count.
- This is the rule's only home in code.

Changes to `DifferentialRow` and the query:
- Replace `DifferentialRow.n_imputed` (l.96) with the four `int | None` fields, named as in the DDL.
- In `differential_table`'s query (l.359), return `r.n_values_numerator, r.n_values_denominator,
  r.n_imputed_numerator, r.n_imputed_denominator` in place of `o.n_imputed`.
- Set `substantially_imputed` (l.403) from the function.
- Rewrite the class docstring (l.75–80) and `ImputationState`'s (l.133–135) to the new state.

**Tests** go in `tests/test_query.py`. Remove `n_imputed=1` from the fixture's `SiteObservation`
(l.65), give its `DifferentialResult` counts, and replace l.256's assertion with the computed flag.

Add a parametrised test of `substantially_imputed`. Each case's expected value is a literal:

| Case | nv_num | nv_den | ni_num | ni_den | Expected | Why |
|---|---|---|---|---|---|---|
| 1 | 3 | 3 | 0 | 0 | `False` | nothing generated |
| 2 | 3 | 3 | 0 | 3 | `True` | (b) only: 3 of 6 is not more than half (ADR l.321–322) |
| 3 | 2 | 2 | 0 | 2 | `True` | (b) only: the 2-vs-2 case (l.320) |
| 4 | 3 | 1 | 0 | 1 | `True` | (b) only: the single imputed bead arm (l.323) |
| 5 | 3 | 3 | 2 | 2 | `True` | (a) only: 4 of 6, neither arm entire |
| 6 | 3 | 3 | 1 | 2 | `False` | 3 of 6 and neither arm entire |
| 7 | 3 | 3 | None | 2 | `None` | undeterminable |
| 8 | None | None | None | None | `None` | external |

### 2.5 `bzk/ui/app.py`

- Replace the `"n_imputed"` column (l.229) with one `"imputed (num · den)"` column, rendering
  `f"{ni_num}/{nv_num} · {ni_den}/{nv_den}"`.
- Where the counts are `None`, render `_unknown(...)` with the reason: *"counts not recorded — the
  analysis ran outside the platform (parameters_observed = false), so its mask is unrecoverable
  (ADR-0036 D8)"*.
- Use the same reason in `"substantially imputed"`'s `_unknown` (l.222–225), replacing the
  `quant.duckdb` reason, which is no longer true.
- Update `tests/test_ui.py` only where it reads those columns.

### 2.6 Docstrings and the real-graph module

- **`bzk/stats/imputation.py` l.8 and l.27.** Name the result's per-arm counts in place of
  `SiteObservation.n_imputed`.
- **`tests/test_query_real_graph.py` l.92–94.** Replace the assertion and its comment with D8's
  state:
  - every row carries all four counts;
  - `n_values_numerator == n_values_denominator == 3`;
  - Σ imputed and Σ values equal the targets fixture's `population` `n_values_imputed` and
    `n_values_total`;
  - `substantially_imputed is not None` on every row.

  Say in the comment that the module is gated off on the current replay (F-c). Leave the gate at
  l.62 untouched.

**After §2, `git grep -nw n_imputed -- bzk tests` must print nothing.** The retired name's history
lives in ONTOLOGY §6.5, not in code.

## 3. Pre-registration — this container

| Check (target) | Before (`f1a13fc`) | After, predicted |
|---|---|---|
| `uv run mypy bzk tests` | Success, 117 files | Success, 117 files |
| `uv run pytest` (full) | 881 passed, 14 skipped | all pass; **14 skipped** (the count of passes rises with the new tests; state it) |
| `uv run pytest tests/test_schema.py` | 20 passed | 20 passed |
| `uv run ruff check bzk tests` | clean | clean |
| `uv run ruff format --check bzk tests` | 117 formatted | 117 formatted |
| `git grep -nw n_imputed -- bzk tests` | 12 lines in 6 files | **no output** |
| `git diff f1a13fc -- tests/fixtures/pxd018299_curation_ids.json tests/fixtures/pxd018299_platform_targets.json` | — | **empty**: no pinned id moves, and the targets fixture is untouched |
| `tests/test_tautology_sweep.py` `sweep()` | 54, 2,045 | 54 modules (no new module); asserts rise. State the figure. The floor at l.1916 stays untouched (carried defect) |

If any prediction fails, stop and report. Do not adjust the code or the test until it matches.

## 4. Commit and report

**One commit**, fast-forwarded onto `main` as in prompt 26, with this message:

`ADR-0036 D8 built: per-arm imputation counts on DifferentialResult (NULL iff parameters_observed=false, guarded in I15), substantially_imputed = (a) or whole-arm (b), SiteObservation.n_imputed retired; ONTOLOGY v1.44; no id moved`

**Files.** The expected set:
- `ONTOLOGY.md`;
- `bzk/ontology/schema.py`, `bzk/ontology/invariants.py`;
- `bzk/analysis/differential.py`, `bzk/sources/pxd018299_differential.py`, `bzk/adapters/perseus.py`;
- `bzk/query/graph.py`, `bzk/ui/app.py`, `bzk/stats/imputation.py`;
- `tests/fixtures/valid_changeset.json`;
- the `tests/` modules named in §2.

Any other file under `bzk/` or `tests/` needs a reason in the report. Touch nothing outside
`ONTOLOGY.md`, `bzk/` and `tests/`.

**Report:**
- the commit hash;
- §0's answers as given;
- §3's table with "After" measured;
- the mutation evidence for the six I15 cases and the differential sum guard;
- the full diff of `ONTOLOGY.md`;
- `git diff --stat f1a13fc`;
- the four-point close (`CLAUDE.md` l.96–99).

Then stop.

## 5. Stale prose this step leaves, enumerated rather than edited

Report every line in `ROADMAP.md` and `HANDOFF.md` that states, as a present fact, either of these:
- that `substantially_imputed` is always `None`;
- that `SiteObservation.n_imputed` carries the numerator.

The reviewer's grep finds `ROADMAP.md` l.1322–1327, l.1472, l.2082, l.2120, l.2172, l.2252, l.2299,
and `HANDOFF.md` l.181 and l.242. Confirm, extend or correct that list. These are dated logs, so
they are corrected in their own prompt, not here.

## 6. For bzk's Mac, after landing — pre-registered now, run later

Claude Code does not run this section. It is here so the predictions are committed before the
measurement exists.

```
git pull --ff-only
uv run python -m bzk.rebuild
uv run python -m bzk.sources.pxd018299_differential
git status --short
uv run python - <<'EOF'
import json
import pathlib

from bzk.query import graph as gq

conn = gq.connect(pathlib.Path.home() / ".bzk-omics" / "graph.kuzu")
aids = gq._rows(conn, "MATCH (a:Analysis) WHERE a.test = 'welch_t' RETURN a.id")
assert len(aids) == 1, aids
rows = gq._rows(
    conn,
    "MATCH (r:DifferentialResult)-[:WAS_GENERATED_BY]->(a:Analysis) WHERE a.id = $id "
    "MATCH (r)-[:RESULT_FOR_SITE]->(o:SiteObservation) "
    "RETURN o.id, r.log2fc, r.adj_p_value, r.n_values_numerator, r.n_values_denominator, "
    "r.n_imputed_numerator, r.n_imputed_denominator",
    id=str(aids[0][0]),
)
fx = json.loads(pathlib.Path("tests/fixtures/pxd018299_platform_targets.json").read_text())
pop = fx["population"]
n = len(rows)
full = [r for r in rows if all(v is not None for v in r[3:])]
print("P1 rows", n, "| all four present", len(full), "| values 3 and 3", sum(r[3] == 3 and r[4] == 3 for r in full))
imp = sum(r[5] + r[6] for r in full)
val = sum(r[3] + r[4] for r in full)
print("P2 imputed", imp, "fixture", pop["n_values_imputed"], "| values", val, "fixture", pop["n_values_total"])
a = {r[0] for r in full if 2 * (r[5] + r[6]) > r[3] + r[4]}
num_full = {r[0] for r in full if r[5] == r[3]}
den_full = {r[0] for r in full if r[6] == r[4]}
b = num_full | den_full
print("P3 (a)", len(a), "| (b)", len(b), "| (a) not (b)", len(a - b), "| (b) not (a)", len(b - a), "| both arms", len(num_full & den_full))
agree = sum(gq.substantially_imputed(*r[3:7]) == (r[0] in a or r[0] in b) for r in full)
print("P3 flag function agrees on", agree, "of", len(full))
up = {r[0] for r in full if r[2] is not None and r[2] < 0.05 and r[1] > 1.0}
print("P4 significant up", len(up), "| WT+IFN entire", len(up & den_full), "| KO+IFN entire", len(up & num_full))
for t in fx["targets"]:
    if t["status"] != "recovered":
        continue
    sig = [
        s["observation"]
        for s in t["sites"]
        if s["adj_p"] is not None and s["adj_p"] < 0.05 and s["log2fc"] > 1.0
    ]
    print("P5", t["gene"], "| sig-up sites", len(sig), "| WT+IFN entire", sum(o in den_full for o in sig))
EOF
```

**Predictions.** Each is marked by kind:
- **[identity]** is forced by construction, so a miss is a defect.
- **[structural]** is derived from the run's fixed parameters.
- **[reasoned]** is a prediction about the data, with its ground stated.

| # | Prediction | Kind |
|---|---|---|
| M0 | **Rebuild.** Every figure in handoff §3 l.69–74 is unchanged: 58 tables; replay lines 18/40, 18/40, 16/38, 23/57; 32,793 / 31,349 statements; 4,195 / 4,768 observations; 48 refusals; exit INCOMPLETE | identity: columns change, no table or statement does |
| M1 | **Differential.** Every `[4b]` line in §3 l.75–81 is unchanged. `git status --short` is empty, because the targets fixture is rewritten byte-identical | identity: §2.3 adds no print and no fixture field |
| P1 | **1,362** rows, **1,362** with all four counts, **1,362** with values 3 and 3 | identity: 8,172 = 1,362 × 6 |
| P2 | imputed **3,997** = fixture; values **8,172** = fixture | identity: §2.3's write-time guard enforces it |
| P3 | (a) ⊆ (b): **(a) not (b) = 0**, and **both arms = 0**. The flag function agrees on **1,362 of 1,362** | structural: `PRESENCE_MIN = 2` *either* with three replicates per arm (`pxd018299_differential.py` l.112–113) leaves one arm with ≤ 1 imputed value, so (a)'s ≥ 4 of 6 needs the other arm entire, and both arms cannot be entire |
| P4a | significant up = **516** | identity, with the fixture |
| P4b | **KO+IFN entire among the 516 = 0** | reasoned: an entirely imputed KO arm sits about 1.8 SD below the observed mean, against a WT arm with ≥ 2 measured values, so its log2FC is negative |
| P4c | **WT+IFN entire among the 516 is more than half (≥ 259)**. This is **against** the handoff's wanted direction, *low* (l.141, l.209) | reasoned: R1 (none of the fourteen targets has a measured WT+IFN arm), and the burden finding that downshifted imputation inflates effect size. A log2FC > 1 is cheapest to reach with an absent WT arm |
| P5 | R1, strong form: all **21** significant-up sites of the 12 recovered genes have WT+IFN entire. Per gene: ADAR 1/1, EIF2AK2 3/3, DDX58 2/2, DDX60 1/1, DHX58 1/1, OAS2 4/4, IFIH1 1/1, STAT1 2/2, PSMB10 1/1, PSMA7 2/2, PSME2 1/1, TAP1 2/2. Weak form, at least one per gene: 12/12 | reasoned: R1 (handoff l.141–142). The 21 site counts are read from the fixture and are identity |

**Reading the result.**
- An identity or structural miss stops everything: it is a defect in §2.
- A reasoned miss is a finding, recorded as measured.
- A P4c that comes out *low* is the handoff's wanted direction and refutes the reviewer's reasoning.
  Record it that way round.

**Where the result goes.** The measured lines go into the next reviewer handoff as a dated home.
Under handoff l.61–67, that is the only home they get.

## Out of scope

- **The real-graph module's gate** at `tests/test_query_real_graph.py` l.62 (F-c). It needs its own
  prompt, and that prompt must decide what each of the seven tests means on a multi-dataset graph.
- **`Imputation.n_values_imputed` / `n_values_total`.** The PXD018299 differential's
  `Imputation` node never receives them: `imputation=IMPUTE | {"method": ...}` at
  `pxd018299_differential.py` l.482 passes neither, so both are NULL in the graph. Found while
  writing this prompt; a separate item.
- **D8's mask exception** (F-b), until a producer reads a mask.
- **The stale prose** §5 enumerates.
- **ADR-0036 D2–D7**, the concordance writer, and §11 Q15.
- **ADR-0034's review.** This build adds no fourth instance of its rule. D8's instance is R3's
  third, already counted.
- **The carried defects:**
  - the tautology floor at l.1916;
  - `protein_groups.py:117`'s SD3 label;
  - §11 Q7's unstruck heading;
  - prompt 22;
  - a guard that mypy ran.
