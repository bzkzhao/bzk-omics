# Prompt 38 — `--live` cannot finish: `SystemExit` escapes the handlers that exist to keep the report alive; and stage 3's note is stale (revision 4)

**Repository:** `main` at the commit adding this prompt. Every line reference below was measured at
`b53d1b3` and is wrong by however far later commits moved the file; §0 re-measures them.

**Why revision 4.** A third independent audit of revision 3 found **no blocker** and seven further
inaccuracies, and surfaced one build hazard now written into §1.5. Three of the seven were in
revision 3's own corrections, including a count that was wrong inside the paragraph fixing a count
— the third time in this prompt's history that a fix reproduced the shape it repaired. All seven
are fixed below, and the audit re-measured revisions 1 and 2's rejections, which still hold.

**Why revision 3.** A second independent audit of revision 2 found **no blocker** and eight
further inaccuracies, five of them inside revision 2's own new text — including a stale countable
in the sentence that cites its home, and an instruction to edit a pasted command that was itself
short by two edits. All eight are fixed below. Revision 2's two rejections were re-measured by that
audit and both held; §4 keeps them.

**Why revision 2.** An independent checker found eight defects in revision 1. Three were
blockers: a line span short by one, which would have left a dangling `]`; a referent asserted
rather than established, with the repository's own citation pointing elsewhere; and a countable
reading "three" over a list of three and "four" in the same sentence. Two findings were
re-measured and **rejected** — see §4. All six valid ones are fixed below.

**Why.** Prompt 37 made stage 3 compute the FINDINGS §1 census, and it does. But
`python -m bzk.audit --live` **exits before any stage runs** on a machine whose content store
lacks the PXD026748 inputs, so **no figure any stage computes under `--live` is reachable by one
command**, whatever a stage now computes. Fixture mode is unaffected and always was: plain
`python -m bzk.audit` exits 0 and writes a nine-stage report today. `notes/REVIEWER-HANDOFF-2026-11-07b.md` §5.2 l.123–126 is the home of the four
figures `bzk.audit` could not regenerate — FINDINGS §1 census, §2 two-route downshift, §5
changing-support count, §6 q-ranges — and **that count is now three: prompt 37 closed §1.**
`drawn_cell_census` (l.461–508) emits every figure §1 quotes at l.27–36, the exceeds count and the
median included. The handoff's phrase predates that build; this prompt does not restate the count
as four. Reaching what the stages compute by one command is the whole point of the 2026-11-08
decision. `run()` wraps the
regeneration in `except Exception` (l.1090); `h10.main` reaches a `raise SystemExit`; and
`SystemExit` derives from `BaseException`, not `Exception`. Prompt 37 §0.4 named this trap for a
wrapper it was writing and the build avoided it there, correctly; the same trap in `run()` was
reported and left, also correctly, because 37 built nothing else.

**What this builds.** The handler fix, one AST guard that closes the class, and the deletion of a
stale note. Nothing else. Three files: `bzk/audit.py`, `tests/test_audit.py`,
`tests/test_tautology_sweep.py` (its `PINNED` set, l.206, and its floor, l.2315 — §1.5). **The two
move on different triggers:** the floor counts asserts, so it moves with any new assert, while
`PINNED` moves only when a new *matching equality* appears. Expect the floor to move by more than
`PINNED` does, and read both off `sweep()` rather than predicting either. Prompt 37's header
conflated the two; that wording is reported, not fixed.

