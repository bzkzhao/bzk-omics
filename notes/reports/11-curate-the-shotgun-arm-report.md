# Report — land the curation record for PXD026748's shotgun arm

**Run at:** 2026-09-19 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Opened at:** `c9bb5bb`, reached by fast-forward from `c7cd241` · **Commits:** `31b4b4a`, `80ff294`, and this report's own · **Pushed, every push a fast-forward** · **`kuzu`:** 0.11.3

**Headline.** The record is in `data/curation/`, byte-identical, and every reviewer figure reproduced: R2's hash, R3's one-shared-Project, R4's 12-of-12 merge, R5's `lfq`. **E1 held at 719/14, E2 held both halves, E3 missed by one** — `tests/test_tautology_sweep.py` needed a classification for the new module's one matching expression, named and explained below. The record was read end to end and **no field is disputed.**

---

## Receipt checks

### R1 — base

```
$ git diff --stat e3d886a..origin/main
 notes/scripts/check_intensity.py              | 115 +++++++++++++++++++
 notes/scripts/coverage_shotgun.py             |  43 +++++++
 notes/scripts/inspect_shotgun.py              | 110 ++++++++++++++++++
 notes/staging/curation_PXD026748_shotgun.json | 154 ++++++++++++++++++++++++++
 4 files changed, 422 insertions(+)
```

**Exactly the four files named, all additions, nothing else.** `git log --oneline e3d886a..origin/main` is one commit, `c9bb5bb notes: stage the shotgun curation record and its inspection scripts`, so `e3d886a` is its parent — `e3d886a notes: track prompt 10d`, one commit past this session's last push. No stop condition fired.

### R2 — the staged record's identity

```
$ sha256sum notes/staging/curation_PXD026748_shotgun.json
fd20cc7efebc6edc4001a604a2d8ff43d597a6b11257f5c6aea9f2d3b090031f
```

**Equal to the reviewer's copy.** 13,260 bytes. No stop condition fired.

### R3 — why its Samples are new

`bzk/ontology/schema.py:243–258`:

```python
    "Experiment": Identity(
        fields=("title", "modality", "organism_taxid"), anchors=(("Project", "CONTAINS"),)
    ),
    "Sample": Identity(
        fields=(
            "cell_line",
            "model_system",
            "source_type",
            "genotype",
            "treatment",
            "timepoint_h",
            "replicate",
            "replicate_type",
            "organism_taxid",
        ),
        anchors=(("Experiment", "PERFORMED_ON"),),
```

Both records through `bzk.curation.loader.load_path`:

| label | GG record | shotgun record | shared |
|---|---|---|---|
| `Project` | 1 | 1 | **1** |
| `Experiment` | 1 | 1 | **0** |
| `Dataset` | 1 | 1 | **0** |
| `Analysis` | 1 | 1 | **0** |
| `Sample` | 12 | 12 | **0** |

**The reviewer's measurement reproduced exactly:** one shared `Project`, zero of everything else.

**Which identity field makes the Samples distinct: none of them.** That is the answer, and it is worth stating as a negative rather than naming a field, because naming one would be false. The two records' twelve `Sample` identity-**field** tuples are *identical* — measured, `sorted(tuple(n.get(f) for f in IDENTITY["Sample"].fields))` compares equal between the two records, twelve distinct tuples each. What makes them distinct is the **anchor**, `("Experiment", "PERFORMED_ON")`, and the `Experiment`s differ on two of their own three identity fields:

| `Experiment` field | GG | shotgun |
|---|---|---|
| `title` | *"HeLa ISG15 knockout diGly proteomics, IFN-alpha then lysate PLpro wild-type vs mutant"* | *"HeLa ISG15 knockout shotgun proteomics of the GG-enrichment input, IFN-alpha then lysate PLpro wild-type vs mutant"* |
| `modality` | `digly_proteomics` | `proteomics` |
| `organism_taxid` | 9606 | 9606 — **same** |

