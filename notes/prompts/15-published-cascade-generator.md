# PROMPT 15 — a generator for PXD026748's published-claim cascade

Working copy: this container's clone of `bzkzhao/bzk-omics`. Report its path.

**Base.** Fetch, then fast-forward to `origin/main`. It must be a fast-forward
of `54cfbde` whose only addition is `walk/PREREG-PXD026748-cascade.md`. Verify
with `git diff --stat 54cfbde..origin/main`. If anything else changed, report it
and stop.

Build the environment with `uv sync`. Run every Python command under
`.venv/bin/python`. **Never force-push, and never amend or rebase a pushed
commit. Do not write, retype or commit any file under `notes/prompts/`.** This
container has no raw store.

**Do not read or quote `walk/PREREG-PXD026748-cascade.md` into the module, and
do not tune anything toward it.** It registers expected figures. The module must
compute its figures without reference to them. The pre-registration is in the
base only so that it demonstrably precedes the run.


## What this turn builds

`bzk/sources/pxd026748_published_cascade.py`, run as
`python -m bzk.sources.pxd026748_published_cascade`. It places each of the 296
rows of `PXD026748`'s Supplementary Table 1 at exactly one stage of the platform
path, and writes `tests/fixtures/pxd026748_published_cascade.json`.

**As in turn 13, you write and test the module. bzk runs it on his machine,
because the raw bytes are only there, and commits the fixture.** Generate no
fixture here.

**The supplement.** `41590_2021_1035_MOESM3_ESM.xlsx`,
`sha256:872371eb9877c6aa1f85e82429e8354993cd4d10c643592ff8ee14012e36a870`, is in
bzk's raw store. Its sheet `Table 1` has these columns, as recorded in
`walk/walk_PXD026748.json`: `#`, `Cluster`, `Uniprot ID`, `Gene name`,
`Protein name`, `Lysine position`, `Multiplicity`, `Sequence window`,
`Ubiquitin sites`, `Acetyl sites`, `In vivo ISG15 targets`,
`Protein Ratio WT/ISG15 KO`. **Which row is the header is not recorded.** Locate
it by content: find the row carrying `Uniprot ID` and `Lysine position`. Stop
with a clear message if that row is not unique.

**Declare it** the way the anchor declares its `SUPP_DATA_1`
(`bzk/sources/protein_groups.py`), with its own label, filename and hash. That
class's `url` hard-codes the anchor's journal path, and this is a different
article (Nature Immunology, doi:10.1038/s41590-021-01035-8). Make the smallest
change that gives this declaration a correct URL without changing the anchor's.
Report what you chose.


## Stages, in order, one per row

Reuse the platform's stage names from `bzk/published_cascade.py`.

1. **`join`.** Match the published (`Uniprot ID`, `Lysine position`) against the
   deposit's (`Protein`, `Position`) over **all** deposit rows. This is the key
   turn 09 used.
   - **No match:** lost, reason `no_key_match`.
   - **More than one match:** lost, reason `ambiguous_key`.
   - **Diagnostic, not a stage:** for every row lost here, record the ids of
     deposit rows whose `Sequence window` equals the published window. **Never
     use them to recover the row.**
2. **`decoy_contaminant`.** The matched row carries `Reverse` or
   `Potential contaminant`.
3. **`localisation`.** The matched row's `Localization prob` is below the
   adapter's declared threshold.
4. **`ingestion`.** The matched row is not among the observations the ingestion
   emits. Record the refusal reason if the row was refused.
5. **`presence`.** The paper's valid-value rule on the matched row's **summed**
   intensities: at least three positive values in at least one of the four
   (genotype, treatment) groups, taken from the curation record's mapping.
   Route A was admitted in `walk/RESULT-PXD026748-multiplicity.md`.

A row passing all five **reaches the test**. There is no significance stage.
Significance is the later reconstruction, and the module must say so in its
docstring.

