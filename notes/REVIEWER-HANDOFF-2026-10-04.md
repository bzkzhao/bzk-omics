# REVIEWER HANDOFF — 2026-10-04

**Public version.** This file supersedes `notes/REVIEWER-HANDOFF-2026-10-03.md` as the starting
point. That file stays as the record of the day before. **Items it carries that this session did not
touch are not restated here.** Read its §6 (roadmap tensions), §7 (open items) and §8 (caveats)
alongside this file's §6 and §7, which list only what changed.

**Line references** are to `main` at `265beac` (`ONTOLOGY.md` v1.44). Re-verify them against the
current commit before citing.

**§3 is the dated home for the `265beac` run's numbers.** Its §3.3 also pre-registers the next run,
committed here before that run exists. Everything else points to its own home.

---

## 1. Where things stand

| Item | State at `265beac` |
|---|---|
| `main` | `265beac`, pushed. Four commits since `9cf9892` (§2) |
| `ONTOLOGY.md` | v1.44. *Last reviewed* is still 2026-08-31 |
| Checks | Targets per `CLAUDE.md` l.96: `pytest` **897 passed, 14 skipped**; `mypy bzk tests` clean over 117 files; `ruff check bzk tests` and `ruff format --check bzk tests` clean. `ruff check .` is red outside those targets, on the notebooks, `notes/scripts` and `data/frame`, and is out of scope |
| Untracked | On bzk's Mac only: `notes/prompts/22-walk-two-route-independence.md`, carried through a third handoff (§6 step 4) |
| ADRs | 36 files, no change: 24 Accepted, 9 Proposed, 3 Superseded |
| ADR-0036 | D8 **built** at `265beac`. D1–D7 not built |
| PXD055843 ingestion | Unchanged: blocked on the PI's imputation answer (2026-10-03 §7) |

## 2. What this session did

| Commit | What |
|---|---|
| `a9b23d8` | Prompt 26 landed |
| `f1a13fc` | `mypy bzk tests` cleared: 14 errors in 3 files, introduced at `856c3d1` (12) and `819fe7d` (2). Type-only; no test added or removed |
| `ce69808` | Prompt 27 landed |
| `265beac` | ADR-0036 D8 built. Detail below |

**What `265beac` built:**
- per-arm imputation counts on `DifferentialResult`;
- I15's write-time guard for them;
- the whole-arm clause (b);
- `query.graph.substantially_imputed`, the flag's only home in code;
- the differential's sum-reconciliation guard;
- `SiteObservation.n_imputed` retired. It was declared and read but never written.

`ONTOLOGY.md` went to v1.44. No id moved: `tests/test_keys.py` pins a result id minted on `ce69808`'s
tree, and the reviewer confirmed that test passes on `ce69808`.

**Two readings of D8 were made in prompt 27 and accepted with it.** Both are recorded in ONTOLOGY
§6.5.
- **F-a.** §3's absence table holds identifying fields only (`tests/test_schema.py` l.331–334). D8's
  absence rule therefore lives in §6.5, the DDL comment and I15, not in that table.
- **F-b.** D8's *"export carries no mask"* exception names no recorded field. The guard therefore
  enforces `parameters_observed = false` ⇒ all four counts NULL, with no exception.

**Prompt defects, recorded in the `265beac` report:**
- §2.2's stated reason for removing `n_imputed=4` at `tests/test_invariants.py` l.690 was wrong.
  Structural validation does not compare properties with DDL columns.
- F-c said seven tests in the real-graph module. There are eight.
- The prompt said a literal-pinned assertion avoids the tautology sweep. The sweep flags any name
  bound from a call, so four comparisons had to be classified in `PINNED`.

## 3. The `265beac` run on bzk's Mac, 2026-10-04 (dated home)

**Commands** were §6 of `notes/prompts/27-d8-imputation-counted-on-the-result.md`:
1. `python -m bzk.rebuild`
2. `python -m bzk.sources.pxd018299_differential`
3. `git status --short`
4. that section's instrument, extracted from the committed prompt and run unchanged.

**Every prediction was pre-registered** in that committed prompt before the run.

### 3.1 Results against the pre-registration

