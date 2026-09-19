# Report — close four gaps the audit of turn 10 found

**Run at:** 2026-09-19 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Opened at:** `554a37d`, verified before anything else · **Commits:** `49aa3c1`, and this report's own · **Pushed** · **`kuzu`:** 0.11.3

**Headline.** All four gaps closed. C1 pins disjointness in the container the `.txt` parametrisation could never reach; C2 carries the protein count into `RebuildReport` and onto the `done:` line; C3 removes a grain from two skip messages that had no business naming one; C4 stops the site sniff's docstring claiming a strikethrough it never had. **No test pinned either C3 string** — one does now. E1 held at 708/14, E2 held. E3 is handed to bzk. This turn adds no capability, and **nothing under `notes/prompts/` was written or committed.**

**One mutation in this turn's own verification was a no-op and was caught by the test passing.** It is reported under C1 rather than quietly replaced, because it is the exact failure mode `CLAUDE.md` point 2 exists to name.

---

## Receipt checks

### R1 — what `RebuildReport` does not carry

`bzk/rebuild.py:444–454` at `554a37d`:

```python
    return RebuildReport(
        tables_created=tables,
        curation_records=replay.curation_records,
        nodes_staged=replay.nodes_staged,
        edges_staged=replay.edges_staged,
        cells_staged=replay.cells_staged,
        deposits_ingested=replay.deposits_ingested,
        site_observations=replay.site_observations,
        refusals=replay.refusals,
        ingestions_skipped=replay.ingestions_skipped,
    )
```

**`protein_observations`.** Every other `ReplayReport` field is carried across. The one added by turn 10 is the one left behind, and `RebuildReport`'s own definition had no field for it to land in.

### R2 — which lines name a grain, and which

`bzk/rebuild.py:433–436`:

```python
        f"done: {tables} tables, {replay.curation_records} curation record(s), "
        f"{replay.deposits_ingested} deposit(s), {replay.site_observations} site observation(s), "
        f"{len(replay.refusals)} refused, {replay.nodes_staged} node statement(s), "
        f"{replay.edges_staged} edge statement(s), {replay.cells_staged:,} quantitative cell(s)"
```

`:354–357`:

```python
            log(
                f"  {path.name} names a deposit that is not in the content store; "
                "sites not ingested"
            )
```

`:362`:

```python
            log(f"  no adapter recognises {source.name}; sites not ingested")
```

**All three name a grain, and all three name the same one: sites.**

They are wrong in two different ways, which is why C2 and C3 are separate changes. The `done:` line at `:433–436` names *sites* for a figure that is genuinely the site count — its fault is **omission**: it reports one grain and is silent about the other, so a protein-grain rebuild reads as having ingested nothing. The two skip lines name *sites* for a deposit whose grain **was never determined**: `_adapter_for` is what decides grain, and neither line is reached with an adapter in hand. There the fix is to name no grain at all, not to name both.

### R3 — the container the parametrisation never includes

`tests/test_adapter_dispatch.py`:

```python
def _every_txt_fixture() -> list[Path]:
    return sorted(FIXTURES.glob("*.txt"))


@pytest.mark.parametrize("path", _every_txt_fixture(), ids=lambda p: p.name)
def test_at_most_one_adapter_claims_any_file(path: Path) -> None:
    """The premise `_adapter_for` rests on, over every tab-separated fixture in the tree.

    `_adapter_for` tries the site adapter, then the protein one, and returns the first that claims
    the file. That is only a *dispatch* and not a coin toss because no file can be claimed twice;
    if this ever fails, the missing refusal branch in `_adapter_for` stops being unreachable and
    the order of the two `if`s silently becomes the decision.
    """
    assert len(_claims(path)) <= 1, f"{path.name} is claimed by more than one adapter"
```

**The workbook. `glob("*.txt")` cannot match an `.xlsx`**, so no spreadsheet was ever passed to the three `sniff`s.

`bzk/adapters/perseus.py:408–413`:

```python
        if spreadsheet.looks_like_a_workbook(raw):
            try:
                rows = spreadsheet.text_rows(raw)
            except spreadsheet.SpreadsheetError:
                return False
            return any(_is_stamped(cell) for row in rows[:HEADER_SCAN_ROWS] for cell in row)
```

