# Report — a generator for PXD026748's published-claim cascade

**Run at:** 2026-09-20 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Opened at:** `08ea62d` · **Commits:** `9586d6f`, and this report's own · **Pushed, every push a fast-forward**

**Headline.** `bzk/sources/pxd026748_published_cascade.py` places each published row at one of five stages and writes the fixture; bzk runs it. **The module reads no pre-registration, carries no expected value anywhere, and compares its figures with nothing** — `walk/PREREG-PXD026748-cascade.md` was not opened in this turn. E1 held at 738/14; E2 held. **One of my own tests was passing without exercising its claim and was found by its mutation** — under *Tests*.

---

## The base check

```
$ git diff --stat 54cfbde..origin/main
 walk/PREREG-PXD026748-cascade.md | 69 ++++++++++++++++++++++++++++++++++++++++
 1 file changed, 69 insertions(+)
```

One commit, `08ea62d walk: pre-register the PXD026748 published cascade`, adding that file and nothing else. `54cfbde` is `HYPOTHESIS v5: register H9s before the PXD026748 reconstruction`. No stop condition fired.

**The pre-registration was not read.** It is in the base so that it demonstrably precedes the run, and that is all it was used for.

---

## The module's outputs, field by field

`tests/fixtures/pxd026748_published_cascade.json`.

### Header

| field | source |
|---|---|
| `dataset` | the loaded `Dataset` node's `external_accession` |
| `published_file`, `published_content_hash` | `SUPP_TABLE_1`, the new declaration |
| `published_sheet` | `"Table 1"`, the constant the reader is given |
| `deposit_file`, `deposit_content_hash` | the `Dataset` node's `label` and `content_hash` |
| `path` | `"platform"`, as the anchor's fixture records |
| `note`, `generated_by` | this module |
| `generated_under.generated_at` | UTC at the start of the run |
| `generated_under.commit`, `.working_tree_clean` | `git rev-parse HEAD` and `git status --porcelain`, as the anchor's `_commit()` does |
| `generated_under.python` | `platform.python_version()`. No numpy or scipy: nothing here computes a statistic |
| `generated_under.presence_rule` | the rule in words, with the threshold and the group count |
| `generated_under.sample_groups` | the four groups and their mapping keys, so the rule can be re-read against the record |

### Per record

| field | source |
|---|---|
| `published` | the seven published columns — `#`, `Cluster`, `Uniprot ID`, `Gene name`, `Lysine position`, `Multiplicity`, `Sequence window` — verbatim from the row |
| `deposit_id` | the matched deposit row's `id`, or `null` where the join lost it |
| `lost_at` | one of the five stages, or `null` |
| `loss_reason` | the stage's reason; at `ingestion` it is **the adapter's own refusal reason** where the adapter refused the row |
| `has_positive_multiplicity_column` | whether the matched row carries any positive `{key}___2` or `{key}___3`. `null` where the join lost the row |
| `window_matches` | join losses only: deposit row ids whose `Sequence window` equals the published one |
| `ambiguous_ids` | `ambiguous_key` losses only: the ids that collided |

### Summary

| field | source |
|---|---|
| `published_rows` | the record count |
| `stages_run` | the five, named |
| `reaches_test` | rows lost at none |
| `lost` | per stage, `{count, reasons}` with reasons counted |
| `reaches_test_by_cluster` | the breakdown |
| `reaches_test_published_multiplicity_2` | the publication's `Multiplicity` column equals 2 |
| `reaches_test_with_positive_multiplicity_column` | the deposit-side flag |

**Two multiplicity counts, because the brief's phrase has two readings.** *"the count of test-reaching rows flagged multiplicity-2"* could mean the publication's `Multiplicity` column or the per-record `___2`/`___3` flag. They are measurements of two different files and can disagree, so both are recorded under names that say which. **Naming the ambiguity rather than picking one is the point**; if one of them is the intended figure, the other costs a line.

**Placement is validated through `cascade.outcome`**, which refuses a record lost at two stages or at none — so the summary's sum cannot be balanced by a record that contradicts itself.

**No `significance` key.** `cascade.cascade()` would emit `significance: 0`, which reads as a stage that ran and lost nothing. The summary counts the five that ran and names them in `stages_run`.

---

## The URL decision

**A `doi` field on `SupplementaryFile`, defaulting to the anchor's.** The prefix was a literal with the anchor's DOI baked in:

```python
SPRINGER_ESM = (
    "https://static-content.springer.com/esm/art%3A10.1038%2Fs41416-020-01167-y/MediaObjects/"
)
```

It is now built by `_esm_prefix(doi)`, with `SPRINGER_ESM = _esm_prefix(ANCHOR_DOI)`. **The constant's value is byte-identical**, every existing declaration's URL is byte-identical, and a file from another article passes its own DOI.

**Why not a second literal.** That is this one copied with two characters changed — the mirror between two sources `CLAUDE.md` § *Single source of truth* refuses, and the one that had no guard until now. `test_the_anchor_declarations_keep_their_urls` pins all three anchor URLs **against literals**, not against `SPRINGER_ESM`, because re-deriving them would compare the new code with itself.