| # | Kind | Measured | Verdict |
|---|---|---|---|
| M0 | identity | Rebuild unchanged from 2026-10-03 §3: 58 tables; replay 18/40, 18/40, 16/38, 23/57; 32,793 node / 31,349 edge statements; 4,195 site / 4,768 protein observations; 48 refusals; exit INCOMPLETE (`S1_TP`) | held |
| M1 | identity | `[4b]` unchanged: 2,341 → 2,298 → 2,056 → 2,029 → 1,362; 3,997 of 8,172 imputed; 516 up; 12 of 14; 4,090 / 5,450 statements. `git status --short` showed `?? notes/prompts/22-walk-two-route-independence.md` and nothing else | held in substance. **Pre-registration wording defect:** "empty" forgot the known untracked file. The targets fixture was rewritten byte-identical, which is what the line existed to test |
| P1 | identity | 1,362 rows; 1,362 with all four counts; 1,362 with values 3 and 3 | held |
| P2 | identity | 3,997 imputed and 8,172 values, both equal to the fixture | held |
| P3 | structural | (a) **431**; (b) **1,077**; (a) not (b) **0**; (b) not (a) **646**; both arms **0**; flag function agrees on 1,362 of 1,362 | held |
| P4a | identity | 516 significant up | held |
| P4b | reasoned | KO+IFN entirely imputed among the 516: **0** | held |
| P4c | reasoned | WT+IFN entirely imputed among the 516: **468** (90.7%). Predicted ≥ 259, against the 2026-10-03 handoff's wanted direction (*low*) | held; **the wanted direction was not met** |
| P5 | reasoned | Significant-up sites of the 12 recovered genes with WT+IFN entirely imputed: **20 of 21**. OAS2 is 3 of 4; every other gene is all of its sites | **strong form refuted by one site**; weak form held, 12 of 12 genes |

### 3.2 What the run establishes

**The tested population has three shapes.**

The presence rule is ≥ 2 measured in *either* arm, with three replicates per arm
(`bzk/sources/pxd018299_differential.py` l.112–113). That admits exactly three shapes of tested
row, and the measured counts reconcile with the imputation total:

| Shape | Rows | Imputed per row | Imputed |
|---|---|---|---|
| One arm entirely imputed, other fully measured: (b) only, exactly half | 646 | 3 | 1,938 |
| One arm entirely imputed, other with one imputed: (a) and (b) | 431 | 4 | 1,724 |
| No arm entirely imputed | 285 | 1.18 mean | 335 |
| **Total** | **1,362** | | **3,997** |

The 285 and 335 are derived from the measured lines, not measured themselves. §3.3 B1 measures 285
directly.

**Clause (b) is the operative half of the flag on this dataset.**
- (b) flags 1,077 of 1,362 (79.1%).
- (a) alone flags 431 (31.6%).
- Without (b), 646 results with no measured value in one arm would display as *not* substantially
  imputed.

**The significant-up set is predominantly detection asymmetry.**
- 468 of the 516 have no measured WT+IFN value. For those, `log2FC` and the Welch p-value are set
  against a generated arm: downshift 1.8 SD, width 0.3 SD.
- 48 of the 516 rest on at least one measured WT+IFN value. Since (a) ⊆ (b) here, they are exactly
  the significant-up results the flag leaves unset.
- **This does not make the 468 false.** Detection in KO+IFN with absence from all three WT+IFN
  replicates may be the biology. But their effect sizes are not measured ratios.
- P4b's 0 is the same mechanism seen from the other side. An entirely imputed KO arm against a
  measured WT arm cannot produce a positive fold change.

**R1 holds at gene level, not at site level.** Every recovered target has at least one significant-up
site with WT+IFN entirely imputed. One OAS2 site has a measured WT+IFN value. §3.3 A identifies it.

**What the 12 of 14 baseline is.** It reproduces the paper's exemplars under the same family of
imputation. What it reproduces is 20 detection-asymmetry calls and one partly measured comparison.
Describe it that way.

**PI first.** These are population and per-protein results about the PI's lab's deposit. Under
2026-10-03 §8 they go to the PI before any demo.

### 3.3 Pre-registration for the next run (§6 step 2)

**Read-only.** No rebuild or differential is needed: the graph written at `265beac` is the input.

**Command.** Run from the repo root. It extracts and runs the block below unchanged:

```
uv run python -c "import pathlib;t=pathlib.Path('notes/REVIEWER-HANDOFF-2026-10-04.md').read_text();s=t.index(\"<<'EOF'\n\")+8;exec(compile(t[s:t.index('\nEOF\n',s)],'handoff_1004','exec'))"
```

