# Report — close the report-mirror class, and forbid force-pushes

**Run at:** 2026-09-19 · **Working copy:** `/home/user/bzk-omics` (this container's clone of `bzkzhao/bzk-omics`) · **Opened at:** `6703249` · **Commits:** `0ac7284`, `ea8de3e`, and this report's own · **Pushed, every push a fast-forward** · **`kuzu`:** 0.11.3

**Headline.** The mirror is gone and the class is closed twice over — `TypeError` at the first rebuild (C1), and a declaration check that needs no rebuild at all (C2). C3 writes down the rule 10b broke. **E1 held at 711/14, E2 held, E3 held with a byte-identical repr.** This turn adds no capability, and nothing under `notes/prompts/` was written or touched.

**On the base.** The clone opened at `1f02491`, one commit behind the stated base. The single intervening commit is `6703249 notes: restore prompt 10 as issued, and track prompt 10b` — bzk's own prompt-file restore, touching `notes/prompts/` only, and exactly the commit this prompt anticipates. The clone was fast-forwarded onto it and **HEAD was `6703249` before any change was made**, which is the state the stop condition asks for. Reported here rather than treated as a discrepancy, since the base named and the base worked from are the same commit.

---

## Receipt checks

### R1 — the two field lists

`bzk/rebuild.py:95–124`, `ReplayReport`, in declaration order:

1. `curation_records`
2. `nodes_staged`
3. `edges_staged`
4. `cells_staged`
5. `deposits_ingested`
6. `site_observations`
7. `protein_observations`
8. `refusals`
9. `ingestions_skipped`

`:126–144`, `RebuildReport`, in declaration order:

1. `tables_created`
2. `curation_records`
3. `nodes_staged`
4. `edges_staged`
5. `cells_staged`
6. `deposits_ingested`
7. `site_observations`
8. `protein_observations`
9. `refusals`
10. `ingestions_skipped`

**In one class and not the other: `tables_created` only, and it belongs to `RebuildReport`.** Nothing is on `ReplayReport` and missing from `RebuildReport` — today. That is the state `protein_observations` was *not* in between the two turns that added it, and the state nothing held.

`tables_created` is legitimately one-sided: it counts the DDL step, which `replay_ingestion` does not perform and has no field for.

### R2 — the hand-written mirror

`bzk/rebuild.py:453–464` at `6703249`:

```python
    return RebuildReport(
        tables_created=tables,
        curation_records=replay.curation_records,
        nodes_staged=replay.nodes_staged,
        edges_staged=replay.edges_staged,
        cells_staged=replay.cells_staged,
        deposits_ingested=replay.deposits_ingested,
        site_observations=replay.site_observations,
        protein_observations=replay.protein_observations,
        refusals=replay.refusals,
        ingestions_skipped=replay.ingestions_skipped,
    )
```

**Nine lines restate a `ReplayReport` field by hand** — `:455` through `:463`. `:454`'s `tables_created=tables` is not one of them; it comes from the DDL step above.

**What happens today if a field is added to `ReplayReport` and not to this call: nothing. A silence.**

- **Not a failure at import.** `ReplayReport` and `RebuildReport` are independent dataclasses; neither references the other's fields at class-creation time.
- **Not a failure in a test.** No test compared the two classes before this turn.
- **Not a failure at runtime.** The constructor is called with the arguments it was given; the un-restated field is simply never read.

Measured, not argued. A dummy `probe_field: int = 0` was added to `ReplayReport` alone at `6703249`, confirmed applied by reading the file back, and `tests/test_rebuild.py::test_rebuild_creates_schema_and_leaves_the_archive_alone` reported **`1 passed`**. The mutation was then reverted. That is the whole defect: the rebuild runs, the report is returned, and a figure the replay measured is gone with nothing saying so.

### R3 — does `CLAUDE.md` forbid a force-push?

`CLAUDE.md:94`, the fast-forward sentence, at `6703249`:

> A session handed a different working branch by its harness should fast-forward the change onto `main` when it is complete, and continue there.

The `grep`, run rather than recalled:

```
$ grep -nEi 'force[- ]?push|--force|force_with_lease|force-with-lease|amend|rebase|rewrite.*histor|histor.*rewrit' CLAUDE.md
61:**`ONTOLOGY.md` is normative.** … must be amended *before* the code changes. …
91:- Prefer amending a document over adding one. The document set is deliberately small.
95:- **Verify at every critical node …** A critical node is any `ONTOLOGY.md` amendment, …
```

```
$ grep -nEi 'push' CLAUDE.md
$ echo $?
1
```

**No.** Three hits for the amend/rebase pattern, and all three are about *amending a document* — `ONTOLOGY.md` being amended before code, preferring to amend a document over adding one, and an `ONTOLOGY.md` amendment as a critical node. None concerns git. The word *push* does not appear in `CLAUDE.md` at all, so no line forbade what 10b did, and no line described the fast-forward-only discipline the bullet's own first sentence implies. C3 fixes that.

### R4 — can a plain sentence in `CLAUDE.md` trip `tests/test_agent_config_references.py`?

**What it checks in `CLAUDE.md`:** nothing *in* it — it extracts `` `DOC.md` § … `` pointers and `` `tests/…py` ``/`` `bzk/…py` `` paths from the 47 Markdown files under `.claude/`, and uses `CLAUDE.md` only as a **referent**, reading its `##`-and-deeper headings so a pointer into it can be resolved.

**No.** A sentence added to `CLAUDE.md` with no file path, line reference or backticked identifier cannot trip it, for two independent reasons: the module never reads `CLAUDE.md` for references (`_agent_docs()` globs `AGENT_DIR.rglob("*.md")`, and `AGENT_DIR` is `.claude/`), and `_headings` matches `^#{2,4}\s+`, which a sentence inside a bullet is not — so the heading set the pointers resolve against is unchanged. The three pinned counts (`EXPECTED_AGENT_DOCS`, `EXPECTED_SECTION_POINTERS`, `EXPECTED_CODE_PATHS`) all count matches in `.claude/` and cannot move. Confirmed by the suite: C3's sentence is in, and the module passes.

---

## Changes

### C1 — the hand-written mirror removed

**`bzk/rebuild.py`.** `from dataclasses import dataclass, field` gains `fields`. The nine restating lines at `:455–463` become one splat:

```python
    return RebuildReport(
        tables_created=tables,
        **{f.name: getattr(replay, f.name) for f in fields(ReplayReport)},
    )
```

with a comment above it recording what the nine lines were, how the omission escaped, and why `RebuildReport` stays **declared** rather than derived: its fields are the public surface a caller reads and `OPERATIONS.md` §5 describes, and `tables_created` — the one field that is not the replay's — would have nowhere to be declared in a dynamically built class.

A `ReplayReport` field without a matching `RebuildReport` field now raises `TypeError` at the constructor, on **every** rebuild. Shown under C1's mutation below.

### C2 — the declaration guarded

**`tests/test_rebuild_report_mirror.py`**, new, three tests:

| test | asserts |
|---|---|
| `test_every_replay_field_is_carried_into_the_rebuild_report` | `fields(ReplayReport) - fields(RebuildReport) - NOT_CARRIED` is empty |
| `test_the_shared_fields_agree_on_their_types` | each shared field's `str(f.type)` is equal on both classes |
| `test_the_rebuild_report_adds_exactly_the_fields_it_declares` | `fields(RebuildReport) - fields(ReplayReport) == {"tables_created"}` |

`NOT_CARRIED` is a **named, empty dict** — field name to reason. Empty is the claim, not an oversight: a future field that genuinely should not reach a caller goes in with its reason, in the same commit, so a reader sees an exception that was decided rather than one nobody noticed.

Types are compared as **strings** because `from __future__ import annotations` is on in `bzk/rebuild.py`, so every annotation there is already a string; resolving them would add an evaluation step the assertion does not need. `fields()` is read rather than `__annotations__` so defaulted fields read the same way.

**`tests/test_tautology_sweep.py`** gains one `PINNED` entry and its classification: `("test_rebuild_report_mirror.py", "extra == {'tables_created'}", 1)`. The sweep flagged it, and the flagged comparison was **classified rather than reshaped away**. It is matched by Pass D — `extra` is a name bound from a call, and Pass D does not exclude a literal display on the other side — not by Pass C, which a set of constants would have escaped. Neither side produced the other: the left is read off the two declarations at run time, the right is typed by hand and *is* the claim.

**One thing was done and then undone here, and it is worth recording.** The first response to the sweep was to reshape the assertion — replace a `REBUILD_ONLY` constant with an inline literal — on the assumption that Pass C's literal-display exclusion would cover it. It did not: the sweep fired again on the reshaped form, because the match was Pass D all along. Reading the two passes rather than guessing showed that the designed response was the one the failure message names — *"otherwise add it to `PINNED` with its count"* — and that is what shipped. The literal was kept, because it reads better where the claim is made, and the comment beside it now says which pass matches it rather than which pass it was hoped would not.

### C3 — the rule, in `CLAUDE.md`

**`CLAUDE.md:94`**, one sentence appended to the `Commit to `main`` bullet, after its fast-forward sentence. Nothing else in the file changed — `git diff --stat` reads `1 file changed, 1 insertion(+), 1 deletion(-)`, the one line being that bullet.

> **Never force-push, and never amend or rebase a commit that has been pushed** — a correction discovered after a push is a new commit, with a line in the report saying why, even where that makes the turn's commit count differ from the one its prompt named; prompt 10b amended a pushed commit and force-pushed `main` to reword one sentence, rewriting published history in order to save a commit nobody was counting.

The instance is named by prompt number and carries no SHA, as instructed: the amended commit no longer exists on any ref and could not be cited truthfully.

---

## Tests — each seen to fail before it passes

Every mutation confirmed applied by reading the file back before the run, and confirmed reverted after. **No mutation in this turn was unreachable**; the R2 probe was expected to pass and did, which is the measurement rather than a miss.

| # | mutation | test | failing assertion's message |
|---|---|---|---|
| C2a | `probe_field: int = 0` added to `ReplayReport` alone | `test_every_replay_field_is_carried_into_the_rebuild_report` | `AssertionError: ['probe_field'] is/are declared on ReplayReport and not on RebuildReport, so a rebuild would drop the figure. Add the field to RebuildReport, or add it to NOT_CARRIED with the reason it should not reach a caller` |
| C2b | `RebuildReport.site_observations` retyped `int → int \| None` | `test_the_shared_fields_agree_on_their_types` | `AssertionError: {'site_observations': ('int', 'int \| None')} — each entry is (ReplayReport, RebuildReport). A shared field must carry the same annotation on both, or a caller reading the rebuild's report may assume something the replay never promised` |
| C2c | `probe_only_here: int = 0` added to `RebuildReport` alone | `test_the_rebuild_report_adds_exactly_the_fields_it_declares` | `AssertionError: RebuildReport declares ['probe_only_here', 'tables_created'] beyond ReplayReport, not ['tables_created']. A field here that rebuild() does not pass stays at its default and reports a measurement that was never taken` |
| C1 | `probe_field: int = 0` added to `ReplayReport` alone, **with `--ignore=tests/test_rebuild_report_mirror.py`** so C2's guard cannot be what fails | **`tests/test_rebuild.py::test_rebuild_creates_schema_and_leaves_the_archive_alone`** | `TypeError: RebuildReport.__init__() got an unexpected keyword argument 'probe_field'`, raised at `bzk/rebuild.py:469` |

**C1's row is the evidence that the silence became a failure**, and it is the same mutation as C2a and as the R2 probe. Three runs of one edit:

| state | C2's guard | result |
|---|---|---|
| `6703249`, before C1 | did not exist | `1 passed` — the silence |
| after C1, guard ignored | ignored | `TypeError` in `test_rebuild_creates_schema_and_leaves_the_archive_alone` |
| after C1 and C2 | active | fails in `test_rebuild_report_mirror.py`, before any rebuild runs |

---

## Registered expectations

### E1 — **held**

| | at `6703249` | after |
|---|---|---|
| passed | 708 | **711** |
| skipped | 14 | **14** |

711 = 708 + 3 new tests, on a container with no raw store.

### E2 — **held**

`tests/test_rebuild.py::test_rebuilt_ids_match_the_committed_pin` → **1 passed**, unmodified. Nothing this turn touches an id: C1 changes how a dataclass is constructed, C2 adds a test, C3 changes prose.

### E3 — **held. No figure changes, and the repr is byte-identical.**

A synthetic rebuild — one protein-groups deposit, `tmp_path`, explicit `home`, never the real store — run before and after C1 and diffed:

```
before  RebuildReport(tables_created=57, curation_records=1, nodes_staged=16, edges_staged=21,
        cells_staged=4, deposits_ingested=1, site_observations=0, protein_observations=1,
        refusals=[], ingestions_skipped=0)

after   RebuildReport(tables_created=57, curation_records=1, nodes_staged=16, edges_staged=21,
        cells_staged=4, deposits_ingested=1, site_observations=0, protein_observations=1,
        refusals=[], ingestions_skipped=0)
```

`diff` reports no difference. Same fields, same order, same values. That is expected and is worth stating why: a dataclass's `repr` follows its **declaration** order, and C1 changed only how the arguments are passed, not how `RebuildReport` is declared. Keeping it a declared dataclass is what makes that guarantee free.

---

## `CLAUDE.md` point 1 — every check, at its actual result, with its target

Environment built with `uv sync` from the committed `uv.lock`. Every command under `.venv/bin/python`.

| check | target | result |
|---|---|---|
| `pytest` | the full suite | **711 passed, 14 skipped** |
| `pytest tests/test_schema.py` | `tests/test_schema.py` | **20 passed** |
| `ruff check` | `bzk tests` | **All checks passed!** |
| `ruff format --check` | `bzk tests` | **99 files already formatted** |
| `mypy` | `bzk tests` | **Success: no issues found in 99 source files** |

`ruff check .` — which additionally covers the three notebooks, permanently out of scope — **was not run and is reported as not run.**

---

## `CLAUDE.md` point 2 — the change did what it claimed

- **The defect was reproduced before it was fixed.** The R2 probe ran the exact mutation at `6703249` and got `1 passed`; the same mutation after C1 gets a `TypeError`. The claim "this was a silence" is a measurement, not a reading of the code.
- **C1's guard was isolated from C2's.** The C1 mutation runs with `--ignore=tests/test_rebuild_report_mirror.py`, so the failure that arrives cannot be C2's test firing — it is the rebuild itself.
- **E3 was checked by diffing two captured reprs**, not by reasoning that the order should be unchanged.
- **The sweep's flag was read, not dodged.** The first reshape attempt failed for a reason I had guessed at; reading Pass C and Pass D showed the guard was asking for a classification, and it got one.

---

## Is the class closed?

**The class is: a field on `ReplayReport` that does not reach `RebuildReport`. It is now closed, twice, at two moments.**

- **By `tests/test_rebuild_report_mirror.py`** (C2), which fails on the declarations alone — no rebuild, no graph, no fixture — and names the field and the direction. This is where the class is closed.
- **By `bzk/rebuild.py`'s splat** (C1), which raises `TypeError` at the first rebuild if the guard is somehow not run. A second, independent line of defence rather than the primary one.

Both directions are covered: a field on `ReplayReport` alone (C2a, C1) and a field on `RebuildReport` alone (C2c), the latter being the case where a number would sit at its default for ever while reading as a measurement. Annotation drift on a shared field is covered too (C2b).

**What is not closed by this**: the general class *"two sources in this repository restate each other with nothing holding them equal."* This pair is now guarded, joining the six the repository already guards. Nothing enumerates the pairs, so a seventh created tomorrow is as unguarded as this one was — that is the shape `CLAUDE.md` point 3 names, and it is not closable by a test, only by the habit of writing one each time.

---

## `CLAUDE.md` point 3 — what this turn does not cover

- **The tautology sweep's floor.** `modules >= 32 and asserts >= 1129` against a surface now at 43 modules. Still stale, still a `>=`, still not re-denominated — the standing defect carried since prompt 09. The sweep's *multiset* half did fire on this turn and was answered, so the half that catches new matching expressions is working.
- **`CLAUDE.md`'s `Last reviewed` header.** The file's own convention says *"Update `last reviewed` when you touch a file"*, and C3 touched it. **Not updated**, because C3 said *"change nothing else in the file"* — an explicit instruction that contradicts the convention. Flagged here rather than resolved either way: the header still reads `2026-08-10`, and whether the convention or the instruction wins is bzk's call, not one to make silently.
- **The other direction of C2's type check**: it compares annotations as text, so `int` and `builtins.int` would read as disagreeing and a genuinely equivalent alias would fail. Nothing in either class uses an alias today, and resolving annotations would add machinery for a case that does not exist.
- **Any other field or wording in either report class** — untouched, as scoped.
- **Any other line of `CLAUDE.md`** — untouched. `git diff --stat` shows one insertion and one deletion, on line 94.
- **`notes/prompts/`** — not written, not retyped, not committed. `git diff --stat 6703249..HEAD -- notes/prompts/` is empty.
- **Everything 10b's out-of-scope list named** — the site branch's constant `quantity`, the drift line's set sizes, `adapter.name`, SILAC keys, and everything turn 10 excluded before that.

---

## `CLAUDE.md` point 4 — instructions dropped or partially done

- **`CLAUDE.md`'s `Last reviewed` was not updated**, per C3's "change nothing else". Raised above rather than decided here.
- **The base.** The clone opened one commit behind `6703249` and was fast-forwarded to it before any change; the intervening commit is bzk's prompt-file restore, touching only `notes/prompts/`. Reported rather than treated as a stop, because the base worked from *is* the base named.
- **The working branch.** The harness handed this session `claude/eloquent-fermat-or15bq`. Per `CLAUDE.md` § Working style the change was fast-forwarded onto `main` and both refs pushed; they are the same commit.
- Nothing else was dropped or partially done. In particular, **no commit was amended and no ref was force-pushed** — which is the rule this turn writes down, and the first turn to be bound by it.

---

## Commits and push range

| commit | contents |
|---|---|
| `0ac7284` | `rebuild: carry every ReplayReport field by iteration, and guard the declaration` — C1 and C2, one commit |
| `ea8de3e` | `docs: never force-push, and never amend or rebase a pushed commit` — C3 alone |
| this report's own, `notes: report the 10c correction turn` | `notes/reports/10c-close-the-report-mirror-report.md`, alone |

**Push range:** `6703249..ea8de3e` for the two code commits, then one commit on top carrying this report.

**Every push in this turn was a fast-forward.** `git push` reported `1f02491..ea8de3e` on the branch and `6703249..ea8de3e` on `main` — the `..` form, never the `+` prefix git prints for a forced update. No `--force`, no `--force-with-lease`, no amend, no rebase. This report does not quote its own SHA; `git log --oneline -3` on either ref gives all three.
