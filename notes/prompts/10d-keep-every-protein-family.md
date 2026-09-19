# PROMPT 10d — the protein-groups adapter keeps every quantity family

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.
Base: `4276731`. Fetch, then fast-forward to it. Stop only if `4276731` is not
on `origin/main`, or if `origin/main` has moved past it. In that case, report
the commits and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`.

**Never force-push, and never amend or rebase a pushed commit** (`CLAUDE.md`
working style). **Do not write, retype or commit any file under
`notes/prompts/`.**

This container has no raw store. No check in this turn needs one. The change
touches no deposit that a committed curation record names: no record names a
protein-groups file.


## Why

The two MaxQuant adapters disagree about I11.
- **The site adapter** stores every quantity family the deposit reports for
  each mapped sample. `bzk/adapters/maxquant_sites.py:641–645` gives the reason:
  keeping one "would discard a matrix at ingestion".
- **The protein-groups adapter** stores only the declared family
  (`bzk/adapters/maxquant_protein_groups.py:381–394`,
  `quantity=self.declared.quantity`).

On `PXD026748`'s shotgun `proteinGroups.txt` there are three families of twelve
columns each: `Intensity`, `LFQ intensity` and `iBAQ`. That was measured on
bzk's machine, and the file is not committed. So today, declaring any one family
discards the other 24 columns at ingestion, and the choice of family is lossy
when it should only be declarative.

After this turn, the declared quantity sets `Analysis.quantity` (I16), and the
store keeps what was reported (I11). That is the split the site adapter's
comment already states.


## Receipt checks

R1. `maxquant_sites.py:641–656`. Quote it. How does the site adapter find a
    sample's column in each family? What does it recover from the mapping key,
    and how does it filter to families that are actually present?

R2. `maxquant_protein_groups.py:175–202` and `:381–394`. Quote both.
    - What does `_sample_columns` return, a column name or a run label?
    - Which family's cells does `parse` emit?
    - Quote the reason the error at `:196–200` gives. Will that reason still be
      true after this turn?

R3. `tests/test_maxquant_protein_groups.py`:
    - `test_every_observation_carries_its_quant_ref_and_its_cells`;
    - `test_the_declared_quantity_chooses_the_column_family`.

    Quote each test's assertions. For each one, say whether it fails once more
    than one family is retained, and why. The second test builds a dict keyed
    by `sample_id` over cells. Say what that dict does when one sample has
    cells in two families.

R4. `grep` for the figure `67,158` across the repository, excluding `.venv`.
    List every home, and say for each whether it counts **all** cells or
    **`LFQ intensity`** cells only. Do not edit any of them (see Out of
    scope).


## Changes

**C1 — Emit a cell for every family present, for every mapped sample.** Mirror
the site adapter's pattern at `maxquant_sites.py:646–656`, adapted to this
adapter's own `QUANTITY_COLUMNS` (`:76–80`):
- recover the run label by removing the **declared** family's prefix from the
  mapping key;
- for each family in `QUANTITY_COLUMNS`, emit a cell for `f"{prefix}{label}"`
  where that column exists.

The lookup must be by exact column name, built from the label. It must never be
by prefix scan. The real shotgun file carries `iBAQ peptides`, which begins
with the `iBAQ ` prefix and is not a sample column. A prefix scan would pick it
up, and a name built from a label cannot.

Keep, unchanged in effect, both of `_sample_columns`' refusals:
- a mapping key that names no column;
- a mapping key outside the declared family.

The declared family is still what the keys must agree with.
`quantity_from_mapping_keys` guarantees that agreement on the replay path.

**C2 — Say the new truth where the old one is written.** Specifically:
- rewrite the reason in the error at `:196–200` so it no longer claims that the
  declared quantity chooses the columns;
- update the `ProteinIngestReport.cells` docstring, if any, so it states that
  it counts cells across all retained families;
- update any comment in this module that says only the declared family is
  stored.

Change nothing in `maxquant_sites.py`.

**C3 — The two R3 tests.** Rewrite each to assert what is now true, and name
each change in the report. Do not delete either test.
- **Test 1:** assert the exact set of `(sample_id, quantity, value)` over every
  family the fixture row carries.
- **Test 2:** the declared quantity determines `Analysis.quantity` **and** the
  family the mapping keys must belong to. Cells exist for each family with
  their own values, whatever is declared. Test 2 has no other job. Its
  docstring currently says "the declaration is what is read", and that sentence
  goes.


## Tests — each seen to fail before it passes

For each test, report the mutation, confirmed applied by read-back and then
reverted, and the failing assertion's message.

T1. **All families retained.** A fixture row carrying all three families for
    two samples yields exactly six cells, each with the right quantity and
    value. Mutation: restrict emission to the declared family.
T2. **No prefix scan.** Add an `iBAQ peptides` column to the fixture header,
    with a numeric value. No cell is emitted from it, and the cell count is
    unchanged. Mutation: replace the built-name lookup with a scan of columns
    starting with each prefix.
T3. **A family that is absent is skipped, not refused.** A fixture with no
    `iBAQ` columns ingests, with no `ibaq` cells. Mutation: make the lookup
    raise on a missing column.
T4. **The declared family still gates the keys.** The existing refusal of a key
    outside the declared family still raises. Name the existing test that pins
    this. If none does, write one.
T5. **Replay.** `tests/test_adapter_dispatch.py`'s replay test (T5 of turn 10)
    still passes. Its `protein_observations` is unchanged, because retention
    changes cells, not observations. Report its cell count before and after.


## Registered expectations

E1. Suite = 711 passed, 14 skipped at base. The new total is 711 + new tests,
    and the rewrites in C3 change no count. Report the split.
E2. `test_rebuilt_ids_match_the_committed_pin` passes unmodified. No
    `ProteinObservation` or `Analysis` id moves: cells are not identity. If
    an id moves, STOP and report it.
E3. `ProteinObservation` counts are unchanged wherever they are asserted. Only
    cell counts rise.


## Task

1. Run R1–R4.
2. Make C1–C3 and write T1–T5.
3. Run E1–E3 and every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit code and tests as one commit (`adapters:` prefix). Push, fast-forward
   only.
5. Write `notes/reports/10d-keep-every-protein-family-report.md` and commit it
   alone. Push.


## Out of scope

- **The figure `67,158`, wherever R4 finds it.** Those are dated measurements
  of the adapter as it was, and they remain true of that date. Do not edit
  them. The report must say which of them now describe superseded behaviour.
- `maxquant_sites.py`, `PerseusAdapter`, and the Perseus retention rule.
- `rebuild.py`. The quantity derivation.
- Any curation record, any ingest, and the shotgun file.
- Choosing a quantity family for `PXD026748`.
- The site branch's constant `quantity`, which is still an open defect.
- The unenumerated-mirrors class carried from 10c.
- `notes/prompts/`.


## Report

- R1–R4 answered, with R4's grep shown.
- C1–C3, each with the file and lines changed.
- T1–T5, each with its mutation and failure message.
- E1–E3, each held or missed.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- Whether the class *an adapter storing fewer families than the deposit
  reports* is closed across the MaxQuant adapters, and by what.
- What this turn does NOT cover.
- Commit SHAs and the push range, stating that every push was a fast-forward.
