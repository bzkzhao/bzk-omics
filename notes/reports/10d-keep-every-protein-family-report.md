# Report — the protein-groups adapter keeps every quantity family

**Run at:** 2026-09-19 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Opened at:** `4276731`, which was `origin/main` exactly · **Commits:** `1b11de2`, and this report's own · **Pushed, every push a fast-forward** · **`kuzu`:** 0.11.3

**Headline.** The two MaxQuant adapters now agree about I11. The declared quantity sets `Analysis.quantity` and fixes the family the mapping keys must belong to; the store keeps every family the file reports. **E1 held at 714/14, E2 held, E3 held.** R4 found eight text homes for `67,158`, all of them counting one family — six of which say "cells" unqualified and now describe superseded behaviour. None was edited, as scoped.

**Base check.** `git fetch` then `git merge-base --is-ancestor 4276731 origin/main` → true, and `git rev-parse origin/main` → `4276731`. The base is `origin/main` exactly, not behind it and not passed. Fast-forwarded and proceeded.

---

## Receipt checks

### R1 — how the site adapter reads every family

`bzk/adapters/maxquant_sites.py:641–656`:

```python
        # **Every quantity the deposit reports, not only the one the `Analysis` declares.** I11 says
        # *its per-sample quantitative values*, and PXD018299 reports two per sample; keeping one
        # would discard a matrix at ingestion, and would leave ADR-0004's `quantity` key column
        # justified by a case it did not handle. The declared quantity says what this ingestion
        # consumed (I16); the store says what was reported.
        cells = [
            quant_store.Cell(
                observation_id=observation_id,
                sample_id=sample_id,
                quantity=quantity,
                value=maxquant.cell_value(row, column, f"{prefix}{label}"),
            )
            for sample_id, label in sample_columns
            for quantity, prefix in sorted(QUANTITY_COLUMNS.items())
            if f"{prefix}{label}" in column
        ]
```

**How it finds a sample's column in each family:** it **builds the name** — `f"{prefix}{label}"` — one per family, from a single run label.

**What it recovers from the mapping key:** the **run label**. `_sample_columns` at `:140–146` strips the recognised quantity prefix off the key (`Ratio mod/base WT_1` → `WT_1`) and returns `(Sample.id, label)`, raising where no prefix is recognised.

**How it filters to families actually present:** the comprehension's trailing `if f"{prefix}{label}" in column`. A family whose built name is not a column is **skipped**, not refused — which is what makes a deposit that writes two of the enum's families an ordinary file rather than a broken one.

### R2 — what the protein-groups adapter did

`bzk/adapters/maxquant_protein_groups.py:175–202` at `4276731`:

```python
def _sample_columns(
    mapping: SampleMapping, column: Mapping[str, int], prefix: str
) -> list[tuple[str, str]]:
    """`(Sample.id, column name)` per mapped sample.

    The curation maps each sample to a **column name**, so the column is taken from the mapping
    rather than guessed from a run label. …
    """
    placed = []
    for sample in mapping.samples:
        key = str(sample.get("mapping_key", ""))
        if key not in column:
            raise MaxQuantProteinGroupsError(
                f"sample mapping key {key!r} names no column in this file. Expected a column of "
                f"the declared quantity's family ({prefix!r}); found "
                f"{sorted(c for c in column if c.startswith(prefix))}"
            )
        if not key.startswith(prefix):
            raise MaxQuantProteinGroupsError(
                f"sample mapping key {key!r} is not of the declared quantity's family {prefix!r}. "
                "The declared quantity chooses the columns, so a mapping naming another family "
                "would record one quantity on the Analysis and store another (I16)."
            )
        placed.append((str(sample["id"]), key))
    return placed
```

`:381–394`:

```python
            for sample_id, name in samples:
                cells.append(
                    quant_store.Cell(
                        observation_id=observation_id,
                        sample_id=sample_id,
                        quantity=self.declared.quantity,
                        # `maxquant.cell_value`, not a local one. The first draft here folded `0`
                        # to `None` — MaxQuant does write 0 for an unquantified protein — and that
                        # is a reading `maxquant_sites.py` had already refused to make (I19). Two
                        # adapters over one deposit cannot mean two things by a zero, so the
                        # convention has one home and this defers to it.
                        value=maxquant.cell_value(row, column, name),
                    )
                )
```