```
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
by_obs = {r[0]: r for r in rows}
fx = json.loads(pathlib.Path("tests/fixtures/pxd018299_platform_targets.json").read_text())
oas2 = next(t for t in fx["targets"] if t["gene"] == "OAS2")
for s in oas2["sites"]:
    if s["adj_p"] is not None and s["adj_p"] < 0.05 and s["log2fc"] > 1.0:
        r = by_obs[s["observation"]]
        print("A", s["site"], f"| log2FC {r[1]:.2f} | adj p {r[2]:.2g}", "| KO+IFN imputed", r[5], "of", r[3], "| WT+IFN imputed", r[6], "of", r[4])
num_full = {r[0] for r in rows if r[5] == r[3]}
den_full = {r[0] for r in rows if r[6] == r[4]}
up = {r[0] for r in rows if r[2] is not None and r[2] < 0.05 and r[1] > 1.0}
down = {r[0] for r in rows if r[2] is not None and r[2] < 0.05 and r[1] < -1.0}
print("B tested", len(rows), "| WT+IFN entire", len(den_full), "| KO+IFN entire", len(num_full), "| neither", len(rows) - len(den_full | num_full))
print("B WT+IFN entire and significant up", len(den_full & up), "of", len(den_full))
print("B significant down", len(down), "| KO+IFN entire", len(down & num_full), "| WT+IFN entire", len(down & den_full))
EOF
```

**Predictions:**

| # | Prediction | Kind |
|---|---|---|
| A1 | Exactly one OAS2 site has WT+IFN imputed < 3 | identity with §3.1 P5 |
| A2 | That site is **K425** | reasoned, **low confidence**. Of the four, K425 has the largest `log2FC` (5.74) and the weakest adj p (0.021, from the fixture). A mixed WT arm inflates variance more than it lowers the mean |
| A3 | Its WT+IFN arm has **2 of 3 imputed**, i.e. one measured value | reasoned. With two measured values, the mean would fall far enough to shrink the fold change |
| A4 | Its KO+IFN arm has **0 imputed** | reasoned. It is a top-ranked up site |
| B1 | WT+IFN entire + KO+IFN entire = **1,077**; neither = **285**; WT+IFN entire and significant up = **468** | identity with §3.1 P3/P4 and §3.2 |
| B2 | **WT+IFN entire > KO+IFN entire** | reasoned. USP18 loss raises conjugation, so more sites should be KO-only than WT-only. No basis for a magnitude, so none is registered |
| B3 | Significant down: KO+IFN entire is **more than half**, and WT+IFN entire is **0** | reasoned. This mirrors P4b and P4c. It is included because it costs one line of the same instrument |

**Reading the result:**
- An identity miss stops the run. It means the graph or the instrument has moved since `265beac`.
- A miss on A2–A4 or B2–B3 is a finding, recorded as measured.

The measured lines get a dated home in the next handoff.

## 4. Corrections to the 2026-10-03 handoff

**1. Its §3 said no other file records the `767e6e4` run's numbers.**
`tests/fixtures/pxd018299_platform_targets.json` `population` records:
- 1,362 tested;
- 516 significant up;
- 3,997 of 8,172 imputed;
- 12 recovered and 13 present.

Prompt 27 and §3.3 compare against it.

**2. Its §1 *Suite* row reported `pytest` and ruff, gave no target for ruff, and omitted mypy.**
- `mypy bzk tests` was red at `767e6e4`, with 14 errors. That is the omission `CLAUDE.md` l.96
  forbids.
- `ruff` is clean only at `bzk tests`.
- Cleared at `f1a13fc`.

**3. Its §7 said several documents name ADRs "through 0032" or "21 invariants".**
- No file in the repository does, apart from that sentence itself.
- "21 invariants" is still correct: I1–I21 are built, and I22 is decided but unbuilt.
- The drift is in notes kept outside the repository.

**4. Its §7 asked to verify Q7 and close it, or say why it stays open.**
- Q7's own body already reads that it was minted as I20 and closed on 2026-08-10.
- Only the heading's strike-through is missing, so this is a mechanical fix.

**5. Its §5 registered "direction wanted: low" for the whole-arm share of the 516.** The measured
share is 90.7% (§3.1 P4c).

## 5. How this session ran

**The four-stage loop was restored for code.**
- The reviewer wrote each prompt after rehearsing it in a scratch clone.
- Claude Code executed.
- The reviewer verified from an independent full clone after each report.
- Rebuild-dependent runs went to bzk's Mac, with predictions committed first.

**The checker stage is not recorded in this session.** If it ran, its audit of prompts 26 and 27
belongs in the next handoff.