**Per record, in addition:**
- the published `#`, `Cluster`, `Uniprot ID`, `Gene name`, `Lysine position`,
  `Multiplicity` and `Sequence window`;
- the matched deposit row id, if any;
- whether that row carries any positive `Intensity {label}___2` or `___3`.

**Summary block:**
- counts lost per stage, with their reasons;
- the number reaching the test;
- that number broken down by `Cluster`;
- the count of test-reaching rows flagged multiplicity-2.

Record the header keys the anchor's fixture records: `generated_by`,
`generated_under` with commit and date, and both files' names and hashes.

**Reuse, don't re-implement:**
- the ingestion's row populations and emitted observations, through
  `_parse_arm` in `bzk/sources/pxd026748_ingest_figures.py`, or the same
  replay functions it uses;
- the anchor's spreadsheet reader.

A second implementation of either would be a second population wearing the same
name. `_parse_arm`'s docstring gives the reason.

**Split the IO from the arithmetic.** A pure function takes published rows, the
deposit table, the emitted and refused row ids, and the sample groups, and
returns the records. `main()` does the IO. `main()` takes `home` and
`fixtures_dir` parameters with real defaults, as turn 13's does. Make the record
paths injectable too, which closes turn 13's unreachable "no partial fixture"
case for this module.


## Tests — `tests/test_pxd026748_published_cascade.py`

Offline only, on synthetic inputs built in `tmp_path`. For workbooks, use
`openpyxl` as `tests/test_perseus.py` does. Each test must be seen to fail
before it passes. Report each mutation and its failure message.

T1. **One row per stage.** One synthetic published row lands at each stage and
    one reaches the test. Assert each placement and each reason. That includes
    `ambiguous_key` as well as `no_key_match`.
T2. **The window diagnostic does not recover.** A published row whose key
    misses but whose window matches a deposit row is lost at `join` and carries
    that row's id in its diagnostic. Mutation: let the diagnostic recover it.
T3. **Presence uses summed intensities and the four groups.** Include a row that
    passes on the summed intensities with three positives in exactly one group,
    and a row that fails with two positives in each group.
T4. **The header row is found by content.** Use a workbook with a title row
    above the header, and one with a duplicated header row. The duplicate must
    stop with a message.
T5. **No partial fixture.** With the supplement absent from a temporary home,
    `main()` exits non-zero and writes nothing.

No test may read bzk's real store or the network.


## Registered expectations for this turn

E1. Suite = the base's count, 724 passed and 14 skipped if unchanged, plus the
    new tests. Report the split.
E2. No existing test changes, and no id pin moves. If the `SUPP_DATA_1` URL
    change touches a test, name it.


## Task

1. Verify the base.
2. Write the module, the declaration and T1–T5.
3. Run E1–E2 and every `CLAUDE.md` point-1 check with its target:
   - `pytest` (full suite) and `pytest tests/test_schema.py`;
   - `ruff check bzk tests`;
   - `ruff format --check bzk tests`;
   - `mypy bzk tests`.
4. Commit the module and tests as one commit (`sources:` prefix). Push,
   fast-forward only.
5. Write `notes/reports/15-published-cascade-generator-report.md` and commit it
   alone. Push.


## Out of scope

- Generating or committing the fixture.
- The reconstruction and any significance stage.
- Any guard on the fixture's values.
- The anchor's cascade modules, apart from the declaration class's URL.
- The B-store defect: the site adapter discarding `___n` intensities.
- The 22 cells that fail the multiplicity sanity check.
- The 44-row gap.
- `notes/prompts/`.


## Report

- The base check.
- The module's outputs, field by field, with sources.
- The URL decision.
- How the header row is found.
- T1–T5, each with its mutation and failure message.
- E1–E2, each held or missed.
- Every `CLAUDE.md` point-1 check at its actual result, with its target.
- What this turn does NOT cover.
- Commit SHAs and the push range, stating every push was a fast-forward.