So the distinctness travels `Experiment.title` + `Experiment.modality` → `Experiment.id` → `Sample` anchor → `Sample.id`. Nothing on the `Sample` itself carries it, which is exactly why the record's rationale (3) says the fields are *deliberately* identical and why R4 is the check that matters.

### R4 — the counterfactual

The staged record loaded with its `experiment` block replaced by the GG record's, **in memory only**, written under a `TemporaryDirectory` and loaded from there:

| label | GG record | swapped shotgun | shared |
|---|---|---|---|
| `Experiment` | 1 | 1 | **1** |
| `Sample` | 12 | 12 | **12** |

**The reviewer's 12-of-12 reproduced.** The committed file's sha256 was re-read afterwards and is unchanged.

This is the silent merge: `load_path` accepts it without complaint, no invariant fires, and the only symptom is a graph twelve `Sample` nodes smaller than the curation describes. T1's counterfactual test is this measurement made permanent.

### R5 — the quantity

```
quantity_from_mapping_keys(load_path(SHOTGUN_RECORD).sample_mapping())  ->  'lfq'
```

**`lfq`, as expected.** The first mapping key is `LFQ intensity 77_Ap_WNE2_trap4_CMB-813_FRIMP_denzel_shotgun-ctrl_wt-1`; all twelve carry the `LFQ intensity ` prefix.

### R6 — the pin

`tests/test_curation_loader.py:488–499` at `c9bb5bb`:

```python
def test_every_record_and_fixture_on_disk_still_loads() -> None:
    """The check is *no key outside the known set*, never *exactly this set*.

    The five files do not agree on their key sets — `corrections` is in one real record and not the
    other two, `note` and `synthetic` are in the fixtures and no real record, `pending` is in one
    fixture alone — so a check written as an equality would refuse at least three of the five: no key
    set is shared by more than two files (`curation_PXD026748.json` and `curation_PXD055843.json`).
    """
    records = sorted(CURATION_DIR.glob("curation_*.json")) + sorted(
        FIXTURES.glob("curation_synthetic_*.json")
    )
    assert len(records) == 5, f"expected the three records and the two twins, found {records}"
```

**Re-measured with the new record present: six files, five distinct key sets, and the shared pair is unchanged.**

| key set | files |
|---|---|
| A | `curation_PXD026748.json`, `curation_PXD055843.json` — **still the only pair** |
| B | `curation_PXD018299.json` (has `corrections`) |
| C | `curation_synthetic_loadable.json` (has `note`, `synthetic`) |
| D | `curation_synthetic_pending.json` (has `note`, `synthetic`, `pending`) |
| E | `curation_PXD026748_shotgun.json` — **new, and its own set** |

The new record is distinct because it is the only file with **no `contrasts_of_interest` key**: the shotgun arm names no contrast. So the docstring's load-bearing clause — *no key set is shared by more than two files* — survives, and the numbers around it move: six files, five key sets, an equality check would refuse **at least four of the six**.

That distinction is worth having measured rather than assumed. Had the shotgun record happened to match key set A, the sentence would still have read true while the reason for it had changed underneath — the pair would have become a triple.

---

## Changes

### C1 — the record in place

```
$ git mv notes/staging/curation_PXD026748_shotgun.json data/curation/curation_PXD026748_shotgun.json
```

**sha256 after the move: `fd20cc7efebc6edc4001a604a2d8ff43d597a6b11257f5c6aea9f2d3b090031f`** — equal to R2's. Byte-identical; not edited.

`notes/staging/` is now empty and git tracks nothing under it (`git ls-files notes/staging` → 0), so no empty directory is committed. The directory itself remains on disk in this container only, as an untracked artefact of the move.

### C2 — the pin at six

`tests/test_curation_loader.py`. **Seen to fail first**, with the record moved and the pin still at five:

```
E       AssertionError: expected the three records and the two twins, found [
          …/curation_PXD018299.json, …/curation_PXD026748.json,
          …/curation_PXD026748_shotgun.json, …/curation_PXD055843.json,
          …/curation_synthetic_loadable.json, …/curation_synthetic_pending.json]
E       assert 6 == 5
```

