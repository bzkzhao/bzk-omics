# Report — the window diagnostic reads multi-window cells

**Run at:** 2026-09-20 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Opened at:** `b0b220e`, exactly · **Commits:** `bc5bfd8`, and this report's own · **Pushed, every push a fast-forward**

**Headline.** The diagnostic now indexes per window rather than per cell, and each match names the candidate protein that owns the window it hit — or `null` with a reason where the counts forbid saying. **No row is recovered and no count moves**, which T10 asserts as an equality between two whole summaries. E1 held at 745/14; **E2 held with exactly the one existing test the prompt anticipates**, plus two classified sweep entries. One mutation was replaced for failing in the wrong way.

**The base check.** `git rev-parse origin/main` → `b0b220e2d764c47614d2b9bf3400c540fdcc50fc`, which is `b0b220e notes: track prompt 15b` exactly — `b0b220e..origin/main` and its diff are both empty. No stop condition fired.

---

## Receipt checks

### R1 — the matching rule as it stood, and what `[]` asserted

`bzk/sources/pxd026748_published_cascade.py:300–310`:

```python
    for row in deposit.rows:
        by_key[_text(row[column["Protein"]]), _text(row[column["Position"]])].append(row)

    window_column = column.get("Sequence window")
    by_window: dict[str, list[str]] | None = None
    if window_column is not None:
        by_window = collections.defaultdict(list)
        for row in deposit.rows:
            by_window[_text(row[window_column])].append(_text(row[column["id"]]))

    records: list[dict[str, Any]] = []
```

`:330–340`:

```python
        # A lead, never a key. `None` where the deposit has no `Sequence window` column at all,
        # because an empty list there would assert that no row shares the window. Computed here
        # rather than in a closure over `cells`: a function defined inside the loop that reads the
        # loop's variable is the late-binding trap, and it is one dict lookup.
        window_lead = (
            None if by_window is None else by_window.get(_text(cells.get("Sequence window")), [])
        )
```

**The rule as it stood: whole-cell string equality.** `:308` keys each deposit row under `_text(row[window_column])` — the entire `Sequence window` cell, stripped — and `:335` looks up the published window against that. A cell holding `AAAKAAA;BBBKBBB` is indexed under that one 15-character string and under neither of its two windows.

**What `[]` asserted to a reader: "no deposit row's `Sequence window` cell equals this window."** The fixture's `note` said *"the ids of deposit rows sharing their Sequence window"*, which a reader takes as *sharing the window* — and for the 85 multi-window rows those two readings come apart. Five of the six join losses would have been recorded as sharing their window with nothing, while a deposit row carries it. **That is a false assertion in a committed fixture**, which is why the fixture was not committed.

### R2 — does the adapter already split a `;`-separated column?

**Yes, in two places in `bzk/adapters/maxquant_sites.py`.** `_promotions`, at `:479–482`:

```python
            candidates = [a.strip() for a in row[column["Proteins"]].split(";") if a.strip()]
            positions = [p.strip() for p in row[column["Positions within proteins"]].split(";")]
            if len(candidates) != len(positions):
                continue
```

and `_site`, at `:577`:

```python
        candidates = [a.strip() for a in row[column["Proteins"]].split(";") if a.strip()]
```

**And it is a named helper one module over**, `bzk/adapters/maxquant_protein_groups.py:461–462`:

```python
def _split(cell: str) -> list[str]:
    return [a.strip() for a in cell.split(";") if a.strip()]
```

Character for character the same rule as the two inline spellings. **So this turn reuses `_split` and writes no fourth copy.**

**The adapter's count guard is reused too, and it is the precedent for C1's `null`.** `:481–482` splits two parallel columns, and where the counts differ it *declines to act* rather than aligning what it has. C1 does the same thing one field along: it records the match and withholds the protein.

---

## Changes

Both in `bzk/sources/pxd026748_published_cascade.py`.

### C1 — split multi-window cells

The eight lines at `:303–308` become one call, `by_window = window_index(deposit)`, and a new pure function sits beside the other arithmetic:

```python
def window_index(deposit: maxquant.MaxQuantTable) -> dict[str, list[dict[str, Any]]] | None:
```

It splits each row's `Sequence window` with `_split`, splits `Proteins` with the same rule, and appends `{"row": …, "protein": …}` under **every** window. `protein` is `proteins[position]` only when `len(proteins) == len(windows)`; otherwise it is `None` and the match carries `protein_unattributed_reason` giving both counts — or, where the table has no `Proteins` column at all, saying so instead.