**A workbook reaches the first branch — the spreadsheet branch**, which decides on Perseus' type-prefix stamp (`C: `/`N: `/`T: `/`M: `) and never looks at annotation rows, because `openpyxl` has nowhere to put them. So the guard turn 10 added — `carries_perseus_annotation`, an annotation-row test on tab-separated text — is **not** the thing that separates the adapters in this container, and the disjointness turn 10 pinned was pinned for the other container only. This is the branch `PXD055843`'s deposit reaches, and E3's third line rests on it.

### R4 — was the sentence struck, or removed?

The sentence in `bzk/adapters/maxquant_sites.py` containing "struck rather than deleted", at `554a37d`:

```
        This function returned `True` for such a
        file, so the claim was not a simplification but a measurable error; it is struck rather
        than deleted so the correction is visible.
```

**Removed and quoted — not struck.** No strikethrough markup appears anywhere in the file. What the paragraph actually does is quote the removed clause, two sentences earlier: *"It read `"which neither of those has"` — true of `proteinGroups.txt`, false of the Perseus export…"*. The technique is sound; the word describing it was wrong, and a docstring that misdescribes its own correction is the same defect one level up from the one it was correcting.

---

## Changes

### C1 — disjointness pinned for the workbook container

**`tests/test_adapter_dispatch.py`**, new section after `_claims` / before the two tab-separated Perseus tests: a local `_sheet` helper (`openpyxl`, as `tests/test_perseus.py:112` does) and two tests. **No workbook fixture is committed** — every workbook is built in `tmp_path` and thrown away, which is the synthetic-twin discipline `tests/test_perseus.py` already states.

| test | file builds | asserts |
|---|---|---|
| `test_a_perseus_stamped_workbook_is_claimed_by_perseus_alone` | header `T: Protein IDs` / `N: LFQ intensity A` / `N: id`, one data row | `_perseus_adapter().sniff(path)` **first**, then `_claims(path) == ["perseus"]` |
| `test_a_plain_workbook_is_claimed_by_nobody` | header `Protein IDs` / `LFQ intensity A` / `id`, no stamp | `_claims(path) == []` |

**The order of the two assertions in the first test is the point, not a style choice.** With the workbook branch deleted, `_claims(path) == ["perseus"]` does still fail — the list comes back empty — but it fails in a way indistinguishable from `openpyxl` having written a file no adapter can read at all, and it says nothing about which half of the claim broke. The non-vacuity assertion turns that into a named failure: *the Perseus workbook branch did not claim this file*. C1a below confirms the test stops there rather than four lines later.

Together these cover **`PXD055843`**, the one committed record whose deposit is a workbook, and they turn E3's third line from an argument into an assertion.

### C2 — `RebuildReport` carries `protein_observations`

**`bzk/rebuild.py`**, three places:

- `RebuildReport` gains the field beside `site_observations`, with a comment recording *how* the omission was found — a real rebuild printing `0 protein observation(s)` in the replay summary while the `done:` line and the repr carried nothing;
- the `done:` line gains `f"{replay.protein_observations} protein observation(s), "`, **in the same wording the replay summary already uses**, so the two lines of one run do not describe the same figure two ways;
- the `RebuildReport(...)` construction populates it from the replay.

`main`'s exit status is unchanged — it still reads `ingestions_skipped` alone.

### C3 — the two skip messages name no grain

**`bzk/rebuild.py`**:

- at what was `:354–357`: the two-line `log(...)` collapses to `log(f"  {path.name} names a deposit that is not in the content store; not ingested")`, with a comment saying why no grain is named;
- at what was `:362`: `log(f"  no adapter recognises {source.name}; not ingested")`.

**Tests matching either string: none.** `grep -rn "sites not ingested"` over the tree returned exactly the two `bzk/rebuild.py` lines and nothing under `tests/`. So **no existing test was updated**, and there is none to name. A new test, `test_a_skipped_deposit_is_reported_without_a_grain`, now pins the message — both that it says `not ingested` and that it does *not* say `sites not ingested`.