- **`_sample_columns` returns a column name**, not a run label — `placed.append((str(sample["id"]), key))`, and `key` is the mapping key, which *is* a column name here. That single fact is why the reader could only ever read one family: it never had a label to build a second name from.
- **`parse` emits cells of the declared family only** — `quantity=self.declared.quantity`, value read from `name`, the one column.
- **The reason at `:196–200`:** *"The declared quantity chooses the columns, so a mapping naming another family would record one quantity on the Analysis and store another (I16)."*

**Will that reason still be true after this turn? No — its premise is gone.** The declared quantity no longer chooses the columns, and the adapter now stores *every* family, so "record one quantity on the `Analysis` and store another" stops describing the hazard. **The refusal itself stays**, for a reason that survives: the declaration fixes the family the keys must belong to, so a key from another family means the `Analysis` records one quantity while the mapping describes a different run of columns. C2 rewrites the sentence; the behaviour is unchanged, and T4 pins it.

### R3 — the two tests, and what the dict does

`test_every_observation_carries_its_quant_ref_and_its_cells` at `4276731`:

```python
    assert observation["quant_ref"] == "protein_values"

    assert [label for label, _ in parsed.cells] == ["ProteinObservation"]
    cells = parsed.cells[0][1]
    assert {(c.sample_id, c.quantity, c.value) for c in cells} == {
        ("bzk:sampleWT", "lfq", 1500000.0),
        ("bzk:sampleKO", "lfq", 2500000.0),
    }
    assert all(c.observation_id == observation["id"] for c in cells)
```

**Fails once more than one family is retained**, and it did: the comparison is a set **equality**, and `HEADER` carries `Intensity ` columns for both samples, so two more members appear on the left. Measured: `Extra items in the right set` — the assertion ran and the two `intensity` cells were absent from the expected set.

`test_the_declared_quantity_chooses_the_column_family` at `4276731`:

```python
    row = _row(lfq_wt="10", intensity_wt="20")
    by_quantity = {}
    for quantity in ("lfq", "intensity"):
        parsed = _adapter(quantity).parse(_write(tmp_path, [row]), _mapping(quantity))
        cells = {c.sample_id: c for c in parsed.cells[0][1]}
        by_quantity[quantity] = cells["bzk:sampleWT"]
    assert by_quantity["lfq"].value == 10.0
    assert by_quantity["intensity"].value == 20.0
    assert by_quantity["lfq"].quantity == "lfq"
    assert by_quantity["intensity"].quantity == "intensity"
```

**Fails, and for the dict's reason.** `{c.sample_id: c for c in ...}` is keyed on the sample alone. **With one sample now holding cells in two families, the later cell overwrites the earlier one and the dict silently keeps exactly one of them** — it does not raise, does not warn, and the test reads whichever survived as though it were *the* cell for that sample. Which one survives is decided by emission order: `sorted(QUANTITY_COLUMNS.items())` yields `intensity`, `lfq`, `ibaq`, so `lfq` is written last and wins. Measured: `assert by_quantity["intensity"].value == 20.0` failed with `assert 10.0 == 20.0`, the `10.0` being the `lfq` cell returned for the `intensity` declaration.

That collapse is exactly the hazard, and **it bit a third test silently**. `test_a_reported_zero_stays_a_zero` builds the same sample-keyed dict and **kept passing** — because `lfq` happens to sort last and is the family it means to read. Green for a reason with nothing to do with its claim. It is fixed below and named as a consequential change.

### R4 — every home of `67,158`