Its docstring records the measurement that forced it (85 of 2,653 rows; 1 of 6 against 6 of 6), why the protein is withheld rather than guessed, and that the splitting rule is reused rather than rewritten.

### C2 — the diagnostic stays a diagnostic

No key, no stage and no count other than the window matches changes. Two places now state what `[]` means:

- **the comment where `window_lead` is built**: *"`[]` means 'no deposit row carries this window AMONG ITS WINDOWS' — the index is built per window, not per cell, so an empty list is a statement about every window of every row and not about whole-cell equality"*;
- **the fixture's `note`**, rewritten to describe `{row, protein}`, the `;`-separated cells, the per-window index, the meaning of an empty list, and the count-mismatch `null`.

---

## Tests — each seen to fail before it passes

Five tests touched or added in `tests/test_pxd026748_published_cascade.py`; the helper `_site_row` gains a `proteins` parameter so a row's candidate set can differ from its razor pick.

| # | mutation | test | failing assertion's message |
|---|---|---|---|
| **T8** | whole-cell equality restored (`windows = [whole cell]`) | `test_a_window_inside_a_multi_window_cell_is_found_with_its_protein` | `assert [] == [{'row': '0', 'protein': 'P09914'}]` |
| **T9′** | aligned by position wherever one exists, dropping the count check | `test_a_count_mismatch_leaves_the_protein_unattributed_with_its_reason` | `AssertionError: assert 'P09914' is None` |
| **T10** | a window match allowed to recover the row | `test_finding_a_window_changes_no_placement_and_no_count` | `AssertionError: a window match is not a recovery` / `assert (None, None) == ('join', 'no_key_match')` |
| **C2** | substring matching instead of per-entry | `test_an_empty_list_means_no_row_carries_the_window_among_its_windows` | `assert [{'row': '0', 'protein': 'P20591'}] == []` |

**T8 pins that the protein is the one at the matched position, not the razor pick.** The row's candidates are `P20591;P09914` with `P20591` as the razor pick, and the published row carries the *second* window — so a match naming `P20591` would be wrong in a way a count check cannot catch.

**T10 asserts two whole summaries equal**, not a handful of named numbers: a count the test forgot to name is exactly where a recovery would hide. It compares the same published rows against a deposit that carries their windows and one that does not, and asserts the placements and the summaries are identical while the leads differ.

### One mutation was replaced for failing in the wrong way

T9's first mutation dropped the count check outright (`aligned = protein_column is not None`). The test went red — with `IndexError: list index out of range`, raised from `proteins[position]` on a row with three windows and two proteins. **That is a crash, not a mis-attribution.** It would have arrived whatever the assertion said, so it is no evidence that the test catches a positional guess.

Replaced by T9′, which stays in range and guesses: `proteins[position] if position < len(proteins) else None`. The window at index 1 then gets `P09914`, and the test fails on `assert match["protein"] is None` — the defect it exists to catch. **This is the third time this session a mutation has been rejected for failing elsewhere or for not applying**, and it is what `CLAUDE.md` point 2 means by never taking the exit status alone.

### One test needed reordering after its mutation

T10's first run failed with `KeyError: 'window_matches'` — recovery means the row is no longer a join loss, so the key it asserted on was never set. A real failure, but it named a missing key rather than the claim. The placement assertion moved to the front, and the mutation now fails on *"a window match is not a recovery"*.

---

## Registered expectations

### E1 — **held**

| | at `b0b220e` | after |
|---|---|---|
| passed | 741 | **745** |
| skipped | 14 | **14** |

745 = 741 + 4 new tests (T8, T9, T10 and the C2-meaning test).

### E2 — **held, with the one test the prompt anticipates and two sweep entries**

**`test_a_window_match_is_recorded_and_never_recovers_the_row` changed**, and it is the only existing test that did. It asserted `records[0]["window_matches"] == ["0"]` — the bare-id shape C1 replaces with `{row, protein}`. Its claim is untouched: the lead is recorded, and it is not a key. The assertion is now `== [{"row": "0", "protein": MX1}]`, with a comment saying the shape moved and the claim did not.

**`tests/test_tautology_sweep.py` gained two `PINNED` entries**, for T10's two whole-object comparisons. Not a behaviour change and not a pin moving: the sweep's own failure message directs new matching expressions to be classified, and 10c settled that classifying is the designed response and reshaping to dodge the matcher is not. Both sides are separate `build(...)` runs over two different deposits; neither produced the other.