The assertion became `assert len(records) == 6` with the message *"expected the four records and the two twins"*, and the docstring was rewritten to R6's measurement: six files, `contrasts_of_interest` named as the shotgun record's distinguishing absence, *at least four of the six*, five distinct key sets, the pair unchanged. A paragraph records that the claim was **re-measured on 2026-09-19 rather than carried over**, and why that mattered.

### C3 — `tests/test_curation_pxd026748_arms.py`

Five tests in a new module. Its docstring states the subtlety the module exists for: the failure mode of getting the `experiment` block wrong is a *smaller graph*, not an error.

| test | asserts |
|---|---|
| `test_the_two_arms_share_a_project_and_nothing_else` | one shared `Project`; disjoint `Sample` (asserted first, on its own line), then disjoint `Experiment`, `Dataset`, `Analysis`; twelve `Sample`s each |
| `test_sharing_an_experiment_would_merge_every_sample` | R4's counterfactual: 12 shared `Sample` ids, 1 shared `Experiment` |
| `test_every_shotgun_sample_matches_a_gg_sample_on_every_identity_field` | the two arms' `Sample` identity-field tuples are equal as sets **and** as sorted lists |
| `test_the_shotgun_mapping_keys_derive_lfq` | R5 |
| `test_a_mapping_key_from_a_second_family_cannot_derive_a_quantity` | one key re-prefixed refuses, naming both families |

Every mutated copy goes through one helper, `_loaded_with(tmp_path, …)`, which writes under `tmp_path`. The committed records are read and never edited.

**`Sample` disjointness is asserted on its own line, and first — that took a correction.** The first draft looped over `("Experiment", "Dataset", "Analysis", "Sample")`. Under T1's mutation it failed at `Experiment` and reported *"the two arms share 1 Experiment id(s)"*, never reaching the twelve `Sample`s that had silently merged behind it. A copied `experiment` block collides on the anchor *and* on everything anchored to it, so the loop always fails one label early and names the wrong thing. Lifted out and asserted first, with a comment saying why.

### C4 — the two restatements replaced

**`bzk/adapters/maxquant_protein_groups.py`**, module docstring and the cell loop's comment. Both said "three families of twelve columns" about a file the repository did not hold.

Module docstring, **was**:

> Until 2026-09-19 the declaration chose the columns too, and PXD026748's shotgun `proteinGroups.txt` is where that bit — three families of twelve columns, twenty-four columns discarded at ingestion by a declaration that should only have been declarative.

**is**:

> Until 2026-09-19 the declaration chose the columns too, and PXD026748's shotgun `proteinGroups.txt` is where that bit: it carries more than one family, so a declaration that should only have been declarative was discarding matrices at ingestion. The families and their column counts are measured and dated in `data/curation/curation_PXD026748_shotgun.json`, rationale item (4), which is that figure's one home — restating it here is what this sentence used to do, and a second copy of a measurement is a defect rather than a convenience.

Cell loop, **was**:

> PXD026748's shotgun `proteinGroups.txt` carries three families of twelve columns; storing one discarded twenty-four columns at ingestion and made the declaration lossy when it should only be declarative.

**is**:

> Storing one family discarded the rest at ingestion and made the declaration lossy when it should only be declarative; the case that showed it is PXD026748's shotgun `proteinGroups.txt`, whose families and column counts are measured and dated in `data/curation/curation_PXD026748_shotgun.json`, rationale item (4).

`grep -n "three families of twelve\|twenty-four columns"` over the module returns nothing. Nothing else in the module changed.

---

## Tests — each seen to fail before it passes

Every mutation confirmed applied by reading the file back before the run, and confirmed reverted after.