```
$ grep -rn "67,158\|67158" --exclude-dir=.venv --exclude-dir=.git .
./ROADMAP.md:68:     … it emits 4,797 `ProteinObservation`s over 23,807 `Protein`s with 67,158 cells and 0 refusals …
./ROADMAP.md:2417:   … **0** refusals, and **67,158** cells were a fourteen-sample mapping supplied …
./ROADMAP.md:2440:   … **0** refusals, **67,158** cells | **held, all six exactly.** …
./ROADMAP.md:2479:   … Measured here: **26,744 of 67,158 `LFQ intensity` cells are `0`** …
./ROADMAP.md:12726:  … measured offline over `HAP1_USP18KO_proteinGroups.txt` would write 67,158 …
./HANDOFF.md:260:    … 0 refusals, **67,158** cells, in 0.726 s — every pre-registered figure exact. …
./HANDOFF.md:1332:   … `quant_ref = 'protein_values'` and **67,158 cells**. …
./tests/test_maxquant_protein_groups.py:388:  … **26,744 of the 67,158 `LFQ intensity` cells on the real file are `0` (39.8%)** …
./bzk/adapters/maxquant.py:132:  … **26,744 of the 67,158 `LFQ intensity` cells in `HAP1_USP18KO_proteinGroups.txt` are `0` (39.8%) …
```

(Three further binary hits — two `__pycache__` files and `.mypy_cache` — are compiled copies of the last two and are not homes.)

**Every one of the eight counts one family's cells, never all of them.** The arithmetic settles it without reading the file: 4,797 `ProteinObservation` × 14 samples = **67,158** exactly, which is one cell per observation per sample — one family. The deposit carries two (14 `Intensity `, 14 `LFQ intensity `, 0 `iBAQ`), so the all-families figure for that same run would be 134,316.

| home | qualified? | counts |
|---|---|---|
| `ROADMAP.md:68` | no — "67,158 cells" | one family (`LFQ intensity`, the `lfq` default) |
| `ROADMAP.md:2417` | no — "**67,158** cells" | one family |
| `ROADMAP.md:2440` | no — "**67,158** cells" | one family |
| `ROADMAP.md:2479` | **yes** — "`LFQ intensity` cells" | one family, said so |
| `ROADMAP.md:12726` | no — "would write 67,158" | one family |
| `HANDOFF.md:260` | no — "**67,158** cells" | one family |
| `HANDOFF.md:1332` | no — "**67,158 cells**" | one family |
| `tests/test_maxquant_protein_groups.py:388` | **yes** — "`LFQ intensity` cells" | one family, said so |
| `bzk/adapters/maxquant.py:132` | **yes** — "`LFQ intensity` cells" | one family, said so |

**None was edited**, as the out-of-scope list requires: they are dated measurements of the adapter as it was and remain true of that date.

**Which of them now describe superseded behaviour:** the six unqualified ones — `ROADMAP.md:68`, `:2417`, `:2440`, `:12726` and `HANDOFF.md:260`, `:1332`. Each says "cells" without naming a family, which read as *all the adapter would write* when it was written and no longer does. The three that say `LFQ intensity` are unaffected: that family's cell count is still 67,158 and the 39.8 % zero prevalence still holds. The ratio in `bzk/adapters/maxquant.py:132` and its copy in the test docstring stay exactly correct, since both numerator and denominator name the family.

---

## Changes

### C1 — every family present, for every mapped sample

**`bzk/adapters/maxquant_protein_groups.py`**, two places:

- **`_sample_columns`** (now `:175–207`) returns `(Sample.id, run label)`, the label recovered as `key[len(prefix):]`. Its docstring says what changed and why, and records that **both refusals are unchanged in effect** — a key naming no column, and a key outside the declared family.
- **the cell loop** (now `:405–432`) is a `cells.extend(...)` generator mirroring `maxquant_sites.py:646–656` over this adapter's own `QUANTITY_COLUMNS`: one cell per `(sample, family)` where `f"{family_prefix}{label}"` is a column.

**The lookup is by exact built name.** The comment at the loop says why in the file's own terms: the real shotgun file carries `iBAQ peptides`, which begins with `iBAQ ` and is not a sample column; a prefix scan would retain it as a measurement of a sample it does not belong to, and a name built from a run label cannot reach it. T2 pins that.

### C2 — the new truth where the old one was written

**`bzk/adapters/maxquant_protein_groups.py`**, four places:

| location | was | is |
|---|---|---|
| module docstring, `:21–23` | "**The declared quantity chooses the column family**" | the declaration sets `Analysis.quantity` and gates the keys; the store keeps every family present, with PXD026748 named as where the old rule bit |
| `QUANTITY_COLUMNS` comment, `:65–67` | "Reading is driven by the declaration" | read in full, not selected from; the declared row validates the keys, the reader walks all of them |
| the out-of-family error, `:196–200` | "The declared quantity chooses the columns, so a mapping … would record one quantity on the Analysis and store another (I16)." | the declaration sets `Analysis.quantity` and fixes the family the keys must belong to; what is *stored* is every family the file reports, whichever is declared |
| `ProteinIngestReport.cells`, `:162–168` | no docstring | counts cells **across every family**, one per `(observation, sample, family present)`; explicitly no longer `groups_emitted * len(samples)`, and the `HAP1_USP18KO` figures describe the adapter before 2026-09-19 |

**`maxquant_sites.py` was not touched.**

### C3 — the two R3 tests, and three consequential ones

| test | change |
|---|---|
| `test_every_observation_carries_its_quant_ref_and_its_cells` | the expected set gains the two `intensity` members, with a comment naming the two `lfq` ones as what it held before |
| `test_the_declared_quantity_chooses_the_column_family` → **renamed** `test_the_declared_quantity_sets_the_analysis_and_gates_the_keys` | asserts `Analysis.quantity` follows the declaration **and** that the cell set is identical for `lfq` and `intensity`. The docstring sentence *"the declaration is what is read"* is gone, and the rename is recorded in the new docstring. **Not deleted** — the same function, rewritten and renamed, because a test whose name asserts the behaviour it now refutes is worse than no test |

**Three further existing tests were changed as consequences.** None is in C3's list; each is named here because the report is where that belongs:

1. **`test_an_empty_group_is_refused_and_counted`** — `len(parsed.cells[0][1]) == 2` became `== 4` (two samples by the two families `HEADER` carries), and an assertion was added that every cell belongs to the surviving observation. Its claim — *the refused row contributes no cells* — is unchanged; only the arithmetic moved. It failed on the first run of the changed adapter, which is how it was found.
2. **`test_a_reported_zero_stays_a_zero`** — its sample-keyed dict now filters to `c.quantity == "lfq"`. **This test did not fail**; it passed because `lfq` sorts last and won the collapse. Fixed because a test that is green for a reason unrelated to its claim is the defect this repository keeps correcting, and because leaving it would make the next family added to `QUANTITY_COLUMNS` silently change what it reads.
3. **`test_a_mapping_key_from_another_family_is_refused`** — docstring only. It said *"The declared quantity chooses the columns"*, the sentence C2 removed from the module. It now says what the refusal is for and that the retention change does not touch it. This is T4's test; its assertions are untouched.

---

## Tests — each seen to fail before it passes

Every mutation confirmed applied by reading the file back before the run, and confirmed reverted after.

| # | mutation | test | failing assertion's message |
|---|---|---|---|
| **T1** | emission restricted to the declared family (`for quantity, family_prefix in [(self.declared.quantity, prefix)]`) | `test_every_family_present_is_retained` | `AssertionError: assert {…} == {…}` / `Extra items in the right set: ('bzk:sampleKO', 'intensity', 2600000.0), ('bzk:sampleKO', 'ibaq', 2700000.0), ('bzk:sampleWT', 'intensity', 1600000.0), ('bzk:sampleWT', 'ibaq', 1700000.0)` |
| **T2** | the built-name lookup replaced by a scan of columns starting with each prefix | `test_a_column_sharing_a_family_prefix_is_not_a_sample_column` | `AssertionError: the extra column adds no cell` / `assert 8 == 6` — the two extra cells are `iBAQ peptides`' `42.0`, attributed to both samples |
| **T3′** | the membership guard replaced by a direct lookup, `column[f"{family_prefix}{label}"] >= 0` | `test_a_family_the_file_does_not_carry_is_skipped_not_refused` | `KeyError: 'iBAQ WT_P_1'`, raised inside the cell comprehension |
| **T4** | the out-of-family refusal made unreachable (`if False:`) | `test_a_mapping_key_from_another_family_is_refused` — **the existing test**, at `tests/test_maxquant_protein_groups.py:434`; none had to be written | `Failed: DID NOT RAISE MaxQuantProteinGroupsError` |
| **C3-2** | `Analysis.quantity` hard-coded to `"lfq"` | `test_the_declared_quantity_sets_the_analysis_and_gates_the_keys` | `AssertionError: the declaration is what the Analysis records` / `assert 'lfq' == 'intensity'` |

