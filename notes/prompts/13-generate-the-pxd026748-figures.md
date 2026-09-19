# PROMPT 13 — a generator for PXD026748's ingest figures

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.

**Base.** Fetch, then fast-forward to `origin/main`. It must be a fast-forward
of `cae91c6` whose only changes, which bzk committed from the reviewer's files,
are:

- **added:** `walk/RESULT-PXD026748-shotgun-ingest.md`;
- **modified:** `data/curation/curation_PXD026748_shotgun.json`, the dated
  correction to its FILTERS item, 93 → 73.

Verify with `git diff --stat cae91c6..origin/main`, and check that the record's
sha256 is
`9501e5ca5b61b2957a1cc6ccf2a79358943f7b88e196b7b1af57bef67d95bd8a`. If either
check fails, report it and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`. **Never force-push, and never amend or rebase a pushed
commit. Do not write, retype or commit any file under `notes/prompts/`.** This
container has no raw store.


## Why a generator, and not a fixture

`PXD026748`'s ingest figures exist only as prose:
- the GG arm's in `notes/reports/09-ingest-PXD026748-report.md`;
- the shotgun arm's in `walk/RESULT-PXD026748-shotgun-ingest.md`.

Giving them a machine-readable home by transcribing that prose would repeat
the error `tests/test_pxd018299_refusals.py` names in its module docstring: a
fixture written from the documents it is supposed to check. The anchor's
fixtures are **generated** from the raw bytes by a module
(`bzk/sources/pxd018299_refusals.py`), and so are these. The raw bytes exist
only on bzk's machine. So this turn writes the generator, and bzk runs it there
and commits what it writes. **Guards against the generated values are the next
turn, once the fixtures exist.**


## Receipt checks

R1. The base: show `git diff --stat cae91c6..origin/main` and the record's
    sha256.

R2. `bzk/sources/pxd018299_refusals.py`. Quote `main()` and name its outputs.
    How does it locate the deposit and configure the adapter? Quote its comment
    on why it does not construct the adapter from constants.

R3. `notes/reports/09-ingest-PXD026748-report.md:176–177`. Quote the
    multi-protein and isoform figures, with their numerators and denominators.
    Then find where turn 09 said **how** it computed them: which column, which
    rows, and what counts as isoform. Quote it. **If the report does not state
    the method, say so plainly.** The generator will then define it, and the
    fixture records that 09's method was unrecorded.

R4. `SiteIngestReport` (`bzk/adapters/maxquant_sites.py:193–`) and
    `ProteinIngestReport` (`bzk/adapters/maxquant_protein_groups.py`). List
    each one's fields.


## The module — `bzk/sources/pxd026748_ingest_figures.py`

`python -m bzk.sources.pxd026748_ingest_figures`, run after the raw deposits
are in place. It follows R2's pattern exactly:
- `load_path` on each `PXD026748` record;
- `rebuild._deposit_for` and `rebuild._adapter_for` for each, the same functions
  the replay uses;
- `adapter.parse`, offline, with no graph;
- one fixture per arm.

If a deposit is absent, exit with a usable message naming the record. If an
adapter doesn't claim its file, exit likewise. Never write a partial fixture.

**Split the IO from the arithmetic.** The pure functions take parsed output and
return fixture dicts, and `main()` does the IO, so the arithmetic is testable
offline.

**`tests/fixtures/pxd026748_digly_ingest.json`**, from `curation_PXD026748.json`:
- `dataset`, `file`, `content_hash`, `generated_by`, `generated_under`, the
  same keys as the anchor's fixture;
- every `SiteIngestReport` count field;
- `cells` in total, and by quantity;
- the refusal membership, as `row`, `reason` and `detail`;
- the **multi-protein share**, as an explicit numerator and denominator for each
  of the three denominators report 09 gives at `:176`:
  - rows after decoy/contaminant;
  - rows after the localisation filter;
  - emitted observations.

  Use the method R3 found. If none was stated, define it, write the definition
  into the fixture as a `method` string, and say in the report that turn 09's
  method is unrecorded and may differ.
- **isoform razor picks**, as a numerator and denominator, with the same rule
  about method.

**`tests/fixtures/pxd026748_shotgun_ingest.json`**, from
`curation_PXD026748_shotgun.json`:
- the same header keys;
- every `ProteinIngestReport` field except `observation_of_row`;
- the refusal membership;
- `cells` by quantity, and cells with value > 0 by quantity;
- the ingestion `Analysis.quantity`;
- `only_identified_by_site`: `in_file`, `emitted`, and `dropped_as_decoy_or_contaminant`.

**Record, don't judge.** The module writes figures. It does not compare them
with any registration, report or document. That comparison belongs to the next
turn's guards and to the reviewer.


## Tests — `tests/test_pxd026748_ingest_figures.py`

Offline only, on synthetic inputs built in `tmp_path`. Commit no deposit and no
generated fixture. Each test must be seen to fail before it passes: report its
mutation and failure message.

T1. **Shotgun arithmetic.** Use a synthetic protein-groups file with:
    - one decoy row that is also site-only;
    - one site-only row that is kept;
    - one ordinary row.

    Assert `only_identified_by_site` = in_file 2, emitted 1, dropped 1. Also
    assert the counts of cells and positive cells by quantity.
T2. **GG arithmetic.** Use a synthetic site table with:
    - one multi-protein row that is kept;
    - one single-protein row that is kept;
    - one multi-protein row that is dropped below localisation.

    Assert each of the three multi-protein numerator/denominator pairs.
T3. **No partial fixture.** With one deposit absent, `main()` exits non-zero,
    names the record, and writes neither fixture. Point `main` at a temporary
    home through an argument or parameter, never the real home.
    `replay_ingestion`'s docstring records the 78-second hazard.


## Registered expectations

E1. Suite = 719 passed, 14 skipped at base, then 719 + the new tests. Report
    the split.
E2. No existing test changes, and no id pin moves. The record correction in the
    base changed no id: the reviewer measured all 16 of its node ids unchanged
    across the edit.


## Task

1. Run R1–R4.
2. Write the module and T1–T3.
3. Run E1–E2 and every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit the module and tests as one commit (`sources:` prefix). Push,
   fast-forward only.
5. Write `notes/reports/13-generate-the-pxd026748-figures-report.md` and commit
   it alone. Push.


## Out of scope

- Generating or committing either fixture.
- Any guard against their values.
- The published cascade and the MOESM3 declaration.
- ADR-0035's review.
- The six superseded homes of `67,158`.
- The site branch's constant `quantity`.
- The unenumerated-mirrors class.
- The drift line.
- `notes/prompts/`.


## Report

- R1–R4 answered.
- The module's outputs, with each field and its source.
- The multi-protein and isoform methods, and whether they are turn 09's or
  newly defined.
- T1–T3, each with its mutation and failure message.
- E1–E2, each held or missed.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- What this turn does NOT cover.
- Commit SHAs and the push range, stating that every push was a fast-forward.