`SPRINGER_ESM` has no reader outside `protein_groups.py` (checked), and the only URL assertion in the suite is `tests/test_protein_groups.py:155`'s prefix check, which passes unchanged.

---

## How the header row is found

**By content, not by position.** Which row is the header is recorded nowhere, and the workbook is reported to carry a title row above it. `header_row_index` returns the index of the one row carrying **both** `Uniprot ID` and `Lysine position`, and raises otherwise:

- **zero candidates** — *"no row carries all of \[…], so the header cannot be located by content and nothing can be joined"*;
- **two or more** — *"N rows carry all of \[…] (0-based indices \[…]); the header must be unique, because choosing one of two would decide silently which block of rows is data."*

They are different defects and the messages say which. The markers are the join key's own two columns: a sheet without both cannot be joined at all, so not finding them is a reason to stop rather than to look harder.

**The sheet is named, not positional.** The workbook has three sheets (`walk/walk_PXD026748.json`), so `spreadsheet.rows` gained an optional `sheet` argument. `sheet=None` is the first sheet — every caller written before today is unchanged — and a named sheet that is absent raises, listing the sheets present. A reader that fell back to the first would answer a question about `Table 1` with another sheet's rows.

---

## Tests — each seen to fail before it passes

`tests/test_pxd026748_published_cascade.py`, fourteen tests, offline on synthetic inputs under `tmp_path`. No deposit, no supplement and no generated fixture is committed.

| # | mutation | test | failing assertion's message |
|---|---|---|---|
| **T1a** | the adapter's refusal reason folded into `not_emitted` | `test_one_published_row_lands_at_each_stage` | `assert ('ingestion', 'not_emitted') == ('ingestion', 'residue_mismatch')` |
| **T1b** | the `Reverse` check disabled, so a decoy falls through | same | `assert (None, None) == ('decoy_contaminant', 'reverse')` |
| **T2** | the window diagnostic used as a second key | `test_a_window_match_is_recorded_and_never_recovers_the_row` | `assert (None, None) == ('join', 'no_key_match')` |
| **T3a** | positives counted over all twelve columns rather than per group | `test_presence_fails_on_two_positives_in_every_group` | `assert (None, None) == ('presence', 'presence_rule')` |
| **T3b** | the presence rule counting `…___2` as well as the summed column | `test_the_multiplicity_flag_reads_the_split_columns_and_presence_does_not` | `assert (None, None) == ('presence', 'presence_rule')` |
| **T4a** | the first header candidate taken instead of requiring uniqueness | `test_a_duplicated_header_row_stops_with_a_message` | `Failed: DID NOT RAISE CascadeSourceError` |
| **T4b** | the header taken as row 0 | `test_a_title_row_above_the_header_is_skipped` | `KeyError: '#'` |
| **T4c** | the named sheet ignored, first sheet read | `test_the_named_sheet_is_read_and_a_missing_one_is_refused` | `CascadeSourceError: no row carries all of ['Uniprot ID', 'Lysine position'] … Read 1 row(s).` |
| **T5** | the fixture written before the supplement is located | `test_main_names_the_supplement_when_only_it_is_missing` | `assert [PosixPath('…/pxd026748_published_cascade.json')] == []` |
| **URL** | `ANCHOR_DOI` changed | `test_the_anchor_declarations_keep_their_urls` | `assert 'https://…1038%2Fs41416-020-01167-y/…' == 'https://…1038%2Fs41590-021-01035-8/…'` |

**T1 covers all five stages and both join reasons** in one pass — seven published rows against seven deposit rows, asserting each placement, then the stage counts and that `significance` is absent from `lost`.

### One of my tests was passing without exercising its claim

**T3b's first run came back green with the mutation applied.** The fixture put the `Intensity A1___2` value on a sample whose *summed* value was already positive, so a rule that wrongly counted the split column reached the same verdict, and the test could not tell the two apart. The column was moved to `Intensity A3___2` — the zero of its group — and the mutation then fails. The test's docstring records why the placement matters, and that it was measured rather than reasoned.