**T3's first mutation failed for the wrong reason and was replaced.** It inserted a call to a helper that does not exist, `_raise_missing(...)`, and the test failed with `NameError: name '_raise_missing' is not defined` — raised while *building* the comprehension, not by the lookup behaving differently. A red run, but not evidence that the guard fires: the same `NameError` would have arrived with the guard deleted, present, or replaced by anything at all. It was replaced by T3′, which makes the lookup itself raise on a family the file lacks and produces a `KeyError` from the line under test. Reported rather than swapped in silence, for the reason `CLAUDE.md` point 2 gives: a mutation that fails elsewhere is as uninformative as one that does not apply.

### T5 — the replay test

`tests/test_adapter_dispatch.py::test_replay_over_a_protein_groups_deposit_counts_protein_observations` **passes unmodified**, and its figures are unchanged:

| | at `4276731` | after |
|---|---|---|
| `protein_observations` | 1 | **1** |
| `cells_staged` | 4 | **4** |

Measured by running the replay on both states. **The cell count does not move, and that is not a coincidence to wave at** — it is the T3 property observed on a second fixture. `curation_synthetic_loadable.json` maps four `Intensity …` columns and `_synthetic_protein_groups()` writes only that one family, so there is no second family to retain and 1 observation × 4 samples × 1 family = 4 either way. Retention changes cells, not observations, and here it changed neither because the file carries one family.

---

## Registered expectations

### E1 — **held**

| | at `4276731` | after |
|---|---|---|
| passed | 711 | **714** |
| skipped | 14 | **14** |

714 = 711 + 3 new tests. The C3 rewrites and the three consequential changes moved no count: each is an edit to an existing test, and the rename is the same function under a new name. No test was deleted.

### E2 — **held**

`tests/test_rebuild.py::test_rebuilt_ids_match_the_committed_pin` → **1 passed**, unmodified. No `ProteinObservation` or `Analysis` id moved, and none could: `evidence_id` is computed over the node's properties, and a cell is not a node property. No STOP condition fired.

### E3 — **held**

`ProteinObservation` counts are unchanged wherever they are asserted. `git diff -U0 tests/` grepped for `groups_emitted`, `ProteinObservation"])` and `protein_observations` returns **no changed line**; the only counts that moved are cell counts, and only upward — `2 → 4` in `test_an_empty_group_is_refused_and_counted`, and `2 → 4` in the set equality of `test_every_observation_carries_its_quant_ref_and_its_cells`. `tests/test_perseus.py:930`'s `report.cells == 6` is the Perseus adapter's and is untouched.

---

## `CLAUDE.md` point 1 — every check, at its actual result, with its target

Environment built with `uv sync` from the committed `uv.lock`. Every command under `.venv/bin/python`.

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **714 passed, 14 skipped** |
| `pytest tests/test_schema.py` | `tests/test_schema.py` | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed!** |
| `ruff format --check` | `bzk tests` | **99 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 99 source files** |

`ruff check .` — which additionally covers the three notebooks, permanently out of scope — **was not run and is reported as not run.**

---

## `CLAUDE.md` point 2 — the change did what it claimed

- **The defect was demonstrated on a fixture carrying the shape the real file has** — three families — rather than argued from the shotgun file, which is not committed and not in this container.
- **Every new guard was made to fail**, with one mutation rejected for failing elsewhere and replaced (T3 → T3′).
- **T5's unchanged cell count was measured on both states**, not assumed, and the reason it does not move is stated rather than left as a happy result.
- **The dict-collapse hazard was traced past the two tests the prompt named**, to a third that was passing on emission order alone.

---

## Is the class closed across the MaxQuant adapters?