**No id pin moved.** `test_rebuilt_ids_match_the_committed_pin` → **1 passed**, unmodified.

### E3 — registered for bzk's rerun, not checkable here

Repeated so the report carries it: the summary is **identical** — exposure 288, the same stage counts, clusters and coerced cells; the six join losses carry exactly the row/protein pairs the prompt tabulates; and `#148` and `#176` carry `protein: null` with the count-mismatch reason.

**Nothing in this container can check any of it**, and two parts are worth separating. That *no count moves* is a property of the code, and T10 asserts it on synthetic input — that one is argued and tested here. That *the six pairs are those six* is a fact about a deposit this container does not hold; it is the prompt's measurement, repeated.

---

## `CLAUDE.md` point 1 — every check, at its actual result, with its target

Environment built with `uv sync` from the committed `uv.lock`. Every command under `.venv/bin/python`.

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **745 passed, 14 skipped** |
| `pytest tests/test_schema.py` | `tests/test_schema.py` | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed!** |
| `ruff format --check` | `bzk tests` | **104 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 104 source files** |

`ruff check .` — which additionally covers the three notebooks, permanently out of scope — **was not run and is reported as not run.**

---

## `CLAUDE.md` point 2 — the change did what it claimed

- **The splitting rule was located before it was reused**, in all three of its existing spellings, rather than a fourth being written from the description.
- **The inertness claim is asserted as two whole summaries**, because that is the form in which "nothing moved" can fail.
- **One mutation was rejected for crashing instead of mis-attributing**, and replaced with one that produces the wrong answer in range.
- **One test was reordered** so its mutation fails on the claim rather than on a key only a lost row carries.
- **The sweep's flag was classified, not dodged.**

---

## `CLAUDE.md` point 3 — what this turn does not cover

- **The pairs are not interpreted.** `#106` matching `O75369` and `#141` matching `P38919` are recorded and nothing here says what they mean. Whether a published claim whose key misses but whose window sits on a different protein is a renaming, a paralogue, a shared peptide or an error in the supplement is the reviewer's, and the fixture is built so that question can be asked rather than answered.
- **`#148` and `#176` stay unattributed.** The count mismatch is recorded with both counts; which candidate owns their window is not decidable from the columns and is not guessed.
- **No row is recovered, and the join key is untouched.** The six stay lost at `join` with `no_key_match`.
- **The splitting rule now has four call sites and no single home.** `maxquant_sites.py:479`, `:577`, `maxquant_protein_groups._split`, and this module importing the third. Reusing the named one was the smallest correct move here, but **a private helper of the protein-groups adapter being the de-facto home of a rule the site adapter spells inline twice is a mirror waiting to drift** — promoting it to `bzk/adapters/maxquant.py` would touch two parse paths and is not this turn's.
- **A window repeated within one cell is indexed twice**, once per position, and would appear twice in a match list. Correct as a per-position record and not deduplicated; nothing observed needs it.
- **The published side is still matched whole.** A published `Sequence window` holding several windows would be looked up as one string and find nothing. The supplement carries one per row; that this holds is an assumption about a file not in this container.
- **Out of scope and untouched:** any change to the join key or any stage, recovering any row, interpreting the pairs, the anchor's cascade module, `notes/prompts/`.
- **The tautology sweep's floor** is still stale and untouched; only two `PINNED` entries were added.

---

## `CLAUDE.md` point 4 — instructions dropped or partially done

- **Nothing dropped.**
- **Two things beyond the letter of the brief, both named above**: the `_site_row` helper gained a `proteins` parameter, without which no test could give a row a candidate set differing from its razor pick; and the two sweep classifications, which the sweep's own guard required before the suite would go green.
- **T9's mutation was replaced**, and both the original and the replacement are reported.
- **No commit was amended and no ref was force-pushed.**

---

## Commits and push range

| commit | contents |
|---|---|
| `bc5bfd8` | `sources: index the window diagnostic per window, not per cell` — C1, C2, the four tests, the one updated test and the two sweep classifications |
| this report's own | `notes/reports/15c-window-diagnostic-report.md`, alone |

**Push range:** `b0b220e..bc5bfd8` for the change, then one commit on top carrying this report.

**Every push in this turn was a fast-forward.** `git push` reported `5d2d798..bc5bfd8` on the branch and `b0b220e..bc5bfd8` on `main` — the `..` form, never the `+` prefix git prints for a forced update. No `--force`, no `--force-with-lease`, no amend, no rebase.