**Measured, so the build does not have to rediscover it.** `bzk/audit.py` holds **five** handlers
that catch `Exception` for the stated purpose of keeping the report alive: l.457
(`_live_whole_column_reference`), l.571 (`_live_drawn_cell_census`), l.659 (the graph read), l.990
(drift), l.1090 (`run()`'s regeneration). **Only l.1090 is reachable by a `SystemExit` today**:
the two live wrappers call `verify` directly and otherwise touch only leaf helpers
(`anchor_population`, `anchor_columns`, `_float_cell`, `_s1_rows`, `s1_columns`,
`log2_zero_as_missing`, `maxquant.read_table`), none of which raises `SystemExit`. The other four
are one refactor away, which is why §1.2 is a guard and not four edits.

**How that was established, because the list above is not the whole call graph.** The two wrappers
also call `audit._cell_provided`, `audit._load`, `audit._sha256_path`, `whole_column_reference`
and `drawn_cell_census`. The claim is not that the list is complete but that **no function either
wrapper reaches raises `SystemExit`**, established by scanning each for `raise SystemExit` rather
than by reading a list. §0.5 re-runs that scan.

---

## 0. Receipt check — answer, then stop and wait

Execute these against the repository. Do not answer from this prompt.

1. **Line references.** Report the line of each, as measured now: `run`, its `except Exception`
   inside the `if live:` block, `stage3_census`, the `stage.not_automated = [` inside
   `stage3_census`, the `claims_lost_before_test_by_stage` key, and the sweep floor assertion.
   This prompt says 1072, 1090, 371, 394, 383 and 2315. Any difference is reported with its size.
2. **Every handler in `bzk/audit.py` that catches `Exception`.** List each by line and by what it
   wraps, and report how many there are **of that kind** — not how many `except` clauses the module
   has, which is nine. This prompt says five of the nine catch `Exception`: 457, 571, 659, 990 and
   1090. Report any sixth, and
   whether `main` contains one (this prompt says it does not — a handler there would swallow
   argparse's own `SystemExit`, which must keep propagating).
3. **Reproduce the defect before fixing it**, without the raw store, in a scratch directory:
   monkeypatch `bzk.sources.pxd018299_h10.main` to raise
   `SystemExit("<filename> is not in the content store")`, call
   `audit.run(out, live=True, home=Path("/nonexistent"))`, and report whether the `SystemExit`
   escapes. Report the observed behaviour, not the expected one. **If it does not escape, stop:
   this prompt's premise is then wrong.**
4. **What stage 3's note is about — establish it, do not assume it.** The surviving clause reads
   *"The count of contrasts with no observed values"*. **This prompt does not identify its referent
   and §1.3 does not depend on identifying it.** Report all of:
   - the seven deposit ids named in `notes/scripts/diagnose_seven_rows.py`'s docstring; the
     `deposit_id` of every row in `tests/fixtures/pxd018299_published_cascade.json` whose `lost_at`
     is `presence`; whether the two sets are equal; and what
     `stage3_census(_committed()).findings["claims_lost_before_test_by_stage"]` gives for
     `presence`;
   - what `walk/CHECKS-census.md` — the record the note itself cites — holds for *a whole arm
     drawn, no measured counterpart*, and whether that file mentions seven of anything;
   - what `drawn_cell_census` returns under `whole_arm_drawn`, and whether a storeless
     `stage3_census(_committed())` reports `drawn_cell_census` as `NOT COMPUTED`. `_committed` is
     the test helper at `tests/test_audit.py` l.27, not an attribute of `bzk.audit`.

   Then state which candidate you think the clause names, **or that it is ambiguous**, and whether
   you found a third. Report it; this prompt does not tell you the answer.
5. **The handler class boundary.** For each function either live wrapper reaches, report whether it
   contains a `raise SystemExit`, by scanning rather than by trusting the list above. Report any
   function that does.

Then stop and wait.

---

## 1. Build

### 1.1 The handler

Every one of the five handlers in §0.2 becomes `except (Exception, SystemExit) as exc`. The
`noqa` comment on each is updated to say why `SystemExit` is included: a helper that turns a
missing input into `SystemExit` must not end a reporting process. **Nothing else about the five
changes** — not the message shape, not the mode downgrade, not the findings key each writes.

**Two rationales go false the moment the handler changes, and both are corrected in this diff.**
`_live_drawn_cell_census`'s docstring (l.535–536) says `_supplement_path`'s `SystemExit` *"would
escape the handler below"*, and the docstring at `tests/test_audit.py` **l.365** says
`except Exception` *"does not catch"* it. After §1.1 the handler below does catch it. Reword both to say why `verify` is still
the right call — it reports a missing input as a findings value rather than ending the stage, and
does not depend on the outer handler to stay alive. Leaving a now-false sentence beside the change
that falsified it is the shape `CLAUDE.md` l.98 describes.

Scope: handlers inside `bzk/audit.py` only, and only those catching `Exception`. The handler at
l.90 catches `(OSError, subprocess.CalledProcessError)` and is **not** touched. No `raise
SystemExit` anywhere is changed, and no handler in any other module is changed.

### 1.2 The guard that closes the class

A new test in `tests/test_audit.py` parses `bzk/audit.py` with `ast` and asserts, **by shape and
not by line number or comment**, that every `ast.ExceptHandler` whose caught type includes
`Exception` also includes `SystemExit`. Report the count it finds; it is five at `b53d1b3`, and
the assertion is on the rule, not on the count. The failure message names each offending
handler's line number and tells the reader why: `except Exception` does not catch `SystemExit`,
so a helper that exits would end the process instead of being reported.

Ten modules under `tests/` parse source with `ast.parse`; **these two are the ones to follow**,
and the count is not the point: `tests/test_analysis_record.py` (l.158,
`ast.walk(ast.parse(source))`) and `tests/test_audit_pxd032267.py` (l.547, `ast.parse(source)`).
Revision 2 also named `tests/test_curation_content_hash.py`; it uses `ast.literal_eval` on a regex
capture and parses no module source, so it is not an exemplar. Revision 3 then called the
remaining two *"two modules"*, which was wrong by eight.

### 1.3 The stale note

Delete the `stage.not_automated = [...]` assignment inside `stage3_census`, **l.394–400
inclusive** — the closing `]` is on l.400, and stopping at l.399 leaves it dangling — so the field
falls back to its default empty list.

**Two candidates were found, and a third reading is already ruled out.** Read literally, *a
contrast with no observed values* would be a claim with all six cells drawn; `drawn_cell_census`
folds that into `whole_arm_drawn` through `all(drawn[:3]) or all(drawn[3:])` (l.474) and emits no
all-six-drawn key of its own, so it is **not** a third candidate and must not trigger the stop
clause below. The stop clause is for a referent outside both candidates and that reading.

**The reason does not depend on §0.4's answer, which is why §0.4 only reports.** The clause carries
the label `NOT_AUTOMATED`, whose meaning in this instrument is *the figure lives only in prose*
(`bzk/audit_pxd032267.py` docstring). Both candidate referents are now produced by stage 3 itself:
the seven as `claims_lost_before_test_by_stage["presence"]` (l.383) in fixture mode, and the
whole-arm-drawn count as `drawn_cell_census["whole_arm_drawn"]` under `--live`, which prompt 37
built. **Under either reading the figure no longer lives only in prose, so the label is wrong and
the clause goes.** If §0.4 found a third candidate that stage 3 does *not* produce, **stop and
report instead of deleting**: the premise is then wrong.

**Do not restate the note's attribution.** Revision 1 named the clause's producing script. The
checker showed the note's own cited record, `walk/CHECKS-census.md`, is `diagnose_round14.py`'s,
exactly as the note says, and that the attribution cannot be settled in a container with no raw
store. That claim is withdrawn, and nothing here turns on which script produces the figure.

**No assertion is added on the number seven, and revision 3's reason for that was wrong.** It said
the cascade is the count's only source, so a guard would compare the fixture against itself. It is
not: `notes/scripts/diagnose_seven_rows.py` l.8 names the seven ids in prose, independently of the
fixture, so a guard would be a two-source mirror — the kind `CLAUDE.md` l.98 says is guarded
everywhere else here. The reason to leave it is different: **§0.4 deliberately leaves the clause's
referent open, and pinning seven would hard-code one of the two readings** on the strength of a
descriptive script's 2026-09-22 docstring, which nothing maintains. Record it in §3.3 as a declared
gap, naming that prose list as the unguarded second source. If the deletion leaves the stage's
`reading` text (l.384) claiming something the findings no longer support, report it; do not rewrite
it.

### 1.4 Expected outcome — registered before the run

| check | expected |
|---|---|
| §0.3 reproduction, before the fix | the `SystemExit` escapes `audit.run` |
| the same call, after the fix | no escape; a report is produced, and the regeneration entry records `SystemExit: <message>` |
| stage count in that report | 9 |
| `pytest`, after the build | 1212 passed, 14 skipped **plus this turn's new tests**, measured in a container with no raw store |
| stage 3's `not_automated`, after §1.3 | empty |

**1212 passed, 14 skipped is the container figure at `b53d1b3`**, re-measured in the reviewer's
clone, not inherited. A machine holding the PXD018299 sites table and Supplementary Data 1 runs
three more passing and three fewer skipped (`1215 / 11`), as prompt 37's build reported; that
relation is applied to a measured container figure, not itself measured on this machine. Report
which machine you measured on.

### 1.5 Tests

In `tests/test_audit.py`, after the stage 3 census tests (the file ends at l.389), in their style:

1. The AST guard of §1.2.
2. `h10.main` monkeypatched to raise `SystemExit`: `audit.run(..., live=True)` returns a report,
   the regeneration entry has `ran` false and its `error` names `SystemExit`, and nothing escapes.
   Model it on `test_a_missing_store_does_not_sink_the_report` (l.158), which does this for
   `FileNotFoundError`.
3. `KeyboardInterrupt` from the same monkeypatched `h10.main` **still escapes**
   `audit.run` — `(Exception, SystemExit)` must not become `BaseException`. This is the test that
   keeps the fix from being too wide.

**Mutate by content, never by a line number measured before §1.3.** Deleting l.394–400 shifts
every later line in `bzk/audit.py` up by seven, so a handler mutation aimed at a pre-deletion line
number lands somewhere unrelated and the guard stays green — a mutation that silently does not
apply, which is the exact hazard `CLAUDE.md` l.97 records. Locate each handler by its text, or
re-measure after the deletion, and confirm every mutation applied by reading the file back.

**Mutation proof, per `CLAUDE.md` l.97.** Mutate each of: one handler back to `except Exception`
(the AST guard must fail, naming that line); the `run()` handler back to `except Exception` (test
2 must fail); and the fix widened to `except BaseException` (test 3 must fail). For each, confirm
the mutation applied by reading the file back, name the failure message, revert, and confirm the
suite is green again. Never take the exit status alone.

**The tautology sweep.** After adding the tests, run `tests/test_tautology_sweep.py`, classify
every new equality as its failure message instructs, regenerate `PINNED` with the command in the
comment at l.201–202 **after** classifying, and report the floor before and after (l.2315 holds
`60` and `2626` now). That comment is prose, and four things come off before it runs: the `#: `
prefixes, the leading *"Regenerate with"* and its opening backtick, the closing backtick, and the
trailing *"**after** classifying whatever is"*. The wrapped string is then rejoined. The floor moves by
hand; do not guess its new value.

---

## 2. Out of scope

- **FINDINGS §2 route 2** and stage 4's note: **prompt 39, reassigned from this prompt.**
  `notes/prompts/37-stage3-live-census.md` l.153 gave both to prompt 38; they moved because the
  `SystemExit` defect leaves every stage's figures unreachable by one command, so a second computed
  figure would land behind the same closed door. The dated record names
  `notes/scripts/diagnose_round16.py` as route 2's script and `notes/logs/round16.txt` as its log
  (`walk/CHECKS-two-route-recovery.md` l.16–17; its l.47 row *this check* carries route 2's
  1.70–1.90). **"Section LL" comes from the script itself** (`diagnose_round16.py` l.8), not from
  that record. Stage 4's note (`bzk/audit.py` l.612–619) instead names
  `notes/scripts/diagnose_imputation_effects.py` for both routes. **The two disagree**; prompt 39
  settles it by measurement and this prompt relies on neither.
- **FINDINGS §5 and §6** (stages 6 and 7). Their source attribution is still unverified.
- **The 22 `raise SystemExit` sites under `bzk/`**, including the **three** identically shaped
  `_supplement_path` helpers (`bzk/sources/pxd018299_h10.py` l.1091,
  `bzk/sources/pxd026748_reconstruction.py` l.975, `bzk/sources/pxd026748_h5c_h9p.py` l.534).
  Turning a missing input into an exit is right for a script's own entry point; the defect is a
  reporting process not surviving it.
- **Handlers in every other module.** This prompt's guard reads `bzk/audit.py` only. Whether
  `bzk/audit_pxd032267.py` has the same shape is **unmeasured** — report it if you look, do not
  fix it.
- **Fetching any deposit**, and making `--live` complete end to end. After this prompt `--live`
  will run to a report on a machine without the PXD026748 inputs, with the regeneration recorded
  as failed and the committed fixture in use; it will **not** have regenerated anything. Say so
  plainly in the report rather than claiming `--live` now works.
- Any fixture, any change under `notes/` or `walk/`, and the `walk/FINDINGS.md` §1 median wording
  prompt 37 reported.

---

## 3. Report

Close with the four points of `CLAUDE.md` l.95–99:

1. Each check by name at its actual result and target: `pytest` (full suite), `pytest
   tests/test_schema.py`, `ruff check bzk tests`, `ruff format --check bzk tests`, `mypy bzk
   tests`. A check not run is reported as not run. State which machine, and whether the raw store
   held anything.
2. The §1.5 mutations, each with its confirmed application and its failure message; the §0.3
   reproduction before and after; and the §1.4 table, expected beside observed.
3. What this did not cover, including at least: the seven-count mirror §1.3 leaves unguarded and
   its prose source; that four of the five handlers are not reachable
   by a `SystemExit` today and the guard is therefore pre-emptive for them; that `--live` still
   regenerates nothing without the PXD026748 inputs; and whether any other module shares the
   handler shape.
4. Any instruction from this prompt dropped or partly done.

---

## 4. Rejected checker findings, recorded so they are not re-raised

Revision 1's audit raised eight findings: six fixed in revision 2, two rejected below. Revision 2's
audit raised eight more, all minor, all fixed in revision 3, and it re-measured both rejections and
found them correct. The two stay recorded so a later round does not re-raise them:

- **"the four FINDINGS figures" has no referent and the count matches no enumeration.** It has
  both: `notes/REVIEWER-HANDOFF-2026-11-07b.md` §5.2 l.123–126. The checker read only the source
  tree. The citation is now in the prompt, which is the valid half of the finding.
- **route 2's producer is `diagnose_imputation_effects.py`, not `diagnose_round16.py`.** The
  checker took stage 4's `not_automated` note as the authority. The dated record
  (`walk/CHECKS-two-route-recovery.md` l.16–17) names `diagnose_round16.py`, and that note is one
  of the things prompt 39 exists to correct. Recorded in §2 as a disagreement, not settled here.