One near-miss, checked and left alone: `bzk/sources/pxd018299_refusals.py:118` raises `SystemExit(f"no adapter recognises {deposit.name}; nothing to refuse")`. Same opening clause, different module, and it already names no grain. C3 named `:356` and `:362`; this is neither, and it needs no change.

### C4 — the "struck" wording corrected

**`bzk/adapters/maxquant_sites.py`**, the `sniff` docstring. One sentence replaced; nothing else in the docstring touched except the re-wrap `ruff format` implies. It now reads:

> **Nothing was struck through**, and an earlier revision of this paragraph said otherwise — it read *"struck rather than deleted"*, describing a strikethrough that was never written. What was actually done is what the sentence above does: the false clause was **removed** from the claim, and it is quoted in full two sentences up, which is how a correction stays visible in a docstring.

**The first version of this sentence was itself false, and was caught before the report went out.** It ended *"— with no `~~` anywhere in the file"*, which stopped being true the moment it was written, because that clause *is* a `~~` in the file: `grep -c '~~'` went from 0 to 1 on the very edit that claimed 0. A sentence correcting a docstring's false self-description by making a new false self-description is the same defect one level further in — the shape `CLAUDE.md` point 3 describes as an observation that surfaces and dies in the same sentence. The literal was removed and the claim reworded to one that does not depend on its own absence; `grep -c '~~'` is back to 0. The code commit was amended rather than followed by a third commit, so *"code and tests as one commit"* still holds; both refs were force-pushed, which is safe here — linear single-developer history, pushed minutes earlier, and bzk's E3 run was against `554a37d`, which is untouched.

The trailing cross-reference in the same paragraph gained four words — *"over both containers, since 10b"* — so the docstring's claim about what `tests/test_adapter_dispatch.py` pins stays true after C1. That is the only other edit in the docstring, and it is reported here rather than folded into "nothing else".

---

## Tests — each seen to fail before it passes

Every mutation was confirmed applied by reading the file back before the run and confirmed reverted by reading it back after; the suite is green again as this is written.

| # | mutation | test | failing assertion's message |
|---|---|---|---|
| C1a | the workbook branch (`perseus.py:408–413`) deleted from `PerseusAdapter.sniff` | `test_a_perseus_stamped_workbook_is_claimed_by_perseus_alone` | `AssertionError: the Perseus workbook branch did not claim this file` / `assert False` — **at the non-vacuity assertion, as required**, not at the `_claims` line four lines later |
| C1b′ | the workbook branch made permissive: `return True` in place of the stamp test | `test_a_plain_workbook_is_claimed_by_nobody` | `AssertionError: assert ['perseus'] == []` |
| C1c | `return True` inserted at the top of `MaxQuantProteinGroupsAdapter.sniff` | `test_a_plain_workbook_is_claimed_by_nobody` | `AssertionError: assert ['maxquant_protein_groups'] == []` |
| C2a | `protein_observations=replay.protein_observations` dropped from `RebuildReport(...)` | `test_a_rebuild_carries_the_protein_count_out_of_the_replay` | `assert 0 == 1` / `where 0 = RebuildReport(…, site_observations=0, protein_observations=0, …).protein_observations` |
| C2b | the `done:` line's protein clause deleted | same | `AssertionError: assert '1 protein observation(s)' in '[rebuild] done: 57 tables, 1 curation record(s), 1 deposit(s), 0 site observation(s), 0 refused, …'` |
| C3a | `:362` reverted to `"; sites not ingested"` | `test_a_skipped_deposit_is_reported_without_a_grain` | `AssertionError: assert 'no adapter recognises SYNTHETIC_perseus.txt; not ingested' in '…'` |

**C1b, the first attempt, was a no-op, and the test passing is how it was caught.** The mutation was `return True or ACCESSION_COLUMN in header and not {…}` inside `MaxQuantProteinGroupsAdapter.sniff`. It applied — the read-back confirmed the text was in the file — and the test **passed**, because the mutated line is unreachable for a workbook: `read_table` decodes the ZIP bytes with `errors="replace"`, finds no `id` column, raises `MaxQuantError`, and the `except (OSError, ValueError)` above returns `False` before the mutated expression is evaluated. A green run from a mutation that never executed is exactly the shape `CLAUDE.md` point 2 names — indistinguishable from a guard that does not fire. It is replaced above by C1c, which inserts `return True` at the top of the function and does reach the assertion. Reported rather than silently swapped, because the swap is the interesting part.