| # | mutation | test | failing assertion's message |
|---|---|---|---|
| **T1** | the shotgun record loaded with the GG record's `experiment` block, from a temporary copy | `test_the_two_arms_share_a_project_and_nothing_else` | `AssertionError: the two arms share 12 Sample id(s): ['bzk:2cddd083…', 'bzk:2f639f75…', … twelve listed]` |
| **T2** | one shotgun sample's `treatment` changed in a temporary copy | `test_every_shotgun_sample_matches_a_gg_sample_on_every_identity_field` | `AssertionError: 2 Sample identity tuple(s) appear in one arm and not the other: [(…, 'IFN-alpha 500 U/mL 72 h; then lysate + recombinant SARS-CoV-2 PLpro WT 1:50 w/w 30 min 37 C', …), (…, 'IFN-alpha, then lysate PLpro WT (mutated)', …)]` |
| **T3** | one mapping key re-prefixed `LFQ intensity ` → `Intensity ` in a temporary copy | `test_the_shotgun_mapping_keys_derive_lfq` | `MaxQuantProteinGroupsError: the sample mapping does not name exactly one quantity's column family … the keys span more than one family: intensity → ['Intensity 77_Ap_…_shotgun-ctrl_wt-1']; lfq → [… the other eleven]` — **both families named**, as required |

**T2's message took a correction too.** The first draft asserted `shotgun == gg` on the two sorted lists. Under the mutation it failed — but pytest's list diff reported *"At index 6 diff"* between two tuples that differed in `replicate`, not in the `treatment` the mutation changed: both lists are sorted, so a single changed field moves one tuple and the first divergent index lands on an unrelated pair. A guard that fires and then names the wrong field is a guard someone will mis-diagnose. The assertion now builds its message from the symmetric difference, which names exactly the two tuples involved, and the list comparison is kept after it for multiplicity.

---

## Registered expectations

### E1 — **held**

| | at `c9bb5bb` | after |
|---|---|---|
| passed | 714 | **719** |
| skipped | 14 | **14** |

719 = 714 + 5 new tests. C2's pin move changed no count, as registered.

### E2 — **held, both halves**

- `test_rebuilt_ids_match_the_committed_pin` → **1 passed, unmodified**. It globs `curation_PXD018299.json` alone, so the fourth record cannot reach it.
- `test_every_record_in_the_export_reaches_the_graph` → **1 passed** with the new record included. The replay line reads:

  ```
  [rebuild] ingestion replay: 4 curation record(s), 0 deposit(s), 0 site observation(s),
            0 protein observation(s), 0 refusal(s), 70 node statement(s),
            170 edge statement(s), 0 quantitative cell(s), 4 ingestion(s) skipped
  ```

  Four records loaded, four ingests skipped — the deposits are absent in this container, which is the state the prompt describes and `OPERATIONS.md` §5's exit 1 names.

### E3 — **missed by one, and it is named**

**`tests/test_tautology_sweep.py` needed changing.** It failed with:

```
E  AssertionError: 1 matching expression(s) or occurrence count(s) are not classified:
   [('test_curation_pxd026748_arms.py', 'shotgun == gg', 1)]
```

**Why it needed changing rather than the test being reshaped:** that module's own failure message directs the reader to classify — *"otherwise add it to `PINNED` with its count"* — and 10c established that classifying is the designed response and reshaping to dodge the matcher is not. The entry was added with its classification: `shotgun` and `gg` are each `sorted(tuple(...))` over one committed record's `Sample` nodes; neither call produced the other, and the two records are written independently by the review loop, so the comparison is a fact about two documents — the shape the neighbouring `test_decision_index.py` block already calls safe.

It is a `PINNED` entry and a comment; no assertion in that module changed, and its floor was not re-denominated (still `modules >= 32 and asserts >= 1129`, still the standing defect).

---

## `CLAUDE.md` point 1 — every check, at its actual result, with its target

Environment built with `uv sync` from the committed `uv.lock`. Every command under `.venv/bin/python`.

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **719 passed, 14 skipped** |
| `pytest tests/test_schema.py` | `tests/test_schema.py` | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed!** |
| `ruff format --check` | `bzk tests` | **100 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 100 source files** |

`ruff check .` — which additionally covers the three notebooks, permanently out of scope — **was not run and is reported as not run.** The three new files under `notes/scripts/` are also outside `bzk tests` and were **not** linted, formatted or type-checked here; they are bzk's, arrived with the base commit, and this turn did not touch them.