**The class is: an adapter storing fewer quantity families than the deposit reports. Across the two MaxQuant adapters it is now closed — by identical construction and by a test each, not by a note.**

- `maxquant_sites.py:646–656` and `maxquant_protein_groups.py`'s cell loop are now the same three lines: build `f"{prefix}{label}"` per family, keep it where the column exists. Each reads its own `QUANTITY_COLUMNS`, which is right — the two grains name different families.
- The protein grain is pinned by T1 (all present families retained), T3 (an absent one skipped) and T2 (a prefix-sharing column not mistaken for one). The site grain was already pinned by `tests/test_maxquant_sites.py`.

**What is not closed, stated plainly:**

- **Nothing asserts the two adapters agree.** The rule is now written twice and guarded twice, which is one more mirror of the kind 10c closed for the report classes — and there is no test comparing the two cell loops. A third MaxQuant adapter, or an edit to one loop, would diverge silently. This is an instance of the unenumerated-mirrors class 10c left open and this prompt puts out of scope; naming it here is the most this turn can do about it.
- **`PerseusAdapter` is outside the claim entirely.** Its retention rule is explicitly out of scope, so "closed across the MaxQuant adapters" is the exact boundary — not "closed across the adapters".

---

## `CLAUDE.md` point 3 — what this turn does not cover

- **The `67,158` figures.** Not edited, as scoped. Six of the eight now describe superseded behaviour and are listed under R4 by file and line. Nothing marks them as dated in place; a reader who lands on `HANDOFF.md:260` will read "67,158 cells" as the adapter's output and be a factor of two low for that deposit.
- **`maxquant_sites.py`, `PerseusAdapter`, the Perseus retention rule** — untouched.
- **`rebuild.py` and the quantity derivation** — untouched. `quantity_from_mapping_keys` still derives the declared family from the mapping keys, which is still correct: the declaration still gates the keys.
- **Any curation record, any ingest, the shotgun file, and the choice of family for PXD026748** — untouched. No committed curation record names a protein-groups file, so no replay figure in the repository moves.
- **The site branch's constant `quantity`** — still an open defect, named in `rebuild._adapter_for`'s docstring.
- **The unenumerated-mirrors class from 10c** — still open, and this turn added a pair to it, as above.
- **The tautology sweep's floor** — still `modules >= 32 and asserts >= 1129` against a larger surface. Not re-denominated. The sweep's multiset half ran clean on this turn's three new tests, so nothing needed classifying.
- **`notes/prompts/`** — not written, not retyped, not committed.
- **SILAC-channel keys** such as `Intensity L …` — still unguarded, and now with one more edge: a file carrying both `Intensity ` and SILAC channel columns would have the channel columns' names built only if a run label matched, which it would not. Unchanged in effect, and still not covered.

---

## `CLAUDE.md` point 4 — instructions dropped or partially done

- **Three existing tests were changed beyond C3's two.** C3 named two; three more needed changing as consequences and are named under C3 above, with which failed and which was passing for the wrong reason. Not a drop — a widening, reported rather than folded in.
- **C3's test 2 was renamed.** The prompt said not to delete either test and gave test 2 a new job; the old name asserted the behaviour this turn removed. Renamed rather than left, with both names recorded in the test's own docstring and here.
- Nothing else was dropped or partially done. **No commit was amended and no ref was force-pushed.**

---

## Commits and push range

| commit | contents |
|---|---|
| `1b11de2` | `adapters: keep every quantity family on the protein-groups grain` — C1, C2, C3 and T1–T4, code and tests, one commit |
| this report's own, `notes: report the 10d retention turn` | `notes/reports/10d-keep-every-protein-family-report.md`, alone |

**Push range:** `4276731..1b11de2` for the code commit, then one commit on top carrying this report.

**Every push in this turn was a fast-forward.** `git push` reported `e16cada..1b11de2` on the branch and `4276731..1b11de2` on `main` — the `..` form, never the `+` prefix git prints for a forced update. No `--force`, no `--force-with-lease`, no amend, no rebase. This report does not quote its own SHA; `git log --oneline -2` on either ref gives both.