**§0.1 failed twice for one reason.** Both prompts reached Claude Code as pasted text and were not
committed. The fix was the same both times: Claude Code wrote the text, checked a reviewer-supplied
sha256 and line count, and landed the prompt as its own commit before rerunning §0. **This is now
standing practice:** every prompt ships with its filename, sha256, line count and landing message.

**Stale bytecode nearly produced false mutation results.** In `265beac`'s first mutation round, two
same-size edits ran against a cached `.pyc`:
- Case 4 stayed red after its restore.
- Case 6a stayed green under its mutation.

Claude Code caught it and reran every case with `-B`, `PYTHONDONTWRITEBYTECODE=1` and a cleared
`__pycache__`. This is the shape `CLAUDE.md` l.97 describes, caught in the act. Mutation runs should
disable bytecode from the start.

## 6. Next, in this order

**1. Land this file** as its own commit (`HANDOFF: …`). Its §3.3 is the pre-registration for step 2.

**2. Run §3.3 on bzk's Mac.**
- Read-only, one command.
- Paste back the A and B lines.

**3. Run `python -m bzk.drift`.**
- The rebuild reports the last check as 20 days old, over 3,013 sequences; the set is now 3,579.
- Paste back its summary.
- **No figures are pre-registered**, because no basis for one exists here. Any drift found is a
  finding, not a miss.

**4. Prompt 22. bzk decides whether it is spent or pending.**
- **Spent:** delete the file. Its subject was withdrawn at `b960c9a`.
- **Pending:** land it as its own commit with a hash check, like prompts 26 and 27.

  It does not stay untracked a fourth time.

**5. Then ADR-0036 step 2: D2 and D3** (`Sample.role` and `bait`; `modality = 'ip_ms'`), as
2026-10-03 §5 sets out.
- The pre-registration is unchanged: 54 Sample ids moved, 0 others, identical differential numbers.
- **Verified since:** the loader gives 54 Samples (12, 12, 12, 18). `Contrast` anchors only on
  `Experiment`. No existing `Experiment` has an IP modality, so `ip_ms` adds a value without moving
  one.
- **One correction for that prompt.** `tests/fixtures/pxd018299_curation_ids.json` pins 18 ids,
  not 12:
  - 4 top-level;
  - 12 `Sample`;
  - 2 `Contrast`.

  The 12 that move are the `Sample` ids.

**Not scheduled, but needs a decision before any demo:** taking §3.2 to the PI.

## 7. Open items — what changed since 2026-10-03 §7

**New:**

- **The real-graph module is gated off.** `tests/test_query_real_graph.py` l.64 requires 2,029
  `SiteObservation`s, and the replay holds 4,195. All eight tests have skipped on every machine
  since about `624d10e` (2026-09-19, the PXD026748 record). That attribution is inferred. Fixing the
  gate means deciding what each test means on a multi-dataset graph.
- **The PXD018299 `Imputation` node has NULL counts.** `pxd018299_differential.py` l.509 passes
  `IMPUTE | {"method": …}`, which does not include `n_values_imputed` or `n_values_total`.
- **D8's mask exception (F-b) is unbuilt.** It stays that way until a producer reads a mask, which
  will need a recorded field.
- **`_require_counts_reconcile` has no committed test.** Its mutation was verified only in Claude
  Code's scratch run.
- **`tests/test_ui.py` l.450 passes the retired `quant.duckdb` reason string.**
- **D8's three prose homes have no mirror test against the guard.** These are §6.5, the DDL comment
  and I15.
- **Stale prose from D8**, enumerated in the `265beac` report and not edited:
  - `ROADMAP.md` l.1322–1327, l.1472–1475, l.2172–2175, l.2252–2253, l.2299–2300;
  - `HANDOFF.md` l.242–243, and l.181 implicitly;
  - adjacent: `ROADMAP.md` l.12548 states the threshold as "more than half" only.

  Corrections go in their own prompt. These are dated logs.
- **No guard checks that mypy was run.** The `f1a13fc` regression lasted two commits under
  report-by-prose. This needs a decision.

**Changed:**

- **The tautology floor is still stale.** It is now `tests/test_tautology_sweep.py` l.1932. It
  asserts ≥ 49 modules and ≥ 1,693 asserts; `265beac` measures 54 and 2,064.
- **Two line numbers moved:**
  - `bzk/sources/protein_groups.py:117` still mislabels SD3;
  - §11 Q7's strike-through: see §4 item 4.

**Closed:**

- **The mypy regression**, at `f1a13fc`.
- **The 2026-10-03 §7.5 whole-arm measurement.** It is now a query, measured in §3.

Everything else in 2026-10-03 §6–§8 stands unchanged.