---

## `CLAUDE.md` point 2 — the change did what it claimed

- **The record is byte-identical**, checked by sha256 on both sides of `git mv` rather than by trusting the command.
- **Every reviewer figure was reproduced independently** — R2's hash, R3's table, R4's 12-of-12, R5's `lfq` — and each matched. None was carried over from the prompt.
- **R6's claim was re-measured with the new file present**, and the report says which part survived and which numbers moved.
- **Each new guard was made to fail**, and two of them were *rebuilt* because the first failure named the wrong thing: T1's loop reported `Experiment` instead of the twelve merged `Sample`s, and T2's list diff reported `replicate` instead of the changed `treatment`. Both are recorded above; a guard that fires and misnames is only half a guard.
- **The record was read end to end** — rationale, all eight `unresolved` items, mapping — before committing. Nothing in it is disputed, so no stop was raised.

---

## `CLAUDE.md` point 3 — what this turn does not cover

- **Any ingest.** The shotgun `proteinGroups.txt` is not in this container and is not placed in any raw store. Turn 12, on bzk's machine.
- **The record's eight `unresolved` items are recorded, not closed.** Several are consequential and none is guarded by a test: the digest split has no representable relation (ADR-0035 R2), replicate labels must not be read as pairing across the arms, the `ko_mut` run block is confounded with hardware, the protein count gap of 1 against the publication is unreconciled, and 93 only-identified-by-site rows will be ingested that the publication removed. **Nothing in the suite would catch a downstream join that ignores any of them** — item (2)'s warning in particular is exactly the kind a query could violate silently. Named here because point 3 asks; not machine-checkable from a curation record alone, and out of scope.
- **The two arms' correspondence is unguarded in the other direction.** T2 asserts the twelve materials agree field-for-field. Nothing asserts that they *should* — that is the record's rationale (3) and the publication's Methods, and a test cannot check a claim about wet-lab material.
- **The six superseded homes of `67,158`** — out of scope, untouched. C4 removed the *"three families of twelve columns"* restatements, which are a different figure; the `67,158` ones remain as 10d's report lists them.
- **The published cascade, turn 09's ingest-figure fixture, ADR-0035's review, the site branch's constant `quantity`, the unenumerated-mirrors class, `notes/prompts/`** — all untouched.
- **The tautology sweep's floor** — still stale, not re-denominated. Only a `PINNED` entry was added.
- **`notes/scripts/`** — the three scripts arrived with the base and were neither run nor checked here. Their measurements are the record's, dated and attributed in it; this turn took them as given, as the review loop's ownership of the record requires.

---

## `CLAUDE.md` point 4 — instructions dropped or partially done

- **E3 was missed by one file**, named above with its reason. Reported rather than presented as held.
- **`notes/staging/` is empty but still exists on disk here.** Git tracks nothing under it, so nothing empty is committed, which is what C1 asked. The directory itself is an untracked local artefact; removing it would be a change to bzk's working tree layout that nothing asked for.
- Nothing else was dropped or partially done. **No commit was amended and no ref was force-pushed.**

---

## Commits and push range

| commit | contents |
|---|---|
| `31b4b4a` | `curation: land the record for PXD026748's shotgun arm` — C1, C2, C3 and T1–T3, plus the `PINNED` classification E3 required |
| `80ff294` | `adapters: point the protein-groups docstrings at the record, not at a restated figure` — C4 alone |
| this report's own, `notes: report the shotgun-arm curation turn` | `notes/reports/11-curate-the-shotgun-arm-report.md`, alone |

**Push range:** `c9bb5bb..80ff294` for the two commits above, then one commit on top carrying this report.

**Every push in this turn was a fast-forward.** `git push` reported `c7cd241..80ff294` on the branch and `c9bb5bb..80ff294` on `main` — the `..` form, never the `+` prefix git prints for a forced update. No `--force`, no `--force-with-lease`, no amend, no rebase. This report does not quote its own SHA; `git log --oneline -3` on either ref gives all three.