**C4 changes a string only, and no test pins it.** Checked: `grep -rn "struck rather" tests/` returns nothing (0 lines), and `grep -rn "sniff.__doc__" tests/` returns nothing (0 lines). Reported as the prompt asks — **none does**. That is also why the self-falsifying first version above reached the point of being written: nothing mechanical could have caught it, and it was found by re-reading the claim against the file, which is what point 2 asks for and not what a green suite provides. The same is true of C3's strings before this turn, which is why the new test was written.

The C2 test follows T5's discipline on both sides: `RebuildReport.protein_observations`, `ReplayReport.protein_observations` and the adapter's own `groups_emitted` are asserted equal to each other, with the adapter parsed separately — no literal stands on both sides of any equality. It runs entirely in `tmp_path` with an explicit `home`, and the synthetic deposit is stored by `raw_store.store` so the record's `content_hash` cannot drift from the bytes.

---

## Registered expectations

### E1 — **held**

| | at `554a37d` | after |
|---|---|---|
| passed | 704 | **708** |
| skipped | 14 | **14** |

708 = 704 + 4 new tests, on a container with **no raw store** (`~/.bzk-omics/` does not exist here). No existing test was modified: `git diff --stat` against `554a37d` shows `bzk/adapters/maxquant_sites.py`, `bzk/rebuild.py` and `tests/test_adapter_dispatch.py` only, and the third is additions plus one import line.

### E2 — **held**

`tests/test_rebuild.py::test_rebuilt_ids_match_the_committed_pin` → **1 passed**, unmodified. Nothing this turn touches an id: C2 and C3 change a dataclass field and two log strings, C1 adds tests, C4 changes a docstring.

### E3 — handed to bzk; not run here

A re-run of turn 10's E3 command over the real raw store should print the same figures — `PXD018299` 2,029 sites / 27 refused, `PXD026748` 2,166 sites / 21 refused / 51,984 cells, `PXD055843` skipped, totals 4,195 / 48 / 100,680 — **plus** `0 protein observation(s)` on the `done:` line and `protein_observations=0` in the `RebuildReport` repr. The `PXD055843` skip line will also now read *"no adapter recognises Supplementary_Data_S1_TP.xlsx; not ingested"* rather than *"; sites not ingested"* — that wording change is C3 and is expected.

---

## `CLAUDE.md` point 1 — every check, at its actual result, with its target

Environment built with `uv sync` from the committed `uv.lock`. Every command under `.venv/bin/python`.

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **708 passed, 14 skipped** |
| `pytest tests/test_schema.py` | `tests/test_schema.py` | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed!** |
| `ruff format --check` | `bzk tests` | **98 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 98 source files** |

`ruff check .` — which additionally covers the three notebooks, permanently out of scope — **was not run and is reported as not run.**

---

## `CLAUDE.md` point 2 — the change did what it claimed

- **C2 was checked against the defect as bzk observed it**, not only against the field: the test reads the `done:` line out of `capsys` and asserts the protein clause is in it, and C2b fails that assertion specifically. The repr was half the gap; the printed line was the other half.
- **C1's non-vacuity requirement was checked by mutation**, not by reading the test: C1a fails at the first assertion and the message names it.
- **One mutation was a no-op and was caught**, documented above rather than replaced in silence.
- **C3 was verified in both directions** — the new message present, the old string absent — so a partial revert of one of the two lines cannot pass.

---

## `CLAUDE.md` point 3 — what this turn does not cover

**Closed here, and by what:**

