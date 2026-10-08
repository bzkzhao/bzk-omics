# REVIEWER HANDOFF — 2026-10-08

**Public version.** This file supersedes `notes/REVIEWER-HANDOFF-2026-10-07.md` as the starting
point. That file stays as the record of the day before.

**What is not restated here.** Items the earlier handoffs carry, which this session did not touch,
are not repeated. Read this file's §6 and §7 alongside:
- 2026-10-07 §6.7 and §7 (this file's §7 says what changed);
- 2026-10-05 §7, open items;
- 2026-10-04 §7, and 2026-10-03 §6–§8.

**Line references** are to `main` at `ce9e83e` (`ONTOLOGY.md` v1.46). Prompt 29 moved
`bzk/curation/loader.py` and `bzk/ontology/invariants.py` substantially, so **every line reference
taken from a handoff dated 10-07 or earlier is stale in those two files**. Re-verify before citing;
this file's own references were read at `ce9e83e`. Module names carry their package path
throughout, because two modules are named `store.py` and only `bzk/ontology/store.py` is on the
write path.

**Dating.** The session ran from 2026-10-07 evening to 2026-10-08. Runs are dated by their
position in the commit chain.

**ADR-0038 remains the dated home for the figures it produced.** This file states one set of new
measurements — prompt 29's rehearsal and build (§3) — and names where each was taken.

---

## 1. Where things stand

| Item | State at `ce9e83e` |
|---|---|
| `main` | `ce9e83e`, pushed. Six commits since `a83a3f7` (§2) |
| `ONTOLOGY.md` | **v1.46**, last reviewed 2026-10-08 |
| Checks | Run at `ce9e83e`: `pytest` **937 passed, 14 skipped**; `pytest tests/test_schema.py` 20 passed; `mypy bzk tests` clean over 117 files; `ruff check bzk tests` and `ruff format --check bzk tests` clean. **The skip count is environment-dependent — see §4.4** |
| ADRs | 38 files: **26 Accepted**, 9 Proposed, 3 Superseded |
| ADR-0038 | Accepted. **D1, D2, D4 and D8 built** at `ce9e83e`. D5, D6-revised and D7 remain unbuilt |
| ADR-0039 | **Accepted** at `6b7b848`, as it stood at `e356356`. Its guard amendment is **built** in `ce9e83e` |
| Graph on bzk's Mac | Still built at `190e696` and now **behind**: `ce9e83e` changes the loader and adds two rel tables. §5 is the cold rebuild that catches it up, and it has not run |
| Content store | PXD055843 S1 and S3 both present under their recorded digests |
| PXD055843 ingestion | Still blocked: the PI's imputation answer and I15's seed, stated at `data/curation/analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` `unresolved[1]` |

## 2. What this session did

Six commits. The first five were landed by bzk with `git am`; **`ce9e83e` was committed and pushed
by the build session itself** (`author=Claude, committer=Claude`), which is a fourth authorship
class — see §5.

| Commit | What |
|---|---|
| `fe06ca8` | `test_pxd018299_h10`: the interpreter and `numpy` version strings dropped from the attempt digests, both pins re-measured (§4.1) |
| `e356356` | ADR-0039 landed `Proposed` |
| `6b7b848` | ADR-0039 accepted; status pins 25/10/3 → 26/9/3 |
| `a5515e9` | Prompt 29 committed |
| `4fe7757` | Prompt 29's §0.6 citation corrected (§4.5) |
| `ce9e83e` | **ADR-0038 D1+D2+D4+D8 built**; ADR-0039's pinned exception built; ONTOLOGY v1.45 → v1.46 |

**What `ce9e83e` builds,** in one line each (ADR-0038 and ONTOLOGY are authoritative):
- **D1.** Every `contrasts_of_interest` entry carries `numerator_samples` / `denominator_samples`,
  lists of the record's own `mapping` keys verbatim. The loader resolves them by exact membership
  and refuses nine distinct faults, including an unknown key in a contrast entry.
- **D2.** **I22** minted, as an entry in `invariants._CHECKS`, so it runs at every `validate` call
  and not only the loader's. `role` gains `isotype_control`; the R7 check widens to
  `antibody` NULL unless `role ∈ {'ip', 'isotype_control'}`.
- **D4.** `NUMERATOR_SAMPLE` / `DENOMINATOR_SAMPLE`, `Contrast → Sample, MANY_MANY`,
  **non-identifying**, written only by the loader. 58 → **60** tables.
- **D8.** Every contrast declares both arms; no optional form.
- **ADR-0039.** The shape guard admits one pinned exception, keyed on the pair, its endpoints and
  its multiplicity.
- **The `_SAMPLE_ROLES` / `_IP_MODALITY` mirror is now guarded** against `ONTOLOGY.md` §5's
  `Sample` DDL comment, closing handoff 10-05 §7's *unguarded mirror*.
- **Q16** minted: must an arm be one condition, and are pooled control arms exempt?

## 3. Dated home — prompt 29's rehearsal and build

**Rehearsal, in a scratch worktree of `dfe6640`, before the prompt was issued.** It built §2.1,
§2.5 and the edge half of §2.2 only. It established I1, I2 and the intermediate failure set, and
it is the reason those were pre-registered as measurements rather than arithmetic.

**Build, at `ce9e83e`, re-measured independently in the reviewer's clone against a detached
worktree at `4fe7757`:**

| | measured |
|---|---|
| **I1** — node ids, all four records, all six labels | **0 gone / 0 new** everywhere |
| **I2** — loader nodes/edges per record | PXD018299 18/40 → **18/52**; PXD026748 18/40 → **18/52**; shotgun 16/38 → **16/38**; PXD055843 23/57 → **23/63** |
| arm edges | **30**, each contrast 3 against 3, agreeing with ADR-0038 M4 |
| **I3** — `tests/fixtures/pxd018299_curation_ids.json` | **byte-identical** to `4fe7757`, `contrasts` block included |
| `tables_created` | 58 → **60** |
| full suite | 908/14 at `4fe7757` → **937/14** at `ce9e83e` |

**The intermediate state held exactly**: with §2.1, the edge half of §2.2 and §2.5 applied but
before the guard amendment and the `test_rebuild.py` pins, the suite gave the four predicted
failures and no others, and `tests/test_schema.py` gave **1 failed, 19 passed** as corrected
(§4.3). Reproducing it needed an edge loop tolerant of arm-less contrasts; that tolerance was
never shipped, because D8 forbids the case.

**33 mutations, every one read back, fired and reverted**, `md5sum`-checked after each batch.
Three did not behave as the build first expected, and all three were real findings — §5.

**Independently re-verified in the reviewer's clone:** I1, I2, I3, the suite count, that the arms
reach neither `props` at mint nor `schema.IDENTITY`, and **the `_CHECKS` mutation** — removing
`"I22": _check_I22` fails `test_I22_runs_in_every_validate_not_only_when_asked` among seven. The
tree was restored byte-identical.

## 4. Corrections

### 4.1 To the 2026-10-07 handoff §1 — the h10 digest, and a class it exposed

`tests/test_pxd018299_h10.py`'s attempt digests hashed `generated_under`, which carries
`platform.python_version()` and `np.__version__`, while `DIGEST_EXCLUSIONS_UNDER` stripped only
`generated_at`, `commit` and `working_tree_clean`. **A `uv` interpreter bump moved the digest with
no behavioural change**, and the failure was indistinguishable from the readouts moving — which is
what the pin exists to detect.

The readouts had not moved: the digest with both version strings stripped is
`ae47810465eb7a0a0ed2f9bd58ea347d278610006949a82d5b19c5b369e2f86c` at `e13f06c` (where
`ATTEMPT_1_DIGEST` was re-measured unchanged) and at `e356356`, under python 3.12.14/numpy 2.5.1
and python 3.13.16/numpy 2.5.3 — one value across two commits and two environments. Fixed in
`fe06ca8`; both pins re-measured.

**The class this exposed, and it is the reusable part.** `tests/test_tautology_sweep.py`'s
`_ARCHIVE_DIGEST_EVIDENCE` carries `green_scope=("-q",)`: its mutated copy runs the **whole
suite**, so *any* unrelated red anywhere makes the sweep fail too, reporting its `test_drift.py`
row as no longer an instance. Two failures, one cause. It cost a worktree at a month-old commit to
tell apart.

- The sweep is **not** at fault and was not edited for this.
- The h10 versions are **excluded rather than asserted separately**, deliberately: an assertion on
  the recorded versions would fail on every upgrade and re-break the sweep the same way. The
  versions each pin was measured under are recorded in prose beside them.
- **Before adding any environment-sensitive assertion anywhere in `tests/`, read this.** The
  coupling is invisible from either file.

### 4.2 To the 2026-10-07 handoff §6.3 — `tests/test_rebuild.py` has three pins, not two

The plan and that handoff both say "two pins". The rehearsal found a third, in a different test:

| Pin | Location at `4fe7757` | Before | After |
|---|---|---|---|
| `tables_created` | l.134 | 58 | **60** |
| `(nodes_staged, edges_staged)` | l.138 | `(18, 40)` | **`(18, 52)`** |
| **`EXPECTED_EDGES`** | defined l.54, asserted l.173, reused l.293 | no arm keys | **+`NUMERATOR_SAMPLE: 6`, +`DENOMINATOR_SAMPLE: 6`** |

`EXPECTED_NODES` does not move. All three moved in `ce9e83e`.

### 4.3 To ADR-0038, ADR-0039 and the 2026-10-07 handoff — the shape-guard figure

All three state the conflict as **2 failed, 18 passed**. That measurement added the DDL *without*
the `schema.py` mirror, and said so. A build that edits both together sees **1 failed, 19 passed**,
and that is what prompt 29 measured. The records are `Accepted` and are not edited; read the
figure as conditional on the mirror being left behind.

### 4.4 To the 2026-10-07 handoff §1 — the suite's skip count is environment-dependent

At `4fe7757` the container reported `908 passed, 14 skipped` and bzk's Mac `914 passed, 8
skipped`; both total 922. Six tests skip in the container and run on the Mac, on local state (the
PXD055843 content store). At `ce9e83e` the container reports **937 passed, 14 skipped**. A check
line is only comparable against a run in the same environment — state which.

### 4.5 To prompt 29 itself, as issued

- **§3's I3 over-reached.** It wrote "`git diff -- tests/fixtures/` is empty". The plan's I3 pins
  only `pxd018299_curation_ids.json`; the wider claim was never measured, and the rehearsal that
  produced the other figures never loaded a fixture. D8 then required arms on
  `curation_synthetic_loadable.json`'s contrast, and the build correctly stopped and asked rather
  than satisfying a false pre-registration. **Both synthetic twins gained the arms**, because their
  own notes state they differ *only* in what is owed, and arms are not what is owed.
- **§0.6's citation went stale between writing and running.** It cited
  `tests/test_decision_index.py` l.73–82 for `ONE_SIDED_SUPERSESSION`; ADR-0039's acceptance commit
  added a transition-log line and shifted it to l.75–84. Corrected in `4fe7757`. **ADR-0039 l.96
  carries the same stale range and is `Accepted`, so it stands uncorrected** — read it as l.75–84.
  The build session first quoted the stale range and asserted it contained the pin, which it did
  not; that is the compound-clause fault in a new place and is why §0 exists.

## 5. How this session ran

**Mutation testing found a hole in the work that produced it.** Removing `"I22": _check_I22` from
`_CHECKS` left the suite green: the loader's own `contrast_kind` call refuses anyway, so no test
proved I22 runs in an *unfiltered* `validate` — the store-write path, which is the whole reason P1
chose an invariant over a loader function. `test_I22_runs_in_every_validate_not_only_when_asked`
closes it. This is `CLAUDE.md` point 2's vacuous-pass shape, found inside the turn that
introduced it.

Two more mutations misbehaved, both informative: the unknown-key mutation failed with
`numerator_samples is absent` rather than the expected text, which **is** ADR-0038 M3's failure and
the reason the key check runs first; and the identity warning's named target was wrong —
`test_the_minted_ids_have_not_moved` never checks `Contrast` ids, the guard that does is in
`tests/test_rebuild.py` l.217.

**A test helper changed meaning, and it was checked rather than waved through.**
`_ip_ms_record()`'s `KO_vs_WT_unstimulated` denominator mixed an `ip` with a control, which I22
correctly refuses, so the helper itself was I22-invalid. Narrowing the denominator to the control
alone makes the record valid **and** exercises both IP kinds from D2's table where it previously
exercised one. Altering a test to satisfy a new rule is the shape that usually means making the
test fit the code; here coverage rose and the docstring says why.

**Bytecode discipline lapsed and was self-reported.** Two late diagnostic scripts ran under
`python -I`, which implies `-E` and therefore ignores `PYTHONDONTWRITEBYTECODE`; twelve
git-ignored `.pyc` files were written. They came after every mutation and suite run, Python
invalidates stale bytecode by source mtime and size, and all twelve were deleted with the final
run leaving none. **`-I` is not a way to disable bytecode.**

**A fourth authorship class.** `ce9e83e` is `author=Claude, committer=Claude` — the build session
pushed its own commit and fast-forwarded `main`, which `CLAUDE.md` permits. The three classes the
10-07 handoff §5 measured still hold for the commits it covered. The 2026-10-07 and 2026-10-08
handoffs are `author=Zhekai Zhao, committer=Zhekai Zhao`.

**The common cause, still being paid.** Of this session's five corrections, three are a clause or a
citation that was true when written and false when read: §4.2's third pin, §4.3's 2/18, §4.5's
l.73–82. The rule the 10-07 handoff added — *measure the thing you add, not only the thing you
were told about* — now has a companion: **a line reference is a measurement with a shelf life.**
Prefer naming the symbol over the line, and re-read any range before quoting it.

## 6. Next — prompts 30, 31, 32

The build plan's shape is unchanged from the 2026-10-07 handoff §6.1, with 29 now done. **Read
that file's §6.4, §6.5 and §6.6 for the scope of each**; this section records only what `ce9e83e`
changes about them.

| Step | Builds | Depends on | Mac run |
|---|---|---|---|
| **30** | D5 — producers bind through the adapter; D7's producer refusal | 29 ✅ | differential only |
| **31** | D6-revised — Perseus proof; untested rows counted on `Analysis` (P3 (i)) | 29 ✅ | read-only parse of S1 |
| **32** | D7 — I4 labels; the untested-row display | 29 ✅, 31 | read-only query |

**What is now available to 30 and 31 that was not before.** `LoadedCuration` carries
`contrast_arms` — the resolved `Sample` ids per arm and the derived kind, from
`invariants.contrast_kind`. Producers take the arms from there, as they already take the node.
A producer must not re-derive kind or re-resolve a mapping key.

**Two stale prose items, each to be fixed by the prompt that already opens the file:**
- **Prompt 30:** `bzk/sources/pxd055843_perseus.py` l.109 says *"The arms are identifying on
  `Contrast`"*. False under D4 — the arms are non-identifying edges. (The file is PXD055843's, but
  it is a producer and 30 is the producer prompt; if 30's scope does not reach it, 31 must.)
- **Prompt 31:** `data/curation/curation_PXD055843.json`'s `rationale` says
  `contrasts_of_interest` is *"carried verbatim onto `LoadedCuration.contrasts` and read by
  nothing"*. False since `ce9e83e` — the loader resolves the arms and emits six edges from them.
  31 already edits that record for P2.

**P2 and P3 are unchanged** and are restated in the 2026-10-07 handoff §6.5. P2's entry is
`data/curation/curation_PXD055843.json` → `unresolved[4]`; P3 is a per-contrast untested count as
one non-identifying field on `Analysis`, with `parameters_json` the precedent for representation
only, since it is itself identifying.

**§5 — for bzk's Mac, owed from prompt 29 and not yet run.** A cold rebuild (`bzk/rebuild.py`
l.154, `drop_stores`), pre-registered in prompt 29 §5: all 16 labels 0 gone / 0 new; 58 → 60
tables; replay 18/40, 18/40, 16/38, 23/57 → **18/52, 18/52, 16/38, 23/63**; edge statements
31,349 → **31,379**; node statements 32,793, observations 4,195 / 4,768, 48 refusals and
`INCOMPLETE` unchanged; 30 arm edges in the graph; M1 `[4b]` unchanged. **Until this runs, the Mac
graph is behind `main` and prompt 30's differential run sits on a stale store.**

## 7. Open items — what changed since 2026-10-07 §7

**New:**
- **An environment-sensitive assertion anywhere in `tests/` re-breaks the tautology sweep**
  (§4.1). Named as a class because it is invisible from either file.
- **I22 holds only while the loader is the only `Contrast` minter.** Nothing guards that;
  `CONTRAST_ANCHOR` catches only an id minted with no anchor. Stated in `invariants.py` and in
  ONTOLOGY §8, enforced by nothing.
- **I22's graph form does not refuse a sample repeated within one arm.** The loader refuses it; a
  hand-built change-set can still carry the duplicate edge.
- **D3's cross-record gap:** two records on one `Experiment` declaring the same (numerator,
  denominator) pair with different arms. The loader refuses the repeat within a record only.
- **The mirror class is closed for the `Sample` role/modality/bait/antibody clauses only.** No
  survey was made of other DDL-comment enums with code mirrors.
- **Seventeen `claude/*` branches on the remote.** `CLAUDE.md` says development lands directly on
  `main`; these are harness branches, several stale. A sweep, not a build item.

**Changed:**
- **The unguarded mirror is closed** (10-05 §7, 10-07 §7) — built in `ce9e83e`.
- **The h10 digest defect is closed** (`fe06ca8`), and the sweep failure it caused with it.
- **D2/D3 enforced only in the loader:** I22 is now in `_CHECKS`, which is the direction 10-05 §7
  pointed. **The D2/D3 invariant itself stays open.**

**Closed:**
- 2026-10-07 §6.2 (P0) and §6.3 (prompt 29) — built in `ce9e83e`.

**Unchanged and still open:** the drift checker reporting failed fetches as drift; F-b generalised;
F-d (unknown keys in `mapping` entries — D1 refuses them in *contrast* entries only); R6's
prefix-only check; the stale tautology floor; `write_cells` over-reporting a repeated key
(ADR-0038 M11); the protein-groups adapter's silently dropped family (M8); ADR-0032 taking
D6-revised (c) into its review; a background-enrichment concordance basis value.

**Questions for the PI, collected** (none blocks prompts 30–32; the first blocks PXD055843
ingestion). Each names the file it is recorded in, because both PXD055843 records carry an
`unresolved` list:
1. Did imputation run on S1 (I15's seed)? *(open since September.)*
   `analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` `unresolved[1]` states the block;
   `curation_PXD055843.json` `unresolved[2]` states the I15 requirement only.
2. Where the untested rows come from. Recorded in no `unresolved` entry; new from ORIGIN.
3. s0 for S1's test. `analysis_PXD055843_siUSP24_IFN_vs_siC_IFN.json` `unresolved[0]` and
   `curation_PXD055843.json` `unresolved[1]`.