**That is the second time this session a green mutation run has caught an inert fixture** (turn 10d's was an unreachable mutation). It is what `CLAUDE.md` point 2 means by *never take the exit status alone*, arriving from the other direction: here the mutation applied and ran, and the fixture was what did nothing.

**Two more tests were fixed for ordinary reasons before the mutations**: the site table lacked `Positions within proteins`, so `_adapter_for` returned `None`; and T1's `emitted_rows` still contained the row it meant to have refused.

### T5 closes turn 13's unreachable case

Turn 13's *"no partial fixture"* test could only reach the first guard: `_deposit_for` locates by `content_hash`, so no synthetic bytes can put a temporary home past it. Here `main` takes `curation_path` and `supplement` as parameters, so `test_main_names_the_supplement_when_only_it_is_missing` builds a synthetic deposit, stores it, points a synthetic record at its real digest, and gives `main` a supplement nothing matches. **The run gets past `_parse_arm` and stops at the supplement's guard** — the state turn 13 could not construct — and T5's mutation shows the directory assertion is live.

---

## Registered expectations

### E1 — **held**

| | at `08ea62d` | after |
|---|---|---|
| passed | 724 | **738** |
| skipped | 14 | **14** |

738 = 724 + 14 new tests.

### E2 — **held**

**No existing test changed.** `git status` before the commit showed two modified source files and two untracked new ones; no file under `tests/` was modified.

**The `SUPP_DATA_1` URL change touches no test.** `tests/test_protein_groups.py:155` asserts `supp.url.startswith("https://static-content.springer.com/")`, which is unaffected; that module runs **8 passed, 1 skipped**, unchanged. The new guard is in the new test file.

**No id pin moved.** `test_rebuilt_ids_match_the_committed_pin` → **1 passed**, unmodified. Nothing this turn writes to the graph.

**The tautology sweep needed no entry** — every equality in the new tests compares against a literal display, which its Pass C excludes.

---

## `CLAUDE.md` point 1 — every check, at its actual result, with its target

Environment built with `uv sync` from the committed `uv.lock`. Every command under `.venv/bin/python`.

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **738 passed, 14 skipped** |
| `pytest tests/test_schema.py` | `tests/test_schema.py` | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed!** |
| `ruff format --check` | `bzk tests` | **104 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 104 source files** |

`ruff check .` — which additionally covers the three notebooks, permanently out of scope — **was not run and is reported as not run.**

---

## `CLAUDE.md` point 2 — the change did what it claimed

- **The module was never run against the real files**, because neither is in this container. What is verified is the placement arithmetic, the header search, the sheet selection and both of `main`'s guards. **The path from `_parse_arm` through a successful write is exercised only as far as the supplement's guard** — that is this turn's evidential boundary, and bzk's run tests the rest.
- **Every guard was made to fail**, and one mutation caught an inert fixture rather than a defect in the code, which is recorded above rather than quietly fixed.
- **The anchor's prefix was checked byte-for-byte** against the literal it replaced, not argued from the construction.
- **The pre-registration was not opened.** The module's figures cannot have been tuned toward it, and its constants — the presence threshold, the stage list, the markers — all trace to a named source in the repository.

---

## `CLAUDE.md` point 3 — what this turn does not cover

- **No fixture is generated or committed**, and nothing guards any value it will carry. That is the next turn's, after bzk's run.
- **Nothing scores the run against `walk/PREREG-PXD026748-cascade.md`.** By construction: this module must not read it, so the comparison is the reviewer's.
- **The window diagnostic's `Sequence window` column is assumed to exist on the real site table and is not verified here.** The code handles its absence (`null`, with a test), but whether the deposit has it is a fact about a file this container does not hold. If it does not, every join loss will carry `null` and the diagnostic will be silent rather than wrong.
- **`_text`'s normalisation is a judgement about `openpyxl`'s typing.** An integral float becomes its integer so `90.0` keys as `90`. A published position stored as text with a stray space is handled by the strip; one stored in any other form is not, and nothing here can predict which the real file uses.
- **The four groups are read off the curation record and assumed to partition the twelve samples.** They do today, 3 × 4, measured. A record mapping a sample into no group, or into two, is not guarded.
- **Out of scope and untouched:** the reconstruction and any significance stage, the B-store defect (the site adapter discarding `___n` intensities — this module reads them off the *table*, not the store, so it is unaffected and does not fix it), the 22 cells failing the multiplicity sanity check, the 44-row gap, the anchor's cascade modules apart from the declaration's URL, and `notes/prompts/`.
- **The tautology sweep's floor** is still stale and untouched.

---

## `CLAUDE.md` point 4 — instructions dropped or partially done

- **Nothing was dropped.**
- **Two shared modules were changed that the brief implied rather than named.** `spreadsheet.rows` and `text_rows` gained an optional `sheet`; the brief said to reuse the anchor's reader and named a sheet the reader could not select. The default preserves every existing caller, and the alternative — a second `openpyxl` call in the new module — is the re-implementation the brief forbids.
- **Both multiplicity counts are recorded** where the brief asked for one, because the phrase has two readings. Named under *The module's outputs* rather than resolved silently.
- **No commit was amended and no ref was force-pushed.**

---

## Commits and push range

| commit | contents |
|---|---|
| `9586d6f` | `sources: place every PXD026748 published claim at one stage of the platform path` — the module, the declaration, the two shared-module changes and fourteen tests |
| this report's own | `notes/reports/15-published-cascade-generator-report.md`, alone |

**Push range:** `08ea62d..9586d6f` for the module, then one commit on top carrying this report.

**Every push in this turn was a fast-forward.** `git push` reported `2f575b5..9586d6f` on the branch and `08ea62d..9586d6f` on `main` — the `..` form, never the `+` prefix git prints for a forced update. No `--force`, no `--force-with-lease`, no amend, no rebase.