- *Disjointness in the workbook container.* **Closed for the two shapes that matter by C1**, with non-vacuity asserted. Not closed as a *parametrisation*: `_every_txt_fixture` still globs `*.txt`, and the two workbook tests are written out rather than folded into it, because a workbook has no committed fixture to glob. A third workbook shape added later needs a third test.
- *`RebuildReport` dropping a grain.* **Closed by C2a and C2b.** The class of defect — a field added to `ReplayReport` and not carried across — is **not** closed: nothing asserts the two dataclasses agree field-for-field, so a *fourth* grain added later could repeat this exactly. That guard is writable (compare the two `__dataclass_fields__` sets, minus the four `RebuildReport` does not take) and is **not written here**; this turn was scoped to the four named gaps. Named as the residue rather than left implicit, per point 3's own standard.
- *A skip message asserting a grain it cannot know.* **Closed by C3a for `:362`.** The sibling at `:356` — the "not in the content store" branch — is changed but **is not pinned by a test**: reaching it needs a curation record whose deposit is absent from the store, which is a different fixture shape than the one this test file builds, and `tests/test_rebuild.py` already exercises that branch without asserting on its wording. A revert of that one line alone would not fail the suite.
- *The docstring's false "struck" claim.* **Closed by C4**, and pinned by nothing — it is prose. A test could assert `"struck rather than deleted" not in MaxQuantSiteAdapter.sniff.__doc__`, but a guard against one phrase is not a guard against the class, and the class here is "a docstring describes itself wrongly", which is not machine-checkable. Stated plainly rather than papered over with a token assertion.

**Not covered, and left as it was:**

- **The site branch's constant `quantity`** (`maxquant_sites.py:171`) — still an open defect, named in `_adapter_for`'s docstring, out of scope by this prompt as by turn 10's.
- **The drift line's "different set (3,013 then, 3,579 now)"** — out of scope, untouched.
- **`adapter.name` reading `maxquant` for the site adapter** — out of scope, untouched.
- **SILAC-channel keys** such as `Intensity L …`, which would derive as `intensity` — still unguarded, as turn 10 reported.
- **The tautology sweep's floor** — `modules >= 32 and asserts >= 1129` against a surface this turn leaves at 42 modules and more assertions than before. Still stale, still a `>=`, still not re-denominated: E1 registered no existing test changes. The sweep's *multiset* half ran clean on this turn's four new tests, so nothing needed classifying.
- **Everything turn 10's out-of-scope list named** — the shotgun zip, the record-count pin, any `PXD026748` ingest, `protein_adjusted`/`ADJUSTED_BY`/I4/I21, `PerseusAdapter` in the dispatch, `ObservationAdapter`, any ADR, `ONTOLOGY.md`, `schema.py`, any invariant, the published cascade, the handoff documents.
- **`notes/prompts/`** — **not written, not retyped, not committed.** The committed `10-wire-the-adapter-dispatch.md` keeps the words of the issued prompt with its headings, emphasis and wrapping lost and its R4 fences mis-nested; bzk replaces it from his own copy. This turn did not touch it.

---

## `CLAUDE.md` point 4 — instructions dropped or partially done

- **E3 was not run**, as instructed — no raw store in this container. Handed to bzk with the two additions it should now print.
- **C3's instruction to "search the tests for any that match either string, and update them in the same commit. Name each one."** was carried out and found **nothing to update**. Reported as *none*, which is the honest discharge of an instruction whose premise did not hold.
- **The working branch.** The harness handed this session `claude/eloquent-fermat-or15bq`. Per `CLAUDE.md` § Working style the change was fast-forwarded onto `main` and both refs pushed; they are the same commit.
- Nothing else was dropped or partially done.

---

## Commits and push range

| commit | contents |
|---|---|
| `49aa3c1` | `rebuild: carry the protein count out of the replay, and stop naming a grain on a skip` — C1–C4, code and tests, one commit, no report. Amended once after its first push, to remove the self-falsifying `~~` described under C4; `708b07c` was its pre-amend SHA and no longer exists on either ref |
| this report's own, `notes: report the 10b correction turn` | `notes/reports/10b-close-the-dispatch-gaps-report.md`, alone; no prompt file |

**Push range:** `554a37d..49aa3c1` for the code commit, then one commit on top carrying this report. Both pushed to `origin/claude/eloquent-fermat-or15bq` and fast-forwarded onto `origin/main`. This report does not quote its own SHA — turn 10's did, by amending it in, which changed the SHA and made the quoted value wrong; `git log --oneline -2` on either ref gives both.
