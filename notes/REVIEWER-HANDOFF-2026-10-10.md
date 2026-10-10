# REVIEWER HANDOFF — 2026-10-10

**Public version.** This file supersedes `notes/REVIEWER-HANDOFF-2026-10-09.md` as the starting
point. That file stays as the record of the day before.

**ADR-0038 is built.** D1–D5, D6-revised (a, b, and both halves of c), D7 at write time, at the
producer and in the display, and D8 — eight decisions, two records, four prompts, seven Mac runs,
closed over 2026-10-07 to 2026-10-10. §6 is the first planning section since `ebc0750` that is not
about ADR-0038.

**What is not restated here.** Items the earlier handoffs carry, which this session did not touch,
are not repeated. Read this file's §6 and §7 alongside:
- 2026-10-09 §7 (this file's §7 says what changed);
- 2026-10-07 §6.7, for order items 3–5;
- 2026-10-05 §7, 2026-10-04 §7, 2026-10-03 §6–§8.

**Line references** are to `main` at `fa3ffca` (`ONTOLOGY.md` v1.48). `bzk/query/graph.py` grew by
287 lines and `bzk/ui/app.py` by 37, so **a line reference into either taken from a handoff dated
10-09 or earlier is stale**. This file's own references were read at `fa3ffca`.

**Dating.** The session ran 2026-10-09 to 2026-10-10. The build landed on 10-09; §5's Mac query
ran late on 10-10.

---

## 1. Where things stand

| Item | State at `fa3ffca` |
|---|---|
| `main` | `fa3ffca`, pushed. Two commits since `1c7fa98`; **sixteen since `89ffb84`**, which is the whole ADR-0038 arc |
| `ONTOLOGY.md` | **v1.48** |
| Checks | `pytest` **982 passed, 14 skipped** in the reviewer's container. Add six for bzk's Mac — the environment split of 10-08 §4.4. `pytest tests/test_schema.py` 20 passed; `mypy bzk tests` clean over 117 files; both `ruff` targets clean |
| ADRs | 38 files: 26 Accepted, 9 Proposed, 3 Superseded |
| **ADR-0038** | **Fully built.** Nothing of it is outstanding |
| ADR-0039 | Accepted and built |
| Graph on bzk's Mac | Current. Cold-rebuilt at `ce9e83e`, differential re-run at `402fce8`, read-only queries at `4724046` and `fa3ffca` |
| PXD055843 ingestion | Still blocked on the PI's imputation answer and I15's seed. **The adapter, its proof and the untested-row machinery are all built and waiting** |

## 2. What this session did

Two commits: `ede3c72` (prompt 32) and `fa3ffca` (the build, `author=Claude, committer=Claude`).

**What `fa3ffca` builds:**
- **`_check_I4`'s third clause** — a result carrying `RESULT_FOR_PROTEIN` must be `not_applied`.
  It reads grain only, never kind, because kind is not visible at write time.
- **D7's label table, homed in `ONTOLOGY.md` §8** under a widened I4 ("at either grain"), with
  `bzk/query/graph.py`'s `I4_LABELS` as its guarded copy. **Eighteen cells — *either IP kind* is
  two — of which six are labelled and twelve refused.**
- **`UnlabelledCell`**, raised with the triple named and **nothing substituted**.
- **Every `DifferentialRow` carries `grain`, `contrast_id`, `kind` and `adjustment_label`.** Kind
  comes only from `invariants.contrast_kind`, cached per contrast.
- **`untested_rows`**, comparing per contrast the observations with no result against
  `Analysis.rows_untested_json`: equal gives `UNTESTED` and the label, unequal gives `MISMATCH`
  naming both numbers and **no label**, a NULL count on an external analysis gives `NOT_RETAINED`,
  and a processing or curation analysis gives `applies=False`.
- **The UI** drops `protein_adjusted or "—"` for `adjustment_label`, and gains a "Rows the source
  analysis did not test" block where a mismatch renders as an error.

**Three judgements the build made that the prompt did not specify, all kept:**
- **A contrast with no `CONTRAST_IN_EXPERIMENT` anchor is refused, not read as `modality` NULL.**
  `contrast_kind` would accept NULL as non-IP — a default where the graph says nothing. Mutation
  P5 shows nothing else catches it.
- **`contrast_kind`'s I22 propagates uncaught.** A result whose kind cannot be derived has no cell,
  which is the no-fallback case. P6 shows that catching it and defaulting to `condition` passes
  every other test.
- **"Untested" is deliberately not an `Absence`.** It is a positive finding about observations that
  are present, not a reason a query came back empty.

## 3. Dated home — prompt 32's runs

**Container, at `fa3ffca`.** D1–D6 held. Nine mutations (P1–P9), each read back, fired and
reverted, the working-tree diff hash unchanged across the run.

**Re-measured independently in the reviewer's clone**, not taken from the report:
- all **18** (grain, kind, state) triples enumerated: exactly **6** in `I4_LABELS`, **12** absent
  and raising;
- the six labelled cells match D7's table, *abundance — no adjustment defined* for
  protein × `condition` included;
- **the mirror guard fires**: editing `stoichiometry-uncorrected` in the code map reds
  `test_the_label_table_mirrors_ontology_section_8` and the whole-table test. Tree restored
  byte-identical;
- `properties(` and `RETURN *` in `bzk/query/graph.py`: still **0** and **0**.

**Mac, 2026-10-10, read-only query.** `differential_table` over the platform `Analysis`:

```
absence: None | rows: 1362
Counter({('site', 'condition', 'not_applied', 'stoichiometry-uncorrected'): 1362})
```

All **1,362** results in one cell, as pre-registered. `git status` clean but for the deferred
prompt 22. **The untested display was not exercised**: no Perseus result is in the graph and none
can be until PXD055843 unblocks, so on real data it is untested, not passing.

## 4. Corrections

### 4.1 To prompt 32 §2.2 — I4's closing sentence could not survive the widening

I4 ended *"`not_applied` is labelled *stoichiometry-uncorrected* in every view and export."* Once
the table makes the label depend on grain and kind, that sentence is true only at site grain. The
build moved the claim **into** the table rather than leaving it beside — which the prompt should
have said and did not. The build raised it in §0 before writing.

### 4.2 To the reviewer — a line reference given from a measurement, not from the file

The stale comment in `bzk/analysis/differential.py` was reported as l.148, from M9's output. M9
measured it when the file was shorter; it is at **l.163** at `fa3ffca`. Left as instructed, with
its scope now stated: *true at site grain, which is all that module writes; the general claim lives
in `ONTOLOGY.md` §8's table*.

This is the 10-08 rule landing on the reviewer: **a line reference is a measurement with a shelf
life**, and one taken out of an older measurement's output is already second-hand.

### 4.3 To prompt 32's edit list — `bzk/query/__init__.py` had to move

`untested_rows` and its types are exported there, because the UI may import only `bzk.query` and
`tests/test_query_absence_coverage.py` classifies every name in `__all__`. Reaching the query
through `query.graph` would have skipped that guard. Two stale counts in that file's docstrings
were corrected with it.

## 5. How this session ran

**The receipt check earned its place, for the fourth time.** Prompt 32's §0 produced five findings
before a line was written, including the one in §4.1 and the fact that `bzk/ui/app.py`'s
`protein_adjusted or "—"` was the exact fallback shape the prompt forbade, sitting in the line the
label replaces — now `adjustment_label` at l.245.

**A countable read more carefully than the prompt framed it.** §0.2 asked how many cells the table
has. The record prints five rows; the answer is **18 cells**, because *"site | either IP kind"* is
two kinds. A build that counted 15 would have missed six refused cells and still passed every test
it wrote.

**Two refusals guard states the write path cannot produce.** The missing-anchor and read-time-I22
refusals exist for a store changed outside `write_change_set`. The tests reach them by deleting
edges directly, and each says so. That is the right way to test an unreachable state: produce it
deliberately and record that you did.

**One assumption stated before it bit.** The untested derivation counts every observation reported
by the `Dataset`s an analysis `USED`, so **two external analyses sharing one `Dataset` would share
that population**. True of every producer today, guarded by nothing, and named in the build's own
point 3 rather than found later.

**The series' three standing rules, unchanged and still earning their keep:**
- *measure the thing you add, not only the thing you were told about* (10-07);
- *a line reference is a measurement with a shelf life* (10-08, and §4.2 here);
- *a scope is a measurement too — grep the repository, not the file* (10-09).

## 6. Next — the first planning round since ADR-0038

Nothing here is blocked by anything else. The three in **(A)** are small, machine-checkable, and
close classes this series identified but did not guard; **(B)** is the next real ingestion; **(C)**
waits on the PI.

### (A) The guards this series named and did not build — one prompt, or three

1. **The one-composition-site rule has no guard** (`bzk/adapters/maxquant_sites.py`). `_site` broke
   it unnoticed until prompt 30 routed it through `_compose`. An AST check that only `_compose`
   builds a family-prefixed header in that module would close it.
2. **`site_change_set` does not check that its `arms` belong to its `contrast`.** `ContrastArms`
   carries no contrast id, so a caller can pass a mismatched pair and nothing notices.
3. **A blank or non-numeric statistics cell raises a bare `ValueError`** naming neither row nor
   column (`bzk/adapters/perseus.py`). Pre-existing on Difference, p and q; inherited by the
   statistic column rule (a) reads.

All three are the same shape: *a rule the code follows and nothing enforces*. They would sit
naturally in one prompt.

### (B) Order item 3 — PXD018299's `ISG15_interactome`, the first real IP ingestion

Platform-run, IP vs IP. It needs **the protein-groups binding function** and **a protein-grain
internal differential writer**, and it is the first thing that will exercise D2's `ip_ms` rows,
I22's non-`condition` kinds, and D7's protein-grain labels on real data rather than constructed
fixtures. ADR-0038 M8 is its open question: *the protein-groups adapter drops a family it cannot
reach from the mapping keys, silently* — an I11 question this build must answer.

### (C) Blocked, and why

- **PXD055843 ingestion** — the PI's imputation answer and I15's seed. Everything else for it is
  built.
- **Order item 4, PXD055843 S3** — the PI and ADR-0032.
- **ADR-0032 (Proposed) should take D6-revised (c) into its review** (ADR-0038 l.399). Still not
  done, and now overdue: (c) is built.

### Housekeeping
- **Seventeen `claude/*` branches on the remote**, several stale. (The 10-09 handoff said
  eighteen; that counted `main` alongside them. Measured at `fa3ffca`:
  `git ls-remote --heads origin | grep -c claude/` is 17.) `CLAUDE.md` says development lands
  directly on `main`.
- **`bzk/sources/pxd055843_perseus.py`'s module docstring** does not say untested rows mint no
  result. Stale since `4724046`.
- **No export module prints `protein_adjusted`**, so I4's *"every view and export"* is enforced by
  the UI alone. If an export path is ever written, the label goes with it.

## 7. Open items — what changed since 2026-10-09 §7

**Closed:**
- **ADR-0038, in full.** D7's display half and D6-revised (c)'s display half were the last two.
- 2026-10-09 §6's whole brief.

**Changed:**
- **The untested display exists but is unexercised on real data** — moved from *not built* to
  *built, waiting on PXD055843*.
- **I4 now covers both grains**, and its label table has a home and a guarded mirror.

**New:**
- **The untested derivation assumes one external analysis per `Dataset`** (§5). Unguarded.
- **Read-time refusals for states the write path cannot produce** — missing anchor, inconsistent
  arms. Deliberate, tested, and worth knowing about before someone "simplifies" them.

**Unchanged and still open:** the three guards in §6(A); `_literal_reads`' blindness to
`json.loads(...)["contrast"]`; the protein-groups binding (M8); `write_cells` over-reporting (M11);
the drift checker reporting failed fetches as drift; F-b generalised; F-d; R6's prefix-only check;
the stale tautology floor; a background-enrichment concordance basis value; the D2/D3
invariant-level check; **I22's reliance on the loader being the only `Contrast` minter**.

**Questions for the PI, collected.** None blocks §6(A) or §6(B); the first blocks PXD055843:
1. Did imputation run on S1 (I15's seed)? *(open since September.)*
   `analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` `unresolved[1]` states the block;
   `curation_PXD055843.json` `unresolved[2]` states the I15 requirement only.
2. Where the untested rows come from — 27 on S1, confirmed by the accepted rule (10-09 §4.1).
   Recorded in no `unresolved` entry; new from ORIGIN.
3. s0 for S1's test. `analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` `unresolved[0]` and
   `curation_PXD055843.json` `unresolved[1]`.
